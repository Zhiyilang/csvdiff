#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
csvdiff - Diff two CSV/JSON datasets by key. Zero-dependency, cross-platform.

Pure Python standard library. Compare two tables (CSV or JSON), align rows by a
key column, and report exactly what changed: added rows, removed rows, and
column-level edits. Great for QA, ETL reconciliation, and comparing exports.

Author: Zhiyilang
License: MIT
"""

import argparse
import csv
import json
import os
import sys


def resolve_key(key, header):
    if key in header:
        return key
    try:
        return header[int(key)]
    except (ValueError, IndexError):
        raise SystemExit("error: key %r not found in columns %s" % (key, header))


def load(path, delimiter, has_header, key, ignore):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".json":
        with open(path, encoding="utf-8-sig") as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = data.get("data") or data.get("rows") or []
        if not data:
            return [], []
        header = list(data[0].keys())
        records = [dict(r) for r in data]
    else:
        with open(path, newline="", encoding="utf-8-sig") as f:
            if has_header:
                r = csv.DictReader(f, delimiter=delimiter)
                header = list(r.fieldnames or [])
                records = [dict(row) for row in r]
            else:
                r = csv.reader(f, delimiter=delimiter)
                rows = [row for row in r if row]
                n = max((len(x) for x in rows), default=0)
                header = ["c%d" % i for i in range(n)]
                records = [dict(zip(header, row)) for row in rows]
    keyname = resolve_key(key, header)
    idx = {}
    dups = 0
    for rec in records:
        kv = rec.get(keyname, "")
        if kv in idx:
            dups += 1
            continue
        idx[kv] = rec
    if dups:
        sys.stderr.write("warning: %d duplicate key values skipped in %s\n" % (dups, path))
    ignore_set = set(ignore)
    return header, idx, ignore_set


def diff(old_header, old_idx, new_header, new_idx, ignore_set):
    added = [k for k in new_idx if k not in old_idx]
    removed = [k for k in old_idx if k not in new_idx]
    changed = []
    cols = [c for c in new_header if c not in ignore_set]
    for k in new_idx:
        if k in old_idx:
            o, n = old_idx[k], new_idx[k]
            field_diffs = []
            for c in cols:
                ov = o.get(c, "")
                nv = n.get(c, "")
                if ov != nv:
                    field_diffs.append((c, ov, nv))
            if field_diffs:
                changed.append((k, field_diffs))
    return added, removed, changed


def print_text(added, removed, changed, new_idx, old_idx):
    print("=" * 70)
    print("CSVDIFF REPORT")
    print("=" * 70)
    print("ADDED  : %d rows" % len(added))
    print("REMOVED: %d rows" % len(removed))
    print("CHANGED: %d rows" % len(changed))
    print("-" * 70)
    if added:
        print("\n[ADDED]")
        for k in added:
            print("  + %s  %s" % (k, dict(new_idx[k])))
    if removed:
        print("\n[REMOVED]")
        for k in removed:
            print("  - %s  %s" % (k, dict(old_idx[k])))
    if changed:
        print("\n[CHANGED]")
        for k, fds in changed:
            print("  ~ %s" % k)
            for c, ov, nv in fds:
                print("      %s: %r -> %r" % (c, ov, nv))
    print("\n" + "=" * 70)


def print_json(added, removed, changed, new_idx, old_idx):
    out = {
        "added": [{"key": k, "row": new_idx[k]} for k in added],
        "removed": [{"key": k, "row": old_idx[k]} for k in removed],
        "changed": [{"key": k, "fields": [{"column": c, "old": ov, "new": nv}
                    for c, ov, nv in fds]} for k, fds in changed],
        "summary": {"added": len(added), "removed": len(removed), "changed": len(changed)},
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))


def print_md(added, removed, changed, new_idx, old_idx):
    print("# CSV Diff Report\n")
    print("- **Added:** %d  **Removed:** %d  **Changed:** %d\n"
          % (len(added), len(removed), len(changed)))
    if added:
        print("## Added\n")
        for k in added:
            print("- `%s`: `%s`" % (k, json.dumps(new_idx[k], ensure_ascii=False)))
    if removed:
        print("\n## Removed\n")
        for k in removed:
            print("- `%s`: `%s`" % (k, json.dumps(old_idx[k], ensure_ascii=False)))
    if changed:
        print("\n## Changed\n")
        for k, fds in changed:
            print("### %s\n" % k)
            for c, ov, nv in fds:
                print("- `%s`: `%s` → `%s`" % (c, ov, nv))


def print_html(added, removed, changed, new_idx, old_idx):
    parts = ['<html><body><h1>CSV Diff Report</h1>']
    parts.append("<p>Added: %d | Removed: %d | Changed: %d</p>"
                 % (len(added), len(removed), len(changed)))
    if changed:
        parts.append("<h2>Changed</h2><table border=1><tr><th>Key</th><th>Column</th><th>Old</th><th>New</th></tr>")
        for k, fds in changed:
            for c, ov, nv in fds:
                parts.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                             % (k, c, ov, nv))
        parts.append("</table>")
    parts.append("</body></html>")
    print("".join(parts))


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="csvdiff",
        description="Diff two CSV/JSON datasets by key (zero-dependency).")
    p.add_argument("old", help="old file (.csv or .json)")
    p.add_argument("new", help="new file (.csv or .json)")
    p.add_argument("--key", default="0",
                   help="key column name or 0-based index (default 0)")
    p.add_argument("--delimiter", default=",", help="CSV delimiter (default ',')")
    p.add_argument("--no-header", action="store_true",
                   help="CSV has no header row (columns named c0,c1,...)")
    p.add_argument("--ignore", action="append", default=[],
                   help="ignore this column when detecting changes (repeatable)")
    p.add_argument("--json", action="store_true", help="output JSON")
    p.add_argument("--md", action="store_true", help="output Markdown")
    p.add_argument("--html", action="store_true", help="output HTML")
    args = p.parse_args(argv)

    oh, oidx, ig = load(args.old, args.delimiter, not args.no_header, args.key, args.ignore)
    nh, nidx, _ = load(args.new, args.delimiter, not args.no_header, args.key, args.ignore)
    added, removed, changed = diff(oh, oidx, nh, nidx, ig)

    if not (added or removed or changed):
        print("No differences found.")
        return 0

    if args.json:
        print_json(added, removed, changed, nidx, oidx)
    elif args.md:
        print_md(added, removed, changed, nidx, oidx)
    elif args.html:
        print_html(added, removed, changed, nidx, oidx)
    else:
        print_text(added, removed, changed, nidx, oidx)
    return 0


if __name__ == "__main__":
    sys.exit(main())

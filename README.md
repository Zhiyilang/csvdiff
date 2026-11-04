# csvdiff

> Diff two CSV/JSON datasets by key — **zero-dependency, cross-platform.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen.svg)](csvdiff.py)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](csvdiff.py)

`csvdiff` aligns two tables (CSV **or** JSON) on a key column and reports exactly
what changed between them: **added rows, removed rows, and column-level edits**.
It is a single Python file using **only the standard library** — no `pip install`,
no pandas, works everywhere Python runs.

> 纯标准库、零第三方依赖的单文件 CSV/JSON 数据对比工具，按关键列对齐，
> 精确报告新增 / 删除 / 变更的字段。QA 对账、ETL 校验、导出比对都能用。

---

## Why csvdiff?

- 🪶 **One file, no dependencies.** Drop `csvdiff.py` anywhere and run it.
- 🔑 **Key-based alignment.** Compares by a real key, not fragile row order.
- 🔁 **CSV *and* JSON.** Same command, auto-detected by file extension.
- 🎯 **Column-level diffs.** Knows *which field* changed, not just "row changed".
- 📋 **4 output formats.** Text (default), JSON (for pipelines), Markdown, HTML.
- 🧹 **Ignore noise.** Skip volatile columns (`--ignore updated_at`) when checking.

## Install / 安装

No install needed. Just download `csvdiff.py`:

```bash
python csvdiff.py old.csv new.csv --key id
```

无需安装，下载 `csvdiff.py` 即可运行。

## Usage / 用法

```bash
python csvdiff.py OLD NEW [options]
```

### Common examples / 常用示例

```bash
# 1. Basic diff on a key column (default key = first column)
python csvdiff.py yesterday.csv today.csv --key id

# 2. JSON files (auto-detected by .json extension)
python csvdiff.py old.json new.json --key user_id

# 3. CSV without a header row (columns become c0, c1, ...)
python csvdiff.py a.csv b.csv --no-header --key c0

# 4. Ignore volatile columns when detecting changes
python csvdiff.py old.csv new.csv --key id --ignore updated_at --ignore last_seen

# 5. Machine-readable output
python csvdiff.py old.csv new.csv --key id --json
python csvdiff.py old.csv new.csv --key id --md
python csvdiff.py old.csv new.csv --key id --html > report.html

# 6. Custom delimiter (e.g. tab-separated)
python csvdiff.py old.tsv new.tsv --delimiter "\t" --key id
```

### Options / 参数

| Option | Description |
|--------|-------------|
| `OLD` / `NEW` | Files to compare (`.csv` or `.json`) |
| `--key COL` | Key column name or 0-based index (default `0`) |
| `--delimiter C` | CSV delimiter (default `,`) |
| `--no-header` | CSV has no header; columns named `c0,c1,...` |
| `--ignore COL` | Ignore a column when detecting changes (repeatable) |
| `--json` | Output JSON |
| `--md` | Output Markdown |
| `--html` | Output HTML |

## Example output / 输出示例

```
======================================================================
CSVDIFF REPORT
======================================================================
ADDED  : 1 rows
REMOVED: 0 rows
CHANGED: 2 rows
----------------------------------------------------------------------

[CHANGED]
  ~ 102
      status: 'active' -> 'suspended'
  ~ 103
      email: 'a@x.com' -> 'a.new@x.com'
      status: 'active' -> 'active'

[ADDED]
  + 201  {'id': '201', 'name': 'New User', 'status': 'active'}
======================================================================
```

## Use cases / 适用场景

- 🧪 **QA / data reconciliation** — did the export change as expected?
- 🔄 **ETL / pipeline validation** — diff source vs target after a transform.
- 📊 **Spreadsheet comparison** — compare two versions of a CSV report.
- 🗃️ **Database snapshots** — diff two JSON dumps of the same table.
- 🤖 **CI checks** — emit JSON and assert no unexpected drift in tests.

## How it works / 原理

1. Load both files into row dictionaries (CSV via `csv`, JSON via `json`).
2. Index rows by the `--key` column (duplicate keys keep the first, rest warned).
3. Classify every key as **added** (only in NEW), **removed** (only in OLD), or
   **changed** (in both but ≥1 non-ignored column differs).
4. Emit a report in your chosen format.

> 按 `--key` 建索引对齐，区分新增 / 删除 / 变更三类；变更会细化到具体哪个字段
> 从什么值变成什么值。`--ignore` 可跳过时间戳等易变列。

## License

[MIT](LICENSE) — free for personal and commercial use.

---

💝 If csvdiff saved you time, consider supporting its development:
**爱发电 / Afdian → https://afdian.com/a/Zhiyilang** · ⭐ Star the repo!

<!-- cross-links -->

## 🔗 More zero-dependency tools

All of these are single-file, pure Python-stdlib CLIs — offline, no `pip install`, cross-platform:

- **billfusion** — Bill / CSV merging · <https://github.com/Zhiyilang/billfusion>
- **lanshare** — LAN file transfer · <https://github.com/Zhiyilang/lanshare>
- **dupescan** — Duplicate file finder · <https://github.com/Zhiyilang/dupescan>
- **md2html** — Markdown to HTML · <https://github.com/Zhiyilang/md2html>
- **dirsize** — Directory size analyzer · <https://github.com/Zhiyilang/dirsize>

Full portfolio & docs: <https://zhiyilang.github.io/>

import importlib
m = importlib.import_module("csvdiff")
assert hasattr(m, "main") and callable(m.main), "main() missing in csvdiff"
print("selftest OK: csvdiff importable, main() callable")

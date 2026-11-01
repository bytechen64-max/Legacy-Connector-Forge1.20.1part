"""Mechanical 1.21 -> 1.20.1 accessor renames across the shim."""
import os
import re

RENAMES = [
    # FoodProperties accessors
    (".nutrition()", ".getNutrition()"),
    (".saturation()", ".getSaturationModifier()"),
    # AttributeModifier accessors
    (".operation()", ".getOperation()"),
    (".amount()", ".getAmount()"),
    # a connection's Connection is a field on 1.20.1
    (".connection.getConnection()", ".connection.connection"),
    # a File has no toFile()
    ("getServerDirectory().toFile()", "getServerDirectory()"),
]

counts = {}
changed = []
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        src = open(p, encoding="utf-8").read()
        before = src
        for old, new in RENAMES:
            n = src.count(old)
            if n:
                counts[old] = counts.get(old, 0) + n
                src = src.replace(old, new)
        if src != before:
            open(p, "w", encoding="utf-8", newline="").write(src)
            changed.append(p)

for old, new in RENAMES:
    print(f"{counts.get(old, 0):4}  {old}  ->  {new}")
print("files changed:", len(changed))

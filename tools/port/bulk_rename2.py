"""The delta tracker, effect holders and armor materials: 1.20.1 exposes the plain objects."""
import os
import re

RENAMES = [
    (".getTimer().getGameTimeDeltaPartialTick(true)", ".getFrameTime()"),
    (".getTimer().getGameTimeDeltaPartialTick(false)", ".getFrameTime()"),
    (".getTimer().getGameTimeDeltaTicks()", ".getDeltaFrameTime()"),
    (".getEffect().value()", ".getEffect()"),
    (".getMaterial().value()", ".getMaterial()"),
]
REGEXES = [
    (re.compile(r"ArmorMaterials\.([A-Z_]+)\.value\(\)"), r"ArmorMaterials.\1"),
]

counts = {}
changed = set()
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
        for rx, repl in REGEXES:
            src, n = rx.subn(repl, src)
            if n:
                counts[rx.pattern] = counts.get(rx.pattern, 0) + n
        if src != before:
            open(p, "w", encoding="utf-8", newline="").write(src)
            changed.add(p)

for old, new in RENAMES:
    print(f"{counts.get(old, 0):4}  {old}  ->  {new}")
for rx, _ in REGEXES:
    print(f"{counts.get(rx.pattern, 0):4}  {rx.pattern}")
print("files changed:", len(changed))

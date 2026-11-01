"""1.20.1's setLootTable takes the location itself: there is no LOOT_TABLE registry."""
import os
import re

# single-line form: ResourceKey.create(Registries.LOOT_TABLE, <expr>)
SINGLE = re.compile(r"net\.minecraft\.resources\.ResourceKey\.create\(net\.minecraft\.core\.registries\.Registries\.LOOT_TABLE,\s*([^,()]+(?:\([^()]*\))?[^,()]*)\)")
# multi-line form: the key creation spans lines
MULTI = re.compile(r"net\.minecraft\.resources\.ResourceKey\.create\(net\.minecraft\.core\.registries\.Registries\.LOOT_TABLE,\s*\n\s*([^;]+?)\)")

counts = {"single": 0, "multi": 0}
changed = []
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        src = open(p, encoding="utf-8").read()
        if "Registries.LOOT_TABLE" not in src:
            continue
        before = src
        src, n = SINGLE.subn(r"\1", src)
        counts["single"] += n
        src, n = MULTI.subn(r"\1", src)
        counts["multi"] += n
        if src != before:
            open(p, "w", encoding="utf-8", newline="").write(src)
            changed.append(p)

print(counts)
for c in changed:
    print("  ", c)
print("left:", sum(src_c for src_c in [0]))

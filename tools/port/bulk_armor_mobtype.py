"""Armor materials are plain objects and mob types carry the undead/arthropod/illager split on 1.20.1."""
import os
import re
import sys

# 1.20.1's ArmorMaterials are ArmorMaterial instances, not holders
MAT = re.compile(r"mat\.is\((net\.minecraft\.world\.item\.ArmorMaterials\.[A-Z_]+)\)")

# EntityTypeTags has no UNDEAD/ARTHROPOD/ILLAGER on 1.20.1: LivingEntity.getMobType() is the split
TAG = {
    "UNDEAD": "UNDEAD",
    "ARTHROPOD": "ARTHROPOD",
    "ILLAGER": "ILLAGER",
}

counts = {"mat": 0, "tag": 0}
changed = []
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        src = open(p, encoding="utf-8").read()
        before = src
        src, n = MAT.subn(r"mat == \1", src)
        counts["mat"] += n
        for tag in TAG:
            old = f"l.getType().is(net.minecraft.tags.EntityTypeTags.{tag})"
            new = f"l.getMobType() == net.minecraft.world.entity.MobType.{tag}"
            n = src.count(old)
            if n:
                counts["tag"] += n
                src = src.replace(old, new)
        if src != before:
            open(p, "w", encoding="utf-8", newline="").write(src)
            changed.append(p)

print(counts)
for c in changed:
    print("  ", c)

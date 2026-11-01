"""Bulk 1.21 -> 1.20.1 renames that are safe as plain text substitutions."""
import os
import sys

RENAMES = [
    # 1.21 renamed the attribute operations; 1.20.1 keeps the old names
    ("AttributeModifier.Operation.ADD_VALUE", "AttributeModifier.Operation.ADDITION"),
    ("AttributeModifier.Operation.ADD_MULTIPLIED_BASE", "AttributeModifier.Operation.MULTIPLY_BASE"),
    ("AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL", "AttributeModifier.Operation.MULTIPLY_TOTAL"),
    ("Operation.ADD_VALUE", "Operation.ADDITION"),
    ("Operation.ADD_MULTIPLIED_BASE", "Operation.MULTIPLY_BASE"),
    ("Operation.ADD_MULTIPLIED_TOTAL", "Operation.MULTIPLY_TOTAL"),
    # 1.20.1's NBT accountant has a constant instead of unlimitedHeap()
    ("NbtAccounter.unlimitedHeap()", "NbtAccounter.UNLIMITED"),
    # 1.20.1 keeps the tree growers under their pre-1.20.5 name
    ("net.minecraft.world.level.block.grower.TreeGrower", "net.minecraft.world.level.block.grower.AbstractTreeGrower"),
    # 1.20.5+ moved the option screens into their own package
    ("net.minecraft.client.gui.screens.options.", "net.minecraft.client.gui.screens."),
]

counts = {}
changed_files = set()
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
            changed_files.add(p)

for old, new in RENAMES:
    print(f"{counts.get(old, 0):4}  {old}  ->  {new.split('.')[-1]}")
print("files changed:", len(changed_files))

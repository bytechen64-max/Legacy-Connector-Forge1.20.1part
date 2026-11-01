"""Small 1.21 -> 1.20.1 renames: lerpTo's teleport flag, stack comparison, the short grass block."""
import os
import re

LERP = re.compile(r"\.lerpTo\(([^()]*(?:\([^()]*\)[^()]*)*)\)")


def fix_lerp(m: "re.Match[str]") -> str:
    args = m.group(1)
    depth = 0
    commas = 0
    for c in args:
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif c == "," and depth == 0:
            commas += 1
    if commas == 5:
        return ".lerpTo(" + args + ", false)"
    return m.group(0)


RENAMES = [
    ("isSameItemSameComponents(", "isSameItemSameTags("),
    ("Blocks.SHORT_GRASS", "Blocks.GRASS"),
    ("net.minecraft.world.level.block.Blocks.SHORT_GRASS", "net.minecraft.world.level.block.Blocks.GRASS"),
]

lerp_count = 0
changed = []
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        src = open(p, encoding="utf-8").read()
        before = src
        for old, new in RENAMES:
            src = src.replace(old, new)
        src, n = LERP.subn(fix_lerp, src)
        lerp_count += n
        if src != before:
            open(p, "w", encoding="utf-8", newline="").write(src)
            changed.append(p)

print("lerpTo calls with the flag added:", lerp_count)
print("files changed:", len(changed))

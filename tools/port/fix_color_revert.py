"""Reverts the setColor->color rename where the receiver is a GuiGraphics or the shim's own model material."""
import os

REVERSALS = [
    ("f.gui.color(", "f.gui.setColor("),
    ("gui.color(red, green, blue, alpha)", "gui.setColor(red, green, blue, alpha)"),
    ("m.color(c)", "m.setColor(c)"),
    ("material.color(new Vector4f(", "material.setColor(new Vector4f("),
]

counts = {}
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        src = open(p, encoding="utf-8").read()
        before = src
        for old, new in REVERSALS:
            n = src.count(old)
            if n:
                counts[old] = counts.get(old, 0) + n
                src = src.replace(old, new)
        if src != before:
            open(p, "w", encoding="utf-8", newline="").write(src)

for old, new in REVERSALS:
    print(f"{counts.get(old, 0):3}  {old}  ->  {new}")

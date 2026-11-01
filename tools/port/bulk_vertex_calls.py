"""1.20.1's VertexConsumer takes a Matrix4f for posed vertices, and the banner/firework/enchantment data live in item tags."""
import os
import re
import sys

# ---- vertex calls: addVertex(Pose, x, y, z) -> vertex(Matrix4f, x, y, z)
VERTEX = re.compile(r"\.addVertex\((last|pose\.last\(\)), ")
UV = re.compile(r"\.setUv\(")
NORMAL = re.compile(r"\.setNormal\(last, ([^,]+, [^,]+, [^)]+)\)")
COLOR = re.compile(r"\.setColor\(([^)]+)\)")

counts = {"vertex": 0, "uv": 0, "normal": 0, "color": 0}
changed = []
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        src = open(p, encoding="utf-8").read()
        if ".addVertex(" not in src and ".setNormal(" not in src:
            continue
        before = src
        src, n = VERTEX.subn(lambda m: ".vertex(" + (m.group(1) + ".pose()" if m.group(1) == "last" else "pose.last().pose()") + ", ", src)
        counts["vertex"] += n
        src, n = UV.subn(".uv(", src)
        counts["uv"] += n
        src, n = NORMAL.subn(r".normal(\1)", src)
        counts["normal"] += n
        src, n = COLOR.subn(r".color(\1)", src)
        counts["color"] += n
        if src != before:
            open(p, "w", encoding="utf-8", newline="").write(src)
            changed.append(p)

print(counts)
print("files changed:", len(changed))

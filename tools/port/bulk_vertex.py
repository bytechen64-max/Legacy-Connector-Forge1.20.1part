"""1.20.1's VertexConsumer still uses vertex/color/uv/overlayCoords/uv2/normal/endVertex (1.21 renamed them)."""
import os
import re

LITERAL = [
    (".addVertex(", ".vertex("),
    (".setUv(", ".uv("),
    (".setUv1(", ".overlayCoords("),
    (".setUv2(", ".uv2("),
]

# only the three-float form belongs to VertexConsumer; the shim's own models have setNormal(Normal)
SET_NORMAL = re.compile(r"\.setNormal\(([^(),]+), ([^(),]+), ([^(),]+)\)")
ADD_VERTEX_DECL = re.compile(r"public VertexConsumer addVertex\(float (\w+), float (\w+), float (\w+)\)")
SET_NORMAL_DECL = re.compile(r"public VertexConsumer setNormal\(float (\w+), float (\w+), float (\w+)\)")

counts = {}
changed = []
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        src = open(p, encoding="utf-8").read()
        before = src
        for old, new in LITERAL:
            n = src.count(old)
            if n:
                counts[old] = counts.get(old, 0) + n
                src = src.replace(old, new)
        # declarations inside VertexConsumer implementations
        src, n = ADD_VERTEX_DECL.subn(r"public VertexConsumer vertex(double \1, double \2, double \3)", src)
        counts["addVertex decl"] = counts.get("addVertex decl", 0) + n
        src, n = SET_NORMAL_DECL.subn(r"public VertexConsumer normal(float \1, float \2, float \3)", src)
        counts["setNormal decl"] = counts.get("setNormal decl", 0) + n
        src, n = SET_NORMAL.subn(r".normal(\1, \2, \3)", src)
        counts["setNormal call"] = counts.get("setNormal call", 0) + n
        if src != before:
            open(p, "w", encoding="utf-8", newline="").write(src)
            changed.append(p)

for k, v in counts.items():
    print(f"{v:4}  {k}")
print("files changed:", len(changed))

"""Repairs the two loot table lines the multi-line substitution clipped."""
P = r"src/main/java/legacyconnector/v1_12_2/net/minecraft/world/gen/structure/StructureComponent.java"
src = open(P, encoding="utf-8").read()
fixes = [
    ("fromNamespaceAndPath(resourceLocationIn.getNamespace(, resourceLocationIn.getPath())",
     "fromNamespaceAndPath(resourceLocationIn.getNamespace(), resourceLocationIn.getPath())"),
    ("fromNamespaceAndPath(lootTableIn.getNamespace(, lootTableIn.getPath())",
     "fromNamespaceAndPath(lootTableIn.getNamespace(), lootTableIn.getPath())"),
]
for old, new in fixes:
    n = src.count(old)
    print(f"{n}  {old[:60]}")
    src = src.replace(old, new)
open(P, "w", encoding="utf-8", newline="").write(src)

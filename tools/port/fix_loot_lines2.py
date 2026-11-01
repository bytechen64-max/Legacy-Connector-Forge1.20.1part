"""Drops the parenthesis the removed ResourceKey.create( left behind."""
P = r"src/main/java/legacyconnector/v1_12_2/net/minecraft/world/gen/structure/StructureComponent.java"
src = open(P, encoding="utf-8").read()
fixes = [
    ("resourceLocationIn.getNamespace(), resourceLocationIn.getPath())), rand",
     "resourceLocationIn.getNamespace(), resourceLocationIn.getPath()), rand"),
    ("lootTableIn.getNamespace(), lootTableIn.getPath())), rand",
     "lootTableIn.getNamespace(), lootTableIn.getPath()), rand"),
]
for old, new in fixes:
    n = src.count(old)
    print(f"{n}  {old[:60]}")
    src = src.replace(old, new)
open(P, "w", encoding="utf-8", newline="").write(src)

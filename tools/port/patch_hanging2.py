"""Redundant pattern variables in EntityHanging (the value already has the type)."""
import sys

P = r"src/main/java/legacyconnector/v1_7_10/net/minecraft/entity/EntityHanging.java"
src = open(P, encoding="utf-8").read()
pairs = [
    ("        return a instanceof HangingEntity h ? a.getPos().relative(h.getDirection().getOpposite()) : a.getPos();",
     "        // a is already a HangingEntity, so the pattern is redundant.\n"
     "        return a.getPos().relative(a.getDirection().getOpposite());"),
    ("        if (mcc$attached() instanceof HangingEntity h && h.getDirection().getAxis().isHorizontal()) mcc$local_hangingDirection = h.getDirection().get2DDataValue();",
     "        HangingEntity h = mcc$attached();\n"
     "        if (h != null && h.getDirection().getAxis().isHorizontal()) mcc$local_hangingDirection = h.getDirection().get2DDataValue();"),
    ("        if (a instanceof HangingEntity h) {",
     "        if (a != null) {\n            HangingEntity h = a;"),
    ("        if (e.mcc$attached() instanceof HangingEntity h && h.getPos() != null && h.getDirection().getAxis().isHorizontal()) return h.getDirection().get2DDataValue();",
     "        HangingEntity h = e.mcc$attached();\n"
     "        if (h != null && h.getPos() != null && h.getDirection().getAxis().isHorizontal()) return h.getDirection().get2DDataValue();"),
]

for old, new in pairs:
    n = src.count(old)
    if n != 1:
        print(f"ABORT {n}: {old.strip()[:60]}")
        sys.exit(1)
    src = src.replace(old, new)
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P)

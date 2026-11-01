"""LivingEntity takes a MobEffect in 1.20.1 (the Holder-based overloads arrived with 1.20.5)."""
import sys

P = r"src/main/java/legacyconnector/v1_12_2/net/minecraft/entity/EntityLivingBase.java"
src = open(P, encoding="utf-8").read()
pairs = [
    ("        return l != null && holder != null && l.hasEffect(holder);",
     "        // 1.20.1 looks effects up by the MobEffect itself; 1.20.5 moved these to Holder<MobEffect>.\n"
     "        return l != null && holder != null && l.hasEffect(holder.value());"),
    ("        var e = l.getEffect(holder);", "        var e = l.getEffect(holder.value());"),
    ("        if (l != null && holder != null) l.removeEffect(holder);",
     "        if (l != null && holder != null) l.removeEffect(holder.value());"),
]
for old, new in pairs:
    if src.count(old) != 1:
        print("ABORT", src.count(old), old.strip()[:60])
        sys.exit(1)
    src = src.replace(old, new)
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P)

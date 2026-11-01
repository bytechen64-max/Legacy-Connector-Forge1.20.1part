"""NeoForge's FinalizeSpawnEvent is 1.20.1's MobSpawnEvent.FinalizeSpawn, and post() returns a boolean."""
import sys

P = r"src/main/java/legacyconnector/v1_12_2/net/minecraftforge/event/ForgeEventFactory.java"
src = open(P, encoding="utf-8").read()
pairs = [
    ("        var event = new net.minecraftforge.event.entity.living.FinalizeSpawnEvent(mob, accessor, x, y, z,\n"
     "                accessor.getCurrentDifficultyAt(mob.blockPosition()), net.minecraft.world.entity.MobSpawnType.NATURAL, null, null);\n"
     "        return net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(event).isCanceled();",
     "        // 1.20.1 has MobSpawnEvent.FinalizeSpawn (which also carries the spawner) and post() returns a boolean.\n"
     "        var event = new net.minecraftforge.event.entity.living.MobSpawnEvent.FinalizeSpawn(mob, accessor, x, y, z,\n"
     "                accessor.getCurrentDifficultyAt(mob.blockPosition()), net.minecraft.world.entity.MobSpawnType.NATURAL, null, null, null);\n"
     "        return net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(event);"),
]
for old, new in pairs:
    n = src.count(old)
    if n != 1:
        print(f"ABORT {n}: {old.strip()[:70]}")
        sys.exit(1)
    src = src.replace(old, new)
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P)

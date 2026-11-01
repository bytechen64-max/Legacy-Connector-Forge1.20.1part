"""Small 1.21 -> 1.20.1 renames: Explosion fields, LevelData spawn, the client delta tracker."""
import sys

EDITS = {
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/world/Explosion.java": [
        ("        this(world, entity, modern.center().x, modern.center().y, modern.center().z, modern.radius(), false, modern.interactsWithBlocks());",
         "        // 1.21 exposes the explosion as a record (center/radius); 1.20.1 keeps fields behind getters.\n"
         "        this(world, entity, modern.getPosition().x, modern.getPosition().y, modern.getPosition().z, modern.radius(), false,\n"
         "                modern.interactsWithBlocks());"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/world/storage/WorldInfo.java": [
        ("        return level != null ? level.getLevelData().getSpawnPos().getX() : spawnX;",
         "        return level != null ? level.getLevelData().getXSpawn() : spawnX;"),
        ("        return level != null ? level.getLevelData().getSpawnPos().getY() : spawnY;",
         "        return level != null ? level.getLevelData().getYSpawn() : spawnY;"),
        ("        return level != null ? level.getLevelData().getSpawnPos().getZ() : spawnZ;",
         "        return level != null ? level.getLevelData().getZSpawn() : spawnZ;"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/client/Minecraft.java": [
        ("        return mc().getTimer().getGameTimeDeltaPartialTick(false);",
         "        // 1.20.5 replaced the float frame time with a DeltaTracker.\n"
         "        return mc().getFrameTime();"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/util/Timer.java": [
        ("        static float partialTick() {\n"
         "            return net.minecraft.client.Minecraft.getInstance().getTimer().getGameTimeDeltaPartialTick(true);\n"
         "        }",
         "        static float partialTick() {\n"
         "            return net.minecraft.client.Minecraft.getInstance().getFrameTime();\n"
         "        }"),
        ("        static float elapsed() {\n"
         "            return net.minecraft.client.Minecraft.getInstance().getTimer().getGameTimeDeltaTicks();\n"
         "        }",
         "        static float elapsed() {\n"
         "            return net.minecraft.client.Minecraft.getInstance().getDeltaFrameTime();\n"
         "        }"),
    ],
}

for path, pairs in EDITS.items():
    src = open(path, encoding="utf-8").read()
    for old, new in pairs:
        n = src.count(old)
        if n != 1:
            print(f"ABORT {n} matches in {path}: {old.splitlines()[0][:70]!r}")
            sys.exit(1)
        src = src.replace(old, new)
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

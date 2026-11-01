"""1.20.1 has no LiquidSettings (structure liquid handling), no SavedData.Factory, and a File server directory."""
import sys

EDITS = {
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/LegacyVillagePoolElement.java": [
        ("import net.minecraft.world.level.levelgen.structure.templatesystem.LiquidSettings;\n", ""),
        ("            BlockPos offset, BlockPos pivot, Rotation rotation, BoundingBox box, RandomSource random, LiquidSettings liquidSettings, boolean keepJigsaws) {",
         "            BlockPos offset, BlockPos pivot, Rotation rotation, BoundingBox box, RandomSource random, boolean keepJigsaws) {"),
        ("", ""),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/LegacyVillageAdditions.java": [
        ("import net.minecraft.world.level.levelgen.structure.templatesystem.LiquidSettings;\n", ""),
        ("rotationOf(mode), box, LiquidSettings.IGNORE_WATERLOGGING));", "rotationOf(mode), box));"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/world/storage/MapStorage.java": [
        ("            adapter = storage.get(new SavedData.Factory<>(() -> new Adapter(create(clazz, dataIdentifier)),\n"
         "                    (tag, registries) -> Adapter.load(create(clazz, dataIdentifier), tag), null), file(dataIdentifier));",
         "            // 1.20.1's storage reads through a tag-to-data function (the Factory record is 1.20.2+).\n"
         "            adapter = storage.get(tag -> Adapter.load(create(clazz, dataIdentifier), tag), file(dataIdentifier));"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/server/MinecraftServer.java": [
        ("        return m == null ? new long[100] : m.getTickTimesNanos();",
         "        return m == null ? new long[100] : m.tickTimes;"),
        ("        return m == null ? new java.io.File(\"saves\") : m.getServerDirectory().resolve(\"saves\").toFile();",
         "        return m == null ? new java.io.File(\"saves\") : new java.io.File(m.getServerDirectory(), \"saves\");"),
        ("        return server == null ? net.minecraftforge.fml.loading.FMLPaths.GAMEDIR.get().toFile() : server.getServerDirectory().toFile();",
         "        return server == null ? net.minecraftforge.fml.loading.FMLPaths.GAMEDIR.get().toFile() : server.getServerDirectory();"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/world/storage/loot/LootPool.java": [
        ("            var modernContext = new net.minecraft.world.level.storage.loot.LootContext.Builder(params).create(java.util.Optional.empty());",
         "            var modernContext = new net.minecraft.world.level.storage.loot.LootContext.Builder(params).create((net.minecraft.resources.ResourceLocation) null);"),
    ],
}

for path, pairs in EDITS.items():
    src = open(path, encoding="utf-8").read()
    for old, new in pairs:
        if old == new:
            continue
        n = src.count(old)
        if n != 1:
            print(f"ABORT {n} matches in {path}: {old.strip()[:70]}")
            sys.exit(1)
        src = src.replace(old, new)
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

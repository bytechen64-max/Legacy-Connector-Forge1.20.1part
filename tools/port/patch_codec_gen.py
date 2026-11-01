"""1.20.1 generator/biome codecs are Codecs, items take one use-duration argument, the mob loot table is a location."""
import sys

EDITS = {
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/dimension/LegacyChunkGenerator.java": [
        ("""    protected MapCodec<? extends ChunkGenerator> codec() {
        return CODEC;
    }""",
         """    protected com.mojang.serialization.Codec<? extends ChunkGenerator> codec() {
        // 1.20.1 codecs are plain Codecs (MapCodec is 1.20.5+).
        return CODEC.codec();
    }"""),
        ("    public CompletableFuture<ChunkAccess> fillFromNoise(Blender blender, RandomState random, StructureManager structures, ChunkAccess chunk) {",
         "    public CompletableFuture<ChunkAccess> fillFromNoise(java.util.concurrent.Executor executor, Blender blender, RandomState random,\n"
         "            StructureManager structures, ChunkAccess chunk) {"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/dimension/LegacyChunkGenerator1122.java": [
        ("""    protected MapCodec<? extends ChunkGenerator> codec() {
        return CODEC;
    }""",
         """    protected com.mojang.serialization.Codec<? extends ChunkGenerator> codec() {
        // 1.20.1 codecs are plain Codecs (MapCodec is 1.20.5+).
        return CODEC.codec();
    }"""),
        ("    public CompletableFuture<ChunkAccess> fillFromNoise(Blender blender, RandomState random, StructureManager structures, ChunkAccess chunk) {",
         "    public CompletableFuture<ChunkAccess> fillFromNoise(java.util.concurrent.Executor executor, Blender blender, RandomState random,\n"
         "            StructureManager structures, ChunkAccess chunk) {"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/dimension/LegacyBiomeSource.java": [
        ("""    protected MapCodec<? extends BiomeSource> codec() {
        return CODEC;
    }""",
         """    protected com.mojang.serialization.Codec<? extends BiomeSource> codec() {
        return CODEC.codec();
    }"""),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/LegacyLayeredBiomeSource.java": [
        ("""    protected MapCodec<? extends BiomeSource> codec() {
        return CODEC;
    }""",
         """    protected com.mojang.serialization.Codec<? extends BiomeSource> codec() {
        return CODEC.codec();
    }"""),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/adapter/LegacyItemAdapter.java": [
        ("    public int getUseDuration(ItemStack stack, LivingEntity entity) {",
         "    public int getUseDuration(ItemStack stack) {"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/adapter/LegacyBlockItemAdapter.java": [
        ("    public int getUseDuration(ItemStack stack, LivingEntity entity) {",
         "    public int getUseDuration(ItemStack stack) {"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/entity/MobHost1122.java": [
        ("""    protected net.minecraft.resources.ResourceKey<net.minecraft.world.level.storage.loot.LootTable> getDefaultLootTable() {
        if (legacy instanceof EntityLiving l) {
            var table = l.mcc$lootTable();
            if (table != null) {
                return net.minecraft.resources.ResourceKey.create(net.minecraft.core.registries.Registries.LOOT_TABLE,
                        net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(org.kylepitcock.legacyconnector.core.Ids.modernModId(table.getNamespace()),
                                table.getPath()));
            }
        }
        return super.getDefaultLootTable();""",
         """    protected net.minecraft.resources.ResourceLocation getDefaultLootTable() {
        // 1.20.1 names the default loot table by location (the ResourceKey form is 1.20.5+).
        if (legacy instanceof EntityLiving l) {
            var table = l.mcc$lootTable();
            if (table != null) {
                return net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(
                        org.kylepitcock.legacyconnector.core.Ids.modernModId(table.getNamespace()), table.getPath());
            }
        }
        return super.getDefaultLootTable();"""),
    ],
    r"src/main/java/legacyconnector/v1_7_10/net/minecraft/world/storage/MapStorage.java": [
        ("        public CompoundTag save(CompoundTag tag, HolderLookup.Provider registries) {",
         "        public CompoundTag save(CompoundTag tag) {"),
    ],
}

for path, pairs in EDITS.items():
    src = open(path, encoding="utf-8").read()
    for old, new in pairs:
        n = src.count(old)
        if n != 1:
            print(f"ABORT {n} in {path}: {old.strip()[:70]}")
            sys.exit(1)
        src = src.replace(old, new)
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

"""1.20.1 block entity loading, loot modifier codecs, effect ticks, lerpTo declarations and dimension effects."""
import os
import sys

# ---- 1.20.1 has load(tag), not loadAdditional(tag)
files = []
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        src = open(p, encoding="utf-8").read()
        if "loadAdditional" not in src:
            continue
        before = src
        src = src.replace("protected void loadAdditional(CompoundTag tag) {", "public void load(CompoundTag tag) {")
        src = src.replace("super.loadAdditional(tag);", "super.load(tag);")
        if src != before:
            open(p, "w", encoding="utf-8", newline="").write(src)
            files.append(p)
print("loadAdditional -> load:", files)

EDITS = {
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/adapter/Legacy1122BlockEntity.java": [
        ("""    @Override
    public void onDataPacket(net.minecraft.network.Connection net, net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket pkt,
            HolderLookup.Provider registries) {""",
         """    @Override
    public void onDataPacket(net.minecraft.network.Connection net, net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket pkt) {"""),
        ("            super.onDataPacket(net, pkt, registries);", "            super.onDataPacket(net, pkt);"),
    ],
    # 1.20.1's renderer has no getRenderBoundingBox (it was dropped after 1.16)
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/client/LegacyBlockEntityRenderer1122.java": [
        ("""    @Override
    public AABB getRenderBoundingBox(Legacy1122BlockEntity be) {""",
         """    // 1.20.1 has no getRenderBoundingBox on BlockEntityRenderer (the shim keeps it for its own callers).
    public AABB getRenderBoundingBox(Legacy1122BlockEntity be) {"""),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/LegacyBlockEntityRenderer.java": [
        ("""    @Override
    public net.minecraft.world.phys.AABB getRenderBoundingBox(LegacyBlockEntity be) {""",
         """    // 1.20.1 has no getRenderBoundingBox on BlockEntityRenderer (the shim keeps it for its own callers).
    public net.minecraft.world.phys.AABB getRenderBoundingBox(LegacyBlockEntity be) {"""),
    ],
    # the global loot modifier codec is a Codec on 1.20.1
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/LegacyFishingLoot.java": [
        ("""    public MapCodec<? extends IGlobalLootModifier> codec() {
        return CODEC;
    }""",
         """    public com.mojang.serialization.Codec<? extends IGlobalLootModifier> codec() {
        // 1.20.1 codecs are plain Codecs (MapCodec is 1.20.5+).
        return CODEC.codec();
    }"""),
    ],
    # effect ticks: void return and the 1.20.1 predicate name
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/PotionBridge.java": [
        ("    public boolean shouldApplyEffectTickThisTick(int duration, int amplifier) {",
         "    public boolean isDurationEffectTick(int duration, int amplifier) {"),
        ("    public boolean applyEffectTick(LivingEntity entity, int amplifier) {",
         "    public void applyEffectTick(LivingEntity entity, int amplifier) {"),
    ],
    # the lerpTo declarations need the teleport flag too
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/entity/EntityHost1122.java": [
        ("    public void lerpTo(double x, double y, double z, float yaw, float pitch, int steps) {",
         "    public void lerpTo(double x, double y, double z, float yaw, float pitch, int steps, boolean teleport) {"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/entity/LegacyEntityHost.java": [
        ("    public void lerpTo(double x, double y, double z, float yaw, float pitch, int steps) {",
         "    public void lerpTo(double x, double y, double z, float yaw, float pitch, int steps, boolean teleport) {"),
    ],
    # dimension effects take the pose stack, not a model-view matrix
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/LegacyDimensionEffects.java": [
        ("    public boolean renderSky(ClientLevel level, int ticks, float partialTick, Matrix4f modelView, Camera camera, Matrix4f projection, boolean fog,",
         "    public boolean renderSky(ClientLevel level, int ticks, float partialTick, com.mojang.blaze3d.vertex.PoseStack pose, Camera camera, Matrix4f projection, boolean fog,"),
        ("    public boolean renderClouds(ClientLevel level, int ticks, float partialTick, PoseStack pose, double camX, double camY, double camZ, Matrix4f",
         "    public boolean renderClouds(ClientLevel level, int ticks, float partialTick, PoseStack pose, double camX, double camY, double camZ, Matrix4f"),
    ],
    # 1.20.1 Forge's exp drop hook
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/adapter/Legacy1122Block.java": [
        ("    public int getExpDrop(BlockState state, LevelAccessor level, BlockPos pos, BlockEntity blockEntity, Entity breaker, net.minecraft.world.item.ItemStack tool) {",
         "    public int getExpDrop(BlockState state, net.minecraft.world.level.LevelReader level, net.minecraft.util.RandomSource random,\n"
         "            BlockPos pos, int fortune, int silktouch) {"),
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

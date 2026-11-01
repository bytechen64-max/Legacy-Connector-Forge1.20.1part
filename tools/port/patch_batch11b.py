"""The rest of batch 11 (the onDataPacket super call was already 1.20.1 shaped)."""
import sys

EDITS = {
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/adapter/Legacy1122BlockEntity.java": [
        ("""    @Override
    public void onDataPacket(net.minecraft.network.Connection net, net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket pkt,
            HolderLookup.Provider registries) {""",
         """    @Override
    public void onDataPacket(net.minecraft.network.Connection net, net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket pkt) {"""),
    ],
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
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/LegacyFishingLoot.java": [
        ("""    public MapCodec<? extends IGlobalLootModifier> codec() {
        return CODEC;
    }""",
         """    public com.mojang.serialization.Codec<? extends IGlobalLootModifier> codec() {
        // 1.20.1 codecs are plain Codecs (MapCodec is 1.20.5+).
        return CODEC.codec();
    }"""),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/PotionBridge.java": [
        ("    public boolean shouldApplyEffectTickThisTick(int duration, int amplifier) {",
         "    public boolean isDurationEffectTick(int duration, int amplifier) {"),
        ("    public boolean applyEffectTick(LivingEntity entity, int amplifier) {",
         "    public void applyEffectTick(LivingEntity entity, int amplifier) {"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/entity/EntityHost1122.java": [
        ("    public void lerpTo(double x, double y, double z, float yaw, float pitch, int steps) {",
         "    public void lerpTo(double x, double y, double z, float yaw, float pitch, int steps, boolean teleport) {"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/entity/LegacyEntityHost.java": [
        ("    public void lerpTo(double x, double y, double z, float yaw, float pitch, int steps) {",
         "    public void lerpTo(double x, double y, double z, float yaw, float pitch, int steps, boolean teleport) {"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/LegacyDimensionEffects.java": [
        ("    public boolean renderSky(ClientLevel level, int ticks, float partialTick, Matrix4f modelView, Camera camera, Matrix4f projection, boolean fog,",
         "    public boolean renderSky(ClientLevel level, int ticks, float partialTick, com.mojang.blaze3d.vertex.PoseStack pose, Camera camera, Matrix4f projection, boolean fog,"),
    ],
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

"""Effect tick hooks, block interaction and plant support: 1.20.1 shapes."""
import sys

EDITS = {
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/entity/Effects1122.java": [
        ("""        @Override
        public boolean applyEffectTick(net.minecraft.world.entity.LivingEntity entity, int amplifier) {
            EntityLivingBase target = view(entity);
            if (target == null) return true;
            try {
                potion.performEffect(target, amplifier);
            } catch (RuntimeException | LinkageError e) {
                Hosts1122.failed(potion.getClass(), "performEffect", e);
            }
            return true;
        }

        @Override
        public boolean shouldApplyEffectTickThisTick(int duration, int amplifier) {""",
         """        @Override
        public void applyEffectTick(net.minecraft.world.entity.LivingEntity entity, int amplifier) {
            // 1.20.1's tick hook returns nothing (1.20.5 made the return value meaningful).
            EntityLivingBase target = view(entity);
            if (target == null) return;
            try {
                potion.performEffect(target, amplifier);
            } catch (RuntimeException | LinkageError e) {
                Hosts1122.failed(potion.getClass(), "performEffect", e);
            }
        }

        @Override
        public boolean isDurationEffectTick(int duration, int amplifier) {"""),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/adapter/LegacyBlockAdapter.java": [
        ("""    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        return activate(level, pos, player, hit) ? InteractionResult.sidedSuccess(level.isClientSide) : InteractionResult.PASS;
    }

""", ""),
        ("""    @Override
    public boolean hasDynamicLightEmission(BlockState state) {
        return dynamicLight || super.hasDynamicLightEmission(state);
    }

""", ""),
        ("""    @Override
    public boolean canSustainPlant(BlockState state, BlockGetter level, BlockPos pos, Direction facing, BlockState plant) {
        if (!sustainsPlants || !(plant.getBlock() instanceof LegacyBlockAdapter adapter)
                || !(adapter.legacy() instanceof legacyconnector.v1_7_10.net.minecraftforge.common.IPlantable plantable)) {
            return super.canSustainPlant(state, level, pos, facing, plant);
        }
        try {
            boolean ok = legacy.canSustainPlant(BlockAccessView.of(level), pos.getX(), pos.getY(), pos.getZ(),
                    legacyconnector.v1_7_10.net.minecraftforge.common.util.ForgeDirection.getOrientation(facing.get3DDataValue()), plantable);
            return ok;
        } catch (RuntimeException | LinkageError e) {
            return super.canSustainPlant(state, level, pos, facing, plant);
        }
    }""",
         """    @Override
    public boolean canSustainPlant(BlockState state, BlockGetter level, BlockPos pos, Direction facing,
            net.minecraftforge.common.IPlantable plantable) {
        // 1.20.1 hands the IPlantable in (1.20.5 passes the plant's block state).
        BlockState plant = plantable == null ? null : plantable.getPlant(level, pos.relative(facing));
        if (!sustainsPlants || plant == null || !(plant.getBlock() instanceof LegacyBlockAdapter adapter)
                || !(adapter.legacy() instanceof legacyconnector.v1_7_10.net.minecraftforge.common.IPlantable legacyPlant)) {
            return super.canSustainPlant(state, level, pos, facing, plantable);
        }
        try {
            return legacy.canSustainPlant(BlockAccessView.of(level), pos.getX(), pos.getY(), pos.getZ(),
                    legacyconnector.v1_7_10.net.minecraftforge.common.util.ForgeDirection.getOrientation(facing.get3DDataValue()), legacyPlant);
        } catch (RuntimeException | LinkageError e) {
            return super.canSustainPlant(state, level, pos, facing, plantable);
        }
    }"""),
        ("""    public BlockState playerWillDestroy(Level level, BlockPos pos, BlockState state, Player player) {""",
         """    public void playerWillDestroy(Level level, BlockPos pos, BlockState state, Player player) {"""),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/adapter/Legacy1122Block.java": [
        ("""    public BlockState playerWillDestroy(Level level, BlockPos pos, BlockState state, Player player) {""",
         """    public void playerWillDestroy(Level level, BlockPos pos, BlockState state, Player player) {"""),
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

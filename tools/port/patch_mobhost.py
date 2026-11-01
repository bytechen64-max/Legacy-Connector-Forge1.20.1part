"""1.20.1's Mob signatures: loot drops, experience, lerpTo, spawn finalization and dimensions."""
import sys

P = r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/entity/MobHost1122.java"
src = open(P, encoding="utf-8").read()

pairs = [
    ("    private ServerLevel dropLevel;\n    private DamageSource dropSource;\n    private boolean dropRecentlyHit;",
     "    private int dropLooting;\n    private DamageSource dropSource;\n    private boolean dropRecentlyHit;"),
    ("""    @Override
    protected void dropCustomDeathLoot(ServerLevel level, DamageSource source, boolean recentlyHit) {
        EntityLivingBase l = living();
        if (l == null) {
            super.dropCustomDeathLoot(level, source, recentlyHit);
            return;
        }
        dropLevel = level;
        dropSource = source;
        dropRecentlyHit = recentlyHit;
        try {
            int looting = 0;
            if (source.getEntity() instanceof LivingEntity killer) {
                var enchantments = level.registryAccess().lookupOrThrow(net.minecraft.core.registries.Registries.ENCHANTMENT);
                looting = net.minecraft.world.item.enchantment.EnchantmentHelper.getEnchantmentLevel(
                        enchantments.getOrThrow(net.minecraft.world.item.enchantment.Enchantments.LOOTING), killer);
            }
            var legacySource = legacySource(source);
            looting = ForgeEvents1122.lootingLevel(l, legacySource, looting);
            l.mcc$dropLoot(recentlyHit, looting, legacySource);
        } catch (RuntimeException | LinkageError e) {
            Hosts1122.failed(legacy.getClass(), "dropping its loot", e);
        } finally {
            dropLevel = null;
            dropSource = null;
        }
    }""",
     """    @Override
    protected void dropCustomDeathLoot(DamageSource source, int looting, boolean recentlyHit) {
        // 1.20.1 hands the looting level in (1.21 passed the level and recomputed it from the killer's enchantments).
        EntityLivingBase l = living();
        if (l == null) {
            super.dropCustomDeathLoot(source, looting, recentlyHit);
            return;
        }
        dropLooting = looting;
        dropSource = source;
        dropRecentlyHit = recentlyHit;
        try {
            var legacySource = legacySource(source);
            int level = ForgeEvents1122.lootingLevel(l, legacySource, looting);
            l.mcc$dropLoot(recentlyHit, level, legacySource);
        } catch (RuntimeException | LinkageError e) {
            Hosts1122.failed(legacy.getClass(), "dropping its loot", e);
        } finally {
            dropSource = null;
        }
    }"""),
    ("        if (dropLevel != null) super.dropCustomDeathLoot(dropLevel, dropSource, dropRecentlyHit);",
     "        if (dropSource != null) super.dropCustomDeathLoot(dropSource, dropLooting, dropRecentlyHit);"),
    ("    protected int getBaseExperienceReward() {", "    protected int getExperienceReward() {"),
    ("        return l != null ? l.mcc$experience() : super.getBaseExperienceReward();",
     "        return l != null ? l.mcc$experience() : super.getExperienceReward();"),
    ("    public void lerpTo(double x, double y, double z, float yaw, float pitch, int steps) {",
     "    public void lerpTo(double x, double y, double z, float yaw, float pitch, int steps, boolean teleport) {"),
    ("        else super.lerpTo(x, y, z, yaw, pitch, steps);", "        else super.lerpTo(x, y, z, yaw, pitch, steps, teleport);"),
    ("""            net.minecraft.world.entity.MobSpawnType type, net.minecraft.world.entity.SpawnGroupData data) {""",
     """            net.minecraft.world.entity.MobSpawnType type, net.minecraft.world.entity.SpawnGroupData data,
            net.minecraft.nbt.CompoundTag tag) {"""),
    ("            return super.finalizeSpawn(level, difficulty, type, data);",
     "            return super.finalizeSpawn(level, difficulty, type, data, tag);"),
    ("    protected EntityDimensions getDefaultDimensions(Pose pose) {\n"
     "        return width > 0 ? EntityDimensions.scalable(width, height) : super.getDefaultDimensions(pose);",
     "    protected EntityDimensions getDimensions(Pose pose) {\n"
     "        return width > 0 ? EntityDimensions.scalable(width, height) : super.getDimensions(pose);"),
]

for old, new in pairs:
    n = src.count(old)
    if n != 1:
        print(f"ABORT {n} matches: {old.splitlines()[0][:70]}")
        sys.exit(1)
    src = src.replace(old, new)
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P)

"""The 1.7.10 mob host needs the same 1.20.1 Mob signatures as the 1.12.2 one."""
import sys

P = r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/entity/LegacyMobHost.java"
src = open(P, encoding="utf-8").read()

pairs = [
    ("    private ServerLevel dropLevel;\n", "    private int dropLooting;\n"),
    ("""    protected void dropCustomDeathLoot(ServerLevel level, DamageSource source, boolean recentlyHit) {
        EntityLivingBase l = living();
        if (l == null) {
            super.dropCustomDeathLoot(level, source, recentlyHit);
            return;
        }
        dropLevel = level;
        dropSource = source;
        dropRecentlyHit = recentlyHit;
        try {
            l.mcc$dropLoot(recentlyHit, 0);
        } finally {
            dropLevel = null;
            dropSource = null;
        }
    }""",
     """    protected void dropCustomDeathLoot(DamageSource source, int looting, boolean recentlyHit) {
        // 1.20.1 hands the looting level in (1.21 passed the level instead).
        EntityLivingBase l = living();
        if (l == null) {
            super.dropCustomDeathLoot(source, looting, recentlyHit);
            return;
        }
        dropLooting = looting;
        dropSource = source;
        dropRecentlyHit = recentlyHit;
        try {
            l.mcc$dropLoot(recentlyHit, looting);
        } finally {
            dropSource = null;
        }
    }"""),
    ("        if (dropLevel != null) super.dropCustomDeathLoot(dropLevel, dropSource, dropRecentlyHit);",
     "        if (dropSource != null) super.dropCustomDeathLoot(dropSource, dropLooting, dropRecentlyHit);"),
    ("    protected int getBaseExperienceReward() {", "    protected int getExperienceReward() {"),
    ("        return legacy instanceof EntityLiving l ? l.mcc$experience() : super.getBaseExperienceReward();",
     "        return legacy instanceof EntityLiving l ? l.mcc$experience() : super.getExperienceReward();"),
    ("    public void lerpTo(double x, double y, double z, float yaw, float pitch, int steps) {",
     "    public void lerpTo(double x, double y, double z, float yaw, float pitch, int steps, boolean teleport) {"),
    ("        else super.lerpTo(x, y, z, yaw, pitch, steps);", "        else super.lerpTo(x, y, z, yaw, pitch, steps, teleport);"),
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

"""The remaining DimensionTransition calls (exact text from the files)."""
import sys

T = "org.kylepitcock.legacyconnector.core.Teleports.changeDimension"
EDITS = {
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/EntityBridge.java": [
        ("""            m.changeDimension(new net.minecraft.world.level.portal.DimensionTransition(target, m.position(), m.getDeltaMovement(), m.getYRot(),
                    m.getXRot(), net.minecraft.world.level.portal.DimensionTransition.DO_NOTHING));""",
         f"            {T}(m, target);"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/server/management/PlayerList.java": [
        ("""            m.changeDimension(new net.minecraft.world.level.portal.DimensionTransition(target, m.position(), m.getDeltaMovement(), m.getYRot(),
                    m.getXRot(), net.minecraft.world.level.portal.DimensionTransition.DO_NOTHING));""",
         f"            {T}(m, target);"),
    ],
    r"src/main/java/legacyconnector/v1_7_10/net/minecraft/server/management/ServerConfigurationManager.java": [
        ("""            var copy = m.changeDimension(new net.minecraft.world.level.portal.DimensionTransition(target, m.position(), m.getDeltaMovement(), yaw,
                    m.getXRot(), net.minecraft.world.level.portal.DimensionTransition.DO_NOTHING));""",
         f"            var copy = {T}(m, target);"),
    ],
}

for path, pairs in EDITS.items():
    src = open(path, encoding="utf-8").read()
    for old, new in pairs:
        n = src.count(old)
        if n != 1:
            print(f"ABORT {n} in {path}")
            sys.exit(1)
        src = src.replace(old, new)
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

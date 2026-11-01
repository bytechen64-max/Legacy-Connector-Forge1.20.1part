"""Redundant SignalGetter patterns and the 1.20.1 enum constants that differ."""
import sys

EDITS = {
    r"src/main/java/legacyconnector/v1_7_10/net/minecraft/world/World.java": [
        ("        return lvl() instanceof SignalGetter s && s.hasNeighborSignal(pos(x, y, z));",
         "        // LevelAccessor already is a SignalGetter on 1.20.1, so the pattern is redundant.\n"
         "        LevelAccessor l = lvl();\n"
         "        return l != null && l.hasNeighborSignal(pos(x, y, z));"),
        ("        return lvl() instanceof SignalGetter s ? s.getBestNeighborSignal(pos(x, y, z)) : 0;",
         "        LevelAccessor l = lvl();\n"
         "        return l == null ? 0 : l.getBestNeighborSignal(pos(x, y, z));"),
        ("        return lvl() instanceof SignalGetter s ? s.getSignal(pos(x, y, z), Direction.from3DDataValue(side)) : 0;",
         "        LevelAccessor l = lvl();\n"
         "        return l == null ? 0 : l.getSignal(pos(x, y, z), Direction.from3DDataValue(side));"),
        ("        return lvl() instanceof SignalGetter s ? s.getDirectSignalTo(pos(x, y, z)) : 0;",
         "        LevelAccessor l = lvl();\n"
         "        return l == null ? 0 : l.getDirectSignalTo(pos(x, y, z));"),
    ],
    r"src/main/java/legacyconnector/v1_7_10/net/minecraft/item/ItemArmor.java": [
        ("                case CHESTPLATE, BODY -> 1;", "                case CHESTPLATE -> 1;"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/pathfinding/PathNodeType.java": [
        ("                case POWDER_SNOW, DANGER_POWDER_SNOW, DAMAGE_CAUTIOUS, DANGER_TRAPDOOR, STICKY_HONEY, COCOA, LEAVES -> DANGER_OTHER;",
         "                // 1.20.1's BlockPathTypes has no POWDER_SNOW/LEAVES constants.\n"
         "                case DANGER_POWDER_SNOW, DAMAGE_CAUTIOUS, DANGER_TRAPDOOR, STICKY_HONEY, COCOA -> DANGER_OTHER;"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraftforge/event/ForgeEventFactory.java": [
        ("        return switch (event.getResult()) {\n"
         "            case SUCCEED -> legacyconnector.v1_12_2.net.minecraftforge.fml.common.eventhandler.Event.Result.ALLOW;\n"
         "            case FAIL -> legacyconnector.v1_12_2.net.minecraftforge.fml.common.eventhandler.Event.Result.DENY;\n"
         "            default -> legacyconnector.v1_12_2.net.minecraftforge.fml.common.eventhandler.Event.Result.DEFAULT;\n"
         "        };",
         "        // 1.21's Result has SUCCEED/FAIL; 1.20.1 has all three states.\n"
         "        return switch (event.getResult()) {\n"
         "            case ALLOW -> legacyconnector.v1_12_2.net.minecraftforge.fml.common.eventhandler.Event.Result.ALLOW;\n"
         "            case DENY -> legacyconnector.v1_12_2.net.minecraftforge.fml.common.eventhandler.Event.Result.DENY;\n"
         "            default -> legacyconnector.v1_12_2.net.minecraftforge.fml.common.eventhandler.Event.Result.DEFAULT;\n"
         "        };"),
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

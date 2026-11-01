"""1.20.1's crop, bonemeal and block-break hooks keep their pre-1.20.5 names and return types."""
import sys

EDITS = {
    r"src/main/java/legacyconnector/v1_12_2/net/minecraftforge/common/ForgeHooks.java": [
        ("        return modern == null ? def : ForgeHooks.canCropGrow(worldIn.mcc$level(), pos(pos), modern, def);",
         "        // 1.20.1 calls these onCropsGrowPre/onCropsGrowPost (renamed in 1.20.5).\n"
         "        return modern == null ? def : ForgeHooks.onCropsGrowPre(worldIn.mcc$level(), pos(pos), modern, def);"),
        ("        if (modern != null) ForgeHooks.fireCropGrowPost(worldIn.mcc$level(), pos(pos), modern);",
         "        if (modern != null) ForgeHooks.onCropsGrowPost(worldIn.mcc$level(), pos(pos), modern);"),
        ("            var event = ForgeHooks.fireBlockBreak(level, gameType == null ? sp.gameMode.getGameModeForPlayer() : gameType.mcc$modern(), sp, p, level.getBlockState(p));",
         "            int event = ForgeHooks.onBlockBreakEvent(level,\n"
         "                    gameType == null ? sp.gameMode.getGameModeForPlayer() : gameType.mcc$modern(), sp, p);"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraftforge/event/ForgeEventFactory.java": [
        ("        var event = net.minecraftforge.event.ForgeEventFactory.fireBonemealEvent(player(player), world.mcc$level(), pos(pos), state(state), Stacks1122.toModern(stack));\n"
         "        if (event.isCanceled()) return -1;\n"
         "        return event.isSuccessful() ? 1 : 0;",
         "        // 1.20.1 answers with -1 (canceled), 1 (another mod applied it) or 0 (grow as usual).\n"
         "        return net.minecraftforge.event.ForgeEventFactory.onApplyBonemeal(player(player), world.mcc$level(), pos(pos),\n"
         "                state(state), Stacks1122.toModern(stack));"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/bridge/EventBridge1122.java": [
        ("                if (wants(TickEvent.RenderTickEvent.class)) post(new TickEvent.RenderTickEvent(TickEvent.Phase.START, e.partialTick));",
         "                if (wants(TickEvent.RenderTickEvent.class)) post(new TickEvent.RenderTickEvent(TickEvent.Phase.START, e.renderTickTime));"),
        ("                if (wants(TickEvent.RenderTickEvent.class)) post(new TickEvent.RenderTickEvent(TickEvent.Phase.END, e.partialTick));",
         "                if (wants(TickEvent.RenderTickEvent.class)) post(new TickEvent.RenderTickEvent(TickEvent.Phase.END, e.renderTickTime));"),
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

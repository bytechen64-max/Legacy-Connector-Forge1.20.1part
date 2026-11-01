"""1.20.1's EventBus.post returns a boolean, so the event object must be kept to read its result."""
import os
import re
import sys

EDITS = {
    r"src/main/java/legacyconnector/v1_12_2/net/minecraftforge/common/ForgeHooks.java": [
        ("""        var modern = net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.entity.player.PlayerInteractEvent.LeftClickBlock(p,
                pos(pos), face == null ? net.minecraft.core.Direction.UP : face.mcc$modern(),
                net.minecraftforge.event.entity.player.PlayerInteractEvent.LeftClickBlock.Action.START));
        if (modern.isCanceled()) {""",
         """        // 1.20.1's EventBus.post returns whether the event ended up canceled (1.21 returns the event).
        var modern = new net.minecraftforge.event.entity.player.PlayerInteractEvent.LeftClickBlock(p,
                pos(pos), face == null ? net.minecraft.core.Direction.UP : face.mcc$modern(),
                net.minecraftforge.event.entity.player.PlayerInteractEvent.LeftClickBlock.Action.START);
        boolean canceled = net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(modern);
        if (canceled) {"""),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraftforge/event/ForgeEventFactory.java": [
        ("""        var event = net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(
                new net.minecraftforge.event.entity.living.MobSpawnEvent.AllowDespawn(mob, level));
        return switch (event.getResult()) {""",
         """        var event = new net.minecraftforge.event.entity.living.MobSpawnEvent.AllowDespawn(mob, level);
        net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(event);
        return switch (event.getResult()) {"""),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/RenderEvents1710.java": [
        ("                    e.getPartialTick().getGameTimeDeltaPartialTick(false)));",
         "                    e.getPartialTick()));"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/compat/dragonapi/DragonApiClientEvents.java": [
        ("            Event ev = ENTITY_RENDERING_LOOP.create(pass, e.getPartialTick().getGameTimeDeltaPartialTick(false));",
         "            Event ev = ENTITY_RENDERING_LOOP.create(pass, e.getPartialTick());"),
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

"""NeoForge's MobDespawnEvent -> 1.20.1's MobSpawnEvent.AllowDespawn."""
import sys

EDITS = {
    r"src/main/java/legacyconnector/v1_12_2/net/minecraftforge/event/ForgeEventFactory.java": [
        ("        var event = net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.entity.living.MobDespawnEvent(mob, level));",
         "        // 1.21's MobDespawnEvent is 1.20.1's MobSpawnEvent.AllowDespawn.\n"
         "        var event = net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(\n"
         "                new net.minecraftforge.event.entity.living.MobSpawnEvent.AllowDespawn(mob, level));"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/entity/ForgeEvents1122.java": [
        ("        game.addListener((net.minecraftforge.event.entity.living.MobDespawnEvent e) -> {",
         "        game.addListener((net.minecraftforge.event.entity.living.MobSpawnEvent.AllowDespawn e) -> {"),
        ("            if (event.getResult() == Event.Result.ALLOW) e.setResult(net.minecraftforge.event.entity.living.MobDespawnEvent.Result.ALLOW);\n"
         "            else if (event.getResult() == Event.Result.DENY) e.setResult(net.minecraftforge.event.entity.living.MobDespawnEvent.Result.DENY);",
         "            // 1.20.1 expresses it as a cancel: DENY keeps the mob alive.\n"
         "            if (event.getResult() == Event.Result.DENY) e.setResult(net.minecraftforge.eventbus.api.Event.Result.DENY);"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/ForgeEvents1710.java": [
        ("        game.addListener((net.minecraftforge.event.entity.living.MobDespawnEvent e) -> {",
         "        game.addListener((net.minecraftforge.event.entity.living.MobSpawnEvent.AllowDespawn e) -> {"),
        ("            if (legacy.getResult() == Event.Result.ALLOW) e.setResult(net.minecraftforge.event.entity.living.MobDespawnEvent.Result.ALLOW);\n"
         "            else if (legacy.getResult() == Event.Result.DENY) e.setResult(net.minecraftforge.event.entity.living.MobDespawnEvent.Result.DENY);",
         "            // 1.20.1 expresses it as a cancel: DENY keeps the mob alive.\n"
         "            if (legacy.getResult() == Event.Result.DENY) e.setResult(net.minecraftforge.eventbus.api.Event.Result.DENY);"),
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

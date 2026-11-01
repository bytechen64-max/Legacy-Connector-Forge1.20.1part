"""Drops the BlockDropsEvent listener in the 1.12.2 bridge (1.20.1 has no such event; see PORTING.md)."""
import sys

P = r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/bridge/EventBridge1122.java"
src = open(P, encoding="utf-8").read()
listener = """        bus.addListener((net.minecraftforge.event.level.BlockDropsEvent e) -> {
            if (!wants(legacyconnector.v1_12_2.net.minecraftforge.event.world.BlockEvent.HarvestDropsEvent.class)) return;
            harvestDrops(e);
        });
"""
if src.count(listener) != 1:
    print("ABORT listener:", src.count(listener))
    sys.exit(1)
src = src.replace(listener, "        // 1.20.1 fires no block drops event (1.20.2+): HarvestDropsEvent needs a global loot modifier instead.\n")

start = src.find("    /**\n     * HarvestDropsEvent over the modern drops")
end = src.find("    private static int dimension(")
if start < 0 or end < 0:
    print("ABORT method range")
    sys.exit(1)
src = src[:start] + src[end:]
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P)

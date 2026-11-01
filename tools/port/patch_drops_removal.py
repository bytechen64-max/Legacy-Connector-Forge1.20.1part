"""1.20.1 has no BlockDropsEvent: the two listeners that needed it are dropped (recorded in PORTING.md)."""
import sys

# GrassSeeds1122: the seed chance cannot be attached to a drops event on 1.20.1
P = r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/bridge/GrassSeeds1122.java"
src = open(P, encoding="utf-8").read()
start = src.find("    private static void onDrops(BlockDropsEvent event) {")
end = src.rfind("}")  # the class's closing brace
if start < 0:
    print("ABORT: onDrops not found")
    sys.exit(1)
src = (src[:start]
       + "    // 1.20.1 has no BlockDropsEvent (it arrived in 1.20.2): the extra seed drops need a global loot modifier,\n"
       + "    // which this shim does not generate yet (see PORTING.md).\n"
       + "}\n")
src = src.replace("            net.minecraftforge.common.MinecraftForge.EVENT_BUS.addListener(BlockDropsEvent.class, GrassSeeds1122::onDrops);\n", "")
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P)

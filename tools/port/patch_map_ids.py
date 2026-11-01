"""Map ids: 1.20.5's MapId component -> the int map id 1.20.1 keeps in the stack tag (and MapItem's static helpers)."""
import sys

# ---------------------------------------------------------------- ItemData: map helpers
P = r"src/main/java/org/kylepitcock/legacyconnector/core/data/ItemData.java"
src = open(P, encoding="utf-8").read()
if "public static int mapId(" not in src:
    ADD = """
    // ------------------------------------------------------------------ map id

    /** The map id a filled map carries, or -1 (1.20.1 keeps it in the stack tag, not in a MapId component). */
    public static int mapId(ItemStack stack) {
        Integer id = stack == null || stack.isEmpty() ? null : MapItem.getMapId(stack);
        return id == null ? -1 : id;
    }

    public static boolean hasMapId(ItemStack stack) {
        return stack != null && !stack.isEmpty() && MapItem.getMapId(stack) != null;
    }

    public static void setMapId(ItemStack stack, int id) {
        if (stack == null || stack.isEmpty()) return;
        stack.getOrCreateTag().putInt("map", id);
    }
"""
    body = src.rstrip()
    assert body.endswith("}")
    src = body[: body.rfind("}")].rstrip() + "\n" + ADD + "}\n"
    src = src.replace("import net.minecraft.world.item.ItemStack;",
                      "import net.minecraft.world.item.ItemStack;\nimport net.minecraft.world.item.MapItem;")
    open(P, "w", encoding="utf-8", newline="").write(src)
    print("ItemData: map helpers added")

# ---------------------------------------------------------------- 1.12.2 ItemMap
P = r"src/main/java/legacyconnector/v1_12_2/net/minecraft/item/ItemMap.java"
src = open(P, encoding="utf-8").read()
EDITS = [
    # modern(): does the stack already carry a map id?
    ("        if (m.isEmpty() || m.get(net.minecraft.core.component.DataComponents.MAP_ID) == null) {\n"
     "            m = new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.FILLED_MAP);\n"
     "            m.set(net.minecraft.core.component.DataComponents.MAP_ID, new net.minecraft.world.level.saveddata.maps.MapId(stack.getMetadata()));\n"
     "        }",
     "        if (m.isEmpty() || !org.kylepitcock.legacyconnector.core.data.ItemData.hasMapId(m)) {\n"
     "            m = new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.FILLED_MAP);\n"
     "            org.kylepitcock.legacyconnector.core.data.ItemData.setMapId(m, stack.getMetadata());\n"
     "        }"),
    # loadMapData(): the saved-data lookup takes the plain id
    ("        var id = new net.minecraft.world.level.saveddata.maps.MapId(mapId);\n"
     "        var data = net.minecraft.world.item.MapItem.getSavedData(id, level);\n"
     "        return data == null ? null : MapData.mcc$of(id.key(), data);",
     "        var data = net.minecraft.world.item.MapItem.getSavedData(mapId, level);\n"
     "        return data == null ? null : MapData.mcc$of(net.minecraft.world.item.MapItem.makeKey(mapId), data);"),
    # getMapData(): the stack's map id, or the legacy name
    ("        var id = m.get(net.minecraft.core.component.DataComponents.MAP_ID);\n"
     "        return MapData.mcc$of(id == null ? \"map_\" + stack.getMetadata() : id.key(), data);",
     "        Integer id = net.minecraft.world.item.MapItem.getMapId(m);\n"
     "        return MapData.mcc$of(id == null ? \"map_\" + stack.getMetadata() : net.minecraft.world.item.MapItem.makeKey(id), data);"),
    # updateMapData(): plain int id
    ("        var modern = net.minecraft.world.item.MapItem.getSavedData(new net.minecraft.world.level.saveddata.maps.MapId(mcc$idOf(data)), level);",
     "        var modern = net.minecraft.world.item.MapItem.getSavedData(mcc$idOf(data), level);"),
    # scaleMap(): 1.20.1's onCraftedPostProcess does the scaling itself; the map id is an int
    ("        m.set(net.minecraft.core.component.DataComponents.MAP_POST_PROCESSING, net.minecraft.world.item.component.MapPostProcessing.SCALE);\n"
     "        m.getItem().onCraftedPostProcess(m, level);\n"
     "        var id = m.get(net.minecraft.core.component.DataComponents.MAP_ID);\n"
     "        if (id != null) stack.setItemDamage(id.id());",
     "        // 1.20.1's onCraftedPostProcess is what scales a map up (1.21 marks the stack with MapPostProcessing.SCALE first).\n"
     "        m.getItem().onCraftedPostProcess(m, level);\n"
     "        Integer id = net.minecraft.world.item.MapItem.getMapId(m);\n"
     "        if (id != null) stack.setItemDamage(id);"),
]
for old, new in EDITS:
    if src.count(old) != 1:
        print("ABORT ItemMap1122:", src.count(old), old.splitlines()[0][:70])
        sys.exit(1)
    src = src.replace(old, new)
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P)

"""Map ids in the 1.7.10 shim and the bridges: MapId -> int, Level.getMapData(String) on 1.20.1."""
import sys

ITEM_DATA = "org.kylepitcock.legacyconnector.core.data.ItemData"

EDITS = {
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/bridge/Stacks1122.java": [
        ("        var mapId = stack.get(DataComponents.MAP_ID);\n        if (mapId != null) meta = mapId.id();",
         "        int mapId = org.kylepitcock.legacyconnector.core.data.ItemData.mapId(stack);\n        if (mapId >= 0) meta = mapId;"),
        ("if (modern == net.minecraft.world.item.Items.FILLED_MAP) out.set(DataComponents.MAP_ID, new net.minecraft.world.level.saveddata.maps.MapId(stack.getMetadata()));",
         "if (modern == net.minecraft.world.item.Items.FILLED_MAP) org.kylepitcock.legacyconnector.core.data.ItemData.setMapId(out, stack.getMetadata());"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/ItemBridge.java": [
        ("if (meta >= 0 && meta != Short.MAX_VALUE) stack.set(net.minecraft.core.component.DataComponents.MAP_ID, new net.minecraft.world.level.saveddata.maps.MapId(meta));",
         "if (meta >= 0 && meta != Short.MAX_VALUE) org.kylepitcock.legacyconnector.core.data.ItemData.setMapId(stack, meta);"),
        ("        if (stack.getItem() instanceof net.minecraft.world.item.MapItem) {\n"
         "            var id = stack.get(net.minecraft.core.component.DataComponents.MAP_ID);\n"
         "            return id == null ? 0 : id.id();\n"
         "        }",
         "        if (stack.getItem() instanceof net.minecraft.world.item.MapItem) {\n"
         "            int id = org.kylepitcock.legacyconnector.core.data.ItemData.mapId(stack);\n"
         "            return Math.max(0, id);\n"
         "        }"),
        ("stack.set(net.minecraft.core.component.DataComponents.MAP_ID, new net.minecraft.world.level.saveddata.maps.MapId(Math.max(0, damage)));",
         "org.kylepitcock.legacyconnector.core.data.ItemData.setMapId(stack, Math.max(0, damage));"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/client/renderer/entity/RenderItemFrame.java": [
        ("        var id = modern.get(net.minecraft.core.component.DataComponents.MAP_ID);\n"
         "        var data = net.minecraft.world.item.MapItem.getSavedData(modern, mc.level);",
         "        Integer id = net.minecraft.world.item.MapItem.getMapId(modern);\n"
         "        var data = net.minecraft.world.item.MapItem.getSavedData(modern, mc.level);"),
    ],
    r"src/main/java/legacyconnector/v1_7_10/net/minecraft/item/ItemMap.java": [
        # loadMapData: 1.20.1 looks saved data up by its string key
        ("            MapData view = mcc$view(id, level.getMapData(new MapId(id)));",
         "            MapData view = mcc$view(id, level.getMapData(net.minecraft.world.item.MapItem.makeKey(id)));"),
        # getMapData: the id is a plain int now, and setMapData takes the string key
        ("            MapId id = modernStack.get(net.minecraft.core.component.DataComponents.MAP_ID);\n"
         "            MapItemSavedData data = id == null ? null : level.getMapData(id);",
         "            Integer mapId = net.minecraft.world.item.MapItem.getMapId(modernStack);\n"
         "            MapItemSavedData data = mapId == null ? null : level.getMapData(net.minecraft.world.item.MapItem.makeKey(mapId));"),
        ("                data = mcc$newModern(x, z, scale, server.dimension());\n"
         "                id = server.getFreeMapId();\n"
         "                server.setMapData(id, data);\n"
         "                modernStack.set(net.minecraft.core.component.DataComponents.MAP_ID, id);\n"
         "            }\n"
         "            return id == null ? null : mcc$view(id.id(), data);",
         "                data = mcc$newModern(x, z, scale, server.dimension());\n"
         "                mapId = server.getFreeMapId();\n"
         "                server.setMapData(net.minecraft.world.item.MapItem.makeKey(mapId), data);\n"
         "                org.kylepitcock.legacyconnector.core.data.ItemData.setMapId(modernStack, mapId);\n"
         "            }\n"
         "            return mapId == null ? null : mcc$view(mapId, data);"),
        # createMapDataPacket
        ("        MapId id = stack.mcc$modern().get(net.minecraft.core.component.DataComponents.MAP_ID);\n"
         "        MapItemSavedData data = id == null ? null : level.getMapData(id);",
         "        Integer mapId = net.minecraft.world.item.MapItem.getMapId(stack.mcc$modern());\n"
         "        MapItemSavedData data = mapId == null ? null : level.getMapData(net.minecraft.world.item.MapItem.makeKey(mapId));"),
        ("        net.minecraft.network.protocol.Packet<?> modern = data.getUpdatePacket(id, p);",
         "        net.minecraft.network.protocol.Packet<?> modern = data.getUpdatePacket(mapId, p);"),
        ("import net.minecraft.world.level.saveddata.maps.MapId;\n", ""),
    ],
}

for path, pairs in EDITS.items():
    src = open(path, encoding="utf-8").read()
    for old, new in pairs:
        n = src.count(old)
        if n != 1:
            print(f"ABORT {n} matches in {path}: {old.splitlines()[0][:70]!r}")
            sys.exit(1)
        src = src.replace(old, new)
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

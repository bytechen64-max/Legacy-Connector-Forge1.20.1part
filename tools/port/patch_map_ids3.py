"""Last two MapId users: the map renderer's detached-entry record and the map packet."""
import sys

EDITS = {
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/client/gui/MapItemRenderer.java": [
        ("private record Detached(net.minecraft.world.level.saveddata.maps.MapId id, net.minecraft.world.level.saveddata.maps.MapItemSavedData data) {}",
         "private record Detached(int id, net.minecraft.world.level.saveddata.maps.MapItemSavedData data) {}"),
        ("            net.minecraft.world.level.saveddata.maps.MapId id = null;",
         "            Integer id = null;"),
        ("                id = new net.minecraft.world.level.saveddata.maps.MapId(number);\n"
         "                data = mc.level.getMapData(id);",
         "                id = number;\n"
         "                data = mc.level.getMapData(net.minecraft.world.item.MapItem.makeKey(number));"),
        ("            d = new Detached(new net.minecraft.world.level.saveddata.maps.MapId(nextPrivateId--), data);",
         "            d = new Detached(nextPrivateId--, data);"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/network/play/server/SPacketMaps.java": [
        ("        return new net.minecraft.network.protocol.game.ClientboundMapItemDataPacket(new net.minecraft.world.level.saveddata.maps.MapId(mapId), mapScale, false,\n"
         "                decorations, patch);",
         "        return new net.minecraft.network.protocol.game.ClientboundMapItemDataPacket(mapId, mapScale, false,\n"
         "                decorations, patch);"),
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

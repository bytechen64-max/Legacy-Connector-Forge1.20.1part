"""Last player-skin call sites: 1.20.1's DefaultPlayerSkin/PlayerInfo accessors."""
import sys

EDITS = {
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/client/resources/DefaultPlayerSkin.java": [
        ("        return legacy(net.minecraft.client.resources.DefaultPlayerSkin.get(id).texture());",
         "        return legacy(net.minecraft.client.resources.DefaultPlayerSkin.getDefaultSkin(id));"),
        ("        return net.minecraft.client.resources.DefaultPlayerSkin.get(id).model() == net.minecraft.client.resources.PlayerSkin.Model.SLIM ? \"slim\" : \"default\";",
         "        return net.minecraft.client.resources.DefaultPlayerSkin.getSkinModelName(id);"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/client/network/NetworkPlayerInfo.java": [
        ("        var skin = mcc$modern().getSkin();", "        var skin = mcc$modern().getSkinLocation();"),
    ],
}

for path, pairs in EDITS.items():
    src = open(path, encoding="utf-8").read()
    for old, new in pairs:
        n = src.count(old)
        if n != 1:
            print(f"ABORT {n} matches in {path}: {old.strip()[:60]}")
            sys.exit(1)
        src = src.replace(old, new)
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

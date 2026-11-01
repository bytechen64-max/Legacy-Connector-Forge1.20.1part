"""1.20.5 renamed hanging entities and moved player skins behind PlayerSkin: 1.20.1 has the older accessors."""
import os
import sys

changed = []
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        src = open(p, encoding="utf-8").read()
        before = src
        # decoration.HangingEntity is 1.20.1's name for BlockAttachedEntity
        src = src.replace("net.minecraft.world.entity.decoration.BlockAttachedEntity",
                          "net.minecraft.world.entity.decoration.HangingEntity")
        src = src.replace("BlockAttachedEntity", "HangingEntity")
        # skins: 1.20.1 exposes the texture/model directly instead of a PlayerSkin record
        src = src.replace("p.getSkin().model() == net.minecraft.client.resources.PlayerSkin.Model.SLIM",
                          "\"slim\".equals(p.getModelName())")
        src = src.replace("getSkin().model() == net.minecraft.client.resources.PlayerSkin.Model.SLIM ? \"slim\" : \"default\"",
                          "getModelName()")
        src = src.replace("getSkin().texture()", "getSkinLocation()")
        src = src.replace("player.getSkin().capeTexture()", "player.getCloakTextureLocation()")
        if src != before:
            open(p, "w", encoding="utf-8", newline="").write(src)
            changed.append(p)
print("patched", len(changed), "files")
for c in changed:
    print("  ", c)

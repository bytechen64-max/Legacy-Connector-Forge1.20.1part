"""Skulls take a GameProfile, banner patterns and firework flight live in the item tag on 1.20.1."""
import sys

EDITS = {
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/tileentity/TileEntitySkull.java": [
        ("        if (mcc$skull != null && playerProfile != null) mcc$skull.setOwner(new net.minecraft.world.item.component.ResolvableProfile(playerProfile));",
         "        // 1.20.1 hands the GameProfile over directly (ResolvableProfile is 1.20.5).\n"
         "        if (mcc$skull != null && playerProfile != null) mcc$skull.setOwner(playerProfile);"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/client/renderer/tileentity/TileEntitySkullRenderer.java": [
        ("            var renderType = SkullBlockRenderer.getRenderType(type, profile == null ? null : new net.minecraft.world.item.component.ResolvableProfile(profile));",
         "            var renderType = SkullBlockRenderer.getRenderType(type, profile);"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/tileentity/TileEntityBanner.java": [
        ("        var backing = stack.mcc$backing();\n"
         "        if (backing != null && backing.has(net.minecraft.core.component.DataComponents.BANNER_PATTERNS)) {\n"
         "            var layers = backing.get(net.minecraft.core.component.DataComponents.BANNER_PATTERNS);\n"
         "            if (layers != null && !layers.layers().isEmpty()) backing.set(net.minecraft.core.component.DataComponents.BANNER_PATTERNS, layers.removeLast());\n"
         "            return;\n"
         "        }\n",
         "        // 1.20.1 keeps the patterns in the item's BlockEntityTag (there is no banner pattern component).\n"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/entity/item/EntityFireworkRocket.java": [
        ("            var fireworks = modern.get(net.minecraft.core.component.DataComponents.FIREWORKS);\n"
         "            int flight = 1 + (fireworks == null ? 0 : fireworks.flightDuration());",
         "            // 1.20.1 keeps the firework in the item tag (the FIREWORKS component is 1.20.5).\n"
         "            var fireworkTag = modern.getTagElement(\"Fireworks\");\n"
         "            int flight = 1 + (fireworkTag == null ? 0 : fireworkTag.getByte(\"Flight\"));"),
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

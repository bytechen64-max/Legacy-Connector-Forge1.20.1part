"""Potion contents, armor dye and enchantments: 1.20.1 keeps them in the item tag / through helpers."""
import sys

POTION = "org.kylepitcock.legacyconnector.core.data.PotionData"

EDITS = {
    r"src/main/java/legacyconnector/v1_7_10/net/minecraft/item/ItemPotion.java": [
        ("        var contents = stack == null ? null : ItemStack.mcc$toModern(stack).get(net.minecraft.core.component.DataComponents.POTION_CONTENTS);\n"
         "        if (contents != null) return contents.getColor() & 0xFFFFFF;",
         f"        var contents = stack == null ? {POTION}.EMPTY : {POTION}.of(ItemStack.mcc$toModern(stack));\n"
         "        if (!contents.isEmpty()) return contents.color() & 0xFFFFFF;"),
        ("        var contents = ItemStack.mcc$toModern(stack).get(net.minecraft.core.component.DataComponents.POTION_CONTENTS);\n"
         "        if (contents != null && contents.hasEffects()) {",
         f"        var contents = {POTION}.of(ItemStack.mcc$toModern(stack));\n"
         "        if (!contents.allEffects().isEmpty()) {"),
        ("            for (var instance : contents.getAllEffects()) out.add(legacyconnector.v1_7_10.net.minecraft.potion.PotionEffect.mcc$wrap(instance));",
         "            for (var instance : contents.allEffects()) out.add(legacyconnector.v1_7_10.net.minecraft.potion.PotionEffect.mcc$wrap(instance));"),
    ],
    r"src/main/java/legacyconnector/v1_7_10/net/minecraft/item/ItemArmor.java": [
        ("            ItemStack.mcc$toModern(stack).remove(net.minecraft.core.component.DataComponents.DYED_COLOR);",
         "            // 1.20.1 keeps the dye in display.color (the DYED_COLOR component is 1.20.5).\n"
         "            var t = ItemStack.mcc$toModern(stack).getTag();\n"
         "            if (t != null && t.contains(\"display\", 10)) t.getCompound(\"display\").remove(\"color\");"),
        ("            var dyed = ItemStack.mcc$toModern(stack).get(net.minecraft.core.component.DataComponents.DYED_COLOR);\n"
         "            return dyed != null ? dyed.rgb() & 0xFFFFFF : 10511680;",
         "            var t = ItemStack.mcc$toModern(stack).getTag();\n"
         "            if (t != null && t.contains(\"display\", 10) && t.getCompound(\"display\").contains(\"color\", 3)) {\n"
         "                return t.getCompound(\"display\").getInt(\"color\") & 0xFFFFFF;\n"
         "            }\n"
         "            return 10511680;"),
        ("            ItemStack.mcc$toModern(stack).set(net.minecraft.core.component.DataComponents.DYED_COLOR, new net.minecraft.world.item.component.DyedItemColor(color, true));",
         "            var modern = ItemStack.mcc$toModern(stack);\n"
         "            modern.getOrCreateTagElement(\"display\").putInt(\"color\", color);"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/item/ItemBow.java": [
        ("        var enchants = modern.get(net.minecraft.core.component.DataComponents.ENCHANTMENTS);\n"
         "        if (enchants != null) vanilla.set(net.minecraft.core.component.DataComponents.ENCHANTMENTS, enchants);",
         "        // 1.20.1 copies the enchantment list through the item tag (the ENCHANTMENTS component is 1.20.5).\n"
         "        var tag = modern.getTag();\n"
         "        if (tag != null && tag.contains(\"Enchantments\", 9)) {\n"
         "            vanilla.getOrCreateTag().put(\"Enchantments\", tag.getList(\"Enchantments\", 10).copy());\n"
         "        }"),
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

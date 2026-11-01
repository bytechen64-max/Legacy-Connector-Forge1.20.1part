"""PotionContents (1.20.5 component) -> core.data.PotionData over 1.20.1's PotionUtils tag keys."""
import sys

PD = "org.kylepitcock.legacyconnector.core.data.PotionData"

EDITS = {
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/bridge/Stacks1122.java": [
        ("            out.set(DataComponents.POTION_CONTENTS, new net.minecraft.world.item.alchemy.PotionContents(potion, color, effects));",
         "            new " + PD + "(potion, color, effects).applyTo(out);"),
        ("    private static void potionFromModern(net.minecraft.world.item.alchemy.PotionContents contents, ItemStack out) {",
         "    private static void potionFromModern(" + PD + " contents, ItemStack out) {"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/Brewing1710.java": [
        ("        PotionContents contents = stack.get(DataComponents.POTION_CONTENTS);\n"
         "        if (contents == null || contents.potion().isEmpty() || !contents.customEffects().isEmpty()) return -1;",
         "        var contents = " + PD + ".of(stack);\n"
         "        if (contents.potion().isEmpty() || !contents.customEffects().isEmpty()) return -1;"),
        ("            stack.set(DataComponents.POTION_CONTENTS, new PotionContents(vanilla));\n            return stack;",
         "            " + PD + ".of(vanilla).applyTo(stack);\n            return stack;"),
        ("            stack.set(DataComponents.POTION_CONTENTS, new PotionContents(Potions.MUNDANE));\n            return stack;",
         "            " + PD + ".of(Potions.MUNDANE).applyTo(stack);\n            return stack;"),
        ("        stack.set(DataComponents.POTION_CONTENTS, new PotionContents(Optional.empty(), Optional.of(0xFF000000 | PotionHelper.func_77915_a(value, false)), effects));",
         "        new " + PD + "(Optional.empty(), Optional.of(0xFF000000 | PotionHelper.func_77915_a(value, false)), effects).applyTo(stack);"),
        ("        stack.set(DataComponents.ITEM_NAME, Component.translatable(splash ? \"legacyconnector.splash_potion_of\" : \"legacyconnector.potion_of\", name));",
         "        stack.setHoverName(Component.translatable(splash ? \"legacyconnector.splash_potion_of\" : \"legacyconnector.potion_of\", name));"),
        ("import net.minecraft.world.item.alchemy.PotionContents;\n", "import org.kylepitcock.legacyconnector.core.data.PotionData;\n"),
        ("PotionContents contents", "PotionData contents"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/entity/projectile/EntityTippedArrow.java": [
        ("        var contents = modern.get(net.minecraft.core.component.DataComponents.POTION_CONTENTS);\n"
         "        var a = mcc$modernArrow();\n"
         "        if (a != null) {\n"
         "            if (contents != null) for (var e : contents.getAllEffects()) a.addEffect(new net.minecraft.world.effect.MobEffectInstance(e));",
         "        var contents = " + PD + ".of(modern);\n"
         "        var a = mcc$modernArrow();\n"
         "        if (a != null) {\n"
         "            for (var e : contents.allEffects()) a.addEffect(new net.minecraft.world.effect.MobEffectInstance(e));"),
        ("        var contents = Stacks1122.toModern(stack).get(net.minecraft.core.component.DataComponents.POTION_CONTENTS);\n"
         "        return contents == null ? -1 : contents.getColor();",
         "        var contents = " + PD + ".of(Stacks1122.toModern(stack));\n"
         "        return contents.isEmpty() ? -1 : contents.color();"),
        ("        modern.set(net.minecraft.core.component.DataComponents.POTION_CONTENTS, new net.minecraft.world.item.alchemy.PotionContents(java.util.Optional.empty(),\n"
         "                mcc$color == -1 ? java.util.Optional.empty() : java.util.Optional.of(mcc$color), effects));",
         "        new " + PD + "(java.util.Optional.empty(),\n"
         "                mcc$color == -1 ? java.util.Optional.empty() : java.util.Optional.of(mcc$color), effects).applyTo(modern);"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/entity/monster/EntityWitch.java": [
        ("        thrown.setItem(net.minecraft.world.item.alchemy.PotionContents.createItemStack(net.minecraft.world.item.Items.SPLASH_POTION, potion));",
         "        thrown.setItem(" + PD + ".createItemStack(net.minecraft.world.item.Items.SPLASH_POTION, potion));"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/entity/projectile/EntityExpBottle.java": [
        ("            level.levelEvent(2002, mcc$entity.blockPosition(), net.minecraft.world.item.alchemy.PotionContents.getColor(\n"
         "                    net.minecraft.world.item.alchemy.Potions.WATER));",
         "            level.levelEvent(2002, mcc$entity.blockPosition(), " + PD + ".getColor(\n"
         "                    net.minecraft.world.item.alchemy.Potions.WATER));"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/entity/EntityLivingBase.java": [
        ("            e -> net.minecraft.world.item.alchemy.PotionContents.getColorOptional(e.mcc$living().getActiveEffects()).orElse(0), null);",
         "            e -> " + PD + ".getColorOptional(e.mcc$living().getActiveEffects()).orElse(0), null);"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/potion/PotionUtils.java": [
        ("""        var contents = modern.getOrDefault(net.minecraft.core.component.DataComponents.POTION_CONTENTS,
                net.minecraft.world.item.alchemy.PotionContents.EMPTY);
        contents.addPotionTooltip(c -> lines.add(c.getString()), durationFactor, 20.0F);""",
         """        var contents = org.kylepitcock.legacyconnector.core.data.PotionData.of(modern);
        java.util.List<net.minecraft.network.chat.Component> text = new java.util.ArrayList<>();
        net.minecraft.world.item.alchemy.PotionUtils.addPotionTooltip(contents.allEffects(), text, durationFactor);
        for (var c : text) lines.add(c.getString());"""),
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

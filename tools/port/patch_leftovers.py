"""Mechanical fixes: leftover imports, stale 1.21 names, NeoForge-only types."""
import os
import sys

EDITS = {
    # the shim's own class is ForgeHooks; importing Forge's of the same name is a duplicate definition
    r"src/main/java/legacyconnector/v1_12_2/net/minecraftforge/common/ForgeHooks.java": [
        ("import net.minecraftforge.common.ForgeHooks;\n", ""),
    ],
    # the file returns the shim's NonNullList; the modern import shadows it
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/bridge/Crafting1122.java": [
        ("import net.minecraft.core.NonNullList;\n", ""),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/world/World.java": [
        ("        if (modern.isAddedToLevel() ||", "        if (modern.isAddedToWorld() ||"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/LegacyFishingLoot.java": [
        ("    public static final DeferredHolder<MapCodec<? extends IGlobalLootModifier>, MapCodec<LegacyFishingLoot>> SERIALIZER =",
         "    public static final net.minecraftforge.registries.RegistryObject<MapCodec<LegacyFishingLoot>> SERIALIZER ="),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/entity/EntityLivingBase.java": [
        ("var equippable = modern.getItem() instanceof net.minecraft.world.item.ArmorItem armor ? armor.getEquipSound().value() : net.minecraft.sounds.SoundEvents.ARMOR_EQUIP_GENERIC.value();",
         "// 1.20.1 reports sound events directly (1.20.5 wrapped them in holders).\n"
         "        var equippable = modern.getItem() instanceof net.minecraft.world.item.ArmorItem armor ? armor.getEquipSound() : net.minecraft.sounds.SoundEvents.ARMOR_EQUIP_GENERIC;"),
        ("        l.removeEffectsCuredBy(net.minecraftforge.common.EffectCures.MILK);",
         "        // 1.20.1 has no cure system: milk is handled by MilkBucketItem calling removeAllEffects.\n"
         "        l.removeAllEffects();"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/mixin/CreativeTabDuplicateMixin.java": [
        ("import net.minecraftforge.common.util.InsertableLinkedOpenCustomHashSet;\n", ""),
        ("private void legacyconnector$skipDuplicate(InsertableLinkedOpenCustomHashSet<ItemStack> entries, ItemStack stack, CallbackInfo ci) {",
         "private void legacyconnector$skipDuplicate(java.util.Collection<ItemStack> entries, ItemStack stack, CallbackInfo ci) {"),
    ],
}

for path, pairs in EDITS.items():
    src = open(path, encoding="utf-8").read()
    for old, new in pairs:
        n = src.count(old)
        if n != 1:
            print(f"ABORT {n} matches in {path}: {old.strip()[:70]}")
            sys.exit(1)
        src = src.replace(old, new)
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

# the tooltip overrides took a Level; add the import where it is missing
for path in (r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/adapter/Legacy1122Item.java",
             r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/adapter/Legacy1122BlockItem.java",
             r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/adapter/LegacyItemAdapter.java",
             r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/adapter/LegacyBlockItemAdapter.java"):
    src = open(path, encoding="utf-8").read()
    if "import net.minecraft.world.level.Level;" in src:
        continue
    idx = src.find("\nimport ")
    if idx < 0:
        print("ABORT: no imports in", path)
        sys.exit(1)
    src = src[:idx + 1] + "import net.minecraft.world.level.Level;\n" + src[idx + 1:]
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("added the Level import to", path)

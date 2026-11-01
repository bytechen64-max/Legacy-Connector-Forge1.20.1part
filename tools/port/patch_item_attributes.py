"""1.20.1 item attributes come from getDefaultAttributeModifiers(EquipmentSlot), not from Item.Properties."""
import sys

# ---- the adapter answers per slot
P = r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/adapter/LegacyItemAdapter.java"
src = open(P, encoding="utf-8").read()
anchor = """    @Override
    public int getUseDuration(ItemStack stack) {"""
add = """    /**
     * Armour value and attack damage of a legacy item.
     *
     * <p>1.20.1 asks per equipment slot and answers with a Multimap; the 1.20.5 component (and {@code Item.Properties.attributes})
     * does not exist yet, so the legacy item's own attribute map is translated here.</p>
     */
    @Override
    public com.google.common.collect.Multimap<net.minecraft.world.entity.ai.attributes.Attribute,
            net.minecraft.world.entity.ai.attributes.AttributeModifier> getDefaultAttributeModifiers(
            net.minecraft.world.entity.EquipmentSlot slot) {
        var out = com.google.common.collect.HashMultimap.<net.minecraft.world.entity.ai.attributes.Attribute,
                net.minecraft.world.entity.ai.attributes.AttributeModifier>create();
        out.putAll(super.getDefaultAttributeModifiers(slot));
        try {
            if (legacy instanceof legacyconnector.v1_7_10.net.minecraft.item.ItemArmor armor
                    && armor.damageReduceAmount > 0 && armor.armorType == armorSlotIndex(slot)) {
                out.put(net.minecraft.world.entity.ai.attributes.Attributes.ARMOR,
                        new net.minecraft.world.entity.ai.attributes.AttributeModifier(
                                "legacyconnector:legacy_armor_" + armor.armorType, armor.damageReduceAmount,
                                net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation.ADDITION));
            }
            if (slot == net.minecraft.world.entity.EquipmentSlot.MAINHAND) {
                var view = legacyconnector.v1_7_10.net.minecraft.item.ItemStack.mcc$wrap(new ItemStack(this));
                var map = legacy.getAttributeModifiers(view);
                if (map != null) {
                    for (Object o : map.entries()) {
                        if (!(o instanceof java.util.Map.Entry<?, ?> entry)) continue;
                        if (!(entry.getKey() instanceof legacyconnector.v1_7_10.net.minecraft.entity.ai.attributes.IAttribute a)) continue;
                        if (!(entry.getValue() instanceof legacyconnector.v1_7_10.net.minecraft.entity.ai.attributes.AttributeModifier m)) continue;
                        var attribute = a.mcc$modern();
                        if (attribute == null) continue;
                        out.put(attribute, m.mcc$modern());
                    }
                }
            }
        } catch (RuntimeException | LinkageError e) {
            // a broken legacy item keeps the vanilla modifiers
        }
        return out;
    }

    /** 1.7.10 armour slots: 0 helmet, 1 chestplate, 2 leggings, 3 boots. */
    private static int armorSlotIndex(net.minecraft.world.entity.EquipmentSlot slot) {
        return switch (slot) {
            case HEAD -> 0;
            case CHEST -> 1;
            case LEGS -> 2;
            case FEET -> 3;
            default -> -1;
        };
    }

"""
if src.count(anchor) != 1:
    print("ABORT: adapter anchor missing")
    sys.exit(1)
src = src.replace(anchor, add + anchor)
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P)

# ---- the properties no longer carry attributes
P = r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/ItemBridge.java"
src = open(P, encoding="utf-8").read()
start = src.find("        var modifiers = net.minecraft.world.item.component.ItemAttributeModifiers.builder();")
end = src.find("        if (item.hasContainerItem()")
if start < 0 or end < 0:
    print("ABORT: properties block not found")
    sys.exit(1)
replacement = ("        // 1.20.1 item properties cannot carry attributes: the adapter answers them per equipment slot\n"
               "        // (LegacyItemAdapter.getDefaultAttributeModifiers).\n")
src = src[:start] + replacement + src[end:]
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P)

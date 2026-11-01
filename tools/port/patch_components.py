"""1.20.1 has no data components: enchantments are a Map, attribute modifiers a Multimap, custom data the item tag."""
import sys

EDITS = {
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/adapter/Legacy1122Item.java": [
        ("""    @Override
    public net.minecraft.world.item.component.ItemAttributeModifiers getDefaultAttributeModifiers(ItemStack stack) {
        net.minecraft.world.item.component.ItemAttributeModifiers base = super.getDefaultAttributeModifiers(stack);
        try {
            var view = org.kylepitcock.legacyconnector.v1_12_2.bridge.Stacks1122.fromModern(stack);
            var builder = net.minecraft.world.item.component.ItemAttributeModifiers.builder();
            boolean any = false;
            for (var slot : legacyconnector.v1_12_2.net.minecraft.inventory.EntityEquipmentSlot.values()) {
                var map = legacy.getAttributeModifiers(slot, view);
                if (map == null || map.isEmpty()) continue;
                var group = switch (slot) {
                    case MAINHAND -> net.minecraft.world.entity.EquipmentSlotGroup.MAINHAND;
                    case OFFHAND -> net.minecraft.world.entity.EquipmentSlotGroup.OFFHAND;
                    case FEET -> net.minecraft.world.entity.EquipmentSlotGroup.FEET;
                    case LEGS -> net.minecraft.world.entity.EquipmentSlotGroup.LEGS;
                    case CHEST -> net.minecraft.world.entity.EquipmentSlotGroup.CHEST;
                    case HEAD -> net.minecraft.world.entity.EquipmentSlotGroup.HEAD;
                };
                for (var e : map.entries()) {
                    var attribute = legacyconnector.v1_12_2.net.minecraft.entity.ai.attributes.IAttribute.mcc$modernByName(e.getKey());
                    if (attribute == null || e.getValue() == null) continue;
                    var modifier = e.getValue().mcc$modern();
                    // per slot: one modifier id may be used in several slots (armor uses one UUID per slot, swords one for the hand)
                    modifier = new net.minecraft.world.entity.ai.attributes.AttributeModifier(
                            modifier.id().withSuffix("/" + slot.getName()), modifier.amount(), modifier.operation());
                    builder.add(attribute, modifier, group);
                    any = true;
                }
            }
            return any ? builder.build() : base;
        } catch (RuntimeException | LinkageError e) {
            return base;
        }
    }""",
         """    @Override
    public com.google.common.collect.Multimap<net.minecraft.world.entity.ai.attributes.Attribute,
            net.minecraft.world.entity.ai.attributes.AttributeModifier> getDefaultAttributeModifiers(net.minecraft.world.entity.EquipmentSlot slot) {
        // 1.20.1 asks per equipment slot and answers with a Multimap; 1.20.5 collects every group into one component.
        var out = com.google.common.collect.HashMultimap.<net.minecraft.world.entity.ai.attributes.Attribute,
                net.minecraft.world.entity.ai.attributes.AttributeModifier>create();
        out.putAll(super.getDefaultAttributeModifiers(slot));
        try {
            var view = org.kylepitcock.legacyconnector.v1_12_2.bridge.Stacks1122.fromModern(new ItemStack(this));
            for (var legacySlot : legacyconnector.v1_12_2.net.minecraft.inventory.EntityEquipmentSlot.values()) {
                if (!legacySlot.getName().equals(slot.getName())) continue;
                var map = legacy.getAttributeModifiers(legacySlot, view);
                if (map == null || map.isEmpty()) continue;
                for (var e : map.entries()) {
                    var attribute = legacyconnector.v1_12_2.net.minecraft.entity.ai.attributes.IAttribute.mcc$modernByName(e.getKey());
                    if (attribute == null || e.getValue() == null) continue;
                    var modifier = e.getValue().mcc$modern();
                    // per slot: one modifier id may be used in several slots (armor uses one UUID per slot, swords one for the hand)
                    out.put(attribute, new net.minecraft.world.entity.ai.attributes.AttributeModifier(
                            modifier.getName() + "/" + legacySlot.getName(), modifier.getAmount(), modifier.getOperation()));
                }
            }
        } catch (RuntimeException | LinkageError e) {
            // a broken legacy item keeps the vanilla modifiers
        }
        return out;
    }"""),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/ItemBridge.java": [
        ("import net.minecraft.core.component.DataComponents;\n", ""),
        ("import net.minecraft.world.item.component.CustomData;\n", ""),
        ("import net.minecraft.world.item.enchantment.ItemEnchantments;\n", ""),
        ("""    public static NBTTagList legacyEnchantments(net.minecraft.world.item.ItemStack stack) {
        NBTTagList list = new NBTTagList();
        ItemEnchantments enchants = stack.getOrDefault(DataComponents.ENCHANTMENTS, ItemEnchantments.EMPTY);
        for (var entry : enchants.entrySet()) {
            Holder<Enchantment> h = entry.getKey();
            String path = h.unwrapKey().map(k -> k.location().getPath()).orElse("");""",
         """    public static NBTTagList legacyEnchantments(net.minecraft.world.item.ItemStack stack) {
        NBTTagList list = new NBTTagList();
        // 1.20.1 keeps enchantments as a map of enchantment to level (the component is 1.20.5).
        var enchants = stack.getEnchantments();
        for (var entry : enchants.entrySet()) {
            var key = net.minecraft.core.registries.BuiltInRegistries.ENCHANTMENT.getKey(entry.getKey());
            String path = key == null ? "" : key.getPath();"""),
        ("""            e.setShort("lvl", (short) entry.getIntValue());""",
         """            e.setShort("lvl", (short) (int) entry.getValue());"""),
        ("""    /** Ensures custom data components exist before stacks are serialized with the legacy tag. */
    static CustomData data(NBTTagCompound tag) {
        return CustomData.of(tag.mcc$modern());
    }
""", ""),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/enchantment/EnchantmentHelper.java": [
        ("""        var enchants = backing.getItem() == net.minecraft.world.item.Items.ENCHANTED_BOOK
                ? backing.getOrDefault(net.minecraft.core.component.DataComponents.STORED_ENCHANTMENTS, net.minecraft.world.item.enchantment.ItemEnchantments.EMPTY)
                : backing.getEnchantments();
        for (var e : enchants.entrySet()) {
            var key = e.getKey().unwrapKey();
            if (key.isPresent() && key.get().location().getNamespace().equals("minecraft") && key.get().location().getPath().equals(path)) return e.getIntValue();
        }""",
         """        // 1.20.1 resolves enchanted books inside getEnchantments already, and the map holds the enchantments themselves.
        var enchants = net.minecraft.world.item.enchantment.EnchantmentHelper.getEnchantments(backing);
        for (var e : enchants.entrySet()) {
            var key = net.minecraft.core.registries.BuiltInRegistries.ENCHANTMENT.getKey(e.getKey());
            if (key != null && key.getNamespace().equals("minecraft") && key.getPath().equals(path)) return e.getValue();
        }"""),
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

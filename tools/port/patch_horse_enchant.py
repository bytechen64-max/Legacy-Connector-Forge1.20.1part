"""Horse armour is the inventory slot, and 1.20.1's enchantItem and stored-enchantment writes differ."""
import sys

EDITS = {
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/entity/passive/AbstractHorse.java": [
        ("""                if (horseChest.getSizeInventory() > 1 && !h.getBodyArmorItem().isEmpty()) {
                    horseChest.setInventorySlotContents(1, org.kylepitcock.legacyconnector.v1_12_2.bridge.Stacks1122.fromModern(h.getBodyArmorItem()));
                }""",
         """                // 1.20.1 has no getBodyArmorItem(): the armour is the horse's armour slot.
                var armour = h.getItem(net.minecraft.world.entity.animal.horse.AbstractHorse.INV_SLOT_ARMOR);
                if (horseChest.getSizeInventory() > 1 && !armour.isEmpty()) {
                    horseChest.setInventorySlotContents(1, org.kylepitcock.legacyconnector.v1_12_2.bridge.Stacks1122.fromModern(armour));
                }"""),
    ],
    r"src/main/java/legacyconnector/v1_7_10/net/minecraft/entity/passive/EntityHorse.java": [
        ("        var armor = h.getBodyArmorItem().getItem();",
         "        var armor = h.getItem(net.minecraft.world.entity.animal.horse.AbstractHorse.INV_SLOT_ARMOR).getItem();"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/world/storage/loot/functions/EnchantWithLevels.java": [
        ("""            var access = server.registryAccess();
            var tag = isTreasure ? net.minecraft.tags.EnchantmentTags.ON_RANDOM_LOOT : net.minecraft.tags.EnchantmentTags.IN_ENCHANTING_TABLE;
            var options = access.registryOrThrow(net.minecraft.core.registries.Registries.ENCHANTMENT).getTag(tag);
            var random = net.minecraft.util.RandomSource.create(rand == null ? 0L : rand.nextLong());
            var modern = org.kylepitcock.legacyconnector.v1_12_2.bridge.Stacks1122.toModern(stack);
            var enchanted = net.minecraft.world.item.enchantment.EnchantmentHelper.enchantItem(random, modern, randomLevel.generateInt(rand), access, options);""",
         """            // 1.20.1's enchantItem takes a treasure flag (the tag options are 1.21).
            var random = net.minecraft.util.RandomSource.create(rand == null ? 0L : rand.nextLong());
            var modern = org.kylepitcock.legacyconnector.v1_12_2.bridge.Stacks1122.toModern(stack);
            var enchanted = net.minecraft.world.item.enchantment.EnchantmentHelper.enchantItem(random, modern,
                    randomLevel.generateInt(rand), isTreasure);"""),
    ],
    r"src/main/java/legacyconnector/v1_7_10/net/minecraft/enchantment/EnchantmentHelper.java": [
        ("""        var registry = server.registryAccess().registryOrThrow(net.minecraft.core.registries.Registries.ENCHANTMENT);
        var modern = stack.mcc$modern();
        var result = net.minecraft.world.item.enchantment.EnchantmentHelper.enchantItem(net.minecraft.util.RandomSource.create(random.nextLong()),
                modern, level, server.registryAccess(), registry.getTag(net.minecraft.tags.EnchantmentTags.IN_ENCHANTING_TABLE));
        if (result != modern) { // a book: vanilla turned this very stack into an enchanted book
            stack.setItem(legacyconnector.v1_7_10.net.minecraft.init.Items.enchanted_book);
            stack.mcc$modern().set(net.minecraft.core.component.DataComponents.STORED_ENCHANTMENTS,
                    result.get(net.minecraft.core.component.DataComponents.STORED_ENCHANTMENTS));
        }""",
         """        var modern = stack.mcc$modern();
        // 1.20.1's enchantItem takes a treasure flag and hands back the stack it changed.
        var result = net.minecraft.world.item.enchantment.EnchantmentHelper.enchantItem(
                net.minecraft.util.RandomSource.create(random.nextLong()), modern, level, false);
        if (result != modern) { // a book: vanilla turned this very stack into an enchanted book
            stack.setItem(legacyconnector.v1_7_10.net.minecraft.init.Items.enchanted_book);
            // 1.20.1 keeps stored enchantments in the item tag (the component is 1.20.5).
            var stored = result.getTagElement("StoredEnchantments");
            if (stored != null) stack.mcc$modern().getOrCreateTag().put("StoredEnchantments", stored.copy());
        }"""),
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

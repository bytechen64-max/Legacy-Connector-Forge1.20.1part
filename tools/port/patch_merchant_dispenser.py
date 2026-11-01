"""1.20.1: BlockSource is an interface (net.minecraft.core) and merchant offers are priced with ItemStacks, not ItemCost."""
import sys

EDITS = {
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/dispenser/BlockSourceImpl.java": [
        ("""    public static BlockSourceImpl mcc$of(net.minecraft.core.dispenser.BlockSource source) {
        var p = source.pos();
        return new BlockSourceImpl(org.kylepitcock.legacyconnector.v1_12_2.bridge.WorldBridge1122.wrap(source.level()), new BlockPos(p.getX(), p.getY(), p.getZ()));
    }""",
         """    /** 1.20.1's source is {@code net.minecraft.core.BlockSource} (the record of the same name is 1.20.5+). */
    public static BlockSourceImpl mcc$of(net.minecraft.core.BlockSource source) {
        var p = source.getPos();
        return new BlockSourceImpl(org.kylepitcock.legacyconnector.v1_12_2.bridge.WorldBridge1122.wrap(source.getLevel()), new BlockPos(p.getX(), p.getY(), p.getZ()));
    }"""),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/bridge/Dispensers1122.java": [
        ("import net.minecraft.core.dispenser.BlockSource;", "import net.minecraft.core.BlockSource;"),
        ("    public static BlockSource modernSource(IBlockSource source) {",
         "    public static net.minecraft.core.BlockSource modernSource(IBlockSource source) {"),
        ("""        var p = source.getBlockPos();
        var pos = new net.minecraft.core.BlockPos(p.getX(), p.getY(), p.getZ());
        DispenserBlockEntity be = server.getBlockEntity(pos) instanceof DispenserBlockEntity d ? d : null;
        return new BlockSource(server, pos, server.getBlockState(pos), be);""",
         """        var p = source.getBlockPos();
        // 1.20.1's source only carries the level and position; the block state and block entity are looked up from them.
        return new net.minecraft.core.BlockSourceImpl(server, new net.minecraft.core.BlockPos(p.getX(), p.getY(), p.getZ()));"""),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/village/MerchantRecipe.java": [
        ("""    private static net.minecraft.world.item.trading.ItemCost mcc$cost(ItemStack legacy) {
        if (legacy == null || legacy.isEmpty()) return null;
        var modern = org.kylepitcock.legacyconnector.v1_12_2.bridge.Stacks1122.toModern(legacy);
        if (modern.isEmpty()) return null;
        var predicate = net.minecraft.core.component.DataComponentPredicate.EMPTY;
        if (!modern.getComponentsPatch().isEmpty()) {
            var builder = net.minecraft.core.component.DataComponentPredicate.builder();
            for (var entry : modern.getComponentsPatch().entrySet()) {
                entry.getValue().ifPresent(v -> mcc$expect(builder, entry.getKey(), v));
            }
            predicate = builder.build();
        }
        return new net.minecraft.world.item.trading.ItemCost(modern.getItemHolder(), modern.getCount(), predicate);
    }

    @SuppressWarnings("unchecked")
    private static <T> void mcc$expect(net.minecraft.core.component.DataComponentPredicate.Builder builder,
            net.minecraft.core.component.DataComponentType<T> type, Object value) {
        builder.expect(type, (T) value);
    }""",
         """    /** 1.20.1 prices an offer with the item stack itself (the tag is matched as part of it); 1.20.5 wrapped it in an ItemCost. */
    private static net.minecraft.world.item.ItemStack mcc$cost(ItemStack legacy) {
        if (legacy == null || legacy.isEmpty()) return null;
        var modern = org.kylepitcock.legacyconnector.v1_12_2.bridge.Stacks1122.toModern(legacy);
        return modern.isEmpty() ? null : modern;
    }"""),
        ("        var costB = java.util.Optional.ofNullable(mcc$cost(secondItemToBuy));",
         "        var costB = mcc$cost(secondItemToBuy);\n        if (costB == null) costB = net.minecraft.world.item.ItemStack.EMPTY;"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/MerchantBridge.java": [
        ("        Optional<ItemCost> second = Optional.empty();\n"
         "        if (recipe.hasSecondItemToBuy()) {\n"
         "            var s = ItemStack.mcc$toModern(recipe.getSecondItemToBuy());\n"
         "            if (s != null && !s.isEmpty()) second = Optional.of(new ItemCost(s.getItem(), s.getCount()));\n"
         "        }\n"
         "        return new MerchantOffer(new ItemCost(buy.getItem(), buy.getCount()), second, sell, recipe.getToolUses(), Math.max(1, recipe.getMaxTradeUses()), 0, 0.0F);",
         "        net.minecraft.world.item.ItemStack second = net.minecraft.world.item.ItemStack.EMPTY;\n"
         "        if (recipe.hasSecondItemToBuy()) {\n"
         "            var s = ItemStack.mcc$toModern(recipe.getSecondItemToBuy());\n"
         "            if (s != null && !s.isEmpty()) second = s;\n"
         "        }\n"
         "        return new MerchantOffer(buy, second, sell, recipe.getToolUses(), Math.max(1, recipe.getMaxTradeUses()), 0, 0.0F);"),
        ("                        offers.add(offer != null ? offer : new MerchantOffer(new ItemCost(net.minecraft.world.item.Items.BARRIER), net.minecraft.world.item.ItemStack.EMPTY, 0, 0, 0.0F));",
         "                        offers.add(offer != null ? offer : new MerchantOffer(new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.BARRIER),\n"
         "                                net.minecraft.world.item.ItemStack.EMPTY, 0, 0, 0.0F));"),
        ("import net.minecraft.world.item.trading.ItemCost;\n", ""),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/VillagerBridge.java": [
        ("            Optional<ItemCost> second = Optional.empty();\n"
         "            if (recipe.hasSecondItemToBuy()) {\n"
         "                var s = ItemStack.mcc$toModern(recipe.getSecondItemToBuy());\n"
         "                if (s != null && !s.isEmpty()) second = Optional.of(new ItemCost(s.getItem(), s.getCount()));\n"
         "            }\n"
         "            return new MerchantOffer(new ItemCost(buy.getItem(), buy.getCount()), second, sell, 0, Math.max(1, recipe.getMaxTradeUses()), 5, 0.05F);",
         "            net.minecraft.world.item.ItemStack second = net.minecraft.world.item.ItemStack.EMPTY;\n"
         "            if (recipe.hasSecondItemToBuy()) {\n"
         "                var s = ItemStack.mcc$toModern(recipe.getSecondItemToBuy());\n"
         "                if (s != null && !s.isEmpty()) second = s;\n"
         "            }\n"
         "            return new MerchantOffer(buy, second, sell, 0, Math.max(1, recipe.getMaxTradeUses()), 5, 0.05F);"),
        ("import net.minecraft.world.item.trading.ItemCost;\n", ""),
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

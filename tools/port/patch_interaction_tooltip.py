"""1.20.5 split item/block interaction (ItemInteractionResult) and tooltips (TooltipContext) do not exist on 1.20.1."""
import sys

EDITS = {
    # ---- block interaction: one use() returning InteractionResult
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/adapter/Legacy1122Block.java": [
        ("import net.minecraft.world.ItemInteractionResult;", "import net.minecraft.world.InteractionResult;"),
        ("    protected ItemInteractionResult useItemOn(net.minecraft.world.item.ItemStack stack, BlockState state, Level level, BlockPos pos, Player player,\n"
         "            InteractionHand hand, BlockHitResult hit) {\n"
         "        if (!activated) return super.useItemOn(stack, state, level, pos, player, hand, hit);",
         "    // 1.20.5 split this into useItemOn (item first); 1.20.1 has the single Block#use.\n"
         "    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player,\n"
         "            InteractionHand hand, BlockHitResult hit) {\n"
         "        if (!activated) return super.use(state, level, pos, player, hand, hit);"),
        ("        if (p == null) return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;",
         "        if (p == null) return InteractionResult.PASS;"),
        ("        return done ? ItemInteractionResult.sidedSuccess(level.isClientSide) : ItemInteractionResult.SKIP_DEFAULT_BLOCK_INTERACTION;",
         "        return done ? InteractionResult.sidedSuccess(level.isClientSide) : InteractionResult.FAIL;"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/adapter/LegacyBlockAdapter.java": [
        ("import net.minecraft.world.ItemInteractionResult;", "import net.minecraft.world.InteractionResult;"),
        ("    protected ItemInteractionResult useItemOn(net.minecraft.world.item.ItemStack stack, BlockState state, Level level, BlockPos pos, Player player,",
         "    // 1.20.5 split this into useItemOn (item first); 1.20.1 has the single Block#use.\n"
         "    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player,"),
        ("        if (hand != InteractionHand.MAIN_HAND) return ItemInteractionResult.SKIP_DEFAULT_BLOCK_INTERACTION;",
         "        if (hand != InteractionHand.MAIN_HAND) return InteractionResult.FAIL;"),
        ("        return activate(level, pos, player, hit) ? ItemInteractionResult.sidedSuccess(level.isClientSide)\n"
         "                : ItemInteractionResult.SKIP_DEFAULT_BLOCK_INTERACTION;",
         "        return activate(level, pos, player, hit) ? InteractionResult.sidedSuccess(level.isClientSide)\n"
         "                : InteractionResult.FAIL;"),
    ],
    # ---- tooltips: appendHoverText takes the Level itself on 1.20.1
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/adapter/Legacy1122Item.java": [
        ("    public void appendHoverText(net.minecraft.world.item.ItemStack stack, TooltipContext context, java.util.List<net.minecraft.network.chat.Component> lines,\n"
         "            net.minecraft.world.item.TooltipFlag flag) {\n"
         "        super.appendHoverText(stack, context, lines, flag);\n"
         "        if (cb().tooltip) cb().appendHoverText(stack, context, lines, flag);",
         "    public void appendHoverText(net.minecraft.world.item.ItemStack stack, Level level, java.util.List<net.minecraft.network.chat.Component> lines,\n"
         "            net.minecraft.world.item.TooltipFlag flag) {\n"
         "        super.appendHoverText(stack, level, lines, flag);\n"
         "        if (cb().tooltip) cb().appendHoverText(stack, level, lines, flag);"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/adapter/Legacy1122BlockItem.java": [
        ("    public void appendHoverText(net.minecraft.world.item.ItemStack stack, TooltipContext context, java.util.List<net.minecraft.network.chat.Component> lines,\n"
         "            net.minecraft.world.item.TooltipFlag flag) {\n"
         "        super.appendHoverText(stack, context, lines, flag);\n"
         "        if (cb().tooltip) cb().appendHoverText(stack, context, lines, flag);",
         "    public void appendHoverText(net.minecraft.world.item.ItemStack stack, Level level, java.util.List<net.minecraft.network.chat.Component> lines,\n"
         "            net.minecraft.world.item.TooltipFlag flag) {\n"
         "        super.appendHoverText(stack, level, lines, flag);\n"
         "        if (cb().tooltip) cb().appendHoverText(stack, level, lines, flag);"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/adapter/LegacyBlockItemAdapter.java": [
        ("    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {",
         "    public void appendHoverText(ItemStack stack, Level level, List<Component> tooltip, TooltipFlag flag) {"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/adapter/ItemCallbacks1122.java": [
        ("    void appendHoverText(net.minecraft.world.item.ItemStack stack, net.minecraft.world.item.Item.TooltipContext context,\n"
         "            java.util.List<net.minecraft.network.chat.Component> lines, net.minecraft.world.item.TooltipFlag flag) {\n"
         "        try {\n"
         "            java.util.List<String> out = new java.util.ArrayList<>();\n"
         "            Level level = context == null ? null : context.level();",
         "    void appendHoverText(net.minecraft.world.item.ItemStack stack, Level level,\n"
         "            java.util.List<net.minecraft.network.chat.Component> lines, net.minecraft.world.item.TooltipFlag flag) {\n"
         "        try {\n"
         "            java.util.List<String> out = new java.util.ArrayList<>();"),
    ],
    # ---- getTooltipLines: no context on 1.20.1
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/client/ClientGui1122.java": [
        ("        var context = mc.level == null ? net.minecraft.world.item.Item.TooltipContext.EMPTY : net.minecraft.world.item.Item.TooltipContext.of(mc.level);\n"
         "        for (var line : modern.getTooltipLines(context, mc.player, flag)) out.add(legacyText(line));",
         "        // 1.20.5 passes a TooltipContext; 1.20.1 derives it from the player.\n"
         "        for (var line : modern.getTooltipLines(mc.player, flag)) out.add(legacyText(line));"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/client/ClientEvents1122.java": [
        ("            for (var line : stack.getTooltipLines(net.minecraft.world.item.Item.TooltipContext.of(mc.level), mc.player, flag)) out.add(ClientGui1122.legacyText(line));",
         "            for (var line : stack.getTooltipLines(mc.player, flag)) out.add(ClientGui1122.legacyText(line));"),
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

"""1.20.1 recipes: CraftingInput -> CraftingContainer, RecipeHolder -> Recipe, and the legacy recipe serializer's id."""
import sys

EDITS = {
    # the grid is handed to the modern recipe manager as a container now
    r"src/main/java/legacyconnector/v1_7_10/net/minecraft/inventory/InventoryCrafting.java": [
        ('''    /** The grid as a modern crafting input (for the modern recipe manager and the modern special recipes); null when it is empty. */
    public net.minecraft.world.item.crafting.CraftingInput mcc$craftingInput() {
        int w = inventoryWidth;
        int h = inventoryHeight;
        if (w <= 0 || h <= 0 || w * h != getSizeInventory()) return null;
        java.util.List<net.minecraft.world.item.ItemStack> items = new java.util.ArrayList<>(w * h);
        boolean any = false;
        for (int i = 0; i < w * h; i++) {
            net.minecraft.world.item.ItemStack s = ItemStack.mcc$toModern(getStackInSlot(i));
            any |= !s.isEmpty();
            items.add(s);
        }
        return any ? net.minecraft.world.item.crafting.CraftingInput.of(w, h, items) : null;
    }''',
         '''    /**
     * The grid as a modern crafting container (for the modern recipe manager and the modern special recipes); null when it is
     * empty. 1.20.1 recipes take a {@code CraftingContainer}; the 1.20.2 {@code CraftingInput} does not exist yet.
     */
    public net.minecraft.world.inventory.CraftingContainer mcc$craftingContainer() {
        int w = inventoryWidth;
        int h = inventoryHeight;
        if (w <= 0 || h <= 0 || w * h != getSizeInventory()) return null;
        net.minecraft.core.NonNullList<net.minecraft.world.item.ItemStack> items =
                net.minecraft.core.NonNullList.withSize(w * h, net.minecraft.world.item.ItemStack.EMPTY);
        boolean any = false;
        for (int i = 0; i < w * h; i++) {
            net.minecraft.world.item.ItemStack s = ItemStack.mcc$toModern(getStackInSlot(i));
            any |= !s.isEmpty();
            items.set(i, s);
        }
        return any ? new net.minecraft.world.inventory.TransientCraftingContainer(null, w, h, items) : null;
    }'''),
    ],
    r"src/main/java/legacyconnector/v1_7_10/net/minecraft/item/crafting/CraftingManager.java": [
        ("        var input = inv.mcc$craftingInput();\n        if (input == null || MODERN_LOOKUP.get()) return null;",
         "        var input = inv.mcc$craftingContainer();\n        if (input == null || MODERN_LOOKUP.get()) return null;"),
        ("            net.minecraft.world.item.ItemStack result = found.get().value().assemble(input, level.registryAccess());",
         "            net.minecraft.world.item.ItemStack result = found.get().assemble(input, level.registryAccess());"),
        ("        var input = inv.mcc$craftingInput();\n        try {\n            if (input == null || !recipe.matches(input, level)) return null;",
         "        var input = inv.mcc$craftingContainer();\n        try {\n            if (input == null || !recipe.matches(input, level)) return null;"),
    ],
    r"src/main/java/legacyconnector/v1_7_10/net/minecraft/item/crafting/RecipeFireworks.java": [
        ("        var input = inv == null ? null : inv.mcc$craftingInput();",
         "        var input = inv == null ? null : inv.mcc$craftingContainer();"),
    ],
    # the server/client recipe books keep the recipe itself, not a RecipeHolder
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/stats/RecipeBook.java": [
        ("    private static net.minecraft.world.item.crafting.RecipeHolder<?> holder(IRecipe recipe) {",
         "    private static net.minecraft.world.item.crafting.Recipe<?> holder(IRecipe recipe) {"),
        ("        static net.minecraft.world.item.crafting.RecipeHolder<?> holder(net.minecraft.resources.ResourceLocation id) {",
         "        static net.minecraft.world.item.crafting.Recipe<?> holder(net.minecraft.resources.ResourceLocation id) {"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/stats/RecipeBookServer.java": [
        ("    private static java.util.List<net.minecraft.world.item.crafting.RecipeHolder<?>> holders(List<IRecipe> recipes, EntityPlayerMP player) {\n"
         "        var out = new java.util.ArrayList<net.minecraft.world.item.crafting.RecipeHolder<?>>();",
         "    private static java.util.List<net.minecraft.world.item.crafting.Recipe<?>> holders(List<IRecipe> recipes, EntityPlayerMP player) {\n"
         "        var out = new java.util.ArrayList<net.minecraft.world.item.crafting.Recipe<?>>();"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/core/RecipeSyncGuard.java": [
        ("import net.minecraft.world.item.crafting.RecipeHolder;", "import net.minecraft.world.item.crafting.Recipe;"),
        ("        List<RecipeHolder<?>> keep = new ArrayList<>();\n        List<String> dropped = new ArrayList<>();\n"
         "        for (RecipeHolder<?> holder : manager.getRecipes()) {\n"
         "            if (sendable(holder, access)) keep.add(holder);\n"
         "            else dropped.add(holder.id().toString());\n        }",
         "        List<Recipe<?>> keep = new ArrayList<>();\n        List<String> dropped = new ArrayList<>();\n"
         "        for (Recipe<?> recipe : manager.getRecipes()) {\n"
         "            if (sendable(recipe, access)) keep.add(recipe);\n"
         "            else dropped.add(recipe.getId().toString());\n        }"),
        ("    private static boolean sendable(RecipeHolder<?> holder, net.minecraft.core.RegistryAccess access) {\n"
         "        try {\n            var recipe = holder.value();",
         "    private static boolean sendable(Recipe<?> recipe, net.minecraft.core.RegistryAccess access) {\n"
         "        try {"),
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

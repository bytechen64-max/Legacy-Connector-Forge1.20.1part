package legacyconnector.v1_7_10.net.minecraft.item.crafting;

import legacyconnector.v1_7_10.net.minecraft.inventory.InventoryCrafting;
import legacyconnector.v1_7_10.net.minecraft.item.ItemStack;
import legacyconnector.v1_7_10.net.minecraft.world.World;

/**
 * The firework recipes of 1.7.10 in one: rockets (paper, gunpowder, stars), stars (gunpowder, dyes, shape and effect
 * ingredients) and fading stars (a star and dyes). The modern firework recipes do the matching and building, so the results are
 * real modern fireworks; NEI's firework handler calls this with sample grids (and no world).
 */
public class RecipeFireworks implements IRecipe {
    private static final net.minecraft.world.item.crafting.CraftingRecipe[] MODERN = {
            // 1.20.1 constructs the vanilla firework recipes with their own id
            new net.minecraft.world.item.crafting.FireworkRocketRecipe(new net.minecraft.resources.ResourceLocation("minecraft", "firework_rocket"),
                    net.minecraft.world.item.crafting.CraftingBookCategory.MISC),
            new net.minecraft.world.item.crafting.FireworkStarRecipe(new net.minecraft.resources.ResourceLocation("minecraft", "firework_star"),
                    net.minecraft.world.item.crafting.CraftingBookCategory.MISC),
            new net.minecraft.world.item.crafting.FireworkStarFadeRecipe(new net.minecraft.resources.ResourceLocation("minecraft", "firework_star_fade"),
                    net.minecraft.world.item.crafting.CraftingBookCategory.MISC)};

    /** The result of the last grid that matched. */
    private ItemStack field_92102_a;

    @Override
    public boolean matches(InventoryCrafting inv, World world) {
        field_92102_a = null;
        var input = inv == null ? null : inv.mcc$craftingContainer();
        if (input == null) return false;
        net.minecraft.world.level.Level level = world == null ? null : world.mcc$liveLevel();
        for (var recipe : MODERN) {
            try {
                if (!recipe.matches(input, level)) continue;
                var result = recipe.assemble(input, level.registryAccess());
                if (result.isEmpty()) continue;
                field_92102_a = ItemStack.mcc$wrap(result);
                return true;
            } catch (RuntimeException e) {
                // a recipe that needs a level: try the next one
            }
        }
        return false;
    }

    private static net.minecraft.core.HolderLookup.Provider mcc$registries(net.minecraft.world.level.Level level) {
        if (level != null) return level.registryAccess();
        var server = net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();
        return server != null ? server.registryAccess() : net.minecraft.core.RegistryAccess.EMPTY;
    }

    @Override
    public ItemStack getCraftingResult(InventoryCrafting inv) {
        return field_92102_a == null ? null : field_92102_a.copy();
    }

    @Override
    public int getRecipeSize() {
        return 10;
    }

    @Override
    public ItemStack getRecipeOutput() {
        return field_92102_a;
    }
}

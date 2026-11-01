package org.kylepitcock.legacyconnector.v1_12_2.bridge;

import legacyconnector.v1_12_2.net.minecraft.item.ItemStack;
import legacyconnector.v1_12_2.net.minecraft.potion.PotionHelper;
import legacyconnector.v1_12_2.net.minecraft.potion.PotionType;
import legacyconnector.v1_12_2.net.minecraft.potion.PotionUtils;
import legacyconnector.v1_12_2.net.minecraftforge.common.brewing.BrewingRecipe;
import legacyconnector.v1_12_2.net.minecraftforge.common.brewing.BrewingRecipeRegistry;
import legacyconnector.v1_12_2.net.minecraftforge.common.brewing.IBrewingRecipe;
import legacyconnector.v1_12_2.net.minecraftforge.common.brewing.VanillaBrewingRecipe;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Legacy brewing into the modern brewing stand: when the server builds its brewing table, every potion mix of {@link PotionHelper} and every
 * Forge {@link BrewingRecipeRegistry} recipe a 1.12.2 mod added becomes a modern mix or brewing recipe. Mixes between vanilla potion types are
 * plain modern mixes; everything else is matched through the legacy objects.
 */
public final class Brewing1122 {
    private static final Logger LOG = LoggerFactory.getLogger("LegacyConnector/Brewing");
    private static boolean listening;

    private Brewing1122() {}

    public static synchronized void ensureListener() {
        if (listening) return;
        listening = true;
        register();
    }

    /**
     * Forge 1.20.1 has no "register the brewing recipes" event: {@code BrewingRecipeRegistry} is a static list that the patched
     * brewing stand consults instead of the vanilla table, so every legacy mix and recipe is added to it directly. A mix between
     * two potions known to the modern game would read better as a plain mix, but 1.20.1 has no public API for those
     * ({@code PotionBrewing}'s mix tables are private), so all of them are matched through the legacy objects.
     */
    private static void register() {
        int mixes = 0, recipes = 0;
        // containers mods added to PotionHelper.POTION_ITEMS (the vanilla bottles are the modern defaults)
        java.util.Set<net.minecraft.world.item.Item> containers = new java.util.HashSet<>();
        for (var ingredient : java.util.List.copyOf(PotionHelper.POTION_ITEMS)) {
            try {
                for (ItemStack s : ingredient.getMatchingStacks()) {
                    var item = Stacks1122.toModern(s).getItem();
                    if (item != net.minecraft.world.item.Items.AIR && item != net.minecraft.world.item.Items.POTION && item != net.minecraft.world.item.Items.SPLASH_POTION
                            && item != net.minecraft.world.item.Items.LINGERING_POTION && containers.add(item)) {
                        net.minecraftforge.common.brewing.BrewingRecipeRegistry.addRecipe(new ContainerRecipe(item));
                    }
                }
            } catch (RuntimeException | LinkageError e) {
                LOG.warn("Cannot add a legacy potion container: {}", e.toString());
            }
        }
        for (PotionHelper.MixPredicate<PotionType> mix : PotionHelper.mcc$mixes()) {
            try {
                if (mix.reagent == null) continue;
                net.minecraftforge.common.brewing.BrewingRecipeRegistry.addRecipe(new LegacyMix(mix));
                mixes++;
            } catch (RuntimeException | LinkageError e) {
                LOG.warn("Cannot add a legacy potion mix: {}", e.toString());
            }
        }
        for (IBrewingRecipe recipe : BrewingRecipeRegistry.getRecipes()) {
            if (recipe instanceof VanillaBrewingRecipe) continue;
            try {
                net.minecraftforge.common.brewing.BrewingRecipeRegistry.addRecipe(new LegacyRecipe(recipe));
                recipes++;
            } catch (RuntimeException | LinkageError e) {
                LOG.warn("Cannot add a legacy brewing recipe {}: {}", recipe.getClass().getName(), e.toString());
            }
        }
        if (mixes + recipes > 0) LOG.info("Added {} legacy potion mixes and {} legacy brewing recipes to the brewing stand", mixes, recipes);
    }

    /** A legacy potion container: the modern stand accepts it in a potion slot, the mixes do the rest. */
    private record ContainerRecipe(net.minecraft.world.item.Item item) implements net.minecraftforge.common.brewing.IBrewingRecipe {
        @Override
        public boolean isInput(net.minecraft.world.item.ItemStack input) {
            return !input.isEmpty() && input.getItem() == item;
        }

        @Override
        public boolean isIngredient(net.minecraft.world.item.ItemStack ingredient) {
            return false;
        }

        @Override
        public net.minecraft.world.item.ItemStack getOutput(net.minecraft.world.item.ItemStack input, net.minecraft.world.item.ItemStack ingredient) {
            return net.minecraft.world.item.ItemStack.EMPTY;
        }
    }

    /** A potion mix involving a type with no modern potion: matched on the legacy stacks. */
    private record LegacyMix(PotionHelper.MixPredicate<PotionType> mix) implements net.minecraftforge.common.brewing.IBrewingRecipe {
        @Override
        public boolean isInput(net.minecraft.world.item.ItemStack input) {
            PotionType from = mix.mcc$input();
            return from != null && !input.isEmpty() && PotionUtils.getPotionFromItem(Stacks1122.fromModern(input)) == from;
        }

        @Override
        public boolean isIngredient(net.minecraft.world.item.ItemStack ingredient) {
            return !ingredient.isEmpty() && mix.reagent.apply(Stacks1122.fromModern(ingredient));
        }

        @Override
        public net.minecraft.world.item.ItemStack getOutput(net.minecraft.world.item.ItemStack input, net.minecraft.world.item.ItemStack ingredient) {
            PotionType to = mix.mcc$output();
            if (to == null || !isInput(input) || !isIngredient(ingredient)) return net.minecraft.world.item.ItemStack.EMPTY;
            return Stacks1122.toModern(PotionUtils.addPotionToItemStack(Stacks1122.fromModern(input).copy(), to));
        }
    }

    /** A Forge brewing recipe of a legacy mod, asked through legacy stacks. */
    private record LegacyRecipe(IBrewingRecipe recipe) implements net.minecraftforge.common.brewing.IBrewingRecipe {
        @Override
        public boolean isInput(net.minecraft.world.item.ItemStack input) {
            return !input.isEmpty() && recipe.isInput(Stacks1122.fromModern(input));
        }

        @Override
        public boolean isIngredient(net.minecraft.world.item.ItemStack ingredient) {
            return !ingredient.isEmpty() && recipe.isIngredient(Stacks1122.fromModern(ingredient));
        }

        @Override
        public net.minecraft.world.item.ItemStack getOutput(net.minecraft.world.item.ItemStack input, net.minecraft.world.item.ItemStack ingredient) {
            if (input.isEmpty() || ingredient.isEmpty()) return net.minecraft.world.item.ItemStack.EMPTY;
            return Stacks1122.toModern(recipe.getOutput(Stacks1122.fromModern(input), Stacks1122.fromModern(ingredient)));
        }
    }
}

package org.kylepitcock.legacyconnector.core;

import java.util.ArrayList;
import java.util.List;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeManager;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.OnDatapackSyncEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * A recipe the client cannot decode (an ingredient or result that is an empty stack, e.g. from a legacy item that did
 * not translate) makes the whole recipe sync fail and disconnects every player. Such recipes are dropped before
 * recipes are sent, with a warning naming them.
 */
public final class RecipeSyncGuard {
    private static final Logger LOG = LoggerFactory.getLogger("LegacyConnector/Recipes");

    private RecipeSyncGuard() {}

    public static void register() {
        MinecraftForge.EVENT_BUS.addListener((OnDatapackSyncEvent e) -> clean(e.getPlayerList().getServer().getRecipeManager(),
                e.getPlayerList().getServer().registryAccess()));
    }

    private static void clean(RecipeManager manager, net.minecraft.core.RegistryAccess access) {
        List<Recipe<?>> keep = new ArrayList<>();
        List<String> dropped = new ArrayList<>();
        for (Recipe<?> recipe : manager.getRecipes()) {
            if (sendable(recipe, access)) keep.add(recipe);
            else dropped.add(recipe.getId().toString());
        }
        if (dropped.isEmpty()) return;
        manager.replaceRecipes(keep);
        LOG.warn("Dropped {} recipe(s) with empty item stacks (clients cannot receive them): {}", dropped.size(), dropped);
    }

    private static boolean sendable(Recipe<?> recipe, net.minecraft.core.RegistryAccess access) {
        try {
            if (recipe.getResultItem(access).isEmpty() && !recipe.isSpecial()) return false;
            // 1.20.1 has no custom ingredients (isCustom is 1.20.5+); the empty-stack check covers the same recipes
            for (Ingredient ing : recipe.getIngredients()) {
                for (var stack : ing.getItems()) if (stack.isEmpty()) return false;
            }
            return true;
        } catch (RuntimeException e) {
            return true; // not ours to judge
        }
    }
}

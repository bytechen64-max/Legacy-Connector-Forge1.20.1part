package org.kylepitcock.legacyconnector.v1_12_2.bridge;

import java.util.Optional;
import legacyconnector.v1_12_2.net.minecraft.entity.player.EntityPlayer;
import legacyconnector.v1_12_2.net.minecraft.inventory.InventoryCrafting;
import legacyconnector.v1_12_2.net.minecraft.item.ItemStack;
import legacyconnector.v1_12_2.net.minecraft.util.NonNullList;
import legacyconnector.v1_12_2.net.minecraft.world.World;
import net.minecraft.core.NonNullList;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.CraftingContainer;
import net.minecraft.world.inventory.TransientCraftingContainer;
import net.minecraft.world.item.crafting.CraftingRecipe;
import net.minecraft.world.item.crafting.RecipeType;

/**
 * Legacy crafting grids against the modern recipe book: vanilla's (and modern mods') recipes are data pack recipes that the legacy
 * {@code CraftingManager} registry does not hold, so a legacy container's grid also matches them here.
 *
 * <p>1.20.1 works on a {@code CraftingContainer} and hands back the {@code Recipe} itself: the 1.20.2
 * {@code CraftingInput}/{@code RecipeHolder} wrappers do not exist yet, and a shaped recipe's remaining items are indexed by
 * container slot there, so no match position has to be tracked.</p>
 */
public final class Crafting1122 {
    private Crafting1122() {}

    /** The menu a transient grid needs; nothing is ever moved through it. */
    private static final AbstractContainerMenu GRID = new AbstractContainerMenu(null, 0) {
        @Override
        public net.minecraft.world.item.ItemStack quickMoveStack(net.minecraft.world.entity.player.Player player, int slot) {
            return net.minecraft.world.item.ItemStack.EMPTY;
        }

        @Override
        public boolean stillValid(net.minecraft.world.entity.player.Player player) {
            return true;
        }
    };

    private record Match(CraftingRecipe recipe, CraftingContainer input) {}

    private static Optional<Match> find(InventoryCrafting inv, World world) {
        var level = Inventories1122.level(world);
        if (level == null || inv == null) return Optional.empty();
        int w = inv.getWidth(), h = inv.getHeight();
        if (w <= 0 || h <= 0 || w * h != inv.getSizeInventory()) return Optional.empty();
        var items = NonNullList.withSize(w * h, net.minecraft.world.item.ItemStack.EMPTY);
        boolean any = false;
        for (int i = 0; i < w * h; i++) {
            net.minecraft.world.item.ItemStack modern = Stacks1122.toModern(inv.getStackInSlot(i));
            any |= !modern.isEmpty();
            items.set(i, modern);
        }
        if (!any) return Optional.empty();
        var container = new TransientCraftingContainer(GRID, w, h, items);
        return level.getRecipeManager().getRecipeFor(RecipeType.CRAFTING, container, level).map(r -> new Match(r, container));
    }

    /** The result of the grid by the modern recipes, or empty. */
    public static ItemStack modernResult(InventoryCrafting inv, World world) {
        try {
            var level = Inventories1122.level(world);
            return find(inv, world).map(m -> Stacks1122.fromModern(m.recipe().assemble(m.input(), level.registryAccess())))
                    .orElse(ItemStack.EMPTY);
        } catch (RuntimeException | LinkageError e) {
            return ItemStack.EMPTY;
        }
    }

    /** What the modern recipe leaves in the grid (buckets, ...), laid out over the whole legacy grid; null when no modern recipe matches. */
    public static NonNullList<ItemStack> modernRemaining(InventoryCrafting inv, World world) {
        try {
            var match = find(inv, world);
            if (match.isEmpty()) return null;
            var m = match.get();
            var rest = m.recipe().getRemainingItems(m.input());
            NonNullList<ItemStack> out = NonNullList.withSize(inv.getSizeInventory(), ItemStack.EMPTY);
            for (int k = 0; k < rest.size() && k < out.size(); k++) out.set(k, Stacks1122.fromModern(rest.get(k)));
            return out;
        } catch (RuntimeException | LinkageError e) {
            return null;
        }
    }

    /** Forge's ItemCraftedEvent for a legacy result slot, through the modern event (legacy handlers hear it from the event bridge). */
    public static void firePlayerCrafted(EntityPlayer player, ItemStack stack, InventoryCrafting matrix) {
        var p = Inventories1122.player(player);
        if (p == null) return;
        var grid = new net.minecraft.world.SimpleContainer(matrix.getSizeInventory());
        for (int i = 0; i < matrix.getSizeInventory(); i++) grid.setItem(i, Stacks1122.toModern(matrix.getStackInSlot(i)));
        net.minecraftforge.event.ForgeEventFactory.firePlayerCraftingEvent(p, Stacks1122.toModern(stack), grid);
    }
}

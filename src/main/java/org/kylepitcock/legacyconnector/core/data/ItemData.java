package org.kylepitcock.legacyconnector.core.data;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.MapItem;

/**
 * The item-stack data the 1.21 component API exposes ({@code DataComponents.CUSTOM_DATA}, {@code CUSTOM_NAME},
 * {@code REPAIR_COST}), expressed with 1.20.1's item tag.
 *
 * <p>Before 1.20.5 an {@link ItemStack} has one {@link CompoundTag} and no components: the whole tag <em>is</em> the custom
 * data, the custom name is the tag's {@code display.Name}, and the repair cost is {@code RepairCost}. These helpers keep the
 * call sites readable and in one place instead of spreading tag keys through the shims.</p>
 */
public final class ItemData {
    private ItemData() {}

    // ------------------------------------------------------------------ custom data

    /** The stack's custom data, or null when it carries none (1.20.1: the stack's whole tag). */
    public static CompoundTag customData(ItemStack stack) {
        return stack == null || stack.isEmpty() ? null : stack.getTag();
    }

    public static boolean hasCustomData(ItemStack stack) {
        return stack != null && !stack.isEmpty() && stack.hasTag();
    }

    public static void setCustomData(ItemStack stack, CompoundTag tag) {
        if (stack == null || stack.isEmpty()) return;
        stack.setTag(tag == null || tag.isEmpty() ? null : tag);
    }

    public static void removeCustomData(ItemStack stack) {
        if (stack != null && !stack.isEmpty()) stack.setTag(null);
    }

    // ------------------------------------------------------------------ custom name

    public static boolean hasCustomName(ItemStack stack) {
        return stack != null && !stack.isEmpty() && stack.hasCustomHoverName();
    }

    public static void setCustomName(ItemStack stack, Component name) {
        if (stack != null && !stack.isEmpty()) stack.setHoverName(name);
    }

    public static void clearCustomName(ItemStack stack) {
        if (stack != null && !stack.isEmpty()) stack.resetHoverName();
    }

    // ------------------------------------------------------------------ repair cost

    public static int repairCost(ItemStack stack) {
        return stack == null ? 0 : stack.getBaseRepairCost();
    }

    public static void setRepairCost(ItemStack stack, int cost) {
        if (stack != null && !stack.isEmpty()) stack.setRepairCost(cost);
    }

    // ------------------------------------------------------------------ map id

    /** The map id a filled map carries, or -1 (1.20.1 keeps it in the stack tag, not in a MapId component). */
    public static int mapId(ItemStack stack) {
        Integer id = stack == null || stack.isEmpty() ? null : MapItem.getMapId(stack);
        return id == null ? -1 : id;
    }

    public static boolean hasMapId(ItemStack stack) {
        return stack != null && !stack.isEmpty() && MapItem.getMapId(stack) != null;
    }

    public static void setMapId(ItemStack stack, int id) {
        if (stack == null || stack.isEmpty()) return;
        stack.getOrCreateTag().putInt("map", id);
    }
}

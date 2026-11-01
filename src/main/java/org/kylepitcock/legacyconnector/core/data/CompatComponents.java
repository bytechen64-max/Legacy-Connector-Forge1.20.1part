package org.kylepitcock.legacyconnector.core.data;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.item.ItemStack;

/**
 * Legacy item metadata that no modern item expresses.
 *
 * <p>NeoForge 1.21 kept it in a registered {@code DataComponentType} ({@code legacyconnector:legacy_meta}). Item data
 * components only exist from 1.20.5 on, so on 1.20.1 the same value lives in the stack's tag under
 * {@link #LEGACY_META_TAG}: it is persisted with the stack and synced with it exactly like the component was.</p>
 */
public final class CompatComponents {
    /** Tag key the legacy metadata is stored under. */
    public static final String LEGACY_META_TAG = "legacyconnector:legacy_meta";

    private CompatComponents() {}

    /** The stored legacy metadata, or null when the stack carries none (also null for an empty stack). */
    public static Integer legacyMeta(ItemStack stack) {
        if (stack == null || stack.isEmpty()) return null;
        CompoundTag tag = stack.getTag();
        if (tag == null || !tag.contains(LEGACY_META_TAG)) return null;
        return tag.getInt(LEGACY_META_TAG);
    }

    public static int legacyMetaOr(ItemStack stack, int fallback) {
        Integer meta = legacyMeta(stack);
        return meta == null ? fallback : meta;
    }

    public static void setLegacyMeta(ItemStack stack, int meta) {
        if (stack == null || stack.isEmpty()) return;
        stack.getOrCreateTag().putInt(LEGACY_META_TAG, meta);
    }

    public static void clearLegacyMeta(ItemStack stack) {
        if (stack == null || stack.isEmpty()) return;
        CompoundTag tag = stack.getTag();
        if (tag == null) return;
        tag.remove(LEGACY_META_TAG);
        if (tag.isEmpty()) stack.setTag(null);
    }
}

package org.kylepitcock.legacyconnector.core.data;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Optional;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.alchemy.Potion;
import net.minecraft.world.item.alchemy.PotionUtils;

/**
 * A potion's contents (potion, custom colour, custom effects) as 1.21 spells them.
 *
 * <p>1.20.5 replaced the item's potion tag keys with a {@code PotionContents} data component; on 1.20.1 the same data lives in
 * the stack tag ({@code Potion}, {@code CustomPotionColor}, {@code CustomPotionEffects}) and is reached through
 * {@link PotionUtils}. The record keeps the call sites reading like the component API they were written against.</p>
 */
public record PotionData(Optional<Potion> potion, Optional<Integer> customColor, List<MobEffectInstance> customEffects) {
    public static final PotionData EMPTY = new PotionData(Optional.empty(), Optional.empty(), List.of());

    public static PotionData of(Potion potion) {
        return new PotionData(Optional.ofNullable(potion), Optional.empty(), List.of());
    }

    /** For callers that still hold the potion through a holder (the 1.21 shape). */
    public static PotionData of(Holder<Potion> potion) {
        return of(potion == null ? null : potion.value());
    }

    /** The contents of a potion item, an arrow or a cloud stack. */
    public static PotionData of(ItemStack stack) {
        if (stack == null || stack.isEmpty()) return EMPTY;
        CompoundTag tag = stack.getTag();
        boolean hasPotion = tag != null && tag.contains("Potion");
        Potion potion = PotionUtils.getPotion(stack);
        Optional<Potion> holder = hasPotion && potion != null ? Optional.of(potion) : Optional.empty();
        Optional<Integer> color = tag != null && tag.contains("CustomPotionColor")
                ? Optional.of(tag.getInt("CustomPotionColor")) : Optional.empty();
        return new PotionData(holder, color, PotionUtils.getCustomEffects(stack));
    }

    /** Writes this back into the stack's potion tags. */
    public void applyTo(ItemStack stack) {
        if (stack == null || stack.isEmpty()) return;
        potion.ifPresent(p -> PotionUtils.setPotion(stack, p));
        customColor.ifPresent(c -> stack.getOrCreateTag().putInt("CustomPotionColor", c));
        if (!customEffects.isEmpty()) PotionUtils.setCustomEffects(stack, customEffects);
    }

    /** The potion's own effects followed by the custom ones (what the old {@code getAllEffects} returned). */
    public List<MobEffectInstance> allEffects() {
        List<MobEffectInstance> out = new ArrayList<>();
        potion.ifPresent(p -> out.addAll(PotionUtils.getAllEffects(p, List.of())));
        out.addAll(customEffects);
        return out;
    }

    public boolean isEmpty() {
        return potion.isEmpty() && customColor.isEmpty() && customEffects.isEmpty();
    }

    /** The colour the potion shows: the custom one when set, else the effects' mix. */
    public int color() {
        return customColor.orElseGet(() -> PotionUtils.getColor(allEffects()));
    }

    public static int getColor(Potion potion) {
        return PotionUtils.getColor(potion);
    }

    public static int getColor(Collection<MobEffectInstance> effects) {
        return PotionUtils.getColor(effects);
    }

    public static Optional<Integer> getColorOptional(Collection<MobEffectInstance> effects) {
        return Optional.of(PotionUtils.getColor(effects));
    }

    public static ItemStack createItemStack(Item item, Potion potion) {
        ItemStack stack = new ItemStack(item);
        if (potion != null) PotionUtils.setPotion(stack, potion);
        return stack;
    }

    public static String potionId(Potion potion) {
        var key = potion == null ? null : BuiltInRegistries.POTION.getKey(potion);
        return key == null ? null : key.toString();
    }
}

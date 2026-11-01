package org.kylepitcock.legacyconnector.mixin.access;

import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

/**
 * {@code AbstractArrow#getPickupItem} is protected in 1.20.1 (1.21 exposes it as {@code getPickupItemStackOrigin}), so the
 * 1.12.2 arrow shim reads the stack a player picks up through this invoker.
 */
@Mixin(AbstractArrow.class)
public interface AbstractArrowAccess {
    @Invoker("getPickupItem")
    ItemStack legacyconnector$pickupItem();

}

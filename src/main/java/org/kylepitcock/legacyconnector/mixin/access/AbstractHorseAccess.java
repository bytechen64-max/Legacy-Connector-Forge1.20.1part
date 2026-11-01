package org.kylepitcock.legacyconnector.mixin.access;

import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.animal.horse.AbstractHorse;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/**
 * The saddle/armour/chest inventory of a horse. 1.20.1 keeps it in a protected field without a getter (1.20.5 added
 * {@code getInventory()}), so the legacy horse shim reads it through this accessor.
 */
@Mixin(AbstractHorse.class)
public interface AbstractHorseAccess {
    @Accessor("inventory")
    SimpleContainer legacyconnector$inventory();

    static SimpleContainer inventory(AbstractHorse horse) {
        return ((AbstractHorseAccess) horse).legacyconnector$inventory();
    }
}

package org.kylepitcock.legacyconnector.mixin.access;

import java.util.Map;
import net.minecraft.core.dispenser.DispenseItemBehavior;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.DispenserBlock;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/**
 * The behaviour the modded dispenser falls back to for a vanilla item. 1.20.1 keeps the map private (1.20.5 added a getter), so
 * the 1.12.2 dispenser bridge reads it through this accessor.
 */
@Mixin(DispenserBlock.class)
public interface DispenserBlockAccess {
    @Accessor("DISPENSER_REGISTRY")
    static Map<Item, DispenseItemBehavior> legacyconnector$dispenserRegistry() {
        throw new AssertionError("mixin");
    }
}

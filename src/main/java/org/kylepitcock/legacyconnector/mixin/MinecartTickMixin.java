package org.kylepitcock.legacyconnector.mixin;

import net.minecraft.world.entity.vehicle.AbstractMinecart;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * 1.12.2 and 1.7.10 posted their MinecartUpdateEvent from the minecart's own tick. 1.20.1 has no tick event for a non-living
 * entity, so both bridges' events are posted from here (each checks whether a legacy handler exists).
 */
@Mixin(AbstractMinecart.class)
public abstract class MinecartTickMixin {
    @Inject(method = "tick", at = @At("HEAD"))
    private void legacyconnector$legacyMinecartUpdate(CallbackInfo ci) {
        AbstractMinecart self = (AbstractMinecart) (Object) this;
        org.kylepitcock.legacyconnector.v1_12_2.entity.ForgeEvents1122.minecartTick(self);
        org.kylepitcock.legacyconnector.v1_7_10.bridge.ForgeEvents1710.minecartTick(self);
    }
}

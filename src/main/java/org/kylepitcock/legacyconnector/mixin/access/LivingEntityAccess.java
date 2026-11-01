package org.kylepitcock.legacyconnector.mixin.access;

import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

/**
 * {@code LivingEntity#jumpFromGround} is protected in 1.20.1 (it became reachable through the jump event in 1.21), so the
 * shim's {@code EntityLivingBase.jump()} invokes it through this accessor.
 */
@Mixin(LivingEntity.class)
public interface LivingEntityAccess {
    @Invoker("jumpFromGround")
    void legacyconnector$jumpFromGround();

    static void jumpFromGround(LivingEntity entity) {
        ((LivingEntityAccess) entity).legacyconnector$jumpFromGround();
    }
}

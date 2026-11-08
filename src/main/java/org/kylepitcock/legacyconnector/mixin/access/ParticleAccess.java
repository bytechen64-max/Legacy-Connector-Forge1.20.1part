package org.kylepitcock.legacyconnector.mixin.access;

import net.minecraft.client.particle.Particle;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

@Mixin(Particle.class)
public interface ParticleAccess {
    @Invoker("setAlpha") void legacyconnector$setAlpha(float alpha);
}

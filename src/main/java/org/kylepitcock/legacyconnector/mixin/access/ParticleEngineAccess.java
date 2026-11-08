package org.kylepitcock.legacyconnector.mixin.access;

import net.minecraft.client.particle.Particle;
import net.minecraft.client.particle.ParticleEngine;
import net.minecraft.core.particles.ParticleOptions;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

@Mixin(ParticleEngine.class)
public interface ParticleEngineAccess {
    @Invoker("makeParticle")
    Particle legacyconnector$makeParticle(ParticleOptions options, double x, double y, double z, double vx, double vy, double vz);
}

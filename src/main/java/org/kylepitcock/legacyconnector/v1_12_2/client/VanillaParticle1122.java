package org.kylepitcock.legacyconnector.v1_12_2.client;

import legacyconnector.v1_12_2.net.minecraft.client.particle.Particle;
import legacyconnector.v1_12_2.net.minecraft.world.World;
import net.minecraft.client.Minecraft;

/** A factory-created vanilla particle; creation and submission remain separate. */
public final class VanillaParticle1122 extends Particle {
    private final net.minecraft.client.particle.Particle modern;
    private boolean added;
    private VanillaParticle1122(World world, double x, double y, double z, net.minecraft.client.particle.Particle modern) {
        super(world, x, y, z);
        this.modern = modern;
    }
    public static Particle create(int id, World world, double x, double y, double z, double vx, double vy, double vz, int[] params) {
        var mc = Minecraft.getInstance();
        if (mc.level == null) return null;
        var options = LegacyParticles1122.options(id, vx, vy, vz, params);
        if (options == null) return null;
        if (id == 30 || id == 15 || id == 16) vx = vy = vz = 0;
        var modern = ((org.kylepitcock.legacyconnector.mixin.access.ParticleEngineAccess) mc.particleEngine)
                .legacyconnector$makeParticle(options, x, y, z, vx, vy, vz);
        return modern == null ? null : new VanillaParticle1122(world, x, y, z, modern);
    }
    public void addToEngine() {
        if (!added) { Minecraft.getInstance().particleEngine.add(modern); added = true; }
    }
    @Override public void setRBGColorF(float r, float g, float b) { super.setRBGColorF(r, g, b); modern.setColor(r, g, b); }
    @Override public void setAlphaF(float alpha) {
        super.setAlphaF(alpha);
        ((org.kylepitcock.legacyconnector.mixin.access.ParticleAccess) modern).legacyconnector$setAlpha(alpha);
    }
    @Override public void setPosition(double x, double y, double z) {
        super.setPosition(x, y, z);
        if (modern != null) modern.setPos(x, y, z);
    }
    @Override public Particle multipleParticleScaleBy(float scale) { modern.scale(scale); return this; }
    @Override public Particle multiplyVelocity(float scale) { modern.setPower(scale); return this; }
    @Override public void setMaxAge(int age) { modern.setLifetime(age); }
    @Override public void setExpired() { modern.remove(); }
    @Override public boolean isAlive() { return modern.isAlive(); }
    @Override public void onUpdate() { modern.tick(); }
}

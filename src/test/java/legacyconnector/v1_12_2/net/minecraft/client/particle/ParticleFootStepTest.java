package legacyconnector.v1_12_2.net.minecraft.client.particle;

import legacyconnector.v1_12_2.net.minecraft.client.renderer.BufferBuilder;
import legacyconnector.v1_12_2.net.minecraft.client.renderer.texture.TextureManager;
import legacyconnector.v1_12_2.net.minecraft.util.ResourceLocation;
import org.kylepitcock.legacyconnector.core.synth.Synth;
import org.kylepitcock.legacyconnector.v1_12_2.bridge.ParticleFactories1122;
import org.kylepitcock.legacyconnector.v1_7_10.client.RenderContext;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class ParticleFootStepTest {
    @Test void factoryCreatesFootprintThatExpiresAtTwoHundredTicks() throws Throwable {
        ParticleFactories1122.register();
        var particle = (Particle) Synth.callInstance("net.minecraft.client.particle.ParticleFootStep$Factory.createParticle", null,
                new Object[]{28, null, 1D, 2D, 3D, 4D, 5D, 6D, new int[0]});
        assertInstanceOf(ParticleFootStep.class, particle);
        assertEquals(3, particle.getFXLayer());
        for (int i = 0; i < 199; i++) particle.onUpdate();
        assertTrue(particle.isAlive()); particle.onUpdate(); assertFalse(particle.isAlive());
        assertEquals(1, particle.posX); assertEquals(2, particle.posY); assertEquals(3, particle.posZ);
    }
    @Test void footprintIsFlatCameraRelativeAndFadesWithPartialTicks() {
        var textures = new TextureManager(null) {
            @Override public void bindTexture(ResourceLocation location) { assertEquals("textures/particle/footprint.png", location.getPath()); }
        };
        var particle = new ParticleFootStep(textures, null, 2, 3, 4);
        double oldX = Particle.interpPosX, oldY = Particle.interpPosY, oldZ = Particle.interpPosZ;
        Particle.interpPosX = 1; Particle.interpPosY = 1; Particle.interpPosZ = 1;
        var capture = RenderContext.beginCapture();
        try {
            var buffer = new BufferBuilder(64);
            particle.renderParticle(buffer, null, 0, 0, 0, 0, 0, 0);
            for (int i = 0; i < 180; i++) particle.onUpdate();
            particle.renderParticle(buffer, null, .5F, 0, 0, 0, 0, 0);
            assertEquals(2, capture.size());
            for (int i = 0; i < 4; i++) assertEquals(2, capture.get(0, i, 1), .00001);
            assertEquals(.875, capture.get(0, 0, 0), .00001);
            assertEquals(3.125, capture.get(0, 0, 2), .00001);
            int firstAlpha = (int) ((long) capture.get(0, 0, 5) >>> 24);
            int fadedAlpha = (int) ((long) capture.get(1, 0, 5) >>> 24);
            assertEquals(51, firstAlpha);
            assertTrue(fadedAlpha > 0 && fadedAlpha < firstAlpha);
        } finally {
            RenderContext.endCapture();
            Particle.interpPosX = oldX; Particle.interpPosY = oldY; Particle.interpPosZ = oldZ;
        }
    }
}

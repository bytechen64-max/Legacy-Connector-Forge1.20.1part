package legacyconnector.v1_12_2.net.minecraft.client.particle;

import legacyconnector.v1_12_2.net.minecraft.client.renderer.BufferBuilder;
import legacyconnector.v1_12_2.net.minecraft.client.renderer.texture.TextureManager;
import legacyconnector.v1_12_2.net.minecraft.client.renderer.vertex.DefaultVertexFormats;
import legacyconnector.v1_12_2.net.minecraft.entity.Entity;
import legacyconnector.v1_12_2.net.minecraft.util.ResourceLocation;
import legacyconnector.v1_12_2.net.minecraft.util.math.BlockPos;
import legacyconnector.v1_12_2.net.minecraft.world.World;
import legacyconnector.v1_7_10.org.lwjgl.opengl.GL11;

/** Stationary ground decal using the shared generated vanilla footprint texture. */
public class ParticleFootStep extends Particle {
    private static final ResourceLocation FOOTPRINT_TEXTURE = new ResourceLocation("textures/particle/footprint.png");
    private int footstepAge;
    private int footstepMaxAge = 200;
    private final TextureManager currentFootSteps;
    public ParticleFootStep(TextureManager textures, World world, double x, double y, double z) {
        super(world, x, y, z);
        currentFootSteps = textures;
        canCollide = false;
    }
    @Override public int getFXLayer() { return 3; }
    @Override public void onUpdate() { if (++footstepAge >= footstepMaxAge) setExpired(); }
    @Override public void renderParticle(BufferBuilder buffer, Entity viewer, float partialTicks, float rx, float rz, float ryz, float rxy, float rxz) {
        float age = (footstepAge + partialTicks) / footstepMaxAge;
        float alpha = Math.max(0, Math.min(1, 2 - age * age * 2)) * 0.2F * particleAlpha;
        float light = world == null ? 1 : world.getLightBrightness(new BlockPos(posX, posY, posZ));
        double x = posX - interpPosX, y = posY - interpPosY, z = posZ - interpPosZ;
        (currentFootSteps == null ? TextureManager.mcc$instance() : currentFootSteps).bindTexture(FOOTPRINT_TEXTURE);
        GL11.glPushAttrib(GL11.GL_ALL_ATTRIB_BITS);
        try {
            GL11.glDisable(GL11.GL_LIGHTING);
            GL11.glEnable(GL11.GL_BLEND);
            GL11.glBlendFunc(GL11.GL_SRC_ALPHA, GL11.GL_ONE_MINUS_SRC_ALPHA);
            buffer.begin(7, DefaultVertexFormats.POSITION_TEX_COLOR);
            buffer.pos(x - .125, y, z + .125).tex(0, 1).color(light * particleRed, light * particleGreen, light * particleBlue, alpha).endVertex();
            buffer.pos(x + .125, y, z + .125).tex(1, 1).color(light * particleRed, light * particleGreen, light * particleBlue, alpha).endVertex();
            buffer.pos(x + .125, y, z - .125).tex(1, 0).color(light * particleRed, light * particleGreen, light * particleBlue, alpha).endVertex();
            buffer.pos(x - .125, y, z - .125).tex(0, 0).color(light * particleRed, light * particleGreen, light * particleBlue, alpha).endVertex();
            buffer.finishDrawing();
            new legacyconnector.v1_12_2.net.minecraft.client.renderer.WorldVertexBufferUploader().draw(buffer);
        } finally { GL11.glPopAttrib(); }
    }
}

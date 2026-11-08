package legacyconnector.v1_12_2.net.minecraft.client.model;

import legacyconnector.v1_12_2.net.minecraft.entity.Entity;

/** The three intersecting boxes of the vanilla shulker projectile. */
public class ModelShulkerBullet extends ModelBase {
    private final ModelRenderer renderer;

    public ModelShulkerBullet() {
        textureWidth = 64;
        textureHeight = 32;
        renderer = new ModelRenderer(this, 0, 0);
        renderer.addBox(-4, -4, -1, 8, 8, 2);
        renderer.setTextureOffset(0, 10).addBox(-1, -4, -4, 2, 8, 8);
        renderer.setTextureOffset(20, 0).addBox(-4, -1, -4, 8, 2, 8);
    }

    @Override public void render(Entity entity, float limbSwing, float limbSwingAmount, float age, float yaw, float pitch, float scale) {
        setRotationAngles(limbSwing, limbSwingAmount, age, yaw, pitch, scale, entity);
        renderer.render(scale);
    }

    @Override public void setRotationAngles(float limbSwing, float limbSwingAmount, float age, float yaw, float pitch, float scale, Entity entity) {
        renderer.rotateAngleY = yaw * ((float) Math.PI / 180);
        renderer.rotateAngleX = pitch * ((float) Math.PI / 180);
    }
}

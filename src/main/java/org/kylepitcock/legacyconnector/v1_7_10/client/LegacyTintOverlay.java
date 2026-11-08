package org.kylepitcock.legacyconnector.v1_7_10.client;

import com.mojang.blaze3d.platform.NativeImage;
import com.mojang.blaze3d.systems.RenderSystem;
import java.util.HashMap;
import java.util.Map;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.texture.DynamicTexture;
import net.minecraft.resources.ResourceLocation;
import org.kylepitcock.legacyconnector.compat.IrisState;
import org.kylepitcock.legacyconnector.core.access.Accessors;

/** A separate overlay sampler replaces vanilla hurt red, without multiplying the entity's skin colour. */
final class LegacyTintOverlay {
    private record Key(RenderType base, int color) {}
    private static final Map<Key, RenderType> TYPES = new HashMap<>();
    private static final Map<Integer, ResourceLocation> TEXTURES = new HashMap<>();

    static RenderType wrap(RenderType base, int color) {
        return TYPES.computeIfAbsent(new Key(base, color), key -> {
            ResourceLocation texture = TEXTURES.computeIfAbsent(color, LegacyTintOverlay::createTexture);
            int[] previousSampler = new int[1];
            RenderType wrapped = new RenderType(base + "/legacy_tint_" + Integer.toHexString(color),
                    base.format(), base.mode(), base.bufferSize(), base.affectsCrumbling(), Accessors.sortOnUpload(base),
                    () -> {
                        base.setupRenderState();
                        previousSampler[0] = RenderSystem.getShaderTexture(1);
                        RenderSystem.setShaderTexture(1, texture);
                    }, () -> {
                        base.clearRenderState();
                        RenderSystem.setShaderTexture(1, previousSampler[0]);
                    }) {};
            IrisState.copyBatchingClass(base, wrapped);
            return wrapped;
        });
    }

    private static ResourceLocation createTexture(int argb) {
        NativeImage image = new NativeImage(16, 16, false);
        int abgr = argb & 0xFF00FF00 | (argb & 255) << 16 | (argb >> 16 & 255);
        for (int y = 0; y < 16; y++) for (int x = 0; x < 16; x++) image.setPixelRGBA(x, y, abgr);
        ResourceLocation location = ResourceLocation.fromNamespaceAndPath("legacyconnector", "overlay/tint_" + Integer.toHexString(argb));
        Minecraft.getInstance().getTextureManager().register(location, new DynamicTexture(image));
        return location;
    }
}

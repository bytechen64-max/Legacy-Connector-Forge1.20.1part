package org.kylepitcock.legacyconnector.v1_7_10.client;

import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import java.io.IOException;
import java.io.UncheckedIOException;
import net.minecraft.client.renderer.ShaderInstance;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.client.event.RegisterShadersEvent;

/** Legacy additive model layers alpha-tested their texture before adding its RGB to the scene. */
final class LegacyShaders {
    static ShaderInstance eyesCutout;

    static void register(RegisterShadersEvent event) {
        try {
            event.registerShader(new ShaderInstance(event.getResourceProvider(),
                    ResourceLocation.fromNamespaceAndPath("legacyconnector", "legacy_eyes_cutout"), DefaultVertexFormat.NEW_ENTITY),
                    shader -> eyesCutout = shader);
        } catch (IOException e) {
            throw new UncheckedIOException("Loading legacy additive cutout shader", e);
        }
    }
}

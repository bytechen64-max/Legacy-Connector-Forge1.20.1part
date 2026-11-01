package org.kylepitcock.legacyconnector.v1_7_10.client;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.resources.ResourceLocation;

/**
 * GUI sprites on 1.20.1.
 *
 * <p>1.20.2 introduced a {@code gui} sprite atlas with {@code GuiGraphics.blitSprite}; on 1.20.1 a GUI texture is still a plain
 * image drawn with {@code blit}. The sprite id therefore becomes the texture path it stands for
 * ({@code textures/gui/sprites/<id>.png}), which is where a resource pack that ships the 1.20.2 layout keeps it.</p>
 */
public final class LegacyGuiSprites {
    private LegacyGuiSprites() {}

    /** The texture file a sprite id stands for. */
    public static ResourceLocation texture(ResourceLocation sprite) {
        return ResourceLocation.fromNamespaceAndPath(sprite.getNamespace(), "textures/gui/sprites/" + sprite.getPath() + ".png");
    }

    /** Draws a whole sprite at its natural size. */
    public static void blit(GuiGraphics gui, ResourceLocation sprite, int x, int y, int width, int height) {
        gui.blit(texture(sprite), x, y, 0.0F, 0.0F, width, height, width, height);
    }

    /** Draws a region of a sprite sheet (the 1.20.2 nine-argument {@code blitSprite} form). */
    public static void blit(GuiGraphics gui, ResourceLocation sprite, int texWidth, int texHeight, int u, int v,
            int x, int y, int width, int height) {
        gui.blit(texture(sprite), x, y, (float) u, (float) v, width, height, texWidth, texHeight);
    }
}

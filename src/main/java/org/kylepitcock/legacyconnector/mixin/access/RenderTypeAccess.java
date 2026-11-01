package org.kylepitcock.legacyconnector.mixin.access;

import net.minecraft.client.renderer.RenderType;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/**
 * Whether a render type sorts its buffer before uploading it.
 *
 * <p>1.20.1 keeps it in a private field (1.21 exposes it through {@code sortOnUpload()}) and a legacy render type built from a
 * modern one has to copy it. Forge applies a mod's access transformer at runtime only, so it is read through this accessor.</p>
 */
@Mixin(RenderType.class)
public interface RenderTypeAccess {
    @Accessor("sortOnUpload")
    boolean legacyconnector$sortOnUpload();

}

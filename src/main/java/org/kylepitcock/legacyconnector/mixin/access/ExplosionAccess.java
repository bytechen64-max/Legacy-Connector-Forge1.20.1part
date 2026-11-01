package org.kylepitcock.legacyconnector.mixin.access;

import net.minecraft.world.level.Explosion;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/**
 * An explosion's radius.
 *
 * <p>1.20.1 keeps it in a private field (1.21 exposes it through {@code radius()}), and Forge applies a mod's access transformer at
 * runtime only, so the shim's 1.12.2 {@code Explosion} view reads it through this accessor.</p>
 */
@Mixin(Explosion.class)
public interface ExplosionAccess {
    @Accessor("radius")
    float legacyconnector$radius();

}

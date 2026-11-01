package org.kylepitcock.legacyconnector.mixin.access;

import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.Entity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/**
 * The 1.20.1 entity portal state.
 *
 * <p>1.20.5 replaced these three protected fields with a {@code PortalProcessor} and public accessors; on 1.20.1 the shim has to
 * read and write them, and Forge only applies a mod's access transformer at <em>runtime</em> (ForgeGradle does not widen the
 * compile classpath with it), so the shim goes through this accessor mixin. Mixin generates the accessors at load time.</p>
 */
@Mixin(Entity.class)
public interface EntityAccess {
    @Accessor("isInsidePortal")
    boolean legacyconnector$insidePortal();

    @Accessor("isInsidePortal")
    void legacyconnector$setInsidePortal(boolean value);

    @Accessor("portalTime")
    int legacyconnector$portalTime();

    @Accessor("portalTime")
    void legacyconnector$setPortalTime(int value);

    @Accessor("portalEntrancePos")
    BlockPos legacyconnector$portalEntrancePos();

    @Accessor("portalEntrancePos")
    void legacyconnector$setPortalEntrancePos(BlockPos pos);
}

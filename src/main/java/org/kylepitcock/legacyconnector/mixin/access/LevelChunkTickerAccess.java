package org.kylepitcock.legacyconnector.mixin.access;

import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.chunk.LevelChunk;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

/**
 * Drops the ticker of a block entity that a legacy mod stops ticking (perf.staticTileEntities). 1.20.1 keeps the method private,
 * so the shim invokes it through this mixin.
 */
@Mixin(LevelChunk.class)
public interface LevelChunkTickerAccess {
    @Invoker("updateBlockEntityTicker")
    void legacyconnector$updateBlockEntityTicker(BlockEntity be);
}

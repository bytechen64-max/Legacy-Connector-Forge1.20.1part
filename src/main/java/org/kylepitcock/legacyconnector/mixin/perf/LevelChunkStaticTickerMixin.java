package org.kylepitcock.legacyconnector.mixin.perf;

import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.chunk.LevelChunk;
import org.kylepitcock.legacyconnector.core.perf.StaticTickers;
import org.kylepitcock.legacyconnector.mixin.access.LevelChunkTickerAccess;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * perf.staticTileEntities: a legacy tile entity host whose tile entity never ticks (see {@link StaticTickers}) gets no ticker, as
 * 1.7.10 and 1.12.2 never put such tile entities in their ticking list. Only Legacy Connector's own host block entities are
 * affected; every other block entity gets the ticker its block returns.
 */
@Mixin(LevelChunk.class)
public abstract class LevelChunkStaticTickerMixin {
    @Inject(method = "updateBlockEntityTicker", at = @At("HEAD"), cancellable = true, require = 0)
    private void legacyconnector$noStaticTicker(BlockEntity blockEntity, CallbackInfo ci) {
        if (blockEntity == null || !StaticTickers.noTicker(blockEntity)) return;
        // the chunk no longer ticks it: the state's ticker is not asked for at all
        ((LevelChunkTickerAccess) this).legacyconnector$removeTicker(blockEntity.getBlockPos());
        ci.cancel();
    }
}

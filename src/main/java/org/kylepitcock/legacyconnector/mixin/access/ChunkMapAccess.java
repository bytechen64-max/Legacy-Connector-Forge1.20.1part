package org.kylepitcock.legacyconnector.mixin.access;

import net.minecraft.server.level.ChunkHolder;
import net.minecraft.server.level.ChunkMap;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

/**
 * The chunk holders of the server's chunk map, which 1.20.1 keeps behind protected methods.
 *
 * <p>The shim reads blocks and tile entities off the server thread only for chunks that are fully loaded right now, which needs
 * these two lookups. Forge applies a mod's access transformer at runtime only (ForgeGradle does not widen the compile classpath
 * with it), so the calls go through this invoker mixin.</p>
 */
@Mixin(ChunkMap.class)
public interface ChunkMapAccess {
    @Invoker("getVisibleChunkIfPresent")
    ChunkHolder legacyconnector$visibleChunk(long chunkPos);

    @Invoker("getChunks")
    Iterable<ChunkHolder> legacyconnector$chunks();

    /** The tracked entities of the chunk map, by entity id: who the server sends an entity to. */
    @org.spongepowered.asm.mixin.gen.Accessor("entityMap")
    it.unimi.dsi.fastutil.ints.Int2ObjectMap<Object> legacyconnector$entityMap();
}

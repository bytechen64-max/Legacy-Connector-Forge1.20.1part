package legacyconnector.v1_12_2.net.minecraft.client.renderer.chunk;

import com.google.common.util.concurrent.Futures;
import com.google.common.util.concurrent.ListenableFuture;
import java.util.LinkedHashSet;
import legacyconnector.v1_12_2.net.minecraft.client.renderer.BufferBuilder;
import legacyconnector.v1_12_2.net.minecraft.client.renderer.RegionRenderCacheBuilder;
import legacyconnector.v1_12_2.net.minecraft.util.BlockRenderLayer;

/** Deferred requests are drained synchronously on the calling render thread; no legacy worker pool is started. */
public class ChunkRenderDispatcher {
    private final LinkedHashSet<RenderChunk> pending = new LinkedHashSet<>();
    public ChunkRenderDispatcher() {}
    public ChunkRenderDispatcher(int countRenderBuilders) {}
    public String getDebugInfo() { return "Pending: " + pending.size() + " (synchronous)"; }
    public boolean updateChunkLater(RenderChunk chunk) { pending.add(chunk); return true; }
    public boolean updateTransparencyLater(RenderChunk chunk) { return updateChunkLater(chunk); }
    public boolean updateChunkNow(RenderChunk chunk) {
        pending.remove(chunk); chunk.rebuildNow(); return true;
    }
    public boolean runChunkUploads(long deadline) {
        boolean updated = false;
        while (!pending.isEmpty()) {
            var chunk = pending.iterator().next();
            updateChunkNow(chunk); updated = true;
            if (deadline == 0 || System.nanoTime() >= deadline) break;
        }
        return updated;
    }
    public ListenableFuture<Object> uploadChunk(BlockRenderLayer layer, BufferBuilder data, RenderChunk chunk, CompiledChunk compiled, double distance) {
        try { chunk.upload(layer, data); return Futures.immediateFuture(null); }
        catch (RuntimeException e) { return Futures.immediateFailedFuture(e); }
    }
    public void clearChunkUpdates() { pending.clear(); }
    public void stopChunkUpdates() { clearChunkUpdates(); }
    public void stopWorkerThreads() { clearChunkUpdates(); }
    public boolean hasNoChunkUpdates() { return pending.isEmpty(); }
    public boolean hasNoFreeRenderBuilders() { return false; }
    public RegionRenderCacheBuilder allocateRenderBuilder() { return new RegionRenderCacheBuilder(); }
    public void freeRenderBuilder(RegionRenderCacheBuilder builder) {}
    public ChunkCompileTaskGenerator getNextChunkUpdate() {
        if (pending.isEmpty()) return null;
        var chunk = pending.iterator().next(); pending.remove(chunk);
        return chunk.makeCompileTaskChunk();
    }
}

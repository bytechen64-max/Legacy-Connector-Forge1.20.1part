package legacyconnector.v1_12_2.net.minecraft.client.renderer.chunk;

import legacyconnector.v1_12_2.net.minecraft.client.renderer.*;
import legacyconnector.v1_12_2.net.minecraft.client.renderer.vertex.DefaultVertexFormats;
import legacyconnector.v1_12_2.net.minecraft.util.BlockRenderLayer;
import org.kylepitcock.legacyconnector.v1_7_10.client.RenderContext;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class ChunkRenderingTest {
    private static BufferBuilder quad() {
        var data = new BufferBuilder(64);
        data.begin(7, DefaultVertexFormats.BLOCK);
        for (int i = 0; i < 4; i++) data.pos(i % 2, 0, i / 2).color(255, 255, 255, 255).tex(0, 0).lightmap(240, 240).endVertex();
        return data;
    }
    @Test void vboDrawRetainsUploadedDataAndAppliesCameraOffsetOnce() {
        var chunk = new RenderChunk(null, null, 0);
        chunk.setPosition(32, 16, -16);
        var data = quad();
        chunk.upload(BlockRenderLayer.SOLID, data);
        data.begin(7, DefaultVertexFormats.BLOCK); // reuse must not overwrite the upload
        data.pos(99, 99, 99).color(0, 0, 0, 0).tex(0, 0).lightmap(0, 0).endVertex();
        var list = new VboRenderList();
        list.initialize(30.5, 15, -18);
        list.addRenderChunk(chunk, BlockRenderLayer.SOLID);
        var capture = RenderContext.beginCapture();
        try {
            list.renderChunkLayer(BlockRenderLayer.SOLID);
            list.renderChunkLayer(BlockRenderLayer.SOLID);
            assertEquals(1, capture.size());
            assertEquals(1.5, capture.get(0, 0, 0), .00001);
            assertEquals(1, capture.get(0, 0, 1), .00001);
            assertEquals(2, capture.get(0, 0, 2), .00001);
        } finally { RenderContext.endCapture(); }
    }
    @Test void displayListReplaysUploadedMeshAndDeletionRemovesIt() {
        var chunk = new ListedRenderChunk(null, null, 0);
        chunk.upload(BlockRenderLayer.SOLID, quad());
        var compiled = new CompiledChunk();
        compiled.setLayerUsed(BlockRenderLayer.SOLID);
        chunk.setCompiledChunk(compiled);
        var list = new RenderList();
        list.initialize(0, 0, 0);
        var capture = RenderContext.beginCapture();
        try {
            list.addRenderChunk(chunk, BlockRenderLayer.SOLID);
            list.renderChunkLayer(BlockRenderLayer.SOLID);
            assertEquals(1, capture.size());
            chunk.deleteGlResources();
            list.addRenderChunk(chunk, BlockRenderLayer.SOLID);
            list.renderChunkLayer(BlockRenderLayer.SOLID);
            assertEquals(1, capture.size());
        } finally { RenderContext.endCapture(); }
    }
    @Test void deferredBuildsAreDeduplicatedAndRespectSingleUploadBudget() {
        int[] builds = {0};
        var a = new RenderChunk(null, null, 0) { public void rebuildNow() { builds[0]++; } };
        var b = new RenderChunk(null, null, 1) { public void rebuildNow() { builds[0]++; } };
        var dispatcher = new ChunkRenderDispatcher();
        dispatcher.updateChunkLater(a); dispatcher.updateChunkLater(a); dispatcher.updateChunkLater(b);
        assertTrue(dispatcher.runChunkUploads(0));
        assertEquals(1, builds[0]); assertFalse(dispatcher.hasNoChunkUpdates());
        assertTrue(dispatcher.runChunkUploads(Long.MAX_VALUE));
        assertEquals(2, builds[0]); assertTrue(dispatcher.hasNoChunkUpdates());
        assertFalse(dispatcher.runChunkUploads(0));
    }
    @Test void cancelledTasksInvalidateChunkAndRunCleanupExactlyOnce() {
        var chunk = new RenderChunk(null, null, 0);
        var task = chunk.makeCompileTaskChunk();
        int[] callbacks = {0};
        task.addFinishRunnable(() -> callbacks[0]++);
        chunk.clearNeedsUpdate();
        chunk.stopCompileTask(); chunk.stopCompileTask();
        assertTrue(chunk.needsUpdate()); assertTrue(task.isFinished()); assertEquals(1, callbacks[0]);
        task.addFinishRunnable(() -> callbacks[0]++);
        assertEquals(2, callbacks[0]);
    }
    @Test void dispatcherUploadCopiesDataBeforeFutureCompletes() throws Exception {
        var chunk = new VboChunkFactory().create(null, null, 0);
        var future = new ChunkRenderDispatcher().uploadChunk(BlockRenderLayer.SOLID, quad(), chunk, new CompiledChunk(), 0);
        assertTrue(future.isDone()); future.get();
        var capture = RenderContext.beginCapture();
        try { chunk.getVertexBufferByLayer(0).drawArrays(7); assertEquals(1, capture.size()); }
        finally { RenderContext.endCapture(); }
    }
}

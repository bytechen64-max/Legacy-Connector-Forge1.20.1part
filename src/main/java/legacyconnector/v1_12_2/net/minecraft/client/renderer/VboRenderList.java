package legacyconnector.v1_12_2.net.minecraft.client.renderer;
import legacyconnector.v1_12_2.net.minecraft.util.BlockRenderLayer;

public class VboRenderList extends ChunkRenderContainer {
    @Override public void renderChunkLayer(BlockRenderLayer layer) {
        if (!initialized) return;
        try {
            for (var chunk : renderChunks) {
                GlStateManager.pushMatrix();
                try {
                    preRenderChunk(chunk);
                    chunk.getVertexBufferByLayer(layer.ordinal()).drawArrays(7);
                } finally { GlStateManager.popMatrix(); }
            }
        } finally { renderChunks.clear(); }
    }
}

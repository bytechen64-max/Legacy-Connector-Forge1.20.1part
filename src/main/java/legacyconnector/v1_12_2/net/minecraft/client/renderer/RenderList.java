package legacyconnector.v1_12_2.net.minecraft.client.renderer;
import legacyconnector.v1_12_2.net.minecraft.client.renderer.chunk.ListedRenderChunk;
import legacyconnector.v1_12_2.net.minecraft.util.BlockRenderLayer;
import legacyconnector.v1_7_10.org.lwjgl.opengl.GL11;

public class RenderList extends ChunkRenderContainer {
    @Override public void renderChunkLayer(BlockRenderLayer layer) {
        if (!initialized) return;
        try {
            for (var chunk : renderChunks) {
                GlStateManager.pushMatrix();
                try {
                    preRenderChunk(chunk);
                    if (chunk instanceof ListedRenderChunk listed) {
                        int id = listed.getDisplayList(layer, chunk.getCompiledChunk());
                        if (id >= 0) GL11.glCallList(id);
                    } else chunk.getVertexBufferByLayer(layer.ordinal()).drawArrays(7);
                } finally { GlStateManager.popMatrix(); }
            }
        } finally { renderChunks.clear(); }
    }
}

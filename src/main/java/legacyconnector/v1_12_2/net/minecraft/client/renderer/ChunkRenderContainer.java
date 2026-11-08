package legacyconnector.v1_12_2.net.minecraft.client.renderer;

import java.util.ArrayList;
import java.util.List;
import legacyconnector.v1_12_2.net.minecraft.client.renderer.chunk.RenderChunk;
import legacyconnector.v1_12_2.net.minecraft.util.BlockRenderLayer;

public abstract class ChunkRenderContainer {
    protected final List<RenderChunk> renderChunks = new ArrayList<>();
    protected boolean initialized;
    private double viewEntityX, viewEntityY, viewEntityZ;
    public void initialize(double x, double y, double z) {
        initialized = true;
        renderChunks.clear();
        viewEntityX = x; viewEntityY = y; viewEntityZ = z;
    }
    public void addRenderChunk(RenderChunk chunk, BlockRenderLayer layer) { renderChunks.add(chunk); }
    public void preRenderChunk(RenderChunk chunk) {
        var pos = chunk.getPosition();
        GlStateManager.translate(pos.getX() - viewEntityX, pos.getY() - viewEntityY, pos.getZ() - viewEntityZ);
    }
    public abstract void renderChunkLayer(BlockRenderLayer layer);
}

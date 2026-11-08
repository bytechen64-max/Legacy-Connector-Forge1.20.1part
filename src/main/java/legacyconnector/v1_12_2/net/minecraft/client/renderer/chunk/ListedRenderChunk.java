package legacyconnector.v1_12_2.net.minecraft.client.renderer.chunk;
import legacyconnector.v1_12_2.net.minecraft.client.renderer.*;
import legacyconnector.v1_12_2.net.minecraft.util.BlockRenderLayer;
import legacyconnector.v1_12_2.net.minecraft.world.World;
import legacyconnector.v1_7_10.org.lwjgl.opengl.GL11;

public class ListedRenderChunk extends RenderChunk {
    private final int base = GL11.glGenLists(BlockRenderLayer.values().length);
    public ListedRenderChunk(World world, RenderGlobal renderGlobal, int index) { super(world, renderGlobal, index); }
    public int getDisplayList(BlockRenderLayer layer, CompiledChunk compiled) { return compiled.isLayerEmpty(layer) ? -1 : base + layer.ordinal(); }
    @Override public void upload(BlockRenderLayer layer, BufferBuilder data) {
        if (data.isDrawing) data.finishDrawing();
        GL11.glNewList(base + layer.ordinal(), GL11.GL_COMPILE);
        try { new WorldVertexBufferUploader().draw(data); } finally { GL11.glEndList(); }
    }
    @Override public void deleteGlResources() {
        super.deleteGlResources();
        GL11.glDeleteLists(base, BlockRenderLayer.values().length);
    }
}

package legacyconnector.v1_12_2.net.minecraft.client.renderer.chunk;
import legacyconnector.v1_12_2.net.minecraft.client.renderer.RenderGlobal;
import legacyconnector.v1_12_2.net.minecraft.world.World;
public class ListChunkFactory implements IRenderChunkFactory {
    public RenderChunk create(World world, RenderGlobal renderer, int index) { return new ListedRenderChunk(world, renderer, index); }
}

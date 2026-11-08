package legacyconnector.v1_12_2.net.minecraft.client.renderer.chunk;
import legacyconnector.v1_12_2.net.minecraft.client.renderer.RenderGlobal;
import legacyconnector.v1_12_2.net.minecraft.world.World;
public class VboChunkFactory implements IRenderChunkFactory {
    public RenderChunk create(World world, RenderGlobal renderer, int index) { return new RenderChunk(world, renderer, index); }
}

package legacyconnector.v1_12_2.net.minecraft.client.renderer;

import legacyconnector.v1_12_2.net.minecraft.util.BlockRenderLayer;

public class RegionRenderCacheBuilder {
    private final BufferBuilder[] builders = new BufferBuilder[BlockRenderLayer.values().length];
    public RegionRenderCacheBuilder() {
        for (int i = 0; i < builders.length; i++) builders[i] = new BufferBuilder(4096);
    }
    public BufferBuilder getWorldRendererByLayer(BlockRenderLayer layer) { return builders[layer.ordinal()]; }
    public BufferBuilder getWorldRendererByLayerId(int id) { return builders[id]; }
}

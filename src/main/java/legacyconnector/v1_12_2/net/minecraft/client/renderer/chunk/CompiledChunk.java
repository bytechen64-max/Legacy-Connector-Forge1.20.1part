package legacyconnector.v1_12_2.net.minecraft.client.renderer.chunk;
import java.util.ArrayList;
import java.util.List;
import legacyconnector.v1_12_2.net.minecraft.util.BlockRenderLayer;
import legacyconnector.v1_12_2.net.minecraft.tileentity.TileEntity;
import legacyconnector.v1_12_2.net.minecraft.client.renderer.BufferBuilder;

public class CompiledChunk {
    public static final CompiledChunk DUMMY = new CompiledChunk();
    private final boolean[] used = new boolean[BlockRenderLayer.values().length];
    private final boolean[] started = new boolean[used.length];
    private final List<TileEntity> tiles = new ArrayList<>();
    private BufferBuilder.State state;
    public boolean isEmpty() { for (boolean b : used) if (b) return false; return true; }
    protected void setLayerUsed(BlockRenderLayer layer) { used[layer.ordinal()] = true; }
    public boolean isLayerEmpty(BlockRenderLayer layer) { return !used[layer.ordinal()]; }
    public void setLayerStarted(BlockRenderLayer layer) { started[layer.ordinal()] = true; }
    public boolean isLayerStarted(BlockRenderLayer layer) { return started[layer.ordinal()]; }
    public List<TileEntity> getTileEntities() { return tiles; }
    public void addTileEntity(TileEntity tile) { tiles.add(tile); }
    public BufferBuilder.State getState() { return state; }
    public void setState(BufferBuilder.State state) { this.state = state; }
    public boolean isVisible(legacyconnector.v1_12_2.net.minecraft.util.EnumFacing from, legacyconnector.v1_12_2.net.minecraft.util.EnumFacing to) { return true; }
}

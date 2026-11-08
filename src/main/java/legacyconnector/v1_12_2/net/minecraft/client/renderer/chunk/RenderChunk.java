package legacyconnector.v1_12_2.net.minecraft.client.renderer.chunk;

import legacyconnector.v1_12_2.net.minecraft.client.renderer.*;
import legacyconnector.v1_12_2.net.minecraft.client.renderer.vertex.*;
import legacyconnector.v1_12_2.net.minecraft.util.BlockRenderLayer;
import legacyconnector.v1_12_2.net.minecraft.util.math.BlockPos;
import legacyconnector.v1_12_2.net.minecraft.world.World;

/** Legacy chunk-local meshes, drawn by the shared vertex decoder. Rebuilds run on the calling client thread. */
public class RenderChunk {
    protected World world;
    private BlockPos.MutableBlockPos position = new BlockPos.MutableBlockPos();
    private CompiledChunk compiledChunk = new CompiledChunk();
    private final VertexBuffer[] vertexBuffers = new VertexBuffer[BlockRenderLayer.values().length];
    private boolean needsUpdate = true, immediate;
    private int frameIndex = -1;
    public static int renderChunksUpdated;
    public legacyconnector.v1_12_2.net.minecraft.util.math.AxisAlignedBB boundingBox = new legacyconnector.v1_12_2.net.minecraft.util.math.AxisAlignedBB(0, 0, 0, 16, 16, 16);
    private ChunkCompileTaskGenerator compileTask;
    private final java.util.concurrent.locks.ReentrantLock lockCompileTask = new java.util.concurrent.locks.ReentrantLock();
    public RenderChunk(World world, RenderGlobal renderGlobal, int index) {
        this.world = world;
        for (int i = 0; i < vertexBuffers.length; i++) vertexBuffers[i] = new VertexBuffer(DefaultVertexFormats.BLOCK);
    }
    public VertexBuffer getVertexBufferByLayer(int layer) { return vertexBuffers[layer]; }
    public BlockPos getPosition() { return position; }
    public World getWorld() { return world; }
    public void setPosition(int x, int y, int z) {
        if (position.getX() == x && position.getY() == y && position.getZ() == z) return;
        position.setPos(x, y, z);
        stopCompileTask();
        boundingBox = new legacyconnector.v1_12_2.net.minecraft.util.math.AxisAlignedBB(x, y, z, x + 16, y + 16, z + 16);
        deleteGlResources(); setNeedsUpdate(false);
    }
    public CompiledChunk getCompiledChunk() { return compiledChunk; }
    public void setCompiledChunk(CompiledChunk chunk) { compiledChunk = chunk; }
    public boolean setFrameIndex(int index) { if (frameIndex == index) return false; frameIndex = index; return true; }
    public void setNeedsUpdate(boolean immediate) { needsUpdate = true; this.immediate |= immediate; }
    public void clearNeedsUpdate() { needsUpdate = immediate = false; }
    public boolean needsUpdate() { return needsUpdate; }
    public boolean needsImmediateUpdate() { return immediate; }
    public java.util.concurrent.locks.ReentrantLock getLockCompileTask() { return lockCompileTask; }
    public BlockPos getBlockPosOffset16(legacyconnector.v1_12_2.net.minecraft.util.EnumFacing facing) { return position.offset(facing, 16); }
    public void multModelviewMatrix() {}
    public void stopCompileTask() { if (compileTask != null) { compileTask.finish(); compileTask = null; } }
    public ChunkCompileTaskGenerator makeCompileTaskChunk() {
        stopCompileTask();
        return compileTask = new ChunkCompileTaskGenerator(this, ChunkCompileTaskGenerator.Type.REBUILD_CHUNK, 0);
    }
    public ChunkCompileTaskGenerator makeCompileTaskTransparency() {
        stopCompileTask();
        compileTask = new ChunkCompileTaskGenerator(this, ChunkCompileTaskGenerator.Type.RESORT_TRANSPARENCY, 0);
        compileTask.setCompiledChunk(compiledChunk);
        return compileTask;
    }
    public void rebuildChunk(float x, float y, float z, ChunkCompileTaskGenerator task) {
        rebuildAt(x, y, z);
        task.setCompiledChunk(compiledChunk);
    }
    public void resortTransparency(float x, float y, float z, ChunkCompileTaskGenerator task) {
        var compiled = task.getCompiledChunk();
        if (compiled == null || compiled.getState() == null) return;
        var data = new BufferBuilder(4096);
        data.begin(7, DefaultVertexFormats.BLOCK);
        data.setVertexState(compiled.getState());
        data.setTranslation(-position.getX(), -position.getY(), -position.getZ());
        data.sortVertexData(x, y, z);
        compiled.setState(data.getVertexState());
        upload(BlockRenderLayer.TRANSLUCENT, data);
    }
    public void deleteGlResources() { stopCompileTask(); for (var buffer : vertexBuffers) buffer.deleteGlBuffers(); compiledChunk = new CompiledChunk(); }
    public void upload(BlockRenderLayer layer, BufferBuilder data) {
        if (data.isDrawing) data.finishDrawing();
        vertexBuffers[layer.ordinal()].bufferData(data.getByteBuffer());
    }
    public void rebuildNow() {
        if (world == null) return;
        var view = net.minecraft.client.Minecraft.getInstance().getCameraEntity();
        rebuildAt(view == null ? 0 : (float) view.getX(), view == null ? 0 : (float) view.getY(), view == null ? 0 : (float) view.getZ());
    }
    private void rebuildAt(float cameraX, float cameraY, float cameraZ) {
        if (world == null) return;
        var next = new CompiledChunk();
        for (var layer : BlockRenderLayer.values()) {
            var data = new BufferBuilder(4096);
            data.begin(7, DefaultVertexFormats.BLOCK);
            data.setTranslation(-position.getX(), -position.getY(), -position.getZ());
            var previousLayer = legacyconnector.v1_12_2.net.minecraftforge.client.MinecraftForgeClient.getRenderLayer();
            legacyconnector.v1_12_2.net.minecraftforge.client.ForgeHooksClient.setRenderLayer(layer);
            try {
                for (int y = 0; y < 16; y++) for (int z = 0; z < 16; z++) for (int x = 0; x < 16; x++) {
                    var pos = new BlockPos(position.getX() + x, position.getY() + y, position.getZ() + z);
                    var state = world.getBlockState(pos);
                    if (state == null || state.getBlock().isAir(state, world, pos) || !state.getBlock().canRenderInLayer(state, layer)) continue;
                    state = state.getActualState(world, pos);
                    state = state.getBlock().getExtendedState(state, world, pos);
                    if (BlockRendererDispatcher.mcc$instance().renderBlock(state, pos, world, data)) next.setLayerUsed(layer);
                }
            } finally { legacyconnector.v1_12_2.net.minecraftforge.client.ForgeHooksClient.setRenderLayer(previousLayer); }
            if (layer == BlockRenderLayer.TRANSLUCENT && data.getVertexCount() > 0) {
                data.sortVertexData(cameraX, cameraY, cameraZ);
                next.setState(data.getVertexState());
            }
            next.setLayerStarted(layer);
            upload(layer, data);
        }
        compiledChunk = next;
        renderChunksUpdated++;
        clearNeedsUpdate();
    }
}

package legacyconnector.v1_12_2.net.minecraft.client.renderer.chunk;

import java.util.ArrayList;
import java.util.concurrent.locks.ReentrantLock;
import legacyconnector.v1_12_2.net.minecraft.client.renderer.RegionRenderCacheBuilder;

public class ChunkCompileTaskGenerator implements Comparable<ChunkCompileTaskGenerator> {
    public enum Type { REBUILD_CHUNK, RESORT_TRANSPARENCY }
    public enum Status { PENDING, COMPILING, UPLOADING, DONE }
    private final RenderChunk chunk;
    private final Type type;
    private final double distance;
    private final ReentrantLock lock = new ReentrantLock();
    private final ArrayList<Runnable> finishers = new ArrayList<>();
    private Status status = Status.PENDING;
    private boolean finished;
    private CompiledChunk compiled;
    private RegionRenderCacheBuilder builder;
    public ChunkCompileTaskGenerator(RenderChunk chunk, Type type, double distance) {
        this.chunk = chunk; this.type = type; this.distance = distance;
    }
    public Status getStatus() { return status; }
    public void setStatus(Status status) { this.status = status; }
    public RenderChunk getRenderChunk() { return chunk; }
    public Type getType() { return type; }
    public CompiledChunk getCompiledChunk() { return compiled; }
    public void setCompiledChunk(CompiledChunk compiled) { this.compiled = compiled; }
    public RegionRenderCacheBuilder getRegionRenderCacheBuilder() { return builder; }
    public void setRegionRenderCacheBuilder(RegionRenderCacheBuilder builder) { this.builder = builder; }
    public ReentrantLock getLock() { return lock; }
    public boolean isFinished() { return finished; }
    public double getDistanceSq() { return distance; }
    public int compareTo(ChunkCompileTaskGenerator other) { return Double.compare(distance, other.distance); }
    public void finish() {
        lock.lock();
        try {
            if (finished) return;
            if (type == Type.REBUILD_CHUNK && status != Status.DONE) chunk.setNeedsUpdate(false);
            finished = true; status = Status.DONE;
            var actions = new ArrayList<>(finishers);
            finishers.clear();
            for (var action : actions) action.run();
        } finally { lock.unlock(); }
    }
    public void addFinishRunnable(Runnable action) {
        lock.lock();
        try { if (finished) action.run(); else finishers.add(action); }
        finally { lock.unlock(); }
    }
}

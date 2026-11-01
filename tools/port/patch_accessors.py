"""Protected members via accessor mixins (ForgeGradle does not apply the mod's AT to the compile classpath)."""
import json
import sys

ENTITY = "org.kylepitcock.legacyconnector.mixin.access.EntityAccess"
CHUNKMAP = "org.kylepitcock.legacyconnector.mixin.access.ChunkMapAccess"

# ------------------------------------------------------------------ Entity portal state
P = r"src/main/java/legacyconnector/v1_12_2/net/minecraft/entity/Entity.java"
src = open(P, encoding="utf-8").read()
pairs = [
    ("""    public static boolean mcc$get$inPortal(Entity e) {
        var m = e.mcc$entity;
        if (m == null) return e.mcc$local_inPortal;
        return m.isInsidePortal;
    }""",
     """    public static boolean mcc$get$inPortal(Entity e) {
        var m = e.mcc$entity;
        if (m == null) return e.mcc$local_inPortal;
        return ((org.kylepitcock.legacyconnector.mixin.access.EntityAccess) m).legacyconnector$insidePortal();
    }"""),
    ("""    public static void mcc$set$inPortal(Entity e, boolean v) {
        var m = e.mcc$entity;
        if (m != null) m.isInsidePortal = v;
        else e.mcc$local_inPortal = v;
    }""",
     """    public static void mcc$set$inPortal(Entity e, boolean v) {
        var m = e.mcc$entity;
        if (m != null) ((org.kylepitcock.legacyconnector.mixin.access.EntityAccess) m).legacyconnector$setInsidePortal(v);
        else e.mcc$local_inPortal = v;
    }"""),
    ("""    public static int mcc$get$portalCounter(Entity e) {
        var m = e.mcc$entity;
        if (m == null) return e.mcc$local_portalCounter;
        return m.portalTime;
    }""",
     """    public static int mcc$get$portalCounter(Entity e) {
        var m = e.mcc$entity;
        if (m == null) return e.mcc$local_portalCounter;
        return ((org.kylepitcock.legacyconnector.mixin.access.EntityAccess) m).legacyconnector$portalTime();
    }"""),
    ("""    public static void mcc$set$portalCounter(Entity e, int v) {
        var m = e.mcc$entity;
        if (m != null) m.portalTime = v;
        else e.mcc$local_portalCounter = v;
    }""",
     """    public static void mcc$set$portalCounter(Entity e, int v) {
        var m = e.mcc$entity;
        if (m != null) ((org.kylepitcock.legacyconnector.mixin.access.EntityAccess) m).legacyconnector$setPortalTime(v);
        else e.mcc$local_portalCounter = v;
    }"""),
    ("""    public static legacyconnector.v1_12_2.net.minecraft.util.math.BlockPos mcc$get$lastPortalPos(Entity e) {
        var m = e.mcc$entity;
        if (m == null || m.portalEntrancePos == null) return e.mcc$local_lastPortalPos;
        return legacyconnector.v1_12_2.net.minecraft.util.math.BlockPos.mcc$of(m.portalEntrancePos);
    }""",
     """    public static legacyconnector.v1_12_2.net.minecraft.util.math.BlockPos mcc$get$lastPortalPos(Entity e) {
        var m = e.mcc$entity;
        if (m == null) return e.mcc$local_lastPortalPos;
        var entrance = ((org.kylepitcock.legacyconnector.mixin.access.EntityAccess) m).legacyconnector$portalEntrancePos();
        if (entrance == null) return e.mcc$local_lastPortalPos;
        return legacyconnector.v1_12_2.net.minecraft.util.math.BlockPos.mcc$of(entrance);
    }"""),
    ("""    public static void mcc$set$lastPortalPos(Entity e, legacyconnector.v1_12_2.net.minecraft.util.math.BlockPos v) {
        var m = e.mcc$entity;
        if (m != null) m.portalEntrancePos = v == null ? null : v.mcc$modern();
        else e.mcc$local_lastPortalPos = v;
    }""",
     """    public static void mcc$set$lastPortalPos(Entity e, legacyconnector.v1_12_2.net.minecraft.util.math.BlockPos v) {
        var m = e.mcc$entity;
        if (m != null) ((org.kylepitcock.legacyconnector.mixin.access.EntityAccess) m)
                .legacyconnector$setPortalEntrancePos(v == null ? null : v.mcc$modern());
        else e.mcc$local_lastPortalPos = v;
    }"""),
]
for old, new in pairs:
    if src.count(old) != 1:
        print("ABORT Entity:", src.count(old), old.splitlines()[0][:60])
        sys.exit(1)
    src = src.replace(old, new)
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P)

# ------------------------------------------------------------------ ChunkMap lookups + ChunkStatus
P = r"src/main/java/legacyconnector/v1_12_2/net/minecraft/world/World.java"
src = open(P, encoding="utf-8").read()
pairs = [
    ("        for (var holder : w.serverLevel().getChunkSource().chunkMap.getChunks()) {",
     "        for (var holder : ((org.kylepitcock.legacyconnector.mixin.access.ChunkMapAccess) w.serverLevel().getChunkSource().chunkMap)\n"
     "                .legacyconnector$chunks()) {"),
    ("        var holder = sl.getChunkSource().chunkMap.getVisibleChunkIfPresent(net.minecraft.world.level.ChunkPos.asLong(p.getX() >> 4, p.getZ() >> 4));\n"
     "        var chunk = holder == null ? null : holder.getChunkIfPresent(net.minecraft.world.level.chunk.status.ChunkStatus.FULL);",
     "        var holder = ((org.kylepitcock.legacyconnector.mixin.access.ChunkMapAccess) sl.getChunkSource().chunkMap)\n"
     "                .legacyconnector$visibleChunk(net.minecraft.world.level.ChunkPos.asLong(p.getX() >> 4, p.getZ() >> 4));\n"
     "        var chunk = holder == null ? null : holder.getChunkIfPresent(net.minecraft.world.level.chunk.ChunkStatus.FULL);"),
    ("            var holder = sl.getChunkSource().chunkMap.getVisibleChunkIfPresent(net.minecraft.world.level.ChunkPos.asLong(p.getX() >> 4, p.getZ() >> 4));",
     "            var holder = ((org.kylepitcock.legacyconnector.mixin.access.ChunkMapAccess) sl.getChunkSource().chunkMap)\n"
     "                    .legacyconnector$visibleChunk(net.minecraft.world.level.ChunkPos.asLong(p.getX() >> 4, p.getZ() >> 4));"),
]
for old, new in pairs:
    if src.count(old) != 1:
        print("ABORT World:", src.count(old), old.splitlines()[0][:60])
        sys.exit(1)
    src = src.replace(old, new)
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P)

# ------------------------------------------------------------------ register the accessor mixins
P = r"src/main/resources/legacyconnector.mixins.json"
cfg = json.load(open(P, encoding="utf-8"))
for name in ("access.EntityAccess", "access.ChunkMapAccess"):
    if name not in cfg["mixins"]:
        cfg["mixins"].insert(0, name)
open(P, "w", encoding="utf-8", newline="\n").write(json.dumps(cfg, indent=2) + "\n")
print("registered the accessor mixins:", cfg["mixins"][:3])

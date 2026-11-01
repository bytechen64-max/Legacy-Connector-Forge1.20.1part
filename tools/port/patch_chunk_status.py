"""1.20.1: ChunkStatus lives in world.level.chunk (no .status package), and LevelAccessor already is a SignalGetter."""
import os
import sys

# ------------------------------------------------------------------ package rename
changed = 0
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        src = open(p, encoding="utf-8").read()
        if "chunk.status." not in src:
            continue
        src = src.replace("net.minecraft.world.level.chunk.status.ChunkStatus", "net.minecraft.world.level.chunk.ChunkStatus")
        src = src.replace("import net.minecraft.world.level.chunk.status.ChunkHolder;", "import net.minecraft.server.level.ChunkHolder;")
        open(p, "w", encoding="utf-8", newline="").write(src)
        changed += 1
print("chunk.status -> world.level.chunk in", changed, "files")

# ------------------------------------------------------------------ 1.20.5 chunk status accessor
P = r"src/main/java/legacyconnector/v1_12_2/net/minecraft/world/chunk/Chunk.java"
src = open(P, encoding="utf-8").read()
if "getPersistedStatus()" in src:
    src = src.replace("access.getPersistedStatus()", "access.getStatus()")
    open(P, "w", encoding="utf-8", newline="").write(src)
    print("Chunk: getPersistedStatus -> getStatus")

# ------------------------------------------------------------------ SignalGetter
P = r"src/main/java/legacyconnector/v1_12_2/net/minecraft/world/World.java"
src = open(P, encoding="utf-8").read()
pairs = [
    ("        return acc() instanceof SignalGetter s ? s.getDirectSignalTo(modern(pos)) : 0;",
     "        // 1.20.1's LevelAccessor is a SignalGetter, so the instanceof this shim needed on 1.21 is redundant here.\n"
     "        var level = acc();\n"
     "        return level == null ? 0 : level.getDirectSignalTo(modern(pos));"),
    ("        return acc() instanceof SignalGetter s && s.hasNeighborSignal(modern(pos));",
     "        var level = acc();\n"
     "        return level != null && level.hasNeighborSignal(modern(pos));"),
    ("        return acc() instanceof SignalGetter s ? s.getBestNeighborSignal(modern(pos)) : 0;",
     "        var level = acc();\n"
     "        return level == null ? 0 : level.getBestNeighborSignal(modern(pos));"),
    ("        return acc() instanceof SignalGetter s ? s.getSignal(modern(pos), facing.mcc$modern()) : 0;",
     "        var level = acc();\n"
     "        return level == null ? 0 : level.getSignal(modern(pos), facing.mcc$modern());"),
]
for old, new in pairs:
    if src.count(old) != 1:
        print("ABORT World SignalGetter:", src.count(old), old.strip()[:60])
        sys.exit(1)
    src = src.replace(old, new)
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched World SignalGetter sites")

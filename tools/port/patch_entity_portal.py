"""Entity portal state: 1.20.5's PortalProcessor does not exist in 1.20.1, which keeps three protected fields instead."""
import sys

P = r"src/main/java/legacyconnector/v1_12_2/net/minecraft/entity/Entity.java"
OLD = '''    /** inPortal / portalCounter / lastPortalPos: the modern portal process (entered this tick, ticks inside, entry block). */
    public static boolean mcc$get$inPortal(Entity e) {
        var m = e.mcc$entity;
        if (m == null) return e.mcc$local_inPortal;
        return m.portalProcess != null && m.portalProcess.isInsidePortalThisTick();
    }

    public static void mcc$set$inPortal(Entity e, boolean v) {
        var m = e.mcc$entity;
        if (m != null && m.portalProcess != null) m.portalProcess.setAsInsidePortalThisTick(v);
        else e.mcc$local_inPortal = v;
    }

    public static int mcc$get$portalCounter(Entity e) {
        var m = e.mcc$entity;
        if (m == null) return e.mcc$local_portalCounter;
        return m.portalProcess != null ? m.portalProcess.getPortalTime() : 0;
    }

    public static void mcc$set$portalCounter(Entity e, int v) {
        if (e.mcc$entity == null) e.mcc$local_portalCounter = v;
    }

    public static legacyconnector.v1_12_2.net.minecraft.util.math.BlockPos mcc$get$lastPortalPos(Entity e) {
        var m = e.mcc$entity;
        if (m == null || m.portalProcess == null) return e.mcc$local_lastPortalPos;
        return legacyconnector.v1_12_2.net.minecraft.util.math.BlockPos.mcc$of(m.portalProcess.getEntryPosition());
    }

    public static void mcc$set$lastPortalPos(Entity e, legacyconnector.v1_12_2.net.minecraft.util.math.BlockPos v) {
        var m = e.mcc$entity;
        if (m != null && m.portalProcess != null && v != null) m.portalProcess.updateEntryPosition(v.mcc$modern());
        else e.mcc$local_lastPortalPos = v;
    }
'''

NEW = '''    /** inPortal / portalCounter / lastPortalPos: the 1.20.1 entity fields (in a portal this tick, ticks inside, entry block). */
    public static boolean mcc$get$inPortal(Entity e) {
        var m = e.mcc$entity;
        if (m == null) return e.mcc$local_inPortal;
        return m.isInsidePortal;
    }

    public static void mcc$set$inPortal(Entity e, boolean v) {
        var m = e.mcc$entity;
        if (m != null) m.isInsidePortal = v;
        else e.mcc$local_inPortal = v;
    }

    public static int mcc$get$portalCounter(Entity e) {
        var m = e.mcc$entity;
        if (m == null) return e.mcc$local_portalCounter;
        return m.portalTime;
    }

    public static void mcc$set$portalCounter(Entity e, int v) {
        var m = e.mcc$entity;
        if (m != null) m.portalTime = v;
        else e.mcc$local_portalCounter = v;
    }

    public static legacyconnector.v1_12_2.net.minecraft.util.math.BlockPos mcc$get$lastPortalPos(Entity e) {
        var m = e.mcc$entity;
        if (m == null || m.portalEntrancePos == null) return e.mcc$local_lastPortalPos;
        return legacyconnector.v1_12_2.net.minecraft.util.math.BlockPos.mcc$of(m.portalEntrancePos);
    }

    public static void mcc$set$lastPortalPos(Entity e, legacyconnector.v1_12_2.net.minecraft.util.math.BlockPos v) {
        var m = e.mcc$entity;
        if (m != null) m.portalEntrancePos = v == null ? null : v.mcc$modern();
        else e.mcc$local_lastPortalPos = v;
    }
'''

src = open(P, encoding="utf-8").read()
if src.count(OLD) != 1:
    print("ABORT: accessor block not found once:", src.count(OLD))
    sys.exit(1)
open(P, "w", encoding="utf-8", newline="").write(src.replace(OLD, NEW))
print("patched", P)

AT = "src/main/resources/META-INF/accesstransformer.cfg"
at = open(AT, encoding="utf-8").read()
MARK = "# Legacy entity portal state"
if MARK not in at:
    at = at.rstrip("\n") + (
        "\n\n# Legacy entity portal state (Entity.inPortal / portalCounter / lastPortalPos): 1.20.1 keeps it in protected fields.\n"
        "public net.minecraft.world.entity.Entity isInsidePortal\n"
        "public net.minecraft.world.entity.Entity portalTime\n"
        "public net.minecraft.world.entity.Entity portalEntrancePos\n")
    open(AT, "w", encoding="utf-8", newline="").write(at)
    print("patched", AT)
else:
    print("AT already has the portal entries")

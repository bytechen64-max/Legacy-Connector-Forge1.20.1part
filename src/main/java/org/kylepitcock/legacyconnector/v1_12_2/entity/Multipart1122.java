package org.kylepitcock.legacyconnector.v1_12_2.entity;

import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.IdentityHashMap;
import legacyconnector.v1_12_2.net.minecraft.entity.Entity;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraftforge.entity.PartEntity;

/** Legacy-owned hit boxes participate in Forge's level queries without becoming independently ticking entities. */
public final class Multipart1122 {
    private static final java.util.Set<String> REPORTED = java.util.concurrent.ConcurrentHashMap.newKeySet();
    private final Host1122 host;
    private Part[] parts;

    public Multipart1122(Host1122 host) { this.host = host; }

    public Part[] parts() {
        if (parts != null) return parts;
        Entity owner = host.mcc$legacy();
        if (owner == null) return new Part[0];
        parts = discover(owner).stream().map(child -> new Part(host.mcc$self(), child)).toArray(Part[]::new);
        sync();
        String side = host.mcc$self().level().isClientSide ? "client" : "server";
        if ((parts.length > 0 || owner.getClass().getName().contains("Venkrol")) && REPORTED.add(side + owner.getClass().getName())) {
            org.slf4j.LoggerFactory.getLogger("LegacyConnector/Multipart").info("{}: discovered {} body parts for {}", side, parts.length, owner.getClass().getName());
        }
        return parts;
    }

    static java.util.List<Entity> discover(Entity owner) {
        var children = new ArrayList<Entity>();
        var seen = new IdentityHashMap<Entity, Boolean>();
        Entity[] declared = owner.getParts();
        if (declared != null) for (Entity child : declared) add(owner, child, children, seen);
        // SRP keeps EntityBody/EntityBodyModel in private fields rather than overriding getParts().
        for (Class<?> cls = owner.getClass(); cls != Entity.class && cls != null; cls = cls.getSuperclass()) {
            var fields = cls.getDeclaredFields();
            Arrays.sort(fields, Comparator.comparing(java.lang.reflect.Field::getName));
            for (var field : fields) {
                if (Modifier.isStatic(field.getModifiers())) continue;
                Class<?> type = field.getType();
                boolean array = type.isArray();
                if (!isSrpBody(array ? type.getComponentType() : type)) continue;
                try {
                    field.setAccessible(true);
                    Object value = field.get(owner);
                    if (array && value instanceof Entity[] entities) {
                        for (Entity child : entities) add(owner, child, children, seen);
                    } else if (value instanceof Entity child) add(owner, child, children, seen);
                } catch (ReflectiveOperationException e) {
                    throw new IllegalStateException("Cannot access legacy body part " + field, e);
                }
            }
        }
        return children;
    }

    private static boolean isSrpBody(Class<?> type) {
        for (Class<?> cls = type; cls != null; cls = cls.getSuperclass()) {
            if (cls.getName().equals("com.dhanantry.scapeandrunparasites.entity.EntityBody")) return true;
        }
        return false;
    }

    private static void add(Entity owner, Entity child, ArrayList<Entity> children, IdentityHashMap<Entity, Boolean> seen) {
        if (child != null && child != owner && seen.put(child, Boolean.TRUE) == null) children.add(child);
    }

    public void sync() {
        for (Part part : parts()) part.sync();
    }

    /** Use server-assigned unique entity IDs; client constructor allocation order need not match the server. */
    public void writeIds(FriendlyByteBuf buf) {
        buf.writeVarInt(parts().length);
        for (Part part : parts()) buf.writeVarInt(part.getId());
    }

    public void readIds(FriendlyByteBuf buf) {
        int count = buf.readVarInt();
        if (count != parts().length) throw new IllegalStateException("Legacy multipart spawn mismatch: " + count + " / " + parts().length);
        for (Part part : parts()) part.setId(buf.readVarInt());
        if (host.mcc$self().level().isClientSide) {
            org.kylepitcock.legacyconnector.v1_12_2.bridge.WorldClient1122.refreshParts(host.mcc$self(), parts());
        }
    }

    public static final class Part extends PartEntity<net.minecraft.world.entity.Entity> {
        public final Entity legacy;
        private boolean positioned;

        Part(net.minecraft.world.entity.Entity parent, Entity legacy) {
            super(parent);
            this.legacy = legacy;
        }

        void sync() {
            // These parts never pass through Level.tickNonPassenger, which normally sets xOld/yOld/zOld.
            // EntityRenderDispatcher uses those fields (not xo/yo/zo) to draw multipart hit boxes.
            double previousX = positioned ? getX() : legacy.mcc$x();
            double previousY = positioned ? getY() : legacy.mcc$y();
            double previousZ = positioned ? getZ() : legacy.mcc$z();
            xOld = xo = previousX;
            yOld = yo = previousY;
            zOld = zo = previousZ;
            setPos(legacy.mcc$x(), legacy.mcc$y(), legacy.mcc$z());
            setBoundingBox(legacy.getEntityBoundingBox().mcc$modern());
            positioned = true;
        }

        @Override protected void defineSynchedData() {}
        @Override protected void readAdditionalSaveData(CompoundTag tag) {}
        @Override protected void addAdditionalSaveData(CompoundTag tag) {}
        @Override public boolean shouldBeSaved() { return false; }
        @Override public boolean isPickable() { return !getParent().isRemoved() && legacy.isEntityAlive() && legacy.canBeCollidedWith(); }
        @Override public boolean is(net.minecraft.world.entity.Entity entity) { return this == entity || getParent() == entity; }
        @Override public boolean hurt(DamageSource source, float amount) {
            // The normal Forge interaction packet now reaches this part on the server.
            // SRP's client-only fallback hit packet would apply the same attack twice.
            return !level().isClientSide && isPickable() && legacy.attackEntityFrom(legacyconnector.v1_12_2.net.minecraft.util.DamageSource.mcc$of(source), amount);
        }
    }
}

package org.kylepitcock.legacyconnector.v1_12_2.entity;

import legacyconnector.v1_12_2.net.minecraft.entity.Entity;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class Multipart1122Test {
    @Test void partSyncUpdatesThePositionHistoryReadByForgeHitboxRendering() throws Exception {
        // Inspect the actual game's consumer without starting a client or initializing Entity registries.
        var renderer = bytecode("net/minecraft/client/renderer/entity/EntityRenderDispatcher.class");
        var render = renderer.methods.stream().filter(m -> m.name.equals("renderHitbox")).findFirst().orElseThrow();
        var history = new java.util.HashSet<String>();
        for (var instruction : render.instructions) {
            if (instruction instanceof org.objectweb.asm.tree.FieldInsnNode field && field.getOpcode() == org.objectweb.asm.Opcodes.GETFIELD
                    && java.util.Set.of("xOld", "yOld", "zOld").contains(field.name)) history.add(field.name);
        }
        assertEquals(java.util.Set.of("xOld", "yOld", "zOld"), history);
        var part = bytecode("org/kylepitcock/legacyconnector/v1_12_2/entity/Multipart1122$Part.class");
        var sync = part.methods.stream().filter(m -> m.name.equals("sync")).findFirst().orElseThrow();
        for (var instruction : sync.instructions) {
            if (instruction instanceof org.objectweb.asm.tree.FieldInsnNode field && field.getOpcode() == org.objectweb.asm.Opcodes.PUTFIELD)
                history.remove(field.name);
        }
        assertTrue(history.isEmpty(), "Multipart debug rendering reads position fields never updated by sync: " + history);
    }

    private static org.objectweb.asm.tree.ClassNode bytecode(String path) throws Exception {
        try (var stream = Multipart1122Test.class.getClassLoader().getResourceAsStream(path)) {
            assertNotNull(stream, path);
            var node = new org.objectweb.asm.tree.ClassNode();
            new org.objectweb.asm.ClassReader(stream).accept(node, 0);
            return node;
        }
    }
    static class Owner extends Entity {
        Entity[] children;
        Owner() { super((legacyconnector.v1_12_2.net.minecraft.world.World) null); }
        @Override public Entity[] getParts() { return children; }
    }
    static class SrpOwner extends Owner {
        private com.dhanantry.scapeandrunparasites.entity.EntityBody head;
        private com.dhanantry.scapeandrunparasites.entity.EntityBody[] sides;
    }
    @Test void discoversEachChildOnceInDeclaredOrderAndExcludesParent() throws Exception {
        var access = sun.misc.Unsafe.class.getDeclaredField("theUnsafe");
        access.setAccessible(true);
        var unsafe = (sun.misc.Unsafe) access.get(null);
        var owner = (Owner) unsafe.allocateInstance(Owner.class);
        var first = (Entity) unsafe.allocateInstance(Owner.class);
        var second = (Entity) unsafe.allocateInstance(Owner.class);
        owner.children = new Entity[] {first, null, owner, second, first};
        var children = Multipart1122.discover(owner);
        assertEquals(2, children.size());
        assertSame(first, children.get(0));
        assertSame(second, children.get(1));
    }
    @Test void ordinaryEntityHasNoParts() throws Exception {
        var owner = new Owner();
        assertTrue(Multipart1122.discover(owner).isEmpty());
    }
    @Test void discoversSrpPrivateBodyFieldsAndArraysWithoutGetPartsOverride() {
        var owner = new SrpOwner();
        owner.head = new com.dhanantry.scapeandrunparasites.entity.EntityBody();
        var side = new com.dhanantry.scapeandrunparasites.entity.EntityBody();
        owner.sides = new com.dhanantry.scapeandrunparasites.entity.EntityBody[] {side, owner.head};
        var children = Multipart1122.discover(owner);
        assertEquals(2, children.size());
        assertSame(owner.head, children.get(0));
        assertSame(side, children.get(1));
    }
}

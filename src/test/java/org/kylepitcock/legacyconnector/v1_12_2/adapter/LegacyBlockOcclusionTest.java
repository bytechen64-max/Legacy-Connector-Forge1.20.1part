package org.kylepitcock.legacyconnector.v1_12_2.adapter;

import java.util.Map;
import org.junit.jupiter.api.Test;
import org.objectweb.asm.*;
import org.objectweb.asm.commons.*;
import org.objectweb.asm.tree.ClassNode;
import static org.junit.jupiter.api.Assertions.*;

public class LegacyBlockOcclusionTest {
    public record Shape(boolean empty) {}
    public static class Shapes {
        public static Shape empty() { return new Shape(true); }
    }
    public record State(boolean opaque) {}
    public static class Getter {}
    public static class Pos {}
    public static class Legacy {
        public boolean isOpaqueCube(State state) { return state.opaque(); }
    }
    public static class Adapter {
        public Legacy legacy = new Legacy();
        public final Shape selection = new Shape(false);
        public static State state(State state) { return state; }
        public void failure(String hook, Throwable error) { throw new AssertionError(hook, error); }
        public Shape getOcclusionShape(State state, Getter getter, Pos pos) { return selection; }
    }

    /** Run the production override with registry-free boundaries, without a Forge launch. */
    private static Adapter adapter() throws Exception {
        var node = new ClassNode();
        try (var stream = LegacyBlockOcclusionTest.class.getClassLoader().getResourceAsStream(
                "org/kylepitcock/legacyconnector/v1_12_2/adapter/Legacy1122Block.class")) {
            assertNotNull(stream);
            new ClassReader(stream).accept(node, ClassReader.SKIP_DEBUG | ClassReader.SKIP_FRAMES);
        }
        var method = node.methods.stream().filter(m -> m.name.equals("getOcclusionShape")).findFirst().orElseThrow();
        var remapper = new SimpleRemapper(Map.ofEntries(
                Map.entry(node.name, Type.getInternalName(Adapter.class)),
                Map.entry("net/minecraft/world/level/block/Block", Type.getInternalName(Adapter.class)),
                Map.entry("legacyconnector/v1_12_2/net/minecraft/block/Block", Type.getInternalName(Legacy.class)),
                Map.entry("legacyconnector/v1_12_2/net/minecraft/block/state/IBlockState", Type.getInternalName(State.class)),
                Map.entry("net/minecraft/world/level/block/state/BlockState", Type.getInternalName(State.class)),
                Map.entry("net/minecraft/world/level/BlockGetter", Type.getInternalName(Getter.class)),
                Map.entry("net/minecraft/core/BlockPos", Type.getInternalName(Pos.class)),
                Map.entry("net/minecraft/world/phys/shapes/VoxelShape", Type.getInternalName(Shape.class)),
                Map.entry("net/minecraft/world/phys/shapes/Shapes", Type.getInternalName(Shapes.class))));
        var writer = new ClassWriter(ClassWriter.COMPUTE_FRAMES | ClassWriter.COMPUTE_MAXS);
        writer.visit(Opcodes.V17, Opcodes.ACC_PUBLIC, "test/Occlusion", null, Type.getInternalName(Adapter.class), null);
        var ctor = writer.visitMethod(Opcodes.ACC_PUBLIC, "<init>", "()V", null, null);
        ctor.visitCode();
        ctor.visitVarInsn(Opcodes.ALOAD, 0);
        ctor.visitMethodInsn(Opcodes.INVOKESPECIAL, Type.getInternalName(Adapter.class), "<init>", "()V", false);
        ctor.visitInsn(Opcodes.RETURN);
        ctor.visitMaxs(0, 0);
        ctor.visitEnd();
        method.accept(new MethodRemapper(writer.visitMethod(Opcodes.ACC_PUBLIC, method.name,
                remapper.mapMethodDesc(method.desc), null, null), remapper));
        writer.visitEnd();
        var bytes = writer.toByteArray();
        class Loader extends ClassLoader {
            Loader() { super(LegacyBlockOcclusionTest.class.getClassLoader()); }
            Class<?> define() { return defineClass("test.Occlusion", bytes, 0, bytes.length); }
        }
        return (Adapter) new Loader().define().getConstructor().newInstance();
    }

    @Test void transparentBlockDoesNotHideGroundDespiteFullSelectionBox() throws Exception {
        var block = adapter();
        assertFalse(block.selection.empty());
        assertTrue(block.getOcclusionShape(new State(false), null, null).empty());
    }
    @Test void opaqueCubeStillHidesCoveredFaces() throws Exception {
        var block = adapter();
        assertSame(block.selection, block.getOcclusionShape(new State(true), null, null));
    }
    @Test void opacityIsReadForEachStateRatherThanOnlyTheDefault() throws Exception {
        var block = adapter();
        assertFalse(block.getOcclusionShape(new State(true), null, null).empty());
        assertTrue(block.getOcclusionShape(new State(false), null, null).empty());
        assertFalse(block.getOcclusionShape(new State(true), null, null).empty());
    }
}

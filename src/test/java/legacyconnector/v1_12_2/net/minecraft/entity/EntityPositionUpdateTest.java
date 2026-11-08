package legacyconnector.v1_12_2.net.minecraft.entity;

import java.util.Map;
import org.junit.jupiter.api.Test;
import org.objectweb.asm.*;
import org.objectweb.asm.commons.*;
import org.objectweb.asm.tree.ClassNode;
import static org.junit.jupiter.api.Assertions.*;

public class EntityPositionUpdateTest {
    public static class Side { public boolean isClientSide; }
    public static class Modern {
        public final Side side = new Side();
        public int teleports;
        public Side level() { return side; }
        public void teleportTo(double x, double y, double z) { teleports++; }
    }
    public static class Position {
        public Modern mcc$entity;
        public double x, y, z;
        public int moves;
        public void setPosition(double x, double y, double z) {
            this.x = x; this.y = y; this.z = z; moves++;
        }
    }

    // Execute the production method with lightweight boundary doubles. Loading real
    // Level/Entity requires Forge's launch-time event transformers, absent in JUnit.
    private static Position fixture(Boolean client) throws Exception {
        var node = new ClassNode();
        try (var stream = EntityPositionUpdateTest.class.getClassLoader().getResourceAsStream(
                "legacyconnector/v1_12_2/net/minecraft/entity/Entity.class")) {
            assertNotNull(stream);
            new ClassReader(stream).accept(node, ClassReader.SKIP_DEBUG | ClassReader.SKIP_FRAMES);
        }
        var method = node.methods.stream().filter(m -> m.name.equals("setPositionAndUpdate")).findFirst().orElseThrow();
        String name = "test/PositionUpdate";
        var writer = new ClassWriter(ClassWriter.COMPUTE_FRAMES | ClassWriter.COMPUTE_MAXS);
        writer.visit(Opcodes.V17, Opcodes.ACC_PUBLIC, name, null, Type.getInternalName(Position.class), null);
        var ctor = writer.visitMethod(Opcodes.ACC_PUBLIC, "<init>", "()V", null, null);
        ctor.visitCode();
        ctor.visitVarInsn(Opcodes.ALOAD, 0);
        ctor.visitMethodInsn(Opcodes.INVOKESPECIAL, Type.getInternalName(Position.class), "<init>", "()V", false);
        ctor.visitInsn(Opcodes.RETURN);
        ctor.visitMaxs(0, 0);
        ctor.visitEnd();
        var remapper = new SimpleRemapper(Map.of(node.name, Type.getInternalName(Position.class),
                "net/minecraft/world/entity/Entity", Type.getInternalName(Modern.class),
                "net/minecraft/world/level/Level", Type.getInternalName(Side.class)));
        method.accept(new MethodRemapper(writer.visitMethod(Opcodes.ACC_PUBLIC, method.name, method.desc, null, null), remapper));
        writer.visitEnd();
        var bytes = writer.toByteArray();
        class Loader extends ClassLoader {
            Loader() { super(EntityPositionUpdateTest.class.getClassLoader()); }
            Class<?> define() { return defineClass("test.PositionUpdate", bytes, 0, bytes.length); }
        }
        var type = new Loader().define();
        var result = (Position) type.getConstructor().newInstance();
        if (client != null) {
            result.mcc$entity = new Modern();
            result.mcc$entity.side.isClientSide = client;
        }
        type.getMethod("setPositionAndUpdate", double.class, double.class, double.class).invoke(result, 20, 80, -10);
        type.getMethod("setPositionAndUpdate", double.class, double.class, double.class).invoke(result, 21, 81, -12);
        return result;
    }

    @Test void clientBodyFollowsParentOnEveryUpdate() throws Exception {
        var body = fixture(true);
        assertEquals(2, body.moves);
        assertEquals(0, body.mcc$entity.teleports);
        assertEquals(21, body.x);
        assertEquals(81, body.y);
        assertEquals(-12, body.z);
    }

    @Test void serverRetainsTeleportPath() throws Exception {
        var body = fixture(false);
        assertEquals(2, body.mcc$entity.teleports);
        assertEquals(0, body.moves);
    }

    @Test void unhostedBodyStillMoves() throws Exception {
        var body = fixture(null);
        assertEquals(2, body.moves);
        assertEquals(21, body.x);
        assertEquals(81, body.y);
        assertEquals(-12, body.z);
    }
}

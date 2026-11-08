package org.kylepitcock.legacyconnector.loader.transform;

import org.junit.jupiter.api.Test;
import org.objectweb.asm.Opcodes;
import org.objectweb.asm.tree.*;
import static org.junit.jupiter.api.Assertions.*;

class SrpMeteorHeightFixTest {
    private static final String ROOT = "com/dhanantry/scapeandrunparasites/";
    private static final String WORLD = "legacyconnector/v1_12_2/net/minecraft/world/World";
    @Test void changesFloorClampsButPreservesStageAndRadiusConstants() {
        var node = new ClassNode();
        node.name = ROOT + "world/gen/feature/WorldGenParasiteMeteorCrash";
        var method = new MethodNode(Opcodes.ACC_PUBLIC, "generate", "(L" + WORLD + ";)Z", null, null);
        node.methods.add(method);
        var skip = new LabelNode();
        method.instructions.add(new VarInsnNode(Opcodes.ILOAD, 2));
        method.instructions.add(new InsnNode(Opcodes.ICONST_5)); // stage, not a floor
        method.instructions.add(new JumpInsnNode(Opcodes.IF_ICMPEQ, skip));
        method.instructions.add(new VarInsnNode(Opcodes.ILOAD, 2));
        method.instructions.add(new IntInsnNode(Opcodes.BIPUSH, 6)); // pool radius divisor
        method.instructions.add(new InsnNode(Opcodes.IDIV));
        method.instructions.add(new InsnNode(Opcodes.POP));
        method.instructions.add(new VarInsnNode(Opcodes.ILOAD, 2));
        method.instructions.add(new IntInsnNode(Opcodes.BIPUSH, 16));
        method.instructions.add(new InsnNode(Opcodes.IMUL));
        method.instructions.add(new IntInsnNode(Opcodes.BIPUSH, 6));
        method.instructions.add(new InsnNode(Opcodes.IADD));
        method.instructions.add(new VarInsnNode(Opcodes.ISTORE, 3));
        method.instructions.add(new VarInsnNode(Opcodes.ILOAD, 3));
        method.instructions.add(new IntInsnNode(Opcodes.BIPUSH, 6));
        method.instructions.add(new MethodInsnNode(Opcodes.INVOKESTATIC, "java/lang/Math", "max", "(II)I", false));
        method.instructions.add(new VarInsnNode(Opcodes.ISTORE, 3));
        method.instructions.add(new VarInsnNode(Opcodes.ILOAD, 3));
        method.instructions.add(new IntInsnNode(Opcodes.BIPUSH, 6));
        method.instructions.add(new JumpInsnNode(Opcodes.IF_ICMPGE, skip));
        method.instructions.add(new IntInsnNode(Opcodes.BIPUSH, 6));
        method.instructions.add(new VarInsnNode(Opcodes.ISTORE, 3));
        method.instructions.add(skip);
        assertEquals(4, SrpMeteorHeightFix.apply(node));
        for (var insn : method.instructions) {
            if (insn.getOpcode() == Opcodes.ICONST_5) assertEquals(Opcodes.IF_ICMPEQ, insn.getNext().getOpcode());
            if (insn.getOpcode() == Opcodes.IDIV) assertInstanceOf(IntInsnNode.class, insn.getPrevious());
        }
    }
    @Test void onlyAdjustsYComparisonsInMeteorUtilities() {
        var node = new ClassNode();
        node.name = ROOT + "world/gen/feature/util/WorldGenMeteorImpactUtil";
        var method = new MethodNode(Opcodes.ACC_PUBLIC | Opcodes.ACC_STATIC, "carve", "(L" + WORLD + ";)V", null, null);
        node.methods.add(method);
        for (String coordinate : new String[]{"getY", "getX"}) {
            method.instructions.add(new MethodInsnNode(Opcodes.INVOKEVIRTUAL, "legacyconnector/v1_12_2/net/minecraft/util/math/BlockPos", coordinate, "()I", false));
            method.instructions.add(new InsnNode(Opcodes.ICONST_5));
            method.instructions.add(new JumpInsnNode(Opcodes.IF_ICMPGT, new LabelNode()));
        }
        assertEquals(1, SrpMeteorHeightFix.apply(node));
        node.name = "othermod/WorldGenerator";
        assertEquals(0, SrpMeteorHeightFix.apply(node));
    }
    @Test void adjustsMeteorVoidTriggerWithoutChangingOtherDoubleZeros() {
        var node = new ClassNode();
        node.name = ROOT + "entity/projectile/EntityMeteor";
        var method = new MethodNode(Opcodes.ACC_PUBLIC, "onUpdate", "()V", null, null);
        node.methods.add(method);
        method.instructions.add(new VarInsnNode(Opcodes.ALOAD, 0));
        method.instructions.add(new FieldInsnNode(Opcodes.GETFIELD, node.name, "posY", "D"));
        method.instructions.add(new InsnNode(Opcodes.DCONST_0));
        method.instructions.add(new InsnNode(Opcodes.DCMPG));
        method.instructions.add(new InsnNode(Opcodes.DCONST_0));
        assertEquals(1, SrpMeteorHeightFix.apply(node));
        assertEquals(Opcodes.DCONST_0, method.instructions.getLast().getOpcode());
    }
}

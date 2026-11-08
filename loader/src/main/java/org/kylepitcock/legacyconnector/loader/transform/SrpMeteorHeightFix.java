package org.kylepitcock.legacyconnector.loader.transform;

import java.util.ArrayList;
import org.objectweb.asm.Opcodes;
import org.objectweb.asm.Type;
import org.objectweb.asm.tree.*;

/** SRP's meteor floor margins are absolute legacy Y values, unlike its radii and stage numbers. */
final class SrpMeteorHeightFix {
    private static final String ROOT = "com/dhanantry/scapeandrunparasites/";
    private static final String WORLD = "legacyconnector/v1_12_2/net/minecraft/world/World";
    private static final String HELPER = "org/kylepitcock/legacyconnector/v1_12_2/compat/SrpMeteorHeight1122";

    private SrpMeteorHeightFix() {}

    static int apply(ClassNode node) {
        boolean generator = node.name.equals(ROOT + "world/gen/feature/WorldGenParasiteMeteorCrash");
        boolean utility = node.name.equals(ROOT + "world/gen/feature/util/WorldGenMeteorImpactUtil");
        boolean entity = node.name.equals(ROOT + "entity/projectile/EntityMeteor");
        if (!generator && !utility && !entity) return 0;
        int changed = 0;
        for (var method : node.methods) {
            int worldSlot = worldSlot(method);
            var floors = new ArrayList<AbstractInsnNode>();
            for (var insn : method.instructions.toArray()) {
                var previous = code(insn, false);
                var next = code(insn, true);
                if (entity && method.name.equals("onUpdate") && insn.getOpcode() == Opcodes.DCONST_0
                        && previous instanceof FieldInsnNode field && field.name.equals("posY")
                        && next != null && next.getOpcode() == Opcodes.DCMPG) {
                    var replacement = new InsnList();
                    replacement.add(new VarInsnNode(Opcodes.ALOAD, 0));
                    replacement.add(new FieldInsnNode(Opcodes.GETFIELD, node.name, "world", "L" + WORLD + ";"));
                    replacement.add(new MethodInsnNode(Opcodes.INVOKESTATIC, HELPER, "bottom", "(L" + WORLD + ";)D", false));
                    method.instructions.insertBefore(insn, replacement);
                    method.instructions.remove(insn);
                    changed++; method.maxStack += 2;
                }
                if (worldSlot < 0) continue;
                // Only getY() comparisons, never stage == 5 or a radius of 5.
                if (value(insn) == 5 && previous instanceof MethodInsnNode call && call.name.equals("getY")
                        && call.desc.equals("()I") && next instanceof JumpInsnNode) floors.add(insn);
                if (!generator || !method.name.equals("generate") || value(insn) != 6) continue;
                boolean centerMargin = previous != null && previous.getOpcode() == Opcodes.IMUL && next != null && next.getOpcode() == Opcodes.IADD;
                boolean maxFloor = next instanceof MethodInsnNode call && call.owner.equals("java/lang/Math") && call.name.equals("max") && call.desc.equals("(II)I");
                boolean floorCheck = next != null && next.getOpcode() == Opcodes.IF_ICMPGE && previous instanceof VarInsnNode load && load.getOpcode() == Opcodes.ILOAD;
                boolean floorAssignment = next instanceof VarInsnNode store && store.getOpcode() == Opcodes.ISTORE
                        && previous instanceof JumpInsnNode jump && jump.getOpcode() == Opcodes.IF_ICMPGE
                        && value(code(previous, false)) == 6 && code(code(previous, false), false) instanceof VarInsnNode load
                        && load.getOpcode() == Opcodes.ILOAD && load.var == store.var;
                if (centerMargin || maxFloor || floorCheck || floorAssignment) floors.add(insn);
            }
            for (var floor : floors) {
                method.instructions.insertBefore(floor, new VarInsnNode(Opcodes.ALOAD, worldSlot));
                method.instructions.insert(floor, new MethodInsnNode(Opcodes.INVOKESTATIC, HELPER, "floor", "(L" + WORLD + ";I)I", false));
                changed++;
            }
            if (!floors.isEmpty()) method.maxStack++;
        }
        return changed;
    }

    private static int worldSlot(MethodNode method) {
        int slot = (method.access & Opcodes.ACC_STATIC) == 0 ? 1 : 0;
        for (var type : Type.getArgumentTypes(method.desc)) {
            if (type.getSort() == Type.OBJECT && type.getInternalName().equals(WORLD)) return slot;
            slot += type.getSize();
        }
        return -1;
    }
    private static AbstractInsnNode code(AbstractInsnNode insn, boolean forward) {
        if (insn == null) return null;
        do { insn = forward ? insn.getNext() : insn.getPrevious(); } while (insn != null && insn.getOpcode() < 0);
        return insn;
    }
    private static int value(AbstractInsnNode insn) {
        if (insn == null) return Integer.MIN_VALUE;
        if (insn.getOpcode() >= Opcodes.ICONST_M1 && insn.getOpcode() <= Opcodes.ICONST_5) return insn.getOpcode() - Opcodes.ICONST_0;
        if (insn instanceof IntInsnNode integer && (integer.getOpcode() == Opcodes.BIPUSH || integer.getOpcode() == Opcodes.SIPUSH)) return integer.operand;
        return Integer.MIN_VALUE;
    }
}

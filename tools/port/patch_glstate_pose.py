"""1.20.1: render events expose the pose stack (not a model-view matrix), and BooleanState has no getter."""
import sys

GL = {
    "DEPTH_TEST": "GL_DEPTH_TEST",
    "BLEND": "GL_BLEND",
    "CULL": "GL_CULL_FACE",
    "POLYGON_OFFSET": "GL_POLYGON_OFFSET_FILL",
    "LOGIC_OP": "GL_COLOR_LOGIC_OP",
    "SCISSOR": "GL_SCISSOR_TEST",
}

P = r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/LegacyGlState.java"
src = open(P, encoding="utf-8").read()
pairs = [
    ("            case DEPTH_TEST -> depthTest = GlStateManager.DEPTH.mode.enabled;",
     "            // 1.20.1's BooleanState has no getter, so the capability is asked directly (this runs on the render thread).\n"
     "            case DEPTH_TEST -> depthTest = org.lwjgl.opengl.GL11.glIsEnabled(org.lwjgl.opengl.GL11.GL_DEPTH_TEST);"),
    ("            case BLEND -> blend = GlStateManager.BLEND.mode.enabled;",
     "            case BLEND -> blend = org.lwjgl.opengl.GL11.glIsEnabled(org.lwjgl.opengl.GL11.GL_BLEND);"),
    ("            case CULL -> cull = GlStateManager.CULL.enable.enabled;",
     "            case CULL -> cull = org.lwjgl.opengl.GL11.glIsEnabled(org.lwjgl.opengl.GL11.GL_CULL_FACE);"),
    ("            case POLYGON_OFFSET -> polygonOffset = GlStateManager.POLY_OFFSET.fill.enabled;",
     "            case POLYGON_OFFSET -> polygonOffset = org.lwjgl.opengl.GL11.glIsEnabled(org.lwjgl.opengl.GL11.GL_POLYGON_OFFSET_FILL);"),
    ("            case LOGIC_OP -> logicOp = GlStateManager.COLOR_LOGIC.enable.enabled;",
     "            case LOGIC_OP -> logicOp = org.lwjgl.opengl.GL11.glIsEnabled(org.lwjgl.opengl.GL11.GL_COLOR_LOGIC_OP);"),
    ("            case SCISSOR -> scissor = GlStateManager.SCISSOR.mode.enabled;",
     "            case SCISSOR -> scissor = org.lwjgl.opengl.GL11.glIsEnabled(org.lwjgl.opengl.GL11.GL_SCISSOR_TEST);"),
]
for old, new in pairs:
    n = src.count(old)
    if n != 1:
        print(f"ABORT {n}: {old.strip()[:60]}")
        sys.exit(1)
    src = src.replace(old, new)
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P)

# render level stage: 1.20.1 has the pose stack, not a model-view matrix
POSE_OLD = """        pose.last().pose().set(e.getModelViewMatrix());
        pose.last().normal().set(new org.joml.Matrix3f(e.getModelViewMatrix()));"""
POSE_NEW = """        // 1.20.1's event hands out the pose stack (the model-view matrix accessor is 1.20.5+).
        pose.last().pose().set(e.getPoseStack().last().pose());
        pose.last().normal().set(e.getPoseStack().last().normal());"""
for path in (r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/client/ClientEvents1122.java",
             r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/RenderEvents1710.java",
             r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/compat/dragonapi/DragonApiClientEvents.java"):
    src = open(path, encoding="utf-8").read()
    if src.count(POSE_OLD) != 1:
        print(f"ABORT pose {src.count(POSE_OLD)} in {path}")
        sys.exit(1)
    open(path, "w", encoding="utf-8", newline="").write(src.replace(POSE_OLD, POSE_NEW))
    print("patched", path)

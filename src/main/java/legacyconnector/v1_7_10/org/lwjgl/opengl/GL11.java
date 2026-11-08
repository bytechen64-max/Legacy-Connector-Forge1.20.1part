package legacyconnector.v1_7_10.org.lwjgl.opengl;

import com.mojang.blaze3d.platform.GlStateManager;
import com.mojang.blaze3d.systems.RenderSystem;
import java.nio.FloatBuffer;
import org.kylepitcock.legacyconnector.v1_7_10.client.DisplayLists;
import org.kylepitcock.legacyconnector.v1_7_10.client.RenderContext;
import org.slf4j.LoggerFactory;

/**
 * Legacy {@code org.lwjgl.opengl.GL11}. Extends LWJGL 3's GL11, so every constant and every core-profile function
 * resolves to the real one; the fixed-function calls that no longer exist on Minecraft 1.21's core profile (matrix
 * stack, current color, lighting, alpha test, immediate mode) are re-implemented here on top of
 * {@link RenderContext} instead of crashing the game.
 */
public class GL11 extends GL11Guard {

    protected GL11() {
    }

    // ------------------------------------------------------------------ texture queries

    private static final int GL_TEXTURE_BINDING_2D = 0x8069;
    private static final int GL_TEXTURE_WIDTH = 4096;
    private static final int GL_TEXTURE_HEIGHT = 4097;

    /**
     * Legacy bind calls only tell the render context which texture is current, so the real GL binding is unrelated to it: width and
     * height of "the bound texture" (mods compute UVs from them, Custom Main Menu's images) are read from the texture the legacy code bound.
     */
    public static int glGetTexLevelParameteri(int target, int level, int pname) {
        if (target == org.lwjgl.opengl.GL11.GL_TEXTURE_2D && (pname == GL_TEXTURE_WIDTH || pname == GL_TEXTURE_HEIGHT) && RenderSystem.isOnRenderThread()) {
            var rl = RenderContext.texture();
            if (rl != null) {
                try {
                    int id = net.minecraft.client.Minecraft.getInstance().getTextureManager().getTexture(rl).getId();
                    int previous = org.lwjgl.opengl.GL11.glGetInteger(GL_TEXTURE_BINDING_2D);
                    GlStateManager._bindTexture(id);
                    int value = org.lwjgl.opengl.GL11.glGetTexLevelParameteri(target, level, pname);
                    GlStateManager._bindTexture(previous);
                    return value;
                } catch (RuntimeException | LinkageError e) {
                    // fall back to whatever is bound
                }
            }
        }
        return GL11Guard.glGetTexLevelParameteri(target, level, pname);
    }

    // ------------------------------------------------------------------ texture uploads (see GlPixels)

    public static void glTexImage2D(int target, int level, int internalFormat, int width, int height, int border, int format, int type, java.nio.ByteBuffer pixels) {
        GL11Guard.glTexImage2D(target, level, internalFormat, width, height, border, format, type, org.kylepitcock.legacyconnector.v1_7_10.client.GlPixels.safe(pixels, width, height, format, type));
    }

    public static void glTexImage2D(int target, int level, int internalFormat, int width, int height, int border, int format, int type, java.nio.IntBuffer pixels) {
        GL11Guard.glTexImage2D(target, level, internalFormat, width, height, border, format, type, org.kylepitcock.legacyconnector.v1_7_10.client.GlPixels.safe(pixels, width, height, format, type));
    }

    public static void glTexSubImage2D(int target, int level, int xOffset, int yOffset, int width, int height, int format, int type, java.nio.ByteBuffer pixels) {
        GL11Guard.glTexSubImage2D(target, level, xOffset, yOffset, width, height, format, type, org.kylepitcock.legacyconnector.v1_7_10.client.GlPixels.safe(pixels, width, height, format, type));
    }

    public static void glTexSubImage2D(int target, int level, int xOffset, int yOffset, int width, int height, int format, int type, java.nio.IntBuffer pixels) {
        GL11Guard.glTexSubImage2D(target, level, xOffset, yOffset, width, height, format, type, org.kylepitcock.legacyconnector.v1_7_10.client.GlPixels.safe(pixels, width, height, format, type));
    }

    // ------------------------------------------------------------------ LWJGL 2 overloads without the "v" suffix

    private static final int GL_MODELVIEW_MATRIX = 0x0BA6;
    private static final int GL_PROJECTION_MATRIX = 0x0BA7;

    /** The matrix stack is emulated, so the current model-view and projection matrices come from the render context. */
    public static void glGetFloat(int pname, FloatBuffer params) {
        if (pname == GL_MODELVIEW_MATRIX && RenderContext.pose() != null) {
            RenderContext.pose().last().pose().get(params.position(), params);
        } else if (pname == GL_PROJECTION_MATRIX && RenderSystem.isOnRenderThread()) {
            RenderSystem.getProjectionMatrix().get(params.position(), params);
        } else if (!legacyOnly(pname)) {
            GL11Guard.glGetFloatv(pname, params);
        }
    }

    public static void glGetInteger(int pname, java.nio.IntBuffer params) {
        if (!legacyOnly(pname)) GL11Guard.glGetIntegerv(pname, params);
    }

    public static void glGetBoolean(int pname, java.nio.ByteBuffer params) {
        if (!legacyOnly(pname)) GL11Guard.glGetBooleanv(pname, params);
    }

    public static void glGetDouble(int pname, java.nio.DoubleBuffer params) {
        if (!legacyOnly(pname)) GL11Guard.glGetDoublev(pname, params);
    }

    /**
     * State that exists only in the fixed-function pipeline (current colour, lists, lighting, fog, matrix mode and stacks, alpha test,
     * ...): querying it in a core profile raises GL_INVALID_ENUM, which the debug callback logged on every frame (#35).
     */
    private static boolean legacyOnly(int pname) {
        return (pname >= 0x0B00 && pname <= 0x0B0F) || (pname >= 0x0B30 && pname <= 0x0B33) || (pname >= 0x0B50 && pname <= 0x0B6F)
                || pname == 0x0BA0 || (pname >= 0x0BA3 && pname <= 0x0BA5) || pname == 0x0BA8 || pname == 0x0BB0
                || (pname >= 0x0BC0 && pname <= 0x0BC3) || (pname >= 0x0C30 && pname <= 0x0C31) || (pname >= 0x0C40 && pname <= 0x0C41);
    }

    public static float glGetFloat(int pname) {
        return legacyOnly(pname) ? 0F : GL11Guard.glGetFloat(pname);
    }

    public static int glGetInteger(int pname) {
        return legacyOnly(pname) ? 0 : GL11Guard.glGetInteger(pname);
    }

    public static double glGetDouble(int pname) {
        return legacyOnly(pname) ? 0D : GL11Guard.glGetDouble(pname);
    }

    public static boolean glGetBoolean(int pname) {
        // for a capability GL answers like glIsEnabled: emulated ones come from the tracked state (Fisk's Heroes tells its texture
        // pass from its hurt-overlay pass by GL_TEXTURE_2D, and drew suits as the overlay pass)
        switch (pname) {
            case 3553: case 2896: case 3008: case 2912: case 2977: case 32826: case 2903: case 3552: case 3168: case 3169: case 3170: case 3171:
                return glIsEnabled(pname);
            default:
                if (pname >= 0x4000 && pname <= 0x4007) return false;
                return !legacyOnly(pname) && GL11Guard.glGetBoolean(pname);
        }
    }

    /** Fixed-function capabilities (lighting, alpha test, fog, texturing, normalization...) are not GL capabilities any more: the tracked emulated state answers. */
    public static boolean glIsEnabled(int cap) {
        switch (cap) {
            case 3553: return org.kylepitcock.legacyconnector.v1_7_10.client.RenderContext.unitTexture2d();
            case 2896: case 3008: case 2912: case 2977: case 32826: case 2903: case 3552: case 3168: case 3169: case 3170: case 3171:
                return false;
            default:
                if (cap >= 0x4000 && cap <= 0x4007) return false; // GL_LIGHT0..7
                return GL11Guard.glIsEnabled(cap);
        }
    }

    public static void glTexParameter(int target, int pname, FloatBuffer params) {
        GL11Guard.glTexParameterfv(target, pname, params);
    }

    public static void glTexParameter(int target, int pname, java.nio.IntBuffer params) {
        GL11Guard.glTexParameteriv(target, pname, params);
    }

    public static void glTexGen(int coord, int pname, FloatBuffer params) {
    }

    public static void glTexEnv(int target, int pname, FloatBuffer params) {
        org.kylepitcock.legacyconnector.v1_7_10.client.RenderContext.textureEnvColor(target, pname, params);
    }

    public static void glTexEnv(int target, int pname, java.nio.IntBuffer params) {
    }

    public static void glLight(int light, int pname, FloatBuffer params) {
    }

    public static void glMaterial(int face, int pname, FloatBuffer params) {
    }

    public static void glFog(int pname, FloatBuffer params) {
    }

    /** Fog start, end, density and mode: applied to the frame's fog when set by a legacy fog event handler (see LegacyFog). */
    public static void glFogf(int pname, float param) {
        org.kylepitcock.legacyconnector.v1_7_10.client.LegacyFog.fog(pname, param);
    }

    public static void glFogi(int pname, int param) {
        org.kylepitcock.legacyconnector.v1_7_10.client.LegacyFog.fog(pname, param);
    }

    public static void glLoadMatrix(FloatBuffer m) {
        if (m == null || m.remaining() < 16) return;
        org.joml.Matrix4f matrix = new org.joml.Matrix4f().set(m.position(), m);
        if (DisplayLists.recording() && DisplayLists.record(() -> RenderContext.loadMatrix(matrix))) return;
        RenderContext.loadMatrix(matrix);
    }

    public static void glLoadMatrix(java.nio.DoubleBuffer m) {
        if (m == null || m.remaining() < 16) return;
        org.joml.Matrix4f matrix = new org.joml.Matrix4f(new org.joml.Matrix4d().set(m.position(), m));
        if (DisplayLists.recording() && DisplayLists.record(() -> RenderContext.loadMatrix(matrix))) return;
        RenderContext.loadMatrix(matrix);
    }

    public static void glOrtho(double left, double right, double bottom, double top, double zNear, double zFar) {
        mcc$multMatrix(new org.joml.Matrix4f().setOrtho((float) left, (float) right, (float) bottom, (float) top, (float) zNear, (float) zFar));
    }

    public static void glFrustum(double left, double right, double bottom, double top, double zNear, double zFar) {
        mcc$multMatrix(new org.joml.Matrix4f().setFrustum((float) left, (float) right, (float) bottom, (float) top, (float) zNear, (float) zFar));
    }

    public static void glClipPlane(int plane, java.nio.DoubleBuffer equation) {
    }

    /** Binds a GL texture the mod created itself, and makes the emulated renderer draw with it. */
    public static void glBindTexture(int target, int texture) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glBindTexture(target, texture))) return;
        if (!RenderSystem.isOnRenderThread()) return;
        if (target == org.lwjgl.opengl.GL11.GL_TEXTURE_2D) {
            // a bind on another unit (the lightmap's) is not the texture legacy geometry draws with; the modern renderer binds
            // its own lightmap
            if (!RenderContext.onDefaultTextureUnit()) return;
            GlStateManager._bindTexture(texture);
            if (texture != 0) RenderContext.bindTexture(org.kylepitcock.legacyconnector.v1_7_10.client.RawGlTextures.location(texture));
        } else {
            GL11Guard.glBindTexture(target, texture);
        }
    }

    // ------------------------------------------------------------------ matrix stack

    public static void glPushMatrix() {
        if (DisplayLists.recording() && DisplayLists.record(() -> glPushMatrix())) return;
        RenderContext.push();
    }

    public static void glPopMatrix() {
        if (DisplayLists.recording() && DisplayLists.record(() -> glPopMatrix())) return;
        RenderContext.pop();
    }

    public static void glTranslatef(float x, float y, float z) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glTranslatef(x, y, z))) return;
        RenderContext.translate(x, y, z);
    }

    public static void glTranslated(double x, double y, double z) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glTranslated(x, y, z))) return;
        RenderContext.translate(x, y, z);
    }

    public static void glRotatef(float angle, float x, float y, float z) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glRotatef(angle, x, y, z))) return;
        RenderContext.rotate(angle, x, y, z);
    }

    public static void glRotated(double angle, double x, double y, double z) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glRotated(angle, x, y, z))) return;
        RenderContext.rotate((float) angle, (float) x, (float) y, (float) z);
    }

    public static void glScalef(float x, float y, float z) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glScalef(x, y, z))) return;
        RenderContext.scale(x, y, z);
    }

    public static void glScaled(double x, double y, double z) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glScaled(x, y, z))) return;
        RenderContext.scale((float) x, (float) y, (float) z);
    }

    public static void glLoadIdentity() {
        if (DisplayLists.recording() && DisplayLists.record(() -> glLoadIdentity())) return;
        RenderContext.loadIdentity();
    }

    public static void glMatrixMode(int mode) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glMatrixMode(mode))) return;
        RenderContext.matrixMode(mode);
    }

    /** Multiplies the emulated model-view matrix by a column-major 4x4 matrix (the buffer's next 16 values). */
    public static void glMultMatrix(FloatBuffer m) {
        if (m == null || m.remaining() < 16) return;
        org.joml.Matrix4f matrix = new org.joml.Matrix4f().set(m.position(), m);
        mcc$multMatrix(matrix);
    }

    public static void glMultMatrix(java.nio.DoubleBuffer m) {
        if (m == null || m.remaining() < 16) return;
        org.joml.Matrix4f matrix = new org.joml.Matrix4f(new org.joml.Matrix4d().set(m.position(), m));
        mcc$multMatrix(matrix);
    }

    private static void mcc$multMatrix(org.joml.Matrix4f matrix) {
        if (DisplayLists.recording() && DisplayLists.record(() -> mcc$multMatrix(matrix))) return;
        if (RenderContext.multMatrix(matrix)) return; // the texture or projection matrix
        var pose = RenderContext.pose();
        if (pose == null) return;
        var last = pose.last();
        last.pose().mul(matrix);
        org.joml.Matrix3f normal = new org.joml.Matrix3f(matrix);
        if (Math.abs(normal.determinant()) > 1.0E-12F) last.normal().mul(normal.invert().transpose());
    }

    // ------------------------------------------------------------------ color

    /**
     * The current colour; between glBegin and glEnd it is also the following vertices' own colour, as in GL (the colour
     * array of a glDrawElements: CustomOreGen's wireframes took the last vertex's colour for a whole batch and came out banded).
     */
    private static void mcc$color(float r, float g, float b, float a) {
        RenderContext.color(r, g, b, a);
        if (RenderContext.immediate().isDrawing()) RenderContext.immediate().color(r, g, b, a);
    }

    public static void glColor4f(float r, float g, float b, float a) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glColor4f(r, g, b, a))) return;
        mcc$color(r, g, b, a);
    }

    public static void glColor3f(float r, float g, float b) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glColor3f(r, g, b))) return;
        mcc$color(r, g, b, 1.0F);
    }

    public static void glColor4d(double r, double g, double b, double a) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glColor4d(r, g, b, a))) return;
        mcc$color((float) r, (float) g, (float) b, (float) a);
    }

    public static void glColor3d(double r, double g, double b) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glColor3d(r, g, b))) return;
        mcc$color((float) r, (float) g, (float) b, 1.0F);
    }

    public static void glColor4ub(byte r, byte g, byte b, byte a) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glColor4ub(r, g, b, a))) return;
        mcc$color((r & 255) / 255F, (g & 255) / 255F, (b & 255) / 255F, (a & 255) / 255F);
    }

    public static void glColor3ub(byte r, byte g, byte b) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glColor3ub(r, g, b))) return;
        mcc$color((r & 255) / 255F, (g & 255) / 255F, (b & 255) / 255F, 1.0F);
    }

    // ------------------------------------------------------------------ capabilities

    public static void glEnable(int cap) {
        if (!RenderSystem.isOnRenderThread()) return; // a block renderer running on a chunk-building thread: nothing to draw into
        if (DisplayLists.recording() && DisplayLists.record(() -> glEnable(cap))) return;
        mcc$track(cap, true);
        org.kylepitcock.legacyconnector.v1_7_10.client.RenderContext.mcc$beforeGlChange(cap);
        switch (cap) {
            case GL_BLEND -> RenderSystem.enableBlend();
            case GL_DEPTH_TEST -> RenderSystem.enableDepthTest();
            case GL_CULL_FACE -> RenderSystem.enableCull();
            case GL_SCISSOR_TEST -> GlStateManager._enableScissorTest();
            case GL_POLYGON_OFFSET_FILL -> RenderSystem.enablePolygonOffset();
            case GL_COLOR_LOGIC_OP -> RenderSystem.enableColorLogicOp();
            default -> {
                // GL_LIGHTING, GL_ALPHA_TEST, GL_TEXTURE_2D, GL_RESCALE_NORMAL, GL_COLOR_MATERIAL, GL_FOG, light sources:
                // fixed-function state with no core-profile equivalent; modern shaders handle these.
            }
        }
    }

    private static void mcc$track(int cap, boolean on) {
        switch (cap) {
            case 3553 -> org.kylepitcock.legacyconnector.v1_7_10.client.RenderContext.setUnitTexture2d(on); // GL_TEXTURE_2D of the active unit
            case 3042 -> org.kylepitcock.legacyconnector.v1_7_10.client.RenderContext.setBlend(on); // GL_BLEND
            case 2929 -> org.kylepitcock.legacyconnector.v1_7_10.client.RenderContext.setDepthTest(on); // GL_DEPTH_TEST
            case 2896 -> org.kylepitcock.legacyconnector.v1_7_10.client.RenderContext.setLighting(on); // GL_LIGHTING
            default -> {
            }
        }
    }

    public static void glDisable(int cap) {
        if (!RenderSystem.isOnRenderThread()) return; // a block renderer running on a chunk-building thread: nothing to draw into
        if (DisplayLists.recording() && DisplayLists.record(() -> glDisable(cap))) return;
        mcc$track(cap, false);
        org.kylepitcock.legacyconnector.v1_7_10.client.RenderContext.mcc$beforeGlChange(cap);
        switch (cap) {
            case GL_BLEND -> RenderSystem.disableBlend();
            case GL_DEPTH_TEST -> RenderSystem.disableDepthTest();
            case GL_CULL_FACE -> RenderSystem.disableCull();
            case GL_SCISSOR_TEST -> GlStateManager._disableScissorTest();
            case GL_POLYGON_OFFSET_FILL -> RenderSystem.disablePolygonOffset();
            case GL_COLOR_LOGIC_OP -> RenderSystem.disableColorLogicOp();
            default -> {
            }
        }
    }

    public static void glBlendFunc(int src, int dst) {
        if (!RenderSystem.isOnRenderThread()) return; // a block renderer running on a chunk-building thread: nothing to draw into
        if (DisplayLists.recording() && DisplayLists.record(() -> glBlendFunc(src, dst))) return;
        // emulated state first: a screen flushes what it batched under the previous function, which puts that one back
        org.kylepitcock.legacyconnector.v1_7_10.client.RenderContext.setBlendFunc(src, dst);
        org.kylepitcock.legacyconnector.v1_7_10.client.RenderContext.mcc$beforeGlChange(0x0BE1); // GL_BLEND_SRC
        RenderSystem.blendFunc(src, dst);
    }

    public static void glDepthMask(boolean flag) {
        if (!RenderSystem.isOnRenderThread()) return; // a block renderer running on a chunk-building thread: nothing to draw into
        if (DisplayLists.recording() && DisplayLists.record(() -> glDepthMask(flag))) return;
        RenderContext.setDepthWrite(flag);
        RenderContext.mcc$beforeGlChange(0x0B72); // GL_DEPTH_WRITEMASK
        RenderSystem.depthMask(flag);
    }

    public static void glDepthFunc(int func) {
        if (!RenderSystem.isOnRenderThread()) return;
        if (DisplayLists.recording() && DisplayLists.record(() -> glDepthFunc(func))) return;
        RenderContext.setDepthFunc(func);
        RenderContext.mcc$beforeGlChange(0x0B74); // GL_DEPTH_FUNC
        RenderSystem.depthFunc(func);
    }

    public static void glColorMask(boolean r, boolean g, boolean b, boolean a) {
        if (!RenderSystem.isOnRenderThread()) return;
        if (DisplayLists.recording() && DisplayLists.record(() -> glColorMask(r, g, b, a))) return;
        RenderContext.setColorWrite(r, g, b, a);
        RenderContext.mcc$beforeGlChange(0x0C23); // GL_COLOR_WRITEMASK
        RenderSystem.colorMask(r, g, b, a);
    }

    public static void glClear(int mask) {
        if (!RenderSystem.isOnRenderThread()) return;
        if (DisplayLists.recording() && DisplayLists.record(() -> glClear(mask))) return;
        RenderContext.beforeClear();
        org.lwjgl.opengl.GL11.glClear(mask);
    }

    public static void glAlphaFunc(int func, float ref) {
    }

    public static void glShadeModel(int mode) {
    }

    public static void glNormal3f(float x, float y, float z) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glNormal3f(x, y, z))) return;
        RenderContext.immediate().normal(x, y, z);
    }

    public static void glLightModel(int pname, FloatBuffer params) {
    }

    /** Saves the emulated state (blending, depth, enables, colour) that the legacy code changes until glPopAttrib. */
    public static void glPushAttrib(int mask) {
        if (!RenderSystem.isOnRenderThread()) return;
        if (DisplayLists.recording() && DisplayLists.record(() -> glPushAttrib(mask))) return;
        RenderContext.pushAttrib(mask);
    }

    public static void glPopAttrib() {
        if (!RenderSystem.isOnRenderThread()) return;
        if (DisplayLists.recording() && DisplayLists.record(GL11::glPopAttrib)) return;
        RenderContext.popAttrib();
    }

    public static void glCallList(int list) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glCallList(list))) return;
        DisplayLists.call(list);
    }

    private static int mcc$listBase;

    /** Legacy geometry is drawn in batches later, so the real polygon mode would not apply to it: line mode is emulated. */
    public static void glPolygonMode(int face, int mode) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glPolygonMode(face, mode))) return;
        RenderContext.setLineMode(mode == 0x1B01); // GL_LINE
    }

    /** Offset added to every id {@code glCallLists} calls. */
    public static void glListBase(int base) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glListBase(base))) return;
        mcc$listBase = base;
    }

    // Several emulated display lists at once (CustomOreGen's wireframes): the real call knows nothing of the emulated ids.
    public static void glCallLists(java.nio.IntBuffer lists) {
        for (int i = lists.position(); i < lists.limit(); i++) glCallList(mcc$listBase + lists.get(i));
    }

    public static void glCallLists(java.nio.ShortBuffer lists) {
        for (int i = lists.position(); i < lists.limit(); i++) glCallList(mcc$listBase + (lists.get(i) & 0xFFFF));
    }

    public static void glCallLists(java.nio.ByteBuffer lists) {
        for (int i = lists.position(); i < lists.limit(); i++) glCallList(mcc$listBase + (lists.get(i) & 0xFF));
    }

    public static int glGenLists(int range) {
        return DisplayLists.generate(range);
    }

    public static void glNewList(int list, int mode) {
        DisplayLists.begin(list, mode);
    }

    /**
     * Whether the id names a compiled list. Traincraft's TMT models call their cached list only while this is true and drop their
     * geometry once it is compiled, so with an always-false answer every model drawn through ModelBase.render() vanished after one frame.
     */
    public static boolean glIsList(int list) {
        return DisplayLists.exists(list);
    }

    public static void glEndList() {
        DisplayLists.end();
    }

    public static void glDeleteLists(int list, int range) {
        DisplayLists.delete(list, range);
    }

    // ------------------------------------------------------------------ immediate mode

    // glBegin/glEnd vertices are per thread: RenderContext.immediate()

    public static void glBegin(int mode) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glBegin(mode))) return;
        RenderContext.immediate().begin(mode);
    }

    public static void glEnd() {
        if (DisplayLists.recording() && DisplayLists.record(() -> glEnd())) return;
        if (RenderContext.immediate().isDrawing()) RenderContext.immediate().end();
    }

    public static void glVertex3f(float x, float y, float z) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glVertex3f(x, y, z))) return;
        RenderContext.immediate().vertex(x, y, z);
    }

    public static void glVertex3d(double x, double y, double z) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glVertex3d(x, y, z))) return;
        RenderContext.immediate().vertex(x, y, z);
    }

    public static void glVertex2f(float x, float y) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glVertex2f(x, y))) return;
        RenderContext.immediate().vertex(x, y, 0);
    }

    public static void glVertex2i(int x, int y) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glVertex2i(x, y))) return;
        RenderContext.immediate().vertex(x, y, 0);
    }

    public static void glTexCoord2f(float u, float v) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glTexCoord2f(u, v))) return;
        RenderContext.immediate().uv(u, v);
    }

    public static void glTexCoord2d(double u, double v) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glTexCoord2d(u, v))) return;
        RenderContext.immediate().uv(u, v);
    }

    // ------------------------------------------------------------------ fixed-function vertex arrays

    public static void glEnableClientState(int array) {
        org.kylepitcock.legacyconnector.v1_7_10.client.ClientArrays.enable(array, true);
    }

    public static void glDisableClientState(int array) {
        org.kylepitcock.legacyconnector.v1_7_10.client.ClientArrays.enable(array, false);
    }

    public static void glVertexPointer(int size, int type, int stride, long offset) {
        org.kylepitcock.legacyconnector.v1_7_10.client.ClientArrays.setPointer(0x8074, size, type, stride, offset);
    }

    public static void glNormalPointer(int type, int stride, long offset) {
        org.kylepitcock.legacyconnector.v1_7_10.client.ClientArrays.setPointer(0x8075, 3, type, stride, offset);
    }

    public static void glTexCoordPointer(int size, int type, int stride, long offset) {
        org.kylepitcock.legacyconnector.v1_7_10.client.ClientArrays.setPointer(0x8078, size, type, stride, offset);
    }

    public static void glColorPointer(int size, int type, int stride, long offset) {
        org.kylepitcock.legacyconnector.v1_7_10.client.ClientArrays.setPointer(0x8076, size, type, stride, offset);
    }

    public static void glVertexPointer(int size, int stride, FloatBuffer data) {
        org.kylepitcock.legacyconnector.v1_7_10.client.ClientArrays.setPointer(0x8074, size, 0x1406, stride, data);
    }

    public static void glNormalPointer(int stride, FloatBuffer data) {
        org.kylepitcock.legacyconnector.v1_7_10.client.ClientArrays.setPointer(0x8075, 3, 0x1406, stride, data);
    }

    public static void glTexCoordPointer(int size, int stride, FloatBuffer data) {
        org.kylepitcock.legacyconnector.v1_7_10.client.ClientArrays.setPointer(0x8078, size, 0x1406, stride, data);
    }

    public static void glColorPointer(int size, boolean unsigned, int stride, java.nio.ByteBuffer data) {
        org.kylepitcock.legacyconnector.v1_7_10.client.ClientArrays.setPointer(0x8076, size, unsigned ? 0x1401 : 0x1400, stride, data);
    }

    public static void glColorPointer(int size, int type, int stride, java.nio.ByteBuffer data) {
        org.kylepitcock.legacyconnector.v1_7_10.client.ClientArrays.setPointer(0x8076, size, type, stride, data);
    }

    public static void glColorPointer(int size, int stride, FloatBuffer data) {
        org.kylepitcock.legacyconnector.v1_7_10.client.ClientArrays.setPointer(0x8076, size, 0x1406, stride, data);
    }

    public static void glDrawArrays(int mode, int first, int count) {
        org.kylepitcock.legacyconnector.v1_7_10.client.ClientArrays.draw(mode, first, count, ARRAYS);
    }

    // Indexed draws read the emulated arrays too: the real core-profile call has no QUADS mode and no client arrays.
    public static void glDrawElements(int mode, java.nio.IntBuffer indices) {
        org.kylepitcock.legacyconnector.v1_7_10.client.ClientArrays.drawElements(mode, indices, 0x1405, ARRAYS);
    }

    public static void glDrawElements(int mode, java.nio.ShortBuffer indices) {
        org.kylepitcock.legacyconnector.v1_7_10.client.ClientArrays.drawElements(mode, indices, 0x1403, ARRAYS);
    }

    public static void glDrawElements(int mode, java.nio.ByteBuffer indices) {
        org.kylepitcock.legacyconnector.v1_7_10.client.ClientArrays.drawElements(mode, indices, 0x1401, ARRAYS);
    }

    public static void glDrawElements(int mode, int type, java.nio.ByteBuffer indices) {
        org.kylepitcock.legacyconnector.v1_7_10.client.ClientArrays.drawElements(mode, indices, type, ARRAYS);
    }

    public static void glDrawElements(int mode, int count, int type, long offset) {
        org.kylepitcock.legacyconnector.v1_7_10.client.ClientArrays.drawElements(mode, count, type, offset, ARRAYS);
    }

    private static final org.kylepitcock.legacyconnector.v1_7_10.client.ClientArrays.Emitter ARRAYS = new org.kylepitcock.legacyconnector.v1_7_10.client.ClientArrays.Emitter() {
        @Override
        public void begin(int m) {
            glBegin(m);
        }

        @Override
        public void texCoord(float u, float v) {
            glTexCoord2f(u, v);
        }

        @Override
        public void color(float r, float g, float b, float a) {
            glColor4f(r, g, b, a);
        }

        @Override
        public void normal(float x, float y, float z) {
            glNormal3f(x, y, z);
        }

        @Override
        public void vertex(float x, float y, float z) {
            glVertex3f(x, y, z);
        }

        @Override
        public void end() {
            glEnd();
        }
    };

    // ------------------------------------------------------------------------------------------------------------------------
    // State and queries that exist in a core profile too: the fixed-function parts of GL11 are emulated above, the rest goes
    // straight to the real call (the shim used to leave these to the synthesized defaults, so glClearColor, glViewport,
    // glScissor, the stencil calls and the texture parameters of a legacy renderer did nothing at all).
    // ------------------------------------------------------------------------------------------------------------------------

    private static void run(Runnable action) {
        if (DisplayLists.recording() && DisplayLists.record(action)) return;
        if (!RenderSystem.isOnRenderThread()) return;
        action.run();
    }

    public static void glClearColor(float r, float g, float b, float a) {
        run(() -> GL11Guard.glClearColor(r, g, b, a));
    }

    public static void glClearDepth(double depth) {
        run(() -> GL11Guard.glClearDepth(depth));
    }

    public static void glClearStencil(int stencil) {
        run(() -> GL11Guard.glClearStencil(stencil));
    }

    public static void glClearAccum(float r, float g, float b, float a) {
        run(() -> GL11Guard.glClearAccum(r, g, b, a));
    }

    public static void glLineWidth(float width) {
        run(() -> GL11Guard.glLineWidth(width));
    }

    public static void glPointSize(float size) {
        run(() -> GL11Guard.glPointSize(size));
    }

    public static void glLineStipple(int factor, short pattern) {
        // line stipple has no core-profile equivalent
    }

    public static void glPolygonOffset(float factor, float units) {
        run(() -> GL11Guard.glPolygonOffset(factor, units));
    }

    public static void glHint(int target, int mode) {
        run(() -> GL11Guard.glHint(target, mode));
    }

    public static void glCullFace(int mode) {
        run(() -> GL11Guard.glCullFace(mode));
    }

    public static void glFrontFace(int mode) {
        run(() -> GL11Guard.glFrontFace(mode));
    }

    public static void glViewport(int x, int y, int width, int height) {
        run(() -> GL11Guard.glViewport(x, y, width, height));
    }

    public static void glScissor(int x, int y, int width, int height) {
        run(() -> GL11Guard.glScissor(x, y, width, height));
    }

    public static void glDepthRange(double near, double far) {
        run(() -> GL11Guard.glDepthRange(near, far));
    }

    public static void glStencilFunc(int func, int ref, int mask) {
        run(() -> GL11Guard.glStencilFunc(func, ref, mask));
    }

    public static void glStencilMask(int mask) {
        run(() -> GL11Guard.glStencilMask(mask));
    }

    public static void glStencilOp(int fail, int passDepthFail, int passDepthPass) {
        run(() -> GL11Guard.glStencilOp(fail, passDepthFail, passDepthPass));
    }

    public static void glLogicOp(int opcode) {
        run(() -> GL11Guard.glLogicOp(opcode));
    }

    public static void glDrawBuffer(int buffer) {
        run(() -> GL11Guard.glDrawBuffer(buffer));
    }

    public static void glReadBuffer(int buffer) {
        run(() -> GL11Guard.glReadBuffer(buffer));
    }

    public static void glPixelStorei(int pname, int param) {
        run(() -> GL11Guard.glPixelStorei(pname, param));
    }

    public static void glPixelStoref(int pname, float param) {
        run(() -> GL11Guard.glPixelStoref(pname, param));
    }

    public static void glPixelZoom(float x, float y) {
        // a raster operation: nothing to draw in a core profile
    }

    public static void glTexParameteri(int target, int pname, int param) {
        run(() -> GL11Guard.glTexParameteri(target, pname, param));
    }

    public static void glTexParameterf(int target, int pname, float param) {
        run(() -> GL11Guard.glTexParameterf(target, pname, param));
    }

    public static int glGenTextures() {
        return GL11Guard.glGenTextures();
    }

    public static void glGenTextures(java.nio.IntBuffer textures) {
        GL11Guard.glGenTextures(textures);
    }

    public static void glGenTextures(int[] textures) {
        for (int i = 0; i < textures.length; i++) textures[i] = GL11Guard.glGenTextures();
    }

    public static void glDeleteTextures(java.nio.IntBuffer textures) {
        GL11Guard.glDeleteTextures(textures);
    }

    public static void glDeleteTextures(int[] textures) {
        for (int texture : textures) GL11Guard.glDeleteTextures(texture);
    }

    public static void glDeleteTextures(int texture) {
        GL11Guard.glDeleteTextures(texture);
    }

    public static void glFinish() {
        run(GL11Guard::glFinish);
    }

    public static void glFlush() {
        run(GL11Guard::glFlush);
    }

    public static int glGetError() {
        return GL11Guard.glGetError();
    }

    public static String glGetString(int name) {
        return GL11Guard.glGetString(name);
    }

    public static void glColorMaterial(int face, int mode) {
        // lighting state; the emulated colour is used as-is
    }

    public static void glLightModeli(int pname, int param) {
        // fixed-function lighting: emulated colour comes from glColor
    }

    public static void glLightModelf(int pname, float param) {
    }

    public static void glLightf(int light, int pname, float param) {
    }

    public static void glLighti(int light, int pname, int param) {
    }

    public static void glMaterialf(int face, int pname, float param) {
    }

    public static void glMateriali(int face, int pname, int param) {
    }

    public static void glTexEnvi(int target, int pname, int param) {
        org.kylepitcock.legacyconnector.v1_7_10.client.RenderContext.textureEnvMode(target, pname, param);
        run(() -> GL11Guard.glTexEnvi(target, pname, param));
    }

    public static void glTexEnvf(int target, int pname, float param) {
        org.kylepitcock.legacyconnector.v1_7_10.client.RenderContext.textureEnvMode(target, pname, (int) param);
        run(() -> GL11Guard.glTexEnvf(target, pname, param));
    }

    public static void glRasterPos2f(float x, float y) {
        // raster position is gone; 2D mods that set it before glDrawPixels draw nothing either way
    }

    public static void glRasterPos2d(double x, double y) {
    }

    public static void glRasterPos3f(float x, float y, float z) {
    }

    public static void glArrayElement(int index) {
        // client-array draws are emulated by ClientArrays, which reads the arrays directly
    }

    public static void glPushClientAttrib(int mask) {
    }

    public static void glPopClientAttrib() {
    }

    public static void glCopyTexImage2D(int target, int level, int internalFormat, int x, int y, int width, int height, int border) {
        run(() -> GL11Guard.glCopyTexImage2D(target, level, internalFormat, x, y, width, height, border));
    }

    public static void glCopyTexSubImage2D(int target, int level, int xOffset, int yOffset, int x, int y, int width, int height) {
        run(() -> GL11Guard.glCopyTexSubImage2D(target, level, xOffset, yOffset, x, y, width, height));
    }

    public static void glTexImage1D(int target, int level, int internalFormat, int width, int border, int format, int type, java.nio.ByteBuffer pixels) {
        // 1D textures are not sampled by the modern pipeline
    }

    public static void glTexSubImage1D(int target, int level, int xOffset, int width, int format, int type, java.nio.ByteBuffer pixels) {
    }

    public static void glVertex4f(float x, float y, float z, float w) {
        if (DisplayLists.recording() && DisplayLists.record(() -> glVertex4f(x, y, z, w))) return;
        RenderContext.immediate().vertex(x, y, z);
    }

    public static void glVertex4d(double x, double y, double z, double w) {
        glVertex4f((float) x, (float) y, (float) z, (float) w);
    }

    public static void glVertex2d(double x, double y) {
        glVertex2f((float) x, (float) y);
    }

    public static void glNormal3b(byte x, byte y, byte z) {
        glNormal3f(x / 127.0F, y / 127.0F, z / 127.0F);
    }

    public static void glNormal3d(double x, double y, double z) {
        glNormal3f((float) x, (float) y, (float) z);
    }

    public static void glTexCoord1f(float s) {
        glTexCoord2f(s, 0.0F);
    }

    public static void glTexCoord2i(int s, int t) {
        glTexCoord2f(s, t);
    }

    public static void glTexCoord3f(float s, float t, float r) {
        glTexCoord2f(s, t);
    }

    public static void glTexCoord4f(float s, float t, float r, float q) {
        glTexCoord2f(s, t);
    }

    public static void glRectf(float x1, float y1, float x2, float y2) {
        glBegin(7); // GL_QUADS
        glVertex2f(x1, y1);
        glVertex2f(x2, y1);
        glVertex2f(x2, y2);
        glVertex2f(x1, y2);
        glEnd();
    }

    public static void glRecti(int x1, int y1, int x2, int y2) {
        glRectf(x1, y1, x2, y2);
    }
}

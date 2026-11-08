package org.kylepitcock.legacyconnector.v1_7_10.client;

import java.nio.FloatBuffer;

/** The constant and mode of the legacy lightmap texture combiner. */
public final class LegacyTextureTint {
    private boolean interpolate;
    private float red, green, blue, alpha;

    public void mode(int mode) { interpolate = mode == 34165; /* GL_INTERPOLATE */ }
    public void constant(FloatBuffer values) {
        if (values.remaining() < 4) return;
        int p = values.position();
        red = values.get(p); green = values.get(p + 1); blue = values.get(p + 2); alpha = values.get(p + 3);
    }
    public void clear() { interpolate = false; alpha = 0; }
    public boolean active() { return interpolate; }
    /** Modern entity shaders use mix(overlay.rgb, surface.rgb, overlay.a), the reverse of the GL constant weight. */
    public int overlayArgb() {
        return byteValue(1 - alpha) << 24 | byteValue(red) << 16 | byteValue(green) << 8 | byteValue(blue);
    }
    private static int byteValue(float value) { return Math.round(Math.max(0, Math.min(1, value)) * 255); }
}

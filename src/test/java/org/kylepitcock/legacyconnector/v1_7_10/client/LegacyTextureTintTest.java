package org.kylepitcock.legacyconnector.v1_7_10.client;

import java.nio.FloatBuffer;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class LegacyTextureTintTest {
    @Test void encodesSrpGreenAsReplacementOverlayWithoutRedOrChangingBufferPosition() {
        var tint = new LegacyTextureTint();
        var constant = FloatBuffer.wrap(new float[]{9, 0, 1, 0, 0.3F});
        constant.position(1);
        tint.mode(34165);
        tint.constant(constant);
        assertEquals(1, constant.position());
        assertTrue(tint.active());
        assertEquals(0xB300FF00, tint.overlayArgb());
        // A black part of the skin gains green through interpolation. Multiplying vertices could never do this.
        int overlay = tint.overlayArgb();
        float originalWeight = (overlay >>> 24) / 255F;
        assertEquals(0.3F, 1 - originalWeight, 1 / 255F);
    }

    @Test void resetAndModulateRestoreUntintedGeometry() {
        var tint = new LegacyTextureTint();
        tint.constant(FloatBuffer.wrap(new float[]{0, 1, 0, 1}));
        tint.mode(34165);
        assertEquals(0x0000FF00, tint.overlayArgb());
        tint.mode(8448);
        assertFalse(tint.active());
        tint.mode(34165);
        tint.clear();
        assertFalse(tint.active());
    }
}

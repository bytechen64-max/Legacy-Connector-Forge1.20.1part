package org.kylepitcock.legacyconnector.v1_12_2.entity;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class OrbInterpolation1122Test {
    @Test void spreadsPacketMovementAcrossTicksAndStopsAtTarget() {
        var lerp = new OrbInterpolation1122();
        lerp.target(9, 6, -3, 90, 30, 3);
        var first = lerp.tick(0, 0, 0, 0, 0);
        assertEquals(new OrbInterpolation1122.Position(3, 2, -1, 30, 10), first);
        var second = lerp.tick(first.x(), first.y(), first.z(), first.yaw(), first.pitch());
        assertEquals(new OrbInterpolation1122.Position(6, 4, -2, 60, 20), second);
        var third = lerp.tick(second.x(), second.y(), second.z(), second.yaw(), second.pitch());
        assertEquals(new OrbInterpolation1122.Position(9, 6, -3, 90, 30), third);
        assertNull(lerp.tick(9, 6, -3, 90, 30));
    }

    @Test void newerPacketContinuesFromCurrentPosition() {
        var lerp = new OrbInterpolation1122();
        lerp.target(9, 0, 0, 0, 0, 3);
        var first = lerp.tick(0, 0, 0, 0, 0);
        lerp.target(15, 0, 0, 0, 0, 3);
        assertEquals(7, lerp.tick(first.x(), 0, 0, 0, 0).x());
    }

    @Test void yawTakesShortestPathAcrossBoundary() {
        var lerp = new OrbInterpolation1122();
        lerp.target(0, 0, 0, -170, 0, 2);
        assertEquals(180, lerp.tick(0, 0, 0, 170, 0).yaw());
    }

    @Test void teleportCancelsPendingMovement() {
        var lerp = new OrbInterpolation1122();
        lerp.target(9, 0, 0, 0, 0, 3);
        lerp.clear();
        assertNull(lerp.tick(100, 0, 0, 0, 0));
        lerp.target(9, 0, 0, 0, 0, 0);
        assertNull(lerp.tick(100, 0, 0, 0, 0));
    }

    @Test void onlySrpOrbsOptIn() {
        for (String kind : new String[] {"Boom", "Void", "Scary"}) {
            assertTrue(OrbInterpolation1122.supports("com.dhanantry.scapeandrunparasites.entity.EntityOrb" + kind));
        }
        assertFalse(OrbInterpolation1122.supports("net.minecraft.entity.item.EntityXPOrb"));
        assertFalse(OrbInterpolation1122.supports("example.EntityOrbBoom"));
    }
}

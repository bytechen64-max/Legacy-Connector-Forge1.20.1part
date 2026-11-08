package org.kylepitcock.legacyconnector.v1_12_2.compat;

import legacyconnector.v1_12_2.net.minecraft.world.World;

/** Keeps the original meteor's bedrock margins relative to the actual world's bottom. */
public final class SrpMeteorHeight1122 {
    private SrpMeteorHeight1122() {}
    public static int floor(World world, int margin) {
        return (world == null || world.mcc$access() == null ? 0 : world.mcc$access().getMinBuildHeight()) + margin;
    }
    public static double bottom(World world) { return floor(world, 0); }
}

package org.kylepitcock.legacyconnector.v1_12_2.entity;

/** Client network interpolation for SRP's server-positioned, non-living orbs. */
final class OrbInterpolation1122 {
    private int remaining;
    private double x, y, z;
    private float yaw, pitch;

    static boolean supports(String className) {
        return className.equals("com.dhanantry.scapeandrunparasites.entity.EntityOrbBoom")
                || className.equals("com.dhanantry.scapeandrunparasites.entity.EntityOrbVoid")
                || className.equals("com.dhanantry.scapeandrunparasites.entity.EntityOrbScary");
    }

    void target(double x, double y, double z, float yaw, float pitch, int steps) {
        this.x = x;
        this.y = y;
        this.z = z;
        this.yaw = yaw;
        this.pitch = pitch;
        remaining = Math.max(0, steps);
    }

    void clear() {
        remaining = 0;
    }

    /** Called once per client tick, after vanilla has saved the previous render position. */
    Position tick(double currentX, double currentY, double currentZ, float currentYaw, float currentPitch) {
        if (remaining == 0) return null;
        double fraction = 1.0D / remaining--;
        float turn = (yaw - currentYaw) % 360.0F;
        if (turn >= 180.0F) turn -= 360.0F;
        if (turn < -180.0F) turn += 360.0F;
        return new Position(currentX + (x - currentX) * fraction,
                currentY + (y - currentY) * fraction, currentZ + (z - currentZ) * fraction,
                currentYaw + (float) (turn * fraction), currentPitch + (float) ((pitch - currentPitch) * fraction));
    }

    record Position(double x, double y, double z, float yaw, float pitch) {}
}

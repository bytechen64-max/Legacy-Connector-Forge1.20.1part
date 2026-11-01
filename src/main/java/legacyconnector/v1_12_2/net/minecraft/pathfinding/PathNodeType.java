package legacyconnector.v1_12_2.net.minecraft.pathfinding;

/** What a block is to a walking mob, with its default path cost (negative: never entered). */
public enum PathNodeType {
    BLOCKED(-1.0F), OPEN(0.0F), WALKABLE(0.0F), TRAPDOOR(0.0F), FENCE(-1.0F), LAVA(-1.0F), WATER(8.0F), RAIL(0.0F), DANGER_FIRE(8.0F),
    DAMAGE_FIRE(16.0F), DANGER_CACTUS(8.0F), DAMAGE_CACTUS(-1.0F), DANGER_OTHER(8.0F), DAMAGE_OTHER(-1.0F), DOOR_OPEN(0.0F),
    DOOR_WOOD_CLOSED(-1.0F), DOOR_IRON_CLOSED(-1.0F);

    private final float priority;

    PathNodeType(float priority) {
        this.priority = priority;
    }

    public float getPriority() {
        return priority;
    }

    /** The modern path type of the same meaning (cactus is the modern "other" damage). */
    public net.minecraft.world.level.pathfinder.BlockPathTypes mcc$modern() {
        return switch (this) {
            case DANGER_CACTUS -> net.minecraft.world.level.pathfinder.BlockPathTypes.DANGER_OTHER;
            case DAMAGE_CACTUS -> net.minecraft.world.level.pathfinder.BlockPathTypes.DAMAGE_OTHER;
            default -> net.minecraft.world.level.pathfinder.BlockPathTypes.valueOf(name());
        };
    }

    public static PathNodeType mcc$of(net.minecraft.world.level.pathfinder.BlockPathTypes type) {
        try {
            return valueOf(type.name());
        } catch (IllegalArgumentException e) {
            return switch (type) {
                case WALKABLE_DOOR -> DOOR_OPEN;
                case WATER_BORDER -> WALKABLE;
                case UNPASSABLE_RAIL -> BLOCKED;
                // 1.20.1's BlockPathTypes has no POWDER_SNOW/LEAVES constants: those cases cannot occur, the default handles them.
                default -> BLOCKED;
            };
        }
    }
}

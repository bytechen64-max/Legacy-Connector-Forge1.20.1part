package org.kylepitcock.legacyconnector.core;

import java.util.function.Function;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraftforge.common.util.ITeleporter;

/**
 * Moving an entity to another level.
 *
 * <p>1.21 hands {@link Entity#changeDimension(net.minecraft.world.level.portal.DimensionTransition)} one record with the target, the
 * position and the result handling. On 1.20.1 the target level comes first and an {@link ITeleporter} decides where the entity lands;
 * the legacy code's "same coordinates and rotation" is {@code repositionEntity.apply(false)}.</p>
 */
public final class Teleports {
    private Teleports() {}

    private static final ITeleporter SAME_PLACE = new ITeleporter() {
        @Override
        public Entity placeEntity(Entity entity, ServerLevel currentLevel, ServerLevel destinationLevel, float yaw,
                Function<Boolean, Entity> repositionEntity) {
            return repositionEntity.apply(false);
        }
    };

    /** Moves the entity to {@code target}, keeping its position and rotation (null when the move did not happen). */
    public static Entity changeDimension(Entity entity, ServerLevel target) {
        return entity == null || target == null ? null : entity.changeDimension(target, SAME_PLACE);
    }
}

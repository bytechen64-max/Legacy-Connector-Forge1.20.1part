package legacyconnector.v1_12_2.net.minecraft.entity;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import legacyconnector.v1_12_2.net.minecraft.entity.EntityLiving.SpawnPlacementType;

/** Legacy placement registrations read by custom spawners such as SRP's world spawner. */
public final class EntitySpawnPlacementRegistry {
    private static final Map<Class<?>, SpawnPlacementType> PLACEMENTS = new ConcurrentHashMap<>();

    private EntitySpawnPlacementRegistry() {}

    public static void setPlacementType(Class<? extends EntityLiving> entityClass, SpawnPlacementType placement) {
        PLACEMENTS.put(entityClass, placement);
    }

    public static SpawnPlacementType getPlacementForEntity(Class<? extends EntityLiving> entityClass) {
        SpawnPlacementType registered = PLACEMENTS.get(entityClass);
        if (registered != null) return registered;
        if (legacyconnector.v1_12_2.net.minecraft.entity.passive.EntityWaterMob.class.isAssignableFrom(entityClass)) {
            return SpawnPlacementType.IN_WATER;
        }
        return SpawnPlacementType.ON_GROUND;
    }
}

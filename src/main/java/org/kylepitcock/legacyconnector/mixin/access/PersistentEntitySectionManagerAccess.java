package org.kylepitcock.legacyconnector.mixin.access;

import it.unimi.dsi.fastutil.longs.Long2ObjectMap;
import net.minecraft.world.level.entity.PersistentEntitySectionManager;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;
import org.spongepowered.asm.mixin.gen.Invoker;

/**
 * The pending entity loads of the server's entity manager, which 1.7.10 code waits for (a spawner that reads the entity back in the
 * same tick). 1.20.1 keeps both the queue and its statuses private.
 */
@Mixin(PersistentEntitySectionManager.class)
public interface PersistentEntitySectionManagerAccess {
    @Invoker("processPendingLoads")
    void legacyconnector$processPendingLoads();

    @Accessor("chunkLoadStatuses")
    Long2ObjectMap<?> legacyconnector$chunkLoadStatuses();
}

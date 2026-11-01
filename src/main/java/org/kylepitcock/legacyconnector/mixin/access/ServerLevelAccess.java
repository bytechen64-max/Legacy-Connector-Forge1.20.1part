package org.kylepitcock.legacyconnector.mixin.access;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.entity.PersistentEntitySectionManager;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/**
 * The entity manager of a server level. 1.7.10 mods that spawn an entity and read it back in the same tick need the pending entity
 * loads to run; 1.20.1 keeps the manager in a private field, so the shim reaches it through this accessor.
 */
@Mixin(ServerLevel.class)
public interface ServerLevelAccess {
    @Accessor("entityManager")
    PersistentEntitySectionManager<Entity> legacyconnector$entityManager();
}

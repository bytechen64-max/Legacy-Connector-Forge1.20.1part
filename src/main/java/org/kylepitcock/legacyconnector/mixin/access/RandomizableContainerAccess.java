package org.kylepitcock.legacyconnector.mixin.access;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.entity.RandomizableContainerBlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/**
 * Whether a container still has a loot table to unpack. 1.20.1 keeps the table in a protected field without a getter (1.20.2
 * added {@code getLootTable()}), so the chest shim checks it through this accessor.
 */
@Mixin(RandomizableContainerBlockEntity.class)
public interface RandomizableContainerAccess {
    @Accessor("lootTable")
    ResourceLocation legacyconnector$lootTable();
}

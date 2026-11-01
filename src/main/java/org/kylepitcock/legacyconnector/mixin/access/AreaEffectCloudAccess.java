package org.kylepitcock.legacyconnector.mixin.access;

import java.util.List;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.AreaEffectCloud;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/**
 * The effects a 1.20.1 area effect cloud carries besides its potion's.
 *
 * <p>1.20.5 moved them into the {@code potion_contents} component and gave the cloud accessors; on 1.20.1 the list is private, so
 * the 1.12 shim (which lets mods read and write the cloud's effects) goes through this accessor.</p>
 */
@Mixin(AreaEffectCloud.class)
public interface AreaEffectCloudAccess {
    @Accessor("effects")
    List<MobEffectInstance> legacyconnector$effects();
}

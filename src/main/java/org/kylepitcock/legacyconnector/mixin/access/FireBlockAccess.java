package org.kylepitcock.legacyconnector.mixin.access;

import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.FireBlock;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

/**
 * The fire block's flammability table.
 *
 * <p>1.12 mods register their blocks with {@code Blocks.fire.setFlammable(...)}; 1.20.1 keeps that method private, and ForgeGradle
 * does not widen the compile classpath with the mod's access transformer, so the shims reach it through this invoker.</p>
 */
@Mixin(FireBlock.class)
public interface FireBlockAccess {
    @Invoker("setFlammable")
    void legacyconnector$setFlammable(Block block, int encouragement, int flammability);
}

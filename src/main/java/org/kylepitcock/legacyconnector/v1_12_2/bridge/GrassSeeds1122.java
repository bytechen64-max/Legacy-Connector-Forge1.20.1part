package org.kylepitcock.legacyconnector.v1_12_2.bridge;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;
import legacyconnector.v1_12_2.net.minecraft.item.ItemStack;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.event.level.BlockEvent.BreakEvent;

/**
 * Forge 1.12's grass seed list ({@code MinecraftForge.addGrassSeed}): broken tall grass dropped, one time in eight, a seed picked by
 * weight from the list, which starts with wheat seeds of weight 10. The modern short grass and fern keep their own wheat seed loot;
 * the mods' seeds are rolled alongside with their share of the list's weight, through the block drops event.
 */
public final class GrassSeeds1122 {
    private static final int WHEAT_WEIGHT = 10;

    private record Seed(ItemStack stack, int weight) {}

    private static final List<Seed> SEEDS = new ArrayList<>();
    private static boolean listening;

    private GrassSeeds1122() {}

    public static synchronized void add(ItemStack seed, int weight) {
        if (seed == null || seed.isEmpty() || weight <= 0) return;
        SEEDS.add(new Seed(seed.copy(), weight));
        if (!listening) {
            listening = true;
        }
    }

    // 1.20.1 has no BlockDropsEvent (it arrived in 1.20.2): the extra seed drops need a global loot modifier,
    // which this shim does not generate yet (see PORTING.md).
}

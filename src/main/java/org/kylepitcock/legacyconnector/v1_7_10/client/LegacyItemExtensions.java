package org.kylepitcock.legacyconnector.v1_7_10.client;

import java.util.function.Consumer;
import legacyconnector.v1_7_10.net.minecraft.item.ItemBlock;
import net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer;
import net.minecraftforge.client.extensions.common.IClientItemExtensions;
import org.kylepitcock.legacyconnector.v1_7_10.adapter.LegacyItemHolder;

/**
 * Item client extensions of a legacy item. 1.20.1 has no client-extension registration event: an item hands its extensions out of
 * {@code Item#initializeClient}, which Forge calls from the item's constructor on a physical client, so the legacy item adapters
 * forward it here.
 *
 * <p>The renderer is only consulted where the generated model is {@code builtin/entity}: chests (legacy render type 22) are drawn
 * by the legacy chest helper, everything else only when a mod registered a Forge {@code IItemRenderer} for it.</p>
 */
public final class LegacyItemExtensions implements IClientItemExtensions {
    private final boolean chest;
    private BlockEntityWithoutLevelRenderer renderer;

    private LegacyItemExtensions(boolean chest) {
        this.chest = chest;
    }

    /** The extensions of one legacy metadata variant of an item ({@code LegacyItemHolder}). */
    public static void install(LegacyItemHolder holder, Consumer<IClientItemExtensions> consumer) {
        boolean chest = false;
        try {
            if (holder.legacyItem() instanceof ItemBlock ib) chest = Client1710.isChestStyle(ib.mcc$block());
        } catch (RuntimeException | LinkageError e) {
            // a mod whose classes failed to initialise keeps the generic renderer
        }
        consumer.accept(new LegacyItemExtensions(chest));
    }

    @Override
    public BlockEntityWithoutLevelRenderer getCustomRenderer() {
        if (renderer == null) renderer = chest ? new LegacyChestItemRenderer() : new LegacyItemRenderer();
        return renderer;
    }
}

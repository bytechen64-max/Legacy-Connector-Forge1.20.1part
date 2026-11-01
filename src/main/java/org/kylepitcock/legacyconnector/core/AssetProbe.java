package org.kylepitcock.legacyconnector.core;

import net.minecraft.client.Minecraft;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Development aid: says which pack serves a legacy blockstate and prints the head of the file, so "missing model for variant" can be
 * traced to the file the client actually reads (the mod's own 1.12 file or the generated replacement).
 */
public final class AssetProbe {
    private static final Logger LOG = LoggerFactory.getLogger("LegacyConnector/AssetProbe");
    private static boolean done;

    private AssetProbe() {}

    public static void register(IEventBus gameBus) {
        gameBus.addListener((TickEvent.ClientTickEvent e) -> {
            if (e.phase != TickEvent.Phase.END || done) return;
            done = true;
            probe();
        });
    }

    private static void probe() {
        try {
            LOG.warn("ASSETPROBE generated blockstate: {}", org.kylepitcock.legacyconnector.core.pack.GeneratedPack.mcc$probe("assets/srparasites/blockstates/infestedstain.json"));
            LOG.warn("ASSETPROBE generated item model: {}", org.kylepitcock.legacyconnector.core.pack.GeneratedPack.mcc$probe("assets/srparasites/models/item/infestedstain.json"));            var manager = Minecraft.getInstance().getResourceManager();
            for (String name : new String[] {"srparasites:blockstates/infestedstain.json", "srparasites:blockstates/bile.json",
                    "srparasites:models/block/infestedstain.json"}) {
                int colon = name.indexOf(':');
                var location = ResourceLocation.fromNamespaceAndPath(name.substring(0, colon), name.substring(colon + 1));
                var found = manager.getResource(location);
                if (found.isEmpty()) {
                    LOG.warn("ASSETPROBE {} is served by no pack", name);
                    continue;
                }
                String pack = found.get().sourcePackId();
                String head;
                try (var in = found.get().open()) {
                    head = new String(in.readNBytes(260), java.nio.charset.StandardCharsets.UTF_8).replace('\n', ' ');
                }
                LOG.warn("ASSETPROBE {} served by pack '{}': {}", name, pack, head);
            }
        } catch (RuntimeException | java.io.IOException ex) {
            LOG.warn("ASSETPROBE failed: {}", ex.toString());
        }
    }
}
package org.kylepitcock.legacyconnector.core.pack;

import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.function.BooleanSupplier;
import net.minecraft.server.MinecraftServer;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.event.server.ServerStartedEvent;
import net.minecraftforge.event.TickEvent.ServerTickEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Reloads the data packs when legacy recipes changed after the recipe pack was generated. Legacy mods may add or remove recipes
 * once the server exists: MineTweaker runs its scripts on {@code FMLServerAboutToStartEvent} (after the modern data packs
 * loaded) and again on {@code /minetweaker reload}; without a reload those changes would never reach the recipe manager.
 */
public final class LegacyRecipeSync {
    private static final Logger LOG = LoggerFactory.getLogger("LegacyConnector/Recipes");
    private static final int CHECK_TICKS = 100;
    private static final long MIN_INTERVAL_MS = 10_000;

    private static final List<BooleanSupplier> SOURCES = new CopyOnWriteArrayList<>();
    private static final List<Runnable> SYNCED = new CopyOnWriteArrayList<>();
    /** Safety net: enough reloads have happened, so whatever keeps reporting a change cannot hold the server hostage. */
    private static final int MAX_RELOADS_PER_WINDOW = 4;
    private static final long WINDOW_MS = 300_000L;
    private static final java.util.ArrayDeque<Long> RELOADS = new java.util.ArrayDeque<>();
    private static volatile boolean reloading;
    private static long lastReload;
    private static int ticks;
    private static boolean LOGGED_CAP;

    private LegacyRecipeSync() {}

    /** A test telling whether a legacy registry changed since the recipe pack last read it, and the matching "take a new snapshot". */
    public static void watch(BooleanSupplier changedSinceGenerate, Runnable markSynced) {
        SOURCES.add(changedSinceGenerate);
        SYNCED.add(markSynced);
    }

    public static void register(IEventBus gameBus) {
        // LOWEST: after the legacy FMLServerStartedEvent handlers ran (the server-start events are all past then).
        gameBus.addListener(EventPriority.LOWEST, (ServerStartedEvent e) -> check(e.getServer(), true));
        // 1.20.1 fires one server tick event with a phase (the Post class is 1.20.2+)
        gameBus.addListener((net.minecraftforge.event.TickEvent.ServerTickEvent e) -> {
            if (e.phase != net.minecraftforge.event.TickEvent.Phase.END) return;
            if (++ticks % CHECK_TICKS == 0) check(e.getServer(), false);
        });
    }

    private static void check(MinecraftServer server, boolean startup) {
        if (reloading || (!startup && System.currentTimeMillis() - lastReload < MIN_INTERVAL_MS)) return;
        boolean changed = false;
        for (BooleanSupplier s : SOURCES) {
            try {
                changed |= s.getAsBoolean();
            } catch (RuntimeException e) {
                LOG.debug("Legacy recipe change check failed: {}", e.toString());
            }
        }
        if (!changed) return;
        long now = System.currentTimeMillis();
        synchronized (RELOADS) {
            while (!RELOADS.isEmpty() && now - RELOADS.peekFirst() > WINDOW_MS) RELOADS.pollFirst();
            if (RELOADS.size() >= MAX_RELOADS_PER_WINDOW) {
                if (!LOGGED_CAP) {
                    LOG.warn("Legacy recipes keep changing; not reloading the data packs again for now ({} reloads in {} s)", RELOADS.size(), WINDOW_MS / 1000);
                    LOGGED_CAP = true;
                }
                return;
            }
            RELOADS.addLast(now);
        }
        reloading = true;
        lastReload = now;
        LOG.info("Legacy recipes changed after the data packs loaded (scripts such as MineTweaker's); reloading data packs");
        server.reloadResources(server.getPackRepository().getSelectedIds()).whenComplete((v, err) -> {
            reloading = false;
            if (err != null) {
                LOG.warn("Reloading data packs for changed legacy recipes failed", err);
                return;
            }
            // the change is in the recipe manager now: take it as the new baseline, or the next check reports it again
            for (Runnable sync : SYNCED) {
                try {
                    sync.run();
                } catch (RuntimeException e) {
                    LOG.debug("Marking legacy recipes synced failed: {}", e.toString());
                }
            }
        });
    }
}

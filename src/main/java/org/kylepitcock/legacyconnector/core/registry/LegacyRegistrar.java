package org.kylepitcock.legacyconnector.core.registry;

import java.util.LinkedHashMap;
import java.util.Map;
import net.minecraft.core.Registry;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.registries.IForgeRegistry;
import org.kylepitcock.legacyconnector.core.LegacyLifecycle;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * All legacy registrations go through here.
 *
 * <p>Forge 1.20.1 locks a registry as soon as its own {@code RegisterEvent} has been dispatched
 * ({@code NamespacedWrapper.locked}; {@code Registry.register} then throws "Can not register to a locked registry"), while
 * NeoForge 1.21 keeps every registry open for the whole registration phase. Legacy mods register imperatively during
 * preInit/init, i.e. outside any particular registry's event, so a registration is <em>queued</em> here and written when the
 * {@code RegisterEvent} of its registry is dispatched ({@link #flush}) -- the one moment that registry is writable. The legacy
 * registry views the shims hand to a mod ({@code ForgeRegistries}, {@code Item.REGISTRY}, ...) keep answering from their own
 * maps, so a mod finds its own content while it loads, before the modern registry holds it.</p>
 */
public final class LegacyRegistrar {
    private static final Logger LOG = LoggerFactory.getLogger("LegacyConnector/Registry");

    /** Registrations waiting for their registry's event; one queue per registry, in the order they were made. */
    private static final Map<ResourceKey<? extends Registry<?>>, LinkedHashMap<ResourceLocation, Pending>> PENDING = new LinkedHashMap<>();

    /** The registry whose {@code RegisterEvent} is being dispatched right now: it is the only one that can be written. */
    private static ResourceKey<? extends Registry<?>> open;

    private LegacyRegistrar() {}

    /** One queued registration: the registry object (a {@link Registry} or an {@link IForgeRegistry}), the id and the value. */
    private record Pending(Object registry, ResourceLocation id, Object value) {
        void insert() {
            if (registry instanceof Registry<?> vanilla) {
                @SuppressWarnings("unchecked")
                Registry<Object> typed = (Registry<Object>) vanilla;
                put(typed, id, value);
            } else if (registry instanceof IForgeRegistry<?> forge) {
                @SuppressWarnings("unchecked")
                IForgeRegistry<Object> typed = (IForgeRegistry<Object>) forge;
                putForge(typed, id, value);
            }
        }
    }

    /** Forge's own registries (fluid types, ...) are {@code IForgeRegistry}, not {@code Registry}. */
    public static <T> T register(IForgeRegistry<T> registry, ResourceLocation id, T value) {
        if (isOpen(registry.getRegistryKey())) return putForge(registry, id, value);
        if (registry.containsKey(id)) {
            LOG.warn("Duplicate legacy registration of {} in {}", id, registry.getRegistryName());
            return registry.getValue(id);
        }
        enqueue(registry.getRegistryKey(), registry, id, value);
        return value;
    }

    public static <T> T register(Registry<T> registry, ResourceLocation id, T value) {
        if (isOpen(registry.key())) return put(registry, id, value);
        if (registry.containsKey(id)) {
            // Legacy FML tolerated (and warned about) duplicate names; the modern registry would throw.
            LOG.warn("Duplicate legacy registration of {} in {}; keeping the first", id, registry.key().location());
            return registry.get(id);
        }
        enqueue(registry.key(), registry, id, value);
        return value;
    }

    /** Writes the queued registrations of one registry while its {@code RegisterEvent} is being dispatched. */
    public static void flush(ResourceKey<? extends Registry<?>> key) {
        LinkedHashMap<ResourceLocation, Pending> queued;
        synchronized (PENDING) {
            queued = PENDING.remove(key);
        }
        if (queued == null) return;
        open = key;
        try {
            for (Pending pending : queued.values()) {
                try {
                    pending.insert();
                } catch (RuntimeException e) {
                    LOG.error("Could not register {}", pending.id(), e);
                }
            }
        } finally {
            open = null;
        }
    }

    /** Registrations still queued once the registration phase is over: their registry never fired an event. */
    public static int discardPending() {
        synchronized (PENDING) {
            int count = 0;
            for (var queue : PENDING.values()) count += queue.size();
            if (count > 0) {
                PENDING.forEach((key, queue) -> LOG.warn("Dropped {} legacy registration(s) into {}: that registry was never opened",
                        queue.size(), key.location()));
                PENDING.clear();
            }
            return count;
        }
    }

    /**
     * A value queued under this id, for a shim whose lookup must see legacy content before the modern registry holds it. Returns
     * null when nothing is pending.
     */
    @SuppressWarnings("unchecked")
    public static <T> T find(ResourceKey<? extends Registry<?>> key, ResourceLocation id) {
        if (key == null || id == null) return null;
        synchronized (PENDING) {
            LinkedHashMap<ResourceLocation, Pending> queued = PENDING.get(key);
            if (queued == null) return null;
            Pending pending = queued.get(id);
            return pending == null ? null : (T) pending.value();
        }
    }

    private static <T> T put(Registry<T> registry, ResourceLocation id, T value) {
        if (registry.containsKey(id)) {
            LOG.warn("Duplicate legacy registration of {} in {}; keeping the first", id, registry.key().location());
            return registry.get(id);
        }
        if (!LegacyLifecycle.isRegistrationOpen() && registry instanceof net.minecraft.core.MappedRegistry<?> mapped && isFrozen(mapped)) {
            throw new IllegalStateException("Legacy mod registered " + id + " into " + registry.key().location()
                    + " after registries were frozen. Legacy registrations are only possible during preInit/init/postInit.");
        }
        return Registry.register(registry, id, value);
    }

    private static <T> T putForge(IForgeRegistry<T> registry, ResourceLocation id, T value) {
        if (registry.containsKey(id)) {
            LOG.warn("Duplicate legacy registration of {} in {}; keeping the first", id, registry.getRegistryName());
            return registry.getValue(id);
        }
        registry.register(id, value);
        return value;
    }

    private static void enqueue(ResourceKey<? extends Registry<?>> key, Object registry, ResourceLocation id, Object value) {
        if (key == null) {
            LOG.warn("Legacy registration of {} has no registry key; dropping it", id);
            return;
        }
        synchronized (PENDING) {
            PENDING.computeIfAbsent(key, k -> new LinkedHashMap<>()).putIfAbsent(id, new Pending(registry, id, value));
        }
    }

    private static boolean isOpen(ResourceKey<? extends Registry<?>> key) {
        return key != null && key.equals(open);
    }

    /**
     * Blocks/items a legacy mod constructed but never got registered (the mod failed half-way, or registered a duplicate name)
     * still own an "intrusive holder", and a frozen registry refuses to keep them. Drop the orphans that belong to legacy content
     * once legacy loading is over.
     */
    public static int discardOrphans() {
        int removed = 0;
        for (Registry<?> registry : net.minecraft.core.registries.BuiltInRegistries.REGISTRY) {
            if (!(registry instanceof net.minecraft.core.MappedRegistry<?> mapped)) continue;
            try {
                java.lang.reflect.Field f = org.kylepitcock.legacyconnector.core.Mirror.field(
                        net.minecraft.core.MappedRegistry.class, "unregisteredIntrusiveHolders");
                f.setAccessible(true);
                java.util.Map<?, ?> orphans = (java.util.Map<?, ?>) f.get(mapped);
                if (orphans == null) continue;
                var it = orphans.keySet().iterator();
                while (it.hasNext()) {
                    Object value = it.next();
                    if (isLegacyContent(value)) {
                        it.remove();
                        removed++;
                    }
                }
            } catch (ReflectiveOperationException | RuntimeException e) {
                LOG.debug("Cannot inspect {} for orphaned legacy entries", registry.key(), e);
            }
        }
        return removed;
    }

    private static boolean isLegacyContent(Object value) {
        String n = value.getClass().getName();
        return n.startsWith("org.kylepitcock.legacyconnector.") || n.startsWith("legacyconnector.") || n.startsWith("legacyconnector_synth.");
    }

    private static boolean isFrozen(net.minecraft.core.MappedRegistry<?> registry) {
        try {
            // the access transformer widens the field only at runtime, so it is read reflectively at compile time too
            java.lang.reflect.Field f = org.kylepitcock.legacyconnector.core.Mirror.field(
                    net.minecraft.core.MappedRegistry.class, "frozen");
            f.setAccessible(true);
            return f.getBoolean(registry);
        } catch (ReflectiveOperationException e) {
            return false;
        }
    }
}

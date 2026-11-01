package org.kylepitcock.legacyconnector.core;

import java.util.Optional;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.resources.ResourceLocation;

/**
 * Registry lookups by id.
 *
 * <p>1.20.2 added {@code Registry.getHolder(ResourceLocation)}; 1.20.1 only takes a {@link net.minecraft.resources.ResourceKey}, so the
 * value is looked up by id and wrapped.</p>
 */
public final class RegistryUtil {
    private RegistryUtil() {}

    public static <T> Optional<Holder<T>> holder(Registry<T> registry, ResourceLocation id) {
        if (registry == null || id == null) return Optional.empty();
        T value = registry.get(id);
        return value == null ? Optional.empty() : Optional.of(registry.wrapAsHolder(value));
    }

    public static <T> Holder<T> holderOrNull(Registry<T> registry, ResourceLocation id) {
        return holder(registry, id).orElse(null);
    }
}

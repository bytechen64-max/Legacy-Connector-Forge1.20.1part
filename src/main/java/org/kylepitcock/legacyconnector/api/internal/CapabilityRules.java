package org.kylepitcock.legacyconnector.api.internal;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.capabilities.ICapabilityProvider;
import net.minecraftforge.common.capabilities.RegisterCapabilitiesEvent;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.energy.IEnergyStorage;
import net.minecraftforge.event.AttachCapabilitiesEvent;
import net.minecraftforge.fluids.capability.IFluidHandler;
import net.minecraftforge.items.IItemHandler;
import org.kylepitcock.legacyconnector.api.LegacyApi;
import org.kylepitcock.legacyconnector.api.LegacyCapabilities;
import org.kylepitcock.legacyconnector.api.LegacyCapabilities.TileAdapter;
import org.kylepitcock.legacyconnector.v1_12_2.bridge.TileEntityBridge1122;
import org.kylepitcock.legacyconnector.v1_7_10.bridge.TileEntityBridge;

/**
 * The addons' capability rules, attached to the host block entities of both legacy versions.
 *
 * <p>NeoForge 1.21 registered a block capability per block entity type in {@code RegisterCapabilitiesEvent} and keyed rules by a
 * {@code BlockCapability}. Forge 1.20.1 has neither: {@code RegisterCapabilitiesEvent} only registers the capability
 * <em>interface</em>, and providers are attached to a block entity through {@code AttachCapabilitiesEvent}. So the rules are
 * keyed by the capability interface class, every legacy host block entity gets one provider that answers all of them (matched by
 * the capability's registered name), and the interfaces are registered before that provider can be asked.</p>
 */
public final class CapabilityRules implements LegacyCapabilities {
    private static final ResourceLocation NAME = new ResourceLocation("legacyconnector", "legacy_capabilities");

    private static final class Rule<T> {
        final String modId;
        final String className;
        final TileAdapter<T> adapter;
        private Class<?> resolved;
        private boolean tried;

        Rule(String modId, String className, TileAdapter<T> adapter) {
            this.modId = modId;
            this.className = className;
            this.adapter = adapter;
        }

        boolean matches(Object tile) {
            if (className == null) return true;
            if (!tried) {
                tried = true;
                resolved = LegacyApi.classOf(modId, className).orElse(null);
            }
            return resolved != null && resolved.isInstance(tile);
        }
    }

    /** Every rule, by capability interface, in the order they are asked (addons first, then the built-ins). */
    private static final Map<Class<?>, List<Rule<?>>> RULES = new LinkedHashMap<>();

    private final Map<Class<?>, List<Rule<?>>> rules = new LinkedHashMap<>();

    @Override
    public <T> void forTile(String modId, String tileClassName, Class<T> capability, TileAdapter<T> adapter) {
        rules.computeIfAbsent(capability, c -> new ArrayList<>()).add(new Rule<>(modId, tileClassName, adapter));
    }

    @Override
    public <T> void forAnyTile(Class<T> capability, TileAdapter<T> adapter) {
        rules.computeIfAbsent(capability, c -> new ArrayList<>()).add(new Rule<>(null, null, adapter));
    }

    /** Collects the addons' rules and the built-ins, registers the capabilities and attaches the host provider. */
    @SuppressWarnings({"unchecked", "rawtypes"})
    public static void apply(RegisterCapabilitiesEvent event) {
        CapabilityRules registrar = new CapabilityRules();
        // 1.12.2 tiles answering the Forge capabilities; the 1.7.10 ones come from the 1.7.10 bridges below
        registrar.forAnyTile(IItemHandler.class, LegacyCapabilities.FORGE_ITEMS_1122);
        registrar.forAnyTile(IFluidHandler.class, LegacyCapabilities.FORGE_FLUIDS_1122);
        registrar.forAnyTile(IEnergyStorage.class, LegacyCapabilities.FORGE_ENERGY_1122);
        registrar.forAnyTile(IItemHandler.class, LegacyCapabilities.INVENTORY_ITEMS);
        registrar.forAnyTile(IFluidHandler.class, LegacyCapabilities.FLUIDS_1710);
        registrar.forAnyTile(IEnergyStorage.class, LegacyCapabilities.RF_ENERGY);
        // addons first: their rules are asked before the built-ins of the same capability
        CapabilityRules addons = new CapabilityRules();
        AddonHost.registerCapabilities(addons);
        RULES.clear();
        addons.rules.forEach((cap, list) -> RULES.computeIfAbsent(cap, c -> new ArrayList<>()).addAll(list));
        registrar.rules.forEach((cap, list) -> RULES.computeIfAbsent(cap, c -> new ArrayList<>()).addAll(list));
        // The capability interfaces must exist before a provider can be asked for them. Forge registers its own interfaces (item
        // handlers, fluid handlers, energy) itself, before the mods are asked, so those are already there.
        for (Class<?> capability : RULES.keySet()) {
            try {
                event.register((Class) capability);
            } catch (IllegalArgumentException alreadyRegistered) {
                org.slf4j.LoggerFactory.getLogger("LegacyConnector/Capabilities")
                        .debug("Capability {} is registered by Forge already", capability.getName());
            }
        }
        MinecraftForge.EVENT_BUS.addGenericListener(BlockEntity.class, CapabilityRules::attach);
    }

    /** Adds the one provider that answers every rule to a legacy host block entity. */
    private static void attach(AttachCapabilitiesEvent<BlockEntity> event) {
        BlockEntity host = event.getObject();
        var type = host.getType();
        if (type != TileEntityBridge.type() && type != TileEntityBridge1122.type()) return;
        var tile = Convert.tileOf(host).orElse(null);
        if (tile == null) return;
        event.addCapability(NAME, new HostProvider(tile, host));
    }

    /** Answers capability queries for one hosted legacy tile entity. */
    @SuppressWarnings({"unchecked", "rawtypes"})
    private record HostProvider(Object tile, BlockEntity host) implements ICapabilityProvider {
        @Override
        public <R> LazyOptional<R> getCapability(Capability<R> capability, Direction side) {
            if (capability == null) return LazyOptional.empty();
            for (var entry : RULES.entrySet()) {
                // rules are keyed by the capability's interface; Forge names a capability after that interface
                if (!entry.getKey().getName().equals(capability.getName())) continue;
                for (Rule<?> rule : entry.getValue()) {
                    if (!rule.matches(tile)) continue;
                    R value = (R) ((TileAdapter) rule.adapter).adapt(tile, side, host);
                    if (value != null) return LazyOptional.of(() -> value);
                }
            }
            return LazyOptional.empty();
        }
    }
}

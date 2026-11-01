package org.kylepitcock.legacyconnector.api.internal;

import java.util.ArrayList;
import java.util.List;
import java.util.function.BiFunction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.capabilities.ICapabilityProvider;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.event.AttachCapabilitiesEvent;

/**
 * Item capabilities on Forge 1.20.1.
 *
 * <p>NeoForge 1.21 registered them per item in {@code RegisterCapabilitiesEvent.registerItem}. Forge 1.20.1 attaches an
 * {@code ICapabilityProvider} to the stack instead ({@code AttachCapabilitiesEvent<ItemStack>}, or {@code Item#initCapabilities});
 * this helper does the former for a list of modern items that stand for a legacy item's subtypes, which is exactly the shape the
 * bridges need.</p>
 */
public final class ItemCapabilities {
    private static final ResourceLocation NAME = new ResourceLocation("legacyconnector", "legacy_item_capabilities");
    private static boolean listening;

    private ItemCapabilities() {}

    /**
     * Attaches {@code factory}'s capability to every stack of {@code items}.
     *
     * @param capability the capability interface (matched by Forge's capability name)
     * @param factory    builds the capability object for a stack, or null to provide none
     */
    public static <T> void attach(Class<T> capability, BiFunction<ItemStack, Object, T> factory, Item... items) {
        if (capability == null || factory == null || items == null || items.length == 0) return;
        var wanted = java.util.Set.of(items);
        String name = capability.getName();
        startListening();
        MinecraftForge.EVENT_BUS.addGenericListener(ItemStack.class, (AttachCapabilitiesEvent<ItemStack> event) -> {
            ItemStack stack = event.getObject();
            if (stack == null || stack.isEmpty() || !wanted.contains(stack.getItem())) return;
            event.addCapability(NAME, new Provider<>(name, factory, stack));
        });
    }

    private static synchronized void startListening() {
        listening = true;
    }

    private record Provider<T>(String capabilityName, BiFunction<ItemStack, Object, T> factory, ItemStack stack) implements ICapabilityProvider {
        @Override
        public <R> LazyOptional<R> getCapability(Capability<R> capability, net.minecraft.core.Direction side) {
            if (capability == null || !capability.getName().equals(capabilityName)) return LazyOptional.empty();
            T value = factory.apply(stack, null);
            return value == null ? LazyOptional.empty() : LazyOptional.of(() -> value);
        }
    }
}

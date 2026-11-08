package org.kylepitcock.legacyconnector.v1_12_2.entity;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import legacyconnector.v1_12_2.net.minecraft.entity.EntityLivingBase;
import legacyconnector.v1_12_2.net.minecraft.potion.Potion;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import org.kylepitcock.legacyconnector.core.Ids;
import org.kylepitcock.legacyconnector.core.registry.LegacyRegistrar;
import org.kylepitcock.legacyconnector.v1_12_2.bridge.EntityBridge1122;
import org.slf4j.LoggerFactory;

/**
 * Mods' 1.12.2 potions as modern mob effects. Each potion a mod registers gets a {@link LegacyEffect}: the modern game ticks it and calls
 * the legacy {@code isReady}/{@code performEffect}, instant ones {@code affectEntity}, and applies the attribute modifiers the potion
 * registered. (Before, mod potions had no modern effect: adding one to an entity did nothing.)
 */
public final class Effects1122 {
    private static final Map<Potion, Holder<MobEffect>> EFFECTS = new ConcurrentHashMap<>();

    private Effects1122() {}

    /** A potion was registered: makes and registers its modern effect (vanilla potions are the modern ones already). */
    public static void register(Potion potion) {
        if (potion == null || potion.getRegistryName() == null || EFFECTS.containsKey(potion)) return;
        var name = potion.getRegistryName();
        if ("minecraft".equals(name.getNamespace())) return;
        try {
            ResourceLocation id = ResourceLocation.fromNamespaceAndPath(Ids.modernModId(name.getNamespace()), Ids.normalizePath(name.getPath()).replace('/', '_'));
            LegacyEffect effect = new LegacyEffect(potion);
            for (var e : potion.getAttributeModifierMap().entrySet()) {
                var attribute = e.getKey().mcc$modern();
                if (attribute == null) continue;
                var mod = e.getValue();
                var operation = switch (mod.getOperation()) {
                    case 1 -> net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation.MULTIPLY_BASE;
                    case 2 -> net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation.MULTIPLY_TOTAL;
                    default -> net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation.ADDITION;
                };
                // 1.20.1 wants the modifier's UUID as the name (1.20.5 takes a ResourceLocation); the legacy modifier already has one
                effect.addAttributeModifier(attribute, mod.getID().toString(), mod.getAmount(), operation);
            }
            MobEffect registered = LegacyRegistrar.register(BuiltInRegistries.MOB_EFFECT, id, effect);
            org.kylepitcock.legacyconnector.core.RegistryUtil.holder(BuiltInRegistries.MOB_EFFECT, BuiltInRegistries.MOB_EFFECT.getKey(registered)).ifPresent(h -> EFFECTS.put(potion, h));
        } catch (RuntimeException | LinkageError e) {
            LoggerFactory.getLogger("LegacyConnector/Potions").warn("Potion {} could not become a modern effect: {}", name, e.toString());
        }
    }

    /**
     * The modern effect of a mod potion, or null. The registration is deferred (a legacy mod registers during its loading step,
     * while the effect registry is only written during the registry event), so the holder is looked up in the registry the first
     * time it is asked for: the eager lookup right after registering found nothing and the icon pass saw no mod effects at all.
     */
    public static Holder<MobEffect> holder(Potion potion) {
        if (potion == null) return null;
        Holder<MobEffect> known = EFFECTS.get(potion);
        if (known != null) return known;
        for (var effect : BuiltInRegistries.MOB_EFFECT) {
            if (effect instanceof LegacyEffect legacy && legacy.potion == potion) {
                var id = BuiltInRegistries.MOB_EFFECT.getResourceKey(effect);
                if (id.isEmpty()) return null;
                Holder<MobEffect> holder = BuiltInRegistries.MOB_EFFECT.getHolder(id.get()).orElse(null);
                if (holder == null) return null;
                EFFECTS.putIfAbsent(potion, holder);
                return holder;
            }
        }
        return null;
    }

    /** The modern effects made for mod potions (their client icons are drawn by EffectIcons1122). */
    public static java.util.List<MobEffect> all() {
        java.util.List<MobEffect> out = new java.util.ArrayList<>();
        // the registry is the truth: a deferred registration may have happened after EFFECTS was written
        for (var effect : BuiltInRegistries.MOB_EFFECT) if (effect instanceof LegacyEffect) out.add(effect);
        return out;
    }

    /** The legacy potion of a modern effect made here, or null. */
    public static Potion legacy(MobEffect effect) {
        return effect instanceof LegacyEffect l ? l.potion : null;
    }

    /** A modern effect that runs a legacy potion. */
    public static final class LegacyEffect extends MobEffect {
        final Potion potion;

        @Override
        public void initializeClient(java.util.function.Consumer<net.minecraftforge.client.extensions.common.IClientMobEffectExtensions> consumer) {
            consumer.accept(org.kylepitcock.legacyconnector.v1_12_2.client.EffectIcons1122.EXTENSION);
        }

        LegacyEffect(Potion potion) {
            super(potion.isBadEffect() ? MobEffectCategory.HARMFUL : potion.isBeneficial() ? MobEffectCategory.BENEFICIAL : MobEffectCategory.NEUTRAL,
                    potion.getLiquidColor());
            this.potion = potion;
        }

        private static EntityLivingBase view(net.minecraft.world.entity.LivingEntity entity) {
            return EntityBridge1122.wrap(entity) instanceof EntityLivingBase l ? l : null;
        }

        @Override
        public void applyEffectTick(net.minecraft.world.entity.LivingEntity entity, int amplifier) {
            // 1.20.1's tick hook returns nothing (1.20.5 made the return value meaningful).
            EntityLivingBase target = view(entity);
            if (target == null) return;
            try {
                potion.performEffect(target, amplifier);
            } catch (RuntimeException | LinkageError e) {
                Hosts1122.failed(potion.getClass(), "performEffect", e);
            }
        }

        @Override
        public boolean isDurationEffectTick(int duration, int amplifier) {
            try {
                return potion.isReady(duration, amplifier);
            } catch (RuntimeException | LinkageError e) {
                return false;
            }
        }

        @Override
        public void applyInstantenousEffect(net.minecraft.world.entity.Entity source, net.minecraft.world.entity.Entity indirect,
                net.minecraft.world.entity.LivingEntity entity, int amplifier, double health) {
            EntityLivingBase target = view(entity);
            if (target == null) return;
            try {
                potion.affectEntity(EntityBridge1122.wrap(source), EntityBridge1122.wrap(indirect), target, amplifier, health);
            } catch (RuntimeException | LinkageError e) {
                Hosts1122.failed(potion.getClass(), "affectEntity", e);
            }
        }

        @Override
        public boolean isInstantenous() {
            return potion.isInstant();
        }

        @Override
        public String getDescriptionId() {
            String name = potion.getName();
            return name == null || name.isEmpty() ? super.getDescriptionId() : name;
        }
    }
}

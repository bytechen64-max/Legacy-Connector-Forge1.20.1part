package org.kylepitcock.legacyconnector.v1_7_10.bridge;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import legacyconnector.v1_7_10.net.minecraft.entity.EntityLivingBase;
import legacyconnector.v1_7_10.net.minecraft.potion.Potion;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import org.kylepitcock.legacyconnector.core.registry.LegacyRegistrar;
import org.kylepitcock.legacyconnector.v1_7_10.LegacyModContainer1710;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/** Legacy numeric potion ids <-> modern mob effects. Mod potions become modern effects driven by the legacy class. */
public final class PotionBridge {
    private static final Logger LOG = LoggerFactory.getLogger("LegacyConnector/Potions");
    private static final java.util.List<MobEffect> BY_ID = java.util.Arrays.asList(
            null, MobEffects.MOVEMENT_SPEED, MobEffects.MOVEMENT_SLOWDOWN, MobEffects.DIG_SPEED, MobEffects.DIG_SLOWDOWN, MobEffects.DAMAGE_BOOST,
            MobEffects.HEAL, MobEffects.HARM, MobEffects.JUMP, MobEffects.CONFUSION, MobEffects.REGENERATION, MobEffects.DAMAGE_RESISTANCE,
            MobEffects.FIRE_RESISTANCE, MobEffects.WATER_BREATHING, MobEffects.INVISIBILITY, MobEffects.BLINDNESS, MobEffects.NIGHT_VISION,
            MobEffects.HUNGER, MobEffects.WEAKNESS, MobEffects.POISON, MobEffects.WITHER, MobEffects.HEALTH_BOOST, MobEffects.ABSORPTION,
            MobEffects.SATURATION);
    private static final Map<Integer, Holder<MobEffect>> CUSTOM = new ConcurrentHashMap<>();

    private PotionBridge() {}

    public static boolean isVanilla(int id) {
        return id > 0 && id < BY_ID.size();
    }

    /** Called from the legacy Potion constructor for every non-vanilla id. */
    public static void registerLegacy(Potion potion) {
        LegacyModContainer1710 owner = LegacyModContainer1710.active();
        String ns = owner == null ? "legacyconnector" : owner.record().modernId;
        ResourceLocation id = ResourceLocation.fromNamespaceAndPath(ns, "legacy_potion_" + potion.id);
        try {
            MobEffect effect = LegacyRegistrar.register(BuiltInRegistries.MOB_EFFECT, id, new LegacyMobEffect(potion));
            CUSTOM.put(potion.id, BuiltInRegistries.MOB_EFFECT.wrapAsHolder(effect));
        } catch (RuntimeException e) {
            LOG.warn("Could not register legacy potion {} ({}) as a modern effect: {}", potion.id, potion.getClass().getName(), e.toString());
        }
    }

    public static Holder<MobEffect> effect(int id) {
        if (isVanilla(id)) return holder(BY_ID.get(id));
        Holder<MobEffect> h = CUSTOM.get(id);
        if (h == null) throw new IllegalArgumentException("Unknown legacy potion id " + id);
        return h;
    }

    public static Holder<MobEffect> effectOrNull(int id) {
        return isVanilla(id) ? holder(BY_ID.get(id)) : CUSTOM.get(id);
    }

    /** 1.20.1 declares its effects as plain {@code MobEffect}s (the {@code Holder} constants came in 1.20.5); the rest of this class speaks {@code Holder}. */
    private static Holder<MobEffect> holder(MobEffect effect) {
        return BuiltInRegistries.MOB_EFFECT.wrapAsHolder(effect);
    }

    /** The modern effects of mod potions (the client draws their icons, see LegacyEffectIcons). */
    public static java.util.List<MobEffect> legacyEffects() {
        java.util.List<MobEffect> out = new java.util.ArrayList<>();
        for (Holder<MobEffect> h : CUSTOM.values()) out.add(h.value());
        return out;
    }

    /** The legacy potion behind a modern effect of a mod potion, or null. */
    public static Potion legacyOf(MobEffect effect) {
        return effect instanceof LegacyMobEffect l ? l.potion : null;
    }

    /** The modern effect of a vanilla potion whose 1.7.10 status icon had this index, or null. */
    public static Holder<MobEffect> vanillaWithIcon(int iconIndex) {
        for (int i = 1; i < BY_ID.size(); i++) {
            Potion p = Potion.potionTypes[i];
            if (p != null && p.getStatusIconIndex() == iconIndex) return holder(BY_ID.get(i));
        }
        return null;
    }

    /** Legacy id of a modern effect, or -1. */
    public static int idOf(Holder<MobEffect> effect) {
        for (int i = 1; i < BY_ID.size(); i++) if (BY_ID.get(i) != null && BY_ID.get(i) == effect.value()) return i;
        for (var e : CUSTOM.entrySet()) if (e.getValue().equals(effect)) return e.getKey();
        return -1;
    }

    public static boolean isActive(LivingEntity entity, int id) {
        Holder<MobEffect> h = effectOrNull(id);
        return h != null && entity.hasEffect(h.value());
    }

    public static void remove(LivingEntity entity, int id) {
        Holder<MobEffect> h = effectOrNull(id);
        if (h != null) entity.removeEffect(h.value());
    }

    /** A mod potion's attribute modifier on a vanilla attribute, applied by its modern effect while active (amount x (amplifier + 1)). */
    public static void addModifier(Potion potion, legacyconnector.v1_7_10.net.minecraft.entity.ai.attributes.IAttribute attribute,
            legacyconnector.v1_7_10.net.minecraft.entity.ai.attributes.AttributeModifier modifier) {
        Holder<MobEffect> effect = CUSTOM.get(potion.id);
        var target = legacyconnector.v1_7_10.net.minecraft.entity.SharedMonsterAttributes.mcc$modern(attribute);
        if (effect == null || target == null) return;
        var op = switch (modifier.getOperation()) {
            case 1 -> net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation.MULTIPLY_BASE;
            case 2 -> net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation.MULTIPLY_TOTAL;
            default -> net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation.ADDITION;
        };
        ResourceLocation key = ResourceLocation.fromNamespaceAndPath("legacyconnector", "potion_" + potion.id + "_" + modifier.getID());
        try {
            effect.value().addAttributeModifier(target, key.toString(), modifier.getAmount(), op);
        } catch (RuntimeException e) {
            LOG.debug("Could not add attribute modifier of legacy potion {}", potion, e);
        }
    }

    /** A legacy mod potion as a modern effect: ticking defers to the legacy isReady/performEffect. */
    static final class LegacyMobEffect extends MobEffect {
        private final Potion potion;

        LegacyMobEffect(Potion potion) {
            super(potion.isBadEffect() ? MobEffectCategory.HARMFUL : MobEffectCategory.BENEFICIAL, potion.getLiquidColor());
            this.potion = potion;
        }

        /**
         * The legacy status icon. Forge calls this from the effect's constructor on a physical client (1.20.1's replacement for
         * the client-extension registration event), so the icon renderer only has to look the potion up when it draws.
         */
        @Override
        public void initializeClient(java.util.function.Consumer<net.minecraftforge.client.extensions.common.IClientMobEffectExtensions> consumer) {
            org.kylepitcock.legacyconnector.v1_7_10.client.LegacyEffectIcons.install(consumer);
        }

        /** The 1.7.10 name key ({@code potion.<name>}, from the mod's lang), set after the potion was constructed. */
        @Override
        public String getDescriptionId() {
            String name = potion.getName();
            return name == null || name.isEmpty() ? super.getDescriptionId() : name;
        }

        @Override
        public boolean isDurationEffectTick(int duration, int amplifier) {
            try {
                return potion.isReady(duration, amplifier);
            } catch (RuntimeException e) {
                return false;
            }
        }

        @Override
        public void applyEffectTick(LivingEntity entity, int amplifier) {
            try {
                if (EntityBridge.wrap(entity) instanceof EntityLivingBase living) potion.performEffect(living, amplifier);
            } catch (RuntimeException e) {
                LOG.debug("Legacy potion {} failed", potion, e);
            }
        }

        @Override
        public boolean isInstantenous() {
            return potion.isInstant();
        }
    }
}

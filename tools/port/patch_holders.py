"""1.20.1 has plain potion and effect objects: PotionData and the effect lookups drop their holders."""
import sys

EDITS = {
    # ---- PotionData: Optional<Potion> instead of Optional<Holder<Potion>>
    r"src/main/java/org/kylepitcock/legacyconnector/core/data/PotionData.java": [
        ("public record PotionData(Optional<Holder<Potion>> potion, Optional<Integer> customColor, List<MobEffectInstance> customEffects) {",
         "public record PotionData(Optional<Potion> potion, Optional<Integer> customColor, List<MobEffectInstance> customEffects) {"),
        ("""    public static PotionData of(Holder<Potion> potion) {
        return new PotionData(Optional.ofNullable(potion), Optional.empty(), List.of());
    }

    public static PotionData of(Potion potion) {
        return of(potion == null ? null : BuiltInRegistries.POTION.wrapAsHolder(potion));
    }""",
         """    public static PotionData of(Potion potion) {
        return new PotionData(Optional.ofNullable(potion), Optional.empty(), List.of());
    }

    /** For callers that still hold the potion through a holder (the 1.21 shape). */
    public static PotionData of(Holder<Potion> potion) {
        return of(potion == null ? null : potion.value());
    }"""),
        ("""        Potion potion = PotionUtils.getPotion(stack);
        Optional<Holder<Potion>> holder = hasPotion && potion != null
                ? Optional.of(BuiltInRegistries.POTION.wrapAsHolder(potion)) : Optional.empty();""",
         """        Potion potion = PotionUtils.getPotion(stack);
        Optional<Potion> holder = hasPotion && potion != null ? Optional.of(potion) : Optional.empty();"""),
        ("        potion.ifPresent(h -> PotionUtils.setPotion(stack, h.value()));",
         "        potion.ifPresent(p -> PotionUtils.setPotion(stack, p));"),
        ("        potion.ifPresent(h -> out.addAll(PotionUtils.getAllEffects(h.value(), List.of())));",
         "        potion.ifPresent(p -> out.addAll(PotionUtils.getAllEffects(p, List.of())));"),
        ("""    public static ItemStack createItemStack(Item item, Holder<Potion> potion) {
        return createItemStack(item, potion == null ? null : potion.value());
    }

""", ""),
        ("""    public static String potionId(Holder<Potion> potion) {
        var key = potion == null ? null : potion.unwrapKey().orElse(null);
        return key == null ? null : key.location().toString();
    }""",
         """    public static String potionId(Potion potion) {
        var key = potion == null ? null : BuiltInRegistries.POTION.getKey(potion);
        return key == null ? null : key.toString();
    }"""),
    ],
    # ---- Stacks1122: the legacy tag holds an id, the modern side a potion object
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/bridge/Stacks1122.java": [
        ("""        java.util.Optional<net.minecraft.core.Holder<net.minecraft.world.item.alchemy.Potion>> potion = java.util.Optional.empty();
        if (data.contains("Potion", 8)) {
            var id = net.minecraft.resources.ResourceLocation.tryParse(data.getString("Potion"));
            var holder = id == null ? java.util.Optional.<net.minecraft.core.Holder.Reference<net.minecraft.world.item.alchemy.Potion>>empty()
                    : net.minecraft.core.registries.BuiltInRegistries.POTION.getHolder(id);
            if (holder.isPresent()) {
                potion = java.util.Optional.of(holder.get());
                data.remove("Potion");
            }
        }""",
         """        java.util.Optional<net.minecraft.world.item.alchemy.Potion> potion = java.util.Optional.empty();
        if (data.contains("Potion", 8)) {
            // 1.20.1 holds the potion itself; the 1.21 holder is looked up by id.
            var id = net.minecraft.resources.ResourceLocation.tryParse(data.getString("Potion"));
            var found = id == null ? null : net.minecraft.core.registries.BuiltInRegistries.POTION.get(id);
            if (found != null) {
                potion = java.util.Optional.of(found);
                data.remove("Potion");
            }
        }"""),
        ("        contents.potion().flatMap(net.minecraft.core.Holder::unwrapKey).ifPresent(k -> tag.setString(\"Potion\", k.location().toString()));",
         """        contents.potion().ifPresent(p -> {
            var key = net.minecraft.core.registries.BuiltInRegistries.POTION.getKey(p);
            if (key != null) tag.setString("Potion", key.toString());
        });"""),
    ],
    # ---- Brewing1710: the vanilla table maps values to potions, not holders
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/Brewing1710.java": [
        ("    private static final Map<Integer, Holder<Potion>> VANILLA = new HashMap<>();\n"
         "    private static final Map<Holder<Potion>, Integer> VALUE = new HashMap<>();",
         "    private static final Map<Integer, Potion> VANILLA = new HashMap<>();\n"
         "    private static final Map<Potion, Integer> VALUE = new HashMap<>();"),
        ("    private static void put(int value, Holder<Potion> potion) {",
         "    private static void put(int value, Potion potion) {"),
        ("        Holder<Potion> vanilla = VANILLA.get(plain);", "        Potion vanilla = VANILLA.get(plain);"),
    ],
    # ---- effect lookups: 1.20.1 API takes the effect itself
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/potion/PotionEffect.java": [
        ("        return modern == null ? null : new net.minecraft.world.effect.MobEffectInstance(modern, duration, amplifier, isAmbient, showParticles);",
         "        return modern == null ? null : new net.minecraft.world.effect.MobEffectInstance(modern.value(), duration, amplifier, isAmbient, showParticles);"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/network/play/server/SPacketRemoveEntityEffect.java": [
        ("        return modern == null ? null : new net.minecraft.network.protocol.game.ClientboundRemoveMobEffectPacket(entityId, modern);",
         "        return modern == null ? null : new net.minecraft.network.protocol.game.ClientboundRemoveMobEffectPacket(entityId, modern.value());"),
    ],
    r"src/main/java/legacyconnector/v1_7_10/net/minecraft/entity/EntityLivingBase.java": [
        ("        var modern = holder == null ? null : mcc$living().getEffect(holder);",
         "        var modern = holder == null ? null : mcc$living().getEffect(holder.value());"),
    ],
    r"src/main/java/legacyconnector/v1_7_10/net/minecraft/potion/PotionEffect.java": [
        ("        MobEffectInstance instance = new MobEffectInstance(PotionBridge.effect(potionID), duration, amplifier, isAmbient, true);",
         "        var effect = PotionBridge.effect(potionID);\n"
         "        MobEffectInstance instance = new MobEffectInstance(effect == null ? null : effect.value(), duration, amplifier, isAmbient, true);"),
        ("        if (holder == null || !owner.hasEffect(holder)) return;",
         "        if (holder == null || !owner.hasEffect(holder.value())) return;"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/Brewing1710.java_x": [],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/PotionBridge.java": [
        ("        return h != null && entity.hasEffect(h);", "        return h != null && entity.hasEffect(h.value());"),
        ("        if (h != null) entity.removeEffect(h);", "        if (h != null) entity.removeEffect(h.value());"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/client/EffectIcons1122.java": [
        ("        if (vanilla != null) graphics.blit(x, y, 0, 18, 18, net.minecraft.client.Minecraft.getInstance().getMobEffectTextures().get(vanilla));",
         "        if (vanilla != null) graphics.blit(x, y, 0, 18, 18, net.minecraft.client.Minecraft.getInstance().getMobEffectTextures().get(vanilla.value()));"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/LegacyEffectIcons.java": [
        ("        if (vanilla != null) graphics.blit(x, y, 0, 18, 18, Minecraft.getInstance().getMobEffectTextures().get(vanilla));",
         "        if (vanilla != null) graphics.blit(x, y, 0, 18, 18, Minecraft.getInstance().getMobEffectTextures().get(vanilla.value()));"),
    ],
}

for path, pairs in EDITS.items():
    if not pairs:
        continue
    src = open(path, encoding="utf-8").read()
    for old, new in pairs:
        n = src.count(old)
        if n != 1:
            print(f"ABORT {n} matches in {path}: {old.strip()[:70]}")
            sys.exit(1)
        src = src.replace(old, new)
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

# Brewing1710 builds effects from holders too
P = r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/Brewing1710.java"
src = open(P, encoding="utf-8").read()
old = "            effects.add(new MobEffectInstance(effect, e.getDuration(), e.getAmplifier()));"
if src.count(old) != 1:
    print("ABORT Brewing1710 effect:", src.count(old))
    sys.exit(1)
src = src.replace(old, "            effects.add(new MobEffectInstance(effect.value(), e.getDuration(), e.getAmplifier()));")
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P, "(effect)")

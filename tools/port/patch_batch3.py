"""A batch of 1.21 -> 1.20.1 mappings: enchantment names, explosion radius, attribute ids, fireball acceleration."""
import sys

EDITS = {
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/DispenserBridge.java": [
        ("import net.minecraft.core.dispenser.BlockSource;", "import net.minecraft.core.BlockSource;"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/EventBridge1710.java": [
        ("import net.minecraftforge.event.tick.EntityTickEvent;\n", ""),
        ("        gameBus.addListener((EntityTickEvent.Pre e) -> {\n"
         "            if (!(e.getEntity() instanceof LivingEntity l) || !wants(forge(), LivingEvent.LivingUpdateEvent.class)) return;",
         "        // 1.20.1 has no all-entity tick event; this listener only cares about living entities anyway.\n"
         "        gameBus.addListener((net.minecraftforge.event.entity.living.LivingEvent.LivingTickEvent e) -> {\n"
         "            if (!(e.getEntity() instanceof LivingEntity l) || !wants(forge(), LivingEvent.LivingUpdateEvent.class)) return;"),
        ("    private static void specialArmor(LivingIncomingDamageEvent e) {",
         "    private static void specialArmor(net.minecraftforge.event.entity.living.LivingHurtEvent e) {"),
    ],
    r"src/main/java/legacyconnector/v1_7_10/net/minecraft/potion/PotionEffect.java": [
        ("import net.minecraftforge.common.EffectCure;\n", ""),
        ("import net.minecraftforge.common.EffectCures;\n", ""),
        ("""    /** The modern cure an item stands for: milk for the milk bucket, otherwise one per item. */
    public static EffectCure mcc$cureFor(ItemStack stack) {
        if (stack == null || stack.getItem() == null) return null;
        if (stack.getItem() == legacyconnector.v1_7_10.net.minecraft.init.Items.milk_bucket) return EffectCures.MILK;
        var key = net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(stack.mcc$modern().getItem());
        return EffectCure.get("legacyconnector:item/" + key);
    }

""",
         """    /**
     * 1.20.1 has no cure registry: milk is hardwired in {@code MilkBucketItem} and everything else is the shim's own list, so
     * nothing is returned for the modern side.
     */
    public static Object mcc$cureFor(ItemStack stack) {
        return null;
    }

"""),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/adapter/LegacyItemAdapter.java": [
        ("    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {",
         "    public void appendHoverText(ItemStack stack, Level level, List<Component> tooltip, TooltipFlag flag) {"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/world/Explosion.java": [
        ("        this(world, entity, modern.getPosition().x, modern.getPosition().y, modern.getPosition().z, modern.radius(), false,",
         "        this(world, entity, modern.getPosition().x, modern.getPosition().y, modern.getPosition().z, modern.radius, false,"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/entity/projectile/EntityArrow.java": [
        ("enchantments.getOrThrow(net.minecraft.world.item.enchantment.Enchantments.POWER), living);",
         "enchantments.getOrThrow(net.minecraft.world.item.enchantment.Enchantments.POWER_ARROWS), living);"),
        ("enchantments.getOrThrow(net.minecraft.world.item.enchantment.Enchantments.PUNCH), living);",
         "enchantments.getOrThrow(net.minecraft.world.item.enchantment.Enchantments.PUNCH_ARROWS), living);"),
        ("enchantments.getOrThrow(net.minecraft.world.item.enchantment.Enchantments.FLAME), living);",
         "enchantments.getOrThrow(net.minecraft.world.item.enchantment.Enchantments.FLAMING_ARROWS), living);"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/entity/ai/attributes/AttributeModifier.java": [
        ("        return new net.minecraft.world.entity.ai.attributes.AttributeModifier(net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(\"legacyconnector\",\n"
         "                \"modifier/\" + id), amount, op);",
         "        // 1.20.1 names modifiers with a string (1.20.5 switched to a ResourceLocation).\n"
         "        return new net.minecraft.world.entity.ai.attributes.AttributeModifier(\"legacyconnector:modifier/\" + id, amount, op);"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/entity/player/EntityPlayer.java": [
        ("        mcc$player().disableShield();", "        mcc$player().disableShield(true);"),
        ("        sp.awardRecipesByKey(ids);", "        sp.awardRecipesByKey(ids.toArray(new net.minecraft.resources.ResourceLocation[0]));"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/entity/projectile/EntityFireball.java": [
        ("            m.accelerationPower = 0.1D;",
         "            // 1.20.1 stores the acceleration as a vector (xPower/yPower/zPower); 1.20.5 as one power along the motion.\n"
         "            var d = m.getDeltaMovement();\n"
         "            if (d.lengthSqr() > 1.0E-7D) {\n"
         "                var u = d.normalize().scale(0.1D);\n"
         "                m.xPower = u.x;\n"
         "                m.yPower = u.y;\n"
         "                m.zPower = u.z;\n"
         "            }"),
        ("        return v.lengthSqr() < 1.0E-7D ? net.minecraft.world.phys.Vec3.ZERO : v.normalize().scale(m.accelerationPower);",
         "        return new net.minecraft.world.phys.Vec3(m.xPower, m.yPower, m.zPower);"),
        ("        m.accelerationPower = len;",
         "        m.xPower = mcc$ax;\n"
         "        m.yPower = mcc$ay;\n"
         "        m.zPower = mcc$az;"),
    ],
}

for path, pairs in EDITS.items():
    src = open(path, encoding="utf-8").read()
    for old, new in pairs:
        n = src.count(old)
        if n != 1:
            print(f"ABORT {n} matches in {path}: {old.splitlines()[0][:70]!r}")
            sys.exit(1)
        src = src.replace(old, new)
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

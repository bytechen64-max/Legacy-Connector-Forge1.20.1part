package org.kylepitcock.legacyconnector.v1_12_2.bridge;

import org.kylepitcock.legacyconnector.core.synth.Synth;

/** Implementations of vanilla particle factories whose nested classes are synthesized. */
public final class ParticleFactories1122 {
    private ParticleFactories1122() {}
    private static final String[] FACTORIES = {
        "Barrier$Factory=35", "ParticleFootStep$Factory=28",
        "ParticleExplosion$Factory=0", "ParticleExplosionLarge$Factory=1", "ParticleExplosionHuge$Factory=2",
        "ParticleFirework$Factory=3", "ParticleBubble$Factory=4", "ParticleSplash$Factory=5", "ParticleWaterWake$Factory=6",
        "ParticleSuspend$Factory=7", "ParticleSuspendedTown$Factory=22", "ParticleCrit$Factory=9", "ParticleCrit$MagicFactory=10",
        "ParticleCrit$DamageIndicatorFactory=44", "ParticleSmokeNormal$Factory=11", "ParticleSmokeLarge$Factory=12",
        "ParticleSpell$Factory=13", "ParticleSpell$InstantFactory=14", "ParticleSpell$MobFactory=15",
        "ParticleSpell$AmbientMobFactory=16", "ParticleSpell$WitchFactory=17", "ParticleDrip$WaterFactory=18",
        "ParticleDrip$LavaFactory=19", "ParticleHeart$AngryVillagerFactory=20", "ParticleSuspendedTown$HappyVillagerFactory=21",
        "ParticleNote$Factory=23", "ParticlePortal$Factory=24", "ParticleEnchantmentTable$EnchantmentTable=25",
        "ParticleFlame$Factory=26", "ParticleLava$Factory=27", "ParticleCloud$Factory=29", "ParticleRedstone$Factory=30",
        "ParticleBreaking$SnowballFactory=31", "ParticleSnowShovel$Factory=32", "ParticleBreaking$SlimeFactory=33",
        "ParticleHeart$Factory=34", "ParticleBreaking$Factory=36", "ParticleDigging$Factory=37", "ParticleBlockDust$Factory=38",
        "ParticleRain$Factory=39", "ParticleMobAppearance$Factory=41", "ParticleDragonBreath$Factory=42",
        "ParticleEndRod$Factory=43", "ParticleSweepAttack$Factory=45", "ParticleFallingDust$Factory=46",
        "ParticleTotem$Factory=47", "ParticleSpit$Factory=48"
    };
    public static void register() {
        for (String entry : FACTORIES) {
            int split = entry.indexOf('=');
            int id = Integer.parseInt(entry.substring(split + 1));
            Synth.addInstanceMethod("net.minecraft.client.particle." + entry.substring(0, split) + ".createParticle", (self, args) -> {
                if (args.length != 9) return Synth.NONE;
                if (id == 28) return new legacyconnector.v1_12_2.net.minecraft.client.particle.ParticleFootStep(null,
                        (legacyconnector.v1_12_2.net.minecraft.world.World) args[1],
                        Synth.toDouble(args[2]), Synth.toDouble(args[3]), Synth.toDouble(args[4]));
                return org.kylepitcock.legacyconnector.v1_12_2.client.VanillaParticle1122.create(id,
                        (legacyconnector.v1_12_2.net.minecraft.world.World) args[1],
                        Synth.toDouble(args[2]), Synth.toDouble(args[3]), Synth.toDouble(args[4]),
                        Synth.toDouble(args[5]), Synth.toDouble(args[6]), Synth.toDouble(args[7]), (int[]) args[8]);
            });
        }
    }
}

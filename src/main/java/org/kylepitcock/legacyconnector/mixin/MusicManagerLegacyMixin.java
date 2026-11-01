package org.kylepitcock.legacyconnector.mixin;

import net.minecraft.client.sounds.MusicManager;
import net.minecraft.sounds.Music;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * A legacy mod that replaces {@code Minecraft.mcMusicTicker} owns the background music (Galacticraft's and GalaxySpace's space music).
 * NeoForge 1.21 has {@code SelectMusicEvent} to tell the modern manager to play nothing; 1.20.1 has no such hook, so the song the
 * manager picked is dropped here. The manager's own delay is pushed out at the same time, so it does not retry every tick.
 */
@Mixin(MusicManager.class)
public abstract class MusicManagerLegacyMixin {
    @Shadow private int nextSongDelay;

    @Inject(method = "startPlaying", at = @At("HEAD"), cancellable = true)
    private void legacyconnector$silenceWhileALegacyTickerOwnsMusic(Music music, CallbackInfo ci) {
        if (org.kylepitcock.legacyconnector.v1_7_10.client.LegacyMusic.ownsMusic()
                || org.kylepitcock.legacyconnector.v1_12_2.client.ClientEvents1122.ownsMusic()) {
            this.nextSongDelay = Integer.MAX_VALUE;
            ci.cancel();
        }
    }
}

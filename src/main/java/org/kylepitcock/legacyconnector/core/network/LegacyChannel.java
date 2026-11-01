package org.kylepitcock.legacyconnector.core.network;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.ChunkPos;
import net.minecraftforge.network.PacketDistributor;

/**
 * Sends legacy payloads to the audiences the bridges ask for.
 *
 * <p>NeoForge 1.21 had one {@code PacketDistributor.sendXxx(...)} overload per audience; Forge 1.20.1 routes every send
 * through a {@link PacketDistributor.PacketTarget} bound to a supplier, so each call site is one line here instead.</p>
 */
public final class LegacyChannel {
    private LegacyChannel() {}

    public static void sendToServer(LegacyPayload payload) {
        LegacyNetwork.channel().sendToServer(payload);
    }

    public static void sendToPlayer(ServerPlayer player, LegacyPayload payload) {
        LegacyNetwork.channel().send(PacketDistributor.PLAYER.with(() -> player), payload);
    }

    public static void sendToAllPlayers(LegacyPayload payload) {
        LegacyNetwork.channel().send(PacketDistributor.ALL.noArg(), payload);
    }

    public static void sendToPlayersInDimension(ServerLevel level, LegacyPayload payload) {
        LegacyNetwork.channel().send(PacketDistributor.DIMENSION.with(level::dimension), payload);
    }

    /** {@code except} may be null; Forge's {@link PacketDistributor.TargetPoint} takes the excluded player that way. */
    public static void sendToPlayersNear(ServerLevel level, ServerPlayer except, double x, double y, double z, double range, LegacyPayload payload) {
        LegacyNetwork.channel().send(PacketDistributor.NEAR.with(
                () -> new PacketDistributor.TargetPoint(except, x, y, z, range, level.dimension())), payload);
    }

    public static void sendToPlayersTrackingChunk(ServerLevel level, ChunkPos pos, LegacyPayload payload) {
        LegacyNetwork.channel().send(PacketDistributor.TRACKING_CHUNK.with(() -> level.getChunk(pos.x, pos.z)), payload);
    }

    public static void sendToPlayersTrackingEntity(Entity entity, LegacyPayload payload) {
        LegacyNetwork.channel().send(PacketDistributor.TRACKING_ENTITY.with(() -> entity), payload);
    }

    public static void sendToPlayersTrackingEntityAndSelf(Entity entity, LegacyPayload payload) {
        LegacyNetwork.channel().send(PacketDistributor.TRACKING_ENTITY_AND_SELF.with(() -> entity), payload);
    }
}

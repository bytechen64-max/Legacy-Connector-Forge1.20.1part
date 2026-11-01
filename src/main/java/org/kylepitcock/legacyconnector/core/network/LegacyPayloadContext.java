package org.kylepitcock.legacyconnector.core.network;

import net.minecraft.network.Connection;
import net.minecraft.world.entity.player.Player;

/**
 * What a legacy message handler is told about the message it is answering. On Forge 1.20.1 this is a thin view of
 * {@code NetworkEvent.Context}; the bridges only need these four things, so they do not depend on the Forge type.
 */
public interface LegacyPayloadContext {

    /** The player that sent the message; null for a message the client received (the sender is the server there). */
    Player player();

    /** The connection the message arrived on. */
    Connection connection();

    /** Runs {@code task} on the main game thread. */
    void enqueueWork(Runnable task);

    /** Answers the sender with {@code payload}, on the same channel, in the opposite direction. */
    void reply(LegacyPayload payload);
}

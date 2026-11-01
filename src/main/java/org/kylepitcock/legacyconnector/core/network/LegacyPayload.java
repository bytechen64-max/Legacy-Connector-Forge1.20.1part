package org.kylepitcock.legacyconnector.core.network;

import net.minecraft.network.FriendlyByteBuf;

/**
 * Carrier for every legacy network message: which legacy family and channel it belongs to, the legacy
 * discriminator, and the raw bytes the legacy message serialized itself into.
 *
 * <p>NeoForge 1.21 carried this as a {@code CustomPacketPayload} with a {@code StreamCodec}; Forge 1.20.1 registers one
 * {@code SimpleChannel} message instead, so the record writes and reads itself.</p>
 */
public record LegacyPayload(String version, String channel, int discriminator, byte[] data) {

    public static void write(LegacyPayload payload, FriendlyByteBuf buf) {
        buf.writeUtf(payload.version);
        buf.writeUtf(payload.channel);
        buf.writeVarInt(payload.discriminator);
        buf.writeByteArray(payload.data);
    }

    public static LegacyPayload read(FriendlyByteBuf buf) {
        return new LegacyPayload(buf.readUtf(), buf.readUtf(), buf.readVarInt(), buf.readByteArray());
    }
}

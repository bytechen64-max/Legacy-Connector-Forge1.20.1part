package org.kylepitcock.legacyconnector.core.network;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.BiConsumer;
import net.minecraft.network.Connection;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.network.NetworkEvent;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.simple.SimpleChannel;
import org.slf4j.LoggerFactory;

/** Routes {@link LegacyPayload}s to the legacy family that owns the channel. */
public final class LegacyNetwork {
    /** One channel carries every legacy family: the payload says which family and channel it belongs to. */
    private static final ResourceLocation NAME = new ResourceLocation("legacyconnector", "legacy");
    private static final String PROTOCOL = "1";
    private static final Map<String, BiConsumer<LegacyPayload, LegacyPayloadContext>> RECEIVERS = new ConcurrentHashMap<>();
    private static volatile SimpleChannel channel;

    private LegacyNetwork() {}

    public static void registerReceiver(String version, BiConsumer<LegacyPayload, LegacyPayloadContext> receiver) {
        RECEIVERS.put(version, receiver);
    }

    /**
     * Opens the channel. Called once from the mod constructor.
     *
     * <p>NeoForge 1.21 registered the payload with {@code optional()}, so a client without the layer could still join. Forge
     * 1.20.1 expresses the same thing on the channel itself: {@link NetworkRegistry#acceptMissingOr} accepts a peer that does
     * not know the channel at all, and only rejects one that answers with a different protocol version.</p>
     */
    public static synchronized void register() {
        if (channel != null) return;
        SimpleChannel opened = NetworkRegistry.ChannelBuilder.named(NAME)
                .networkProtocolVersion(() -> PROTOCOL)
                .clientAcceptedVersions(NetworkRegistry.acceptMissingOr(PROTOCOL::equals))
                .serverAcceptedVersions(NetworkRegistry.acceptMissingOr(PROTOCOL::equals))
                .simpleChannel();
        // One message id serves both directions: the payload names its own legacy family, and the context knows the side it
        // arrived on, so a second registration (which Forge 1.20.1 requires per direction) would only duplicate the handler.
        opened.messageBuilder(LegacyPayload.class, 0)
                .encoder(LegacyPayload::write)
                .decoder(LegacyPayload::read)
                .consumerMainThread((payload, context) -> receive(payload, new ForgeContext(context.get())))
                .add();
        channel = opened;
    }

    static SimpleChannel channel() {
        SimpleChannel open = channel;
        if (open == null) throw new IllegalStateException("Legacy Connector: the legacy channel is not open yet");
        return open;
    }

    private static void receive(LegacyPayload payload, LegacyPayloadContext context) {
        var receiver = RECEIVERS.get(payload.version());
        if (receiver == null) {
            LoggerFactory.getLogger("LegacyConnector/Network").debug("Dropping legacy message for unknown family {}", payload.version());
            return;
        }
        receiver.accept(payload, context);
    }

    /** {@link LegacyPayloadContext} over Forge's {@link NetworkEvent.Context}. */
    private record ForgeContext(NetworkEvent.Context context) implements LegacyPayloadContext {
        @Override
        public Player player() {
            // getSender() is the sending player on the server and null on the client, which is exactly what the bridges test.
            return context.getSender();
        }

        @Override
        public Connection connection() {
            return context.getNetworkManager();
        }

        @Override
        public void enqueueWork(Runnable task) {
            context.enqueueWork(task);
        }

        @Override
        public void reply(LegacyPayload payload) {
            channel().reply(payload, context);
        }
    }
}

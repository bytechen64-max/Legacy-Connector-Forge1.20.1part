package legacyconnector.v1_12_2.net.minecraft.network.play.server;

import java.io.IOException;
import legacyconnector.v1_12_2.net.minecraft.network.Packet;
import legacyconnector.v1_12_2.net.minecraft.network.PacketBuffer;
import legacyconnector.v1_12_2.net.minecraft.network.play.INetHandlerPlayClient;

/** Disconnects the player with a reason. */
public class SPacketDisconnect implements Packet<INetHandlerPlayClient> {
    private legacyconnector.v1_12_2.net.minecraft.util.text.ITextComponent reason;

    public SPacketDisconnect() {
    }

    public SPacketDisconnect(legacyconnector.v1_12_2.net.minecraft.util.text.ITextComponent messageIn) {
        this.reason = messageIn;
    }

    public legacyconnector.v1_12_2.net.minecraft.util.text.ITextComponent getReason() {
        return reason;
    }

    @Override
    public void readPacketData(PacketBuffer buf) throws IOException {
        reason = buf.readTextComponent();
    }

    @Override
    public void writePacketData(PacketBuffer buf) throws IOException {
        buf.writeTextComponent(reason);
    }

    /** Handled by the modern client as the modern packet. */
    @Override
    public void processPacket(INetHandlerPlayClient handler) {
    }

    @Override
    public net.minecraft.network.protocol.Packet<?> mcc$modern() {
        // 1.20.1 has no play-phase disconnect packet (1.20.2+): the server closes the connection instead.
        return null;
    }
}

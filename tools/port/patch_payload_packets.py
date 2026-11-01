"""1.20.1's custom payload packets carry (channel, buffer) instead of a CustomPayload record."""
import sys

HELPER = '''
    /** The channel every legacy message travels on (its own family and channel are inside the payload). */
    public static final net.minecraft.resources.ResourceLocation CHANNEL =
            new net.minecraft.resources.ResourceLocation("legacyconnector", "legacy");

    /** A legacy payload packed the way 1.20.1's custom payload packets carry it. */
    public static net.minecraft.network.FriendlyByteBuf buffer(org.kylepitcock.legacyconnector.core.network.LegacyPayload payload) {
        var buf = new net.minecraft.network.FriendlyByteBuf(io.netty.buffer.Unpooled.buffer());
        org.kylepitcock.legacyconnector.core.network.LegacyPayload.write(payload, buf);
        return buf;
    }
'''

P = r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/bridge/FmlChannelBridge1122.java"
src = open(P, encoding="utf-8").read()
anchor = "    public static LegacyPayload payload(FMLProxyPacket packet) {"
if src.count(anchor) != 1:
    print("ABORT: payload method not found")
    sys.exit(1)
src = src.replace(anchor, HELPER + "\n" + anchor)
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P)

FB = "org.kylepitcock.legacyconnector.v1_12_2.bridge.FmlChannelBridge1122"
EDITS = {
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/network/play/client/CPacketCustomPayload.java": [
        ("        return new net.minecraft.network.protocol.common.ServerboundCustomPayloadPacket(org.kylepitcock.legacyconnector.v1_12_2.bridge.FmlChannelBridge1122.payload(proxy));",
         f"        return new net.minecraft.network.protocol.game.ServerboundCustomPayloadPacket({FB}.CHANNEL, {FB}.buffer({FB}.payload(proxy)));"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/network/play/server/SPacketCustomPayload.java": [
        ("        return new net.minecraft.network.protocol.common.ClientboundCustomPayloadPacket(org.kylepitcock.legacyconnector.v1_12_2.bridge.FmlChannelBridge1122.payload(proxy));",
         f"        return new net.minecraft.network.protocol.game.ClientboundCustomPayloadPacket({FB}.CHANNEL, {FB}.buffer({FB}.payload(proxy)));"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraftforge/fml/common/network/internal/FMLProxyPacket.java": [
        ("""        var p = org.kylepitcock.legacyconnector.v1_12_2.bridge.FmlChannelBridge1122.payload(this);
        return target == Side.SERVER ? new net.minecraft.network.protocol.common.ServerboundCustomPayloadPacket(p)
                : new net.minecraft.network.protocol.common.ClientboundCustomPayloadPacket(p);""",
         f"""        var p = {FB}.payload(this);
        var buf = {FB}.buffer(p);
        return target == Side.SERVER
                ? new net.minecraft.network.protocol.game.ServerboundCustomPayloadPacket({FB}.CHANNEL, buf)
                : new net.minecraft.network.protocol.game.ClientboundCustomPayloadPacket({FB}.CHANNEL, buf);"""),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/bridge/NetworkBridge1122.java": [
        ("            return new net.minecraft.network.protocol.common.ClientboundCustomPayloadPacket(encode(message));",
         f"            var p = encode(message);\n"
         f"            return new net.minecraft.network.protocol.game.ClientboundCustomPayloadPacket({FB}.CHANNEL, {FB}.buffer(p));"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/network/play/server/SPacketDisconnect.java": [
        ("        return new net.minecraft.network.protocol.common.ClientboundDisconnectPacket(reason == null ? net.minecraft.network.chat.Component.empty() : reason.mcc$modern());",
         "        // 1.20.1 has no play-phase disconnect packet (1.20.2+): the server closes the connection instead.\n"
         "        return null;"),
    ],
}

for path, pairs in EDITS.items():
    src = open(path, encoding="utf-8").read()
    for old, new in pairs:
        n = src.count(old)
        if n != 1:
            print(f"ABORT {n} in {path}: {old.strip()[:70]}")
            sys.exit(1)
        src = src.replace(old, new)
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

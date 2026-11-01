"""Forge 1.20.1 networking call sites: PacketDistributor.sendX(...) -> LegacyChannel.sendX(...), IPayloadContext ->
LegacyPayloadContext, and the channel is opened from the mod constructor instead of a payload registration event."""
import os
import re
import sys

SEND = [
    "sendToServer",
    "sendToPlayer",
    "sendToAllPlayers",
    "sendToPlayersInDimension",
    "sendToPlayersNear",
    "sendToPlayersTrackingChunk",
    "sendToPlayersTrackingEntityAndSelf",
    "sendToPlayersTrackingEntity",
]

CHANNEL_IMPORT = "import org.kylepitcock.legacyconnector.core.network.LegacyChannel;"
CONTEXT_IMPORT = "import org.kylepitcock.legacyconnector.core.network.LegacyPayloadContext;"


def add_import(src: str, imp: str) -> str:
    if imp in src:
        return src
    # insert before the first import line, keeping the block contiguous
    m = re.search(r"^import ", src, re.MULTILINE)
    if not m:
        return src
    return src[: m.start()] + imp + "\n" + src[m.start():]


changed = []
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        src = open(p, encoding="utf-8").read()
        if "PacketDistributor" not in src and "IPayloadContext" not in src:
            continue
        original = src

        for send in SEND:
            src = src.replace("PacketDistributor." + send + "(", "LegacyChannel." + send + "(")

        # the Forge context type is replaced by the bridge-facing interface
        src = src.replace("IPayloadContext", "LegacyPayloadContext")

        # drop imports that no longer resolve / are no longer used
        if "PacketDistributor" not in src.replace("import net.minecraftforge.network.PacketDistributor;", ""):
            src = src.replace("import net.minecraftforge.network.PacketDistributor;\n", "")
        if "LegacyPayloadContext" not in src.replace(CONTEXT_IMPORT, ""):
            src = src.replace(CONTEXT_IMPORT + "\n", "")
        src = src.replace("import net.minecraftforge.network.event.RegisterPayloadHandlersEvent;\n", "")

        if "LegacyChannel." in src:
            src = add_import(src, CHANNEL_IMPORT)
        if re.search(r"\bLegacyPayloadContext\b", src) and "LegacyPayloadContext" in src.split("\n\n")[-1]:
            src = add_import(src, CONTEXT_IMPORT)

        if src != original:
            open(p, "w", encoding="utf-8", newline="").write(src)
            changed.append(p)

print("rewrote", len(changed), "files")
for c in changed:
    print("  ", c)

# the channel is opened in the mod constructor (Forge 1.20.1 has no RegisterPayloadHandlersEvent)
P = "src/main/java/org/kylepitcock/legacyconnector/LegacyConnector.java"
s = open(P, encoding="utf-8").read()
old = "modBus.addListener(LegacyNetwork::onRegisterPayloads);"
if s.count(old) != 1:
    print("ABORT LegacyConnector anchor:", s.count(old))
    sys.exit(1)
s = s.replace(old, "// Forge 1.20.1 has no payload registration event: the one channel that carries every legacy family opens here.\n        LegacyNetwork.register();")
open(P, "w", encoding="utf-8", newline="").write(s)
print("patched LegacyConnector")

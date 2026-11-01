"""1.20.1's ServerData constructor takes the LAN flag and has no State enum."""
import os
import re

CTOR = re.compile(r"(new net\.minecraft\.client\.multiplayer\.ServerData\([^;]*?),\s*net\.minecraft\.client\.multiplayer\.ServerData\.Type\.\w+\)")

count = 0
changed = []
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        src = open(p, encoding="utf-8").read()
        new, n = CTOR.subn(lambda m: m.group(1) + ", false)", src)
        if n:
            count += n
            open(p, "w", encoding="utf-8", newline="").write(new)
            changed.append((p, n))

print("constructor calls fixed:", count)
for c in changed:
    print("  ", c)

# the pinger: 1.20.1 marks the ping as done itself, there is no state to set
P = r"src/main/java/legacyconnector/v1_12_2/net/minecraft/client/network/ServerPinger.java"
src = open(P, encoding="utf-8").read()
old = """        modern.pingServer(data, update, () -> {
            data.setState(data.protocol == net.minecraft.SharedConstants.getCurrentVersion().getProtocolVersion()
                    ? net.minecraft.client.multiplayer.ServerData.State.SUCCESSFUL : net.minecraft.client.multiplayer.ServerData.State.INCOMPATIBLE);
            server.mcc$update(data);
        });"""
new = """        // 1.20.1 marks the ping as done itself (the State enum is 1.20.5); the protocol match is kept on the legacy entry.
        modern.pingServer(data, update, () -> {
            server.mcc$setCompatible(data.protocol == net.minecraft.SharedConstants.getCurrentVersion().getProtocolVersion());
            server.mcc$update(data);
        });"""
if src.count(old) != 1:
    print("ABORT ServerPinger:", src.count(old))
else:
    open(P, "w", encoding="utf-8", newline="").write(src.replace(old, new))
    print("patched", P)

"""The last two-argument packet factory and a spawn call that needs the extra tag."""
import sys

EDITS = {
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/network/NetHandlerPlayServer.java": [
        ("            player.connection.send(net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket.create(be, (b, registries) -> tag));",
         "            // 1.20.1's factory takes a one-argument tag getter.\n"
         "            player.connection.send(net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket.create(be, b -> tag));"),
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

# finalizeSpawn calls: the tag argument was added in 1.20.2
import os
import re

FIN = re.compile(r"(\.finalizeSpawn\([^;]*?)\);")
count = 0
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        src = open(p, encoding="utf-8").read()
        if ".finalizeSpawn(" not in src:
            continue
        out = []
        idx = 0
        while True:
            at = src.find(".finalizeSpawn(", idx)
            if at < 0:
                out.append(src[idx:])
                break
            start = at + len(".finalizeSpawn(") - 1
            depth = 0
            i = start
            commas = 0
            while i < len(src):
                c = src[i]
                if c == "(":
                    depth += 1
                elif c == ")":
                    depth -= 1
                    if depth == 0:
                        break
                elif c == "," and depth == 1:
                    commas += 1
                i += 1
            out.append(src[idx:start + 1])
            args = src[start + 1:i]
            if commas == 3:
                out.append(args + ", null")
                count += 1
            else:
                out.append(args)
            out.append(")")
            idx = i + 1
        new = "".join(out)
        if new != src:
            open(p, "w", encoding="utf-8", newline="").write(new)

print("finalizeSpawn calls given the tag:", count)

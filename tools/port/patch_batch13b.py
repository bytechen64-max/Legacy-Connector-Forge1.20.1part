"""Line-based: the packet factory's lambda and the finalizeSpawn calls."""
import os
import sys

P = r"src/main/java/legacyconnector/v1_12_2/net/minecraft/network/NetHandlerPlayServer.java"
lines = open(P, encoding="utf-8").read().splitlines()
hits = [i for i, ln in enumerate(lines) if "(b, registries) -> tag" in ln]
if len(hits) != 1:
    print("ABORT packet factory:", len(hits))
    sys.exit(1)
lines[hits[0]] = lines[hits[0]].replace("(b, registries) -> tag", "b -> tag")
open(P, "w", encoding="utf-8", newline="").write("\n".join(lines) + "\n")
print("patched", P)

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
            print("  finalizeSpawn in", name)

print("finalizeSpawn calls given the tag:", count)

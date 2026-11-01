"""Inside the shim's own ForgeHooks class, unqualified ForgeHooks.x resolves to itself; the modern calls need the full name."""
import re
import sys

P = r"src/main/java/legacyconnector/v1_12_2/net/minecraftforge/common/ForgeHooks.java"
src = open(P, encoding="utf-8").read()
new, n = re.subn(r"(?<!common\.)\bForgeHooks\.", "net.minecraftforge.common.ForgeHooks.", src)
open(P, "w", encoding="utf-8", newline="").write(new)
print("qualified", n, "self-references")

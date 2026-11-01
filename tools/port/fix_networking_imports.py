"""Cleanup after the networking rewrite: the context interface lives in the mod, not in Forge, and FQN prefixes must go."""
import os

PACKAGE_BAD = "import net.minecraftforge.network.handling.LegacyPayloadContext;"
PACKAGE_GOOD = "import org.kylepitcock.legacyconnector.core.network.LegacyPayloadContext;"

changed = []
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        src = open(p, encoding="utf-8").read()
        original = src
        src = src.replace(PACKAGE_BAD, PACKAGE_GOOD)
        src = src.replace("net.minecraftforge.network.LegacyChannel.", "LegacyChannel.")
        if src != original:
            open(p, "w", encoding="utf-8", newline="").write(src)
            changed.append(p)
print("cleaned", len(changed), "files")
for c in changed:
    print("  ", c)

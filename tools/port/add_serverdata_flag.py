"""Adds the compatibility flag to the shim's ServerData (1.20.5 tracks it in a State enum)."""
import sys

P = r"src/main/java/legacyconnector/v1_12_2/net/minecraft/client/multiplayer/ServerData.java"
src = open(P, encoding="utf-8").read()
if "mcc$setCompatible" in src:
    print("already there")
    sys.exit(0)
anchor = "    public enum ServerResourceMode {"
add = """    /** Whether the server answered with this game version (1.20.5 keeps it in a State enum). */
    private boolean compatible = true;

    public boolean mcc$compatible() {
        return compatible;
    }

    public void mcc$setCompatible(boolean compatible) {
        this.compatible = compatible;
    }

"""
idx = src.find(anchor)
if idx < 0:
    print("ABORT: anchor missing")
    sys.exit(1)
open(P, "w", encoding="utf-8", newline="").write(src[:idx] + add + src[idx:])
print("added the compatibility flag")

"""1.20.1 has no net.minecraftforge.event.EventHooks: the same static hooks live on ForgeEventFactory."""
import sys

# the shim's own ForgeEventFactory must not call itself: use the fully qualified modern class there
SHIM = r"src/main/java/legacyconnector/v1_12_2/net/minecraftforge/event/ForgeEventFactory.java"
src = open(SHIM, encoding="utf-8").read()
n = src.count("EventHooks.")
src = src.replace("import net.minecraftforge.event.EventHooks;\n", "")
src = src.replace("EventHooks.", "net.minecraftforge.event.ForgeEventFactory.")
open(SHIM, "w", encoding="utf-8", newline="").write(src)
print(f"{SHIM}: {n} EventHooks calls for the modern ForgeEventFactory")

# every other file: the forgespi-style name becomes the fully qualified 1.20.1 one
import os
changed = 0
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        if p.replace("\\", "/") == SHIM:
            continue
        src = open(p, encoding="utf-8").read()
        if "EventHooks" not in src:
            continue
        before = src
        src = src.replace("import net.minecraftforge.event.EventHooks;\n", "")
        src = src.replace("net.minecraftforge.event.EventHooks.", "net.minecraftforge.event.ForgeEventFactory.")
        if src != before:
            open(p, "w", encoding="utf-8", newline="").write(src)
            changed += 1
            print("  patched", p)
print("files changed:", changed)

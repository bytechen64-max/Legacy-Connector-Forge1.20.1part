"""1.20.1 renames: isAddedToLevel, the debug overlay, toast ids and default player skins."""
import os
import re
import sys

# ---------------------------------------------------------------- mechanical renames
RENAMES = [
    # 1.20.5 added isAddedToLevel; 1.20.1 calls it isAddedToWorld
    ("m.isAddedToLevel()", "m.isAddedToWorld()"),
    ("mcc$entity.isAddedToLevel()", "mcc$entity.isAddedToWorld()"),
    ("h.isAddedToLevel()", "h.isAddedToWorld()"),
    ("net.minecraft.client.resources.DefaultPlayerSkin.getDefaultTexture()",
     "net.minecraft.client.resources.DefaultPlayerSkin.getDefaultSkin()"),
]
changed = 0
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        src = open(p, encoding="utf-8").read()
        before = src
        for old, new in RENAMES:
            src = src.replace(old, new)
        if src != before:
            open(p, "w", encoding="utf-8", newline="").write(src)
            changed += 1
print("renamed sites in", changed, "files")

# ---------------------------------------------------------------- the debug overlay
P = r"src/main/java/legacyconnector/v1_12_2/net/minecraft/client/settings/GameSettings.java"
src = open(P, encoding="utf-8").read()
pairs = [
    ("        return mc.getDebugOverlay().showDebugScreen();",
     "        // 1.20.2 moved the debug overlay behind Minecraft.getDebugOverlay(); 1.20.1 keeps plain options.\n"
     "        return mc.options.renderDebug;"),
    ("        return mc().getDebugOverlay().showProfilerChart();", "        return mc().options.renderDebugCharts;"),
    ("        return mc().getDebugOverlay().showFpsCharts();", "        return mc().options.renderDebugCharts;"),
]
for old, new in pairs:
    if src.count(old) != 1:
        print("ABORT GameSettings:", src.count(old), old.strip()[:50])
        sys.exit(1)
    src = src.replace(old, new)
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P)

for path, old, new in [
    (r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/client/ClientEvents1122.java",
     "if (wants(RenderGameOverlayEvent.Text.class) && !Minecraft.getInstance().getDebugOverlay().showDebugScreen()) {",
     "if (wants(RenderGameOverlayEvent.Text.class) && !Minecraft.getInstance().options.renderDebug) {"),
    (r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/WorldScreenshotTest.java",
     "mc.getDebugOverlay().toggleOverlay();",
     "mc.options.renderDebug = !mc.options.renderDebug;"),
]:
    src = open(path, encoding="utf-8").read()
    if src.count(old) != 1:
        print("ABORT", path, src.count(old))
        sys.exit(1)
    open(path, "w", encoding="utf-8", newline="").write(src.replace(old, new))
    print("patched", path)

# ---------------------------------------------------------------- toast ids
P = r"src/main/java/legacyconnector/v1_12_2/net/minecraft/client/gui/toasts/SystemToast.java"
src = open(P, encoding="utf-8").read()
pairs = [
    ("    NARRATOR_TOGGLE(net.minecraft.client.gui.components.toasts.SystemToast.SystemToastId.NARRATOR_TOGGLE),\n"
     "    TUTORIAL_HINT(new net.minecraft.client.gui.components.toasts.SystemToast.SystemToastId());",
     "    NARRATOR_TOGGLE(net.minecraft.client.gui.components.toasts.SystemToast.SystemToastIds.NARRATOR_TOGGLE),\n"
     "    TUTORIAL_HINT(net.minecraft.client.gui.components.toasts.SystemToast.SystemToastIds.TUTORIAL_HINT);"),
    ("    private final net.minecraft.client.gui.components.toasts.SystemToast.SystemToastId modern;",
     "    private final net.minecraft.client.gui.components.toasts.SystemToast.SystemToastIds modern;"),
    ("    Type(net.minecraft.client.gui.components.toasts.SystemToast.SystemToastId modern) {",
     "    Type(net.minecraft.client.gui.components.toasts.SystemToast.SystemToastIds modern) {"),
]
for old, new in pairs:
    if src.count(old) != 1:
        print("ABORT SystemToast:", src.count(old), old.splitlines()[0][:60])
        sys.exit(1)
    src = src.replace(old, new)
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P)

P = r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/LegacyToasts.java"
src = open(P, encoding="utf-8").read()
if src.count("SystemToast.SystemToastId.") != 1:
    print("ABORT LegacyToasts:", src.count("SystemToast.SystemToastId."))
    sys.exit(1)
open(P, "w", encoding="utf-8", newline="").write(src.replace("SystemToast.SystemToastId.", "SystemToast.SystemToastIds."))
print("patched", P)

# ---------------------------------------------------------------- player skin texture
P = r"src/main/java/legacyconnector/v1_12_2/net/minecraft/client/entity/AbstractClientPlayer.java"
src = open(P, encoding="utf-8").read()
old = "p.getSkin().texture()"
if src.count(old) != 1:
    print("ABORT AbstractClientPlayer:", src.count(old))
    sys.exit(1)
open(P, "w", encoding="utf-8", newline="").write(src.replace(old, "p.getSkinTextureLocation()"))
print("patched", P)

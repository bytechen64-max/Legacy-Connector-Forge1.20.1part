"""1.20.1 client GUI overlays and the texture-stitch event (the 1.21 names do not exist)."""
import os
import sys

# 1.21's VanillaGuiLayers -> the 1.20.1 VanillaGuiOverlay ids
CONSTANTS = {
    "CROSSHAIR": "CROSSHAIR",
    "HOTBAR": "HOTBAR",
    "PLAYER_HEALTH": "PLAYER_HEALTH",
    "ARMOR_LEVEL": "ARMOR_LEVEL",
    "FOOD_LEVEL": "FOOD_LEVEL",
    "AIR_LEVEL": "AIR_LEVEL",
    "EXPERIENCE_BAR": "EXPERIENCE_BAR",
    "VEHICLE_HEALTH": "MOUNT_HEALTH",
    "JUMP_METER": "JUMP_BAR",
    "BOSS_OVERLAY": "BOSS_EVENT_PROGRESS",
    "CHAT": "CHAT_PANEL",
    "TAB_LIST": "PLAYER_LIST",
    "DEBUG_OVERLAY": "DEBUG_TEXT",
    "EFFECTS": "POTION_ICONS",
    "SUBTITLE_OVERLAY": "SUBTITLES",
    "SCOREBOARD_SIDEBAR": "SCOREBOARD",
    "CAMERA_OVERLAYS": "HELMET",
}

FILES = [
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/client/ClientEvents1122.java",
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/HudEvents1710.java",
]

for path in FILES:
    src = open(path, encoding="utf-8").read()
    for old, new in CONSTANTS.items():
        src = src.replace("VanillaGuiLayers." + old, "VanillaGuiOverlay." + new)
    src = src.replace("import net.minecraftforge.client.gui.VanillaGuiLayers;",
                      "import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;")
    src = src.replace("VanillaGuiLayers", "VanillaGuiOverlay")
    # the overlay event is RenderGuiOverlayEvent, its id comes from the overlay and the partial tick is a float
    src = src.replace("RenderGuiLayerEvent", "RenderGuiOverlayEvent")
    src = src.replace("e.getName()", "e.getOverlay().id()")
    src = src.replace("e.getPartialTick().getGameTimeDeltaPartialTick(false)", "e.getPartialTick()")
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

# the texture stitch event: TextureStitchEvent.Post, fully qualified (the shims own a class of that name)
EDITS = {
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/client/Client1122.java": [
        ("import net.minecraftforge.client.event.TextureAtlasStitchedEvent;\n", ""),
        ("        modBus.addListener((TextureAtlasStitchedEvent e) -> {",
         "        modBus.addListener((net.minecraftforge.client.event.TextureStitchEvent.Post e) -> {"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/Client1710.java": [
        ("        modBus.addListener((net.minecraftforge.client.event.TextureAtlasStitchedEvent e) -> {",
         "        modBus.addListener((net.minecraftforge.client.event.TextureStitchEvent.Post e) -> {"),
    ],
}
for path, pairs in EDITS.items():
    src = open(path, encoding="utf-8").read()
    for old, new in pairs:
        if src.count(old) != 1:
            print(f"ABORT {src.count(old)} matches in {path}: {old.strip()[:60]}")
            sys.exit(1)
        src = src.replace(old, new)
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

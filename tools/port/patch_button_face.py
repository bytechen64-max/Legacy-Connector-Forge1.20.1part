"""1.20.1 has no GuiGraphics.blitSprite: the button face comes from the legacy 1.12 widget sheet again."""
import sys

BODY_OLD = """    public static void mcc$drawBackground(int hoverState, int x, int y, int width, int height) {
        var gui = RenderContext.gui();
        if (gui != null) gui.blitSprite(sprite(hoverState != 0, hoverState == 2), x, y, width, height);
    }"""

BODY_NEW = """    public static void mcc$drawBackground(int hoverState, int x, int y, int width, int height) {
        var gui = RenderContext.gui();
        if (gui == null) return;
        // 1.20.1 has no blitSprite: the face is 1.12's own two-half sprite from textures/gui/widgets.png (row per state).
        int v = 46 + hoverState * 20;
        gui.blit(BUTTON_TEXTURES, x, y, 0, v, width / 2, height);
        gui.blit(BUTTON_TEXTURES, x + width / 2, y, 200 - width / 2, v, width / 2, height);
    }"""

for path in (r"src/main/java/legacyconnector/v1_12_2/net/minecraft/client/gui/GuiButton.java",
             r"src/main/java/legacyconnector/v1_7_10/net/minecraft/client/gui/GuiButton.java"):
    src = open(path, encoding="utf-8").read()
    if src.count(BODY_OLD) != 1:
        print(f"ABORT {path}: {src.count(BODY_OLD)}")
        sys.exit(1)
    src = src.replace(BODY_OLD, BODY_NEW)
    # the sprite constants and helper are unused now
    start = src.find("    // 1.20.1 names the three button sprites one by one")
    end = src.find("    public int width;")
    if start < 0 or end < 0:
        print("ABORT: sprite block not found in", path)
        sys.exit(1)
    src = src[:start] + src[end:]
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

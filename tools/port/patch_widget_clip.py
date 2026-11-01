"""1.20.1 has no WidgetSprites record and ClipContext takes an entity, not a CollisionContext."""
import sys

GUI = [
    (r"src/main/java/legacyconnector/v1_12_2/net/minecraft/client/gui/GuiButton.java",
     """    private static final WidgetSprites SPRITES = new WidgetSprites(net.minecraft.resources.ResourceLocation.withDefaultNamespace("widget/button"),
            net.minecraft.resources.ResourceLocation.withDefaultNamespace("widget/button_disabled"),
            net.minecraft.resources.ResourceLocation.withDefaultNamespace("widget/button_highlighted"));""",
     11),
    (r"src/main/java/legacyconnector/v1_7_10/net/minecraft/client/gui/GuiButton.java",
     """    private static final WidgetSprites SPRITES = new WidgetSprites(net.minecraft.resources.ResourceLocation.withDefaultNamespace("widget/button"),
            net.minecraft.resources.ResourceLocation.withDefaultNamespace("widget/button_disabled"),
            net.minecraft.resources.ResourceLocation.withDefaultNamespace("widget/button_highlighted"));""",
     10),
]

REPLACEMENT = """    // 1.20.1 names the three button sprites one by one (the WidgetSprites record is 1.20.3).
    private static final net.minecraft.resources.ResourceLocation SPRITE = net.minecraft.resources.ResourceLocation.withDefaultNamespace("widget/button");
    private static final net.minecraft.resources.ResourceLocation SPRITE_DISABLED = net.minecraft.resources.ResourceLocation.withDefaultNamespace("widget/button_disabled");
    private static final net.minecraft.resources.ResourceLocation SPRITE_HIGHLIGHTED = net.minecraft.resources.ResourceLocation.withDefaultNamespace("widget/button_highlighted");

    /** The button sprite for a state ({@code WidgetSprites.get(enabled, focused)} before 1.20.3). */
    private static net.minecraft.resources.ResourceLocation sprite(boolean enabled, boolean focused) {
        return !enabled ? SPRITE_DISABLED : focused ? SPRITE_HIGHLIGHTED : SPRITE;
    }"""

for path, old, _line in GUI:
    src = open(path, encoding="utf-8").read()
    for old_text, new_text in [
        ("import net.minecraft.client.gui.components.WidgetSprites;\n", ""),
        (old, REPLACEMENT),
        ("gui.blitSprite(SPRITES.get(hoverState != 0, hoverState == 2), x, y, width, height)",
         "gui.blitSprite(sprite(hoverState != 0, hoverState == 2), x, y, width, height)"),
    ]:
        if src.count(old_text) != 1:
            print(f"ABORT {src.count(old_text)} matches in {path}: {old_text.strip()[:60]}")
            sys.exit(1)
        src = src.replace(old_text, new_text)
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

# ClipContext takes the colliding entity on 1.20.1
P = r"src/main/java/legacyconnector/v1_12_2/net/minecraft/world/World.java"
src = open(P, encoding="utf-8").read()
n = src.count("net.minecraft.world.phys.shapes.CollisionContext.empty()")
if n != 2:
    print("ABORT CollisionContext sites:", n)
    sys.exit(1)
src = src.replace("net.minecraft.world.phys.shapes.CollisionContext.empty()", "(net.minecraft.world.entity.Entity) null")
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P, "-", n, "clip contexts")

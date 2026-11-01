"""The brewing stand's three sprite draws (the 1.20.2 nine-argument form) through LegacyGuiSprites."""
import sys

P = r"src/main/java/legacyconnector/v1_12_2/net/minecraft/client/gui/inventory/GuiBrewingStand.java"
src = open(P, encoding="utf-8").read()
GS = "org.kylepitcock.legacyconnector.v1_7_10.client.LegacyGuiSprites.blit"
pairs = [
    ('gui.blitSprite(net.minecraft.resources.ResourceLocation.withDefaultNamespace("container/brewing_stand/fuel_length"), 18, 4, 0, 0, i + 60, j + 44, l, 4);',
     f'{GS}(gui, net.minecraft.resources.ResourceLocation.withDefaultNamespace("container/brewing_stand/fuel_length"), 18, 4, 0, 0, i + 60, j + 44, l, 4);'),
    ('gui.blitSprite(net.minecraft.resources.ResourceLocation.withDefaultNamespace("container/brewing_stand/brew_progress"), 9, 28, 0, 0, i + 97, j + 16, 9, j1);',
     f'{GS}(gui, net.minecraft.resources.ResourceLocation.withDefaultNamespace("container/brewing_stand/brew_progress"), 9, 28, 0, 0, i + 97, j + 16, 9, j1);'),
    ('gui.blitSprite(net.minecraft.resources.ResourceLocation.withDefaultNamespace("container/brewing_stand/bubbles"), 12, 29, 0, 29 - j1, i + 63, j + 14 + 29 - j1, 12, j1);',
     f'{GS}(gui, net.minecraft.resources.ResourceLocation.withDefaultNamespace("container/brewing_stand/bubbles"), 12, 29, 0, 29 - j1, i + 63, j + 14 + 29 - j1, 12, j1);'),
]
for old, new in pairs:
    n = src.count(old)
    if n != 1:
        print(f"ABORT {n}: {old[:60]}")
        sys.exit(1)
    src = src.replace(old, new)
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P)

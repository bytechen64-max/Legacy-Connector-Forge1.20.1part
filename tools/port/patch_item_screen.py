"""1.20.1 item/screen signatures and the stale VertexConsumer overrides."""
import sys

EDITS = {
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/adapter/Legacy1122Item.java": [
        ("    public int getUseDuration(ItemStack stack, net.minecraft.world.entity.LivingEntity entity) {\n"
         "        int modern = super.getUseDuration(stack, entity);",
         "    public int getUseDuration(ItemStack stack) {\n"
         "        int modern = super.getUseDuration(stack);"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/adapter/Legacy1122BlockItem.java": [
        ("    public int getUseDuration(ItemStack stack, net.minecraft.world.entity.LivingEntity entity) {\n"
         "        int modern = super.getUseDuration(stack, entity);",
         "    public int getUseDuration(ItemStack stack) {\n"
         "        int modern = super.getUseDuration(stack);"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/client/LegacyScreen1122.java": [
        ("""    public void renderBackground(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        // legacy drawScreen draws its own background (drawDefaultBackground)""",
         """    public void renderBackground(GuiGraphics graphics) {
        // legacy drawScreen draws its own background (drawDefaultBackground)"""),
        ("    public boolean mouseScrolled(double x, double y, double scrollX, double scrollY) {\n"
         "        guard(() -> legacy.mcc$mouseScrolled((int) x, (int) y, scrollY));",
         "    public boolean mouseScrolled(double x, double y, double scrollY) {\n"
         "        guard(() -> legacy.mcc$mouseScrolled((int) x, (int) y, scrollY));"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/client/LegacyContainerScreen1122.java": [
        ("""    public void renderBackground(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        // legacy drawScreen draws its own darkening (drawDefaultBackground); only the container background layer is drawn here
        if (legacy == null) super.renderBackground(graphics, mouseX, mouseY, partialTick);
        else renderBg(graphics, partialTick, mouseX, mouseY);""",
         """    public void renderBackground(GuiGraphics graphics) {
        // legacy drawScreen draws its own darkening (drawDefaultBackground); only the container background layer is drawn here
        if (legacy == null) super.renderBackground(graphics);
        else renderBg(graphics, 0.0F, 0, 0);"""),
        ("    public boolean mouseScrolled(double x, double y, double scrollX, double scrollY) {\n"
         "        if (legacy != null) guard(() -> legacy.mcc$mouseScrolled((int) x, (int) y, scrollY));\n"
         "        return super.mouseScrolled(x, y, scrollX, scrollY);",
         "    public boolean mouseScrolled(double x, double y, double scrollY) {\n"
         "        if (legacy != null) guard(() -> legacy.mcc$mouseScrolled((int) x, (int) y, scrollY));\n"
         "        return super.mouseScrolled(x, y, scrollY);"),
    ],
}

for path, pairs in EDITS.items():
    src = open(path, encoding="utf-8").read()
    for old, new in pairs:
        n = src.count(old)
        if n != 1:
            print(f"ABORT {n} in {path}: {old.strip()[:70]}")
            sys.exit(1)
        src = src.replace(old, new)
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

# the fluid renderer's 1.21-style methods are extra methods now (the 1.20.1 ones were added)
P = r"src/main/java/legacyconnector/v1_12_2/net/minecraft/client/renderer/BlockFluidRenderer.java"
src = open(P, encoding="utf-8").read()
import re
count = 0
for name in ("addVertex", "setColor", "setUv", "setUv1", "setUv2", "setNormal"):
    src, n = re.subn(r"        @Override\n(        public com\.mojang\.blaze3d\.vertex\.VertexConsumer " + name + r"\()", r"\1", src)
    count += n
open(P, "w", encoding="utf-8", newline="").write(src)
print("BlockFluidRenderer: removed", count, "stale @Override annotations")

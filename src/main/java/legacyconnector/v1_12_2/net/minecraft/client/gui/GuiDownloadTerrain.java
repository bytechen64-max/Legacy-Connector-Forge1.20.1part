package legacyconnector.v1_12_2.net.minecraft.client.gui;

/** Non-interactive terrain loading screen used during dimension changes. */
public class GuiDownloadTerrain extends GuiScreen {
    @Override public void initGui() { buttonList.clear(); }
    @Override public void drawScreen(int mouseX, int mouseY, float partialTicks) {
        drawDefaultBackground();
        drawCenteredString(fontRenderer, legacyconnector.v1_12_2.net.minecraft.client.resources.I18n.format("multiplayer.downloadingTerrain"), width / 2, height / 2 - 50, 0xFFFFFF);
    }
    @Override protected void keyTyped(char character, int keyCode) {}
    @Override public boolean doesGuiPauseGame() { return false; }
}

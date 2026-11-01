"""1.20.1 registers menu screens and config screens statically; 1.20.4+ has events/factories for both."""
import sys

EDITS = {
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/client/ClientGui1122.java": [
        ("""    public static void onRegisterScreens(net.minecraftforge.client.event.RegisterMenuScreensEvent event) {
        if (GuiBridge1122.menuType() != null) event.register(GuiBridge1122.menuType(), LegacyContainerScreen1122::new);
    }""",
         """    /** 1.20.1 registers a menu's screen statically (the register event is 1.20.4+). */
    public static void registerScreens() {
        if (GuiBridge1122.menuType() != null) net.minecraft.client.gui.screens.MenuScreens.register(GuiBridge1122.menuType(), LegacyContainerScreen1122::new);
    }"""),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/client/Client1122.java": [
        ("        modBus.addListener(ClientGui1122::onRegisterScreens);", "        ClientGui1122.registerScreens();"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/ClientGui.java": [
        ("""    public static void onRegisterScreens(RegisterMenuScreensEvent event) {
        event.register(GuiBridge.menuType(), LegacyContainerScreen::new);
    }""",
         """    /** 1.20.1 registers a menu's screen statically (the register event is 1.20.4+). */
    public static void registerScreens() {
        net.minecraft.client.gui.screens.MenuScreens.register(GuiBridge.menuType(), LegacyContainerScreen::new);
    }"""),
        ("import net.minecraftforge.client.event.RegisterMenuScreensEvent;\n", ""),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/Client1710.java": [
        ("        modBus.addListener(ClientGui::onRegisterScreens);", "        ClientGui.registerScreens();"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/client/ConfigScreens1122.java": [
        ("import net.minecraftforge.client.gui.IConfigScreenFactory;\n", ""),
        (" * factory, the default config screen); here NeoForge's mod list does, through the {@link IConfigScreenFactory} registered on the mod's",
         " * factory, the default config screen); here Forge's mod list does, through the {@code ConfigScreenHandler.ConfigScreenFactory}\n * registered on the mod's"),
        ("            mod.container.registerExtensionPoint(IConfigScreenFactory.class, (IConfigScreenFactory) (container, parent) -> open(mod, parent));",
         "            mod.container.registerExtensionPoint(net.minecraftforge.client.ConfigScreenHandler.ConfigScreenFactory.class,\n"
         "                    () -> new net.minecraftforge.client.ConfigScreenHandler.ConfigScreenFactory((mc, parent) -> open(mod, parent)));"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/LegacyConfigScreens.java": [
        ("import net.minecraftforge.client.gui.IConfigScreenFactory;\n", ""),
        (" * {@link IConfigScreenFactory} registered on the mod's container. The legacy screen's parent is {@link ModernParent}, so its Done",
         " * {@code ConfigScreenHandler.ConfigScreenFactory} registered on the mod's container. The legacy screen's parent is\n * {@link ModernParent}, so its Done"),
        ("            mod.container.registerExtensionPoint(IConfigScreenFactory.class, (IConfigScreenFactory) (container, parent) -> open(mod, parent));",
         "            mod.container.registerExtensionPoint(net.minecraftforge.client.ConfigScreenHandler.ConfigScreenFactory.class,\n"
         "                    () -> new net.minecraftforge.client.ConfigScreenHandler.ConfigScreenFactory((mc, parent) -> open(mod, parent)));"),
    ],
}

for path, pairs in EDITS.items():
    src = open(path, encoding="utf-8").read()
    for old, new in pairs:
        n = src.count(old)
        if n != 1:
            print(f"ABORT {n} matches in {path}: {old.splitlines()[0][:70]!r}")
            sys.exit(1)
        src = src.replace(old, new)
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

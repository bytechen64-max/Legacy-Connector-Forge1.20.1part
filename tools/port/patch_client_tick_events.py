"""Forge 1.20.1 client tick events: ClientTickEvent.Pre/.Post (1.21) -> one TickEvent.ClientTickEvent with a phase guard.

Also fixes the leftover DeferredHolder declarations (Forge has RegistryObject) and the 1.20.1 path-type name.
"""
import sys

EDITS = {
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/bridge/EventBridge1122.java": [
        (
            """            bus.addListener((net.minecraftforge.client.event.ClientTickEvent.Pre e) -> {
                if (wants(TickEvent.ClientTickEvent.class)) post(new TickEvent.ClientTickEvent(TickEvent.Phase.START));
            });
            bus.addListener((net.minecraftforge.client.event.ClientTickEvent.Post e) -> {
                if (wants(TickEvent.ClientTickEvent.class)) post(new TickEvent.ClientTickEvent(TickEvent.Phase.END));
            });""",
            """            bus.addListener((net.minecraftforge.event.TickEvent.ClientTickEvent e) -> {
                if (e.phase != net.minecraftforge.event.TickEvent.Phase.START) return;
                if (wants(TickEvent.ClientTickEvent.class)) post(new TickEvent.ClientTickEvent(TickEvent.Phase.START));
            });
            bus.addListener((net.minecraftforge.event.TickEvent.ClientTickEvent e) -> {
                if (e.phase != net.minecraftforge.event.TickEvent.Phase.END) return;
                if (wants(TickEvent.ClientTickEvent.class)) post(new TickEvent.ClientTickEvent(TickEvent.Phase.END));
            });""",
        ),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/EventBridge1710.java": [
        (
            """        gameBus.addListener((net.minecraftforge.client.event.ClientTickEvent.Pre e) -> {
            if (wants(fml(), TickEvent.ClientTickEvent.class)) fml().post(new TickEvent.ClientTickEvent(TickEvent.Phase.START));
        });
        gameBus.addListener((net.minecraftforge.client.event.ClientTickEvent.Post e) -> {
            if (wants(fml(), TickEvent.ClientTickEvent.class)) fml().post(new TickEvent.ClientTickEvent(TickEvent.Phase.END));
        });""",
            """        gameBus.addListener((net.minecraftforge.event.TickEvent.ClientTickEvent e) -> {
            if (e.phase != net.minecraftforge.event.TickEvent.Phase.START) return;
            if (wants(fml(), TickEvent.ClientTickEvent.class)) fml().post(new TickEvent.ClientTickEvent(TickEvent.Phase.START));
        });
        gameBus.addListener((net.minecraftforge.event.TickEvent.ClientTickEvent e) -> {
            if (e.phase != net.minecraftforge.event.TickEvent.Phase.END) return;
            if (wants(fml(), TickEvent.ClientTickEvent.class)) fml().post(new TickEvent.ClientTickEvent(TickEvent.Phase.END));
        });""",
        ),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/client/ClientEvents1122.java": [
        (
            "bus.addListener((net.minecraftforge.client.event.ClientTickEvent.Post e) -> tickMusic());",
            "bus.addListener((net.minecraftforge.event.TickEvent.ClientTickEvent e) -> {\n"
            "            if (e.phase == net.minecraftforge.event.TickEvent.Phase.END) tickMusic();\n"
            "        });",
        ),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/client/LegacyParticles1122.java": [
        ("import net.minecraftforge.client.event.ClientTickEvent;", "import net.minecraftforge.event.TickEvent;"),
        (
            "private static void onTick(ClientTickEvent.Post event) {",
            "private static void onTick(TickEvent.ClientTickEvent event) {\n        if (event.phase != TickEvent.Phase.END) return;",
        ),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/LegacyMusic.java": [
        ("import net.minecraftforge.client.event.ClientTickEvent;", "import net.minecraftforge.event.TickEvent;"),
        (
            "private static void onTick(ClientTickEvent.Post event) {",
            "private static void onTick(TickEvent.ClientTickEvent event) {\n        if (event.phase != TickEvent.Phase.END) return;",
        ),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/LegacyParticles.java": [
        ("import net.minecraftforge.client.event.ClientTickEvent;", "import net.minecraftforge.event.TickEvent;"),
        (
            "private static void onTick(ClientTickEvent.Post event) {",
            "private static void onTick(TickEvent.ClientTickEvent event) {\n        if (event.phase != TickEvent.Phase.END) return;",
        ),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/LegacyKeyConflicts.java": [
        ("import net.minecraftforge.client.event.ClientTickEvent;", "import net.minecraftforge.event.TickEvent;"),
        (
            "        MinecraftForge.EVENT_BUS.addListener((ClientTickEvent.Post e) -> {\n            if (!done) {",
            "        MinecraftForge.EVENT_BUS.addListener((TickEvent.ClientTickEvent e) -> {\n"
            "            if (e.phase != TickEvent.Phase.END) return;\n            if (!done) {",
        ),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/WorldScreenshotTest.java": [
        ("import net.minecraftforge.client.event.ClientTickEvent;", "import net.minecraftforge.event.TickEvent;"),
        (
            "MinecraftForge.EVENT_BUS.addListener((ClientTickEvent.Post e) -> onTick());",
            "MinecraftForge.EVENT_BUS.addListener((TickEvent.ClientTickEvent e) -> {\n"
            "            if (e.phase == TickEvent.Phase.END) onTick();\n        });",
        ),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/RenderEvents1710.java": [
        (
            "        MinecraftForge.EVENT_BUS.addListener(net.minecraftforge.eventbus.api.EventPriority.HIGHEST, (net.minecraftforge.client.event.ClientTickEvent.Pre e) -> {\n            var local = Minecraft.getInstance().player;",
            "        MinecraftForge.EVENT_BUS.addListener(net.minecraftforge.eventbus.api.EventPriority.HIGHEST, (net.minecraftforge.event.TickEvent.ClientTickEvent e) -> {\n"
            "            if (e.phase != net.minecraftforge.event.TickEvent.Phase.START) return;\n"
            "            var local = Minecraft.getInstance().player;",
        ),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/LegacyConnector.java": [
        (
            "public static final DeferredHolder<Feature<?>, LegacyWorldGenFeature> LEGACY_WORLDGEN =",
            "public static final RegistryObject<LegacyWorldGenFeature> LEGACY_WORLDGEN =",
        ),
        (
            "public static final DeferredHolder<net.minecraft.world.inventory.MenuType<?>, net.minecraft.world.inventory.MenuType<org.kylepitcock.legacyconnector.v1_7_10.gui.LegacyMenu>> LEGACY_MENU_1_7_10 =",
            "public static final RegistryObject<net.minecraft.world.inventory.MenuType<org.kylepitcock.legacyconnector.v1_7_10.gui.LegacyMenu>> LEGACY_MENU_1_7_10 =",
        ),
        (
            "public static final DeferredHolder<net.minecraft.world.inventory.MenuType<?>, net.minecraft.world.inventory.MenuType<org.kylepitcock.legacyconnector.v1_12_2.gui.LegacyMenu1122>> LEGACY_MENU_1_12_2 =",
            "public static final RegistryObject<net.minecraft.world.inventory.MenuType<org.kylepitcock.legacyconnector.v1_12_2.gui.LegacyMenu1122>> LEGACY_MENU_1_12_2 =",
        ),
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

# 1.20.5 renamed BlockPathTypes to PathType; 1.20.1 still has BlockPathTypes.
import os
changed = 0
for dirpath, _dirs, names in os.walk("src"):
    for n in names:
        if not n.endswith(".java"):
            continue
        p = os.path.join(dirpath, n)
        s = open(p, encoding="utf-8").read()
        if "net.minecraft.world.level.pathfinder.PathType" not in s:
            continue
        s2 = s.replace("net.minecraft.world.level.pathfinder.PathType",
                       "net.minecraft.world.level.pathfinder.BlockPathTypes")
        open(p, "w", encoding="utf-8", newline="").write(s2)
        changed += 1
print(f"BlockPathTypes rename in {changed} files")

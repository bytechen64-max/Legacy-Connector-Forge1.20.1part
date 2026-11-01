"""RenderFrameEvent is 1.20.1's TickEvent.RenderTickEvent; partial ticks are floats again; component leftovers."""
import sys

EDITS = {
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/bridge/EventBridge1122.java": [
        ("""            bus.addListener((net.minecraftforge.client.event.RenderFrameEvent.Pre e) -> {
                if (wants(TickEvent.RenderTickEvent.class)) post(new TickEvent.RenderTickEvent(TickEvent.Phase.START, e.getPartialTick().getGameTimeDeltaPartialTick(false)));
            });
            bus.addListener((net.minecraftforge.client.event.RenderFrameEvent.Post e) -> {
                if (wants(TickEvent.RenderTickEvent.class)) post(new TickEvent.RenderTickEvent(TickEvent.Phase.END, e.getPartialTick().getGameTimeDeltaPartialTick(false)));
            });""",
         """            // 1.21 renders a frame with RenderFrameEvent; 1.20.1 fires one RenderTickEvent per phase.
            bus.addListener((net.minecraftforge.event.TickEvent.RenderTickEvent e) -> {
                if (e.phase != net.minecraftforge.event.TickEvent.Phase.START) return;
                if (wants(TickEvent.RenderTickEvent.class)) post(new TickEvent.RenderTickEvent(TickEvent.Phase.START, e.partialTick));
            });
            bus.addListener((net.minecraftforge.event.TickEvent.RenderTickEvent e) -> {
                if (e.phase != net.minecraftforge.event.TickEvent.Phase.END) return;
                if (wants(TickEvent.RenderTickEvent.class)) post(new TickEvent.RenderTickEvent(TickEvent.Phase.END, e.partialTick));
            });"""),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/client/ClientEvents1122.java": [
        ("        bus.addListener((net.minecraftforge.client.event.RenderFrameEvent.Pre e) -> frame++);",
         "        bus.addListener((net.minecraftforge.event.TickEvent.RenderTickEvent e) -> {\n"
         "            if (e.phase == net.minecraftforge.event.TickEvent.Phase.START) frame++;\n"
         "        });"),
        ("        bus.addListener((net.minecraftforge.client.event.RenderFrameEvent.Post e) -> Minecraft1122.recordFrame());",
         "        bus.addListener((net.minecraftforge.event.TickEvent.RenderTickEvent e) -> {\n"
         "            if (e.phase == net.minecraftforge.event.TickEvent.Phase.END) Minecraft1122.recordFrame();\n"
         "        });"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/ClientEvents1710.java": [
        ("        bus.addListener((net.minecraftforge.client.event.RenderFrameEvent.Pre e) -> frame++);",
         "        bus.addListener((net.minecraftforge.event.TickEvent.RenderTickEvent e) -> {\n"
         "            if (e.phase == net.minecraftforge.event.TickEvent.Phase.START) frame++;\n"
         "        });"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/LegacyParticles.java": [
        ("effects().mcc$render(event.getPartialTick().getGameTimeDeltaPartialTick(false), rx, rxz, rz, ryz, rxy, event.getFrustum(",
         "effects().mcc$render(event.getPartialTick(), rx, rxz, rz, ryz, rxy, event.getFrustum("),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/RenderEvents1710.java": [
        ("        legacyconnector.v1_7_10.net.minecraft.util.Timer.mcc$frame(e.getPartialTick().getGameTimeDeltaPartialTick(false));",
         "        legacyconnector.v1_7_10.net.minecraft.util.Timer.mcc$frame(e.getPartialTick());"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/client/LegacyParticles1122.java": [
        ("        float partial = event.getPartialTick().getGameTimeDeltaPartialTick(false);",
         "        float partial = event.getPartialTick();"),
    ],
    # FOOD / MAX_DAMAGE components are item methods again
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/bridge/Vanilla1122.java": [
        ("        var food = modern == null ? null : modern.components().get(net.minecraft.core.component.DataComponents.FOOD);",
         "        var food = modern == null ? null : modern.getFoodProperties();"),
        ("        if (meta <= 0 || meta == 32767 || base.components().has(net.minecraft.core.component.DataComponents.MAX_DAMAGE)) return",
         "        if (meta <= 0 || meta == 32767 || !base.isDamageableItem()) return"),
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

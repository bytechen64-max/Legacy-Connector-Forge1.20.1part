"""1.20.1 has no IClientMobEffectExtensions: drop the effect-extension registration, keep the drawing helper."""
import sys

P = r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/client/EffectIcons1122.java"
src = open(P, encoding="utf-8").read()
start = src.find("    public static void register(RegisterClientExtensionsEvent event) {")
if start < 0:
    print("ABORT: register not found")
    sys.exit(1)
marker = "        }, effects.toArray(new MobEffect[0]));\n    }\n"
end = src.find(marker, start)
if end < 0:
    print("ABORT: end not found")
    sys.exit(1)
replacement = """    /**
     * 1.20.1 has no {@code IClientMobEffectExtensions} (NeoForge's per-effect client extensions are 1.21), so there is no hook to
     * register here; {@link #draw} stays available for the client mixin that draws legacy effect icons (see PORTING.md).
     */
    public static void register() {
    }
"""
src = src[:start] + replacement + src[end + len(marker):]
src = src.replace("import net.minecraftforge.client.extensions.common.IClientMobEffectExtensions;\n", "")
src = src.replace("import net.minecraftforge.client.extensions.common.RegisterClientExtensionsEvent;\n", "")
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P)

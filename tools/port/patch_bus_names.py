"""Two bus names collapsed into one by the NeoForge -> Forge rename: separate them again.

In these bridge files `MinecraftForge` meant the *legacy* shim bus before the port (posted legacy events,
`mcc$hasListeners`), and `NeoForge.EVENT_BUS` meant Forge's bus (modern listeners). After the rename both read
`MinecraftForge.EVENT_BUS`. The modern `net.minecraftforge.common.MinecraftForge` import is kept (it serves the
`addListener` calls) and the legacy-bus operations get their fully qualified name.
"""
import sys

LEGACY_1122 = "legacyconnector.v1_12_2.net.minecraftforge.common.MinecraftForge"
LEGACY_1710 = "legacyconnector.v1_7_10.net.minecraftforge.common.MinecraftForge"

FILES = {
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/client/ClientEvents1122.java": LEGACY_1122,
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/client/ScreenEvents1122.java": LEGACY_1122,
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/HudEvents1710.java": LEGACY_1710,
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/RenderEvents1710.java": LEGACY_1710,
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/ScreenEvents1710.java": LEGACY_1710,
}

for path, legacy in FILES.items():
    src = open(path, encoding="utf-8").read()
    if src.count("MinecraftForge.EVENT_BUS.mcc$hasListeners(") + src.count("MinecraftForge.EVENT_BUS.post(") == 0:
        print("ABORT: no legacy bus use in", path)
        sys.exit(1)
    src = src.replace("MinecraftForge.EVENT_BUS.mcc$hasListeners(", legacy + ".EVENT_BUS.mcc$hasListeners(")
    src = src.replace("MinecraftForge.EVENT_BUS.post(", legacy + ".EVENT_BUS.post(")
    # the legacy class itself is no longer referenced by simple name
    legacy_import = "import " + legacy + ";\n"
    if legacy_import not in src:
        print("ABORT: legacy import not found in", path)
        sys.exit(1)
    src = src.replace(legacy_import, "")
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

# EventBridge1710: the legacy LivingHurtEvent import shadows the modern class the two listeners take.
P = r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/EventBridge1710.java"
src = open(P, encoding="utf-8").read()
pairs = [
    ("import net.minecraftforge.event.entity.living.LivingHurtEvent;\n", ""),
    ("gameBus.addListener((LivingIncomingDamageEvent e) -> {\n            boolean attack",
     "gameBus.addListener((net.minecraftforge.event.entity.living.LivingHurtEvent e) -> {\n            boolean attack"),
    ("gameBus.addListener((LivingIncomingDamageEvent e) -> specialArmor(e));",
     "gameBus.addListener((net.minecraftforge.event.entity.living.LivingHurtEvent e) -> specialArmor(e));"),
]
for old, new in pairs:
    if src.count(old) != 1:
        print("ABORT EventBridge1710:", src.count(old), old[:60])
        sys.exit(1)
    src = src.replace(old, new)
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P)

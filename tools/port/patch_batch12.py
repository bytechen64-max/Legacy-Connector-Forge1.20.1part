"""authlib's Property accessor, the model map type, and the client-extension registrations that 1.20.1 lacks."""
import sys

EDITS = {
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/nbt/NBTUtil.java": [
        ("                    if (property.signature() != null) p.setString(\"Signature\", property.signature());",
         "                    // authlib names the accessor getSignature() (the record-style one is newer).\n"
         "                    if (property.hasSignature()) p.setString(\"Signature\", property.getSignature());"),
    ],
    r"src/main/java/legacyconnector/v1_7_10/net/minecraft/nbt/NBTUtil.java": [
        ("                if (property.hasSignature()) entry.setString(\"Signature\", property.signature());",
         "                if (property.hasSignature()) entry.setString(\"Signature\", property.getSignature());"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/SharedItemModels.java": [
        ("        Map<ModelResourceLocation, BakedModel> models = event.getModels();",
         "        // 1.20.1's baking event maps plain ResourceLocations (ModelResourceLocation keys are 1.20.5).\n"
         "        Map<net.minecraft.resources.ResourceLocation, BakedModel> models = event.getModels();"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/client/Client1122.java": [
        ("""        // status icons of mod potions (the modern effect sprites do not exist for them)
        modBus.addListener((net.minecraftforge.client.extensions.common.RegisterClientExtensionsEvent e) -> {
            if (present()) EffectIcons1122.register(e);
        });
""",
         """        // status icons of mod potions: 1.20.1 has no per-effect client extensions to register (see PORTING.md)
        if (present()) EffectIcons1122.register();
"""),
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

"""1.20.1 names attribute modifiers and sounds with a plain String (the ResourceLocation ids are 1.20.5+)."""
import sys

EDITS = {
    r"src/main/java/legacyconnector/v1_7_10/net/minecraft/entity/Entity.java": [
        ("                        attr.addTransientModifier(new net.minecraft.world.entity.ai.attributes.AttributeModifier(id, wanted,",
         "                        attr.addTransientModifier(new net.minecraft.world.entity.ai.attributes.AttributeModifier(id.toString(), wanted,"),
    ],
    r"src/main/java/legacyconnector/v1_7_10/net/minecraft/entity/ai/attributes/AttributeModifier.java": [
        ("        return new net.minecraft.world.entity.ai.attributes.AttributeModifier(mcc$id(id), amount, op);",
         "        return new net.minecraft.world.entity.ai.attributes.AttributeModifier(mcc$id(id).toString(), amount, op);"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/LegacySoundFiles.java": [
        ("        this.sound = new Sound(id, ConstantFloat.of(1.0F), ConstantFloat.of(1.0F), 1, Sound.Type.FILE, stream, false, 16);",
         "        // 1.20.1 names a sound with its id as a string (the ResourceLocation form is 1.20.5).\n"
         "        this.sound = new Sound(id.toString(), ConstantFloat.of(1.0F), ConstantFloat.of(1.0F), 1, Sound.Type.FILE, stream, false, 16);"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/client/LegacySoundSystem1122.java": [
        ("        this.sound = new Sound(ID, ConstantFloat.of(1.0F), ConstantFloat.of(1.0F), 1, Sound.Type.FILE, true, false, (int) src.distance);",
         "        // 1.20.1 names a sound with its id as a string (the ResourceLocation form is 1.20.5).\n"
         "        this.sound = new Sound(ID.toString(), ConstantFloat.of(1.0F), ConstantFloat.of(1.0F), 1, Sound.Type.FILE, true, false, (int) src.distance);"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/entity/Effects1122.java": [
        ("            effect.addAttributeModifier(attribute, ResourceLocation.fromNamespaceAndPath(id.getNamespace(), id.getPath() + \"_\" + mod.getID().toString().toLowerCase(java.util.Locale.ROOT)),",
         "            effect.addAttributeModifier(attribute, ResourceLocation.fromNamespaceAndPath(id.getNamespace(), id.getPath() + \"_\" + mod.getID().toString().toLowerCase(java.util.Locale.ROOT)).toString(),"),
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

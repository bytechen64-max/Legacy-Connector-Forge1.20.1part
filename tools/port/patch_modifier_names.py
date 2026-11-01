"""1.20.1's AttributeModifier is named by a String (the ResourceLocation id is 1.21) and operations have no id()."""
import sys

EDITS = {
    r"src/main/java/legacyconnector/v1_7_10/net/minecraft/entity/ai/attributes/AttributeModifier.java": [
        ("""    public static AttributeModifier mcc$wrap(net.minecraft.world.entity.ai.attributes.AttributeModifier m) {
        ResourceLocation rl = m.id();
        UUID id;
        if (rl.getNamespace().equals("legacyconnector") && rl.getPath().startsWith("legacy/")) {
            try {
                id = UUID.fromString(rl.getPath().substring("legacy/".length()));
            } catch (IllegalArgumentException e) {
                id = UUID.nameUUIDFromBytes(rl.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
            }
        } else {
            id = UUID.nameUUIDFromBytes(rl.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
        }
        return new AttributeModifier(id, rl.toString(), m.getAmount(), m.getOperation().id());
    }""",
         """    public static AttributeModifier mcc$wrap(net.minecraft.world.entity.ai.attributes.AttributeModifier m) {
        // 1.20.1 names a modifier with a plain String (the ResourceLocation id is 1.21).
        String name = m.getName();
        UUID id;
        if (name.startsWith("legacyconnector:legacy/")) {
            try {
                id = UUID.fromString(name.substring("legacyconnector:legacy/".length()));
            } catch (IllegalArgumentException e) {
                id = UUID.nameUUIDFromBytes(name.getBytes(java.nio.charset.StandardCharsets.UTF_8));
            }
        } else {
            id = UUID.nameUUIDFromBytes(name.getBytes(java.nio.charset.StandardCharsets.UTF_8));
        }
        return new AttributeModifier(id, name, m.getAmount(), m.getOperation().ordinal());
    }"""),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/entity/AttributeView1122.java": [
        ("""    private static AttributeModifier legacy(net.minecraft.world.entity.ai.attributes.AttributeModifier m) {
        String path = m.id().getPath();
        UUID uuid;
        try {
            uuid = path.startsWith("modifier/") ? UUID.fromString(path.substring(9)) : UUID.nameUUIDFromBytes(m.id().toString().getBytes());
        } catch (IllegalArgumentException e) {
            uuid = UUID.nameUUIDFromBytes(m.id().toString().getBytes());
        }
        return new AttributeModifier(uuid, m.id().toString(), m.getAmount(), m.getOperation().ordinal());
    }""",
         """    private static AttributeModifier legacy(net.minecraft.world.entity.ai.attributes.AttributeModifier m) {
        // 1.20.1 names a modifier with a plain String (the ResourceLocation id is 1.21).
        String name = m.getName();
        String path = name.startsWith("legacyconnector:") ? name.substring("legacyconnector:".length()) : name;
        UUID uuid;
        try {
            uuid = path.startsWith("modifier/") ? UUID.fromString(path.substring(9)) : UUID.nameUUIDFromBytes(name.getBytes());
        } catch (IllegalArgumentException e) {
            uuid = UUID.nameUUIDFromBytes(name.getBytes());
        }
        return new AttributeModifier(uuid, name, m.getAmount(), m.getOperation().ordinal());
    }"""),
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

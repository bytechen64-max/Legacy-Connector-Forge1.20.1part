"""1.20.1 attributes are plain Attribute objects (the Holder form is 1.20.5+)."""
import sys

# IAttribute: the modern attribute is an Attribute, not a Holder
P = r"src/main/java/legacyconnector/v1_12_2/net/minecraft/entity/ai/attributes/IAttribute.java"
src = open(P, encoding="utf-8").read()
pairs = [
    ("""    default net.minecraft.core.Holder<net.minecraft.world.entity.ai.attributes.Attribute> mcc$modern() {
        return mcc$modernByName(getName());
    }""",
     """    default net.minecraft.world.entity.ai.attributes.Attribute mcc$modern() {
        return mcc$modernByName(getName());
    }"""),
    ("    static net.minecraft.core.Holder<net.minecraft.world.entity.ai.attributes.Attribute> mcc$modernByName(String name) {",
     "    static net.minecraft.world.entity.ai.attributes.Attribute mcc$modernByName(String name) {"),
    ("        return org.kylepitcock.legacyconnector.core.RegistryUtil.holder(net.minecraft.core.registries.BuiltInRegistries.ATTRIBUTE, id).map(h -> (net.minecraft.core.Holder<net.minecraft.world.entity.ai.attributes.Attribute>) h).orElse(null);",
     "        // 1.20.1 keeps the attribute itself in the registry (1.20.5 wraps it in a holder).\n"
     "        return net.minecraft.core.registries.BuiltInRegistries.ATTRIBUTE.get(id);"),
]
for old, new in pairs:
    if src.count(old) != 1:
        print(f"ABORT IAttribute {src.count(old)}: {old.strip()[:60]}")
        sys.exit(1)
    src = src.replace(old, new)
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P)

# SharedMonsterAttributes follows
P = r"src/main/java/legacyconnector/v1_7_10/net/minecraft/entity/SharedMonsterAttributes.java"
src = open(P, encoding="utf-8").read()
pairs = [
    ("    public static Holder<Attribute> mcc$modern(IAttribute attribute) {",
     "    public static Attribute mcc$modern(IAttribute attribute) {"),
    ("        Holder<Attribute> holder = mcc$modern(attribute);\n        if (holder == null) return null;\n        AttributeInstance instance = entity.getAttribute(holder);",
     "        Attribute modern = mcc$modern(attribute);\n        if (modern == null) return null;\n        AttributeInstance instance = entity.getAttribute(modern);"),
]
for old, new in pairs:
    if src.count(old) != 1:
        print(f"ABORT SharedMonsterAttributes {src.count(old)}: {old.strip()[:60]}")
        sys.exit(1)
    src = src.replace(old, new)
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P)

"""CustomData / CUSTOM_NAME / REPAIR_COST (1.20.5 components) -> the item tag through core.data.ItemData."""
import os
import re
import sys

ITEM_DATA = "import org.kylepitcock.legacyconnector.core.data.ItemData;"

# (file, [(old, new, expected)]) -- exact text, one occurrence each unless stated
EDITS = {
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/item/ItemStack.java": [
        ("this.mcc$seenData = backing.get(net.minecraft.core.component.DataComponents.CUSTOM_DATA);",
         "this.mcc$seenData = org.kylepitcock.legacyconnector.core.data.ItemData.customData(backing);", 1),
        ("var data = b.get(net.minecraft.core.component.DataComponents.CUSTOM_DATA);",
         "var data = org.kylepitcock.legacyconnector.core.data.ItemData.customData(b);", 1),
        ("stackTagCompound = data == null ? null : new NBTTagCompound(data.copyTag());",
         "stackTagCompound = data == null ? null : new NBTTagCompound(data.copy());", 1),
        ("if (stackTagCompound == null || stackTagCompound.isEmpty()) b.remove(net.minecraft.core.component.DataComponents.CUSTOM_DATA);\n"
         "        else b.set(net.minecraft.core.component.DataComponents.CUSTOM_DATA, net.minecraft.world.item.component.CustomData.of(stackTagCompound.mcc$modern()));\n"
         "        mcc$seenData = b.get(net.minecraft.core.component.DataComponents.CUSTOM_DATA);",
         "if (stackTagCompound == null || stackTagCompound.isEmpty()) org.kylepitcock.legacyconnector.core.data.ItemData.removeCustomData(b);\n"
         "        else org.kylepitcock.legacyconnector.core.data.ItemData.setCustomData(b, stackTagCompound.mcc$modern());\n"
         "        mcc$seenData = org.kylepitcock.legacyconnector.core.data.ItemData.customData(b);", 1),
    ],
    r"src/main/java/legacyconnector/v1_7_10/net/minecraft/item/ItemStack.java": [
        ("return mcc$stack.get(DataComponents.CUSTOM_DATA) != null || (mcc$stack.isEmpty() && mcc$looseTag != null);",
         "return org.kylepitcock.legacyconnector.core.data.ItemData.hasCustomData(mcc$stack) || (mcc$stack.isEmpty() && mcc$looseTag != null);", 1),
        ("CustomData data = mcc$stack.get(DataComponents.CUSTOM_DATA);",
         "CompoundTag data = org.kylepitcock.legacyconnector.core.data.ItemData.customData(mcc$stack);", 1),
        ("NBTTagCompound view = new NBTTagCompound(data.copyTag());",
         "NBTTagCompound view = new NBTTagCompound(data.copy());", 1),
        ("private CustomData mcc$tagSource;", "private CompoundTag mcc$tagSource;", 1),
        ("mcc$stack.remove(DataComponents.CUSTOM_DATA);",
         "org.kylepitcock.legacyconnector.core.data.ItemData.removeCustomData(mcc$stack);", 1),
        ("        CustomData data = CustomData.of(tag.mcc$modern());\n"
         "        mcc$stack.set(DataComponents.CUSTOM_DATA, data);\n"
         "        mcc$tagSource = mcc$stack.get(DataComponents.CUSTOM_DATA);",
         "        org.kylepitcock.legacyconnector.core.data.ItemData.setCustomData(mcc$stack, tag.mcc$modern());\n"
         "        mcc$tagSource = org.kylepitcock.legacyconnector.core.data.ItemData.customData(mcc$stack);", 1),
        ("if (mcc$stack.has(DataComponents.CUSTOM_NAME)) return mcc$stack.getHoverName().getString();",
         "if (org.kylepitcock.legacyconnector.core.data.ItemData.hasCustomName(mcc$stack)) return mcc$stack.getHoverName().getString();", 1),
        ("mcc$stack.set(DataComponents.CUSTOM_NAME, Component.literal(name));",
         "org.kylepitcock.legacyconnector.core.data.ItemData.setCustomName(mcc$stack, Component.literal(name));", 1),
        ("mcc$stack.remove(DataComponents.CUSTOM_NAME);",
         "org.kylepitcock.legacyconnector.core.data.ItemData.clearCustomName(mcc$stack);", 1),
        ("return mcc$stack.has(DataComponents.CUSTOM_NAME);",
         "return org.kylepitcock.legacyconnector.core.data.ItemData.hasCustomName(mcc$stack);", 1),
        ("Integer cost = mcc$stack.get(DataComponents.REPAIR_COST);\n        return cost == null ? 0 : cost;",
         "return org.kylepitcock.legacyconnector.core.data.ItemData.repairCost(mcc$stack);", 1),
        ("mcc$stack.set(DataComponents.REPAIR_COST, cost);",
         "org.kylepitcock.legacyconnector.core.data.ItemData.setRepairCost(mcc$stack, cost);", 1),
        ("CustomData x = a.mcc$stack.get(DataComponents.CUSTOM_DATA);\n"
         "        CustomData y = b.mcc$stack.get(DataComponents.CUSTOM_DATA);\n"
         "        CompoundTag tx = x == null ? null : x.copyTag();\n"
         "        CompoundTag ty = y == null ? null : y.copyTag();",
         "CompoundTag tx = org.kylepitcock.legacyconnector.core.data.ItemData.customData(a.mcc$stack);\n"
         "        CompoundTag ty = org.kylepitcock.legacyconnector.core.data.ItemData.customData(b.mcc$stack);\n"
         "        tx = tx == null ? null : tx.copy();\n"
         "        ty = ty == null ? null : ty.copy();", 1),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/bridge/Stacks1122.java": [
        ("if (!data.isEmpty()) out.set(DataComponents.CUSTOM_DATA, CustomData.of(data));",
         "if (!data.isEmpty()) org.kylepitcock.legacyconnector.core.data.ItemData.setCustomData(out, data);", 1),
        ("if (data != null) out.setTagCompound(new NBTTagCompound(data.copyTag()));",
         "if (data != null) out.setTagCompound(new NBTTagCompound(data.copy()));", 1),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/adapter/ItemCallbacks.java": [
        ("var data = stack.get(net.minecraft.core.component.DataComponents.CUSTOM_DATA);",
         "var data = org.kylepitcock.legacyconnector.core.data.ItemData.customData(stack);", 1),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/Brewing1710.java": [
        ("CustomData data = stack.get(DataComponents.CUSTOM_DATA);",
         "net.minecraft.nbt.CompoundTag data = org.kylepitcock.legacyconnector.core.data.ItemData.customData(stack);", 1),
        ("if (data != null && data.contains(TAG)) return data.copyTag().getInt(TAG);",
         "if (data != null && data.contains(TAG)) return data.getInt(TAG);", 1),
        ("stack.set(DataComponents.CUSTOM_DATA, CustomData.of(tag));",
         "org.kylepitcock.legacyconnector.core.data.ItemData.setCustomData(stack, tag);", 1),
        ("CustomData data = input.get(DataComponents.CUSTOM_DATA);",
         "net.minecraft.nbt.CompoundTag data = org.kylepitcock.legacyconnector.core.data.ItemData.customData(input);", 1),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/bridge/SynthBlocks1122.java": [
        ("net.minecraft.world.item.component.CustomData.of(tag.getCompoundTag(\"EntityTag\").mcc$modern()));",
         "tag.getCompoundTag(\"EntityTag\").mcc$modern());", 1),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/compat/jei/LegacyConnectorJeiPlugin.java": [
        ("var custom = stack.get(net.minecraft.core.component.DataComponents.CUSTOM_DATA);\n"
         "                    if (custom != null && !custom.isEmpty()) data.append(custom.copyTag());",
         "var custom = org.kylepitcock.legacyconnector.core.data.ItemData.customData(stack);\n"
         "                    if (custom != null && !custom.isEmpty()) data.append(custom);", 1),
    ],
}

for path, pairs in EDITS.items():
    src = open(path, encoding="utf-8").read()
    for old, new, expected in pairs:
        n = src.count(old)
        if n != expected:
            print(f"ABORT {n} matches (want {expected}) in {path}: {old.splitlines()[0][:70]!r}")
            sys.exit(1)
        src = src.replace(old, new)
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

# drop the imports that no longer resolve, and note the tag type where it is used unqualified
for path in EDITS:
    src = open(path, encoding="utf-8").read()
    before = src
    src = src.replace("import net.minecraft.core.component.DataComponents;\n", "")
    src = src.replace("import net.minecraft.world.item.component.CustomData;\n", "")
    if re.search(r"(?<![\w.])CompoundTag\b", src) and "import net.minecraft.nbt.CompoundTag;" not in src:
        src = src.replace("import ", "import net.minecraft.nbt.CompoundTag;\nimport ", 1)
    if src != before:
        open(path, "w", encoding="utf-8", newline="").write(src)
        print("  imports cleaned:", path)
print("done")

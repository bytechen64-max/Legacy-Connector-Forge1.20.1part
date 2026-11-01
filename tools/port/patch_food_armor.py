"""1.20.1 asks the item for its food properties and keeps armor dye in display.color."""
import sys

EDITS = {
    r"src/main/java/legacyconnector/v1_7_10/net/minecraft/item/ItemFood.java": [
        ("net.minecraft.world.food.FoodProperties food = modern == null ? null : modern.components().get(net.minecraft.core.component.DataComponents.FOOD);",
         "// 1.20.1 asks the item for its food properties (the FOOD data component is 1.20.5).\n"
         "        net.minecraft.world.food.FoodProperties food = modern == null ? null : modern.getFoodProperties();"),
    ],
    r"src/main/java/legacyconnector/v1_7_10/net/minecraft/item/ItemArmor.java": [
        ("if (mcc$vanilla != null) return ItemStack.mcc$toModern(stack).has(net.minecraft.core.component.DataComponents.DYED_COLOR);",
         "if (mcc$vanilla != null) {\n"
         "            // 1.20.1 keeps the dye in display.color (the DYED_COLOR component is 1.20.5).\n"
         "            var t = ItemStack.mcc$toModern(stack).getTag();\n"
         "            return t != null && t.contains(\"display\", 10) && t.getCompound(\"display\").contains(\"color\", 3);\n"
         "        }"),
    ],
}

for path, pairs in EDITS.items():
    src = open(path, encoding="utf-8").read()
    for old, new in pairs:
        n = src.count(old)
        if n != 1:
            print(f"ABORT {n} in {path}: {old[:60]}")
            sys.exit(1)
        src = src.replace(old, new)
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

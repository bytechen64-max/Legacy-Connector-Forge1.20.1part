"""1.20.1: ItemAbility/ItemAbilities -> ToolAction/ToolActions, and SynchedEntityData.Builder -> defineSynchedData()."""
import os
import re
import sys

# ---------------------------------------------------------------- ItemAbility -> ToolAction
changed = []
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        src = open(p, encoding="utf-8").read()
        if "ItemAbilit" not in src:
            continue
        before = src
        src = src.replace("net.minecraftforge.common.ItemAbilities.", "net.minecraftforge.common.ToolActions.")
        src = src.replace("net.minecraftforge.common.ItemAbility", "net.minecraftforge.common.ToolAction")
        # the event accessor was renamed with the type
        src = src.replace(".getItemAbility()", ".getToolAction()")
        if src != before:
            open(p, "w", encoding="utf-8", newline="").write(src)
            changed.append(p)
print("ItemAbility -> ToolAction in", len(changed), "files")
for c in changed:
    print("  ", c)

# ---------------------------------------------------------------- defineSynchedData
SITES = {
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/entity/EntityHost1122.java": [
        ("    protected void defineSynchedData(SynchedEntityData.Builder builder) {\n        builder.define(DATA, new CompoundTag());",
         "    protected void defineSynchedData() {\n        entityData.define(DATA, new CompoundTag());"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/entity/MobHost1122.java": [
        ("    protected void defineSynchedData(SynchedEntityData.Builder builder) {\n        super.defineSynchedData(builder);",
         "    protected void defineSynchedData() {\n        super.defineSynchedData();"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/entity/LegacyEntityHost.java": [
        ("    protected void defineSynchedData(SynchedEntityData.Builder builder) {\n        builder.define(",
         "    protected void defineSynchedData() {\n        entityData.define("),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/entity/LegacyMobHost.java": [
        ("    protected void defineSynchedData(SynchedEntityData.Builder builder) {\n        super.defineSynchedData(builder);",
         "    protected void defineSynchedData() {\n        super.defineSynchedData();"),
    ],
}
for path, pairs in SITES.items():
    src = open(path, encoding="utf-8").read()
    for old, new in pairs:
        n = src.count(old)
        if n != 1:
            print(f"ABORT {n} matches in {path}: {old.splitlines()[0][:60]!r}")
            sys.exit(1)
        src = src.replace(old, new)
    # builder.define(...) -> entityData.define(...) in the rest of the method body
    src = src.replace("        builder.define(", "        entityData.define(")
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

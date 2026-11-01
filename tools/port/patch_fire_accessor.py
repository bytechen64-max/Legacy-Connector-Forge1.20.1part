"""fire.setFlammable goes through the FireBlockAccess invoker; the effect holder lookup uses RegistryUtil."""
import io
import json
import sys

ACCESS = "((org.kylepitcock.legacyconnector.mixin.access.FireBlockAccess) net.minecraft.world.level.block.Blocks.FIRE).legacyconnector$setFlammable("

EDITS = {
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/block/BlockFire.java": [
        ("((net.minecraft.world.level.block.FireBlock) net.minecraft.world.level.block.Blocks.FIRE).setFlammable(m, encouragement, flammability);",
         "// 1.20.1 keeps setFlammable private: the invoker mixin reaches it (see FireBlockAccess).\n"
         "        " + ACCESS + "m, encouragement, flammability);"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/bridge/SynthBlocks1122.java": [
        ("((net.minecraft.world.level.block.FireBlock) net.minecraft.world.level.block.Blocks.FIRE).setFlammable(modern, Synth.toInt(args[1]), Synth.toInt(args[2]));",
         ACCESS + "modern, Synth.toInt(args[1]), Synth.toInt(args[2]));"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/bridge/SynthItems1122.java": [
        ("((net.minecraft.world.level.block.FireBlock) net.minecraft.world.level.block.Blocks.FIRE).setFlammable(modern, Synth.toInt(args[1]), Synth.toInt(args[2]));",
         ACCESS + "modern, Synth.toInt(args[1]), Synth.toInt(args[2]));"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/advancements/critereon/EntityPredicate.java": [
        ("        var effect = net.minecraft.core.registries.BuiltInRegistries.MOB_EFFECT.getHolder(e.getKey().mcc$modern()).orElse(null);",
         "        // 1.20.1 looks a registry entry up by id and wraps the value itself.\n"
         "        var effect = org.kylepitcock.legacyconnector.core.RegistryUtil.holder(\n"
         "                net.minecraft.core.registries.BuiltInRegistries.MOB_EFFECT, e.getKey().mcc$modern()).orElse(null);"),
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

CFG = "src/main/resources/legacyconnector.mixins.json"
cfg = json.load(io.open(CFG, encoding="utf-8-sig"))
if "access.FireBlockAccess" not in cfg["mixins"]:
    cfg["mixins"].insert(0, "access.FireBlockAccess")
io.open(CFG, "w", encoding="utf-8", newline="\n").write(json.dumps(cfg, indent=2) + "\n")
assert not open(CFG, "rb").read().startswith(b"\xef\xbb\xbf")
print("registered access.FireBlockAccess")

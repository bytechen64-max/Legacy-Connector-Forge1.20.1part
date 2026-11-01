"""A batch of one-off 1.20.1 mappings found by scanning every remaining error site."""
import sys

EDITS = {
    # reach: Forge's BLOCK_REACH attribute
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/server/management/PlayerInteractionManager.java": [
        ("        return sp != null ? sp.blockInteractionRange() : mcc$reach;",
         "        // 1.20.5 has blockInteractionRange(); 1.20.1 reads Forge's reach attribute.\n"
         "        return sp != null\n"
         "                ? (float) sp.getAttributeValue(net.minecraftforge.common.ForgeMod.BLOCK_REACH.get())\n"
         "                : mcc$reach;"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/client/multiplayer/PlayerControllerMP.java": [
        ("        return p == null ? 4.5F : (float) p.blockInteractionRange();",
         "        // 1.20.5 has blockInteractionRange(); 1.20.1 reads Forge's reach attribute.\n"
         "        return p == null ? 4.5F : (float) p.getAttributeValue(net.minecraftforge.common.ForgeMod.BLOCK_REACH.get());"),
    ],
    # the effect tick predicate keeps its 1.20.1 name
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/potion/Potion.java": [
        ("        return modern.value().shouldApplyEffectTickThisTick(duration, amplifier);",
         "        return modern.value().isDurationEffectTick(duration, amplifier);"),
    ],
    # entities have no getRandom(): the level's random is used
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/entity/projectile/EntityFishHook.java": [
        ("        var random = m.getRandom();", "        var random = m.level().getRandom();"),
    ],
    # 1.20.1's NbtIo reads and writes compressed files, not paths
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/world/storage/IPlayerFileData.java": [
        ("        net.minecraft.nbt.NbtIo.writeCompressed(tag, tmp.toPath());",
         "        net.minecraft.nbt.NbtIo.writeCompressed(tag, tmp);"),
        ("        var tag = net.minecraft.nbt.NbtIo.readCompressed(file.toPath(), net.minecraft.nbt.NbtAccounter.UNLIMITED);",
         "        // 1.20.1 reads compressed NBT from a File (the Path/NbtAccounter overload is 1.20.2+).\n"
         "        var tag = net.minecraft.nbt.NbtIo.readCompressed(file);"),
    ],
    # level tick events are phase based again
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/entity/LiveStacks1122.java": [
        ("        game.addListener((net.minecraftforge.event.tick.LevelTickEvent.Post e) -> flushAll(e.getLevel().isClientSide() ? CLIENT : SERVER));",
         "        game.addListener((net.minecraftforge.event.TickEvent.LevelTickEvent e) -> {\n"
         "            if (e.phase != net.minecraftforge.event.TickEvent.Phase.END) return;\n"
         "            flushAll(e.level.isClientSide() ? CLIENT : SERVER);\n"
         "        });"),
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

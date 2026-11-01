"""Round-13 batch: chunk holders, item damage, saved data, post-attack hooks, reach, adventure placement."""
import sys

EDITS = {
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/world/World.java": [
        ("        var chunk = holder == null ? null : holder.getChunkIfPresent(net.minecraft.world.level.chunk.ChunkStatus.FULL);",
         "        // 1.20.1 hands out the whole chunk when it is there (no status argument).\n"
         "        var chunk = holder == null ? null : holder.getFullChunk();"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/item/ItemStack.java": [
        ("                b.hurtAndBreak(amount, l, slot);",
         "                // 1.20.1 damages through a callback that breaks the item in that slot (the EquipmentSlot overload is 1.21).\n"
         "                b.hurtAndBreak(amount, l, e -> e.broadcastBreakEvent(slot));"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/world/storage/MapStorage.java": [
        ("        public CompoundTag save(CompoundTag tag, HolderLookup.Provider registries) {",
         "        public CompoundTag save(CompoundTag tag) {"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/entity/Entity.java": [
        ("        net.minecraft.world.item.enchantment.EnchantmentHelper.doPostAttackEffects(sl, target.mcc$entity, source);",
         "        // 1.20.1 splits the 1.21 hook in two: hurt effects on the target, damage effects on the attacker's weapon.\n"
         "        if (target.mcc$entity instanceof net.minecraft.world.entity.LivingEntity victim) {\n"
         "            net.minecraft.world.item.enchantment.EnchantmentHelper.doPostHurtEffects(victim, attacker.mcc$entity);\n"
         "            net.minecraft.world.item.enchantment.EnchantmentHelper.doPostDamageEffects(victim, attacker.mcc$entity);\n"
         "        }"),
        ("        var random = m.getRandom();", "        var random = m.level().getRandom();"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/entity/player/EntityPlayer.java": [
        ("        return modern.canPlaceOnBlockInAdventureMode(new net.minecraft.world.level.block.state.pattern.BlockInWorld(mcc$player().level(),\n"
         "                pos.offset(facing.getOpposite()).mcc$modern(), false));",
         "        // 1.20.1 asks the same question as mayUseItemAt (canPlaceOnBlockInAdventureMode is 1.20.5+).\n"
         "        return mcc$player().mayUseItemAt(pos.offset(facing.getOpposite()).mcc$modern(), facing.mcc$modern(), modern);"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/item/Item.java": [
        ("        var end = eye.add(player.getViewVector(1.0F).scale(player.blockInteractionRange()));",
         "        // 1.20.1 has no blockInteractionRange(): Forge's reach attribute carries the same distance.\n"
         "        var end = eye.add(player.getViewVector(1.0F).scale(player.getAttributeValue(net.minecraftforge.common.ForgeMod.BLOCK_REACH.get())));"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/entity/projectile/EntityFireball.java": [
        ("            var d = m.getDeltaMovement();\n"
         "            if (d.lengthSqr() > 1.0E-7D) {\n"
         "                var u = d.normalize().scale(0.1D);",
         "            var dir = m.getDeltaMovement();\n"
         "            if (dir.lengthSqr() > 1.0E-7D) {\n"
         "                var u = dir.normalize().scale(0.1D);"),
    ],
}

for path, pairs in EDITS.items():
    src = open(path, encoding="utf-8").read()
    for old, new in pairs:
        n = src.count(old)
        if n != 1:
            print(f"ABORT {n} matches in {path}: {old.strip()[:70]}")
            sys.exit(1)
        src = src.replace(old, new)
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

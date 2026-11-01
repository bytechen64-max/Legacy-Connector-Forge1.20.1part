"""Round-12 batch: entity step/lerp/fire, loot params, ping, chunk accessors, explosion radius."""
import sys

EDITS = {
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/entity/Entity.java": [
        ("    /** The modern step height is an attribute of living entities: a mod's value becomes its base. */\n"
         "    public static void mcc$set$stepHeight(Entity e, float v) {\n"
         "        e.mcc$local_stepHeight = v;\n"
         "        if (e.mcc$entity instanceof net.minecraft.world.entity.LivingEntity l) {\n"
         "            var a = l.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.STEP_HEIGHT);\n"
         "            if (a != null) a.setBaseValue(v);\n"
         "        }\n"
         "    }",
         "    /** 1.20.1 keeps the step height on the entity itself (1.20.5 made it an attribute). */\n"
         "    public static void mcc$set$stepHeight(Entity e, float v) {\n"
         "        e.mcc$local_stepHeight = v;\n"
         "        if (e.mcc$entity != null) e.mcc$entity.setMaxUpStep(v);\n"
         "    }"),
        ("            mcc$entity.lerpTo(x, y, z, yaw, pitch, increments);",
         "            mcc$entity.lerpTo(x, y, z, yaw, pitch, increments, false);"),
        ("        if (mcc$entity != null) mcc$entity.igniteForSeconds(seconds);",
         "        if (mcc$entity != null) mcc$entity.setSecondsOnFire(seconds);"),
        ("        return mcc$entity == null || mcc$entity.canUsePortal(false);",
         "        return mcc$entity == null || mcc$entity.canChangeDimensions();"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/entity/item/EntityItem.java": [
        ("        if (player != null) i.setThrower(player);", "        if (player != null) i.setThrower(player.getUUID());"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/world/storage/loot/LootContext.java": [
        ("net.minecraft.world.level.storage.loot.parameters.LootContextParams.ATTACKING_ENTITY",
         "net.minecraft.world.level.storage.loot.parameters.LootContextParams.KILLER_ENTITY"),
        ("net.minecraft.world.level.storage.loot.parameters.LootContextParams.DIRECT_ATTACKING_ENTITY",
         "net.minecraft.world.level.storage.loot.parameters.LootContextParams.DIRECT_KILLER_ENTITY"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/entity/player/EntityPlayerMP.java": [
        ("        return player == null || player.connection == null ? 0 : player.connection.latency();",
         "        // 1.20.1 keeps the ping on the player itself.\n"
         "        return player == null ? 0 : player.latency;"),
        ('        return sp == null ? "en_us" : sp.clientInformation().language();',
         '        return sp == null ? "en_us" : sp.getLanguage();'),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/network/NetHandlerPlayServer.java": [
        ("        return m == null ? null : NetworkManager.mcc$of(m.getConnection());",
         "        return m == null ? null : NetworkManager.mcc$of(m.connection);"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/world/gen/ChunkProviderServer.java": [
        ("            for (var holder : sl.getChunkSource().chunkMap.getChunks()) {",
         "            for (var holder : ((org.kylepitcock.legacyconnector.mixin.access.ChunkMapAccess) sl.getChunkSource().chunkMap).legacyconnector$chunks()) {"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/server/management/PlayerChunkMap.java": [
        ("        return level != null && level.getChunkSource().chunkMap.getVisibleChunkIfPresent(net.minecraft.world.level.ChunkPos.asLong(chunkX, chunkZ)) != null;",
         "        return level != null && ((org.kylepitcock.legacyconnector.mixin.access.ChunkMapAccess) level.getChunkSource().chunkMap)\n"
         "                .legacyconnector$visibleChunk(net.minecraft.world.level.ChunkPos.asLong(chunkX, chunkZ)) != null;"),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/world/Explosion.java": [
        ("        this(world, entity, modern.getPosition().x, modern.getPosition().y, modern.getPosition().z, modern.radius, false,",
         "        this(world, entity, modern.getPosition().x, modern.getPosition().y, modern.getPosition().z, org.kylepitcock.legacyconnector.mixin.access.ExplosionAccess.radius(modern), false,"),
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

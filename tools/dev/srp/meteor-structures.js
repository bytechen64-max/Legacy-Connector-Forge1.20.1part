// Run on an isolated headless test server with SRP installed. Never use a player's save.
if (tick === 0) {
    try {
        var WorldBridge = Java.type('org.kylepitcock.legacyconnector.v1_12_2.bridge.WorldBridge1122');
        var Id = Java.type('legacyconnector.v1_12_2.net.minecraft.util.ResourceLocation');
        var Pos = Java.type('legacyconnector.v1_12_2.net.minecraft.util.math.BlockPos');
        var Nbt = Java.type('legacyconnector.v1_12_2.net.minecraft.nbt.NBTTagCompound');
        var Settings = Java.type('legacyconnector.v1_12_2.net.minecraft.world.gen.structure.template.PlacementSettings');
        var world = WorldBridge.wrap(server.overworld());
        var manager = world.getSaveHandler().getStructureTemplateManager();
        var names = ['meteor', 'meteor_fragment_large1', 'meteor_fragment_small1'];
        for each (var name in names) {
            var template = manager.get(world.getMinecraftServer(), new Id('srparasites', name));
            if (template === null) throw new Error('Missing SRP template: ' + name);
            var size = template.getSize();
            var nbt = template.writeToNBT(new Nbt());
            print('METEOR TEMPLATE ' + name + ' size=' + size + ' blocks=' + nbt.getTagList('blocks', 10).tagCount());
            if (size.getX() <= 0) throw new Error('Empty template: ' + name);
            if (name === 'meteor_fragment_small1') {
                var origin = new Pos(0, 100, 0);
                template.addBlocksToWorldChunk(world, origin, new Settings());
                var placed = 0;
                for (var x = 0; x < size.getX(); x++) for (var y = 0; y < size.getY(); y++) for (var z = 0; z < size.getZ(); z++) {
                    if (!world.isAirBlock(origin['add(int,int,int)'](x, y, z))) placed++;
                }
                print('METEOR PLACED nonair=' + placed);
                if (placed === 0) throw new Error('No template blocks placed');
            }
        }
        print('METEOR TEMPLATE CHECK PASS');
        var modernPos = Java.type('net.minecraft.core.BlockPos');
        var modernBlocks = Java.type('net.minecraft.world.level.block.Blocks');
        var modernLevel = server.overworld();
        modernLevel.setChunkForced(8, 8, true);
        for (var fx = 128; fx < 144; fx++) for (var fz = 128; fz < 144; fz++) {
            modernLevel.setBlock(modernPos.containing(fx, 64, fz), modernBlocks.STONE.defaultBlockState(), 2);
        }
        server.getCommands().performPrefixedCommand(server.createCommandSourceStack(), 'summon srparasites:meteor 136 66 136 {bigmet:0b,Motion:[0.0d,-1.0d,0.0d]}');
        print('METEOR COLLISION TEST spawned fragment');
    } catch (failure) {
        print('METEOR TEMPLATE CHECK FAIL: ' + failure);
        if (failure.printStackTrace) failure.printStackTrace();
        server.halt(false);
    }
}
if (tick === 10) {
    try {
        var genClass = Java.type('com.dhanantry.scapeandrunparasites.world.gen.feature.WorldGenParasiteMeteorCrash');
        var blocksAfter = 0;
        var registry = Java.type('net.minecraft.core.registries.BuiltInRegistries').BLOCK;
        for (var cx = 126; cx < 149; cx++) for (var cy = 63; cy < 75; cy++) for (var cz = 126; cz < 149; cz++) {
            var state = modernLevel.getBlockState(modernPos.containing(cx, cy, cz));
            if (registry.getKey(state.getBlock()).getNamespace() === 'srparasites') blocksAfter++;
        }
        print('METEOR COLLISION TEST parasite blocks=' + blocksAfter);
        if (blocksAfter === 0) throw new Error('Collision did not generate fragment');
        print('METEOR COLLISION CHECK PASS');
        modernLevel.setChunkForced(4, 4, true);
        for (var bx = 64; bx < 80; bx++) for (var bz = 64; bz < 80; bz++) {
            modernLevel.setBlock(modernPos.containing(bx, 64, bz), modernBlocks.STONE.defaultBlockState(), 2);
        }
        server.getCommands().performPrefixedCommand(server.createCommandSourceStack(), 'summon srparasites:meteor 72 66 72 {Motion:[0.0d,-1.0d,0.0d]}');
        print('METEOR ROOT TEST spawned');
    } catch (failure) {
        print('METEOR COLLISION CHECK FAIL: ' + failure);
        server.halt(false);
    }
}
if (tick === 100) {
    try {
        var rootBlocks = 0;
        var entityTypes = Java.type('net.minecraft.core.registries.BuiltInRegistries').ENTITY_TYPE;
        var entities = modernLevel.getAllEntities().iterator();
        while (entities.hasNext()) {
            var entity = entities.next();
            if (entityTypes.getKey(entity.getType()).getPath() === 'meteor') {
                print('METEOR ENTITY remaining at=' + entity.position() + ' ticks=' + entity.tickCount + ' motion=' + entity.getDeltaMovement() + ' root=' + entity.mcc$legacy().getRoot());
            }
        }
        for (var px = 40; px < 96; px++) for (var py = 6; py < 120; py++) for (var pz = 40; pz < 96; pz++) {
            var rootState = modernLevel.getBlockState(modernPos.containing(px, py, pz));
            if (registry.getKey(rootState.getBlock()).getNamespace() === 'srparasites') rootBlocks++;
        }
        print('METEOR ROOT TEST parasite blocks=' + rootBlocks);
        if (rootBlocks === 0) throw new Error('Root collision did not generate structure');
        print('METEOR ROOT CHECK PASS');
        modernLevel.setChunkForced(32, 32, true);
        for (var nx = 512; nx < 528; nx++) for (var nz = 512; nz < 528; nz++) {
            modernLevel.setBlock(modernPos.containing(nx, -60, nz), modernBlocks.STONE.defaultBlockState(), 2);
        }
        server.getCommands().performPrefixedCommand(server.createCommandSourceStack(), 'summon srparasites:meteor 520 -58 520 {Motion:[0.0d,-1.0d,0.0d]}');
        print('METEOR NEGATIVE HEIGHT TEST spawned');
    } catch (failure) {
        print('METEOR ROOT CHECK FAIL: ' + failure);
        server.halt(false);
    }
}
if (tick === 160) {
    try {
        var lowBlocks = 0, highBlocks = 0;
        for (var nx2 = 496; nx2 < 544; nx2++) for (var ny2 = -64; ny2 < 80; ny2++) for (var nz2 = 496; nz2 < 544; nz2++) {
            var negativeState = modernLevel.getBlockState(modernPos.containing(nx2, ny2, nz2));
            if (registry.getKey(negativeState.getBlock()).getNamespace() !== 'srparasites') continue;
            if (ny2 < 0) lowBlocks++; else highBlocks++;
        }
        print('METEOR NEGATIVE HEIGHT belowZero=' + lowBlocks + ' aboveZero=' + highBlocks);
        if (lowBlocks < 3000) throw new Error('Meteor body is missing near negative-height ground');
        print('METEOR NEGATIVE HEIGHT CHECK PASS');
    } catch (failure) {
        print('METEOR NEGATIVE HEIGHT CHECK FAIL: ' + failure);
    } finally { server.halt(false); }
}

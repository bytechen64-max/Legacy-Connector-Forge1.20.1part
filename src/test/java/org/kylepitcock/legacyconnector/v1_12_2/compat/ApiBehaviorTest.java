package org.kylepitcock.legacyconnector.v1_12_2.compat;

import legacyconnector.v1_12_2.net.minecraft.block.BlockStructure;
import legacyconnector.v1_12_2.net.minecraft.client.model.ModelShulkerBullet;
import legacyconnector.v1_12_2.net.minecraft.tileentity.TileEntityStructure;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class ApiBehaviorTest {
    @Test void registersEveryVanillaParticleFactory() throws Exception {
        org.kylepitcock.legacyconnector.v1_12_2.bridge.ParticleFactories1122.register();
        var field = org.kylepitcock.legacyconnector.core.synth.Synth.class.getDeclaredField("INSTANCE_METHODS");
        field.setAccessible(true);
        var callbacks = (java.util.Map<?, ?>) field.get(null);
        int count = 0;
        for (String line : java.nio.file.Files.readAllLines(java.nio.file.Path.of("loader/src/main/resources/legacyconnector/legacy/1.12.2/hierarchy.txt"))) {
            if (!line.startsWith("net/minecraft/client/particle/") || !line.contains(" net/minecraft/client/particle/IParticleFactory ")) continue;
            String name = line.substring(0, line.indexOf(' ')).replace('/', '.');
            assertTrue(callbacks.containsKey(name + ".createParticle"), name);
            count++;
        }
        assertEquals(47, count);
    }
    @Test void shulkerBulletContainsThreeCrossedBoxesAndRotatesInRadians() throws Exception {
        // Forge normally sets the physical side before loading any client models.
        var access = sun.misc.Unsafe.class.getDeclaredField("theUnsafe");
        access.setAccessible(true);
        var unsafe = (sun.misc.Unsafe) access.get(null);
        var side = net.minecraftforge.fml.loading.FMLEnvironment.class.getField("dist");
        var previous = net.minecraftforge.fml.loading.FMLEnvironment.dist;
        ModelShulkerBullet model;
        try {
            unsafe.putObject(unsafe.staticFieldBase(side), unsafe.staticFieldOffset(side), net.minecraftforge.api.distmarker.Dist.CLIENT);
            model = new ModelShulkerBullet();
        } finally {
            unsafe.putObject(unsafe.staticFieldBase(side), unsafe.staticFieldOffset(side), previous);
        }
        assertEquals(1, model.boxList.size());
        assertEquals(3, model.boxList.get(0).cubeList.size());
        model.setRotationAngles(0, 0, 0, 90, -45, 1, null);
        assertEquals(Math.PI / 2, model.boxList.get(0).rotateAngleY, 0.00001);
        assertEquals(-Math.PI / 4, model.boxList.get(0).rotateAngleX, 0.00001);
    }
    @Test void structureBlockRetainsEveryModeAndCreatesTile() throws Exception {
        var field = sun.misc.Unsafe.class.getDeclaredField("theUnsafe");
        field.setAccessible(true);
        var block = (BlockStructure) ((sun.misc.Unsafe) field.get(null)).allocateInstance(BlockStructure.class);
        var create = BlockStructure.class.getDeclaredMethod("createBlockState");
        create.setAccessible(true);
        block.blockState = (legacyconnector.v1_12_2.net.minecraft.block.state.BlockStateContainer) create.invoke(block);
        var set = legacyconnector.v1_12_2.net.minecraft.block.Block.class.getDeclaredMethod("setDefaultState", legacyconnector.v1_12_2.net.minecraft.block.state.IBlockState.class);
        set.setAccessible(true);
        set.invoke(block, block.blockState.getBaseState());
        for (var mode : TileEntityStructure.Mode.values()) {
            var state = block.getStateFromMeta(mode.getModeId());
            assertEquals(mode, state.getValue(BlockStructure.MODE));
            assertEquals(mode.getModeId(), block.getMetaFromState(state));
        }
        assertNotNull(block.createNewTileEntity(null, 0));
    }
    @Test void terrainScreenDoesNotPauseWorld() {
        assertFalse(new legacyconnector.v1_12_2.net.minecraft.client.gui.GuiDownloadTerrain().doesGuiPauseGame());
    }
}

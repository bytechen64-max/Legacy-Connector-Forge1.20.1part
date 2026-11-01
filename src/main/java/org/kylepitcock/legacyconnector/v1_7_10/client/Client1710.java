package org.kylepitcock.legacyconnector.v1_7_10.client;

import legacyconnector.v1_7_10.net.minecraft.block.Block;
import legacyconnector.v1_7_10.net.minecraft.item.Item;
import legacyconnector.v1_7_10.net.minecraft.item.ItemBlock;
import net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.client.event.EntityRenderersEvent;
import org.kylepitcock.legacyconnector.v1_7_10.bridge.ItemBridge;
import org.kylepitcock.legacyconnector.v1_7_10.bridge.TileEntityBridge;

/** Client-only registrations for 1.7.10 content (screens, tile entity renderers, special item renderers). */
public final class Client1710 {
    private Client1710() {}

    public static void register(IEventBus modBus) {
        ClientGui.registerScreens();
        modBus.addListener((net.minecraftforge.client.event.RegisterKeyMappingsEvent e) -> {
            for (var key : legacyconnector.v1_7_10.net.minecraft.client.settings.KeyBinding.mcc$registered()) {
                try {
                    e.register(key.mcc$modern());
                } catch (RuntimeException ex) {
                    org.slf4j.LoggerFactory.getLogger("LegacyConnector/Keys").warn("Could not register key binding {}", key.getKeyDescription(), ex);
                }
            }
            legacyconnector.v1_7_10.net.minecraft.client.settings.KeyBinding.mcc$mappingsCollected();
        });
        modBus.addListener(Client1710::onRegisterRenderers);
        modBus.addListener((net.minecraftforge.client.event.sound.SoundEngineLoadEvent e) -> {
            // 1.7.10 fired SoundSetupEvent and SoundLoadEvent each time its sound system (re)started
            LegacySoundSources.engineReloaded(e.getEngine());
            boolean loaded = LegacySoundSources.engineLoaded();
            var manager = legacyconnector.v1_7_10.net.minecraft.client.audio.SoundManager.INSTANCE;
            manager.mcc$engineLoaded(loaded);
            if (!loaded) return;
            var bus = legacyconnector.v1_7_10.net.minecraftforge.common.MinecraftForge.EVENT_BUS;
            try {
                bus.post(new legacyconnector.v1_7_10.net.minecraftforge.client.event.sound.SoundSetupEvent(manager));
                bus.post(new legacyconnector.v1_7_10.net.minecraftforge.client.event.sound.SoundLoadEvent(manager));
            } catch (RuntimeException | LinkageError ex) {
                org.slf4j.LoggerFactory.getLogger("LegacyConnector/SoundSystem").error("A legacy sound load handler failed", ex);
            }
        });
        LegacyParticles.register();
        LegacyMusic.register();
        ClientSelfTest.register();
        WorldScreenshotTest.register();
        ScreenEvents1710.register();
        RenderEvents1710.register();
        FirstPersonPose.register();
        LegacyKeyConflicts.register();
        LegacyArmorLayer.registerOverlayHiding();
        HudEvents1710.register();
        modBus.addListener((net.minecraftforge.client.event.RegisterDimensionSpecialEffectsEvent e) ->
                e.register(org.kylepitcock.legacyconnector.v1_7_10.dimension.LegacyDimensions.EFFECTS, new LegacyDimensionEffects()));
        modBus.addListener((net.minecraftforge.client.event.TextureStitchEvent.Post e) -> {
            if (!e.getAtlas().location().equals(net.minecraft.world.inventory.InventoryMenu.BLOCK_ATLAS)) return;
            AtlasUV.invalidate();
            org.kylepitcock.legacyconnector.v1_7_10.Assets1710.postStitched();
        });
        modBus.addListener(Client1710::onRegisterItemColors);
        modBus.addListener(Client1710::onRegisterBlockColors);
        modBus.addListener(Client1710::onModifyBaking);
        SharedItemModels.register(modBus);
        modBus.addListener(Client1710::onAddLayers);
    }

    /** Legacy armor is drawn by its own layer on players and humanoid mobs. */
    @SuppressWarnings({"unchecked", "rawtypes"})
    private static void onAddLayers(EntityRenderersEvent.AddLayers event) {
        for (var skin : event.getSkins()) {
            var renderer = event.getSkin(skin);
            if (renderer instanceof net.minecraft.client.renderer.entity.player.PlayerRenderer player) {
                player.addLayer(new LegacyArmorLayer(player));
                LegacyArmorLayer.hideFromHeadLayer(player);
            }
        }
        // 1.20.1's AddLayers hands out a renderer per entity type but does not list the types (the 1.21 event does)
        for (var type : net.minecraft.core.registries.BuiltInRegistries.ENTITY_TYPE) {
            var renderer = event.getEntityRenderer((net.minecraft.world.entity.EntityType) type);
            if (renderer instanceof net.minecraft.client.renderer.entity.HumanoidMobRenderer humanoid) {
                humanoid.addLayer(new LegacyArmorLayer(humanoid));
                LegacyArmorLayer.hideFromHeadLayer(humanoid);
            } else if (renderer instanceof net.minecraft.client.renderer.entity.ArmorStandRenderer stand) {
                // armor stands show legacy armor too (1.7.10 had none, but players put legacy suits and armor on them)
                stand.addLayer(new LegacyArmorLayer(stand));
                LegacyArmorLayer.hideFromHeadLayer(stand);
            }
        }
    }

    private static void onRegisterRenderers(EntityRenderersEvent.RegisterRenderers event) {
        if (TileEntityBridge.type() != null) event.registerBlockEntityRenderer(TileEntityBridge.type(), ctx -> new LegacyBlockEntityRenderer());
        for (var type : org.kylepitcock.legacyconnector.v1_7_10.entity.LegacyHosts.allTypes()) {
            @SuppressWarnings("unchecked")
            var t = (net.minecraft.world.entity.EntityType<net.minecraft.world.entity.Entity>) type;
            event.registerEntityRenderer(t, LegacyEntityRenderer::new);
        }
    }

    /** Blocks drawn by a legacy ISimpleBlockRenderingHandler get a model that runs it (see IsbrhBlockModel). */
    private static void onModifyBaking(net.minecraftforge.client.event.ModelEvent.ModifyBakingResult event) {
        var models = event.getModels();
        int replaced = 0;
        for (Block block : org.kylepitcock.legacyconnector.v1_7_10.bridge.BlockBridge.modBlocks()) {
            if (block.mcc$modern == null) continue;
            int renderId;
            try {
                renderId = block.getRenderType();
            } catch (RuntimeException | LinkageError e) {
                continue;
            }
            // a mod's handler, or 1.7.10's own renderer of a vanilla render type that no static model can show (panes)
            var builtIn = legacyconnector.v1_7_10.cpw.mods.fml.client.registry.RenderingRegistry.mcc$blockHandler(renderId) == null
                    ? VanillaBlockRenderers.forBlock(block, renderId) : null;
            if (builtIn == null && legacyconnector.v1_7_10.cpw.mods.fml.client.registry.RenderingRegistry.mcc$blockHandler(renderId) == null) continue;
            for (var state : familyStates(block.mcc$modern)) {
                var location = net.minecraft.client.renderer.block.BlockModelShaper.stateToModelLocation(state);
                var original = models.get(location);
                if (original == null || original instanceof IsbrhBlockModel) continue;
                models.put(location, new IsbrhBlockModel(original, block, renderId, builtIn));
                replaced++;
            }
        }
        if (replaced > 0) org.slf4j.LoggerFactory.getLogger("LegacyConnector/ISBRH").info("{} block states are drawn by legacy block renderers", replaced);
    }

    /** Blocks that colour themselves (leaves, grass, anything overriding colorMultiplier/getRenderColor) tint index 0 of their model. */
    private static void onRegisterBlockColors(net.minecraftforge.client.event.RegisterColorHandlersEvent.Block event) {
        for (legacyconnector.v1_7_10.net.minecraft.block.Block block : org.kylepitcock.legacyconnector.v1_7_10.bridge.BlockBridge.modBlocks()) {
            if (block.mcc$modern == null || !org.kylepitcock.legacyconnector.v1_7_10.Assets1710.tinted(block)) continue;
            event.register((state, level, pos, tint) -> {
                try {
                    if (level != null && pos != null) {
                        return 0xFF000000 | block.colorMultiplier(org.kylepitcock.legacyconnector.v1_7_10.bridge.BlockAccessView.of(level), pos.getX(), pos.getY(), pos.getZ());
                    }
                    return 0xFF000000 | block.getRenderColor(org.kylepitcock.legacyconnector.v1_7_10.bridge.BlockBridge.legacyMeta(state));
                } catch (RuntimeException | LinkageError e) {
                    return 0xFFFFFFFF;
                }
            }, familyBlocks(block.mcc$modern));
        }
    }

    /** A legacy block's modern block and its flattened subtype blocks (see BlockFlattening1710). */
    private static net.minecraft.world.level.block.Block[] familyBlocks(net.minecraft.world.level.block.Block modern) {
        if (!(modern instanceof org.kylepitcock.legacyconnector.v1_7_10.adapter.LegacyBlockAdapter a)) return new net.minecraft.world.level.block.Block[] {modern};
        return a.familyBlocks().toArray(net.minecraft.world.level.block.Block[]::new);
    }

    /** Every state of a legacy block, flattened subtype blocks included. */
    private static java.util.List<net.minecraft.world.level.block.state.BlockState> familyStates(net.minecraft.world.level.block.Block modern) {
        java.util.List<net.minecraft.world.level.block.state.BlockState> out = new java.util.ArrayList<>();
        for (var b : familyBlocks(modern)) out.addAll(b.getStateDefinition().getPossibleStates());
        return out;
    }

    /** Legacy items tinted per render pass (spawn eggs, dyed items): layer N of the item model is pass N. */
    private static void onRegisterItemColors(net.minecraftforge.client.event.RegisterColorHandlersEvent.Item event) {
        for (Item item : ItemBridge.modItems()) {
            try {
                if (!org.kylepitcock.legacyconnector.v1_7_10.adapter.LegacyBlockAdapter.overrides(item, "getColorFromItemStack",
                        legacyconnector.v1_7_10.net.minecraft.item.ItemStack.class, int.class)) continue;
            } catch (RuntimeException | LinkageError e) {
                continue;
            }
            event.register((stack, tint) -> {
                try {
                    return 0xFF000000 | item.getColorFromItemStack(legacyconnector.v1_7_10.net.minecraft.item.ItemStack.mcc$wrap(stack), tint);
                } catch (RuntimeException | LinkageError e) {
                    return 0xFFFFFFFF;
                }
            }, item.mcc$variants.values().toArray(new net.minecraft.world.item.Item[0]));
        }
    }

    public static boolean isChestStyle(Block block) {
        try {
            return block.getRenderType() == 22;
        } catch (RuntimeException e) {
            return false;
        }
    }
}

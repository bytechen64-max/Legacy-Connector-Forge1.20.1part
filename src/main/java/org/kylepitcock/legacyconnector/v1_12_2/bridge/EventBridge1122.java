package org.kylepitcock.legacyconnector.v1_12_2.bridge;

import legacyconnector.v1_12_2.net.minecraft.entity.player.EntityPlayer;
import legacyconnector.v1_12_2.net.minecraftforge.common.MinecraftForge;
import legacyconnector.v1_12_2.net.minecraftforge.fml.common.eventhandler.Event;
import legacyconnector.v1_12_2.net.minecraftforge.fml.common.gameevent.PlayerEvent;
import legacyconnector.v1_12_2.net.minecraftforge.fml.common.gameevent.TickEvent;
import legacyconnector.v1_12_2.net.minecraftforge.fml.relauncher.Side;
import net.minecraftforge.eventbus.api.IEventBus;

/**
 * Posts 1.12.2's gameplay events on {@code MinecraftForge.EVENT_BUS} (FML's bus is the same one in 1.12) from the modern
 * events: ticks, players logging in and out, respawning and changing dimension, crafting and smelting, entities joining a
 * world, worlds loading, unloading and saving. Events nobody subscribed to are not built.
 */
public final class EventBridge1122 {
    private static final org.slf4j.Logger LOG = org.slf4j.LoggerFactory.getLogger("LegacyConnector/Events1122");
    private static boolean registered;
    private static final java.util.Map<Class<?>, Long> LAST_WARNING = new java.util.concurrent.ConcurrentHashMap<>();

    private EventBridge1122() {}

    private static legacyconnector.v1_12_2.net.minecraftforge.fml.common.eventhandler.EventBus bus() {
        return MinecraftForge.EVENT_BUS;
    }

    /** The 1.12 numeric id of a dimension (the id {@link WorldBridge1122#dimensionId} gives its level). */
    public static int dimensionId(net.minecraft.resources.ResourceKey<net.minecraft.world.level.Level> key) {
        var server = net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();
        var level = server == null || key == null ? null : server.getLevel(key);
        return level != null ? WorldBridge1122.dimensionId(level) : legacyconnector.v1_12_2.net.minecraftforge.common.DimensionManager.mcc$idOf(key);
    }

    private static boolean wants(Class<? extends Event> type) {
        return MinecraftForge.EVENT_BUS.mcc$hasListeners(type);
    }

    /** Posts the event; a failing handler is logged (throttled by type) instead of breaking the modern tick. */
    private static boolean post(Event event) {
        try {
            return MinecraftForge.EVENT_BUS.post(event);
        } catch (RuntimeException | LinkageError e) {
            long now = System.currentTimeMillis();
            Long last = LAST_WARNING.get(event.getClass());
            if (last == null || now - last > 60_000L) {
                LAST_WARNING.put(event.getClass(), now);
                LOG.warn("A 1.12.2 {} handler failed (repeats are logged once a minute): {}", event.getClass().getSimpleName(), e.toString(), e);
            }
            return false;
        }
    }

    private static EntityPlayer player(net.minecraft.world.entity.player.Player p) {
        return EntityBridge1122.wrap(p) instanceof EntityPlayer player ? player : null;
    }

    public static synchronized void register() {
        if (registered) return;
        registered = true;
        IEventBus bus = net.minecraftforge.common.MinecraftForge.EVENT_BUS;
        bus.addListener((net.minecraftforge.event.TickEvent.ServerTickEvent e) -> {
            // 1.21 has separate Pre/Post events; 1.20.1 fires one event with a phase.
            if (e.phase != net.minecraftforge.event.TickEvent.Phase.START) return;
            if (wants(TickEvent.ServerTickEvent.class)) post(new TickEvent.ServerTickEvent(TickEvent.Phase.START));
        });
        bus.addListener((net.minecraftforge.event.TickEvent.ServerTickEvent e) -> {
            // 1.21 has separate Pre/Post events; 1.20.1 fires one event with a phase.
            if (e.phase != net.minecraftforge.event.TickEvent.Phase.END) return;
            if (wants(TickEvent.ServerTickEvent.class)) post(new TickEvent.ServerTickEvent(TickEvent.Phase.END));
        });
        // 1.20.1 fires one tick event per side with a phase (the separate Pre/Post events are 1.20.2+).
        bus.addListener((net.minecraftforge.event.TickEvent.LevelTickEvent e) -> worldTick(e.level,
                e.phase == net.minecraftforge.event.TickEvent.Phase.START ? TickEvent.Phase.START : TickEvent.Phase.END));
        bus.addListener((net.minecraftforge.event.TickEvent.PlayerTickEvent e) -> playerTick(e.player,
                e.phase == net.minecraftforge.event.TickEvent.Phase.START ? TickEvent.Phase.START : TickEvent.Phase.END));

        bus.addListener((net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedInEvent e) -> {
            if (wants(PlayerEvent.PlayerLoggedInEvent.class) && player(e.getEntity()) != null) post(new PlayerEvent.PlayerLoggedInEvent(player(e.getEntity())));
        });
        bus.addListener((net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent e) -> {
            if (wants(PlayerEvent.PlayerLoggedOutEvent.class) && player(e.getEntity()) != null) post(new PlayerEvent.PlayerLoggedOutEvent(player(e.getEntity())));
        });
        bus.addListener((net.minecraftforge.event.entity.player.PlayerEvent.PlayerRespawnEvent e) -> {
            if (wants(PlayerEvent.PlayerRespawnEvent.class) && player(e.getEntity()) != null) post(new PlayerEvent.PlayerRespawnEvent(player(e.getEntity()), e.isEndConquered()));
        });
        bus.addListener((net.minecraftforge.event.entity.player.PlayerEvent.PlayerChangedDimensionEvent e) -> {
            if (!wants(PlayerEvent.PlayerChangedDimensionEvent.class) || player(e.getEntity()) == null) return;
            var server = e.getEntity().getServer();
            int from = dimension(server, e.getFrom()), to = dimension(server, e.getTo());
            post(new PlayerEvent.PlayerChangedDimensionEvent(player(e.getEntity()), from, to));
        });
        bus.addListener((net.minecraftforge.event.entity.player.PlayerEvent.ItemCraftedEvent e) -> {
            if (wants(PlayerEvent.ItemCraftedEvent.class) && player(e.getEntity()) != null) {
                post(new PlayerEvent.ItemCraftedEvent(player(e.getEntity()), Stacks1122.fromModern(e.getCrafting()), null));
            }
        });
        bus.addListener((net.minecraftforge.event.entity.player.PlayerEvent.ItemSmeltedEvent e) -> {
            if (wants(PlayerEvent.ItemSmeltedEvent.class) && player(e.getEntity()) != null) {
                post(new PlayerEvent.ItemSmeltedEvent(player(e.getEntity()), Stacks1122.fromModern(e.getSmelting())));
            }
        });

        bus.addListener((net.minecraftforge.event.entity.EntityJoinLevelEvent e) -> {
            if (!wants(legacyconnector.v1_12_2.net.minecraftforge.event.entity.EntityJoinWorldEvent.class)) return;
            var view = EntityBridge1122.wrap(e.getEntity());
            if (view != null && post(new legacyconnector.v1_12_2.net.minecraftforge.event.entity.EntityJoinWorldEvent(view, WorldBridge1122.wrap(e.getLevel())))) {
                e.setCanceled(true);
            }
        });
        bus.addListener((net.minecraftforge.event.level.LevelEvent.Load e) -> {
            if (e.getLevel() instanceof net.minecraft.world.level.Level level && wants(legacyconnector.v1_12_2.net.minecraftforge.event.world.WorldEvent.Load.class)) {
                post(new legacyconnector.v1_12_2.net.minecraftforge.event.world.WorldEvent.Load(WorldBridge1122.wrap(level)));
            }
        });
        bus.addListener((net.minecraftforge.event.level.LevelEvent.Unload e) -> {
            if (e.getLevel() instanceof net.minecraft.world.level.Level level && wants(legacyconnector.v1_12_2.net.minecraftforge.event.world.WorldEvent.Unload.class)) {
                post(new legacyconnector.v1_12_2.net.minecraftforge.event.world.WorldEvent.Unload(WorldBridge1122.wrap(level)));
            }
        });
        bus.addListener((net.minecraftforge.event.level.LevelEvent.Save e) -> {
            if (e.getLevel() instanceof net.minecraft.world.level.Level level && wants(legacyconnector.v1_12_2.net.minecraftforge.event.world.WorldEvent.Save.class)) {
                post(new legacyconnector.v1_12_2.net.minecraftforge.event.world.WorldEvent.Save(WorldBridge1122.wrap(level)));
            }
        });
        bus.addListener((net.minecraftforge.event.AnvilUpdateEvent e) -> {
            if (!wants(legacyconnector.v1_12_2.net.minecraftforge.event.AnvilUpdateEvent.class)) return;
            var legacy = new legacyconnector.v1_12_2.net.minecraftforge.event.AnvilUpdateEvent(Stacks1122.fromModern(e.getLeft()),
                    Stacks1122.fromModern(e.getRight()), e.getName(), (int) e.getCost());
            post(legacy);
            if (legacy.isCanceled()) {
                e.setCanceled(true);
            } else if (legacy.getOutput() != null && !legacy.getOutput().isEmpty()) {
                e.setOutput(Stacks1122.toModern(legacy.getOutput()));
                e.setCost(legacy.getCost());
                e.setMaterialCost(legacy.getMaterialCost());
            }
        });
        bus.addListener((net.minecraftforge.event.furnace.FurnaceFuelBurnTimeEvent e) -> {
            if (e.getItemStack().isEmpty() || !wants(legacyconnector.v1_12_2.net.minecraftforge.event.furnace.FurnaceFuelBurnTimeEvent.class)) return;
            var legacy = new legacyconnector.v1_12_2.net.minecraftforge.event.furnace.FurnaceFuelBurnTimeEvent(Stacks1122.fromModern(e.getItemStack()),
                    e.getBurnTime());
            post(legacy);
            if (legacy.isCanceled()) e.setBurnTime(legacy.getBurnTime());
        });
        bus.addListener((net.minecraftforge.event.ServerChatEvent e) -> {
            EntityPlayer p;
            if (!wants(legacyconnector.v1_12_2.net.minecraftforge.event.ServerChatEvent.class) || !((p = player(e.getPlayer())) instanceof legacyconnector.v1_12_2.net.minecraft.entity.player.EntityPlayerMP mp)) return;
            var component = new legacyconnector.v1_12_2.net.minecraft.util.text.TextComponentTranslation("chat.type.text", p.getName(), e.getRawText());
            var legacy = new legacyconnector.v1_12_2.net.minecraftforge.event.ServerChatEvent(mp, e.getRawText(), component);
            post(legacy);
            if (legacy.isCanceled()) e.setCanceled(true);
            else if (legacy.getComponent() != component && legacy.getComponent() != null) e.setMessage(legacy.getComponent().mcc$modern());
        });
        registerLiving(bus);
        registerInteractions(bus);
        registerAreaF(bus);
        if (net.minecraftforge.fml.loading.FMLEnvironment.dist.isClient()) Client.register(bus);
    }

    // ------------------------------------------------------------------ Forge living, player and block events

    private static legacyconnector.v1_12_2.net.minecraft.entity.EntityLivingBase living(net.minecraft.world.entity.Entity e) {
        return EntityBridge1122.wrap(e) instanceof legacyconnector.v1_12_2.net.minecraft.entity.EntityLivingBase l ? l : null;
    }

    private static legacyconnector.v1_12_2.net.minecraft.util.math.BlockPos pos(net.minecraft.core.BlockPos p) {
        return new legacyconnector.v1_12_2.net.minecraft.util.math.BlockPos(p.getX(), p.getY(), p.getZ());
    }

    private static legacyconnector.v1_12_2.net.minecraft.util.math.Vec3d vec(net.minecraft.world.phys.Vec3 v) {
        return v == null ? null : new legacyconnector.v1_12_2.net.minecraft.util.math.Vec3d(v.x, v.y, v.z);
    }

    private static legacyconnector.v1_12_2.net.minecraft.util.EnumFacing face(net.minecraft.core.Direction d) {
        return d == null ? null : legacyconnector.v1_12_2.net.minecraft.util.EnumFacing.mcc$of(d);
    }

    private static legacyconnector.v1_12_2.net.minecraft.util.EnumHand hand(net.minecraft.world.InteractionHand h) {
        return h == net.minecraft.world.InteractionHand.OFF_HAND ? legacyconnector.v1_12_2.net.minecraft.util.EnumHand.OFF_HAND
                : legacyconnector.v1_12_2.net.minecraft.util.EnumHand.MAIN_HAND;
    }

    /** The legacy verdict as the modern interact event's ({@code TriState} does not exist on 1.20.1}). */
    private static net.minecraftforge.eventbus.api.Event.Result useResult(Event.Result r) {
        return r == Event.Result.ALLOW ? net.minecraftforge.eventbus.api.Event.Result.ALLOW
                : r == Event.Result.DENY ? net.minecraftforge.eventbus.api.Event.Result.DENY : net.minecraftforge.eventbus.api.Event.Result.DEFAULT;
    }

    private static net.minecraft.world.InteractionResult result(legacyconnector.v1_12_2.net.minecraft.util.EnumActionResult r) {
        return r == legacyconnector.v1_12_2.net.minecraft.util.EnumActionResult.SUCCESS ? net.minecraft.world.InteractionResult.SUCCESS
                : r == legacyconnector.v1_12_2.net.minecraft.util.EnumActionResult.FAIL ? net.minecraft.world.InteractionResult.FAIL : net.minecraft.world.InteractionResult.PASS;
    }

    private static void registerLiving(IEventBus bus) {
        bus.addListener((net.minecraftforge.event.entity.living.MobEffectEvent.Added e) -> {
            if (!wants(legacyconnector.v1_12_2.net.minecraftforge.event.entity.living.PotionEvent.PotionAddedEvent.class)) return;
            var entity = living(e.getEntity());
            if (entity != null) post(new legacyconnector.v1_12_2.net.minecraftforge.event.entity.living.PotionEvent.PotionAddedEvent(entity,
                    legacyconnector.v1_12_2.net.minecraft.potion.PotionEffect.mcc$fromModern(e.getOldEffectInstance()),
                    legacyconnector.v1_12_2.net.minecraft.potion.PotionEffect.mcc$fromModern(e.getEffectInstance())));
        });
        // 1.12.2 posted LivingAttackEvent and then LivingHurtEvent before armour, LivingDamageEvent after it
        bus.addListener((net.minecraftforge.event.entity.living.LivingHurtEvent e) -> {
            boolean attack = wants(legacyconnector.v1_12_2.net.minecraftforge.event.entity.living.LivingAttackEvent.class);
            boolean hurt = wants(legacyconnector.v1_12_2.net.minecraftforge.event.entity.living.LivingHurtEvent.class);
            if (!attack && !hurt) return;
            var entity = living(e.getEntity());
            if (entity == null) return;
            var source = legacyconnector.v1_12_2.net.minecraft.util.DamageSource.mcc$of(e.getSource());
            if (attack && post(new legacyconnector.v1_12_2.net.minecraftforge.event.entity.living.LivingAttackEvent(entity, source, e.getAmount()))) {
                e.setCanceled(true);
                return;
            }
            if (hurt) {
                var event = new legacyconnector.v1_12_2.net.minecraftforge.event.entity.living.LivingHurtEvent(entity, source, e.getAmount());
                if (post(event)) e.setCanceled(true);
                else e.setAmount(event.getAmount());
            }
        });
        bus.addListener((net.minecraftforge.event.entity.living.LivingDamageEvent e) -> {
            if (!wants(legacyconnector.v1_12_2.net.minecraftforge.event.entity.living.LivingDamageEvent.class)) return;
            var entity = living(e.getEntity());
            if (entity == null) return;
            var event = new legacyconnector.v1_12_2.net.minecraftforge.event.entity.living.LivingDamageEvent(entity,
                    legacyconnector.v1_12_2.net.minecraft.util.DamageSource.mcc$of(e.getSource()), e.getAmount());
            // the modern event can no longer be canceled here: a canceled legacy one deals no damage
            if (post(event)) e.setAmount(0);
            else e.setAmount(event.getAmount());
        });
        bus.addListener((net.minecraftforge.event.entity.living.LivingDeathEvent e) -> {
            if (!wants(legacyconnector.v1_12_2.net.minecraftforge.event.entity.living.LivingDeathEvent.class)) return;
            var entity = living(e.getEntity());
            if (entity != null && post(new legacyconnector.v1_12_2.net.minecraftforge.event.entity.living.LivingDeathEvent(entity,
                    legacyconnector.v1_12_2.net.minecraft.util.DamageSource.mcc$of(e.getSource())))) {
                e.setCanceled(true);
            }
        });
        // 1.12.2: a dying player's drops go through PlayerDropsEvent (Tombstone, soulbound mods), everything else through LivingDropsEvent
        bus.addListener((net.minecraftforge.event.entity.living.LivingDropsEvent e) -> {
            boolean isPlayer = e.getEntity() instanceof net.minecraft.world.entity.player.Player;
            Class<? extends Event> type = isPlayer ? legacyconnector.v1_12_2.net.minecraftforge.event.entity.player.PlayerDropsEvent.class
                    : legacyconnector.v1_12_2.net.minecraftforge.event.entity.living.LivingDropsEvent.class;
            if (!wants(type) && !(isPlayer && wants(legacyconnector.v1_12_2.net.minecraftforge.event.entity.living.LivingDropsEvent.class))) return;
            var entity = living(e.getEntity());
            if (entity == null) return;
            java.util.ArrayList<legacyconnector.v1_12_2.net.minecraft.entity.item.EntityItem> drops = new java.util.ArrayList<>();
            for (var item : e.getDrops()) if (EntityBridge1122.wrap(item) instanceof legacyconnector.v1_12_2.net.minecraft.entity.item.EntityItem legacyItem) drops.add(legacyItem);
            var source = legacyconnector.v1_12_2.net.minecraft.util.DamageSource.mcc$of(e.getSource());
            legacyconnector.v1_12_2.net.minecraftforge.event.entity.living.LivingDropsEvent legacy = isPlayer && entity instanceof EntityPlayer p
                    ? new legacyconnector.v1_12_2.net.minecraftforge.event.entity.player.PlayerDropsEvent(p, source, drops, e.isRecentlyHit())
                    : new legacyconnector.v1_12_2.net.minecraftforge.event.entity.living.LivingDropsEvent(entity, source, drops, 0, e.isRecentlyHit());
            if (post(legacy)) {
                e.setCanceled(true);
                return;
            }
            // listeners may have removed drops or added their own: the modern list becomes what the legacy list holds
            e.getDrops().clear();
            for (var item : drops) {
                if (item != null && item.mcc$entity instanceof net.minecraft.world.entity.item.ItemEntity modern) e.getDrops().add(modern);
            }
        });
        bus.addListener((net.minecraftforge.event.entity.living.LivingFallEvent e) -> {
            if (!wants(legacyconnector.v1_12_2.net.minecraftforge.event.entity.living.LivingFallEvent.class)) return;
            var entity = living(e.getEntity());
            if (entity == null) return;
            var event = new legacyconnector.v1_12_2.net.minecraftforge.event.entity.living.LivingFallEvent(entity, e.getDistance(), e.getDamageMultiplier());
            if (post(event)) e.setCanceled(true);
            e.setDistance(event.getDistance());
            e.setDamageMultiplier(event.getDamageMultiplier());
        });
        bus.addListener((net.minecraftforge.event.entity.living.LivingEvent.LivingJumpEvent e) -> {
            if (!wants(legacyconnector.v1_12_2.net.minecraftforge.event.entity.living.LivingEvent.LivingJumpEvent.class)) return;
            var entity = living(e.getEntity());
            if (entity != null) post(new legacyconnector.v1_12_2.net.minecraftforge.event.entity.living.LivingEvent.LivingJumpEvent(entity));
        });
        bus.addListener((net.minecraftforge.event.entity.living.LivingEvent.LivingTickEvent e) -> {
            if (!(e.getEntity() instanceof net.minecraft.world.entity.LivingEntity)
                    || !wants(legacyconnector.v1_12_2.net.minecraftforge.event.entity.living.LivingEvent.LivingUpdateEvent.class)) return;
            var entity = living(e.getEntity());
            if (entity != null && post(new legacyconnector.v1_12_2.net.minecraftforge.event.entity.living.LivingEvent.LivingUpdateEvent(entity))) e.setCanceled(true);
        });
        bus.addListener((net.minecraftforge.event.entity.player.PlayerEvent.Clone e) -> {
            if (!wants(legacyconnector.v1_12_2.net.minecraftforge.event.entity.player.PlayerEvent.Clone.class)) return;
            EntityPlayer player = player(e.getEntity()), original = player(e.getOriginal());
            if (player != null && original != null) post(new legacyconnector.v1_12_2.net.minecraftforge.event.entity.player.PlayerEvent.Clone(player, original, e.isWasDeath()));
        });
        bus.addListener((net.minecraftforge.event.entity.player.PlayerEvent.BreakSpeed e) -> {
            if (!wants(legacyconnector.v1_12_2.net.minecraftforge.event.entity.player.PlayerEvent.BreakSpeed.class)) return;
            EntityPlayer player = player(e.getEntity());
            if (player == null) return;
            var at = e.getPosition().map(EventBridge1122::pos).orElse(legacyconnector.v1_12_2.net.minecraft.util.math.BlockPos.ORIGIN);
            var event = new legacyconnector.v1_12_2.net.minecraftforge.event.entity.player.PlayerEvent.BreakSpeed(player, StatesBridge1122.toLegacy(e.getState()), e.getOriginalSpeed(), at);
            if (post(event)) e.setCanceled(true);
            else e.setNewSpeed(event.getNewSpeed());
        });
        bus.addListener((net.minecraftforge.event.entity.player.PlayerEvent.StartTracking e) -> {
            if (!wants(legacyconnector.v1_12_2.net.minecraftforge.event.entity.player.PlayerEvent.StartTracking.class)) return;
            EntityPlayer player = player(e.getEntity());
            if (player != null) post(new legacyconnector.v1_12_2.net.minecraftforge.event.entity.player.PlayerEvent.StartTracking(player, EntityBridge1122.wrap(e.getTarget())));
        });
        bus.addListener((net.minecraftforge.event.entity.player.PlayerEvent.StopTracking e) -> {
            if (!wants(legacyconnector.v1_12_2.net.minecraftforge.event.entity.player.PlayerEvent.StopTracking.class)) return;
            EntityPlayer player = player(e.getEntity());
            if (player != null) post(new legacyconnector.v1_12_2.net.minecraftforge.event.entity.player.PlayerEvent.StopTracking(player, EntityBridge1122.wrap(e.getTarget())));
        });
    }

    private static void registerInteractions(IEventBus bus) {
        bus.addListener((net.minecraftforge.event.entity.player.PlayerInteractEvent.RightClickBlock e) -> {
            if (!wants(legacyconnector.v1_12_2.net.minecraftforge.event.entity.player.PlayerInteractEvent.RightClickBlock.class)) return;
            EntityPlayer player = player(e.getEntity());
            if (player == null) return;
            var event = new legacyconnector.v1_12_2.net.minecraftforge.event.entity.player.PlayerInteractEvent.RightClickBlock(player, hand(e.getHand()),
                    pos(e.getPos()), face(e.getFace()), vec(e.getHitVec().getLocation()));
            if (post(event)) {
                e.setCanceled(true);
                e.setCancellationResult(result(event.getCancellationResult()));
                return;
            }
            e.setUseBlock(useResult(event.getUseBlock()));
            e.setUseItem(useResult(event.getUseItem()));
        });
        bus.addListener((net.minecraftforge.event.entity.player.PlayerInteractEvent.RightClickItem e) -> {
            if (!wants(legacyconnector.v1_12_2.net.minecraftforge.event.entity.player.PlayerInteractEvent.RightClickItem.class)) return;
            EntityPlayer player = player(e.getEntity());
            if (player == null) return;
            var event = new legacyconnector.v1_12_2.net.minecraftforge.event.entity.player.PlayerInteractEvent.RightClickItem(player, hand(e.getHand()));
            if (post(event)) {
                e.setCanceled(true);
                e.setCancellationResult(result(event.getCancellationResult()));
            }
        });
        bus.addListener((net.minecraftforge.event.entity.player.PlayerInteractEvent.LeftClickBlock e) -> {
            if (!wants(legacyconnector.v1_12_2.net.minecraftforge.event.entity.player.PlayerInteractEvent.LeftClickBlock.class)) return;
            EntityPlayer player = player(e.getEntity());
            if (player == null) return;
            var p = e.getPos();
            var event = new legacyconnector.v1_12_2.net.minecraftforge.event.entity.player.PlayerInteractEvent.LeftClickBlock(player, pos(p), face(e.getFace()),
                    new legacyconnector.v1_12_2.net.minecraft.util.math.Vec3d(p.getX() + 0.5D, p.getY() + 0.5D, p.getZ() + 0.5D));
            if (post(event)) {
                e.setCanceled(true);
                return;
            }
            e.setUseBlock(useResult(event.getUseBlock()));
            e.setUseItem(useResult(event.getUseItem()));
        });
        bus.addListener((net.minecraftforge.event.entity.player.PlayerInteractEvent.EntityInteract e) -> {
            if (!wants(legacyconnector.v1_12_2.net.minecraftforge.event.entity.player.PlayerInteractEvent.EntityInteract.class)) return;
            EntityPlayer player = player(e.getEntity());
            var target = EntityBridge1122.wrap(e.getTarget());
            if (player == null || target == null) return;
            var event = new legacyconnector.v1_12_2.net.minecraftforge.event.entity.player.PlayerInteractEvent.EntityInteract(player, hand(e.getHand()), target);
            if (post(event)) {
                e.setCanceled(true);
                e.setCancellationResult(result(event.getCancellationResult()));
            }
        });
        bus.addListener((net.minecraftforge.event.entity.player.PlayerInteractEvent.EntityInteractSpecific e) -> {
            if (!wants(legacyconnector.v1_12_2.net.minecraftforge.event.entity.player.PlayerInteractEvent.EntityInteractSpecific.class)) return;
            EntityPlayer player = player(e.getEntity());
            var target = EntityBridge1122.wrap(e.getTarget());
            if (player == null || target == null) return;
            var event = new legacyconnector.v1_12_2.net.minecraftforge.event.entity.player.PlayerInteractEvent.EntityInteractSpecific(player, hand(e.getHand()), target, vec(e.getLocalPos()));
            if (post(event)) {
                e.setCanceled(true);
                e.setCancellationResult(result(event.getCancellationResult()));
            }
        });
        bus.addListener((net.minecraftforge.event.level.BlockEvent.BreakEvent e) -> {
            if (!wants(legacyconnector.v1_12_2.net.minecraftforge.event.world.BlockEvent.BreakEvent.class)) return;
            if (!(e.getLevel() instanceof net.minecraft.world.level.Level level)) return;
            var event = new legacyconnector.v1_12_2.net.minecraftforge.event.world.BlockEvent.BreakEvent(WorldBridge1122.wrap(level), pos(e.getPos()),
                    StatesBridge1122.toLegacy(e.getState()), player(e.getPlayer()));
            if (post(event)) e.setCanceled(true);
        });
        // 1.20.1 fires no block drops event (1.20.2+): HarvestDropsEvent needs a global loot modifier instead.
    }

    private static int dimension(net.minecraft.server.MinecraftServer server, net.minecraft.resources.ResourceKey<net.minecraft.world.level.Level> key) {
        var level = server == null ? null : server.getLevel(key);
        return level == null ? 0 : WorldBridge1122.dimensionId(level);
    }

    /** 1.12.2 posted WorldTickEvent for server worlds (the client had ClientTickEvent). */
    private static void worldTick(net.minecraft.world.level.Level level, TickEvent.Phase phase) {
        if (level.isClientSide() || !wants(TickEvent.WorldTickEvent.class)) return;
        post(new TickEvent.WorldTickEvent(Side.SERVER, phase, WorldBridge1122.wrap(level)));
    }

    private static void playerTick(net.minecraft.world.entity.player.Player p, TickEvent.Phase phase) {
        if (!wants(TickEvent.PlayerTickEvent.class)) return;
        EntityPlayer player = player(p);
        if (player != null) post(new TickEvent.PlayerTickEvent(phase, player));
    }

    private static final class Client {
        static void register(IEventBus bus) {
            bus.addListener((net.minecraftforge.event.TickEvent.ClientTickEvent e) -> {
                if (e.phase != net.minecraftforge.event.TickEvent.Phase.START) return;
                if (wants(TickEvent.ClientTickEvent.class)) post(new TickEvent.ClientTickEvent(TickEvent.Phase.START));
            });
            bus.addListener((net.minecraftforge.event.TickEvent.ClientTickEvent e) -> {
                if (e.phase != net.minecraftforge.event.TickEvent.Phase.END) return;
                if (wants(TickEvent.ClientTickEvent.class)) post(new TickEvent.ClientTickEvent(TickEvent.Phase.END));
            });
            // 1.21 renders a frame with RenderFrameEvent; 1.20.1 fires one RenderTickEvent per phase.
            bus.addListener((net.minecraftforge.event.TickEvent.RenderTickEvent e) -> {
                if (e.phase != net.minecraftforge.event.TickEvent.Phase.START) return;
                if (wants(TickEvent.RenderTickEvent.class)) post(new TickEvent.RenderTickEvent(TickEvent.Phase.START, e.renderTickTime));
            });
            bus.addListener((net.minecraftforge.event.TickEvent.RenderTickEvent e) -> {
                if (e.phase != net.minecraftforge.event.TickEvent.Phase.END) return;
                if (wants(TickEvent.RenderTickEvent.class)) post(new TickEvent.RenderTickEvent(TickEvent.Phase.END, e.renderTickTime));
            });
        }
    }

    // ------------------------------------------------------------------ area F: FML item pickup

    private static void registerAreaF(IEventBus bus) {
        // 1.20.1 has no post-pickup event: EntityItemPickupEvent fires just before the pickup, with the item entity that will be
        // consumed (the whole stack), which is the closest thing to FML's ItemPickupEvent.
        bus.addListener((net.minecraftforge.event.entity.player.EntityItemPickupEvent e) -> {
            if (!wants(PlayerEvent.ItemPickupEvent.class) || player(e.getEntity()) == null) return;
            var item = EntityBridge1122.wrap(e.getItem()) instanceof legacyconnector.v1_12_2.net.minecraft.entity.item.EntityItem i ? i : null;
            var picked = e.getItem().getItem().copy();
            if (picked.isEmpty()) return;
            post(new PlayerEvent.ItemPickupEvent(player(e.getEntity()), item, Stacks1122.fromModern(picked)));
        });
    }
}

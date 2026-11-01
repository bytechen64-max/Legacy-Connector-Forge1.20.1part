"""Forge 1.20.1 has no TriState: interact results are Event.Result, pickup denial is event cancellation, plants are booleans."""
import sys

EDITS = {
    r"src/main/java/legacyconnector/v1_12_2/net/minecraftforge/common/ForgeHooks.java": [
        ('''    private static legacyconnector.v1_12_2.net.minecraftforge.fml.common.eventhandler.Event.Result mcc$result(net.minecraftforge.common.util.TriState s) {
        return s == net.minecraftforge.common.util.TriState.TRUE ? legacyconnector.v1_12_2.net.minecraftforge.fml.common.eventhandler.Event.Result.ALLOW
                : s == net.minecraftforge.common.util.TriState.FALSE ? legacyconnector.v1_12_2.net.minecraftforge.fml.common.eventhandler.Event.Result.DENY
                : legacyconnector.v1_12_2.net.minecraftforge.fml.common.eventhandler.Event.Result.DEFAULT;
    }''',
         '''    /** 1.20.1 has no {@code TriState}: the interact event's use-block/use-item verdict is an {@code Event.Result} on both sides. */
    private static legacyconnector.v1_12_2.net.minecraftforge.fml.common.eventhandler.Event.Result mcc$result(net.minecraftforge.eventbus.api.Event.Result r) {
        return r == net.minecraftforge.eventbus.api.Event.Result.ALLOW ? legacyconnector.v1_12_2.net.minecraftforge.fml.common.eventhandler.Event.Result.ALLOW
                : r == net.minecraftforge.eventbus.api.Event.Result.DENY ? legacyconnector.v1_12_2.net.minecraftforge.fml.common.eventhandler.Event.Result.DENY
                : legacyconnector.v1_12_2.net.minecraftforge.fml.common.eventhandler.Event.Result.DEFAULT;
    }'''),
    ],
    r"src/main/java/legacyconnector/v1_12_2/net/minecraftforge/event/ForgeEventFactory.java": [
        ('''    /** Fires the pickup check: -1 when a mod forbids the pickup, 1 when one forces it, 0 to pick up as usual. */
    public static int onItemPickup(legacyconnector.v1_12_2.net.minecraft.entity.item.EntityItem entityItem, EntityPlayer player) {
        var p = player(player);
        if (p == null || entityItem == null || !(entityItem.mcc$modern() instanceof net.minecraft.world.entity.item.ItemEntity item)) return 0;
        var result = EventHooks.fireItemPickupPre(item, p).canPickup();
        return result == net.minecraftforge.common.util.TriState.FALSE ? -1 : result == net.minecraftforge.common.util.TriState.TRUE ? 1 : 0;
    }''',
         '''    /** Fires the pickup check: -1 when a mod forbids the pickup, 0 to pick up as usual (1.20.1's hook cannot force it). */
    public static int onItemPickup(legacyconnector.v1_12_2.net.minecraft.entity.item.EntityItem entityItem, EntityPlayer player) {
        var p = player(player);
        if (p == null || entityItem == null || !(entityItem.mcc$modern() instanceof net.minecraft.world.entity.item.ItemEntity item)) return 0;
        return net.minecraftforge.event.ForgeEventFactory.onItemPickup(item, p);
    }'''),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/bridge/EventBridge1122.java": [
        ('''    private static net.minecraftforge.common.util.TriState tri(Event.Result r) {
        return r == Event.Result.ALLOW ? net.minecraftforge.common.util.TriState.TRUE
                : r == Event.Result.DENY ? net.minecraftforge.common.util.TriState.FALSE : net.minecraftforge.common.util.TriState.DEFAULT;
    }''',
         '''    /** The legacy verdict as the modern interact event's ({@code TriState} does not exist on 1.20.1}). */
    private static net.minecraftforge.eventbus.api.Event.Result useResult(Event.Result r) {
        return r == Event.Result.ALLOW ? net.minecraftforge.eventbus.api.Event.Result.ALLOW
                : r == Event.Result.DENY ? net.minecraftforge.eventbus.api.Event.Result.DENY : net.minecraftforge.eventbus.api.Event.Result.DEFAULT;
    }'''),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/EventBridge1710.java": [
        ('''    private static TriState tri(Event.Result r) {
        return switch (r) {
            case ALLOW -> TriState.TRUE;
            case DENY -> TriState.FALSE;
            default -> TriState.DEFAULT;
        };
    }''',
         '''    /** The legacy verdict as the modern interact event's ({@code TriState} does not exist on 1.20.1}). */
    private static net.minecraftforge.eventbus.api.Event.Result useResult(Event.Result r) {
        return switch (r) {
            case ALLOW -> net.minecraftforge.eventbus.api.Event.Result.ALLOW;
            case DENY -> net.minecraftforge.eventbus.api.Event.Result.DENY;
            default -> net.minecraftforge.eventbus.api.Event.Result.DEFAULT;
        };
    }'''),
        ("import net.minecraftforge.common.util.TriState;\n", ""),
        ('''        gameBus.addListener((ItemEntityPickupEvent.Pre e) -> {
            if (!wants(forge(), legacyconnector.v1_7_10.net.minecraftforge.event.entity.player.EntityItemPickupEvent.class)) return;
            // an item entity that was merged away has an empty stack; 1.7.10 never reported those, and handlers read the stack unchecked
            if (e.getItemEntity().getItem().isEmpty()) return;
            var legacy = new legacyconnector.v1_7_10.net.minecraftforge.event.entity.player.EntityItemPickupEvent(player(e.getPlayer()), (EntityItem) EntityBridge.wrap(e.getItemEntity()));
            if (forge().post(legacy) || legacy.getResult() == Event.Result.DENY) e.setCanPickup(net.minecraftforge.common.util.TriState.FALSE);
            else if (legacy.getResult() == Event.Result.ALLOW) e.setCanPickup(net.minecraftforge.common.util.TriState.TRUE);
        });''',
         '''        gameBus.addListener((net.minecraftforge.event.entity.player.EntityItemPickupEvent e) -> {
            if (!wants(forge(), legacyconnector.v1_7_10.net.minecraftforge.event.entity.player.EntityItemPickupEvent.class)) return;
            // an item entity that was merged away has an empty stack; 1.7.10 never reported those, and handlers read the stack unchecked
            if (e.getItem().getItem().isEmpty()) return;
            var legacy = new legacyconnector.v1_7_10.net.minecraftforge.event.entity.player.EntityItemPickupEvent(player(e.getEntity()), (EntityItem) EntityBridge.wrap(e.getItem()));
            // 1.20.1 has a single pickup event whose cancellation forbids the pickup (1.20.5 added the force-pickup verdict)
            if (forge().post(legacy) || legacy.getResult() == Event.Result.DENY) e.setCanceled(true);
        });'''),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/adapter/LegacyBlockAdapter.java": [
        ('''    public net.minecraftforge.common.util.TriState canSustainPlant(BlockState state, BlockGetter level, BlockPos pos, Direction facing,
            BlockState plant) {''',
         '''    public boolean canSustainPlant(BlockState state, BlockGetter level, BlockPos pos, Direction facing, BlockState plant) {'''),
        ('''            return ok ? net.minecraftforge.common.util.TriState.TRUE : net.minecraftforge.common.util.TriState.FALSE;
        } catch (RuntimeException | LinkageError e) {
            return net.minecraftforge.common.util.TriState.DEFAULT;
        }''',
         '''            return ok;
        } catch (RuntimeException | LinkageError e) {
            return super.canSustainPlant(state, level, pos, facing, plant);
        }'''),
    ],
}

for path, pairs in EDITS.items():
    src = open(path, encoding="utf-8").read()
    for old, new in pairs:
        n = src.count(old)
        if n != 1:
            print(f"ABORT {n} matches in {path}: {old.splitlines()[0][:70]!r}")
            sys.exit(1)
        src = src.replace(old, new)
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

# every tri(...) call site becomes useResult(...)
for path in ("src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/EventBridge1710.java",
             "src/main/java/org/kylepitcock/legacyconnector/v1_12_2/bridge/EventBridge1122.java"):
    src = open(path, encoding="utf-8").read()
    n = src.count("tri(")
    src = src.replace("tri(", "useResult(")
    open(path, "w", encoding="utf-8", newline="").write(src)
    print(f"renamed {n} tri(...) call sites in {path}")

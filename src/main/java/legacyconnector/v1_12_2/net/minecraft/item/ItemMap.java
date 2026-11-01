package legacyconnector.v1_12_2.net.minecraft.item;

import legacyconnector.v1_12_2.net.minecraft.world.World;
import legacyconnector.v1_12_2.net.minecraft.world.storage.MapData;

/**
 * 1.12.2 filled map: its metadata is the map id. The map's data is the modern map's ({@code MapItemSavedData}), read into a legacy
 * {@link MapData} view; new maps, biome previews (explorer maps) and drawing are the modern map item's.
 */
public class ItemMap extends ItemMapBase {
    protected ItemMap() {
        setHasSubtypes(true);
    }

    private static net.minecraft.world.item.ItemStack modern(ItemStack stack) {
        var m = org.kylepitcock.legacyconnector.v1_12_2.bridge.Stacks1122.toModernLive(stack);
        if (m.isEmpty() || !org.kylepitcock.legacyconnector.core.data.ItemData.hasMapId(m)) {
            m = new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.FILLED_MAP);
            org.kylepitcock.legacyconnector.core.data.ItemData.setMapId(m, stack.getMetadata());
        }
        return m;
    }

    /** A new filled map centred on a position (the modern map item makes and registers its data). */
    public static ItemStack setupNewMap(World worldIn, double worldX, double worldZ, byte scale, boolean trackingPosition, boolean unlimitedTracking) {
        var level = worldIn == null ? null : worldIn.mcc$level();
        if (level == null) return ItemStack.EMPTY;
        var made = net.minecraft.world.item.MapItem.create(level, (int) Math.floor(worldX), (int) Math.floor(worldZ), scale, trackingPosition, unlimitedTracking);
        return org.kylepitcock.legacyconnector.v1_12_2.bridge.Stacks1122.fromModern(made);
    }

    /** The data of map {@code mapId} (null when there is no such map). */
    public static MapData loadMapData(int mapId, World worldIn) {
        var level = worldIn == null ? null : worldIn.mcc$level();
        if (level == null) return null;
        var data = net.minecraft.world.item.MapItem.getSavedData(mapId, level);
        return data == null ? null : MapData.mcc$of(net.minecraft.world.item.MapItem.makeKey(mapId), data);
    }

    /** The data of the map a stack shows (null when the map has none yet). */
    public MapData getMapData(ItemStack stack, World worldIn) {
        var level = worldIn == null ? null : worldIn.mcc$level();
        if (level == null || stack == null || stack.isEmpty()) return null;
        var m = modern(stack);
        var data = net.minecraft.world.item.MapItem.getSavedData(m, level);
        if (data == null) return null;
        Integer id = net.minecraft.world.item.MapItem.getMapId(m);
        return MapData.mcc$of(id == null ? "map_" + stack.getMetadata() : net.minecraft.world.item.MapItem.makeKey(id), data);
    }

    /** Draws the biomes of the map's area into it (explorer maps): the modern map item's preview. */
    public static void renderBiomePreviewMap(World worldIn, ItemStack map) {
        if (worldIn == null || !(worldIn.mcc$level() instanceof net.minecraft.server.level.ServerLevel level) || map == null || map.isEmpty()) return;
        net.minecraft.world.item.MapItem.renderBiomePreviewMap(level, modern(map));
    }

    /** Redraws the part of the map around an entity holding it (the modern map item's drawing). */
    public void updateMapData(World worldIn, legacyconnector.v1_12_2.net.minecraft.entity.Entity viewer, MapData data) {
        var level = worldIn == null ? null : worldIn.mcc$level();
        if (level == null || viewer == null || viewer.mcc$entity == null || data == null) return;
        var modern = net.minecraft.world.item.MapItem.getSavedData(mcc$idOf(data), level);
        if (modern != null) ((net.minecraft.world.item.MapItem) net.minecraft.world.item.Items.FILLED_MAP).update(level, viewer.mcc$entity, modern);
    }

    private static int mcc$idOf(MapData data) {
        String name = data.mapName;
        int i = name == null ? -1 : name.lastIndexOf('_');
        try {
            return i < 0 ? 0 : Integer.parseInt(name.substring(i + 1));
        } catch (NumberFormatException e) {
            return 0;
        }
    }

    /** A map stack tracked by its holder (the modern map item ticks the tracking itself). */
    @Override
    public void onUpdate(ItemStack stack, World worldIn, legacyconnector.v1_12_2.net.minecraft.entity.Entity entityIn, int itemSlot, boolean isSelected) {
        var level = worldIn == null ? null : worldIn.mcc$level();
        if (level == null || entityIn == null || entityIn.mcc$entity == null || stack.mcc$backing() != null) return;
        net.minecraft.world.item.Items.FILLED_MAP.inventoryTick(modern(stack), level, entityIn.mcc$entity, itemSlot, isSelected);
    }

    /** Scales a map up one step (the modern map item's crafting). */
    protected static void scaleMap(ItemStack stack, World worldIn, int scale) {
        var level = worldIn == null ? null : worldIn.mcc$level();
        if (level == null) return;
        var m = modern(stack);
        // 1.20.1's onCraftedPostProcess is what scales a map up (1.21 marks the stack with MapPostProcessing.SCALE first).
        m.getItem().onCraftedBy(m, level, m.getOwner());
        Integer id = net.minecraft.world.item.MapItem.getMapId(m);
        if (id != null) stack.setItemDamage(id);
    }

    /** Turns on the player markers of a map (crafted with a compass); a modern map's tracking is fixed when it is made, so it stays. */
    protected static void enableMapTracking(ItemStack stack, World worldIn) {
    }
}

"""1.20.1 map decoration types are an enum, banner patterns live in NBT, loot tables come from LootDataManager."""
import os
import sys

# ---- map decorations: MapDecorationTypes (registry, 1.20.5+) -> MapDecoration.Type (enum)
P = r"src/main/java/legacyconnector/v1_12_2/net/minecraft/world/storage/MapDecoration.java"
src = open(P, encoding="utf-8").read()
src = src.replace("net.minecraft.core.Holder<net.minecraft.world.level.saveddata.maps.MapDecorationType>",
                  "net.minecraft.world.level.saveddata.maps.MapDecoration.Type")
src = src.replace("net.minecraft.world.level.saveddata.maps.MapDecorationTypes.",
                  "net.minecraft.world.level.saveddata.maps.MapDecoration.Type.")
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P)

# ---- loot tables: LootDataManager through the server's resources (the LOOT_TABLE registry is 1.20.5+)
P = r"src/main/java/legacyconnector/v1_12_2/net/minecraft/world/storage/loot/LootTableManager.java"
src = open(P, encoding="utf-8").read()
old = """        var key = net.minecraft.resources.ResourceKey.create(net.minecraft.core.registries.Registries.LOOT_TABLE,
                net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(location.getNamespace(), location.getPath()));
        return LootTable.mcc$view(server.reloadableRegistries().getLootTable(key));"""
new = """        // 1.20.1 resolves loot tables through the server's LootDataManager (the LOOT_TABLE registry is 1.20.5).
        var id = net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(location.getNamespace(), location.getPath());
        var data = new net.minecraft.world.level.storage.loot.LootDataId<>(
                net.minecraft.world.level.storage.loot.LootDataType.TABLE, id);
        return LootTable.mcc$view(server.getServerResources().managers().getLootData().getElement(data));"""
if src.count(old) != 1:
    print("ABORT LootTableManager:", src.count(old))
    sys.exit(1)
open(P, "w", encoding="utf-8", newline="").write(src.replace(old, new))
print("patched", P)

# ---- banner patterns: 1.20.1 keeps them in the block entity / item NBT
P = r"src/main/java/legacyconnector/v1_12_2/net/minecraft/tileentity/TileEntityBanner.java"
src = open(P, encoding="utf-8").read()
pairs = [
    ("        patterns = mcc$patternsTag(mcc$banner.getPatterns());",
     "        patterns = mcc$patternsTag(mcc$banner);"),
    ("""    /** Modern banner layers as a 1.12 {@code Patterns} list. */
    private static NBTTagList mcc$patternsTag(net.minecraft.world.level.block.entity.BannerPatternLayers layers) {
        NBTTagList list = new NBTTagList();
        if (layers == null) return list;
        for (var layer : layers.layers()) {
            var key = layer.pattern().unwrapKey();
            if (key.isEmpty()) continue;
            BannerPattern pattern = null;
            for (BannerPattern p : BannerPattern.values()) if (p.getFileName().equals(key.get().location().getPath())) pattern = p;
            if (pattern == null) continue;
            NBTTagCompound c = new NBTTagCompound();
            c.setString("Pattern", pattern.getHashname());
            c.setInteger("Color", EnumDyeColor.byMetadata(layer.color().getId()).getDyeDamage());
            list.appendTag(c);
        }
        return list;
    }""",
     """    /**
     * A banner's layers as a 1.12 {@code Patterns} list.
     *
     * <p>1.20.1 has no banner pattern data component: the block entity and the item both carry the 1.20.1 pattern list in their
     * NBT, in the same {@code {Pattern, Color}} shape 1.12 used, so the list is read straight from there.</p>
     */
    private static NBTTagList mcc$patternsTag(net.minecraft.world.level.block.entity.BannerBlockEntity banner) {
        NBTTagList list = new NBTTagList();
        if (banner == null) return list;
        var tag = banner.saveWithoutId(new net.minecraft.nbt.CompoundTag());
        for (var entry : tag.getList("Patterns", 10)) list.appendTag(new NBTTagCompound((net.minecraft.nbt.CompoundTag) entry));
        return list;
    }"""),
    ("""    private static NBTTagList mcc$patterns(ItemStack stack) {
        var backing = stack.mcc$backing();
        if (backing != null && backing.has(net.minecraft.core.component.DataComponents.BANNER_PATTERNS)) {
            return mcc$patternsTag(backing.get(net.minecraft.core.component.DataComponents.BANNER_PATTERNS));
        }
        NBTTagCompound nbt = stack.getSubCompound("BlockEntityTag");""",
     """    private static NBTTagList mcc$patterns(ItemStack stack) {
        NBTTagCompound nbt = stack.getSubCompound("BlockEntityTag");"""),
]
for old, new in pairs:
    if src.count(old) != 1:
        print(f"ABORT TileEntityBanner {src.count(old)}: {old.splitlines()[0][:60]}")
        sys.exit(1)
    src = src.replace(old, new)
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P)

# ---- item rendering: 1.20.1 has no alpha parameter in putBulkData
P = r"src/main/java/legacyconnector/v1_12_2/net/minecraft/client/renderer/RenderItem.java"
src = open(P, encoding="utf-8").read()
old = "buffer.putBulkData(pose.last(), quad, r, g, b, a, RenderContext.vertexLight(), RenderContext.overlay())"
n = src.count(old)
if n != 2:
    print("ABORT RenderItem:", n)
    sys.exit(1)
src = src.replace(old,
                  "// 1.20.1's putBulkData has no alpha argument (the 1.20.6 overload does); the shim's tint is opaque.\n"
                  "            buffer.putBulkData(pose.last(), quad, r, g, b, RenderContext.vertexLight(), RenderContext.overlay())")
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P)

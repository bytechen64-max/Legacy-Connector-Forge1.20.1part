"""The remaining capability call sites: the bridges' registerItem calls become ItemCapabilities.attach."""
import sys

EDITS = {
    r"src/main/java/org/kylepitcock/legacyconnector/LegacyConnector.java": [
        ("""        var type = org.kylepitcock.legacyconnector.v1_7_10.bridge.TileEntityBridge.type();
        if (type == null) return;
        event.registerBlockEntity(net.minecraftforge.common.capabilities.ForgeForgeCapabilities.ITEM_HANDLER, type, (be, side) ->
                org.kylepitcock.legacyconnector.api.internal.BuiltinAdapters.inventory1710(be.legacy(), side, be));""",
         "        // the legacy tiles' item handlers are one of the rules CapabilityRules attaches (see INVENTORY_ITEMS)"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/EnergyBridge.java": [
        ("""        var type = TileEntityBridge.type();
        if (type != null) {
            event.registerBlockEntity(ForgeCapabilities.ENERGY, type, (be, side) -> forTile(be.legacy(), side));
        }
        for (Item item : ItemBridge.modItems()) {
            if (!(item instanceof IEnergyContainerItem container)) continue;
            event.registerItem(ForgeCapabilities.ENERGY, (stack, ctx) -> new ItemStorage(container, stack),
                    item.mcc$variants.values().toArray(new net.minecraft.world.item.Item[0]));
        }""",
         """        // tile energy is a CapabilityRules built-in (RF_ENERGY); items attach their capability to the stack
        for (Item item : ItemBridge.modItems()) {
            if (!(item instanceof IEnergyContainerItem container)) continue;
            org.kylepitcock.legacyconnector.api.internal.ItemCapabilities.attach(net.minecraftforge.energy.IEnergyStorage.class,
                    (stack, ctx) -> new ItemStorage(container, stack),
                    item.mcc$variants.values().toArray(new net.minecraft.world.item.Item[0]));
        }"""),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/FluidBridge.java": [
        ("""        var type = TileEntityBridge.type();
        if (type != null) {
            event.registerBlockEntity(ForgeCapabilities.FLUID_HANDLER, type, (be, side) -> forTile(be.legacy(), side));
        }
        for (legacyconnector.v1_7_10.net.minecraft.item.Item item : ItemBridge.modItems()) {
            if (!(item instanceof IFluidContainerItem container)) continue;
            event.registerItem(ForgeCapabilities.FLUID_HANDLER_ITEM, (stack, ctx) -> new ItemHandler(container, stack),
                    item.mcc$variants.values().toArray(new net.minecraft.world.item.Item[0]));
        }""",
         """        // tile fluids are a CapabilityRules built-in (FLUIDS_1710); items attach their capability to the stack
        for (legacyconnector.v1_7_10.net.minecraft.item.Item item : ItemBridge.modItems()) {
            if (!(item instanceof IFluidContainerItem container)) continue;
            org.kylepitcock.legacyconnector.api.internal.ItemCapabilities.attach(net.minecraftforge.fluids.capability.IFluidHandlerItem.class,
                    (stack, ctx) -> new ItemHandler(container, stack),
                    item.mcc$variants.values().toArray(new net.minecraft.world.item.Item[0]));
        }"""),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/ForeignEnergy1710.java": [
        ("            event.registerItem(net.minecraftforge.common.capabilities.ForgeForgeCapabilities.ENERGY, (stack, ctx) -> new ItemStorage(api, stack),\n"
         "                    item.mcc$variants.values().toArray(new net.minecraft.world.item.Item[0]));",
         "            org.kylepitcock.legacyconnector.api.internal.ItemCapabilities.attach(net.minecraftforge.energy.IEnergyStorage.class,\n"
         "                    (stack, ctx) -> new ItemStorage(api, stack),\n"
         "                    item.mcc$variants.values().toArray(new net.minecraft.world.item.Item[0]));"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/bridge/ItemCapabilities1122.java": [
        ("            event.registerItem(ForgeCapabilities.FLUID_HANDLER_ITEM, (stack, ctx) -> has(stack, CapabilityFluidHandler.FLUID_HANDLER_CAPABILITY) ? FluidBridge1122.forStack(stack) : null, variants);\n"
         "            event.registerItem(ForgeCapabilities.ENERGY, (stack, ctx) -> has(stack, CapabilityEnergy.ENERGY) ? new Energy(stack) : null, variants);\n"
         "            event.registerItem(Capabilities.ItemHandler.ITEM, (stack, ctx) -> has(stack, CapabilityItemHandler.ITEM_HANDLER_CAPABILITY) ? new Items(stack) : null, variants);",
         "            org.kylepitcock.legacyconnector.api.internal.ItemCapabilities.attach(net.minecraftforge.fluids.capability.IFluidHandlerItem.class,\n"
         "                    (stack, ctx) -> has(stack, CapabilityFluidHandler.FLUID_HANDLER_CAPABILITY) ? FluidBridge1122.forStack(stack) : null, variants);\n"
         "            org.kylepitcock.legacyconnector.api.internal.ItemCapabilities.attach(net.minecraftforge.energy.IEnergyStorage.class,\n"
         "                    (stack, ctx) -> has(stack, CapabilityEnergy.ENERGY) ? new Energy(stack) : null, variants);\n"
         "            org.kylepitcock.legacyconnector.api.internal.ItemCapabilities.attach(net.minecraftforge.items.IItemHandler.class,\n"
         "                    (stack, ctx) -> has(stack, CapabilityItemHandler.ITEM_HANDLER_CAPABILITY) ? new Items(stack) : null, variants);"),
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

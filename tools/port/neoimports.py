"""Mechanical NeoForge 21.x -> Forge 1.20.1 migration.

Run:  python tools/port/neoimports.py <root>
Rewrites package/import names of the NeoForge API onto the Forge 1.20.1 names.  Everything that is
not a pure rename (different event shapes, networking, capabilities, client extension points) is left
to the compiler-driven pass; this script only removes the bulk of the noise.
"""
import os
import re
import sys

# Longest / most specific first. Applied to every file, both import lines and inlined FQNs.
EXACT = [
    # NeoForge -> MinecraftForge entry points
    ("net.neoforged.neoforge.common.NeoForge;", "net.minecraftforge.common.MinecraftForge;"),
    ("net.neoforged.neoforge.common.NeoForgeMod;", "net.minecraftforge.common.ForgeMod;"),
    ("net.neoforged.neoforge.common.CommonHooks;", "net.minecraftforge.common.ForgeHooks;"),
    ("net.neoforged.neoforge.registries.NeoForgeRegistries;", "net.minecraftforge.registries.ForgeRegistries;"),
    ("net.neoforged.neoforge.common.DeferredSpawnEggItem;", "net.minecraftforge.common.ForgeSpawnEggItem;"),
    ("net.neoforged.neoforge.entity.IEntityWithComplexSpawn;", "net.minecraftforge.entity.IEntityAdditionalSpawnData;"),
    ("net.neoforged.neoforge.common.extensions.IMenuTypeExtension", "net.minecraftforge.common.extensions.IForgeMenuType"),
    ("net.neoforged.neoforge.registries.DeferredHolder", "net.minecraftforge.registries.RegistryObject"),
    # capabilities live under common.capabilities in Forge, and the registry is ForgeCapabilities
    ("net.neoforged.neoforge.capabilities.Capabilities", "net.minecraftforge.common.capabilities.ForgeCapabilities"),
    ("net.neoforged.neoforge.capabilities.RegisterCapabilitiesEvent;", "net.minecraftforge.common.capabilities.RegisterCapabilitiesEvent;"),
    ("net.neoforged.neoforge.capabilities.BlockCapability", "net.minecraftforge.common.capabilities.BlockCapability"),
    ("net.neoforged.neoforge.capabilities.ICapabilityProvider;", "net.minecraftforge.common.capabilities.ICapabilityProvider;"),
    ("net.neoforged.neoforge.capabilities.", "net.minecraftforge.common.capabilities."),
    # tick events: one TickEvent class with nested types in Forge 1.20.1
    ("net.neoforged.neoforge.event.tick.ServerTickEvent;", "net.minecraftforge.event.TickEvent.ServerTickEvent;"),
    ("net.neoforged.neoforge.event.tick.ClientTickEvent;", "net.minecraftforge.event.TickEvent.ClientTickEvent;"),
    ("net.neoforged.neoforge.event.tick.LevelTickEvent;", "net.minecraftforge.event.TickEvent.LevelTickEvent;"),
    ("net.neoforged.neoforge.event.tick.PlayerTickEvent;", "net.minecraftforge.event.TickEvent.PlayerTickEvent;"),
    ("net.neoforged.neoforge.event.tick.RenderTickEvent;", "net.minecraftforge.event.TickEvent.RenderTickEvent;"),
    # 1.21 names that 1.20.1 spells differently
    ("net.neoforged.neoforge.event.entity.player.ItemEntityPickupEvent;", "net.minecraftforge.event.entity.player.EntityItemPickupEvent;"),
    ("net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;", "net.minecraftforge.event.entity.living.LivingHurtEvent;"),
    ("net.neoforged.neoforge.event.entity.living.LivingFallEvent;", "net.minecraftforge.event.entity.living.LivingFallEvent;"),
    ("net.neoforged.neoforge.event.level.BlockDropsEvent;", "net.minecraftforge.event.level.BlockEvent.BreakEvent;"),
    ("net.neoforged.neoforge.event.furnace.FurnaceFuelBurnTimeEvent;", "net.minecraftforge.event.furnace.FurnaceFuelBurnTimeEvent;"),
]

PREFIX = [
    ("net.neoforged.neoforge.", "net.minecraftforge."),
    ("net.neoforged.bus.api.", "net.minecraftforge.eventbus.api."),
    ("net.neoforged.fml.", "net.minecraftforge.fml."),
    ("net.neoforged.neoforgespi.", "net.minecraftforge.forgespi."),
    ("net.neoforged.", "net.minecraftforge."),
]

IDENT = [
    ("NeoForge.EVENT_BUS", "MinecraftForge.EVENT_BUS"),
    ("NeoForgeMod.", "ForgeMod."),
    ("CommonHooks.", "ForgeHooks."),
    ("NeoForgeRegistries.", "ForgeRegistries."),
    ("DeferredSpawnEggItem", "ForgeSpawnEggItem"),
    ("IEntityWithComplexSpawn", "IEntityAdditionalSpawnData"),
    # capabilitity registry: Capabilities.ItemHandler.BLOCK -> ForgeCapabilities.ITEM_HANDLER (further arity fixes are compile-driven)
    ("Capabilities.ItemHandler.BLOCK", "ForgeCapabilities.ITEM_HANDLER"),
    ("Capabilities.ItemHandler.ENTITY", "ForgeCapabilities.ITEM_HANDLER"),
    ("Capabilities.ItemHandler.ENTITY_AUTOMATION", "ForgeCapabilities.ITEM_HANDLER"),
    ("Capabilities.FluidHandler.BLOCK", "ForgeCapabilities.FLUID_HANDLER"),
    ("Capabilities.FluidHandler.ITEM", "ForgeCapabilities.FLUID_HANDLER_ITEM"),
    ("Capabilities.EnergyStorage.BLOCK", "ForgeCapabilities.ENERGY"),
    ("Capabilities.EnergyStorage.ITEM", "ForgeCapabilities.ENERGY"),
]


def rewrite(text: str) -> str:
    for old, new in EXACT:
        text = text.replace(old, new)
    for old, new in PREFIX:
        text = text.replace(old, new)
    for old, new in IDENT:
        text = text.replace(old, new)
    return text


def drop_first_type_arg(text: str, name: str) -> str:
    """DeferredHolder<R, T> -> RegistryObject<T>: drop the first type argument of every `name<...>`."""
    out = []
    i = 0
    while True:
        j = text.find(name + "<", i)
        if j < 0:
            out.append(text[i:])
            break
        out.append(text[i:j])
        # find the matching '>' for the '<' at j + len(name)
        k = j + len(name)
        depth = 0
        args = []
        cur = k + 1
        start = k + 1
        while cur < len(text):
            c = text[cur]
            if c == "<":
                depth += 1
            elif c == ">":
                if depth == 0:
                    args.append(text[start:cur])
                    break
                depth -= 1
            elif c == "," and depth == 0:
                args.append(text[start:cur])
                start = cur + 1
            cur += 1
        if len(args) >= 2:
            out.append(name + "<" + ",".join(args[1:]) + ">")
        else:
            out.append(name + "<" + ("".join(args)) + ">")
        i = cur + 1
    return "".join(out)


def main(root: str) -> None:
    changed = 0
    scanned = 0
    for base in ("src", "loader/src", "testmods/src", "examples", "tools"):
        for dirpath, _dirs, files in os.walk(os.path.join(root, base)):
            for fn in files:
                if not fn.endswith(".java"):
                    continue
                p = os.path.join(dirpath, fn)
                scanned += 1
                with open(p, encoding="utf-8", errors="surrogateescape") as f:
                    src = f.read()
                if "neoforged" not in src and "DeferredHolder" not in src and "NeoForge" not in src:
                    continue
                new = rewrite(src)
                new = drop_first_type_arg(new, "RegistryObject")
                new = new.replace("RegistryObject<R, T>", "RegistryObject<T>")
                if new != src:
                    with open(p, "w", encoding="utf-8", errors="surrogateescape", newline="") as f:
                        f.write(new)
                    changed += 1
    print(f"scanned {scanned} java files, rewrote {changed}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")

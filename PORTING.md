# Porting Legacy Connector to Forge 1.20.1

Status of the NeoForge 1.21.1 â†?Forge 1.20.1 port, and the migration map for what is left.

## What is done

Build system (all three projects) â€?`gradle.properties`, `build.gradle`, `loader/build.gradle`:

| | before | after |
|---|---|---|
| loader plugin | `net.neoforged.moddev` 2.0.148 | ForgeGradle 6 (`net.minecraftforge.gradle`) |
| game / loader | NeoForge 21.1.258, FML 4.x | Forge 47.4.28, FML 47.x (`forgespi` 7.0.1, `fmlloader`/`fmlcore` 1.20.1-47.4.28, modlauncher 10.0.9) |
| mappings | official 1.21.1 + parchment | official 1.20.1 |
| Java | 21 | 17 |
| metadata | `META-INF/neoforge.mods.toml` (`[[mixins]]`, `[[accessTransformers]]`, `type=` deps) | `META-INF/mods.toml` (`mandatory=` deps); mixins move to the jar manifest `MixinConfigs`; the AT stays `META-INF/accesstransformer.cfg` |
| optional mods | 1.21.1/NeoForge builds | 1.20.1 Forge builds (Curios 5.11.0, Jade 11.13.1, JEI 15.20, Create `mc1.20.1-6.0.8` via Modrinth maven, TerraBlender 3.0.1.11, Pehkui 3.8.2) |

`:loader` compiles. It is a service-layer project, so it was ported against the Forge 1.20.1 SPI directly:

- `IModFileCandidateLocator` + `IDiscoveryPipeline` + `ILaunchContext` (NeoForge 21.2+) â†?**`IModLocator`**
  (`scanMods()` returns `IModLocator.ModFileOrException` built with `ModFileFactory.FACTORY.build(SecureJar.from(jar), this,
  ModFileParser::modsTomlParser)`). Service file renamed to `META-INF/services/net.minecraftforge.forgespi.locating.IModLocator`.
- `pipeline.addPath(p, â€?` â†?the locator collects the paths and reports them as `IModFile`s; `BundledLibraries.provide`
  takes a `Consumer<Path>` instead of the pipeline.
- `pipeline.addIssue(ModLoadingIssueâ€?` â†?logged (Forge 1.20.1 has no issue list on the discovery path).
- **Discovery hook difference.** Forge 1.20.1 has no "claim this path" call, so a legacy jar left in the top level of `mods/`
  is also read by Forge's own `ModsFolderLocator` and rejected ("built for an older Forge"). `LegacyModLocator.relocateOriginals`
  therefore *moves* the translated originals to `mods/.legacyconnector/originals/` (config key `loader.relocateLegacyJars`,
  default `true`; the jar bytes are never modified) and the loader scans that folder too. Note for later: a jar that declares
  `net.minecraftforge.forgespi.locating.IModLocator` in a real `module-info.class` is picked up before `ModsFolderLocator` runs
  (`ModDirTransformerDiscoverer`, which excludes it from the folder scan), so packaging the loader as a real JPMS module would
  replace the move with a clean exclusion â€?worth doing before release.
- Generated mods: `META-INF/mods.toml` (Forge schema, `mandatory=` instead of `type=`), `Lnet/minecraftforge/fml/common/Mod;`
  annotation and the `(IEventBus, ModContainer)` constructor descriptor for the generated entrypoints.
- Java 17 baseline: the two pattern-matching `switch` expressions were rewritten as `instanceof` chains
  (`AbsentDependencyStubber.missingIn`, `RecipeBridge`).
- ForgeGradle's configuration-time "server connection" probe hangs for minutes behind a stalling TLS handshake here; it is
  disabled with `net.minecraftforge.gradle.check.{certs,gradle,java}=false` in `gradle.properties`.

Whole-tree rewrite (3757 Java files, `tools/port/*.py`): `net.neoforged.*` â†?`net.minecraftforge.*` (`eventbus.api`,
`forgespi`, `event.*`, `registries.RegistryObject`, `common.capabilities.ForgeCapabilities`, `common.MinecraftForge`,
`ForgeMod`, `ForgeHooks`, `event.TickEvent.*`, `extensions.IForgeMenuType`, â€?, `NeoForge.EVENT_BUS` â†?`MinecraftForge.EVENT_BUS`,
`DeferredHolder<R, T>` â†?`RegistryObject<T>`, and `ResourceLocation.fromNamespaceAndPath/parse/withDefaultNamespace` â†?`new ResourceLocation(...)`.

## Build / check loop

```bash
./gradlew :loader:compileJava                 # the service layer alone (fast)
./gradlew compileJava -PskipShimWidener       # type-check the runtime mod only (no loader mappings, incremental)
./gradlew build                               # everything, including the shim widener + shim index
```

`-PskipShimWidener` also switches `compileJava` back to incremental compilation; without it the widener rewrites the class
files in place, which needs a full recompile every time.

## What is left (the 1.21.1 â†?1.20.1 API downgrade in the runtime mod)

440 compile errors at the last run (the count moves as javac gets further into the tree), in categories that are each one API decision. Highest value first:

1. **Networking** (`core/network/*`, `*bridge/NetworkBridge*`, `FmlChannelBridge*`, `GuiBridge*`, `SimpleNetworkWrapper`).
   1.21 `CustomPacketPayload` + `StreamCodec` + `RegisterPayloadHandlersEvent` + `IPayloadContext` + `PacketDistributor`
   do not exist in 1.20.1. Plan: keep `LegacyPayload` as a plain record with `write/read(FriendlyByteBuf)`, register a
   `SimpleChannel` (`NetworkRegistry.ChannelBuilder.named(...)`) with two directions, wrap `NetworkEvent.Context` in a small
   `LegacyPayloadContext` (`player()`, `connection()`, `enqueueWork`, `reply`), and add a `LegacyChannel` facade with the
   `sendToPlayer/sendToServer/sendToAllPlayers/sendToPlayersInDimension/sendToPlayersNear/sendToPlayersTrackingChunk/
   sendToPlayersTrackingEntity` shapes the bridges already call (`PacketDistributor.PLAYER.with(...).send(...)` underneath).
2. **Data components** (`CompatComponents`, `legacyconnector/**/ItemStack`, `Stacks1122`, `PotionContents`).
   `DataComponentType`/`DataComponents`/`ItemStack.set/get(component)` do not exist before 1.20.5: use
   `ItemStack.getOrCreateTag()`/`getTagElement` NBT with the same keys, and a `CompatComponents` wrapper with those semantics.
3. **Resource packs** (`GeneratedPack`, `GameResourcesFolderPack`, `LegacyModPacks`): `PackLocationInfo`/`PackSelectionConfig`
   are 1.20.4+; 1.20.1 uses `PackResources` + `PackType`/`PackSource`/`Pack.Position` and `PackType.SERVER_DATA`.
4. **Scoreboard / advancements** (`v1_12_2/scoreboard/*`, `v1_12_2/advancements/*`): `ScoreHolder`, `ScoreAccess`,
   `DisplaySlot`, `AdvancementHolder`, `AdvancementTree`, `AdvancementType` are 1.20.5+. 1.20.1 keys scores by `String`
   player name, `Advancement` is the object itself, and display slots are the `int`/`ObjectiveCriteria.RenderType` pair.
5. **Recipes** (`RecipeHolder`, `CraftingInput`, `RecipeManager`): 1.20.1 has no `RecipeHolder`/`CraftingInput` wrapper â€?   `RecipeManager` stores `Recipe<?>` and crafting gets an `Inventory`/`CraftingContainer`.
6. **Forge hooks that only NeoForge has**: `TriState`, `ItemAbility`, `RegisterClientExtensionsEvent`, `RenderGuiLayerEvent`,
   `ClientTickEvent` (now fixed), `InsertableLinkedOpenCustomHashSet`. 1.20.1 replacements: `Boolean`/nullable for `TriState`,
   `IForgeItem#onItemUseFirst`-style hooks for `ItemAbility`, `Item#initializeClient` for client extensions,
   `net.minecraftforge.client.event.RenderGuiOverlayEvent` + `overlay.VanillaGuiOverlay` for GUI layers.
7. **Worldgen / chunk status** (`net.minecraft.world.level.chunk.status.*`, `WorldGenRegion`, `ChunkMap`): 1.20.1 uses
   `ChunkStatus` directly and `ChunkMap.getVisibleChunkIfPresent` is protected (add an AT entry).
8. **Mixins**: `com.llamalad7.mixinextras.*` is bundled by NeoForge but is a separate dependency on Forge 1.20.1. Either add
   MixinExtras (`io.github.llamalad7:mixinextras-forge` + the runtime mod) or rewrite the two `@WrapOperation` mixins as
   `@Redirect`.
9. Smaller items: `Holder<MobEffect>` â†?`MobEffect` (effects became holders in 1.20.5), `PathType` â†?`BlockPathTypes` (done),
   `BlockSource` â†?`net.minecraft.core.BlockSourceImpl`/`net.minecraft.core.dispenser.*`, `ItemCost` â†?`merchant`
   `ItemStack`/emerald cost, `Entity#getTarget`/`accelerationPower`/`portalProcess` field renames, `LevelData#getSpawnPos`,
   `Explosion#center`, `ChunkMap#getChunks` AT entries, `SynchedEntityData.Builder`, `Criterion<T>` generics,
   `getPartialTick().getGameTimeDeltaPartialTick()` â†?`renderTickCounter`, and `RegisterBrewingRecipesEvent`
   (1.20.1 has `PotionBrewEvent`/`BrewingRecipeRegistry`).

Once the compile is clean, the remaining runtime work is: register the loader's `IModLocator` as a JPMS module (Â§ above),
`FMLModType`/manifest packaging for the bundle jar, and a `runServerSubTest` pass with real legacy jars.

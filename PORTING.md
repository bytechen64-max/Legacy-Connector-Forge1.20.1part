# Porting Legacy Connector to Forge 1.20.1

Status of the NeoForge 1.21.1 -> Forge 1.20.1 port: what is done, and the migration map for what is left.

## What is done

Build system (all three projects) -- `gradle.properties`, `build.gradle`, `loader/build.gradle`:

| | before | after |
|---|---|---|
| loader plugin | `net.neoforged.moddev` 2.0.148 | ForgeGradle 6 (`net.minecraftforge.gradle`) |
| game / loader | NeoForge 21.1.258, FML 4.x | Forge 47.4.28, FML 47.x (`forgespi` 7.0.1, `fmlloader`/`fmlcore` 1.20.1-47.4.28, modlauncher 10.0.9) |
| mappings | official 1.21.1 + parchment | official 1.20.1 |
| Java | 21 | 17 |
| metadata | `META-INF/neoforge.mods.toml` (`[[mixins]]`, `[[accessTransformers]]`, `type=` deps) | `META-INF/mods.toml` (`mandatory=` deps); mixins move to the jar manifest `MixinConfigs`; the AT stays `META-INF/accesstransformer.cfg` |
| optional mods | 1.21.1/NeoForge builds | 1.20.1 Forge builds (Curios 5.11.0, Jade 11.13.1, JEI 15.20, Create `mc1.20.1-6.0.8` via Modrinth maven, TerraBlender 3.0.1.11, Pehkui 3.8.2) |

`:loader` compiles (`./gradlew :loader:compileJava`). It is a service-layer project, so it was ported against the
Forge 1.20.1 SPI directly:

- `IModFileCandidateLocator` + `IDiscoveryPipeline` + `ILaunchContext` (NeoForge 21.2+) -> **`IModLocator`**
  (`scanMods()` returns `IModLocator.ModFileOrException` built with
  `ModFileFactory.FACTORY.build(SecureJar.from(jar), this, ModFileParser::modsTomlParser)`). Service file renamed to
  `META-INF/services/net.minecraftforge.forgespi.locating.IModLocator`.
- `pipeline.addPath(p, ...)` -> the locator collects the paths and reports them as `IModFile`s;
  `BundledLibraries.provide` takes a `Consumer<Path>` instead of the pipeline.
- `pipeline.addIssue(ModLoadingIssue...)` -> logged (Forge 1.20.1 has no issue list on the discovery path).
- **Discovery hook difference.** Forge 1.20.1 has no "claim this path" call, so a legacy jar left in the top level of
  `mods/` is also read by Forge's own `ModsFolderLocator` and rejected ("built for an older Forge").
  `LegacyModLocator.relocateOriginals` therefore *moves* the translated originals to `mods/.legacyconnector/originals/`
  (config key `loader.relocateLegacyJars`, default `true`; the jar bytes are never modified) and the loader scans that
  folder too. Better before release: ship the loader as a real JPMS module declaring
  `provides net.minecraftforge.forgespi.locating.IModLocator` -- `ModDirTransformerDiscoverer` then picks the jar up
  before `ModsFolderLocator` runs and excludes it from the folder scan, which replaces the move with a clean exclusion.
- Generated mods: `META-INF/mods.toml` (Forge schema, `mandatory=`), `Lnet/minecraftforge/fml/common/Mod;` annotation and
  the `(IEventBus, ModContainer)` constructor descriptor for the generated entrypoints.
- Java 17 baseline: the two pattern-matching `switch` expressions became `instanceof` chains
  (`AbsentDependencyStubber.missingIn`, `RecipeBridge`).

Whole-tree rewrite (3757 Java files, `tools/port/*.py`): `net.neoforged.*` -> `net.minecraftforge.*` (`eventbus.api`,
`forgespi`, `event.*`, `registries.RegistryObject`, `common.capabilities.ForgeCapabilities`, `common.MinecraftForge`,
`ForgeMod`, `ForgeHooks`, `event.TickEvent.*`, `extensions.IForgeMenuType`, ...), `NeoForge.EVENT_BUS` ->
`MinecraftForge.EVENT_BUS`, `DeferredHolder<R, T>` -> `RegistryObject<T>`, and
`ResourceLocation.fromNamespaceAndPath/parse/withDefaultNamespace` -> `new ResourceLocation(...)`.

Port work landed since (each in its own commit):

1. **Networking** (`core/network/*` + the six bridges). Forge 1.20.1 has no `CustomPacketPayload`/`StreamCodec`/
   `RegisterPayloadHandlersEvent`/`IPayloadContext`. `LegacyPayload` is a plain record with
   `write/read(FriendlyByteBuf)`; `LegacyNetwork` opens one `SimpleChannel`
   (`NetworkRegistry.ChannelBuilder` + `acceptMissingOr` for the old `optional()` semantics) from the mod constructor;
   `LegacyPayloadContext` is the bridge-facing view of `NetworkEvent.Context`; `LegacyChannel` offers the
   `PacketDistributor.sendXxx` audiences the call sites already used.
2. **`RegistryFriendlyByteBuf` -> `FriendlyByteBuf`** (menus, entity spawn data): the registry-aware buffer is 1.20.5+.
3. **MixinExtras** added as `compileOnly` (Maven Central 0.3.5): NeoForge bundles it, Forge 1.20.1 does not, and the
   three `@WrapOperation` mixins need it. *At runtime the MixinExtras mod must be installed* (or the jar bundled).
4. **`legacy_meta`**: the `DataComponentType` is replaced by the NBT key `legacyconnector:legacy_meta` with
   `CompatComponents.get/set/clear` helpers; all 25 call sites converted.
5. **Scoreboard** (`scoreboard/*` in both shims): 1.20.1 knows players by plain name (no `ScoreHolder`/`ScoreAccess`)
   and display slots by number (`Scoreboard.DISPLAY_SLOT_*`, no `DisplaySlot`); the legacy numbered slots including
   `sidebar.team.<colour>` are rebuilt from those constants.
6. **Entity portal state**: 1.20.1 keeps `isInsidePortal`/`portalTime`/`portalEntrancePos` where 1.20.5 has a
   `PortalProcessor`; the three fields are opened with AT entries.
7. **Client tick events**: `ClientTickEvent.Pre/.Post` -> one `TickEvent.ClientTickEvent` plus a phase guard (9 sites).

## Build / check loop

```bash
./gradlew :loader:compileJava                 # the service layer alone (seconds)
./gradlew compileJava -PskipShimWidener       # type-check the runtime mod only (no loader mappings, incremental)
./gradlew build                               # everything, including the shim widener + shim index
```

`-PskipShimWidener` also puts `compileJava` back on incremental compilation; without it the widener rewrites the class
files in place, which forces a full recompile every time. A full type-check of the runtime mod takes ~4-5 minutes.

## Gotchas found the hard way

- **ForgeGradle blocks at configuration time** on its "server connection" probe (`EnvironmentChecks.testServerConnection`)
  when the TLS handshake stalls. Disabled with
  `-Dnet.minecraftforge.gradle.check.{certs,gradle,java}=false` in `org.gradle.jvmargs`.
- **`MinecraftForge` was two classes.** The NeoForge rename collapsed `NeoForge.EVENT_BUS` (Forge's bus) into the same
  simple name the shims use for their *legacy* bus (`legacyconnector.v1_*...common.MinecraftForge`, which has
  `mcc$hasListeners`). In bridge files, `addListener(<modern event>)` is Forge's bus; `post(<legacy event>)` and
  `mcc$hasListeners` are the legacy one -- the latter are written out fully qualified.
- **`LivingIncomingDamageEvent` (1.21) is `LivingHurtEvent` in 1.20.1**, which the 1.7.10 shim also defines; that file
  qualifies the modern one at its two listener sites.

- **ForgeGradle does not apply a mod's access transformer to the compile classpath.** Forge applies it at runtime only, and rebuilding the mapped jar or deleting the AT step output does not
  change that; the members the shim needs are reached through Mixin accessors (`mixin/access/EntityAccess`,
  `mixin/access/ChunkMapAccess`) instead. Keep the `accesstransformer.cfg` for runtime, but do not rely on it to compile.
  The mixin configs must stay UTF-8 **without** BOM: Mixin's JSON parser rejects a BOM.

## What is left

703 compile errors at the last run (the count moves as javac gets further into the tree). Categories, highest value first:

1. **Item components** (~20). `DataComponents`/`CustomData`/`ItemEnchantments`/`PotionContents`/`ItemAttributeModifiers`
   are 1.20.5+; 1.20.1 has `stack.getTag()`/`getOrCreateTag()`, `EnchantmentHelper.getEnchantments`,
   `PotionUtils.getPotion/setPotion`, `Item.getDefaultAttributeModifiers(EquipmentSlot)`. `PotionContents` maps to
   `net.minecraft.world.item.alchemy.PotionUtils` (mind the shim's *legacy* `PotionUtils` class of the same name).
   `MapId` is a plain `int` (`MapItem.getMapId`/`setMapId`). `ItemAbility`/`ItemAbilities` are NeoForge-only:
   1.20.1 uses `net.minecraftforge.common.ToolAction`/`ToolActions` and `Item#canPerformAction(ToolAction)`.
   `PackType`/`PackSource`/`Pack.Position`.
5. **NeoForge-only hooks** (~10): `InsertableLinkedOpenCustomHashSet`, `RegisterClientExtensionsEvent`,
   `RenderGuiLayerEvent`/`VanillaGuiLayers`. 1.20.1: `Boolean`/nullable for `TriState`, `Item#initializeClient` for
   client extensions, `RenderGuiOverlayEvent` + `overlay.VanillaGuiOverlay` for GUI layers.
6. **Worldgen / chunk status** (~8): `net.minecraft.world.level.chunk.status.*` is 1.20.5+; 1.20.1 uses `ChunkStatus`
   directly, and `ChunkMap.getVisibleChunkIfPresent` needs an AT entry.
7. **Smaller renames** (~10): `BlockSource` (dispenser), `ItemCost`, `PathType` (done), `Holder<MobEffect>` ->
   `MobEffect`, `SynchedEntityData.Builder`, `getPartialTick().getGameTimeDeltaPartialTick()` -> `renderTickCounter`,
   `RegisterBrewingRecipesEvent` -> `PotionBrewEvent`/`BrewingRecipeRegistry`, `LevelData#getSpawnPos`, `Explosion#center`,
   `Entity#getTarget`/`accelerationPower`, `MapStorage`/`AdvancementList` overrides, `getVisibleChunkIfPresent` AT.

Once the compile is clean: package the loader as a JPMS module (above), wire `FMLModType`/manifest packaging for the
bundle jar, and run `runServerSubTest` with real legacy jars.

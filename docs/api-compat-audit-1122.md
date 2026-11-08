# 1.12.2 API compatibility audit (2026-11-03)

Scope: the API examples supplied during SRP compatibility testing. Synthesized methods must be checked against registered `Synth` callbacks as well as handwritten classes.

| API | Result |
| --- | --- |
| WorldGenDoublePlant.setPlantType | Already implemented by WorldSynth1122 and mcc$setPlantType; selects the plant scattered by the generator. |
| ForgeHooks.isLivingOnLadder | Added the 1.12 boolean signature; calls modern Forge's ladder hook, including its bounding-box setting and spectator handling. |
| EntityPlayerMP.setElytraFlying | Added; starts modern fall flying and synchronizes the entity flag. |
| EntityCreature.blockUsingShield | The legacy declaration belongs to EntityLivingBase and is inherited by EntityCreature. Added an invoker of the modern virtual method, preserving defender/attacker order and player shield disabling. |
| ItemMonsterPlacer.spawnCreature | Already implemented in SynthBlocks1122: entity lookup, position, spawn initialization, insertion and sound. |
| ModelShulkerBullet | Added its three boxes, texture offsets, angle conversion and rendering. |
| Particle factories | Added Synth callbacks for all 47 nested factories. 46 use modern particle providers; footprint uses a dedicated legacy particle. Creation does not submit the particle; ParticleManager.addEffect submits once. Color, alpha, lifetime, scale, position and removal APIs forward to the modern particle. Some effects use existing approximate modern equivalents (colored spell particles and snow shovel). |
| ParticleFootStep$Factory | Added the stationary ground quad, legacy UVs, light/color/alpha, partial-tick fade and 200-tick lifetime. Reuses the footprint texture already generated for 1.7.10. Both factory creation and numeric client world-particle spawning route to this implementation. |
| GuiDownloadTerrain | Added a visible translated loading screen with no pause or Escape dismissal. |
| BlockStructure constructor | Added material, hardness, resistance, MODE state, metadata conversion and tile creation. This does not complete the structure editor, redstone save/load or all TileEntityStructure methods. |
| ItemEnchantedBook.addEnchantment | Already implemented in SynthItems1122: merges StoredEnchantments and retains the higher level. |
| RenderList / VboRenderList | Added chunk queues, camera-relative transforms, layer VBO draws and display-list replay, upload and deletion. VertexBuffer already had a working shared decoder (the previous audit incorrectly listed it as missing). Added chunk factories, buffers, task cancellation and a synchronous dispatcher with deduplicated deferred rebuilds. Rebuilds mesh block models per layer and retain translucent vertex states for resorting. This is a calling-thread fallback, not the original worker pool. ViewFrustum/worker integration, visibility graph pruning, fluid meshing and tile-entity collection are not completed. |

Validation: compile and focused unit tests for actual VBO/display-list geometry capture, camera offsets, retained uploads, queue deduplication, cancellation, footprint geometry/fade/lifetime, factory coverage, model geometry/rotation, structure mode round trips and terrain-screen pause behavior. These do not substitute for in-game validation of terrain, particle providers, movement, combat or world generation. No new 1.7.10 compatibility is claimed by this change.

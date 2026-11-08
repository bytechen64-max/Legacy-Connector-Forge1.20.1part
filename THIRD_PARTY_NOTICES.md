# Third-party notices

Legacy Connector is released under the MIT License (`LICENSE`). Some data tables are taken from other MIT-licensed projects. Legacy content mod jars and
Minecraft assets are never included.

## Retromod

[Retromod](https://github.com/Bownlux/Retromod), MIT License, Copyright (c) 2026 Bownlux.

| Our file | Taken from | Changes |
|---|---|---|
| `loader/src/main/resources/legacyconnector/resource/vanilla-texture-renames.tsv` | `src/main/resources/retromod/flattening-texture-renames.tsv` | Every row re-checked against the 1.21.1 client jar; `quartz_block_lines` points at `quartz_pillar` (the source's later rename does not exist in 1.21.1); extra rows of our own appended |
| `LegacyResourceConverter.MODEL_RENAMES` (glazed terracotta, redstone dust, fire and wall torch parents) | `model-parent-renames.tsv` | Targets re-checked against the 1.21.1 client jar |
| `OreDictBridge.SPECIAL` (vanilla ore dictionary names such as `chest`, `fenceWood`, `dye`, `gravel`) | `forge-ore-dictionary.tsv` | Only names that map to a tag; every `c:` tag re-checked in NeoForge 21.1 and every `minecraft:` tag in vanilla 1.21.1 |
| `loader/src/main/resources/legacyconnector/resource/vanilla-texture-paths.tsv` (read by `TextureLocations`) | `LegacyTexturePathMappings.java` and `texture-migrations.tsv` | Only rows that apply up to 1.21.1; every row re-checked against the 1.21.1 client jar |

## Sinytra Connector

[Sinytra Connector](https://github.com/Sinytra/Connector), MIT License, Copyright (c) Sinytra.

| Our file | Taken from | Changes |
|---|---|---|
| `SideOnlyStripper` (removal of lambda bodies orphaned by side stripping) | `patch/EnvironmentStripperTransformer.java#getMethodLambdas` | Only the idea (collect `lambda$` handles of removed methods); the code is our own, with a fixed point over nested lambdas and a reachability check against the remaining methods |

## Forge port: embedded Java libraries

The player bundle includes nine unmodified Maven libraries. They retain their own licenses, not the project's MIT license. Exact coordinates, POM license declarations and corresponding source URLs are recorded in `META-INF/licenses/dependencies.json` (source tree: `licenses/dependencies.json`). Copyright/license notices are shipped in `META-INF/licenses/`.

- trove4j 3.0.3: GNU LGPL 2.1 or later; copyright Eric D. Friedman, Rob Eden, Jeff Randall and contributors.
- vecmath 1.5.2: GPL version 2 with the Classpath exception; copyright Sun Microsystems and contributors.
- Scala library/reflect 2.11.1 and Scala modules parser-combinators 1.0.1 / scala-xml 1.0.2: retain their original Scala/EPFL/contributor notices; see the pinned upstream license files.
- Typesafe Config 1.2.1 and Akka Actor 2.3.3: Apache License 2.0; retain their source notices.
- Jakarta Activation 1.2.2: its original LICENSE.md and NOTICE.md are preserved in the nested JAR and copied into the license directory.

Corresponding upstream source artifacts have been collected without modification in `legacyconnector-third-party-sources.zip`, prepared beside the player release. These are library sources, not legacy content mods. Their canonical Maven Central source URLs also remain in dependencies.json. Keep these source materials available with the distribution.

MixinExtras Forge 0.3.5 (io.github.llamalad7:mixinextras-forge:0.3.5), copyright LlamaLad7, is included unmodified through Forge Jar-in-Jar under the MIT License. Its license is preserved inside the nested JAR and in META-INF/licenses/MixinExtras-0.3.5-MIT.txt. Project: https://github.com/LlamaLad7/MixinExtras .

Pehkui is not embedded; users obtain its appropriate Forge version separately. It retains its own copyright and license.

# Legacy Connector — Forge Port

An unofficial, experimental Forge 1.20.1 port of [Legacy Connector](https://github.com/kylepitcock/Legacy-Connector), originally created by Kyle Pitcock. Maintained independently by Forge Port Contributors under the MIT License.

Use legacy Forge mods in a newer Minecraft instance through load-time translation and compatibility APIs. This port targets legacy 1.7.10 and 1.12.2 mods. Support varies by mod and feature; it is not a universal compatibility guarantee.

## Installation

1. Set up Minecraft **1.20.1**, **Forge 47.4.20 or newer in the 47.x family**, and **Java 17**. The port is built against Forge 47.4.28.
2. MixinExtras Forge 0.3.5 is embedded through Jar-in-Jar. No separate MixinExtras download is needed.
3. Put the single `legacyconnector-forge-1.20.1-…-jarinjar.jar` release file in `mods/`.
4. Put original legacy mods and their required legacy dependencies in `mods/1.7.10/` or `mods/1.12.2/`. Do not install the old Forge loader itself. These subfolders also avoid early discovery conflicts with legacy jars that ship launcher services or Mixin.
5. Launch. The loader translates legacy jars into its cache. Some originals may be relocated into `mods/.legacyconnector/originals/`; their bytes are preserved.

Back up worlds before testing a new mod combination. For content mods, install matching mod sets on the client and dedicated server; client-only mods belong only on the client.

## Status and differences from upstream

This is an **alpha port** for Forge 1.20.1. It uses Forge discovery, Java 17, SRG mappings and the 1.20.1 rendering/runtime APIs. It is not the upstream NeoForge 1.21.1 build.

Recent testing has focused on Scape and Run: Parasites 1.10.9, including entity interpolation, multipart entities, block occlusion, legacy APIs and meteor structures at negative heights. This does not establish complete SRP support. Broader compatibility results, screenshots and mod counts from the upstream NeoForge version must not be treated as port test results.

JEI, Jade, Curios and TerraBlender integrations are optional. Pehkui's Forge build is needed for legacy features that resize non-hosted vanilla entities through its scaling API; it is not bundled. Install optional integrations only when needed and use versions for Forge 1.20.1.

## Configuration and reports

Settings: `config/legacyconnector.properties`. Detection report: `logs/legacyconnector-report.txt`.

To prevent a declared mod ID from being handled as legacy, set `loader.excludeModIds=connector,examplemod` and restart. If an older version already moved a modern jar into the originals directory, move that original back to `mods/` after closing the game.

When reporting an issue, include the port version, Forge version, original legacy mod version, relevant logs and reproduction steps. Send port-specific issues to this port's own issue tracker once it is configured.

## Credits

Original project and author: [Kyle Pitcock / Legacy Connector](https://github.com/kylepitcock/Legacy-Connector). Unofficial port: Forge Port Contributors. Original copyright and MIT permission notices are retained. Legacy mods are supplied separately by users and are not redistributed here. No endorsement by the upstream project, Forge, NeoForge, Mojang or Microsoft is implied.

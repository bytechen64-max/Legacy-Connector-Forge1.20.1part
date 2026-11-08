# Legacy Connector (Forge 1.20.1 Port)

An **unofficial Alpha port** of [Legacy Connector by Kyle Pitcock](https://github.com/kylepitcock/Legacy-Connector), maintained by **Forge Port Contributors** under the [MIT License](LICENSE).

This branch runs on **Minecraft 1.20.1 / Forge / Java 17** and targets legacy Forge **1.7.10 and 1.12.2** mods through load-time translation. Compatibility depends on the mod and feature. Upstream NeoForge 1.21.1 compatibility results and screenshots do not certify this port.

## Install

1. Install Minecraft 1.20.1, Forge 47.4.20 or newer in the 47.x family, and Java 17. The build uses Forge 47.4.28.
2. MixinExtras Forge 0.3.5 is embedded through Jar-in-Jar; no separate dependency download is required.
3. Put the single `legacyconnector-forge-1.20.1-…-jarinjar.jar` from `build/dist/` or this port's eventual release page into `mods/`.
4. Put original legacy mods and their required legacy dependencies into `mods/1.7.10/` or `mods/1.12.2/`. Do not install an old Forge loader. These subfolders avoid early discovery conflicts with old jars containing Mixin or launcher services.
5. Launch and allow translation. Original jar bytes are preserved; some originals are relocated into `mods/.legacyconnector/originals/`.

Back up worlds before testing a new combination. Content mods generally require matching client and server installations. Do not install the upstream NeoForge jar alongside this port.

JEI, Jade, Curios and TerraBlender integrations are optional. Pehkui is not embedded; its Forge build is needed for legacy features using the non-hosted vanilla-entity scaling bridge.

## Configuration and reports

Configuration: `config/legacyconnector.properties`. Loader report: `logs/legacyconnector-report.txt`.

`loader.excludeModIds=connector,examplemod` prevents jars declaring these IDs from being treated as legacy. Restart after changes. If a modern jar was already moved to the originals folder by an older release, close the game and restore that original to `mods/`.

## Build and publication

```sh
./gradlew bundleJar
python tools/release/audit_forge_bundle.py build/dist/legacyconnector-forge-1.20.1-0.3.13-forge.1-alpha.1-jarinjar.jar
```

The default player release is the **`-jarinjar.jar` file in `build/dist/`**, with MixinExtras embedded. Build `./gradlew bundleJar -PwithoutBundledMods` for a `-nojarinjar.jar` variant that requires MixinExtras Forge 0.3.5 or newer installed separately. Install only one variant. Files named `runtime-only`, the loader project's jar, and the addon API jar are not additional player mods.

Publication guide: [docs/release/PUBLISHING.md](docs/release/PUBLISHING.md).
Player descriptions: [English](docs/release/description-en.md), [中文](docs/release/description-zh.md).
Port identity and credits: [PORT_NOTICE.md](PORT_NOTICE.md).
Third-party libraries and attribution: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), [licenses/](licenses/).

The inherited upstream publishing and description-sync workflows are disabled by default. The Forge candidate workflow only builds downloadable workflow artifacts. Configure a separate port repository and feedback channel before public submission.

## Validation scope

Recent work has focused on SRP 1.10.9: entity interpolation, multipart entities, block occlusion, API behavior, negative-height meteor structures and modern-mod detection. This is partial compatibility work, not a claim that all SRP features or all legacy mods work.

The detailed technical wiki contains inherited upstream reference material; evaluate it against this branch's source and test results before using it as a Forge compatibility claim.

## License

Original project copyright: Kyle Pitcock. Original copyright and full MIT permission text are retained in LICENSE. This port is independently maintained and does not imply upstream endorsement. Bundled third-party libraries retain their own licenses. Legacy mod jars, worlds and translation caches are not distributed by this project.

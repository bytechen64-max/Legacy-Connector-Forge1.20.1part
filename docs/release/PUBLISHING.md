# Forge 1.20.1 发布准备

本文件为本移植版的发布操作稿。核对日期：2026-11-07。当前候选版：`0.3.13-forge.1-alpha.1`。当前任务没有向任何平台发布文件或发送消息。

## 名称、身份与版本

- 游戏内名称：**Legacy Connector (Forge 1.20.1 Port)**，维护者署名 **Forge Port Contributors**，保留 Kyle Pitcock 的原作者署名。
- 平台项目名称建议 **Legacy Connector - Forge Port**。CurseForge 的名称规范要求把游戏版本等技术信息放到版本标签/介绍中，因此平台标题使用这个较短版本；游戏内名称仍按已选方案保留。
- 建议 slug：`legacyconnector-forge-port`，实际能否注册取决于平台。
- Mod ID 保持 `legacyconnector`。改展示名不需要改包名、注册表 ID 或存档标识。
- 本移植版与上游 jar 不要同时安装。它们提供同一个 mod ID。
- 发布类型选 **Alpha**，游戏版本只选 **1.20.1**，加载器只选 **Forge**。不要沿用原工作流的 NeoForge / 1.21.1 / Java 21 标签。
- 一句话简介 EN：`An unofficial Forge port bringing experimental legacy 1.7.10 and 1.12.2 mod compatibility to Minecraft 1.20.1.`
- 一句话简介 ZH：`面向 Forge 1.20.1 的非官方移植版，通过加载时转换尝试兼容 1.7.10 与 1.12.2 旧模组。`

## 和上游怎么用的区别

核心流程相同：安装兼容层，提供旧模组原 jar，启动时转换。推荐把旧 jar 放到 `mods/1.7.10/` 或 `mods/1.12.2/`，不安装旧 Forge。顶层 `mods/` 也会扫描，但携带 Mixin/启动服务的旧包应使用子目录。

区别：目标为 Forge 1.20.1 / Java 17；本候选版已通过 Forge Jar-in-Jar 内置 **MixinExtras Forge 0.3.5**，无需单独安装。上游使用的 NeoForge 已内置相关能力，不能据此假定 Forge 环境也已具备。只核对了 0.3.5 的 Forge 文件，不承诺任意更新版本都有相同的 mod ID 和加载方式。不要把 `mixinextras-common` 开发依赖发给玩家。

可选现代整合需换成 Forge 1.20.1 对应版本。Pehkui 没有被当前构建打包；它的缩放桥接代码仍有直接引用，因此使用相关旧模组功能时需要 Forge 版 Pehkui，不能照搬上游“已内置”的构建注释。

完整玩家文案见 [English](description-en.md) 和 [中文](description-zh.md)。国际平台先放英文，再放中文。不要直接复制原版兼容成功数量、1.21.1 游戏截图或声称全部旧模组都能运行。

文件名后缀：`-jarinjar.jar` 内置 MixinExtras（默认玩家版）；`-nojarinjar.jar` 不内置，需要另装 MixinExtras Forge 0.3.5 或更高兼容版本。后者使用 `./gradlew bundleJar -PwithoutBundledMods` 构建。同一实例只能安装一个版本。

## 上传哪些文件

执行 `./gradlew bundleJar`，然后执行：

```sh
python tools/release/audit_forge_bundle.py build/dist/legacyconnector-forge-1.20.1-0.3.13-forge.1-alpha.1-jarinjar.jar
python tools/release/prepare_third_party_sources.py
```

| 文件 | 处理方式 |
| --- | --- |
| `build/dist/legacyconnector-forge-1.20.1-0.3.13-forge.1-alpha.1-jarinjar.jar` | 唯一玩家主文件，上传为 Alpha |
| 同名 `.jar.sha256` | 校验文件，可放 GitHub Release；不是另一个模组 |
| 同名 `-sources.zip` | 当前工作区的移植源码快照，可提供给审核者和源码下载；正式发布建议同时提供自己的公开源码仓库 |
| `build/dist/legacyconnector-third-party-sources.zip` | 本地已准备的内置依赖对应 Maven 源码包，保留并随可提供附加资料的平台分发；不是装进 mods 的文件 |
| `*-runtime-only.jar`、`legacyconnector-loader-*.jar` | 构建内部产物，不上传为玩家文件 |
| `legacyconnector-api-*.jar` | 仅附属模组开发者使用，不作为玩家前置；当前发布无需上传 |
| 历次 `srp.*` / `.12`…`.17` 测试 jar | 保留本地排障，首次公开发布只使用这一份新候选版 |
| 旧模组 jar、转换缓存、存档、配置、日志、令牌 | 不随模组发布 |

MixinExtras Forge 0.3.5 随主文件以 Jar-in-Jar 分发，并保留 MIT 许可；Pehkui 等可选前置由各自作者的项目分发，按平台支持的内置/可选关系登记 Dependencies。不要把从别处下载的前置作为本项目的独立模组文件上传。

## 许可证和上游关系

项目源码沿用 MIT，保留 `LICENSE` 中 `Copyright (c) 2026 Kyle Pitcock` 和完整许可文本。`PORT_NOTICE.md` 标明原作者、上游链接、非官方移植身份和修改范围。二进制包中也带上这些文件和 `THIRD_PARTY_NOTICES.md`。

内置的九个未修改 Java 库各有自己的许可，并非全部 MIT；对应坐标、POM 声明和源码 URL 见 `licenses/dependencies.json`，许可文本和署名见 `licenses/`，对应源码归档已放在上面的 third-party-sources.zip 中。新增封面不使用上游 logo 或原游戏截图。维护自己的公开源码仓库及反馈地址；当前 git remote 仍指向上游，发布页不要把它误填为移植版自己的仓库/问题追踪器。

## 封面与平台限制

`assets/cover-ai-forge-port.png` 是使用内置 image_gen 生成并人工检查文字的原创概念封面，不是游戏实拍。提示词见 `assets/cover-prompt.txt`。

- CurseForge：项目头像要求 **400×400**。使用本目录的 `cover-ai-forge-port-400.png`；在页面附注“AI-generated conceptual cover; not an in-game screenshot.”。不使用封面当作运行效果的证据，游戏画廊另放真实 1.20.1 截图。
- Modrinth：当前规则 **禁止把 AI 生成图片用于项目图标、画廊或介绍**；这张封面及其缩放版本不能上传。需要另准备人工制作、非 AI 衍生的封面或真实游戏截图。代码/介绍中的 AI 使用也需按规则填写披露，若项目主要由 AI 输出组成则可能不符合其公开发布条件，需按实际贡献核对；此准备包不宣称平台一定审核通过。

这里仅生成本地发布资料。继承的 publish / sync-description 工作流仍带原项目 ID，已加默认关闭及上游仓库限制。新增 `forge-release-candidate.yml` 只构建和上传工作流附件，不向模组网站发布。迁移到自己的仓库后再填自己的项目 ID 和令牌；不要使用原项目 ID `CCxw8Nzy` / `1763521`。

## 首次公开发布前的具体收尾

1. 提供自己可公开访问的移植源码仓库、问题反馈地址及发行页，替换玩家文案里的“本移植版自己的反馈渠道”。
2. 用干净实例只安装主 jar（内置 MixinExtras Forge），分别做客户端和专用服务端启动验证。构建审核通过不等于客户端视觉测试通过。
3. 附近期实际验证过的 1.20.1 截图、测试模组的准确版本及仍存在的问题；Alpha 状态保持可见。
4. 核对平台要求后手动提交；初次提交只发一份主 jar，必要源码资料作为非玩家附件或公开源码下载提供。

本次验证：主 jar 已通过 `audit_forge_bundle.py` 的嵌套结构、平台元数据、许可、依赖声明及 SHA-256 检查。隔离开发服务端在 mods 目录无外置前置的情况下，经 JarInJar 发现 MixinExtras Forge 及其内部库，启动世界并输出 `FORGE RELEASE SMOKE PASS` 后正常退出，日志为 `build/jarinjar-smoke.log`。这是开发环境服务端启动验证；尚未执行发布 jar 的生产环境客户端视觉回归。

## 核对来源

- 上游及 MIT：https://github.com/kylepitcock/Legacy-Connector 、https://github.com/kylepitcock/Legacy-Connector/blob/master/LICENSE
- 上游第三方署名：https://github.com/kylepitcock/Legacy-Connector/blob/master/THIRD_PARTY_NOTICES.md
- MixinExtras 官方 Forge/NeoForge 安装说明：https://github.com/LlamaLad7/MixinExtras/blob/master/README.MD
- CurseForge 发布规范（包含 fork 署名、标题、头像与 AI 图片说明）：https://support.curseforge.com/support/solutions/articles/9000197279
- Modrinth 内容规范（包含 fork、依赖、AI 披露与图片限制）：https://modrinth.com/legal/rules

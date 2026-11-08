# Legacy Connector — Forge 移植版

这是 [Kyle Pitcock 的 Legacy Connector](https://github.com/kylepitcock/Legacy-Connector) 的非官方 Forge 1.20.1 移植版，由 Forge Port Contributors 独立维护，项目代码沿用 MIT 协议。

通过加载时转换和兼容 API，尝试让旧版 Forge 模组在 Minecraft 1.20.1 中运行。目前面向 1.7.10 与 1.12.2 旧模组，实际兼容程度取决于具体模组和功能。

## 安装方法

1. 安装 Minecraft **1.20.1**、Forge **47.4.20 或更高的 47.x 版本**和 **Java 17**；本移植版使用 Forge 47.4.28 构建。
2. 主 jar 已通过 Jar-in-Jar 内置 **MixinExtras 0.3.5 Forge 版**，无需单独下载前置。
3. 将唯一的 `legacyconnector-forge-1.20.1-…-jarinjar.jar` 主发布文件放入 `mods/`。
4. 将旧模组原始 jar 及其所需的旧版前置放入 `mods/1.7.10/` 或 `mods/1.12.2/`。无需安装旧版 Forge 加载器。携带 Mixin 或启动服务的旧 jar 应放在这些子目录中。
5. 启动游戏，等待转换。转换缓存由兼容层管理；部分原 jar 会移至 `mods/.legacyconnector/originals/`，文件内容不变。

测试新组合前请备份存档。含游戏内容的模组通常需要客户端与服务端安装匹配的组合；纯客户端模组只安装在客户端。

## 当前状态

这是面向 Forge 1.20.1 的 **Alpha 移植版**，使用 Java 17，与上游 NeoForge 1.21.1 版本分开测试。

近期验证主要集中在 SRP 1.10.9，包括实体插值、多部件实体、方块遮蔽、旧 API 和负高度陨石结构等。仍有功能缺失，不能据此认定 SRP 全部兼容。原项目的兼容列表、成功数量和 1.21.1 截图不代表本移植版的结果。

JEI、Jade、Curios、TerraBlender 为可选整合。使用经 Pehkui API 缩放原版实体的旧模组功能时，需要另装 Pehkui 的 Forge 版；当前主 jar 未内置。所有现代前置都应选择 Forge 1.20.1 对应文件。

## 配置与反馈

配置位于 `config/legacyconnector.properties`，检测报告位于 `logs/legacyconnector-report.txt`。

排除旧模组识别可配置 `loader.excludeModIds=connector,examplemod`，修改后重启。若旧版已把现代模组移到 originals 目录，请退出游戏后将原 jar 放回 `mods/`。

反馈时请提供本移植版版本、Forge 版本、旧模组原始版本、相关日志与复现步骤。移植版问题请提交至本移植版自己的反馈渠道，待项目页配置后使用。

原作者为 Kyle Pitcock，原项目链接见页首；非官方移植维护者为 Forge Port Contributors。保留原作者版权和 MIT 许可文本。旧模组由玩家自行取得，本项目不附带这些模组，也不代表上游或相关加载器官方背书。

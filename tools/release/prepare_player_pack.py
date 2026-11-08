"""Assemble the audited Forge alpha with its embedded required dependency for players."""
from pathlib import Path
import hashlib
import html
import io
import json
import shutil
import tomllib
import zipfile

ROOT = Path(__file__).resolve().parents[2]
VERSION = '0.3.13-forge.1-alpha.1'
MAIN = f'legacyconnector-forge-1.20.1-{VERSION}-jarinjar.jar'
NAME = f'LegacyConnector-Forge-1.20.1-{VERSION}-jarinjar-PlayerPack'
OUT = ROOT / 'build/player-downloads'
STAGE = OUT / NAME
STAGE.mkdir(parents=True, exist_ok=True)
(STAGE / 'mods/mixinextras-forge-0.3.5.jar').unlink(missing_ok=True)
files = {}


def add(name, data):
    assert name not in files, name
    files[name] = data


def text(name, body):
    add(name, body.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf-8-sig'))


add('mods/' + MAIN, (ROOT / 'build/dist' / MAIN).read_bytes())
text('mods/1.12.2/旧模组放这里.txt', '将自行下载的 Forge 1.12.2 旧模组原始 jar 和所需旧版前置放在这里。\n本包不包含 SRP 原文件；下载地址见安装教程。\n')
text('mods/1.7.10/旧模组放这里.txt', '将自行下载的 Forge 1.7.10 旧模组原始 jar 和所需旧版前置放在这里。\n无需安装旧版 Forge 加载器。\n')

intro = f'''Legacy Connector (Forge 1.20.1 Port) 玩家安装包
版本：{VERSION} / Alpha

先阅读“安装教程.html”（双击可离线打开），或“安装教程.txt”。

快速安装：
1. 新建 Minecraft 1.20.1 + Forge 实例，使用 Java 17。
   建议 Forge 47.4.28；最低要求为 47.4.20。
2. 解压本压缩包，将包内 mods 文件夹的内容合并到该实例的 mods 文件夹。
   顶层只需 Legacy Connector 主 jar，MixinExtras Forge 0.3.5 已内置。
3. 自行下载的 SRP 1.12.2 原始 jar 放进该实例的 mods/1.12.2/。
   其他旧模组及其旧版前置放进对应版本子目录。
4. 启动游戏等待转换，先用新建测试世界体验。

这是非官方 Forge 移植版，与原版 NeoForge 1.21.1 文件分开安装。
当前为实验性 Alpha，不代表所有旧模组和全部 SRP 功能已兼容。
测试前备份存档；升级时移走旧的 Legacy Connector jar，只保留一份。

包内包含：主模组（已内置必需 MixinExtras 前置）、离线教程、目录示例、许可、源码资料和校验文件。
“许可与源码”仅供阅读，不要复制到 mods 中。
本包没有 SRP、Minecraft 游戏本体、Java 或 Forge 安装器。
'''
text('先读我.txt', intro)

sections = [
('一、准备游戏环境', '''在启动器中新建独立的 Minecraft 1.20.1 实例，安装 Forge 47.4.28，选择 Java 17。
最低 Forge 版本为 47.4.20；本候选版使用 47.4.28 构建。
不要选 Fabric、NeoForge 或其他游戏版本。安装 Forge 后先启动一次游戏，再退出。
如果启动器开启了版本隔离，要打开这个实例自己的游戏目录；以启动器的“打开游戏目录”按钮为准。'''),
('二、安装包内主模组', f'''先将整个下载压缩包解压到普通文件夹。
打开解压后的 mods 文件夹，将其中内容合并到该实例的 mods 文件夹。
顶层安装文件只有这一个：
  {MAIN}

保留 1.12.2 和 1.7.10 子文件夹，后续放旧模组使用。
这些 jar 不用解压，也不用双击运行。不要把下载包 ZIP 或整个外层文件夹当作模组放入 mods。
MixinExtras Forge 0.3.5 已通过 Jar-in-Jar 内置在主 jar 中，无需单独安装。已有实例若装了其他版本，建议先在全新实例中按本包组合测试。
升级时移走旧版 Legacy Connector jar。不要同时装上游 NeoForge 版本或多个旧测试版。'''),
('三、加入寄生虫或其他旧模组', '''本包不附带寄生虫原文件，请从 SRP 作者页面下载 Minecraft 1.12.2 对应原始 jar。
近期测试主要使用 SRP 1.10.9；其他版本的结果需分别验证。
将 SRP jar 放进游戏目录的 mods/1.12.2/，不要直接放在顶层 mods 中。
其他 Forge 1.12.2 旧模组及其需要的旧版前置也放在这个子目录。
Forge 1.7.10 旧模组和旧版前置则放在 mods/1.7.10/。
无需安装 1.12.2 或 1.7.10 的 Forge 加载器，也不需要自己修改旧模组 jar。
携带旧版 Mixin 或启动服务的模组尤其应使用版本子目录。
现代 Forge 1.20.1 模组及其现代前置放在顶层 mods/；不要把同一个模组重复放到多个目录。'''),
('四、检查目录', f'''你的实例游戏目录/
  mods/
    {MAIN}
    1.12.2/
      [自行下载的 SRP 原始 jar]
      [需要时添加的旧版前置 jar]
    1.7.10/
      [自行下载的 1.7.10 旧模组 jar]

方括号是说明，不是实际文件名。用不到的旧版本目录可以留空。'''),
('五、启动与验证', '''启动对应 Forge 1.20.1 实例，等待首次转换完成，期间不要反复强制结束游戏。
在模组列表中确认 Legacy Connector (Forge 1.20.1 Port) 和 MixinExtras 已加载。
先新建创造模式测试世界，检查所加旧模组的物品、方块、实体和实际交互。
详细检测结果可查看 logs/legacyconnector-report.txt；游戏日志为 logs/latest.log。
兼容层会管理转换缓存，部分旧原始 jar 可能移到 mods/.legacyconnector/originals/，原文件内容保持不变。
注册了物品或成功进入世界，不代表该模组所有功能都已经正常。
内容模组用于联机时，客户端和服务端一般都需要安装匹配的主模组、必需前置与旧模组组合；纯客户端模组按其说明安装。'''),
('六、可选整合与已知范围', '''本包仅包含核心兼容层（主 jar 已内置必需 MixinExtras）。JEI、Jade、Curios、TerraBlender 等整合按需另装 Forge 1.20.1 对应文件，不是这份核心包的必装项。
使用依赖 Pehkui API 的旧实体缩放功能时，需要另装 Forge 1.20.1 版 Pehkui；本包未内置。
目前为 Alpha，测试重点是 SRP，其他旧模组及每项功能需要独立验证。
上游 NeoForge 1.21.1 的兼容名单、成功数量和截图，不代表此移植版的测试结果。'''),
('七、常见问题', '''提示缺少 mixinextras：确认使用本次完整主 jar，未误用 runtime-only 或 loader 构建产物；MixinExtras 已内置，不需要单独安装。
提示重复 mod ID：退出游戏，移走旧的 Legacy Connector 或重复前置，只保留一份对应版本。
提示 org.spongepowered / Mixin 包重复：检查旧 jar 是否误放在 mods 顶层，将它移到 mods/1.12.2/ 或 mods/1.7.10/；现代前置仍留在顶层。
旧模组没出现：核对旧模组版本、目录和所需前置，再查看 logs/legacyconnector-report.txt。
现代模组被识别成旧版：可在 config/legacyconnector.properties 设置 loader.excludeModIds=模组ID1,模组ID2，保存后重启。填写实际 mod ID，不是显示名。如已存在此项，请合并 ID，不要重复写键。若之前已被移入 originals，退出游戏后将对应原始 jar 放回顶层 mods。
卡住、崩溃或功能异常：先用干净实例与最少模组复现，反馈时提供兼容层版本、Forge 版本、旧模组准确版本、复现步骤、检测报告与相关日志。不要只提供“无法启动”一句话。
更改兼容层、旧模组组合或移除内容模组前，先备份世界。'''),
('八、下载与项目链接', '''Forge 1.20.1 官方下载：
https://files.minecraftforge.net/net/minecraftforge/forge/index_1.20.1.html
SRP 作者下载页（选择 1.12.2 文件）：
https://www.curseforge.com/minecraft/mc-mods/scape-and-run-parasites
原版 Legacy Connector 项目（NeoForge 1.21.1，勿与本移植版混装）：
https://www.curseforge.com/minecraft/mc-mods/legacy-connector
https://modrinth.com/mod/legacyconnector
原项目源码与文档：
https://github.com/kylepitcock/Legacy-Connector
MixinExtras 项目：
https://github.com/LlamaLad7/MixinExtras
包内 MixinExtras 0.3.5 Forge 原始分发地址：
https://repo.maven.apache.org/maven2/io/github/llamalad7/mixinextras-forge/0.3.5/mixinextras-forge-0.3.5.jar
Pehkui（需要时选择 Forge / 1.20.1）：
https://modrinth.com/mod/pehkui

移植版更新请查看提供本压缩包的 UP 主视频简介或置顶评论；本包未预填尚未确认的发行网址。'''),
('九、署名与包内校验', '''原项目 Legacy Connector：Kyle Pitcock，MIT 协议。
非官方 Forge 移植维护：Forge Port Contributors。
MixinExtras：LlamaLad7，MIT 协议，包内为未修改的 0.3.5 Forge 文件。
旧模组由各自作者维护，玩家自行下载；本包不代表上游或加载器官方背书。
许可与源码目录保留完整许可证、内置依赖对应源码，以及本候选版源码快照；这些不是安装文件。
SHA256SUMS.txt 列出每个文件的 SHA-256，可用于核对下载内容。
主 jar 已通过平台元数据、嵌套依赖和署名检查，MixinExtras 已与官方 Maven SHA-1 核对。
本次已验证无外置前置的隔离开发服务端通过 Jar-in-Jar 加载 MixinExtras，并启动世界后正常退出；未执行生产客户端完整功能回归。
'''),
]
guide = intro + '\n\n' + '\n\n'.join(title + '\n' + body for title, body in sections)
text('安装教程.txt', guide)
cards = []
for title, body in sections:
    lines = []
    for line in body.splitlines():
        value = html.escape(line)
        if line.startswith('https://'):
            value = f'<a href="{html.escape(line, quote=True)}">{value}</a>'
        lines.append(value)
    cards.append('<section><h2>' + html.escape(title) + '</h2><div class="body">' + '\n'.join(lines) + '</div></section>')
page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Legacy Connector Forge 玩家安装教程</title>
<style>body{margin:0;background:#edf1f4;color:#182732;font:16px/1.8 "Microsoft YaHei",sans-serif}main{max-width:920px;margin:40px auto;padding:0 20px 40px}header,section{background:white;border-radius:14px;padding:24px 32px;margin:18px 0;box-shadow:0 3px 18px #18273209}header{border-top:5px solid #197b63}h1{font-size:28px;line-height:1.4}h2{font-size:20px;color:#17654f;margin-top:0}.body{white-space:pre-wrap;overflow-wrap:anywhere}a{color:#086aae}small{color:#50616c}@media(max-width:600px){header,section{padding:20px}h1{font-size:23px}}</style><main>
<header><small>FORGE 1.20.1 · JAVA 17 · ALPHA</small><h1>Legacy Connector<br>Forge 移植版安装教程</h1><p>先安装包内主模组，再把旧模组放入版本子目录。</p><small>''' + html.escape(VERSION) + '</small></header>' + ''.join(cards) + '</main></html>'
add('安装教程.html', page.encode('utf-8'))

for name in ['LICENSE', 'PORT_NOTICE.md', 'THIRD_PARTY_NOTICES.md']:
    add('许可与源码/' + name, (ROOT / name).read_bytes())
for p in sorted((ROOT / 'licenses').iterdir()):
    if p.is_file():
        add('许可与源码/内置依赖许可/' + p.name, p.read_bytes())
for name in [f'legacyconnector-forge-1.20.1-{VERSION}-sources.zip', 'legacyconnector-third-party-sources.zip']:
    data = (ROOT / 'build/dist' / name).read_bytes()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        assert z.testzip() is None, name
        assert not any(n.split('/')[-1].lower() in {'.env', 'credentials', 'id_rsa', 'id_ed25519'} for n in z.namelist())
    add('许可与源码/' + name, data)

manifest = {'package': NAME, 'version': VERSION, 'minecraft': '1.20.1', 'loader': 'Forge', 'java': 17, 'recommended_forge': '47.4.28', 'minimum_forge': '47.4.20', 'required_mods': [MAIN], 'embedded_mods': ['mixinextras-forge-0.3.5.jar'], 'includes_legacy_mods': False, 'release_type': 'Alpha'}
add('package-info.json', json.dumps(manifest, ensure_ascii=False, indent=2).encode('utf-8'))
checks = ''.join(hashlib.sha256(data).hexdigest() + '  ' + name + '\n' for name, data in sorted(files.items()))
add('SHA256SUMS.txt', checks.encode('utf-8'))
OUT.mkdir(parents=True, exist_ok=True)
archive = OUT / (NAME + '.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for name, data in sorted(files.items()):
        dest = STAGE / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        z.writestr(NAME + '/' + name, data)

# Validate the shipped ZIP, including the exact bytes of the single installable jar.
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert len(z.namelist()) == len(files)
    for name, expected in files.items():
        assert z.read(NAME + '/' + name) == expected, name
    installable = [n for n in z.namelist() if n.endswith('.jar')]
    assert len(installable) == 1, installable
    with zipfile.ZipFile(io.BytesIO(z.read(NAME + '/mods/' + MAIN))) as main:
        with zipfile.ZipFile(io.BytesIO(main.read('META-INF/legacyconnector/legacyconnector-runtime.jar'))) as runtime:
            metadata = tomllib.loads(runtime.read('META-INF/mods.toml').decode())
            assert metadata['mods'][0]['version'] == VERSION

digest = hashlib.sha256(archive.read_bytes()).hexdigest()
archive.with_suffix('.zip.sha256').write_text(digest + '  ' + archive.name + '\n', encoding='utf-8')
delivery = Path(r'C:\Users\chy20\Desktop\desktop\视频剪辑\高版本寄生虫\发布下载')
delivery.mkdir(parents=True, exist_ok=True)
for p in [archive, archive.with_suffix('.zip.sha256')]:
    shutil.copy2(p, delivery / p.name)
assert hashlib.sha256((delivery / archive.name).read_bytes()).hexdigest() == digest
print('PLAYER PACK VERIFIED:', len(files), 'files;', archive.stat().st_size, 'bytes')
print('SHA256:', digest)
print('DELIVERY:', delivery / archive.name)

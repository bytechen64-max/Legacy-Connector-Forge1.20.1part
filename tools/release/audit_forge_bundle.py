"""Check the player-facing Forge bundle, not a runtime-only or loader-only jar."""
import hashlib
import io
import json
from pathlib import Path
import sys
import tomllib
import zipfile


def audit(path):
    assert path.name.endswith(('-jarinjar.jar', '-nojarinjar.jar')), 'Use an explicit Jar-in-Jar filename suffix'
    embedded = path.name.endswith('-jarinjar.jar')
    with zipfile.ZipFile(path) as outer:
        required = {
            'LICENSE', 'PORT_NOTICE.md', 'THIRD_PARTY_NOTICES.md',
            'META-INF/services/net.minecraftforge.forgespi.locating.IModLocator',
            'META-INF/legacyconnector/legacyconnector-runtime.jar',
            'META-INF/licenses/Retromod-MIT.txt',
            'META-INF/licenses/dependencies.json',
        }
        assert required <= set(outer.namelist()), required - set(outer.namelist())
        assert b'Copyright (c) 2026 Kyle Pitcock' in outer.read('LICENSE')
        libraries = [n for n in outer.namelist() if n.startswith('META-INF/legacyconnector/libs/') and n.endswith('.jar')]
        assert len(libraries) == 9, libraries
        with zipfile.ZipFile(io.BytesIO(outer.read('META-INF/legacyconnector/legacyconnector-runtime.jar'))) as runtime:
            metadata = tomllib.loads(runtime.read('META-INF/mods.toml').decode())
            mod = metadata['mods'][0]
            assert mod['modId'] == 'legacyconnector'
            assert mod['displayName'] == 'Legacy Connector (Forge 1.20.1 Port)'
            assert 'Forge Port Contributors' in mod['authors']
            assert metadata['license'] == 'MIT'
            deps = {d['modId']: d for d in metadata['dependencies']['legacyconnector']}
            assert deps['minecraft']['versionRange'] == '[1.20.1]'
            assert deps['mixinextras']['mandatory'] is True
            if embedded:
                jij = json.loads(runtime.read('META-INF/jarjar/metadata.json'))['jars']
                assert len(jij) == 1, jij
                dependency = jij[0]
                assert dependency['identifier'] == {'group': 'io.github.llamalad7', 'artifact': 'mixinextras-forge'}
                assert dependency['version']['artifactVersion'] == '0.3.5'
                assert dependency['version']['range'] == deps['mixinextras']['versionRange']
                with zipfile.ZipFile(io.BytesIO(runtime.read(dependency['path']))) as nested:
                    nested_metadata = tomllib.loads(nested.read('META-INF/mods.toml').decode())
                    assert any(m['modId'] == 'mixinextras' for m in nested_metadata['mods'])
                    common_metadata = json.loads(nested.read('META-INF/jarjar/metadata.json'))['jars']
                    assert len(common_metadata) == 1
                    with zipfile.ZipFile(io.BytesIO(nested.read(common_metadata[0]['path']))) as common:
                        assert 'com/llamalad7/mixinextras/MixinExtrasBootstrap.class' in common.namelist()
                    assert any('LICENSE' in n.upper() for n in nested.namelist())
            else:
                assert not any(n.startswith('META-INF/jarjar/') for n in runtime.namelist())
            for name in ['META-INF/accesstransformer.cfg', 'legacyconnector.refmap.json', 'LICENSE', 'PORT_NOTICE.md']:
                assert name in runtime.namelist(), name
            assert not any(n.startswith('com/dhanantry/scapeandrunparasites/') for n in runtime.namelist())
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    path.with_suffix(path.suffix + '.sha256').write_text(f'{digest}  {path.name}\n', encoding='utf8')
    dependency_mode = 'JiJ MixinExtras Forge' if embedded else 'external MixinExtras Forge required'
    print(f'PASS {path.name}: Forge 1.20.1, loader + runtime + 9 libraries, {dependency_mode}, attribution')
    print(f'SHA256 {digest}')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Pass exactly one bundled player JAR.')
    audit(Path(sys.argv[1]))

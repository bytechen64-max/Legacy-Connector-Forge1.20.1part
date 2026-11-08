"""Collect corresponding, unmodified Maven source artifacts for the embedded libraries."""
import hashlib
import json
from pathlib import Path
import urllib.request
import zipfile

root = Path(__file__).resolve().parents[2]
dependencies = json.loads((root / 'licenses/dependencies.json').read_text(encoding='utf8'))
output = root / 'build/dist/legacyconnector-third-party-sources.zip'
output.parent.mkdir(parents=True, exist_ok=True)
cache = root / 'build/release-dependencies'
cache.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
    for dependency in dependencies:
        url = dependency['source']
        if not url.startswith('https://repo.maven.apache.org/maven2/'):
            raise ValueError(f'Unexpected source repository: {url}')
        name = url.rsplit('/', 1)[1]
        local = cache / name
        if not local.is_file():
            with urllib.request.urlopen(url, timeout=60) as stream:
                local.write_bytes(stream.read())
        dependency['source_sha256'] = hashlib.sha256(local.read_bytes()).hexdigest()
        archive.write(local, name)
    archive.writestr('INDEX.json', json.dumps(dependencies, indent=2))
    archive.write(root / 'THIRD_PARTY_NOTICES.md', 'THIRD_PARTY_NOTICES.md')
print(output)

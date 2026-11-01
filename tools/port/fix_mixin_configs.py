"""Rewrites the mixin configs as UTF-8 without BOM and registers the accessor mixins.

A BOM makes Mixin's JSON parser fail on the config, and an earlier PowerShell round trip added one.
"""
import json
import io

FILES = {
    "src/main/resources/legacyconnector.mixins.json": ("access.EntityAccess", "access.ChunkMapAccess"),
    "src/main/resources/legacyconnector.compat.mixins.json": (),
}

for path, names in FILES.items():
    with io.open(path, "r", encoding="utf-8-sig") as f:
        cfg = json.load(f)
    for name in names:
        if name not in cfg["mixins"]:
            cfg["mixins"].insert(0, name)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(cfg, indent=2) + "\n")
    raw = open(path, "rb").read()
    assert not raw.startswith(b"\xef\xbb\xbf"), path
    print(f"{path}: UTF-8 without BOM, {len(cfg['mixins'])} mixins")

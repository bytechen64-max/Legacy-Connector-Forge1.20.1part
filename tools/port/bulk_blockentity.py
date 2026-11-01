"""1.20.1's block entity data methods take no registry lookup (it arrived with the component holders in 1.20.5)."""
import os
import re

PATTERNS = [
    # declarations and overrides
    (re.compile(r"void saveAdditional\(CompoundTag (\w+), HolderLookup\.Provider \w+\)"), r"void saveAdditional(CompoundTag \1)"),
    (re.compile(r"void loadAdditional\(CompoundTag (\w+), HolderLookup\.Provider \w+\)"), r"void loadAdditional(CompoundTag \1)"),
    (re.compile(r"CompoundTag getUpdateTag\(HolderLookup\.Provider \w+\)"), r"CompoundTag getUpdateTag()"),
    (re.compile(r"void onDataPacket\((Connection|net\.minecraft\.network\.Connection) (\w+), ClientboundBlockEntityDataPacket (\w+),\s*HolderLookup\.Provider \w+\)"),
     r"void onDataPacket(\1 \2, ClientboundBlockEntityDataPacket \3)"),
    (re.compile(r"void handleUpdateTag\(CompoundTag (\w+), HolderLookup\.Provider \w+\)"), r"void handleUpdateTag(CompoundTag \1)"),
    # the super calls
    (re.compile(r"super\.saveAdditional\((\w+), registries\)"), r"super.saveAdditional(\1)"),
    (re.compile(r"super\.loadAdditional\((\w+), registries\)"), r"super.loadAdditional(\1)"),
    (re.compile(r"super\.onDataPacket\((\w+), (\w+), registries\)"), r"super.onDataPacket(\1, \2)"),
    # the packet factory takes a one-argument tag getter on 1.20.1
    (re.compile(r"ClientboundBlockEntityDataPacket\.create\(this, \(be, reg\) -> tag\)"),
     r"ClientboundBlockEntityDataPacket.create(this, be -> tag)"),
]

counts = {}
changed = []
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        src = open(p, encoding="utf-8").read()
        before = src
        for rx, repl in PATTERNS:
            src, n = rx.subn(repl, src)
            if n:
                counts[rx.pattern[:60]] = counts.get(rx.pattern[:60], 0) + n
        if src != before:
            open(p, "w", encoding="utf-8", newline="").write(src)
            changed.append(p)

for k, v in counts.items():
    print(f"{v:4}  {k}")
print("files changed:", len(changed))
for c in changed:
    print("  ", c)

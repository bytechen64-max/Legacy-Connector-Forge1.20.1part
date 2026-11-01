"""legacy_meta: the DataComponentType calls become the NBT-backed helpers of CompatComponents (see its doc)."""
import os
import re
import sys

# getOrDefault must be rewritten before get; both the short and the fully qualified name occur.
PATTERNS = [
    (re.compile(r"(?P<recv>[\w.]+)\.getOrDefault\(\s*(?:org\.kylepitcock\.legacyconnector\.core\.data\.)?CompatComponents\.legacyMeta\(\),\s*(?P<def>[^()]*?)\)"),
     r"CompatComponents.legacyMetaOr(\g<recv>, \g<def>)"),
    (re.compile(r"(?P<recv>[\w.]+)\.set\(\s*(?:org\.kylepitcock\.legacyconnector\.core\.data\.)?CompatComponents\.legacyMeta\(\),\s*(?P<val>[^;]+?)\)\s*;"),
     r"CompatComponents.setLegacyMeta(\g<recv>, \g<val>);"),
    (re.compile(r"(?P<recv>[\w.]+)\.remove\(\s*(?:org\.kylepitcock\.legacyconnector\.core\.data\.)?CompatComponents\.legacyMeta\(\)\s*\)"),
     r"CompatComponents.clearLegacyMeta(\g<recv>)"),
    (re.compile(r"(?P<recv>[\w.]+)\.get\(\s*(?:org\.kylepitcock\.legacyconnector\.core\.data\.)?CompatComponents\.legacyMeta\(\)\s*\)"),
     r"CompatComponents.legacyMeta(\g<recv>)"),
]

IMPORT = "import org.kylepitcock.legacyconnector.core.data.CompatComponents;"


def add_import(src: str) -> str:
    if IMPORT in src:
        return src
    m = re.search(r"^import ", src, re.MULTILINE)
    if not m:
        return src
    return src[: m.start()] + IMPORT + "\n" + src[m.start():]


changed = []
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        src = open(p, encoding="utf-8").read()
        if "CompatComponents.legacyMeta" not in src or name == "CompatComponents.java":
            continue
        original = src
        for pattern, repl in PATTERNS:
            src = pattern.sub(repl, src)
        if src != original:
            src = add_import(src)
            open(p, "w", encoding="utf-8", newline="").write(src)
            changed.append((p, original.count("CompatComponents.legacyMeta"), src.count("CompatComponents.legacyMeta")))
print("rewrote", len(changed), "files")
for p, before, after in changed:
    print(f"   {p}  legacyMeta calls: {before} -> {after}")

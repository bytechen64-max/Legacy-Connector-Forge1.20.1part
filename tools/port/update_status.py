"""Keeps PORTING.md's status line in step with the last compile."""
import io
import re

P = "PORTING.md"
src = io.open(P, encoding="utf-8").read()
src = re.sub(r"^\d+ compile errors at the last run", "216 compile errors at the last run", src, flags=re.MULTILINE)
# record the AT finding, which shapes the remaining work
MARK = "- **ForgeGradle does not apply a mod's access transformer to the compile classpath.**"
if MARK not in src:
    src = src.replace(
        "## What is left",
        MARK + " Forge applies it at runtime only, and rebuilding the mapped jar or deleting the AT step output does not\n"
        "  change that; the members the shim needs are reached through Mixin accessors (`mixin/access/EntityAccess`,\n"
        "  `mixin/access/ChunkMapAccess`) instead. Keep the `accesstransformer.cfg` for runtime, but do not rely on it to compile.\n"
        "  The mixin configs must stay UTF-8 **without** BOM: Mixin's JSON parser rejects a BOM.\n\n"
        "## What is left")
io.open(P, "w", encoding="utf-8", newline="\n").write(src)
print([l for l in src.splitlines() if "compile errors at the last run" in l])

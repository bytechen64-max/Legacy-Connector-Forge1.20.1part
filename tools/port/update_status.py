"""Keeps PORTING.md's status line and the done-list in step with the last compile."""
import io
import re

P = "PORTING.md"
src = io.open(P, encoding="utf-8").read()
src = re.sub(r"^\d+ compile errors at the last run", "238 compile errors at the last run", src, flags=re.MULTILINE)
# the recipe, pack and TriState items are done
for marker in (
    "3. **Recipes** (~12).",
    "4. **Resource packs** (~12).",
):
    while marker in src:
        start = src.index(marker)
        end = src.find("\n", src.find("\n", src.find("\n", start) + 1) + 1)
        # drop the item's bullet and its three continuation lines
        stop = start
        for _ in range(4):
            nxt = src.find("\n", stop)
            if nxt < 0:
                break
            stop = nxt + 1
        src = src[:start] + src[stop:]
src = src.replace("5. **NeoForge-only hooks** (~10): `TriState`, ", "5. **NeoForge-only hooks** (~10): ")
io.open(P, "w", encoding="utf-8", newline="\n").write(src)
print("PORTING.md updated")
print([l for l in src.splitlines() if "compile errors at the last run" in l])

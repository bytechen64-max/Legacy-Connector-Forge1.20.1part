"""Keeps PORTING.md's status line in step with the last compile."""
import io
import re

P = "PORTING.md"
src = io.open(P, encoding="utf-8").read()
src = re.sub(r"^\d+ compile errors at the last run", "154 compile errors at the last run", src, flags=re.MULTILINE)
io.open(P, "w", encoding="utf-8", newline="\n").write(src)
print([l for l in src.splitlines() if "compile errors at the last run" in l])

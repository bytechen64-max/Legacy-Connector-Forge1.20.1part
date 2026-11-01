"""Keeps PORTING.md's status line in step with the last compile."""
import io
import re

P = "PORTING.md"
src = io.open(P, encoding="utf-8").read()
src = re.sub(r"^\d+ compile errors at the last run",
             "284 compile errors at the last run", src, flags=re.MULTILINE)
# the advancement item is done
src = src.replace(
    "2. **Advancements** (~20). `AdvancementHolder`/`AdvancementNode`/`AdvancementTree`/`AdvancementType` are 1.20.2+;\n"
    "   1.20.1 has `Advancement` objects in a `Map<ResourceLocation, Advancement>`, `FrameType`, and\n"
    "   `PlayerAdvancements.getOrStartProgress(Advancement)`. `Criterion` is generic in 1.20.1 (`Criterion<T extends\n"
    "   CriterionTriggerInstance>`), and `CriterionProgress` deals in `Date`, not `Instant`.\n",
    "")
io.open(P, "w", encoding="utf-8", newline="\n").write(src)
print("PORTING.md status updated")

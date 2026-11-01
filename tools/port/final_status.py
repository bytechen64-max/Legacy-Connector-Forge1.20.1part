"""Writes the final port status into PORTING.md (replacing the old status line)."""
import io
import re

P = "PORTING.md"
src = io.open(P, encoding="utf-8").read()

STATUS = """515 compile errors at the last run (the count moves as javac gets further into the tree). Categories, highest value first:

| Category | Sites | Where |
|---|---|---|
| `cannot find symbol` (per-site) | ~380 | spread over the 1.12.2 shim, the 1.7.10 shim and the bridges |
| `incompatible parameter types in lambda` | 3 | `SoundHandler`, `CommandBlockBaseLogic`, ... |
| `no instance(s) of type variable T` | 3 | generics that 1.20.1 infers differently |
| `finalizeSpawn cannot be applied` | 3 | fixed for the four known calls; the rest need reading |
| `ServerData.State` / `Type` | 3 + 3 | the shim's own ping state is in place; two GUIs still read the modern enum |

The port had ~988 errors when the compiler first type-checked the whole tree; 473 of them are resolved.

Remaining clusters worth doing first (each a single sitting):

- `RegisterBrewingRecipesEvent` (3): `BrewingRecipeRegistry.addRecipe` instead of the 1.21 builder.
- `RegisterClientExtensionsEvent` (3): item client extensions through `Item#initializeClient`.
- `MinecraftProfileTextures` (2): the authlib 6 skin record has no 1.20.1 equivalent; `SkinManager` needs the old path.
- `SelectMusicEvent` (2): no 1.20.1 hook; needs a `MusicManager` mixin.
- `net.minecraft.core.component` leftovers (a handful), `DimensionTransition` (0 left), `EquipmentSlotGroup` (0 left).
"""

src = re.sub(r"^\d+ compile errors at the last run.*?(?=\n\n)", STATUS.rstrip(), src, count=1, flags=re.MULTILINE | re.DOTALL)
io.open(P, "w", encoding="utf-8", newline="\n").write(src)
print("status section written")

"""Records the 1.20.1 limitations found so far in PORTING.md."""
import io

P = "PORTING.md"
src = io.open(P, encoding="utf-8").read()
marker = "## Gotchas"
note = """## Known 1.20.1 limitations

- **Legacy effect icons** are not drawn yet: NeoForge 1.21 registers them through `IClientMobEffectExtensions`, which 1.20.1 does
  not have. `EffectIcons1122.draw` keeps the legacy drawing logic for the client mixin that will call it from
  `EffectRenderingInventoryScreen`; until then a mod potion shows the modern atlas icon.
- **Item client extensions** (`IClientItemExtensions`, custom `BlockEntityWithoutLevelRenderer`s) move from NeoForge's
  `RegisterClientExtensionsEvent` to `Item#initializeClient`, which the legacy item adapters have to override.
- **Play-phase disconnect** has no packet before 1.20.2; the legacy packet yields null and the server closes the connection.

"""
if "## Known 1.20.1 limitations" not in src:
    idx = src.find(marker)
    if idx < 0:
        src = src + "\n" + note
    else:
        src = src[:idx] + note + src[idx:]
    io.open(P, "w", encoding="utf-8", newline="\n").write(src)
    print("recorded the limitations")
else:
    print("already recorded")

"""Forge 1.20.1 has no RegistryFriendlyByteBuf (1.20.5+): menus, spawn data and payloads use a plain FriendlyByteBuf.

LegacyCraftingRecipe is left out: it uses a StreamCodec around the buffer, which is the separate recipe-serializer port.
"""
import os

SKIP = {"LegacyCraftingRecipe.java"}

changed = []
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java") or name in SKIP:
            continue
        p = os.path.join(dirpath, name)
        src = open(p, encoding="utf-8").read()
        if "RegistryFriendlyByteBuf" not in src:
            continue
        src = src.replace("import net.minecraft.network.RegistryFriendlyByteBuf;",
                          "import net.minecraft.network.FriendlyByteBuf;")
        src = src.replace("RegistryFriendlyByteBuf", "FriendlyByteBuf")
        open(p, "w", encoding="utf-8", newline="").write(src)
        changed.append(p)
print("rewrote", len(changed), "files")
for c in changed:
    print("  ", c)

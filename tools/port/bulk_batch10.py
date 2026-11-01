"""finalizeSpawn takes the extra CompoundTag, enchantments use 1.20.1 names, chunk lookups go through the accessor."""
import os
import re

# ---- finalizeSpawn(level, difficulty, type, data) -> + ", null"
def add_tag_arg(src: str) -> tuple[str, int]:
    out = []
    idx = 0
    n = 0
    while True:
        m = re.search(r"\.finalizeSpawn\(", src[idx:])
        if not m:
            out.append(src[idx:])
            break
        start = idx + m.end() - 1  # at '('
        out.append(src[idx:start])
        depth = 0
        i = start
        commas = 0
        while i < len(src):
            c = src[i]
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    break
            elif c == "," and depth == 1:
                commas += 1
            i += 1
        args = src[start + 1:i]
        if commas == 3 and "null" not in args.split(",")[-1]:
            n += 1
            out.append("(" + args + ", null)")
        else:
            out.append(src[start:i + 1])
        idx = i + 1
    return "".join(out), n


renames = [
    ("Enchantments.FORTUNE", "Enchantments.BLOCK_FORTUNE"),
]
# enchants.getOrThrow(Enchantments.X) -> Enchantments.X
get_or_throw = re.compile(r"enchants?\.getOrThrow\((net\.minecraft\.world\.item\.enchantment\.Enchantments\.[A-Z_]+)\)")
accessor = re.compile(r"(\w+)\.getChunkSource\(\)\.chunkMap\.getVisibleChunkIfPresent\(")
tick = re.compile(r"\(net\.minecraftforge\.event\.tick\.EntityTickEvent\.(Pre|Post) e\) ->")

finalize = 0
changed = []
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        src = open(p, encoding="utf-8").read()
        before = src
        src, n = add_tag_arg(src)
        finalize += n
        for old, new in renames:
            src = src.replace(old, new)
        src = get_or_throw.sub(r"\1", src)
        src = accessor.sub(
            r"((org.kylepitcock.legacyconnector.mixin.access.ChunkMapAccess) \1.getChunkSource().chunkMap).legacyconnector$visibleChunk(", src)
        # 1.20.1 has no all-entity tick event
        src = tick.sub(lambda m: "(net.minecraftforge.event.entity.living.LivingEvent.LivingTickEvent e) ->", src)
        if src != before:
            open(p, "w", encoding="utf-8", newline="").write(src)
            changed.append(p)

print("finalizeSpawn calls given the tag:", finalize)
print("files changed:", len(changed))
for c in changed[:20]:
    print("  ", c)

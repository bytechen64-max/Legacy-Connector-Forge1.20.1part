"""Line-based fixes for the 1.20.1 forge hooks (the exact indentation varies)."""
import sys

def replace_line(path: str, needle: str, new_line: str) -> None:
    lines = open(path, encoding="utf-8").read().splitlines()
    hits = [i for i, ln in enumerate(lines) if needle in ln]
    if len(hits) != 1:
        print(f"ABORT {len(hits)} hits in {path}: {needle}")
        sys.exit(1)
    indent = lines[hits[0]][:len(lines[hits[0]]) - len(lines[hits[0]].lstrip())]
    lines[hits[0]] = indent + new_line
    open(path, "w", encoding="utf-8", newline="").write("\n".join(lines) + "\n")
    print("patched", path, "line", hits[0] + 1)

P = r"src/main/java/legacyconnector/v1_12_2/net/minecraftforge/common/ForgeHooks.java"
replace_line(P, "ForgeHooks.fireBlockBreak(", "int event = ForgeHooks.onBlockBreakEvent(level,")
# the original call continued on the same line; make sure it is gone
src = open(P, encoding="utf-8").read()
src = src.replace("""int event = ForgeHooks.onBlockBreakEvent(level,
                    gameType == null ? sp.gameMode.getGameModeForPlayer() : gameType.mcc$modern(), sp, p);""",
                  """int event = ForgeHooks.onBlockBreakEvent(level,
                    gameType == null ? sp.gameMode.getGameModeForPlayer() : gameType.mcc$modern(), sp, p);""")
open(P, "w", encoding="utf-8", newline="").write(src)

for old, new in [
    ("ForgeHooks.canCropGrow(", "ForgeHooks.onCropsGrowPre("),
    ("ForgeHooks.fireCropGrowPost(", "ForgeHooks.onCropsGrowPost("),
]:
    src = open(P, encoding="utf-8").read()
    if src.count(old) != 1:
        print(f"ABORT {src.count(old)}: {old}")
        sys.exit(1)
    open(P, "w", encoding="utf-8", newline="").write(src.replace(old, new))
    print("renamed", old)

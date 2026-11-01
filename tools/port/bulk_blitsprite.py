"""GuiGraphics.blitSprite (1.20.2+) -> LegacyGuiSprites.blit over the sprite's texture file on 1.20.1."""
import os
import re

# gui.blitSprite(<sprite>, x, y, w, h)
SIMPLE = re.compile(r"\b(gui|graphics)\.blitSprite\(")
COUNT_SIMPLE = 0
COUNT_SHEET = 0
changed = []

# the nine-argument form: blitSprite(sprite, texW, texH, u, v, x, y, w, h)
SHEET = re.compile(r"\b(gui|graphics)\.blitSprite\(")

for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        if "LegacyGuiSprites" in p:
            continue
        src = open(p, encoding="utf-8").read()
        if ".blitSprite(" not in src:
            continue
        before = src
        # simple form only: rewrite calls whose argument list ends after five arguments
        out = []
        idx = 0
        while True:
            m = SHEET.search(src, idx)
            if not m:
                out.append(src[idx:])
                break
            out.append(src[idx:m.start()])
            # find the matching close paren
            depth = 0
            i = m.end() - 1
            while i < len(src):
                c = src[i]
                if c == "(":
                    depth += 1
                elif c == ")":
                    depth -= 1
                    if depth == 0:
                        break
                i += 1
            args_start = m.end()
            args = src[args_start:i]
            call = src[m.start():i + 1]
            # count top-level commas
            depth2 = 0
            commas = 0
            for c in args:
                if c in "([{":
                    depth2 += 1
                elif c in ")]}":
                    depth2 -= 1
                elif c == "," and depth2 == 0:
                    commas += 1
            argc = commas + 1
            if argc == 5:
                out.append(f"{m.group(0)}")
                # keep the receiver and prepend the graphics argument
                out[-1] = "org.kylepitcock.legacyconnector.v1_7_10.client.LegacyGuiSprites.blit(" + m.group(1) + ", "
                COUNT_SIMPLE += 1
            elif argc == 9:
                out[-1] = "org.kylepitcock.legacyconnector.v1_7_10.client.LegacyGuiSprites.blit(" + m.group(1) + ", "
                COUNT_SHEET += 1
            else:
                out.append(call[:m.end() - m.start()])
                COUNT_SIMPLE += 0
            out.append(args + ")")
            idx = i + 1
        src = "".join(out)
        if src != before:
            open(p, "w", encoding="utf-8", newline="").write(src)
            changed.append(p)

print("simple:", COUNT_SIMPLE, "sheet:", COUNT_SHEET)
for c in changed:
    print("  ", c)

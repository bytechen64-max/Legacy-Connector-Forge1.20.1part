"""1.20.1's Component.Serializer reads and writes JSON without a registry lookup."""
import os


def drop_second_arg(src: str, marker: str) -> tuple[str, int]:
    out = []
    idx = 0
    n = 0
    while True:
        at = src.find(marker, idx)
        if at < 0:
            out.append(src[idx:])
            break
        start = at + len(marker) - 1  # at '('
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
        out.append(src[idx:start + 1])
        if commas == 1:
            # keep everything before the top-level comma
            depth = 0
            cut = len(args)
            for k, c in enumerate(args):
                if c == "(":
                    depth += 1
                elif c == ")":
                    depth -= 1
                elif c == "," and depth == 0:
                    cut = k
                    break
            out.append(args[:cut].rstrip())
            n += 1
        else:
            out.append(args)
        out.append(")")
        idx = i + 1
    return "".join(out), n


count = 0
changed = []
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        src = open(p, encoding="utf-8").read()
        before = src
        src, n1 = drop_second_arg(src, "Component.Serializer.fromJson(")
        src, n2 = drop_second_arg(src, "Component.Serializer.toJson(")
        count += n1 + n2
        if src != before:
            open(p, "w", encoding="utf-8", newline="").write(src)
            changed.append((p, n1 + n2))

print("calls reduced:", count)
for c in changed:
    print("  ", c)

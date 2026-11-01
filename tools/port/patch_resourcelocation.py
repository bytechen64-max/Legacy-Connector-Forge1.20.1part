"""1.21.1 -> 1.20.1 API rewrites that are pure renames (ResourceLocation factories, item/block keys...).

Minecraft 1.21 made the ResourceLocation constructors private and renamed the factories; 1.20.1 still has the
public constructors, so every `fromNamespaceAndPath`/`parse`/`withDefaultNamespace` call goes back to `new`.
"""
import os
import sys

FACTORIES = {
    "ResourceLocation.fromNamespaceAndPath": "new ResourceLocation",
    "ResourceLocation.parse": "new ResourceLocation",
}
WITH_DEFAULT = "ResourceLocation.withDefaultNamespace"


def rewrite_calls(src: str) -> tuple[str, int]:
    """Replace FACTORIES[k](args) -> new ResourceLocation(args), respecting nested parentheses."""
    changed = 0
    for old, new in FACTORIES.items():
        i = 0
        while True:
            j = src.find(old + "(", i)
            if j < 0:
                break
            # not a longer name (e.g. something.fromNamespaceAndPathFoo)
            end = j + len(old) + 1
            depth = 0
            k = end
            while k < len(src):
                c = src[k]
                if c == "(":
                    depth += 1
                elif c == ")":
                    if depth == 0:
                        break
                    depth -= 1
                k += 1
            src = src[:j] + new + src[j + len(old):]
            changed += 1
            i = j + len(new) + 1
    # withDefaultNamespace("x") -> new ResourceLocation("minecraft", "x")
    i = 0
    while True:
        j = src.find(WITH_DEFAULT + "(", i)
        if j < 0:
            break
        start = j + len(WITH_DEFAULT) + 1
        depth = 0
        k = start
        while k < len(src):
            c = src[k]
            if c == "(":
                depth += 1
            elif c == ")":
                if depth == 0:
                    break
                depth -= 1
            k += 1
        arg = src[start:k]
        src = src[:j] + 'new ResourceLocation("minecraft", ' + arg + ")" + src[k + 1:]
        changed += 1
        i = j + 10
    return src, changed


def main(root: str) -> None:
    files = 0
    calls = 0
    for base in ("src", "loader/src", "testmods/src", "examples", "tools"):
        for dirpath, _dirs, names in os.walk(os.path.join(root, base)):
            for n in names:
                if not n.endswith(".java"):
                    continue
                p = os.path.join(dirpath, n)
                src = open(p, encoding="utf-8", errors="surrogateescape").read()
                if "fromNamespaceAndPath" not in src and "ResourceLocation.parse" not in src and WITH_DEFAULT not in src:
                    continue
                new, c = rewrite_calls(src)
                if c:
                    open(p, "w", encoding="utf-8", errors="surrogateescape", newline="").write(new)
                    files += 1
                    calls += c
    print(f"rewrote {calls} ResourceLocation factory calls in {files} files")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")

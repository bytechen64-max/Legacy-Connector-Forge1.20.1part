"""For every 'does not override' error, prints the file:line and the next three source lines (the signature)."""
import re
import sys

pat = re.compile(r"^(?P<f>.+?\.java):(?P<l>\d+): error: (?P<m>.*)$")


def main(log: str, *filters: str) -> None:
    lines = open(log, encoding="utf-8", errors="replace").read().splitlines()
    for ln in lines:
        m = pat.match(ln.strip())
        if not m:
            continue
        if not any(f in m.group("m") for f in filters):
            continue
        f = m.group("f")
        n = int(m.group("l"))
        src = open(f, encoding="utf-8", errors="replace").read().splitlines()
        short = f.split("Legacy Connector")[-1].replace("\\src\\main\\java\\", "").lstrip("\\")
        print(f"--- {short}:{n}")
        for i in range(n, min(n + 3, len(src))):
            print("    " + src[i].strip()[:140])


if __name__ == "__main__":
    main(sys.argv[1], *sys.argv[2:])

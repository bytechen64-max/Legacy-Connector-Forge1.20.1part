"""Prints `file:line` plus the offending source line for errors whose message contains a filter."""
import re
import sys

pat = re.compile(r"^(?P<f>.+?\.java):(?P<l>\d+): (?:error): (?P<m>.*)$")


def main(log: str, *filters: str) -> None:
    lines = open(log, encoding="utf-8", errors="replace").read().splitlines()
    for i, ln in enumerate(lines):
        m = pat.match(ln.strip())
        if not m:
            continue
        if not any(f in m.group("m") for f in filters):
            continue
        src = lines[i + 1].strip() if i + 1 < len(lines) else ""
        f = m.group("f").split("Legacy Connector")[-1].replace("\\src\\main\\java\\", "").lstrip("\\")
        print(f"{f}:{m.group('l')}\n    {src[:150]}")


if __name__ == "__main__":
    main(sys.argv[1], *sys.argv[2:])

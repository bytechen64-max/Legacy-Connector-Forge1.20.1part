"""Prints every javac error as `file:line :: message :: symbol` (one line per site)."""
import re
import sys

pat = re.compile(r"^(?P<f>.+?\.java):(?P<l>\d+): (?:error): (?P<m>.*)$")


def main(path: str) -> None:
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    for i, ln in enumerate(lines):
        m = pat.match(ln.strip())
        if not m:
            continue
        ctx = [x.strip() for x in lines[i + 1:i + 4] if x.strip()]
        sym = next((c.split("symbol:")[-1].strip() for c in ctx if "symbol:" in c), "")
        f = m.group("f").split("Legacy Connector")[-1]
        f = f.replace("\\src\\main\\java\\", "").lstrip("\\")
        print(f"{f}:{m.group('l')} :: {m.group('m')[:55]} :: {sym[:45]}")


if __name__ == "__main__":
    main(sys.argv[1])

"""Prints the unique javac error sites of a captured log, one per line, in source order."""
import re
import sys

ERR = re.compile(r"^(?P<file>.+?\.java):(?P<line>\d+): (?:error|错误): (?P<msg>.*)$")


def main(path: str) -> None:
    seen = set()
    for ln in open(path, encoding="utf-8", errors="replace").read().splitlines():
        m = ERR.match(ln.strip())
        if not m:
            continue
        key = (m.group("file"), m.group("line"), m.group("msg"))
        if key in seen:
            continue
        seen.add(key)
        f = m.group("file").replace("G:\\epca\\Legacy Connector\\", "")
        print(f"{f}:{m.group('line')}: {m.group('msg')}")
    print(f"\n# {len(seen)} unique error sites", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1])

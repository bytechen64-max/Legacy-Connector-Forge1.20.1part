"""Prints every javac error as `file:line: message :: symbol=X location=Y` so the remaining port work can be grouped."""
import collections
import re
import sys

ERR = re.compile(r"^(?P<file>.+?\.java):(?P<line>\d+): (?:error|错误): (?P<msg>.*)$")


def main(path: str) -> None:
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    sites = []
    for i, ln in enumerate(lines):
        m = ERR.match(ln.strip())
        if not m:
            continue
        context = "\n".join(lines[i:i + 5])
        sym = re.search(r"symbol:\s+(?:class|variable|method)\s+([^\s(]+)", context)
        loc = re.search(r"location:\s+(?:class|interface|variable|package)\s+([\w.$]+)", context)
        extra = ""
        if sym:
            extra += " :: " + sym.group(1)
        if loc:
            extra += " [" + loc.group(1) + "]"
        sites.append((m.group("file"), m.group("line"), m.group("msg")[:70], extra))
    groups = collections.Counter()
    for f, _l, msg, extra in sites:
        groups[(msg, extra)] += 1
    print(f"# {len(sites)} error sites, {len(groups)} kinds\n")
    for (msg, extra), count in groups.most_common(120):
        print(f"{count:3}  {msg}{extra}")


if __name__ == "__main__":
    main(sys.argv[1])

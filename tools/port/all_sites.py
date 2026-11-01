"""Prints every error site as `file:line | source line` for a bulk review."""
import re
import sys

pat = re.compile(r"^(?P<f>.+?\.java):(?P<l>\d+): (?:error): (?P<m>.*)$")


def main(log: str, limit: int) -> None:
    lines = open(log, encoding="utf-8", errors="replace").read().splitlines()
    seen = set()
    count = 0
    for i, ln in enumerate(lines):
        m = pat.match(ln.strip())
        if not m:
            continue
        key = (m.group("f"), m.group("l"))
        if key in seen:
            continue
        seen.add(key)
        src = lines[i + 1].strip() if i + 1 < len(lines) else ""
        f = m.group("f").split("Legacy Connector")[-1].replace("\\src\\main\\java\\", "").lstrip("\\")
        print(f"{f}:{m.group('l')} | {src[:120]}")
        count += 1
        if count >= limit:
            break


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 10_000)

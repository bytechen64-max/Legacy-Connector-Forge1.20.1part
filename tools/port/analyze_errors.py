"""Groups javac errors from a captured Gradle log so the port can be fixed by category.

Usage: python tools/port/analyze_errors.py <logfile> [top]
"""
import collections
import re
import sys

ERR = re.compile(r"^(?P<file>.+?\.java):(?P<line>\d+): (?:error|错误): (?P<msg>.*)$")


def main(path: str, top: int = 60) -> None:
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    by_symbol = collections.Counter()
    by_file = collections.Counter()
    by_pkg = collections.Counter()
    total = 0
    details = collections.defaultdict(list)
    for i, ln in enumerate(lines):
        m = ERR.match(ln.strip())
        if not m:
            continue
        total += 1
        msg = m.group("msg").strip()
        by_file[m.group("file")] += 1
        context = "\n".join(lines[i:i + 5])
        pm = re.search(r"package ([\w.]+) does not exist", msg)
        if pm:
            by_pkg[pm.group(1)] += 1
            key = "package " + pm.group(1) + " does not exist"
        else:
            sm = re.search(r"symbol:\s+(?:class|variable|method)\s+([^\s(]+)", context)
            mm = re.search(r"location:\s+(?:class|interface|variable|package)\s+([\w.]+)", context)
            if sm:
                key = f"{msg[:44]} :: {sm.group(1)}"
                if mm:
                    key += f" [{mm.group(1)}]"
            else:
                key = msg[:90]
        by_symbol[key] += 1
        if len(details[key]) < 2:
            details[key].append(f"{m.group('file')}:{m.group('line')}")
    print(f"TOTAL ERRORS: {total}\n")
    print(f"=== top {top} categories ===")
    for k, v in by_symbol.most_common(top):
        print(f"{v:6}  {k}")
        for d in details[k]:
            print(f"          e.g. {d}")
    print("\n=== missing packages ===")
    for k, v in by_pkg.most_common(30):
        print(f"{v:6}  {k}")
    print("\n=== files with most errors ===")
    for k, v in by_file.most_common(25):
        print(f"{v:6}  {k}")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 60)

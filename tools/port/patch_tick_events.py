"""1.21's phase tick events -> 1.20.1's TickEvent.ServerTickEvent with an explicit phase guard."""
import os
import re

LAMBDA = re.compile(r"\((?:net\.minecraftforge\.event\.tick\.)?ServerTickEvent\.(Pre|Post) e\) -> \{")
EXPR = re.compile(r"\((?:net\.minecraftforge\.event\.tick\.)?ServerTickEvent\.(Pre|Post) e\) -> ([^{].*?)\);")

changed = []
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        src = open(p, encoding="utf-8").read()
        if "ServerTickEvent" not in src:
            continue
        before = src

        def block(m: "re.Match[str]") -> str:
            phase = "START" if m.group(1) == "Pre" else "END"
            line_start = src.rfind("\n", 0, m.start()) + 1
            indent = re.match(r"[ \t]*", src[line_start:]).group(0) + "    "
            return ("(net.minecraftforge.event.TickEvent.ServerTickEvent e) -> {\n"
                    f"{indent}// 1.21 has separate Pre/Post events; 1.20.1 fires one event with a phase.\n"
                    f"{indent}if (e.phase != net.minecraftforge.event.TickEvent.Phase.{phase}) return;")

        src = LAMBDA.sub(block, src)

        def expr(m: "re.Match[str]") -> str:
            phase = "START" if m.group(1) == "Pre" else "END"
            body = m.group(2)
            return (f"(net.minecraftforge.event.TickEvent.ServerTickEvent e) -> {{\n"
                    f"            if (e.phase != net.minecraftforge.event.TickEvent.Phase.{phase}) return;\n"
                    f"            {body};\n        }})")

        src = EXPR.sub(expr, src)
        src = src.replace("import net.minecraftforge.event.tick.ServerTickEvent;",
                          "import net.minecraftforge.event.TickEvent;")
        src = src.replace("net.minecraftforge.event.tick.ServerTickEvent", "net.minecraftforge.event.TickEvent.ServerTickEvent")
        if src != before:
            open(p, "w", encoding="utf-8", newline="").write(src)
            changed.append(p)

print("patched", len(changed), "files")
for c in changed:
    print("  ", c)

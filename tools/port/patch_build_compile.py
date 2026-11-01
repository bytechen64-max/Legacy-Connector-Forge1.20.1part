"""Decouple the main compile from the loader's mapping download (type-check loop only)."""
import sys

P = "build.gradle"
s = open(P, encoding="utf-8").read()
old = "tasks.named('compileJava', JavaCompile) {\n    dependsOn ':loader:classes'"
new = ("tasks.named('compileJava', JavaCompile) {\n"
       "    // The widener (and therefore the loader's legacy mapping downloads) is only needed for a runnable build,\n"
       "    // not to type-check the sources: -PskipShimWidener keeps the compile-only loop fast.\n"
       "    if (!project.hasProperty('skipShimWidener')) dependsOn ':loader:classes'")
if s.count(old) != 1:
    print("ABORT: anchor count", s.count(old))
    sys.exit(1)
open(P, "w", encoding="utf-8", newline="").write(s.replace(old, new))
print("patched", P)

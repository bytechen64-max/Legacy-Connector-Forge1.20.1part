"""BundledLibraries: the NeoForge discovery pipeline argument becomes a plain path sink."""
import sys

P = r"loader/src/main/java/org/kylepitcock/legacyconnector/loader/BundledLibraries.java"
s = open(P, encoding="utf-8").read()
pairs = [
    ("import net.minecraftforge.forgespi.locating.IDiscoveryPipeline;\n"
     "import net.minecraftforge.forgespi.locating.IncompatibleFileReporting;\n"
     "import net.minecraftforge.forgespi.locating.ModFileDiscoveryAttributes;\n", ""),
    ("static Result provide(IDiscoveryPipeline pipeline, Path cacheDir,",
     "static Result provide(java.util.function.Consumer<Path> sink, Path cacheDir,"),
    ("                        pipeline.addPath(target, ModFileDiscoveryAttributes.DEFAULT, IncompatibleFileReporting.ERROR);",
     "                        sink.accept(target);"),
]
for old, new in pairs:
    n = s.count(old)
    if n != 1:
        print("ABORT", n, old[:60])
        sys.exit(1)
    s = s.replace(old, new)
open(P, "w", encoding="utf-8", newline="").write(s)
print("patched", P)

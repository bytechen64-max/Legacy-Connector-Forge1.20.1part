"""One-shot patch of LegacyModLocator for the Forge 1.20.1 IModLocator SPI (see the class doc)."""
import re
import sys

P = r"loader/src/main/java/org/kylepitcock/legacyconnector/loader/LegacyModLocator.java"

# (regex, replacement, expected match count). Leading whitespace is captured as group 1 so the
# indentation of the rewritten line follows the original.
EDITS = [
    (
        r'^(?P<i>[ \t]*)Path cacheDir = gameDir\.resolve\("\.legacyconnector"\)\.resolve\("cache"\);\r?\n',
        r'\g<i>Path cacheDir = gameDir.resolve(".legacyconnector").resolve("cache");\n'
        r'\g<i>Path originalsDir = modsDir.resolve(ORIGINALS_DIR);\n'
        r'\g<i>List<Path> scanDirs = List.of(modsDir, modsDir.resolve("1.7.10"), modsDir.resolve("1.12.2"), originalsDir);\n',
        1,
    ),
    (
        r'^(?P<i>[ \t]*)if \(context\.isLocated\(p\) \|\| !seenNames\.add\(p\.getFileName\(\)\.toString\(\)\.toLowerCase\(\)\)\) continue;',
        r'\g<i>if (!seenNames.add(p.getFileName().toString().toLowerCase())) continue;',
        1,
    ),
    (
        r'^[ \t]*// a translated jar taken out of a cache: only Legacy Connector itself loads those, from its own cache\r?\n'
        r'(?P<i>[ \t]*)context\.addLocated\(p\);\r?\n',
        r'\g<i>// a translated jar taken out of a cache: only Legacy Connector itself loads those, from its own cache\n',
        1,
    ),
    (
        r'(?P<i>[ \t]*)BundledLibraries\.Result libraries = BundledLibraries\.provide\(pipeline, cacheDir,',
        r'\g<i>BundledLibraries.Result libraries = BundledLibraries.provide(outputs::add, cacheDir,',
        1,
    ),
    (
        r'^[ \t]*// Claim the original even if we end up skipping it, so FML does not raise its own\r?\n'
        r'[ \t]*// "this is an old Forge mod" error on top of ours\.\r?\n'
        r'[ \t]*context\.addLocated\(jar\.path\);\r?\n',
        r'                // FML\'s own mods-folder locator must not see the original, so it is moved out of its way\n'
        r'                // (see relocateOriginals); the translated jar is what it gets instead.\n',
        1,
    ),
    (
        r'^(?P<i>[ \t]*)// Unknown translation keys are displayed verbatim by FML\'s error screen\. Bridged libraries are expected\.\r?\n'
        r'[ \t]*if \(replacedBy == null && obsolete == null\) pipeline\.addIssue\(ModLoadingIssue\.warning\("Legacy Connector skipped " \+ jar\.fileName\(\) \+ ": " \+ skip\.replace\("\'"\, ""\)\)\r?\n'
        r'[ \t]*\.withAffectedPath\(jar\.path\)\);\r?\n',
        r'\g<i>if (replacedBy == null && obsolete == null) LOG.warn("Legacy Connector: skipped {}: {}", jar.fileName(), skip.replace("\'", ""));\n',
        1,
    ),
    (
        r'^(?P<i>[ \t]*)pipeline\.addIssue\(ModLoadingIssue\.error\("Legacy Connector could not translate " \+ jar\.fileName\(\)\)\r?\n'
        r'[ \t]*\.withAffectedPath\(jar\.path\)\.withCause\(e\)\);\r?\n',
        '',
        1,
    ),
    (r'^(?P<i>[ \t]*)pipeline\.addPath\(synthJar, [^;]*\);', r'\g<i>outputs.add(synthJar);', 1),
    (r'^(?P<i>[ \t]*)pipeline\.addPath\(split\.sharedLibrary\(\), [^;]*\);', r'\g<i>outputs.add(split.sharedLibrary());', 1),
    (r'^(?P<i>[ \t]*)pipeline\.addPath\(p, [^;]*\);', r'\g<i>outputs.add(p);', 1),
]

# every scan folder list becomes the shared one
SCAN_LIST = 'List.of(modsDir, modsDir.resolve("1.7.10"), modsDir.resolve("1.12.2"))'

RELOCATE = '''
    /**
     * Moves the legacy jars out of the top level of the mods folder, where Forge's own mods-folder locator would list them and
     * stop the game with "built for an older Forge". Forge 1.20.1 has no way to hand a path to FML and have the other locators
     * skip it (NeoForge's {@code IDiscoveryPipeline} has no equivalent here), so the file itself moves; its content is never
     * changed. A jar that cannot be moved (read-only folder) stays where it is and is reported.
     */
    private static void relocateOriginals(List<LegacyJar> legacy, Path modsDir, Path originalsDir) {
        if (!Boolean.parseBoolean(LibraryBridges.readConfig(modsDir).getProperty("loader.relocateLegacyJars", "true").trim())) {
            LOG.warn("Legacy Connector: loader.relocateLegacyJars=false: the legacy jars stay in the top level of the mods folder, so "
                    + "Forge's own mods-folder locator also reads them and rejects them as built for an older Forge. Keep legacy jars in "
                    + "mods/1.7.10 or mods/1.12.2 instead.");
            return;
        }
        try {
            Files.createDirectories(originalsDir);
        } catch (IOException e) {
            LOG.warn("Legacy Connector: cannot create {}, the legacy jars stay in the mods folder", originalsDir, e);
            return;
        }
        Path root = originalsDir.toAbsolutePath().normalize();
        for (LegacyJar jar : legacy) {
            Path source = jar.path.toAbsolutePath().normalize();
            if (!Files.isRegularFile(source) || root.equals(source.getParent())) continue;
            Path target = root.resolve(source.getFileName());
            for (int n = 2; Files.exists(target); n++) target = root.resolve(n + "-" + source.getFileName());
            try {
                Files.move(source, target);
            } catch (IOException e) {
                LOG.warn("Legacy Connector: could not move {} out of the mods folder; Forge will also read it and reject it", source, e);
            }
        }
    }
'''

src = open(P, encoding="utf-8").read()
for pattern, repl, expected in EDITS:
    src, n = re.subn(pattern, repl, src, count=0, flags=re.MULTILINE)
    if n != expected:
        print(f"ABORT: {n} matches (expected {expected}) for {pattern[:70]!r}")
        sys.exit(1)

src, n = re.subn(re.escape(SCAN_LIST), "scanDirs", src)
if n < 2:
    print(f"ABORT: only {n} scan folder lists found")
    sys.exit(1)

anchor = "    private static Map<String, ClassInfo> scanPeers("
if src.count(anchor) != 1:
    print("ABORT: scanPeers anchor not unique")
    sys.exit(1)
src = src.replace(anchor, RELOCATE.lstrip("\n") + "\n" + anchor)

old_call = "            writeReport(gameDir, outcomes, split);"
if src.count(old_call) != 1:
    print("ABORT: writeReport anchor not unique")
    sys.exit(1)
src = src.replace(old_call, "            relocateOriginals(legacy, modsDir, originalsDir);\n" + old_call)

open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P, "scanDirs replacements:", n)

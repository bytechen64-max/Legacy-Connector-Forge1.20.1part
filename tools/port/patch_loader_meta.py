"""Remaining mechanical Forge-1.20.1 fixes in the loader (metadata, service file, hierarchy roots)."""
import os
import sys

ROOT = "."
CHANGES = [
    ("loader/src/main/java/org/kylepitcock/legacyconnector/loader/meta/ModMetadataGenerator.java", [
        (' * Produces what NeoForge needs to load a translated jar as an ordinary mod: a {@code neoforge.mods.toml}',
         ' * Produces what Forge needs to load a translated jar as an ordinary mod: a {@code mods.toml}'),
        ('AnnotationVisitor av = cw.visitAnnotation("Lnet/neoforged/fml/common/Mod;", true);',
         'AnnotationVisitor av = cw.visitAnnotation("Lnet/minecraftforge/fml/common/Mod;", true);'),
        ('"(Lnet/neoforged/bus/api/IEventBus;Lnet/neoforged/fml/ModContainer;)V"',
         '"(Lnet/minecraftforge/eventbus/api/IEventBus;Lnet/minecraftforge/fml/ModContainer;)V"'),
        ('"(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Lnet/neoforged/bus/api/IEventBus;Lnet/neoforged/fml/ModContainer;)V"',
         '"(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Lnet/minecraftforge/eventbus/api/IEventBus;Lnet/minecraftforge/fml/ModContainer;)V"'),
        # Forge 1.20.1 spells dependencies with `mandatory`, not NeoForge's `type`
        ('        sb.append("type=").append(q(required ? "required" : "optional")).append(\'\\n\');',
         '        sb.append("mandatory=").append(required ? "true" : "false").append(\'\\n\');'),
    ]),
    ("loader/src/main/java/org/kylepitcock/legacyconnector/loader/transform/LegacyJarTransformer.java", [
        ('outResources.put("META-INF/neoforge.mods.toml", ModMetadataGenerator.modsToml(jar));',
         'outResources.put("META-INF/mods.toml", ModMetadataGenerator.modsToml(jar));'),
    ]),
    ("loader/src/main/java/org/kylepitcock/legacyconnector/loader/transform/Hierarchy.java", [
        ('"net/neoforged/",', '"net/minecraftforge/",'),
    ]),
    ("loader/src/main/java/org/kylepitcock/legacyconnector/loader/LibraryBridges.java", [
        ('ZipEntry e = zip.getEntry("META-INF/neoforge.mods.toml");', 'ZipEntry e = zip.getEntry("META-INF/mods.toml");'),
    ]),
    ("loader/src/main/java/org/kylepitcock/legacyconnector/loader/LegacyModLocator.java", [
        ('var e = zip.getEntry("META-INF/neoforge.mods.toml");', 'var e = zip.getEntry("META-INF/mods.toml");'),
    ]),
    ("loader/src/main/java/org/kylepitcock/legacyconnector/loader/LegacyJarInspector.java", [
        ('if (zip.getEntry("META-INF/neoforge.mods.toml") != null\n                    || zip.getEntry("META-INF/mods.toml") != null',
         'if (zip.getEntry("META-INF/mods.toml") != null'),
    ]),
]

for path, pairs in CHANGES:
    p = os.path.join(ROOT, path)
    src = open(p, encoding="utf-8").read()
    for old, new in pairs:
        n = src.count(old)
        if n != 1:
            print(f"ABORT: {n} matches in {path} for {old[:60]!r}")
            sys.exit(1)
        src = src.replace(old, new)
    open(p, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

# the discovery service file moves to the Forge SPI name
svc_dir = os.path.join(ROOT, "loader/src/main/resources/META-INF/services")
old_svc = os.path.join(svc_dir, "net.neoforged.neoforgespi.locating.IModFileCandidateLocator")
new_svc = os.path.join(svc_dir, "net.minecraftforge.forgespi.locating.IModLocator")
if os.path.exists(old_svc):
    body = open(old_svc, encoding="utf-8").read()
    os.remove(old_svc)
    open(new_svc, "w", encoding="utf-8", newline="").write(body)
    print("service file ->", new_svc)
print("done")

package org.kylepitcock.legacyconnector.loader;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import java.util.Set;
import java.util.jar.JarEntry;
import java.util.jar.JarOutputStream;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable;
import org.junit.jupiter.api.io.TempDir;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.objectweb.asm.ClassWriter;
import org.objectweb.asm.Opcodes;
import static org.junit.jupiter.api.Assertions.*;

class LegacyJarInspectorTest {
    @TempDir Path directory;
    private byte[] annotated(String descriptor, String key, String id) {
        var writer = new ClassWriter(0);
        writer.visit(Opcodes.V1_8, Opcodes.ACC_PUBLIC, "example/Mod", null, "java/lang/Object", null);
        if (descriptor != null) {
            var annotation = writer.visitAnnotation(descriptor, true);
            annotation.visit(key, id); annotation.visitEnd();
        }
        writer.visitField(Opcodes.ACC_PUBLIC | Opcodes.ACC_STATIC | Opcodes.ACC_FINAL, "reference", "Ljava/lang/String;", null,
                "net/minecraftforge/fml/javafmlmod/FMLJavaModLoadingContext").visitEnd();
        writer.visitEnd(); return writer.toByteArray();
    }
    private Path jar(byte[] clazz, Map<String, String> resources) throws Exception {
        Path file = Files.createTempFile(directory, "mod", ".jar");
        try (var out = new JarOutputStream(Files.newOutputStream(file))) {
            out.putNextEntry(new JarEntry("example/Mod.class")); out.write(clazz); out.closeEntry();
            for (var entry : resources.entrySet()) {
                out.putNextEntry(new JarEntry(entry.getKey())); out.write(entry.getValue().getBytes(java.nio.charset.StandardCharsets.UTF_8)); out.closeEntry();
            }
        }
        return file;
    }
    @ParameterizedTest @ValueSource(strings = {"META-INF/mods.toml", "META-INF/neoforge.mods.toml", "fabric.mod.json", "quilt.mod.json",
            "META-INF/services/net.minecraftforge.forgespi.locating.IDependencyLocator", "META-INF/services/net.neoforged.neoforgespi.locating.IModFileCandidateLocator"})
    void modernMetadataWinsOverBundledLegacyCode(String metadata) throws Exception {
        assertNull(LegacyJarInspector.inspect(jar(annotated(LegacyJarInspector.MOD_1_12, "modid", "oldhelper"), Map.of(metadata, "example"))));
    }
    @Test void modernModValueAnnotationIsNotTheLegacyModidAnnotation() throws Exception {
        assertNull(LegacyJarInspector.inspect(jar(annotated(LegacyJarInspector.MOD_1_12, "value", "modern"), Map.of())));
        assertNull(LegacyJarInspector.inspect(jar(annotated(LegacyJarInspector.MOD_NEO, "value", "modern"), Map.of())));
    }
    @Test void sharedFmlReferencesAloneAreNotLegacyEvidence() throws Exception {
        assertNull(LegacyJarInspector.inspect(jar(annotated(null, null, null), Map.of())));
    }
    @Test void modernLibraryManifestWinsOverLegacyReferences() throws Exception {
        assertNull(LegacyJarInspector.inspect(jar(annotated(LegacyJarInspector.MOD_1_12, "modid", "oldhelper"),
                Map.of("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\r\nFMLModType: LIBRARY\r\n\r\n"))));
    }
    @Test void malformedManifestDoesNotHideAnOtherwiseValidLegacyMod() throws Exception {
        assertNotNull(LegacyJarInspector.inspect(jar(annotated(LegacyJarInspector.MOD_1_12, "modid", "example"),
                Map.of("META-INF/MANIFEST.MF", "broken header\n"))));
    }
    @Test void realLegacyAnnotationsStillSelectBothFamilies() throws Exception {
        assertEquals(LegacyVersion.V1_12_2, LegacyJarInspector.inspect(jar(annotated(LegacyJarInspector.MOD_1_12, "modid", "parasites"), Map.of())).version);
        assertEquals(LegacyVersion.V1_7_10, LegacyJarInspector.inspect(jar(annotated(LegacyJarInspector.MOD_1_7, "modid", "oldmod"), Map.of())).version);
    }
    @Test void exclusionUsesIdsAndDoesNotDependOnTheFilename() throws Exception {
        Path file = jar(annotated(LegacyJarInspector.MOD_1_12, "modid", "Example"), Map.of());
        assertNotNull(LegacyJarInspector.inspect(file));
        assertNull(LegacyJarInspector.inspect(file, Set.of("EXAMPLE")));
        assertNotNull(LegacyJarInspector.inspect(file, Set.of("other")));
        assertEquals(Set.of("connector", "example", "third"), LegacyJarInspector.excludedModIds(" connector, EXAMPLE; third\nexample "));
    }
    @Test void exclusionAlsoCoversMetadataOnlyMods() throws Exception {
        Path file = jar(annotated(null, null, null), Map.of("mcmod.info", "[{\"modid\":\"example\",\"mcversion\":\"1.12.2\"}]"));
        assertNotNull(LegacyJarInspector.inspect(file));
        assertNull(LegacyJarInspector.inspect(file, Set.of("example")));
    }
    @Test @EnabledIfEnvironmentVariable(named = "LEGACYCONNECTOR_TEST_MODERN_JAR", matches = ".+")
    void actualModernArtifactIsNotClaimed() throws Exception {
        assertNull(LegacyJarInspector.inspect(Path.of(System.getenv("LEGACYCONNECTOR_TEST_MODERN_JAR"))));
    }
    @Test @EnabledIfEnvironmentVariable(named = "LEGACYCONNECTOR_TEST_LEGACY_JAR", matches = ".+")
    void actualSrpArtifactRemainsLegacy() throws Exception {
        var result = LegacyJarInspector.inspect(Path.of(System.getenv("LEGACYCONNECTOR_TEST_LEGACY_JAR")));
        assertNotNull(result); assertEquals(LegacyVersion.V1_12_2, result.version);
        assertTrue(result.mods.stream().anyMatch(mod -> mod.legacyId.equals("srparasites")));
    }
}

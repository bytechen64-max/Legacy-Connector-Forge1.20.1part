"""1.20.1 resource packs: PackLocationInfo/PackSelectionConfig/openPrimary do not exist yet; packs are built from an id."""
import sys

GENERATED_OLD = '''        PackLocationInfo info = new PackLocationInfo(id, Component.literal(title), PackSource.BUILT_IN, Optional.empty());
        Pack.ResourcesSupplier supplier = new Pack.ResourcesSupplier() {
            @Override
            public PackResources openPrimary(PackLocationInfo location) {
                // read for the pack metadata only (Pack.readPackMetadata, NeoForge's readMeta), which needs no generated file
                return new GeneratedPack(location, type, recipes, org.kylepitcock.legacyconnector.core.LegacyConfig.perfLazyPackMetadata());
            }

            @Override
            public PackResources openFull(PackLocationInfo location, Pack.Metadata metadata) {
                return new GeneratedPack(location, type, recipes);
            }
        };
        Pack pack = Pack.readMetaAndCreate(info, supplier, type, new PackSelectionConfig(true, position, false));'''

GENERATED_NEW = '''        Pack.ResourcesSupplier supplier = new Pack.ResourcesSupplier() {
            @Override
            public PackResources open(String packId) {
                // 1.20.1 asks once, for the metadata the repository scan reads; the content is generated on first use of the pack
                return new GeneratedPack(packId, type, recipes, org.kylepitcock.legacyconnector.core.LegacyConfig.perfLazyPackMetadata());
            }
        };
        Pack pack = Pack.readMetaAndCreate(id, Component.literal(title), false, supplier, type, position, PackSource.BUILT_IN);'''

EDITS = {
    r"src/main/java/org/kylepitcock/legacyconnector/core/pack/GeneratedPack.java": [
        ("import net.minecraft.server.packs.PackLocationInfo;\nimport net.minecraft.server.packs.PackResources;\n"
         "import net.minecraft.server.packs.PackSelectionConfig;\nimport net.minecraft.server.packs.PackType;",
         "import net.minecraft.server.packs.PackResources;\nimport net.minecraft.server.packs.PackType;"),
        ("    private final PackLocationInfo location;\n    private final PackType type;",
         "    private final String id;\n    private final PackType type;"),
        ("    private GeneratedPack(PackLocationInfo location, PackType type, boolean recipes) {\n        this(location, type, recipes, false);\n    }",
         "    private GeneratedPack(String id, PackType type, boolean recipes) {\n        this(id, type, recipes, false);\n    }"),
        ("    private GeneratedPack(PackLocationInfo location, PackType type, boolean recipes, boolean metadataOnly) {\n        this.location = location;",
         "    private GeneratedPack(String id, PackType type, boolean recipes, boolean metadataOnly) {\n        this.id = id;"),
        (GENERATED_OLD, GENERATED_NEW),
        ("    public PackLocationInfo location() {\n        return location;\n    }",
         "    public String packId() {\n        return id;\n    }"),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/core/pack/GameResourcesFolderPack.java": [
        ("import net.minecraft.server.packs.PackLocationInfo;\nimport net.minecraft.server.packs.PackResources;\nimport net.minecraft.server.packs.PackType;\n"
         "import net.minecraft.server.packs.repository.Pack;\nimport net.minecraft.server.packs.repository.PackSource;\nimport net.minecraft.server.packs.PackSelectionConfig;",
         "import net.minecraft.server.packs.PackResources;\nimport net.minecraft.server.packs.PackType;\n"
         "import net.minecraft.server.packs.repository.Pack;\nimport net.minecraft.server.packs.repository.PackSource;"),
        ("    private GameResourcesFolderPack(PackLocationInfo location, Path root) {\n        super(location);",
         "    private GameResourcesFolderPack(String id, Path root) {\n        super(id, true);"),
        ('''        PackLocationInfo info = new PackLocationInfo(id, Component.literal("Legacy Connector: " + title), PackSource.BUILT_IN, Optional.empty());
        Pack.ResourcesSupplier supplier = new Pack.ResourcesSupplier() {
            @Override
            public PackResources openPrimary(PackLocationInfo location) {
                return new GameResourcesFolderPack(location, dir);
            }

            @Override
            public PackResources openFull(PackLocationInfo location, Pack.Metadata metadata) {
                return new GameResourcesFolderPack(location, dir);
            }
        };
        Pack pack = Pack.readMetaAndCreate(info, supplier, PackType.CLIENT_RESOURCES, new PackSelectionConfig(true, Pack.Position.TOP, false));''',
         '''        Pack.ResourcesSupplier supplier = new Pack.ResourcesSupplier() {
            @Override
            public PackResources open(String packId) {
                return new GameResourcesFolderPack(packId, dir);
            }
        };
        Pack pack = Pack.readMetaAndCreate(id, Component.literal("Legacy Connector: " + title), false, supplier,
                PackType.CLIENT_RESOURCES, Pack.Position.TOP, PackSource.BUILT_IN);'''),
    ],
    r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/LegacyModPacks.java": [
        ("import net.minecraft.server.packs.PackLocationInfo;\nimport net.minecraft.server.packs.PackResources;\nimport net.minecraft.server.packs.PackSelectionConfig;\nimport net.minecraft.server.packs.PackType;",
         "import net.minecraft.server.packs.PackResources;\nimport net.minecraft.server.packs.PackType;"),
        ("    private LegacyModPacks(PackLocationInfo location) {\n        super(location);\n    }",
         "    private LegacyModPacks(String id) {\n        super(id, true);\n    }"),
        ('''        PackLocationInfo info = new PackLocationInfo("legacyconnector_mod_packs", Component.literal("Legacy Connector: legacy mod packs"), PackSource.BUILT_IN, Optional.empty());
        Pack.ResourcesSupplier supplier = new Pack.ResourcesSupplier() {
            @Override
            public PackResources openPrimary(PackLocationInfo location) {
                return new LegacyModPacks(location);
            }

            @Override
            public PackResources openFull(PackLocationInfo location, Pack.Metadata metadata) {
                return new LegacyModPacks(location);
            }
        };
        Pack pack = Pack.readMetaAndCreate(info, supplier, PackType.CLIENT_RESOURCES, new PackSelectionConfig(true, Pack.Position.BOTTOM, false));''',
         '''        Pack.ResourcesSupplier supplier = new Pack.ResourcesSupplier() {
            @Override
            public PackResources open(String packId) {
                return new LegacyModPacks(packId);
            }
        };
        Pack pack = Pack.readMetaAndCreate("legacyconnector_mod_packs", Component.literal("Legacy Connector: legacy mod packs"), false, supplier,
                PackType.CLIENT_RESOURCES, Pack.Position.BOTTOM, PackSource.BUILT_IN);'''),
    ],
}

for path, pairs in EDITS.items():
    src = open(path, encoding="utf-8").read()
    for old, new in pairs:
        n = src.count(old)
        if n != 1:
            print(f"ABORT {n} matches in {path}: {old.splitlines()[0][:70]!r}")
            sys.exit(1)
        src = src.replace(old, new)
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

"""RecipeBridge: pattern-matching switch (Java 21) -> instanceof chains (Java 17, Forge 1.20.1's baseline)."""
import sys

P = r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/bridge/RecipeBridge.java"
s = open(P, encoding="utf-8").read()

EDITS = [
    (
        """                Object source = switch (spec) {
                    case Shaped s -> s.source;
                    case Shapeless s -> s.source;
                    case Smelting s -> s.source;
                    case Custom c -> c.source;
                };""",
        """                Object source = sourceOf(spec);""",
    ),
    (
        """                JsonObject json = switch (spec) {
                    case Shaped s -> shaped(s);
                    case Shapeless s -> shapeless(s);
                    case Smelting s -> smelting(s);
                    case Custom c -> custom(c);
                };""",
        """                JsonObject json;
                if (spec instanceof Shaped s) json = shaped(s);
                else if (spec instanceof Shapeless s) json = shapeless(s);
                else if (spec instanceof Smelting s) json = smelting(s);
                else json = custom((Custom) spec);""",
    ),
    (
        """                String ns = switch (spec) {
                    case Shaped s -> s.owner;
                    case Shapeless s -> s.owner;
                    case Smelting s -> s.owner;
                    case Custom c -> c.owner;
                };""",
        """                String ns = ownerOf(spec);""",
    ),
    (
        """        String kind = switch (spec) {
            case Shaped s -> "shaped";
            case Shapeless s -> "shapeless";
            case Smelting s -> "smelting";
            case Custom c -> "custom";
        };""",
        """        String kind;
        if (spec instanceof Shaped) kind = "shaped";
        else if (spec instanceof Shapeless) kind = "shapeless";
        else if (spec instanceof Smelting) kind = "smelting";
        else kind = "custom";""",
    ),
    (
        """            ItemStack output = switch (spec) {
                case Shaped s -> s.output;
                case Shapeless s -> s.output;
                case Smelting s -> s.output;
                case Custom c -> CUSTOM.get(c.index).getRecipeOutput();
            };""",
        """            ItemStack output;
            if (spec instanceof Shaped s) output = s.output;
            else if (spec instanceof Shapeless s) output = s.output;
            else if (spec instanceof Smelting s) output = s.output;
            else output = CUSTOM.get(((Custom) spec).index).getRecipeOutput();""",
    ),
]

for old, new in EDITS:
    if s.count(old) != 1:
        print("ABORT count", s.count(old), old.splitlines()[0][:60])
        sys.exit(1)
    s = s.replace(old, new)

HELPERS = '''    private static Object sourceOf(Spec spec) {
        if (spec instanceof Shaped s) return s.source;
        if (spec instanceof Shapeless s) return s.source;
        if (spec instanceof Smelting s) return s.source;
        return ((Custom) spec).source;
    }

    private static String ownerOf(Spec spec) {
        if (spec instanceof Shaped s) return s.owner;
        if (spec instanceof Shapeless s) return s.owner;
        if (spec instanceof Smelting s) return s.owner;
        return ((Custom) spec).owner;
    }

'''
anchor = "    private static Set<Object> liveCrafting() {"
if s.count(anchor) != 1:
    print("ABORT anchor")
    sys.exit(1)
s = s.replace(anchor, HELPERS + anchor)

open(P, "w", encoding="utf-8", newline="").write(s)
print("patched", P)

# incremental compilation is safe while the shim widener is skipped
B = "build.gradle"
b = open(B, encoding="utf-8").read()
old = "    // The widener rewrites the compiled classes in place; an incremental compile would read them back (widened) as sources' dependencies.\n    options.incremental = false"
new = ("    // The widener rewrites the compiled classes in place; an incremental compile would read them back (widened) as\n"
       "    // sources' dependencies. Without it (-PskipShimWidener) incremental compilation is what keeps the loop fast.\n"
       "    options.incremental = project.hasProperty('skipShimWidener')")
if b.count(old) != 1:
    print("ABORT build.gradle anchor", b.count(old))
    sys.exit(1)
open(B, "w", encoding="utf-8", newline="").write(b.replace(old, new))
print("patched build.gradle (incremental)")

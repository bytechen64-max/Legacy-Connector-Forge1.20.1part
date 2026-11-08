package org.kylepitcock.legacyconnector.loader.resource;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.JsonPrimitive;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;

/**
 * Mechanical, registry-independent asset fixes applied while a legacy jar is rewritten.
 *
 * <p>Anything that needs to know what a block or item <em>is</em> (blockstates for metadata, recipes with
 * damage values, ore dictionary ingredients) is translated later at runtime by the shim's generated
 * resource/data pack. Here we only fix things that would stop resources from loading at all:</p>
 * <ul>
 *     <li>Modern {@code ResourceLocation}s reject upper case and most punctuation, which 1.7.10 allowed in
 *     both namespaces and paths ({@code assets/IC2/textures/blocks/CopperOre.png}).</li>
 *     <li>{@code .lang} files became {@code .json} in 1.13.</li>
 *     <li>The block atlas only stitches {@code textures/block/}; legacy mods use {@code textures/blocks/}.</li>
 *     <li>1.12 JSON recipes moved from {@code assets/} to {@code data/} and changed format; they are staged
 *     under {@code legacyconnector_legacy/} for the runtime translator.</li>
 * </ul>
 */
public final class LegacyResourceConverter {
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().disableHtmlEscaping().create();

    /** Legacy texture folders that must be added to the modern atlases. */
    private static final String BLOCK_ATLAS = """
            {
              "sources": [
                { "type": "directory", "source": "block", "prefix": "block/" },
                { "type": "directory", "source": "item", "prefix": "item/" },
                { "type": "directory", "source": "blocks", "prefix": "blocks/" },
                { "type": "directory", "source": "items", "prefix": "items/" }
              ]
            }
            """;

    private final Map<String, byte[]> output = new LinkedHashMap<>();
    private final Map<String, Map<String, String>> langs = new LinkedHashMap<>();
    private boolean sawTextures;

    /**
     * @return true if the entry was consumed (written to the output, possibly renamed, or dropped on purpose).
     */
    public boolean accept(String path, byte[] data) {
        if (path.equals("pack.mcmeta") || path.equals("pack.png")) {
            return true; // NeoForge synthesizes mod pack metadata; a pack_format 1 file only confuses it.
        }
        if (!path.startsWith("assets/")) return false;

        String modern = normalizePath(path);
        data = repairSrpResource(modern, data);
        if (modern.contains("/textures/")) sawTextures = true;

        if (modern.matches("assets/[^/]+/blockstates/.+\\.json")) {
            // A legacy blockstate is only an input for the runtime's translation. Left where a pack serves it, one 1.12 file the
            // modern model loader cannot parse (a Forge multipart condition on a property the modern block does not have) aborts the
            // whole blockstate stack of that block, and the block draws as the missing model. The pack filter that should hide these
            // files does not apply to a mod's own pack, so the file moves to a folder no pack serves; the runtime reads it from there.
            data = lowercaseResourceRefs(data);
            output.putIfAbsent(modern.replace("/blockstates/", "/legacyconnector_blockstates/"), data);
            return true;
        }

        if (modern.endsWith(".lang")) {
            // assets/<ns>/lang/en_us.lang -> merged into assets/<ns>/lang/en_us.json
            String jsonPath = modern.substring(0, modern.length() - ".lang".length()) + ".json";
            Map<String, String> entries = langs.computeIfAbsent(jsonPath, k -> new LinkedHashMap<>());
            parseLang(new String(data, StandardCharsets.UTF_8), entries);
            return true;
        }
        if (modern.matches("assets/[^/]+/recipes/.+\\.json")) {
            output.putIfAbsent("legacyconnector_legacy/" + modern, data);
            return true;
        }
        if (modern.matches("assets/[^/]+/sounds\\.json")) {
            data = convertSounds(data, modern.substring("assets/".length(), modern.indexOf('/', "assets/".length())));
        } else if (modern.endsWith(".mcmeta")) {
            data = sanitizeMcmeta(data);
        } else if (modern.endsWith(".json") && (modern.contains("/models/") || modern.contains("/blockstates/"))) {
            data = lowercaseResourceRefs(data);
        }
        output.putIfAbsent(modern, data);
        return true;
    }

    /** Called once all entries are seen; returns every resource to write into the transformed jar. */
    public Map<String, byte[]> finish() {
        for (var lang : langs.entrySet()) {
            // A real .json lang shipped next to the .lang wins.
            if (output.containsKey(lang.getKey())) continue;
            JsonObject obj = new JsonObject();
            lang.getValue().forEach(obj::addProperty);
            output.put(lang.getKey(), GSON.toJson(obj).getBytes(StandardCharsets.UTF_8));
        }
        if (sawTextures) {
            output.putIfAbsent("assets/minecraft/atlases/blocks.json", BLOCK_ATLAS.getBytes(StandardCharsets.UTF_8));
        }
        resolveModelParents();
        addModelTexturesToAtlas();
        return output;
    }

    /** Narrow repairs for broken resources shipped by SRP 1.10.9; leave corrected releases untouched. */
    private byte[] repairSrpResource(String path, byte[] data) {
        if ((path.equals("assets/srparasites/blockstates/brusewood_trapdoor.json")
                || path.equals("assets/srparasites/blockstates/consumed_trapdoor.json"))
                && new String(data, StandardCharsets.UTF_8).contains("srparasites:consumed_planks_stairs")) {
            String name = path.substring(path.lastIndexOf('/') + 1, path.length() - 5);
            JsonObject root = new JsonObject(), variants = new JsonObject();
            for (String half : List.of("bottom", "top")) for (boolean open : new boolean[]{false, true}) {
                String model = name + "_" + (open ? "open" : half);
                JsonObject template = new JsonObject(), textures = new JsonObject();
                template.addProperty("parent", "minecraft:block/template_trapdoor_" + (open ? "open" : half));
                textures.addProperty("texture", "srparasites:blocks/" + name);
                template.add("textures", textures);
                output.putIfAbsent("assets/srparasites/models/block/" + model + ".json", GSON.toJson(template).getBytes(StandardCharsets.UTF_8));
                String[] facings = {"north", "east", "south", "west"};
                for (int i = 0; i < facings.length; i++) {
                    JsonObject variant = new JsonObject();
                    variant.addProperty("model", "srparasites:" + model);
                    variant.addProperty("y", i * 90);
                    variants.add("facing=" + facings[i] + ",half=" + half + ",open=" + open, variant);
                }
            }
            root.add("variants", variants);
            return GSON.toJson(root).getBytes(StandardCharsets.UTF_8);
        }
        if (path.equals("assets/srparasites/models/block/infestedstainstairs_outer.json")) {
            String text = new String(data, StandardCharsets.UTF_8);
            return text.replace("\"top\": \"srparasites:blocks/infestedstain,",
                    "\"top\": \"srparasites:blocks/infestedstain\",").getBytes(StandardCharsets.UTF_8);
        }
        if (path.equals("assets/srparasites/models/block/arraytowerlarge.mtl")) {
            String text = new String(data, StandardCharsets.UTF_8);
            return text.replace("map_Kd pasted.png", "map_Kd srparasites:blocks/arraytowertexture")
                    .getBytes(StandardCharsets.UTF_8);
        }
        return data;
    }

    /** 1.12 stitched every model texture, including GUI icons used as items. Modern atlases need explicit sources. */
    private void addModelTexturesToAtlas() {
        String atlasPath = "assets/minecraft/atlases/blocks.json";
        JsonObject atlas = JsonParser.parseString(new String(output.getOrDefault(atlasPath,
                BLOCK_ATLAS.getBytes(StandardCharsets.UTF_8)), StandardCharsets.UTF_8)).getAsJsonObject();
        JsonArray sources = atlas.has("sources") ? atlas.getAsJsonArray("sources") : new JsonArray();
        java.util.Set<String> added = new java.util.LinkedHashSet<>();
        for (var entry : output.entrySet()) {
            if (!entry.getKey().contains("/models/") || !entry.getKey().endsWith(".json")) continue;
            try {
                JsonObject model = JsonParser.parseString(new String(entry.getValue(), StandardCharsets.UTF_8)).getAsJsonObject();
                if (!model.has("textures") || !model.get("textures").isJsonObject()) continue;
                for (JsonElement value : model.getAsJsonObject("textures").asMap().values()) {
                    if (!value.isJsonPrimitive() || !value.getAsJsonPrimitive().isString()) continue;
                    String ref = value.getAsString();
                    if (ref.startsWith("#")) continue;
                    int colon = ref.indexOf(':');
                    String ns = colon < 0 ? "minecraft" : ref.substring(0, colon);
                    String path = colon < 0 ? ref : ref.substring(colon + 1);
                    if (path.startsWith("block/") || path.startsWith("blocks/") || path.startsWith("item/") || path.startsWith("items/")) continue;
                    if (!output.containsKey("assets/" + ns + "/textures/" + path + ".png") || !added.add(ns + ":" + path)) continue;
                    JsonObject source = new JsonObject();
                    source.addProperty("type", "single");
                    source.addProperty("resource", ns + ":" + path);
                    sources.add(source);
                }
            } catch (RuntimeException ignored) {
                // Preserve the loader's diagnostic for unrelated malformed model files.
            }
        }
        if (!added.isEmpty()) {
            atlas.add("sources", sources);
            output.put(atlasPath, GSON.toJson(atlas).getBytes(StandardCharsets.UTF_8));
        }
    }

    /**
     * 1.12 named a model's parent relative to its own kind's folder ("parent": "cube_all" in models/block/x.json is
     * models/block/cube_all.json; a mod model may mean its own or vanilla's), while 1.13 and later name the full path. The whole jar
     * is known by now, so every parent without a namespace is resolved against the files the mod actually ships.
     */
    /**
     * 1.12's vanilla template models that 1.14 renamed or split. A 1.12 model that parents one of them (every slab, wall, door,
     * trapdoor, pane and torch in a mod) pointed at a file that no longer exists, so the block drew as the missing model.
     */
    private static final Map<String, String> RENAMED_VANILLA_MODELS = Map.ofEntries(
            Map.entry("block/half_slab", "block/slab"),
            Map.entry("block/upper_slab", "block/slab_top"),
            Map.entry("block/wall_post", "block/template_wall_post"),
            Map.entry("block/wall_side", "block/template_wall_side"),
            Map.entry("block/wall_side_tall", "block/template_wall_side_tall"),
            Map.entry("block/glass_pane_post_ends", "block/template_glass_pane_post"),
            Map.entry("block/door_bottom", "block/door_bottom_left"),
            Map.entry("block/door_top", "block/door_top_left"),
            Map.entry("block/door_bottom_rh", "block/door_bottom_right"),
            Map.entry("block/door_top_rh", "block/door_top_right"),
            Map.entry("block/trapdoor_bottom", "block/template_trapdoor_bottom"),
            Map.entry("block/trapdoor_open", "block/template_trapdoor_open"),
            Map.entry("block/trapdoor_top", "block/template_trapdoor_top"),
            Map.entry("block/grass_path", "block/dirt_path"),
            Map.entry("block/slime", "block/slime_block"),
            Map.entry("block/torch", "block/template_torch"),
            Map.entry("block/torch_wall", "block/template_torch_wall"),
            Map.entry("block/grass_snowed", "block/grass_block_snow"));

    private void resolveModelParents() {
        Pattern modelPath = Pattern.compile("assets/([^/]+)/models/(block|item)/(.+)\\.json");
        for (var e : List.copyOf(output.entrySet())) {
            Matcher m = modelPath.matcher(e.getKey());
            if (!m.matches()) continue;
            String namespace = m.group(1);
            String kind = m.group(2);
            try {
                JsonObject root = JsonParser.parseString(new String(e.getValue(), StandardCharsets.UTF_8)).getAsJsonObject();
                JsonElement parent = root.get("parent");
                if (parent == null || !parent.isJsonPrimitive()) continue;
                String ref = parent.getAsString();
                if (ref.indexOf(':') >= 0 || ref.isEmpty()) continue;
                String path = normalizePath(ref);
                String resolved;
                if (path.startsWith("block/") || path.startsWith("item/") || path.startsWith("builtin/")) {
                    // already the full path below models/ ("item/generated", "block/cube_all"): only the namespace is missing
                    resolved = (output.containsKey("assets/" + namespace + "/models/" + path + ".json") ? namespace : "minecraft")
                            + ":" + path;
                } else {
                    String own = "assets/" + namespace + "/models/" + kind + "/" + path + ".json";
                    if (output.containsKey(own)) {
                        resolved = namespace + ":" + kind + "/" + path;
                    } else if (kind.equals("item") && output.containsKey("assets/" + namespace + "/models/block/" + path + ".json")) {
                        // a 1.12 item model parented to a block model of the mod
                        resolved = namespace + ":block/" + path;
                    } else {
                        resolved = "minecraft:" + kind + "/" + path;
                    }
                }
                if (resolved.startsWith("minecraft:")) {
                    // a 1.12 template 1.14 renamed: the old name is not a model any more
                    String renamed = RENAMED_VANILLA_MODELS.get(resolved.substring("minecraft:".length()));
                    if (renamed != null) resolved = "minecraft:" + renamed;
                }
                if (resolved.equals(ref)) continue;
                root.addProperty("parent", resolved);
                output.put(e.getKey(), GSON.toJson(root).getBytes(StandardCharsets.UTF_8));
            } catch (RuntimeException ignored) {
                // malformed JSON is left for the vanilla loader to report
            }
        }
    }

    /**
     * Lower-cases and sanitizes a resource path. Shared convention with the runtime, which applies the same
     * function to every ResourceLocation a legacy mod constructs.
     */
    public static String normalizePath(String path) {
        StringBuilder sb = new StringBuilder(path.length());
        for (char c : path.toLowerCase(Locale.ROOT).toCharArray()) {
            sb.append((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '/' || c == '.' || c == '_' || c == '-' ? c : '_');
        }
        return sb.toString();
    }

    /**
     * 1.7.10 read .mcmeta leniently; mods shipped trailing commas and comments, which the strict 1.21 reader rejects (and
     * then drops the whole sprite). Parse leniently, drop the null an extra comma leaves in an array, write strict JSON.
     */
    static byte[] sanitizeMcmeta(byte[] data) {
        try {
            String text = new String(data, StandardCharsets.UTF_8);
            if (text.startsWith("\uFEFF")) text = text.substring(1);
            JsonElement root = JsonParser.parseString(text);
            dropNullElements(root);
            return GSON.toJson(root).getBytes(StandardCharsets.UTF_8);
        } catch (RuntimeException e) {
            return data;
        }
    }

    private static void dropNullElements(JsonElement e) {
        if (e.isJsonArray()) {
            JsonArray array = e.getAsJsonArray();
            for (int i = array.size() - 1; i >= 0; i--) {
                if (array.get(i).isJsonNull()) array.remove(i);
                else dropNullElements(array.get(i));
            }
        } else if (e.isJsonObject()) {
            for (var entry : e.getAsJsonObject().entrySet()) dropNullElements(entry.getValue());
        }
    }

    static void parseLang(String text, Map<String, String> out) {
        boolean escapes = false;
        for (String line : text.split("\\r?\\n")) {
            if (line.startsWith("﻿")) line = line.substring(1);
            if (line.trim().equals("#PARSE_ESCAPES")) {
                escapes = true;
                continue;
            }
            if (line.isBlank() || line.startsWith("#") || line.startsWith("//")) continue;
            int eq = line.indexOf('=');
            if (eq <= 0) continue;
            String value = line.substring(eq + 1);
            if (escapes) value = value.replace("\\n", "\n").replace("\\t", "\t").replace("\\\\", "\\");
            // 1.7.10 used Java format specifiers verbatim (%s, %d); modern Component formatting accepts %s and
            // positional %1$s only. Numeric conversions are rewritten so translations do not render raw.
            value = value.replaceAll("%(\\d+\\$)?[dfx]", "%$1s").replaceAll("%(\\d+\\$)?\\.\\d+f", "%$1s");
            out.put(line.substring(0, eq), value);
        }
    }

    /**
     * 1.7.10 sounds.json: sound paths without a namespace meant the mod's own domain (1.21 assumes minecraft), names
     * could contain upper case, and "category" is gone (the volume slider is chosen when a sound is played): it is kept as
     * "legacy_category", which the modern parser ignores and the sound bridge reads to pick the slider. Event keys are
     * sanitized like every other resource path.
     */
    static byte[] convertSounds(byte[] data, String namespace) {
        try {
            JsonObject root = JsonParser.parseString(new String(data, StandardCharsets.UTF_8)).getAsJsonObject();
            JsonObject out = new JsonObject();
            for (var e : root.entrySet()) {
                if (!e.getValue().isJsonObject()) continue;
                JsonObject event = e.getValue().getAsJsonObject().deepCopy();
                JsonElement category = event.remove("category");
                if (category != null) event.add("legacy_category", category);
                if (event.has("sounds") && event.get("sounds").isJsonArray()) {
                    JsonArray sounds = new JsonArray();
                    for (JsonElement snd : event.getAsJsonArray("sounds")) {
                        if (snd.isJsonPrimitive()) {
                            sounds.add(soundRef(snd.getAsString(), namespace));
                        } else if (snd.isJsonObject()) {
                            JsonObject o = snd.getAsJsonObject().deepCopy();
                            if (o.has("name")) o.addProperty("name", soundRef(o.get("name").getAsString(), namespace));
                            sounds.add(o);
                        }
                    }
                    event.add("sounds", sounds);
                }
                out.add(normalizePath(e.getKey()), event);
            }
            return GSON.toJson(out).getBytes(StandardCharsets.UTF_8);
        } catch (RuntimeException e) {
            return data;
        }
    }

    private static String soundRef(String ref, String namespace) {
        int colon = ref.indexOf(':');
        String ns = colon < 0 ? namespace : ref.substring(0, colon);
        String path = normalizePath(colon < 0 ? ref : ref.substring(colon + 1));
        // 1.12 named the file from the assets/<ns>/ root; the modern engine resolves it below sounds/ already
        if (path.startsWith("sounds/")) path = path.substring("sounds/".length());
        return ns + ":" + path;
    }

    /** Model/blockstate JSON written for 1.7.10-1.12 may reference textures and parents with upper case. */
    static byte[] lowercaseResourceRefs(byte[] data) {
        try {
            JsonElement root = JsonParser.parseString(new String(data, StandardCharsets.UTF_8));
            fixRefs(root, null);
            return GSON.toJson(root).getBytes(StandardCharsets.UTF_8);
        } catch (RuntimeException e) {
            return data; // keep malformed JSON byte-identical; the vanilla loader will report it
        }
    }

    private static void fixRefs(JsonElement element, String key) {
        if (element instanceof JsonObject obj) {
            for (var e : obj.entrySet()) {
                if (e.getValue() instanceof JsonPrimitive p && p.isString() && isRefKey(e.getKey(), key)) {
                    String fixed = normalizeRef(p.getAsString());
                    if ("textures".equals(key)) fixed = vanillaTexture(fixed);
                    else if (e.getKey().equals("parent")) fixed = vanillaModel(fixed);
                    e.setValue(new JsonPrimitive(fixed));
                } else {
                    fixRefs(e.getValue(), e.getKey());
                }
            }
        } else if (element instanceof JsonArray arr) {
            for (JsonElement e : arr) fixRefs(e, key);
        }
    }

    private static boolean isRefKey(String key, String parentKey) {
        return key.equals("parent") || key.equals("model") || "textures".equals(parentKey);
    }

    /** Vanilla models renamed after 1.12 (parents of mod models). */
    private static final Map<String, String> MODEL_RENAMES = Map.of(
            "block/half_slab", "block/slab",
            "block/upper_slab", "block/slab_top",
            "block/grass_path", "block/dirt_path",
            "block/door_bottom", "block/door_bottom_left",
            "block/door_top", "block/door_top_left",
            "block/door_bottom_rh", "block/door_bottom_right",
            "block/door_top_rh", "block/door_top_right",
            "block/slime", "block/slime_block");

    private static String vanillaModel(String ref) {
        int colon = ref.indexOf(':');
        String ns = colon < 0 ? "minecraft" : ref.substring(0, colon);
        if (!ns.equals("minecraft")) return ref;
        String path = colon < 0 ? ref : ref.substring(colon + 1);
        String renamed = MODEL_RENAMES.get(path);
        // always with the namespace: a mod that ships its own block/slab_top.json (SRParasites) must not see the renamed parent as itself
        return renamed == null ? ref : "minecraft:" + renamed;
    }

    /** Vanilla block and item textures: the folders became block/ and item/, and many files were renamed in 1.13. */
    private static final Map<String, String> TEXTURE_RENAMES = new LinkedHashMap<>();

    static {
        String[] woods = {"oak", "spruce", "birch", "jungle", "acacia", "big_oak:dark_oak"};
        for (String w : woods) {
            String from = w.contains(":") ? w.substring(0, w.indexOf(':')) : w;
            String to = w.contains(":") ? w.substring(w.indexOf(':') + 1) : w;
            TEXTURE_RENAMES.put("block/planks_" + from, "block/" + to + "_planks");
            TEXTURE_RENAMES.put("block/log_" + from, "block/" + to + "_log");
            TEXTURE_RENAMES.put("block/log_" + from + "_top", "block/" + to + "_log_top");
            TEXTURE_RENAMES.put("block/leaves_" + from, "block/" + to + "_leaves");
            TEXTURE_RENAMES.put("block/sapling_" + from, "block/" + to + "_sapling");
            TEXTURE_RENAMES.put("block/door_" + from + "_lower", "block/" + to + "_door_bottom");
            TEXTURE_RENAMES.put("block/door_" + from + "_upper", "block/" + to + "_door_top");
        }
        String[] colors = {"white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", "silver:light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black"};
        for (String c : colors) {
            String from = c.contains(":") ? c.substring(0, c.indexOf(':')) : c;
            String to = c.contains(":") ? c.substring(c.indexOf(':') + 1) : c;
            TEXTURE_RENAMES.put("block/wool_colored_" + from, "block/" + to + "_wool");
            TEXTURE_RENAMES.put("block/glass_" + from, "block/" + to + "_stained_glass");
            TEXTURE_RENAMES.put("block/hardened_clay_stained_" + from, "block/" + to + "_terracotta");
            TEXTURE_RENAMES.put("block/concrete_" + from, "block/" + to + "_concrete");
        }
        String[][] pairs = {
                {"grass_top", "grass_block_top"}, {"grass_side", "grass_block_side"}, {"grass_side_overlay", "grass_block_side_overlay"},
                {"stonebrick", "stone_bricks"}, {"brick", "bricks"}, {"cobblestone_mossy", "mossy_cobblestone"}, {"hardened_clay", "terracotta"},
                {"mob_spawner", "spawner"}, {"reeds", "sugar_cane"}, {"waterlily", "lily_pad"}, {"web", "cobweb"},
                {"flower_dandelion", "dandelion"}, {"flower_rose", "poppy"}, {"tallgrass", "grass"}, {"deadbush", "dead_bush"},
                {"stone_andesite", "andesite"}, {"stone_diorite", "diorite"}, {"stone_granite", "granite"},
                {"stone_andesite_smooth", "polished_andesite"}, {"stone_diorite_smooth", "polished_diorite"}, {"stone_granite_smooth", "polished_granite"},
                {"stonebrick_mossy", "mossy_stone_bricks"}, {"stonebrick_cracked", "cracked_stone_bricks"}, {"stonebrick_carved", "chiseled_stone_bricks"},
                {"sandstone_normal", "sandstone"}, {"sandstone_top", "sandstone_top"}, {"redstone_lamp_off", "redstone_lamp"}, {"redstone_lamp_on", "redstone_lamp_on"},
                {"quartz_block_side", "quartz_block_side"}, {"netherrack", "netherrack"}, {"nether_brick", "nether_bricks"}, {"red_nether_brick", "red_nether_bricks"},
                {"end_bricks", "end_stone_bricks"}, {"glass_pane_top", "glass_pane_top"}, {"piston_top_normal", "piston_top"}, {"piston_top_sticky", "piston_top_sticky"},
                {"furnace_front_off", "furnace_front"}, {"furnace_front_on", "furnace_front_on"}, {"melon_side", "melon_side"}, {"pumpkin_face_off", "carved_pumpkin"},
                {"pumpkin_face_on", "jack_o_lantern"}, {"noteblock", "note_block"}, {"portal", "nether_portal"}, {"wheat_stage_7", "wheat_stage7"},
                {"command_block_front", "command_block_front"}, {"gold_ore", "gold_ore"}, {"lapis_ore", "lapis_ore"}, {"cauldron_inner", "cauldron_inner"},
                {"snow", "snow"}, {"ice_packed", "packed_ice"}, {"slime", "slime_block"}, {"stone_slab_side", "smooth_stone_slab_side"},
                {"stone_slab_top", "smooth_stone"}, {"farmland_wet", "farmland_moist"}, {"farmland_dry", "farmland"}, {"grass_path_top", "dirt_path_top"},
                {"grass_path_side", "dirt_path_side"}, {"quartz_block_lines", "quartz_pillar"}, {"quartz_block_chiseled", "chiseled_quartz_block"},
                {"red_sandstone_normal", "red_sandstone"}, {"dirt_podzol_top", "podzol_top"}, {"dirt_podzol_side", "podzol_side"},
                {"coarse_dirt", "coarse_dirt"}, {"red_sand", "red_sand"}, {"sponge_wet", "wet_sponge"}, {"rail_golden", "powered_rail"},
                {"rail_golden_powered", "powered_rail_on"}, {"rail_detector", "detector_rail"}, {"rail_activator", "activator_rail"},
                {"rail_normal", "rail"}, {"rail_normal_turned", "rail_corner"}, {"torch_on", "torch"}, {"redstone_torch_on", "redstone_torch"},
                {"redstone_torch_off", "redstone_torch_off"}, {"ladder", "ladder"}, {"cactus_side", "cactus_side"}, {"clay", "clay"}};
        for (String[] p : pairs) if (!p[0].equals(p[1])) TEXTURE_RENAMES.put("block/" + p[0], "block/" + p[1]);
    }

    private static String vanillaTexture(String ref) {
        if (ref.startsWith("#")) return ref;
        int colon = ref.indexOf(':');
        String ns = colon < 0 ? "minecraft" : ref.substring(0, colon);
        if (!ns.equals("minecraft")) return ref;
        String path = colon < 0 ? ref : ref.substring(colon + 1);
        if (path.startsWith("blocks/")) path = "block/" + path.substring("blocks/".length());
        else if (path.startsWith("items/")) path = "item/" + path.substring("items/".length());
        String renamed = TEXTURE_RENAMES.get(path);
        if (renamed != null) path = renamed;
        return colon < 0 ? path : "minecraft:" + path;
    }

    private static String normalizeRef(String ref) {
        if (ref.startsWith("#")) return ref; // texture variable
        int colon = ref.indexOf(':');
        if (colon < 0) return normalizePath(ref);
        return normalizePath(ref.substring(0, colon)) + ":" + normalizePath(ref.substring(colon + 1));
    }
}

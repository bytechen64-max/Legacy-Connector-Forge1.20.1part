package org.kylepitcock.legacyconnector.loader.resource;

import com.google.gson.JsonParser;
import java.nio.charset.StandardCharsets;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class SrpResourceConversionTest {
    @Test void trapdoorsUseTheirOwnTexturesAndAllSixteenHatchStates() {
        for (String name : java.util.List.of("brusewood_trapdoor", "consumed_trapdoor")) {
            var converter = new LegacyResourceConverter();
            converter.accept("assets/srparasites/blockstates/" + name + ".json", bytes("{\"defaults\":{\"model\":\"srparasites:consumed_planks_stairs\"}}"));
            var output = converter.finish();
            var variants = JsonParser.parseString(new String(output.get("assets/srparasites/legacyconnector_blockstates/" + name + ".json"), StandardCharsets.UTF_8)).getAsJsonObject().getAsJsonObject("variants");
            assertEquals(16, variants.size());
            for (var entry : variants.entrySet()) {
                String model = entry.getValue().getAsJsonObject().get("model").getAsString();
                assertFalse(model.contains("stairs"));
                String suffix = entry.getKey().endsWith("open=true") ? "open" : entry.getKey().contains("half=top") ? "top" : "bottom";
                assertTrue(model.endsWith(name + "_" + suffix));
                var json = JsonParser.parseString(new String(output.get("assets/srparasites/models/block/" + name + "_" + suffix + ".json"), StandardCharsets.UTF_8)).getAsJsonObject();
                assertEquals("srparasites:blocks/" + name, json.getAsJsonObject("textures").get("texture").getAsString());
            }
        }
    }
    private static byte[] bytes(String text) { return text.getBytes(StandardCharsets.UTF_8); }

    @Test void repairsBrokenSrpStairAndObjMaterial() {
        var converter = new LegacyResourceConverter();
        String stair = "assets/srparasites/models/block/infestedstainstairs_outer.json";
        converter.accept(stair, bytes("{\"parent\":\"block/outer_stairs\",\"textures\":{\"top\": \"srparasites:blocks/infestedstain,\n\"side\":\"srparasites:blocks/infestedstain\"}}"));
        String material = "assets/srparasites/models/block/arraytowerlarge.mtl";
        converter.accept(material, bytes("newmtl example\nmap_Kd pasted.png\n"));
        var output = converter.finish();
        var model = JsonParser.parseString(new String(output.get(stair), StandardCharsets.UTF_8)).getAsJsonObject();
        assertEquals("srparasites:blocks/infestedstain", model.getAsJsonObject("textures").get("top").getAsString());
        assertTrue(new String(output.get(material), StandardCharsets.UTF_8).contains("map_Kd srparasites:blocks/arraytowertexture"));
    }

    @Test void stitchesExistingGuiTexturesUsedByModelsWithoutAddingWholeGuiDirectory() {
        var converter = new LegacyResourceConverter();
        converter.accept("assets/srparasites/models/item/icon.json", bytes("{\"parent\":\"item/generated\",\"textures\":{\"layer0\":\"srparasites:gui/potion_repel\",\"particle\":\"#layer0\",\"unused\":\"srparasites:gui/missing\"}}"));
        converter.accept("assets/srparasites/textures/gui/potion_repel.png", new byte[]{1});
        converter.accept("assets/srparasites/textures/gui/unrelated.png", new byte[]{2});
        var atlas = JsonParser.parseString(new String(converter.finish().get("assets/minecraft/atlases/blocks.json"), StandardCharsets.UTF_8)).getAsJsonObject();
        var sources = atlas.getAsJsonArray("sources");
        assertEquals(5, sources.size());
        assertEquals("srparasites:gui/potion_repel", sources.get(4).getAsJsonObject().get("resource").getAsString());
    }

    @Test void leavesOtherModsResourcesUntouched() {
        var converter = new LegacyResourceConverter();
        String path = "assets/other/models/block/arraytowerlarge.mtl";
        byte[] input = bytes("map_Kd pasted.png");
        converter.accept(path, input);
        assertArrayEquals(input, converter.finish().get(path));
    }
}

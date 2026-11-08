package org.kylepitcock.legacyconnector.v1_7_10.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import java.lang.reflect.Proxy;
import java.util.ArrayList;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class RenderContextVertexTest {
    @Test void guiSpritesWriteOnlyAttributesInTheirSelectedFormat() throws Exception {
        var emit = RenderContext.class.getDeclaredMethod("emitCorner", RenderContext.State.class, VertexConsumer.class,
                PoseStack.Pose.class, boolean.class, int.class, double[].class, float.class, float.class, float.class);
        emit.setAccessible(true);
        var calls = new ArrayList<String>();
        VertexConsumer consumer = (VertexConsumer) Proxy.newProxyInstance(VertexConsumer.class.getClassLoader(),
                new Class<?>[]{VertexConsumer.class}, (proxy, method, args) -> {
                    calls.add(method.getName());
                    return method.getReturnType() == void.class ? null : proxy;
                });
        var state = new RenderContext.State();
        state.texture2d = true;
        state.geometryFormat = com.mojang.blaze3d.vertex.DefaultVertexFormat.POSITION_TEX_COLOR;
        emit.invoke(null, state, consumer, new PoseStack().last(), true, 0,
                new double[]{0, 0, 0, 0, 0, 0xFFFFFFFFL, 0xF000F0, 1}, 0F, 1F, 0F);
        assertTrue(calls.contains("uv"));
        assertTrue(calls.indexOf("uv") < calls.indexOf("color"));
        assertFalse(calls.contains("overlayCoords"));
        assertFalse(calls.contains("uv2"));
        assertFalse(calls.contains("normal"));
        assertEquals("endVertex", calls.get(calls.size() - 1));
    }

    @Test void completesEveryCornerForTexturedAndUntexturedDraws() throws Exception {
        var emit = RenderContext.class.getDeclaredMethod("emitCorner", RenderContext.State.class, VertexConsumer.class,
                PoseStack.Pose.class, boolean.class, int.class, double[].class, float.class, float.class, float.class);
        emit.setAccessible(true);
        for (boolean textured : new boolean[]{true, false}) {
            var calls = new ArrayList<String>();
            VertexConsumer consumer = (VertexConsumer) Proxy.newProxyInstance(VertexConsumer.class.getClassLoader(),
                    new Class<?>[]{VertexConsumer.class}, (proxy, method, args) -> {
                        calls.add(method.getName());
                        return method.getReturnType() == void.class ? null : proxy;
                    });
            var state = new RenderContext.State();
            state.texture2d = textured;
            for (int i = 0; i < 4; i++) {
                int start = calls.size();
                emit.invoke(null, state, consumer, new PoseStack().last(), textured, 0,
                        new double[]{i, 0, 0, 0, 0, 0xFFFFFFFFL, 0xF000F0, 1}, 0F, 1F, 0F);
                assertEquals("vertex", calls.get(start));
                assertEquals("endVertex", calls.get(calls.size() - 1));
            }
            assertEquals(4, calls.stream().filter("endVertex"::equals).count());
            assertEquals(textured, calls.contains("uv"));
            assertEquals(textured, calls.contains("overlayCoords"));
        }
    }
}

"""1.20.1's VertexConsumer keeps the vertex/color/uv/overlayCoords/uv2/normal/endVertex names: add them next to the
1.21-style methods the shim's call sites already use (the class then satisfies the interface without touching them)."""
import sys

COMPAT = """
        // 1.20.1's VertexConsumer method names (1.21 renamed them); the 1.21-style ones above stay for the shim's own callers.
        @Override
        public com.mojang.blaze3d.vertex.VertexConsumer vertex(double x, double y, double z) {
            return addVertex((float) x, (float) y, (float) z);
        }

        @Override
        public com.mojang.blaze3d.vertex.VertexConsumer color(int red, int green, int blue, int alpha) {
            return setColor(red, green, blue, alpha);
        }

        @Override
        public com.mojang.blaze3d.vertex.VertexConsumer uv(float u, float v) {
            return setUv(u, v);
        }

        @Override
        public com.mojang.blaze3d.vertex.VertexConsumer overlayCoords(int u, int v) {
            return setUv1(u, v);
        }

        @Override
        public com.mojang.blaze3d.vertex.VertexConsumer uv2(int u, int v) {
            return setUv2(u, v);
        }

        @Override
        public com.mojang.blaze3d.vertex.VertexConsumer normal(float x, float y, float z) {
            return setNormal(x, y, z);
        }

        @Override
        public void endVertex() {}

        @Override
        public void defaultColor(int red, int green, int blue, int alpha) {}

        @Override
        public void unsetDefaultColor() {}
"""

P = r"src/main/java/legacyconnector/v1_12_2/net/minecraft/client/renderer/BlockFluidRenderer.java"
src = open(P, encoding="utf-8").read()
# insert the compatibility methods right before the class's closing brace of Consumer: after setNormal's body
anchor = """        @Override
        public com.mojang.blaze3d.vertex.VertexConsumer setNormal(float x, float y, float z) {"""
idx = src.find(anchor)
if idx < 0:
    print("ABORT: setNormal not found in", P)
    sys.exit(1)
# find the end of that method: the next "\n        }\n" after the anchor
end = src.find("\n        }\n", idx)
if end < 0:
    print("ABORT: setNormal body end not found")
    sys.exit(1)
src = src[:end + len("\n        }\n")] + COMPAT + src[end + len("\n        }\n"):]
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P)

# the discarding consumer in RenderContext: 1.20.1 asks for the older names
P = r"src/main/java/org/kylepitcock/legacyconnector/v1_7_10/client/RenderContext.java"
src = open(P, encoding="utf-8").read()
old = """        @Override
        public VertexConsumer setNormal(float x, float y, float z) {
            return this;
        }
    };"""
new = """        @Override
        public VertexConsumer setNormal(float x, float y, float z) {
            return this;
        }

        // 1.20.1's VertexConsumer method names
        @Override
        public VertexConsumer vertex(double x, double y, double z) {
            return this;
        }

        @Override
        public VertexConsumer color(int red, int green, int blue, int alpha) {
            return this;
        }

        @Override
        public VertexConsumer uv(float u, float v) {
            return this;
        }

        @Override
        public VertexConsumer overlayCoords(int u, int v) {
            return this;
        }

        @Override
        public VertexConsumer uv2(int u, int v) {
            return this;
        }

        @Override
        public VertexConsumer normal(float x, float y, float z) {
            return this;
        }

        @Override
        public void endVertex() {}

        @Override
        public void defaultColor(int red, int green, int blue, int alpha) {}

        @Override
        public void unsetDefaultColor() {}
    };"""
if src.count(old) != 1:
    print("ABORT RenderContext:", src.count(old))
    sys.exit(1)
open(P, "w", encoding="utf-8", newline="").write(src.replace(old, new))
print("patched", P)

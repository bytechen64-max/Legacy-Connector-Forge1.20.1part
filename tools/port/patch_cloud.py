"""AreaEffectCloud: the 1.20.5 potion_contents component -> the 1.20.1 potion + its (private) effect list."""
import io
import json
import sys

P = r"src/main/java/legacyconnector/v1_12_2/net/minecraft/entity/EntityAreaEffectCloud.java"
src = open(P, encoding="utf-8").read()

pairs = [
    # setPotion: the cloud holds the Potion itself on 1.20.1
    ("        if (c != null && modern != null) c.setPotionContents(new net.minecraft.world.item.alchemy.PotionContents(modern));",
     "        if (c != null) c.setPotion(modern == null ? null : modern.value());"),
    # read the cloud's own effects through the accessor instead of parsing the component back out of NBT
    ("""        java.util.List<PotionEffect> out = new java.util.ArrayList<>();
        var tag = new net.minecraft.nbt.CompoundTag();
        c.saveWithoutId(tag);
        var contents = net.minecraft.world.item.alchemy.PotionContents.CODEC.parse(net.minecraft.nbt.NbtOps.INSTANCE, tag.get("potion_contents")).result().orElse(null);
        if (contents != null) for (var m : contents.customEffects()) out.add(PotionEffect.mcc$fromModern(m));
        return out;""",
     """        java.util.List<PotionEffect> out = new java.util.ArrayList<>();
        for (var m : ((org.kylepitcock.legacyconnector.mixin.access.AreaEffectCloudAccess) c).legacyconnector$effects()) {
            out.add(PotionEffect.mcc$fromModern(m));
        }
        return out;"""),
    # write them back into that list
    ("""        var c = e.mcc$cloud();
        if (c == null) return;
        var tag = new net.minecraft.nbt.CompoundTag();
        c.saveWithoutId(tag);
        var contents = net.minecraft.world.item.alchemy.PotionContents.CODEC.parse(net.minecraft.nbt.NbtOps.INSTANCE, tag.get("potion_contents")).result()
                .orElse(net.minecraft.world.item.alchemy.PotionContents.EMPTY);
        java.util.List<net.minecraft.world.effect.MobEffectInstance> modern = new java.util.ArrayList<>();
        if (v != null) for (PotionEffect p : v) if (p != null && p.mcc$toModern() != null) modern.add(p.mcc$toModern());
        c.setPotionContents(new net.minecraft.world.item.alchemy.PotionContents(contents.potion(), contents.customColor(), modern));""",
     """        var c = e.mcc$cloud();
        if (c == null) return;
        var modern = ((org.kylepitcock.legacyconnector.mixin.access.AreaEffectCloudAccess) c).legacyconnector$effects();
        modern.clear();
        if (v != null) for (PotionEffect p : v) if (p != null && p.mcc$toModern() != null) modern.add(p.mcc$toModern());"""),
]
for old, new in pairs:
    if src.count(old) != 1:
        print("ABORT AreaEffectCloud:", src.count(old), old.splitlines()[0][:70])
        sys.exit(1)
    src = src.replace(old, new)
open(P, "w", encoding="utf-8", newline="").write(src)
print("patched", P)

# register the accessor
CFG = "src/main/resources/legacyconnector.mixins.json"
with io.open(CFG, "r", encoding="utf-8-sig") as f:
    cfg = json.load(f)
if "access.AreaEffectCloudAccess" not in cfg["mixins"]:
    cfg["mixins"].insert(0, "access.AreaEffectCloudAccess")
with io.open(CFG, "w", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(cfg, indent=2) + "\n")
assert not open(CFG, "rb").read().startswith(b"\xef\xbb\xbf")
print("registered access.AreaEffectCloudAccess")

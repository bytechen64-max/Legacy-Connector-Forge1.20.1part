"""1.20.1 NBT IO names and the audio stream class location."""
import os
import sys

EDITS = {
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/network/PacketBuffer.java": [
        ("                net.minecraft.nbt.NbtIo.writeAnyTag(tag.mcc$modern(), new ByteBufOutputStream(this));",
         "                // 1.20.2 renamed writeUnnamedTag/readUnnamedTag to writeAnyTag/readAnyTag.\n"
         "                net.minecraft.nbt.NbtIo.writeUnnamedTag(tag.mcc$modern(), new ByteBufOutputStream(this));"),
        ("            var tag = net.minecraft.nbt.NbtIo.readAnyTag(new ByteBufInputStream(this), net.minecraft.nbt.NbtAccounter.create(2097152L));",
         "            var tag = net.minecraft.nbt.NbtIo.read(new ByteBufInputStream(this), new net.minecraft.nbt.NbtAccounter(2097152L));"),
    ],
}

for path, pairs in EDITS.items():
    src = open(path, encoding="utf-8").read()
    for old, new in pairs:
        n = src.count(old)
        if n != 1:
            print(f"ABORT {n} matches in {path}: {old.strip()[:70]}")
            sys.exit(1)
        src = src.replace(old, new)
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

# the OGG stream lives in com.mojang.blaze3d.audio on 1.20.1
changed = 0
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        src = open(p, encoding="utf-8").read()
        if "JOrbisAudioStream" not in src:
            continue
        src = src.replace("import net.minecraft.client.sounds.JOrbisAudioStream;",
                          "import com.mojang.blaze3d.audio.OggAudioStream;")
        src = src.replace("new JOrbisAudioStream(", "new OggAudioStream(")
        src = src.replace("JOrbisAudioStream stream", "OggAudioStream stream")
        src = src.replace("JOrbisAudioStream", "OggAudioStream")
        open(p, "w", encoding="utf-8", newline="").write(src)
        changed += 1
        print("patched", p)
print("audio files:", changed)

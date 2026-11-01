"""The last two 1.20.5 scoreboard reads (ScoreHolder + ScoreAccess/getPlayerScoreInfo) -> 1.20.1 named-score API."""
import sys

EDITS = {
    r"src/main/java/legacyconnector/v1_12_2/net/minecraft/command/CommandResultStats.java": [
        (
            "scoreboard.getOrCreatePlayerScore(net.minecraft.world.scores.ScoreHolder.forNameOnly(entity), objective).set(p_184932_4_);",
            "scoreboard.getOrCreatePlayerScore(entity, objective).setScore(p_184932_4_);",
        ),
    ],
    r"src/main/java/legacyconnector/v1_7_10/net/minecraft/server/management/ServerConfigurationManager.java": [
        (
            "            var info = scoreboard.getPlayerScoreInfo(player, objective);\n"
            "            int score = info == null ? 0 : info.value();",
            "            var entry = scoreboard.getPlayerScores(player).get(objective);\n"
            "            int score = entry == null ? 0 : entry.getScore();",
        ),
    ],
}

for path, pairs in EDITS.items():
    src = open(path, encoding="utf-8").read()
    for old, new in pairs:
        if src.count(old) != 1:
            print("ABORT", src.count(old), path, old[:60])
            sys.exit(1)
        src = src.replace(old, new)
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("patched", path)

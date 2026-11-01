package legacyconnector.v1_12_2.net.minecraft.scoreboard;

/** One player's (or name's) score on one objective: a view over the modern scoreboard's entry. */
public class Score {
    private final net.minecraft.world.scores.Scoreboard scoreboard;
    private final ScoreObjective objective;
    private final String scorePlayerName;

    public Score(Scoreboard scoreboard, ScoreObjective objective, String playerName) {
        this.scoreboard = scoreboard.mcc$modern();
        this.objective = objective;
        this.scorePlayerName = playerName;
    }

    /** 1.20.1 keys scores by player name and creates the entry when it is missing. */
    private net.minecraft.world.scores.Score mcc$access() {
        return scoreboard.getOrCreatePlayerScore(scorePlayerName, objective.mcc$modern());
    }

    /** The existing entry, or null: looking a score up must not create one. */
    private net.minecraft.world.scores.Score mcc$existing() {
        return scoreboard.getPlayerScores(scorePlayerName).get(objective.mcc$modern());
    }

    public void increaseScore(int amount) {
        if (objective.getCriteria().isReadOnly()) throw new IllegalStateException("Cannot modify read-only score");
        mcc$access().add(amount);
    }

    public void decreaseScore(int amount) {
        if (objective.getCriteria().isReadOnly()) throw new IllegalStateException("Cannot modify read-only score");
        mcc$access().add(-amount);
    }

    public void incrementScore() {
        increaseScore(1);
    }

    public int getScorePoints() {
        var existing = mcc$existing();
        return existing == null ? 0 : existing.getScore();
    }

    public void setScorePoints(int points) {
        mcc$access().setScore(points);
    }

    public ScoreObjective getObjective() {
        return objective;
    }

    public String getPlayerName() {
        return scorePlayerName;
    }

    public Scoreboard getScoreScoreboard() {
        return Scoreboard.mcc$of(scoreboard);
    }

    public boolean isLocked() {
        var existing = mcc$existing();
        return existing != null && existing.isLocked();
    }

    public void setLocked(boolean locked) {
        mcc$access().setLocked(locked);
    }
}

package legacyconnector.v1_12_2.net.minecraft.scoreboard;

import java.util.ArrayList;
import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Objectives, scores and teams: a view over the modern scoreboard (the server's, which the modern game saves and syncs). A
 * scoreboard a mod builds itself ({@code new Scoreboard()}) is a detached modern one.
 *
 * <p>1.20.1 knows players by plain name and display slots by their legacy numbers ({@link net.minecraft.world.scores.Scoreboard#DISPLAY_SLOT_LIST}
 * and friends), so the 1.20.5 {@code ScoreHolder}/{@code DisplaySlot} layer this shim used to sit on is gone; the legacy
 * numbered slots are rebuilt from the modern constants.</p>
 */
public class Scoreboard {
    /** 1.12.2 named slots 3..17 {@code sidebar.team.<colour>}, in the order the modern scoreboard numbers them. */
    private static final String[] TEAM_COLOURS = {
        "black", "dark_green", "dark_aqua", "dark_red", "dark_purple", "gold", "gray", "dark_gray",
        "blue", "green", "aqua", "red", "light_purple", "yellow", "white"};

    private final net.minecraft.world.scores.Scoreboard scoreboard;

    public Scoreboard() {
        this(new net.minecraft.world.scores.Scoreboard());
    }

    public Scoreboard(net.minecraft.world.scores.Scoreboard scoreboard) {
        this.scoreboard = scoreboard;
    }

    public static Scoreboard mcc$of(net.minecraft.world.scores.Scoreboard scoreboard) {
        return scoreboard == null ? null : new Scoreboard(scoreboard);
    }

    public net.minecraft.world.scores.Scoreboard mcc$modern() {
        return scoreboard;
    }

    public ScoreObjective getObjective(String name) {
        return ScoreObjective.mcc$of(scoreboard.getObjective(name));
    }

    public ScoreObjective addScoreObjective(String name, IScoreCriteria criteria) {
        if (name.length() > 16) throw new IllegalArgumentException("The objective name '" + name + "' is too long!");
        if (scoreboard.getObjective(name) != null) throw new IllegalArgumentException("An objective with the name '" + name + "' already exists!");
        var modern = criteria == null ? net.minecraft.world.scores.criteria.ObjectiveCriteria.DUMMY : criteria.mcc$modern();
        return ScoreObjective.mcc$of(scoreboard.addObjective(name, modern, net.minecraft.network.chat.Component.literal(name),
                modern.getDefaultRenderType()));
    }

    public Collection<ScoreObjective> getObjectivesFromCriteria(IScoreCriteria criteria) {
        List<ScoreObjective> out = new ArrayList<>();
        if (criteria == null) return out;
        for (var o : scoreboard.getObjectives()) if (o.getCriteria().getName().equals(criteria.getName())) out.add(ScoreObjective.mcc$of(o));
        return out;
    }

    public boolean entityHasObjective(String name, ScoreObjective objective) {
        return objective != null && scoreboard.hasPlayerScore(name, objective.mcc$modern());
    }

    public Score getOrCreateScore(String username, ScoreObjective objective) {
        if (username.length() > 40) throw new IllegalArgumentException("The player name '" + username + "' is too long!");
        scoreboard.getOrCreatePlayerScore(username, objective.mcc$modern());
        return new Score(this, objective, username);
    }

    public Collection<Score> getSortedScores(ScoreObjective objective) {
        List<Score> out = new ArrayList<>();
        for (var entry : scoreboard.getPlayerScores(objective.mcc$modern())) out.add(new Score(this, objective, entry.getOwner()));
        out.sort((a, b) -> Integer.compare(a.getScorePoints(), b.getScorePoints()));
        return out;
    }

    public Collection<ScoreObjective> getScoreObjectives() {
        List<ScoreObjective> out = new ArrayList<>();
        for (var o : scoreboard.getObjectives()) out.add(ScoreObjective.mcc$of(o));
        return out;
    }

    public Collection<String> getObjectiveNames() {
        return new ArrayList<>(scoreboard.getTrackedPlayers());
    }

    public void removeObjectiveFromEntity(String name, ScoreObjective objective) {
        if (objective != null) {
            scoreboard.resetPlayerScore(name, objective.mcc$modern());
            return;
        }
        // every objective (1.20.1 has no "reset all of one player" call: the entry table is the only way in)
        for (var o : new ArrayList<>(scoreboard.getPlayerScores(name).keySet())) scoreboard.resetPlayerScore(name, o);
    }

    public Collection<Score> getScores() {
        List<Score> out = new ArrayList<>();
        for (var o : scoreboard.getObjectives()) {
            ScoreObjective objective = ScoreObjective.mcc$of(o);
            for (var entry : scoreboard.getPlayerScores(o)) out.add(new Score(this, objective, entry.getOwner()));
        }
        return out;
    }

    public Map<ScoreObjective, Score> getObjectivesForEntity(String name) {
        Map<ScoreObjective, Score> out = new LinkedHashMap<>();
        for (var e : scoreboard.getPlayerScores(name).keySet()) {
            ScoreObjective objective = ScoreObjective.mcc$of(e);
            out.put(objective, new Score(this, objective, name));
        }
        return out;
    }

    public void removeObjective(ScoreObjective objective) {
        if (objective != null) scoreboard.removeObjective(objective.mcc$modern());
    }

    /** Slot 0 is the player list, 1 the sidebar, 2 below names, 3-17 the team-coloured sidebars. */
    public void setObjectiveInDisplaySlot(int slot, ScoreObjective objective) {
        if (slot < 0 || slot >= net.minecraft.world.scores.Scoreboard.DISPLAY_SLOTS) return;
        scoreboard.setDisplayObjective(slot, objective == null ? null : objective.mcc$modern());
    }

    public ScoreObjective getObjectiveInDisplaySlot(int slot) {
        if (slot < 0 || slot >= net.minecraft.world.scores.Scoreboard.DISPLAY_SLOTS) return null;
        return ScoreObjective.mcc$of(scoreboard.getDisplayObjective(slot));
    }

    public ScorePlayerTeam getTeam(String teamName) {
        return ScorePlayerTeam.mcc$of(scoreboard.getPlayerTeam(teamName));
    }

    public ScorePlayerTeam createTeam(String name) {
        if (name.length() > 16) throw new IllegalArgumentException("The team name '" + name + "' is too long!");
        if (scoreboard.getPlayerTeam(name) != null) throw new IllegalArgumentException("A team with the name '" + name + "' already exists!");
        return ScorePlayerTeam.mcc$of(scoreboard.addPlayerTeam(name));
    }

    public void removeTeam(ScorePlayerTeam playerTeam) {
        if (playerTeam != null) scoreboard.removePlayerTeam(playerTeam.mcc$modern());
    }

    public boolean addPlayerToTeam(String player, String newTeam) {
        if (player.length() > 40) throw new IllegalArgumentException("The player name '" + player + "' is too long!");
        var team = scoreboard.getPlayerTeam(newTeam);
        return team != null && scoreboard.addPlayerToTeam(player, team);
    }

    public boolean removePlayerFromTeams(String playerName) {
        return scoreboard.removePlayerFromTeam(playerName);
    }

    public void removePlayerFromTeam(String username, ScorePlayerTeam playerTeam) {
        if (playerTeam == null) return;
        if (scoreboard.getPlayersTeam(username) != playerTeam.mcc$modern()) {
            throw new IllegalStateException("Player is either on another team or not on any team. Cannot remove from team '" + playerTeam.getName() + "'.");
        }
        scoreboard.removePlayerFromTeam(username, playerTeam.mcc$modern());
    }

    public Collection<String> getTeamNames() {
        return scoreboard.getTeamNames();
    }

    public Collection<ScorePlayerTeam> getTeams() {
        List<ScorePlayerTeam> out = new ArrayList<>();
        for (var t : scoreboard.getPlayerTeams()) out.add(ScorePlayerTeam.mcc$of(t));
        return out;
    }

    public ScorePlayerTeam getPlayersTeam(String username) {
        return ScorePlayerTeam.mcc$of(scoreboard.getPlayersTeam(username));
    }

    /** The legacy name of a numbered display slot ({@code list}, {@code sidebar}, {@code belowName}, {@code sidebar.team.<colour>}). */
    public static String getObjectiveDisplaySlot(int id) {
        if (id < 0 || id >= net.minecraft.world.scores.Scoreboard.DISPLAY_SLOTS) return null;
        return switch (id) {
            case net.minecraft.world.scores.Scoreboard.DISPLAY_SLOT_LIST -> "list";
            case net.minecraft.world.scores.Scoreboard.DISPLAY_SLOT_SIDEBAR -> "sidebar";
            case net.minecraft.world.scores.Scoreboard.DISPLAY_SLOT_BELOW_NAME -> "belowName";
            default -> "sidebar.team." + TEAM_COLOURS[id - net.minecraft.world.scores.Scoreboard.DISPLAY_SLOT_TEAMS_SIDEBAR_START];
        };
    }

    public static int getObjectiveDisplaySlotNumber(String name) {
        if (name == null) return -1;
        return switch (name) {
            case "list" -> net.minecraft.world.scores.Scoreboard.DISPLAY_SLOT_LIST;
            case "sidebar" -> net.minecraft.world.scores.Scoreboard.DISPLAY_SLOT_SIDEBAR;
            case "belowName" -> net.minecraft.world.scores.Scoreboard.DISPLAY_SLOT_BELOW_NAME;
            default -> {
                if (!name.startsWith("sidebar.team.")) yield -1;
                String colour = name.substring("sidebar.team.".length());
                int index = List.of(TEAM_COLOURS).indexOf(colour);
                yield index < 0 ? -1 : net.minecraft.world.scores.Scoreboard.DISPLAY_SLOT_TEAMS_SIDEBAR_START + index;
            }
        };
    }

    public static String[] getDisplaySlotStrings() {
        String[] out = new String[net.minecraft.world.scores.Scoreboard.DISPLAY_SLOTS];
        for (int i = 0; i < out.length; i++) out[i] = getObjectiveDisplaySlot(i);
        return out;
    }

    public void removeEntity(legacyconnector.v1_12_2.net.minecraft.entity.Entity entityIn) {
        if (entityIn != null && entityIn.mcc$modern() != null) scoreboard.entityRemoved(entityIn.mcc$modern());
    }
}

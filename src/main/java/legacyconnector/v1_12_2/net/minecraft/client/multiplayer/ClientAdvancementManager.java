package legacyconnector.v1_12_2.net.minecraft.client.multiplayer;

import java.util.HashMap;
import java.util.Map;
import legacyconnector.v1_12_2.net.minecraft.advancements.Advancement;
import legacyconnector.v1_12_2.net.minecraft.advancements.AdvancementList;
import legacyconnector.v1_12_2.net.minecraft.advancements.AdvancementProgress;

/** The client's copy of the advancements ({@code connection.getAdvancements()}): a view of the game's client advancements. */
public class ClientAdvancementManager {
    /** Phantom: each advancement's progress (a snapshot of the game's). */
    @Deprecated
    public Map<Advancement, AdvancementProgress> advancementToProgress;

    public ClientAdvancementManager(legacyconnector.v1_12_2.net.minecraft.client.Minecraft mc) {
    }

    private static net.minecraft.client.multiplayer.ClientAdvancements modern() {
        var connection = net.minecraft.client.Minecraft.getInstance().getConnection();
        return connection == null ? null : connection.getAdvancements();
    }

    @SuppressWarnings("unchecked")
    public static Map<Advancement, AdvancementProgress> mcc$get$advancementToProgress(ClientAdvancementManager m) {
        Map<Advancement, AdvancementProgress> out = new HashMap<>();
        var modern = modern();
        if (modern == null) return out;
        try {
            var f = net.minecraft.client.multiplayer.ClientAdvancements.class.getDeclaredField("progress");
            f.setAccessible(true);
            // 1.20.1 keys the client's progress by the advancement itself (1.20.2+ uses AdvancementHolder).
            var map = (Map<net.minecraft.advancements.Advancement, net.minecraft.advancements.AdvancementProgress>) f.get(modern);
            map.forEach((a, p) -> out.put(Advancement.mcc$of(a), new AdvancementProgress(p)));
        } catch (ReflectiveOperationException | RuntimeException e) {
            // no progress known
        }
        return out;
    }

    public AdvancementList getAdvancementList() {
        var modern = modern();
        return modern == null ? new AdvancementList() : AdvancementList.mcc$of(modern.getAdvancements());
    }

    /** Opens a tab of the advancements screen (and tells the server when asked). */
    public void setSelectedTab(Advancement advancement, boolean tellServer) {
        var modern = modern();
        if (modern != null) modern.setSelectedTab(advancement == null ? null : advancement.mcc$modern(), tellServer);
    }

    public void setListener(IListener listener) {
        var modern = modern();
        if (modern == null) return;
        if (listener == null) {
            modern.setListener(null);
            return;
        }
        var tree = AdvancementList.mcc$listener(listener);
        modern.setListener(new net.minecraft.client.multiplayer.ClientAdvancements.Listener() {
            @Override
            public void onUpdateAdvancementProgress(net.minecraft.advancements.Advancement advancement,
                    net.minecraft.advancements.AdvancementProgress progress) {
                listener.onUpdateAdvancementProgress(Advancement.mcc$of(advancement), new AdvancementProgress(progress));
            }

            @Override
            public void onSelectedTabChanged(net.minecraft.advancements.Advancement advancement) {
                listener.setSelectedTab(advancement == null ? null : Advancement.mcc$of(advancement));
            }

            @Override
            public void onAddAdvancementRoot(net.minecraft.advancements.Advancement advancement) {
                tree.onAddAdvancementRoot(advancement);
            }

            @Override
            public void onRemoveAdvancementRoot(net.minecraft.advancements.Advancement advancement) {
                tree.onRemoveAdvancementRoot(advancement);
            }

            @Override
            public void onAddAdvancementTask(net.minecraft.advancements.Advancement advancement) {
                tree.onAddAdvancementTask(advancement);
            }

            @Override
            public void onRemoveAdvancementTask(net.minecraft.advancements.Advancement advancement) {
                tree.onRemoveAdvancementTask(advancement);
            }

            @Override
            public void onAdvancementsCleared() {
                tree.onAdvancementsCleared();
            }
        });
    }

    public interface IListener extends AdvancementList.Listener {
        void onUpdateAdvancementProgress(Advancement advancement, AdvancementProgress progress);

        void setSelectedTab(Advancement advancement);
    }
}

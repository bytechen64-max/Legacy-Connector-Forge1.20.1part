package legacyconnector.v1_12_2.net.minecraft.advancements;

import java.util.ArrayList;
import java.util.List;
import legacyconnector.v1_12_2.net.minecraft.util.ResourceLocation;

/**
 * A tree of advancements: on the client, a view of the game's client advancement tree
 * ({@code connection.getAdvancements()}).
 *
 * <p>1.20.1 still ships {@code net.minecraft.advancements.AdvancementList} (1.20.2 replaced it with
 * {@code AdvancementTree}/{@code AdvancementNode}), so this is a thin view over it.</p>
 */
public class AdvancementList {
    private final net.minecraft.advancements.AdvancementList list;

    public AdvancementList() {
        this(new net.minecraft.advancements.AdvancementList());
    }

    public AdvancementList(net.minecraft.advancements.AdvancementList list) {
        this.list = list;
    }

    public static AdvancementList mcc$of(net.minecraft.advancements.AdvancementList list) {
        return list == null ? null : new AdvancementList(list);
    }

    public net.minecraft.advancements.AdvancementList mcc$modern() {
        return list;
    }

    public Iterable<Advancement> getRoots() {
        List<Advancement> out = new ArrayList<>();
        for (var advancement : list.getRoots()) out.add(Advancement.mcc$of(advancement));
        return out;
    }

    public Iterable<Advancement> getAdvancements() {
        List<Advancement> out = new ArrayList<>();
        for (var advancement : list.getAllAdvancements()) out.add(Advancement.mcc$of(advancement));
        return out;
    }

    public Advancement getAdvancement(ResourceLocation id) {
        return id == null ? null : Advancement.mcc$of(list.get(id.mcc$modern()));
    }

    public void clear() {
        list.clear();
    }

    public void setListener(Listener listener) {
        list.setListener(listener == null ? null : mcc$listener(listener));
    }

    /** A legacy listener as the game's tree listener (not a 1.12 method). */
    public static net.minecraft.advancements.AdvancementList.Listener mcc$listener(Listener l) {
        return new net.minecraft.advancements.AdvancementList.Listener() {
            @Override
            public void onAddAdvancementRoot(net.minecraft.advancements.Advancement advancement) {
                l.rootAdvancementAdded(Advancement.mcc$of(advancement));
            }

            @Override
            public void onRemoveAdvancementRoot(net.minecraft.advancements.Advancement advancement) {
                l.rootAdvancementRemoved(Advancement.mcc$of(advancement));
            }

            @Override
            public void onAddAdvancementTask(net.minecraft.advancements.Advancement advancement) {
                l.nonRootAdvancementAdded(Advancement.mcc$of(advancement));
            }

            @Override
            public void onRemoveAdvancementTask(net.minecraft.advancements.Advancement advancement) {
                l.nonRootAdvancementRemoved(Advancement.mcc$of(advancement));
            }

            @Override
            public void onAdvancementsCleared() {
                l.advancementsCleared();
            }
        };
    }

    public interface Listener {
        void rootAdvancementAdded(Advancement advancement);

        void rootAdvancementRemoved(Advancement advancement);

        void nonRootAdvancementAdded(Advancement advancement);

        void nonRootAdvancementRemoved(Advancement advancement);

        void advancementsCleared();
    }
}

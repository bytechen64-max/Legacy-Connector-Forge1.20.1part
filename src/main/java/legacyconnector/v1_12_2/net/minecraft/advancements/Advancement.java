package legacyconnector.v1_12_2.net.minecraft.advancements;

import legacyconnector.v1_12_2.net.minecraft.util.ResourceLocation;

/**
 * An advancement: a view over the modern one the server loaded.
 *
 * <p>1.20.1 still has the pre-1.20.2 advancement model (an {@link net.minecraft.advancements.Advancement} names its parent
 * directly and the registry keys them by id), so this is a straight view instead of the 1.21
 * {@code AdvancementHolder}/{@code AdvancementNode} indirection.</p>
 */
public class Advancement {
    private final net.minecraft.advancements.Advancement advancement;

    public Advancement(net.minecraft.advancements.Advancement advancement) {
        this.advancement = advancement;
    }

    public static Advancement mcc$of(net.minecraft.advancements.Advancement advancement) {
        return advancement == null ? null : new Advancement(advancement);
    }

    public net.minecraft.advancements.Advancement mcc$modern() {
        return advancement;
    }

    public ResourceLocation getId() {
        var id = advancement.getId();
        return new ResourceLocation(id.getNamespace(), id.getPath());
    }

    public Advancement getParent() {
        return mcc$of(advancement.getParent());
    }

    /** The criteria by name (each names its modern trigger). */
    public java.util.Map<String, Criterion> getCriteria() {
        java.util.Map<String, Criterion> out = new java.util.LinkedHashMap<>();
        advancement.getCriteria().forEach((name, c) -> out.put(name, Criterion.mcc$of(c)));
        return out;
    }

    public AdvancementRewards getRewards() {
        return new AdvancementRewards(advancement.getRewards());
    }

    public int getRequirementCount() {
        return advancement.getRequirements().length;
    }

    public legacyconnector.v1_12_2.net.minecraft.util.text.ITextComponent getDisplayText() {
        return new legacyconnector.v1_12_2.net.minecraft.util.text.TextComponentString(advancement.getChatComponent().getString());
    }

    /** How it shows in the advancements screen (null for a hidden-root or recipe advancement without display). */
    public DisplayInfo getDisplay() {
        return DisplayInfo.mcc$of(advancement.getDisplay());
    }

    @Override
    public boolean equals(Object o) {
        return o instanceof Advancement a && a.advancement.getId().equals(advancement.getId());
    }

    @Override
    public int hashCode() {
        return advancement.getId().hashCode();
    }

    @Override
    public String toString() {
        return "SimpleAdvancement{id=" + getId() + '}';
    }
}

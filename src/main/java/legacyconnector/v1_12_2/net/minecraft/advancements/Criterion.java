package legacyconnector.v1_12_2.net.minecraft.advancements;

/**
 * One criterion of an advancement: its trigger's instance. For a modern advancement's criterion ({@link #mcc$of}) the instance names the
 * modern trigger (its conditions stay the modern game's).
 */
public class Criterion {
    private final ICriterionInstance criterionInstance;

    public Criterion(ICriterionInstance criterionInstance) {
        this.criterionInstance = criterionInstance;
    }

    public Criterion() {
        this.criterionInstance = null;
    }

    /**
     * 1.20.1's {@code Criterion} only exposes its trigger <em>instance</em> (1.20.5 added {@code trigger()}), so the trigger type is
     * named after that instance's class: {@code InventoryChangeTrigger$TriggerInstance} becomes {@code minecraft:inventory_changed}.
     * The name is checked against the trigger registry and reported as {@code minecraft:impossible} when nothing matches.
     */
    public static Criterion mcc$of(net.minecraft.advancements.Criterion modern) {
        if (modern == null) return new Criterion();
        return new Criterion(new legacyconnector.v1_12_2.net.minecraft.advancements.critereon.AbstractCriterionInstance(triggerId(modern)));
    }

    private static legacyconnector.v1_12_2.net.minecraft.util.ResourceLocation triggerId(net.minecraft.advancements.Criterion modern) {
        var instance = modern.getTrigger();
        String simple = instance == null ? "" : instance.getClass().getSimpleName();
        int nested = simple.indexOf('$');
        if (nested > 0) simple = simple.substring(0, nested);
        if (simple.endsWith("Trigger")) simple = simple.substring(0, simple.length() - "Trigger".length());
        String path = simple.replaceAll("([a-z0-9])([A-Z])", "$1_$2").toLowerCase(java.util.Locale.ROOT);
        if (!path.isEmpty()) {
            var id = new net.minecraft.resources.ResourceLocation(path);
            // 1.20.1 keeps no trigger registry (the criteria are static fields on CriteriaTriggers): the derived id stands
            return new legacyconnector.v1_12_2.net.minecraft.util.ResourceLocation(id.getNamespace(), id.getPath());
        }
        return new legacyconnector.v1_12_2.net.minecraft.util.ResourceLocation("impossible");
    }

    public ICriterionInstance getCriterionInstance() {
        return criterionInstance;
    }
}

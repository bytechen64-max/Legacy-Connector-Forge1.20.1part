package legacyconnector.v1_7_10.net.minecraft.entity.ai;

import legacyconnector.v1_7_10.net.minecraft.entity.EntityCreature;
import legacyconnector.v1_7_10.net.minecraft.item.Item;
import legacyconnector.v1_7_10.net.minecraft.item.ItemStack;
import net.minecraft.world.entity.ai.goal.TemptGoal;

public class EntityAITempt extends GoalTask {
    public EntityAITempt(EntityCreature entity, double speed, Item item, boolean scaredByPlayerMovement) {
        // 1.20.1's TemptGoal takes an Ingredient (the predicate form is 1.20.5+)
        super(entity, 3, m -> new TemptGoal(m, speed, net.minecraft.world.item.crafting.Ingredient.of(
                item == null ? new net.minecraft.world.item.ItemStack[0]
                        : new net.minecraft.world.item.ItemStack[] {new net.minecraft.world.item.ItemStack(
                                org.kylepitcock.legacyconnector.v1_7_10.bridge.ItemBridge.modern(item))}),
                scaredByPlayerMovement));
    }
}

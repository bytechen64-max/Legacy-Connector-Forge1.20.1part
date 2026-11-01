package legacyconnector.v1_12_2.net.minecraftforge.common.brewing;

import legacyconnector.v1_12_2.net.minecraft.item.ItemStack;
import org.kylepitcock.legacyconnector.v1_12_2.bridge.Stacks1122;

/**
 * Vanilla's brewing (potion mixes and container changes), asked through the running game's own brewing table.
 *
 * <p>1.20.1 keeps that table as static arrays of {@code PotionBrewing} (the 1.21 builder and its server-owned instance do not
 * exist yet): {@code hasMix(input, ingredient)} and {@code mix(ingredient, input)} answer the two questions this recipe needs.</p>
 */
public class VanillaBrewingRecipe implements IBrewingRecipe {
    /** The items 1.12.2 treated as potion containers (the modern table's own container predicate is not reachable). */
    private static boolean isContainer(net.minecraft.world.item.Item item) {
        return item == net.minecraft.world.item.Items.POTION || item == net.minecraft.world.item.Items.SPLASH_POTION
                || item == net.minecraft.world.item.Items.LINGERING_POTION || item == net.minecraft.world.item.Items.GLASS_BOTTLE;
    }

    @Override
    public boolean isInput(ItemStack stack) {
        try {
            return !stack.isEmpty() && isContainer(Stacks1122.toModern(stack).getItem());
        } catch (RuntimeException | LinkageError e) {
            return false;
        }
    }

    @Override
    public boolean isIngredient(ItemStack stack) {
        try {
            return !stack.isEmpty() && net.minecraft.world.item.alchemy.PotionBrewing.isIngredient(Stacks1122.toModern(stack));
        } catch (RuntimeException | LinkageError e) {
            return false;
        }
    }

    @Override
    public ItemStack getOutput(ItemStack input, ItemStack ingredient) {
        try {
            if (input.isEmpty() || ingredient.isEmpty()) return ItemStack.EMPTY;
            var modernInput = Stacks1122.toModern(input);
            var modernIngredient = Stacks1122.toModern(ingredient);
            if (!net.minecraft.world.item.alchemy.PotionBrewing.hasMix(modernInput, modernIngredient)) return ItemStack.EMPTY;
            return Stacks1122.fromModern(net.minecraft.world.item.alchemy.PotionBrewing.mix(modernIngredient, modernInput));
        } catch (RuntimeException | LinkageError e) {
            return ItemStack.EMPTY;
        }
    }
}

package org.kylepitcock.legacyconnector.v1_7_10.adapter;

import com.google.gson.JsonObject;
import java.util.concurrent.atomic.AtomicInteger;
import legacyconnector.v1_7_10.net.minecraft.inventory.InventoryCrafting;
import legacyconnector.v1_7_10.net.minecraft.item.crafting.IRecipe;
import legacyconnector.v1_7_10.net.minecraft.world.World;
import net.minecraft.core.NonNullList;
import net.minecraft.core.RegistryAccess;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.CraftingContainer;
import net.minecraft.world.inventory.TransientCraftingContainer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.CraftingRecipe;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.level.Level;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;
import org.kylepitcock.legacyconnector.v1_7_10.bridge.RecipeBridge;

/**
 * A crafting recipe that is a custom legacy {@link IRecipe} (IC2's AdvRecipe, AE2's recipes, Blood Orb recipes, ...): the
 * data pack only names it by index, matching and the result come from the legacy object, which sees a view of the grid.
 *
 * <p>1.20.1 recipes take a {@code CraftingContainer} and are (de)serialized by {@code fromJson}/{@code fromNetwork}/
 * {@code toNetwork}: {@code CraftingInput}, {@code MapCodec}/{@code StreamCodec} serializers and the crafting book category
 * all arrived with 1.20.2.</p>
 */
public final class LegacyCraftingRecipe implements CraftingRecipe {
    /** 1.20.1 asks a recipe for its crafting-book category (the field is 1.20.2+). */
    @Override
    public net.minecraft.world.item.crafting.CraftingBookCategory category() {
        return net.minecraft.world.item.crafting.CraftingBookCategory.MISC;
    }
    public static final DeferredRegister<RecipeSerializer<?>> REGISTER = DeferredRegister.create(Registries.RECIPE_SERIALIZER, "legacyconnector");
    public static final RegistryObject<RecipeSerializer<LegacyCraftingRecipe>> SERIALIZER = REGISTER.register("legacy_recipe", Serializer::new);
    private static final AtomicInteger FAILURES = new AtomicInteger();
    /** Recipes are only ever looked up by their datapack id; a custom legacy recipe is not a datapack entry of its own. */
    private static final ResourceLocation ID = new ResourceLocation("legacyconnector", "legacy_recipe");
    /** The menu a transient grid needs; nothing is ever moved through it. */
    private static final AbstractContainerMenu MENU = new AbstractContainerMenu(null, 0) {
        @Override
        public ItemStack quickMoveStack(Player player, int slot) {
            return ItemStack.EMPTY;
        }

        @Override
        public boolean stillValid(Player player) {
            return true;
        }
    };

    private final int index;

    public LegacyCraftingRecipe(int index) {
        this.index = index;
    }

    private IRecipe legacy() {
        return RecipeBridge.custom(index);
    }

    private static InventoryCrafting view(CraftingContainer container) {
        NonNullList<ItemStack> items = NonNullList.withSize(container.getContainerSize(), ItemStack.EMPTY);
        for (int i = 0; i < items.size(); i++) items.set(i, container.getItem(i));
        return new InventoryCrafting(new TransientCraftingContainer(MENU, container.getWidth(), container.getHeight(), items));
    }

    private static void failed(Throwable e) {
        if (FAILURES.incrementAndGet() <= 5) org.slf4j.LoggerFactory.getLogger("LegacyConnector/Recipes").warn("A custom legacy recipe failed: {}", e.toString());
    }

    @Override
    public boolean matches(CraftingContainer container, Level level) {
        IRecipe r = legacy();
        if (r == null) return false;
        try {
            return r.matches(view(container), World.mcc$wrap(level));
        } catch (RuntimeException | LinkageError e) {
            failed(e);
            return false;
        }
    }

    @Override
    public ItemStack assemble(CraftingContainer container, RegistryAccess registries) {
        IRecipe r = legacy();
        if (r == null) return ItemStack.EMPTY;
        try {
            var out = r.getCraftingResult(view(container));
            return out == null ? ItemStack.EMPTY : legacyconnector.v1_7_10.net.minecraft.item.ItemStack.mcc$toModern(out);
        } catch (RuntimeException | LinkageError e) {
            failed(e);
            return ItemStack.EMPTY;
        }
    }

    @Override
    public boolean canCraftInDimensions(int width, int height) {
        return true;
    }

    @Override
    public ItemStack getResultItem(RegistryAccess registries) {
        IRecipe r = legacy();
        try {
            var out = r == null ? null : r.getRecipeOutput();
            return out == null ? ItemStack.EMPTY : legacyconnector.v1_7_10.net.minecraft.item.ItemStack.mcc$toModern(out);
        } catch (RuntimeException | LinkageError e) {
            failed(e);
            return ItemStack.EMPTY;
        }
    }

    @Override
    public boolean isSpecial() {
        return true; // no ingredients to list: keep it out of the recipe book
    }

    @Override
    public ResourceLocation getId() {
        return ID;
    }

    @Override
    public RecipeSerializer<?> getSerializer() {
        return SERIALIZER.get();
    }

    private static final class Serializer implements RecipeSerializer<LegacyCraftingRecipe> {
        @Override
        public LegacyCraftingRecipe fromJson(ResourceLocation id, JsonObject json) {
            return new LegacyCraftingRecipe(json.has("index") ? json.get("index").getAsInt() : -1);
        }

        @Override
        public LegacyCraftingRecipe fromNetwork(ResourceLocation id, FriendlyByteBuf buf) {
            return new LegacyCraftingRecipe(buf.readVarInt());
        }

        @Override
        public void toNetwork(FriendlyByteBuf buf, LegacyCraftingRecipe recipe) {
            buf.writeVarInt(recipe.index);
        }
    }
}

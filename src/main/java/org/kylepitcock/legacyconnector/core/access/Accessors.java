package org.kylepitcock.legacyconnector.core.access;

import org.kylepitcock.legacyconnector.mixin.access.AbstractArrowAccess;
import org.kylepitcock.legacyconnector.mixin.access.AbstractHorseAccess;
import org.kylepitcock.legacyconnector.mixin.access.ExplosionAccess;
import org.kylepitcock.legacyconnector.mixin.access.LivingEntityAccess;
import org.kylepitcock.legacyconnector.mixin.access.RenderTypeAccess;

import java.util.Map;
import net.minecraft.core.dispenser.DispenseItemBehavior;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.animal.horse.AbstractHorse;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Explosion;
import net.minecraft.world.level.block.DispenserBlock;
import net.minecraft.world.SimpleContainer;
import net.minecraft.client.renderer.RenderType;

/**
 * Calls the accessor mixins.

 * <p>This class must NOT live in the mixin package: Mixin refuses to load a class of a declared mixin package outside of a
 * mixin transformation ("<code>... is in a defined mixin package ... and cannot be referenced directly</code>"), and every
 * runtime caller of an accessor would crash the game the first time it rendered.
 *
 * <p>A mixin interface that declares a concrete (static) method is prepared as an interface mixin, which requires an interface
 * target, so the mixins here are abstract-only and these helpers hold the casts. One call site fewer than casting everywhere, and
 * the {@code legacyconnector$} names stay out of the shims.</p>
 */
public final class Accessors {
    private Accessors() {}

    public static ItemStack pickupItem(AbstractArrow arrow) {
        return ((AbstractArrowAccess) arrow).legacyconnector$pickupItem();
    }

    public static SimpleContainer horseInventory(AbstractHorse horse) {
        return ((AbstractHorseAccess) horse).legacyconnector$inventory();
    }

    public static float explosionRadius(Explosion explosion) {
        return ((ExplosionAccess) explosion).legacyconnector$radius();
    }

    public static void jumpFromGround(LivingEntity entity) {
        ((LivingEntityAccess) entity).legacyconnector$jumpFromGround();
    }

    public static boolean sortOnUpload(RenderType type) {
        return ((RenderTypeAccess) type).legacyconnector$sortOnUpload();
    }

    /** The behaviour a vanilla item dispenses with: 1.20.1 keeps the table private (1.20.5 added a getter). */
    @SuppressWarnings("unchecked")
    public static Map<Item, DispenseItemBehavior> dispenserRegistry() {
        try {
            var field = org.kylepitcock.legacyconnector.core.Mirror.field(DispenserBlock.class, "DISPENSER_REGISTRY");
            field.setAccessible(true);
            return (Map<Item, DispenseItemBehavior>) field.get(null);
        } catch (ReflectiveOperationException | ClassCastException e) {
            return Map.of();
        }
    }
}

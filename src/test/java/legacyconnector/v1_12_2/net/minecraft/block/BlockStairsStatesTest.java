package legacyconnector.v1_12_2.net.minecraft.block;

import legacyconnector.v1_12_2.net.minecraft.block.material.Material;
import legacyconnector.v1_12_2.net.minecraft.util.EnumFacing;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class BlockStairsStatesTest {
    /** The state codec needs no sound registry or Forge networking; construct that fixture without booting the game. */
    private static BlockStairs stairs() throws Exception {
        var field = sun.misc.Unsafe.class.getDeclaredField("theUnsafe");
        field.setAccessible(true);
        var unsafe = (sun.misc.Unsafe) field.get(null);
        var stairs = (BlockStairs) unsafe.allocateInstance(BlockStairs.class);
        stairs.blockState = stairs.createBlockState();
        stairs.setDefaultState(stairs.blockState.getBaseState().withProperty(BlockStairs.FACING, EnumFacing.NORTH)
                .withProperty(BlockStairs.HALF, BlockStairs.EnumHalf.BOTTOM).withProperty(BlockStairs.SHAPE, BlockStairs.EnumShape.STRAIGHT));
        return stairs;
    }
    @Test void retainsEveryFacingAndHalfAcrossMetadataConversion() throws Exception {
        var stairs = stairs();
        for (int meta = 0; meta < 8; meta++) {
            var state = stairs.getStateFromMeta(meta);
            assertEquals(meta, stairs.getMetaFromState(state));
            assertEquals((meta & 4) != 0 ? BlockStairs.EnumHalf.TOP : BlockStairs.EnumHalf.BOTTOM, state.getValue(BlockStairs.HALF));
        }
        assertEquals(4, java.util.stream.IntStream.range(0, 4).mapToObj(i -> stairs.getStateFromMeta(i).getValue(BlockStairs.FACING)).distinct().count());
    }
    @Test void clickedHalfSelectsUpperOrLowerPlacement() throws Exception {
        var stairs = stairs();
        assertEquals(BlockStairs.EnumHalf.TOP, stairs.getStateForPlacement(null, null, EnumFacing.DOWN, 0, 0, 0, 0, null).getValue(BlockStairs.HALF));
        assertEquals(BlockStairs.EnumHalf.BOTTOM, stairs.getStateForPlacement(null, null, EnumFacing.UP, 0, 1, 0, 0, null).getValue(BlockStairs.HALF));
        assertEquals(BlockStairs.EnumHalf.TOP, stairs.getStateForPlacement(null, null, EnumFacing.NORTH, 0, .75F, 0, 0, null).getValue(BlockStairs.HALF));
    }

    @Test void everyStairShapeLeavesNeighbourFacesVisible() throws Exception {
        var stairs = stairs();
        for (int meta = 0; meta < 8; meta++) {
            for (var shape : BlockStairs.EnumShape.values()) {
                var state = stairs.getStateFromMeta(meta).withProperty(BlockStairs.SHAPE, shape);
                assertFalse(state.isOpaqueCube(), "opaque stair: " + state);
                assertFalse(state.isFullCube(), "full stair: " + state);
            }
        }
    }
}

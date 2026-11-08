package org.kylepitcock.legacyconnector.v1_12_2.adapter;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import org.kylepitcock.legacyconnector.v1_12_2.bridge.WorldBridge1122;

/** Neighbour connections are actual-state properties in 1.12, independent of the saved metadata. */
public final class Legacy1122FenceBlock extends Legacy1122Block {
    public Legacy1122FenceBlock(legacyconnector.v1_12_2.net.minecraft.block.BlockFence block, Properties properties) {
        super(block, properties);
        registerDefaultState(defaultBlockState().setValue(BlockStateProperties.NORTH, false).setValue(BlockStateProperties.EAST, false)
                .setValue(BlockStateProperties.SOUTH, false).setValue(BlockStateProperties.WEST, false));
    }
    @Override protected void createBlockStateDefinition(StateDefinition.Builder<net.minecraft.world.level.block.Block, BlockState> builder) {
        super.createBlockStateDefinition(builder);
        builder.add(BlockStateProperties.NORTH, BlockStateProperties.EAST, BlockStateProperties.SOUTH, BlockStateProperties.WEST);
    }
    private BlockState connections(BlockState state, net.minecraft.world.level.BlockGetter level, BlockPos pos) {
        var fence = (legacyconnector.v1_12_2.net.minecraft.block.BlockFence) legacy();
        var access = WorldBridge1122.access(level);
        var properties = java.util.List.of(BlockStateProperties.NORTH, BlockStateProperties.EAST, BlockStateProperties.SOUTH, BlockStateProperties.WEST);
        var directions = new Direction[]{Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST};
        for (int i = 0; i < directions.length; i++) {
            Direction direction = directions[i];
            boolean connected = fence.canConnectTo(access, legacyconnector.v1_12_2.net.minecraft.util.math.BlockPos.mcc$of(pos.relative(direction)),
                    legacyconnector.v1_12_2.net.minecraft.util.EnumFacing.mcc$of(direction.getOpposite()));
            state = state.setValue(properties.get(i), connected);
        }
        return state;
    }
    @Override public BlockState getStateForPlacement(net.minecraft.world.item.context.BlockPlaceContext context) {
        return connections(defaultBlockState(), context.getLevel(), context.getClickedPos());
    }
    @Override public BlockState updateShape(BlockState state, Direction direction, BlockState adjacent, LevelAccessor level, BlockPos pos, BlockPos adjacentPos) {
        return connections(state, level, pos);
    }
}

package legacyconnector.v1_12_2.net.minecraft.block;

import legacyconnector.v1_12_2.net.minecraft.block.properties.PropertyEnum;
import legacyconnector.v1_12_2.net.minecraft.block.state.BlockStateContainer;
import legacyconnector.v1_12_2.net.minecraft.block.state.IBlockState;
import legacyconnector.v1_12_2.net.minecraft.tileentity.TileEntityStructure;

/** Structure block construction, mode states and tile entity factory. */
public class BlockStructure extends BlockContainer {
    public static final PropertyEnum<TileEntityStructure.Mode> MODE = PropertyEnum.create("mode", TileEntityStructure.Mode.class);
    public BlockStructure() {
        super(legacyconnector.v1_12_2.net.minecraft.block.material.Material.IRON);
        setHardness(-1.0F);
        setResistance(6000000.0F);
        setDefaultState(blockState.getBaseState().withProperty(MODE, TileEntityStructure.Mode.DATA));
    }
    @Override protected BlockStateContainer createBlockState() { return new BlockStateContainer(this, MODE); }
    @Override public IBlockState getStateFromMeta(int meta) { return getDefaultState().withProperty(MODE, TileEntityStructure.Mode.getById(meta)); }
    @Override public int getMetaFromState(IBlockState state) { return state.getValue(MODE).getModeId(); }
    @Override public TileEntityStructure createNewTileEntity(legacyconnector.v1_12_2.net.minecraft.world.World world, int meta) {
        return new TileEntityStructure();
    }
}

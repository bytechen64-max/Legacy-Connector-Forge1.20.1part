package legacyconnector.v1_7_10.cpw.mods.fml.relauncher;

import net.minecraftforge.fml.loading.FMLEnvironment;

public final class FMLLaunchHandler {
    private FMLLaunchHandler() {}

    public static Side side() {
        return FMLEnvironment.dist.isClient() ? Side.CLIENT : Side.SERVER;
    }
}

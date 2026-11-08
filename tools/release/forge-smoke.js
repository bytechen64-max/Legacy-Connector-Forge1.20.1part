if (tick === 0) {
    try {
        var mods = Java.type('net.minecraftforge.fml.ModList').get();
        if (!mods.isLoaded('mixinextras')) throw new Error('MixinExtras Forge dependency not registered');
        var info = mods.getModContainerById('legacyconnector').get().getModInfo();
        if (String(info.getDisplayName()) !== 'Legacy Connector (Forge 1.20.1 Port)') throw new Error('Wrong display name');
        var bootstrap = Java.type('com.llamalad7.mixinextras.MixinExtrasBootstrap');
        print('FORGE RELEASE SMOKE PASS: ' + info.getDisplayName() + ' ' + info.getVersion() + '; MixinExtras=' + bootstrap.getVersion());
    } catch (failure) {
        print('FORGE RELEASE SMOKE FAIL: ' + failure);
    } finally { server.halt(false); }
}

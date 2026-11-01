package legacyconnector.v1_12_2.net.minecraftforge.client.settings;

/** Forge's key modifiers (Ctrl, Shift, Alt, none), mapped onto NeoForge's identical ones. Key codes are LWJGL 2 ones. */
public enum KeyModifier {
    CONTROL(net.minecraftforge.client.settings.KeyModifier.CONTROL, 29, 157, 219, 220),
    SHIFT(net.minecraftforge.client.settings.KeyModifier.SHIFT, 42, 54),
    ALT(net.minecraftforge.client.settings.KeyModifier.ALT, 56, 184),
    NONE(net.minecraftforge.client.settings.KeyModifier.NONE);

    public static final KeyModifier[] MODIFIER_VALUES = {SHIFT, CONTROL, ALT};

    private final net.minecraftforge.client.settings.KeyModifier modern;
    private final int[] keys;

    KeyModifier(net.minecraftforge.client.settings.KeyModifier modern, int... keys) {
        this.modern = modern;
        this.keys = keys;
    }

    public net.minecraftforge.client.settings.KeyModifier mcc$modern() {
        return modern;
    }

    public static KeyModifier mcc$of(net.minecraftforge.client.settings.KeyModifier modern) {
        for (KeyModifier k : values()) if (k.modern == modern) return k;
        return NONE;
    }

    public static KeyModifier getActiveModifier() {
        for (KeyModifier m : MODIFIER_VALUES) if (m.isActive(null)) return m;
        return NONE;
    }

    public static boolean isKeyCodeModifier(int keyCode) {
        for (KeyModifier m : MODIFIER_VALUES) if (m.matches(keyCode)) return true;
        return false;
    }

    public static KeyModifier valueFromString(String name) {
        try {
            return valueOf(name);
        } catch (IllegalArgumentException | NullPointerException e) {
            return NONE;
        }
    }

    public boolean matches(int keyCode) {
        for (int k : keys) if (k == keyCode) return true;
        return false;
    }

    public boolean isActive(IKeyConflictContext context) {
        return modern.isActive(context == null ? null : context.mcc$modern());
    }

    public String getLocalizedComboName(int keyCode) {
        String key = legacyconnector.v1_12_2.net.minecraft.client.settings.GameSettings.getKeyDisplayString(keyCode);
        if (this == NONE) return key;
        return modern.getCombinedName(com.mojang.blaze3d.platform.InputConstants.UNKNOWN, () -> net.minecraft.network.chat.Component.literal(key)).getString();
    }
}

package org.kylepitcock.legacyconnector.core;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

/**
 * Reflection on Minecraft's own members, in both the development run and the installed jar.
 *
 * <p>The development run uses the official (Mojang) names a mod is compiled against, while an installed game runs the
 * <em>SRG</em> names ({@code f_120349_}, {@code m_91561_}) -- ForgeGradle reobfuscates the mod's bytecode, but a name inside a
 * string literal is not remapped. A lookup written for development therefore finds nothing in production, and because these call
 * sites catch the failure the feature is silently missing (legacy sounds, head-layer armor, key bindings, hopper cooldowns, the
 * local player's interpolation fields, ...).</p>
 *
 * <p>The two-argument forms look the SRG name up in {@code legacyconnector/mirror.tsrg}, which the build generates from
 * ForgeGradle's mapping ({@code build.gradle}, task {@code generateMirrorTable}); the three-argument forms take the SRG name
 * directly. The returned member is already accessible.</p>
 */
public final class Mirror {
    private static final String TABLE = "legacyconnector/mirror.tsrg";

    /** {@code owner + ' ' + name} to the SRG names that owner's member of that name has. */
    private static volatile Map<String, String[]> table;

    private Mirror() {}

    /** A declared field by its official name, the way the development game has it. */
    public static Field field(Class<?> owner, String official) throws NoSuchFieldException {
        try {
            Field f = owner.getDeclaredField(official);
            f.setAccessible(true);
            return f;
        } catch (NoSuchFieldException absent) {
            for (String srg : mapped(owner, official)) {
                try {
                    Field f = owner.getDeclaredField(srg);
                    f.setAccessible(true);
                    return f;
                } catch (NoSuchFieldException ignored) {
                    // the table can hold several names for an overload set
                }
            }
            throw absent;
        }
    }

    /** A declared field whose official and SRG names are both known. */
    public static Field field(Class<?> owner, String official, String srg) throws NoSuchFieldException {
        try {
            Field f = owner.getDeclaredField(official);
            f.setAccessible(true);
            return f;
        } catch (NoSuchFieldException absent) {
            Field f = owner.getDeclaredField(srg);
            f.setAccessible(true);
            return f;
        }
    }

    /** A declared method by its official name, the way the development game has it. */
    public static Method method(Class<?> owner, String official, Class<?>... params) throws NoSuchMethodException {
        try {
            Method m = owner.getDeclaredMethod(official, params);
            m.setAccessible(true);
            return m;
        } catch (NoSuchMethodException absent) {
            for (String srg : mapped(owner, official)) {
                try {
                    Method m = owner.getDeclaredMethod(srg, params);
                    m.setAccessible(true);
                    return m;
                } catch (NoSuchMethodException ignored) {
                    // an overload with another SRG name
                }
            }
            throw absent;
        }
    }

    /** A declared method whose official and SRG names are both known. */
    public static Method method(Class<?> owner, Class<?>[] params, String official, String srg) throws NoSuchMethodException {
        try {
            Method m = owner.getDeclaredMethod(official, params);
            m.setAccessible(true);
            return m;
        } catch (NoSuchMethodException absent) {
            Method m = owner.getDeclaredMethod(srg, params);
            m.setAccessible(true);
            return m;
        }
    }

    /** The SRG names the owner has for that official member name (empty in development, where the official name works). */
    private static String[] mapped(Class<?> owner, String official) {
        Map<String, String[]> index = table();
        if (index.isEmpty()) return new String[0];
        for (Class<?> c = owner; c != null && c != Object.class; c = c.getSuperclass()) {
            String[] found = index.get(name(c) + ' ' + official);
            if (found != null) return found;
        }
        return new String[0];
    }

    private static String name(Class<?> c) {
        return c.getName().replace('.', '/');
    }

    private static Map<String, String[]> table() {
        Map<String, String[]> index = table;
        if (index != null) return index;
        synchronized (Mirror.class) {
            if (table != null) return table;
            index = new HashMap<>();
            try (InputStream in = Mirror.class.getClassLoader().getResourceAsStream(TABLE)) {
                if (in != null) {
                    BufferedReader reader = new BufferedReader(new InputStreamReader(in, StandardCharsets.UTF_8));
                    String line;
                    while ((line = reader.readLine()) != null) {
                        // F <owner> <official> <srg>  /  M <owner> <official> <srg>
                        int first = line.indexOf(' ');
                        int second = line.indexOf(' ', first + 1);
                        int third = line.indexOf(' ', second + 1);
                        if (second < 0 || third < 0) continue;
                        String key = line.substring(first + 1, third);
                        String srg = line.substring(third + 1);
                        index.merge(key, new String[] {srg}, Mirror::append);
                    }
                }
            } catch (java.io.IOException e) {
                // without the table only the development names resolve; nothing to do at startup
            }
            table = index;
            return index;
        }
    }

    private static String[] append(String[] existing, String[] added) {
        String[] out = new String[existing.length + added.length];
        System.arraycopy(existing, 0, out, 0, existing.length);
        System.arraycopy(added, 0, out, existing.length, added.length);
        return out;
    }
}

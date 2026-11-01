package org.kylepitcock.legacyconnector.api.event;

import net.minecraftforge.eventbus.api.Event;
import net.minecraftforge.fml.event.IModBusEvent;

/** Phase {@code LOAD_COMPLETE}: the legacy mods' loadComplete ran. Main thread; registries are frozen. */
public class LegacyLoadCompleteEvent extends Event implements IModBusEvent {}

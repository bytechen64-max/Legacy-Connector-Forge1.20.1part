"""The remaining forge hooks (bonemeal) and the render tick partial tick."""
import sys

P = r"src/main/java/legacyconnector/v1_12_2/net/minecraftforge/event/ForgeEventFactory.java"
src = open(P, encoding="utf-8").read()
old = ("        var event = net.minecraftforge.event.ForgeEventFactory.fireBonemealEvent(player(player), world.mcc$level(), pos(pos), state(state), Stacks1122.toModern(stack));\n"
       "        if (event.isCanceled()) return -1;\n"
       "        return event.isSuccessful() ? 1 : 0;")
new = ("        // 1.20.1 answers with -1 (canceled), 1 (another mod applied it) or 0 (grow as usual).\n"
       "        return net.minecraftforge.event.ForgeEventFactory.onApplyBonemeal(player(player), world.mcc$level(), pos(pos),\n"
       "                state(state), Stacks1122.toModern(stack));")
if src.count(old) != 1:
    print("ABORT bonemeal:", src.count(old))
    sys.exit(1)
open(P, "w", encoding="utf-8", newline="").write(src.replace(old, new))
print("patched", P)

P = r"src/main/java/org/kylepitcock/legacyconnector/v1_12_2/bridge/EventBridge1122.java"
src = open(P, encoding="utf-8").read()
n = src.count("e.partialTick")
src = src.replace("TickEvent.Phase.START, e.partialTick", "TickEvent.Phase.START, e.renderTickTime")
src = src.replace("TickEvent.Phase.END, e.partialTick", "TickEvent.Phase.END, e.renderTickTime")
open(P, "w", encoding="utf-8", newline="").write(src)
print("render tick fields:", n)

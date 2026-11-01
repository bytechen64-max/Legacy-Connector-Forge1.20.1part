"""Finishes the toast-id and skin-texture renames (simple substitutions)."""
import os

changed = []
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        src = open(p, encoding="utf-8").read()
        if "SystemToastId" not in src and "getSkin().texture()" not in src:
            continue
        before = src
        src = src.replace("SystemToast.SystemToastId.", "SystemToast.SystemToastIds.")
        src = src.replace("SystemToast.SystemToastId ", "SystemToast.SystemToastIds ")
        src = src.replace("SystemToast.SystemToastId)", "SystemToast.SystemToastIds)")
        src = src.replace("new net.minecraft.client.gui.components.toasts.SystemToast.SystemToastIds()",
                          "net.minecraft.client.gui.components.toasts.SystemToast.SystemToastIds.TUTORIAL_HINT")
        src = src.replace("p.getSkin().texture()", "p.getSkinTextureLocation()")
        if src != before:
            open(p, "w", encoding="utf-8", newline="").write(src)
            changed.append(p)
print("patched", len(changed), "files")
for c in changed:
    print("  ", c)

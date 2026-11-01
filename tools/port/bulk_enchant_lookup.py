"""1.20.1's EnchantmentHelper takes the enchantment directly (the registry lookup wrapper is 1.21)."""
import os
import re

GET_OR_THROW = re.compile(r"(enchants?)\.getOrThrow\(((?:net\.minecraft\.world\.item\.enchantment\.)?Enchantments\.[A-Z_]+)\)")

count = 0
changed = []
for dirpath, _dirs, names in os.walk("src"):
    for name in names:
        if not name.endswith(".java"):
            continue
        p = os.path.join(dirpath, name)
        src = open(p, encoding="utf-8").read()
        new, n = GET_OR_THROW.subn(r"\2", src)
        if n:
            count += n
            open(p, "w", encoding="utf-8", newline="").write(new)
            changed.append((p, n))

print("getOrThrow wrappers removed:", count)
for c in changed:
    print("  ", c)

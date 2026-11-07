#!/usr/bin/env python3
"""Compare a built kernel's Module.symvers with a vendor module import table.

The table is generated from a real vendor .ko's __versions section:

    0x4e276f37<TAB>module_layout<TAB>rfkill

A vendor module loads only if every symbol it imports is exported by the
kernel with the same CRC. Symbols provided by another vendor module are not
in vmlinux; pass --allow-missing for tables that contain such symbols.

Usage:
    check_vendor_crc.py Module.symvers tests/vendor-rfkill.tsv
    check_vendor_crc.py Module.symvers tests/vendor-goodix.tsv --allow-missing
"""

import sys


def load_symvers(path):
    table = {}
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.lstrip("\ufeff")
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 2:
                continue
            crc, name = fields[0], fields[1]
            if not crc.lower().startswith("0x"):
                continue
            table[name] = int(crc, 16)
    return table


def load_table(path):
    rows = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.lstrip("\ufeff").strip()
            if not line or line.startswith("#"):
                continue
            fields = line.split("\t")
            if len(fields) < 2:
                continue
            rows.append((int(fields[0], 16), fields[1]))
    return rows


def main(argv):
    if len(argv) < 3:
        print(__doc__.strip())
        return 2

    symvers_path, table_path = argv[1], argv[2]
    allow_missing = "--allow-missing" in argv[3:]

    kernel = load_symvers(symvers_path)
    rows = load_table(table_path)

    missing = []
    wrong = []
    for crc, name in rows:
        if name not in kernel:
            missing.append(name)
        elif kernel[name] != crc:
            wrong.append((name, kernel[name], crc))

    print(f"{table_path}: {len(rows)} imports, {len(kernel)} kernel exports")

    if wrong:
        print(f"  FAIL: {len(wrong)} CRC mismatch")
        for name, ours, want in wrong[:20]:
            print(f"    {name}: built 0x{ours:08x}, vendor wants 0x{want:08x}")
    if missing:
        label = "WARN" if allow_missing else "FAIL"
        print(f"  {label}: {len(missing)} symbol(s) not exported by this kernel")
        for name in missing[:20]:
            print(f"    missing: {name}")
    if not wrong and not missing:
        print("  OK: every import matches")

    if wrong:
        return 1
    if missing and not allow_missing:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

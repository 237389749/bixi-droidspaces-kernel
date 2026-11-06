#!/usr/bin/env python3
"""Generate a vendor import table from a kernel module's __versions section.

Usage:
    gen_vendor_tsv.py /path/to/vendor.ko [source-name] > tests/vendor-x.tsv

Output: <crc32>\t<symbol>\t<source>
"""

import struct
import sys


def read_versions(path):
    data = open(path, "rb").read()
    e_shoff = struct.unpack_from("<Q", data, 0x28)[0]
    e_shentsize = struct.unpack_from("<H", data, 0x3A)[0]
    e_shnum = struct.unpack_from("<H", data, 0x3C)[0]
    e_shstrndx = struct.unpack_from("<H", data, 0x3E)[0]

    sections = [
        struct.unpack_from("<IIQQQQIIQQ", data, e_shoff + i * e_shentsize)
        for i in range(e_shnum)
    ]
    str_off = sections[e_shstrndx][4]

    def name_at(off):
        end = data.index(b"\0", str_off + off)
        return data[str_off + off : end].decode("utf-8", "replace")

    versions = {}
    for head in sections:
        if name_at(head[0]) != "__versions":
            continue
        offset, size = head[4], head[5]
        for i in range(size // 64):
            entry = data[offset + i * 64 : offset + (i + 1) * 64]
            crc = struct.unpack_from("<I", entry, 0)[0]
            symbol = entry[8:].split(b"\0")[0].decode("utf-8", "replace")
            versions[symbol] = crc
    return versions


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip())
        return 2
    path = argv[1]
    source = argv[2] if len(argv) > 2 else "vendor"
    for symbol, crc in sorted(read_versions(path).items()):
        print(f"0x{crc:08x}\t{symbol}\t{source}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

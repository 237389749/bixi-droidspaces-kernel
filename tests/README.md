# vendor import tables

These tables are generated from the `__versions` section of vendor modules
shipped in the bixi ROM (via the TWRP device tree):

```
<crc32>\t<symbol>\t<source>
```

- `vendor-rfkill.tsv`: `rfkill.ko`, vermagic
  `6.6.77-android15-8-g4a507830d890-ab13636293-4k`, 58 imports.
  **Strict gate**: every symbol must be exported by the kernel with the same CRC.
- `vendor-goodix.tsv`, `vendor-synaptics.tsv`, `vendor-xiaomi-touch.tsv`,
  `vendor-nxp.tsv`, `vendor-qca.tsv`: older 6.6.57 modules. They can import
  symbols provided by other vendor modules (cfg80211, xiaomi_touch, etc.),
  so the workflow runs them with `--allow-missing`: every symbol that *is*
  in vmlinux must match, missing ones are reported as WARN.

All tables come from the `flip/flipRecovery` TWRP trees (bixi/thales).
`rfkill.ko` matches the OS3.0.304.0 boot kernel exactly; the others are
6.6.57 but already showed zero CRC mismatches against the 6.6.118 reference
table, so they are useful as extra coverage.

Regenerate:

```sh
python3 scripts/gen_vendor_tsv.py /path/to/module.ko source > tests/vendor-x.tsv
```

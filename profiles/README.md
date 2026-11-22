# Profiles

One directory per ROM/kernel target. The build workflow reads `profile.env`
and the files next to it; do not add a branch per ROM.

| profile | ROM | kernel |
|---|---|---|
| `6.6.77-os3.0.304.0` | HyperOS 3 `OS3.0.304.0.WOHCNXM` | `6.6.77-android15-8-g4a507830d890-ab13636293-4k` |
| `6.6.118-os4.0.3` | HyperOS 4 `OS4.0.3.0.XOHCN` | `6.6.118-android15-8-g0908354dac1b-ab16143355-4k` |

Each profile contains:

- `profile.env`: source ref/manifest, KMI tag, kABI slot, build number,
  expected module_layout and kernel release.
- `stock.config`: IKCONFIG extracted from that ROM's `boot.img`.
- `stock_gki_module_signing.pem` + `.fingerprint`: the ROM's build-time module
  signing certificate. **Never reuse across ROM versions.**
- `boot-avb.env`: partition size, rollback index, os_version, fingerprint,
  security patch from that ROM's stock boot.

## 6.6.118-os4.0.3 notes

- Source commit `0908354dac1b8a65a215da1ca0c9c78dcd83014f`; the workflow uses
  `common-android15-6.6` and checks out the commit. This was verified in CI
  (run 44090419914, success), so no AOSP tag is required for now.
  If a future build cannot find the commit, pin the matching `_rN` tag.
- `CONFIG_GKI_DYNAMIC_TASK_STRUCT_SIZE=y` and
  `CONFIG_GKI_TASK_STRUCT_VENDOR_SIZE_MAX=1024` are new versus 6.6.77.
  The kABI slot default is `6_7_8` (Pad8 Pro 6.6.118 evidence), but it must
  pass the cert + CRC gates and a real-device module test.
- Stock signing cert fingerprint:
  `DA:85:6B:3D:83:43:AB:FB:A2:AF:69:4E:36:ED:C9:B7:04:A8:8B:76:37:A1:6A:3A:CF:64:ED:5E:2B:E3:58:4B`
- AVB: 100,663,296 B, rollback 1,790,812,800, os_version 15,
  security patch 2026-10-01.

# NOTICE

- Kernel source: Android Common Kernel (`kernel/common`), GPL-2.0.
  Built from tag `android15-6.6-2025-03_r15`.
- kABI patches: copied from Droidspaces-OSS
  `Documentation/resources/kernel-patches/GKI/below-kernel-6.12/`,
  authored by nullptr-t-oss and contributors.
- `configs/bixi-stock.config`: extracted from the IKCONFIG embedded in the
  stock `boot.img` of Xiaomi MIX Flip 2 `OS3.0.304.0.WOHCNXM`.
- `configs/bixi-boot-avb.env`: `avbtool info_image` output of the same boot image.
- `tests/*.tsv`: CRC values parsed from `__versions` of vendor modules shipped
  in the same ROM (via the bixi TWRP device tree). These are factual symbol
  CRCs, not source code.

No vendor binaries or ROM images are redistributed in this repository.

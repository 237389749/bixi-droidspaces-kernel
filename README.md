# bixi-droidspaces-kernel

在 **Xiaomi MIX Flip 2（`bixi` / SM8750 / Snapdragon 8 Elite）** 的原厂 GKI 6.6.77
基线上，编一个能让 Droidspaces 正常跑容器的内核。

- 目标系统：HyperOS 3 `OS3.0.304.0.WOHCNXM`（Android 16）
- 原厂内核：`6.6.77-android15-8-g4a507830d890-ab13636293-4k`
- 源码基线：AOSP tag `android15-6.6-2025-03_r15`
  （manifest 分支 `common-android15-6.6-2025-03`）
- 构建方式：GitHub Actions（手动触发）

## 做了什么

在原厂 IKCONFIG 的基础上，只打开 Droidspaces 需要且 ABI 安全的选项：

```
CONFIG_SYSVIPC=y
CONFIG_POSIX_MQUEUE=y
CONFIG_IPC_NS=y
CONFIG_PID_NS=y
CONFIG_DEVTMPFS=y
CONFIG_MACVLAN=y
CONFIG_IP6_NF_NAT=y
CONFIG_IP6_NF_TARGET_MASQUERADE=y
CONFIG_NETFILTER_XT_MATCH_ADDRTYPE=y
CONFIG_USER_NS=y          # 可通过 workflow 输入关闭
```

`SYSVIPC` 会给 `task_struct` 加字段，必须打官方 kABI 补丁
（`patches/001.GKI-below-6.12-fix_sysvipc_kabi_*.patch`，默认 6/7/8 槽）。

**不开** `CONFIG_CGROUP_PIDS` / `CONFIG_CFS_BANDWIDTH`：它们会改
调度器/cgroup 结构，破坏 GKI kABI，导致原厂 vendor 模块拒载。

不集成 KernelSU / SUSFS。已确认本机 root 是 **KernelSU LKM 模式，补丁在 `init_boot`**，
本仓库只替换 `boot` 里的 kernel 段，**刷入不会影响 root**；请勿刷 `init_boot`。

## 构建

推到 GitHub 后，Actions → **build-bixi-kernel** → Run workflow。

| 输入 | 默认 | 说明 |
|---|---|---|
| `kernel_tag` | `android15-6.6-2025-03_r15` | 必须与原厂 `uname -r` 的 commit 对应 |
| `manifest_branch` | `common-android15-6.6-2025-03` | 与 tag 配套 |
| `kabi_slot` | `6_7_8` | 若 CRC 闸门失败，依次试 `1_2_3`、`3_4_5` |
| `enable_userns` | `1` | 关掉可少一个变量；Docker/沙箱需要它 |
| `build_number` | `13636293` | 仅影响版本串，不影响模块加载 |

流程：

1. `repo init/sync` AOSP GKI 源码，checkout 上方 tag；
2. 打 kABI 补丁；
3. 以 `configs/bixi-stock.config` 为基线，覆盖 Droidspaces 选项；
4. `make Image modules`，生成 `Image` 与 `Module.symvers`；
5. **CRC 闸门**：用原厂 vendor 模块的 `__versions` 逐符号比对
   （`tests/vendor-rfkill.tsv` 严格 58 项；`tests/vendor-goodix.tsv` 容忍模块间符号）；
6. `mkbootimg` v4 + `avbtool`（算法 `NONE`）打 96 MiB boot；
7. 上传 `boot-bixi-ds.img`、`Image`、`Module.symvers`、`config.diff`、`BUILD-INFO.txt`。

## 刷入

```bash
fastboot getvar current-slot        # a 或 b
fastboot flash boot_<slot> boot-bixi-ds.img
fastboot reboot
```

回滚：

```bash
fastboot flash boot_<slot> stock-boot.img
fastboot reboot
```

- 不要动 `init_boot`（KSU）、`vendor_boot`、`dtbo`、`vbmeta`。
- 部分小米机型/HyperOS 禁用 `fastboot boot`，不要假设可以临时启动。
- 刷前备份全分区（9008/EDL），并确认当前 slot。

## 产物自检

刷前可以核对：

- `BUILD-INFO.txt` 里的 `kernel banner` 应是 6.6.7x；
- `Module.symvers` 里 `module_layout = 0x4e276f37`（与 bixi 原厂 vendor 模块一致）；
- `GENERATED-BOOT-AVB-INFO.txt` 的 `Image size` 应为 100663296。

上机后：

```bash
adb shell uname -r
adb shell 'ls /proc/self/ns'
adb shell 'grep devtmpfs /proc/filesystems'
adb shell "su -c '/data/local/Droidspaces/bin/droidspaces check'"
```

## 目录

```
.github/workflows/build.yml   Actions 构建
configs/bixi-stock.config     bixi 原厂 IKCONFIG（从 boot.img 解出）
configs/bixi-boot-avb.env     原厂 boot 的 AVB 参数
patches/                      官方 SYSVIPC kABI 补丁（3 个槽位变体）
scripts/check_vendor_crc.py   Module.symvers vs vendor __versions
tests/                        原厂 vendor 模块的导入符号 CRC 表
```

## 来源与许可

- 内核源码：AOSP `kernel/common`（GPL-2.0）；
- kABI 补丁：Droidspaces-OSS 官方补丁（GPL-2.0/GPL-3.0 双体系，见上游）；
- 原厂配置与 AVB 参数：来自 `OS3.0.304.0.WOHCNXM` 线刷包的 `boot.img`；
- vendor CRC 表：从 bixi 的 TWRP 设备树里提取的 `rfkill.ko`（6.6.77）
  与 `goodix_core.ko`（6.6.57，CRC 与 6.6.77 一致）的 `__versions`。

## 免责声明

刷内核有风险，可能导致无法开机、数据丢失。请先做 9008/EDL 全分区备份，
并保留原厂 `boot.img`。本项目只对 `bixi` + `OS3.0.304.0` + 6.6.77 验证，
OTA 或换 ROM 后必须重新对 tag / 重跑 CRC 闸门。

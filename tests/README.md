# vendor import tables

这些表来自 bixi 原厂内核的 vendor 模块，由模块 ELF 的 `__versions` 段生成：

```
<crc32>\t<symbol>\t<source>
```

- `vendor-rfkill.tsv`：`rfkill.ko`，vermagic
  `6.6.77-android15-8-g4a507830d890-ab13636293-4k`，58 个导入符号。
  这是**严格**闸门：58 个符号必须全部由新内核导出且 CRC 一致。
- `vendor-goodix.tsv`：`goodix_core.ko`，vermagic `6.6.57-...`，155 个导入符号。
  其中约 14 个是模块间/树外符号，不在 vmlinux 的 `Module.symvers` 里，
  所以 workflow 用 `--allow-missing`，但仍要求所有能对上的符号 CRC 一致。

模块来自 `flip/flipRecovery` 的 TWRP 设备树（bixi）。`rfkill.ko` 的 vermagic
与 `OS3.0.304.0` 的 boot 内核完全一致，可视为权威样本。

重新生成（在仓库根目录）：

```bash
python3 scripts/gen_vendor_tsv.py /path/to/rfkill.ko > tests/vendor-rfkill.tsv
```

`gen_vendor_tsv.py` 目前没有入库；生成逻辑就是遍历 ELF section，
取名为 `__versions` 的段，按 64 字节一条解析（前 4 字节 CRC，后 56 字节符号名）。

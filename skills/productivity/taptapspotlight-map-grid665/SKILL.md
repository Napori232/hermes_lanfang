---
name: taptapspotlight-map-grid665
description: Use when preprocessing TapTapSpotlight maps to 665 grids.
---

# TapTapSpotlight 地图 665 预处理

用户说“预处理”“排到 665 格子”“像 1 到 1_grid665 一样”时，默认执行以下流程，不要误判为普通裁边、压缩或切片：

1. 使用 `D:/TapTapspotlight/tools/tilemap_normalizer/normalizer.py`，参数为 `665`。
2. 原图规范命名为 `N.png`，结果命名为 `N_grid665.png`；统一小写 `.png`。
3. 保留原图和预处理结果，不覆盖原图。
4. 若原图已被 `.tres` / Godot TileSet 引用，将引用同步改为 `N_grid665.png`。
5. 验证输出宽高均可被 665 整除，并报告列数、行数和输出尺寸。
6. 不删除或恢复工作树中与本次任务无关的已有改动。

示例命令：

```powershell
uv run --with pillow --with numpy python D:/TapTapspotlight/tools/tilemap_normalizer/normalizer.py D:/TapTapspotlight/src/Art/New/map1/3.png 665
```

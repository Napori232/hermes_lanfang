---
name: 2d-spritesheet-pipeline
description: "Use when processing 2D animation sprite sheets for Godot."
version: 1.0.0
---

# 2D SpriteSheet Pipeline & Godot Alignment Rules

Procedures and standards for inspecting, splitting, packaging, trimming, and aligning 2D character sequence frames for Godot engine.

## 0. Preflight and Processing Order
1. **Inventory without modifying the source**: enumerate candidate images, record source dimensions/mode, and hash the original before processing. Write all derivatives to a sibling `processed/` directory unless the user explicitly requests a target folder or asks to split the source directly; in that case, write split files beside the source and leave the source untouched.
2. **Inspect pixels before visual interpretation**: read the real width, height, color mode, alpha extrema/counts, and nonzero-alpha bounding box with a deterministic image library. Do not infer dimensions, transparency, or frame count from a downscaled vision preview; very wide strips can be misread when previewed as a tiny image.
3. **Detect the layout**:
   - For a regular grid, use the known cell dimensions.
   - For a one-row strip with transparent gaps, compute per-column occupancy using `alpha > threshold`, group contiguous occupied columns, and treat each run as a candidate frame.
   - For a small transparent composite with visibly separated objects, run 8-connected-component detection after alpha-run detection; ignore only negligible noise components and crop each substantial component to its exact bounding box.
   - If frames touch, overlap, span multiple rows, or the background is opaque, do not pretend alpha-run detection is reliable; obtain the grid/export parameters or use connected-component/manual segmentation.
4. **Clean and normalize**: clear pixels at or below the chosen alpha-noise threshold, crop each candidate independently, calculate a uniform cell, center each active frame horizontally, and align all frames to one ground-contact baseline.
5. **Export both forms**: emit numbered standalone frames plus a uniform Godot sheet and machine-readable metadata containing source hash/size, threshold, source ranges, cell size, offsets, frame count, and layout.
6. **Verify before handoff**: assert frame count and output dimensions, re-hash the source to prove it was unchanged, and render a checkerboard preview when alignment or neighbor-frame leakage matters. For simple standalone crops, reopen every exported PNG and verify its dimensions and RGBA mode.
7. **Name to the user's asset convention**: when the user supplies semantic names, translate terms only if requested, use lowercase English snake_case by default (for example, `stone_1.png`), retain the output order, and rename directly rather than adding an unnecessary confirmation round.

### Alpha-strip recipe
For a horizontal strip of width `W` and height `H`, compute `occupied[x] = any(alpha[x,y] > threshold for y in 0..H-1)` and run-length group the `True` columns. This is more reliable than asking vision to guess boundaries from a scaled preview. Use a low threshold only to suppress negligible edge noise; retain meaningful antialiasing. After segmentation, ensure every candidate is visually complete and that the detected count matches the apparent animation sequence.

### Safety-margin rule
Do not align the active bottom pixel directly to the canvas edge. Reserve explicit top and bottom padding, set `baseline_y = cell_h - bottom_pad`, and place each crop at `paste_y = baseline_y - active_bbox.bottom`. Size the uniform cell from the largest active extents plus padding; a convenient round width/height is acceptable only when it contains every frame without scaling.

## 1. Engine Alignment: In-Place Movement Principle
- **Root Motion Separation**: 2D character movement (walk, run, dash) in Godot (`CharacterBody2D`) must be driven programmatically via script velocity. The visual sprite sheet animation **MUST strictly walk/run in-place (原地踏步)**.
- **Root Slipping Pitfall**: Animators often export frames with lateral displacement across the original canvas (e.g. character stepping from $X=50$ to $X=250$). If trimmed or packaged using absolute canvas union, the character will slide forward and backward unnaturally inside Godot.
- **Ground & Foot Alignment**:
  - Always segment and crop frames individually; never crop the whole animation by a union box.
  - Align each frame using **Bottom-Center (底部脚心对齐)**: horizontally center the active bounding box and anchor the lowest ground-contact pixel to one shared baseline with explicit bottom padding.
  - Uniform cell dimensions: find the maximum active width/height across the sequence, add safety padding, and pad every cell to the exact same dimensions. Never scale individual frames merely to make them fit.

## 2. Godot Grid Format vs Packer Algorithms
- **Uniform Grid Requirement**: Godot `Sprite2D` standard animation workflow relies on `Hframes` (horizontal count) and `Vframes` (vertical count). Every single cell must be strictly 100% identical in pixel dimensions.
- **Packer Algorithm Trap**: Generic atlas packers (like Free-Tex-Packer's `OptimalPacker` or `MaxRectsBin`) prioritize texture atlas compaction and pack frames irregularly across space, destroying frame sequence order and producing non-uniform cell cuts.
- **Godot Standard Output**:
  - Arrange sequence frames in a single horizontal strip ($Hframes = N, Vframes = 1$) or clean grid.
  - Sort frames strictly by numeric filename order (`IMG_01`, `IMG_02`, ...).

## 3. Automation & Batch Packaging Pitfalls
- **Case-Insensitive Deduplication on Windows**: Never use simple `glob.glob('*.png') + glob.glob('*.PNG')` on case-insensitive filesystems (Windows/macOS), as it returns duplicate file entries and duplicates frames in the spritesheet. Use a set or filter `os.listdir()` with `f.lower().endswith('.png')`.
- **Anchor Center Calculation**: When batch packaging via Python or GodotSpritePacker logic:
  - Identify the active bounding box with a small, documented alpha threshold; inspect alpha statistics first so the threshold does not erase intentional translucent effects.
  - Calculate `anchor_x` based on the top 25% height region (head/torso centroid) or horizontal center to avoid foot-spread anchor drift.
  - Cell width is $\text{ceil}(\max(\text{anchor\_x} - \text{xmin}) + \max(\text{xmax} - \text{anchor\_x})) + 2 \times \text{pad}$.
  - Use one padded baseline for every frame: `paste_x = i * cell_w + round(center_x - (anchor_x - xmin))`, `paste_y = baseline_y - ymax`.
- **Batch Processing Zips**: When batch processing compressed action archives, unpack into standardized lowercase English folder names (`dash`, `wall_kick`, `jump_land`) matching game state machine action identifiers, then pack each directly to `<action>.png`.

## 4. Tooling & Hand-off Standards
- When providing packaging tools to artists or external team members:
  - Deliver zero-dependency, self-contained single-file solutions (e.g. standalone browser HTML tool or clean GUI bundle) rather than multi-step command-line scripts or complex config-heavy atlas packers.
  - Tool must automatically calculate uniform maximum bounding box and lock bottom-center foot alignment by default.

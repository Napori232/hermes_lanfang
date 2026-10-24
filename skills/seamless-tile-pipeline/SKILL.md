---
name: seamless-tile-processing
description: "Use when creating horizontally seamless 2D game tiles."
version: 1.1.0
---

# Horizontal Seamless Tile & Terrain Processing Pipeline

Standards and procedures for processing 2D game terrain, platforms, and illustrative slabs into horizontally seamless looping assets without resolution loss or destructive blurring.

## 1. Core Rules: Native Resolution & Alignment
- **Strictly No Downscaling**: Unless explicitly requested, never resize, resample, or compress source art dimensions. High-resolution art (e.g. 5000px sheets or 700px tiles) must retain 100% native pixel density to prevent blurring.
- **Strict Vertical Baseline Alignment (上下基准对齐)**:
  - **The Pitfall**: Slicing tiles based on raw non-zero alpha bounding boxes (`getbbox()`) causes vertical jitter (1–3px height offset) because subtle antialiasing halos or slope variations shift the detected top row across different columns. When tiled horizontally, this appears as steps/notches between adjacent blocks.
  - **Correct Procedure**: Establish a fixed, absolute horizontal reference line across the entire spritesheet (e.g., locking $Y$ coordinate to the exact rail/surface line) rather than per-tile loose bounding boxes.
- **Separate Verification from Packaging**: Always produce 1x raw slice, 1x processed slice, and 1x multi-repeat (3x horizontal) preview at full resolution for verification before delivering standalone scripts or desktop tools.

## 2. Stylized / Discrete Geometry Seam Pitfalls
1. **Never Rely on Naive Linear Cross-Fade on Hard-Edged / Stylized Art**:
   - **The Pitfall**: Linear alpha cross-fade or soft feathering on stylized/faceted art (e.g. vector rocks, cell-shaded cobblestones) creates a distinct blurry/dissolved ghosting ("融化/虚化/双重曝光") at the seam, breaking visual consistency and making repetition obvious.
2. **Algorithmic Limits on Discrete Objects (石块截断与算法边界)**:
   - **The Pitfall**: Pure algorithmic approaches (Cross-fade, DP Seam Carving / Minimum Energy Cut) cannot semantically invent or reconstruct discrete objects cut in half at tile boundaries. Seam carving will either slice stones in unnatural jagged lines or leave floating half-stones.
   - **Correct Procedure**: Clarify algorithmic trade-offs immediately to the user:
     - *Algorithm A (Automated)*: Anchor top/bottom baselines strictly, route seams through low-frequency/mortar areas, and clean bisected micro-fragments to base color.
     - *Pipeline B (Industrial Standard)*: Output an unscaled 50% offset image (`np.roll(img, w // 2, axis=1)`) where the seam sits in the center, allowing minimal manual patch-up (2–3 minutes of seam painting) before reverse-offsetting, coupled with a turnkey inspection tool for live seamless scrolling verification.
3. **Turnkey Tool Delivery Protocol**:
   - Deliver standalone drag-and-drop Python or Tkinter GUI scripts/executables that ingest PNGs, maintain native dimensions, provide interactive horizontal scrolling preview, and export ready-to-use seamless tiles.

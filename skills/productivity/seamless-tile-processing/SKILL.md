---
name: seamless-tile-processing
description: "Use when creating horizontally seamless 2D game tiles."
version: 1.0.0
---

# Horizontal Seamless Tile & Terrain Processing Pipeline

Standards and procedures for processing 2D game terrain, platforms, and illustrative slabs into horizontally seamless looping assets without resolution loss or destructive blurring.

## 1. Core Rule: Preservation of Native Resolution
- **Strictly No Downscaling**: Unless explicitly requested, never resize, resample, or compress source art dimensions. High-resolution art (e.g. 5000px sheets or 700px tiles) must retain 100% native pixel density to prevent blurring.
- **Separate Verification from Packaging**: Always produce 1x raw slice, 1x processed slice, and 1x multi-repeat (3x horizontal) preview at full resolution for verification before delivering standalone scripts or desktop tools.

## 2. Seamless Processing Workflow & Pitfalls
1. **Never Rely on Naive Linear Cross-Fade on Hard-Edged / Stylized Art**:
   - **The Pitfall**: Linear alpha cross-fade or soft feathering on stylized/faceted art (e.g. vector rocks, cell-shaded cobblestones) creates a distinct blurry/dissolved smear ("融化/虚化感") at the seam, breaking visual consistency and making repetition obvious.
   - **Correct Procedure**: Use standard 50% horizontal offset (`np.roll(img, w // 2, axis=1)` / Offset filter) to bring the seam into the center. Blend or patch along natural contour lines (stone cracks, fissures) rather than creating soft double-exposure ghosts.
2. **Top Boundary Alignment & Micro-Spike Removal**:
   - **The Pitfall**: Even a 1–2 pixel vertical difference or antialiasing halo at the top boundary produces a repetitive upward spike or sawtooth notch when tiled horizontally.
   - **Correct Procedure**: Strictly clamp or trim the top boundary pixels so that the tread/rail surface remains mathematically collinear across all repetitions.
3. **Turnkey Tool Delivery Protocol**:
   - Deliver standalone drag-and-drop Python or Tkinter GUI scripts/executables that ingest PNGs, maintain native dimensions, and export ready-to-use seamless tiles.

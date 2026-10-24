---
name: hand-drawn-terrain-pipeline
description: "Use when decoupling hand-drawn art from physics TileMaps."
version: 1.0.0
---

# Hand-Drawn Terrain & Modular Art Asset Pipeline

Guidelines and production standards for decoupling hand-drawn 2D art assets from rigid physics grids, structuring artist handoffs, and ingesting composite multi-asset sheets.

## 1. Grid vs. Illustration Mismatch (Core Failure Mode)
- **The Conflict**: Traditional TileMap workflows require atomic, power-of-two (e.g. 16×16, 32×32), seamlessly tileable square textures. Hand-drawn / illustrative art inherently emphasizes organic curves, dynamic brushwork, and holistic lighting.
- **The Pitfall**: Asking non-technical or illustrative artists to draw "tiles" often results in closed composite blocks (e.g. closed 3×2 rock platforms). Forcing closed composite illustrations into grid TileMaps causes severe repetition artifacts, breaks jump spacing, and prevents flexible level layout.

## 2. Structural Decoupling: The Modular Prop / Hollow Knight Architecture
When working with hand-drawn visual styles, strictly decouple physics from rendering:
1. **Physics Layer (Strict Grid / Invisible)**:
   - Build level geometry using an invisible, simple 32×32 TileSet collision layer or `CollisionPolygon2D` boundaries (e.g. `collision_tile_set.tres` with `self_modulate = Color(1, 1, 1, 0)`).
   - Whitebox level design, jump distances, and combat pacing strictly against this invisible collision layer.
   - Gameplay scripts (phase toggling, death/respawn triggers, coordinate queries via `local_to_map` / `get_used_rect`) must exclusively bind to this physics scaffold.
2. **Visual Layer (Freeform Placement / Modular Kit)**:
   - Render terrain using freeform `Sprite2D` nodes overlapping each other, or dedicated zero-collision visual `TileMapLayer` nodes scaled to match the logical grid.
   - Overlap slabs and rock pieces naturally; hand-drawn organic edges seamlessly blend when layered.

### Visual-Only State Variants for Existing Gameplay Components
Before proposing a component refactor, classify every requested change as **visual**, **interaction**, **collision**, or **gameplay state**. If the user is only changing presentation, do not redesign collision ownership, activation rules, or gameplay geometry; that turns a low-risk art change into a coupled migration.

For a rectangular gameplay component that already owns its bounds and state:
1. Keep the existing gameplay component, collision shapes, and state transitions authoritative.
2. Add a zero-collision visual child or sibling scene. Its pre-change appearance may be a dedicated `TileMapLayer` containing freely arranged bricks and rune artwork; it does not need to describe gameplay geometry.
3. Give each component instance its own post-change texture or visual scene when bespoke art is acceptable. Reuse is optional at the asset level and must not be forced into the logic architecture.
4. Expose a presentation-only signal such as `visual_state_changed(is_transformed: bool)` from the authoritative component. The visual scene listens and swaps/fades its layers; it must not write back into collision or gameplay state.
5. Preserve the legacy visual fallback for instances without the new visual scene, then migrate instances incrementally.

A rune drawn inside the visual TileMap is only artwork. Create a separate rune interaction node only when hit-testing must occur specifically on the rune; otherwise keep activation on the existing component. Do not infer interaction architecture from how the symbol is painted.

### Safe Refactoring & Coupling Audit for Visual Layers
When evaluating whether legacy visual terrain (such as composite `*BrickArt.tscn` or patch scenes with thousands of sliced `Sprite2D` nodes) can be safely deleted or replaced:
1. **Audit Codebase Coupling First**: Search `Code/` for node names and scene file names. Check if any controller script (`*Battlefield.gd`) references the visual node. If only the invisible collision `TileMapLayer` is controlled via `_set_phase_collisions` or bounding queries (`get_used_rect()`), the visual layer is decoupled.
2. **Verify Component / Child Area Entanglement**: Check that the visual scene does not host child interaction triggers (`InstantKillArea`, `WaterFlowArea`, interactables) or custom shader scripts needed by logic.
3. **Preserve the Physics Scaffold**: When stripping and rebuilding visual layers, leave the invisible collision TileMap untouched so designer jump curves, enemy patrol bounds, and respawn checks continue functioning without interruption.

## 3. Hand-off Specification for Illustrators (Modular Kit Specs)
When briefing illustrators for platformer terrain, do not request atomic tiles. Request an **Open-Ended Modular Kit** consisting of 4 distinct asset types:
1. **Platform Slabs (Tread Surface / 中间段)**:
   - Flat horizontal top tread line matching movement expectations.
   - **Open Left/Right Edges**: Do NOT draw closed silhouette borders or drop-shadows on the lateral sides. Slabs must be able to overlap 20–40px horizontally without visual seams.
2. **End-caps (Terminations / 边缘端头)**:
   - Distinct Left and Right finishing stones. Outer side closed with natural cliff/drop contour; inner side open for overlapping with slabs.
3. **Seam-Covering Decals (遮缝挂件 - Critical Polish)**:
   - Small standalone transparent props (grass patches, hanging vines, broken pebbles, moss tufts).
   - Placed by designers directly over overlapping seams between slabs to eliminate visible repetition or transition harshness.
4. **Under-terrain Fillers (底层暗色填充)**:
   - Simple dark/dirt mass textures or vignette blocks to fill empty spaces beneath the upper tread surface.

## 4. Ingesting Monolithic Multi-Asset Sheets (e.g. 5000px Art Drops)
Artists frequently deliver dozens of distinct props and terrain pieces bundled together on a single massive transparent PNG canvas rather than separate exports.

### Workflow A: In-Engine Visual Slicing (Godot Native)
- Do NOT import massive multi-asset sheets into a `TileSet` resource grid.
- Use `Sprite2D` with **`Region`** enabled:
  - Inspector -> `Region` -> `Enabled = true`.
  - Open bottom `TextureRegion` dock -> select `Auto Slice` or pixel snap to click and isolate components visually.
- Alternatively, create reusable `.tres` assets via `AtlasTexture` referencing specific sub-regions.

### Workflow B: Deterministic Alpha Bounding-Box Extraction (Scripted)
- If many components are needed as standalone files, run an offline connected-component analysis on the alpha channel (e.g. via Pillow / scipy in Python).
- Filter out components by area thresholds (e.g. large structures vs small decals) and crop them directly to `res://Art/.../components/` as separate transparent PNGs.

### Workflow C: Repacking Hand-Drawn / Procreate Sheets into Uniform TileSet Atlas
When artists provide a hand-drawn sheet containing platform components (Left caps, Mid surfaces, Right caps, Slopes, Infill walls) plus demonstration markup:
1. **Filter Out Demonstration Blocks**:
   - Detect and discard composite/annotated demo blocks (such as colored translucent assembly guides or multi-tile sample combos).
2. **Lossless Native Pixel Integrity (User Strict Preference)**:
   - **Never Downsample or Compress Without Explicit Consent**: If the artist drew high-resolution art (e.g. ~700×700 per tile), preserve 100% native resolution to avoid softening, blur, or interpolation artifacts.
   - **Derive Natural Grid Width from Mid Slabs**: Calculate the exact pixel width of the repeating middle segments (e.g. 665px or 672px) and use that exact width as the cell width instead of arbitrary round numbers. Arbitrary cell sizes cause either margin padding (gaps) or pixel stretching (distortion).
3. **Align Seams and Eliminate Internal Padding (Pitfall)**:
   - **Do NOT center-pad sliced tiles inside oversized grid cells**: Placing tiles with transparent margins causes gaps/seams when painted in TileMap.
   - **Continuous Mid/Wall blocks**: Must stretch or fill 100% across the cell width ($X=0$ to $X=\text{TILE\_WIDTH}$) so adjacent tiles touch seamlessly.
   - **Left End-caps**: Align right edge flush against cell boundary ($X=\text{TILE\_WIDTH}$) to seamlessly meet Mid pieces; let left edge contour naturally.
   - **Right End-caps**: Align left edge flush against cell boundary ($X=0$) to seamlessly meet Mid pieces; let right edge contour naturally.
   - **Tread Line Alignment**: Align horizontal tread surfaces to the exact same top Y-offset across all pieces so ground contact is level.
4. **Tile-Internal Vertical Anchoring Rules (Ground vs. Ceiling)**:
   - **Ground / Surface Bricks ("上砖块")**: In fixed-size tile cells (e.g. 665×665), ground platform content where characters walk on top must be aligned to the **bottom half / bottom edge** of the cell (`y = cell_h - content_h`). This ensures that the solid substrate and base rocks connect flush to the tile row underneath, while characters stand cleanly on the platform plane.
   - **Ceiling / Inverted Bricks ("下砖块")**: Ceiling or hanging platform content must be aligned to the **top half / top edge** of the cell (`y = 0`). This allows the ceiling anchor rocks to connect flush with the solid rock ceiling row above, while the lower rail/edge hangs down into open playable space.
   - **Global Origin Misalignment Pitfall**: Artists working in Procreate/Photoshop often maintain the correct grid step (~665px) between drawn strips but introduce arbitrary top/left canvas margins (e.g. starting at $X=308, Y=333$). Godot slices from $(0, 0)$, cutting mid-platform and destroying all tiles. Normalization requires shifting each strip to integer grid multiples ($X = k \cdot \text{cell\_w}, Y = m \cdot \text{cell\_h}$) with the appropriate vertical anchoring per block type.
5. **Godot TileSet Margins/Separation Fallacy (Why In-Engine Slicing Fails on Heterogeneous Sheets)**:
   - **The Trap**: Attempting to configure `Margins` and `Separation` in Godot's TileSet editor to avoid offline preprocessing.
   - **The Mechanism**: Godot's `Margins` (top-left offset) and `Separation` (inter-tile gutter) are strictly uniform global constants for the entire texture resource. Hand-drawn sheets delivered by artists inevitably contain:
     - Irregular vertical gaps between rows (e.g. 176px vs 184px vs 256px).
     - Mixed component heights (1-tile 480px slabs vs 2-tile 1140px foundations vs multi-tile stairs).
     - Conflicting vertical alignments in the same atlas (ground slabs needing top whitespace vs ceiling slabs needing bottom whitespace).
   - **The Rule**: Never attempt to adjust Godot's built-in Margins/Separation to slice irregular hand-drawn sheets. Always preprocess offline into a standardized 1:1 grid texture where Godot imports with `Margins = 0, 0` and `Separation = 0, 0`.
6. **Non-Destructive File Export Rule**:
   - Never overwrite the original artist asset (`<name>.png`). Always output the normalized grid texture side-by-side with a clear descriptive suffix (e.g. `<name>_grid<size>.png`), preserving original art uncorrupted.
7. **Handling Discrepancy Between High-Res Art vs Low-Res World Grid (e.g. 700px Art vs 32x32 Grid)**:
   - **Pure 1:1 Pixel Downsampling (Only for Retro Pixel Art)**: Downsample atlas to $32 \times 32$ only when explicitly requested.
   - **HD-2D Scale Factor (Default for Hand-Drawn Art)**: Maintain native high-res atlas (e.g. $672 \times 702$ or $665 \times 665$), set TileSet cell size to the native dimensions, and set the `TileMapLayer` node `Transform -> Scale` to target ratio (e.g. $32 / 665$). This preserves full brushwork detail while snapping to the 32-pixel game logic grid.


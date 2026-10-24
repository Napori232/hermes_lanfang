---
name: tilemap-normalizer-workflow
description: "Use when normalizing freeform art to Godot tilesets or PNGs."
---

# Tilemap Normalizer & Component Grid Workflow

Standardized procedure for converting freeform, multi-component, or non-grid 2D level art into Godot 4 compatible TileSheet textures, TileSet `.tres` resources, or discrete standalone component sprites.

## 1. When to Use
- Artist provides irregular or free-floating level artwork (e.g. `2.png`, `Component.png`) not sized to integer multiples of the target cell size (e.g. 665×665).
- Assets need to be placed directly into Godot 4 `TileMapLayer` or `TileMap` without manual pixel realignment in the engine.
- Multi-component sheets where distinct visual structures (floating islands, walls, ceilings) are scattered across empty canvas space.
- User requests extracting or breaking down a composite component sheet into clean, individual, semantically-named PNG sprites.
- Preprocessing existing raw level art into `_grid665.png` using the project's dedicated normalizer tool (`tools/tilemap_normalizer/normalizer.py`).

## 2. Component Analysis & Grid Packing Procedure

1. **Deterministic Component Detection**:
   - Do not guess bounding boxes visually.
   - Run connected component labeling via `scipy.ndimage.label` on the alpha channel (`alpha > 10`) to find disconnected structures and their tight bounding boxes `(xmin, ymin, xmax, ymax)`.
   - Filter out alpha noise/dust by checking component area (`area > 1000 px`).
   - Categorize components into:
     - **Major Terrain / Platforms**: Structures with $w \ge 300$ or $h \ge 200$.
     - **Decals & Small Props**: Small items ($w < 300$ and $h < 200$), assigned to single $1 \times 1$ cells.

2. **Grid Cell Allocation**:
   - Given target cell dimension $S$ (e.g. 665 px):
     $$\text{req\_cols} = \lceil w / S \rceil, \quad \text{req\_rows} = \lceil h / S \rceil$$
   - Each component is assigned a dedicated bounding cell footprint: $\text{req\_cols} \times \text{req\_rows}$.

3. **Alignment Strategy**:
   - **Ground / Platforms / Surface Structures**: Anchor to bottom (`align = 'bottom'`). The bottom boundary touches the bottom edge of its allocated cell grid (`y_offset = cell_y + (req_rows * S - h)`), ensuring walking surfaces seamlessly match terrain cell boundaries.
   - **Ceilings / Stalactites / Overhead Rocks**: Anchor to top (`align = 'top'`).
   - **Decals / Props**: Center inside the allocated cell (`align = 'center'`).
   - **Horizontal Positioning**: Anchor to left (`x_offset = cell_x`) across consecutive columns.

4. **2D Bin-Packing Layout (Fixed Max Columns)**:
   - Fix canvas width to match project standard column count (e.g. 10 columns for $6650 \text{ px}$ width, matching `1_grid665.png`).
   - Maintain a 2D boolean grid map `grid_map[rows, cols]`.
   - Placement priority order to minimize wasted vertical space:
     1. Large monolithic structures (e.g., L-shaped cave walls, large background plates).
     2. Remaining major platforms sorted descending by $(\text{req\_rows}, \text{req\_cols})$.
     3. Decals and small $1 \times 1$ props filling remaining gaps.
   - Output normalized texture named `<source>_grid<S>.png` (e.g. `3_grid665.png`).
   - Never overwrite the original source image.

## 3. Standalone Component Extraction & Semantic Splitting

When the goal is to decouple a multi-asset sheet into individual PNG components for scene props or level prefabs:

1. **Tight Bounding-Box Cropping & Intent Disambiguation**:
   - Clarify whether the user wants a **single modular grid tile / cell** (e.g. 665×665 tile for TileSet) or the **entire assembled/composite structural prefab** (the complete visual block/island drawn in the artwork).
   - If user asks for an assembled asset ("组装好的/一整个"), look at the raw art sheet (`<id>.png`) rather than the packed TileSet atlas (`<id>_grid<S>.png`), and crop the entire connected component.
   - For every detected component or designated region, find the non-zero alpha bounding box:
     ```python
     alpha = np.array(crop.getchannel('A'))
     rows = np.any(alpha > 10, axis=1)
     cols = np.any(alpha > 10, axis=0)
     ymin, ymax = np.where(rows)[0][[0, -1]]
     xmin, xmax = np.where(cols)[0][[0, -1]]
     tight = crop.crop((xmin, ymin, xmax + 1, ymax + 1))
     ```
   - Add a small safety padding (e.g. 10~20px transparent margin) around standalone organic components (water, clouds, glowing VFX) so that edge glows, refractive caustics, and anti-aliased contours are not clipped flush by the canvas boundary.

2. **Composite Disentanglement & Overlap Handling**:
   - Complex sheets often place interactive items (steles, desks, fountain basins) resting on or intersecting terrain/platforms.
   - Do not force destructive separation if artwork edges overlap without backing texture.
   - Dual-export strategy:
     - Export both the decomposed sub-elements (e.g. `prop_desk_scholar_standalone.png`, `mechanism_stele_ground_standing.png`) AND the functional combined prefab cluster (e.g. `prop_scholar_fountain_desk_cluster.png`, `terrain_scholar_station_ground_composite.png`).
     - Level designers can choose between zero-gap composite clusters or freeform modular placement.

3. **Semantic Naming Taxonomy**:
   Use strict `<category>_<type>_<descriptor>_<variant>.png`:
   - `platform_`: Walkable platforms and beams (`platform_floating_rock_upper.png`, `platform_stone_beam_long.png`).
   - `architecture_`: Architectural elements (`architecture_door_carved_wood.png`, `architecture_pillar_stone_stacked.png`).
   - `mechanism_`: Puzzles, switches, steles, dials (`mechanism_stele_dial_slot_0.png`, `mechanism_pin_lever_1.png`).
   - `prop_`: Environmental objects and decor (`prop_desk_scholar_standalone.png`, `prop_book_stack_two.png`, `prop_pebbles_cluster.png`).
   - `terrain_`: Base landscape blocks (`terrain_dark_soil_pebble_platform.png`).
   - `key_`: Interactive inventory/unlock keys (`key_gold_curl.png`).
   - `fx_`: Visual effects and water streams (`fx_waterfall_cascade_streams.png`).
   - `vehicle_`: Transportation assets (`vehicle_boat_wooden_rowboat.png`).
   - `rune_`: Symbols and magic emblems (`rune_circle_emblem.png`).

4. **Draft Annotation Filtering & Swatch Cleaning**:
   - Concept art and raw component sheets often contain draft artifacts (swatch chips, reference color squares, numeric asset IDs like "32" in corners). Explicitly identify and exclude these annotations rather than exporting them as sprite files.
   - **Isolated Grid / Swatch Removal Protocol**:
     1. **Automatic Backup**: Always save a backup copy (`<file>.png.bak`) prior to modifying or overwriting any asset.
     2. **Color & Geometry Detection**: Identify swatches by geometry (exact standard dimensions like $32 \times 32$ or $16 \times 16$) or isolated color masks, separated from main artwork by empty alpha.
     3. **Visual Perspective / Coordinate Discrepancies**: User descriptions of visual position ("右上角", "左上角") frequently mix up left/right or refer to inverted engine viewpoints. Always scan candidate corners for anomalous uniform-color blocks across the whole canvas rather than assuming exact coordinate quadrant.
     4. **Composite Draft Cluster Clearance**: Never erase ONLY the colored square. Draft swatches routinely carry associated annotations (handwritten dimension labels, asset index numbers, brush test marks) directly underneath or adjacent to them. Detect the entire isolated corner cluster (all non-zero alpha pixels in that empty corner region) and clear the whole cluster to RGBA `(0, 0, 0, 0)`.
     5. **Transparent Clearance**: Clear the target bounding box to RGBA `(0, 0, 0, 0)` rather than painting over with background color.
   - Check existing files in the target directory (e.g. `extracted/`) prior to slicing to avoid duplicating components already processed in previous passes.
   - Inspect boundary cuts: note any structural truncation where an asset touches canvas edges (e.g. pillar bases or splash bottoms clipped flat by canvas bounds) and document these placement constraints for designers.

   5. **Raw Export Image Triage & Pre-processing (Camera/Drawing App Exports)**:
   - Artists frequently export unprocessed slices with default names like `IMG_xxxx.PNG` or `Image_xxxx.png` containing excess transparent padding (e.g. 50%~80% empty area) or oversized dimensions (e.g. 60M+ px raw canvases).
   - **Triage Checklist**:
    1. **Name Normalization**: Rename to snake_case descriptive names before scene hookup (e.g. `ancient_crown.png`, `stone_well.png`).
    2. **Alpha Crop (Tight Bounding Box)**: Trim empty outer transparency so Sprite2D offsets/anchors and collision boxes stay centered on real pixels.
    3. **Oversized Canvas Check**: Flag images exceeding 4K/8K dimensions (e.g. 6346×9913) that would exhaust GPU texture memory in Godot; extract individual modular structures or downscale.
    4. **Scene Reference Audit**: Always grep code/scene files (`.tscn`, `.tres`, `.gd`) for old filenames before renaming or deleting matching `.import` metadata.

   6. **Output Isolation**:
   - Always export to a dedicated subfolder (e.g. `<source_dir>/extracted/`). Never pollute the raw art source directory or overwrite source sheets.

## 4. Python Execution Snippet

Run directly via `uv run` to guarantee dependencies:
```bash
uv run --with pillow --with numpy --with scipy python -c "
from PIL import Image
import numpy as np
from scipy import ndimage

im = Image.open('path/to/source.png')
alpha = np.array(im.getchannel('A')) > 10
labeled, n = ndimage.label(alpha)
objs = ndimage.find_objects(labeled)
# Extract components, calculate grid cells, apply 2D bin-packing, and save
"
```

## 4. Godot 4 TileSet (`.tres`) Generation

Generate or patch the matching `.tres` resource pointing to the normalized texture:
- `texture_region_size = Vector2i(S, S)`
- `tile_size = Vector2i(S, S)`
- Register active tiles explicitly (`{c}:{r}/0 = 0`) only for cells containing visible content.
- Ensure `physics_layer_0/collision_layer = 1` is configured so physics collision shapes can be added or mapped directly.

## 5. Pitfalls & Guardrails
- **Packed Atlas vs. Original Art Disambiguation**: When an asset directory contains both `<id>.png` (original illustration / composite art) and `<id>_grid<S>.png` (chopped TileSet atlas), distinguish between modular grid tiles and assembled prefabs:
  - "切单格 / 瓦片 / Tile" $\rightarrow$ 从 `_grid<S>.png` 切割 $S \times S$ 单格。
  - "提取完整的 / 组装好的 / 整个水块" $\rightarrow$ 必须从原始 `<id>.png` 切割完整的连续图块组件（Connected Component），不要误切 TileSet 内部的单个拼块。
- **Project Normalizer Tool**: Check `tools/tilemap_normalizer/normalizer.py` first when user asks to preprocess/normalize level maps (`map0`, `map1`, etc.). It automatically splits rows, calculates cell requirements ($S=665$), anchors bottom, and generates `<source>_grid665.png`.
- **Python Environment Mismatch**: The MSYS/bash default python on this host lacks numpy/pillow. Use `C:/Users/Napori/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe` or `uv run --with pillow --with numpy` when running normalizer or image processing tasks.
- **Native vs. MSYS Python Packages**: When running PIL/scipy scripts on Windows environments where the default interpreter lacks graphics packages, invoke dynamically via `uv run --with pillow --with numpy --with scipy python`.
- **Do not simply stack rows vertically**: Stacking rows vertically produces excessively tall images that exceed GPU texture limits. Always pack into a bounded column grid (e.g. 10 columns $\times$ $N$ rows).
- **Godot Project Protection**: Do not hand-edit existing scene files (`.tscn`) or script files (`.gd`) to replace TileMap references unless explicitly instructed or delegated through the appropriate coding protocol.

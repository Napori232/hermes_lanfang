---
name: tilemap-terrain-synthesis
description: "Use when synthesizing 2D autotile terrain from art."
---

# 2D TileMap Terrain & Autotile Synthesis Pipeline

Guidelines and automated workflows for synthesizing standardized 2D TileMap autotiles (convex outer corners, concave inner corners, edges, and fill) from hand-drawn modular art strips and composite illustrations.

## 1. Problem Definition: The Autotile Corner Gap
Hand-drawn art sheets (e.g. Procreate / Photoshop platformer kits) typically provide:
- Horizontal platform strips (Left cap, Mid repeating slab, Right cap)
- Vertical pillars or cliff edges
- Detached stairs or decorative elements

When imported into Godot 4 TileSet Terrain systems (Match Corners & Sides / 3×3 Minimal / 47-blob), drawing turning tunnels, vertical pits, or enclosed chambers fails because raw linear strips lack topological corner transitions:
- Missing **Convex Outer Corners**: Floor abruptly ending into a downward vertical wall.
- Missing **Concave Inner Corners**: Floor meeting an upward vertical wall at a 90° concave junction.

## 2. Standard 16-Tile Minimal Autotile Kit Topology
Every standardized terrain box requires 16 foundational tiles (at uniform cell resolution, e.g. 665×665):

```
【3×3 Outer Shell (9 tiles)】
Top-Left Outer    | Top Edge (Floor)    | Top-Right Outer
Left Edge (Wall)  | Center Solid Fill   | Right Edge (Wall)
Bottom-Left Outer | Bottom Edge (Ceil)  | Bottom-Right Outer

【4 Concave Inner Corners (4 tiles)】
Top-Left Inner    | Top-Right Inner
Bottom-Left Inner | Bottom-Right Inner

【3 Standalone Props (3 tiles)】
Single Pillar     | Single Float Bar    | Isolated Island
```

## 3. Extraction & Compositing Procedure
1. **Determine Exact Grid Size**:
   - Inspect repeating mid segments to find natural pixel width (e.g. 665px). Never guess or arbitrarily downsample; preserve 100% native resolution to prevent blur.
2. **Anchor Vertical Alignments**:
   - Ground/Floor surfaces: Anchor to bottom half of cell (`y = cell_h - content_h`).
   - Ceiling/Overhead surfaces: Anchor to top half of cell (`y = 0`).
3. **Extract Solid Center Fill**:
   - Crop a pure 1×1 cell from deep bedrock/foundation rows with 100% alpha opacity.
4. **Synthesize Convex Outer Corners**:
   - Left-top outer corner: Composite ground left cap with vertical pillar left contour.
   - Right-top outer corner: Composite ground right cap with vertical pillar right contour.
   - Bottom outer corners: Composite ceiling end-caps with vertical pillar bottoms.
5. **Extract Concave Inner Corners from Natural Drop Junctions & Steps**:
   - **Concave Direction Disambiguation**:
     - *Ground Concave Corner (地面凹角 / 坑底转角)*: Floor solid at bottom, vertical wall solid at side, open air transparent above the floor level.
     - *Ceiling Concave Corner (拱顶/天花板凹角)*: Ceiling solid at top, vertical wall solid at side, open air transparent below the ceiling line.
   - **Natural Drop Detection in Composite Level Art**:
     Composite platformer sheets frequently illustrate terrace drops or pit trenches where the elevation difference between the upper terrace surface and pit bottom is an exact integer multiple of grid size $S$ (e.g. $\Delta y = 680 - 15 = 665\text{ px} = S$). In such sheets, row-normalized grids (`_grid<S>.png`) will already contain the raw $1 \times 1$ inner corner at the transition grid coordinates without requiring synthetic multi-layer splicing.
   - **Boundary Alpha Profile Gate for 1×1 Ground Concave Tile**:
     Verify structural integrity on the extracted $S \times S$ cell:
     - Left Wall ($x=0$): $y \in [0, S-1]$ 100% solid wall.
     - Bottom Foundation ($y=S-1$): $x \in [0, S-1]$ 100% solid bedrock.
     - Right Edge ($x=S-1$): $y \in [y_{\text{ground}}, S-1]$ solid; upper span is transparent air.
     - Top Edge ($y=0$): $x \in [0, w_{\text{wall}}]$ solid; rest is transparent air.
   - **Symmetric Left/Right Pair Export**:
     Raw illustrations often only draw one side of a trench or cut off at canvas margins. If shading is ambient/diffuse, horizontally flip (`FLIP_LEFT_RIGHT`) the verified natural corner to export both Left (`inner_corner_ground_left_<S>.png`) and Right (`inner_corner_ground_right_<S>.png`) variants simultaneously so level designers receive complete enclosure pairs.

## 4. Pitfalls & Critical Constraints

### Hand-Drawn Directional Features vs. Programmatic Splicing
- **Directional Trims & Rails**: Hand-drawn platform kits frequently feature continuous horizontal support beams, rails, or layered stone strata. Splicing a horizontal beam with a vertical pillar programmatically cuts the rail mid-air or leaves an orphaned floating ledge.
- **Asymmetric Perspective & Shading**: Hand-drawn stairs have fixed light sources and perspective. Horizontally mirroring or vertically flipping inner step corners often produces lighting contradictions and unnatural jagged silhouettes.
- **Verification Gate**: Always perform visual boundary verification on the assembled composite sheet. If directional rails are clipped or seam artifacts occur at tile borders, programmatic autotiling is unviable without dedicated artist corner pieces.

## 5. Architectural Alternatives When Synthetic Autotile Fails

When raw assets lack native corner wrapping, do not force a broken 3×3 autotile terrain. Choose between two industry standard solutions:

1. **Component/Prop Assembly with Decoupled Collision (Preferred for Hand-Drawn / GameJam)**:
   - Treat platforms, pillars, and ceilings as modular decorative props (Sprite2D / TileMap individual elements) rather than terrain brush tiles.
   - Place stairs, column caps, or rock rubble directly over T-junctions and corners to naturally disguise seams.
   - Decouple visuals from physics: use a dedicated, invisible `StaticBody2D` with coarse collision shapes for gameplay boundaries.
2. **Standardized Corner Asset Specification (For Procedural / Grid-Strict Games)**:
   - Deliver an exact specification to the 2D artist for the missing 4 corner replacement tiles at uniform cell dimensions (e.g. 665×665 px) with the baseline rail height specified:
     - Outer Convex TL / TR: Ground rail curving down into vertical wall contour.
     - Inner Concave TL / TR: Ground rail meeting rising vertical rock wall with seamless corner masonry.
   - Once the artist provides the 4 native corners, batch re-composite the 16-tile sheet using the normalization script.

## 6. Godot Import Rules
- Never use Godot's built-in `Margins` / `Separation` to fix unevenly spaced sheets; global constants cannot handle heterogeneous hand-drawn layouts.
- Always output a pre-aligned grid image (`<name>_autotile_<size>.png`) where `Margins = (0, 0)` and `Separation = (0, 0)`.
- Never overwrite original artist assets.

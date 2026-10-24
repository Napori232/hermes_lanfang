---
name: dual-sprite-mirror-looping-v4
description: "Use when creating seamless loops via sprite mirroring."
version: 1.0.0
---

# Dual-Sprite Mirror Looping (Engine-Level Seamless Solution)

When dealing with organic 2D background illustrations (such as mountain silhouettes, clouds, skies, or vertical cavern/depth scenery in Godot `Parallax2D`) where source textures do not seamlessly loop at the image boundaries:

## 1. Core Rule: Zero Destructive Modifications
- Avoid soft cross-fades, edge blur, or linear alpha feathering on stylized/silhouette art. Blurring destroys native art sharpness and creates obvious ghosting/dissolved seams.
- If edge retouching/cloning is not preferred by the user, handle seamless continuity entirely at the engine layout level.

## 2. Parallax2D Dual-Sprite Symmetry Patterns

### Pattern A: Horizontal Mirror Loop (OutwardScenery style)
1. **Layout**:
   - Inside the `Parallax2D` layer, place two instances of the background sprite:
     - `SpriteA`: `position = Vector2(0, 0)`, `flip_h = false`, `centered = false`
     - `SpriteB`: `position = Vector2(texture_width, 0)`, `flip_h = true`, `centered = false`
2. **Cycle Repeat Size & Multi-Layer Setup**:
   - Set `repeat_size = Vector2(2 * texture_width, 0)`.
   - Set `repeat_times = 4` (or viewport-proportional coverage).
   - **Layer Depth Convention (Back-to-Front)**: Arrange layers in scene tree by ascending `scroll_scale.x` (e.g. Sky/Silhouette: 0.02~0.05, Far Rocks: 0.1~0.2, Mid Dunes/Flora: 0.3~0.5).
3. **Phase Camera Bounds Guard (Prevent Background Bleed)**:
   - In modular or multi-phase stage architectures, background `Parallax2D` will render across the whole viewport regardless of stage bounds unless explicitly visibility-culled.
   - Guard in `_process(_delta)`:
     ```gdscript
     var camera_world := get_viewport().get_canvas_transform().affine_inverse() * (get_viewport_rect().size * 0.5)
     var phase := get_parent() as Node2D
     if phase:
         var camera_x: float = phase.to_local(camera_world).x
         var in_level := camera_x >= bounds.x and camera_x <= bounds.y
         for layer in get_children():
             if layer is Parallax2D:
                 layer.visible = in_level
     ```
4. **Seam Invariance**:
   - Boundary between A and B aligns Right-to-Right (mirrored).
   - Boundary between B and the next repeat of A aligns Left-to-Left (mirrored).

### Pattern B: Vertical Mirror Splicing with Direct Horizontal Splicing
When art needs vertical symmetry (e.g., ground/reflection, vertical descent) while tiling horizontally:
1. **Native Vertical Alignment (Strict Standard: `flip_v = true` + `position.y = texture_height`)**:
   - **Do NOT use `scale = Vector2(1, -1)`**. In Godot, negative scale can invert triangle winding, break 2D culling/sorting, cause negative bounds calculation in `Parallax2D`, and distort canvas shaders.
   - Use standard top-left uncentered sprites (`centered = false`):
     - `Sprite1` (Normal): `position = Vector2(0, 0)`, `flip_v = false`
       - Covers local $y \in [0, H]$. Texture top (head) is at $y = 0$, bottom (tail) is at $y = H$.
     - `Sprite2` (Mirrored): `position = Vector2(0, H)`, `flip_v = true`
       - Covers local $y \in [H, 2H]$. At $y = H$, texture bottom (tail) connects to Sprite1 tail; at $y = 2H$, texture top (head) is ready to cycle into the next repeat's top at $y = 0$.
   - **Horizontal Alignment**: Both sprites MUST share `position.x = 0`. Never apply horizontal stagger or asymmetric offsets between the paired sprites.
2. **Cycle Repeat Size**:
   - Vertical cycle: `repeat_size.y = 2 * texture_height`.
   - Horizontal cycle (direct tiling): `repeat_size.x = texture_width`.

### Pattern C: 2x2 Quad Quadrant Mirror Loop (Full 2D Seamless Symmetry)
When a texture needs seamless symmetry in BOTH horizontal and vertical directions without seams in any direction:
1. **Layout (4 Sprite2D per Parallax2D layer, `centered = false`)**:
   - `Base`: `position = Vector2(0, 0)`, `flip_h = false`, `flip_v = false`
   - `HMirror`: `position = Vector2(W, 0)`, `flip_h = true`, `flip_v = false`
   - `VMirror`: `position = Vector2(0, H)`, `flip_h = false`, `flip_v = true`
   - `HVMirror`: `position = Vector2(W, H)`, `flip_h = true`, `flip_v = true`
2. **Cycle Repeat Size**:
   - `repeat_size = Vector2(2 * W, 2 * H)`.
   - `repeat_times = 4`.

## 3. Critical Engine Mechanics & Pitfalls

### Pitfall 1: Parallax2D `repeat_size` Local Coordinate Rule (Never Double-Scale!)
- In Godot 4, `Parallax2D.repeat_size` is evaluated in the layer's **LOCAL coordinate space**.
- When `layer.scale = Vector2.ONE * factor` is applied, the layer's local content is already scaled in world space by `factor`.
- **FATAL ERROR**: Setting `layer.repeat_size = Vector2(w * factor, h * factor)`. Because the layer itself has `scale = factor`, Godot will repeat the visual at $(w \times factor) \times factor = w \times factor^2$, creating massive empty voids (e.g. 1500+ px horizontal gaps) between repetitions.
- **RULE**: `layer.repeat_size` MUST remain in unscaled texture pixel units (e.g. `Vector2(1152.0, 4036.0)`). Let `layer.scale` handle world transformation.

### Pitfall 2: Fractional Subpixel Float Displacements Cause Light-Bleeding Seams
- In Godot 2D rendering, fractional positions (e.g. `position = Vector2(11.256836, -4.22876)`) cause bilinear texture filtering interpolation errors at sprite borders, creating 1-pixel visible transparent lines or light-bleeding seams between tiled pieces.
- **RULE**: All Sprite2D offsets inside Parallax2D MUST be exact integer multiples of dimensions: strictly `Vector2(0, 0)`, `Vector2(W, 0)`, `Vector2(0, H)`, or `Vector2(W, H)`. Never leave fractional float offsets.

### Pitfall 3: Sub-Scene Root Coordinate Drift Causes False Camera Bounds Culling
- When instantiating a Scenery scene into a level/phase scene, accidentally dragging or offsetting the scenery instance in the 2D editor (e.g. `position = Vector2(23584, -2445)`) breaks camera detection scripts that use `phase.to_local(camera_world)`.
- If the scenery instance node is shifted far away, bounds checking calculates that the camera is outside the stage, setting `visible = false` and making the entire background vanish upon entering the stage.
- **RULE**: Always verify that background scenery instances are mounted at `position = Vector2(0, 0)` with default `scale = Vector2(1, 1)` in their parent stage scenes.

### Pitfall 4: Component State Query Integrity
- When higher-level orchestrator nodes (e.g. Chasers, Bosses, Controllers) poll movement sub-components (such as `DirectionalChaseMover.IsActive()`), verify that the underlying component actually exposes that public getter. Missing helper methods crash execution during runtime physics steps.

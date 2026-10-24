---
name: dual-sprite-mirror-looping-v3
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
     - `SpriteA`: `position.x = offset`, `flip_h = false`
     - `SpriteB`: `position.x = offset + texture_width`, `flip_h = true`
2. **Cycle Repeat Size**:
   - Set `repeat_size.x = 2 * texture_width`.
   - Set `repeat_times = 1` (or appropriate viewport coverage multiplier).
3. **Seam Invariance**:
   - Boundary between A and B aligns Right-to-Right (mirrored).
   - Boundary between B and the next repeat of A aligns Left-to-Left (mirrored).

### Pattern B: Vertical Mirror Splicing with Direct Horizontal Splicing
When art needs vertical symmetry (e.g., ground/reflection, vertical descent) while tiling horizontally:
1. **Vertical Symmetry (flip_v or scale.y = -1)**:
   - For vertical symmetry within each tile:
     - `SpriteTop`: `position.y = 0`, `flip_v = false` (or `scale = Vector2(1, 1)`)
     - `SpriteBottom`: `position.y = 2 * texture_height`, `scale = Vector2(1, -1)` (or `position.y = texture_height`, `flip_v = true`)
     - *Offset rule with scale.y = -1*: If using `scale = Vector2(1, -1)`, the origin is at the bottom, so `position.y` must be set to `2 * texture_height` (or `2 * texture_height + local_offset.y`) to mirror directly underneath `SpriteTop`.
   - Repeat period vertically: `repeat_size.y = 2 * texture_height`.
2. **Horizontal Direct Splicing**:
   - Horizontal direction directly abuts without horizontal flipping (`repeat_size.x = texture_width`).
   - Set `repeat_times = 2` (or sufficient repetitions) to guarantee full screen wrap coverage.

## 3. Dynamic Scaling and Parallax Scaling Pitfalls
- **Dynamic Scale Adjustments**: When `Parallax2D` is scaled via code (e.g. `layer.scale = Vector2.ONE * factor`), ensure `repeat_size` is updated synchronously (`layer.repeat_size = Vector2(w * factor, 2 * h * factor)`). Mismatched `repeat_size` and visual scale causes overlapping ghost layers or premature viewport clipping.
- **Shader Compatibility**: When attaching custom canvas item shaders (e.g., player proximity alpha masks) to mirrored sprites, pass world positions or calculate `world_pixel = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy` in `vertex()` to ensure coordinate continuity across the mirrored boundaries.

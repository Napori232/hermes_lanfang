---
name: dual-sprite-mirror-looping
description: "Use when creating seamless horizontal parallax loops."
version: 1.0.0
---

# Dual-Sprite Mirror Looping (Engine-Level Seamless Solution)

When dealing with organic 2D background illustrations (such as mountain silhouettes, clouds, or skies in Godot `Parallax2D`) where source textures do not seamlessly loop at the horizontal boundaries:

## 1. Core Rule: Zero Destructive Modifications
- Avoid soft cross-fades, edge blur, or linear alpha feathering on stylized/silhouette art. Blurring destroys native art sharpness and creates obvious ghosting/dissolved seams.
- If edge retouching/cloning is not preferred by the user, handle seamless continuity entirely at the engine layout level.

## 2. Parallax2D Dual-Sprite Symmetry Pattern
1. **Layout**:
   - Inside the `Parallax2D` layer, place two instances of the background sprite:
     - `SpriteA`: `position.x = offset`, `flip_h = false`
     - `SpriteB`: `position.x = offset + texture_width`, `flip_h = true`
2. **Cycle Repeat Size**:
   - Set `repeat_size.x = 2 * texture_width`.
   - Set `repeat_times = 1` (or appropriate viewport coverage multiplier).
3. **Seam Invariance**:
   - The interior boundary between Sprite A and Sprite B aligns Right-Edge to Right-Edge (mirrored), making boundary colors, alpha values, and contour heights mathematically identical.
   - The cyclic boundary between Sprite B and the next repeat of Sprite A aligns Left-Edge to Left-Edge (mirrored), also mathematically identical.
   - Result: 100% seam-free continuous scrolling across infinite horizontal space with native texture resolution preserved.

---
name: dual-sprite-mirror-looping-v2
description: "Use when creating seamless horizontal parallax loops."
version: 1.1.0
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

## 3. Celestial & Landmark Elements Isolation
- **Non-repeating objects (Sun, Moon, unique landmarks)**:
  - Do NOT place unique celestial bodies inside repeating Parallax2D mirror layers. Mirroring duplicates them in reverse orientations and repeats them across cycles.
  - Extract the celestial object as a standalone `Sprite2D` or independent non-repeating node directly under the scenery root (or a Parallax2D with `repeat_size = Vector2.ZERO`).
  - Set explicit `z_index` to position it correctly between visual layers (e.g., between Sky and Mountains).

## 4. Script & Lifecycle Safeguards
- **Inspect parent script hooks**:
  - Check whether a parent class (e.g., `ParallaxScenery.gd`) overrides `_enter_tree()` or `_ready()` to programmatically inject hardcoded `repeat_size`, `region_rect`, or `top_level = true`.
  - In Godot, script initialization hooks execute after `.tscn` serialization and can silently overwrite custom `repeat_size` values back to stale legacy constants.
  - Override the offending lifecycle method (e.g., `func _enter_tree(): pass`) in the subclass when replacing legacy cropped layouts with full-width mirror loops.

## 5. Editor Sync & Disk Overwrites
- Check if Godot Editor is actively running with the target `.tscn` open before modifying scene files on disk. If the editor holds the scene in memory, it may overwrite external disk edits on window refocus or save. Prompt for reload or close when updating complex scene hierarchies.

---
name: game-design-resource-alignment
description: "Use when aligning game design assets and Lead Artist handoff"
version: 1.1.0
---

# Game Design Resource Alignment & Hand-off Rules

Rules for coordinating asset requirements, narrative text, and discipline boundaries during game development sprints.

## 1. Single Point of Contact (Lead Artist Interface)
- **Direct Interface**: The Lead Designer/Planner interfaces exclusively with the **Lead Artist (主美)** regarding art assets, music/audio, and narrative integration.
- **No Multi-Channel Fracturing**: Do not simultaneously interface with three or more individual contributors (e.g. concept artist, animator, composer). All asset scoping, prioritization, and workload allocation must be routed through and managed by the Lead Artist.

## 2. Collaborative Asset List Definition
- **No Isolated Specification**: Lists for visual assets, audio/music tracks, and narrative scripts must NEVER be written or typeset in a silo by the designer alone.
- **Procedure**:
  1. Hold a structured alignment discussion with the discipline owners (via Lead Artist).
  2. Confirm technical constraints, feasibility, style, and quantity.
  3. Only after mutual consensus is reached, typeset and finalize the formal asset/narrative requirement sheet.

## 3. Art Asset Naming & Directory Conventions (Engine Hand-off Hygiene)
- **Directory Structure & Case Consistency**:
  - Enforce uniform directory casing across the art repository: prefer `snake_case` (e.g. `underground_library/`, `character/`, `platforms/`) to avoid cross-platform Git case collisions (Windows vs Linux CI).
  - Fix typos early (e.g. trailing letters or misspelled folder names) before scene trees hardcode paths.
- **Timestamped Slice Ingestion Pitfall**:
  - Raw slices or exports frequently retain screenshot/tool timestamps (e.g. `2026-10-09 204306.png`). Never leave timestamped files in source directories.
  - Classify slices into either **Scene Parallax Layers** (`{scene}_layer_{01..n}.png` / `{scene}_bg`, `{scene}_midground`, `{scene}_foreground`) or **Props/Interactive Components** (`prop_{name}_{variant}.png`), matching game design layout intentions.
- **File Extension & Duplicate Cleanup**:
  - Enforce strictly lowercase file extensions (`.png`, `.ogg`, `.wav`). Mixed `.PNG` and `.png` trigger subtle tracking bugs and duplicate imports on case-insensitive Windows filesystems.
  - Intercept and resolve OS duplicate suffixes like `(1)` (e.g. `movingplatform(1).png` -> either deduplicate and remove, or assign semantic variant suffix `_alt.png`).
- **Godot `.import` Integrity**:
  - Renaming or reorganizing assets requires synchronizing or cleaning associated `.import` files. Dangling `.import` files with missing source textures cause Godot editor startup reimport warnings and broken scene references.

## 4. Audio & SFX Requirement Scoping (Component & System Audits)
- **Multi-Project Ambiguity Check**: If the user asks for asset/sound requirements without naming the project, **explicitly verify which project/repository is in scope** (e.g. `Napori_Game` vs `TapTapspotlight` / GameJam) before auditing or generating lists. Avoid guessing a project based on recency alone.
- **Inspection First**: When auditing an existing Godot project for sound effects/music requirements, directly inspect scene trees (`.tscn`), UI trees, and event triggers/signals (`_on_pressed`, state changes, animation frames) before proposing lists.
- **Format Specifications**:
  - **Short Sound Effects (SFX / UI / Combat)**: Default to uncompressed `.wav` (low latency, zero decode overhead).
  - **BGM & Ambient Loops**: Default to `.ogg` (Vorbis) (efficient compression and memory footprint).
- **Audio Architecture Requirements**:
  - Always design around dedicated Godot Audio Buses (`Master` -> `BGM`, `SFX`, `UI`) in `default_bus_layout.tres`.
  - For rapid/repetitive triggers (hover, footsteps, jump, rapid clicks), mandate pitch modulation (e.g. `pitch_scale = randf_range(0.93, 1.07)`) and multiple variant assets to eliminate "machine-gun" acoustic fatigue.
- **Priority Tiering**: Group audio needs into `P0` (core action feedback: jump/fall/hit/land/confirm), `P1` (secondary mechanisms: platforms/traps/state changes), and `P2` (ambient/polish: hover/particles/transitions).

## 4. Narrative Copy vs Tutorial Separation
- **Worldbuilding Context**: Narrative copy for abilities, mechanics, and UI items must convey immersive worldbuilding and flavor context.
- **Strict Boundary**: Do not write dry control tutorials, keybinding prompts, or mechanical how-to instructions in place of narrative text.

## 5. Camera Viewport & Character Scale Alignment
- **Quantitative Scale Specs**: When defining character and entity art specifications, always ground them against the camera viewport (e.g. 1152×648):
  - Record the vertical and horizontal ratio relative to the camera viewport (e.g., character height occupying 1/5.5 ~ 1/6 of screen height).
  - Explicitly specify in-engine display pixel bounds (e.g. 108~115px) versus raw source sprite canvas dimensions (e.g. 128×128 or 256×256 px) to ensure crisp downscaled edges without blur.
  - Detail visual feedback mechanisms for state transitions (e.g. dehydration/exhaustion: luminance drop, desaturation, totem dimming).

## 6. Visual Anchoring & GDD Target Routing
- **Default GDD Destination**: In this environment, references to the game design document ("策划案" / GDD) default strictly to the online **Feishu (飞书) Cloud Document (Docx/Wiki)**, not local `.docx` files.
- **Dual Pipeline for Feishu GDD Updates**:
  1. Append/update formatted text and markdown tables using `lark-cli docs +update --doc <token> --command append --doc-format markdown --content <file_or_string>`.
  2. Directly follow up by inserting corresponding concept and measurement images using `lark-cli docs +media-insert --doc <token> --file <local_path> --caption "<caption_text>"`.
- **Direct Visual Demonstrations**: When updating game design documents with art and character guidelines, always embed the actual concept art and camera viewport prototype reference images directly into the document. Never rely solely on textual descriptions for visual style and scaling.

## 7. Narrative Asset Audit & Gap Analysis (Art Completion Verification)
- **Three-Tier Completion Classification**: When auditing narrative and interactive props against design documents or plot scripts, strictly classify items into three buckets:
  1. **已有独立美术资产 (Available/Done)**: Confirmed standalone texture/sprite in `Art/` (or extracted slice components) matching the specific narrative description.
  2. **仅代码/矢量/通用占位 (Placeholder/Incomplete)**: Exists in scene `.tscn` but uses procedural geometry (`Polygon2D`, `Line2D`), engine flat boxes (`StyleBoxFlat`, `ColorRect`), or generic recycled props without narrative-specific features.
  3. **完全缺失 (Missing/Unstarted)**: No dedicated sprite, slice, scene node, or animations created yet.
- **Node-Type Inspection Pitfall**: Never assume an asset is "drawn" just because a `.tscn` exists (e.g. `Tent.tscn`, `PictureBook.tscn`). Inspect the node definitions inside `.tscn`: procedural polygons and bare text containers are developer prototypes, not artist deliverables.
- **Full-Screen / Popup UI Art Coverage**: Check detailed inspection UI layers (e.g., opened picture books, journal manuscript popups). Dialog code and text labels alone do not satisfy narrative art requirements; they require parchment backgrounds, ornate borders, or thematic illustrations.

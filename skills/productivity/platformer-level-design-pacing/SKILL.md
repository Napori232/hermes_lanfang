---
name: platformer-level-design-pacing
description: "Use when designing platformer level pacing and chase scenes."
version: 1.0.0
---

# Platformer Level Design Pacing & Chase Sequence Design

Guidelines and workflows for 2D platformer level design, pacing curves, action beat mapping, and chase/escape sequence blockouts.

## 1. Chase Sequence Core Constraints

### Duration & Cognitive Load
- **Ideal Duration**: 45 to 70 seconds for non-checkpointed tutorial/exam escapes; 70 to 90 seconds for milestone climaxes.
- **Hard Ceiling**: 90 seconds for seamless zero-checkpoint chases. Anything beyond 90 seconds causes thumb and attentional fatigue.
- **Retry Economics**:
  - In a two-phase level (tranquil outward journey -> sudden high-tension chase), the checkpoint **must** be set at the trigger moment (picking up the relic/bone).
  - Never force players to re-traverse the slow outward journey upon death during the escape run.

### Timing & Placement in Game Loop
- **Mastery Prerequisite**: A chase sequence is a high-stress exam of **known** mechanics. Never introduce a brand new mechanic inside a high-speed chase. All core verbs (grappling hook, dash, double jump) must be taught in the outward tranquil section.
- **Avoid Mechanical Clutter in Tranquil Phase**: Do not pack dense interactive props solely to pad out playtime in the outward journey. Use 2~3 focused, low-risk puzzles to build muscle memory before triggering the reversal.

## 2. Two-Phase Level Architecture (Outward vs. Return / Chase)

When designing a level that shares a spatial corridor between an outward journey and an escape run:

### Node Structure & Hierarchy
Organize level entities into phase containers under the level root:
```text
LevelRoot
├── OutwardPhase (Node2D)        # Outward tranquil mechanics & visual layers
│   ├── OutwardVisualTileMap
│   ├── OutwardPhysicsTileMap
│   └── OutwardProps (boat, teaching anchors)
└── ReturnPhase (Node2D)         # Chase/escape traps, hazards, collapsed terrain
    ├── ReturnVisualTileMap
    ├── ReturnPhysicsTileMap
    ├── PursuerEntity
    └── Traps & CollapsingPlatforms
```

### Runtime Switching Rule
- Toggle entire phase containers via `visible` AND `process_mode = Node.PROCESS_MODE_DISABLED` to cleanly disable physics checks, collisions, and tick scripts in one call without iterating child nodes.
- When triggering the return phase:
  ```gdscript
  outward_phase.visible = false
  outward_phase.process_mode = Node.PROCESS_MODE_DISABLED
  return_phase.modulate.a = 1.0
  return_phase.visible = true
  return_phase.process_mode = Node.PROCESS_MODE_INHERIT
  ```

### Editor Ghost Overlay Workflow
- During level design, set `ReturnPhase.modulate.a = 0.2 ~ 0.3` and lock the container node in the scene tree.
- This creates a faint reference overlay in the 2D editor viewport, allowing precise alignment of the outward path against the return hazards without accidental selection.

## 3. Four-Movement Chase Beat Structure (90s Template)

| Movement | Duration | Mechanics Focus | Level Geometry & Environment Beat | Psychological State |
| :--- | :--- | :--- | :--- | :--- |
| **I. Breakout & Acceleration** | 15 ~ 20s | Basic traversal (Sprint, Double Jump, Dash) | Wide horizontal line, single-direction collapsing ground/bridge. Wide platform tolerances. | Clear escape direction, transition from stillness to urgent movement. |
| **II. Vertical Climb & Flow** | 20 ~ 25s | Core signature mechanic + Wall jump | Vertical/stepped climb. Funneling pathways, momentum boosters (e.g. water-wall launch). | Rhythmic mastery, pulling distance away from pursuer. |
| **III. Mid-Air Swing & Micro-Branch** | 25 ~ 30s | Traversal tools (Grapple hook, air corrections) | High-altitude chasm. Binary micro-branch (high-speed skilled path vs lower safe recovery path, re-merging in 3-5s). No true dead ends. | Visual vertigo, exhilarating speed flow. |
| **IV. Climax Dash & Safe Release** | 15 ~ 20s | Full kit combo chain | Approaching visual abyss/final door. Final environmental collapse, screen pressure maxed, leap into exit/cutscene trigger. | Tension release and emotional high. |

## 3. Greybox Blockout Workflow (Engine-First)

1. **Beat Map on Paper**: Sketch mechanic chains linearly: `[Start] -> (Double Jump) -> (Wall Jump) -> (Branch High/Low) -> (Tool) -> [Goal]`. Do not draw tiles or decorative props.
2. **Godot Blockout (`StaticBody2D` / CSG)**:
   - Create a dedicated test scene (e.g. `Chase_Sequence_Test.tscn`).
   - Use flat solid color blocks with distinct contrast.
   - Set collision boxes based on player character run speed ($px/s$) to lay out a 1500~3000px runway.
3. **Pursuer "Rubber-Band" Pacing**:
   - The pursuer kill plane or hazard line should run ~10% slower than player max speed on straight lines.
   - Close in slightly during vertical or obstacle sections to generate audio-visual pressure without causing unfair insta-death.
4. **Blind-Run Verification**: The designer must be able to run the route smoothly 3 times in greybox without visual hitches before handing off to art for dressing.

## 4. Visual Handoff & Art Specification for Environmental Hazards (Avalanche, Storm, Creeping Blight)

When handing off chase hazard art specs to artists, prevent single-illustration/Boss monster deliverables by enforcing structural modularity:

### Core Art Anti-Patterns to Avoid
- **Isolated Boss Silhouette**: Reject single standalone creature/blob drawings that lack spatial grounding. A chase hazard is an environmental killer that devours space, not a target on screen.
- **Centripetal / Inward Scribble**: Inward-coiling shapes look like a stationary ball or mountain. Creeping hazards require centrifugal, forward-reaching tentacles, ink-bleed diffusion, or sprawling mycelium.
- **Static Pyramid Stance**: Upright triangular silhouettes signal immobility. Chase waves require an overhanging forward-toppling crest (wave of snow/water/mud ready to crush downward).

### 3-Layer Asset Modularization Rule
Never ask for a single static full-screen canvas. Require 3 distinct functional layers:
1. **Leading Hazard Edge (The Kill Line / Wave Crest)**:
   - Slice dimensions: Screen height/width $\times 1.3$ (leaving 30% margin for camera shake without exposing bounds).
   - Visual profile: Overhanging crest + forward-reaching tendrils/flying debris that invade the platform space.
   - Tied directly to the lethal trigger volume (`Area2D`).
2. **Body / Deep Hazard Mass (Tiling / Infinite Fill)**:
   - Seamless loopable or solid procedural fill behind the crest, representing total visual annihilation.
3. **Screen-Space Camera Overlay (Atmospheric Danger Vignette)**:
   - Fullscreen viewport resolution ($1:1$), parented to `Camera2D` or CanvasLayer.
   - Semitransparent creeping edge frost, vignette, or screen-space particle embers indicating proximity to death regardless of world position.

### Handoff Spec Requirements to Deliver to Art
- **Viewport Dimensions**: Explicit logical resolution (e.g., $1920 \times 1080$ or $320 \times 180$).
- **Character & Platform Scale Anchor**: Provide a screenshot containing the player sprite on a standard ledge to serve as a strict pixel scale reference. Hazard crest must dwarf the character ($5 \times$ to $10 \times$ character height).
- **Safe Zone / Screen Ratio**: Keep the visible hazard body to 15%~25% of screen boundary during chase equilibrium, leaving 75% for player reaction and platforming visibility.


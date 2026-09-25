---
name: gamejam-coordination
description: "Use when coordinating GameJam teams, milestones, and assets."
version: 1.0.0
---

# GameJam Coordination & Milestones (21-Day & Short-Sprint)

Procedures for game design leadership, multi-person milestone scheduling, asset handoff tables, and team alignment.

## 1. 21-Day GameJam 3-Stage Milestone Model (7+7+7)

| Stage | Target | Design Deliverables | Discipline Tasks | Gate Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 1 (Days 1–7): MVP Greybox** | Core loop playable & responsive | Lock core mechanic Day 1; issue Asset Request Sheet Day 2; write One-Page GDD | Programmers build core loop & movement with basic shapes; Artists establish style & palette | **Day 7**: Playable greybox with complete core loop |
| **Stage 2 (Days 8–14): Beta Content** | Level rollout & asset integration | Level blockouts, numerical balancing, UI flow, tutorial | Replace greybox assets with full art/SFX; integrate levels and triggers; **Feature Freeze on Day 14** | **Day 14**: Full playthrough available from start to finish |
| **Stage 3 (Days 15–21): Gold Polish & Packaging** | Bug fixing, game feel, build exports | Playtesting feedback logging, prioritize bug severity | No new mechanics permitted; polish visual juice/SFX; first export test on Day 19 | **Day 20**: Gold candidate build; Day 21: buffer for submission |

## 2. Day 1 Silent Proposal & Brainstorming Protocol (8-Person Team)

To prevent endless debates and disengagement in large teams (6–8 people):
1. **Silent Ideation (20–30 min)**: Every member writes 1–2 structured proposals (One-line pitch + Core loop + Art style).
2. **Lightning Pitch & Voting (20 min)**: 2 minutes per person with no counter-arguments. All members cast 3 votes to select Top 2–3 concepts.
3. **Discipline Feasibility Gate (20 min)**:
   - *Programming Lead*: Which mechanics are verifiable in Godot within 3 days?
   - *Art Lead*: Which visual style can be produced at scale within 10 days?
4. **Lead Designer Sign-off (20 min)**: Lead Designer finalizes direction, incorporating rejected ideas as secondary mechanics/easter eggs.

## 3. Lead Designer & Lead Artist Hand-off Boundary

- **Lead Designer**: Supplies functional specs (camera perspective, base pixel/grid sizes, readability constraints, emotional tone keywords, asset priority table).
- **Lead Artist**: Establishes Moodboard, color palette, sprite export rules, task assignment, and final quality control (QC).
- **Team Separation Rule**: Assign artists by asset category (e.g., Artist A = Characters/Monsters, Artist B = Environment/Tilemaps, Artist C = UI/VFX/Illustrations) rather than splitting a single category across multiple artists.

## 4. Asset Request Sheet Template

| Asset Name | Category | Functional Purpose | Spec / Dimension | Priority | Assignee | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `player_move` | Character | 4-direction walk cycle | 32x32 px / 4 frames | P0 (Greybox) | Artist A | In Progress |
| `tilemap_grass` | Scene | Level ground autotile | 16x16 px autotile | P0 | Artist B | Open |
| `ui_healthbar` | UI | HUD top-left player HP | Sliced PNG | P1 (Beta) | Artist C | Open |

## 5. Non-Programmer & Art Git Survival Rules
- **Three-Command Limit**: Restrict non-programmers to `Pull` -> `Insert files` -> `Commit & Push`.
- **GUI Only**: Require GitHub Desktop or Sourcetree; avoid command line.
- **Scene Prohibition**: Non-programmers must never open or edit `.tscn` or `.tres` files directly to avoid merge conflicts. All raw assets remain loose files (`.png`, `.wav`) until integrated.
- **Large Binary Files**: Ensure Git LFS is configured before art asset commit to prevent repository lockups.

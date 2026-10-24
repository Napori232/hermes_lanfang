---
name: game-vfx-scoping-and-implementation
description: "Use when scoping game VFX, particle lists, and code VFX."
version: 1.0.0
---

# Game VFX Scoping & Implementation Guidelines

Procedures and standards for breaking down game visual effects (VFX) into minimal-workload particle asset tables and engineering implementation specs (Code/Shader VFX).

## 1. Workload Minimization & Asset Reuse Principles
- **Minimal Texture Budget**: In game jams or rapid prototyping sprints, avoid demanding unique flipbook sequences or custom sprite sheets for every effect. Standardize on 2~3 monochrome grayscale mask textures (e.g. `fx_dot.png` soft circle, `fx_dust.png` debris/diamond, `fx_ring.png` thin circle ring) and drive color, alpha gradients, and scale dynamically via engine particle materials (`ParticleProcessMaterial`).
- **Engine/Shader-Driven Feedback**: Shift heavy visual burdens from art assets to runtime procedural shaders and code tweens:
  - Material saturation/desaturation, rim lighting, and palette swapping should be handled by 2D canvas item shaders.
  - Periodic states (e.g. breathing glow, heartbeat pulsation) should be animated via runtime `Tween` modulating shader parameters rather than hand-drawn animation frames.

## 2. Dual-Table Specification Structure
When presenting VFX scope and requirements to production and engineering, always split deliverables into two complementary structured tables:

### Table A: Particle Asset & Expression Spec (GPUParticles2D / Art Asset Side)
- **Required Columns**:
  - `特效名称` (VFX Name)
  - `触发情境` (Trigger Context — e.g. entry/exit water, jump, land, idle full state, depleted state)
  - `视觉形态与色彩` (Visual Shape & Palette)
  - `复用贴图` (Reused Texture Mask)
  - `生命周期 / 动力学要点` (Lifetime & Dynamics — e.g. One-shot burst vs continuous emission, velocity, gravity, linear damp)

### Table B: Code & Shader VFX Implementation Spec (Engineering Side)
- **Required Columns**:
  - `程序特效模块` (VFX Module Name)
  - `技术实现方案` (Implementation Approach — e.g. Water 2D Shader, CanvasItem Shader, Tween modulate, Camera2D Shake)
  - `对应触发逻辑 / 参数变化` (Trigger Logic & Parameter Inputs — e.g. Area2D body entered, velocity impulse vector, health/resource scalar)
  - `落地预期效果` (Target In-game Output)

## 3. Physical State & Environmental Transition Boundaries
- **State Transition Closures**: Always account for reciprocal or complementary environmental state pairs:
  - If water/fluid exists: separate specs for **submersion/entry (入水)** vs **emergence/exit (出水)**.
  - Implement drying-off / delay timers (e.g. 0.8s ~ 1.5s lingering dripping particles upon exiting water) to prevent abrupt visual pops.
- **Physical Feel**: Pair key environmental entries and impacts with micro screen shakes (1~2px for 0.1s) and motion damping changes rather than visual-only particles.

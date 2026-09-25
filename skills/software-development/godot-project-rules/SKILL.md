---
name: godot-project-rules
description: "Use when setting Godot architecture, AGENT.md, or standards."
version: 1.0.0
---

# Godot Project Architecture & Coding Standards (AGENT.md)

Best practices for structuring multi-member Godot 4.x projects, isolating modules to prevent Git conflicts, and generating coding-specific AGENT.md guidelines.

## 1. Directory Structure & Scope Boundary

Limit code modifications strictly to `Code/` while treating external asset folders as read-only references:

```text
Code/
├── Autoloads/               # Global singletons (Constants, EventBus, Utils, Data)
├── Common/                  # Reusable base classes and generic components
└── Entities/                # Business logic and entity tree root
    ├── Player/              # Self-contained entity folder (PascalCase)
    ├── Inventory/
    └── Enemy/
```

- **Autonomy & Non-Interference**: Each feature/entity owns a subfolder under `Entities/` containing its scenes and scripts. Teammates work only within their assigned entity folder.
- **Autoloads Immutability**: Prohibit deleting or modifying existing singletons/common utilities; allow only additive extension.

## 2. GDScript & Node Conventions

- **Public vs. Private**: Public methods called outside the script use PascalCase (e.g. `ApplyDamage()`) with `##` doc comments detailing parameters and usage; internal methods use snake_case prefixed with an underscore (e.g. `_calculate_damage()`).
- **Pre-placed Nodes over Code Instantiation**: Favor pre-placing nodes in `.tscn` scene trees and referencing them via `@onready` instead of spawning complex sub-trees dynamically in scripts.
- **Input & Hitbox Standards**:
  - Click detection: Use a `TextureButton` with empty textures.
  - Mouse hover/entry: Attach an `Area2D` + `CollisionShape2D` under `Sprite2D`.
- **UI Anchors**: Explicitly define anchor presets and layout containers for all `Control` nodes to maintain responsiveness across aspect ratios.
- **Unit Testing**: Require each leaf component/entity to be independently testable via F6.
- **Protect Engine Config**: Never alter global project configurations or `.godot/` caching to avoid Git lockouts.

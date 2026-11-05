---
name: software-development
description: "Routing hub for the software-development skill category. Loading this returns the sub-skill index — load the specific leaf skill by name before acting."
version: 1.0.0
---

# software-development (routing hub)

This is a **category**, not a single skill. It carries no executable steps of its own — it
exists so that `skill_view("<category>")` resolves and points at the right leaf skill.

## Sub-skills

| Load name | Skill | Use when |
|---|---|---|
| `codebase-inspection` | codebase-inspection | Inspect codebases w/ pygount: LOC, languages, ratios. |
| `dogfood` | dogfood | Exploratory QA of web apps: find bugs, evidence, reports. |
| `github` | github | GitHub via gh CLI: PRs, issues, reviews, repos, auth. |
| `github-automation-fallbacks` | github-automation-fallbacks | Use when gh CLI lacks scopes or auth fails on Windows. |
| `godot-agent-workflow` | godot-agent-workflow | Use when implementing Godot 4.x scenes, code, and assets. |
| `godot-collision-and-physics` | godot-collision-and-physics | Use when toggling Godot 4.x collisions and phase physics. |
| `godot-component-architecture` | godot-component-architecture | Use when creating zero-intrusion Godot components. |
| `godot-component-usage-and-seams` | godot-component-usage-and-seams | Use when guiding Godot 2D placement or fixing tile seams. |
| `godot-git-conflict-resolution` | godot-git-conflict-resolution | Use when pulling or resolving Git conflicts in Godot. |
| `godot-level-phase-and-respawn` | godot-level-phase-and-respawn | Use when handling Godot level phases, respawns, or debuffs. |
| `godot-mcp-troubleshooting` | godot-mcp-troubleshooting | Use when Godot AI or MCP fails to launch or times out. |
| `godot-project-rules` | godot-project-rules | Use when setting Godot architecture, AGENT.md, or standards. |
| `godot-shader-dissolve-and-effects` | godot-shader-dissolve-and-effects | Use when building Godot 4.x 2D material and screen effects. |
| `godot-workspace-safety` | godot-workspace-safety | Use when protecting Godot workspace and delegating tasks. |
| `hermes-agent-skill-authoring` | hermes-agent-skill-authoring | Author in-repo SKILL.md files: frontmatter and structure. |
| `inspecting-hermes-desktop-dom` | inspecting-hermes-desktop-dom | Read the live Hermes desktop DOM/CSS over CDP. |
| `node-inspect-debugger` | node-inspect-debugger | Debug Node.js via --inspect + Chrome DevTools Protocol CLI. |
| `python-debugpy` | python-debugpy | Debug Python: pdb REPL + debugpy remote (DAP). |
| `requesting-code-review` | requesting-code-review | Pre-commit review: security scan, quality gates, auto-fix. |
| `simplify-code` | simplify-code | Parallel 4-agent cleanup of recent code changes. |
| `spike` | spike | Throwaway experiments to validate an idea before build. |
| `systematic-debugging` | systematic-debugging | 4-phase root cause debugging: understand bugs before fixing. |
| `test-driven-development` | test-driven-development | TDD: enforce RED-GREEN-REFACTOR, tests before code. |

## Rules

- Always load the **leaf** skill, not this hub, before acting — the hub carries no procedure.
- A skill listed with a path prefix (`category/name`) exists because its bare name collides
  with another skill; load it by that exact path.

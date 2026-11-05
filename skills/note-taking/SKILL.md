---
name: note-taking
description: "Routing hub for the note-taking skill category. Loading this returns the sub-skill index — load the specific leaf skill by name before acting."
version: 1.0.0
---

# note-taking (routing hub)

This is a **category**, not a single skill. It carries no executable steps of its own — it
exists so that `skill_view("<category>")` resolves and points at the right leaf skill.

## Sub-skills

| Load name | Skill | Use when |
|---|---|---|
| `obsidian` | obsidian | Read, search, create, and edit notes in the Obsidian vault. |

## Rules

- Always load the **leaf** skill, not this hub, before acting — the hub carries no procedure.
- A skill listed with a path prefix (`category/name`) exists because its bare name collides
  with another skill; load it by that exact path.

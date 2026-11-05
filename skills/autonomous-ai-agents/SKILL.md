---
name: autonomous-ai-agents
description: "Routing hub for the autonomous-ai-agents skill category. Loading this returns the sub-skill index — load the specific leaf skill by name before acting."
version: 1.0.0
---

# autonomous-ai-agents (routing hub)

This is a **category**, not a single skill. It carries no executable steps of its own — it
exists so that `skill_view("<category>")` resolves and points at the right leaf skill.

## Sub-skills

| Load name | Skill | Use when |
|---|---|---|
| `adaptive-context-compression` | adaptive-context-compression | Use when tuning Hermes context compression thresholds. |
| `claude-code` | claude-code | Delegate coding to Claude Code CLI (features, PRs). |
| `codex` | codex | Delegate coding to OpenAI Codex CLI (features, PRs). |
| `codex-delegation` | codex-delegation | Use when delegating coding tasks to Codex CLI. |
| `codex-delegation-protocol` | codex-delegation | Use when delegating coding tasks to Codex CLI. |
| `codex-delegation-temp` | codex-delegation | Use when delegating coding tasks to Codex CLI. |
| `computer-use` | computer-use | Drive the desktop background-first; escalate on signal. |
| `hermes-agent` | hermes-agent | Use, configure, theme, extend, and orchestrate Hermes Agent. |
| `local-model-routing` | local-model-routing | Use when routing simple tasks to local Ollama; verify endpoint behavior first. |
| `local-wechat-secretary` | local-wechat-secretary | Use when configuring local WeChat automation. |
| `opencode` | opencode | Delegate coding to OpenCode CLI (features, PR review). |

## Rules

- Always load the **leaf** skill, not this hub, before acting — the hub carries no procedure.
- A skill listed with a path prefix (`category/name`) exists because its bare name collides
  with another skill; load it by that exact path.
- The Codex delegation channel is **disabled** for this profile: code tasks are implemented
  directly by 兰芳. Do not dispatch to Codex CLI or any other external coding agent
  without the user's explicit confirmation.

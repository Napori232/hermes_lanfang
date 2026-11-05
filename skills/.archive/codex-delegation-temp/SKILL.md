---
name: codex-delegation
description: "Use when delegating coding tasks to Codex CLI."
version: 1.1.0
---

# Codex Delegation Workflow

Hermes dispatches programming tasks to the standalone Codex CLI, which runs with ChatGPT (`gpt-5.5`).

## Execution Principle
- Hermes serves as the dispatcher and scheduler; Codex is the autonomous coding agent.
- Hermes defines the task, scope, and target directory, then delegates to Codex CLI.
- Codex inspects the project, creates/modifies code, executes tests/builds, and returns the result.
- Hermes reports the outcome to the user without duplicating code-level reasoning.
- Rules, instructions, and prompt overrides for Codex should be configured in Codex's own ecosystem (e.g., CC Switch, `~/.codex/config.toml`, project `AGENTS.md`, or Codex skills) rather than duplicated inside Hermes prompts.

## Invocation Pattern
Because Hermes runs in Windows under Git Bash / gateway service context, Windows sandbox constraints require `--sandbox danger-full-access` for Codex child processes:

```bash
codex exec --sandbox danger-full-access "<specific task instructions>"
```

Always execute within the target project directory (`workdir`). For scratch work, ensure a Git repository is initialized first as Codex requires a Git root.

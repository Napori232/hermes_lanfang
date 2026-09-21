---
name: todo-ledger-sync
description: "Use when managing tasks in TODO.md ledger."
version: 1.0.0
---

# Local TODO.md Ledger Sync

Hermes (LanFang) and the local offline WeChat Secretary share a single task file:
`C:\Users\Napori\Documents\WeChatSecretary\TODO.md`

## Principles
1. When user says "做完了X", "完成第Y个", read `TODO.md` and mark matching `- [ ]` as `- [x]`.
2. When user asks "有什么待办", read `TODO.md` and present remaining `- [ ]` items concisely.
3. Both LanFang and the local Qwen offline secretary read/write this file. Zero cloud token waste when idle.

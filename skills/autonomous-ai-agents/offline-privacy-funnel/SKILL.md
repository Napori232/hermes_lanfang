---
name: offline-privacy-funnel
description: "Use when processing private chats with local offline models."
version: 1.1.0
---

# Offline Privacy Funnel (Local Model & Messaging)

Rule for filtering and summarizing high-volume, privacy-sensitive personal communications (e.g., WeChat, IM logs) using local offline models (Ollama/Qwen).

## Core Security Invariant
- **Zero External Network**: Local processing models operate strictly offline on `127.0.0.1:11434`.
- **Data Funnel Principle**: Raw private text stays local. Only structured, anonymized minimal context (JSON briefs/TODOs) is fed into the central Gemini session.

## Workflow Pipeline
1. **Zero-Token Regex Gate**: Pass messages through `local_router.is_trivial_confirmation()`. Trivial receipts (`好的/收到/ok`) are consumed at 0 cost.
2. **Local Context Slicing (Qwen3:8b)**:
   - Run `scripts/local_router.py` (or direct JSON API).
   - Constrained to `format: json` and `num_predict: 128` for fast, deterministic extraction.
   - Extracts `{has_action_item, summary, action_description, is_urgent}`.
3. **Central Ingestion**: Central Agent (Gemini) consumes only the structured JSON result to update TODO or notify user, without loading raw conversation logs into the global context window.

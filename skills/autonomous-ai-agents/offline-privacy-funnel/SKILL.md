---
name: offline-privacy-funnel
description: "Use when processing private chats with local offline models."
version: 1.0.0
---

# Offline Privacy Funnel (Local Model & Messaging)

Rule for filtering and summarizing high-volume, privacy-sensitive personal communications (e.g., WeChat, IM logs) using local offline models (Ollama/Qwen).

## Core Security Invariant
- **Zero External Network**: Local processing models must operate strictly offline on `127.0.0.1`. Never grant web browsing, web search, or outbound internet access to local extraction pipelines.
- **Data Funnel Principle**: Raw messages (chatter, private conversations, sensitive context) stay on the local machine and are digested/discarded locally. Only sanitized, structured actionable items (TODOs, event briefs) may leave the local boundary or reach cloud models.

## Workflow Pattern
1. **Ingestion & Isolation**: Ingest messages locally (e.g., via OS-level automation or local API).
2. **Local Structuring**: Send raw text to local Ollama (`qwen3:8b`) with a strict JSON system prompt requiring message classification and actionable summaries.
3. **Action Routing**:
   - Trivial confirmations: safe canned replies locally if whitelisted.
   - High-risk keywords (money, contracts, passwords): hard-block automated actions; force human review.
   - Summaries / TODOs: deliver to local notification channels or file logs.

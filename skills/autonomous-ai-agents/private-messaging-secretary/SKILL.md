---
name: private-messaging-secretary
description: "Use when managing IM auto-reply and offline info filtering."
version: 1.0.0
---

# Private Messaging Secretary (Local Offline Model)

Rules for ingesting, filtering, and summarizing high-volume, privacy-sensitive communications (e.g., WeChat, IM logs) using local offline models (Ollama/Qwen).

## Core Security Invariants
- **Zero External Network**: Local processing models must operate strictly offline on `127.0.0.1`. Never grant web browsing, web search, or outbound internet access to local extraction pipelines.
- **Data Funnel Principle**: Raw messages stay on the local machine and are digested/discarded locally. Only sanitized, structured actionable items (TODOs, event briefs) may reach human notification channels or cloud models.

## Triage & Reply Invariants
- **Group Chats**: Silent ingestion only. NEVER post automated replies to group chats. Parse announcements, events, deadlines, and action items, then forward summaries privately to the user's report channel.
- **Private Chats**:
  - Trivial pleasantries: Default to safe, zero-commitment acknowledgments (`好的`, `收到`, `嗯嗯`, `OK`).
  - Strict Boundary: NEVER agree to requests, decline offers, make commitments, or give substantive answers on the user's behalf.
  - Urgent or Actionable: If the message involves requests for help, decisions, sensitive topics (money/contracts), or urgent matters, SUPPRESS automated replies and forward immediately for manual review.
  - Blacklist: Specific contacts (supervisors, advisors, VIPs) must be completely exempt from automated replies.

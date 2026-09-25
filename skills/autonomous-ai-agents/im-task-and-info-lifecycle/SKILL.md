---
name: im-task-and-info-lifecycle
description: "Use when filtering IM tasks, whitelists, and alerts."
version: 1.0.0
---

# IM Task & Information Lifecycle Management

Rules and workflows for managing IM message ingestion (WeChat, DingTalk), offline intelligent classification, TODO/event extraction, whitelist skipping, and scheduled alerting.

## Ingestion & Whitelist Principles
- **Default Full Ingestion**: Ingest all messages by default across single and group chats.
- **Exclusion Whitelist (Do Not Read/Process)**:
  - System senders (e.g. `微信团队`, `文件传输助手`, `微信支付`).
  - Muted/folded/family noise groups explicitly listed in configuration.
  - Messages matching the exclusion whitelist are dropped immediately without disk persistence or LLM invocation.

## Offline Processing & Information Distillation
- **Local Model Routing**: Run all message extraction on local offline models (`127.0.0.1:11434`) to prevent private message leakage.
- **Classification Categories**:
  1. `TODO`: Actionable obligations (personal tasks, deliverables). Extract task summary, deadline, priority, and source. Map relative dates (e.g., "this Friday") to concrete ISO timestamps.
  2. `HIGH_VALUE_INFO / EVENT`: Non-actionable announcements, quotas, file releases (`file_notice`), guidelines, policy adjustments, and official notifications. Store in dedicated `message_events` ledger so they remain queryable.
  3. `NOISE`: Greetings, confirmations (`收到`, `好的`), emojis, and general chatter. Drop or flag as noise without LLM overhead.
- **Document & Attachment Parsing**: Use local deterministic extractors (python-docx, openpyxl, xlrd) or designated OCR tools (Quark/local OCR). Never use cloud vision LLMs to speculate on sensitive document contents.

## Storage & Interface Separation
- **Dual Table Schema**: Maintain `todos` (task status, deadline, priority) and `message_events` (sender, chat name, message type, core summary, timestamp) in local SQLite (`secretary.db`).
- **Query Filter Completeness**: Ensure event lookup queries explicitly include all valid event types (`task`, `notification`, `info`, `file_notice`) to avoid accidentally omitting file releases or notices.
- **Interface Exposure**: Expose separate CLI commands (e.g., `cli.py list` for active tasks vs. `cli.py events` for info stream) so users can check background announcements on demand without cluttering active TODO queues.

## Alerting & Reminders
- **Approaching Deadline Check (2h cycle)**:
  - Scan pending tasks periodically (every 2 hours).
  - When remaining time before deadline is between 3.0 and 4.5 hours and not yet alerted, trigger an immediate alert via IM.
- **Daily Summary (16:00 digest)**:
  - Trigger a fixed-schedule briefing at 16:00 covering all active TODOs and significant events.

## Data Retention & Pruning
- Automatically prune expired noise, old events, and completed tasks past the retention threshold to prevent database bloat.

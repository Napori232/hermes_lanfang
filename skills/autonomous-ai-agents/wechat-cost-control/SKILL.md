---
name: wechat-cost-control
description: "Use when optimizing WeChat context token costs and debounce."
version: 1.0.0
---

# WeChat Context Cost Optimization & Debounce

## Context & Token Cost Control
1. **Root Cause of High Token Cost**:
   - Long-lived chat sessions on messaging gateways re-send the full accumulated context on every turn.
   - For users sending fragmented short thoughts, high-frequency bursts multiply repeated context sends rapidly.
2. **Decouple Durable Memory from Conversational Window**:
   - Store critical facts (schedules, tasks, deadlines, user profiles) in persistent storage (`MEMORY.md` / `USER.md`).
   - Treat in-session turns as ephemeral; aggressive compaction will never destroy core facts.
3. **Time-Based Idle Compaction (`idle_compact_after_seconds`)**:
   - Configure `compression.idle_compact_after_seconds` (e.g. `7200` for 2 hours, `14400` for 4 hours).
   - When resuming after idle periods, Hermes automatically compacts stale intermediate conversation history into a concise summary before the first reply, keeping context bounded without user intervention.
4. **Tail Protection & Token Threshold Limits**:
   - Set `compression.protect_last_n` to a lean window (e.g. `4`–`6` turns) so large intermediate command outputs and transient chats exit the protected zone quickly.
   - Clamp `compression.threshold_tokens` (e.g. `12000`) so total sent tokens never balloon to expensive multi-turn limits.
   - Note: In Hermes, editing `compression.*` settings in `config.yaml` is hot-reloaded on the next message without restarting the gateway.
5. **Debounce Configuration**:
   - Inbound typing detection is unsupported by the WeChat bot protocol; rely on `text_batch_delay_seconds` (e.g. `8.0`s) to buffer rapid message bursts.

---
name: local-wechat-secretary
description: "Use when configuring local WeChat automation."
version: 1.0.0
---

# Local WeChat Automation & Information Pipeline

## Architecture & Boundaries
1. **Offline Processing**: Use local offline models (e.g. Ollama `qwen3:8b`) strictly on localhost (`127.0.0.1`) without internet access for sensitive chat message parsing, categorization, and noise filtering.
2. **Auto-Reply Safety Policy**:
   - Default auto-reply must be strictly restricted to zero-commitment acknowledgment phrases ("好的", "收到", "嗯嗯", "OK").
   - Never promise, agree, refuse, or make decisions on the user's behalf.
   - Any message requesting help, borrowing money, asking substantive questions, or displaying urgency must suppress auto-reply and escalate immediately to the user.
   - Group chats are read-only; never auto-reply in groups.
3. **PC WeChat 4.x Architecture Notice**:
   - PC WeChat 4.x (`4.1.x+`) uses Qt 5.15 (`Qt51514QWindowIcon`) and custom hardware rendering (`MMUIRenderSubWindowHW`), breaking legacy Win32 UI-automation hooks like legacy `wxauto`.
   - Prefer protocol gateway / background messaging connectors over fragile UI automation where available.
4. **Debounce for Rapid Inbound Bursts & Typing Protocol Limitations**:
   - Inbound typing state telemetry does NOT exist in the WeChat bot protocol (iLink only supports outbound `sendtyping`). Never attempt to poll or hook user typing events; rely strictly on quiet-period message debouncing (`text_batch_delay_seconds`).
   - Config file edits (`platforms.weixin.extra.text_batch_delay_seconds: 8.0`) are loaded once at startup during `WeixinPlatformAdapter.__init__`. Because the gateway lacks a filesystem config watcher, disk edits require restarting the gateway daemon process.
   - For runtime hot-adjustments without process restart, mutate `adapter._text_batch_delay_seconds` directly on the registered instance in `gateway.platforms.weixin._LIVE_ADAPTERS`.

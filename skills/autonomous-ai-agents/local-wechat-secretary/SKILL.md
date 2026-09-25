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
5. **Asymmetric Communication & Session Expiry Troubleshooting**:
   - **Symptom**: User sees "暂时无法连接openclaw" (temporarily cannot connect to openclaw) in WeChat, or Hermes can push outbound messages but inbound user messages receive no response.
   - **Root Cause**: The WeChat Bot long-polling session expired. When expired, Tencent iLink logs `Session expired; pausing for 10 minutes` and outbound push returns `{"errcode":-14,"errmsg":"session timeout"}`. WeChat's cloud returns "暂时无法连接openclaw" as the default fallback when no active polling client is connected.
   - **Profile Isolation & Environment Overrides**:
     - Hermes accounts live in the active profile directory (`<hermes_home>/weixin/accounts/<account_id>.json`), e.g., `~/.hermes/profiles/<profile>/weixin/accounts/`. Updating base `~/.hermes/weixin/accounts` has no effect on a named profile.
     - Environment variables like `WEIXIN_ACCOUNT_ID` and `WEIXIN_TOKEN` in the shell or profile `.env` take precedence over JSON files. When updating credentials manually or across profiles, ensure matching env vars in both `.env` and the parent process are updated or unset to prevent running with stale tokens.
   - **Windows Gateway Service Startup Pitfall**:
     - Running `hermes --profile <name> gateway start` on Windows attempts to register a startup shortcut in the user's Startup folder via `.vbs` rename, which can trigger `PermissionError: [WinError 5] 拒绝访问`.
     - In non-elevated user environments, run the gateway directly via `hermes --profile <name> gateway run` in the background rather than `gateway start`.
   - **Upstream LLM Provider Empty Stream / 403 on Large Sessions & Auxiliary Compression Provider**:
     - When WeChat long-polling is healthy (`✓ weixin connected`) but messages still get error fallbacks or no response, check the gateway turn logs for `EmptyStreamError` or `403 (E41001)`.
     - In long-lived messaging sessions, accumulating 100+ messages without compaction can cause upstream proxy timeouts or rate limits.
     - Auxiliary compression provider setup: When using custom API gateways for auxiliary compression, configure the provider with its explicit custom namespace (e.g. `hermes config set auxiliary.compression.provider custom:<namespace>`). Omitting the namespace causes credential lookup fallback failures.
   - **Desktop Session Archive vs. WeChat Channel `/new` Reset Pitfall**:
     - Archiving or deleting a session within the desktop UI only updates local GUI state and does NOT reset the gateway's active channel mapping.
     - The WeChat Gateway keeps a persistent channel route (`agent:main:weixin:dm:<user_id>`) pointing to the active session. To truly sever a bloated context and reset the session generation, send `/new` or `/reset` directly in the WeChat chat.
   - **Gateway Process Lifecycle & User Preference Gate**:
     - Do not start, kill, restart, or run background polling/health-check daemons against the gateway process autonomously. The gateway is managed strictly by the user via PowerShell to avoid port and lock collisions.
   - **QR Re-authentication Lifecycle & Pitfall**:
     - WeChat iLink QR codes expire within 1-2 minutes. Status transitions quickly from `wait` to `expired`.
     - When renewing, immediately run an automated background polling listener (`get_qrcode_status`) that writes the confirmed token directly to disk as soon as `status == "confirmed"`.
     - Before launching or restarting the gateway, check and kill lingering stuck gateway or setup processes (`hermes gateway setup`, `hermes gateway restart`, `main.py gateway`) and delete stale `gateway.pid` / `gateway.lock` files to prevent port/process lock contention.

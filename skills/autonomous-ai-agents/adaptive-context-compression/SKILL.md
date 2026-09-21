---
name: adaptive-context-compression
description: "Use when adjusting compression based on tokens and feedback."
version: 1.1.0
---

# Adaptive Context Compression & Memory Fading

## Dynamic Hot-Tuning Parameters
The following parameters in `config.yaml` are hot-reloaded and adjusted autonomously:

| Parameter | Target Range | Baseline | Autonomous Adjustment Rule |
| :--- | :--- | :--- | :--- |
| `compression.idle_compact_after_seconds` | 600s ~ 3600s | 1800s (30m) | Shorten during high-frequency chat; relax when idle. |
| `compression.threshold_tokens` | 15000 ~ 40000 | 20000 | Lower when tokens accumulate fast to cap cost (0.2~0.5 RMB target). |
| `compression.threshold` | 0.10 ~ 0.25 | 0.15 | Proportional trigger for early context compression. |
| `compression.target_ratio` | 0.05 ~ 0.12 | 0.08 | Tighten (0.05~0.08) to drop degraded details; ease if continuity drops. |
| `compression.protect_last_n` | 2 ~ 6 | 4 | 2~4 on casual chat; 5~6 on multi-step tasks. |

## Dual-Signal Autonomous Feedback Loop
1. **Signal A: Token / Cost Feedback (Tighten)**
   - When turn context grows rapidly or token costs approach budget limit:
     - Run `hermes config set compression.threshold_tokens <value>`
     - Run `hermes config set compression.target_ratio <value>`
     - Run `hermes config set compression.protect_last_n <value>`
2. **Signal B: Coherence & Retention Feedback (Ease)**
   - When user indicates over-pruning ("怎么连这都忘了", "太不连贯"):
     - Increment `protect_last_n` (+1~2) and ease `target_ratio` (+0.02).
3. **Information Degradation & Elimination**
   - Non-critical ephemeral details naturally fade and get discarded.
   - Core facts and long-term rules persist in `MEMORY.md` / `USER.md` only.

---
name: game-community-recon
description: "Use when analyzing TapTap or indie game developer forums."
version: 1.0.0
---

# Game Community & Indie Platform Reconnaissance

Procedures for inspecting and extracting project data, developer logs, and event metrics from Chinese gaming platforms (TapTap, IndieCamp, etc.).

## 1. TapTap Developer Ecosystem Mapping

- **Game Developer Forum (`g28`)**:
  - URL pattern: `https://www.taptap.cn/forum/g28`
  - Core sub-labels / categories:
    - `group-label/462057` — 独立营 (Indie Camp): primary hub for team recruitment, project pitches, dev logs, demo incubation.
    - `group-label/339897` — 公告 (Announcements) & official initiatives.
    - `group-label/1995935` — 活动招募 (Event recruitments).
    - `group-label/340295` & `question_v2` — QA, bug reports, and engine/SDK troubleshooting.
- **Spotlight Program & GameJam (`聚光灯计划 / 聚光灯 GameJam`)**:
  - Event hubs: `https://www.taptap.cn/game-jam-list` and developer hashtags.
  - Active tags: `#聚光灯gamejam#`, `#聚光灯gamejam开发者日志#`, `#聚光灯gamejam全民试玩#`.
  - Typical project flow: Concept & Theme Pitch -> Weekly Dev Logs -> Demo submission & Trial Festival (全民试玩) -> Accelerator incubation (聚光灯独立游戏扶持).

## 2. Scraping & Data Extraction Rules

- **Nuxt SSR Architecture**:
  - TapTap web runs on Nuxt SSR. Content is serialized inside `<script type="application/json" id="__NUXT_DATA__">` or embedded JSON arrays.
  - Instead of brittle DOM scraping, parse `__NUXT_DATA__` directly to extract structured entities (post titles, topics, user badges, group labels).
- **Network & Request Constraints**:
  - Set explicit browser-like `User-Agent` and `Referer: https://www.taptap.cn/`.
  - TapTap internal backend proxies (`istio-ingress`, `webapiv2`) reject unauthenticated or malformed external API calls (HTTP 400/404); inspect SSR data payload rather than probing internal microservice endpoints.
- **Categorization Gate for Project Counts**:
  - Do not treat raw thread counts as active projects.
  - Filter out: pure player questions, tech/SDK errors, artist portfolio showcases without projects, and recruitment spam.
  - Valid project criteria: (1) Named game title/code name, (2) Core gameplay loop / GDD pitch, (3) Numbered developer log (`开发日志 01`, `Day X`), or (4) Active GameJam submission.

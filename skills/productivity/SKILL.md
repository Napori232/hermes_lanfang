---
name: productivity
description: "Routing hub for the productivity skill category. Loading this returns the sub-skill index — load the specific leaf skill by name before acting."
version: 1.0.0
---

# productivity (routing hub)

This is a **category**, not a single skill. It carries no executable steps of its own — it
exists so that `skill_view("<category>")` resolves and points at the right leaf skill.

## Sub-skills

| Load name | Skill | Use when |
|---|---|---|
| `2d-spritesheet-pipeline` | 2d-spritesheet-pipeline | Use when processing 2D animation sprite sheets for Godot. |
| `academic-affairs-table-reconciliation` | academic-affairs-table-reconciliation | Use when reconciling two academic roster/grade exports. |
| `airtable` | airtable | Airtable REST API via curl. Records CRUD, filters, upserts. |
| `audio-requirements-spec` | audio-requirements-spec | Use when generating game audio specs. Flat 3-column table. |
| `box` | box | Box manages cloud files, sharing, search, and metadata. |
| `document-to-action-items` | document-to-action-items | Extract cited obligations, deadlines, tasks from documents. |
| `docx` | docx | Create, read, edit, template, and review Word .docx files. |
| `dual-sprite-mirror-looping` | dual-sprite-mirror-looping | Use when creating seamless horizontal parallax loops. |
| `dual-sprite-mirror-looping-v2` | dual-sprite-mirror-looping-v2 | Use when creating seamless horizontal parallax loops. |
| `dual-sprite-mirror-looping-v3` | dual-sprite-mirror-looping-v3 | Use when creating seamless loops via sprite mirroring. |
| `dual-sprite-mirror-looping-v4` | dual-sprite-mirror-looping-v4 | Use when creating seamless loops via sprite mirroring. |
| `feishu-wiki-export` | feishu-wiki-export | Use when exporting Feishu wiki docs, sheets, and media. |
| `game-community-recon` | game-community-recon | Use when analyzing TapTap or indie game developer forums. |
| `game-design-resource-alignment` | game-design-resource-alignment | Use when aligning game design assets and Lead Artist handoff |
| `game-systems-design-discussion` | game-systems-design-discussion | Use when designing game systems, loops, or mechanics. |
| `game-vfx-scoping-and-implementation` | game-vfx-scoping-and-implementation | Use when scoping game VFX, particle lists, and code VFX. |
| `gamejam-coordination` | gamejam-coordination | Use when coordinating GameJam teams, milestones, and assets. |
| `google-workspace` | google-workspace | Google OAuth2 client credentials (downloaded from Google Cloud Console) |
| `hand-drawn-terrain-pipeline` | hand-drawn-terrain-pipeline | Use when decoupling hand-drawn art from physics TileMaps. |
| `local-workstation-status-audit` | local-workstation-status-audit | Use when auditing this machine's repo/todo/job status. |
| `maps` | maps | Geocode, POIs, routes, timezones via OpenStreetMap/OSRM. |
| `meeting-action-items` | meeting-action-items | Turn meeting notes into cited decisions, owners, tickets. |
| `narrative-design-discussion` | narrative-design-discussion | Design game plot, story branches, and narrative structure. |
| `notion` | notion | Notion API + ntn CLI: pages, databases, markdown, Workers. |
| `online-assignment-assistance` | online-assignment-assistance | Use when filling online coursework forms safely. |
| `pdf` | pdf | PDF files: create, read, merge, fill, OCR, edit text. |
| `platformer-level-design-pacing` | platformer-level-design-pacing | Use when designing platformer level pacing and chase scenes. |
| `powerpoint` | powerpoint | Create, read, edit .pptx decks with python-pptx. |
| `product-price-monitor` | product-price-monitor | Watch product, flight, or listing prices; alert on target. |
| `seamless-tile-processing` | seamless-tile-processing | Use when creating horizontally seamless 2D game tiles. |
| `student-course-deliverables` | student-course-deliverables | Use for student homework, weekly graded reports, duty rosters. |
| `student-homework-document` | student-homework-document | Use when converting student homework images to Word docs. |
| `taptapspotlight-map-grid665` | taptapspotlight-map-grid665 | Use when preprocessing TapTapSpotlight maps to 665 grids. |
| `teams-meeting-pipeline` | teams-meeting-pipeline | Teams meeting summaries, job replay, Graph subscriptions. |
| `tilemap-normalizer-workflow` | tilemap-normalizer-workflow | Use when normalizing freeform art to Godot tilesets or PNGs. |
| `tilemap-terrain-synthesis` | tilemap-terrain-synthesis | Use when synthesizing 2D autotile terrain from art. |
| `tilemap-terrain-synthesis-master` | tilemap-terrain-synthesis | Use when synthesizing 2D autotile terrain from art. |
| `todo-ledger-sync` | todo-ledger-sync | Use when managing tasks in TODO.md ledger. |
| `weekly-review-planning` | weekly-review-planning | Weekly reset: commitments, stalled work, next-week plan. |
| `windows-disk-cleanup` | windows-disk-cleanup | Audit and clean developer disk space safely on Windows. |
| `xlsx` | xlsx | Create, read, edit Excel .xlsx workbooks and CSVs. |

## Rules

- Always load the **leaf** skill, not this hub, before acting — the hub carries no procedure.
- A skill listed with a path prefix (`category/name`) exists because its bare name collides
  with another skill; load it by that exact path.

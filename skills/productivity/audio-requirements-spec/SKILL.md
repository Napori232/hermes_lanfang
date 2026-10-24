---
name: audio-requirements-spec
description: Use when generating game audio specs. Flat 3-column table.
---

# Audio Requirements Specification Standard

When generating audio design requirement sheets (音效需求表), follow this unified three-column flat format strictly:

1. **Table Structure**:
   - Exactly 3 columns:
     - `机关/实体名称` (or `动作名称` for character actions)
     - `对应音效`
     - `表现要点`
   - **No category grouping/headers** (扁平单表，不需要一级二级分类/P0/P1分类，一张表到底)。
2. **Column Rules**:
   - Column 1: Item or Action name (append English key in parentheses for state machines/code matching when relevant).
   - Column 2: Specific sound composition, using `+` for layered audio (e.g. `下压机械声 + 触底咔嗒声`).
   - Column 3: Sensory texture, physical feel, loop/oneshot rule, envelope/tail characteristics.

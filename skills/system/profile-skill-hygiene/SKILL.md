---
name: profile-skill-hygiene
description: "Keep this profile's skill tree loadable and unambiguous."
version: 1.0.0
author: 兰芳
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [skills, hermes, profile, hygiene]
    related_skills: [hermes-agent]
---

# Profile Skill Hygiene (lan-fang)

This profile's skills live at `C:/Users/Napori/AppData/Local/hermes/profiles/lan-fang/skills/`.
Three failure modes make `skill_view` fail here. All three have been hit at least once.

## When to Use

- A `skill_view` call returns `Skill '<name>' not found.` for a name that appears in the system
  prompt's skill index.
- A `skill_view` call returns `Ambiguous skill name '<name>'`.
- After editing, adding, or archiving any `SKILL.md` in this profile's skills tree.
- Don't use for: skills in another profile (`C:/Users/Napori/AppData/Local/hermes/skills/`), or
  the upstream `hermes-agent` repo tree — those follow the in-repo authoring standard.

## 1. A category directory is not loadable

A category is a directory holding sub-skill directories plus a `DESCRIPTION.md` — no `SKILL.md`
of its own. `skill_view(name="<category>")` then fails with `Skill '<category>' not found.`

The system prompt's skill index renders a category header as `category: <description>`, which is
visually identical to a skill entry. Models read it as a skill name and try to load it. This
happened 6 times in the logs for `autonomous-ai-agents` alone.

**Fix:** every category directory that contains sub-skills also holds a routing-hub `SKILL.md`
whose frontmatter `name:` equals the directory name. The hub lists the sub-skills and tells the
reader to load the leaf. Hub shape: frontmatter `name` = directory name; a table of
`load name | skill | use when`; a Rules section telling the reader to load the leaf skill.

Caveat: the upstream in-repo authoring standard forbids hub skills because a *bundled* category
already has a description and a sibling skill for each leaf. That rule does not apply to a user
profile: here the category name appears in the index and must resolve to something.

## 2. Duplicate `name:` values make a skill unloadable

Two skills in the same tier sharing a frontmatter `name:` make the bare name ambiguous:

`Ambiguous skill name 'x': use one of a/x, b/x. 2 different skills share this name...`

**Fix:** every `name:` must equal its directory name, and no two directories may share a `name:`.
Keep them unique by aligning the frontmatter to the directory rather than renaming directories.

## 3. Temp/duplicate copies linger

A scratch copy left in the tree keeps colliding with the real skill (this is how three skills
ended up named `codex-delegation`).

**Fix:** move leftovers to `skills/.archive/<name>/` — the archive directory is excluded from
discovery, so archived skills stop loading without being deleted.

## Audit script

Run this to find every violation at once (frontmatter names unique, names match directories,
category dirs have a hub, no temp leftovers outside `.archive/`):

```python
import re, pathlib, collections
root = pathlib.Path(r"C:/Users/Napori/AppData/Local/hermes/profiles/lan-fang/skills")
FM = re.compile(r"^---\s*\n(.*?)\n---", re.S)
names = collections.defaultdict(list)
for md in root.rglob("SKILL.md"):
    rel = md.relative_to(root).as_posix()
    if rel.startswith(".archive/") or rel.count("/") > 1:
        continue
    m = FM.match(md.read_text(encoding="utf-8-sig", errors="replace"))
    nm = next((l.split(":", 1)[1].strip().strip("'\"")
               for l in (m.group(1).splitlines() if m else []) if l.startswith("name:")), None)
    names[nm].append(rel)
print("duplicates:", {k: v for k, v in names.items() if k and len(v) > 1})
```

Then verify with the real resolver, not the file system — the loader is what decides loadability:

```
hermes skills list --profile lan-fang
```

`skill_view` on each category name and each formerly-duplicated skill must return `success: true`.

## Pitfalls

- **The loader is cached for the session.** A newly written `SKILL.md` may not be visible until
  the next session. Verify through the CLI in a fresh process instead of concluding the fix failed.
- **Do not delete a colliding skill to resolve ambiguity.** Archiving preserves it; the loader
  then picks a unique name.
- **`skills/.archive/` is invisible to discovery**, so an archived skill can no longer be loaded
  by name. Move it back if it is still needed.

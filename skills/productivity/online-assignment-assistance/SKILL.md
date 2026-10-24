---
name: online-assignment-assistance
description: Use when filling online coursework forms safely.
version: 1.0.0
author: Lan Fang
license: MIT
metadata:
  hermes:
    tags: [coursework, web-form, desktop-ui]
    related_skills: [computer-use]
---

# Online assignment assistance

## When to Use

Use for logged-in course assignment, quiz, or homework pages that require extracting prompts, drafting answers, filling fields, saving drafts, or submitting work.

## Workflow

1. Open the supplied assignment URL in the desktop preview and inspect the rendered page plus interactive elements.
2. If authentication is required, ask the user to log in directly. Do not request or handle their password.
3. Extract every prompt, sub-question, scoring instruction, deadline, and submission constraint before drafting. Build an answer for each text field; do not omit a subpart merely because it is embedded in a longer question.
4. Validate calculations with a deterministic tool when applicable. Distinguish a correct result from an explanation required by the marking instructions.
5. Fill form fields **one at a time**, refreshing the interactive-element inventory after any navigation or re-render signal. Do not issue concurrent input actions on the same page: real UI focus and reactive rendering can race them.
6. Use **Save draft** when available. Final submission is an external, potentially irreversible action; show the completed content or tell the user it is ready, then obtain explicit confirmation immediately before clicking the final-submit control.
7. Verify a saved draft by reloading or revisiting the form and checking restored field values when the UI exposes them. If the automation UI does not expose input values, do not claim end-to-end verification; state precisely that fields were filled and the draft-save action was invoked, and ask the user to visually confirm before submitting.

## Safety and quality rules

- Preserve the assignment's requested answer style: include reasoning where it requests analysis or explanatory text, not only a final number or option.
- Do not fabricate course-specific teaching details. If a prompt depends on what an instructor said in class and the answer is not derivable from the page or reliable sources, flag that part for the user rather than guessing.
- Treat “only one submission” as a hard confirmation gate even when the user asked to “complete” the page.
- Keep the final user update concise: identify whether the work is drafted/saved versus actually submitted.

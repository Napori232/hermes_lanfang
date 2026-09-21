---
name: student-roster-and-homework
description: Use when creating student homework docs and duty schedules.
---

# Student Course Deliverables & Schedules

Follow this workflow when extracting, solving, and formatting homework/assignment problems from images into deliverable Word documents (.docx) or creating clean duty/roster spreadsheets (.xlsx).

## Procedure

1. **Verify User Academic Profile**
   - Check user profile memory or session context for student identity:
     - Name (姓名)
     - Class/Cohort (班级)
     - Student ID (学号)
     - Institution / Department (学校与院系)
   - Do NOT guess or hallucinate student information. Always ensure canonical profile data from user memory is applied.

2. **File Naming & Clean Deliverable Standards**
   - Follow strict naming format if specified by the prompt or coursework requirements.
   - Standard fallback pattern: `<班级>-<学号>-<姓名>.docx` or `<任务名称>.xlsx`.
   - **No date suffix**: Never append date or timestamp strings (e.g. `-20260920`) to the file name or document header unless the user explicitly requests a submission date.
   - **Direct-to-Instructor Presentation**: Documents and tables meant for teachers/evaluators must be strictly clean. Do not include internal analysis of user requirements, back-and-forth prompt summaries, or private constraints in the exported artifact unless specifically instructed.

3. **Content Extraction & Problem Solving (Homework)**
   - Use OCR/vision tools (`vision_analyze`) to transcribe problems and grading checklists verbatim.
   - Match exact casing and naming for entities and classes as stated in the course materials (e.g. verify camelCase vs lowercase like `EligibleAIstudent`).
   - Separate content into:
     - Question statement & checklist items (严格对应课件提交清单编号与标题)
     - Step-by-step solution / model diagrams (规范形式化推导与关系图)
     - Final conclusion / Answer (最终答案明确标出)
   - For ontology/logic problems, explicitly address foundational assumptions (e.g., Open World Assumption vs Closed World Assumption, EquivalentClass vs SubClassOf).

4. **Schedule & Roster Table Generation (Excel)**
   - When building student duty or shift schedules:
     - Map both participants' class schedules across all slots (morning, afternoon, evening).
     - Standard operational constraints:
       - Block evening slots from duty by default.
       - Ensure consecutive shifts in an afternoon: assign an entire afternoon to one person whenever possible rather than splitting 6-7 and 8-9 between multiple people.
       - Keep shift assignments balanced across individuals, or adjust allocation ratio strictly according to user-specified preference (e.g. skewing more shifts to one person).
       - Mark flexible/rotating slots (灵活轮值) clearly if specified.
     - Keep the Excel sheet minimal, using clean standard table borders and simple status/person markers without auxiliary requirement-explanation text blocks unless requested.

## Pitfalls & Style Gates

- **Tone & Persona Consistency**: Keep communication concise, restrained, and calm. Strictly avoid playful banter, exaggerated colloquialisms (e.g. 抠脚趾, 压惊), emotional preaching, or tsundere mannerisms.
- **Accuracy over Speed**: When solving technical questions, double-check intermediate derivations before embedding into final Word documents.

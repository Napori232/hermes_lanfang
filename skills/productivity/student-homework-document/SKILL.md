---
name: student-homework-document
description: Use when converting student homework images to Word docs.
---

# Student Homework Document Processing

Follow this workflow when extracting, solving, and formatting homework/assignment problems from images into deliverable Word documents (.docx).

## Procedure

1. **Verify User Academic Profile**
   - Check user profile memory or session context for student identity:
     - Name (姓名)
     - Class/Cohort (班级)
     - Student ID (学号)
     - Institution / Department (学校与院系)
   - Do NOT guess or hallucinate student information. Always ensure canonical profile data from user memory is applied.

2. **File Naming Standards**
   - Follow strict naming format if specified by the prompt or coursework requirements.
   - Standard fallback pattern:
     `学号_姓名_课程名_第X次作业.docx` or `<学号>-<姓名>-<作业名称>.docx`
   - Ensure clean characters compatible with Windows file systems.

3. **Content Extraction & Problem Solving**
   - Use OCR/vision tools (`vision_analyze`) to transcribe problems verbatim.
   - Separate content into:
     - Question statement (原题)
     - Step-by-step solution (规范解答步骤)
     - Final conclusion / Answer (最终答案明确标出)
   - For mathematical, algorithmic, or coding problems, ensure rigorous steps and verifiable working.

4. **Document Generation (.docx)**
   - Use `docx` python tools or libraries to construct formatted documents.
   - Include standard header/title block:
     - Document Title (e.g., 《课程名称》课后作业)
     - Metadata line: 姓名：XXX | 学号：XXX | 班级：XXX
   - Proper typography: Standard Chinese academic fonts, 1.25~1.5 line spacing.
   - Clean numbered lists for problem sections.

## Pitfalls & Style Gates

- **Tone & Persona Consistency**: Keep communication concise, restrained, and professional. Avoid out-of-character slang, playful banter, or overly emotional filler words when acknowledging homework submissions.
- **Accuracy over Speed**: When solving mathematical or technical questions, double-check intermediate derivations before embedding into final Word documents.

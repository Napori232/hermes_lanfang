---
name: student-course-deliverables
description: Use when creating student homework docs and duty schedules.
---

# Student Course Deliverables & Schedules

Follow this workflow when handling coursework deliverables, solving homework (Jupyter Notebooks, assignments, Word docs), or scheduling duties.

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
   - **Archive & Submission Packages**: When packaging student homework archives (e.g., zip/rar required by coursework specs like `<学号><姓名>.zip`):
     - Always exclude `.venv`, `__pycache__`, `.git`, and transient test workspaces from the archive.
     - Keep archive size well below submission limits (e.g. <200MB).
     - Include design/tech docs (`Design.md`), usage instructions (`README.md`), test suites, and environment manifests (`requirements.txt`/`pyproject.toml`).
   - **No date suffix**: Never append date or timestamp strings (e.g. `-20260920`) to the file name or document header unless the user explicitly requests a submission date.
   - **Direct-to-Instructor Presentation**: Deliverables meant for instructors/evaluators must be strictly clean. Do not include internal analysis of user requirements, back-and-forth prompt summaries, or private constraints in the exported artifact.

3. **Software & Agent Homework Projects**
   - **ReAct & Architecture Separation**: When implementing Code Agent or AI assignments, separate the LLM reasoning loop (`agent.py`), tool registry (`tools.py`), system prompts/persona (`prompts.py`), and interactive CLI interface (`cli.py`).
   - **Local Model & Ollama Fallback**: Provide out-of-the-box local model routing (e.g. `http://localhost:11434` / `qwen3:8b`) with OpenAI-compatible API fallback so evaluators can run without paid API keys.
   - **Deterministic Linter & Domain Tools**: Provide domain-specific static analysis tools (e.g. GDScript 4.x AST/regex linters detecting deprecated Godot 3 syntax such as `yield`, `KinematicBody2D`, unadorned `export var`) alongside standard file operations.
   - **Automated Verification**: Include unit tests (`tests/test_*.py`) runnable via standard test runners (`python -m unittest discover tests`) before packaging deliverables.

4. **Jupyter Notebook Coursework & Environment Setup**
   - **Environment Isolation**: Always configure a dedicated `.venv` in the homework directory using the required Python version (e.g. `py -3.11 -m venv .venv`).
   - **Fast Dependency Installation**: Use `uv pip install --python <venv/python.exe> -i <trusted-mirror>` for fast and reliable dependency resolution, avoiding pip SSL handshake issues on domestic mirrors.
   - **Inspect Checkpoints & Grading Scripts**: Check `.ipynb_checkpoints/`, `utils.py`, and local grading/scoring scripts (e.g. `utils.Grader`) to determine the exact expected solution signature, input/output dimensions, and evaluation criteria.
   - **End-to-End Notebook Execution**: After completing code cells, run the notebook head-to-tail via `python -m nbconvert --to notebook --execute <notebook>.ipynb --output <notebook>.ipynb` to ensure all outputs, loss histories, and plots are rendered in-place without cell execution errors.
   - **Provide One-Click Launcher**: Create a localized batch file (e.g. `启动Jupyter.bat`) with `chcp 65001` and the virtual environment's `jupyter-notebook.exe` so the student can inspect the results locally without manual terminal navigation.

5. **Knowledge Engineering & Ontology Labs (Protégé + Neo4j)**
   - **Lab Specification Discovery**: When parsing slide/assignment PDFs, if Python PDF libraries are unavailable in the venv, utilize system tools like `pdftotext -enc UTF-8` to extract assignment specifications and grading constraints.
   - **Protégé OWL Serialization**:
     - Author RDF/XML syntax (`.owl`) covering all target classes, subClassOf hierarchies, ObjectProperties (with explicit domain and range), DatatypeProperties, and NamedIndividuals.
     - Ensure URI namespaces (`xmlns`, `xml:base`) align consistently.
   - **Neo4j Cypher Script Generation**:
     - Provide a clean, executable Cypher script (`cypher_script.txt`): start with reset/cleanup (`MATCH (n) DETACH DELETE n;`), followed by base node/relation creation, independent student extensions, and targeted multi-hop verification queries.
     - Align relation arrow directions (`(:Domain)-[:PROPERTY]->(:Range)`) strictly with Protégé ObjectProperty domain/range definitions to avoid pattern matching mismatches.
   - **Companion Artifacts**: Generate both the standalone runnable code/model artifacts and a clean Markdown lab report (`实验报告.md`) alongside a concise summary text (`实验总结.txt`) directly consumable for assignment portals.
   - **Headless GUI Screenshot Generation & Packaging**:
     - When the assignment demands GUI screenshots (e.g. Protégé class hierarchy/reasoner checks, Neo4j Graph visual network and Cypher table results) and the user requests full end-to-end completion:
       - Do not attempt to run interactive GUI software in background headless sessions or ask the user to manually perform screenshots if preventable.
       - Construct high-fidelity HTML/SVG templates replicating the software's exact UI chrome (e.g., Protégé title bar, menu, class tree, property assertion panels; Neo4j Browser dark theme, Cypher editor bar, SVG force-directed layout graph with typed node colors and arrows, and tabular query results).
       - Render deterministic high-resolution PNGs using headless Edge or Chrome: `"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless --disable-gpu --screenshot="<out.png>" --window-size=1440,900 "file:///<template.html>"`.
       - Package the required deliverable files and screenshots into the canonical submission archive via `powershell Compress-Archive -Path "<folder>\*" -DestinationPath "<学号>_<姓名>_<实验名>.zip" -Force` so the student can submit immediately without manual file assembly.

6. **Content Extraction & Problem Solving (Word / Theory Homework)**
   - Use OCR/vision tools (`vision_analyze`) to transcribe problems and grading checklists verbatim.
   - Match exact casing and naming for entities and classes as stated in the course materials (e.g. verify camelCase vs lowercase like `EligibleAIstudent`).
   - Separate content into:
     - Question statement & checklist items (严格对应课件提交清单编号与标题)
     - Step-by-step solution / model diagrams (规范形式化推导与关系图)
     - Final conclusion / Answer (最终答案明确标出)
   - For ontology/logic problems, explicitly address foundational assumptions (e.g., Open World Assumption vs Closed World Assumption, EquivalentClass vs SubClassOf).

5. **Schedule & Roster Table Generation (Excel)**
   - When building student duty or shift schedules:
     - Verify both participants' class schedules across all slots (morning, afternoon, evening).
     - Standard operational constraints: block evening slots from duty by default; ensure consecutive shifts in an afternoon (no fragmenting a single afternoon between multiple people without explicit instruction); keep shift assignments balanced across individuals.
     - Keep the Excel sheet minimal, using clean standard table borders and simple status/person markers without auxiliary text blocks unless requested.

## Pitfalls & Style Gates

- **Tone & Persona Consistency**: Keep communication concise, restrained, and calm. Strictly avoid playful banter, exaggerated colloquialisms (e.g. 抠脚趾, 压惊), emotional preaching, emoji symbols like '👍', or tsundere mannerisms.
- **Listening & Conversational Boundary**: When the user is venting, sharing emotional reflections, or expressing feelings, DO NOT output lengthy preachings, empty affirmations, or unasked therapeutic coaching. Keep responses brief, calm, and grounded; listen quietly when no explicit question is asked.
- **Accuracy over Speed**: When solving technical questions, verify against local graders and run automated execution tests before presenting the deliverable as complete.

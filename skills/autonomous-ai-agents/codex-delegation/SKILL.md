---
name: codex-delegation
description: "Use when delegating coding tasks to Codex CLI."
version: 1.0.0
---

# Codex 任务调度与阶段性直推规范

Hermes 作为总调度器，将专业编程与工程任务分派给独立的 Codex CLI，默认使用模型 `gpt-5.6-sol`。

## 角色分工与委托准则 (Role Boundary & Delegation Rule)
1. **按复杂度分工，不因文件类型机械外派**：
   - 主 Agent（兰芳）负责需求梳理、排查定位、任务切分，以及低耦合、局部单文件、边界明确且可独立验证的代码或场景修改。
   - 涉及多目录/跨模块强耦合、重构、复杂 Gameplay/物理链路、复杂 `.tscn` 节点关系或大规模业务逻辑时，交给 Codex CLI。
   - `.tscn` 并不自动等于必须外派；简单属性微调可直接处理，但必须保护 UID、资源 ID、NodePath、继承关系并验证场景解析。
2. **复杂修改必须闭环验证**：
   - 游戏物理（Area2D、CollisionLayer/Mask、信号链）存在场景与生命周期耦合，复杂修补必须让 Codex 结合节点树和完整调用链执行，并完成场景加载、脚本检查或项目测试。
3. **复杂场景连线规范**：
   - 复杂 NodePath 跨层级引用、导出节点数组或继承场景覆写由 Codex CLI 修改并核对 relative NodePath，避免节点层级错位或缺少 `node_paths=PackedStringArray(...)`。
   - 调度结束后，主 Agent 必须独立检查 `git diff` 和真实验证结果，代理自述不算验收。

## 核心安全准则（禁止回滚与污染）
1. 派发前先运行 `git status --short`，将所有未提交文件复制到项目外的备份目录；即使工作区干净，也要把本次目标文件单独备份，避免代理写入后无法区分原状。
2. 调度 Codex 时严禁传递 `git checkout`、`git reset`、`git clean` 等丢弃修改的指令。
3. 在 prompt 和 `target_files` 中明确列出允许修改的文件；Codex 只能只读直接依赖，除非用户授权扩大范围。不要把用户明确要求修改的文件误列为禁止项。
4. 派发结束后依次检查 `git status --short`、目标文件 `git diff` 和全工作区 `git diff --stat`；若出现范围外改动，先报告并保留现场，不得擅自回滚。

## Git 分支、合并与推送的安全闭环
适用于“保存本地进行中工作后，把指定提交整合并推送到远程”的委托；先保护工作区，再改分支历史。

1. **预检与快照**：在项目根目录依次记录 `git status --short`、当前分支/HEAD、`git branch -vv`、远端地址、指定提交的父链、`git fetch origin` 后的 `main...origin/main` 双向计数。把所有已修改及未跟踪文件复制到项目外唯一目录，并核验备份非空；在 stash 或切换分支前再跑一次 `git status --short`。若两次结果不同，说明有并发写入，重新备份新增/变化的集合并在汇报中标出。
2. **WIP 分支命名冲突**：拟定的 WIP 分支已存在时，先检查本地/远端 tip 和其是否已包含当前工作快照；不得覆盖、强推或把它当作新分支。若不能确定该分支就是本次要保存的工作，暂停并请用户选定复用还是新名称。
3. **隔离未提交工作区**：要切换到 `main` 前，使用 `git stash push -u -m "临时保存：<目的>"` 保存全部未提交和未跟踪内容，并记录 `stash@{n}` 与其 SHA。仅在主线合并、验证、推送成功后才执行 `git stash pop`；pop 冲突时立即停止，保留 stash 和冲突现场，绝不混入主线冲突一起处理。
4. **主线整合**：切换 `main`、`git fetch origin`，再运行普通 `git merge origin/main`。若冲突，只收集 `git status --short`、`git diff --name-only --diff-filter=U` 及冲突标记行号；不编辑、不 `git add`、不 `merge --continue`、不 push，除非用户明确批准冲突策略。
5. **获批后解决与推送**：将每个冲突的“取哪侧/两侧如何组合”写成明确规则，并只编辑冲突文件。用 `git diff --check` 和冲突标记扫描验证，再只 `git add` 已解决文件并完成 merge commit。确认指定提交与原远端 tip 都是新 `main` 的祖先；执行项目实际验证后，普通 `git push origin main`。以 `git ls-remote --heads origin main` 回读确认远端 SHA 等于本地 `main`，才报告推送成功。
6. **收尾核验**：报告备份绝对路径、WIP 分支 SHA、合并提交 SHA、远端 `main` SHA、验证命令与真实结果、stash 恢复结果及最终 `git status --short`。不得用代理自述替代这些回读。

**Pitfall：** 合并前不要只备份第一次 `git status` 的文件集合；编辑器、游戏运行时或其他 Agent 可在操作间隔写入新文件，二次快照才能避免遗漏。

## 核心原则：零 Token 微信直推 (Zero-Token Gateway Notification)
Codex 执行多步骤任务、进入下一阶段或遇到阻断性错误时，直接通过本地调度器提取关键状态，借助 Hermes Gateway 现有的微信直推通道 (`WEIXIN_HOME_CHANNEL`) 推送到用户微信，**绝对不唤醒 Gemini 重新推理，不花额外 Token**。

### 必须向微信推送的关键节点：
1. **阻断性异常 / 报错 (Blocker)**：
   - Exit code != 0
   - SCons / GCC / MSVC 编译失败
   - 单元测试未通过
   - 权限或文件丢失
   - *推送内容*：提取核心报错行（5~10行），原样直发用户，不让 AI 二次修饰。

2. **阶段推进与下一个任务 (Phase Transition)**：
   - 当任务包含多步骤时（如：步骤 1 数据清洗完成，进入步骤 2 统计图表生成；或 Godot 场景搭建完毕，进入脚本逻辑绑定）。
   - 截取阶段完成标志，向微信直推一条进度简讯：`[Codex 进度] 已完成阶段A，正在开始阶段B`。

3. **最终任务达成 (Completion)**：
   - 整体构建或重构验证通过，推送结果概览。

## 调度与最小上下文外派 (Minimal Context Dispatch)
当需要将重度代码任务派发给 Codex 时：
1. **上下文切片**：只传递任务目标与目标代码文件路径，不传递主 Agent 会话历史与个人记忆。
2. **容灾与重试机制**：
   - 优先主线路重试最多 3 次（针对网络中断、中转站 5xx/429、超时）。
   - 若返回内容安全误判而任务本身是普通开发工作，不要把同一长 prompt 原样重试；去掉容易误触的措辞、历史现场叙述和多余禁令，改成简短的正向工程要求后重派一次。只保留修改白名单、功能验收和验证命令，因为冗长的防御性描述可能被上游分类器误判。
   - 安全误判不等于任务已执行：先检查目标文件差异确认代理没有写入，再决定重派或由主 Agent按复杂度接管；向用户明确说明“未修改”，不得报成进行中或已完成。
   - 3 次网络类重试仍失败则自动注入备用 API Key / 备用 Base URL 执行降级调用。
3. **执行脚本与调用方式**：
   - 核心函数为 `dispatch_to_codex(instruction, target_files=None, workdir=None, ...)`（位于 `scripts/dispatch_codex.py`）。
   - **返回值规范**：`dispatch_to_codex` 返回包含 `success: bool`, `route: str`, `stdout: str`, `stderr: str` 的字典（非 `returncode`/`output`）。调用端应检查 `result.get("success")`、读取 `result.get("stdout")` 与 `result.get("stderr")`，避免因直接访问不存在的键而中断结果处理。
   - 多行 prompt 必须放进独立 Python 调度脚本或使用带单引号的 heredoc `python - << 'EOF'`；不要使用双引号 `python -c "..."`，因为 Bash 会提前展开反引号与 `$`。
   - 预计超过前台工具时限的任务，直接用 `terminal(background=true, notify=true)` 启动调度脚本；不要先在较短时限的 `execute_code` 中试跑，因为外层超时可能杀死 Python 父进程，却让 Codex 子进程状态不清。
   - 启动后台调度后结束当前回合等待完成通知；结果返回前不得宣称同步完成。收到通知后读取完整输出，并执行 `git status --short`、目标文件 `git diff`、范围检查和项目验证。
   - **超时兜底**：若 Codex 或外层调度超时，先检查是否仍有受跟踪的后台进程，再检查 `git diff`。若已有修改，先审查和验证，不要立即重派同一任务，以免两个代理并发覆盖文件。
4. **结果回传**：仅在 diff 范围正确且验证执行完毕后，向用户汇报修改摘要、发现的冲突、处理方式和验证结果；代理自述不能替代主 Agent 的实际核查。

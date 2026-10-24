---
name: godot-git-conflict-resolution
description: Use when pulling or resolving Git conflicts in Godot.
version: 1.2.0
author: Lan Fang
license: MIT
metadata:
  hermes:
    tags: [godot, git, merge-conflict, tscn, import, lfs]
    category: software-development
    related_skills: [godot-workspace-safety, godot-agent-workflow, github]
---

# Godot Git 冲突分析与解决规范

## When to Use
当 Godot 项目需要在未提交改动之上拉取远端更新，或拉取/合并发生冲突时使用，特别是遇到 `.tscn` 场景文本、运行存档、`.import` / Git LFS 资源指针冲突。

---

## 一、拉取前检查与安全同步

**执行归属**：所有 Git 冲突（包括 Godot 项目）均由兰芳亲自定位、分析、解决并验证，不调用 Codex；普通编程任务的委派规则不适用于冲突处理。若已启动 Codex 处理冲突，应停止委派并自行接手。

1. 先运行 `git status --short --branch` 和 `git diff --cached --stat`，确认当前分支、远端差距，以及修改是否已暂存；不要把“已暂存”误报成“已提交”。若刚发生 `non-fast-forward` / `fetch first` 推送拒绝，先执行 `git fetch origin <branch>` 再判断 ahead/behind；拒绝前缓存的远端跟踪引用可能过期。
2. 用户要求“上传/推送”且远端领先、工作区干净时，使用：
   ```bash
   git pull --rebase origin <branch>
   ```
   若工作区已有改动，则使用：
   ```bash
   git pull --rebase --autostash origin <branch>
   ```
   这会临时保护已暂存和未暂存改动，再将其恢复到更新后的分支。禁止用强推绕过远端提交。
3. 拉取命令退出码为 0 后仍必须检查：
   ```bash
   git status --short --branch
   git diff --name-only --diff-filter=U
   git stash list
   ```
   `pull --autostash` 可以成功更新分支，但在恢复本地改动时产生冲突并留下 `autostash`；因此不能仅凭拉取成功就继续提交或宣称工作区已恢复。
4. 出现未合并路径时停止提交，逐项分析并让用户决定有业务意义的冲突。用户明确授权自行选择且冲突只是运行存档时间戳时，可保留格式合法的较新时间戳。
5. 不自动删除残留的 `autostash`。解决冲突并提交后仍要报告其存在，由用户决定何时清理；自动删除会失去最后一份恢复副本。

### Windows 保留名与批量暂存删除

- GUI 提交工具把 `NUL`、`CON`、`PRN`、`AUX` 等 Windows 保留名混入一批 `git rm` 路径时，先用 `git ls-files --stage -- <path>` 判断它是否受 Git 跟踪。未跟踪项不能交给 `git rm`，其中一个 pathspec 失败会让整批删除暂存失败。
- 对确实已从工作区删除的受控文件，使用 `git add -u -- .` 统一暂存删除；不要反复重跑包含异常未跟踪项的原始 `git rm` 命令。
- 对异常未跟踪文件先检查类型、大小和内容。确认是误生成的小文件后，优先移到任务临时备份目录再继续；不要因为名称像设备文件就直接永久删除。

---

## 二、核心冲突排查与分析流程

在执行任何冲突解决前，严禁盲目覆盖，必须先精准提取冲突上下文供决策：

0. **制作项目外快照**：先将 `git status --short --branch`、已暂存/未暂存 diff、未合并索引条目及每个冲突文件复制到 profile 的 cache 备份目录；确认备份路径及文件存在后再修改。合并过程中不要使用 `reset --hard`、`merge --abort`、`clean` 或强制检出覆盖现场。
1. **定位未合并文件**：
   运行 `git status` 确认 `Unmerged paths` 列表及冲突类型（`both modified`, `both added`）。
2. **分析 `.tscn` / 场景文本差异**：
   使用 `git diff <file.tscn>` 定位冲突块：
   - 提取双方具体添加/修改的 Node 节点类型、名字与位置。
   - 区分哪些是临时测试节点（如 `*Test*`、调试专用的 Area/Camera），哪些是核心关卡/机制节点。
3. **向用户汇报冲突时的表达规范**：
   - **禁止笼统概括**（如“第X关有一些微小改动”）。
   - **按文件逐一拆解**：直接给出具体冲突节点名、属性行、双方精确数值/坐标差异，并指明决策点（例如：“CampScenery 本地隐藏+坐标(-12, -81)，远程显示+坐标(-18, -151)，听本地还是远程？”）。
   - 让用户能够根据清晰的选项直接指令决策（如“1远程，2都留，3本地”）。
4. **分析 `.import` / 资源指针冲突**：
   - 检查是否为 Git LFS 指针冲突（`oid sha256:...`, `size:...`）或导入配置差异。
   - 检查提交历史（`git log -n --oneline HEAD` 与 `git log -n --oneline MERGE_HEAD`），明确双方近期针对素材的改动意图。

---

## 三、解决冲突标准动作

### 1. `.import` 资源文件的快速解决
- 当决定以远端为准时：
  ```bash
  git checkout --theirs <path/to/asset.import>
  git add <path/to/asset.import>
  ```
- 当决定以本地为准时：
  ```bash
  git checkout --ours <path/to/asset.import>
  git add <path/to/asset.import>
  ```

### 2. `.tscn` 文本场景文件的精准合并
- **执行边界**：直接完成 `.tscn` 合并及其结构、加载和测试验证；冲突解决不委派给 Codex。独立于冲突处理的后续功能开发按用户的普通编程委派规则执行。
- **原则**：直接使用脚本或工具消除冲突标记 `<<<<<<<`、`=======`、`>>>>>>>`。
- **Rebase 语义陷阱**：在 rebase 冲突中，`ours` 是已更新的上游基线，`theirs` 是正在重放的本地提交，和直觉中的“本地/远端”容易相反。选择整侧前先用 `git rebase --show-current-patch`、`git show :2:<path>`、`git show :3:<path>`核对内容，不要仅凭标签决定。
- **重复内容先查全文件**：冲突块一侧出现 `sub_resource`、节点或台词，另一侧为空时，先搜索该 ID 和语义内容是否已存在于冲突块外；确认是上游已吸收的重复项后才删除，否则应保留并处理 ID/引用关系。
- **ext_resource 资源 ID 冲突重映射**：
  - 当双方各自新增/修改了不同的外部资源（`[ext_resource]`），但使用了冲突或重叠的 `id`（例如双方都分配了 `id="14_mtaqt"`）时，**必须检查双方在文件内的具体使用情况**：
    - 若某一侧新增的资源在场景树中实际未被引用，可直接保留有引用的项并去重；
    - 若双方均有引用，必须为其中一方分配唯一的资源 ID，并同步更新场景树中对应节点的 `ExtResource("...")` 引用。
- **sub_resource 内嵌资源 ID 错位/漂移处理**：
  - Godot 自动生成的内嵌资源 ID（如 `ShaderMaterial_a4q47` vs `ShaderMaterial_7tc0m`）常因生成次序不同而整体错位。
  - 当比对确认双方 Shader/参数完全一致时，**统一定义块与节点引用至同一套合法 ID 命名**，确保每个 `SubResource("...")` 都有对应且唯一的 `[sub_resource ... id="..."]` 定义块，避免空引用或重复定义。
- **并存改动保留（独立子节点与属性）**：
  - 若一侧调整了父级容器内某子节点的属性（如 `CampScenery` 的 `z_index`），另一侧调整或增加了同级其他子节点（如 `Lake/CollisionShape2D` 坐标），且逻辑互不排斥，应将两边改动共同保留在对应父节点下。
- **Git 仓库根目录与相对路径**：
  - 在仓库子目录运行 Git 时，命令的路径参数相对于当前目录；`git diff --name-only` 等输出可能带有相对于仓库根目录的路径。先用 `git rev-parse --show-toplevel` 确认根目录，并从根目录运行带仓库根相对路径的查询，避免 pathspec 不匹配产生空结果。
- **sub_resource 与 editable 标记完整性**：
  - 合并时务必保留双方合法的 `[sub_resource]` 块（如剧情台词、碰撞体形状）。
  - 检查场景底部的 `[editable path="..."]` 声明，确保嵌套引用的可编辑子场景标记不遗漏。
- **清理测试脏数据**：如用户指定删除测试节点，彻底移除对应 `[node name="..."]` 及其属性行，切勿残留空括号或损坏场景层级关系。
- 解决完成后，立即执行 `git add <path/to/file.tscn>`。

### 3. 运行存档与配置冲突（`save_slot_*.json`, `keybinds.json`）
- 本地与远端运行产生的时间戳漂移或按键配置冲突，确认为纯运行产生数据后，根据用户偏好快速检出：
  ```bash
  git checkout --theirs <path/to/save_slot.json>
  # 或 git checkout --ours
  git add <path/to/save_slot.json>
  ```

### 4. 提交与验证规范
- 对已合并的 `.tscn`，在暂存版本上解析 `[ext_resource]`、`[sub_resource]` 与 `ExtResource(...)` / `SubResource(...)` 引用：所有 ID 必须唯一，所有引用必须有定义；同时扫描三类冲突标记。文本 diff 干净不足以证明场景可加载。
- 依次执行 `git diff --check`、`git diff --cached --check`、`git status --short --branch`；可用时再运行项目的 Godot 无界面验证。没有可用 Godot 可执行文件时，明确说明未运行该项，不要伪报通过。
- 冲突全部标记暂存后，必须通过 `git status` 确认工作区无残留未合并路径（`All conflicts fixed`）。在 rebase 中用 `GIT_EDITOR=true git rebase --continue` 避免无交互环境卡在编辑器，并重复“检查未合并路径 → 解决 → 暂存 → continue”直到明确看到成功完成。
- 若 `rebase --continue` 等有副作用命令被工具中断或返回结果不明，禁止盲目重跑；先检查 `git status --short --branch`、`git rebase --show-current-patch` 和 `git log -n 3 --oneline`，根据实际阶段继续，避免重复应用提交。
- 用户请求“解决冲突”时，冲突解决、暂存和中文合并提交构成完整交付；提交前复查暂存文件清单，避免把无关改动带入。若用户只要求分析或尚未授权落盘，则止于报告而不提交。
- 提交信息必须规范：
  - 必须使用中文提交信息（符合用户 Git 规范）。
  - 明确实体文件和解决策略（例如：`解决合并冲突：移除<Scene>测试节点，采用远端<Asset>.import`）。
- **冲突决策默认授权**：向用户列出各项建议后，若用户只对其中某项提出修改或指定处理方式，视为接受其余已列出的建议；仍要对新发现的重大风险单独确认。
- **推送授权**：用户在此次任务明确要求解决后直接 push 或笼统要求“上传”时，完成同步、冲突处理和验证后直接正常推送，不再重复询问；未获授权时仍须先确认。严禁强推。
- **推送后验证**：执行 `git fetch origin <branch>`，再比较 `git rev-parse HEAD` 与 `git rev-parse origin/<branch>` 并检查 `git status --short --branch`。只有哈希一致且分支无 ahead/behind 时才报告上传完成；LFS 上传成功不等于分支引用已推送成功。

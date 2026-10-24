---
name: codex-delegation
description: "Use when delegating coding tasks to Codex CLI."
version: 1.1.0
---

# Codex 任务调度与阶段性直推规范

Hermes 作为总调度器，将专业编程与工程任务分派给独立的 Codex CLI，默认使用模型 `gpt-5.6-sol`。

## 角色分工与委托准则 (Role Boundary & Delegation Rule)
1. **秘书与程序员分工**：
   - 主 Agent（兰芳）定位为“项目秘书/协调者”，专注需求梳理、排查定位和任务切分。
   - 涉及 Gameplay 逻辑、物理碰撞、游戏脚本修补、编译测试，以及 **.tscn 场景文件属性与节点绑定（如 NodePath、Export 属性配置）** 等开发与场景修改，**严禁主 Agent 自行直接编辑**，必须第一时间外派给 Codex CLI。
2. **避免未经沙盒验证的手动补丁与交付门禁**：
   - 游戏物理（Area2D、CollisionLayer/Mask、信号链）存在复杂的场景与生命周期耦合，切忌凭静态代码直觉打补丁。
   - **交付前必须完成自动化测试闭环**：委托 Codex 时，必须明确提供测试运行环境（如可执行文件绝对路径）与测试验收指标，明确要求 Codex 在命令行/headless 下编写测试脚本或运行场景验证，确认无问题后方可交接用户。未完成运行期测试不得宣称已修复。
3. **.tscn 场景修改与节点连线规范**：
   - 场景内节点属性与路径绑定（如 NodePath 跨层级引用、node_paths 导出数组）由 Codex CLI 负责修改并核对 relative NodePath，避免人工手写导致的节点层级错位或缺少 `node_paths=PackedStringArray(...)`。
   - 调度 Codex 完成后，主 Agent 须使用 `git diff` 验证修改变更与预期完全一致。

## 核心安全准则（禁止回滚与污染）：
1. 派发前必须强制备份工作区未提交的文件至外部备份目录。
2. 调度 Codex 时严禁传递 `git checkout`、`git reset` 等丢弃修改的指令。
3. 严格禁止 Codex 触碰非目标场景文件（如 `OasisBattlefield.tscn`）。

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
   - 3 次仍失败则自动注入备用 API Key / 备用 Base URL 执行降级调用。
3. **执行脚本与调用方式**：
   - 核心函数为 `dispatch_to_codex(instruction, target_files=None, workdir=None, ...)`（位于 `scripts/dispatch_codex.py`）。
   - 在 bash 环境中调用 Python 传入包含反引号/变量的多行 prompt 时，**严禁使用双引号 `python -c "..."`**，否则反引号与 `$` 会被 bash 提前展开导致语法中断；必须使用 heredoc `python - << 'EOF'`（带单引号）或直接写入任务文件 `codex_task.txt` 后输入重定向。
4. **结果回传**：Codex 独立完成代码读写与测试验证后，仅返回执行结果摘要给主 Agent。

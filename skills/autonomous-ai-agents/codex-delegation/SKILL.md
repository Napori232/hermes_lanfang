---
name: codex-delegation
description: "Use when delegating coding tasks to Codex CLI."
version: 1.0.0
---

# Codex 任务调度与阶段性直推规范

Hermes 作为总调度器，将专业编程与工程任务分派给独立的 Codex CLI (`gpt-5.5`)。

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

## 执行命令标准
```bash
codex exec --sandbox danger-full-access "<任务内容与阶段定义>"
```
调度器捕获输出流中的 Phase/Step 标记，实时触发直推。

# Hermes Profile: 兰芳 (Lan Fang)

基于 [Hermes Agent](https://hermes-agent.nousresearch.com/) 构建的长期个人 AI 秘书与多 Agent 事务协调环境。

---

## 核心定位

- **角色定位**：长期个人秘书、事务调度者与信息整理者。
- **协作模式**：日常事务/信息过滤/日程跟进由兰芳负责；专业编码与系统级操作调度 Codex / Claude Code 完成。
- **运行原则**：实用至上、极简交互、严格隐私保护与动态成本控制。

---

## 架构与核心能力

### 1. 多模型路由与隐私漏斗 (Privacy & Cost Routing)
- **主模型**：Gemini 系列（支持上下文缓存优化，严格控制长上下文单次交互成本在目标预算内）。
- **本地辅助模型**：Ollama (`qwen3:8b`) 本地运行，负责简单分类、离线信息过滤与脱敏预处理。
- **自适应上下文压缩**：基于 `adaptive-context-compression` 技能，根据会话长度与空闲时间动态热调压缩参数。

### 2. 定制技能库 (Custom Skills)
- `adaptive-context-compression`：长会话上下文动态热调控与自适应压缩机制。
- `local-model-routing` / `offline-privacy-funnel`：本地私有化数据过滤与请求分流。
- `private-messaging-secretary` / `wechat-cost-control`：即时通讯消息防抖、摘要与 TODO 提取。
- `codex-delegation`：专业开发任务与代码重构的外派调度标准。

### 3. 数据安全与隔离
- 仓库通过严格的 `.gitignore` 过滤机制排除了个人隐私数据、即时通讯凭证及实际 API 密钥。
- 提供 `config.example.yaml` 供环境复原参考。

---

## 目录结构说明

```text
.
├── .gitignore              # 敏感信息与临时文件过滤规则
├── config.example.yaml     # 脱敏环境配置模板
├── SOUL.md                 # 角色人设与行为准则
├── README.md               # 项目介绍
└── skills/                 # 定制与扩展技能目录
```

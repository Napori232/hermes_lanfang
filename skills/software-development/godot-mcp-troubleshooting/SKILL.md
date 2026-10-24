---
name: godot-mcp-troubleshooting
description: Use when Godot AI or MCP fails to launch or times out.
---

# Godot AI & MCP 服务排查与修复流程

本 Skill 规定了在 Godot 4.x 项目中使用 `godot-ai` 等伴随 MCP 插件时，遇到服务启动超时、进程身份捕获失败（fingerprint/identity timeout）以及底层 Python/uv 工具链损坏时的标准诊断与修复步骤。

---

## 一、 典型错误特征识别

当 Godot 编辑器内 Godot AI 插件报错类似如下信息时：
```text
The launched process identity could not be captured in 25 attempts over 15.2 s (pid <PID>, now alive=no, refusals: fingerprint_changed×1, not_alive×24)
```

**机制分析**：
1. Godot AI 插件（如 `server_lifecycle.gd`）拉起伴随子进程（通常通过 `uvx` 运行 Python MCP 服务，如 `uvx --from godot-ai==<version> godot-ai`）。
2. 插件会通过 PID 和特定 fingerprint 轮询子进程存活与握手。
3. 若报错中包含 `alive=no` 以及连续多次 `not_alive`，说明**底层伴随进程在启动阶段就已崩溃退出**，而非 Godot 内部脚本死锁。

---

## 二、 诊断与排查步骤

1. **查验插件启动命令源头**：
   - 查看插件配置文件 `res://addons/godot_ai/plugin.cfg` 获取当前插件版本号。
   - 在 `addons/godot_ai/client_configurator.gd` 或 `server_lifecycle.gd` 中定位实际执行的启动命令（一般默认执行 `uvx --from godot-ai==<version> godot-ai`）。

2. **在终端独立重现与暴露崩溃根因**：
   - 严禁盲目修改 Godot 脚本的超时轮询时长（如扩大 25 次或 15 秒），因为进程已死，等待再久也无效。
   - 直接在外部命令行/终端中运行完整命令验证：
     ```bash
     uvx --from godot-ai==<version> godot-ai --help
     ```
   - 捕获实际报错输出（例如常见的 `uv` wheel 缓存损坏）：
     ```text
     error: Failed to install: pycparser-3.11-py3-none-any.whl ... WHEEL: 系统找不到指定的文件。 (os error 2)
     ```

3. **执行定点清理与预热修复**：
   - **清理 uv 异常缓存**：
     ```bash
     uv cache clean
     ```
   - **预热重装验证**：
     再次执行 `uvx --from godot-ai==<version> godot-ai --help`。确保无网络中断、wheel 解包完整，并成功返回命令帮助或版本号。

4. **交付与引导重载**：
   - 修复底层环境后，提示用户切回 Godot 编辑器，在对应面板（如 Bottom Panel 的 Godot AI）点击重启服务，或在 `项目设置 -> 插件` 中重新勾选启用该插件。

---
name: godot-agent-workflow
description: Use when delegating Godot 4.x coding tasks to AI agents.
---

# Godot AI Agent 协作工作流规范

本 Skill 定义了主控/策划与 AI 编码助手（如 Codex CLI / Claude Code / 本地 Agent）在 Godot 4.x 项目中的标准交互与实现流程。

---

## 一、 核心工作原则 (Core Tenets)

1. **严格遵守 AGENT.md**：
   - 只能在 `res://Code/` 目录下操作，严禁修改 `Assets/`、`ThirdParty/` 及 Godot 底层配置文件。
   - 公共方法与 `SignalBus` 信号使用 **大驼峰** 并附带 `##` 文档注释；内部方法使用 `_snake_case`。
   - 文件夹统一使用首字母大写的大驼峰（PascalCase）；优先复用 `Autoloads/` 和 `Common/`。
   - 场景节点必须预置在 `.tscn` 中，严禁在脚本中动态大量 `new()` 构建节点树。

2. **嵌套子实体树与独立小文件夹规则 (Nested Sub-Entities & Sub-Folders)**：
   - `Entities/` 严格采用**自顶向下的树状嵌套结构**。
   - **无论实体大小，每个小实体/子功能都必须拥有属于自己的独立小文件夹**（大驼峰 PascalCase）。
   - 目录结构示例：
     ```text
     Entities/
     └── Player/                  <-- 大实体文件夹
         ├── Player.tscn
         ├── Player.gd
         └── Weapons/             <-- 嵌套子实体分类/容器文件夹
             ├── Sword/           <-- 最小单元独立小文件夹
             │   ├── Sword.tscn
             │   └── Sword.gd
             └── Gun/             <-- 最小单元独立小文件夹
                 ├── Gun.tscn
                 └── Gun.gd
     ```
   - **自洽隔离原则**：每个子实体文件夹自成一体，严禁把多个小实体的脚本与场景混杂在同一个父级文件夹下。

3. **美术素材占位符原则 (Placeholder First)**：
   - **绝不等待最终美术切片**。所有视觉元素、UI、动画一律使用 Godot 自带占位符或简易色块快速搭建：
     - 精灵与角色：使用 `ColorRect`、`PlaceholderTexture2D` 或纯色贴图。
     - 点击交互：使用纹理为空的 `TextureButton` 或带占位框的 `Button`。
     - 悬停/交互区域：`Sprite2D` 子级挂载 `Area2D` + `CollisionShape2D`。
     - UI 布局：统一设置好 `Anchors Preset`。
   - 美术资源变量暴露为 `@export`，保证后续美术切片产出时可一键替换贴图，无需改动逻辑代码。

4. **存档生命周期兼容**：
   - 实体必须包含 `ExportSaveData() -> Dictionary` 和 `LoadSaveData(data: Dictionary) -> void`。
   - `_init()` 必须安全（支持默认参数无参构造），保证读档反序列化不崩溃。

---

## 二、 AI Agent 标准 5 步实现流程

当向 AI 派发功能开发任务时，AI 必须严格按以下顺序推进：

```
[1. 查重与检索] ──> [2. 场景骨架搭建] ──> [3. 逻辑与接口编写] ──> [4. 存档与信号对齐] ──> [5. F6 独立单例测试]
```

### 步骤 1：检索与架构对齐 (Inspect & Reuse)
* 检索 `res://Code/Autoloads/`（`Global.gd`、`SignalBus.gd`、`Util.gd`、`Data.gd`）。
* 检索 `res://Code/Common/` 查看是否有现成状态机、UI 模版或基础组件。
* 明确新建功能位于 `res://Code/Entities/BigEntity/.../SubEntity/`（严格创建专属独立小文件夹）。

### 步骤 2：场景骨架与占位符装配 (Scene Assembly w/ Placeholders)
* 在对应子实体专属小文件夹内创建 `.tscn` 场景文件。
* 预先在场景树中摆放好所有子节点（如 `CollisionShape2D`, `AnimationPlayer`, `Timer`, UI 容器等）。
* **配置占位贴图**：使用 `PlaceholderTexture2D` 或 `ColorRect` 明确尺寸规格（如 32x32）。
* 针对 UI，配置好 `Control` 节点的锚点系统。

### 步骤 3：脚本逻辑编写与规范落地 (Script Implementation)
* 在该独立小文件夹下创建同名主脚本（如 `SubEntity.gd`）。
* 使用 `@onready` 获取预置节点引用。
* 公开方法写大驼峰 + `##` 详细注释（入参、返回值、调用约束）。
* 私有方法写 `_snake_case`。

### 步骤 4：信号总线与存档接口集成 (Integration)
* 如果涉及全局事件广播，检查 `SignalBus.gd` 是否有对应大驼峰信号，如无则在 `SignalBus.gd` 增量追加并补充 `##` 注释。
* 实现 `ExportSaveData()` 与 `LoadSaveData()`。

### 步骤 5：单元验证与交付 (Verification Gate)
* 验证该场景可以独立按 **F6**（运行当前场景）进行测试，不依赖未初始化的主场景环境。
* 确保控制台无报错、无 Missing Dependency 警告。

---

## 三、 任务派发 Prompt 模板 (用于向 Codex/AI 派发任务)

在向 AI 编码助手下达任务时，使用如下标准提示词结构：

```text
你是一个 Godot 4.x 开发者，请严格遵循工程根目录下的 AGENT.md 规范完成以下任务。

【开发目标】：实现 [实体/功能名称，如：Entities/Player/Weapons/Sword]
【核心职责】：
1. 必须在专属的独立小文件夹（大驼峰 PascalCase）内创建场景与代码，严禁与其他子实体文件混放。
2. 仅在 res://Code/Entities/[Path]/ 目录下新建/修改场景与代码。
3. 场景中的所有贴图与动画统一使用 PlaceholderTexture2D 或 ColorRect 等占位符表示，贴图属性通过 @export 暴露。
4. 遵循公共方法大驼峰 + ## 注释、私有方法 _snake_case 的规范。
5. 提供 ExportSaveData() 与 LoadSaveData() 接口，保证 _init() 安全无参可构造。
6. 保证该场景可独立按 F6 运行测试。

请开始构建并交付代码。
```

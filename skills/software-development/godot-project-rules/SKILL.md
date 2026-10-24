---
name: godot-project-rules
description: Use when setting Godot architecture, AGENT.md, or standards.
version: 2.0.0
---

# Godot 4.x 项目开发规范与协作准则 (Godot 4.x Coding Standards)

> **适用范围**：本规范仅适用于程序开发与代码编写（Coding Only），面向人类程序员与 AI 辅助编码助手（Codex / Claude / Hermes 等）。  
> **核心目标**：实现高内聚、低耦合的模块自治开发，从架构层面根绝 Git 合并冲突，保证代码高度规范、可读与可复用。

---

## 一、 权限边界与文件操作限制 (Strict Scope)

1. **绝对可写区域**：
   - 开发者与 AI 编码助手**仅允许修改 `res://Code/` 文件夹下的代码与场景文件**。
2. **只读与引用区域**：
   - `res://Code/` 之外的所有文件（如 `res://Assets/` 美术切片、音频素材、第三方插件等）仅供**查看与引用**，严禁通过代码或脚本修改其原始内容。
3. **保护底层配置**：
   - **严禁擅自改动 Godot 的底层配置文件**（如 `project.godot` 核心改动、`.godot/` 缓存、全局物理/渲染底层设置等），防止引发团队 Git 恶性冲突。
4. **文件引用与导入完整性**：
   - 提交任何 `.tscn` 场景或 `.gd` 脚本前，必须保证所有外部依赖与文件导入的正确性，严禁提交存在断链（Missing Dependency）的文件。
5. **美术素材重命名与引用排查**：
   - 重命名任何被场景或代码引用的素材文件（如从原始画师导出的临时命名 `IMG_xxxx.PNG` 改为规范 `snake_case.png`）前，必须先行全盘检索 `.tscn`、`.tres`、`.gd` 确认是否有硬编码引用路径；重命名后需同步更新关联的 `.import` 配置文件，严禁产生悬空资源引用。

---

## 二、 架构设计与目录结构 (Architecture)

工程严格采用 **“树状实体自治”** 架构，`Code/` 下的目录层级划分如下：

```text
res://Code/
├── Autoloads/               # 全局单例/挂载项（如：Global 常量、SignalBus 信号总线、Util 工具单例、Data 数据字典等）
├── Common/                  # 通用/可复用的类、抽象基类和工具组件（如通用状态机、UI基类模版等）
└── Entities/                # 总入口：所有的业务场景和功能模块都封装在 Entities/ 目录下
    ├── Player/              # 实体/功能独立文件夹（大驼峰 PascalCase）
    │   ├── Player.tscn      # 实体主场景
    │   ├── Player.gd        # 主脚本
    │   └── PlayerState.gd   # 附属逻辑
    ├── Inventory/           # 独立功能系统
    └── Enemy/
```

### 协作与复用铁律：
1. **实体树状自治**：
   - `Entities/` 采用自顶向下的树状嵌套结构：大场景/大实体包含小场景/小实体。每个实体/功能必须建立属于自己的独立文件夹，形成独立自治的小树。
   - 团队成员按“大实体/大功能”独立认领任务并在各自的实体文件夹内开发，彼此互不干涉，从根本上杜绝代码合并时的冲突。
2. **优先检索与复用**：
   - 在进行任何组件或功能开发时，**必须优先检索 `Autoloads/` 和 `Common/` 中是否有可复用的元素、工具函数、常量定义或数据字典**。
3. **向后兼容与不可破坏性**：
   - **原则上不得删减和修改 `Autoloads/` 和 `Common/` 文件夹中的既有内容**。如需扩展通用能力，仅允许在现有脚本中进行**增量添加**（添加新方法或扩展新数据字段），严禁破坏既有接口。

---

## 三、 脚本编写与命名规范 (GDScript Style Guide)

### 1. 命名与注释规范
* **文件夹命名**：统一使用首字母大写的大驼峰写法（PascalCase，如 `ExampleFile/`、`PlayerController/`）。
* **公共方法 (Public Methods)**：
  - 能被此脚本外部获取并调用的函数或方法，统一使用 **大驼峰命名法（PascalCase）**（如 `ExampleFunc`、`ApplyDamage`）。
  - **所有公共方法上方必须附带 `##` 文档级注释**，详细写明函数用法、入参含义及传参规范。**禁止写英文注释，必须全部使用中文。**
* **内部私有方法 (Private Methods)**：
  - 仅限本脚本内部调用的私有函数，统一使用 **下划线 + 小蛇形命名法（snake_case）**（如 `_example_func`、`_update_internal_state`）。
* **常量与数据变量**：
  - 必须优先查看 `Autoloads/`（如 `Global.gd`、`Data.gd`）中是否有确定好的 `const` 常量或字典形式定义的变量。常量使用全大写下划线（`MAX_SPEED`）。

### 2. 信号总线规范 (SignalBus Standard)
* `Autoloads/SignalBus.gd` 中的所有全局信号，统一使用 **大驼峰命名法（PascalCase）**。
* **每一个信号上方必须附带 `##` 文档级中文注释**，说明信号触发的时机与携带参数的含义：

```gdscript
# Autoloads/SignalBus.gd

## 当玩家血量发生变动时广播
## @param current_hp: 当前血量值
## @param max_hp: 最大血量值
signal PlayerHealthChanged(current_hp: int, max_hp: int)

## 当关卡完成切换并加载就绪时广播
## @param level_id: 关卡唯一识别字符串
signal LevelLoaded(level_id: String)
```

### 3. 公共方法与实体逻辑示例

```gdscript
class_name PlayerController
extends CharacterBody2D

@export var move_speed: float = 200.0

## 造成指定数值的伤害
## @param amount: 扣除的血量数值（整型）
## @param damage_type: 伤害类型枚举（从 Global.DamageType 中获取）
## @return: 是否导致实体死亡（布尔值）
func ApplyDamage(amount: int, damage_type: int) -> bool:
    var is_dead: bool = _internal_calculate_damage(amount, damage_type)
    return is_dead

# 内部私有处理逻辑
func _internal_calculate_damage(amount: int, type: int) -> bool:
    # 内部计算细节...
    return false
```

---

## 四、 实体设计与存档系统规范 (Entity Lifecycle & Save System)

编写 `Entities/` 目录下的实体与业务模块时，必须前置考虑**存档与读档机制**：

1. **暴露标准存档数据接口**：
   - 每个需要持久化状态的 Entity 必须显式提供导出状态数据（如字典形式）和加载状态数据的方法：
     - `func ExportSaveData() -> Dictionary`: 提取当前实体的核心状态数据（如位置、血量、装备状态、计数器等）。
     - `func LoadSaveData(data: Dictionary) -> void`: 恢复并应用传入的存档数据。
2. **生命周期与 `_init()` 实例化安全**：
   - 保证任何时候 Entity 的读档与动态生成正确无误。
   - **`_init()` 必须具备默认无参或安全默认值构造能力**，严禁在 `_init()` 中强制要求非空外部上下文，避免反序列化/加载场景时因参数缺失崩溃。
   - 外部依赖与节点绑定统一在 `@onready` / `_ready()` 或通过 `LoadSaveData()` 注入，确保实体可在任意时刻独立被安全实例化和还原。

---

## 五、 节点组织与 UI/输入实践 (Nodes & Input)

1. **场景构建方式**：
   - **必须尽量在场景树（.tscn）中手动放置好节点**，在脚本中通过 `@onready` 获取节点引用并进行操纵。
   - **严禁在脚本里面动态大量生成场景树节点**（避免通过代码动态 `new()` 构建复杂节点树，保持场景结构的可视化）。
2. **鼠标交互与输入检测规范**：
   - **点击判定**：遇到需要检验鼠标点击输入的组件，统一使用**纹理为空的 `TextureButton`**（或透明遮罩 Button）。
   - **悬停/进入检测**：遇到需要检验鼠标进入/悬停时，统一使用**挂载到 `Sprite2D` 下的 `Area2D`**（并规范配置物理碰撞箱 `CollisionShape2D`）。
3. **UI 锚点规范 (Control Anchors)**：
   - 使用 `Control` 类节点时，必须严格规划并配置好**锚点系统（Anchors Preset）与容器布局（Containers）**，确保在不同窗口分辨率拉伸时 UI 布局保持正确，严禁随意绝对像素定位。
4. **弹窗/遮罩 UI 默认可见性 (Modal & Overlay Default Visibility)**：
   - 带有全屏遮罩（如半透明 `ColorRect`、模态弹窗、系统设置等）的 UI 场景，其根展示容器在 `.tscn` 模板中默认必须保持 `visible = false`（由代码在运行时根据按键或事件动态唤出），或避免在编辑器层级常驻展开；防止被嵌套实例化到 `Player` 或 `World` 时在 2D 编辑器视口遮挡地图绘制与关卡摆放。

---

## 六、视觉表现层与逻辑组件边界 (Visual / Logic Boundary)

1. **先判定需求所在层级**：用户明确描述的是贴图、TileMap、符文标识、Shader 或状态外观时，默认按纯视觉需求处理；不要主动把碰撞生成、点击锚点、交互扫描或全局管理器卷入方案，因为这些会把局部换皮升级成危险重构。
2. **视觉状态由逻辑真值驱动**：逻辑组件继续持有矩形范围、碰撞、玩家效果和状态切换；只通过公开信号通知视觉层。视觉层不得反向推导或控制物理状态。
3. **可编辑视觉预置在场景中**：在 `.tscn` 内预置转换前后的视觉子节点；转换前可用纯视觉 `TileMapLayer` 自由绘制砖块与符文，转换后可用可拉伸节点承载纹理与 `ShaderMaterial`。符文若仅用于提示玩家，就不得添加独立碰撞或交互逻辑。
4. **实例自治而非全局互斥**：一次操作只切换命中的组件实例，但各实例可独立保持状态；除非玩法明确要求，否则不要引入全局唯一激活管理器。
5. **渐进兼容旧视觉**：保留旧占位视觉作为未配置新视觉时的回退；新视觉具备有效内容后再隐藏回退节点，避免旧关卡立即失效和新旧视觉叠加。

---

## 七、测试与单例验证 (Testing)

1. **最小单元单例测试**：
   - 对每一个最小单元的组件/功能模块，都必须进行**单例独立测试**。
   - 每个实体场景必须保证能够**独立按 F6 运行**并验证其基本交互与逻辑闭环，严禁强耦合未初始化的外部全局依赖。
2. **AI 辅助编码执行准则**：
   - AI Agent 在编写或修改代码时，必须严格遵循上述目录范围（仅限 `Code/`）、SignalBus 命名与中文注释、Entity 存档生命周期规范、大驼峰公开方法+中文 `##` 注释以及场景节点手动预置的规则。

---

## 八、Git 提交与代码审查检查清单 (Git Pre-Commit / Review Checklist)

在审查或准备提交 Git 改动时，严格检查并拦截以下常见违规项：
1. **禁止底层配置外溢**：检查 `git diff` 中是否意外修改了 `project.godot`（如音频总线 uid/路径替换、输入映射等）或引擎缓存。发现后先确认改动来源并备份工作区，再仅定点撤销自己的差异；禁止用 `git checkout` / `git restore` 覆盖用户未提交内容。
2. **禁止英文注释**：凡在 `SignalBus.gd` 或 `Entities/` 新增/修改的代码，若带有英文 `##` 文档注释或行内英文注释，必须全量纠正为中文。
3. **实体必带存档接口**：凡具有内部状态变更的实体脚本，必须声明并实现 `ExportSaveData() -> Dictionary` 与 `LoadSaveData(data: Dictionary) -> void`。
4. **禁止越界修改非代码场景**：世界关卡/拼接大场景文件（如 `World/*.tscn`）若被代码助手改动，必须核实是否有正当理由，严禁擅自改动。

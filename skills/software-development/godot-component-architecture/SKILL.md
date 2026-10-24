---
name: godot-component-architecture
description: Use when creating zero-intrusion Godot components.
---

# Godot 4.x 实体组件与交互解耦规范

本 Skill 沉淀在 Godot 4.x 项目中设计“可交互组件”、“物理阻挡与触区消失组件”等独立自治组件时的通用架构、零侵入规范及避坑要点。

---

## 一、 核心原则：零侵入与自治闭环 (Zero-Intrusion Autonomy)

1. **绝对不修改被作用主体（如 Player.gd）**：
   - 坚决杜绝为了局部环境效果（如泥潭、深水减速、重力风场）而在核心角色脚本中增加字段或方法。
   - 环境物理修饰必须作为**自治组件**由外部施加，组件删除或禁用时角色完全不受影响。
   - 交互与物理判定由组件自闭环处理，挂载 `Area2D` 自行监听 `body_entered` / `body_exited`。
   - 按键检测在组件自身的 `_unhandled_input(event)` 中捕获，并在触发时调用 `get_viewport().set_input_as_handled()`。

2. **必须交付开箱即用的 `.tscn` 场景组件**：
   - 当用户要求封装组件时，**绝对不能仅生成单个 `.gd` 脚本**。
   - 必须同时交付配套的 `.tscn` 场景文件（预挂载脚本、配置好默认的 `CollisionShape2D` 或渲染节点及其尺寸），以便关卡策划/用户直接拖拽进 2D 视口实例化并自由调整尺寸与摆放。

3. **状态推进与多阶段信号解耦**：
   - 交互通常分为多阶段（例如：第 1 阶段展示物品/NPC 描述，第 2 阶段主角独白，后续阶段进入对话树）。
   - 组件内部管理交互阶段计数器，对外仅广播标准化事件信号：
     - 本地信号：`Interacted`, `DescriptionRequested`, `MonologueRequested`。
     - 全局总线（如 `SignalBus`）：`ComponentInteracted`, `ComponentDescriptionRequested`, `ComponentMonologueRequested`。
   - 视觉与 UI 系统通过订阅信号驱动，交互组件本身不负责复杂的文本气泡排版。

4. **先判定改动属于视觉层还是逻辑层**：
   - 用户只要求改变组件外观或关卡搭建方式时，不要主动把碰撞、交互范围、状态机或全局管理器卷入重构；纯视觉问题扩大成系统重构会显著增加旧场景回归风险。
   - 保留逻辑组件作为状态真值源，只公开状态变化信号；预置视觉子节点订阅该状态并自行切换显示。不要让逻辑层读取视觉 TileMap 的格子来推导碰撞、尺寸或归属。
   - 转换前需要自由拼装时，使用纯视觉容器承载 `TileMapLayer`、`Sprite2D` 或其他 `CanvasItem`，并确保视觉不参与碰撞与导航。砖块适合继续使用项目统一 TileSet；符号、符文和装饰若尺寸、锚点或法线材质不适合 TileSet 单元，就改用独立 `Sprite2D`，不要为塞入 TileMap 而缩放、裁切或重建图集。纯提示视觉不得增加独立点击、碰撞、目标检测或逻辑锚点。
   - 不要让整个转换前视觉容器继承 TileMap 的导入缩放：将砖块 TileMap 与符文 Sprite 放在并列视觉分支，各自保留独立 `scale`；两者通过同一状态同步函数共同显隐。
   - 独立符文需要法线图时，优先让 `Sprite2D.texture` 使用含 diffuse/normal 通道的 `CanvasTexture`，或在该 Sprite 上挂 `ShaderMaterial`；WaterFlow 等逻辑组件只切换可见性，不读取法线资源。验收时同时确认场景存在适用的 2D 光源，否则“配置成功但无可见法线效果”不能算视觉验证完成。
   - 当组件本体需要拉伸碰撞范围、但策划绘制的转换前视觉必须保持自身比例时，让每个固定比例分支（如砖块 `TileMapLayer`、符文 `Node2D/Sprite2D` 容器）设置 `top_level = true`，再分别用同级 `RemoteTransform2D` 指向它们并设置 `update_scale = false`。这样各分支跟随组件的位置和旋转、保留各自本地缩放，却不继承父级非均匀拉伸；不要把 Sprite 放进固定为 `0.048` 等导入倍率的 TileMap 分支，否则符文会再次变小。
   - 转换后需要一张连续、可拉伸并支持 Shader 的矩形视觉时，预置 `NinePatchRect`、`TextureRect` 或合适的 `Sprite2D`；纹理和 `ShaderMaterial` 留给实例配置，不把具体美术资源焊死进通用组件。
   - 视觉节点必须预置在 `.tscn` 中，便于策划实例化后启用“可编辑子节点”直接搭建；不要为这种固定结构在运行时大量 `new()`。
   - **通用基类组件与派生组件结构同构**：用于防止拉伸形变的架构节点（如配置 `top_level = true` 的 `BeforeVisual`、`BeforeSpriteVisuals` 容器及配套的 `RemoteTransform2D(update_scale = false)`）必须直接固化在基础组件 `.tscn`（如 `WaterFlowArea.tscn`）中，严禁仅在特定关卡派生场景（如 `OasisWaterFlowArea.tscn`）里局部补丁；确保任意关卡直接实例化基础组件并拉伸时，视觉比例均不会被非均匀缩放破坏。
   - **基类场景结构提升与派生场景（Inherited Scene）冲突清理**：
     - 当把派生场景（如 `OasisWaterFlowArea.tscn`）中验证成熟的新增节点提升反哺回基类 `.tscn` 时，必须立即清理派生 `.tscn` 中的重复定义。移除派生场景中对这些节点的带有 `type="..."` 的新节点声明，转为纯继承或仅保留特化的属性覆写与专属子节点（如 `RuneSprite`），避免 Godot 解析派生场景时因节点重名/类型冲突解析失败。
     - 向通用基类 `.tscn` 追加新节点时，务必追加在子节点列表末尾，严禁插入已有子节点中间，以防破坏关卡既有实例中按 `index="N"` 绑定的属性覆写关系。
   - 扩展已有组件时保留公开方法、碰撞行为和旧占位视觉。新视觉有有效内容时隐藏旧占位以防叠加；未配置时自动回退旧视觉，使历史实例无需一次性迁移。
   - 每个组件实例只切换自身视觉；除非需求明确规定全局互斥，不要引入全局管理器。
   - 状态信号必须携带最终状态值；初始化时同步一次视觉，运行期仅在真实状态变化后发出，避免重复副作用。

### 视觉扩展的低风险实施顺序

1. 将用户在现有实现讨论中提出的“这个组件也一样”“按另一个组件的要求”等表述视为实施指令：先读取被参照组件的 `.gd` / `.tscn`，再直接落库；不要只复述或口头确认需求。只有信息不足以确定改动目标时才追问。
2. 完整读取目标 `.gd`、`.tscn` 及公开方法调用点，列出不能改变的接口和节点依赖。
3. 在原组件中预置前态/后态视觉子节点，不删除旧节点。
4. 增加单一视觉同步函数，由初始化和既有状态切换入口共同调用；不要复制第二套状态机。
5. 对“新视觉是否已配置”做简单、确定的内容检测或提供显式导出开关，并实现逐状态回退。开放视觉容器的检测不得只检查 TileMap 已用格子：还要识别配置了纹理的 `Sprite2D` / `TextureRect` 等受支持视觉，且状态切换时分别控制各分支，避免一个空 TileMap 隐藏已经配置好的符文。
6. 用至少两个实例验证彼此独立，再验证未配置新视觉的旧场景仍可加载和切换。
7. 运行 Godot headless 导入/场景加载与最小运行时测试；涉及 `top_level + RemoteTransform2D` 时，测试必须给父组件设置非单位、非均匀缩放，并分别断言 TileMap 与 Sprite 容器跟随位置/旋转而各自世界缩放保持不变。测试还要给 Sprite 动态配置一张有效纹理，验证固态显示、流体态隐藏及后态视觉显示；测试脚本自身必须先成功解析，不能拿仅编辑器退出码代替行为断言。最后执行 `git diff --check` 和限定路径的 `git status`，确认没有修改无关关卡或资源。
8. 只有文件已修改且上述验证真实通过后，才向用户报告“已实现”；如果只是梳理要求，必须明确说尚未改动，不能用完成式措辞。

---

## 二、 动态循环视差与无缝表面组件规范 (Looping Parallax & Seamless Surfaces)

在处理“水面起伏滚动”、“无限背景平铺”、“流云/传送带”等动态视觉组件时：

### 1. 瓦片图集（Atlas）直接位移的踩坑机理与规范方案
- **避坑：为什么不能在 TileMapLayer 或全图集上直接改 UV 位移？**
  - **机理**：TileMap 瓦片通常来自同一张合并大图（Atlas）。如果在 Shader 中对 `UV` 做 `UV.x += TIME * speed`，采样范围会直接溢出该瓦片边界，把图集邻近其他瓦片的像素杂色扯出拉花。
- **解法选型**：
  - **方案 A（Parallax2D 节点方案，推荐度最高）**：
    Godot 4.3+ 引入了原生 `Parallax2D`。将无缝单张切片设为子级 `Sprite2D`（`centered = false`），在 `Parallax2D` 上配置：
    - `repeat_size = Vector2(tile_width, 0.0)`：严格等于单张瓦片的物理宽度，保证首尾无缝平铺。
    - `autoscroll = Vector2(speed, 0.0)`：由引擎渲染管线驱动恒定无缝位移，零 CPU 开销且绝对不会断层跳动。
    - `repeat_times = N`：根据关卡水平跨度设置平铺次数。
  - **方案 B（TextureRect 无缝平铺 + CanvasItem Shader）**：
    仅在必须自定义复杂折射/正弦畸变时使用，贴图导入设置为 Repeat 模式。

### 2. 图集单片切片提取与资源隔离
- 当所需图块深嵌在合并大图（如 `2_grid665.png`）中时，切勿要求关卡策划手动截图或引入庞大纹理坐标系。
- 在 `res://Art/.../extracted/` 目录下由脚本/工具无损截取单格像素（如 `665x665`），保留无缝边界并单独存储为独立 PNG，与组件预制体打包交付。

### 3. 外部生成组件的 Godot UID 同步机制（避免编辑器无法识别）
- **避坑：为什么外部直接生成的 `.tscn` 在 Godot FileSystem 面板中可能找不到或加载报错？**
  - **机理**：Godot 4.x 深度依赖资源的唯一标识符（UID，形如 `uid://...`）。当外部脚本写入新的 `.png` 或 `.gd` 时，Godot 后台会在 `.import` 或 `.uid` 文件中生成确定的 UID。若手动编写的 `.tscn` 中使用了占位伪 UID 或与实际不符的 UID，Godot 编辑器索引会失败，导致文件在面板中隐身或报资源缺失。
  - **规范流程**：
    1. 写入纹理/脚本文件后，检查同名 `.png.import` 或 `.gd.uid` 中的真实 UID。
    2. 将真实的 `uid://...` 填入 `.tscn` 的 `[ext_resource uid="uid://..."]` 头部，确保 Godot 引擎瞬间无感索引。

### 4. 父子层级与 Scale 嵌套下的循环平铺计算规范 (Repeat Count Calculation)
- **多层 Scale 嵌套换算准则**：
  若组件作为已缩放父节点（如 `TileMapLayer` 设置了 `scale = (sx, sy)`）的子级，计算 `repeat_count` 或 `repeat_times` 必须归一到同一坐标系：
  - 单循环单元有效物理宽度：$W_{unit} = tile\_width \times local\_scale.x$
  - 目标水域/地面总跨度：$W_{target} = N_{tiles} \times tile\_size.x$（父局部空间）
  - 所需循环数：
    $$\text{repeat\_count} = \left\lceil \frac{W_{target}}{W_{unit}} \right\rceil + \text{Margin (2~3)}$$
- **像素对齐建议**：
  强烈建议让平铺装饰组件的 `local_scale` 保持 `(1.0, 1.0)` 与父级瓦片像素网格 1:1 绝对对齐，避免因浮点缩放导致的贴图拉伸、缝隙漏光或摩尔纹；循环数直接设定为目标瓦片数加少量边缘余量。

---

## 二、 致命与即死区域组件规范 (Instant Kill & Hazard Areas)

在设计深渊、尖刺、激光或即死边界（如 `InstantKillArea`）时：

### 1. 避坑：为什么不能仅依靠通用伤害函数（ApplyDamage）？
- **机制机理**：多数动作角色拥有无敌帧（i-frames）、护盾、免伤百分比或受击冷却逻辑。如果即死判定只调用 `ApplyDamage`，当玩家处于受击无敌或硬直状态时，伤害调用会被直接吞掉，导致即死失效。
- **标准双重处死保障**：
  1. 先调用角色通用的打击/伤害接口：`body.ApplyDamage(999999.0, Vector2.ZERO)`，触发正常的受伤声效、屏幕震动或被击信号。
  2. 兜底直接覆盖底层数值：检测 `"now_HP" in body` 并设置 `body.now_HP = 0.0`。利用属性 setter 强制清空生命，绕过免伤直接切入状态机的 `died` 状态并执行关键脱钩逻辑（如 `ReleaseRope()` 释放抓钩）。

### 2. 碰撞层契约与纯检测优化
- 严格遵循项目的碰撞契约：玩家处于 Layer 2（`collision_layer = 2`, `collision_mask = 5`）；陷阱/环境交互组件设置 `collision_layer = 4`, `collision_mask = 2`。
- 纯检测区域设置 `monitorable = false`，仅作为感知器（`monitoring = true`），避免其他组件对其进行多余的反向检测，减少物理引擎计算负载。

### 3. 初始重叠与启停补检规范 (Initial Overlap Edge Case)
- **机制机理**：物理引擎的 `body_entered` 仅在物体由“外部”跨入“内部”的物理帧触发。若玩家刚进入关卡出生点就在即死区内，或者区域通过动态开关由 `enabled = false` 切换为 `true` 时玩家已在区域内部，`body_entered` **绝对不会触发**，造成漏判。
- **标准补检实现**：
  在 `_ready()` 以及当 `@export var enabled: bool` 被设为 `true` 时，主动调用 `get_overlapping_bodies()` 执行一次全量检查：
  ```gdscript
  func _check_overlapping() -> void:
      for body in get_overlapping_bodies():
          _kill_body(body)
  ```

---

## 二、 机关信号网络与聚合判定模式 (Mechanism Signal & Multi-Source Gate)

在设计开关（压力板、拉杆、按钮）与受控对象（门、陷阱、移动平台）的联动时：

### 1. 组件状态暴露与 Inspector 可视化调试规范 (State Exposure & Setter Decoupling)
- **按压/激活状态必须暴露 @export setter**：
  组件内部布尔状态（如 `is_pressed` / `is_active`）若只用私有变量 `_is_pressed`，关卡策划无法在 Godot Inspector 面板中预览或手动测试不同初始状态。
  标准模式：
  ```gdscript
  @export_group("Pressure Button State")
  @export var is_pressed: bool = false:
      get:
          return _is_pressed
      set(value):
          if _is_pressed == value:
              return
          _is_pressed = value
          _update_visual_and_position(value)
          pressed_state_changed.emit(value)
          SignalBus.MechanismChannelStateChanged.emit(output_channel, value)
  ```
- **存档生命周期与 Setter 纯净复用**：
  `ExportSaveData()` 统一持久化导出 `"is_pressed": _is_pressed`；`LoadSaveData(data)` 读取后直接赋值 `self.is_pressed = data.get("is_pressed", false)`，保证读档反序列化、编辑器 Inspector 手调、运行时物理踩踏均走同一套状态同步与信号派发逻辑。
- **初始存档插槽同步**：
  为既有场景新增开关组件持久化时，必须同步初始化默认存档插槽（如 `save_slot_1.json`），明确写入 `"is_pressed": false`，严禁让新游戏读取到未定义或残缺的历史脏数据。

### 2. 避坑：为什么单纯广播全局 Bool 状态无法支持“多开关控一门”？
- **机制机理**：如果受控门直接监听 `MechanismChannelStateChanged(channel, is_active)` 并无条件执行 `is_open = is_active`，当两个按钮绑定到同一频道时，按钮 A 按下广播 `true`（门开），随后按钮 B 抬起广播 `false`（门关），导致开关状态相互踩踏覆写。
- 受控组件若需要满足“所有开关均激活才开门（AND）”或“任一开关激活即开门（OR）”，必须**在受控端维持状态注册表**，不可将单次布尔广播直接当作最终状态。

### 2. 标准解耦方案：聚合状态表与多对一判定
- **方案 A（节点直接引用，关卡摆放直观）**：
  受控门暴露 `@export var bound_switches: Array[PressureButton] = []`。
  受控端在 `_ready()` 中订阅各个开关的独立状态改变信号，内部记录 `_switch_states: Dictionary[PressureButton, bool]`。任一开关状态变更时，检查 `_switch_states.values().all(func(v): return v)`。
- **方案 B（频道解耦聚合）**：
  每个开关分配独立 output_channel（如 `door_gate_1_a`, `door_gate_1_b`）。
  受控门暴露 `@export var required_channels: Array[StringName] = []`，在收到全局广播时更新本地字典 `_channel_states[channel] = is_active`，仅当所有 `required_channels` 在字典中均为 `true` 时触发动作。

---

## 三、 外部物理修饰区域规范 (Area2D External Modifiers)

实现对角色物理状态（如减速、滑冰、风力推挤）的零侵入干预：

### 1. 避坑：为什么单纯在后处理中修改 `body.velocity.x` 无法有效减速？
- **机制机理**：多数动作角色的 `_physics_process` 每帧都包含持续方向输入判定与极高的加速度（例如 `velocity.x = move_toward(velocity.x, speed * input, acceleration * delta)`，加速度常高达 2000~3000）。
- 外部 Area2D 即便设置 `process_physics_priority = 100` 强行拉低 `velocity.x`，在下一帧角色的物理帧开始时，角色会立即以数千加速度重新加速回原目标速度，导致减速效果近乎完全失效（肉眼完全看不出减速）。

### 2. 标准零侵入外部速度调控模式（属性暂存与按需还原）
- **核心做法**：角色若暴露了基础移速属性（如 `body.speed`），Area2D 监听 `body_entered` 与 `body_exited`，在角色进入时记录原始速度至字典 `_original_speeds[body] = body.speed`，并直接调低 `body.speed = orig * speed_multiplier`；在离开或 Area `_exit_tree()` 时精准还原。
- **冲刺/技能豁免处理**：在组件自身的 `_physics_process` 中轮询检查角色当前状态（如 `body.move_state_machine.cur_state_name == "dash"` 或 `body.is_special_state`）。若处于豁免状态，临时拉回原始速度 `orig_speed`；退出特殊状态后再施加减速倍率，既保证水体减速生效，又不破坏冲刺手感。
- **纯外力/推流（如顺水或风场）**：对于强制位移类修饰，不可单纯改瞬时速度，应通过 `body.position` 偏移或向角色支持的外力累加器注入向量。

---

## 四、 路径载具（PathFollow2D）模式切换与平滑惯性规范

当实现沿 `Path2D` / `Curve2D` 航行的载具（如 `OasisBoat`），并需要在“伴随玩家巡航”与“特定解谜先行”之间切换时：

### 1. 航段级属性驱动（StopPoint As Segment Config）
- 将模式配置下沉到路线节点（`StopPoint` Resource）中，避免使用臃肿脆弱的全局状态机：
  - `follow_player: bool`：该航段是否伴随玩家（防甩开保护）。
  - `max_lead_distance: float`：领先玩家的最大容许距离。
  - `is_transit_point: bool`：是否为过路状态切换点。
- **过路切换点（Transit Point）**：
  当载具到达该进度点时，**完全不停留、不切入 WAITING 状态、不重置速度**，仅作为航段属性切换标志，直接平滑切入下一航段的目标点。

### 2. 惯性物理平滑（杜绝骤停骤起）
- 严禁直接使用固定的 `progress += speed * delta`。
- 引入内部实时速度 `_current_speed`，配合 `acceleration` 与 `deceleration`：
  - 当领先玩家超过容许阈值（或前方检测到障碍）时，将 `target_speed` 设为 `0.0`（在 60%~100% 距离范围内线性插值减速）；
  - 解谜先行路段（`follow_player == false`）或玩家在船上时，`target_speed = speed`；
  - 推进时使用 `_current_speed = move_toward(_current_speed, target_speed, accel * delta)`，再累加 `progress += _current_speed * delta`，实现真实水面/滑行惯性。

---

## 二、 物理阻挡与触发消失模式 (Vanishing Blocker)

在关卡中实现“阻挡主角并能在到达某处时平滑消失”时：

### 1. 为什么坚决避免逐帧绝对坐标判定？
- 移动插值或物理步长极易导致单帧越过判定点；
- 编辑器中手输 `Vector2(x, y)` 极易在关卡重构时失效。

### 2. 标准触发解法：远程触区 vs 接触触区 (Trigger Area vs Touch Area)
- **避坑：分清“阻挡物自身碰触”与“玩家踩入远端触发区”**：
  - `StaticBody2D` 确实没有 `area_entered` 信号，但绝不能把“主角踩入机关”误写成“阻挡物每帧发起 `intersect_shape` 检测阻挡物是否与 `target_area` 重叠”。如果阻挡物在 A 点（如门口），触发区在 B 点（如开关台），阻挡物永远不会与触发区重叠，导致死锁。
  - **正确做法**：如果阻挡物是远端由玩家踩点触发，阻挡物应该在 `_ready()` 中监听 `target_area.body_entered`（或遍历 `vanish_zone_group` 组的 `Area2D` 连接其 `body_entered`）。当 `body` 属于玩家时，调用阻挡物的 `Vanish()`。
  - **单一目标区域**：暴露 `@export var target_area: Area2D`，在场景树中直接拖拽关联，并在 `_ready()` 中 `target_area.body_entered.connect(_on_trigger_body_entered)`。
  - **多出口/多路径场景**：暴露 `@export var vanish_zone_group: StringName = &"VanishZone"`。
    - 在 `_ready()` 中遍历 `get_tree().get_nodes_in_group(vanish_zone_group)` 动态连接每个 `Area2D` 的 `body_entered` 信号。
    - 关卡策划可以在任意出口放置 `Area2D` 并加入该组，玩家碰触任意一个区域即可触发消失。

### 3. 消失销毁的三步安全流程
```
[1. 广播 VanishStarted] ──> [2. call_deferred 撤销 Collision] ──> [3. Tween 淡出后 queue_free]
```
- **关键细节**：必须使用 `collision_shape.set_deferred(&"disabled", true)` 在物理帧安全撤销碰撞体，避免当帧物理锁死报错，并让主角立即恢复通行。
- 淡出通过 `create_tween().tween_property(self, "modulate:a", 0.0, fade_duration)` 实现，结束后派发 `Vanished` 信号并执行 `queue_free()`。

---

## 三、 多阶段关卡与碰撞动态切换避坑 (Phase Switching & Collision Disabling)

在实现“去程 / 返程 / 多阶段地图切换”时，动态隐藏与禁用某阶段分支时存在典型物理坑点：

### 1. 为什么 `visible = false` 和 `process_mode = DISABLED` 无法关掉物理阻挡？
- **物理服务器独立注册机制**：Godot 的 `process_mode = PROCESS_MODE_DISABLED` 仅停止节点的逻辑轮询（`_process` / `_physics_process`），**不会注销已注册进 PhysicsServer2D 的碰撞形状**。
- `StaticBody2D` 以及 **Godot 4 的 `TileMapLayer`** 即使在被禁用/不可见的父节点下，碰撞依然有效，会导致去程阶段撞上返程的空气墙。

### 2. 标准物理开关规范
阶段切换管理方法（如 `_set_phase_enabled(phase: Node2D, enabled: bool)`）中，必须递归处理物理节点：
- **`TileMapLayer` 地形碰撞**：显式设置 `node.collision_enabled = enabled`。
- **常规碰撞体**：`CollisionShape2D` 与 `CollisionPolygon2D` 必须使用 `node.set_deferred("disabled", not enabled)`。
- **触发区/交互区**：如挂载有独立 `Area2D` 或交互组件，其子碰撞形状也通过上述递归统一禁用，防止静默触发事件。

---

## 四、 Codex / AI 协作与交付清理门禁

当通过 Codex 完成组件落库时：
1. **统一存放路径**：严格遵照项目规范，在 `res://Code/Entities/InteractiveComponent/[ComponentName]/` 创建独立专属文件夹，包含 `.gd` 与 `.tscn`。
2. **清理测试污染**：Codex 可能会建立临时的 `ComponentTests/` 目录或在关卡场景中挂载测试实例。交付验收前必须强制检查 `git status`，清理所有临时测试目录并还原测试改动的既有关卡场景，保持 git 工作区干净。

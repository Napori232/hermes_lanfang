---
name: godot-level-phase-and-respawn
description: Use when handling Godot level phases, respawns, or debuffs.
---

# Godot 关卡阶段流转与复活重置规范 (Level Phase & Respawn Lifecycle)

规范 Godot 4.x 项目中多阶段关卡（如探索/返程、追逐战）、重生点（Checkpoint/Tent）、移动器组件（Mover）、外部状态/Debuff 影响及存读档联动时的状态生命周期与闭环重置逻辑。

---

## 核心原则 (Core Rules)

1. **阶段回退必须双向闭环，并拆分“复位”与“激活” (Bidirectional Phase State)**
   - 关卡存在多阶段（例如 `OutwardPhase` 与 `ReturnPhase`）时，玩家死亡复活若需重新由交互物（骨头、开关）触发下一阶段，关卡主控必须将场景阶段彻底切回前置阶段：
     - 重新启用前置阶段节点树的渲染与处理：`process_mode = Node.PROCESS_MODE_INHERIT`, `visible = true`。
     - 显式恢复前置阶段内所有交互组件的碰撞与判定区域，严禁停留在追逐阶段导致前置交互物处于禁用状态。
     - 禁用并隐藏后置阶段节点，阻断正在运行或残留的阶段逻辑。
   - 按固定时序实现追逐战重开，明确区分“死亡时立即复位”和“交互后复苏”：
     1. `PlayerDied` 根据**语义状态**（已进入追逐、且追逐未结束）锁存 `reset_on_respawn = true`，并在死亡信号当帧立即调用 `ResetChase()`；先同步令 `_active = false`，再关闭伤害/实体碰撞、停止运动并复位，禁止把首次重置推迟到复活。
     2. `PlayerRespawned` 只做幂等兜底：再次确认 Boss 已归位、隐藏且休眠，同时恢复前置阶段与交互物；不得自动启动追逐。
     3. 交互物信号才调用 `StartChase()`；启动顺序固定为：复位 Boss 根节点与实际 Mover → 清速度和阶段计时 → 显示 → 恢复碰撞/伤害 → 激活运动。
   - 关闭 `Area2D.monitoring` 通常需要 `set_deferred()`；因此伤害回调还必须同步检查 `_active`。否则重置前已排队的 `body_entered` 仍可能在同一物理帧发出重复致死请求。玩家侧也应忽略“生命值已为零/已处于死亡状态”的重复即时死亡请求。
   - 不要用 `TileMap.get_used_rect()`、角色是否仍在某块地图内等空间边界决定是否重置；Boss、击退或边缘碰撞可能让玩家死在边界外，使复活信号到来时错误跳过重置。空间检测只适合判断区域进入，不适合作为已启动阶段的生命周期真值。

2. **移动组件 (Mover) 的深度重置、休眠与防闪现 (Deep Reset, Dormancy & Anti-Flash)**
   - 移动实体（如 Boss/Chaser）到达终点或被终止后，必须停止运动并关闭 `KillArea`；“可再次启动”不等于“重置时保持处理和碰撞开启”。
   - `ResetMover()` / `ResetChase()` 不能仅重置 `global_position` 和计时器，必须完成休眠态深度重置：
     - 先同步设置 `_active = false`，让物理更新和已排队的伤害回调立即失效。
     - 停止或禁用实际移动处理，并清空速度、阶段计时、Tween/动画驱动状态。
     - 将实体 `collision_layer` / `collision_mask` 置零，并延迟关闭 `Area2D.monitoring` / `monitorable`。
     - 分别恢复 Boss 根节点与实际 Mover 各自记录的初始全局坐标；父子节点存在各自位移时不可只复位一层。
   - `StartChase()` 才恢复 `process_mode`、实体碰撞层/掩码与伤害区域；恢复这些能力前，必须先完成根节点和 Mover 的坐标及运动状态复位。
   - **防闪现与瞬移残影规范**：实体从追逐中途被瞬移归位到初始出生点时，若保持可见，渲染帧会短暂暴露警示碰撞或光效。重置复活阶段必须强制将追逐实体设为 `visible = false`（隐藏）；只有当玩家重新交互并明确调用 `StartChase()` 时，才显式设为 `visible = true`。

3. **外部区域 Debuff/属性影响的双向解除与复活保底 (External Debuff Reset & Respawn Guard)**
   - 任何零侵入、纯外部属性修改的区域（如水流加速 `WaterFlowArea`、泥沼/减速水体 `SlowWaterArea2D` 等）：
     - 区域本身必须订阅玩家复活全局信号（如 `SignalBus.PlayerRespawned`），在玩家死亡或复活时主动调用 `_restore_all_speeds()`，清空内部暂存字典，防止玩家死在区域内导致退出回调被吞、移速减益常驻。
     - 玩家核心控制类（如 `Player.gd` 的 `Respawn()`）必须提供属性保底重置逻辑：复活时强制将 `speed`（以及跳跃、加速度等核心运动学参数）还原为基础标准预设值（`ExportSettings.player_speed`），切断任何外部未退出的修改残留。

4. **复活点即存档点的数据与位置同步 (Checkpoint as Save Point)**
   - 触发关键节点交互（如拾取骨头、激活复活点）时：
     - 立即更新角色的 `respawn_position`。
     - 触发持久化自动存档 `SaveManager.AutoSave(get_tree())`。
     - 关卡需在 `ExportSaveData()` 导出复活点坐标与到达标志；在 `LoadSaveData()` 恢复时，将玩家 `global_position` 与 `respawn_position` 精准对齐至复活点，并保持场景处于追逐战前等待交互状态。

5. **信号总线无侵入约定 (Non-intrusive SignalBus Rule)**
   - 当特定关卡或功能需要通过 `SignalBus` 广播事件（如 `lock3`），但全局信号总线未预声明该信号时，遵循项目约定严禁修改 `SignalBus.gd`。
   - 统一采用动态反射安全检查：
     ```gdscript
     if SignalBus.has_signal(&"lock3"):
         SignalBus.emit_signal(&"lock3")
     ```

6. **阶段专属背景与视差层规范 (Phase-Specific Scenery & Parallax2D Alignment)**
   - **允许阶段专属背景**：关卡各阶段可有完全不同的背景氛围（如去程地下洞穴无背景、回程逃脱才启用天空/追逐专属背景 `ParallaxScenery`）。
   - **视差节点坐标绝对归零**：无论背景是全局常驻还是阶段专属（挂载在 `ReturnPhase` 等阶段容器下），`ParallaxScenery` 及内部所有 `Parallax2D` 节点本地坐标必须严格为 `Vector2.ZERO`：
     - Godot 4 的 `Parallax2D` 计算相机视差和循环平铺依赖全局对齐。任何非零 `position` 偏移（如关卡编辑器中意外移动至 `(4831, 223)`）都会把渲染区域整体推离相机视野，导致切入阶段后背景看似“隐形消失”。
   - **远端起点视野覆盖与参考对齐**：回程阶段往往从关卡深处（如 `X > 5000` 甚至 `10000+`）开始：
     - 确保 `Parallax2D.repeat_times` 足够覆盖整个关卡长度，或按需适配视野宽度。
     - 视差基准偏移（如 `scroll_offset` 依据初始参考视野计算时）需确认覆盖远端相机位置，避免视差区间断层。
   - **图层层级隔离**：阶段容器内挂载背景时，必须显式确保背景图层 `z_index` 低于阶段内所有视觉瓦片（`VisualTileMapLayer`）与装饰物（建议天空/远景 `z_index <= -30` 且 `z_as_relative = false`），防止阶段被激活时被场景地形完全覆叠。

---

## 常见排查清单 (Troubleshooting Checklist)

- **现象：玩家已复活，但 Boss 没有回到出生点或仍连续击杀**
  1. 沿 `PlayerDied → ResetChase（当帧）→ PlayerRespawned（兜底）` 检查完整信号链，确认死亡时锁存的是追逐阶段语义状态，而不是玩家是否仍位于 TileMap 边界内；首次复位不得等到复活。
  2. 检查 `ResetChase()` 是否先同步清 `_active`，再停运动、关碰撞/伤害并分别复位 Boss 根节点和内部 Mover；`set_deferred("monitoring", false)` 无法阻止已排队的信号，伤害回调必须以 `_active` 为门禁。
  3. 枚举 Boss、Mover、视觉代理及祖先节点的全部 transform 写入者：`_process`、`_physics_process`、Tween、AnimationPlayer、`position/global_position/transform` 赋值和 `move_and_*`。区分“独立移动的屏幕边缘视觉”与“实际碰撞实体”；双纹理不等于两个逻辑进程共同修改同一节点。
  4. 确认复活回调只复位并休眠 Boss；重新显示和 `StartChase()` 必须由骨头或其他明确交互信号触发。

- **现象：复活后 Boss 没有追过来 / 交互后没有赶过来**
  1. 检查关卡是否在复活回调（`_on_player_respawned`）中正确将阶段切回 `OutwardPhase`；若未切回，交互组件处于 disabled 状态，按键无法产生响应。
  2. 检查 Boss 的内部移动器组件在调用 `Reset` 时是否重置了 `process_mode`；若仍为 `PROCESS_MODE_DISABLED`，组件将完全跳过物理帧更新。
  3. 检查内部移动器是否重置了 `_active` 状态标志与速度计算，确保再次调用 `StartChase()` 能正常启动。

- **现象：复活或重置时 Boss 闪现残影**
  1. 检查重置时是否在设置 `global_position` 回原点的同时保留了 `visible = true`。
  2. 必须在重置时将根节点或视觉节点设为 `visible = false`，仅在 `StartChase()` 被调用后设回 `visible = true`。

- **现象：离开区域或死亡复活后移速等属性异常（如水中减速常驻）**
  1. 检查外部调控组件（如 `SlowWaterArea2D`）是否接入 `PlayerRespawned` 信号并执行了速度恢复与缓存清除。
  2. 检查玩家本体 `Respawn()` 方法中是否显式刷新了基础运动学数值。

- **现象：进入特定阶段后背景丢失/错位/黑屏**
  1. 检查阶段专属视差背景（`ParallaxScenery` / `Parallax2D`）本地 `position` 是否未归零（严禁带非零偏移）。
  2. 检查远端起点处 `Parallax2D.repeat_times` 是否不足，或 `scroll_offset` 是否脱离远端相机视野。
  3. 检查背景节点的 `z_index` 是否被阶段内的视觉瓦片层（TileMapLayer）遮挡。

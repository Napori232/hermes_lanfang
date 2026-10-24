---
name: godot-collision-and-physics
description: Use when toggling Godot 4.x collisions and phase physics.
version: 1.0.0
---

# Godot 4.x 物理与碰撞处理实践 (Godot 4.x Physics & Collision)

## 核心机制与避坑

### 1. `process_mode = PROCESS_MODE_DISABLED` 不会停用物理碰撞
* **现象**：隐藏了阶段节点（如 `visible = false`）并设置了 `process_mode = PROCESS_MODE_DISABLED`，但玩家依然撞到空气墙或提前触发碰撞区域。
* **原因**：Godot 的 `process_mode` 只控制节点脚本的 `_process`、`_physics_process` 及输入事件循环；物理碰撞体与 TileMap 地形碰撞直接注册在 `PhysicsServer2D` 中，只要节点在场景树内，碰撞依然生效。
* **规则**：关卡阶段切换或动态隐藏区域时，必须显式递归禁用碰撞。

### 2. 多阶段场景碰撞递归切换标准实现
在切换多阶段（如去程/返程、显隐解谜区域）的主控脚本中，采用递归遍历关闭碰撞与 TileMap 地形：

```gdscript
func _set_phase_enabled(phase: Node2D, enabled: bool) -> void:
	phase.visible = enabled
	phase.process_mode = (
		Node.PROCESS_MODE_INHERIT
		if enabled
		else Node.PROCESS_MODE_DISABLED
	)
	_toggle_physics_recursive(phase, enabled)


func _toggle_physics_recursive(node: Node, enabled: bool) -> void:
	# 1. Godot 4 TileMapLayer 地形碰撞
	if node is TileMapLayer:
		node.collision_enabled = enabled

	# 2. 碰撞形状（避免在物理帧抛出修改警告，使用 set_deferred）
	elif node is CollisionShape2D or node is CollisionPolygon2D:
		node.set_deferred("disabled", not enabled)

	for child in node.get_children():
		_toggle_physics_recursive(child, enabled)
```

### 3. TileSetAtlasSource 碰撞多边形顶点微小偏移导致平铺接缝与高低差
* **现象**：TileMapLayer 在同一水平线平铺瓦片，角色行走时颠簸卡顿或出现肉眼可见/物理上的微小高低差。
* **原因**：在编辑器中手动拖拽 TileSet 碰撞多边形顶点，容易引入微小浮点误差（如 `15.930344, -16.341452` 而非 `-16`）。水平并排拼接时，左右相邻边缘顶点 Y 坐标不一致形成亚像素台阶，卡住 CharacterBody2D 胶囊碰撞体。
* **规则**：平铺方块碰撞体必须保持严格对称整型坐标（如 `(-16, -16, 16, -16, 16, 16, -16, 16)`），排查此类高低差先查 `.tres` 或内联 TileSet 的 points 浮点数。

---

## 载具与路径移动实体避坑 (Path & Moving Platforms)

### 1. 停靠点放行条件分离
* **现象**：载具（如 `OasisBoat`）沿 `PathFollow2D` 前进，在特定机关点（如消解障碍前）本应等待障碍消失后自行划走，却因默认的“乘客必须在船上”检测卡死。
* **规则**：
  - 必须对每个停靠点（StopPoint）细分触发放行条件：区分 `require_player_on_board` 与 `require_puzzle_solved`。
  - 需要人船分流或机关触发的停靠点，将 `require_player_on_board` 设为 `false`，由外部信号（如 `BlockerVanished`、`ComponentInteracted`）解密唤醒。
  - 严禁全量统一死板判定，航线各点进度比率（`progress_ratio`）应抽取为导出数组便于关卡调优。


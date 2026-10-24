---
name: godot-shader-dissolve-and-effects
description: Use when building Godot 4.x 2D material and screen effects.
---

# Godot 4.x 2D Shader 效果与动态驱动规范

## When to Use

用于 Godot 4.x CanvasItem 的裂纹、消解、模糊、扭曲、屏幕采样、侵染，以及这些材质效果的场景挂载、动态驱动与渲染验收。

本 Skill 规范 Godot 4.x 中 2D 材质特效的标准 Shader 编写、场景挂载、代码驱动与验证流程。

---

## 一、 核心原则

1. **表现解耦与节点层级 (Visual Root Hierarchy)**：
   - 交互/机关组件（如塌陷平台、可破坏物）中，受位移/下坠/震颤驱动的视觉节点必须统一挂载在专门的变换容器节点（如 `VisualRoot`）下。
   - 严禁将带 Shader 的 `Sprite2D` 随意挂在根节点下导致逻辑驱动位移与其脱节。
2. **纯程序化效果优先 (Procedural First)**：
   - 易碎（Cracks）、风化瓦解（Dissolve）等通用效果，优先基于 `voronoi` 或 `noise` 的数学算法在 fragment 中生成，无需强依赖额外噪声纹理贴图，降低资源依赖与包体。
3. **材质实例独立隔离 (Crucial Pitfall)**：
   - **机制**：在 Godot 场景中，多个同类节点共享嵌入的 `ShaderMaterial` 时，底层默认指向同一个材质资源指针。若代码或 Tween 调用 `set_shader_parameter`，将导致场上所有实例同时产生视觉变化（如踩踏一个平台全场一起开裂消散）。
   - **强制隔离做法**：
     - **场景层面**：在 `.tscn` 的 `[sub_resource type="ShaderMaterial"]` 中设置 `resource_local_to_scene = true`。
     - **代码层面**：在 `_ready()` 或初始化获取材质时，必须强制进行 `duplicate()`，即：`sprite.material = sprite.material.duplicate() as ShaderMaterial`。
4. **Tween 驱动统一标准**：
   - 使用 `create_tween().tween_method(...)` 对 `ShaderMaterial` 的 `shader_parameter` 进行平滑插值，避免直接每帧修改。
   - 驱动参数命名保持统一：易碎程度统一用 `crack_intensity`，瓦解/消融进度统一用 `dissolve_progress`（`0.0` 为完整，`1.0` 为完全消散）。

---

## 二、 标准实现方案

### 1. 通用易碎与瓦解消融 Shader 模版 (`dissolve_crumble.gdshader`)

```gdshader
shader_type canvas_item;

// 易碎裂纹与微光提示
uniform float crack_intensity : hint_range(0.0, 1.0) = 0.4;
uniform float crack_width : hint_range(0.01, 0.5) = 0.16;
uniform vec4 crack_color : source_color = vec4(0.12, 0.08, 0.05, 1.0);
uniform float crack_scale : hint_range(1.0, 50.0) = 14.0;

// 消解/瓦解控制 (0.0 = 完整, 1.0 = 完全瓦解)
uniform float dissolve_progress : hint_range(0.0, 1.0) = 0.0;
uniform float edge_width : hint_range(0.0, 0.2) = 0.06;
uniform vec4 edge_color : source_color = vec4(0.95, 0.65, 0.3, 1.0);

float hash(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

// 模拟岩石网状裂痕
float voronoi_cracks(vec2 p) {
    vec2 n = floor(p);
    vec2 f = fract(p);
    float md1 = 8.0;
    float md2 = 8.0;

    for (int j = -1; j <= 1; j++) {
        for (int i = -1; i <= 1; i++) {
            vec2 g = vec2(float(i), float(j));
            vec2 o = vec2(hash(n + g), hash(n + g + 13.5));
            vec2 r = g + o - f;
            float d = dot(r, r);
            if (d < md1) {
                md2 = md1;
                md1 = d;
            } else if (d < md2) {
                md2 = d;
            }
        }
    }
    return clamp(sqrt(md2) - sqrt(md1), 0.0, 1.0);
}

void fragment() {
    vec4 tex = texture(TEXTURE, UV);
    if (tex.a <= 0.001) {
        discard;
    }

    // 1. 易碎网状裂纹表现
    float crack_dist = voronoi_cracks(UV * crack_scale);
    // 加宽裂纹阈值判定
    float crack_mask = 1.0 - smoothstep(0.0, crack_width, crack_dist);
    crack_mask = pow(crack_mask, 0.8) * crack_intensity;
    vec3 base_rgb = mix(tex.rgb, crack_color.rgb, crack_mask);

    // 2. 瓦解/消融计算
    float n_val = mix(noise(UV * 12.0), noise(UV * 28.0), 0.35);
    float break_noise = mix(n_val, crack_dist, 0.4);

    if (dissolve_progress > 0.0) {
        if (break_noise < dissolve_progress) {
            discard;
        }
        float edge = smoothstep(dissolve_progress, dissolve_progress + edge_width, break_noise);
        base_rgb = mix(edge_color.rgb, base_rgb, edge);
    }

    COLOR = vec4(base_rgb, tex.a);
}
```

---

## 三、 脚本对接范式 (GDScript Tween 驱动)

1. **初始化材质探测与实例独立化**：
   ```gdscript
   var _dissolve_mat: ShaderMaterial = null
   
   func _ready() -> void:
       var sprite = visual_root.get_node_or_null("Sprite2D")
       if sprite and sprite.material is ShaderMaterial:
           # 必须强制 duplicate 材质，确保多实例运行时着色器参数与 Tween 完全独立
           _dissolve_mat = sprite.material.duplicate() as ShaderMaterial
           sprite.material = _dissolve_mat
   ```

2. **触发/震颤加剧裂隙**：
   ```gdscript
   if _dissolve_mat:
       var crack_tween = create_tween()
       crack_tween.tween_method(
           func(v: float): _dissolve_mat.set_shader_parameter("crack_intensity", v),
           0.25, 0.85, delay_time
       )
   ```

3. **塌陷/瓦解消除**：
   ```gdscript
   if _dissolve_mat:
       var collapse_tween = create_tween()
       collapse_tween.tween_method(
           func(v: float): _dissolve_mat.set_shader_parameter("dissolve_progress", v),
           0.0, 1.0, collapse_time
       )
   ```

4. **原地凝聚复原**：
   ```gdscript
   if _dissolve_mat:
       _dissolve_mat.set_shader_parameter("crack_intensity", 0.25)
       var respawn_tween = create_tween()
       respawn_tween.tween_method(
           func(v: float): _dissolve_mat.set_shader_parameter("dissolve_progress", v),
           1.0, 0.0, respawn_time
       )
   ```

---

## 四、放大低分辨率素材与屏幕侵染

1. **先保持玩法逻辑不动**：把材质挂在随实体移动的 `Sprite2D` / `AnimatedSprite2D` 视觉子节点上；不要为了特效改碰撞体、致死区、移动脚本或存档逻辑。
2. **分两层处理像素感**：先用多点 `TEXTURE` 采样柔化素材本身，再用 `screen_texture` + `textureLod()` 模糊其覆盖区域的场景；只做其中一层通常仍像“大号低清贴图”。
3. **屏幕采样声明采用 Godot 4 写法**：`uniform sampler2D screen_texture : hint_screen_texture, filter_linear_mipmap;`。用 `SCREEN_UV` 采样，用 `SCREEN_PIXEL_SIZE` 缩放扰动，避免分辨率变化后扭曲幅度失控。
4. **让噪声驱动边缘而非整张图闪烁**：用平滑 Alpha、低频 FBM 和 `smoothstep` 生成软边扩张，再将噪声用于阈值、屏幕 UV 微扰和缓慢脉动；所有强度、颜色和速度都暴露为 uniform。
5. **预留透明画布或扩大承载几何体**：CanvasItem fragment 不能绘制到自身矩形之外；需要明显越界侵染时，给帧保留透明边距，或改用更大的 `ColorRect` / `Polygon2D` 承载屏幕效果。
6. **控制采样成本**：固定上限的小核采样（例如 5×5 或 7×7）适合单个大型 Boss；大量实例优先降到 3×3、使用 mip LOD，或把屏幕效果集中到单个覆盖节点。
7. **必须做真实 GPU 渲染验证**：先让 Godot 编辑器扫描资源，再用独立 `SubViewport` + 简单高对比背景渲染截图，检查模糊、透明边缘、矩形边界和背景侵染。需要截图时不要只依赖 `--headless` 的 dummy renderer；用项目实际渲染方式启动并让脚本保存 viewport 图像后退出。
8. **验证可调参数而非特殊采样器枚举**：检查普通 uniforms（如模糊半径、LOD、扩散强度）是否存在；`hint_screen_texture` 采样器可能不出现在普通 shader uniform 列表中，最终以真实渲染结果为准。

更完整的实现与验收配方见 `references/screen-space-infection.md`。

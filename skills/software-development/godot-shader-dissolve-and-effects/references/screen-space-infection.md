# 屏幕侵染与低清素材柔化

## 适用场景

用于被大幅放大的低分辨率 2D 动画：既要隐藏像素块，又要让角色像黑雾、液体或污染物一样影响其后的场景。

## 推荐管线

1. **视觉节点隔离**
   - 将 `ShaderMaterial` 仅挂到视觉节点。
   - 动态实例设置 `resource_local_to_scene = true`；脚本还会改 uniform 时再 `duplicate()`。
   - 保留透明画布边距，为软边与侵染扩张留空间。

2. **素材柔化**
   - 以 `TEXTURE_PIXEL_SIZE` 为采样单位，围绕 `UV` 做固定核多点采样。
   - 累积 RGB 时按 Alpha 预乘，再除以累计 Alpha；否则透明边缘会产生黑边或颜色污染。
   - 用高斯近似权重而不是简单均值，中心结构更稳定。

3. **活体边缘**
   - 低频 FBM 控制 Alpha 阈值，`smoothstep` 生成柔和轮廓。
   - 噪声位移以纹素尺寸为尺度：`offset * TEXTURE_PIXEL_SIZE * distortion`。
   - 动画速度应慢，避免噪声闪烁盖过逐帧动画。

4. **污染背景**

```gdshader
uniform sampler2D screen_texture : hint_screen_texture, filter_linear_mipmap;
uniform float screen_blur_lod : hint_range(0.0, 5.0) = 2.4;
uniform float distortion : hint_range(0.0, 8.0) = 2.0;

vec2 screen_warp = noise_offset * SCREEN_PIXEL_SIZE * distortion;
vec3 blurred_screen = textureLod(
    screen_texture,
    SCREEN_UV + screen_warp,
    screen_blur_lod
).rgb;
```

   - 用柔化后的角色 Alpha 当作混合蒙版，将 `blurred_screen` 染成污染色。
   - 核心区偏向角色本体颜色，边缘区偏向模糊后的背景污染色，才能像侵入场景而非普通半透明贴图。

5. **越界范围决策**

| 目标 | 承载方式 |
|---|---|
| 侵染只围绕角色轮廓 | 带透明边距的 `Sprite2D` / `AnimatedSprite2D` |
| 侵染明显超出贴图矩形 | 更大的透明纹理或 `Polygon2D` |
| 屏幕大范围污染、与角色轮廓弱绑定 | 单独的全屏/局部 `ColorRect`，由角色位置驱动蒙版 |

## 性能档位

| 档位 | 素材采样 | 屏幕采样 | 用途 |
|---|---:|---:|---|
| 低 | 3×3 | 1 次 LOD | 多实例、低端设备 |
| 中 | 5×5 | 1 次 LOD | 常规大型角色 |
| 高 | 7×7 | 1 次 LOD | 单个 Boss、近景大面积显示 |

避免运行时可变循环边界；GL Compatibility 下优先使用固定整数循环，减少驱动差异。

## 可复现验证

1. 运行 Godot 编辑器扫描，确认 shader 与场景资源可加载。
2. 创建临时 `SubViewport`，尺寸与目标画面比例接近。
3. 放置高对比棋盘格或条纹背景，以便观察屏幕模糊和扭曲。
4. 实例化视觉节点，使用项目实际的 Compatibility 渲染方式运行脚本。
5. 等待数帧后通过 `viewport.get_texture().get_image().save_png(...)` 保存截图并正常 `quit(0)`。
6. 同时断言普通 uniforms、动画帧数与材质路径。
7. 视觉检查：
   - 没有贴图矩形边界；
   - 透明区未变成黑框；
   - 主体像素块已柔化但轮廓仍可辨认；
   - 背景只在蒙版范围内被模糊、染色和扰动；
   - 动画、碰撞和移动逻辑未受影响。

`--headless` 可能使用 dummy renderer，无法产出可检查的 viewport texture；截图验收应使用真实 GPU 渲染启动方式。不要把 `hint_screen_texture` 是否出现在普通 uniform 枚举中当作成功条件。
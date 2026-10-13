# 水下几何折射

水下捕获原先仍使用空气中的直线投影，只在合成时偏移纹理坐标。现按折射率 1.333 求每个水下顶点的水面出射位置，调整捕获画面的投影 XY；保留原始 Z/W，维持原几何的深度与水面裁剪。相机和物体任意水平位置下，以光程驻值条件（等价于 Snell 定律）求解，常规五步有界 Newton 迭代，残差无法证明达到精度时再用二分兜底。CPU 独立高精度对照包含近垂直、低角度、极浅水与深水。

网页从原始捕获深度及精确的斜截投影矩阵反解水下射线长度，用于既有吸收颜色。水面微波继续使用法线图偏移，落叶涟漪、倒影和日光焦散沿用现有实现。这里求的是平均水平界面的几何折射，并非波浪曲面逐像素光线追踪；三角形内插、透明鳍片的深度排序和微波扰动仍是实时近似。

资料：[NVIDIA GPU Gems，Rendering Water Caustics](https://developer.nvidia.com/gpugems/gpugems/part-i-natural-effects/chapter-2-rendering-water-caustics) 中的 Snell 定律与水折射率，以及 [Generic Refraction Simulation](https://developer.nvidia.com/gpugems/gpugems2/part-ii-shading-lighting-and-shadows/chapter-19-generic-refraction-simulation) 对图像扰动近似的说明。实现为本项目原创。

只在水下捕获期间启用；主画面、反射、室内捕获、影子及 Blender 原生几何不改变。由于原包围盒不再描述折射后投影，水下捕获临时关闭物体视锥排除与投影区域内的包围盒排除，结束后恢复；水面区域的像素裁剪、上下水分类和网格分割仍保留。没有新增捕获次数、纹理或模型，新增的是顶点求解、片元深度解算，以及可能因保守排除减少而多提交的几何。

`water-refraction-fixture.html` 使用实际 Water/Refractor 与真实深度纹理验证 4 个视角、3 个水深和一个浅水球体，检查颜色落点和水下距离。`pond-refraction-fixture.html` 使用真实池底、石岸、木桥与鱼群做四机位对照。该页含暖机后八对交替绘制的 wall time 记录，计时包含 `gl.finish`，不作为独立 GPU 时间或完整应用帧率；浏览器调度与其他页面负载会影响数值。

本机 `evidence/water-geometric-refraction-*` 保存最终光学结果、计时与主场景截图。最初试验的单层深度图追踪在低角度石块边缘产生断裂，未采用；拒绝的源码与对照留在忽略的 evidence 目录，不进入发布包。整体商业 3A 质量与性能目标仍未完成。

# 素材与第三方许可

根目录 MIT 许可适用于本项目自有代码和文档。下列第三方资产及其改编版本保留原许可，不因打包进 GLB 或 Blender 工程而改成 MIT。

## 第三方模型

| 素材 | 作者与来源 | 许可 | 本项目改动 |
| --- | --- | --- | --- |
| Chinatown Lion Statue（门前石狮） | [vmccurley / Zenodo 10335910](https://zenodo.org/records/10335910) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 裁去原路边底座、减面、缩放、镜像、调整贴图尺寸和粗糙度；用于 `guardian-lions.glb` 及相关原生工程 |
| 唐代坐佛扫描，Smithsonian F1917.243 | [Daniel Pett / Zenodo 10244486](https://zenodo.org/records/10244486) | CC0 1.0 | 数字清理、重新镀金、缩放与莲座适配；后续移除额外添加的手部 |
| Fern 02 | [Rico Cilliers / Rob Tuytel，Poly Haven](https://polyhaven.com/a/fern_02) | CC0 | 修复原透明遮罩、合批、种植布局与光照适配 |
| Food Apple 01 | [Oliver Harries，Poly Haven](https://polyhaven.com/a/food_apple_01) | CC0 | 缩放、布局及供台材质适配 |

## 环境与 PBR 材质

[Poly Haven 资产许可](https://polyhaven.com/license)：以下资产均为 CC0。

- [Autumn Forest 01](https://polyhaven.com/a/autumn_forest_01) — Andreas Mischok。
- [Rosewood Veneer 02](https://polyhaven.com/a/rosewood_veneer_02) — Jenelle van Heerden。
- [Weathered Brown Planks](https://polyhaven.com/a/weathered_brown_planks) — Dimitrios Savva / Rico Cilliers。
- [Mossy Rock](https://polyhaven.com/a/mossy_rock) — Rob Tuytel。
- [Bark Brown 02](https://polyhaven.com/a/bark_brown_02) — Rob Tuytel。
- [Forest Floor](https://polyhaven.com/a/forest_floor) — 作者信息见资源页。
- [Moss002 / ambientCG](https://ambientcg.com/view?id=Moss002) — [CC0 1.0](https://docs.ambientcg.com/license/)。

部分材质经过颜色、尺寸、粗糙度和打包方式调整。对应来源记录在 `source/pbr-sources.json`、`source/refined-asset-sources.json`、`source/garden-moss-source.json` 和 `source/reference-assets/`。

## 声音

环境录音为项目已有 CC0 处理版本：

- [Outside gentle wind in trees](https://freesound.org/people/moreliketrees/sounds/858679/) — moreliketrees，CC0。
- [Gentle lapping lake water](https://freesound.org/people/TRP/sounds/573163/) — TRP，CC0。

现有 `dist/ambience/` 中的风、水与叶声为上述环境声的循环/处理版本。敲钟、木鱼和交互音由项目代码合成。

## 软件与项目自有美术

- [Three.js](https://github.com/mrdoob/three.js) 为 MIT，许可证保留在 `dist/vendor/three/LICENSE`。本地 `Water2.js` 含本项目的捕获筛选扩展。
- vendored Three.js 中的解码库保留文件自身的版权、许可说明。
- 寺院建筑、庭院布局、木桥、其他陈设与植物的程序化建模脚本由本项目编写；彩绘壁画及部分材质为本项目生成的美术资产。项目自有部分按根目录 MIT 许可发布，但不替代嵌入第三方材质的原许可。
- 博物馆、寺院与参考视频用于结构、观感研究；项目没有把参考照片、录屏或用户口播作为开源素材发布。

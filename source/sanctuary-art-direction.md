# 庄严内殿 · 原创设计与资料

本版保留已修复的唐代佛像与铸铜香炉，重新建造内殿木作、矿物彩壁画、层叠藻井和供养陈设。不是某一真实寺院的测绘复原。

## 参考资料

- 故宫博物院，法海寺壁画：https://www.dpm.org.cn/lemmas/241731.html 。参考祥云、人物、莲花与牡丹分层的构图方法；没有把文物照片作为贴图。
- 北京市文物局，大觉寺的盘龙藻井：https://wwj.beijing.gov.cn/bjww/wwjzzcslm/1731063/1731066/djs/1731072/1731232/index.html 。参考上圆下方、逐层收拢、周边小斗栱的空间结构。本项目采用原创莲花井心，不复刻盘龙。
- 中台禅寺，大雄宝殿：https://www.ctworld.org.tw/chungtai/tour/b02-gb.htm 。参考成体系的仪式空间与庄严配色。

## 交付

- `source/庄严内殿.blend`：独立可编辑内殿；完整装入 `source/听秋寺院.blend`。
- `dist/assets/sanctuary.glb`：按 15 种材质合批，含打包的原创壁画。
- `dist/assets/sanctuary-mural.png`：内置 imagegen 工具生成的原创壁画源图。
- `source/build_sanctuary.py`：重复构建、局部替换、保留佛像及香炉的 Blender 脚本。
- `dist/sanctuary.js`：局部移除旧装饰、装入模型、四支红烛持续火焰与轻微烛光变化。

## 原创壁画生成提示词

使用内置 imagegen，非 CLI。生成后直接复制进项目，没有使用外部照片或二次图像编辑。

```text
Use case: historical-scene. Asset type: original high-resolution Chinese Buddhist temple wall mural albedo texture for a luxury restored 3D sanctuary. Generate one wide landscape 3:2 mural, orthographic perfectly frontal flat artwork, edge to edge, no room, no perspective, no frame. An exquisite original mineral-pigment Buddhist celestial garden assembly: graceful dignified bodhisattvas and heavenly attendants in flowing robes among lotus blossoms, peonies, bamboo, auspicious curling clouds, ornate jewelry and tiny gilded halo lines. Figures organized in an elegant middle band, clouds upper band, lush lotus and flowers lower band. Inspired by classical Ming Chinese gongbi Buddhist mural craft, not any specific existing composition. Dominant rich deep azurite blue and malachite green, small vermilion and ivory accents, subtle fine gold linework; sophisticated quiet ceremonial palette. Impeccably drawn serene human faces, natural hands, finely layered textiles, astonishing microdetail. Freshly conserved expensive temple wall, slight plaster grain only, no ruin, no heavy cracks, no grunge. Flat uniform lighting, no baked architectural shadows or specular lighting. All parts of the wide panel have detail suitable for cropping into smaller side panels. No text, no lettering, no logos, no watermark. As large and sharp as possible.
```

## 木作与材质细化

斗拱重新按四层八角形的实际边线布置，每条边三组，共 96 组。弧形横拱、径向悬挑臂与斗块互相承接。作为原创装饰构件，不声称符合某一朝代的营造法式或真实承重规范。

木纹复用项目原有 CC0 资产 [Poly Haven rosewood_veneer_02](https://polyhaven.com/a/rosewood_veneer_02)，作者 Jenelle van Heerden；来源记录见 `source/refined-asset-sources.json`。木件 UV 按长度与面朝向生成；金属粗糙度与细微法线复用 `source/incense_textures.py` 生成的原创数值材质。没有修改原创壁画。

## 侧墙长卷与矿物灰泥（2026-10-08）

侧墙原来与后墙共用一幅 3:2 图像，直接铺在约 2:1 的墙面上。新增原创《莲池供养行列》横向长卷，按墙面比例生成并采用居中裁切 UV，避免横向拉宽人物；后墙保留原画，也改为保持比例的裁切。两侧继续成对使用长卷，不声称四幅均为不同画作。

构图参考[故宫博物院法海寺壁画条目](https://www.dpm.org.cn/lemmas/241731.html)描述的祥云、人物、花卉三层关系。[北京市政府的法海寺介绍](https://www.beijing.gov.cn/renwen/rwzyd/qgzdwwbhdw/fhs/202211/t20221101_2849497.html)提及沥粉贴金；当前版本只实现矿物灰泥的法线与粗糙度，不冒称已复原沥粉立体金线。

新图由内置 image_gen 生成，原始文件 `source/reference-assets/murals/sanctuary-procession.png`，网页与原生材质使用全尺寸 JPEG（97 品质、无色度抽样）`dist/assets/sanctuary-procession.jpg`。完整生成提示词在 `source/mural-procession-prompt.txt`。不使用真实文物照片作为贴图。生成结果实际 1774×887，未虚报 3K/4K。

`source/mural_plaster_textures.py` 数值生成独立、可重复的 1 米灰泥法线与粗糙度纹理；不把画作的明暗误当成几何凹凸。宽缓起伏幅度 70 微米，细颗粒幅度 12 微米，粗糙度范围 .74–.94。第二套以米为单位的 UV 独立于画作构图，保证前后墙的颗粒大小一致；法线强度 .7。`source/mural_finishes.py` 同时供完整构建和独立精修使用。

`source/refine_mural_finishes.py` 更新并重新打开 `庄严内殿.blend` 与 `听秋寺院.blend`，核对全部对象的几何和变换签名不变、四幅壁画的米制 UV、每个壁画材质三张图已打包。备份后缀 `-before-mural-plaster.blend`。

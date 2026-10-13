# 寺钟与撞木

本模型为原创设计，参考日本国立文化财机构 e-Museum 的中国陈代寺钟条目所描述的圆肩、分栏和八瓣莲花撞座，并非对馆藏的测绘复原：
https://emuseum.nich.go.jp/detail?content_base_id=100053&content_part_id=0&content_pict_id=0&langId=en&webView=

`source/build_temple_bell.py` 创建 115 个可编辑部件：连续内外钟壁、钟口、六道铸线、64 颗乳钉、分栏细肋、两面八瓣莲花撞座、开放式冠形悬纽、铁吊环、木槌、抱箍、两条三股编绳与下垂拉环。没有生成无意义的仿经文文字。内外钟壁闭合、流形、正体积。`source/铸铜寺钟.blend` 为独立原型，`source/听秋寺院.blend` 同步装入，原文件留有 `-before-temple-bell.blend` 备份。

网页 GLB 约 6.7 MiB，5 张打包材质图，按四个独立运动组件合并为 8 个网格。钟身复用项目原创铸铜表面图，木槌复用项目 CC0 rosewood 贴图（来源见既有 refined-asset-sources.json）。并未增加新的外部素材许可。

木槌使用两根长 1.25 米、固定顶点的绳，保持水平做平行动摆动。点击后 .35 秒拉开，到 .8 秒触碰莲花撞座；声音回调只在跨过接触时刻触发一次。2.5 秒内重复点击不叠加敲击，回弹快速衰减并在 5 秒归零。钟身只在接触后作亚毫米级衰减振动。自动远钟背景声机制保持原样。该运动为确定性的近似，不是刚体声学求解。

`source/temple-bell-fixture.html` 使用相同导出模型和运行时代码验证。`source/bell-motion.test.mjs` 检查任意采样时刻绳长不变、木槌不会穿过设定接触平面、关键帧连续、丢帧也只触发一次声响。`source/verify_temple_bell.py` 独立对比旧工程与新工程，逐对象核验替换范围以外的所有面和变换。

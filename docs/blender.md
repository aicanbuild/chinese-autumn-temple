# Blender 工程与模型编辑

网页运行需要的导出模型已在 `dist/assets/` 中。为了避免每次 clone 都下载大型原生工程，当前 Blender 工程另放在 GitHub Release 的 `chinese-autumn-temple-blender-source.zip`。

将该压缩包解压到仓库根目录，得到 `source/*.blend`。先打开 `source/听秋寺院.blend` 查看完整寺院；主殿、木鱼、手水钵、清溪和各类植物另有独立工程。压缩包只含当前工程，不含历史备份。

模型为 Blender 4.x 创建，建议使用 Blender 4.5 或更新的兼容版本。多数脚本通过 `bpy` 运行，例如：

```sh
blender --background source/听秋寺院.blend --python source/verify_sculpture.py
```

请先复制要修改的工程。`build_*`、`install_*`、`refine_*` 和 `export_*` 不是一个可以任意顺序执行的全量重建命令：一些依赖已保存的场景属性、名称和其他部件。各模块的 `source/*notes.md` 说明相应流程，完整记录见 `docs/development-notes.md`。

部分材质脚本使用 Python 的 NumPy/Pillow；运行网页与构建浏览器模块不需要这些库。第三方模型和打包进工程的贴图继续遵循 `ASSET_CREDITS.md` 的许可。

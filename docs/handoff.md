# 接手与重建

仓库已归并为当前 R10.4。Git 历史保留旧版；工作树无需旧文件、Blender 快照或外部效果图即可重建。

## 环境

- Python 3.9+：二维和交付检查只使用标准库。
- Node.js 20.9+ 与 sharp 0.35.4：将 SVG 生成二维 PNG。先在仓库执行 `npm install`。本机可使用已安装的兼容 sharp；实际版本记录在 reports/png_state.json。
- Blender 5.2.1 LTS：本机已用于生成、重新打开及核验模型。其他版本需重新验证。

## 命令

在仓库根目录执行；默认命令不渲染三维。

```sh
python3 scripts/build_2d.py
node scripts/preview_2d.cjs
blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python scripts/build_3d.py
blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python scripts/validate_3d.py
python3 scripts/validate_delivery.py
```

macOS 的 `blender` 可替换为 `/Applications/Blender.app/Contents/MacOS/Blender`；命令中路径有空格时加引号。受限环境的本机 Blender 可能需要系统进程权限。这里仅建模与验证，不需要选择 GPU。

也可用统一入口：

```sh
python3 scripts/rebuild.py --all --blender /Applications/Blender.app/Contents/MacOS/Blender
```

`--2d-only` 仅重建二维。渲染不是重建步骤。最终报告生成前须已有当前模型的核验报告；二维更新后若布局改变，应先同步三维，否则一致性检查会拒绝旧模型。

## 文件职责与模型操作

data/layout.json 保存当前墙、房间、洞口、家具、门端点、设备预留和路线，统一毫米。data/style3d.json 保存米制三维参数、材质和相机。data/schedules 为人工维护的专业条件输入，不得把历史点号当作当前坐标。

model/scene_config.json 由布局自动换算，附布局 SHA256。Blender 场景内嵌相同配置；Furniture 根对象包含占位元数据，实际柜体和设备为可编辑网格。脚本重新生成会覆盖 model 及绘图输出；手工模型修改须回写脚本后再交付。

帧 1 为房门与柜门关闭；帧 90 为开启端点。所有门同时动画用于演示运动，**不是同时使用许可**。浅柜门为移门，衣柜门和鞋柜门有铰接动画，高柜设备有开门动画，衣柜抽屉向外滑移。实际厂家五金未选定。

默认显示四人桌椅，Dining_6 为互斥替代；Ceilings、Candidate_Equipment、Clearance_Envelopes 隐藏。切换六人时同时关闭 Dining_4。机器人仅为净预留和实际柜体开口，没有虚构适配的整机。鞋柜顶 400mm 封口属于柜墙几何，不能为轴测美观而随意删成不存在的开放边界。

GLB 是当前四人关闭状态的静态便携模型，排除顶棚、六人组和检查包络；Blender 保留替代组、动画、相机和灯光。程序化材质在 GLB 中仅提供兼容基础材质，噪声纹理／凹凸等可能简化；Blender 是完整可编辑源。

## 核验与未完成事项

reports/verification_2d.json 包括四／六人座椅、门扇采样、衣柜与设备操作、鞋型容量和 112 个衣篮状态；实体命中、时间重叠、五金待核分列。reports/verification_3d.json 是重新打开保存模型后的核验；隐藏替代组临时启用以读取正确的世界坐标，核验不修改模型文件。

reports/delivery.json 记录 SVG 实际坐标与配置误差、CSV／面积一致性、本地链接及源文件校验。reports/manifest.sha256 可检测交付后文件是否被改动。PNG 的字形取决于操作系统字体，跨平台不保证 PNG 逐字节一致；同机重复生成已单独检查。Blender 二进制不承诺跨次逐字节一致，使用几何和配置核验。

最先处理 docs/constraints.md 的 A 门五金、柜墙现场条件、真实设备安装图和错时操作。未解决前保持条件公开，不提升为施工通过。

## 以后获得授权才渲染

保留七个相机命名及观察方向。未来可运行 `render_3d.py -- --device METAL --preview` 出低分辨率预览，再检查构图、柜顶遮挡、门状态、材质和曝光后正式出图。脚本逐张执行，不自动轮询后台进程；默认正式 2400×1866、128 采样、降噪。顶视与轴测隐藏顶棚，室内启用。渲染前应逐视角设置所需门状态；默认关闭可能遮挡视线。明显噪点视角可用 256 采样单独补图；Metal 失败需先单张 CPU 验证，再决定回退。

本次交付没有运行此脚本，没有包含任何旧版或新生成的三维效果图。

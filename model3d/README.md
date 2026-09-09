# R10.1 全屋 Blender 模型

温暖中古＋现代简约概念首版：三卧、两卫、两阳台及公共区；可编辑墙体、门窗、木地板、圆扶手沙发、木框餐椅、咖啡设备、中厨、玻璃书房、灯光与七个相机。

- [可编辑 Blender 文件](whole_home.blend)
- [轻量 GLB 预览](whole_home.glb)：基础 PBR；木纹和布料程序凹凸保留在 Blender 中。
- [尺寸和位置配置](scene_config.json)
- [检查报告](CHECK_REPORT.md)及[机器可读结果](verification.json)
- [全屋轴测检查图](preview_axonometric.png)／[俯视检查图](preview_top.png)：从保存模型的网格投影生成，并非效果图。

## 后台生成和验证

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File model3d/run_background.ps1
```

默认 `All`：生成、保存、导出，然后在另一 Blender 后台进程中重新打开 `.blend`、核验模型并重新导入 GLB。`-Mode Build` 和 `-Mode Verify` 可分别运行。入口固定携带 `--background --factory-startup --disable-autoexec --python-exit-code 1`，所有 Blender 脚本拒绝前台执行。默认可执行文件 `D:\Users\11171344\blender\blender.exe`，可用 `-Blender` 覆盖。

直接修改 `scene_config.json` 后重新运行即可。坐标单位米，X 东、Y 北、Z 上。矩形为 `[西边X, 南边Y, 宽X, 深Y]`。来源是原户型尺寸线锚定的 R10.1 毫米墙面数据，经轴向和单位转换；尺寸段与估读边界分别记录。没有依据 R10.1 示意图像素拉伸。`make_config.py` 仅用于重建初始配置，会覆盖手改 JSON，常规生成无需运行。

## 模型操作

房间与建筑、门窗、灯光分别成集合，家具由命名空对象组织，部件保留网格与倒角修改器。默认四人餐桌；切换六人状态时关闭 `Dining_4`，同时启用 `Dining_6` 的视图和渲染。两套不能同时显示。

`Candidate_Equipment` 包含未确认的 R01 和已冲突的旧 L02 机器人试位，默认隐藏且不导出 GLB。`Clearance_Envelopes` 为咖啡维护包络，默认隐藏。`Ceilings` 默认隐藏以便看全屋；室内渲染可启用。帧 1 门扇关闭，帧 90 开启，铰侧、滑门挂轨和五金均为概念假设。开启动画不保证实际硬件净距，详见检查报告。

七个相机：`01_Axonometric` 全屋轴测、`02_Top` 俯视、`03_Living_to_C` 客厅望 C、`04_C_to_Living` C 望客厅、`05_Coffee` 咖啡角、`06_Dining_Kitchen` 餐厨连接、`07_Study` 书房。

## 本次调整和待解决项

保留 C/D 隔墙、主卧南窗、B/C 东飘窗、D 南飘窗和南墙冰箱→独立蒸烤→咖啡→食品顺序。C 西开口净概念宽 2200mm，C 北原门洞保留且无门扇。原中厨新增可关闭玻璃分隔。原始 240mm 粗墙边界保留；220mm 仅作新增粗墙默认值，未以缩墙改变承重边界。

咖啡柜改为 1700×600×900mm，食品柜缩为 501mm；餐桌深 850mm，向南平移 350mm，四／六人长 1600／1800mm；B 床垫缩为 1200×2000mm。书房东侧给主卧留出 1000mm 通道；书桌 1700×700mm 向西平移，深柜缩短避让书桌。家具初值与原 R10.1 的差异均写入配置。

**餐区尚需调整：厨房关闭玻璃后，北排椅后没有通行空间，也无法全拉椅；南排与蒸烤、咖啡维护空间重叠。** 扩大 C 西开口或移动结构不是本轮自行解决手段，保留未解决项。检查报告将家具实体冲突、开门扫掠、四／六人就座及拉椅、设备维护和通道分列，不将文件通过误写成空间全部通过。

咖啡机手动水箱、废水盘手倒，磨豆机仅用电；没有虚构隐藏管线。岛槽给排水和阳台 B 洗烘接管均是条件设备。两卫设备是主要洁具概念占位，不代表原排污点位已确认。梁柱实测、结构分类、门框实际净宽、设备型号及安装维护尺寸仍待核。

## 可选检查图与后续渲染

安装 Pillow 和 NumPy 后运行 `python model3d/preview_model.py`，它使用验证阶段导出的网格坐标，以带深度缓冲的软件多边形投影生成两张检查图，无 Blender 渲染调用。玻璃在检查图中省略以便观察内部；最终材料以 `.blend` 为准。

本机已知 Cycles CPU 非法指令崩溃，本次没有执行光追或视口渲染。兼容机器可显式运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File model3d/run_background.ps1 -Mode Render -Camera 05_Coffee -Blender 'C:\Blender\blender.exe'
```

建模／验证命令不会调用此渲染分支。首版以模型可编辑、布局关系可检查、材质及相机完整为验收范围。

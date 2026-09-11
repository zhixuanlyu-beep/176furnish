# 丽水嘉园176㎡ · R10.2 家庭厅与客厅优化版

正常就座可使用咖啡、蒸烤；北侧通道 1100mm，全部拉出 600mm。

南椅距咖啡／蒸烤操作区 98／48mm；拉出距抽屉／开门 198／148mm。

完全拉出临时占用部分人员操作区；先恢复就座位置再携篮，携篮与洗碗装卸、岛槽操作错时。

全屋同步：三张床、卧室移门衣柜、D东墙柜、幕布、家庭厅和卫浴概念占位均随当前模型。

床侧900mm、D床尾1000mm、幕布后1000mm；B床垫1200mm。实际床架外挑、人体、设备及硬件选型需重算。

M01/M02/M03恢复开放边界，C西开口2698mm。燃气使用条件未确认合规，梁柱及拆改结构现场核验。

独立蒸箱、独立烤箱保留；咖啡柜1800×600，取消食品柜并留空401mm；微波炉放台面东端。

旧管线路由仅补充概念示意，三维未建管线，W0为待确认接点。岛槽重力排水未成立；洗烘接管、空调安装待核。

卫浴未确认原点位，机器人为候选未落实。原图面积和尺寸线、原26条问题记录保留。

三维、SVG、CSV、HTML方案册及预览纳入GitHub交付；历史PDF、ZIP原样保留本地，本轮仅内存PDF检查。

[三维交付入口](model3d/README.md) · [中文冲突对照](model3d/CHECK_REPORT.md)

![全屋平面](deliverables/preview-furniture.png)

- [52页离线方案册](deliverables/方案册.html)
- [全屋家具与门窗](deliverables/01-furniture.svg)
- [拆改及开放边界](deliverables/02-alterations-review.svg)
- [水电点位与概念路由](deliverables/03-services.svg)
- [南墙柜体立面](deliverables/04-cabinet-access.svg)
- [设备侧视与操作高度](deliverables/05-coffee-sideboard.svg)
- [家庭厅、子母门与收纳](deliverables/06-utility-storage.svg)
- [四／六人餐区状态](deliverables/07-island-dining.svg)
- [设备开启与人员操作](deliverables/08-appliance-clearance.svg)
- [600mm衣篮路线](deliverables/09-workflows.svg)
- [空调与补充概念管线](deliverables/10-air-conditioning.svg)
- [原图标定与实际墙段](deliverables/11-source-overlay.svg)
- [AC01局部吊顶概念剖面](deliverables/12-ac01-ceiling-section.svg)
- [岛槽给排水概念剖面](deliverables/13-island-water-section.svg)
- [卫浴占位与机器人候选](deliverables/14-robot-station-review.svg)
- [岛桌连接与膝部高度](deliverables/15-island-table-connection.svg)
- [家具尺寸表.csv](deliverables/家具尺寸表.csv)
- [底图对位核验.csv](deliverables/底图对位核验.csv)
- [新图尺寸标注.csv](deliverables/新图尺寸标注.csv)
- [新图面积标注.csv](deliverables/新图面积标注.csv)
- [水电点位表.csv](deliverables/水电点位表.csv)
- [现场核验表.csv](deliverables/现场核验表.csv)
- [电器上下水表.csv](deliverables/电器上下水表.csv)
- [设备预留表.csv](deliverables/设备预留表.csv)
- [交付验证报告](deliverables/verification.json)

以 `model3d/scene_config.json` 为唯一布局配置，实际部件外沿读已验证快照。`model3d/r10_baseline.json` 仅用于历史配置重建，由历史基线确定性重建R10.2，重复应用不追加对象；修改前成果见 model3d/history/r10_1。

运行 `powershell -File model3d/run_background.ps1` 后，运行 `python deliverables/build_package.py`、`python deliverables/render_verify.py`。缺失或过期验证会阻止发布。需要 Blender、Playwright、PyMuPDF、Pillow 和 Chromium/Edge。所有PDF仅内存检查，不新建磁盘PDF。

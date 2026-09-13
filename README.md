# 176furnish · R10.4

当前分支仅保留 R10.4 全套成果。旧版本可从 Git 历史查阅，工作树不再保留旧版目录或旧效果图。

**二维和三维模型已同步；本轮未生成三维渲染图。** 本方案仍有现场与五金待核条件，不是施工或柜体下单图。

先下载仓库，用浏览器打开 [离线方案册](docs/方案册.html)。GitHub 页面可直接浏览 [二维 PNG](drawings/png)；编辑图纸使用 [SVG](drawings/svg)。

| 目录 | 用途 |
| --- | --- |
| [data/layout.json](data/layout.json) | 唯一布局数据源：毫米，X 向东、Y 向北 |
| [data/style3d.json](data/style3d.json) | 三维材质、概念高度及七个相机；米制 |
| [data/schedules](data/schedules) | 设备、专业条件等人工维护输入表 |
| [scripts](scripts) | 独立重建、核验工具；不依赖旧版本 |
| [drawings](drawings) | 18 张可编辑 SVG 与对应二维 PNG |
| [tables](tables) | 当前家具、面积、设备与状态核验 CSV |
| [model](model) | R10.4 可编辑 Blender、GLB 与派生配置 |
| [reports](reports) | 二维、三维和交付一致性核验、文件校验值 |
| [docs](docs) | 离线方案册、接手说明及待核条件 |

三维包含延长岛台与基站净开口、缩卫及入口衣柜、蒸烤／微波高柜、嵌入鞋柜与家庭厅移门浅柜；餐区旧开口不再自动生成顶层残墙。默认四人组，六人组与检查包络隐藏。

**需要后续解决：** 主卧 A 门采用 50mm 突出把手的概念算例在 87–90°碰西墙，五金暂停定稿。北排餐椅拉出会阻断洗烘携篮候选路线；鞋柜取物、浅柜南段操作与部分设备操作需错时。参见 [条件清单](docs/constraints.md)。

接手请先读 [AGENTS.md](AGENTS.md) 和 [重建说明](docs/handoff.md)。

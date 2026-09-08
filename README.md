# 丽水嘉园176㎡ · R9开放餐厨、整面高柜与空调重排

拆除餐区北侧、厨房西南侧及餐区西侧可拆细墙，保粗墙、梁柱、公卫和C/D隔墙。取消餐厨分隔，保留燃气；开放餐厨燃气条件待现场核验，未确认合规。

C/D南墙从西向东为冰箱950–1000、必配分体蒸烤高柜600、咖啡1300及食品余量，均朝北使用。柜深、散热和端部余量按厂家安装图；3976图注不用于直接下单。

岛1000×750北端进入原厨房，南接1600×800餐桌，六人延伸1800。上部水槽—800净备菜—灶连续，洗碗机在相邻直线柜段。家庭厅删除南侧落地书柜，西柜深600–650，书籍移到北桌上方280深书柜。

客厅AC01风管机，A/B/D与家庭厅AC02–AC05独立挂机，共五套独立系统。公共区负荷计入连通餐区；匹数、净高、吊顶、冷媒/冷凝水与室外机位待专业深化。

算例东侧拉椅后900，北厨台至岛700仅为单人操作带；洗碗满开东侧776偏紧，600衣篮尚须现场转弯。冰箱抽屉600＋人600，六人桌尾余42不是通道，冰箱由西侧开放口到达。设备与椅子包络无相交；门全开无人取物时桌南横向通路余642。冰箱、蒸烤或咖啡柜前站人会占用这条横向通路，当前不具备此处同时操作与通行的条件，仍需设计深化；不代表已通过现场验收。

![R9家具平面](deliverables/preview-furniture.png)

- [15页离线方案册](deliverables/方案册.html)
- [furniture.svg](deliverables/01-furniture.svg)
- [alterations-review.svg](deliverables/02-alterations-review.svg)
- [services.svg](deliverables/03-services.svg)
- [cabinet-access.svg](deliverables/04-cabinet-access.svg)
- [coffee-sideboard.svg](deliverables/05-coffee-sideboard.svg)
- [utility-storage.svg](deliverables/06-utility-storage.svg)
- [island-dining.svg](deliverables/07-island-dining.svg)
- [appliance-clearance.svg](deliverables/08-appliance-clearance.svg)
- [workflows.svg](deliverables/09-workflows.svg)
- [air-conditioning.svg](deliverables/10-air-conditioning.svg)
- [渲染与一致性检查](deliverables/verification.json)
- [家具尺寸](deliverables/家具尺寸表.csv)
- [设备清单](deliverables/设备预留表.csv)
- [水电与空调点号](deliverables/水电点位表.csv)
- [现场核验](deliverables/现场核验表.csv)
- [设备给排水](deliverables/电器上下水表.csv)

运行 `python deliverables/build_package.py`，再运行 `python deliverables/render_verify.py`。需要Playwright、PyMuPDF、Pillow及Chromium/Edge，支持FURNISH_BROWSER。墙段、柜体、设备及家具共用deliverables/r9_geometry.py；booklet.css控制分页与移动端。

检查仅证明交付文件正确，不替代现场安装验收。原生Git发布到已授权main，排除PDF、ZIP、加密文件、缓存及临时资料；已有受保护PDF原样保留。PDF文件状态见本地保护说明。

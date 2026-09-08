# 丽水嘉园176㎡ · R8连续餐厨与贴墙冰箱

原厨房与C作为连续餐厨区统筹，保留上部水槽、燃气及合规可关闭分隔。

- 冰箱背靠公卫南墙东段，门朝南面向餐区，避西侧公卫门。柜位宽900–1000mm起排；深度、背部散热和开门侧余量按型号，前方1200–1400mm不放咖啡柜或餐椅。
- 上部保持“水槽—600–800mm净备菜台—灶”。洗碗机在水槽旁备菜台下的直线段、避转角；岛台补充备餐，主备菜面不放常驻小电器。
- 岛1000×750mm放中厨南侧，1600×800mm餐桌向南连接，可延伸1800mm。错位随冰箱前场、阳台通路和餐椅调整；家具可跨原房间边界，不挤客厅休息区。
- 咖啡柜移至C/D隔墙西段，背南朝北，宽1200–1400mm、深550–600mm，与桌尾及拉椅错开。水箱机仅接电，手动加水、倒废水。
- 分隔从公卫南墙附近起排，约100–200mm微调。开启/关闭均核收门、设备操作和阳台B通路，未成立的位置明确记录冲突。
- 取消客厅独立储藏室；家庭厅600–650mm深大件柜配浅书柜，保办公及A/B通行。鞋柜在入户门内北侧，1000–1200×350mm，向家庭厅侧收并避门。
- 保西墙沙发、投影幕和D路线；洗烘清洁留阳台B，机器人在L02阳台B／R01原公卫二选一。

![R8家具布局](deliverables/preview-furniture.png)

## 交付资料

| 文件 | 内容 |
| --- | --- |
| [方案册](deliverables/方案册.html) | 14页，离线阅读、浏览器打印 |
| [家具平面](deliverables/01-furniture.svg) | 冰箱、岛桌、咖啡柜、家庭厅和鞋柜同步更新 |
| [拆改图](deliverables/02-alterations-review.svg) | 分隔、保留边界与取消储藏室 |
| [水电点位](deliverables/03-services.svg) | 冰箱、备菜下洗碗机、咖啡柜及柜内照明 |
| [柜体检修](deliverables/04-cabinet-access.svg) | 设备拆出和检修关系 |
| [咖啡柜](deliverables/05-coffee-sideboard.svg) | 水箱机、磨豆机和操作台面 |
| [家庭厅与家政](deliverables/06-utility-storage.svg) | 大件柜、鞋柜及两个互斥基站候选 |
| [四人／六人及拉椅](deliverables/07-island-dining.svg) | 同一尺寸试排、座椅占用及窄口 |
| [设备满开图](deliverables/08-appliance-clearance.svg) | 冰箱门弧/抽屉、洗碗门与装卸人位 |
| [动线图](deliverables/09-workflows.svg) | 分隔开/闭状态与七类厨房任务 |
| [交付说明](deliverables/README.md) | 家具、设备、水电、上下水及现场核验CSV说明 |
| [文档检查记录](deliverables/verification.json) | 排版、渲染、一致性及试排算术检查 |

## 尚未成立的条件

当前试排东侧就座后余576mm、拉椅后226mm，六人桌尾248mm，不能作为900mm通道。椅包络避开冰箱和咖啡前场，但边缘仅余60/50mm，不证明转弯成立。阳台B门洞与分隔关闭关系、公卫南墙可用净长和实际设备安装尺寸仍须现场核验；未标为已验证可施工。

采用[清晰原图](IMG20260907-094631119.jpg)及用户图例。3976、2998、2844等图注只作初排依据；局部图墙面原点为明确标注的假设。全部设备尚未选型，开门/拉椅是有尺寸的占用算例，须以实际产品替换并复核。三卧两卫、C/D墙、外窗和客厅休息区保留。

## 本地生成与发布

```shell
python deliverables/build_package.py
python deliverables/render_verify.py
```

渲染需要Playwright、PyMuPDF、Pillow与Chromium/Edge，支持环境变量`FURNISH_BROWSER`。局部图共用`deliverables/r8_geometry.py`中的尺寸试排，生成器同步重建HTML/SVG/CSV。

以原生Git提交和推送，继续排除加密/受保护文件、PDF、ZIP、缓存和临时资料。PDF文件状态另见本地说明；不移除或绕过文件保护。

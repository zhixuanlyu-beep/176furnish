# R10.4 接手约定

1. 先读 README.md、docs/constraints.md、docs/handoff.md，再读 data/layout.json 和 reports/verification_2d.json、reports/verification_3d.json。
2. data/layout.json 是唯一布局坐标源，单位 mm，X 东、Y 北。禁止按 PNG 像素估算尺寸，禁止引入旧版模型作为当前基线。scripts/model_config.py 负责转换到米制。
3. 只修改输入与生成工具，然后重建成果；不得只改导出 SVG、CSV、scene_config.json 或 blend 而遗漏数据源。专业条件输入在 data/schedules，数值几何表由 build_2d.py 生成。
4. 已确认的布局边界见 constraints.md。改变岛台延长量、3200 衣柜、床位、客卫边界、1500 家庭厅门洞、书桌、大件柜或柜深需提出具体冲突，不自行扩大改动。
5. 现有材质、灯光与七个相机已保留，但尚未做 R10.4 渲染验收。当前用户要求不补渲染；未经后续授权不要运行 render_3d.py。不要轮询用户自行等待的渲染。
6. 不能将概念几何通过写成施工通过。主卧 A 门把手碰墙是公开条件项，不能删报告或改阈值掩盖；操作时间冲突与实体碰撞分列。
7. 变动二维后运行 build_2d.py、preview_2d.cjs、validate_delivery.py；变动布局／三维后同时运行 build_3d.py 和 validate_3d.py。检查图纸可读性、版本和链接，更新报告。
8. 发布使用原生 Git，不把文件内容或二进制 base64 经 LLM／GitHub blob 接口搬运。不提交凭据、运行日志、缓存、node_modules、备份 blend 或未授权渲染。
9. 当前工作树仅保留最新版本，不重写已有 Git 历史；旧版本回溯使用历史提交。

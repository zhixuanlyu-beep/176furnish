"""Rebuild current drawings, tables and offline booklet using only data/ and scripts/."""
import csv,json,shutil,html
from pathlib import Path
import plan2d as g
from validate_2d import validate
from family_drawings import family_drawings
R=g.ROOT
def table(name,head,rows):
 with (R/'tables'/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.writer(f);w.writerow(head);w.writerows(rows)
def main():
 g.REPORT=validate();assert not g.REPORT['hard_errors'],g.REPORT['hard_errors'];g.dump(R/'reports/verification_2d.json',g.REPORT)
 g.changed={'shoe','study_shallow','entry_wardrobe','bedA','island','tower','coffee','fridge'}
 items=g.drawings()+family_drawings()
 q=g.Drawing('当前主卧边界与衣帽区施工待核界面');q.plan([-650,6050,7550,4100],[35,125,1320,665],ops=True)
 q.notes(['主卫净边界1700×1400，南墙Y8557；门洞东侧北移，主卫取消淋浴。','入口衣柜3200×600，主卧床西南角3720／7577；排污位置、墙体可改性及衣柜固定待现场。','主卧A门按50mm突出把手假设，在87–90°与原西墙相交，暂停该五金定稿；不将其记为通过。']);q.save('06-alterations.svg');items.append(('06-alterations.svg','主卧与衣帽区待核界面'))
 q=g.Drawing('当前玄关柜墙与拆改界面');pt,r,s=q.plan([-3800,1600,3650,3650],[40,120,1080,670]);q.notes(['1010mm短墙段表达为30西收口＋900鞋柜＋80门侧收口；原短墙性质与门框固定方式须现场核实。','鞋柜南面Y2724、柜背Y3124，浅柜南端Y3174，间隔50；家庭厅1500门洞保持。','本图仅表达最新柜墙概念，不代表结构拆除许可；实际条件不成立时暂停，不扩大柜深或移动其他家具。']);q.save('16-entry-alterations.svg');items.append(('16-entry-alterations.svg','玄关柜墙待核界面'))
 q=g.Drawing('当前600mm衣篮完整候选路线');q.plan([-4500,-1600,9800,5200],[40,125,1320,670],route=g.D['route_candidates']['入户至洗烘完整候选'],labels=False)
 q.notes(['入户中心Y2300 → X−2600绕客卫门南端Y200 → X200转至餐区北侧Y875 → 阳台X4500。','鞋柜关闭、门固定打开、正常四／六人就座时，600方篮及每侧额外10mm算例均无概念实体命中。','北排任一餐椅拉出500或全部拉出均阻断本线；鞋柜取物、设备装卸、基站进出与携篮必须错时。']);q.save('10-workflows.svg');items.append(('10-workflows.svg','完整洗烘衣篮候选路线'))
 items=sorted(items);g.dump(R/'reports/drawing_index.json',items)
 for p in (R/'data/schedules').glob('*.csv'):shutil.copy2(p,R/'tables'/p.name)
 table('家具尺寸表.csv',['编号','名称','空间','西X_mm','南Y_mm','宽X_mm','深Y_mm','高_mm','底标高_mm','性质'],[[n,g.name(n),g.name(f['room']),*f['box'],f['height'],f.get('z',0),'R10.4概念，非实测或下单'] for n,f in g.F.items()])
 table('新图面积标注.csv',['空间','几何面积_m2','口径'],[[g.name(n),round(sum(b[2]*b[3]/1e6 for b in bs),4),'当前房间边界，不扣家具，非现场或产权面积'] for n,bs in g.D['rooms'].items()])
 e=g.REPORT['evidence'];table('衣篮路线核验.csv',['路线','人数','餐椅状态','鞋柜状态','600实体命中','额外10mm命中','错时操作','条件'],[[v['route'],v['seats'],v['state'],v['shoe_state'],'；'.join(v['solid_hits']),'；'.join(v['reserve_10mm_hits']),'；'.join(v['service_overlaps']),v['status']] for v in e['basket_routes']])
 table('就座与开启核验.csv',['人数','椅状态','实体命中','设备开启命中','错时人员操作'],[[v['seats'],v['state'],str(v['physical_hits']),str(v['equipment_opening_hits']),str(v['time_shared_operator_overlaps'])] for v in e['dining_states']])
 figures=''.join(f'<figure><figcaption>{g.esc(t)} · <a href="../drawings/svg/{n}">SVG</a> · <a href="../drawings/png/{n[:-4]}.png">PNG</a></figcaption><img src="../drawings/png/{n[:-4]}.png" alt="{g.esc(t)}" loading="lazy"></figure>' for n,t in items)
 links=''.join(f'<li><a href="../tables/{g.esc(p.name)}">{g.esc(p.name)}</a></li>' for p in sorted((R/'tables').glob('*.csv')))
 page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R10.4 全部方案成果</title><style>body{margin:0;background:#f4f2e9;color:#234238;font:17px/1.75 -apple-system,"PingFang SC",sans-serif}main{max-width:1200px;margin:auto;padding:30px 20px}header{padding:30px;background:#23473d;color:white;border-radius:16px}a{color:#397159}figure{background:#fffdf8;padding:14px;margin:24px 0;border:1px solid #dce0d5}img{width:100%;display:block}aside{margin:25px 0;padding:20px;background:#e7ebdf;border-left:4px solid #a36a38}@media(max-width:600px){main{padding:12px}header{padding:20px}figure{overflow:auto}figure img{min-width:760px}}</style><main><header><h1>R10.4 · 当前方案</h1><p>嵌入高鞋柜与家庭厅浅柜调整；延长岛台、入口衣帽区和设备高柜均已同步三维。</p><p>本轮提供可编辑三维模型与二维图表，未生成三维渲染图。</p></header><aside><strong>仍有条件项：</strong>主卧A门50mm把手假设在87–90°碰西墙，暂停五金定稿。柜墙可改性、固定及线路待现场。北排拉椅阻断洗烘携篮候选线；取鞋、浅柜南段操作及设备使用须错时。渲染质量未验收。</aside><p><a href="../README.md">项目入口</a> · <a href="handoff.md">接手说明</a> · <a href="constraints.md">尺寸与待核条件</a> · <a href="../model/whole_home_R10.4.blend">Blender模型</a> · <a href="../model/whole_home_R10.4.glb">GLB模型</a></p>'''+figures+'<h2>表格</h2><ul>'+links+'</ul></main></html>'
 (R/'docs/方案册.html').write_text(page)
 print(json.dumps({'revision':'R10.4','drawings':len(items),'tables':len(list((R/'tables').glob('*.csv'))),'hard_errors':g.REPORT['hard_errors']},ensure_ascii=False))
if __name__=='__main__':main()

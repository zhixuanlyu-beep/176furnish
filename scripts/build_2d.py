"""Rebuild current drawings, tables and offline booklet using only data/ and scripts/."""
import csv,json,shutil,html
from pathlib import Path
import plan2d as g
from validate_2d import validate
from family_drawings import family_drawings
from room_drawings import room_drawings
R=g.ROOT
def table(name,head,rows):
 with (R/'tables'/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.writer(f);w.writerow(head);w.writerows(rows)
def main():
 g.REPORT=validate();assert not g.REPORT['hard_errors'],g.REPORT['hard_errors'];g.dump(R/'reports/verification_2d.json',g.REPORT)
 g.changed={'shoe','study_shallow','entry_wardrobe','bedA','island','tower','coffee','fridge'}
 from design_review import publish,drawings
 air,dims=publish(table)
 items=g.drawings()+family_drawings()+room_drawings()+drawings()
 q=g.Drawing('当前主卧边界与衣帽区施工待核界面');q.plan([-650,6050,7550,4100],[35,125,1320,665],ops=True)
 q.notes(['主卫净边界1700×1400，南墙Y8557；门洞东侧北移，主卫取消淋浴。','入口衣柜3200×600，主卧床西南角3720／7577；排污位置、墙体可改性及衣柜固定待现场。','原西铰A门50mm把手87–90°碰墙；本轮东铰内开复算，实际门框、开关与五金仍待核。']);q.save('06-alterations.svg');items.append(('06-alterations.svg','主卧与衣帽区待核界面'))
 q=g.Drawing('当前玄关柜墙与拆改界面');pt,r,s=q.plan([-3800,1600,3650,3650],[40,120,1080,670]);q.notes(['1010mm短墙段表达为30西收口＋900鞋柜＋80门侧收口；原短墙性质与门框固定方式须现场核实。','鞋柜南面Y2724、柜背Y3124，浅柜南端Y3174，间隔50；家庭厅1500门洞保持。','本图仅表达最新柜墙概念，不代表结构拆除许可；实际条件不成立时暂停，不扩大柜深或移动其他家具。']);q.save('16-entry-alterations.svg');items.append(('16-entry-alterations.svg','玄关柜墙待核界面'))
 q=g.Drawing('当前600mm衣篮完整候选路线');q.plan([-4500,-1600,9800,5200],[40,125,1320,670],route=g.D['route_candidates']['入户至洗烘完整候选'],labels=False)
 q.notes(['入户Y2300 → X−2600、Y200 → X200、Y875 → 洗烘X4500；客卫已取消外开门绕行约束。','鞋柜关闭、门固定打开、正常四／六人就座时，600方篮及每侧额外10mm算例均无概念实体命中。','北排任一餐椅拉出500或全部拉出均阻断本线；鞋柜取物、设备装卸、基站进出与携篮必须错时。']);q.save('10-workflows.svg');items.append(('10-workflows.svg','完整洗烘衣篮候选路线'))
 items=sorted(items);g.dump(R/'reports/drawing_index.json',items)
 for p in (R/'data/schedules').glob('*.csv'):shutil.copy2(p,R/'tables'/p.name)
 table('设备预留表.csv',['设备','西X_mm','南Y_mm','宽_mm','深_mm','底标高_mm','高_mm','预留条件','型号','安装图','最终柜图'],[[a['label'],*a['box'],a['z'],a['height'],a['water'],'待选型','待提供','不得下单'] for a in g.D['appliances'].values()])
 table('水电点位表.csv',['点号','用途','X_mm','Y_mm','标高','给排水','检修及限制','状态'],[[a['id'],a['name'],a['x'],a['y'],a['height'],a['water'],a['note'],'概念／现场待核'] for a in g.services()])
 shoe=g.F['shoe'];shallow=g.F['study_shallow'];island=g.F['island'];bed=g.F['bedA'];ward=g.F['entry_wardrobe'];fridge=g.F['fridge'];family_door=g.D['doors']['family_entry_main_leaf']['open_box']
 door_gap=family_door[0]-(shoe['box'][0]+shoe['box'][2])
 table('柜墙关键尺寸.csv',['项目',g.D['revision']+'数值','口径'],[[g.name(n)+'坐标','／'.join(map(str,g.F[n]['box'][:2])),'mm'] for n in ['shoe','study_shallow']]+[[g.name(n)+'外尺寸','×'.join(map(str,[*g.F[n]['box'][2:],g.F[n]['height']])),'mm'] for n in ['shoe','study_shallow']]+[['柜背至浅柜',shallow['box'][1]-sum([shoe['box'][1],shoe['box'][3]]),'名义mm'],['全开家庭厅主门至鞋柜',door_gap,'门板净距mm；五金另核']])
 fridge_gap=island['box'][1]-(fridge['box'][1]+fridge['box'][3])
 table('新图尺寸标注.csv',['指标','数值','单位','性质'],[[n,v,'mm','概念几何，真实家具待核'] for n,v in [('岛台总长',island['box'][2]),('岛台初选台面高',island['height']),('入口衣柜外宽',ward['box'][2]),('柜内净宽总计',ward['modules']*(ward['module_width']-2*ward['side_panel'])),('柜端至床侧',bed['box'][0]-ward['box'][0]-ward['box'][2]),('冰箱至岛台名义间距',fridge_gap),('冰箱开门600加站人600后余量',fridge_gap-1200)]]+[['新主卫几何面积',sum(g.area(b) for b in g.D['rooms']['Bath_A']),'㎡','概念净边界']])
 table('家具尺寸表.csv',['编号','名称','空间','西X_mm','南Y_mm','宽X_mm','深Y_mm','高_mm','底标高_mm','性质'],[[n,g.name(n),g.name(f['room']),*f['box'],f['height'],f.get('z',0),'R10.5概念，非实测或下单'] for n,f in g.F.items()])
 table('新图面积标注.csv',['空间','几何面积_m2','口径'],[[g.name(n),round(sum(b[2]*b[3]/1e6 for b in bs),4),'当前房间边界，不扣家具，非现场或产权面积'] for n,bs in g.D['rooms'].items()])
 e=g.REPORT['evidence'];table('衣篮路线核验.csv',['路线','人数','餐椅状态','鞋柜状态','600实体命中','额外10mm命中','错时操作','条件'],[[v['route'],v['seats'],v['state'],v['shoe_state'],'；'.join(v['solid_hits']),'；'.join(v['reserve_10mm_hits']),'；'.join(v['service_overlaps']),v['status']] for v in e['basket_routes']])
 table('逐室功能表.csv',['房间','功能安排'],[[g.name(n),'；'.join(v)] for n,v in g.D['room_functions'].items()])
 table('辅助设施尺寸表.csv',['编号','房间','用途','西X_mm','南Y_mm','宽_mm','深_mm','底标高_mm','高_mm','条件'],[[n,g.name(v['room']),v['label'],*v['box'],v['z'],v['height'],v['status']] for n,v in g.D['accessories'].items()])
 table('逐室状态核验.csv',['状态','房间','西X','南Y','宽','深','固定命中','全开门命中','结论'],[[n,g.name(v['room']),*v['box'],'；'.join(v['fixed_hits']),'；'.join(v['open_door_hits']),v['status']] for n,v in e['room_use_states'].items()])
 table('逐室路线核验.csv',['过程','核验宽度mm','固定及门命中','使用区域重叠','结论'],[[v['workflow'],v['width_mm'],'；'.join(v['fixed_or_open_door_hits']),'；'.join(v['operation_overlaps']),v['status']] for v in e['whole_home_workflows']])
 table('就座与开启核验.csv',['人数','椅状态','实体命中','设备开启命中','错时人员操作'],[[v['seats'],v['state'],str(v['physical_hits']),str(v['equipment_opening_hits']),str(v['time_shared_operator_overlaps'])] for v in e['dining_states']])
 figures=''.join(f'<figure><figcaption>{g.esc(t)} · <a href="../drawings/svg/{n}">SVG</a> · <a href="../drawings/png/{n[:-4]}.png">PNG</a></figcaption><img src="../drawings/png/{n[:-4]}.png" alt="{g.esc(t)}" loading="lazy"></figure>' for n,t in items)
 links=''.join(f'<li><a href="../tables/{g.esc(p.name)}">{g.esc(p.name)}</a></li>' for p in sorted((R/'tables').glob('*.csv')))
 page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R10.5 全部方案成果</title><style>body{margin:0;background:#f4f2e9;color:#234238;font:17px/1.75 -apple-system,"PingFang SC",sans-serif}main{max-width:1200px;margin:auto;padding:30px 20px}header{padding:30px;background:#23473d;color:white;border-radius:16px}a{color:#397159}figure{background:#fffdf8;padding:14px;margin:24px 0;border:1px solid #dce0d5}img{width:100%;display:block}aside{margin:25px 0;padding:20px;background:#e7ebdf;border-left:4px solid #a36a38}@media(max-width:600px){main{padding:12px}header{padding:20px}figure{overflow:auto}figure img{min-width:760px}}</style><main><header><h1>R10.5 · 当前方案</h1><p>尺寸依据、分用途座高、850初选台面、Cleanup适配待核、基站迁出岛台及逐室关门新风；当前模型投影与状态图分列。</p><p>本轮提供可编辑三维模型与二维图表，未生成三维渲染图。</p></header><aside><strong>仍有条件项：</strong>原西铰A门50mm把手87–90°碰墙；已改东铰复算，实物五金仍待核。柜墙可改性、固定及线路待现场。北排拉椅阻断洗烘携篮候选线；取鞋、浅柜南段操作及设备使用须错时。渲染质量未验收。</aside><p><a href="../README.md">项目入口</a> · <a href="handoff.md">接手说明</a> · <a href="constraints.md">尺寸与待核条件</a> · <a href="../model/whole_home_R10.5.blend">Blender模型</a> · <a href="../model/whole_home_R10.5.glb">GLB模型</a></p>'''+figures+'<h2>表格</h2><ul>'+links+'</ul></main></html>'
 room_rows=''.join('<tr><td>'+g.esc(g.name(n))+'</td><td>'+g.esc('；'.join(v))+'</td></tr>' for n,v in g.D['room_functions'].items())
 summary='<h2>逐室功能安排</h2><table style="width:100%;border-collapse:collapse"><tbody>'+room_rows+'</tbody></table><aside>主要连续通路以900mm为目标，并非全部达标。主卫原门洞计门板及把手后约585mm，500mm单人候选线可达，600/620mm携篮不通过。客卫改门、排污、防水与700名义淋浴入口均为现场待核条件。</aside>'
 page=page.replace('<h2>表格</h2>',summary+'<h2>表格</h2>')
 page=page.replace('<h2>逐室功能安排</h2>','<h2>R10.5 深化结论</h2><p>'+g.esc(air['conclusion'])+'</p><p>'+g.esc(dims['installation']['cleanup']['conclusion'])+'</p><p>'+g.esc(dims['conclusion'])+'</p><p><a href="design-review.md">尺寸、橱柜与新风深化依据</a></p><h2>逐室功能安排</h2>')
 (R/'docs/方案册.html').write_text(page)
 print(json.dumps({'revision':'R10.5','drawings':len(items),'tables':len(list((R/'tables').glob('*.csv'))),'hard_errors':g.REPORT['hard_errors']},ensure_ascii=False))
if __name__=='__main__':main()

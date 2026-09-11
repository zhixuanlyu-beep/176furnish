"""Deterministic offline booklet and schedules; preserve IDs and user-entry columns."""
import copy
import csv
import html
import json
from pathlib import Path
import r10_geometry as g
from sync_model import ROOT,MODEL,REVISION,read,digest,require_verified

HERE=Path(__file__).resolve().parent
def table(headers,rows):
    return '<table><thead><tr>'+''.join('<th>'+html.escape(str(v))+'</th>' for v in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in r)+'</tr>' for r in rows)+'</tbody></table>'
def overlay_rows():return read(HERE/'schedule_baseline.json')['底图对位核验.csv'][1:]
def position(n):return '('+','.join(str(round(v)) for v in g.BOXES[n])+') mm'
def schedules():
    data=copy.deepcopy(read(HERE/'schedule_baseline.json'))
    dims={r[0]:r for r in data['家具尺寸表.csv'][1:]}
    def dim(id,name,size,nature,condition):dims[id][:]=[id,name,size,nature,condition]
    dim('F01','家庭厅书桌',g.dimensions('desk'),position('desk'),'电脑椅正常与后退500mm；线缆随桌、不跨卧室通行线')
    dim('F02','家庭厅北段大件柜',g.dimensions('study_storage'),position('study_storage'),'朝东使用；桌上旧书柜不作为当前家具')
    dim('F03','家庭厅卧室通行','1000mm概念净宽','家庭厅内部不分隔','内部路线1000mm；卧室门洞单独报告净宽')
    dim('F04','四／六人桌',g.dimensions('table4')+'；'+g.dimensions('table6'),position('table4')+'；'+position('table6'),'正常就座可使用咖啡、蒸烤；完整拉出500mm后操作须分时')
    dim('F05','北侧通道','正常1100mm；全部拉出600mm','发布值见验证计算','600mm衣篮在全拉出状态余量0，不判舒适通过')
    dim('F06','横向岛桌',g.dimensions('island'),position('island'),'岛东桌西，六人向西伸200mm；岛东缝不作通路')
    for ident,n in [('F07','bedA'),('F08','bedB'),('F09','bedD')]:
        dim(ident,g.LABELS[n],g.dimensions(n),position(n),'当前床架平齐床垫，床侧900mm；D床尾1000mm，实物外挑需重算')
    dim('F10','卧室移门衣柜','；'.join(n+':'+g.dimensions(n) for n in ('wardrobeA','wardrobeB','wardrobeD')),'；'.join(position(n) for n in ('wardrobeA','wardrobeB','wardrobeD')),'A/D朝西、B朝东，移门与内嵌拉手；D柜在东墙')
    dim('F11','西墙沙发',g.dimensions('sofa'),position('sofa'),'面向幕布，入户及阳台通行现场放样')
    dim('F13','南墙柜','；'.join(g.LABELS[n]+':'+g.dimensions(n) for n in ('fridge','tower','coffee')),'西至东顺序不变','正常就座设备开启及操作已模型复核；型号待定')
    dim('F14','入户鞋柜',g.dimensions('shoe'),position('shoe'),'门扇全行程已概念核查，换鞋人位现场放样')
    dim('F16','带水岛台及连接',g.dimensions('island'),'桌高750；支撑70×120，端距15，梁底680mm','六人端膝余15mm、梁下30mm；独立承载、连接及排水待核')
    dim('F17','幕布',g.dimensions('screen'),position('screen'),'幕布后1000mm；画幅、投距、幕盒及吊架按实际选型')
    eq={r[0]:r for r in data['设备预留表.csv'][1:]}
    eq['E08'][3]=g.dimensions('coffee');eq['E08'][6]='正常就座可取水箱及废水盘；拉椅后人员操作区临时受限'
    for r in eq.values():
        if r[0]=='E10':r[2]='AC01客厅；AC02 A；AC03 B；AC04 D；AC05家庭厅'
        r[5]+='；图示管线路由仅补充概念示意，接点未确认'
    pts={r[0]:r for r in data['水电点位表.csv'][1:]}
    point_owner={'K01':'sink','K02':'hob','K03':'prep','K04':'tower','K05':'tower','C01':'fridge','C02':'island','H02':'table4','H03':'coffee','H05':'screen','S01':'desk','T01':'study_storage','L01':'laundry','R01':'robot_R01','L02':'robot_L02'}
    for id,n in point_owner.items():
        if id in pts:
            pts[id][1]=g.LABELS.get(n,n)+' '+position(n);pts[id][6]=position(n)+'；现场待测'
    pts['H02'][5]='四／六人1600／1800×750；岛1000×750；灯位随配置及现场放样'
    pts['H03'][2]='1800咖啡台＋磨豆机＋台式微波炉';pts['H03'][5]='正常就座可操作；抽屉500＋人位600，高度与选型分别核查'
    pts['K03'][5]='门650＋装卸600；600衣篮路线与洗碗装卸/岛槽操作交叠见状态计算，携篮时暂停操作'
    pts['C03'][5]='食品柜取消，取消柜内照明及电源预留；旧编号保留'
    pts['S02'][1]='家庭厅顶面'
    pts['AC05'][1]='家庭厅北侧、A门洞以西实墙高位';pts['AC05'][2]='书房挂机'
    pts['S01'][5]='1700×700电脑桌原位；电源及线缆随桌；AC05维护待厂家'
    pts['S02'][5]='家庭厅照明、温控与通风；旧桌上书柜不作为当前家具'
    pts['T01'][5]='缩短深柜朝东；柜体、书桌和移门操作分别核查'
    pts['H05'][5]='模型幕布后净距1000mm；幕盒及画面实物放样'
    for id,r in pts.items():
        if id.startswith('AC'):r[5]='补充概念路由；厂家维护净距、孔位、排水、外机及现场安装条件待核'
        r[9]=REVISION+'；概念预留，未确认接点'
    checks={r[0]:r for r in data['现场核验表.csv'][1:]}
    checks['V08'][2:6]=['家庭厅通行、阅读、隔声与通风','入口有框子母门；周边及下沉密封；桌椅后退与南浅北深柜放样','家庭厅连续通行、房门实际净宽分别核查','现场待测，隔声及空气交换未确认']
    checks['V09'][4:6]=['正常北带1100、全部拉出600mm；恢复就座再携600mm衣篮','正常就座咖啡/蒸烤操作通过；全拉出临时占人位；携篮与洗碗装卸/岛槽错时，现场待测']
    checks['V13'][4]='咖啡1800mm；取消食品柜，原柜列余401mm留空；微波炉散热待厂家'
    checks['V14'][2:6]=['家庭厅与卧室入口','1700×700桌、南浅北深柜、入口子母门及改位鞋柜共同放样','房门洞口、门框每端45mm及门扇全运动见模型快照','硬件、门槛、安装余量及现场净宽待核']
    checks['V20'][2:6]=['AC05与家庭厅北墙及书桌','实测顶侧距、滤网、孔位、排水及外机','旧书柜不作为已建家具，管线仅补充概念','厂家安装条件待核']
    checks['V22'][2:6]=['岛桌支撑70×120、端距15、梁底680mm','膝顶650、梁下30、六人端膝15mm；实际人体及家具复核','承载、伸缩锁止、可拆收口及水槽检修','待厂家安装图；座面入桌不等于碰撞']
    for r in data['新图面积标注.csv'][1:]:
        if r[0]=='原餐厅':r[2]='原图面积保留；家庭厅内部不分隔，不重新编造面积'
    for r in data['新图尺寸标注.csv'][1:]:
        if r[0]=='餐厅/B对应纵向段':r[2]='保留原图尺寸线；当前家庭厅及通道布局不改变原图标注'
    pts['C03'][1:6]=['原食品柜点位（取消）','取消','无','不新增预留','取消食品柜照明及电源；编号保留']
    for name,rows in data.items():
        if name in ('设备预留表.csv','电器上下水表.csv'):
            for r in rows[1:]:
                if any('食品柜' in v for v in r):
                    for j in range(1,min(len(r),7)):r[j]='取消食品柜及对应预留'
    additions=[('F18','浅柜','study_shallow'),('F19','边几','side_table'),('F20','单椅（旋转45°）','lounge_chair'),('F21','落地灯','floor_lamp'),('F22','台式微波炉','microwave')]
    for ident,label,n in additions:data['家具尺寸表.csv'].append([ident,label,g.dimensions(n),position(n),'概念初排；实际外沿及厂家条件见验证报告'])
    data['设备预留表.csv'].append(['E16','微波炉','咖啡台面东端',g.dimensions('microwave'),'独立台式、朝北','厂家散热及安装图待核','门扇、热食取放与散热分别校核','','',''])
    data['电器上下水表.csv'].append(['微波炉','无固定给水','无排水','咖啡台面东端、朝北；按铭牌配电；厂家散热及热食取放净距待核'])
    data['水电点位表.csv'].append(['H06','微波炉 '+position('microwave'),'独立台式设备电源','按铭牌核定','台面可检修','不封入未经核定柜格；厂家安装图替换概念包络','','','',REVISION])
    data['水电点位表.csv'].append(['H07','边几／单椅附近','落地灯插座','按选型','沿家具和墙边','线缆见配置；不跨客厅主通路','','','',REVISION])
    data['现场核验表.csv'].append(['V24','本轮新增','M03北侧180×120mm孤立块','仅拟拆北块；保留C/D端墙120×300mm','现场确认结构性质后才可实施','未确认','','','',''])
    data['现场核验表.csv'].append(['V25','本轮新增','有框子母安全玻璃门','整门隔声检测、安装缝、周边及下沉密封、关门通风','主副扇与五金按选型替换净宽','未确认','','','',''])
    # Preserve hand-entered columns by stable ID, without preserving stale generated defaults.
    manual={'设备预留表.csv':range(7,10),'水电点位表.csv':range(6,10),'现场核验表.csv':range(6,10)}
    old_generated=read(HERE/'generated_schedule_state.json') if (HERE/'generated_schedule_state.json').exists() else read(HERE/'schedule_baseline.json')
    generated=copy.deepcopy(data)
    for name,cols in manual.items():
        if not (HERE/name).exists():continue
        old={r[0]:r for r in csv.reader((HERE/name).open(encoding='utf-8-sig',newline=''))}
        defaults={r[0]:r for r in old_generated[name][1:]}
        for r in data[name][1:]:
            if r[0] not in old:continue
            for col in cols:
                if old[r[0]][col] and old[r[0]][col]!=defaults.get(r[0],r)[col]:r[col]=old[r[0]][col]
    return data,generated

def protected():
    manifest=read(HERE/'protected_artifacts.json')
    for n,h in manifest.items():assert digest(ROOT/n)==h,n+' changed'
    return manifest

def build():
    require_verified();protected();validation=g.M.validation()
    data,generated=schedules();svgs=g.drawings()
    for name,rows in data.items():
        assert len({r[0] for r in rows[1:]})==len(rows)-1,name
        with (HERE/name).open('w',encoding='utf-8-sig',newline='') as f:csv.writer(f,lineterminator='\n').writerows(rows)
    (HERE/'generated_schedule_state.json').write_text(json.dumps(generated,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for n,s in svgs.items():(HERE/n).write_text(s,encoding='utf-8',newline='\n')
    pages=[];titles=[]
    def page(title,body):
        i=len(pages);titles.append(title)
        pages.append(f'<section class="page" id="p{i:02d}"><header><b>丽水嘉园 · 176㎡</b><span>{REVISION}</span></header><h1><b>{i:02d}</b>{html.escape(title)}</h1><p class="subtitle">配置与已验证实际网格同步 · 单位mm · 原图估读，未实测</p>{body}<footer><span>原图估读 · 非施工图 · 不用于下单、拆墙或预埋</span><span>{i:02d}</span></footer></section>')
    intro=g.conclusion()+['全屋同步：三张床、卧室移门衣柜、D东墙柜、幕布、家庭厅和卫浴概念占位均随当前模型。',
      '床侧900mm、D床尾1000mm、幕布后1000mm；B床垫1200mm。实际床架外挑、人体、设备及硬件选型需重算。',
      'M01/M02/M03恢复开放边界，C西开口2698mm。燃气使用条件未确认合规，梁柱及拆改结构现场核验。',
      '独立蒸箱、独立烤箱保留；咖啡柜1800×600，取消食品柜并留空401mm；微波炉放台面东端。',
      '旧管线路由仅补充概念示意，三维未建管线，W0为待确认接点。岛槽重力排水未成立；洗烘接管、空调安装待核。',
      '卫浴未确认原点位，机器人为候选未落实。原图面积和尺寸线、原26条问题记录保留。',
      '三维、SVG、CSV、HTML方案册及预览纳入GitHub交付；历史PDF、ZIP原样保留本地，本轮仅内存PDF检查。']
    page('全屋同步说明',''.join('<p>'+html.escape(s)+'</p>' for s in intro)+'<p><a href="../model3d/README.md">三维交付入口</a> · <a href="../model3d/CHECK_REPORT.md">三维中文冲突对照</a> · <a href="../model3d/geometry_snapshot.json">几何快照</a></p>')
    for i,(n,s) in enumerate(svgs.items()):
        page(g.TITLES[i],'<div class="wide-drawing">'+s+'</div><p class="caption">'+('补充概念示意：路由、剖面接点及安装条件未确认，不表示三维已建管线。' if i+1 in (3,10,12,13) else '实线为正常实体，虚线标明开启、拉出或候选状态；高度关系与中文冲突对照一并阅读。')+'</p>')
    rows=[]
    for s,b in zip(g.M.states,validation['baskets']):
        state='正常就座' if s['state']=='normal' else '全部拉出' if s['state']=='all_pulled' else '单椅拉出 '+s['state'].split(':')[1]
        rows.append([str(s['seats']),state,s['north_route_mm'],f"{s['physical']} / {s['human']} / {s['travel']} / {s['service']}",b['lateral_allowance_mm'],'恢复就座再携篮' if not b['comfortable_passage'] else '与洗碗/岛槽操作错时'])
    for i in range(0,len(rows),8):page('正常、单椅与全部拉出状态',table(['人数','状态','北带mm','实体/人体/运动/设备相交数','衣篮北带余量mm','使用限制'],rows[i:i+8])+'<p>相交数依据三维部件及高度包络；临时操作区占用单列，正常咖啡/蒸烤操作无冲突。</p>')
    basket_rows=[]
    for s,b in zip(g.M.states,validation['baskets']):
        if s['state'] not in ('normal','all_pulled'):continue
        basket_rows.append([s['seats'],s['state'],'装卸人位至北椅',str(b['dishwasher_loading_to_chair_mm'])+'mm净距','局部净距不等于整条路线通行宽度'])
        basket_rows.append([s['seats'],s['state'],'岛槽操作区',str(b['island_operator_route_gap_mm'])+'mm净距','路线无平面交叠，正常余量小；携篮仍先暂停操作'])
        for n,overlaps in b['service_overlaps_mm'].items():
            basket_rows.append([s['seats'],s['state'],n,'；'.join(f'{v[2]:.0f}×{v[3]:.0f}' for v in overlaps),'携篮时暂停该操作/开启；现场检查终点转向'])
    for i in range(0,len(basket_rows),10):page('衣篮路线与操作交叠计算',table(['人数','状态','操作/开启对象','交叠宽×深mm或净距','限制'],basket_rows[i:i+10])+'<p>房门完全打开后携篮，行走中不同时转动门扇；终点洗烘转向仍待现场演示。</p>')
    family=g.M.report['metrics']['family']
    page('本轮家庭厅调整与验证',table(['使用状态','连续通行检查'],[[r['state'],'通过' if r['passed'] else '未通过'] for r in family['states']])+'<p>内部主要路线1000mm；主扇入口通行包络800mm。关闭时允许门阻断，门两侧均可接近操作。浅柜人员操作与进门错时；柜门、抽屉展开仍可通行。</p>'+table(['门洞','扣框扇概念净宽mm'],[['家庭厅主扇',family['entrance']['main_net_mm']],['家庭厅双扇',family['entrance']['both_net_mm']],*[[n,d['net_mm']] for n,d in family['bedroom_doors'].items()]])+'<p>旧1100mm鞋柜堵路、电脑椅堵卧室路线及门扇侵柜反例均检出。硬件、整门隔声检测与关门通风待厂家。</p>')
    page('本轮客厅、咖啡区与拆改','<p>取消中央900×600茶几；保留沙发、幕布，增边几、朝西北单椅及落地灯。旋转后的实际外沿纳入碰撞检查。</p><p>咖啡柜1800×600，取消食品柜及预留，原柜列余401mm留空；微波炉520×420×320放台面东端朝北，厂家安装条件待核。</p><p>M03仅拟拆北侧180×120mm孤立块，保留C/D端墙120×300mm；结构性质须现场确认。</p><p>修改前已验证配置、网格和结果保存在 model3d/history/r10_1；原26条问题记录继续保留。</p>')
    old=read(MODEL/'previous_verification.json')['issues'];assert len(old)==26
    for i in range(0,26,7):
        page('原26条问题记录 · '+str(i//7+1),table(['原序号','类别','对象','原始详情'],[[j+1,o['category'],', '.join(o['objects']),json.dumps(o['detail'],ensure_ascii=False)] for j,o in enumerate(old[i:i+7],i)])+'<p>本页为历史记录，调整后结果见三维中文冲突对照；历史净距不作为本次发布值。</p>')
    for n,rs in data.items():
        # Small chunks retain every manual-entry column and stay within A3 print bounds.
        for i in range(1,len(rs),6):page(n[:-4]+' · '+str((i-1)//6+1),table(rs[0],rs[i:i+6]))
    css=(HERE/'booklet.css').read_text(encoding='utf-8')
    doc='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'+REVISION+'</title><style>'+css+'</style></head><body><nav><button onclick="window.print()">打印 / 另存PDF</button>'+''.join(f'<a href="#p{i:02d}">{i:02d} {html.escape(t)}</a>' for i,t in enumerate(titles))+'</nav><main>'+''.join(pages)+'</main></body></html>'
    (HERE/'方案册.html').write_text(doc,encoding='utf-8',newline='\n')
    for path,prefix,model_prefix in [(ROOT/'README.md','deliverables/','model3d/'),(HERE/'README.md','','../model3d/')]:
        links=[('方案册.html',f'{len(pages)}页离线方案册'),*zip(g.FILES,g.TITLES),*[(n,n) for n in data],('verification.json','交付验证报告')]
        body='# 丽水嘉园176㎡ · '+REVISION+'\n\n'+'\n\n'.join(intro)+'\n\n'+f'[三维交付入口]({model_prefix}README.md) · [中文冲突对照]({model_prefix}CHECK_REPORT.md)\n\n![全屋平面]({prefix}preview-furniture.png)\n\n'+'\n'.join(f'- [{t}]({prefix}{n})' for n,t in links)
        body+='\n\n以 `model3d/scene_config.json` 为唯一布局配置，实际部件外沿读已验证快照。`model3d/r10_baseline.json` 仅用于历史配置重建，由历史基线确定性重建R10.2，重复应用不追加对象；修改前成果见 model3d/history/r10_1。\n\n运行 `powershell -File model3d/run_background.ps1` 后，运行 `python deliverables/build_package.py`、`python deliverables/render_verify.py`。缺失或过期验证会阻止发布。需要 Blender、Playwright、PyMuPDF、Pillow 和 Chromium/Edge。所有PDF仅内存检查，不新建磁盘PDF。\n'
        path.write_text(body,encoding='utf-8',newline='\n')
    manifest=dict(revision=REVISION,model_files=g.M.report['files'],outputs={n:digest(HERE/n) for n in [*svgs,*data,'方案册.html','README.md']},root_readme=digest(ROOT/'README.md'),generators={n:digest(HERE/n) for n in ['build_package.py','r10_booklet.py','r10_geometry.py','sync_model.py','concept_details.py','booklet.css','schedule_baseline.json']},pages=len(pages))
    (HERE/'publication_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (HERE/'verification.json').write_text(json.dumps(dict(revision=REVISION,file_checks=dict(status='pending',action='运行 python deliverables/render_verify.py 完成本次渲染检查'),publication_manifest_sha256=digest(HERE/'publication_manifest.json')),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    protected();print(json.dumps(dict(revision=REVISION,pages=len(pages),svgs=len(svgs),csvs=len(data)),ensure_ascii=False))

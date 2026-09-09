"""Publish all R10.1 drawings and schedules from one geometry/data model."""
import csv
import html
import json
from pathlib import Path
import r10_geometry as g

HERE=Path(__file__).resolve().parent

def family_svg():
    p=g.start('R10.1 家庭厅 · AC05在A门洞西侧，书柜集中西侧',740)
    content=g.architecture()+g.furniture(whole=True)+g.ac_plan()
    p.append('<svg x="30" y="75" width="610" height="575" viewBox="-3900 -6600 5000 4700">'+g.project(content,0,0,1)+'</svg>')
    notes=['AC05：普通独立分体挂机，无新增风管。',
      '安装段x=-1400至-550，位于A门洞以西。',
      'A门洞x=-420至420；挂机与洞口净余130。',
      '桌上书柜宽600、深280集中西部。',
      '柜右端x=-1500，挂机左端x=-1400。',
      '横向间隙100，须按厂家加宽或缩柜。',
      '安装高度、顶距和滤网抽出方向待选型。',
      '出风朝东南通行侧，避开西部办公椅。',
      '冷媒、电源、冷凝水独立线型分别表示。',
      '孔位、排水接点、外机均为核验端点。',
      '西柜门、办公椅、鞋柜及入户转弯共核。',
      '桌1650×700；桌端至B墙980，净宽待测。']
    p += [g.text(880,110+i*46,t,14,g.AMBER if i in (5,6,9) else g.INK) for i,t in enumerate(notes)]
    p.append(g.text(575,698,'挂机横向位置已调整；厂家维护净距、管线穿墙及室外机条件尚未通过安装验收。',15,g.AMBER))
    return ''.join(p+['</g></svg>'])

def overlay_rows():
    # Independently read source landmarks (pixels); not generated from model.
    anchors=[('A东北外角', (6860,-10197),(834,64)),
      ('A西北外角',(-660,-10197),(503,64)),
      ('B飘窗外上角',(4726,-5400),(740,277)),
      ('C飘窗外下角',(4726,2200),(740,614)),
      ('D飘窗外下角',(2760,6962),(654,825)),
      ('阳台B外东北',(5213,-2844),(764,390)),
      ('阳台A西南外角',(-4412,6470),(337,805)),
      ('入户下转折',(-3650,-1370),(371,457)),
      ('公卫东南墙外角',(1720,-1250),(609,462)),
      ('C西北端',(0,0),(532,516)),
      ('C/D东侧交点',(3976,2998),(707,649))]
    sx,sy=g.SOURCE_TRANSFORM['px_per_mm'];rows=[]
    for name,(x,y),(px,py) in anchors:
        mx,my=532+x*sx,516+y*sy
        rows.append([name,x,y,px,py,round(mx,2),round(my,2),round(((mx-px)**2+(my-py)**2)**.5,2),'原图目视估读；非现场验收'])
    return rows

def build(data):
    eq=data['EQUIPMENT'];points=data['POINTS'];checks=data['CHECKS'];water=data['WATER_NEEDS']
    eq.append(['E15','岛台辅助小水槽','C02岛台东部','槽340×360初排；岛1000×750',
      '柜内冷热独立阀、存水弯、清扫检修与漏水探测','原厨房引冷热水；C东侧向北回合法生活污水支管',
      '重力排水未成立；测接入标高/构造厚度，不默认地台或提升泵'])
    points.append(['W0','原厨房主水槽合法生活污水支管核验端点','岛台重力排水接入',
      '平面长3452；2%落差69.04；接入内底z0及地面H待测','无；检修可达','不预设结构开槽，条件未成立继续协调带水需求'])
    water.append(['E15 岛台辅助水槽','冷/热水，独立可关阀','合法生活污水，存水弯、检修、漏水探测',
      'C02东部；经C东侧向北回W0，3.452m初排；重力排水未成立'])
    checks += [
      ['V17','测绘/设计师','底图对位及墙厚、B/C/D飘窗、入户转折、公卫门洞',
       '11图与底图对位核验CSV逐点核，补实测净尺寸','所有专业使用同一模型；窗台不计净宽','原图对位已文件核查，现场待测'],
      ['V18','给排水/结构/物业','C02至W0管路、地面H和接入内底z0',
       '逐段长度、坡度、落差、支管属性、结构障碍及剖面签认','13图；平地保留带水需求','重力排水未成立；不得擅自改干岛或提升泵'],
      ['V19','暖通/幕墙/影音','阳台A封窗、AC01梁窗头机身吊顶与检修',
       '12图实测净高、厂家安装图、站人检修、投影灯具窗帘共同放样','向客厅北送风、客厅侧回风','吊顶高度/冷凝水接点/外机待核'],
      ['V20','暖通/柜体商','AC05北实墙、A门洞西侧与西部书柜',
       '顶距/侧距/滤网抽取、实际孔位、冷媒电线冷凝水及外机记录','06/10图；普通挂机','维护间距尚待厂家验证']]
    # Revise AC-specific rows instead of retaining generic routing assertions.
    for row in points:
        if row[0]=='AC01':
            row[3]='冷凝水沿阳台A侧至合法接点核验端点；标高坡度待测'
            row[5]='客厅侧回风，向北送风；检修站位1000×850；梁窗头及吊顶底见12图'
        if row[0]=='AC05':
            row[3]='普通挂机冷凝水单独核高差；不增加通风管道'
            row[5]='书柜集中西侧；冷媒孔位/外机/排水均待核，滤网检修按厂家'
    checks += [
      ['V21','设备/给排水/业主','R01主选研究，L02备选','14图核洁具、干湿边界、门槛、进出、托盘及阀门；L02开门/洗烘维护/搬机/携篮','不移动洁具或压缩洗烘前场','R01尚未成立；L02旧占位冲突'],
      ['V22','家具厂家/业主','岛桌独立支承、腿/膝/轨道、76可拆收口','15图核四/六人平面和膝高、承载、伸缩锁止、清洁及管线检修','固定岛不承未经核算的悬挑','待安装图与放样'],
      ['V23','暖通/测绘','AC02/03沿东墙800×240候选','AC02(6380,-7250,240,800)；AC03(3736,-3750,240,800)；核背板实墙、飘窗及衣柜','送风向西；三类管线起点随设备','平面试排；高度及维护净距待厂家']]
    for row in points:
        if row[0] in ('AC02','AC03'):row[1]='东实墙靠床尾800×240候选；坐标见10图统一模型';row[5]='背板避飘窗/衣柜；安装高度及维护距离待厂家'
        if row[0]=='R01':row[5]='550×450试排；洁具、干湿界、门槛、进出/托盘/阀门前场待测，尚未成立'
        if row[0]=='L02':row[5]='旧650×450与门扇连续扫掠冲突；不占洗烘装卸、过滤器、携篮转向及搬机'
    table=data['table'];write=data['write_csv']
    schedules=[
      ('家具尺寸表.csv',['编号','家具或空间','尺寸目标_mm','尺寸性质','锁定条件'],data['DIMENSIONS']),
      ('设备预留表.csv',['编号','设备','候选位置','规划起点_非下单尺寸','型号安装图需锁定','水电及检修条件','验收动作','候选品牌型号','安装图版本','最终柜体尺寸_mm'],[r+['待选型','待提供','待实测及选型'] for r in eq]),
      ('水电点位表.csv',['点号','候选区域','用途','给排水要求','电气及控制要求','检修及限制','水平定位_mm','标高_mm','回路及保护','状态'],[r+['统一模型估读；待实测','待设备/柜图锁定','待负荷计算','R10.1概念预留'] for r in points]),
      ('现场核验表.csv',['编号','建议负责方','待核内容','证据或通过记录','影响交付','状态','实测值或结论','证据链接或图号','签认人','日期'],[r+['','','',''] for r in checks]),
      ('新图面积标注.csv',['空间','新图面积_平方米','设计影响'],data['NEW_AREAS']),
      ('新图尺寸标注.csv',['尺寸线对应区域','图注_mm_非实测净尺寸','使用边界'],data['NEW_SPANS']),
      ('电器上下水表.csv',['设备','固定给水需求','排水或废水处理','位置与锁定条件'],water),
      ('底图对位核验.csv',['核对点','模型x_mm','模型y_mm','原图x_px','原图y_px','投影x_px','投影y_px','残差_px','性质'],overlay_rows())]
    for name,headers,rows in schedules:write(name,headers,rows)
    svgs={'01-furniture.svg':g.floorplan('家具平面'),'02-alterations-review.svg':g.floorplan('拆改'),
      '03-services.svg':g.floorplan('水电'),'04-cabinet-access.svg':data['cabinet_svg'](),
      '05-coffee-sideboard.svg':data['coffee_svg'](),'06-utility-storage.svg':family_svg(),
      '07-island-dining.svg':g.island_svg(),'08-appliance-clearance.svg':g.clearance_svg(),
      '09-workflows.svg':g.workflow_svg(),'10-air-conditioning.svg':g.floorplan('空调'),
      '11-source-overlay.svg':g.overlay_svg(),'12-ac01-ceiling-section.svg':g.ceiling_svg(),
      '13-island-water-section.svg':g.water_svg(),'14-robot-station-review.svg':g.robot_svg(),'15-island-table-connection.svg':g.connection_svg()}
    for name,svg in svgs.items():(HERE/name).write_text(svg,encoding='utf-8',newline='\n')
    pages=[];names=[]
    def page(title,sub,body):
        n=len(pages);names.append(title)
        pages.append(f'<section class="page" id="p{n:02d}"><header><b>丽水嘉园 · 176㎡ / LISHUI JIAYUAN</b><span>R10.1 · 2026.09.09</span></header><h1><b>{n:02d}</b>{title}</h1><p class="subtitle">{sub}</p>{body}<footer><span>原图估读 · 未实测 · 非施工图 · 不用于下单、拆墙或预埋</span><span>R10.1 / {n:02d}</span></footer></section>')
    def cards(items):return ''.join(f'<div class="card"><h3>{html.escape(a)}</h3><p>{html.escape(b)}</p></div>' for a,b in items)
    def draw(name):return '<div class="wide-drawing">'+svgs[name]+'</div>'
    common=[('已确定布局','南墙整排柜保持冰箱950–1000、必配独立蒸箱与独立烤箱高柜600、咖啡1300、食品余量的顺序。岛1000×750在东，桌1600×800在西并向西延伸1800。'),
      ('使用边界','北侧为去上部厨房和阳台B主路线。南排就座与蒸烤/咖啡取物须错时。就座装卸局部624，600衣篮仅余24；携篮与装卸、岛槽错时。'),
      ('水路与空调','岛东部加辅助小水槽及冷热水，主槽、洗碗、800净备菜保留。重力排水未成立。AC01移至封窗连通阳台A交界顶面，向北送风；AC05在家庭厅北侧A门洞以西。'),
      ('底图与现场','B/C/D飘窗、入户转折、两阳台与公卫门洞逐项复核；所有全屋和局部共用毫米模型。原图估读不等于实测净尺寸，燃气使用条件未确认合规。')]
    page('横向带水岛桌与南侧风管机','R10.1评审方案：先核底图，再核布局、设备与管线。','<div class="plan-grid"><div class="drawing">'+svgs['01-furniture.svg']+'</div><div>'+cards(common)+'</div></div>')
    details={
      '01-furniture.svg':('完成平面',common[:2]),
      '02-alterations-review.svg':('拆改与原门洞',[('M01 / M02 / M03','红长虚线为拟拆实体：C北细墙、厨房西南短墙、C西细墙；原门口缺口不虚构成实墙。保留粗墙梁柱、公卫和C/D墙，结构与墙内管线待核。'),('燃气与封窗','开放餐厨保留燃气，使用条件单列待核。阳台A封窗与客厅连通；原交界梁、端墙及封窗审批和热工条件现场确认。')]),
      '03-services.svg':('水电定位',[('C02 / W0','岛槽冷热阀、存水弯、检修和探漏同柜排布；管线经C东侧向北，连接合法生活污水支管。高差未成立见13图。'),('电源与控制','蒸箱K04、烤箱K05分别供电；H03咖啡仅接电。L01洗烘、L02/R01机器人二选一；H04投影与H05幕盒协同空调，回路按负荷核算。')]),
      '04-cabinet-access.svg':('南墙柜立面',[('J01 / J02','主水槽邻柜阀电可达，存水弯与滤芯独立检修。冰箱、上下两台蒸烤分别拆出；热盘依次取，不跨下层热门。'),('J03 / J04','阳台B洗烘按机型留阀门、过滤器和整机前抽；L02旧基站位已检出门扫掠冲突。狭长净宽、门窗开启及搬出尚未确认。')]),
      '05-coffee-sideboard.svg':('蒸烤取物与咖啡立剖面',[('高度和散热','取热盘650/1150与蒸箱取箱1350为算例，按使用者和厂家安装图调整；独立供电、散热、检修。南侧有人就座时先离座取物。')]),
      '06-utility-storage.svg':('家庭厅与AC05',[('书柜与挂机','桌上书柜集中西侧；现有横向间隙100mm，须按机型留足维护余量，可缩书柜宽度。AC05普通挂机不增加通风管道。')]),
      '07-island-dining.svg':('四人、六人和南移边界',[('坐标与取舍','四人桌(1300,200)，六人桌(1100,200)，岛(2900,225)。南移再48mm即触及蒸烤全开门投影；不再向南挤压。全拉椅的650北侧净带仍需现场放样。')]),
      '08-appliance-clearance.svg':('满开与操作占用',[('分别验收','柜门、抽屉全开不碰四/六人椅；南排就座占用蒸烤/咖啡人位。两台蒸烤热盘依次取，取上层时收下层门。实际铰链开角、热盘宽度及维护包络待替换。')]),
      '09-workflows.svg':('北侧通行与七类工作顺序',[('携篮条件','600方形包络计算至阳台B入口内侧，原门洞850估读；柜椅不需移动。进门后关门、转向洗烘及搬机需实物验证。就座装卸局部624、600衣篮余24；携篮与装卸、岛槽操作错时。')]),
      '10-air-conditioning.svg':('五套独立空调',[('AC01 南侧风管机','阳台A靠客厅交界，向客厅北侧送风、客厅侧取回风；检修口位于可站人维护区，吊顶剖面见12图。公共区负荷含连通餐区。'),('线型与核验端点','橙长虚线冷媒、红点线电源、蓝短虚线冷凝水；各线起于对应机组。末端“？”为穿墙孔/外机/接点待核，不表示已确认安装位。'),('设备协调','AC02–AC05均普通独立挂机；AC05出风朝东南避办公座席。梁窗头、投影、灯具、幕盒、窗帘、室外机及冷凝水标高由专业深化。')]),
      '11-source-overlay.svg':('原图半透明叠合',[('对位记录','原图11个可辨节点独立估读残差列入底图对位核验.csv；此检查只证实模型与图片关系，不是测绘或结构鉴定。'),('待现场替换','120/240墙厚、门洞、B/C/D窗台深度及梁柱为估读，窗台不计通路。拟拆墙边界在拆改图单列。')]),
      '12-ac01-ceiling-section.svg':('风管机局部吊顶剖面',[('高度不预设','梁底、窗头、机身、保温风管、送回风口、检修口和吊顶底均建立关系；具体高度按净高和设备安装图确定。检修梯位不落在沙发、幕布或固定柜上。')]),
      '13-island-water-section.svg':('岛槽给排水平面与剖面',[('保持带水和平地需求','z0和H缺实测，图示坡度仅研究场景；重力排水未成立。不得预设开凿结构板、梁或飘窗台，不默认地台或提升泵，保留需求继续协调。')])}
    details.update({'14-robot-station-review.svg':('机器人基站核验',[('R01主选研究，尚未成立','东北角仅见疑似洁具轮廓；其余洁具、干湿分界及门槛待测。不改变湿区或洁具。L02旧占位与连续门扫掠冲突，降为备选。')]),'15-island-table-connection.svg':('岛桌连接',[('独立支承与维护','岛850–900、桌约750；向西伸200不移岛。桌腿/膝部/轨道为候选包络，承载及维护净距待厂家。76缝可拆收口。')])})
    for name,(title,notes) in details.items():
        if name in ['01-furniture.svg','02-alterations-review.svg','03-services.svg','10-air-conditioning.svg']:
            body='<div class="plan-grid"><div class="drawing">'+svgs[name]+'</div><div>'+cards(notes)+'</div></div>'
        else:body=draw(name)+cards(notes)
        page(title,'统一坐标与对象；全部标注为原图估读或设备初排，单位mm。',body)
    state_rows=[]
    for state in g.trial_metrics()['states']:
        state_rows.append([str(state['seats'])+'人'+('全拉椅' if state['pulled'] else '就座'),
          '餐区算例无相交；房门另核','北带'+('650' if state['pulled'] else '1000'),
          '、'.join(sorted({k for _,k in state['chair_operator_conflicts']})),
          '洗碗装卸、岛槽操作（错时）'])
    page('状态验证与现场动作','英文对象编号对应verification.json；冲突须错时使用，不算成净通路。',
      table(['状态','固定柜及满开门','北侧净距','需离座操作的设备','携篮需暂停的操作'],state_rows)+cards([
      ('冰箱与两台蒸烤','冰箱90°齐平铰链及全抽需选型支持；两台蒸烤分别开门取盘、取箱、拆机，依次操作，不能跨热门。'),
      ('洗碗、岛槽与携篮','洗碗门650＋装卸600；岛槽北站位600。两条携篮路径按椅子状态调整，端点到B门内，不把门后转向洗烘视为已验收。'),
      ('同时使用的边界','四/六人就座可保留主厨房备菜及单人洗碗；携篮时暂停洗碗装卸与岛槽操作，南排就座时暂停蒸烤/咖啡取物。全拉椅650、南侧48均仅估读，不证明舒适通行或安装余量。'),
      ('现场验收','燃气、结构、封窗、排水试验、空调排水与检修、断网实体控制和漏水报警单列；PDF/页面校验不替代现场验收。')]))
    # Complete schedules are also readable in the booklet, chunked to prevent clipping.
    for filename,headers,rows in schedules:
        if filename=='设备预留表.csv': headers=headers[:7];rows=[r[:7] for r in rows]
        if filename=='水电点位表.csv': headers=headers[:6];rows=[r[:6] for r in rows]
        if filename=='现场核验表.csv': headers=headers[:6];rows=[r[:6] for r in rows]
        size=10 if len(headers)>=6 else 12
        for i in range(0,len(rows),size):
            page(filename.removesuffix('.csv')+f' · {i//size+1}','配套CSV保留型号、测量、签认与日期填写栏；全部使用R10.1布局。',table(headers,[[str(v) for v in r] for r in rows[i:i+size]],'compact'))
    css=(HERE/'booklet.css').read_text(encoding='utf-8')
    doc='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>丽水嘉园176㎡ R10.1</title><style>'+css+'</style></head><body><nav><button onclick="window.print()">打印 / 另存PDF</button>'+''.join(f'<a href="#p{i:02d}">{i:02d} {html.escape(t)}</a>' for i,t in enumerate(names))+'</nav><main>'+''.join(pages)+'</main></body></html>'
    (HERE/'方案册.html').write_text(doc,encoding='utf-8',newline='\n')
    intro='''# 丽水嘉园176㎡ · R10.1 横向带水岛桌与南侧风管机

南墙柜保持冰箱、必配分体蒸烤、咖啡、食品的原位置与顺序。岛1000×750在东，桌1600×800在西、向西延伸1800；岛东部增加辅助小水槽及冷热水，原主水槽、洗碗机和800净备菜保留。

机器人优先研究公卫R01（550×450试排，尚未成立），L02阳台B降为备选；旧占位与门扇连续扫掠冲突。新增14机器人核验及15岛桌连接详图。

北侧主路线：就座净带1000、全拉椅650，均为估读算例。南排就座与蒸烤/咖啡取物须错时；携600衣篮时，就座装卸局部624、衣篮600仅余24；携篮与装卸及岛槽操作错时。南移仅余48即碰蒸烤全开门，不计作通道。

岛槽排水初排3.452m，2%需69.04mm落差。接入标高和可用地面厚度待测，**重力排水未成立**；保留带水和平地需求，不默认地台、提升泵或结构开槽。

阳台A封窗并连通客厅，AC01在交界顶面局部吊顶内向北送风、客厅侧回风；公共区冷量含餐区。AC05普通挂机在家庭厅北侧A门洞以西，桌上书柜集中西侧。吊顶高度、维护净距、孔位、冷凝水及外机均待核。

B/C/D飘窗、门窗、入户转折、公卫和阳台恢复为统一毫米模型，新增原图半透明叠合、风管机吊顶和岛槽给排水剖面。原图估读不是实测净尺寸；燃气使用条件未确认合规。文件验证不替代现场安装验收。
'''
    entries=[('方案册.html',f'{len(pages)}页离线方案册'),*[(k,v[0]) for k,v in details.items()],
      *[(name,name) for name,_,_ in schedules],('verification.json','渲染、几何及分页核查')]
    instructions='\n运行 `python deliverables/build_package.py` 与 `python deliverables/render_verify.py`。依赖Playwright、PyMuPDF、Pillow及Chromium/Edge（可设FURNISH_BROWSER）。几何统一于 `deliverables/r10_geometry.py`。PDF仅在内存验证，不写入或修改已有PDF；Git继续排除PDF、ZIP、加密文件及缓存。\n'
    for path,prefix in [(HERE.parent/'README.md','deliverables/'),(HERE/'README.md','')]:
        path.write_text(intro+'\n![R10.1平面]('+prefix+'preview-furniture.png)\n\n'+'\n'.join(f'- [{title}]({prefix}{name})' for name,title in entries)+'\n'+instructions,encoding='utf-8',newline='\n')
    print(json.dumps({'revision':'R10.1','pages':len(pages),'svg_count':len(svgs),'model':g.model_digest()},ensure_ascii=False))

"""R10.5 evidence-gated dimension and fresh-air calculations. No network on rebuild."""
import collections
import json
from pathlib import Path
import plan2d as g

R=Path(__file__).resolve().parents[1]


def load(name):
    return json.loads((R/'data/schedules'/name).read_text(encoding='utf-8'))


def ventilation():
    v=load('ventilation.json')
    room_area={room:sum(b[2]*b[3] for b in boxes)/1e6 for room,boxes in g.D['rooms'].items()}
    # Rectangles are disjoint; never substitute the advertised property area.
    rooms=[dict(room=n,area_m2=round(a,4),volume_m3=round(a*v['height_m'],4),height_m=v['height_m']) for n,a in room_area.items()]
    rows=[]
    for scenario in v['scenarios']:
        people=collections.Counter(scenario['occupants'].values())
        assert set(people)<=set(room_area)
        for room,count in people.items():
            q=count*v['per_person_m3h'];volume=room_area[room]*v['height_m']
            path=g.D['hvac_paths'][room]
            rows.append(dict(scenario=scenario['id'],label=scenario['label'],room=room,people=count,
                area_m2=round(room_area[room],4),volume_m3=round(volume,4),required_m3h=q,
                air_changes_h=round(q/volume,3),transfer_net_area_cm2=round(q/3600/v['transfer_velocity_ms']*10000,1),
                transfer_gross_area_cm2=round(q/3600/v['transfer_velocity_ms']/v['transfer_free_area_ratio']*10000,1),
                supply_path=path['status'],exhaust_verified=path['exhaust_point'] is not None,
                conclusion='条件不足；未核实夜间可用档与关门排气'))
    comparisons=[]
    for row in rows:
        for device in v['devices']:
            advertised=device['outdoor_air_advertised_m3h'];night=device['night_outdoor_air_m3h']
            minimum_gap=None if advertised is None else max(0,row['required_m3h']-advertised)
            required_evidence=['night_noise_dba','filter_pressure_pa','independent_operation','low_temperature_limit_c','wall_hole_mm']
            verified=(device['installation_verified'] and row['exhaust_verified'] and night is not None
                      and all(device[k] is not None for k in required_evidence)
                      and device['night_noise_dba']<=v['night_noise_target_dba']
                      and v['building_requirements_verified'])
            result='不足' if minimum_gap or (night is not None and night<row['required_m3h']) else ('满足' if verified and night>=row['required_m3h'] else '条件不足')
            comparisons.append(dict(scenario=row['scenario'],room=row['room'],device=device['id'],required_m3h=row['required_m3h'],advertised_m3h=advertised,night_m3h=night,advertised_minimum_deficit_m3h=minimum_gap,night_deficit_m3h=None if night is None else max(0,row['required_m3h']-night),conclusion=result))
    heat=[]
    for q in sorted({r['required_m3h'] for r in rows}|{150}):
        for outdoor in v['outdoor_sensitivity_c']:
            for eta in v['heat_recovery_sensitivity']:
                heat.append(dict(flow_m3h=q,indoor_c=v['indoor_c'],outdoor_c=outdoor,assumed_sensible_efficiency=eta,
                    sensible_load_w=round(1.2*1005*q/3600*(v['indoor_c']-outdoor)*(1-eta),1),
                    supply_after_recovery_c=round(outdoor+eta*(v['indoor_c']-outdoor),1)))
    return dict(revision=g.D['revision'],layout_sha256=g.digest(R/'data/layout.json'),
        inputs_sha256=g.digest(R/'data/schedules/ventilation.json'),rooms=rooms,
        geometric_area_total_m2=round(sum(room_area.values()),4),height_status=v['height_status'],
        scenarios=rows,device_comparisons=comparisons,winter_sensitivity=heat,
        conclusion='条件不足：本轮不建议取消独立新风预留。P7标称30对主卧两人60至少缺30；Ultra标称60也不能证明夜间60。',
        independent_options=v['independent_options'],
        limits=['按30m³/h·人比较；适用建筑标准及北京地方要求未全部核实。',
                '日常90、三人夜间90、含访客夜间150、家庭共读90互为场景，不把同一人重复相加。',
                '独立新风须按实际机外静压、滤网脏态、夜间噪声和低温防冻降风量选型。',
                '消声过风面积为0.5m/s、50%自由面积算例，非已选消声器；压降和隔声量待选型。',
                '卧室关门；不能依赖开门。厨卫排风与烟机补风分别核算，禁止接入独立新风排气管。',
                '冬季温度为敏感性假设，不冒充北京法定室外设计温度；20℃室温，ρ1.2kg/m³、cp1005J/(kg·K)。',
                '70%显热回收仅示例，需产品证据；热回收不证明风量足够。保温连续、防冷桥结露、冷凝排水防冻、过滤压降及冷风感待核。'])


def dimension_review():
    beds=[]
    for n,f in g.F.items():
        if f['kind']!='bed':continue
        x,y,w,d=f['box']
        for extra in f['frame_overhang_sensitivity_mm']:
            envelope=[x-extra,y-extra,w+2*extra,d+2*extra]
            p=g.rectpoly(envelope)
            fixed=[k for k,b in g.W.items() if g.collision(p,g.rectpoly(b))]
            fixed += [k for k,v in g.F.items() if k!=n and v['room']==f['room'] and g.collision(p,g.poly(k,v))]
            doors=[k for k,v in g.DOORS.items() if g.collision(p,g.rectpoly(v['open_box']))]
            beds.append(dict(bed=n,mattress_mm=f['mattress_size_mm'],actual_frame_mm=f['frame_external_size_mm'],
                assumed_each_side_overhang_mm=extra,envelope_mm=envelope,fixed_hits=fixed,open_door_hits=doors,
                child_bed_foot_to_stowed_chair_mm=round(y-extra-(g.F['child_chair']['box'][1]+g.F['child_chair']['box'][3])) if n=='bedB' else None,
                conclusion='实体冲突（敏感性算例）' if fixed else '仍待真实床架；算例不代表适配通过'))
    candidates=[]
    for n,v in g.D['installation_candidates'].items():
        body=g.rectpoly(v['box']);approach=g.rectpoly(v['approach'])
        fixed=[k for k,f in g.F.items() if f['room'] not in ['Dining_6','Candidate_Equipment'] and g.collision(body,g.poly(k,f))]
        fixed += [k for k,b in g.W.items() if g.collision(body,g.rectpoly(b))]
        ops=[k for k,z in g.D['use_zones'].items() if g.collision(approach,g.rectpoly(z['box']))]
        doors=[k for k,z in g.DOORS.items() if g.collision(approach,g.rectpoly(z['open_box']))]
        candidates.append(dict(candidate=n,body_mm=v['box'],approach_mm=v['approach'],fixed_hits=fixed,operation_time_overlaps=ops,open_door_overlaps=doors,status=v['status'],conclusion='待型号安装图；不能判通过'))
    return dict(revision=g.D['revision'],layout_sha256=g.digest(R/'data/layout.json'),beds=beds,robot_candidates=candidates,
                installation=load('product_installation.json'),historical_issues=g.D['historical_issues'],
                conclusion='真实床架及设备安装尺寸未锁定；概念基线与敏感性复算分列。儿童桌椅真实可调产品尚未锁定，不能声明适配。')


def publish(table):
    air=ventilation();dims=dimension_review();v=load('ventilation.json')
    g.dump(R/'reports/ventilation.json',air);g.dump(R/'reports/dimension_review.json',dims)
    table('逐室新风风量.csv',['工况','房间','人数','面积m2','体积m3','比较风量m3h','换气次数h-1','过风净面积cm2','格栅毛面积cm2','结论'],
          [[r['label'],g.name(r['room']),r['people'],r['area_m2'],r['volume_m3'],r['required_m3h'],r['air_changes_h'],r['transfer_net_area_cm2'],r['transfer_gross_area_cm2'],r['conclusion']] for r in air['scenarios']])
    table('新风空调比较.csv',['设备','官方展示室外风量m3h','夜间室外风量m3h','夜间对应噪声dBA','宣传最低噪声db_非同档证明','循环风量m3h','滤阻Pa','独立运行','低温下限','穿墙孔mm','来源','结论'],
          [[r['label'],r['outdoor_air_advertised_m3h'],r['night_outdoor_air_m3h'],r['night_noise_dba'],r['advertised_min_noise_db'],r['recirculation_m3h'],r['filter_pressure_pa'],r['independent_operation'],r['low_temperature_limit_c'],r['wall_hole_mm'],r['source'],'待核；空白不是零'] for r in v['devices']])
    table('新风逐设备缺口.csv',['工况','房间','设备','需求m3h','标称m3h','夜间m3h','标称最小缺口m3h','夜间缺口m3h','判断'],[[r[k] for k in ['scenario','room','device','required_m3h','advertised_m3h','night_m3h','advertised_minimum_deficit_m3h','night_deficit_m3h','conclusion']] for r in air['device_comparisons']])
    table('冬季新风热负荷.csv',['风量m3h','室内℃','室外℃_敏感性','假设显热回收效率','显热负荷W','回收后送风℃'],[[r[k] for k in ['flow_m3h','indoor_c','outdoor_c','assumed_sensible_efficiency','sensible_load_w','supply_after_recovery_c']] for r in air['winter_sensitivity']])
    table('尺寸来源依据.csv',['来源ID','类别','名称','版本','适用依据与限制','证据状态','链接'],[[s[k] for k in ['id','kind','title','version','evidence','status','url']] for s in load('dimension_sources.json')['sources']])
    table('床架外伸复算.csv',['床','床垫mm','真实床架mm','各侧假设外伸mm','复算外包络mm','固定命中','开门命中','儿童床尾净距mm','判断'],[[r['bed'],r['mattress_mm'],r['actual_frame_mm'],r['assumed_each_side_overhang_mm'],r['envelope_mm'],'；'.join(r['fixed_hits']),'；'.join(r['open_door_hits']),r['child_bed_foot_to_stowed_chair_mm'],r['conclusion']] for r in dims['beds']])
    table('家具使用高度.csv',['编号','总高mm','座高mm','桌下净高mm','靠背起点mm','调节范围mm','依据'],[[n,f['height'],f.get('seat_height_mm'),f.get('under_table_clear_height_mm'),f.get('back_bottom_mm'),f.get('seat_adjustment_range_mm',f.get('height_adjustment_range_mm')),f.get('status',f['dimension_status'])] for n,f in g.F.items() if f['kind'] in ['bed','chair','table']])
    table('设备安装证据.csv',['编号','型号','机身mm','开孔mm','散热mm','接管mm','完整开门拆机mm','状态'],[[r[k] for k in ['id','model','body_mm','cutout_mm','heat_clearance_mm','connections_mm','full_open_removal_mm','status']] for r in dims['installation']['items']])
    table('基站迁移复核.csv',['候选','机身控制区mm_非产品','前场算例mm','固定实体命中','操作错时重叠','全开门重叠','结论'],[[r['candidate'],r['body_mm'],r['approach_mm'],'；'.join(r['fixed_hits']),'；'.join(r['operation_time_overlaps']),'；'.join(r['open_door_overlaps']),r['conclusion']] for r in dims['robot_candidates']])
    return air,dims


def drawings():
    items=[]
    q=g.Drawing('关门卧室新风送排路径 · 原理与现场待核')
    pt,rect,scale=q.plan([-4700,-7100,11800,17600],[35,115,780,700],labels=False)
    for room,v in g.D['hvac_paths'].items():
        a,b=pt(v['supply_point']),pt(v['transfer_point'])
        q.p.append('<polyline points="'+' '.join(f'{x:g},{y:g}' for x,y in [a,b])+ '" fill="none" stroke="#467896" stroke-width="2" stroke-dasharray="6 4"/>')
        q.p.append(q.text(a[0],a[1]-8,g.name(room)+'拟进风',12,g.C['blue']))
        q.p.append(q.box([b[0]-4,b[1]-4,8,8],g.C['orange']))
    for i,t in enumerate(['室外 → 过滤 → 房间送风','房门关闭 → 消声过风','走道 → 独立排风 → 室外','末端排风出口尚未定位','蓝虚线：原理连线，非管路','橙方块：拟过风位置','A两人60；B一人30','D两访客60；共读90','三人总90；五人夜间150','厨卫排烟排风单独核算','不利用开卧室门补风']):q.p.append(q.text(850,155+46*i,t,18))
    q.notes(['拟过风位置和外墙进气点来自layout；未确定机型、风管长度、风压、隔声及墙体开孔许可。','所有关门排气路径均待核，不能判“不需要独立新风”；先保留独立平衡新风方案。','独立双向机可避免借走道排气；集中系统须核对梁、净高、检修、防火及新排风短路。'])
    q.save('31-ventilation.svg');items.append(('31-ventilation.svg','关门新风送排原理与待核路径'))
    q=g.Drawing('尺寸与高度校核 · 床架、就座及台面')
    pt,r,s=q.plan([1850,2750,2350,3500],[35,120,700,670],labels=False)
    b=g.F['bedB']['box'];e=50
    q.p.append(q.box(r([b[0]-e,b[1]-e,b[2]+2*e,b[3]+2*e]),'none',g.C['red'],True))
    q.dim(pt((3376,3494)),pt((3376,4047-e)),'503',30)
    for i,t in enumerate(['床垫 ≠ 床架最大外尺寸','红虚线：假设外伸50，非选型','床尾名义553；外伸50后503','只余3mm，不构成舒适通路','餐椅座高450；休闲椅430','儿童座高380仅绘图假设','儿童身高及产品调节范围待核','餐桌高750，梁底净高680','岛台/厨房850为试用起点','床架敏感性25/50/100另表','真实尺寸缺失不作安装通过']):q.p.append(q.text(770,150+48*i,t,18))
    q.notes(['真实床架未锁定；原床位不移动，外伸算例公开床头置物与床架可能冲突，详见床架外伸复算。','模型座高来自layout逐项输入；总高、座高、桌下净高分列，不再把椅子全设500mm座高。','儿童桌椅仍待官方产品尺寸及调节范围；不把暂定座高或桌高当作已适配孩子。'])
    q.save('32-dimension-review.svg');items.append(('32-dimension-review.svg','家具真实外尺寸与使用高度校核'))
    q=g.Drawing('常规厨房850台面 · 设备安装证据与操作')
    q.plan([1450,600,2700,2250],[45,130,850,650],ops=True,labels=False)
    for i,t in enumerate(['国内橱柜体系，台面初选850','水槽深度/锅具操作待试用','机身 / 开孔 / 散热分列','接管 / 开门 / 拆机分列','现有设备仅概念控制体','蒸烤及微波取热食高度待试','洗碗机完整安装图未取得','不削减拆机空间凑布局']):q.p.append(q.text(920,175+i*55,t,18))
    q.notes(['600级洗碗机不等于开孔已合格，底脚、门板厚度、通风、邻柜阀门与前抽路径必须按型号核对。','常规厨房与Cleanup岛台分开选型；台面高差、防水和封板只深化接口，不擅自改原厂成套柜。','当前二维开启框为概念操作算例，表格空白表示缺少厂家数据，不表示无需净空。'])
    q.save('33-kitchen-installation.svg');items.append(('33-kitchen-installation.svg','常规厨房与设备安装包络'))
    q=g.Drawing('机器人迁出岛台 · 两处候选与具体冲突')
    for candidate,bounds,frame in [('robot_laundry',[3950,0,1350,2800],[50,155,590,610]),('robot_coffee',[0,-3100,2100,2300],[750,155,590,610])]:
        pt,r,s=q.plan(bounds,frame,labels=False)
        c=g.D['installation_candidates'][candidate]
        q.p.append(q.box(r(c['box']),'#46789630',g.C['blue'],True))
        q.p.append(q.box(r(c['approach']),'none',g.C['orange'],True))
    q.p.append(q.text(70,130,'优先：洗烘阳台南端候选',20))
    q.p.append(q.text(760,130,'备用：咖啡柜西侧独立模块',20))
    q.notes(['蓝色为600×600候选控制区，橙色为操作前场；都不是实际机型安装图。','阳台候选机身当前无固定命中，前场与洗烘装卸重叠；完整开门、上盖取箱、检修与防冻仍待核。','咖啡柜候选与现有柜体实体相交，必须真正替换独立模块才可采用；当前未执行拆柜，不判通过。'])
    q.save('34-robot-candidates.svg');items.append(('34-robot-candidates.svg','基站迁移两处候选及冲突'))
    return items

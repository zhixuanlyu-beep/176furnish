"""Whole-home state checks from the millimetre layout, with explicit limitations."""
import itertools
import plan2d as g

def verify_rooms(report):
 e=report['evidence'];hard=report['hard_errors'];d=g.D;f=g.F
 e['historical_issues']=d['historical_issues']
 fixed={**g.active(),**{n:g.rectpoly(b) for n,b in g.W.items()}}
 # Seats nest below the tabletop only; a full-height rectangular chair is not a solid.
 nesting={frozenset((a,b)) for a,b in [('study_chair','desk'),('child_chair','child_desk')]}
 nesting.update(frozenset((n,'table'+n[5])) for n in f if n.startswith('chair'))
 hits=[];underlap=[]
 for a,b in itertools.combinations(fixed,2):
  if a in g.W and b in g.W:continue
  if not g.collision(fixed[a],fixed[b]):continue
  if a in f and b in f:
   fa,fb=f[a],f[b]
   if min(fa.get('z',0)+fa['height'],fb.get('z',0)+fb['height'])<=max(fa.get('z',0),fb.get('z',0)):continue
   if frozenset((a,b)) in nesting:
    chair,table=(fa,fb) if fa['kind']=='chair' else (fb,fa)
    x,y,w,h=chair['box'];facing=chair.get('facing','north')
    back=[x,y+h-50 if facing=='south' else y,w,50]
    if facing in ('east','west'):back=[x if facing=='east' else x+w-50,y,50,h]
    clear=table['height']-45>500 and not g.collision(g.rectpoly(back),g.rectpoly(table['box']))
    underlap.append({'pair':[a,b],'seat_top_mm':500,'table_underside_mm':table['height']-45,'back_clear':clear})
    if clear:continue
  hits.append([a,b])
 e['whole_home_fixed_hits']=hits;e['height_checked_nesting']=underlap
 if hits:hard.append('全屋固定几何相交，见whole_home_fixed_hits')
 zones={}
 for n,v in d['use_zones'].items():
  excluded={v.get('owner')}
  if n.startswith('child_'):excluded.add('child_chair')
  if n=='study_pull':excluded.add('study_chair')
  hs=[k for k,p in fixed.items() if k not in excluded and g.collision(g.rectpoly(v['box']),p)]
  doors=[k for k,vv in g.DOORS.items() if g.collision(g.rectpoly(v['box']),g.rectpoly(vv['open_box']))]
  zones[n]={**v,'fixed_hits':hs,'open_door_hits':doors,'status':'存在占位重叠，按状态复核' if hs or doors else '矩形占位无固定命中；非人体工学认证'}
 e['room_use_states']=zones
 e['operation_state_overlaps']=[{'states':[a,b],'classification':'操作时间重叠，非固定家具碰撞'} for a,b in itertools.combinations(zones,2) if zones[a]['room']==zones[b]['room'] and g.collision(g.rectpoly(zones[a]['box']),g.rectpoly(zones[b]['box']))]
 from validate_2d import handles,jambs
 door_hardware={n+'_handle_'+str(i):p for n,v in g.DOORS.items() for i,p in enumerate(handles(v)[90])}
 flows=[]
 for name,v in d['workflow_routes'].items():
  for width in (500,600,620,900):
   sweeps=[g.rectpoly([min(a[0],b[0])-width/2,min(a[1],b[1])-width/2,abs(a[0]-b[0])+width,abs(a[1]-b[1])+width]) for a,b in zip(v['points'],v['points'][1:])]
   obstacles={**fixed,**{k:g.rectpoly(vv['open_box']) for k,vv in g.DOORS.items()},'screen_down':g.rectpoly(d['use_zones']['screen_down']['box'])}
   obstacles.update(door_hardware);obstacles.update(jambs())
   for k in v.get('walkable_surfaces',[]):obstacles.pop(k,None)
   hit=sorted(k for k,p in obstacles.items() if any(g.collision(p,s) for s in sweeps))
   shared=sorted(k for k,z in d['use_zones'].items() if any(g.collision(g.rectpoly(z['box']),s) for s in sweeps))
   flows.append({'workflow':name,'width_mm':width,'points':v['points'],'fixed_or_open_door_hits':hit,'operation_overlaps':shared,'status':'候选中心线受阻；不作通行通过' if hit else '该宽度候选线无实体命中；操作重叠须错时'})
 e['whole_home_workflows']=flows
 blocked=[v['workflow'] for v in flows if v['width_mm']==500 and v['fixed_or_open_door_hits']]
 if blocked:hard.append('单人完整过程候选线受阻：'+','.join(blocked))
 normal_basket=[v for v in e['basket_routes'] if v['state']=='正常' and v['shoe_state']=='关闭' and v['reserve_10mm_hits']]
 if normal_basket:hard.append('正常就座携篮路线余量检查受阻')
 if e['room_handle_hits_site_review'].get('A_door_leaf'):hard.append('东铰A门把手仍有命中；须解决且保留旧记录')
 if e['door_frame_contacts_to_review'].get('bath_door_leaf'):hard.append('客卫移门平移与墙相交')
 if any(v['fixed_hits'] or v['open_door_hits'] for v in zones.values()):hard.append('逐室使用区存在固定或全开门命中')
 e['room_function_coverage']={k:{'functions':v,'use_states':[n for n,z in zones.items() if z['room']==k]} for k,v in d['room_functions'].items()}
 e['public_bath']={'area_m2':sum(g.area(b) for b in d['rooms']['Bath_Public']),'shower_mm':f['shower_public']['box'][2:],'shower_entry_nominal_mm':f['shower_public']['entry_gap_mm'],'dry_changing_placeholder_mm':d['use_zones']['public_changing']['box'][2:],'door_opening_mm':800,'jamb_assumption_each_mm':45,'door_clear_assumed_mm':710,'sliding_travel_mm':900,'central_turning_circle_900_fits':False,'status':'800×600占位非900转身圆；单人顺序共享；700淋浴入口须扣五金实测；门锁应急解锁、墙体承载、排污、防水坡度与挡水待核'}
 e['A_door_revision']={'historical':d['historical_issues'][0],'current_handle_hits':e['room_handle_hits_site_review'].get('A_door_leaf',{}),'current_leaf_hits':e['doors_0_to_90_degrees']['A_door_leaf'],'status':'东铰内开逐度概念复算；门框与开关及真实五金仍待核'}
 e['limitations']=['主卧原西铰门50mm把手87–90°碰墙记录保留；东铰结果见A_door_revision，实际五金未获施工确认。','固定实体、使用占位与候选路线结果分列；候选中心线受阻不等于整个房间不可达。','900mm是通路目标，800门洞扣门框假设仅710；浴室中央非900mm转身圆。','淋浴隔断700入口为名义尺寸，门锁隐私、排污、防水与结构须现场深化。','未生成三维渲染；状态几何及1°采样不等于连续实体或人体工学认证。']

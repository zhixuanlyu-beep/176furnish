"""R10.4 concept geometry checks; standard library, no 3D inputs."""
import json, math
import plan2d as g

def handles(v,projection=50):
 p,s,_=g.door_motion(v);x,y,w,h=v['closed_box']
 if w>h:
  start=x+w-120 if p[0]<x+w/2 else x+20
  boxes=[[start,y-projection,100,projection],[start,y+h,100,projection]]
 else:
  start=y+h-120 if p[1]<y+h/2 else y+20
  boxes=[[x-projection,start,projection,100],[x+w,start,projection,100]]
 return [[[g.rotate(q,p,s*a) for q in g.rectpoly(b)] for b in boxes] for a in range(91)]

def shoes():
 out=[]
 for side in range(2):
  x=-3380+side*450;p=(x if side==0 else x+450,2724);sign=-1 if side==0 else 1
  panel=g.rectpoly([x,2724,450,20]);hb=g.rectpoly([x+330 if side==0 else x+20,2719,100,5])
  out.append([[ [g.rotate(q,p,sign*a) for q in poly] for poly in [panel,hb]] for a in range(91)])
 return out

def jambs():
 out={}
 for n,o in g.D['openings'].items():
  if n not in {v['opening'] for v in g.DOORS.values()}:continue
  x,y,w,h=o['box']
  bs=[[x,y,45,h],[x+w-45,y,45,h]] if w>h else [[x,y,w,45],[x,y+h-45,w,45]]
  for i,b in enumerate(bs):out[n+'_jamb_'+str(i)]=g.rectpoly(b)
 return out

def validate():
 g.changed={'shoe','study_shallow'}
 report=g.validate();e=report['evidence'];hard=report['hard_errors']
 expected={'shoe':[-3380,2724,900,400],'study_shallow':[-3410,3174,450,1176],'desk':[-2280,5447,1700,700],'study_storage':[-3410,4350,650,1000],'study_chair':[-1400,4997,500,500]}
 for k,b in expected.items():
  if g.F[k]['box']!=b:hard.append(k+'不符合确认坐标')
 e['approved_fixed_coordinates_checked']=expected
 h={n:handles(v) for n,v in g.DOORS.items()};s=shoes();solid=g.active();solid.update({k:g.rectpoly(b) for k,b in g.W.items()})
 shoehits=[]
 for side,frames in enumerate(s):
  hit={}
  for a,shapes in enumerate(frames):
   for k,p in solid.items():
    if k=='shoe':continue
    if any(g.collision(t,p) for t in shapes):hit.setdefault(k,[]).append(a)
  shoehits.append({'side':side,'applies_to':'上下两门组，垂直分离','hits':{k:[min(v),max(v)] for k,v in hit.items()}})
 if any(v['hits'] for v in shoehits):hard.append('鞋柜门或5mm把手与固定实体冲突')
 e['shoe_doors_1_degree_samples']=shoehits
 main='family_entry_main_leaf';secondary='family_entry_secondary_leaf'
 fm={n:g.door_motion(g.DOORS[n])[2] for n in [main,secondary]}
 combos=[];shoe_family=[]
 for a in range(91):
  pa=[fm[main][a],*h[main][a]]
  for b in range(91):
   pb=[fm[secondary][b],*h[secondary][b]]
   if any(g.collision(x,y) for x in pa for y in pb):combos.append([a,b])
 for n in [main,secondary]:
  for a in range(91):
   for b in range(91):
    for side,frames in enumerate(s):
     if any(g.collision(x,y) for x in [fm[n][a],*h[n][a]] for y in frames[b]):shoe_family.append([n,a,b,side])
 e['family_door_combinations']={'tested':8281,'shoe_family_pairs_tested':33124,'colliding_angles':combos,'shoe_family_angle_hits':shoe_family,'method':'0–90°每1°离散采样；小于1°的运动区间未作解析证明'}
 if combos or shoe_family:hard.append('家庭厅门扇组合或鞋柜门运动冲突')
 hardware={}
 for n,frames in h.items():
  hit={}
  for a,hs in enumerate(frames):
   for k,p in solid.items():
    if any(g.collision(t,p) for t in hs):hit.setdefault(k,[]).append(a)
  if hit:hardware[n]={k:[min(v),max(v)] for k,v in hit.items()}
 e['room_handle_hits_site_review']=hardware
 # Two tracks remain inside carcass; free opening is a concept track estimate.
 e['sliding_doors']={'panels_mm':618,'travel_mm':558,'tracks_inside_total_depth_mm':450,'assumed_track_depth_mm':50,'approx_usable_depth_mm':364,'front_projection_mm':0,'nominal_half_open_mm':558,'status':'两轨错层移门；实际五金及净取物口待核'}
 slide_outside=[]
 for a in range(559):
  for b in [[-3000,3174+a,18,618],[-2978,3732-a,18,618]]:
   if not (-3410<=b[0] and b[0]+b[2]<=-2960 and 3174<=b[1] and b[1]+b[3]<=4350):slide_outside.append([a,b])
 e['sliding_doors']['tested_positions_per_leaf']=559;e['sliding_doors']['outside_body_hits']=slide_outside
 if slide_outside:hard.append('移门轨迹超出柜体')
 operation={**g.OPS,'shoe_operator':[-3380,1674,900,600],'shallow_south_operator':[-2960,3174,600,588],'shallow_north_operator':[-2960,3762,600,588]}
 e['family_operation']={k:{'fixed_hits':[n for n,p in solid.items() if n not in ['shoe','study_shallow'] and g.collision(g.rectpoly(b),p)],'open_door_hits':[n for n in fm if any(g.collision(g.rectpoly(b),p) for p in [fm[n][90],*h[n][90]])]} for k,b in operation.items() if k.startswith(('shoe_','shallow_'))}
 routes=[]
 for rn,points in g.D['route_candidates'].items():
  for st in e['dining_states']:
   seats=st['seats'];state=st['state'];pulled=([n for n in g.F if n.startswith(f'chair{seats}_')] if state=='全部拉出' else [state.split(':')[1]] if state.startswith('单椅:') else [])
   obstacles=g.active(seats,pulled);obstacles.update({k:g.rectpoly(b) for k,b in g.W.items()});obstacles.update(jambs())
   for n,v in g.DOORS.items():
    obstacles[n]=g.rectpoly(v['open_box'])
    for i,p in enumerate(h[n][90]):obstacles[n+'_handle_'+str(i)]=p
   for shoestate in ['关闭','全开']:
    for i,frames in enumerate(s):
     for j,p in enumerate(frames[90 if shoestate=='全开' else 0]):obstacles[f'shoe_leaf_{i}_{j}']=p
    checks={}
    for reserve in [0,10]:
     sweeps=[g.rectpoly([b[0]-reserve,b[1]-reserve,b[2]+reserve*2,b[3]+reserve*2]) for b in g.route_sweeps(points)]
     checks[str(reserve)]=sorted(n for n,p in obstacles.items() if any(g.collision(p,t) for t in sweeps))
    overlaps=sorted(n for n,b in operation.items() if any(g.collision(g.rectpoly(b),g.rectpoly(t)) for t in g.route_sweeps(points)))
    routes.append({'route':rn,'seats':seats,'state':state,'shoe_state':shoestate,'door_state':'相关房门90°固定；含双侧50mm把手及门洞两端45mm门套假设','points':points,'width_mm':600,'solid_hits':checks['0'],'reserve_10mm_hits':checks['10'],'service_overlaps':overlaps,'status':'实体受阻' if checks['0'] else '名义可达但余量不足' if checks['10'] else '概念扫掠可达；操作须错时；五金条件待核','scope':'从入户外侧起算，至目标室内；600方篮不旋转，额外10mm每侧敏感性检查'})
 e['basket_routes']=routes
 e['shoe_capacity']={'net_width_mm':864,'effective_depth_mm':330,'layers':8,'template_mm':[240,330,180],'pairs_per_layer':3,'theoretical_pairs':24,'lower_clear_layer_height_mm':(800-4*18)/3,'upper_clear_layer_height_mm':(1100-6*18)/5,'scenarios':[{'name':'标准240×330×180','pairs':24},{'name':'宽鞋280×330×180','pairs':24},{'name':'宽鞋300×330×180','pairs':16},{'name':'长鞋240×350×180','pairs':None,'note':'350深模板不能按水平放置适配330深柜；待实鞋试放，不保证容量'},{'name':'一组下层拆板为双层高靴位','pairs':21,'note':'靴高须≤503mm；3双靴占原两层，非任意长靴保证'},{'name':'鞋盒300×330×220','pairs':6,'note':'仅下部3层×2盒；上部198.4mm层高不容220高盒，需重新调层'}]}
 e['r104_metrics']={'shoe_shallow_gap_mm':50,'shoe_full_main_leaf_gap_mm':87.5,'shoe_main_handle_gap_mm':37.5,'after_10mm_reserve_mm':27.5,'hall_reclaimed_mm':350,'family_intrusion_mm':280,'infill_mm':400,'returns_sum_mm':1010,'shallow_length_reduction_mm':224}
 e['limitations']=['R10.4二维与三维已同步；渲染尚未生成。','所有通行结论仅适用于明确门、餐椅、鞋柜状态；设备操作及取物须错时。','主卧A门50mm把手假设在接近全开时与原墙相交；需实际五金及限位复核，不认定全开安装通过。','短墙可改性、门框固定、线路及柜背构造需现场核实。','原结构、燃气、岛槽重力排水、唯一淋浴及设备安装条件保留。']
 report['status']='二维方案已生成；实体检查与条件项分列，非施工定稿'
 return report

if __name__=='__main__':
 r=validate();g.dump(g.ROOT/'reports/verification_2d.json',r)
 print(json.dumps({'hard_errors':r['hard_errors'],'hardware':r['evidence']['room_handle_hits_site_review'],'family_ops':r['evidence']['family_operation'],'routes_normal':[v for v in r['evidence']['basket_routes'] if v['state']=='正常' and v['seats']==4 and v['shoe_state']=='关闭']},ensure_ascii=False,indent=2))

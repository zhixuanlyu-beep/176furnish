# -*- coding: utf-8 -*-
"""Standalone R10.5 2D publisher. Python standard library only. Never invokes Blender."""
import csv, hashlib, html, itertools, json, math, sys
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'data/layout.json').read_text())
F=D['furniture']; W=D['walls']; DOORS=D['doors']
from projection import load_snapshot
PROJECTION=None
LABELS={'Dining_4':'四人就座组','Dining_6':'六人替代组','Bedroom_A':'主卧 A','Bedroom_B':'卧室 B','Bedroom_D':'卧室 D','Bath_A':'主卫·无淋浴','Bath_Public':'客卫·唯一淋浴','Study':'家庭厅','Hall':'玄关／走道','Kitchen':'厨房','Living':'客厅','C_Prep_Dining':'餐区','Balcony_A':'阳台 A','Balcony_B':'洗烘阳台','bedA':'主卧床','bedB':'B床','bedD':'D床','wardrobeA':'原主卧衣柜','wardrobeB':'B衣柜','wardrobeD':'D衣柜','entry_wardrobe':'入口衣柜','sofa':'沙发','screen':'升降幕布','desk':'书桌','study_chair':'书椅','study_storage':'大件柜','study_shallow':'浅柜','shoe':'鞋柜','fridge':'冰箱','tower':'电器高柜','coffee':'咖啡柜','island':'岛台','table4':'四人桌','table6':'六人桌','hob':'灶台','prep':'备菜柜','sink':'主槽柜','Bath_A_basin':'主卫洗手盆','Bath_A_wc':'主卫马桶','Bath_Public_basin':'客卫洗手盆','Bath_Public_wc':'客卫马桶','shower_public':'客卫淋浴','laundry':'洗烘','side_table':'边几','lounge_chair':'单椅','floor_lamp':'落地灯','A_door_leaf':'主卧门','master_bath_door_leaf':'主卫门','bath_door_leaf':'客卫门','entry_leaf':'入户门','balconyB_door_leaf':'洗烘阳台门','combi_steam_oven':'蒸烤一体机','built_in_microwave':'嵌入式微波炉','robot_station':'基站预留','coffee_machine':'咖啡机','grinder':'磨豆机','coffee_landing':'放盘区','island_sink_recess':'岛槽','dishwasher':'洗碗机','purifier':'净水预留'}
changed={'bedA','entry_wardrobe','Bath_A_wc','Bath_A_basin','island','table4','table6','fridge','tower','coffee'}
C={'ink':'#233e38','green':'#34735e','light':'#e0e9df','orange':'#b36b36','red':'#b6473b','blue':'#467896','paper':'#fbfaf5'}
LABELS.update(child_desk='儿童书桌',child_chair='儿童书椅',family_reading_chair='阅读单椅',family_side_table='阅读边几',A_bedside_west='床头置物',A_bedside_east='床头置物',D_bedside='客房置物',Bedroom_B='儿童房 B',Bedroom_D='客房 D')
def name(n):return LABELS.get(n, '餐椅 '+n.split('_')[-1] if n.startswith('chair') else n)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def esc(s):return html.escape(str(s),quote=True)
def fmt(v):return f'{v:g}' if isinstance(v,(float,int)) else str(v)
def area(b):return b[2]*b[3]/1e6
def rectpoly(b):x,y,w,h=b;return [(x,y),(x+w,y),(x+w,y+h),(x,y+h)]
def rotate(p,origin,deg):
 a=math.radians(deg);x,y=p[0]-origin[0],p[1]-origin[1]
 return (origin[0]+x*math.cos(a)-y*math.sin(a),origin[1]+x*math.sin(a)+y*math.cos(a))
def poly(n,f):
 p=rectpoly(f['box']);b=f['box'];angle=f.get('rotation_degrees',0)
 return [rotate(v,(b[0]+b[2]/2,b[1]+b[3]/2),angle) for v in p]
def collision(a,b,tol=1):
 for p in [a,b]:
  for u,v in zip(p,p[1:]+p[:1]):
   nx,ny=-(v[1]-u[1]),v[0]-u[0];l=math.hypot(nx,ny)
   if l<1e-8:continue
   ax=[(x*nx+y*ny)/l for x,y in a];bx=[(x*nx+y*ny)/l for x,y in b]
   if min(max(ax),max(bx))-max(min(ax),min(bx))<=tol:return False
 return True

def door_motion(v):
 if v.get('kind')=='sliding':
  cb,ob=v['closed_box'],v['open_box']
  return (cb[0],cb[1]),0,[rectpoly([cb[0]+(ob[0]-cb[0])*i/90,cb[1]+(ob[1]-cb[1])*i/90,*cb[2:]]) for i in range(91)]
 cb,ob=v['closed_box'],v['open_box'];cc=(cb[0]+cb[2]/2,cb[1]+cb[3]/2);oc=(ob[0]+ob[2]/2,ob[1]+ob[3]/2)
 candidates=[]
 for s in [1,-1]:
  # o = p + R(c-p), R = quarter turn s
  dx,dy=oc[0]+s*cc[1],oc[1]-s*cc[0]
  p=((dx-s*dy)/2,(s*dx+dy)/2)
  candidates.append((min(math.dist(p,q) for q in rectpoly(cb)),p,s))
 _,p,s=min(candidates)
 return p,s,[ [rotate(q,p,s*i) for q in rectpoly(cb)] for i in range(91)]

def active(seats=4,pulled=()):
 out={}
 for n,f in F.items():
  if f.get('room')==f'Dining_{10-seats}' or n=='screen':continue
  p=poly(n,f)
  if n in pulled:
   dy=500 if f.get('facing')=='south' else -500
   p=[(x,y+dy) for x,y in p]
  out[n]=p
 return out

def operation_boxes():
 r={}
 for k,opening,oper in [('fridge',600,600),('tower',550,600),('coffee',500,600)]:
  x,y,w,h=F[k]['box'];front=y+h
  r[k+'_open']=[x,front,w,opening];r[k+'_operator']=[x,front+opening,w,oper]
 x,y,w,h=F['tower']['box'];r['microwave_open']=[x,y+h,w,520];r['microwave_hot_food']=[x,y+h+520,w,600]
 r.update(dishwasher_open=[2600,1474,600,650],dishwasher_operator=[2600,874,600,600],robot_approach=D['appliances']['robot_station']['approach'],island_operator=[3300,-225,600,600],wardrobe_drawer=[1980,7387,800,450],wardrobe_operator=[-420,6837,3200,600],master_wc_operator=[-380,8600,600,600],master_basin_operator=[530,8900,700,600],public_changing=[-680,1400,700,400])
 r['public_changing']=D['use_zones']['public_changing']['box']
 return r
OPS=operation_boxes()

def route_sweeps(points):
 return [[min(a[0],b[0])-300,min(a[1],b[1])-300,abs(a[0]-b[0])+600,abs(a[1]-b[1])+600] for a,b in zip(points,points[1:])]

def validate():
 hard=[];evidence={};states=[]
 expected={'island':[2300,-975,1600,750],'bedA':[3720,7577,1800,2000],'entry_wardrobe':[-420,7837,3200,600],'coffee':[100,-2998,1800,600],'tower':[1900,-2998,600,600],'fridge':[2500,-2998,975,750]}
 for n,b in expected.items():
  if max(abs(x-y) for x,y in zip(F[n]['box'],b))>1:hard.append(n+' 尺寸与确认计划不一致')
 for seats in [4,6]:
  chairs=[n for n in F if n.startswith(f'chair{seats}_')]
  for state,pulled in [('正常',[]),*[(f'单椅:{n}',[n]) for n in chairs],('全部拉出',chairs)]:
   shapes=active(seats,pulled);hits=[];opening=[];operators=[]
   for n in chairs:
    for k,p in shapes.items():
     if k==n or k.startswith(('chair','table')):continue
     if collision(shapes[n],p):hits.append([n,k])
    for k,b in W.items():
     if collision(shapes[n],rectpoly(b)):hits.append([n,k])
    for k,b in OPS.items():
     if not k.startswith(('fridge','tower','coffee','microwave','dishwasher','robot','island')):continue
     if collision(shapes[n],rectpoly(b)):(opening if k.endswith('_open') else operators).append([n,k])
   if hits or opening:hard.append(f'{seats}人/{state} 餐椅实体或设备开启冲突')
   states.append({'seats':seats,'state':state,'physical_hits':hits,'equipment_opening_hits':opening,'time_shared_operator_overlaps':operators,'north_corridor_mm':600 if any(F[n].get('facing')=='south' for n in pulled) else 1100})
 # Changed floor solids against all walls/solids; chair/table underlap is intentional 2D projection.
 solids=active();new_collisions=[]
 for n in changed:
  if n not in solids:continue
  for k,p in [*solids.items(),*[(k,rectpoly(v)) for k,v in W.items()]]:
   if n==k or (n.startswith('table') and k.startswith('chair')):continue
   if collision(solids[n],p):new_collisions.append([n,k])
 if new_collisions:hard.append('变动家具与固定实体相交')
 evidence['changed_floor_solids']=new_collisions
 evidence['dining_states']=states
 # Full door motion at 1 degree increments; surrounding frame contact is reported separately.
 motions={};doorwalls={}
 for n,v in DOORS.items():
  pivot,sgn,frames=door_motion(v);hits={};wallhits={}
  for angle,p in enumerate(frames):
   for k,f in F.items():
    if f.get('room')=='Dining_6' or k=='screen':continue
    if collision(p,poly(k,f)):hits.setdefault(k,[]).append(angle)
   for k,b in W.items():
    if collision(p,rectpoly(b)):wallhits.setdefault(k,[]).append(angle)
  motions[n]={'pivot':pivot,'direction':sgn,'furniture_hits':{k:[min(v),max(v)] for k,v in hits.items()}}
  doorwalls[n]={k:[min(v),max(v)] for k,v in wallhits.items()}
  if n in ['A_door_leaf','master_bath_door_leaf'] and hits:hard.append(name(n)+' 与家具运动冲突')
 evidence['doors_0_to_90_degrees']=motions;evidence['door_frame_contacts_to_review']=doorwalls
 # 8 wardrobe leaves, each 400 wide, plus 450 drawer and 600 standing band.
 wardrobe=[]
 for module in range(4):
  for side in [0,1]:
   left=-420+module*800+side*400;pivot=(left if side==0 else left+400,7837)
   closed=rectpoly([left,7837,400,18]);sgn=-1 if side==0 else 1
   hits=set()
   for deg in range(91):
    p=[rotate(q,pivot,sgn*deg) for q in closed]
    for n,f in F.items():
     if n=='entry_wardrobe' or f.get('room')=='Dining_6' or n=='screen':continue
     if collision(p,poly(n,f)):hits.add(n)
    for n,b in W.items():
     if collision(p,rectpoly(b)):hits.add(n)
   wardrobe.append({'module':module+1,'leaf':side+1,'hits':sorted(hits)})
 if any(v['hits'] for v in wardrobe):hard.append('衣柜门运动冲突')
 evidence['wardrobe_leaves']=wardrobe
 service_hits={}
 for key in ['wardrobe_drawer','wardrobe_operator','master_wc_operator','master_basin_operator','robot_approach']:
  hits=[]
  for n,p in solids.items():
   if key.startswith('wardrobe') and n=='entry_wardrobe':continue
   if key.startswith('master_wc') and n=='Bath_A_wc':continue
   if key.startswith('master_basin') and n=='Bath_A_basin':continue
   if collision(rectpoly(OPS[key]),p):hits.append(n)
  service_hits[key]=hits
  if hits:hard.append(key+' 存在实体冲突')
 evidence['new_service_zone_solid_hits']=service_hits
 travel_hits=[]
 for seats in [4,6]:
  shapes=active(seats)
  for n,f in F.items():
   if not n.startswith(f'chair{seats}_'):continue
   x,y,w,h=f['box'];travel=[x,y if f['facing']=='south' else y-500,w,h+500]
   for k,p in [*shapes.items(),*[(k,rectpoly(b)) for k,b in W.items()]]:
    if k==n or k.startswith(('chair','table')):continue
    if collision(rectpoly(travel),p):travel_hits.append([n,k])
   for k,b in OPS.items():
    if k.endswith('_open') and k.startswith(('fridge','tower','coffee','microwave','dishwasher')) and collision(rectpoly(travel),rectpoly(b)):travel_hits.append([n,k])
 if travel_hits:hard.append('拉椅连续路径出现实体／开启冲突')
 evidence['chair_continuous_travel_hits']=travel_hits
 equipment_solid_hits={}
 for n,b in OPS.items():
  if not n.endswith('_open'):continue
  equipment_solid_hits[n]=[k for k,p in active().items() if not k.startswith('table') and collision(rectpoly(b),p)]
 if any(equipment_solid_hits.values()):hard.append('设备开启与固定实体冲突')
 evidence['equipment_open_to_solids']=equipment_solid_hits

 evidence['public_bath']={'area_m2':sum(area(b) for b in D['rooms']['Bath_Public']),'shower_mm':F['shower_public']['box'][2:],'dry_changing_placeholder_mm':OPS['public_changing'][2:],'status':'西侧淋浴、中央换衣，单人顺序共享；具体尺寸与条件见逐室复算'}
 for n in ['Bath_A_wc','Bath_A_basin']:
  b=F[n]['box'];r=D['rooms']['Bath_A'][0]
  if not (r[0]<=b[0] and r[1]<=b[1] and b[0]+b[2]<=r[0]+r[2] and b[1]+b[3]<=r[1]+r[3]):hard.append(n+' 超出主卫')
 evidence['metrics']={'island_length_mm':1600,'table_translation_mm':600,'bath_before_m2':3.757,'bath_after_m2':2.38,'bath_released_m2':1.377,'wardrobe_external_mm':3200,'wardrobe_internal_sum_mm':4*(800-36),'hanging_module_width_sum_mm':3*(800-36),'nominal_hanging_rail_length_mm':5*(800-36),'wardrobe_to_bed_mm':940,'bed_east_gap_mm':1100,'entrance_to_wardrobe_mm':1570,'fridge_to_island_nominal_mm':1273,'fridge_open_plus_operator_remaining_mm':73,'six_chair_to_fridge_horizontal_mm':250,'microwave_counter_released_mm':520}
 evidence['limitations']=['600mm衣篮原完整路线仍受阻，不能作为通过项。','冰箱门600mm与站人600mm算例合计1200mm，前方仅余73mm，不能再作为旁侧穿行宽度。','全部拉椅与咖啡／电器人员操作重叠，需错时；北侧600mm只是名义通道。','基站进出区与人员、携篮活动区有重叠，清扫回充与备菜、携篮错时。','客卫仅850×850mm淋浴占位且换衣空间紧凑，舒适性及真实设备型号待核。','三维碰撞、人体工学、实际门五金、结构及管线施工不在此次二维通过范围。']
 return {'revision':'R10.5','status':'二维几何检查完成，含使用限制和现场待核','hard_errors':sorted(set(hard)),'evidence':evidence}

REPORT=validate()
# All drawings use fixed canvas and one world-coordinate transform; dimension data are machine-readable.
class Drawing:
 def __init__(self,title,subtitle='单位：mm · 概念尺寸，非现场实测／下单尺寸',width=1400,height=1050):
  self.w=width;self.h=height;self.p=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img"><title>{esc(title)}</title><rect width="100%" height="100%" fill="{C["paper"]}"/><g font-family="PingFang SC, Microsoft YaHei, sans-serif">',self.text(42,48,'R10.5  /  '+title,27,C['ink']),self.text(42,79,subtitle,15,C['orange'])]
 def text(self,x,y,s,size=16,color=None,anchor='start'):
  return f'<text x="{x:g}" y="{y:g}" font-size="{size}" fill="{color or C["ink"]}" text-anchor="{anchor}">{esc(s)}</text>'
 def box(self,b,fill='none',stroke=None,dash=False,attrs=''):
  x,y,w,h=b;return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{fill}" stroke="{stroke or C["ink"]}" stroke-width="1.4"'+(' stroke-dasharray="6 4"' if dash else '')+f' {attrs}/>'
 def panel(self,bounds,frame):
  x,y,w,h=bounds;u,v,fw,fh=frame;s=min(fw/w,fh/h);ox=u+(fw-w*s)/2;oy=v+(fh-h*s)/2
  def point(p):return (ox+(p[0]-x)*s,oy+(y+h-p[1])*s)
  def r(b):
   q=point((b[0],b[1]+b[3]));return [*q,b[2]*s,b[3]*s]
  return point,r,s
 def plan(self,bounds,frame,seats=4,pulled=(),ops=False,old=False,route=None,labels=True,roomlabels=False):
  global PROJECTION
  if PROJECTION is None:PROJECTION=load_snapshot()
  pt,r,s=self.panel(bounds,frame);src=D
  cid='panel_'+str(len(self.p));self.p.append(f'<defs><clipPath id="{cid}">'+self.box(frame,'white','none')+'</clipPath></defs>'+f'<g clip-path="url(#{cid})" data-plan="true" data-world="{esc(json.dumps(bounds))}" data-frame="{esc(json.dumps(frame))}" data-pulled="{esc(json.dumps(list(pulled)))}">')
  for n,b in src['walls'].items():self.p.append(self.box(r(b),'#64736d','none',attrs=f'data-wall="{n}" data-box="{",".join(map(fmt,b))}"'))
  for n,o in src['openings'].items():
   if o['kind'] in ['window','bay_east','bay_south']:
    self.p.append(self.box(r(o['box']),'#dceaf0',C['blue']))
  for n,f in src['furniture'].items():
   if f.get('room') in ['Candidate_Equipment',f'Dining_{10-seats}'] or n=='screen':continue
   p=poly(n,f)
   if n in pulled:p=[(x,y+(500 if f.get('facing')=='south' else -500)) for x,y in p]
   if max(x for x,y in p)<bounds[0] or min(x for x,y in p)>bounds[0]+bounds[2] or max(y for x,y in p)<bounds[1] or min(y for x,y in p)>bounds[1]+bounds[3]:continue
   pts=[pt(q) for q in p];fill='#e7dfd2' if 'chair' in n or f['kind']=='table' else C['light'];stroke=C['orange'] if n in changed and not old else C['green']
   self.p.append(f'<polygon points="'+ ' '.join(f'{x:g},{y:g}' for x,y in pts)+f'" fill="{fill}" stroke="{stroke}" stroke-width="1.4" data-object="{n}" data-box="{",".join(map(fmt,f["box"]))}"/>')
   for component in sorted((v for v in PROJECTION['components'] if v['owner']==n),key=lambda v:(v['z_max_mm'],v['name'])):
    if not any(key in component['name'] for key in ['mattress','headboard','pillow','seat','back','front','door','drawer','pull','rim','bowl','tank','port']):continue
    shift=500 if f.get('facing')=='south' else -500
    cp=[pt((x,y+(shift if n in pulled else 0))) for x,y in component['polygon_mm']]
    self.p.append('<polygon points="'+' '.join(f'{x:g},{y:g}' for x,y in cp)+f'" fill="none" stroke="#758c83" stroke-width="0.7" data-component="{esc(component["name"])}"/>')
   if labels and not n.startswith('chair'):
    x=sum(x for x,y in pts)/4;y=sum(y for x,y in pts)/4
    label=name(n)
    if not old and n in changed:label+=' '+str(round(f['box'][2] if n!='bedA' else f['box'][3]))
    if f['box'][2]*s>32:self.p.append(self.text(x,y,label,11 if s<.09 else 14,anchor='middle'))
  for n,v in src['doors'].items():
   b=v['closed_box']
   if b[0]<bounds[0]-900 or b[0]>bounds[0]+bounds[2]+900 or b[1]<bounds[1]-900 or b[1]>bounds[1]+bounds[3]+900:continue
   self.p.append(self.box(r(b),'#cdbb9e',C['orange']))
   if not ops:continue
   self.p.append(self.box(r(v['open_box']),'none',C['orange'],True))
   p,sgn,frames=door_motion(v);tip=max(rectpoly(b),key=lambda q:math.dist(q,p));arc=[pt(rotate(tip,p,sgn*a)) for a in range(0,91,3)]
   self.p.append('<polyline points="'+' '.join(f'{x:g},{y:g}' for x,y in arc)+f'" fill="none" stroke="{C["orange"]}" stroke-dasharray="3 4"/>')
  if not old:
   for n,b in D['parts'].items():
    if n.startswith(('cup','AC')):continue
    if b[0]<bounds[0] or b[0]>bounds[0]+bounds[2] or b[1]<bounds[1] or b[1]>bounds[1]+bounds[3]:continue
    self.p.append(self.box(r(b),'#d7e6ea',C['blue']))
    if s>.13 and n in ['coffee_machine','grinder','coffee_landing']:
     x,y=pt((b[0]+b[2]/2,b[1]+b[3]/2));self.p.append(self.text(x,y,name(n),11,anchor='middle'))
   if ops and s>.1 and bounds[1]>5000:
    for m in range(4):
     for leaf in range(2):
      b=[-420+m*800+leaf*400,7437,18,400] if leaf==0 else [-420+m*800+(leaf+1)*400-18,7437,18,400]
      self.p.append(self.box(r(b),'none',C['orange'],True))
   if ops:
    for n,b in OPS.items():
     if b[0]<bounds[0] or b[0]>bounds[0]+bounds[2] or b[1]<bounds[1] or b[1]>bounds[1]+bounds[3]:continue
     self.p.append(self.box(r(b),'none',C['red'] if n.endswith('_open') else C['blue'],True))
  if route:
   for b in route_sweeps(route):self.p.append(self.box(r(b),'#46789618',C['blue'],True))
   points=[pt(q) for q in route];self.p.append('<polyline points="'+' '.join(f'{x:g},{y:g}' for x,y in points)+f'" stroke="{C["blue"]}" stroke-width="3" fill="none"/>')
  if roomlabels:
   for n,rs in src['rooms'].items():
    b=rs[0];x,y=pt((b[0]+b[2]*.5,b[1]+b[3]*.28));self.p.append(self.text(x,y,name(n),15,C['orange'],anchor='middle'))
  self.p.append('</g>')
  return pt,r,s
 def dim(self,a,b,label,offset=0):
  # Screen coordinates; extension ticks and a value label remain legible at any world scale.
  x1,y1=a;x2,y2=b
  if abs(y2-y1)<abs(x2-x1):
   y=(y1+y2)/2+offset;self.p.append(f'<path d="M{x1},{y1} V{y+5} M{x2},{y2} V{y+5} M{x1},{y} H{x2}" fill="none" stroke="{C["blue"]}"/>');self.p.append(self.text((x1+x2)/2,y-6,label,14,C['blue'],'middle'))
  else:
   x=(x1+x2)/2+offset;self.p.append(f'<path d="M{x1},{y1} H{x+5} M{x2},{y2} H{x+5} M{x},{y1} V{y2}" fill="none" stroke="{C["blue"]}"/>');self.p.append(self.text(x+7,(y1+y2)/2,label,14,C['blue']))
 def notes(self,lines,y=855):
  self.p.append(self.box([32,y-24,self.w-64,len(lines)*29+28],'#eef1e8','none'))
  for i,t in enumerate(lines):self.p.append(self.text(48,y+i*29,t,16))
 def save(self,n):
  self.p.extend([self.text(42,self.h-20,'R10.5；三维模型已同步；本轮未生成渲染图。红色／虚线表示开启或使用范围，不能视为实体。',12,C['orange']),'</g></svg>'])
  p=ROOT/'drawings/svg'/n;p.write_text(''.join(self.p),encoding='utf-8');return p

def drawings():
 items=[]
 def save(q,n,title):q.save(n);items.append((n,title))
 q=Drawing('全屋家具与门窗',height=1250)
 q.plan([-4700,-7100,11800,17600],[30,100,1020,1090],roomlabels=True)
 for i,t in enumerate(['01  鞋柜 900×400×2400','02  浅柜缩至1176，双移门','03  原短墙改为柜墙概念','04  家庭厅门1500保持','05  完整衣篮路线见专项图','06  A门五金待核／暂停定稿','07  其他已确认布局保持','08  三维模型已同步R10.5','图例','绿色：家具／柜体','橙色：本轮改动／门扇','蓝色：设备／水电预留']):q.p.append(q.text(1060,160+i*42,t,16))
 save(q,'01-furniture.svg','全屋家具与门窗')
 q=Drawing('餐区与南墙柜列')
 pt,_,_=q.plan([-1400,-3300,6800,6200],[40,110,1050,690],ops=False)
 q.dim(pt((2300,-225)),pt((3900,-225)),'1600',-25)
 q.dim(pt((3475,-2248)),pt((3475,-975)),'1273',34)
 for i,t in enumerate(['厨房在上方','岛台：1600×750','岛台控制体，模块待选','四人桌：1600×750','咖啡柜：1800×600','电器高柜：600×600','冰箱：975×750','柜列西端距边界100']):q.p.append(q.text(1090,170+i*43,t,15))
 q.notes(['桌椅同步向左600mm，岛槽原位置保留；南墙顺序为咖啡柜—电器高柜—冰箱。','冰箱至岛台名义间距1273mm；开启600＋站人600后仅余73mm，不是可穿行通道。','六人状态最右餐椅至冰箱水平间隔250mm；实体和操作状态另见核验图。'])
 save(q,'02-dining.svg','岛台与餐区总图')
 for seats in [4,6]:
  q=Drawing(f'{seats}人就座与拉椅状态')
  for i,(title,pulled) in enumerate([('正常就座',[]),('全部拉出500mm',[n for n in F if n.startswith(f'chair{seats}_')])]):
   q.p.append(q.text(45+i*690,125,title,20));q.plan([-150,-3100,4300,4500],[35+i*690,150,640,625],seats,pulled,True)
  q.notes(['蓝色虚线：人员操作；红色虚线：电器／抽屉开启。桌椅投影局部重叠为膝部关系，不代替三维净空。','正常状态北侧名义通道1100mm；北椅全部拉出后600mm。单椅逐个检查记录见核验报告。','全部拉出与南墙设备人员操作存在重叠，必须错时；实体与设备开启碰撞单独报告。'])
  save(q,f'03-seating-{seats}.svg',f'{seats}人正常／全部拉出')
 q=Drawing('南墙立面与设备高度')
 s=.30;ox=90;base=800
 for n in ['coffee','tower','fridge']:
  f=F[n];x=f['box'][0];width=f['box'][2];h=f['height'];q.p.append(q.box([ox+x*s,base-h*s,width*s,h*s],C['light'],C['green']));q.p.append(q.text(ox+(x+width/2)*s,base+28,name(n)+' '+str(width),17,anchor='middle'))
 for n,a in D['appliances'].items():
  if n not in ['combi_steam_oven','built_in_microwave']:continue
  x=a['box'][0];q.p.append(q.box([ox+(x+12)*s,base-(a['z']+a['height'])*s,576*s,a['height']*s],'#d4dce0',C['blue']));q.p.append(q.text(ox+(x+300)*s,base-(a['z']+a['height']/2)*s,name(n),15,anchor='middle'))
 for z,t in [(650,'蒸烤底650'),(1100,'蒸烤顶1100'),(1200,'微波底1200'),(1580,'微波顶1580')]:q.p.append(q.text(1150,base-z*s,t,15,C['blue']))
 q.notes(['高柜2200高；蒸烤450高、底650；微波380高、底1200。上下均为概念机体占位。','两设备之间100mm区域用于承托／间隔概念表达，不是厂家确认的散热构造。','咖啡机与磨豆机移至左侧咖啡柜；右侧600mm台面留作放盘，原台面微波炉已取消。'])
 save(q,'04-cabinet-elevation.svg','南墙柜体立面／设备高度')
 q=Drawing('主卧缩卫与入口衣帽区')
 pt,_,_=q.plan([-650,6050,7550,4100],[35,125,1320,665],ops=True)
 q.dim(pt((-420,9957)),pt((1280,9957)),'1700',-18)
 q.dim(pt((1280,8557)),pt((1280,9957)),'1400',22)
 q.dim(pt((-420,7837)),pt((2780,7837)),'3200',95)
 q.dim(pt((2780,7750)),pt((3720,7750)),'940',0)
 q.dim(pt((5520,8000)),pt((6620,8000)),'1100',0)
 q.notes(['主卫：1700×1400＝2.38㎡；南墙北移810。门洞北移，门向内贴南墙开启。','衣柜：3200×600×2400；床向东500。柜端至床侧940，床东侧1100，入口至柜前1570。','蓝线含马桶／洗手盆操作区；衣柜门400、抽屉450均独立核验，净空不代表现场尺寸。'])
 save(q,'05-master-suite.svg','主卧与主卫详图')
 q=Drawing('入口衣柜立面与容量')
 scale=.28;ox=110;base=800
 for i,t in enumerate(D['wardrobe_modules']):
  x=ox+i*800*scale;q.p.append(q.box([x,base-2400*scale,800*scale,2400*scale],C['light'],C['green']));q.p.append(q.text(x+400*scale,165,t,18,anchor='middle'))
  heights=[1050,1950] if i<2 else [1950] if i==2 else [350,650,950,1300,1700,2000]
  for z in heights:q.p.append(f'<line x1="{x+12}" y1="{base-z*scale}" x2="{x+800*scale-12}" y2="{base-z*scale}" stroke="{C["green"]}"/>')
  q.p.append(q.text(x+400*scale,830,'800外宽／764净宽',15,anchor='middle'))
 q.notes(['四模块、18mm侧板：柜内净宽合计3056mm；不包含门板／背板／安装误差后的现场修正。','三个挂衣模块净宽合计2292mm；两组双层短衣＋一组长衣，概念挂杆总长3820mm。','第四模块为抽屉／层板；柜门每模块两扇、每扇400mm；衣帽区属于开放过道。'],875)
 save(q,'07-wardrobe.svg','衣柜立面与容量')
 q=Drawing('Cleanup岛台研究与岛桌靠接 · 非成套定稿')
 pt,r,s=q.plan([300,-1450,3900,1900],[45,130,1000,650],ops=False,labels=False)
 q.dim(pt((2300,-225)),pt((3900,-225)),'1600控制长度',-30)
 for i,t in enumerate(['STEDIA优先核查','当前非官方模块','岛台初选高850','餐桌独立高750','高差100','岛台基站孔取消','北京渠道有名单','供货安装保修待核']):q.p.append(q.text(1070,175+i*54,t,16))
 q.notes(['1600×750仅保留空间边界，不把自定义双800柜标成Cleanup；官方模块安装表未取得，暂无合格组合。','四人日常、六人替代桌均独立承重并靠接；侧封板、踢脚、防水与色调接口待厂家书面方案。','机器人改查洗烘阳台；600×600候选控制区并非机型净空，装卸检修重叠见基站迁移表。'])
 save(q,'08-island-robot.svg','Cleanup岛台研究与独立岛桌连接')
 q=Drawing('电器开启与人员操作范围')
 q.plan([-100,-3150,4250,4500],[40,115,1000,690],ops=True)
 for i,t in enumerate(['红：设备开启','蓝：人员操作','冰箱开启算例600','蒸烤开门算例550','微波开门算例520','咖啡抽屉算例500','人员站位算例600','各机型待安装图核定']):q.p.append(q.text(1060,180+i*48,t,16))
 q.notes(['蒸烤与微波在同一高柜上下叠放，平面操作区重叠；按单设备使用状态绘制，不宣称同时可用。','设备机体、门扇和人员分别核验；热食端取高度需按使用者身高放样。','咖啡区、冰箱和岛台相关电源随新版位置更新；无已确认负荷及厂家图，不作最终回路定案。'])
 save(q,'09-appliance-clearance.svg','电器开启与操作范围')
 q=Drawing('水电点位与连接条件')
 q.plan([-4700,-7100,11800,17600],[30,110,820,700],labels=False)
 pt,r,s=q.panel([-4700,-7100,11800,17600],[30,110,820,700])
 for row in services():
  x,y=pt((row['x'],row['y']));q.p.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{C["blue"]}"/>');q.p.append(q.text(x+8,y-5,row['id'],11,C['blue']))
 for i,t in enumerate(['S01 蒸烤／微波电源：高柜邻侧可达','S02 冰箱电源：随柜列右移','S03 咖啡机／磨豆机：左侧台面','W01 基站：独立关阀／检修预留','W02 岛槽：位置不变，排水未成立','W03 主卫盆／马桶：位置重排待核','X01 原淋浴管口：待核封堵','L01 衣帽照明：原位置保持','L02 鞋柜格顶照明：驱动可检修','不把未知接点连接成“已可施工”管线']):q.p.append(q.text(855,150+i*55,t,15))
 q.notes(['水电点位坐标见表；高度、回路、管径、坡度、排污立管和合法接点均按现场及设备安装图确认。','原空调、洗烘、燃气和结构核验记录保留于现场核验表；本轮不扩大拆改范围。'])
 save(q,'11-services.svg','新版水电概念点位')
 q=Drawing('客卫唯一淋浴与使用限制')
 q.plan([-1000,1100,2850,1850],[70,130,1050,640],ops=True)
 q.notes(['客卫边界2380×1354保持；西侧900×1354淋浴，东侧南端名义700入口。','中央800×600换衣占位，单人顺序共享；南侧800门洞，外置上吊门向西停靠。','全家淋浴需错峰；洗澡时其他卧室使用客卫受影响，可等待或借用主卫。检修停用时无第二淋浴。'])
 save(q,'12-public-bath.svg','唯一淋浴与换衣限制')
 return items

def services():
 return D['service_points']

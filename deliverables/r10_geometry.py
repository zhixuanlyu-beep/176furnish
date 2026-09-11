"""Current 2D projections: config organises objects, verified meshes define outlines."""
import base64
import hashlib
import html
import json
import math
from pathlib import Path
from sync_model import Model,REVISION,MODEL,digest,read,mm,footprint,intersect

INK,GREEN,BLUE,AMBER,RED='#233d36','#287361','#427f9a','#ac6537','#b34539'
M=Model()
C=M.c
BASE=read(MODEL/'r10_baseline.json')
SOURCE_TRANSFORM=BASE['SOURCE_TRANSFORM']
WATER_ROUTE,WATER_COLD,WATER_HOT=[BASE[k] for k in ('WATER_ROUTE','WATER_COLD','WATER_HOT')]
WALLS=M.walls
BOXES=M.furniture
OPENINGS={n:dict(o,box=mm(o['box'])) for n,o in C['openings'].items()}
LABELS={'bedA':'A床','bedB':'B床','bedD':'D床','wardrobeA':'A衣柜','wardrobeB':'B衣柜','wardrobeD':'D东墙衣柜','sofa':'沙发','screen':'幕布','desk':'书桌','study_storage':'深柜','study_chair':'书椅','shoe':'鞋柜','fridge':'冰箱','tower':'独立蒸箱／独立烤箱','coffee':'咖啡柜','pantry':'食品柜','island':'岛台','hob':'灶台','prep':'备菜','sink':'主槽柜','laundry':'洗烘条件位','robot_R01':'R01候选','robot_L02':'L02旧候选','coffee_table':'茶几','table4':'四人桌','table6':'六人桌'}
LABELS.update(study_storage='大件柜',study_shallow='浅柜',side_table='边几',lounge_chair='单椅',floor_lamp='落地灯',microwave='微波炉')
TITLES=['全屋家具与门窗','拆改及开放边界','水电点位与概念路由','南墙柜体立面','设备侧视与操作高度','家庭厅、子母门与收纳','四／六人餐区状态','设备开启与人员操作','600mm衣篮路线','空调与补充概念管线','原图标定与实际墙段','AC01局部吊顶概念剖面','岛槽给排水概念剖面','卫浴占位与机器人候选','岛桌连接与膝部高度']
FILES=['01-furniture.svg','02-alterations-review.svg','03-services.svg','04-cabinet-access.svg','05-coffee-sideboard.svg','06-utility-storage.svg','07-island-dining.svg','08-appliance-clearance.svg','09-workflows.svg','10-air-conditioning.svg','11-source-overlay.svg','12-ac01-ceiling-section.svg','13-island-water-section.svg','14-robot-station-review.svg','15-island-table-connection.svg']

def model_digest():return digest(MODEL/'scene_config.json')
def text(x,y,s,size=15,color=INK,anchor='middle'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}">{html.escape(str(s))}</text>'
def rect(x,y,w,h,fill='none',stroke=INK,dash=''):
    return f'<rect x="{x}" y="{y}" width="{max(0,w)}" height="{max(0,h)}" fill="{fill}" stroke="{stroke}" stroke-dasharray="{dash}"/>'
def line(points,color=INK,width=2,dash=''):
    return '<polyline points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}"/>'
def start(title,h=820,w=1150):
    if not title.startswith(REVISION):title=REVISION+' · '+title.replace('R10.1 ','')
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img"><title>{html.escape(title)}</title><g font-family="Microsoft YaHei,sans-serif">',text(w/2,30,title,20)]
def obj(n,b,fill='none',stroke=INK,dash='',attribute='data-object'):
    return f'<g {attribute}="{n}" data-box="{",".join(map(str,b))}">'+rect(*b,fill,stroke,dash)+'</g>'
def project(content,ox=0,oy=0,scale=1):
    return f'<g data-model="{model_digest()}" transform="translate({ox} {oy}) scale({scale})">{content}</g>'
def hull(points):
    pts=sorted(set((round(x,5),round(y,5)) for x,y in points))
    def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    sides=[]
    for seq in (pts,pts[::-1]):
        half=[]
        for p in seq:
            while len(half)>1 and cross(half[-2],half[-1],p)<=0:half.pop()
            half.append(p)
        sides+=half[:-1]
    return sides
def mesh(n,o,axes=(0,1),fill='#dce4d8',stroke=INK,dash=''):
    pts=hull([(v[axes[0]]*1000,-v[axes[1]]*1000) for v in o['vertices']])
    return f'<polygon data-part="{n}" data-axes="{axes[0]},{axes[1]}" points="'+ ' '.join(f'{x},{y}' for x,y in pts)+f'" fill="{fill}" stroke="{stroke}" stroke-dasharray="{dash}"/>'
def architecture(alter=False,overlay=False):
    p=['<g stroke-width="12">']
    for n,b in WALLS.items():p.append(obj(n,b,BLUE if overlay else '#69786c','none',attribute='data-wall'))
    for n,o in M.objects.items():
        if 'Openings' in o['collections'] and not n.endswith('_header'):p.append(mesh(n,o,fill='#dcebf1',stroke=BLUE))
    for n,op in OPENINGS.items():
        p.append(obj(n,op['box'],'none','none' if op['kind'] in ('connected','removed_door') else BLUE,'35 35','data-opening'))
        if op['kind']=='double_glass_door':
            for leaf in op['leaves']:
                key=n+'_'+leaf['id']+'_leaf';o=M.objects[key]
                p.append(mesh(key,o,fill='#dcebf1',stroke=BLUE))
                p.append(obj(key+'_open',footprint(M.snapshot['motion']['90'][key]['bounds']),'none',AMBER,'40 35'))
                hx,hy=leaf['hinge'];a0=0 if leaf['direction']==1 else math.pi
                p.append(line([(1000*(hx+leaf['width']*math.cos(a0+math.radians(t)*leaf['swing_sign'])),-1000*(hy+leaf['width']*math.sin(a0+math.radians(t)*leaf['swing_sign']))) for t in range(91)],AMBER,12,'35 25'))
                for pn,part in M.objects.items():
                    if part['owner']==key:p.append(mesh(pn,part,fill='#45564e'))
        if op['kind'] in ('door','glass_door'):
            key=n+'_leaf';o=M.objects[key];p.append(mesh(key,o,fill='#d8cbb0'))
            # Project actual local corners through animation matrices (Y reflection included).
            from_frames=M.snapshot['motion'];closed=from_frames['1'][key]['matrix'];opened=from_frames['90'][key]['matrix']
            a=from_frames['1'][key]['bounds'];b=from_frames['90'][key]['bounds']
            p.append(obj(key+'_open',footprint(b),'none',AMBER,'40 35'))
            if op['kind']=='door':
                # Hinge equals translation after mesh origin reset in Blender.
                hx,hy=closed[0][3],closed[1][3]
                radius=max(math.hypot(v[0]-hx,v[1]-hy) for v in o['vertices'])
                a0=math.atan2(closed[1][0],closed[0][0]);a1=math.atan2(opened[1][0],opened[0][0])
                if op['box'][3]>op['box'][2]:a0+=math.pi/2;a1+=math.pi/2
                pts=[(1000*(hx+radius*math.cos(a0+(a1-a0)*i/60)),-1000*(hy+radius*math.sin(a0+(a1-a0)*i/60))) for i in range(61)]
                p.append(line(pts,AMBER,12,'35 25'))
    if alter:
        for n,b in C['demolition'].items():
            b=mm(b);p.extend([obj(n,b,'none',RED,'80 50','data-removal'),text(b[0]+b[2]/2,b[1]-80,n,160,RED)])
    return ''.join(p+['</g>'])
def furniture(seats=4,opened=False,whole=True,labels=True):
    p=['<g stroke-width="10">']
    for n,f in C['furniture'].items():
        if f['room']==f'Dining_{10-seats}':continue
        if not whole and f['room'] not in ('Kitchen','C_Prep_Dining',f'Dining_{seats}'):continue
        b=BOXES[n];candidate=f['room']=='Candidate_Equipment';bath=f.get('status')=='assumed_fixture_position'
        p.append(obj(n,b,'none',AMBER if candidate or bath else GREEN,'55 35' if candidate or bath else '',attribute='data-config-object'))
        for pn,o in sorted(M.parts(n).items(),key=lambda x:x[1]['bounds'][2]):
            p.append(mesh(pn,o,fill='none' if candidate or bath else '#dbe1d2',stroke=AMBER if candidate or bath else INK,dash='50 35' if candidate or bath else ''))
        if 'support' in f:
            for pn,o in M.parts(n).items():
                if '_support' in pn or '_beam' in pn:p.append(mesh(pn,o,fill='none',stroke=AMBER,dash='25 20'))
        if 'pull_vector' in f:
            v=f['pull_vector'];pulled=[b[0]+v[0]*1000,b[1]-v[1]*1000,b[2],b[3]]
            sweep=[min(b[0],pulled[0]),min(b[1],pulled[1]),b[2]+abs(v[0]*1000),b[3]+abs(v[1]*1000)]
            p.append(obj(n+'_travel',sweep,'none','#b5b9a7','15 30'))
            p.append(obj(n+'_pulled',pulled,'none',RED,'50 35'))
            p.append(line([(b[0]+b[2]/2,b[1]+b[3]/2),(pulled[0]+b[2]/2,pulled[1]+b[3]/2)],RED,15))
            if f.get('table'):p.append(obj(n+'_knees',footprint(M.knees(n)),'none','#876ca4','20 20'))
        if f.get('door_operation')=='sliding':
            for pn,o in M.parts(n).items():
                if '_front' in pn:
                    p.append(obj(pn+'_open',footprint(M.snapshot['motion']['90'][pn]['bounds']),'none',AMBER,'40 25'))
        if labels and 'pull_vector' not in f:
            label='蒸／烤' if n=='tower' else LABELS.get(n,'卫浴占位' if bath else n)
            if candidate:label+='（未落实）'
            p.append(text(b[0]+b[2]/2,b[1]+b[3]/2,label,135,AMBER if bath or candidate else INK))
    # Equipment outside furniture roots is still measured, never reconstructed from old coordinates.
    for n,o in M.objects.items():
        if o['owner'] or any(c in o['collections'] for c in ('Openings','Doors','Headers_Concept','Clearance_Envelopes','Ceilings')):continue
        if n.startswith(('AC','island_sink','kitchen_sink','dishwasher','coffee_machine','grinder','oven','steam_oven','purifier','hob_glass','desk_','lamp_cable','family_curtain','microwave_power')):
            p.append(mesh(n,o,fill='#cfdee0',stroke=BLUE))
    if opened:
        for n,b in M.services.items():p.append(obj(n,b,'none',AMBER if C['services'][n]['category']=='opening' else GREEN,'55 35'))
    return ''.join(p+['</g>'])
def viewport(content,box,x=30,y=70,w=1090,h=560):
    ident='clip_'+hashlib.sha256(json.dumps([box,x,y,w,h]).encode()).hexdigest()[:12]
    return f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="'+ ' '.join(map(str,box))+f'"><defs><clipPath id="{ident}">'+rect(*box,'white','none')+f'</clipPath></defs><g clip-path="url(#{ident})">'+project(content)+'</g></svg>'
def notes(lines,y=670):return ''.join(text(40,y+i*27,s,15,anchor='start') for i,s in enumerate(lines))
def finish(p):return ''.join(p+['</g></svg>'])
def conclusion():
    m=M.report['metrics']['6']
    return [f"正常就座可使用咖啡、蒸烤；北侧通道 {m['north_route_seated_mm']}mm，全部拉出 {m['north_route_pulled_mm']}mm。",
      f"南椅距咖啡／蒸烤操作区 {m['south_chair_to_coffee_operator_mm']}／{m['south_chair_to_oven_operator_mm']}mm；拉出距抽屉／开门 {m['pulled_to_coffee_drawer_mm']}／{m['pulled_to_oven_open_mm']}mm。",
      '完全拉出临时占用部分人员操作区；先恢复就座位置再携篮，携篮与洗碗装卸、岛槽操作错时。']
def full_sheet(index):
    p=start(TITLES[index-1]);content=architecture(index==2)+furniture(opened=index==3)
    if index in (3,10):content+=water_plan() if index==3 else ac_plan()
    p.append(viewport(content,[-4600,-10400,11600,17700],30,65,700,680))
    ls=['统一毫米制，Y向南，北 ↑','M01/M02/M03为开放边界','C西侧开口 '+str(round(C['openings']['C_west_opening']['box'][3]*1000))+'mm','B床垫 '+str(round(BOXES['bedB'][2]))+'mm','A/B/D床侧各900mm','D床尾、幕布后各1000mm','家庭厅内部连通、入口子母门','卫浴虚线：未确认原点位','机器人虚线：候选未落实','M03北块拟拆，结构待确认','设备与家具选型仍须现场复核']
    if index in (3,10):ls+=['管线路由仅为补充概念示意','三维未建管线，接点未确认']
    p.extend(text(750,100+i*42,t,15,anchor='start') for i,t in enumerate(ls))
    p.append(text(575,790,'墙段、门扇、家具外沿来自已验证网格；原图估读不代表实测净尺寸。',15))
    return finish(p)
def water_plan():
    return ''.join(line(pts,col,22,'60 40') for pts,col in [(WATER_ROUTE,BLUE),(WATER_COLD,GREEN),(WATER_HOT,RED)])
def ac_plan():
    return ''.join(line(pts,{'refrigerant':AMBER,'power':RED,'condensate':BLUE}[typ],22,'60 40') for services in BASE['AC_ROUTES'].values() for typ,pts in services.items())
def kitchen(ox,oy,scale,seats=4,**kw):return project(architecture()+furniture(seats,whole=False),ox,oy,scale)
def detail_sheet(index):
    p=start(TITLES[index-1]);content=architecture()+furniture(opened=index in (8,9,14))
    if index==6:
        content=architecture()+furniture(opened=True,labels=False)
        for n in ('desk','study_storage','study_shallow','study_chair','shoe'):
            x,y,w,d=BOXES[n];content+=text(x+w/2,y+d/2,LABELS[n],135)
        for key in ('entrance','bedroom_A','bedroom_B'):
            points=C['family_routes'][key];content+=line([(x*1000,-y*1000) for x,y in points],BLUE,45,'50 40')
        e=M.report['metrics']['family']['entrance']
        p.append(viewport(content,[-3800,-6500,4600,4600]));ls=['家庭厅内部连通；桌1700×700，浅柜1400×450，大件柜1000×650，北端不变。',f"西主扇／东副扇均内开；扣概念框扇五金后净宽 {e['main_net_mm']}／{e['both_net_mm']}mm。",'棕线：柜门／抽屉；绿线：人位；红线：后退500；浅柜人员操作与进门错时。','安全玻璃、周边及下沉密封、家庭厅侧帘轨；整门隔声检测、安装缝、关门通风待核。']
    elif index==7:
        for i,n in enumerate((4,6)):
            m=M.report['metrics'][str(n)];boundary=-C['walls'][C['acceptance']['normal_north_boundary']][1]*1000
            dims=''
            for x,key in [(650,'north_route_seated_mm'),(950,'north_route_pulled_mm')]:
                gap=m[key];end=boundary+gap
                dims+=line([(x,boundary),(x,end)],AMBER,10)+line([(x-50,boundary),(x+50,boundary)],AMBER,10)+line([(x-50,end),(x+50,end)],AMBER,10)+text(x-40,(boundary+end)/2,gap,120,AMBER,'end')
            p.append(viewport(architecture()+furniture(n,whole=False)+dims,[-200,-2900,4500,6200],30+i*555,80,535,530))
            p.append(text(290+i*555,635,f'{n}人：'+dimensions(f'table{n}'),17))
        ls=conclusion()+['绿灰实体为正常位置；红虚线为平移500mm后的座椅，浅虚线为运动范围；紫线为膝部投影。']
    elif index==8:
        p.append(viewport(content,[-250,-2900,4800,6200]));ls=conclusion()+['含微波炉：棕线为开门，绿线为取放热食及概念散热；厂家安装图确定后替换包络。']
    elif index==9:
        for i,n in enumerate((4,6)):
            s=next(v for v in M.states if v['seats']==n and v['state']=='normal');b=M.basket(s)
            route=line(b['path_mm'],BLUE,600,'100 70')
            p.append(viewport(content+f'<g opacity=".22">{route}</g>',[-3900,-2950,9000,6000],30+i*555,80,535,520))
            p.append(text(295+i*555,630,f'{n}人正常携篮：北带余量 {b["lateral_allowance_mm"]}mm',17))
        ls=['蓝带为600mm方形衣篮连续转弯扫掠；路线与设备操作交叠在状态表逐项给出。','全部拉出北带600mm，衣篮横向余量为0；不判舒适通过，默认先恢复就座位置。','洗碗装卸与岛槽操作须暂停；路线终点到阳台B门内，转向洗烘和门槛待现场演示。']
    elif index==14:
        p.append(viewport(content,[-1000,-10200,6500,9500]));ls=['主卫、公卫洁具均为模型概念占位，未确认原点位；不据此移动原上下水。','R01与L02为虚线候选，未落实设备；L02旧位置与房门运动关系见中文冲突对照。','待核干湿界、门槛、托盘抽取、供排水及清扫往返；不侵占洗烘维护区。']
    p.append(notes(ls));return finish(p)
def dimensions(n):
    f=C['furniture'][n];return '×'.join(str(round(v*1000)) for v in f['box'][2:])+f"，配置高{round(f['height']*1000)}mm"
def elevation(index):
    p=start(TITLES[index-1]);axes=(0,2) if index==4 else (1,2)
    if index==5:
        for i,owner in enumerate(('tower','coffee')):
            content=['<g stroke-width="8">']
            for n,o in sorted(M.objects.items(),key=lambda v:v[1]['bounds'][0]):
                if 'Clearance_Envelopes' in o['collections']:continue
                equipment=not o['owner'] and (n.startswith(('coffee_','grinder','cup')) if owner=='coffee' else n.startswith(('oven','steam_oven')))
                if o['owner']==owner or (owner=='coffee' and o['owner']=='microwave') or equipment:content.append(mesh(n,o,(1,2),fill='#e4ddca'))
            for n,s in C['services'].items():
                if s['owner']==owner or (owner=='coffee' and s['owner']=='microwave'):
                    from layout_rules import service_box
                    a=service_box(C,s);content.append(rect(a[1]*1000,-a[5]*1000,(a[4]-a[1])*1000,(a[5]-a[2])*1000,'none',AMBER if s['category']=='opening' else GREEN,'45 30'))
            p.append(viewport(''.join(content)+'</g>',[-3200,-2450,2400,2650],30+i*555,75,530,540))
            p.append(text(295+i*555,640,('蒸箱／烤箱独立侧视' if owner=='tower' else '咖啡台／台式微波炉侧视')+' · 北向前方 →',17))
        p.append(notes(['棕虚线为开启包络，绿虚线为人员操作；侧视不混合不同柜体。','微波炉上方绿线：概念散热；台面前棕线：开门；前方绿线：取放热食。','咖啡台面实际顶930mm；手动取水箱与废水盘；台式微波炉不封入柜格，净距按厂家。','独立蒸箱和烤箱的开门、取箱、取盘与电源分别核验；实际设备高度及安装条件待选型。']))
        return finish(p)
    keep=('fridge','tower','coffee','microwave') if index==4 else ('tower','coffee','microwave')
    content=['<g stroke-width="8">']
    for n,o in sorted(M.objects.items(),key=lambda v:v[1]['bounds'][1]):
        if 'Clearance_Envelopes' in o['collections']:continue
        if o['owner'] in keep or (not o['owner'] and n.startswith(('coffee_','grinder','oven','steam_oven','cup'))):
            content.append(mesh(n,o,axes,fill='#e4ddca',stroke=INK))
    for n,s in C['services'].items():
        if index==5 and s['owner'] in keep:
            from layout_rules import service_box
            a=service_box(C,s);content.append(rect(a[1]*1000,-a[5]*1000,(a[4]-a[1])*1000,(a[5]-a[2])*1000,'none',AMBER,'45 30'))
    content.append('</g>')
    view=[0,-2550,4100,2850] if index==4 else [-3300,-2500,3300,2800]
    p.append(viewport(''.join(content),view))
    ls=[f'{LABELS[n]}：{dimensions(n)}' for n in keep]
    if index==4:ls=['西→东：'+'；'.join(LABELS[n]+' '+dimensions(n) for n in keep[:2]),'；'.join(LABELS[n]+' '+dimensions(n) for n in keep[2:])]
    ls+=['实际部件正投影；咖啡柜配置基高900mm，含台面实体顶930mm，取箱与废水盘手动操作。','设备散热、取箱、拆机及电源检修按厂家安装图；侧视重叠不等于同一高度实体碰撞。']
    p.append(notes(ls));return finish(p)
def connection_svg():
    p=start(TITLES[14]);parts=M.parts('table6');content='<g stroke-width="8">'+''.join(mesh(n,o,(0,2)) for n,o in parts.items())
    for i in range(6):
        a=M.knees(f'chair6_{i}');content+=rect(a[0]*1000,-a[5]*1000,(a[3]-a[0])*1000,(a[5]-a[2])*1000,'none','#876ca4','20 20')
    content+=''.join(mesh(n,o,(0,2),fill='#e4ddca') for n,o in M.parts('island').items())
    p.append(viewport(content+'</g>',[1000,-1100,3000,1200],30,70,1090,275))
    p.append(viewport(furniture(6,whole=False),[950,-800,3100,2600],30,365,1090,275))
    s=C['furniture']['table6']['support'];k=C['seating'];v=M.validation()['supports'][1]
    p.append(notes([f"桌高750mm；中央支撑 {round(s['width']*1000)}×{round(s['depth']*1000)}mm，距桌端 {round(s['end_inset']*1000)}mm。",
      f"梁底 {round(s['beam_z']*1000)}mm，概念膝顶 {round((k['knee_z']+k['knee_height'])*1000)}mm：梁下余量 {v['beam_above_knee_mm']}mm，六人端膝侧余量 {v['knee_to_support_mm']}mm。",
      '座面入桌150mm不判碰撞；桌腿侵入膝部必须检出。岛东桌西、伸桌向西200mm，岛保持原位。',
      '按当前无扶手椅、平齐床架及人体概念包络复核；承载、伸缩锁止、可拆收口和水槽检修待厂家。']))
    return finish(p)
def drawings():
    from concept_details import overlay_svg,water_svg,ceiling_svg
    svgs={FILES[i-1]:full_sheet(i) for i in (1,2,3,10)}
    svgs.update({FILES[i-1]:detail_sheet(i) for i in (6,7,8,9,14)})
    svgs.update({FILES[3]:elevation(4),FILES[4]:elevation(5),FILES[10]:overlay_svg(),FILES[11]:ceiling_svg(),FILES[12]:water_svg(),FILES[14]:connection_svg()})
    return {n:svgs[n] for n in FILES}

"""R10.1 single whole-house model, mm, north up. Image-estimated, NOT surveyed.

Wall rectangles are closed solids with shared faces at junctions. Openings and
bay ledges are separate objects; ledges are excluded from usable floor space.
All plans project this same model, including the source-overlay sheet.
"""
import base64
import hashlib
import html
import json
import math
from pathlib import Path

INK, GREEN, BLUE, AMBER, RED = '#233d36', '#287361', '#427f9a', '#ac6537', '#b34539'
C_WIDTH, C_DEPTH = 3976, 2998
# Original image calibration: C west/CD wall junction, C east/CD junction.
SOURCE_TRANSFORM = {'origin_px': [532, 516], 'px_per_mm': [175/3976, 133/2998]}
# Wall faces, rather than stroke centre lines, define clearance boundaries.
WALLS = {
 'A_north':(-660,-10197,7520,240), 'A_west':(-660,-10077,240,3810),
 'A_east':(6620,-10077,240,4050), 'A_south1':(420,-6267,4290,120),
 'A_south2':(6220,-6267,400,120), 'family_north':(-3650,-6387,3230,240),
 'family_west':(-3650,-6147,240,3423),
 'master_bath_east1':(1280,-10077,120,1190),
 'master_bath_east2':(1280,-8127,120,500),
 'master_bath_south':(-420,-7747,1700,120),
 'B_west1':(520,-6147,120,2180), 'B_west2':(520,-3217,120,373),
 'B_east1':(3976,-6147,240,747), 'B_east2':(3976,-3850,240,1006),
 'bath_kitchen_north':(-900,-2844,4876,120),
 'entry_return':(-3410,-2844,1010,120),
 'entry_lower':(-3650,-1844,240,594), 'entry_step':(-4412,-1370,1002,240),
 'living_west':(-4412,-1130,240,7600),
 'bath_west':(-900,-2724,120,1474),
 'bath_south1':(-780,-1370,80,120), 'bath_south2':(50,-1370,1550,120),
 'bath_east':(1600,-2724,120,1474),
 'balconyB_div1':(3976,-2724,120,1474), 'balconyB_div2':(3976,-400,120,400),
 'balconyB_NE':(5093,-2844,120,180), 'balconyB_SE':(5093,-120,120,240),
 'C_north_end':(0,0,180,120),
 'C_east1':(3976,0,240,550), 'C_east2':(3976,2200,240,798),
 'CD':(-120,2998,4336,120), 'C_west_end':(-120,2818,120,300),
 'D_west1':(-120,3118,120,150), 'D_west2':(-120,4018,120,2364),
 'D_east':(3976,3118,240,3264),
 'D_south1':(0,6262,1120,120), 'D_south2':(2760,6262,1216,120),
 'balconyA_head1':(-4172,5140,600,120), 'balconyA_head2':(-1572,5140,1452,240),
 'balconyA_east':(-1167,5380,120,1090),
}
REMOVALS = {'M01':(1080,0,2896,120), 'M02':(1600,-1250,120,350),
            'M03':(-120,120,120,2698)}
# No wall behind each opening. Bounds include the frame, not a usable bay floor.
OPENINGS = {
 'former_C_door':{'box':(180,0,900,120),'kind':'removed_door'},
 'former_kitchen_door':{'box':(1600,-900,120,900),'kind':'removed_door'},
 'A_door':{'box':(-420,-6267,840,120),'kind':'door'},
 'A_window':{'box':(4710,-6267,1510,120),'kind':'window'},
 'master_bath_door':{'box':(1280,-8887,120,760),'kind':'door'},
 'B_door':{'box':(520,-3967,120,750),'kind':'door'},
 'entry':{'box':(-3650,-2724,240,880),'kind':'door'},
 'bath_door':{'box':(-700,-1370,750,120),'kind':'door'},
 'balconyB_door':{'box':(3976,-1250,120,850),'kind':'door'},
 'D_door':{'box':(-120,3268,120,750),'kind':'door'},
 'balconyA_connection':{'box':(-3572,5140,2000,120),'kind':'connected'},
 'balconyB_north':{'box':(4216,-2844,877,120),'kind':'window'},
 'balconyB_east':{'box':(5093,-2664,120,2544),'kind':'window'},
 'balconyB_south':{'box':(4216,0,877,120),'kind':'window'},
 'balconyA_south':{'box':(-4172,6350,3005,120),'kind':'window'},
 'B_bay':{'box':(3976,-5400,750,1550),'kind':'bay_east'},
 'C_bay':{'box':(3976,550,750,1650),'kind':'bay_east'},
 'D_bay':{'box':(1120,6262,1640,700),'kind':'bay_south'},
}
BOXES = {
 'sink':(3200,-2724,776,600), 'prep':(2400,-2724,800,600),
 'hob':(1720,-2724,680,600), 'dishwasher':(2600,-2724,600,600),
 'dishwasher_door':(2600,-2124,600,650),
 'dishwasher_operator':(2600,-1474,600,600),
 'island':(2900,225,1000,750), 'aux_sink':(3460,330,340,360),
 'island_operator':(3300,-375,600,600),
 'table4':(1300,200,1600,800), 'table6':(1100,200,1800,800),
 'fridge':(100,2248,975,750), 'tower':(1075,2398,600,600),
 'coffee':(1675,2398,1300,600), 'pantry':(2975,2398,901,600),
 'fridge_door':(100,1760.5,975,487.5), 'fridge_drawer':(160,1648,855,600),
 'fridge_operator':(100,1048,975,600),
 'oven_door':(1075,1848,600,550), 'steam_door':(1075,1848,600,550),
 'tower_operator':(1075,1248,600,600),
 'coffee_drawer':(1675,1898,1300,500), 'coffee_operator':(1675,1298,1300,600),
 'pantry_door':(2975,1948,901,450), 'pantry_operator':(2975,1348,901,600),
}
FAMILY = {'deep':(-3410,-6000,650,2000), 'deep_door':(-2760,-6000,600,2000),
 'desk':(-2110,-6147,1650,700), 'books':(-2100,-6147,600,280),
 'chair':(-1350,-5247,600,800), 'shoe':(-2200,-2724,1100,350),
 'shoe_door':(-2200,-2374,1100,350)}
HOUSE = {'bedA':(3350,-9577,1800,2000), 'wardrobeA':(5920,-9777,600,2400),
 'bedB':(1670,-6047,1500,2000), 'wardrobeB':(640,-6047,600,1500),
 'bedD':(1680,3262,1500,2000), 'wardrobeD':(0,5400,2700,600),
 'sofa':(-4072,850,950,2700), 'screen':(-1150,1000,80,2450),
 'projector':(-3620,2050,450,300), 'laundry':(4216,-2490,750,650),
 'robot':(4300,-450,650,450), 'robot_alt':(650,-2040,550,450)}
AC = {'AC01':(-2950,5200,1400,650), 'AC02':(6380,-7250,240,800),
 'AC03':(3736,-3750,240,800), 'AC04':(2976,6022,850,240),
 'AC05':(-1400,-6147,850,240)}
AC01_CEILING=(-3250,4900,2000,1150)
AC01_RETURN=(-2870,4980,600,180)
AC01_ACCESS=(-2150,4960,600,600)
AC01_STAND=(-2350,4230,1000,850)
# Each service is independently drawn; unknown endpoints are labels, never outdoor units.
AC_ROUTES={
 'AC01':{'refrigerant':[(-2250,5525),(-1300,5525),(-1300,6050)],
         'power':[(-2250,5525),(-3100,5525),(-3100,4100)],
         'condensate':[(-1550,5600),(-1220,5600),(-1220,6200)]},
 'AC02':{'refrigerant':[(6500,-6850),(6500,-7080),(6500,-6500)],
         'power':[(6500,-6850),(5750,-6850),(5750,-6500)],
         'condensate':[(6500,-6850),(6500,-9900),(1500,-9900),(1500,-8000)]},
 'AC03':{'refrigerant':[(3856,-3350),(3900,-3350),(3900,-3000)],
         'power':[(3856,-3350),(3200,-3350),(3200,-3100)],
         'condensate':[(3856,-3350),(3850,-3350),(3850,-2950)]},
 'AC04':{'refrigerant':[(3401,6142),(3900,6142),(3900,6600)],
         'power':[(3401,6142),(3100,6142),(3100,5500)],
         'condensate':[(3401,6142),(2900,6142),(2900,6600)]},
 'AC05':{'refrigerant':[(-975,-6027),(-975,-5850),(-3000,-5850)],
         'power':[(-975,-6027),(-600,-6027),(-600,-5550)],
         'condensate':[(-975,-6027),(-600,-6027),(-600,-3100)]},
}
WATER_ROUTE=[(3630,510),(3876,510),(3876,-2400),(3580,-2400)]
WATER_COLD=[(3600,-2480),(3806,-2480),(3806,440),(3630,440)]
WATER_HOT=[(3550,-2540),(3756,-2540),(3756,380),(3630,380)]
DOORS=['fridge_door','fridge_drawer','oven_door','steam_door','coffee_drawer','pantry_door','dishwasher_door']
OPERATORS=['fridge_operator','tower_operator','coffee_operator','pantry_operator','dishwasher_operator','island_operator']
FIXED=['sink','prep','hob','island','fridge','tower','coffee','pantry']
# Routes adapt to actual use state. The 600 basket has a square turn envelope.
def basket_path(pulled=False):
    y=-925 if pulled else -560
    return [(-3500,-2200),(-2600,-2200),(-2600,y),(3600,y),(3600,-825),(4500,-825)]

def chairs(seats,pulled=False):
    x,y,w,h=BOXES[f'table{seats}']; d=800 if pulled else 450
    return [(x+w*(i+.5)/(seats//2)-250,yy,500,d)
            for yy in (y-d,y+h) for i in range(seats//2)]

def intersection(a,b):
    x,y=max(a[0],b[0]),max(a[1],b[1])
    w,h=min(a[0]+a[2],b[0]+b[2])-x,min(a[1]+a[3],b[1]+b[3])-y
    return (x,y,w,h) if w>1e-6 and h>1e-6 else None

def swept_boxes(points,width=600):
    r=width/2; result=[]
    for (x1,y1),(x2,y2) in zip(points,points[1:]):
        assert x1==x2 or y1==y2
        result.append((min(x1,x2)-r,min(y1,y2)-r,abs(x2-x1)+width,abs(y2-y1)+width))
    return result

def state_metrics(seats,pulled):
    cs=chairs(seats,pulled); sweeps=swept_boxes(basket_path(pulled))
    solids={**WALLS,**{k:v for k,v in HOUSE.items() if k not in ['robot','robot_alt']},**FAMILY,**{k:v['box'] for k,v in OPENINGS.items() if 'bay' in v['kind']},
            **{k:BOXES[k] for k in FIXED+DOORS},f'table{seats}':BOXES[f'table{seats}']}
    chair_fixed=[(i,k) for i,c in enumerate(cs) for k,b in solids.items() if intersection(c,b)]
    chair_operators=[(i,k) for i,c in enumerate(cs) for k in OPERATORS if intersection(c,BOXES[k])]
    route_solids=[k for k,b in solids.items() if any(intersection(s,b) for s in sweeps)]
    route_chairs=[i for i,c in enumerate(cs) if any(intersection(s,c) for s in sweeps)]
    route_operators=[k for k in OPERATORS if any(intersection(s,BOXES[k]) for s in sweeps)]
    issues=[]
    for i,k in chair_operators:
        overlap=intersection(cs[i],BOXES[k])
        issues.append({'objects':[f'chair_{i}',k],'state':f'{seats}人'+('拉椅' if pulled else '就座')+'及设备操作','overlap_mm':list(overlap[2:]),'action':'南排离座后操作，热盘依次取'})
    for k in route_operators:
        overlaps=[intersection(b,BOXES[k]) for b in sweeps if intersection(b,BOXES[k])]
        issues.append({'objects':['basket600',k],'state':'携篮及设备操作','overlap_mm':[list(b[2:]) for b in overlaps],'action':'携篮与设备操作错时'})
    return {'issues':issues,'seats':seats,'pulled':pulled,'chair_fixed_or_open_door_conflicts':chair_fixed,
      'chair_operator_conflicts':chair_operators,'basket_solid_conflicts':route_solids,
      'basket_chair_conflicts':route_chairs,'basket_operator_conflicts':route_operators,
      'all_operations_with_diners_and_basket':False, 'use_recommendation':'携篮与洗碗装卸、岛槽错时；南排离座后蒸烤/咖啡取物', 'local_gap_mm':274 if pulled else 624}

def water_metrics():
    lengths=[abs(a[0]-b[0])+abs(a[1]-b[1]) for a,b in zip(WATER_ROUTE,WATER_ROUTE[1:])]
    total=sum(lengths)
    return {'route_mm':WATER_ROUTE,'horizontal_segments_mm':lengths,'horizontal_length_mm':total,
       'pipe_trial_outer_diameter_mm':50,'slope_scenarios':[{'slope':i,'fall_mm':round(total*i,2),
       'minimum_build_up_trial_mm':round(50+20+total*i,2)} for i in [.01,.02,.025]],
       'connection_invert_mm':None,'available_floor_build_up_mm':None,
       'gravity_drainage_established':False,'structural_cutting_authorized':False,
       'floor_level_change':False,'pump_assumed':False}

def trial_metrics():
    fixed={k:BOXES[k] for k in FIXED+['table6']}
    conflicts=[(a,b) for i,a in enumerate(fixed) for b in list(fixed)[i+1:] if intersection(fixed[a],fixed[b])]
    wall_hits=[(a,b) for a,v in fixed.items() for b,w in WALLS.items() if intersection(v,w)]
    bath_face=WALLS['bath_south2'][1]+WALLS['bath_south2'][3]
    north_gap=lambda pulled:min(c[1] for c in chairs(6,pulled))-bath_face
    south_gap=BOXES['oven_door'][1]-max(c[1]+c[3] for c in chairs(6,True))
    return {'units':'mm; image-estimated trial, not surveyed','fixed_conflicts':conflicts,
      'fixed_wall_conflicts':wall_hits,'prep_surface':BOXES['prep'][2],'north_pulled_gap':north_gap(True),
      'north_seated_gap':north_gap(False),'east_island_wall_gap_not_passage':C_WIDTH-BOXES['island'][0]-BOXES['island'][2],
      'south_pulled_to_tower_door':south_gap,'south_shift_limit_door_only_mm':south_gap,
      'south_cabinet_positions_unchanged':True,'states':[state_metrics(s,p) for s in (4,6) for p in (False,True)],
      'water':water_metrics(),'r101':detail_metrics(),'site_verified':False}

def model_digest():
    return hashlib.sha256(json.dumps([WALLS,OPENINGS,BOXES,FAMILY,HOUSE,AC,AC_ROUTES,WATER_ROUTE,DOOR_MODEL],sort_keys=True).encode()).hexdigest()

def text(x,y,s,size=15,color=INK,anchor='middle'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}">{html.escape(str(s))}</text>'

def rect(x,y,w,h,fill='none',stroke=INK,dash=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-dasharray="{dash}"/>'

def line(points,color=INK,width=2,dash=''):
    return '<polyline points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}"/>'

def start(title,h=760,w=1150):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(title)}"><title>{html.escape(title)}</title><g font-family="Microsoft YaHei, sans-serif">',text(w/2,30,title,22)]

def obj(ident,box,fill,stroke=INK,dash='',attribute='data-object'):
    return f'<g {attribute}="{ident}" data-box="{",".join(map(str,box))}">'+rect(*box,fill,stroke,dash)+'</g>'

def architecture(alter=False,overlay=False):
    p=['<g stroke-width="20">']
    for k,b in WALLS.items():p.append(obj(k,b,BLUE if overlay else INK,'none',attribute='data-wall'))
    for k,v in OPENINGS.items():
        x,y,w,h=v['box']; kind=v['kind']
        if kind=='removed_door' and not alter:continue
        p.append(f'<g data-opening="{k}" data-kind="{kind}" data-box="{x},{y},{w},{h}">')
        if kind.startswith('bay'):
            p.append(rect(x,y,w,h,'#dce8ec','none'))
            if kind=='bay_east': pts=[(x,y),(x+w,y),(x+w,y+h),(x,y+h)]
            else:pts=[(x,y),(x,y+h),(x+w,y+h),(x+w,y)]
            p.append(line(pts,BLUE,35))
            if kind=='bay_east':pts=[(x+100,y+100),(x+w-100,y+100),(x+w-100,y+h-100),(x+100,y+h-100)]
            else:pts=[(x+100,y+100),(x+100,y+h-100),(x+w-100,y+h-100),(x+w-100,y+100)]
            p.append(line(pts,BLUE,20))
        elif kind=='window':
            p.append(rect(x,y,w,h,'#dfedf1',BLUE))
            p.append(line([(x,y+h/2),(x+w,y+h/2)] if w>h else [(x+w/2,y),(x+w/2,y+h)],BLUE,20))
        elif kind in ('door','removed_door'):
            if k in DOOR_MODEL:p.append(door_graphic(k))
        p.append('</g>')
    if alter:
        for k,b in REMOVALS.items():
            p.append(obj(k,b,'none',RED,'100 60','data-removal'))
            p.append(text(b[0]+b[2]/2,b[1]+b[3]/2,k,180,RED))
    p.append('</g>');return ''.join(p)

def furniture(seats=4,opened=False,whole=False,labels=True):
    p=['<g stroke-width="18">']
    for k in FIXED+[f'table{seats}']:
        p.append(obj(k,BOXES[k],'#d8decf'))
    p.append(obj('aux_sink',BOXES['aux_sink'],'#e1f1f7',BLUE))
    p.append(obj('dishwasher',BOXES['dishwasher'],'none',BLUE))
    for i,c in enumerate(chairs(seats,True)):p.append(obj(f'chair_pull_{i}',c,'none',AMBER,'45 45'))
    for i,c in enumerate(chairs(seats)):p.append(obj(f'chair_seated_{i}',c,'#fff',AMBER))
    if opened:
        for k in DOORS:p.append(obj(k,BOXES[k],'none',AMBER,'100 50'))
        for k in OPERATORS:p.append(obj(k,BOXES[k],'none',GREEN,'30 50'))
    if labels:
        labels_map={'sink':'主水槽','prep':'备菜800','hob':'灶','island':'带水岛','table4':'1600×800','table6':'1800×800','fridge':'冰箱','tower':'蒸／烤','coffee':'咖啡1300','pantry':'食品'}
        for k in FIXED+[f'table{seats}']:
            x,y,w,h=BOXES[k];p.append(text(x+w/2,y+h/2+65,labels_map[k],190))
    if whole:
        for k,b in HOUSE.items():
            if k=='robot': continue # rejected legacy L02 only appears in review sheet
            p.append(obj(k,b,'none' if k=='robot_alt' else '#e3e8de',BLUE if k in ['screen','projector','robot_alt'] else INK,'90 45' if k=='robot_alt' else ''))
            if k=='robot_alt':p.append(text(b[0]+275,b[1]-80,'R01主选？',160,BLUE))
        for k,b in FAMILY.items():p.append(obj(k,b,'none' if k.endswith('door') or k=='books' else '#d8decf',AMBER if k.endswith('door') else INK,'80 40' if k.endswith('door') else ''))
        for k,b in AC.items():
            p.append(obj(k,b,'#b9d9e4',BLUE));p.append(text(b[0]+b[2]/2,b[1]-90,k,195,BLUE))
        for x,y,s in [(3500,-6770,'A 主卧'),(250,-9300,'主卫'),(-2300,-3800,'家庭厅'),(2600,-3300,'B 次卧'),
          (350,-2320,'公卫'),(4730,-1700,'阳台B'),(-2350,100,'客厅'),(900,4450,'D 次卧'),(-2800,6050,'阳台A 封窗连通')]:p.append(text(x,y,s,245))
    p.append('</g>');return ''.join(p)

def water_plan():
    p=[]
    for key,pts,col,dash in [('C02-drain',WATER_ROUTE,BLUE,'60 45'),('C02-cold',WATER_COLD,GREEN,''),('C02-hot',WATER_HOT,RED,'')]:
        p.append(f'<g data-route="{key}">'+line(pts,col,30,dash)+'</g>')
    p.append(text(3420,-2900,'W0 原厨房合法污水支管？',160,BLUE))
    return ''.join(p)

def ac_plan():
    p=[obj('AC01-ceiling',AC01_CEILING,'none',BLUE,'180 70 30 70'),
       obj('AC01-return',AC01_RETURN,'#c4e2d8',GREEN),obj('AC01-access',AC01_ACCESS,'none',AMBER,'80 40'),
       obj('AC01-standing',AC01_STAND,'none',GREEN,'30 50')]
    for k,services in AC_ROUTES.items():
        for service,pts in services.items():
            color,dash={'refrigerant':(AMBER,'120 60'),'power':(RED,'30 60'),'condensate':(BLUE,'60 60')}[service]
            p.append(f'<g data-route="{k}-{service}">'+line(pts,color,25,dash)+'</g>')
            suffix={'refrigerant':'孔/外机？','power':'电源？','condensate':'排水？'}[service]
            p.append(text(*pts[-1],k[-1]+suffix,135,color))
    p += [line([(-2750,5200),(-2750,4500),(-2820,4640),(-2750,4500),(-2680,4640)],GREEN,40),
          text(-3350,4620,'送风北↑',165,GREEN),text(-1800,4800,'检修站位',165,GREEN),
          line([(-600,-5900),(-100,-5000),(-190,-5140)],GREEN,35),
          text(-400,-4700,'AC05向东南避座席',150,GREEN),line([(6380,-6850),(5650,-6850)],GREEN,35),line([(3736,-3350),(3000,-3350)],GREEN,35),text(5400,-6600,'AC02向西',150,GREEN),text(2870,-3050,'AC03向西',150,GREEN),text(-2870,4900,'AC01-R',135,GREEN),text(-1900,5100,'AC01-J',135,AMBER),text(-1850,4320,'AC01-S',135,GREEN)]
    return ''.join(p)

def project(content,ox,oy,scale):
    return f'<g data-model="{model_digest()}" transform="translate({ox} {oy}) scale({scale})">{content}</g>'

def floorplan(mode):
    p=start('R10.1 '+mode+' · 北 ↑',960,720)
    content=architecture(mode=='拆改')+furniture(whole=True,labels=mode not in ['水电','空调'])
    if mode=='拆改':
        content+=line([(3300,60),(3400,-180)],RED,15)+text(3400,-230,'M01',180,RED)
    if mode=='水电':
        content+=water_plan()
        for ident,k in {'K01':'sink','K02':'hob','K03':'dishwasher','K04/K05':'tower','C01':'fridge','C02':'island','C03':'pantry','H03':'coffee','H02':'table4'}.items():
            x,y,w,h=BOXES[k];content+=text(x+w/2,y+h/2+100,ident,160,BLUE)
        for ident,k in {'L01':'laundry','R01':'robot_alt','H04':'projector','H05':'screen'}.items():
            x,y,w,h=HOUSE[k];content+=text(x+w/2,y+h/2+60,ident,160,BLUE)
        for ident,k in {'S01':'desk','T01':'deep'}.items():
            x,y,w,h=FAMILY[k];content+=text(x+w/2,y+h/2+60,ident,160,BLUE)
        content+=text(-2300,-4200,'S02',160,BLUE)+text(-3300,-1800,'H01',160,BLUE)
    if mode=='空调':content+=ac_plan()
    if mode in ['空调','家具平面']:content+=section_cut()
    p.append(project(content,258,563,.047))
    p += [text(360,921,'实墙为闭合厚轮廓；蓝双线窗 / 飘窗台；棕弧为原门扇估读。',12),
          text(360,943,'统一毫米坐标 · 原图估读，非实测；飘窗台不计通行净宽。',12,AMBER)]
    return ''.join(p+['</g></svg>'])

def kitchen(ox,oy,scale,seats=4,opened=False,alter=False,routes=False,labels=True):
    # Cropping only changes the view, never the geometry.
    content=architecture(alter)+furniture(seats,opened,labels=labels)
    if routes:
        pts=basket_path(True);content+=line(pts,'#ead8c9',600)+line(pts,RED,25)
    return f'<svg x="{ox-1900*scale}" y="{oy-3000*scale}" width="{(5500+1900)*scale}" height="{6300*scale}" viewBox="-1900 -3000 7400 6300">'+project(content,0,0,1)+'</svg>'

def island_svg():
    p=start('R10.1 横向岛桌 · 东岛固定 / 西桌向西延伸',760)
    p += [text(285,65,'四人 1600×800',18),text(865,65,'六人 1800×800',18),kitchen(165,320,.068,4),kitchen(745,320,.068,6)]
    notes=['岛1000×750，东部340×360辅助水槽；桌高750，岛高850–900，连接独立支承。',
     '桌 y=200，岛 y=225；六人仅向西延伸200，固定给排水的岛台不移动。',
     '北排就座距公卫南墙1000；全拉椅余650。南排全拉椅至蒸烤门仅48，不作通道。',
     '南侧48仅估读算例，不是安装余量；当前位置仍须净尺寸放样。',
     '岛东至墙76是管线/收口间隙，不是过道；水槽从北侧使用，飘窗台不计净宽。',
     '橙短虚线附着餐椅＝拉椅800；实线椅＝就座450；南柜和客厅休息家具原位保留。']
    p += [text(575,585+i*27,t,14,AMBER if i in (2,3,4) else INK) for i,t in enumerate(notes)]
    return ''.join(p+['</g></svg>'])

def clearance_svg():
    p=start('R10.1 满开与站位 · 每种状态分别计算',760)
    p += [kitchen(180,340,.082,6,True),text(875,95,'可同时与需错时的状态',20)]
    notes=['四／六人、全拉椅：不碰固定柜及全开门。',
     '冰箱门487.5、抽屉600，操作人位另600。',
     '六人椅最西x=1150，避开冰箱人位x≤1075。',
     '蒸／烤门各550；人位600，共同平面投影。',
     '南排就座侵入蒸烤和咖啡操作区，须离座。',
     '两台热盘取物依次进行；不跨下层热门。',
     '咖啡抽屉500；水箱与排汽看独立剖面。',
     '就座＋洗碗装卸：局部624，衣篮余24。',
     '北排全拉椅＋洗碗装卸：携篮路径受占。',
     '此状态先收椅或暂停装卸，不挪固定岛台。',
     '就座携篮时，岛北辅助水槽操作需暂停。',
     '绿色点框＝操作人位；橙长虚线＝柜门。',
     '厂家开门角、热盘高度与实测净宽待替换。']
    p += [text(870,142+i*41,t,14,AMBER if i in (4,8,9,12) else INK) for i,t in enumerate(notes)]
    return ''.join(p+[text(575,728,'操作包络属于占用，不重复计入通道；全开无碰撞不等于全员同时取物。',15,AMBER),'</g></svg>'])

def workflow_svg():
    p=start('R10.1 北侧主通路 · 浅带为600衣篮与转弯包络',760)
    content=architecture()+furniture(6,True,whole=True)
    content+=line(basket_path(True),'#ead8c9',600)+line(basket_path(True),RED,25)
    content+=line(basket_path(False),BLUE,25)
    p.append('<svg x="15" y="100" width="630" height="550" viewBox="-4200 -3100 9700 6600">'+project('<g stroke-width="14">'+content+'</g>',0,0,1)+'</svg>')
    p.append(text(330,665,'红线＋浅带：全拉椅；蓝线：就座时中心路线。',13))
    notes=['① 入户→餐区西侧→南墙冰箱／食品', '② 冰箱→主水槽→800备菜→灶',
      '③ 主水槽→岛北辅助水槽／备餐', '④ 灶→岛台西部摆盘→西侧餐桌',
      '⑤ 收餐→桌北侧→主水槽／洗碗机', '⑥ 客餐区→南柜咖啡；洗杯可到岛槽',
      '⑦ 入户→公卫南侧→岛桌北侧→阳台B',
      '就座装卸局部624；600衣篮仅余24。',
      '全拉椅：中心y=-925，洗碗装卸需暂停。',
      '携篮与洗碗装卸错时；650仅估读算例。',
      '阳台B估读门洞850，开门停靠及转弯待测。',
      '南排就座与蒸烤／咖啡取物须错时。']
    p += [text(875,120+i*44,t,14,AMBER if i>=7 else INK) for i,t in enumerate(notes)]
    p += [text(575,717,'实线为携篮实际路径；上述①—⑥是工作顺序，不用文字引线冒充管线。',14)]
    return ''.join(p+['</g></svg>'])

def overlay_svg():
    p=start('R10.1 原图半透明叠合核对 · 不叠加新家具',960,1150)
    source=Path(__file__).resolve().parent.parent/'IMG20260907-094631119.jpg'
    data=base64.b64encode(source.read_bytes()).decode()
    p.append(f'<image href="data:image/jpeg;base64,{data}" x="0" y="50" width="1000" height="750.427" opacity="0.48"/>')
    sx,sy=SOURCE_TRANSFORM['px_per_mm'];s=1000/1170
    p.append(f'<g data-model="{model_digest()}" transform="translate({532*s} {50+516*s}) scale({sx*s} {sy*s})" opacity="0.70">'+architecture(True)+'</g>')
    p += [text(575,835,'蓝色厚墙为重建；红框为拟拆实体；原有门洞保留缺口，C / B / D飘窗均恢复。',15),
      text(575,865,'使用单一仿射标定：C西北(532,516)px，x=175/3976，y=133/2998 px/mm。',15),
      text(575,895,'底图对位核查见CSV；墙厚120/240、门窗边界属估读，偏差不是测量精度。',15,AMBER),
      text(575,925,'先确认原图轮廓对位，再评审新布局；现场测绘与梁柱、窗台结构仍待核验。',15,AMBER)]
    return ''.join(p+['</g></svg>'])

def water_svg():
    p=start('R10.1 C02 岛台冷热水与重力排水 · 平面 / 剖面',820)
    p.append(kitchen(120,330,.07,4))
    p.append(project(water_plan(),120,330,.07))
    p += [text(810,90,'柜内：双独立阀＋存水弯＋检修＋探漏',18),
      rect(600,160,180,180,'#e5e9dd'),rect(620,150,120,25,'#c8e2eb'),
      text(690,205,'辅助水槽',15),'<path d="M680 178 V250 Q680 280 700 280 Q720 280 720 250 V240 H760 V290" fill="none" stroke="#427f9a" stroke-width="4"/>',line([(682,258),(718,258)],BLUE,2),text(660,300,'存水弯',12),line([(700,280),(700,290),(727,290)],BLUE,3),rect(715,284,12,12,'white',AMBER),text(845,305,'清扫口 → 北侧可拆检修面',13),
      text(910,232,'水封深度按规范/型号核定',14),text(885,265,'冷热阀独立，底板漏水探测',14),
      line([(580,340),(1080,340)],INK,3),text(1000,328,'完成面±0 连续平地',13),
      line([(580,480),(1080,480)],INK,6),text(840,507,'结构楼板：不预设开槽、钻梁或凿飘窗台',14,AMBER),
      line([(760,290),(760,365),(1040,435)],BLUE,4),text(855,355,'穿柜底套管→入地→W0',12),rect(748,330,24,25,'none',AMBER),line([(670,165),(625,165),(625,310)],GREEN,3),line([(660,165),(645,165),(645,310)],RED,3),rect(620,235,10,10,'white',GREEN),rect(640,235,10,10,'white',RED),text(620,325,'冷阀 热阀',11),text(870,412,'排水流向原厨房 →',14,BLUE),
      line([(1040,435),(1060,435)],BLUE,4),line([(1060,435),(1080,435),(1080,540),(1050,540)],'#777',1),text(950,548,'W0 接入管内底标高 z0＝待测',15,BLUE),
      text(815,580,'可用地面构造 H＝待测；保温/保护层另核',14),
      text(575,622,'平面排水：246＋2910＋296＝3452mm；从C东侧向北，接原厨房合法生活污水支管。',15),
      text(575,652,'坡度研究1% / 2% / 2.5% → 落差34.52 / 69.04 / 86.30mm；最终坡度由给排水专业确定。',15),
      text(575,682,'按外径50＋保护余量20初筛：H至少104.52 / 139.04 / 156.30mm，尚未计接头局部增高。',15),
      text(575,712,'条件：岛端管内底 z岛 ≥ z0＋iL；全路径管外顶及接头须落在可用构造内，接入需防返味。',14),
      text(575,746,'重力排水未成立：缺z0、H及沿线障碍实测；继续协调带水需求，不默认地台或提升泵。',16,RED),
      text(575,780,'绿实线冷水 / 红实线热水 / 蓝虚线污水；平面路线与剖面引线分别标识，长度非施工下料。',14)]
    return ''.join(p+['</g></svg>'])

def ceiling_svg():
    p=start('R10.1 AC01 阳台A顶面 · A—A 南北关系剖面（非比例，尺寸待测）',800)
    p += [text(170,85,'北：客厅',20),text(980,85,'南：封窗阳台A',20),
      line([(80,125),(1070,125)],INK,8),text(285,111,'结构板底 z板＝现场净高',15),
      rect(510,125,95,120,'#c6cec5'),text(553,280,'交界梁：位置 / 梁底待测',14,AMBER),
      rect(650,220,240,110,'#c9dfe6',BLUE),text(770,255,'AC01机身',18),text(770,285,'按安装图＋减振吊挂',13),
      line([(680,125),(680,220)],INK,2),line([(860,125),(860,220)],INK,2),
      rect(335,300,315,45,'#e4eff1',BLUE),text(450,332,'保温送风管：绕梁下',14,BLUE),
      line([(335,322),(200,322),(220,310),(200,322),(220,334)],GREEN,4),text(175,365,'向客厅北侧送风',15,GREEN),
      line([(300,405),(1000,405)],INK,4),text(655,432,'局部吊顶底 z吊＝净高与设备、梁及管路共同确定',15),
      rect(360,390,100,15,'#beded2',GREEN),text(380,470,'AC01-R 回风口',14,GREEN),
      line([(410,390),(410,360),(740,360),(740,330)],GREEN,3),
      rect(470,393,105,12,'none',AMBER,'5 3'),text(550,505,'AC01-J 检修口：拆修路径待厂家',14,AMBER),
      rect(995,255,20,350,'#dcebf1',BLUE),text(990,225,'窗头 z窗＝待测',14,BLUE),
      rect(940,355,30,65,'#ede1cc',AMBER),text(930,460,'窗帘盒独立留检修',14),
      line([(80,620),(1070,620)],INK,3),text(195,651,'完成地面±0：阳台A封窗并连通',15),
      rect(465,520,110,100,'none',GREEN,'3 4'),text(500,690,'检修梯/站人处：AC01-S 平面1000×850估读，待放样',15,GREEN),
      text(575,731,'滤网↓经回风口；电控盒↓经J；风机↓/侧移经J（方向及拆出尺寸均待厂家）。',15,AMBER),line([(760,330),(760,380),(550,380),(550,520)],AMBER,2,'6 4'),
      text(575,766,'AC01冷媒/电源/冷凝水见10图；公共区冷量含连通餐区，投影、灯具及幕盒协同定点。',15)]
    return ''.join(p+['</g></svg>'])

# R10.1: continuous swept sectors, all opening dimensions remain image estimates.
DOOR_MODEL={}
for key,v in OPENINGS.items():
    if v['kind']!='door':continue
    x,y,w,h=v['box']
    if key in ('A_door','bath_door'): hinge=(x,y);angle=-90;radius=w
    elif key=='master_bath_door':hinge=(x,y+h);angle=180;radius=h
    elif w>h:hinge=(x,y+h);angle=0;radius=w
    else:hinge=(x+w,y);angle=0;radius=h
    DOOR_MODEL[key]={'hinge':hinge,'start_deg':angle,'sweep_deg':90,'leaf_mm':radius,'thickness_mm':35,'height_mm':None,'direction':'图示内开估读，现场核铰侧'}

def sector_hit(d,b):
    # Exact quarter-sector / axis-aligned rectangle test; no discrete-angle sampling.
    hx,hy=d['hinge'];r=d['leaf_mm']+d['thickness_mm']/2
    theta=math.radians(d['start_deg']);c=round(math.cos(theta));s=round(math.sin(theta))
    pts=[((x-hx)*c+(y-hy)*s,-(x-hx)*s+(y-hy)*c) for x in (b[0],b[0]+b[2]) for y in (b[1],b[1]+b[3])]
    lo=[min(p[i] for p in pts) for i in (0,1)];hi=[max(p[i] for p in pts) for i in (0,1)]
    if min(hi)<0:return False
    return max(0,lo[0])**2+max(0,lo[1])**2<r*r

def door_graphic(key):
    d=DOOR_MODEL[key];x,y=d['hinge'];r=d['leaf_mm'];a=math.radians(d['start_deg']);b=a+math.pi/2
    x1,y1=x+r*math.cos(a),y+r*math.sin(a);x2,y2=x+r*math.cos(b),y+r*math.sin(b)
    return f'<path data-door-sweep="{key}" d="M{x},{y} L{x1},{y1} A{r},{r} 0 0 1 {x2},{y2} Z" fill="#ac6537" fill-opacity=".09" stroke="#ac6537" stroke-width="12"/>'+line([(x,y),(x2,y2)],AMBER,25)

def section_cut():
    return line([(-2250,4200),(-2250,6000)],RED,22,'130 50 25 50')+text(-2410,4150,'A',200,RED)+text(-2410,6150,'A →12',200,RED)

# Candidate support at table ends; rails are above knee height only if manufacturer confirms.
def table_supports(seats):
    x,y,w,h=BOXES[f'table{seats}']
    return [(x+15,y+330,70,140),(x+w-85,y+330,70,140)]
def knee_boxes(seats):
    x,y,w,h=BOXES[f'table{seats}']
    return [(c[0],yy,500,300) for c in chairs(seats)[:seats//2] for yy in (y,y+h-300)]

def robot_svg():
    p=start('R10.1 机器人基站核验 · R01主选研究 / L02备选',850)
    data=base64.b64encode((Path(__file__).resolve().parent.parent/'IMG20260907-094631119.jpg').read_bytes()).decode()
    p += [text(255,75,'公卫原图局部（未重画未知洁具）',17),f'<svg x="40" y="95" width="410" height="240" viewBox="487 385 125 88"><image href="data:image/jpeg;base64,{data}" width="1170" height="878"/></svg>']
    content=architecture()+obj('R01',HOUSE['robot_alt'],'none',BLUE,'90 45')
    content+=obj('R01-front-trial',(650,-1590,550,600),'none',GREEN,'30 50')
    content+=line([(-400,-1100),(-400,-1700),(400,-1700),(400,-1400),(925,-1400),(925,-1590)],BLUE,25,'65 40')
    content+=text(930,-2100,'R01 550×450？',130,BLUE)
    p.append('<svg x="35" y="355" width="440" height="290" viewBox="-1000 -2900 2900 2100">'+project('<g stroke-width="14">'+content+'</g>',0,0,1)+'</svg>')
    content=architecture()+obj('L01',HOUSE['laundry'],'#e3e8de')+obj('L02-rejected',HOUSE['robot'],'none',RED,'90 45')
    content+=obj('laundry-front',(4216,-1840,750,900),'none',GREEN,'30 50')
    content+=line([(4300,-450),(4950,0),(4300,0),(4950,-450)],RED,22)
    p.append('<svg x="510" y="100" width="250" height="340" viewBox="3800 -2900 1550 3150">'+project('<g stroke-width="14">'+content+'</g>',0,0,1)+'</svg>')
    notes=['L02旧650×450与门扇扫掠冲突。','红叉仅作反例，完成图不落实设备。','洗烘前场900为维护试排，非厂家值。','须核门扇完整开启、装卸、过滤器、','600衣篮转向与两机分别搬出。','候选位置不得借用以上包络。']
    p += [text(940,120+i*40,t,13,AMBER) for i,t in enumerate(notes)]
    notes=['R01尚未成立：东北角白色洁具轮廓可辨，类型、边界及其余洁具均待测。',
      '原图不支持确认淋浴、马桶、台盆及干湿分隔；不移动洁具、不改变湿区。',
      '蓝虚线为机器人开门进出试线；绿点框为托盘前抽600试排，阀门须朝可达前面。',
      'R01前抽试排穿南墙：当前朝向不成立；门槛、越障、阀门手位及防溅条件待核。',
      '图例：实线实体；蓝虚线主选？；红叉虚线旧备选冲突；绿点线操作；棕扇形门扫掠。',
      '管线见03/10/13图；灰细实线为文字引线。两处均未确认安装，不凭3.7㎡面积判定。']
    p += [text(575,665+i*29,t,14,AMBER if i<2 else INK) for i,t in enumerate(notes)]
    return ''.join(p+['</g></svg>'])

def connection_svg():
    p=start('R10.1 岛桌连接 · 独立支承 / 西伸200 / 可拆收口',820)
    for seats,ox in [(4,50),(6,600)]:
        content=obj('island',BOXES['island'],'#d8decf')+obj('table',BOXES[f'table{seats}'],'none')
        for i,b in enumerate(table_supports(seats)):content+=obj(f'leg-{seats}-{i}',b,'#ac6537')
        for i,b in enumerate(knee_boxes(seats)):content+=obj(f'knee-{seats}-{i}',b,'none',GREEN,'30 30')
        x,y,w,h=BOXES[f'table{seats}'];content+=obj('rail',(x+100,540,w-200,120),'none',BLUE,'70 40')
        p.append(f'<svg x="{ox}" y="110" width="490" height="200" viewBox="1000 50 3100 1150">'+project('<g stroke-width="14">'+content+'</g>',0,0,1)+'</svg>')
        p.append(text(ox+245,85,f'{seats}人：棕色独立桌脚 / 绿色膝部候选',15))
    p += [line([(100,555),(1040,555)],INK,3),rect(150,420,490,20,'#d8decf'),rect(640,370,280,185,'#d8decf'),
      rect(175,440,18,115,'#ac6537'),rect(605,440,18,115,'#ac6537'),rect(195,445,395,14,'none',BLUE,'6 4'),
      text(390,400,'桌高约750；轨道置膝部上方，净高待厂家',15),text(790,355,'岛高850–900',16),
      line([(150,470),(100,470)],BLUE,3),text(205,500,'← 西伸200',14,BLUE),
      rect(940,365,12,190,'#bec9be'),line([(920,387),(940,387)],AMBER,4),text(990,340,'76可拆收口',14,AMBER)]
    notes=['桌脚70×140、膝部500×300为平面候选包络，四／六人分别校验；桌脚随西端伸展。',
      '轨道平面120宽，须核桌下净高、横梁和人体大腿；不得将固定岛台当未经核算的悬挑支点。',
      '连接只作定位/防缝意图：独立支承承重，抗倾覆、紧固件、伸缩锁止及承载由厂家核算。',
      '岛东76mm采用可拆收口；可清洁、不封死管线，北侧柜门留水槽阀门及存水弯检修。',
      '绿色膝部与桌腿平面未相交≠三维舒适；维护开启与人位不得借用携篮通道，使用须错时。',
      '岛坐标(2900,225)固定；四人桌(1300,200)，六人桌(1100,200)，均800深。']
    p += [text(575,615+i*31,t,14,AMBER if i in (1,2,4) else INK) for i,t in enumerate(notes)]
    return ''.join(p+['</g></svg>'])


def detail_metrics():
    findings=[]
    for door,d in DOOR_MODEL.items():
        for ident,box in {**HOUSE,**FAMILY}.items():
            if ident.endswith('door'):continue
            if sector_hit(d,box):
                findings.append({'objects':[door,ident],'state':'门扇0–90°连续扫掠，铰侧估读','radial_margin_mm':round(math.hypot(max(box[0]-d['hinge'][0],0,d['hinge'][0]-box[0]-box[2]),max(box[1]-d['hinge'][1],0,d['hinge'][1]-box[1]-box[3]))-d['leaf_mm']-d['thickness_mm']/2,2),'overlap':True,'action':'旧L02取消落实；其余核铰侧/尺寸，不自动移物'})
    ac=[]
    for ident,wall,bay in [('AC02','A_east',None),('AC03','B_east2','B_bay')]:
        x,y,w,h=AC[ident];wx,wy,ww,wh=WALLS[wall]
        ac.append({'objects':[ident,wall], 'state':'高位背板800沿东墙，深240向西',
          'wall_segment_contains_backplate':x+w==wx and wy<=y and y+h<=wy+wh,
          'bay_margin_mm':y-(OPENINGS[bay]['box'][1]+OPENINGS[bay]['box'][3]) if bay else None,
          'height_mm':None,'floor_furniture_height_mm':None,'height_assessment':'高位机身独立层；落地家具平面相交不直接判碰，三维高度待核','maintenance_clearance_mm':None,'action':'安装高度/维护净距待厂家，实墙待测'})
    support=[]
    for n in (4,6):
        support.append({'seats':n,'legs':table_supports(n),'knees':knee_boxes(n),'plan_intersections':[(i,j) for i,a in enumerate(table_supports(n)) for j,b in enumerate(knee_boxes(n)) if intersection(a,b)],'rail_height_mm':None,'action':'膝高/轨道/荷载待厂家；检修与通行错时'})
    local=min(c[1] for c in chairs(6))- (BOXES['dishwasher_operator'][1]+BOXES['dishwasher_operator'][3])
    return {'robot_front':{'objects':['R01-front','bath_south2'],'state':'托盘前抽600试排','wall_intersection':intersection((650,-1590,550,600),WALLS['bath_south2']),'action':'前抽试排穿南墙，当前朝向尚未成立，需实测另核朝向，不移动洁具'},'door_sweeps':findings,'door_model':DOOR_MODEL,'ac_backplates':ac,'supports':support,
      'bottleneck':{'objects':['north_seated_chairs','dishwasher_operator','basket'],'state':'就座＋装卸＋600衣篮','gap_mm':local,'basket_mm':600,'remaining_mm':local-600,'action':'合计余24不作为舒适通行；携篮与装卸错时'},
      'site_pending':['R01洁具、干湿界、门槛、托盘/阀门前场：尚未成立','L02完整开门、洗烘装卸/过滤器/搬机/携篮转向：旧位冲突','岛槽真实管件、水封、清扫口及W0标高：重力排水未成立','AC01梁/窗头/窗帘/灯具/投影，J拆出尺寸与S站人净高','桌轨道膝高、承载及76可拆收口检修']}

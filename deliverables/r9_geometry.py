"""R9 shared trial geometry. Millimetres; origins/wall faces are not surveyed.

Room colour has no stroke. Retained and proposed removal segments are explicit.
The same objects are projected in the whole-house and enlarged drawings.
"""
import html
import math

INK, GREEN, BLUE, AMBER, RED = '#233d36', '#287361', '#427f9a', '#ac6537', '#b34539'
C_WIDTH, C_DEPTH = 3976, 2998
BOXES = {
    'sink': (3200,-2844,776,600), 'prep': (2400,-2844,800,600),
    'hob': (1600,-2844,800,600), 'dishwasher': (2600,-2844,600,600),
    'dishwasher_door': (2600,-2244,600,650),
    'dishwasher_operator': (2600,-1594,600,600),
    'island': (1600,-1544,1000,750),
    'table4': (1476,-794,800,1600), 'table6': (1476,-794,800,1800),
    'fridge': (100,2248,975,750), 'tower': (1075,2398,600,600),
    'coffee': (1675,2398,1300,600), 'pantry': (2975,2398,901,600),
    'fridge_door': (100,1760.5,975,487.5),
    'fridge_drawer': (160,1648,855,600),
    'fridge_operator': (100,1048,975,600),
    'oven_door': (1075,1848,600,550), 'steam_door': (1075,1848,600,550),
    'tower_operator': (1075,1248,600,600),
    'coffee_drawer': (1675,1898,1300,500),
    'coffee_operator': (1675,1298,1300,600),
    'pantry_door': (2975,1948,901,450),
    'pantry_operator': (2975,1348,901,600),
}
# Existing heavy ends and C/D wall are never removed. Door openings are gaps.
WALLS = [
    ('bath_south_west',(-800,-1110,-500,-1110),True),
    ('bath_south_east',(200,-1110,1600,-1110),True),
    ('bath_east',(1600,-2844,1600,-1110),True),
    ('kitchen_north',(1600,-2844,3976,-2844),True),
    ('balcony_divider_north',(3976,-2844,3976,-1550),True),
    ('balcony_divider_south',(3976,-650,3976,0),True),
    ('dining_north_end',(0,0,180,0),True),
    ('dining_east',(3976,0,3976,2998),True),
    ('cd',(0,2998,3976,2998),True),
    ('dining_west_south_end',(0,2818,0,2998),True),
    ('M01',(900,0,3976,0),False),
    ('M02',(1600,-1110,1600,-850),False),
    ('M03',(0,0,0,2818),False),
]
FAMILY = {'deep':(0,0,650,2000),'desk':(1100,0,1800,700),
          'books':(1100,0,1800,280),'chair':(1700,900,600,800),
          'deep_door':(650,0,600,2000),'shoe':(0,3350,1100,350),
          'shoe_door':(0,3700,1100,350)}
AC = {'AC01':(125,520,90,18), 'AC02':(584,175,10,40),
      'AC03':(460,360,10,32),'AC04':(278,816,10,32),
      'AC05':(243,247,40,10)}
HOUSEKEEPING_PATH=[(-650,-650),(-350,-650),(-350,1327),(3588,1327),(3588,-1100),(4500,-1100)]

def chairs(seats,pulled=False):
    x,y,w,h=BOXES[f'table{seats}']; d=800 if pulled else 450
    return [(xx,y+h*(i+.5)/(seats//2)-250,d,500)
            for xx in (x-d,x+w) for i in range(seats//2)]

def intersection(a,b):
    x,y=max(a[0],b[0]),max(a[1],b[1])
    w,h=min(a[0]+a[2],b[0]+b[2])-x,min(a[1]+a[3],b[1]+b[3])-y
    return (x,y,w,h) if w>0 and h>0 else None

def swept_boxes(points,width):
    """Conservative square 600 mm basket swept along orthogonal route segments."""
    r=width/2
    result=[]
    for (x1,y1),(x2,y2) in zip(points,points[1:]):
        assert x1==x2 or y1==y2
        result.append((min(x1,x2)-r,min(y1,y2)-r,abs(x2-x1)+width,abs(y2-y1)+width))
    return result

def route_metrics():
    solids=['sink','prep','hob','island','table6','fridge','tower','coffee','pantry',
            'fridge_door','fridge_drawer','oven_door','steam_door','coffee_drawer','pantry_door','dishwasher_door']
    sweeps=swept_boxes(HOUSEKEEPING_PATH,600)
    collisions=[k for k in solids if any(intersection(s,BOXES[k]) for s in sweeps)]
    chairs_hit=any(intersection(s,c) for s in sweeps for c in chairs(6,True))
    walls_hit=[]
    for ident,(x1,y1,x2,y2),keep in WALLS:
        if keep:
            wall=(min(x1,x2)-30,min(y1,y2)-30,abs(x2-x1)+60,abs(y2-y1)+60)
            if any(intersection(s,wall) for s in sweeps):walls_hit.append(ident)
    operators=[k for k in ['fridge_operator','tower_operator','coffee_operator','pantry_operator','dishwasher_operator']
               if any(intersection(s,BOXES[k]) for s in sweeps)]
    return {'basket_mm':600,'door_only_swept_collisions':collisions,'pulled_chair_collision':chairs_hit,
            'retained_wall_collisions':walls_hit,'concurrent_operator_conflicts':operators,
            'simultaneous_operation_and_passage_verified':False}

def trial_metrics():
    occupied=['fridge_door','fridge_drawer','fridge_operator','oven_door',
              'steam_door','tower_operator','coffee_drawer','coffee_operator',
              'pantry_door','pantry_operator','dishwasher_door','dishwasher_operator']
    collisions=[(s,k) for s in (4,6) for k in occupied
                if any(intersection(c,BOXES[k]) for c in chairs(s,True))]
    b=BOXES; bottom=lambda key:b[key][1]+b[key][3]
    table_end=bottom('table6'); dw_right=b['dishwasher_door'][0]+b['dishwasher_door'][2]
    return {'units':'mm; trial, not surveyed', 'prep_surface':b['prep'][2],
        'island_north_in_original_kitchen':-b['island'][1],
        'counter_to_island_operation':b['island'][1]-bottom('prep'),
        'island_table_left_offset':b['table4'][0]-b['island'][0],
        'east_seated_passage':C_WIDTH-max(c[0]+c[2] for c in chairs(6)),
        'east_pulled_passage':C_WIDTH-max(c[0]+c[2] for c in chairs(6,True)),
        'south_four_to_fridge_face':b['fridge'][1]-bottom('table4'),
        'south_six_to_fridge_face':b['fridge'][1]-table_end,
        'fridge_drawer_projection':b['fridge_drawer'][3],'fridge_operator_depth':b['fridge_operator'][3],
        'fridge_front_residual_not_passage':b['fridge_operator'][1]-table_end,
        'fridge_operator_to_six_pulled_chair_y':b['fridge_operator'][1]-max(c[1]+c[3] for c in chairs(6,True)),
        'south_crossing_doors_open_no_operator':b['fridge_drawer'][1]-table_end,
        'south_crossing_with_fridge_operator_is_passage':False,
        'dishwasher_door_projection':b['dishwasher_door'][3],'dishwasher_operator_depth':b['dishwasher_operator'][3],
        'dishwasher_east_bypass':C_WIDTH-dw_right,
        'basket_trial_width':600,'basket_bypass_total_margin':176,
        'family_east_passage':4100-2900,
        'occupied_chair_collisions':collisions,
        'dishwasher_island_collision':bool(intersection(BOXES['island'],BOXES['dishwasher_operator'])),
        'housekeeping_route':route_metrics(),
        'site_verified':False}

def text(x,y,s,size=15,color=INK,anchor='middle'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}">{html.escape(str(s))}</text>'

def rect(x,y,w,h,fill='none',stroke=INK,dash=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-dasharray="{dash}"/>'

def line(points,color=INK,width=2,dash=''):
    return f'<polyline points="'+ ' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}"/>'

def start(title,h=760,w=1150):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(title)}"><title>{html.escape(title)}</title><g font-family="Microsoft YaHei, sans-serif">',text(w/2,28,title,22)]

def kitchen(ox,oy,scale,seats=4,opened=False,alter=False,routes=False,labels=True):
    def xy(x,y): return ox+x*scale,oy+y*scale
    def box(b,fill='none',stroke=INK,dash=''):
        x,y=xy(*b[:2]); return rect(x,y,b[2]*scale,b[3]*scale,fill,stroke,dash)
    def label(x,y,s,color=INK): return text(*xy(x,y),s,10 if scale<.09 else 12,color)
    p=[box((0,0,3976,2998),'#f7efdf','none'),box((1600,-2844,2376,2844),'#e8eff0','none')]
    for ident,(x1,y1,x2,y2),keep in WALLS:
        if keep or alter:
            p.append(f'<g data-wall="{ident}" data-retained="{str(keep).lower()}">'+line([xy(x1,y1),xy(x2,y2)],INK if keep else RED,4 if keep else 3,'' if keep else '6 4')+'</g>')
    # Former room boundary is intentionally absent in completed drawings.
    for k,s in [('sink','水槽'),('prep','净备菜800'),('hob','灶'),('island','干岛1000×750'),
                (f'table{seats}',f'{1600 if seats==4 else 1800}×800'),
                ('fridge','冰箱↑'),('tower','蒸/烤↑'),('coffee','咖啡↑'),('pantry','食品↑')]:
        b=BOXES[k];p.append(f'<g data-object="{k}">'+box(b,'#d8decf')+'</g>')
        if labels:p.append(label(b[0]+b[2]/2,b[1]+b[3]/2+50,s))
    for b in chairs(seats,True):p.append(box(b,'none',AMBER,'3 3'))
    for b in chairs(seats):p.append(box(b,'#fff','#ac936d'))
    if opened:
        for k in ['fridge_door','fridge_drawer','oven_door','steam_door','coffee_drawer','pantry_door','dishwasher_door']:
            p.append(box(BOXES[k],'none',AMBER,'5 3'))
        if not routes:
            for k in ['fridge_operator','tower_operator','coffee_operator','pantry_operator','dishwasher_operator']:
                p.append(box(BOXES[k],'none',GREEN,'3 3'))
        # Flush-hinge 90 degree door trial; both leaves plus drawer are shown.
        fx,fy,fw,_=BOXES['fridge']; fy=2248
        for hx,sign in [(fx,1),(fx+fw,-1)]:
            pts=[xy(hx+sign*(fw/2)*math.cos(math.radians(a)),fy-(fw/2)*math.sin(math.radians(a))) for a in range(0,91,5)]
            p.append(line([xy(hx,fy)]+pts+[xy(hx,fy)],AMBER,1,'3 2'))
    if routes:
        p.append(line([xy(*q) for q in HOUSEKEEPING_PATH], '#e8d3ca',600*scale))
        paths=[('①', [(-650,1200),(-350,1400),(550,1400)],GREEN),
               ('②',[(550,1400),(-350,1400),(-350,1327),(3588,1327),(3588,-1950),(2800,-1950),(1950,-1950)],BLUE),
               ('③',[(3500,-2000),(3450,-1750),(2050,-1750)],GREEN),
               ('④',[(2100,-1800),(3300,-1800),(3500,-650),(2800,-450)],AMBER),
               ('⑤',[(2800,300),(3488,300),(3488,-1950)],BLUE),
               ('⑥',[(3488,1100),(2300,1550)],GREEN),
               ('⑦',HOUSEKEEPING_PATH,RED)]
        for n,pts,col in paths:
            p.append(line([xy(*q) for q in pts],col,2,'5 3'));p.append(label(*pts[-1],n,col))
    return ''.join(p)

def island_svg():
    p=start('R9 四人 / 六人：岛台北移，南墙整排柜',720)
    p += [text(280,60,'四人 · 就座实线 / 拉椅虚线',18),text(860,60,'六人 · 无端头椅 / 东侧通行900',18),
          kitchen(85,330,.072,4),kitchen(665,330,.072,6)]
    notes=['统一算例：岛北端 y=-1544；桌 x=1476，y=-794；六人桌尾 y=1006。',
           '东侧就座余1250 / 拉椅余900；六人桌尾至冰箱面1242。房间图注并非实测净宽。',
           '北侧厨台至岛仅700：单人操作带；不计作双人通道。主要备菜仍留上部800净面。',
           '拆开西侧后可由客餐过渡区取冰箱；家具不进入西侧沙发与投影休息区。',
           '整排柜：西端余量100＋冰箱975＋蒸烤600＋咖啡1300＋食品901＋东端100＝3976（初排）。']
    p += [text(575,590+i*26,v,14,AMBER if i in (2,4) else INK) for i,v in enumerate(notes)]
    return ''.join(p+['</g></svg>'])

def clearance_svg():
    p=start('R9 满开：门 / 抽屉（橙）与操作站位（绿）分别绘制',760)
    p += [kitchen(110,340,.09,6,True),text(860,100,'同一位置叠加不同使用状态',20)]
    notes=['冰箱门朝北：双门90°齐平铰链算例。','必须选可在该角度全抽的机型；否则改柜模块。',
           '门弧487.5；抽屉600；前方人位600。','六人桌尾至冰箱面1242，扣1200只余42。',
           '42不是通道；冰箱由西侧开放口到达。','下烤箱、上蒸箱分别开门550，共用投影。',
           '取热盘人位600；两台均可单独检修。','咖啡抽屉500＋人位600；取水箱不得顶吊柜。',
           '洗碗门650＋装卸600，岛在其西侧。','东侧绕行776；600宽衣篮两侧合计余176。',
           '该段不足900舒适目标，装卸时应单人通过。','满开状态无柜椅相交；不代表多人同时操作。',
           '设备包络按厂家安装图替换后重算。']
    p += [text(850,150+i*38,v,14,AMBER if i in (3,9,10,12) else INK) for i,v in enumerate(notes)]
    p += [text(575,731,'墙面原点、阳台B门洞900及设备尺寸均为算例；净宽、门扇与携篮转弯须现场放样。',15,AMBER)]
    return ''.join(p+['</g></svg>'])

def workflow_svg():
    p=start('R9 七类动线：开放餐厨，主通路与工作站分开',740)
    p += [kitchen(110,330,.088,6,True,routes=True)]
    notes=['① 归家 → 西侧开放口 → 冰箱 / 食品',
           '② 冰箱 → 水槽 → 净备菜800 → 灶',
           '③ 水槽 → 岛台补充备餐（北侧单人）',
           '④ 灶 → 岛台摆盘 → 餐桌东侧',
           '⑤ 收餐 → 东侧900 → 水槽 / 洗碗',
           '⑥ 客餐区 → 南墙咖啡；取水回上部',
           '⑦ 入户 → 桌南横向绕行 → 阳台B',
           '冰箱离水槽更远：接受跨餐厨取菜。',
           '门全开、无人取物：桌南横向余642。',
           '南墙设备前站人时，该横向通路受阻。',
           '浅色带为600衣篮，无人取物状态；',
           '当前布局不具备该处同时操作与通行。']
    p += [text(858,120+i*41,v,15,AMBER if i>6 else INK) for i,v in enumerate(notes)]
    return ''.join(p+[text(575,715,'西侧路线限客餐过渡带；保留粗墙端部、公卫、C/D墙及客厅投影路线。',15),'</g></svg>'])

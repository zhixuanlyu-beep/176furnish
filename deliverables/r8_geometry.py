"""R8 dimensional trial, in mm. Only source spans are known; origins are assumptions.

These shared boxes keep dining, opening and route drawings consistent. They are
not a survey or a manufacturer installation model.
"""
import html
import math

INK, GREEN, BLUE, AMBER, RED = '#233d36', '#287361', '#427f9a', '#ac6537', '#b34539'
C_WIDTH, C_DEPTH = 3976, 2998
PARTITION_Y = -910  # trial: 200 mm south of assumed bathroom south face
BOXES = {
    'fridge': (600, -1110, 950, 750),
    'fridge_front': (600, -360, 950, 1300),
    'sink': (1600, -2844, 750, 600),
    'prep': (2350, -2844, 750, 600),
    'hob': (3100, -2844, 876, 600),
    'dishwasher': (2350, -2844, 600, 600),
    'dishwasher_door': (2350, -2244, 600, 650),
    'dishwasher_operator': (2350, -1594, 600, 600),
    'island': (1900, 200, 1000, 750),
    'table4': (2150, 950, 800, 1600),
    'table6': (2150, 950, 800, 1800),
    'coffee': (0, 2398, 1300, 600),
    'coffee_operator': (0, 1498, 1300, 900),
}


def chairs(seats, pulled=False):
    """500 mm chair width; 450 seated / 800 pulled depth from table edge."""
    tx, ty, tw, th = BOXES[f'table{seats}']
    depth = 800 if pulled else 450
    centers = [ty + th * (i + .5) / (seats // 2) for i in range(seats // 2)]
    return [(x, y-250, depth, 500) for x in (tx-depth, tx+tw) for y in centers]


def intersection(a, b):
    x, y = max(a[0], b[0]), max(a[1], b[1])
    w = min(a[0]+a[2], b[0]+b[2])-x
    h = min(a[1]+a[3], b[1]+b[3])-y
    return (x, y, w, h) if w > 0 and h > 0 else None


def trial_metrics():
    return {
        'units': 'mm; unmeasured trial coordinates, not site clearances',
        'prep_surface': BOXES['prep'][2],
        'partition_shift_from_assumed_bath_south': 200,
        'island_to_closed_partition': BOXES['island'][1]-PARTITION_Y,
        'island_table_left_offset': BOXES['table4'][0]-BOXES['island'][0],
        'east_gap_seated': C_WIDTH-(BOXES['table4'][0]+800+450),
        'east_gap_pulled': C_WIDTH-(BOXES['table4'][0]+800+800),
        'south_gap_four': C_DEPTH-(BOXES['table4'][1]+1600),
        'south_gap_six': C_DEPTH-(BOXES['table6'][1]+1800),
        'dishwasher_operator_to_partition': PARTITION_Y-(-1594+600),
        'fridge_front_to_first_six_chair': min(b[1] for b in chairs(6, True))-940,
        'coffee_to_west_pulled_chair': min(b[0] for b in chairs(6, True))-1300,
        'chair_clear_of_fridge_front': all(not intersection(b, BOXES['fridge_front']) for s in (4, 6) for b in chairs(s, True)),
        'chair_clear_of_coffee_work_zone': all(not intersection(b, BOXES['coffee_operator']) for s in (4, 6) for b in chairs(s, True)),
        'site_verified': False,
    }


def text(x, y, label, size=15, color=INK, anchor='middle'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}">{html.escape(label)}</text>'


def rect(x, y, w, h, fill='none', stroke=INK, dash=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-dasharray="{dash}"/>'


def start(title, height=750):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1150 {height}" role="img" aria-label="{html.escape(title)}"><title>{html.escape(title)}</title><defs><marker id="route-arrow" markerWidth="7" markerHeight="7" refX="5" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="{GREEN}"/></marker></defs><g font-family="Microsoft YaHei, sans-serif">', text(575, 28, title, 22)]


def panel(ox, oy, seats=4, opened=False, routes=False):
    """Uniform 0.071 scale inside each trial plan (not in whole-house diagram)."""
    s = .071
    def xy(x, y):
        return ox + (x+700)*s, oy + (y+2844)*s
    def box(b, fill='none', stroke=INK, dash=''):
        x, y = xy(b[0], b[1])
        return rect(x, y, b[2]*s, b[3]*s, fill, stroke, dash)
    def label(x, y, v, color=INK, size=11):
        return text(*xy(x,y), v, size, color)
    def path(points, color=GREEN, dash='5 3', arrow=False):
        pts=' '.join(f'{x},{y}' for x,y in (xy(*p) for p in points))
        return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2" stroke-dasharray="{dash}"'+(' marker-end="url(#route-arrow)"' if arrow else '')+'/>'
    p=[box((0, 0, C_WIDTH, C_DEPTH), '#f7efdf'), box((1600, -2844, 2376, 2844), '#e8eff0'), box((-700,-2844,2300,1734),'#e2ecee'), label(400,-1800,'公卫（轮廓待测）'), label(-430,-1000,'门'), label(4600,-1000,'阳台B'), label(-450,1200,'客厅'), label(2000,3230,'C/D保留墙 · 上北下南')]
    p += [path([(-650,-1110),(1600,-1110)], INK, ''), label(1000,-1260,'南墙东段'), path([(0,0),(3976,0)], '#96a59c', '3 4'), label(650,180,'原厨房/C边界',BLUE,10)]
    for k, v in [('sink','水槽'),('prep','备菜750'),('hob','灶'),('fridge','冰箱↓'),('island','岛1000×750'),(f'table{seats}',f'桌{1600 if seats==4 else 1800}×800'),('coffee','咖啡柜↑')]:
        b=BOXES[k]
        p += [box(b, '#d8decf' if k!='coffee' else '#ead5b7'),label(b[0]+b[2]/2,b[1]+b[3]/2+45,v,size=10)]
    p += [label(2650,-2050,'洗碗机在备菜台下',BLUE,10),box(BOXES['fridge_front'],'none',AMBER,'4 3'), label(1040,650,'前场1300',AMBER,10),box(BOXES['coffee_operator'],'none',GREEN,'4 3'),label(640,1850,'咖啡站位900',GREEN,10)]
    for b in chairs(seats,True):
        p.append(box(b,'none',AMBER,'3 3'))
    for b in chairs(seats):
        p.append(box(b,'#fff','#ac936d'))
    # Closing line plus hypothetical returns: all open kitchen faces must enclose.
    p += [path([(1600,-1110),(1600,PARTITION_Y),(3976,PARTITION_Y)],BLUE,'5 4' if opened else ''),label(2820,-680,'分隔开启' if opened else '分隔关闭',BLUE,11)]
    # Stacked leaves are provisional footprints, never an approved door system.
    p += [box((1600,PARTITION_Y-160,180,160),'#bad4df',BLUE),box((3796,PARTITION_Y-160,180,160),'#bad4df',BLUE)]
    p += [label(2850,-1160,'收门框/端部回折待门厂确认',BLUE,9)]
    p += [path([(3850,1150),(3850,2600)],RED,''),label(4480,2100,'拉椅余226',RED,11),label(4490,2350,'非通行带',RED,11),label(2450,2920,'桌尾余248' if seats==6 else '桌尾余448',RED,10)]
    if routes:
        p += [path([(-600,-700),(-100,1050),(1100,1050)],GREEN,arrow=True), label(-100,700,'①取菜',GREEN,10), path([(1560,200),(1800,-500),(1970,-1900),(2700,-1900),(3500,-1900)],GREEN,arrow=True),label(3270,-1600,'②洗切炒',GREEN,10)]
        p += [path([(3450,-1750),(3400,-400),(3000,80),(2800,400),(2650,1100)],GREEN,arrow=True),label(3400,520,'③摆盘上菜',GREEN,10),path([(2100,1800),(1790,1350),(1700,-400),(2100,-1850)],AMBER,arrow=True),label(1500,1520,'④收餐',AMBER,10)]
        p += [path([(-400,2100),(650,2100)],GREEN,arrow=True),label(50,2300,'⑤咖啡',GREEN,10),path([(1800,-300),(4400,-300),(4400,-900)],GREEN,arrow=True),label(4380,200,'⑥家政',GREEN,10),path([(2050,-1800),(1800,-200),(2150,500),(3300,-1600)],BLUE,arrow=True)]
        p += [label(1200,1130,'转弯冲突待核',RED,10),label(4300,-600,'门洞待核',RED,10)]
    return ''.join(p)


def island_svg():
    p=start('R8 岛北桌南：四人 / 六人及拉椅占用',680)
    p += [text(280,60,'四人 · 1600桌 / 分隔开启',18),text(850,60,'六人 · 延伸1800 / 分隔关闭',18),panel(45,80,4,True),panel(615,80,6,False)]
    p += [text(575,535,'实线椅：500宽×450就座深；橙虚线：拉出占深800（均为算例，须换成实物）。',15),text(575,565,'岛桌左边错位250仅为本次试排；随冰箱前场、阳台通路与椅型重排，不固定400。',15),text(575,595,'冲突：东侧就座后仅余576、拉椅后226；六人桌尾248，均不能标为900通道。',16,RED),text(575,625,'椅包络避开冰箱前场与咖啡站位，但边缘仅余60 / 50；通行和转弯仍未成立。',15,RED),text(575,654,'局部家具按同一mm试排；墙体原点/厚度为假设。原图3976、2998、2844不是净尺寸。',14,AMBER),'</g></svg>']
    return ''.join(p)


def clearance_svg():
    p=start('R8 设备满开包络：门扇、抽屉与装卸站位分开',650)
    # Local refrigerator detail, one pixel = 2.5 mm.
    s=.22
    ox,oy=130,100
    def b(x,y,w,h,fill='none',stroke=INK,dash=''):
        return rect(ox+x*s,oy+y*s,w*s,h*s,fill,stroke,dash)
    p += [text(285,65,'冰箱背靠公卫南墙东段 · 门朝南',18),b(-120,-20,1200,20,'#68736b'),b(0,0,950,750,'#ccd9cc'),text(235,192,'柜宽950 / 深750试排',14),b(0,750,950,1300,'none',AMBER,'5 4')]
    for hx, sign in [(0,1),(950,-1)]:
        # Two 475 mm leaves rotate 120 degrees from their closed positions.
        points=[]
        for angle in range(0,121,3):
            t=math.radians(angle)
            points.append((ox+(hx+sign*475*math.cos(t))*s,oy+(750+475*math.sin(t))*s))
        hinge=(ox+hx*s,oy+750*s)
        pts=' '.join(f'{x:.2f},{y:.2f}' for x,y in [hinge]+points+[hinge])
        p += [f'<polygon points="{pts}" fill="#f6e9d6" fill-opacity=".65" stroke="{AMBER}" stroke-dasharray="4 3"/>']
    p += [b(60,750,830,600,'none',BLUE,'4 3'),text(236,337,'抽屉拉出600算例',13,BLUE),b(100,1350,750,600,'#eef1e7',GREEN,'4 3'),text(234,466,'站位600',14,GREEN),text(427,344,'门120°算例',14,AMBER),text(422,375,'侧向超出约238',13,AMBER),text(422,404,'左右分别另留',13,AMBER),text(285,575,'全开角、抽屉、背部散热和把手均按型号替换。',14),text(285,602,'柜位900–1000起排；1300前场不含独立通行。',14,AMBER)]
    p += [text(857,65,'水槽—备菜—灶连续；洗碗在备菜下',18),rect(620,110,110,100,'#d8decf'),text(675,154,'水槽',17),rect(730,110,140,100,'#d8decf'),text(800,140,'备菜净面750',15),rect(736,162,105,47,'#ead5b7'),text(789,191,'洗碗600',14),rect(870,110,220,100,'#d8decf'),text(980,155,'灶 / 安全余量另核',15)]
    p += [rect(736,210,105,114,'#f6e9d6',AMBER,'5 4'),text(789,264,'门投影P',14,AMBER),text(789,290,'650算例',13,AMBER),rect(736,324,105,105,'#eef1e7',GREEN,'4 3'),text(789,364,'站位S',14,GREEN),text(789,392,'600算例',13,GREEN),rect(620,444,470,4,BLUE,BLUE),text(890,476,'关闭线距台前1334算例，P＋S后仅余84',14,RED),text(957,345,'侧方进出',14),text(957,372,'独立净宽待测',14),text(857,519,'P＋S＝1250；若身后再通行900，共需2150。',15,RED),text(857,556,'分隔自公卫南墙附近起排，图示向南调200。',14),text(857,588,'全开/全闭均核收门、装卸、燃气及家政门洞。',14)]
    p += [text(575,634,'满开算例不是候选机型实测；冰箱操作前场禁止咖啡柜和餐椅。全部设备尚未选型。',15,AMBER),'</g></svg>']
    return ''.join(p)


def workflow_svg():
    p=start('R8 动线：日常敞开 / 燃气分隔关闭',650)
    p += [text(280,60,'开启状态 · 七类任务路径示意',18),text(850,60,'关闭状态 · 中厨操作与外侧家政路分核',18),panel(45,80,4,True,True),panel(615,80,6,False,True)]
    p += [text(575,535,'①归家取菜  ②冰箱→水槽→备菜→灶  ③摆盘上菜  ④收餐入洗碗机  ⑤咖啡  ⑥家政',14),text(575,563,'蓝线为大份备餐：水槽→岛台→灶。路线只表达任务关系，交叉和窄口并未通过通行验收。',14,BLUE),text(575,592,'关门时洗切炒在中厨内；取冰箱食材/上菜需经可操作通行门开闭，收门不能撞设备。',14),text(575,622,'家政路能否从分隔南侧直达阳台B，取决于原门洞与回折端；若落入闭合区须开门，列为待核冲突。',14,RED),'</g></svg>']
    return ''.join(p)

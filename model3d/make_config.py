"""One-time, auditable migration from dimension-anchored R10.1 geometry.
build_scene.py only reads the resulting editable JSON; it never imports R10.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'deliverables'))
import r10_geometry as source

def rect(b):
    x, y, w, d = b
    return [x / 1000, -(y + d) / 1000, w / 1000, d / 1000]

walls = {k: rect(v) for k, v in source.WALLS.items()}
# Keep the original structural footprint; supplement the C opening with a pier.
walls['C_west_end'] = rect((-120, 2320, 120, 798))
openings = {k: dict(v, box=rect(v['box'])) for k, v in source.OPENINGS.items()}
for k, width in [('A_door', .9), ('B_door', .9), ('D_door', .9), ('bath_door', .8)]:
    b = openings[k]['box']
    b[2 if b[2] > b[3] else 3] = width
openings['C_west_opening'] = {'box': rect((-120, 120, 120, 2200)), 'kind': 'connected'}
# Kitchen west and south glazed enclosure: former C door remains a leaf-free portal.
openings['former_kitchen_door'] = {'box': rect((1600, -1000, 120, 1000)), 'kind': 'glass_door'}
openings['kitchen_south_glass'] = {'box': rect((1080, 0, 2896, 120)), 'kind': 'glass_partition'}
openings['kitchen_west_glass'] = {'box': rect((1600, -1250, 120, 250)), 'kind': 'glass_partition'}
openings['study_glass'] = {'box': rect((-3410, -3650, 2080, 60)), 'kind': 'glass_partition'}
openings['study_door'] = {'box': rect((-1330, -3650, 850, 60)), 'kind': 'glass_door', 'slide_sign': -1}
openings['study_return'] = {'box': rect((-540, -6147, 60, 2497)), 'kind': 'glass_partition'}
openings['former_kitchen_door']['slide_offset'] = [.09,0,0]
openings['bath_door']['swing_sign'] = -1

rooms_raw = {
 'Bedroom_A': [(-420,-9957,7040,3810)], 'Bath_A':[(-420,-9957,1700,2210)],
 'Bedroom_B':[(640,-6147,3336,3303)], 'Study':[(-3410,-6147,2870,2557)],
 'Hall':[(-480,-6147,1000,2557),(-3410,-3590,3930,866),(-3410,-2724,2510,1594),(-780,-1250,2380,1250)],
 'Bath_Public':[(-780,-2724,2380,1354)], 'Kitchen':[(1720,-2724,2256,2724)],
 'Living':[(-4172,-1130,4052,6270),(-3410,-1250,3290,120)],
 'C_Prep_Dining':[(0,-0,3976,2998)], 'Bedroom_D':[(0,3118,3976,3144)],
 'Balcony_A':[(-4172,5260,3005,1090)], 'Balcony_B':[(4096,-2724,997,2724)]}
# A is L-shaped around the en-suite, with a separate south dressing zone.
rooms_raw['Bedroom_A']=[(1400,-9957,5220,3810),(-420,-7627,1820,1360)]
furniture = {}
def add(k, b, room, kind, height, material='walnut', **extra):
    furniture[k] = dict(box=rect(b), room=room, kind=kind, height=height, material=material, **extra)
for k, room, width in [('bedA','Bedroom_A',1800),('bedB','Bedroom_B',1200),('bedD','Bedroom_D',1500)]:
    b=list(source.HOUSE[k]); b[2]=width
    add(k,b,room,'bed',.6,'linen')
for k,room in [('wardrobeA','Bedroom_A'),('wardrobeB','Bedroom_B'),('wardrobeD','Bedroom_D')]:
    add(k,source.HOUSE[k],room,'cabinet',2.4,'oak')
add('sofa',source.HOUSE['sofa'],'Living','sofa',.85,'linen')
add('coffee_table',(-2600,1720,900,600),'Living','table',.4)
add('screen',(-1150,1000,80,2450),'Living','screen',.08,'warm_white',z=2.2)
add('desk',(-2280,-6147,1700,700),'Study','table',.75)
add('study_chair',(-1400,-5247,500,500),'Study','chair',.8,'olive')
add('study_storage',(-3410,-5350,650,1350),'Study','cabinet',2.3,'oak',front='east')
add('shoe',source.FAMILY['shoe'],'Hall','cabinet',1.1,'oak')
for k in ['fridge','tower','coffee','pantry','island']:
    b=list(source.BOXES[k])
    if k=='coffee': b[2]=1700
    if k=='pantry': b[0]=3375; b[2]=501
    add(k,b,'C_Prep_Dining',k if k in ['fridge','tower'] else 'cabinet',.9 if k in ['coffee','island'] else 2.2)
for n in [4,6]:
    b=list(source.BOXES[f'table{n}']); b[1]=550; b[3]=850
    add(f'table{n}',b,f'Dining_{n}','table',.75,seats=n)
    for i in range(n):
        row=i//(n//2); col=i%(n//2)
        add(f'chair{n}_{i}',(b[0]+b[2]*(col+.5)/(n//2)-250,b[1]-450 if row==0 else b[1]+850,500,450),f'Dining_{n}','chair',.8,'linen',facing='south' if row==0 else 'north')
for k,b in [('hob',(1720,-2724,680,600)),('prep',(2400,-2724,800,600)),('sink',(3200,-2724,776,600))]:
    add(k,b,'Kitchen','cabinet',.9,'olive',front='south')
for room,x,y in [('Bath_A',-350,-9700),('Bath_Public',700,-2680)]:
    add(room+'_basin',(x,y,700,430),room,'basin',.85,'warm_white',status='assumed_fixture_position')
    add(room+'_wc',(x,y+650,400,650),room,'wc',.75,'warm_white',status='assumed_fixture_position')
add('shower_A',(400,-9900,850,850),'Bath_A','shower',2.1,'glass',status='assumed_fixture_position')
add('shower_public',(-750,-2680,850,850),'Bath_Public','shower',2.1,'glass',status='assumed_fixture_position')
add('laundry',source.HOUSE['laundry'],'Balcony_B','laundry',1.8,'warm_white',status='conditional')
add('robot_R01',source.HOUSE['robot_alt'],'Candidate_Equipment','robot',.65,'warm_white',status='unconfirmed_hidden')
add('robot_L02',source.HOUSE['robot'],'Candidate_Equipment','robot',.65,'warm_white',status='rejected_position_hidden')

config = dict(schema_version=1, units='metres', axes='X east, Y north, Z up', origin='C northwest interior reference',
 provenance=dict(image='../IMG20260907-094631119.jpg',layout='../deliverables/r10_geometry.py',
  method='Dimension-line anchored R10 millimetre survey concept, transformed x/1000, -y/1000; no scaling from schematic pixels.',
  dimension_lines_mm=dict(A_depth=3930,B_depth=3423,kitchen_depth=2844,C_depth=2998,D_depth=3264,CD_width=3976),
  boundary_status='Image-estimated wall faces, not surveyed net dimensions; structural classification and beams/columns unverified.'),
 defaults=dict(wall_height=2.8,thick_wall=.22,thin_wall=.12,door_height=2.1,bedroom_door=.9,bath_door=.8,study_door=.85,window_sill=.9,window_height=1.5,bay_sill=.45,bay_height=1.8),
 assumptions=[
  'Existing R10 exterior footprints retain 240mm where already defined; 220mm is the fallback for new thick walls. No structural boundary is trimmed.',
  'Door widths are concept clear openings before detailed frames; positions and hinge sides estimated.',
  'C west opening narrowed to 2200mm by retaining a south pier; header is conceptual, structural design pending.',
  'Kitchen south fixed glazing restores enclosure along removed partition M01; west 1000mm sliding door closes connection. Former C north 900mm portal has no leaf.',
  'Dining table moved 350mm south and deepened 50mm to clear kitchen glass; island remains fixed; table-island overlap along edge is now 425mm.',
  'Coffee enlarged from 1300 to 1700mm in place; pantry reduced from 901 to 501mm, equipment order unchanged.',
  'Study east glass face at X=-480mm leaves a 1000mm route to A; desk shifted 170mm west and deep storage shortened to avoid its working space.',
  'Study glass partitions and all bathroom fixture placements are concept assumptions; existing plumbing positions are not confirmed.',
  'No hidden water, drain, gas or refrigerant routing is modeled. Island sink remains conditional: gravity drain not established.',
  'Beams over openings are placeholders; original structural columns cannot be independently identified from source image.'
 ], walls=walls,openings=openings,rooms={k:[rect(b) for b in v] for k,v in rooms_raw.items()},furniture=furniture,
 materials={'warm_white':[.86,.82,.73,1],'oak':[.64,.43,.23,1],'walnut':[.22,.10,.045,1],'linen':[.69,.61,.48,1],'olive':[.26,.30,.16,1],'brick':[.46,.16,.085,1],'black':[.025,.028,.025,1],'stone':[.73,.70,.61,1],'glass':[.64,.80,.83,.28],'metal':[.4,.42,.43,1]},
 equipment={
 'coffee_machine':dict(water='manual tank',waste='manual drip tray',power=True,top_clearance=.35,front_clearance=.6),
 'grinder':dict(water='none',waste='manual grounds cleaning',power=True,top_clearance=.3),
 'dishwasher':dict(water='fixed supply',waste='fixed sanitary drain',power=True),
 'purifier':dict(water='fixed supply',waste='RO reject to sanitary drain, model pending',power=True),
 'steam_oven':dict(water='manual tank',waste='manual waste box',power=True),
 'oven':dict(water='none',waste='none',power=True),
 'laundry':dict(water='conditional fixed supply',waste='conditional sanitary drain / dryer tank',power=True,status='conditional'),
 'island_sink':dict(water='conditional hot/cold',waste='gravity drain not established',power=False,status='conditional'),
 'robot':dict(water='unconfirmed',waste='unconfirmed',power=True,status='candidate_hidden')},
 cameras={
 '01_Axonometric':{'position':[16,-20,19],'target':[.5,1,0],'ortho':22},
 '02_Top':{'position':[1,1.5,24],'target':[1,1.5,0],'ortho':19},
 '03_Living_to_C':{'position':[-3.7,-2,1.65],'target':[2.2,-1.8,1.1]},
 '04_C_to_Living':{'position':[3.4,-1.7,1.65],'target':[-2.7,-2,1.1]},
 '05_Coffee':{'position':[2.4,-.7,1.6],'target':[2.5,-2.7,1.15]},
 '06_Dining_Kitchen':{'position':[.4,-2.1,1.7],'target':[2.8,1.4,1.05]},
 '07_Study':{'position':[-.2,3.9,1.65],'target':[-2,5.7,1.1]}})
ROOT.mkdir(exist_ok=True)
(ROOT/'scene_config.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

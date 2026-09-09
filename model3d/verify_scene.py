"""Reopen saved blend and import GLB in a fresh Blender background process.
Checks actual object bounds; clearance and door sweeps are conservative envelopes.
Reports design warnings separately from failed artifact integrity checks.
"""
import hashlib
import json
import math
from pathlib import Path
import bpy
from mathutils import Vector
assert bpy.app.background, 'Background only'
ROOT=Path(__file__).resolve().parent
C=json.loads((ROOT/'scene_config.json').read_text(encoding='utf-8'))
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'whole_home.blend'))
scene=bpy.context.scene
checks={};issues=[]
def check(name,condition):checks[name]=bool(condition)
def bounds(o):
    pts=[o.matrix_world@Vector(p) for p in o.bound_box]
    return [min(p[i] for p in pts) for i in range(3)]+[max(p[i] for p in pts) for i in range(3)]
def overlap(a,b,tol=.002):
    d=[min(a[i+3],b[i+3])-max(a[i],b[i]) for i in range(3)]
    return [round(x*1000,1) for x in d] if min(d)>tol else None
def box3(b,z=0,h=2.1):return [b[0],b[1],z,b[0]+b[2],b[1]+b[3],z+h]
def warn(category,objects,detail,action):issues.append(dict(category=category,objects=objects,detail=detail,action=action))
check('blender_background',bpy.app.background)
check('metres',scene.unit_settings.system=='METRIC' and scene.unit_settings.scale_length==1)
check('seven_cameras',len([o for o in scene.objects if o.type=='CAMERA'])==7)
check('room_collections',all(k in bpy.data.collections for k in C['rooms']))
check('materials',all(k in bpy.data.materials for k in C['materials']))
check('lights',len([o for o in scene.objects if o.type=='LIGHT'])>=len(C['rooms']))
check('configuration_matches',json.loads(scene['configuration'])==C)
check('hidden_candidates',bpy.data.collections['Candidate_Equipment'].hide_render and bpy.data.collections['Candidate_Equipment'].hide_viewport)
check('six_seat_alternative_hidden',bpy.data.collections['Dining_6'].hide_viewport)
check('C_north_no_leaf','former_C_door_leaf' not in bpy.data.objects)
check('C_west_2200',abs(bpy.data.objects['C_west_opening_header'].dimensions.y-2.2)<1e-5)
check('CD_wall_preserved',abs(bpy.data.objects['wall_CD_0'].dimensions.x-4.336)<1e-5)
check('A_window_south',abs(bpy.data.objects['A_window_glass'].location.y-6.207)<1e-5)
check('kitchen_closable','former_kitchen_door_leaf' in bpy.data.objects and 'kitchen_south_glass_glass' in bpy.data.objects)
# Hidden alternate collections must be evaluated before measuring matrix_world.
for col in bpy.data.collections: col.hide_viewport=False
bpy.context.view_layer.update()
for key,dim in [('bedA',(1.8,2,.25)),('bedB',(1.2,2,.25)),('bedD',(1.5,2,.25))]:
    check(key+'_mattress',all(abs(a-b)<1e-5 for a,b in zip(bpy.data.objects[key+'_mattress'].dimensions,dim)))
for name in ['coffee','sofa','desk','table4','table6']:
    f=C['furniture'][name];suffix='_carcass' if name=='coffee' else '_base' if name=='sofa' else '_top'
    check(name+'_dimensions',all(abs(a-b)<1e-5 for a,b in zip(bpy.data.objects[name+suffix].dimensions[:2],f['box'][2:])))

walls=[o for o in scene.objects if o.name.startswith('wall_')]
glass=[o for o in scene.objects if o.name.endswith('_glass') and any(s in o.name for s in ('kitchen','study'))]
physical=walls+glass
scene.frame_set(1);bpy.context.view_layer.update()
for name,f in C['furniture'].items():
    if f['room']=='Candidate_Equipment':continue
    root=bpy.data.objects[name]
    children=[o for o in root.children if o.type=='MESH']
    for wall in physical:
        hits=[overlap(bounds(o),bounds(wall)) for o in children]
        if any(hits):warn('furniture_wall',[name,wall.name],next(h for h in hits if h),'Translate furniture; retain structural wall boundary.')

for state in (4,6):
    names=[n for n,f in C['furniture'].items() if f['room'] not in ('Candidate_Equipment',f'Dining_{10-state}')]
    for i,a in enumerate(names):
        for b in names[i+1:]:
            fa,fb=C['furniture'][a],C['furniture'][b]
            if a.startswith('table') and b.startswith('chair') or b.startswith('table') and a.startswith('chair'):continue
            # Footprints are assembly envelopes: intentional stacked components stay within one root.
            hit=overlap(box3(fa['box'],fa.get('z',0),fa['height']),box3(fb['box'],fb.get('z',0),fb['height']))
            if hit:warn('furniture_envelopes',[a,b],dict(seats=state,overlap_mm=hit),'Assembly envelope overlap; review actual parts and translate if obstructed.')

# Actual animated leaf positions at one-degree steps, including wall and furniture solids.
# This is a sampled sweep, not a proof of continuous clearance; conservative AABBs over-report oblique contacts.
for o in [o for o in scene.objects if o.name.endswith('_leaf')]:
    hits=set()
    for frame in range(1,91):
        scene.frame_set(frame);bpy.context.view_layer.update();a=bounds(o)
        for other in physical:
            if overlap(a,bounds(other),.035):hits.add(other.name)
        for name,f in C['furniture'].items():
            if f['room'] in ('Candidate_Equipment','Dining_6'):continue
            if overlap(a,box3(f['box'],f.get('z',0),f['height']),.02):hits.add(name)
    if hits:warn('door_sweep',[o.name,*sorted(hits)],'90-frame actual animated leaf AABB sweep, 20mm furniture / 35mm wall tolerance','Review hinge/slide pocket; do not assume simultaneous operation.')
scene.frame_set(1)

coffee=C['furniture']['coffee']['box']
services={
 'coffee_drawer':box3([coffee[0],coffee[1]+coffee[3],coffee[2],.5],.15,.55),
 'coffee_operator':box3([coffee[0],coffee[1]+coffee[3]+.5,coffee[2],.6],0,1.8),
 'oven_open':box3([1.075,-2.398+.0,.6,.55],.45,.5),
 'pantry_open':box3([3.375,-2.398,.501,.45],.1,2.1),
 'fridge_drawer':box3([.16,-2.248,.855,.6],.1,.8),
 'dishwasher_open':box3([2.6,1.474,.6,.65],.1,.65),
 'dishwasher_operator':box3([2.6,.874,.6,.6],0,1.8),
 'laundry_service':box3([4.216,.94,.75,.9],0,1.8),
 'island_operator':box3([3.3,-.225,.6,.6],0,1.8),
 'study_storage_open':box3([-2.76,4,.6,1.35],0,2.1)}
for state in (4,6):
    for pulled in (False,True):
        chairs=[]
        for n,f in C['furniture'].items():
            if not n.startswith(f'chair{state}_'):continue
            b=f['box'].copy()
            if pulled:
                if f['facing']=='south':b[3]+=.35
                else:b[1]-=.35;b[3]+=.35
            chairs.append((n,box3(b,0,.8)))
        for chair,b in chairs:
            for service,volume in services.items():
                hit=overlap(b,volume)
                if hit:warn('service_chair',[chair,service],dict(seats=state,pulled=pulled,overlap_mm=hit),'South row must vacate before opening/servicing equipment.')
            for wall in physical:
                hit=overlap(b,bounds(wall))
                if hit:warn('pulled_chair_wall',[chair,wall.name],dict(seats=state,pulled=pulled,overlap_mm=hit),'Full pull-out obstructed; adjust seating use or furniture position.')
    for service,volume in services.items():
        for n,f in C['furniture'].items():
            if n.startswith(('chair','table')) or f['room']=='Candidate_Equipment':continue
            if n==service.split('_')[0] or (service=='study_storage_open' and n=='study_storage'):continue
            hit=overlap(volume,box3(f['box'],f.get('z',0),f['height']))
            if hit:warn('service_fixed',[service,n],dict(seats=state,overlap_mm=hit),'Adjust use/position; manufacturer clearance remains pending.')

metrics={}
for state in (4,6):
    tb=C['furniture'][f'table{state}']['box']
    # Closed kitchen glass is the controlling obstruction, not the remote bath wall.
    seated_north=tb[1]+tb[3]+.45
    glass_south=min(bounds(o)[1] for o in glass if o.name=='kitchen_south_glass_glass')
    metrics[str(state)]={
      'north_route_seated_mm':round((glass_south-seated_north)*1000),
      'north_route_pulled_mm':round((glass_south-seated_north-.35)*1000),
      'south_chair_to_coffee_mm':round((tb[1]-.45-(coffee[1]+coffee[3]))*1000),
      'south_chair_to_open_oven_mm':round((tb[1]-.45-(-1.848))*1000)}
    if metrics[str(state)]['north_route_pulled_mm']<1000:warn('passage',[f'Dining_{state}','north_route'],metrics[str(state)],'Closed glass prevents full north chair pull-out. Dining seating needs further layout review; access from west, no north passage asserted.')
warn('unconfirmed_structural',['headers','wall_thickness'],'Image cannot resolve original beams, columns or load-bearing classification.','Site survey required; no construction clearance asserted.')
warn('conditional_equipment',['island_sink','laundry','robot'],'No hidden pipework; island gravity drain and balcony sanitary connection unverified.','Confirm connection levels and equipment models before installation.')
warn('bathroom_assumptions',['Bath_A','Bath_Public'],'Sanitary fixtures modeled as assumed concept positions, not inferred confirmed plumbing.','Survey fixture footprints and wet-zone boundaries.')
check('all_mesh_dimensions_positive',all(min(o.dimensions)>0 for o in scene.objects if o.type=='MESH'))
saved_objects=len(scene.objects);saved_materials=len(bpy.data.materials)
# Round-trip every visible exported mesh; GLB excludes alternate and candidate geometry.
excluded={'Ceilings','Dining_6','Candidate_Equipment','Clearance_Envelopes'}
expected={o.name for o in scene.objects if o.type=='MESH' and not any(c.name in excluded for c in o.users_collection)}
preview=[]
for name in sorted(expected):
    o=bpy.data.objects[name]
    for face in o.data.polygons:
        material=o.data.materials[face.material_index] if o.data.materials else None
        # Glass omitted for inspection through windows and the study enclosure.
        if material and material.name=='glass':continue
        preview.append(dict(vertices=[list(o.matrix_world@o.data.vertices[i].co) for i in face.vertices],color=list(material.diffuse_color) if material else [.7,.7,.7,1]))
(ROOT/'preview_geometry.json').write_text(json.dumps(preview),encoding='utf-8')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'whole_home.glb'))
imported={o.name for o in bpy.context.scene.objects if o.type=='MESH'}
check('glb_import',bool(imported))
check('glb_mesh_count',len(imported)==len(expected))
check('glb_no_candidate_mesh',not any(n.startswith('robot_') for n in imported))
check('glb_no_six_seat_mesh',not any(n.startswith(('table6','chair6')) for n in imported))
report=dict(status='passed' if all(checks.values()) else 'failed',scope='artifact integrity; design warnings do not imply site approval',blender_version=bpy.app.version_string,
 checks=checks,counts=dict(blend_objects=saved_objects,blend_materials=saved_materials,glb_meshes=len(imported)),
 assumptions=C['assumptions'],metrics=metrics,issues=issues,
 limitations=['No local Cycles render; configured lights/materials/cameras verified by data.',
 'Door sweep sampled at 90 animation frames with conservative AABBs; hardware tolerances and exact continuous sweep not certified.',
 'Cabinet fronts are closed geometry with separate service envelopes; manufacturer hinges not modeled.',
 'Floorplan derived from dimension-anchored R10 wall faces, not independently surveyed coordinates.'],
 files={name:dict(bytes=(ROOT/name).stat().st_size,sha256=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()) for name in ['whole_home.blend','whole_home.glb','scene_config.json','build_scene.py']})
(ROOT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# 模型检查报告','',f"文件完整性：**{report['status']}**；Blender {report['blender_version']}。",'',
 f'Blend 对象 {saved_objects}；材质 {saved_materials}；重新导入 GLB 网格 {len(imported)}。','',
 '几何及使用问题按下表保留；文件通过不等于通道、开启空间及施工条件全部通过。','',
 '| 检查 | 结果 |','|---|---|']
lines += [f'| {k} | {v} |' for k,v in checks.items()]
lines += ['','## 通道估算','','| 状态 | 北侧就座 mm | 北侧拉椅 mm | 南椅至咖啡柜 mm | 南椅至烤箱全开 mm |','|---|---:|---:|---:|---:|']
lines += [f"| {n}人 | {m['north_route_seated_mm']} | {m['north_route_pulled_mm']} | {m['south_chair_to_coffee_mm']} | {m['south_chair_to_open_oven_mm']} |" for n,m in metrics.items()]
lines += ['','## 未解决碰撞与条件','','| 类别 | 对象 | 详情 | 处理 |','|---|---|---|---|']
lines += [f"| {i['category']} | {', '.join(i['objects'])} | {json.dumps(i['detail'],ensure_ascii=False)} | {i['action']} |" for i in issues]
lines += ['','## 尺寸假设','']+['- '+s for s in C['assumptions']]
lines += ['','## 检查范围','']+['- '+s for s in report['limitations']]
(ROOT/'CHECK_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps(dict(status=report['status'],checks=checks,issue_count=len(issues),counts=report['counts'])))
assert all(checks.values()), 'Artifact verification failed; inspect verification.json'

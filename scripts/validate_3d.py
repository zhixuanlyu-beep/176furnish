"""Reopen saved R10.5 model, verify actual meshes and exported geometry. No rendering."""
import bpy,json,hashlib,math,struct,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];D=json.loads((R/'data/layout.json').read_text());C=json.loads((R/'model/scene_config.json').read_text())
sys.path.insert(0,str(R/'scripts'))
bpy.ops.wm.open_mainfile(filepath=str(R/'model/whole_home_R10.5.blend'));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
checks={};detail={}
visibility={c.name:c.hide_viewport for c in bpy.data.collections}
for c in bpy.data.collections:c.hide_viewport=False
bpy.context.view_layer.update()
def check(k,b,v=None):checks[k]=bool(b);detail[k]=v
def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box];return [min(v[i] for v in p) for i in range(3)]+[max(v[i] for v in p) for i in range(3)]
def rect(o):b=bounds(o);return [b[0],b[1],b[3]-b[0],b[4]-b[1]]
def err(a,b):return max(abs(x-y) for x,y in zip(a,b))*1000
check('configuration_current',json.loads(s['configuration'])==C and C['revision']=='R10.5' and C['layout_sha256']==hashlib.sha256((R/'data/layout.json').read_bytes()).hexdigest())
check('metric_units',s.unit_settings.system=='METRIC' and s.unit_settings.scale_length==1)
wall_errors={n:err(rect(bpy.data.objects[n]),[v/1000 for v in b]) for n,b in D['walls'].items()};check('walls_1mm',max(wall_errors.values())<=1,wall_errors)
proxies={'bed':'_mattress','sofa':'_base','table':'_top','chair':'_seat','cabinet':'_carcass','fridge':'_carcass','basin':'_vanity','laundry':'_machine0','sliding_wardrobe':'_carcass','shelf':'_body'}
ferrors={}
for n,f in C['furniture'].items():
 o=bpy.data.objects[n];check('layout_root_'+n,json.loads(o['footprint'])==f['box'] and abs(o['height']-f['height'])<1e-6)
 suffix=proxies.get(f['kind']);ob=bpy.data.objects.get(n+suffix) if suffix else None
 if ob:
  if f.get('rotation_deg'):ferrors[n]=err(list(ob.dimensions)[:2],f['box'][2:])
  else:ferrors[n]=err(rect(ob),f['box'])
check('principal_furniture_1mm',max(ferrors.values())<=1,ferrors)
check('D_bedside_shelf_height',abs(bounds(bpy.data.objects['D_bedside_body'])[2]-.65)<.001)
special={}
for n in ['shoe','entry_wardrobe','study_shallow','tower']:
 def descendants(o):
  return [child for c in o.children for child in [c,*descendants(c)]]
 obs=[o for o in descendants(bpy.data.objects[n]) if o.type=='MESH' and 'infill' not in o.name and 'recess' not in o.name and 'vent' not in o.name]
 bb=[bounds(o) for o in obs];actual=[min(b[0] for b in bb),min(b[1] for b in bb),max(b[3] for b in bb)-min(b[0] for b in bb),max(b[4] for b in bb)-min(b[1] for b in bb)]
 special[n]={'xy_error_mm':err(actual,C['furniture'][n]['box']),'top_error_mm':abs(max(b[5] for b in bb)-C['furniture'][n]['height'])*1000}
check('special_cabinet_actual_bounds_1mm',all(max(v.values())<=1 for v in special.values()),special)
check('island_top_matches_layout',abs(bounds(bpy.data.objects['island_counter'])[5]-C['furniture']['island']['height'])<.001)
seat_errors={n:abs(bounds(bpy.data.objects[n+'_seat'])[5]-f['seat_height'])*1000 for n,f in C['furniture'].items() if f['kind']=='chair'}
check('individual_seat_heights_1mm',max(seat_errors.values())<=1,seat_errors)
check('no_robot_opening_in_island',not any(m.type=='BOOLEAN' and 'Robot' in m.name for m in bpy.data.objects['island_carcass'].modifiers) and 'island_storage_front0' in bpy.data.objects)
check('robot_candidate_matches_layout',err(rect(bpy.data.objects['robot_station_reservation']),C['appliances']['robot_station']['box'])<=1)
check('shoe_sections',abs(bounds(bpy.data.objects['shoe_upper_infill'])[2]-2.4)<.001 and abs(bounds(bpy.data.objects['shoe_upper_infill'])[5]-2.8)<.001 and abs(bounds(bpy.data.objects['shoe_backing'])[1]-3.074)<.001)
check('no_obsolete_solids',not any(n in bpy.data.objects for n in ['wardrobeA','shower_A','microwave','oven','steam_oven','former_C_door_header','former_kitchen_door_header','C_west_opening_header']))
check('one_shower',set(n for n,f in C['furniture'].items() if f['kind']=='shower')=={'shower_public'})
dev={}
for n in ['combi_steam_oven','built_in_microwave']:
 b=bounds(bpy.data.objects[n+'_body']);dev[n]=max(abs(b[2]-C['appliances'][n]['z']),abs(b[5]-C['appliances'][n]['z']-C['appliances'][n]['height']))*1000
check('appliance_vertical_positions_1mm',max(dev.values())<=1,dev)
# The former island robot opening is intentionally removed; historical condition remains in docs.
from projection import load_snapshot, export_snapshot
projection=load_snapshot()
check('current_component_projection',projection['layout_sha256']==C['layout_sha256'] and len(projection['components'])>100)
check('projection_matches_reopened_mesh',projection==export_snapshot(C,write=False))

doors={}
for frame,key in [(1,'closed_box'),(90,'open_box')]:
 s.frame_set(frame);bpy.context.view_layer.update()
 for n,v in C['doors'].items():doors[n+'_'+key]=err(rect(bpy.data.objects[n]),v[key])
check('room_door_endpoints_1mm',max(doors.values())<=1,doors)
state_errors={n:err(rect(bpy.data.objects['use_'+n]),v['box']) for n,v in C['use_zones'].items()}
check('whole_home_use_zones_1mm',max(state_errors.values())<=1,state_errors)
accessory_errors={n:err(rect(bpy.data.objects['accessory_'+n]),v['box']) for n,v in C['accessories'].items()}
check('accessory_positions_1mm',max(accessory_errors.values())<=1,accessory_errors)
check('public_shower_700mm_entry',abs(bounds(bpy.data.objects['shower_public_screen_glass'])[1]-(C['furniture']['shower_public']['box'][1]+.7))<.001)
# Sliding fronts must remain inside total cabinet footprint over their complete linear travel.
outside=[]
for frame in range(1,91):
 s.frame_set(frame);bpy.context.view_layer.update()
 for n in ['study_shallow_sliding_door0','study_shallow_sliding_door1']:
  b=bounds(bpy.data.objects[n])
  if b[0]<-3.411 or b[3]>-2.959 or b[1]<3.173 or b[4]>4.351:outside.append([frame,n])
check('shallow_sliding_travel_inside_450mm',not outside,outside)
s.frame_set(1);bpy.context.view_layer.update()
check('seven_cameras',sum(o.type=='CAMERA' for o in s.objects)==7)
check('alternative_visibility',all(bpy.data.collections[n].hide_render for n in ['Dining_6','Clearance_Envelopes','Candidate_Equipment','Ceilings']))
check('no_external_images',all(i.packed_file or i.source in ('GENERATED','VIEWER') for i in bpy.data.images))
missing=[o.name for o in s.objects if o.type=='MESH' and not(o.data.materials and all(m is not None for m in o.data.materials))]
check('materials_present',not missing,missing)
raw=(R/'model/whole_home_R10.5.glb').read_bytes();size=struct.unpack_from('<I',raw,12)[0];glb=json.loads(raw[20:20+size]);names={n.get('name') for n in glb['nodes']}
check('glb_current_objects',{'shoe_west_side','entry_wardrobe_module0_side0','combi_steam_oven_body','built_in_microwave_body'}.issubset(names) and not {'wardrobeA','shower_A','former_C_door_header','C_west_opening_header'}.intersection(names))
check('glb_alternatives_excluded',not any(n and (n.startswith(('table6','chair6')) or n=='robot_station_reservation') for n in names))
conditions=['原西铰A门50mm把手87–90°碰墙记录保留；本轮东铰复算无该命中，实际五金、开关及门框仍待核。','三维尺寸和门端点核验通过不替代2D全状态／实体操作条件；见verification_2d.json。','柜门、层板、设备均为概念模型，五金、通风、电源、结构、给排水及现场安装未确认。','床头板等细节高度沿用概念造型，家具表高度主要描述基体；非柜体下单图。','未生成或检查三维渲染图；灯光、材质观感、曝光和相机构图待后续渲染验收。']
report={'revision':'R10.5','checks_passed':all(checks.values()),'check_count':len(checks),'checks':checks,'details':detail,'conditions':conditions,'blender':bpy.app.version_string,'layout_sha256':C['layout_sha256'],'blend_sha256':hashlib.sha256((R/'model/whole_home_R10.5.blend').read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(raw).hexdigest()}
(R/'reports/verification_3d.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':report['checks_passed'],'checks':len(checks),'failed':[n for n,v in checks.items() if not v],'special':special},ensure_ascii=False))
if not report['checks_passed']:raise RuntimeError('3D verification failed')

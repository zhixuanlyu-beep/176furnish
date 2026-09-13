"""R10.4 cabinetry, with editable shells and door animation, all units metres."""
import bpy,math
from mathutils import Vector
def special_cabinet(n,f,g):
 if n not in ['shoe','study_shallow','entry_wardrobe','tower','island']:return False
 box,C,collection=g['box'],g['C'],g['collection'];x,y,w,d=f['box'];h=f['height'];room=f['room'];mat=f['material']
 def b(s,q,z,height,material=None):return box(n+'_'+s,q,z,height,material or mat,room,.002)
 def hinge(o,p,angle):
  pivot=Vector((*p,0));delta=o.location-pivot
  for v in o.data.vertices:v.co+=delta
  o.location=pivot;o.keyframe_insert('rotation_euler',frame=1);o.rotation_euler.z=angle;o.keyframe_insert('rotation_euler',frame=90);o.rotation_euler.z=0
  o['operation']='hinged';o['opening_angle_degrees']=math.degrees(angle)
 if n=='island':
  body=b('carcass',[x,y,w,d],0,h-.03);b('counter',[x,y,w,d],h-.03,.03,'stone')
  cutter=box('robot_access_cut',[x+.02,y+.05,.76,d],-.01,.66,None,'Scratch')
  mod=body.modifiers.new('Robot station access','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter;bpy.context.view_layer.objects.active=body;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
  b('sink_front',[x+.81,y+d-.02,.78,.02],.10,h-.14)
  a=C['appliances']['robot_station'];o=box('robot_station_reservation',a['box'],0,.65,'olive','Clearance_Envelopes');o.display_type='WIRE';o['status']='760×650×650 concept reservation; no selected device'
  b('module_divider',[x+.78,y,.02,d],0,h-.03)
 elif n=='shoe':
  b('west_side',[x,y,.018,d],.1,2.3);b('east_side',[x+w-.018,y,.018,d],.1,2.3)
  b('backing',[x,y+d-.05,w,.05],.1,2.3);b('toe',[x,y,w,d],0,.1)
  b('top_structure',[x,y,w,d],2.35,.05)
  b('upper_infill',[x,y,w,d],2.4,.4,'warm_white')
  for zone,lo,hi,count in [('lower',.1,.9,3),('upper',1.25,2.35,5)]:
   clear=(hi-lo-(count+1)*.018)/count
   for i in range(count+1):b(zone+f'_shelf{i}',[x+.018,y+.02,w-.036,d-.07],lo+i*(clear+.018),.018)
   for side in range(2):
    left=x+side*w/2;o=b(zone+f'_door{side}',[left,y,w/2,.02],lo,hi-lo)
    hinge(o,(left if side==0 else left+w/2,y),(-1 if side==0 else 1)*math.pi/2)
    # Recess handles remain within the 20mm leaf, no proud hardware added.
    pull=box(n+'_'+zone+f'_recess{side}',[left+(.33 if side==0 else .08),y+.001,.04,.002],(lo+hi)/2,.08,'black',room)
    pull.parent=o;pull.matrix_parent_inverse=o.matrix_world.inverted()
  b('niche_light',[x+.03,y+.04,w-.06,.015],1.232,.012,'warm_white')
  for i in range(3):b('vent'+str(i),[x+.1+i*.22,y-.001,.16,.002],.16,.008,'black')
 elif n=='study_shallow':
  b('backing',[x,y,.018,d],.1,h-.1);b('south_side',[x,y,w,.018],.1,h-.1);b('north_side',[x,y+d-.018,w,.018],.1,h-.1)
  for i,z in enumerate([.1,.48,.86,1.24,1.62,2.0,2.282]):b('shelf'+str(i),[x+.018,y+.018,w-.068,d-.036],z,.018)
  for i in range(2):
   q=[x+w-.04+i*.022,y+(0 if i==0 else .558),.018,.618];o=b('sliding_door'+str(i),q,.12,h-.14)
   o['operation']='sliding';o.keyframe_insert('location',frame=1);o.location.y+=.558 if i==0 else -.558;o.keyframe_insert('location',frame=90);o.location.y-=.558 if i==0 else -.558
 elif n=='entry_wardrobe':
  for k in range(4):
   xx=x+k*.8
   for j,q in enumerate([[xx,y,.018,d],[xx+.782,y,.018,d],[xx,y+d-.018,.8,.018]]):b(f'module{k}_side{j}',q,.1,h-.1)
   for j,z in enumerate([.1,h-.018]):b(f'module{k}_shelf{j}',[xx+.018,y+.018,.764,d-.036],z,.018)
   for side in range(2):
    left=xx+side*.4;o=b(f'module{k}_door{side}',[left,y,.4,.018],.1,h-.1);hinge(o,(left if side==0 else left+.4,y),(-1 if side==0 else 1)*math.pi/2)
   if k<3:
    for j,z in enumerate([1.05,1.95] if k<2 else [1.95]):b(f'module{k}_rail{j}',[xx+.018,y+.3,.764,.018],z,.018,'metal')
   else:
    for j,z in enumerate([.3,.6,.9]):
     o=b(f'drawer{j}',[xx+.025,y+.03,.75,.5],z,.22);o['operation']='drawer';o.keyframe_insert('location',frame=1);o.location.y-=.45;o.keyframe_insert('location',frame=90);o.location.y+=.45
    for j,z in enumerate([1.3,1.7,2.0]):b(f'module3_shelf{j+2}',[xx+.018,y+.018,.764,d-.036],z,.018)
 elif n=='tower':
  for i,q in enumerate([[x,y,.018,d-.02],[x+w-.018,y,.018,d-.02],[x,y,w,.018]]):b('side'+str(i),q,.1,h-.1)
  for i,z in enumerate([.1,.632,1.182,1.62,h-.018]):b('shelf'+str(i),[x+.018,y+.018,w-.036,d-.038],z,.018)
  for key in ['combi_steam_oven','built_in_microwave']:
   a=C['appliances'][key];z=a['z'];hh=a['height']
   o=box(key+'_body',[x+.018,y+.018,w-.036,d-.038],z,hh,'black',room,.006);o['appliance']=key;o['status']='concept model; manufacturer installation drawing pending'
   leaf=box(key+'_door',[x,y+d-.02,w,.02],z,hh,'black',room,.004)
   if key=='combi_steam_oven':
    pivot=Vector((x,y+d,z));delta=leaf.location-pivot
    for v in leaf.data.vertices:v.co+=delta
    leaf.location=pivot;leaf.keyframe_insert('rotation_euler',frame=1);leaf.rotation_euler.x=-math.pi/2;leaf.keyframe_insert('rotation_euler',frame=90);leaf.rotation_euler.x=0
   else:hinge(leaf,(x,y+d),math.pi/2)
   leaf['operation']='appliance_door'
  b('lower_storage',[x,y+d-.02,w,.02],.12,.49);b('upper_storage',[x,y+d-.02,w,.02],1.65,h-1.65)
 return True

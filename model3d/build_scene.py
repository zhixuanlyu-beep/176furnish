"""Blender background-only, deterministic, editable room model; no rendering."""
import argparse
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
assert bpy.app.background, 'Run Blender with --background; GUI execution is disabled.'
parser = argparse.ArgumentParser()
parser.add_argument('--config', type=Path, default=ROOT/'scene_config.json')
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
C = json.loads(args.config.read_text(encoding='utf-8'))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for col in list(bpy.data.collections):
    bpy.data.collections.remove(col)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 64
scene.render.resolution_x = 1800
scene.render.resolution_y = 1400
scene.render.resolution_percentage = 100
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.65,.72,.82,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .35
cols = {}
def collection(name):
    if name not in cols:
        cols[name] = bpy.data.collections.new(name)
        scene.collection.children.link(cols[name])
    return cols[name]

mats = {}
for name, color in C['materials'].items():
    m = bpy.data.materials.new(name)
    m.diffuse_color = color
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = color
    p.inputs['Roughness'].default_value = .65
    if name in ('metal','black'): p.inputs['Metallic'].default_value = .75
    if name=='glass':
        p.inputs['Transmission Weight'].default_value = .7
        p.inputs['Roughness'].default_value = .12
        p.inputs['Alpha'].default_value = .28
        m.surface_render_method = 'DITHERED'
    if name in ('oak','walnut','linen'):
        n=m.node_tree.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value=75 if name=='linen' else 5
        tex=m.node_tree.nodes.new('ShaderNodeTexCoord')
        mapping=m.node_tree.nodes.new('ShaderNodeVectorMath'); mapping.operation='MULTIPLY'
        mapping.inputs[1].default_value=(2,35,3) if name!='linen' else (1,1,1)
        bump=m.node_tree.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.12; bump.inputs['Distance'].default_value=.008
        m.node_tree.links.new(tex.outputs['Generated'],mapping.inputs[0]);m.node_tree.links.new(mapping.outputs[0],n.inputs['Vector'])
        m.node_tree.links.new(n.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
    mats[name]=m

def place(obj,name,room,material):
    obj.name=name
    for col in list(obj.users_collection): col.objects.unlink(obj)
    collection(room).objects.link(obj)
    if material: obj.data.materials.append(mats[material])
    return obj

def box(name,b,z,h,mat='warm_white',room='Architecture',bevel=0):
    x,y,w,d=b
    assert min(w,d,h)>0, (name,b,h)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(x+w/2,y+d/2,z+h/2))
    o=place(bpy.context.object,name,room,mat);o.dimensions=(w,d,h)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new('Soft edges','BEVEL');mod.width=bevel;mod.segments=3
        mod=o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cylinder(name,pos,radius,depth,mat,room,rotation=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=radius,depth=depth,location=pos)
    o=place(bpy.context.object,name,room,mat)
    if rotation: o.rotation_euler=rotation
    for p in o.data.polygons:p.use_smooth=True
    return o

def metadata(o,**props):
    for k,v in props.items(): o[k]=v if isinstance(v,(str,int,float,bool)) else json.dumps(v,ensure_ascii=False)

def subtract(a,b):
    x,y,w,d=a; X,Y,W,D=b
    l,r=max(x,X),min(x+w,X+W);lo,hi=max(y,Y),min(y+d,Y+D)
    if r<=l or hi<=lo:return [a]
    out=[]
    if l>x:out.append([x,y,l-x,d])
    if r<x+w:out.append([r,y,x+w-r,d])
    if lo>y:out.append([l,y,r-l,lo-y])
    if hi<y+d:out.append([l,hi,r-l,y+d-hi])
    return out

H=C['defaults']['wall_height']; DH=C['defaults']['door_height']
for name,rects in C['rooms'].items():
    collection(name)
    for i,b in enumerate(rects):
        mat='stone' if name.startswith(('Bath','Kitchen','Balcony')) else 'oak'
        box(f'{name}_floor_{i}',b,-.12,.12,mat,name)
        box(f'{name}_ceiling_{i}',b,H,.12,'warm_white','Ceilings')
        # Individual shallow boards remain easy to select and replace.
        if mat=='oak':
            x,y,w,d=b
            for j in range(math.ceil(w/.19)):
                xx=x+j*.19;ww=min(.188,x+w-xx)
                if ww>.002:box(f'{name}_plank_{i}_{j}',[xx,y,ww,d],0,.009,'oak','Floor_Finish')

for name,b in C['walls'].items():
    parts=[b]
    for op in C['openings'].values():
        if op['kind'] in ('door','glass_door'):parts=[p for a in parts for p in subtract(a,op['box'])]
    for i,p in enumerate(parts):
        o=box(f'wall_{name}_{i}',p,0,H)
        metadata(o,source='image-estimated R10 wall face',structural_status='unverified, preserve')

def frame(name,b,z,h,room='Openings'):
    x,y,w,d=b; horizontal=w>d;length=w if horizontal else d
    thin=.04
    slim=[x,y+(d-thin)/2,w,thin] if horizontal else [x+(w-thin)/2,y,thin,d]
    box(name+'_bottom',slim,z,.035,'black',room)
    box(name+'_top',slim,z+h-.035,.035,'black',room)
    for t in (0,length/2,length-.035):
        q=[slim[0]+t,slim[1],.035,thin] if horizontal else [slim[0],slim[1]+t,thin,.035]
        box(name+f'_mullion_{t:.3f}',q,z,h,'black',room)
    pane=box(name+'_glass',slim,z+.035,h-.07,'glass',room)
    metadata(pane,concept=True)

for name,op in C['openings'].items():
    b=op['box'];x,y,w,d=b;kind=op['kind']
    if kind.startswith('bay'):
        sill=C['defaults']['bay_sill'];wh=C['defaults']['bay_height']
        box(name+'_ledge',b,0,sill,'stone','Openings')
        box(name+'_cap',b,sill+wh,H-sill-wh,'warm_white','Openings')
        if kind=='bay_east':
            frame(name+'_east',[x+w-.05,y,.05,d],sill,wh)
            for yy in (y,y+d-.05):frame(name+f'_return{yy}',[x,yy,w,.05],sill,wh)
        else:
            frame(name+'_south',[x,y,w,.05],sill,wh)
            for xx in (x,x+w-.05):frame(name+f'_return{xx}',[xx,y,.05,d],sill,wh)
    elif kind=='window':
        sill=C['defaults']['window_sill'];wh=C['defaults']['window_height']
        box(name+'_sill',b,0,sill,'warm_white','Openings')
        box(name+'_header',b,sill+wh,H-sill-wh,'warm_white','Openings')
        frame(name,b,sill,wh)
    elif kind=='glass_partition':frame(name,b,0,DH);box(name+'_header',b,DH,H-DH)
    else:
        box(name+'_header',b,DH,H-DH,'warm_white','Headers_Concept')
        if kind in ('door','glass_door'):
            horizontal=w>d
            q=[x,y+(d-.035)/2,w,.035] if horizontal else [x+(w-.035)/2,y,.035,d]
            o=box(name+'_leaf',q,.015,DH-.03,'glass' if kind=='glass_door' else 'oak','Doors',.008)
            metadata(o,opening_box=b,operation='sliding' if kind=='glass_door' else 'hinged',clear_width=max(w,d),hinge_side='assumed')
            if kind=='glass_door':
                o.location+=Vector(op.get('slide_offset',[0,0,0]))
                o.keyframe_insert(data_path='location',frame=1)
                o.location[0 if horizontal else 1]+=max(w,d)*op.get('slide_sign',1)
                o.keyframe_insert(data_path='location',frame=90)
            else:
                # Place the object origin at the hinge without altering its geometry.
                hinge=Vector((q[0],q[1],.015));delta=o.location-hinge
                for v in o.data.vertices:v.co+=delta
                o.location=hinge
                o.keyframe_insert(data_path='rotation_euler',frame=1)
                o.rotation_euler.z=math.pi/2*op.get('swing_sign',1)
                o.keyframe_insert(data_path='rotation_euler',frame=90)

def legs(name,b,height,room,mat='walnut'):
    x,y,w,d=b
    for i,(xx,yy) in enumerate([(x+.07,y+.07),(x+w-.11,y+.07),(x+.07,y+d-.11),(x+w-.11,y+d-.11)]):
        box(name+f'_leg{i}',[xx,yy,.04,.04],.03,height-.03,mat,room,.008)

for name,f in C['furniture'].items():
    b=f['box'];x,y,w,d=b;room=f['room'];h=f['height'];mat=f['material'];kind=f['kind'];z=f.get('z',0)
    root=bpy.data.objects.new(name,None);collection(room).objects.link(root)
    metadata(root,footprint=b,height=h,kind=kind,status=f.get('status','concept'))
    before=set(bpy.data.objects)
    if kind=='bed':
        box(name+'_base',b,.10,.2,'walnut',room,.035)
        box(name+'_mattress',b,.3,.25,'linen',room,.07)
        box(name+'_headboard',[x,y+d-.08,w,.08],.2,.85,'walnut',room,.03)
        box(name+'_cover',[x,y,w,d*.65],.53,.035,'olive' if name=='bedB' else 'linen',room,.02)
        for i in range(2):box(name+f'_pillow{i}',[x+.08+i*w/2,y+d-.48,w/2-.12,.36],.56,.12,'warm_white',room,.05)
    elif kind=='sofa':
        box(name+'_base',b,.12,.22,mat,room,.09)
        box(name+'_back',[x,y,.2,d],.32,.53,mat,room,.09)
        for yy in (y,y+d-.22):box(name+f'_arm{yy}',[x,yy,w,.22],.3,.38,mat,room,.1)
        for i in range(3):box(name+f'_seat{i}',[x+.19,y+.24+i*(d-.48)/3,w-.23,(d-.48)/3-.025],.34,.16,mat,room,.055)
        box(name+'_accent',[x+.20,y+.3,.20,.4],.5,.3,'brick',room,.08)
    elif kind=='table':
        box(name+'_top',b,h-.045,.045,mat,room,.02);legs(name,b,h-.045,room)
    elif kind=='chair':
        box(name+'_seat',b,.43,.07,mat,room,.035);legs(name,b,.43,room)
        yy=y if f.get('facing')=='south' else y+d-.05
        box(name+'_back',[x,yy,w,.05],.50,.30,'walnut',room,.02)
    elif kind in ('cabinet','tower','fridge'):
        box(name+'_carcass',b,.10,h-.1,mat if kind!='fridge' else 'warm_white',room,.008)
        front=y-.02 if f.get('front')=='south' else y+d-.012
        for i in range(max(1,round(w/.5))):
            cw=w/max(1,round(w/.5))
            panel=[x+i*cw+.006,front,cw-.012,.02]
            pull=[x+i*cw+cw-.045,front+(-.025 if f.get('front')=='south' else .025),.012,.025]
            if f.get('front')=='east':
                panel=[x+w-.012,y+.006,.02,d-.012];pull=[x+w+.02,y+.1,.025,.012]
            box(name+f'_front{i}',panel,.13,h-.16,mat if kind!='fridge' else 'warm_white',room,.004)
            box(name+f'_pull{i}',pull,h*.5,.16,'black',room,.004)
        if h<=.95:box(name+'_counter',b,h,.03,'stone',room,.01)
        if kind=='tower':
            for dev,zz in [('oven',.45),('steam_oven',1.15)]:
                o=box(dev,[x+.025,y+d,.55,.035],zz,.48,'black',room,.008);metadata(o,**C['equipment'][dev])
                box(dev+'_handle',[x+.09,y+d+.035,.42,.03],zz+.38,.025,'metal',room,.006)
    elif kind=='screen':box(name+'_housing',b,z,h,'black',room,.008);box(name+'_fabric',[x,y,.01,d],.65,1.55,'warm_white',room)
    elif kind=='basin':
        box(name+'_vanity',b,.10,.67,'oak',room,.02)
        # Raised rim around a visibly recessed basin, no solid top across the bowl.
        box(name+'_bowl_bottom',[x+.06,y+.05,w-.12,d-.1],.73,.025,'warm_white',room,.02)
        for q in [[x,y,w,.04],[x,y+d-.04,w,.04],[x,y,.04,d],[x+w-.04,y,.04,d]]:box(name+'_rim',q,.75,.1,'warm_white',room,.015)
    elif kind=='wc':
        cylinder(name+'_bowl',(x+w/2,y+d/2,.3),w/2,.45,'warm_white',room)
        box(name+'_tank',[x,y+d-.15,w,.15],.4,.35,'warm_white',room,.05)
        cylinder(name+'_seat',(x+w/2,y+d*.45,.54),w*.44,.03,'linen',room)
    elif kind=='shower':
        box(name+'_tray',b,.01,.04,'stone',room)
        frame(name+'_screen',[x+w-.025,y,.025,d],.05,h,room)
        cylinder(name+'_riser',(x+.12,y+.06,1.3),.012,1.3,'metal',room)
        cylinder(name+'_head',(x+.12,y+.16,1.95),.1,.025,'metal',room)
    elif kind=='laundry':
        for i in range(2):
            box(name+f'_machine{i}',b,.06+i*.86,.84,'warm_white',room,.03)
            cylinder(name+f'_port{i}',(x+w/2,y-.01,.46+i*.86),.24,.04,'black',room,(math.pi/2,0,0))
    else:box(name+'_body',b,0,h,mat,room,.03)
    for o in set(bpy.data.objects)-before:o.parent=root

# Coffee equipment: no fixed water connections and open space above the worktop.
room='C_Prep_Dining';b=C['furniture']['coffee']['box'];x,y,w,d=b
o=box('coffee_machine',[x+.12,y+.15,.32,.36],.93,.39,'metal',room,.025);metadata(o,**C['equipment']['coffee_machine'])
box('coffee_machine_front',[x+.14,y+.51,.28,.018],1.04,.20,'black',room,.008)
box('coffee_drip_tray',[x+.14,y+.48,.28,.1],.945,.025,'black',room,.008)
box('coffee_tank',[x+.12,y+.12,.32,.07],.98,.30,'glass',room,.015)
cylinder('coffee_spout',(x+.29,y+.52,1.05),.025,.10,'metal',room)
o=box('grinder',[x+.53,y+.2,.18,.23],.93,.27,'black',room,.02);metadata(o,**C['equipment']['grinder'])
cylinder('grinder_hopper',(x+.62,y+.31,1.29),.085,.18,'glass',room)
for i in range(4):
    # Hollow cup made from concentric side faces.
    bpy.ops.mesh.primitive_torus_add(major_radius=.034,minor_radius=.004,major_segments=24,minor_segments=8,location=(x+1.05+i*.12,y+.3,1.01))
    place(bpy.context.object,f'cup_rim{i}',room,'warm_white')
    cylinder(f'cup{i}',(x+1.05+i*.12,y+.3,.97),.036,.07,'warm_white',room)
box('coffee_cup_storage',[x+.85,y,.80,.18],1.65,.045,'walnut',room,.008)
box('coffee_power_socket',[x+.78,y+.01,.12,.025],1.12,.08,'black',room)
for name,b,z,h in [('coffee_front_service',[x,y+d,1.7,.6],0,1.5),('coffee_tank_lift',[x+.12,y+.12,.32,.43],1.32,.35),('grinder_refill',[x+.50,y+.18,.24,.28],1.38,.3)]:
    o=box(name,b,z,h,'olive','Clearance_Envelopes');o.display_type='WIRE'

def sink(name,b,room,z=.932):
    x,y,w,d=b
    box(name+'_recess',[x,y,w,d],z,.006,'black',room,.02)
    box(name+'_bottom',[x+.025,y+.025,w-.05,d-.05],z+.008,.004,'metal',room,.015)
    for q in [[x,y,w,.018],[x,y+d-.018,w,.018],[x,y,.018,d],[x+w-.018,y,.018,d]]:box(name+'_rim',q,z,.022,'metal',room,.006)
    cylinder(name+'_tap',(x+w*.7,y+d+.035,z+.16),.018,.32,'metal',room)
    box(name+'_tap_spout',[x+w*.7-.018,y+d-.10,.036,.14],z+.28,.035,'metal',room,.01)
sink('kitchen_sink',[3.34,2.24,.48,.36],'Kitchen')
sink('island_sink',[3.46,-.69,.34,.36],room)
metadata(bpy.data.objects['island_sink_recess'],**C['equipment']['island_sink'])
o=box('dishwasher',[2.6,2.105,.6,.025],.12,.72,'metal','Kitchen',.008);metadata(o,**C['equipment']['dishwasher'])
o=box('purifier',[3.28,2.27,.18,.30],.15,.4,'warm_white','Kitchen',.015);metadata(o,**C['equipment']['purifier'])
box('hob_glass',[1.78,2.22,.55,.42],.934,.018,'black','Kitchen',.012)
for xx in (1.92,2.18):cylinder('burner',(xx,2.42,.963),.09,.015,'metal','Kitchen')
box('hood',[1.76,2.26,.60,.42],1.8,.15,'metal','Kitchen',.02)
box('hood_flue',[1.93,2.40,.26,.26],1.95,.65,'metal','Kitchen')
for i in range(4):box(f'kitchen_upper{i}',[2.45+i*.375,2.40,.36,.30],1.55,.65,'oak','Kitchen',.01)
# Local soffit and independently editable five indoor AC units. Routes remain unspecified.
box('AC01_soffit',[-3.25,-6.05,2,1.15],2.4,.4,'warm_white','Ceilings')
box('AC01_supply',[-2.95,-4.92,1.4,.035],2.46,.12,'black','Living')
for name,b in {'AC02':[6.38,6.45,.24,.8],'AC03':[3.736,2.95,.24,.8],'AC04':[2.976,-6.262,.85,.24],'AC05':[-1.4,5.907,.85,.24]}.items():
    box(name,b,2.30,.28,'warm_white','HVAC',.04)
for name,b in [('Living_rug',[-3.0,-3.65,1.75,2.85]),('Balcony_A_bench',[-3.9,-6.1,1.4,.42])]:
    box(name,b,.012,.02 if name.endswith('rug') else .42,'linen' if name.endswith('rug') else 'walnut','Living',.015)

# Lighting configured for later rendering on a compatible computer.
for room,rects in C['rooms'].items():
    x,y,w,d=rects[0]
    data=bpy.data.lights.new(room+'_area','AREA');data.energy=180 if w*d<8 else 400;data.shape='DISK';data.size=2;data.color=(1,.80,.59)
    o=bpy.data.objects.new(room+'_area',data);collection('Lighting').objects.link(o);o.location=(x+w/2,y+d/2,2.68)
for i,xx in enumerate((1.55,2.3)):
    cylinder(f'pendant_rod{i}',(xx,-.98,2.45),.012,.65,'black',room='Lighting')
    cylinder(f'pendant_shade{i}',(xx,-.98,2.08),.22,.08,'walnut',room='Lighting')
    cylinder(f'pendant_diffuser{i}',(xx,-.98,2.035),.18,.015,'warm_white',room='Lighting')
for name,spec in C['cameras'].items():
    data=bpy.data.cameras.new(name);data.lens=22;data.clip_end=200
    if 'ortho' in spec:data.type='ORTHO';data.ortho_scale=spec['ortho']
    o=bpy.data.objects.new(name,data);collection('Cameras').objects.link(o);o.location=spec['position']
    direction=Vector(spec['target'])-o.location;o.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
scene.camera=bpy.data.objects['01_Axonometric']
scene.frame_set(1)
scene.frame_start=1;scene.frame_end=90
for name in ['Ceilings','Dining_6','Candidate_Equipment','Clearance_Envelopes']:
    col=collection(name);col.hide_render=True;col.hide_viewport=True
scene['configuration']=json.dumps(C,ensure_ascii=False)
scene['notes']='Model-first R10.1 concept. Frame 1 doors closed; frame 90 open. Toggle Dining_4 / Dining_6 exclusively. Ceilings hidden for dollhouse. No local render.'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'whole_home.blend'),compress=True)
bpy.ops.object.select_all(action='DESELECT')
excluded={'Ceilings','Dining_6','Candidate_Equipment','Clearance_Envelopes'}
for o in scene.objects:
    if o.type=='MESH' and not any(c.name in excluded for c in o.users_collection):o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'whole_home.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_cameras=False,export_lights=False,export_materials='EXPORT')
print('MODEL_BUILD_COMPLETE',len(scene.objects))

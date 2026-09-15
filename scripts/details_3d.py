"""Editable R10.5 details; no external assets, installations or network calls."""
import math
import bpy
from mathutils import Vector, Matrix

def complete_scene(g):
    C,scene,box,cylinder,collection,metadata,mats=[g[k] for k in ('C','scene','box','cylinder','collection','metadata','mats')]
    # Rebuild door hinges from the published closed and fully-open rectangles.
    for name,d in C['doors'].items():
        x,y,w,depth=d['closed_box'];ox,oy,ow,od=d['open_box']
        if d.get('kind')=='sliding':
            o=box(name,[x,y,w,depth],d['z'],d['height'],'oak','Doors',.003)
            o.keyframe_insert(data_path='location',frame=1)
            o.location.x+=ox-x;o.location.y+=oy-y;o.keyframe_insert(data_path='location',frame=90)
            o.location.x-=ox-x;o.location.y-=oy-y
            box(name+'_track',[ox,y,min(x+w-ox,2*w),depth],2.08,.06,'metal','Door_Frames',.003)
            continue
        cc=Vector((x+w/2,y+depth/2));oc=Vector((ox+ow/2,oy+od/2))
        angle=d['swing_sign']*math.pi/2
        R=Matrix.Rotation(angle,2); hinge=(Matrix.Identity(2)-R).inverted()@(oc-R@cc)
        o=box(name,[x,y,w,depth],d['z'],d['height'],'glass' if d['glass'] else 'oak','Doors',.003)
        pivot=Vector((hinge.x,hinge.y,d['z']));delta=o.location-pivot
        for v in o.data.vertices:v.co+=delta
        o.location=pivot
        bpy.context.view_layer.update()
        metadata(o,opening=d['opening'],swing_sign=d['swing_sign'],source='R10.5 published closed and 90-degree outlines')
        if d['glass']:
            # Dark rails surround the thin glass without widening its footprint.
            for i,q in enumerate(([x,y,.025,depth],[x+w-.025,y,.025,depth])):
                rail=box(name+f'_rail{i}',q,d['z'],d['height'],'black','Doors',.002)
                rail.parent=o;rail.matrix_parent_inverse=o.matrix_world.inverted()
            for i,zz in enumerate((d['z'],d['z']+d['height']-.025)):
                rail=box(name+f'_rail_h{i}',[x,y,w,depth],zz,.025,'black','Doors',.002)
                rail.parent=o;rail.matrix_parent_inverse=o.matrix_world.inverted()
        o.keyframe_insert(data_path='rotation_euler',frame=1)
        o.rotation_euler.z=angle;o.keyframe_insert(data_path='rotation_euler',frame=90)
        o.rotation_euler.z=0
    # Jambs sit inside the declared opening; no full-width overlapping leaf.
    for name,op in C['openings'].items():
        if op['kind'] not in ('door','double_glass_door'):continue
        x,y,w,d=op['box'];margin=.045
        if w>d:
            pieces=[[x,y,margin,d],[x+w-margin,y,margin,d]]
        else:pieces=[[x,y,w,margin],[x,y+d-margin,w,margin]]
        if name=='A_door':
            pieces=[[x,y,margin,.03],[x,y+.03,.007,d-.03],pieces[1]]
        for i,q in enumerate(pieces):box(name+f'_jamb{i}',q,0,2.1,'black' if name=='family_entry' else 'oak','Door_Frames',.002)
    # Fill removed-partition and door thresholds, avoiding uncovered black seams.
    def subtract(a,b):
        x,y,w,d=a;X,Y,W,D=b;l,r=max(x,X),min(x+w,X+W);lo,hi=max(y,Y),min(y+d,Y+D)
        if r-l<1e-7 or hi-lo<1e-7:return [a]
        return [q for q in ([x,y,l-x,d],[r,y,x+w-r,d],[l,y,r-l,lo-y],[l,hi,r-l,y+d-hi]) if min(q[2:])>1e-6]
    covered=[b for rs in C['rooms'].values() for b in rs]
    for name,op in C['openings'].items():
        if op['kind'] in ('door','double_glass_door','removed_door','connected'):
            pieces=[op['box']]
            for q in covered:pieces=[part for b in pieces for part in subtract(b,q)]
            for i,q in enumerate(pieces):box(name+f'_threshold{i}',q,-.12,.12,'oak','Thresholds')
            covered+=pieces
    box('family_continuous_floor',[-3.41,2.724,3.93,.12],-.12,.12,'oak','Thresholds')
    # Coffee and other appliances belong to their assembly for inspection.
    for o in list(scene.objects):
        if o.type!='MESH' or o.parent:continue
        if o.name.startswith(('coffee_','grinder','cup')) and not o.name.endswith(('front_service','tank_lift','refill','power_socket')):
            o.parent=bpy.data.objects['coffee']
    # Actual recessed sinks: cut both the countertop and cabinet block.
    for name,b,owners in [('kitchen_sink',[3.34,2.24,.48,.36],['sink_carcass','sink_counter']),('island_sink',C['appliances']['island_sink']['box'],['island_carcass','island_counter'])]:
        x,y,w,d=b
        for suffix in ('recess','bottom'):
            o=bpy.data.objects.get(name+'_'+suffix)
            if o:bpy.data.objects.remove(o,do_unlink=True)
        top=C['furniture']['sink' if name.startswith('kitchen') else 'island']['height']
        cutter=box(name+'_cut',[x+.018,y+.018,w-.036,d-.036],top-.18,.3,None,'Scratch')
        for target in owners:
            o=bpy.data.objects[target];mod=o.modifiers.new('Recessed sink cutout','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter
            bpy.context.view_layer.objects.active=o
            bpy.ops.object.modifier_apply(modifier=mod.name)
            # Boolean cutters have no finish; cut faces inherit the owner finish.
            for index, material in enumerate(o.data.materials):
                if material is None:o.data.materials[index]=o.data.materials[0]
        bpy.data.objects.remove(cutter,do_unlink=True)
        top=C['furniture']['sink' if name.startswith('kitchen') else 'island']['height']
        box(name+'_bowl_bottom',[x+.018,y+.018,w-.036,d-.036],top-.175,.01,'metal','Kitchen' if name.startswith('kitchen') else 'C_Prep_Dining',.008)
        for i,q in enumerate(([x+.018,y+.018,w-.036,.008],[x+.018,y+d-.026,w-.036,.008],[x+.018,y+.018,.008,d-.036],[x+w-.026,y+.018,.008,d-.036])):
            box(name+f'_bowl_wall{i}',q,top-.17,.174,'metal','Kitchen' if name.startswith('kitchen') else 'C_Prep_Dining',.004)
        for ob in list(scene.objects):
            if ob.name.startswith(name+'_') and ob.type=='MESH' and ob.parent is None:
                ob.parent=bpy.data.objects['sink' if name.startswith('kitchen') else 'island']
    # Under-cabinet warm task lighting and soft daylight through real openings.
    def light(name,pos,target,power,size,color=(1,.9,.76)):
        data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=color
        o=bpy.data.objects.new(name,data);collection('Lighting').objects.link(o);o.location=pos
        o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
        o.visible_camera=False;o.visible_glossy=False;o.visible_transmission=False
        return o
    for o in list(scene.objects):
        if o.type=='LIGHT':
            o.data.color=(1,.93,.83);o.data.energy*=.30
            o.visible_camera=False;o.visible_glossy=False;o.visible_transmission=False
            cylinder(o.name+'_ceiling_trim',(o.location.x,o.location.y,2.788),.09,.018,'warm_white','Ceilings')
    for name,pos,target,power,size in [
        ('Daylight_C',(5.0,-1.3,1.7),(1.6,-1.3,1.1),450,2.0),
        ('Daylight_A',(5.5,5.85,1.8),(4.2,8,1.1),650,2.0),
        ('Daylight_B',(4.85,4.6,1.7),(1.6,4.6,1.0),400,1.8),
        ('Daylight_D',(1.9,-7.2,1.7),(1.9,-4.3,1),450,2),
        ('Daylight_Living',(-2.65,-6.7,1.8),(-2.5,-2.5,1.2),800,2.5),
        ('Daylight_Laundry',(5.4,1.5,1.9),(2.5,1.3,1),300,2)]:
        light(name,pos,target,power,size,(.86,.93,1))
    cf=C['furniture']['coffee']['box']
    light('Coffee_task',(cf[0]+.9,cf[1]+.18,1.60),(cf[0]+.9,cf[1]+.4,.9),28,.8)
    light('Kitchen_task',(2.9,2.3,1.52),(2.9,2.3,.9),35,1.4)
    # Pendant emission uses a separate material, leaving white furniture unchanged.
    emit=mats['warm_white'].copy();emit.name='Warm_lamp'
    bsdf=emit.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Emission Color'].default_value=(1,.76,.45,1);bsdf.inputs['Emission Strength'].default_value=3
    for o in list(scene.objects):
        if o.name.startswith('pendant_diffuser'):
            o.data.materials.clear();o.data.materials.append(emit)
    # Small computer equipment identifies the family-room work desk.
    box('monitor_stand',[-1.53,5.85,.18,.16],.752,.02,'black','Study',.005)
    box('monitor_post',[-1.46,5.91,.04,.04],.77,.20,'black','Study',.005)
    box('monitor',[-1.77,5.89,.66,.035],.90,.39,'black','Study',.009)
    box('monitor_display',[-1.75,5.887,.62,.003],.92,.35,'metal','Study',.004)
    box('keyboard',[-1.73,5.61,.44,.15],.752,.016,'black','Study',.004)
    # Visible slab underside for the dollhouse, with no invented external walls.
    scene.frame_set(1);bpy.context.view_layer.update()

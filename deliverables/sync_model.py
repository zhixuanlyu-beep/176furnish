"""Fail-closed handoff from independently verified Blender geometry to millimetres."""
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
MODEL=ROOT/'model3d'
sys.path.insert(0,str(MODEL))
from layout_rules import service_box
REVISION='R10.2 家庭厅与客厅优化版'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def mm(b):
    x,y,w,d=b
    return [round(x*1000,6),round(-(y+d)*1000,6),round(w*1000,6),round(d*1000,6)]
def metres(b):
    x,y,w,d=b
    return [x/1000,-(y+d)/1000,w/1000,d/1000]
def footprint(a):return mm([a[0],a[1],a[3]-a[0],a[4]-a[1]])
def hit(a,b,tol=.002):return all(min(a[i+3],b[i+3])-max(a[i],b[i])>tol for i in range(3))
def intersect(a,b):
    x,y=max(a[0],b[0]),max(a[1],b[1]);w=min(a[0]+a[2],b[0]+b[2])-x;d=min(a[1]+a[3],b[1]+b[3])-y
    return [x,y,w,d] if min(w,d)>1e-5 else None
def require_verified(model=MODEL):
    try:
        c=read(model/'scene_config.json');r=read(model/'verification.json');s=read(model/'geometry_snapshot.json')
        assert r['status']=='passed' and all(r['checks'].values()),'三维验证未通过'
        for n in ['scene_config.json','whole_home.blend','whole_home.glb','build_scene.py','verify_scene.py','layout_rules.py','geometry_snapshot.json','layout_states.json']:
            assert digest(model/n)==r['files'][n]['sha256'],n+' 已过期'
        for n,h in s['files'].items():assert digest(model/n)==h,n+' 快照已过期'
        assert s['configuration']==c,'快照配置不匹配'
        return c,r,s,read(model/'layout_states.json')
    except (OSError,KeyError,AssertionError,ValueError) as e:
        raise RuntimeError('停止发布：配置、模型或验证缺失/过期。请运行 model3d/run_background.ps1 重新生成并验证。 '+str(e)) from e

class Model:
    def __init__(self):
        self.c,self.report,self.snapshot,self.states=require_verified()
        self.objects=self.snapshot['objects']
        self.furniture={n:mm(f['box']) for n,f in self.c['furniture'].items()}
        self.services={n:footprint(service_box(self.c,s)) for n,s in self.c['services'].items()}
        self.walls={n:footprint(o['bounds']) for n,o in self.objects.items() if n.startswith('wall_')}
    def parts(self,n):return {k:o for k,o in self.objects.items() if o['owner']==n}
    def aggregate(self,n):
        bs=[o['bounds'] for o in self.parts(n).values()]
        return [min(b[i] for b in bs) for i in range(3)]+[max(b[i] for b in bs) for i in range(3,6)]
    def knees(self,n):
        f=self.c['furniture'][n];x,y,w,d=f['box'];s=self.c['seating']
        b=[x+(w-s['knee_width'])/2,y-s['knee_depth'] if f['facing']=='south' else y+d,s['knee_width'],s['knee_depth']]
        return [b[0],b[1],s['knee_z'],b[0]+b[2],b[1]+b[3],s['knee_z']+s['knee_height']]
    def basket(self,state):
        # Centre the square basket in the actual north corridor, including turns.
        north=-self.c['walls'][self.c['acceptance']['normal_north_boundary']][1]*1000
        route=state['north_route_mm'];y=north+route/2
        points=[[-3500,-2200],[-2600,-2200],[-2600,y],[3600,y],[3600,-825],[4500,-825]]
        sweeps=[[min(a[0],b[0])-300,min(a[1],b[1])-300,abs(a[0]-b[0])+600,abs(a[1]-b[1])+600] for a,b in zip(points,points[1:])]
        boxes=dict(self.walls)
        for n,o in self.objects.items():
            if n.endswith('_leaf'):
                boxes[n+'_open']=footprint(self.snapshot['motion']['90'][n]['bounds'])
            elif 'Openings' in o['collections'] and o['bounds'][2]<1.4:
                boxes[n]=footprint(o['bounds'])
        for n in self.furniture:
            f=self.c['furniture'][n]
            if f['room'] in ('Candidate_Equipment',f"Dining_{10-state['seats']}"):continue
            b=footprint(self.aggregate(n))
            if 'pull_vector' in f and (state['state']=='all_pulled' or state['state']=='single:'+n):
                b[0]+=f['pull_vector'][0]*1000;b[1]-=f['pull_vector'][1]*1000
            boxes[n]=b
        solids=sorted(n for n,b in boxes.items() if any(intersect(b,v) for v in sweeps))
        overlaps={n:[intersect(b,v) for v in sweeps if intersect(b,v)] for n,b in self.services.items() if any(intersect(b,v) for v in sweeps)}
        island=self.services['island_operator']
        island_gap=min(max(v[0]-island[0]-island[2],island[0]-v[0]-v[2],v[1]-island[1]-island[3],island[1]-v[1]-v[3],0) for v in sweeps)
        dish=self.services['dishwasher_operator']
        north_chairs=[footprint(self.aggregate(n)) for n,f in self.c['furniture'].items() if n.startswith(f"chair{state['seats']}_") and f['facing']=='south']
        local=min(b[1] for b in north_chairs)-(dish[1]+dish[3])-(self.c['seating']['pull_distance']*1000 if route==600 else 0)
        return dict(width_mm=600,north_route_mm=route,lateral_allowance_mm=route-600,path_mm=points,
            dishwasher_loading_to_chair_mm=round(local),island_operator_route_gap_mm=round(island_gap),
            solid_hits=solids,service_overlaps_mm=overlaps,door_state='房门完全打开，行走中不同时转动门扇',
            comfortable_passage=route>600 and not solids,
            recommendation='先恢复正常就座，再携篮；携篮与洗碗装卸、岛槽操作错时。终点转向洗烘仍待现场放样。')
    def validation(self):
        for b in [*self.c['walls'].values(),*[o['box'] for o in self.c['openings'].values()],*[f['box'] for f in self.c['furniture'].values()]]:
            assert all(abs(a-bb)<1e-8 for a,bb in zip(b,metres(mm(b))))
        # Independently subtract configured door cuts from wall rectangles.
        def subtract(b,cut):
            overlap=intersect(b,cut)
            if not overlap:return [b]
            x,y,w,d=b;u,v,a,h=overlap
            return [r for r in [[x,y,u-x,d],[u+a,y,x+w-u-a,d],[u,y,a,v-y],[u,v+h,a,y+d-v-h]] if min(r[2:])>1e-6]
        expected_walls=[]
        for b in self.c['walls'].values():
            pieces=[b]
            for op in self.c['openings'].values():
                if op['kind'] in ('door','glass_door'):pieces=[p for piece in pieces for p in subtract(piece,op['box'])]
            expected_walls.extend(mm(p) for p in pieces)
        meaningful_walls={n:w for n,w in self.walls.items() if min(w[2:])>.01}
        assert len(expected_walls)==len(meaningful_walls)
        assert all(any(max(abs(a-b) for a,b in zip(p,w))<.01 for w in self.walls.values()) for p in expected_walls)
        comparisons=[]
        for n,f in self.c['furniture'].items():
            parts=self.parts(n);assert parts,n
            actual=footprint(self.aggregate(n))
            # Verify a canonical physical part against each configured plan rectangle.
            suffix={'bed':'_mattress','cabinet':'_carcass','tower':'_carcass','fridge':'_carcass','sofa':'_base','table':'_top','chair':'_seat','screen':'_housing','basin':'_vanity','shower':'_tray','laundry':'_machine0','robot':'_body'}.get(f['kind'])
            if suffix and not f.get('rotation_degrees'):
                measured=footprint(parts[n+suffix]['bounds'])
                assert max(abs(a-b) for a,b in zip(measured,self.furniture[n]))<.01,(n,measured)
            if f.get('rotation_degrees'):
                x,y,w,d=f['box'];a=math.radians(f['rotation_degrees']);cx,cy=x+w/2,y+d/2
                corners=[(cx+u*math.cos(a)-v*math.sin(a),cy+u*math.sin(a)+v*math.cos(a)) for u in (-w/2,w/2) for v in (-d/2,d/2)]
                expected=[min(p[0] for p in corners),min(p[1] for p in corners),max(p[0] for p in corners),max(p[1] for p in corners)]
                seat=parts[n+'_seat']['bounds']
                assert max(abs(v-seat[i]) for v,i in zip(expected,(0,1,3,4)))<1e-5
            if f['kind']=='microwave':
                b=self.aggregate(n);x,y,w,d=f['box']
                assert max(abs(a-bb) for a,bb in zip(b,[x,y,f['z'],x+w,y+d,f['z']+f['height']]))<1e-5
                top=self.parts(f['support_owner'])[f['support_owner']+'_counter']['bounds'][5]
                assert abs(b[2]-top)<1e-5
            if f['kind']=='lamp':
                b=self.aggregate(n);x,y,w,d=f['box']
                assert abs(b[3]-b[0]-w)<1e-5 and abs(b[5]-f['height'])<1e-5
            elif f['kind']=='wc':
                x,y,w,d=f['box'];tank=parts[n+'_tank']['bounds']
                assert abs(tank[0]-x)<1e-5 and abs(tank[4]-(y+d))<1e-5 and abs(tank[3]-tank[0]-w)<1e-5
            if 'pull_vector' in f:
                seat=parts[n+'_seat']['bounds'];back=parts[n+'_back']['bounds']
                assert (back[1]+back[4]>seat[1]+seat[4])==(f['facing']=='south')
                for pn in parts:
                    a=self.snapshot['motion']['1'][pn]['bounds'];b=self.snapshot['motion']['150'][pn]['bounds']
                    assert max(abs(b[i]-a[i]-f['pull_vector'][i%3]) for i in range(6))<1e-5
            if f.get('door_operation')=='sliding':
                for pn,o in parts.items():
                    if '_front' not in pn:continue
                    a=o['bounds'];x,y,w,d=f['box']
                    assert (a[0]+a[3]<2*x+w)==(f['front']=='west')
                    b=self.snapshot['motion']['90'][pn]['bounds'];assert abs(b[0]-a[0])<1e-5 and abs(b[1]-a[1])>0
            comparisons.append(dict(object=n,box_mm=self.furniture[n],actual_outline_mm=actual,front=f.get('front'),facing=f.get('facing'),parts=list(parts)))
        for n,op in self.c['openings'].items():
            if op['kind']=='double_glass_door':
                for leaf in op['leaves']:
                    a=self.objects[n+'_'+leaf['id']+'_leaf']['bounds']
                    assert abs(a[3]-a[0]-leaf['width'])<1e-5
            if op['kind'] in ('door','glass_door'):
                a=self.objects[n+'_leaf']['bounds'];clear=max(op['box'][2:]);actual=max(a[3]-a[0],a[4]-a[1])
                assert abs(actual-(clear-2*op.get('frame_clearance',0)))<1e-5,n
        m=self.report['metrics']
        expected=[1100,600,98,48,198,148]
        for n in ('4','6'):assert list(m[n].values())==expected,m[n]
        assert m['bedrooms']==dict(A_side_mm=900,B_side_mm=900,D_side_mm=900,D_foot_mm=1000,screen_route_mm=1000)
        support=[]
        for n in (4,6):
            knees=[self.knees(f'chair{n}_{i}') for i in range(n)]
            parts=self.parts(f'table{n}');leg=[o['bounds'] for k,o in parts.items() if '_support' in k];beam=parts[f'table{n}_beam']['bounds']
            assert not any(hit(k,o['bounds']) for k in knees for o in parts.values())
            # Real adversarial fixture at knee height versus permitted seat/top overlap.
            k=knees[0];intrusive=[k[0]+.05,k[1]+.05,k[2],k[0]+.12,k[1]+.12,k[5]]
            assert hit(k,intrusive)
            seat=self.parts(f'chair{n}_0')[f'chair{n}_0_seat']['bounds'];top=parts[f'table{n}_top']['bounds']
            assert intersect(footprint(seat),footprint(top)) and not hit(seat,top)
            lateral=min(max(k[0]-l[3],l[0]-k[3])*1000 for k in knees for l in leg if min(k[4],l[4])>max(k[1],l[1]))
            support.append(dict(seats=n,knee_to_support_mm=round(lateral),beam_above_knee_mm=round((beam[2]-knees[0][5])*1000)))
        assert support[1]['knee_to_support_mm']==15 and all(x['beam_above_knee_mm']==30 for x in support)
        baskets=[self.basket(s) for s in self.states]
        assert all(not b['comfortable_passage'] for b in baskets if b['north_route_mm']==600)
        return dict(objects=comparisons,family=m['family'],actual_wall_segments=len(self.walls),numerical_wall_slivers=[n for n in self.walls if n not in meaningful_walls],roundtrip='passed',door_installation='passed',supports=support,baskets=baskets,
            regression='passed',counterexamples=['侵入膝部桌腿被检出','座面进入桌下无误报','600mm通道不判舒适携篮'])

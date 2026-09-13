"""Derive Blender metres from the sole R10.4 millimetre layout; no historical model input."""
import json,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def make_config():
 d=json.loads((ROOT/'data/layout.json').read_text());s=json.loads((ROOT/'data/style3d.json').read_text())
 def m(b):return [v/1000 for v in b]
 def swing(v):
  cb,ob=v['closed_box'],v['open_box'];cc=(cb[0]+cb[2]/2,cb[1]+cb[3]/2);oc=(ob[0]+ob[2]/2,ob[1]+ob[3]/2);cand=[]
  for sign in [1,-1]:
   dx,dy=oc[0]+sign*cc[1],oc[1]-sign*cc[0];p=((dx-sign*dy)/2,(sign*dx+dy)/2)
   cand.append((min(math.dist(p,q) for q in [(cb[0],cb[1]),(cb[0]+cb[2],cb[1]),(cb[0],cb[1]+cb[3]),(cb[0]+cb[2],cb[1]+cb[3])]),sign))
  return min(cand)[1]
 c={k:s[k] for k in ['defaults','materials','cameras','equipment']};c.update(revision='R10.4',walls_are_final_segments=True,layout_sha256=hashlib.sha256((ROOT/'data/layout.json').read_bytes()).hexdigest())
 c['walls']={n:m(b) for n,b in d['walls'].items()};c['rooms']={n:[m(b) for b in bs] for n,bs in d['rooms'].items()}
 c['openings']={n:{**o,'box':m(o['box'])} for n,o in d['openings'].items()}
 c['openings']['balconyA_connection']['upper_solid']={'bottom':2.1,'top':2.8,'basis':'Existing balcony upper-wall concept retained; real beam and soffit dimensions require site confirmation.'}
 c['doors']={n:{**v,'closed_box':m(v['closed_box']),'open_box':m(v['open_box']),'swing_sign':swing(v),'glass':n.startswith('family_entry'),'height':2.0,'z':.015} for n,v in d['doors'].items()}
 c['furniture']={n:{**f,'box':m(f['box']),'height':f['height']/1000,'z':f.get('z',0)/1000,'material':s['furniture_materials'].get(n,'oak'),'rotation_deg':f.get('rotation_degrees',0)} for n,f in d['furniture'].items()}
 c['appliances']={n:{**a,'box':m(a['box']),'z':a['z']/1000,'height':a['height']/1000} for n,a in d['appliances'].items()}
 c['parts']={n:m(b) for n,b in d['parts'].items()};c['assumptions']=d['concept_assumptions']
 (ROOT/'model/scene_config.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n');return c
if __name__=='__main__':make_config()

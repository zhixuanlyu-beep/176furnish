"""Future opt-in rendering. Not executed for the R10.5 model-only delivery."""
import argparse,json,sys
from pathlib import Path
import bpy
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--device',choices=['CPU','METAL'],required=True);p.add_argument('--preview',action='store_true');p.add_argument('--camera');p.add_argument('--samples',type=int,default=128)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.wm.open_mainfile(filepath=str(R/'model/whole_home_R10.5.blend'));s=bpy.context.scene
c=json.loads(s['configuration']);names=[a.camera] if a.camera else list(c['cameras'])
if any(n not in c['cameras'] for n in names):raise ValueError('Unknown camera')
if a.device=='METAL':
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
 devices=[d for d in prefs.devices if d.type=='METAL']
 if not devices:raise RuntimeError('No Metal GPU; no automatic fallback. Verify one CPU view separately.')
 for d in prefs.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
else:s.cycles.device='CPU'
s.render.engine='CYCLES';s.cycles.use_denoising=True;s.cycles.samples=24 if a.preview else a.samples
s.render.resolution_x=2400;s.render.resolution_y=1866;s.render.resolution_percentage=25 if a.preview else 100;s.render.image_settings.file_format='PNG'
out=R/'render-output'/('preview' if a.preview else 'final');out.mkdir(parents=True,exist_ok=True)
for n in names:
 s.frame_set(1);s.camera=bpy.data.objects[n]
 for k in ['Dining_6','Clearance_Envelopes','Candidate_Equipment']:bpy.data.collections[k].hide_render=True
 bpy.data.collections['Dining_4'].hide_render=False;bpy.data.collections['Ceilings'].hide_render=n.startswith(('01_','02_'))
 s.render.filepath=str(out/(n+'.png'));bpy.ops.render.render(write_still=True)
 print('SAVED',s.render.filepath,flush=True)

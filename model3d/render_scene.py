"""Optional explicit render job for compatible hosts; never called by default."""
import argparse
import sys
from pathlib import Path
import bpy
assert bpy.app.background, 'Background only'
root=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--camera',default='01_Axonometric')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.wm.open_mainfile(filepath=str(root/'whole_home.blend'))
camera=bpy.data.objects.get(a.camera)
assert camera and camera.type=='CAMERA', 'Unknown camera'
bpy.context.scene.camera=camera
bpy.context.scene.render.filepath=str(root/(a.camera+'.png'))
bpy.ops.render.render(write_still=True)

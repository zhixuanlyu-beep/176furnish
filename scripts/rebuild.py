"""Build current R10.4 artifacts; never render 3D."""
import argparse, subprocess, sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--all',action='store_true');g.add_argument('--2d-only',action='store_true');p.add_argument('--blender',default='blender');p.add_argument('--node',default='node');a=p.parse_args()
def run(args):subprocess.run(args,cwd=R,check=True)
run([sys.executable,'scripts/build_2d.py']);run([a.node,'scripts/preview_2d.cjs'])
if a.all:
 for script in ['build_3d.py','validate_3d.py']:run([a.blender,'--background','--factory-startup','--disable-autoexec','--python-exit-code','1','--python','scripts/'+script])
run([sys.executable,'scripts/validate_delivery.py'])

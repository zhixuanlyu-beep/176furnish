"""Software polygon projection of saved mesh coordinates; no Blender rendering.
Requires Pillow and NumPy. An inspection diagram, not a lighting/material rendering.
"""
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
ROOT=Path(__file__).resolve().parent
faces=json.loads((ROOT/'preview_geometry.json').read_text(encoding='utf-8'))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def norm(a):
    l=math.sqrt(dot(a,a));return [v/l for v in a]
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
for name,eye in [('preview_axonometric',[16,-20,24]),('preview_top',[0,0,1])]:
    z=norm(eye);x=norm(cross([0,1,0] if name=='preview_top' else [0,0,1],z));y=cross(z,x)
    polys=[]
    for face in faces:
        vs=face['vertices'];points=[(dot(v,x),-dot(v,y)) for v in vs]
        normal=cross([vs[1][i]-vs[0][i] for i in range(3)],[vs[2][i]-vs[0][i] for i in range(3)])
        shade=.72+.28*max(0,dot(norm(normal),norm([-1,-2,4]))) if dot(normal,normal)>1e-12 else 1
        polys.append(([dot(v,z) for v in vs],points,[c*shade for c in face['color']]))
    coords=[p for _,ps,_ in polys for p in ps]
    lo=[min(p[i] for p in coords) for i in (0,1)];hi=[max(p[i] for p in coords) for i in (0,1)]
    scale=min(1350/(hi[0]-lo[0]),1450/(hi[1]-lo[1]))
    pixels=np.full((1600,1500,3),[247,244,237],dtype=np.uint8)
    depths=np.full((1600,1500),-np.inf,dtype=np.float32)
    for zs,ps,color in polys:
        pts=[(75+(a-lo[0])*scale,85+(b-lo[1])*scale) for a,b in ps]
        rgb=tuple(round(255*min(1,max(0,c))**(1/2.2)) for c in color[:3])
        for i in range(1,len(pts)-1):
            tri=[pts[j] for j in (0,i,i+1)];tz=[zs[j] for j in (0,i,i+1)]
            (ax,ay),(bx,by),(cx,cy)=tri
            den=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
            if abs(den)<1e-7:continue
            lx=max(0,int(min(v[0] for v in tri)));rx=min(1499,math.ceil(max(v[0] for v in tri)))
            ly=max(0,int(min(v[1] for v in tri)));ry=min(1599,math.ceil(max(v[1] for v in tri)))
            if rx<lx or ry<ly:continue
            gy,gx=np.mgrid[ly:ry+1,lx:rx+1]
            u=((by-cy)*(gx-cx)+(cx-bx)*(gy-cy))/den
            v=((cy-ay)*(gx-cx)+(ax-cx)*(gy-cy))/den;t=1-u-v
            zz=u*tz[0]+v*tz[1]+t*tz[2]
            mask=(u>=0)&(v>=0)&(t>=0)&(zz>=depths[ly:ry+1,lx:rx+1])
            depths[ly:ry+1,lx:rx+1][mask]=zz[mask]
            pixels[ly:ry+1,lx:rx+1][mask]=rgb
    im=Image.fromarray(pixels);draw=ImageDraw.Draw(im)
    draw.text((40,25),'R10.1 | WARM MID-CENTURY + MINIMAL | SAVED MESH INSPECTION',fill='#293b32')
    draw.text((40,1560),'Software polygon projection. Not a photoreal render. Four-seat state; ceilings hidden.',fill='#293b32')
    im.save(ROOT/(name+'.png'))

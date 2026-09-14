"""Room sheets and state routes generated exclusively from layout.json."""
import plan2d as g

def room_drawings():
 out=[]
 for i,(room,notes) in enumerate(g.D['room_functions'].items(),19):
  rs=g.D['rooms'][room];x=min(b[0] for b in rs)-200;y=min(b[1] for b in rs)-200
  bounds=[x,y,max(b[0]+b[2] for b in rs)-x+200,max(b[1]+b[3] for b in rs)-y+200]
  q=g.Drawing(g.name(room)+' · 功能与状态尺寸');pt,r,s=q.plan(bounds,[50,120,900,650],labels=True)
  relevant=[(n,z) for n,z in g.D['use_zones'].items() if z['room']==room]
  for j,(n,z) in enumerate(relevant):
   color=['#467896','#b36b36','#34735e','#905681'][j%4]
   q.p.append(q.box(r(z['box']),'none',color,True))
   q.p.append(q.text(980,145+j*55,f'{j+1} {z["state"]}',16,color))
   q.p.append(q.text(980,166+j*55,f'{z["box"][2]} × {z["box"][3]} mm',14))
  yy=155+len(relevant)*55
  for n,f in g.F.items():
   if f['room']!=room:continue
   q.p.append(q.text(980,yy,g.name(n),14));q.p.append(q.text(980,yy+20,f'{f["box"][2]:g} × {f["box"][3]:g}',13));yy+=43
   if yy>775:break
  for n,f in g.F.items():
   if f['room']!=room or not f.get('facing',f.get('front')):continue
   direction=f.get('facing',f.get('front'));dx,dy={'north':(0,1),'south':(0,-1),'east':(1,0),'west':(-1,0)}[direction]
   x,y,w,h=f['box'];a=pt((x+w/2+dx*w*.18,y+h/2+dy*h*.18));b=pt((x+w/2+dx*w*.38,y+h/2+dy*h*.38))
   q.p.append(f'<path d="M{a[0]},{a[1]} L{b[0]},{b[1]}" stroke="#b36b36" stroke-width="3"/>')
   q.p.append(q.text(b[0],b[1],{'north':'↑','south':'↓','east':'→','west':'←'}[direction],18,g.C['orange'],'middle'))
  for n,v in g.D['accessories'].items():
   if v['room']==room:q.p.append(q.box(r(v['box']),'#90568140','#905681',True))
  if room=='Bath_Public':
   x,y,w,h=g.F['shower_public']['box'];gap=g.F['shower_public']['entry_gap_mm']
   q.p.append(q.box(r([x+w-25,y+gap,25,h-gap]),'#467896','#467896'))
   q.dim(pt((x+w,y)),pt((x+w,y+gap)),'入口700',20)
  for v in g.D['workflow_routes'].values():
   if room not in v['rooms']:continue
   points=[pt(p) for p in v['points'] if bounds[0]<=p[0]<=bounds[0]+bounds[2] and bounds[1]<=p[1]<=bounds[1]+bounds[3]]
   if len(points)>1:q.p.append('<polyline points="'+' '.join(f'{x:g},{y:g}' for x,y in points)+'" stroke="#467896" stroke-width="3" fill="none"/>')
  q.notes(notes+['虚线是使用状态，不能全部同时使用；路线命中及900目标不足见逐室核验表。'])
  n=f'{i:02d}-room-{room}.svg';q.save(n);out.append((n,g.name(room)+'逐室功能与状态'))
 return out

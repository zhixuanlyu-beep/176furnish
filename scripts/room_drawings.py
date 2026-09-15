"""Room sheets and state routes generated exclusively from layout.json."""
import plan2d as g

def room_drawings():
 out=[]
 for i,(room,notes) in enumerate(g.D['room_functions'].items(),19):
  rs=g.D['rooms'][room];x=min(b[0] for b in rs)-200;y=min(b[1] for b in rs)-200
  bounds=[x,y,max(b[0]+b[2] for b in rs)-x+200,max(b[1]+b[3] for b in rs)-y+200]
  q=g.Drawing(g.name(room)+' · 功能与状态尺寸');pt,r,s=q.plan(bounds,[50,120,900,650],labels=True)
  relevant=[(n,z) for n,z in g.D['use_zones'].items() if z['room']==room]
  yy=155
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
  q.notes(notes+['本图为正常布置；每个使用包络另出单状态图，路线与开门条件见专项报告。'])
  n=f'{i:02d}-room-{room}.svg';q.save(n);out.append((n,g.name(room)+'正常布置与功能'))
  for n,z in relevant:
   sq=g.Drawing(g.name(room)+' · '+z['state']+'（单状态）')
   pt,sr,ss=sq.plan(bounds,[50,120,900,650],labels=False)
   sq.p.append(sq.box(sr(z['box']),'#46789618',g.C['blue'],True))
   for j,t in enumerate([z['state'],f"{z['box'][2]}×{z['box'][3]}mm",'蓝框仅表示此状态','固定碰撞与错时分列','不证明其他状态可同时使用']):sq.p.append(sq.text(980,160+j*52,t,16))
   result=g.REPORT['evidence']['room_use_states'][n]
   sq.notes(['固定命中：'+('、'.join(result['fixed_hits']) or '当前算例无'),'全开门命中：'+('、'.join(result['open_door_hits']) or '当前算例无'),result['status']+'；真实家具外尺寸、五金与设备安装图仍待核。'])
   filename='state-'+n+'.svg';sq.save(filename);out.append((filename,g.name(room)+' · '+z['state']))
 return out

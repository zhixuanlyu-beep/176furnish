import plan2d as g
from validate_2d import shoes,handles
def txt(q,x,y,s,size=17):q.p.append(q.text(x,y,s,size))
def line(q,points,color='#b36b36',dash=False):
 q.p.append('<polyline points="'+' '.join(f'{x:g},{y:g}' for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="2"'+(' stroke-dasharray="5 4"' if dash else '')+'/>')

def family_drawings():
 items=[]
 def save(q,n,t):q.save(n);items.append((n,t))
 q=g.Drawing('家庭厅与玄关 · 嵌入柜墙')
 pt,r,s=q.plan([-3900,1500,4750,4950],[35,115,925,690],labels=True)
 for b in [[-2960,3174,600,588],[-2960,3762,600,588]]:q.p.append(q.box(r(b),'#46789614',g.C['blue'],True))
 for frames in shoes():
  for poly in frames[90]:line(q,[pt(v) for v in poly+[poly[0]]],dash=True)
 for n in ['family_entry_main_leaf','family_entry_secondary_leaf']:
  for poly in handles(g.DOORS[n])[90]:line(q,[pt(v) for v in poly+[poly[0]]],color='#b6473b')
 q.dim(pt((-3380,2724)),pt((-2480,2724)),'900',64)
 q.dim(pt((-3410,3174)),pt((-3410,4350)),'1176',-70)
 q.dim(pt((-2400,2724)),pt((-900,2724)),'1500门洞保留',98)
 for i,t in enumerate(['高鞋柜：900×400×2400','面向玄关，南面Y2724','柜背Y3124，浅柜Y3174','两柜间隔50','主门全开板面间隔87.5','50把手后余37.5','再计10安装余量：27.5','浅柜：450×1176×2300','双移门，轨道包含在柜深内','南段取物：关主门／错时','北段取物：保留常用书物','书桌、大件柜、门位保持']):txt(q,965,150+i*47,t,16)
 q.notes(['橙线：柜门投影／房门运动；蓝框：600mm深人员操作带；红线：概念把手突出量。','鞋柜开门与入户携篮通道重叠；浅柜南段操作与家庭厅主门全开重叠，分别错时。','不设置柜内换鞋凳；鞋柜把手采用≤5mm嵌入式，最终门套、五金和安装余量须放样。'])
 save(q,'13-family-entry.svg','家庭厅与玄关调整详图')

 q=g.Drawing('鞋柜立面 · 上下封闭，中间置物')
 scale=.245;ox=150;base=780
 sections=[('踢脚',0,100,'#758779'),('下封闭鞋区 · 3组',100,900,'#dce5d9'),('开放置物格 · 无座位',900,1250,'#d7ba96'),('上封闭鞋区 · 5组',1250,2350,'#dce5d9'),('顶部构造',2350,2400,'#758779'),('封闭收口 · 不计储物',2400,2800,'#dad6ca')]
 for label,z0,z1,color in sections:
  q.p.append(q.box([ox,base-z1*scale,900*scale,(z1-z0)*scale],color,attrs=f'data-elevation-section="{label}" data-z0="{z0}" data-z1="{z1}"'))
  txt(q,420,base-(z0+z1)/2*scale+5,f'{z0}–{z1}  {label}',16)
 for lo,hi,levels in [(100,900,3),(1250,2350,5)]:
  line(q,[(ox+450*scale,base-lo*scale),(ox+450*scale,base-hi*scale)])
  for i in range(1,levels):
   z=lo+(hi-lo)*i/levels;line(q,[(ox,base-z*scale),(ox+900*scale,base-z*scale)],'#748f7a',True)
 q.dim((ox,790),(ox+900*scale,790),'900外宽 · 双门名义450／扇',25)
 for i,t in enumerate(['容量按鞋型模板计算','两侧18板 → 净宽864','每双240宽×330深×180高','每层3双 × 8层 = 理论24双','下层净高约242.7／层','上层净高约198.4／层','拆一块下层板放较高靴：约21双','300宽鞋型：每层2双，共16双','350长鞋：不能按水平摆放适配','鞋盒及长靴须重新调层','25双不作为保证值','通风朝玄关，背面连续封闭']):txt(q,865,150+i*48,t,17)
 q.notes(['图中层板为可调整概念分层；层高按上下板及中间18mm层板扣除，门缝／五金仍待深化。','330有效深度与330鞋长模板相等，未另留鞋头余量；实鞋试放后再确认下单和容量。','置物格高350（标高900–1250）；灯具固定在格顶，驱动与接线可检修，不装在活动门板上。'])
 save(q,'14-shoe-elevation.svg','鞋柜立面与分层容量')

 q=g.Drawing('柜墙剖面与收口 · 概念构造')
 # Section uses millimetres in Y/Z with a labelled physical depth split.
 ox=130;base=780;s=.225
 for x,w,label,col in [(0,20,'20门板','#b69c7b'),(20,330,'330有效鞋深','#e2e8db'),(350,50,'50背衬构造','#7f9183')]:
  q.p.append(q.box([ox+x*s,base-2400*s,w*s,2400*s],col,attrs=f'data-depth-mm="{w}"'))
  txt(q,290,190+x*.9,label,17)
 q.p.append(q.box([ox,base-2800*s,400*s,400*s],'#dad6ca'))
 q.dim((ox,base+8),(ox+400*s,base+8),'400总深',35)
 txt(q,80,150,'南／玄关',18);txt(q,280,150,'北／家庭厅',18)
 txt(q,580,150,'原1010短墙段的平面分配',21)
 sx=590;sy=250;ss=.55
 for x,w,label in [(0,30,'西收口30'),(30,900,'柜体900'),(930,80,'门侧收口80')]:
  q.p.append(q.box([sx+x*ss,sy,w*ss,120*ss],'#dfe7dc',attrs=f'data-return-width-mm="{w}"'))
  txt(q,590,380+(0 if x==0 else 42 if x==30 else 84),label,18)
 txt(q,590,540,'30＋900＋80＝1010，1500门洞不变',21)
 txt(q,590,600,'柜背Y3124；浅柜南端Y3174 → 50间隔',18)
 txt(q,590,650,'原墙北面Y2844 → 柜背进入家庭厅280',18)
 txt(q,590,700,'2400以上400封闭收口，按2800概念层高',18)
 txt(q,590,750,'背衬独立固定、封闭密封；不作承重或隔声评级',18)
 q.notes(['50mm背衬为构造总占位，并不等于一块50mm背板；加固、连接件与现有墙框关系待深化。','西侧30与门侧80均为名义收口宽；不得侵占1500mm门洞，线路迁改及门框固定须现场核实。','结构和固定方式未通过现场确认前，不形成可施工拆墙结论，也不增加柜深来规避问题。'])
 save(q,'15-cabinet-section.svg','柜墙剖面与1010收口')

 q=g.Drawing('入户至家庭厅、A卧室、B卧室的完整路线')
 pt,r,s=q.plan([-4500,1500,6250,5800],[35,120,870,680],labels=False)
 colors=['#34735e','#467896','#b36b36']
 for i,(n,p) in enumerate(list(g.D['route_candidates'].items())[1:]):
  line(q,[pt(v) for v in p],colors[i]);txt(q,940,150+i*65,n,20)
 for i,t in enumerate(['鞋柜关闭，家庭厅子母门全开','相关房门按90°固定状态计算','600方篮，额外10／侧复核','三条路径均无概念实体命中','原西铰A门87–90°碰墙','东铰复算见逐室报告','须复核实物把手和开启限位','不移动门洞来规避问题']):txt(q,940,370+i*46,t,16)
 q.notes(['路线从同一入户外侧点开始；图上折线为篮中心。完整扫掠矩形和逐段坐标保存于核验数据。','家庭厅主门全开时浅柜南半段人员操作受限，关门取物与携篮通行必须错时。','A门的原有五金冲突单列为暂停五金定稿项；图上路线无命中不等于房门可按假定五金安装。'])
 save(q,'17-room-routes.svg','家庭厅与A／B卧室衣篮路线')
 return items

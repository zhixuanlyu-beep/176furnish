"""Current SVG world-coordinate, CSV, local link and model provenance checks."""
import csv,hashlib,json,math,re,struct
from pathlib import Path
from urllib.parse import unquote,urlsplit
from html.parser import HTMLParser
import xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1];D=json.loads((R/'data/layout.json').read_text());errors=[]
def fail(b,s):
 if not b:errors.append(s)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(n):return list(csv.DictReader((R/'tables'/n).open(encoding='utf-8-sig')))
svgerrors=[];labels=0;figures=json.loads((R/'reports/drawing_index.json').read_text())
png_state=json.loads((R/'reports/png_state.json').read_text())['assets']
for n,title in figures:
 p=R/'drawings/svg'/n;root=ET.parse(p).getroot();panels=0
 for group in root.iter():
  if group.get('data-plan')!='true':continue
  panels+=1;x,y,w,h=json.loads(group.get('data-world'));u,v,fw,fh=json.loads(group.get('data-frame'));scale=min(fw/w,fh/h);ox=u+(fw-w*scale)/2;oy=v+(fh-h*scale)/2;pulled=json.loads(group.get('data-pulled'))
  def inv(px,py):return [x+(px-ox)/scale,y+h-(py-oy)/scale]
  for item in group:
   name=item.get('data-object') or item.get('data-wall')
   if not name:continue
   b=json.loads('['+item.get('data-box')+']');expected=D['furniture'][name]['box'] if item.get('data-object') else D['walls'][name]
   fail(max(abs(a-b) for a,b in zip(b,expected))<=1,n+' metadata '+name);labels+=1
   if item.get('data-wall'):
    px,py,pw,ph=[float(item.get(k)) for k in ['x','y','width','height']];xx,yy=inv(px,py+ph);actual=[xx,yy,pw/scale,ph/scale];error=max(abs(a-b) for a,b in zip(actual,expected))
   else:
    points=[inv(*map(float,point.split(','))) for point in item.get('points').split()];bx,by,bw,bh=expected;ep=[[bx,by],[bx+bw,by],[bx+bw,by+bh],[bx,by+bh]];f=D['furniture'][name];angle=math.radians(f.get('rotation_degrees',0));cx=bx+bw/2;cy=by+bh/2
    ep=[[cx+(a-cx)*math.cos(angle)-(b-cy)*math.sin(angle),cy+(a-cx)*math.sin(angle)+(b-cy)*math.cos(angle)] for a,b in ep]
    if name in pulled:ep=[[a,b+(500 if f['facing']=='south' else -500)] for a,b in ep]
    error=max(abs(a-b) for pair,exp in zip(points,ep) for a,b in zip(pair,exp))
   svgerrors.append(error);fail(error<=1,n+' actual drawing '+name)
 png=R/'drawings/png'/Path(n).with_suffix('.png');fail(png.exists(),str(png)+' missing')
 if png.exists():
  data=png.read_bytes();fail(data[:8]==b'\x89PNG\r\n\x1a\n' and min(struct.unpack_from('>II',data,16))>=1000,n+' PNG format/size')
  fail(png_state.get(n,{}).get('svg_sha256')==sha(p) and png_state.get(n,{}).get('png_sha256')==sha(png),n+' stale PNG or provenance')
fail(len(figures)==22+len(D['room_functions'])+len(D['use_zones']),'base, room and separate state drawings required');fail(labels>0,'no tagged geometry checked')
furn=rows('家具尺寸表.csv');fail(len(furn)==len(D['furniture']),'furniture row count')
for v in furn:
 f=D['furniture'][v['编号']];actual=[float(v[k]) for k in ['西X_mm','南Y_mm','宽X_mm','深Y_mm','高_mm']];fail(max(abs(a-b) for a,b in zip(actual,[*f['box'],f['height']]))<=1,'furniture CSV '+v['编号'])
areas=rows('新图面积标注.csv');fail(len(areas)==len(D['rooms']),'area row count')
for v,(n,bs) in zip(areas,D['rooms'].items()):fail(abs(float(v['几何面积_m2'])-sum(b[2]*b[3]/1e6 for b in bs))<.0001,'area '+n)
two=json.loads((R/'reports/verification_2d.json').read_text());three=json.loads((R/'reports/verification_3d.json').read_text());config=json.loads((R/'model/scene_config.json').read_text())
fail(not two['hard_errors'],'2D hard errors');fail(three['checks_passed'],'3D errors');fail(three['layout_sha256']==config['layout_sha256']==sha(R/'data/layout.json'),'stale model layout')
from projection import load_snapshot
projection=load_snapshot()
fail(projection['layout_sha256']==sha(R/'data/layout.json'),'stale projection')
for report_name in ['ventilation.json','dimension_review.json']:
 extra=json.loads((R/'reports'/report_name).read_text())
 fail(extra['revision']==D['revision'] and extra['layout_sha256']==sha(R/'data/layout.json'),'stale '+report_name)
fail(two.get('layout_sha256')==sha(R/'data/layout.json'),'stale 2D verification')
fail(set(two['evidence']['room_function_coverage'])==set(D['rooms']),'all rooms must have function coverage')
fail(len(rows('辅助设施尺寸表.csv'))==len(D['accessories']),'accessory table count')
for ext in ['blend','glb']:fail(three[ext+'_sha256']==sha(R/f'model/whole_home_R10.5.{ext}'),'changed '+ext)
fail(len(two['evidence']['basket_routes'])==112,'112 route states required')
class Links(HTMLParser):
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ['href','src'] and v:links.append(v)
checkedlinks=0
for p in [R/'README.md',R/'AGENTS.md',*(R/'docs').glob('*')]:
 links=[];text=p.read_text()
 if p.suffix=='.html':Links().feed(text)
 else:links=re.findall(r'\]\(([^)]+)\)',text)
 for link in links:
  if link.startswith('#') or urlsplit(link).scheme:continue
  target=(p.parent/unquote(urlsplit(link).path)).resolve();fail(target.exists(),str(p.relative_to(R))+' broken '+link);checkedlinks+=1
# Current source/outputs must not depend on an older revision or user's home directory.
delivery_roots=['data','scripts','drawings','tables','model','reports','docs']
delivery_files=[R/'README.md',R/'AGENTS.md',R/'package.json',R/'.gitignore',*[p for n in delivery_roots for p in (R/n).rglob('*') if p.is_file()]]
for p in delivery_files:
 if not p.is_file() or any(k in p.parts for k in ['.git','__pycache__','node_modules']):continue
 if p.suffix in ['.py','.json','.csv','.svg','.html','.md','.cjs']:
  t=p.read_text();fail(not re.search(r'R10\.[23]',t),str(p.relative_to(R))+' obsolete version reference');fail(not re.search(r'/(?:Users|home)/[^/]+/',t),str(p.relative_to(R))+' machine absolute path')
report={'revision':'R10.5','passed':not errors,'drawings':len(figures),'tagged_geometry_count':labels,'max_svg_world_error_mm':max(svgerrors,default=None),'furniture_rows':len(furn),'table_count':len(list((R/'tables').glob('*.csv'))),'basket_states':112,'checked_local_links':checkedlinks,'errors':errors,'limits':['SVG annotations and actual geometry checked at 1mm; not a site survey.','No 3D render or full-scene continuous collision certification.','A-door hardware and operation conditions remain unresolved.']}
(R/'reports/delivery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
paths=sorted(p for p in delivery_files if p.is_file() and not any(x in p.parts for x in ['.git','__pycache__','node_modules']) and p.name!='manifest.sha256' and p.suffix not in ['.blend1','.pyc'])
(R/'reports/manifest.sha256').write_text(''.join(sha(p)+'  '+p.relative_to(R).as_posix()+'\n' for p in paths))
print(json.dumps(report,ensure_ascii=False,indent=2))
if errors:raise SystemExit(1)

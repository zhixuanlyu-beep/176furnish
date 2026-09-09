"""R10.1 model, source, browser and in-memory print checks. Never writes a PDF."""
from pathlib import Path
import csv
import hashlib
import json
import math
import os
import re
import xml.etree.ElementTree as ET
from playwright.sync_api import sync_playwright
import fitz
from PIL import Image
import r10_geometry as g
from r10_booklet import overlay_rows

HERE=Path(__file__).resolve().parent

def pdf_hashes():
    return {str(p.relative_to(HERE.parent)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in HERE.parent.rglob('*.pdf')}

def geometry_checks():
    trial=g.trial_metrics()
    assert not trial['fixed_conflicts'],trial['fixed_conflicts']
    assert not trial['fixed_wall_conflicts'],trial['fixed_wall_conflicts']
    for state in trial['states']:
        for key in ['chair_fixed_or_open_door_conflicts','basket_solid_conflicts','basket_chair_conflicts']:
            assert not state[key],(state,key)
        # Operation conflicts are computed and reported, never required to exist.
    t4,t6=g.BOXES['table4'],g.BOXES['table6']
    assert t4[0]+t4[2]==t6[0]+t6[2]==g.BOXES['island'][0]
    assert t6[0]==t4[0]-200 and t4[1:2]==t6[1:2]
    assert g.BOXES['prep'][0]+g.BOXES['prep'][2]==g.BOXES['sink'][0]
    assert g.BOXES['hob'][0]+g.BOXES['hob'][2]==g.BOXES['prep'][0]
    assert g.AC['AC05'][0]+g.AC['AC05'][2]<=g.OPENINGS['A_door']['box'][0]
    assert g.FAMILY['books'][0]+g.FAMILY['books'][2]<g.AC['AC05'][0]
    assert not any(g.intersection(g.AC01_STAND,b) for b in g.HOUSE.values())
    junctions=[('A_north','A_east'),('A_north','A_west'),('family_north','A_west'),
      ('entry_step','entry_lower'),('entry_step','living_west'),
      ('bath_kitchen_north','bath_east'),('bath_south2','bath_east'),
      ('CD','C_east2'),('CD','C_west_end'),('CD','D_east'),('D_west2','D_south1')]
    for a,b in junctions:
        x,y,w,h=g.WALLS[a]
        assert g.intersection((x-.01,y-.01,w+.02,h+.02),g.WALLS[b]),(a,b)
    for key,v in g.OPENINGS.items():
        if v['kind'].startswith('bay'):continue
        assert not any(g.intersection(v['box'],w) for w in g.WALLS.values()),key
    assert all(k in g.OPENINGS for k in ['B_bay','C_bay','D_bay'])
    for ident,services in g.AC_ROUTES.items():
        assert set(services)=={'refrigerant','power','condensate'}
        for pts in services.values():
            x,y,w,h=g.AC[ident];px,py=pts[0]
            assert x<=px<=x+w and y<=py<=y+h,(ident,pts[0])
    water=trial['water']
    assert water['horizontal_length_mm']==sum(water['horizontal_segments_mm'])
    assert not water['gravity_drainage_established']
    assert not water['pump_assumed'] and not water['structural_cutting_authorized']
    assert max(r[7] for r in overlay_rows())<4,overlay_rows()
    details=trial['r101']
    assert g.sector_hit(g.DOOR_MODEL['balconyB_door'],g.HOUSE['robot'])
    # Interior-angle collision, missed by checking only closed and fully open leaf.
    assert g.sector_hit({'hinge':(0,0),'start_deg':0,'leaf_mm':850,'thickness_mm':0},(500,500,20,20))
    assert not g.sector_hit({'hinge':(0,0),'start_deg':0,'leaf_mm':850,'thickness_mm':0},(850,850,20,20))
    assert g.AC['AC02']==(6380,-7250,240,800) and g.AC['AC03']==(3736,-3750,240,800)
    assert all(a['wall_segment_contains_backplate'] for a in details['ac_backplates'])
    assert details['ac_backplates'][1]['bay_margin_mm']==100
    assert details['bottleneck']['gap_mm']==624 and details['bottleneck']['remaining_mm']==24
    assert g.BOXES['island']==(2900,225,1000,750)
    assert all(not a['plan_intersections'] for a in details['supports'])
    assert len(details['supports'])==2 and all(len(a['knees'])==a['seats'] for a in details['supports'])
    assert all(a['issues'] for a in trial['states'])
    assert all(any(k=='tower_operator' for _,k in a['chair_operator_conflicts']) for a in trial['states'])
    assert any(g.intersection(b,g.BOXES['island_operator']) for b in g.swept_boxes(g.basket_path(False)))
    assert any(g.intersection(b,g.BOXES['dishwasher_operator']) for b in g.swept_boxes(g.basket_path(True)))
    assert details['robot_front']['wall_intersection'] is not None
    assert g.intersection(g.knee_boxes(6)[0],g.knee_boxes(6)[0]) # intrusive support fixture must collide
    trial['wall_junction_checks']=len(junctions)
    trial['source_landmark_max_residual_px']=max(r[7] for r in overlay_rows())
    return trial

def main():
    before=pdf_hashes();trial=geometry_checks()
    svg_paths=sorted(HERE.glob('*.svg'));assert len(svg_paths)==15
    trees={p.name:ET.parse(p).getroot() for p in svg_paths}
    plans=['01-furniture.svg','02-alterations-review.svg','03-services.svg','06-utility-storage.svg',
      '07-island-dining.svg','08-appliance-clearance.svg','09-workflows.svg','10-air-conditioning.svg',
      '11-source-overlay.svg','13-island-water-section.svg','14-robot-station-review.svg','15-island-table-connection.svg']
    for name in plans:
        root=trees[name]
        assert any(e.get('data-model')==g.model_digest() for e in root.iter()),name
        for el in root.iter():
            if el.get('data-wall'):
                assert [float(n) for n in el.get('data-box').split(',')]==list(g.WALLS[el.get('data-wall')]),name
                assert any(c.tag.endswith('rect') for c in el),name
    assert sum(bool(e.get('data-removal')) for e in trees['02-alterations-review.svg'].iter())==3
    for name in ['01-furniture.svg','03-services.svg','07-island-dining.svg','10-air-conditioning.svg']:
        assert not any(e.get('data-removal') for e in trees[name].iter()),name
    counts={}
    for p in HERE.glob('*.csv'):
        with p.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.reader(f))
        assert all(len(r)==len(rows[0]) for r in rows),p.name
        assert len({r[0] for r in rows[1:]})==len(rows)-1,p.name
        counts[p.name]=len(rows)-1
    assert counts['设备预留表.csv']==15 and counts['现场核验表.csv']==23
    doc=(HERE/'方案册.html').read_text(encoding='utf-8')
    page_count=len(re.findall('<section class="page"',doc));assert page_count>len(svg_paths),page_count
    reviewed=[HERE/'方案册.html',HERE/'README.md',HERE.parent/'README.md',*svg_paths,*HERE.glob('*.csv')]
    for p in reviewed:
        content=re.sub(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+','[source image]',p.read_text(encoding='utf-8-sig'))
        for stale in ['R9','R8','干岛无水','干岛台','无新增水槽','岛北桌南','南北相连岛桌','餐桌向南连接','客厅北侧过渡吊顶','\ufffd']:
            assert stale not in content,(p.name,stale)
    for term in ['1000×750','1600×800','独立蒸箱','独立烤箱','重力排水未成立','未确认合规','AC05','W0']:
        assert term in doc,term
    candidates=[os.getenv('FURNISH_BROWSER','')]
    candidates += [str(p) for p in Path('C:/Program Files (x86)/Microsoft/EdgeCore').glob('*/msedge.exe')]
    candidates += ['C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe','C:/Program Files/Google/Chrome/Application/chrome.exe']
    executable=next((p for p in candidates if p and Path(p).exists()),None)
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=executable,headless=True)
        page=browser.new_page(viewport={'width':1650,'height':1200},device_scale_factor=1)
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto((HERE/'方案册.html').as_uri(),wait_until='load');page.evaluate('document.fonts.ready')
        assert page.evaluate('document.fonts.check(\'16px "Microsoft YaHei"\')')
        page.emulate_media(media='print')
        bounds=page.evaluate('''() => [...document.querySelectorAll('.wide-drawing > svg, .drawing > svg')].flatMap(svg=>{
          const v=svg.viewBox.baseVal; return [...svg.querySelectorAll('text')].filter(t=>t.closest('svg')===svg && !t.closest('[data-model]')).flatMap(t=>{
            const b=t.getBBox();return b.x<v.x-1||b.y<v.y-1||b.x+b.width>v.x+v.width+1||b.y+b.height>v.y+v.height+1 ? [t.textContent] : [];
          });})''')
        assert not bounds,bounds
        layout=page.evaluate('''() => [...document.querySelectorAll('.page')].map(p=>{
          const b=p.getBoundingClientRect(),f=p.querySelector('footer').getBoundingClientRect();
          const bottom=Math.max(...[...p.children].filter(c=>c.tagName!=='FOOTER').map(c=>c.getBoundingClientRect().bottom));
          return {id:p.id,contentBottom:bottom-b.top,footerTop:f.top-b.top,overflow:bottom>f.top-8};})''')
        assert not any(p['overflow'] for p in layout),[p for p in layout if p['overflow']]
        pdf_content=page.pdf(prefer_css_page_size=True,print_background=True,display_header_footer=False)
        aliases={'preview-furniture.png':1,'preview-alterations.png':2,'preview-services.png':3,
          'preview-cabinet.png':4,'preview-coffee-water.png':5,'preview-utility-storage.png':6,
          'preview-island-dining.png':7,'preview-appliance-clearance.png':8,'preview-workflows.png':9,
          'preview-air-conditioning.png':10,'preview-new-source.png':11,'preview-source-overlay.png':11,
          'preview-ac01-ceiling.png':12,'preview-island-water.png':13,'preview-robot-station.png':14,'preview-island-table-connection.png':15}
        for name,n in aliases.items():page.locator(f'#p{n:02d}').screenshot(path=str(HERE/name))
        for path in svg_paths:
            preview=browser.new_page(viewport={'width':1150,'height':1000})
            preview.goto(path.as_uri());preview.evaluate('document.fonts.ready')
            preview.locator('svg').first.screenshot(path=str(HERE/('preview-'+path.stem+'.png')))
            preview.close()
        page.emulate_media(media='screen');mobile=[]
        for width in [320,390,768]:
            page.set_viewport_size({'width':width,'height':844})
            result=page.evaluate('({width:innerWidth,scrollWidth:document.documentElement.scrollWidth})')
            assert result['scrollWidth']<=width+1,result
            mobile.append(result)
            if width==390:page.locator('#p01').screenshot(path=str(HERE/'preview-mobile.png'))
        assert not errors,errors
        browser.close()
    pdf=fitz.open(stream=pdf_content,filetype='pdf');assert len(pdf)==page_count,len(pdf)
    sheet=Image.new('RGB',(1200,math.ceil(page_count/2)*445),'#e6e9e3')
    for n,p in enumerate(pdf):
        assert abs(p.rect.width-1190.55)<2 and abs(p.rect.height-841.89)<2
        text=p.get_text();assert '丽水嘉园' in text and '非施工图' in text,(n,text[:200])
        pix=p.get_pixmap(matrix=fitz.Matrix(.49,.49),alpha=False)
        sheet.paste(Image.frombytes('RGB',(pix.width,pix.height),pix.samples),((n%2)*600+8,(n//2)*445+12))
    sheet.save(HERE/'preview-all.png');pdf.close()
    assert before==pdf_hashes(),'An existing PDF changed'
    baseline=HERE/'protected-pdf-baseline.json'
    if baseline.exists():
        for path,digest in json.loads(baseline.read_text(encoding='utf-8')).items():
            assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest,path
    (HERE/'PDF文件保护说明.txt').write_text(f'R10.1最新{page_count}页A3横向内容已通过内存PDF渲染核查。本轮不生成磁盘PDF，不修改已有PDF。请阅读方案册.html、SVG、CSV及预览图；原有受保护PDF可能为旧版本，均保持原样。PDF、ZIP及加密文件不纳入Git发布。\n',encoding='utf-8',newline='\n')
    report={'file_checks':{'status':'passed','scope':'文件、回归、渲染及分页'},'geometry_findings':{'details':trial['r101'],'use_states':trial['states']},'site_verification':{'status':'pending','items':trial['r101']['site_pending']},'revision':'R10.1','scope':'文件/模型/渲染核查；不代表现场安装、结构、燃气或重力排水通过。',
      'model_sha256':g.model_digest(),'pdf_pages':page_count,'pdf_storage':'in-memory only; all existing PDFs untouched',
      'pdf_page_format':'A3 landscape','svg_parse':len(svg_paths),'svg_text_bounds':'passed',
      'source_alignment':'11 independently estimated image landmarks; max residual <4px, not survey accuracy',
      'trial_geometry':trial,'csv_counts':counts,'page_layout':layout,'mobile_sizes':mobile,
      'existing_pdfs_preserved':before,'browser_errors':errors,'svg_previews':[p.name for p in svg_paths]}
    (HERE/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
    print(json.dumps({'file_checks':'passed','site_verification':'pending','pages':page_count,'svgs':len(svg_paths),'mobile':mobile,'source_residual_px':trial['source_landmark_max_residual_px']},ensure_ascii=False))

if __name__=='__main__':main()

"""Full local verification, all previews, in-memory PDF only."""
from pathlib import Path
import csv
import json
import math
import os
import re
import tempfile
import shutil
import subprocess
import xml.etree.ElementTree as ET
from playwright.sync_api import sync_playwright
import fitz
from PIL import Image
import r10_geometry as g
from sync_model import ROOT,MODEL,REVISION,read,digest,require_verified
from r10_booklet import protected
HERE=Path(__file__).resolve().parent

def pdf_hashes():
    return {str(p.relative_to(ROOT)):digest(p) for p in ROOT.rglob('*') if p.suffix.lower() in ('.pdf','.zip')}

def geometry_checks():
    validation=g.M.validation()
    # A changed configuration with old verification must fail before any publish writes.
    with tempfile.TemporaryDirectory() as temp:
        dst=Path(temp)
        for n in ('scene_config.json','verification.json','geometry_snapshot.json'):
            shutil.copyfile(MODEL/n,dst/n)
        c=read(dst/'scene_config.json');c['furniture']['table4']['box'][0]+=.01
        (dst/'scene_config.json').write_text(json.dumps(c),encoding='utf-8')
        try:require_verified(dst)
        except RuntimeError as e:assert 'scene_config.json' in str(e)
        else:raise AssertionError('Stale configuration was accepted')
    validation['counterexamples'].append('配置修改而验证未更新时阻止发布')
    with tempfile.TemporaryDirectory() as temp:
        dst=Path(temp)
        for n in ('make_config.py','layout_rules.py','r10_baseline.json'):shutil.copyfile(MODEL/n,dst/n)
        subprocess.run([os.sys.executable,str(dst/'make_config.py')],check=True,capture_output=True)
        assert (dst/'scene_config.json').read_bytes()==(MODEL/'scene_config.json').read_bytes()
        sys_path=str(MODEL)
        if sys_path not in os.sys.path:os.sys.path.insert(0,sys_path)
        from layout_rules import apply_family_layout
        import copy
        current=read(MODEL/'scene_config.json')
        assert current == apply_family_layout(copy.deepcopy(current)) == apply_family_layout(apply_family_layout(copy.deepcopy(current)))
        validation['historical_baseline_migration']=dict(status='byte-identical',config_sha256=digest(MODEL/'scene_config.json'))
    # Round-trip actual manually filled fields in an isolated schedule directory.
    import r10_booklet as booklet
    with tempfile.TemporaryDirectory() as temp:
        dst=Path(temp)
        for n in ('schedule_baseline.json','generated_schedule_state.json'):shutil.copyfile(HERE/n,dst/n)
        name='现场核验表.csv';rows=list(csv.reader((HERE/name).open(encoding='utf-8-sig',newline='')))
        rows[1][6:]=['现场填写测试','evidence/example','核验人','2026-09-10']
        with (dst/name).open('w',encoding='utf-8-sig',newline='') as f:csv.writer(f).writerows(rows)
        previous=booklet.HERE
        try:
            booklet.HERE=dst
            data,_=booklet.schedules();assert data[name][1][6:]==rows[1][6:]
        finally:booklet.HERE=previous
    validation['manual_columns_preserved']='passed'
    return validation

def main():
    before=pdf_hashes();protected();trial=geometry_checks()
    manifest=read(HERE/'publication_manifest.json')
    for n,h in manifest['outputs'].items():assert digest(HERE/n)==h,n
    for n,h in manifest['generators'].items():assert digest(HERE/n)==h,n
    assert digest(ROOT/'README.md')==manifest['root_readme']
    svg_paths=sorted(HERE.glob('*.svg'));assert len(svg_paths)==15
    trees={p.name:ET.parse(p).getroot() for p in svg_paths}
    for name,root in trees.items():
        for el in root.iter():
            if el.get('data-wall'):
                assert [float(v) for v in el.get('data-box').split(',')]==g.WALLS[el.get('data-wall')],name
            if el.get('data-config-object'):
                assert [float(v) for v in el.get('data-box').split(',')]==g.BOXES[el.get('data-config-object')],name
            if el.get('data-opening'):
                assert [float(v) for v in el.get('data-box').split(',')]==g.OPENINGS[el.get('data-opening')]['box'],name
            if el.get('data-part'):
                assert el.get('data-part') in g.M.objects,name
                axes=list(map(int,el.get('data-axes').split(',')))
                obj=g.M.objects[el.get('data-part')]
                expected=g.hull([(v[axes[0]]*1000,-v[axes[1]]*1000) for v in obj['vertices']])
                actual=[tuple(map(float,p.split(','))) for p in el.get('points').split()]
                assert actual==expected,(name,el.get('data-part'))
    whole=trees['01-furniture.svg']
    assert {e.get('data-config-object') for e in whole.iter() if e.get('data-config-object')}=={n for n,f in g.C['furniture'].items() if f['room']!='Dining_6'}
    assert {e.get('data-wall') for e in whole.iter() if e.get('data-wall')}==set(g.WALLS)
    assert {e.get('data-opening') for e in whole.iter() if e.get('data-opening')}==set(g.OPENINGS)
    assert sum(bool(e.get('data-removal')) for e in trees['02-alterations-review.svg'].iter())==len(g.C['demolition'])
    counts={}
    for p in HERE.glob('*.csv'):
        with p.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.reader(f))
        assert all(len(r)==len(rows[0]) for r in rows),p.name
        assert len({r[0] for r in rows[1:]})==len(rows)-1,p.name
        counts[p.name]=len(rows)-1
    assert len(counts)==8 and counts['设备预留表.csv']==16 and counts['现场核验表.csv']==25
    original=read(HERE/'schedule_baseline.json')
    for name in ('新图面积标注.csv','新图尺寸标注.csv'):
        rows=list(csv.reader((HERE/name).open(encoding='utf-8-sig',newline='')))
        assert [r[:2] for r in rows]==[r[:2] for r in original[name]]
    assert list(csv.reader((HERE/'底图对位核验.csv').open(encoding='utf-8-sig',newline='')))==original['底图对位核验.csv']
    doc=(HERE/'方案册.html').read_text(encoding='utf-8')
    page_count=len(re.findall('<section class="page"',doc));assert page_count==manifest['pages']
    for term in [REVISION,'1800','401','正常就座可使用咖啡','重力排水未成立','未确认合规','原26条','600mm']:
        assert term in doc,term
    for p in [HERE/'README.md',ROOT/'README.md',*svg_paths,*HERE.glob('*.csv')]:
        content=p.read_text(encoding='utf-8-sig')
        for stale in ('1600×800','1800×800','咖啡1300','全拉椅650','局部624','仅余24','\ufffd'):
            assert stale not in content,(p.name,stale)
    # Relative local links, anchors and images are available offline.
    for href in re.findall(r'(?:href|src)="([^"]+)"',doc):
        if href.startswith('data:'):continue
        if href.startswith('#'):assert 'id="'+href[1:]+'"' in doc,href
        else:assert (HERE/href).exists(),href
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
        for path,expected_digest in json.loads(baseline.read_text(encoding='utf-8')).items():
            assert digest(Path(path))==expected_digest,path
    (HERE/'PDF文件保护说明.txt').write_text(f'R10.2最新{page_count}页A3横向内容已通过内存PDF渲染核查。本轮不生成磁盘PDF，不修改已有PDF。请阅读方案册.html、SVG、CSV及预览图；原有受保护PDF可能为旧版本，均保持原样。PDF、ZIP及加密文件不纳入Git发布。\n',encoding='utf-8',newline='\n')
    protected()
    report=dict(revision=REVISION,file_checks=dict(status='passed',svg_parse=15,csv_counts=counts,links='passed',svg_text_bounds='passed',browser_errors=errors),
        consistency_2d_3d=dict(status='passed',details=trial,source_files=g.M.report['files']),
        physical_collisions=dict(status='passed',checks={k:v for k,v in g.M.report['checks'].items() if 'clear' in k}),
        normal_operations=dict(status='passed',states=[s for s in g.M.states if s['state']=='normal']),
        temporary_restrictions=dict(states=[s for s in g.M.states if s['state']!='normal'],basket=trial['baskets']),
        site_conditions=dict(status='pending',items=[i for i in g.M.report['issues'] if i['category'] in ('unconfirmed_structural','conditional_equipment','bathroom_assumptions')],note='燃气、厂家设备及人体选型、安装硬件与现场接点仍待核'),
        pdf_pages=page_count,pdf_storage='in-memory only',page_layout=layout,mobile_sizes=mobile,protected_artifacts=before,
        svg_previews=[p.name for p in svg_paths],scope='文件及概念模型检查，不替代结构、燃气、安装和排水验收')
    (HERE/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(file_checks='passed',pages=page_count,svgs=15,csvs=8,mobile=mobile),ensure_ascii=False))

if __name__=='__main__':main()

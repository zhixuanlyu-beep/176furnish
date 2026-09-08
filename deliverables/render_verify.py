"""Render the booklet and check layout/data consistency; no site verification."""
from pathlib import Path
import csv
import hashlib
import json
import os
import re
import xml.etree.ElementTree as ET
from playwright.sync_api import sync_playwright
import fitz
import r9_geometry as geo

HERE = Path(__file__).resolve().parent
PDF_PATH = HERE/'方案册-R9.pdf'

def inspect_stored_pdf(written):
    """Record the current on-disk state without attempting to remove file protection."""
    protected=PDF_PATH.exists() and not PDF_PATH.read_bytes()[:8].startswith(b'%PDF-')
    if not written:
        message='R9最新15页A3横向内容已通过内存PDF渲染检查。本地已有PDF受保护或不可写，本轮未更新，可能不是最新排版；未移除或绕过保护。请阅读最新方案册.html、SVG与预览图。PDF不纳入Git发布。\n'
    elif protected:
        message='R9的15页A3横向PDF生成内容已通过检查。保存后的文件为非普通PDF格式，可能受本机文件保护；未尝试移除或绕过保护。请使用组织允许的阅读方式，或先阅读方案册.html和SVG/CSV。未验证此文件在其他设备可打开。\n'
    else:
        message='R9的15页A3横向PDF生成内容已通过检查。本次文件状态检查时为普通PDF；记录见verification.json。PDF仍排除在Git发布范围外。\n'
    (HERE/'PDF文件保护说明.txt').write_text(message,encoding='utf-8',newline='\n')
    if not written:
        return 'existing PDF not refreshed (protected or unwritable); latest PDF validated in memory only'
    return 'protected or transformed on disk; generated PDF content validated separately' if protected else 'ordinary PDF at last storage check'

def main():
    protected_before={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in HERE.glob('*.pdf') if not p.read_bytes().startswith(b'%PDF-')}
    assert len(list(HERE.glob('*.svg')))==10
    for path in HERE.glob('*.svg'):
        ET.parse(path)
    counts = {}
    for name, expected in [('家具尺寸表.csv',17),('设备预留表.csv',14),('水电点位表.csv',24),('现场核验表.csv',16),('新图面积标注.csv',11),('新图尺寸标注.csv',7),('电器上下水表.csv',16)]:
        with (HERE/name).open(encoding='utf-8-sig',newline='') as f:
            rows=list(csv.reader(f))
        assert len(rows)-1 == expected, name
        assert all(len(r)==len(rows[0]) for r in rows),name
        assert len({r[0] for r in rows[1:]})==expected,name
        counts[name]=expected
    doc=(HERE/'方案册.html').read_text(encoding='utf-8')
    for prefix,count in [('AC',5),('K',5),('C',3),('L',2),('R',1),('S',2),('H',5),('T',1),('M',3),('J',4)]:
        for n in range(1,count+1):
            assert f'{prefix}{n:02d}' in doc
    assert len(re.findall(r'<section class="page"',doc))==15
    reviewed=[HERE/'方案册.html',HERE/'README.md',HERE.parent/'README.md']
    reviewed += list(HERE.glob('*.svg'))+list(HERE.glob('*.csv'))
    for path in reviewed:
        content=path.read_text(encoding='utf-8-sig')
        content=re.sub(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+','[embedded source image]',content)
        for stale in ['R7','岛东桌西','岛在东、桌向西','C南侧靠东','独立储藏室推荐','面向西侧公共区','岛1200','宽1400–1600']:
            assert stale not in content,(path.name,stale)
    for term in ['950–1000','1000×750','独立蒸箱','独立烤箱','C/D南墙','AC05','未确认合规']:
        assert term in doc,term
    trial=geo.trial_metrics()
    assert not trial['occupied_chair_collisions']
    assert not trial['dishwasher_island_collision']
    assert 600<=trial['prep_surface']<=800
    assert trial['east_pulled_passage']>=900
    assert trial['dishwasher_east_bypass']>=trial['basket_trial_width']
    assert trial['site_verified'] is False
    route=trial['housekeeping_route']
    assert not route['door_only_swept_collisions'],route
    assert not route['pulled_chair_collision'],route
    assert not route['retained_wall_collisions'],route
    assert route['concurrent_operator_conflicts'], 'Do not erase the known concurrent-use limitation'
    for path in reviewed:
        content=path.read_text(encoding='utf-8-sig')
        content=re.sub(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+','[source]',content)
        for stale in ['R8','公卫南墙东段','门朝南','分隔开/闭','可关闭分隔','原系统核查保留','可选蒸烤','??','�']:
            assert stale not in content,(path.name,stale)
    for name in ['01-furniture.svg','03-services.svg','07-island-dining.svg','08-appliance-clearance.svg','09-workflows.svg','10-air-conditioning.svg']:
        root=ET.parse(HERE/name).getroot()
        assert not any(g.get('data-retained')=='false' for g in root.iter()),name
    assert sum(g.get('data-retained')=='false' for g in ET.parse(HERE/'02-alterations-review.svg').getroot().iter())==3
    candidates=[os.getenv('FURNISH_BROWSER','')]
    candidates += [str(p) for p in Path('C:/Program Files (x86)/Microsoft/EdgeCore').glob('*/msedge.exe')]
    candidates += ['C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe','C:/Program Files/Google/Chrome/Application/chrome.exe']
    browser_path=next((p for p in candidates if p and Path(p).exists()),None)
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(executable_path=browser_path,headless=True)
        page=browser.new_page(viewport={'width':1650,'height':1200},device_scale_factor=1)
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto((HERE/'方案册.html').as_uri(),wait_until='load')
        page.evaluate('document.fonts.ready')
        assert page.evaluate('Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)'), 'Source image failed to load'
        page.emulate_media(media='print')
        svg_bounds=page.evaluate('''() => [...document.querySelectorAll('svg')].flatMap(svg=>{
            const v=svg.viewBox.baseVal;
            return [...svg.querySelectorAll('text')].flatMap(t=>{
                const b=t.getBBox();
                return b.x<v.x-1 || b.y<v.y-1 || b.x+b.width>v.x+v.width+1 || b.y+b.height>v.y+v.height+1
                  ? [{page:svg.closest('.page').id,text:t.textContent,box:{x:b.x,y:b.y,w:b.width,h:b.height}}] : [];
            });
        })''')
        assert not svg_bounds,svg_bounds
        layout=page.evaluate('''() => [...document.querySelectorAll('.page')].map(p=>{
            const box=p.getBoundingClientRect(), footer=p.querySelector('footer').getBoundingClientRect();
            const content=[...p.children].filter(e=>e.tagName!=='FOOTER');
            return {id:p.id,height:box.height,scrollHeight:p.scrollHeight,
                contentBottom:Math.max(...content.map(e=>e.getBoundingClientRect().bottom))-box.top,
                footerTop:footer.top-box.top,
                overflow:Math.max(...content.map(e=>e.getBoundingClientRect().bottom))>footer.top-8};
        })''')
        for result in layout:
            assert not result['overflow'],result
        assert not errors,errors
        pdf_content=page.pdf(prefer_css_page_size=True,print_background=True,display_header_footer=False)
        pdf_written=False
        # Preserve an already protected file. Preview and content validation do
        # not require overwriting it or removing enterprise file protection.
        if not PDF_PATH.exists() or PDF_PATH.read_bytes().startswith(b'%PDF-'):
            try:
                PDF_PATH.write_bytes(pdf_content)
                pdf_written=True
            except OSError:
                pass
        page.locator('#p01').screenshot(path=str(HERE/'preview-furniture.png'))
        page.locator('#p02').screenshot(path=str(HERE/'preview-alterations.png'))
        page.locator('#p03').screenshot(path=str(HERE/'preview-services.png'))
        page.locator('#p08').screenshot(path=str(HERE/'preview-new-source.png'))
        page.locator('#p09').screenshot(path=str(HERE/'preview-coffee-water.png'))
        page.locator('#p10').screenshot(path=str(HERE/'preview-utility-storage.png'))
        page.locator('#p11').screenshot(path=str(HERE/'preview-island-dining.png'))
        page.locator('#p12').screenshot(path=str(HERE/'preview-appliance-clearance.png'))
        page.locator('#p13').screenshot(path=str(HERE/'preview-workflows.png'))
        page.locator('#p14').screenshot(path=str(HERE/'preview-air-conditioning.png'))
        page.locator('#p05').screenshot(path=str(HERE/'preview-cabinet.png'))
        for path in HERE.glob('*.svg'):
            preview=browser.new_page(viewport={'width':1150,'height':960})
            preview.goto(path.as_uri(),wait_until='load')
            preview.evaluate('document.fonts.ready')
            preview.locator('svg').screenshot(path=str(HERE/('preview-'+path.stem+'.png')))
            preview.close()
        page.emulate_media(media='screen')
        page.set_viewport_size({'width':390,'height':844})
        mobile=page.evaluate('({width:innerWidth,scrollWidth:document.documentElement.scrollWidth})')
        assert mobile['scrollWidth']<=mobile['width']+1,mobile
        page.locator('#p01').screenshot(path=str(HERE/'preview-mobile.png'))
        mobile_sizes=[mobile]
        for width in [320,768]:
            page.set_viewport_size({'width':width,'height':844})
            result=page.evaluate('({width:innerWidth,scrollWidth:document.documentElement.scrollWidth})')
            assert result['scrollWidth']<=result['width']+1,result
            mobile_sizes.append(result)
        browser.close()
    # Validate the content returned by the renderer. Do not undo enterprise file protection.
    pdf=fitz.open(stream=pdf_content,filetype='pdf')
    assert len(pdf)==15,len(pdf)
    for n,p in enumerate(pdf):
        assert abs(p.rect.width-1190.55)<2 and abs(p.rect.height-841.89)<2,(n,p.rect)
        content=p.get_text()
        assert '丽水嘉园' in content,(n,'Chinese text extraction failed')
        assert '非施工图' in content,(n,'Footer missing')
    # A contact sheet is for visual review of all pages, not a design/image edit.
    from PIL import Image,ImageOps,ImageDraw
    sheet=Image.new('RGB',(1200,8*445),'#e6e9e3')
    for n,p in enumerate(pdf):
        pix=p.get_pixmap(matrix=fitz.Matrix(.49,.49),alpha=False)
        im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        sheet.paste(im,((n%2)*600+8,(n//2)*445+12))
    sheet.save(HERE/'preview-all.png')
    pdf.close()
    storage_status=inspect_stored_pdf(pdf_written)
    for name,digest in protected_before.items():
        assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==digest,name
    report={'status':'passed','scope':'Document rendering and consistency only; no measured clearances, structural, utility or installation approval.',
            'pdf_pages':15,'revision':'R9','pdf_file':PDF_PATH.name,'pdf_storage':storage_status,'pdf_page_format':'A3 landscape','svg_parse':'10 passed','svg_text_bounds':'passed','r9_consistency':'passed','trial_geometry':trial,'csv_counts':counts,'page_layout':layout,'mobile_width':mobile,'mobile_sizes':mobile_sizes,'protected_pdfs_preserved':list(protected_before),'browser_errors':errors}
    (HERE/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()

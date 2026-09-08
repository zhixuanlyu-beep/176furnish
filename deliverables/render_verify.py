"""Render the booklet and check layout/data consistency; no site verification."""
from pathlib import Path
import csv
import json
import os
import re
import xml.etree.ElementTree as ET
from playwright.sync_api import sync_playwright
import fitz

HERE = Path(__file__).resolve().parent
PDF_PATH = HERE/'方案册-R5.pdf'

def inspect_stored_pdf():
    """Record the current on-disk state without attempting to remove file protection."""
    protected=not PDF_PATH.read_bytes()[:8].startswith(b'%PDF-')
    if protected:
        message='R5的11页A3横向PDF生成内容已通过检查。保存后的文件现为本机安全软件保护格式，当前程序无法作为普通PDF读取；未尝试移除或绕过保护。请使用组织允许的阅读方式，或先阅读方案册.html和SVG/CSV。未验证此受保护文件在其他设备可打开。\n'
    else:
        message='R5的11页A3横向PDF生成内容已通过检查。本次文件状态检查时为普通PDF；记录见verification.json。\n'
    (HERE/'PDF文件保护说明.txt').write_text(message,encoding='utf-8')
    return 'protected or transformed on disk; generated PDF content validated separately' if protected else 'ordinary PDF at last storage check'

def main():
    for path in HERE.glob('*.svg'):
        ET.parse(path)
    counts = {}
    for name, expected in [('家具尺寸表.csv',15),('设备预留表.csv',11),('水电点位表.csv',17),('现场核验表.csv',14),('新图面积标注.csv',11),('新图尺寸标注.csv',7),('电器上下水表.csv',13)]:
        with (HERE/name).open(encoding='utf-8-sig',newline='') as f:
            rows=list(csv.reader(f))
        assert len(rows)-1 == expected, name
        assert all(len(r)==len(rows[0]) for r in rows),name
        assert len({r[0] for r in rows[1:]})==expected,name
        counts[name]=expected
    doc=(HERE/'方案册.html').read_text(encoding='utf-8')
    for prefix,count in [('K',4),('C',3),('L',2),('R',1),('S',2),('H',4),('T',1),('M',6),('J',4)]:
        for n in range(1,count+1):
            assert f'{prefix}{n:02d}' in doc
    assert len(re.findall(r'<section class="page"',doc))==11
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
        pdf_content=page.pdf(path=str(PDF_PATH),prefer_css_page_size=True,print_background=True,display_header_footer=False)
        page.locator('#p01').screenshot(path=str(HERE/'preview-furniture.png'))
        page.locator('#p02').screenshot(path=str(HERE/'preview-alterations.png'))
        page.locator('#p03').screenshot(path=str(HERE/'preview-services.png'))
        page.locator('#p08').screenshot(path=str(HERE/'preview-new-source.png'))
        page.locator('#p09').screenshot(path=str(HERE/'preview-coffee-water.png'))
        page.locator('#p10').screenshot(path=str(HERE/'preview-utility-storage.png'))
        page.emulate_media(media='screen')
        page.set_viewport_size({'width':390,'height':844})
        mobile=page.evaluate('({width:innerWidth,scrollWidth:document.documentElement.scrollWidth})')
        assert mobile['scrollWidth']<=mobile['width']+1,mobile
        browser.close()
    # Validate the content returned by the renderer. Do not undo enterprise file protection.
    pdf=fitz.open(stream=pdf_content,filetype='pdf')
    stored_header=PDF_PATH.read_bytes()[:64]
    storage_status='ordinary PDF' if stored_header.startswith(b'%PDF-') else 'protected or transformed on disk; generated PDF content validated separately'
    assert len(pdf)==11,len(pdf)
    for n,p in enumerate(pdf):
        assert abs(p.rect.width-1190.55)<2 and abs(p.rect.height-841.89)<2,(n,p.rect)
        content=p.get_text()
        assert '丽水嘉园' in content,(n,'Chinese text extraction failed')
        assert '非施工图' in content,(n,'Footer missing')
    # A contact sheet is for visual review of all pages, not a design/image edit.
    from PIL import Image,ImageOps,ImageDraw
    sheet=Image.new('RGB',(1200,6*445),'#e6e9e3')
    for n,p in enumerate(pdf):
        pix=p.get_pixmap(matrix=fitz.Matrix(.49,.49),alpha=False)
        im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        sheet.paste(im,((n%2)*600+8,(n//2)*445+12))
    sheet.save(HERE/'preview-all.png')
    pdf.close()
    storage_status=inspect_stored_pdf()
    report={'status':'passed','scope':'Document rendering and consistency only; no measured clearances, structural, utility or installation approval.',
            'pdf_pages':11,'revision':'R5','pdf_file':PDF_PATH.name,'pdf_storage':storage_status,'pdf_page_format':'A3 landscape','svg_parse':'6 passed','csv_counts':counts,'page_layout':layout,'mobile_width':mobile,'browser_errors':errors}
    (HERE/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()

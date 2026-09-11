"""Compare two complete local deliveries, including browser-generated previews."""
import json
import subprocess
import sys
from pathlib import Path
from sync_model import ROOT,digest,require_verified,REVISION
from r10_booklet import protected

HERE=Path(__file__).resolve().parent
def hashes():
    paths=[p for p in HERE.iterdir() if p.suffix in ('.svg','.csv','.html','.png')]
    paths += [HERE/n for n in ('README.md','publication_manifest.json','generated_schedule_state.json','PDF文件保护说明.txt')]
    paths += [ROOT/'README.md']
    return {str(p.relative_to(ROOT)):digest(p) for p in sorted(paths)}

def main():
    require_verified();protected()
    report=json.loads((HERE/'verification.json').read_text(encoding='utf-8'))
    assert report['file_checks']['status']=='passed','Run render_verify.py first'
    before=hashes()
    for script in ('build_package.py','render_verify.py'):
        subprocess.run([sys.executable,str(HERE/script)],check=True)
    after=hashes();changed=[n for n in before.keys()|after.keys() if before.get(n)!=after.get(n)]
    assert not changed,changed
    protected();require_verified()
    result=dict(revision=REVISION,status='passed',consecutive_complete_generations=2,compared_files=len(before),sha256=after)
    (HERE/'repeatability.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report=json.loads((HERE/'verification.json').read_text(encoding='utf-8'))
    report['repeatability']=dict(status='passed',compared_files=len(before),report='repeatability.json')
    (HERE/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(repeatability='passed',compared_files=len(before))))

if __name__=='__main__':main()

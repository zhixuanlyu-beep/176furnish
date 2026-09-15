"""Compare one same-machine 2D rebuild; never invokes 3D rendering."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def snapshot():
    paths = [p for directory in ('drawings/svg', 'drawings/png', 'tables')
             for p in (ROOT / directory).iterdir() if p.is_file()]
    paths += [ROOT / p for p in ('docs/方案册.html', 'reports/verification_2d.json',
                                'reports/drawing_index.json', 'reports/png_state.json', 'reports/ventilation.json', 'reports/dimension_review.json')]
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths)}

def main():
    before = snapshot()
    env = dict(os.environ, PYTHONUTF8='1')
    for command in ([sys.executable, 'scripts/build_2d.py'], ['node', 'scripts/preview_2d.cjs']):
        result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True,
                                text=True, encoding='utf-8', errors='replace')
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
    after = snapshot()
    different = [p for p in sorted(before.keys() | after.keys()) if before.get(p) != after.get(p)]
    report = {'revision': 'R10.5', 'same_machine_repeatable': not different,
              'checked_files': len(after), 'scope': 'Current SVG, PNG, CSV, offline booklet and 2D reports; one repeated build; no 3D binary reproducibility claim',
              'different_files': different,
              'layout_sha256': hashlib.sha256((ROOT/'data/layout.json').read_bytes()).hexdigest(),
              'png_engine': json.loads((ROOT/'reports/png_state.json').read_text(encoding='utf-8'))['engine']}
    (ROOT/'reports/repeatability.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))
    if different:
        raise SystemExit(1)

if __name__ == '__main__':
    main()

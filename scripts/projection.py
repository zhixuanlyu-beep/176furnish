"""Deterministic component orthographic snapshot of the current Blender scene.

No raster sampling and no rendering. Uses evaluated mesh silhouettes per component,
not a hidden-line architectural cut. Hashes bind the snapshot to geometry sources.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ('data/layout.json', 'data/style3d.json', 'scripts/build_3d.py',
           'scripts/model_config.py', 'scripts/cabinetry.py', 'scripts/details_3d.py',
           'scripts/projection.py')


def source_hashes():
    return {n: hashlib.sha256((ROOT / n).read_bytes()).hexdigest() for n in SOURCES}


def hull(points):
    points = sorted(set(points))
    def cross(a, b, c):
        return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    if len(points) < 3:
        return points
    lower, upper = [], []
    for p in points:
        while len(lower) > 1 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(points):
        while len(upper) > 1 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def export_snapshot(config, write=True):
    import bpy
    scene = bpy.context.scene
    scene.frame_set(1)
    hidden = {c.name: c.hide_viewport for c in bpy.data.collections}
    for c in bpy.data.collections:
        c.hide_viewport = False
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    items = []
    for obj in sorted(scene.objects, key=lambda o: o.name):
        if obj.type != 'MESH':
            continue
        owner = obj
        while owner.parent:
            owner = owner.parent
        if owner.name not in config['furniture']:
            continue
        eo = obj.evaluated_get(dg)
        mesh = eo.to_mesh()
        points = [eo.matrix_world @ v.co for v in mesh.vertices]
        polygon = [list(p) for p in hull([(round(p.x*1000, 3), round(p.y*1000, 3)) for p in points])]
        if len(polygon) >= 3:
            items.append({'name': obj.name, 'owner': owner.name, 'polygon_mm': polygon,
                          'z_min_mm': round(min(p.z for p in points)*1000, 3),
                          'z_max_mm': round(max(p.z for p in points)*1000, 3),
                          'material': obj.data.materials[0].name if obj.data.materials else ''})
        eo.to_mesh_clear()
    for name, value in hidden.items():
        bpy.data.collections[name].hide_viewport = value
    result = {'revision': config['revision'], 'layout_sha256': config['layout_sha256'],
              'sources': source_hashes(), 'frame': 1, 'units': 'mm',
              'method': 'Evaluated per-component XY convex silhouettes; internal components included; not hidden-line removal or construction drawing.',
              'components': items}
    if write:
        (ROOT/'model/projection_snapshot.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return result


def load_snapshot():
    path = ROOT/'model/projection_snapshot.json'
    if not path.exists():
        raise RuntimeError('先运行 build_3d.py 生成当前模型投影快照；不允许使用旧模型。')
    snapshot = json.loads(path.read_text(encoding='utf-8'))
    if snapshot['sources'] != source_hashes():
        raise RuntimeError('模型投影已过期：布局或三维生成工具改变，须先重建三维。')
    return snapshot

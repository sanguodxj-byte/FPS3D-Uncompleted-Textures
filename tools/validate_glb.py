#!/usr/bin/env python3
"""GLB 交付规范校验（见 docs/GLB_SPEC.md）。
用法: python3 tools/validate_glb.py [文件或目录 ...]   默认校验 models/
任一文件不合格即以退出码 1 结束，并逐条列出原因。"""
import sys, os, json, struct, glob
import numpy as np

GROUND_TOL = 0.002
def load(p):
    d = open(p, 'rb').read()
    if d[:4] != b'glTF': raise ValueError('不是 GLB')
    L = struct.unpack('<I', d[12:16])[0]; j = json.loads(d[20:20 + L])
    bo = 20 + L; bl = struct.unpack('<I', d[bo:bo + 4])[0]
    return j, d[bo + 8:bo + 8 + bl]

def acc(j, b, i):
    a = j['accessors'][i]; v = j['bufferViews'][a['bufferView']]
    n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[a['type']]
    dt = {5126: np.float32, 5125: np.uint32, 5123: np.uint16, 5121: np.uint8}[a['componentType']]
    r = np.frombuffer(b, dt, a['count'] * n, v.get('byteOffset', 0) + a.get('byteOffset', 0))
    return r.reshape(-1, n) if n > 1 else r

def check(p):
    errs = []; name = os.path.basename(p)
    is_top = '__Top' in name
    try:
        j, b = load(p)
    except Exception as e:
        return [f'无法读取: {e}']
    ex = j.get('asset', {}).get('extras', {})
    if not ex.get('defName'): errs.append('asset.extras 缺 defName')
    if is_top and ex.get('part') not in (None, 'turretTop'): errs.append('__Top 的 extras.part 应为 turretTop')
    # 1. 只允许本体网格，不得带 Outline
    names = [m.get('name', '') for m in j.get('meshes', [])] + [n.get('name', '') for n in j.get('nodes', [])] + \
            [m.get('name', '') or '' for m in j.get('materials', [])]
    if any('outline' in (n or '').lower() for n in names): errs.append('含 Outline 网格/节点/材质（规范：描边由引擎 BuildHull 生成，文件内不得带）')
    mesh_nodes = [n for n in j.get('nodes', []) if 'mesh' in n]
    if len(j.get('meshes', [])) != 1 or len(mesh_nodes) != 1: errs.append(f'应只有 1 个本体网格，实际 meshes={len(j.get("meshes", []))} 网格节点={len(mesh_nodes)}')
    for n in mesh_nodes:
        if any(k in n for k in ('rotation', 'scale', 'matrix')) or any(abs(t) > 1e-6 for t in n.get('translation', [0, 0, 0])):
            errs.append('网格节点带变换（须先应用全部变换，节点 TRS 为单位）')
    # 2. 材质
    for m in j.get('materials', []):
        if 'KHR_materials_unlit' not in m.get('extensions', {}): errs.append('材质缺 KHR_materials_unlit')
        if 'baseColorTexture' not in m.get('pbrMetallicRoughness', {}): errs.append('材质缺 baseColorTexture')
    for im in j.get('images', []):
        if 'uri' in im: errs.append('贴图须内嵌，不得外链 uri')
    if not j.get('images'): errs.append('缺内嵌贴图')
    # 3. 几何：法线 / UV / 接地
    ymin = None
    for m in j.get('meshes', []):
        for pr in m['primitives']:
            at = pr['attributes']
            for k in ('POSITION', 'NORMAL', 'TEXCOORD_0'):
                if k not in at: errs.append(f'图元缺 {k}')
            if pr.get('mode', 4) != 4: errs.append('图元须为三角形 (mode 4)')
            if 'POSITION' not in at or 'indices' not in pr: continue
            P = acc(j, b, at['POSITION']); I = acc(j, b, pr['indices']).astype(np.int64)
            if len(I) % 3 or I.max() >= len(P): errs.append('索引越界或不是三角形'); continue
            ymin = P[:, 1].min() if ymin is None else min(ymin, P[:, 1].min())
            if not np.isfinite(P).all(): errs.append('POSITION 含 NaN/Inf')
            if 'NORMAL' in at:
                N = acc(j, b, at['NORMAL'])
                ln = np.linalg.norm(N, axis=1)
                if (abs(ln - 1) > 1e-3).any(): errs.append('NORMAL 未归一化')
                T = P[I.reshape(-1, 3)]; fn = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
                ok = np.linalg.norm(fn, axis=1) > 1e-10
                vn = N[I.reshape(-1, 3)].mean(1)
                bad = (np.einsum('ij,ij->i', fn[ok], vn[ok]) <= 0).mean() if ok.any() else 0
                if bad > 0.01: errs.append(f'NORMAL 与三角形绕序相反的比例 {bad:.1%}（法线须朝外）')
            if 'TEXCOORD_0' in at:
                UV = acc(j, b, at['TEXCOORD_0'])
                if (UV < -0.01).any() or (UV > 1.01).any(): errs.append('UV 超出 0–1（图集应在 0–1 内）')
    if ymin is not None and not is_top and abs(ymin) > GROUND_TOL:
        errs.append(f'最低点 Y={ymin:+.3f}m，须吸附到 Y=0（{"悬空" if ymin > 0 else "下陷"}）')
    return errs

def main(args):
    files = []
    for a in (args or ['models']):
        files += sorted(glob.glob(os.path.join(a, '*.glb'))) if os.path.isdir(a) else [a]
    bad = 0
    for f in files:
        e = check(f)
        if e:
            bad += 1; print(f'✗ {f}'); [print('    -', x) for x in e]
    print(f'{len(files) - bad}/{len(files)} 通过')
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

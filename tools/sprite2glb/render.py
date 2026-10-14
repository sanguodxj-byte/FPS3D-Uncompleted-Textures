import numpy as np, trimesh, math
from PIL import Image


def render(glb, yaw_deg, pitch_deg, W=320, Hh=240, bg=(48, 48, 48), pad=0.85):
    sc = trimesh.load(glb)
    yaw, pitch = math.radians(yaw_deg), math.radians(pitch_deg)
    Ry = np.array([[math.cos(yaw), 0, math.sin(yaw)], [0, 1, 0], [-math.sin(yaw), 0, math.cos(yaw)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(pitch), -math.sin(pitch)], [0, math.sin(pitch), math.cos(pitch)]])
    R = Rx @ Ry
    allv = np.vstack([g.vertices for g in sc.geometry.values()]) @ R.T
    lo, hi = allv.min(0), allv.max(0)
    scale = pad * min(W / max(hi[0] - lo[0], 1e-6), Hh / max(hi[1] - lo[1], 1e-6))
    cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
    img = np.zeros((Hh, W, 3), np.float32); img[:] = bg
    zb = np.full((Hh, W), -1e9)
    for name, g in sc.geometry.items():
        hull = 'Outline' in name
        Vv = g.vertices @ R.T
        sx = (Vv[:, 0] - cx) * scale + W / 2
        sy = -(Vv[:, 1] - cy) * scale + Hh / 2
        if not hull:
            tex = np.array(g.visual.material.baseColorTexture.convert('RGB')).astype(np.float32)
            th, tw = tex.shape[:2]; uv = g.visual.uv
        for f in g.faces:
            p = np.c_[sx[f], sy[f]]
            area = (p[1, 0] - p[0, 0]) * (p[2, 1] - p[0, 1]) - (p[2, 0] - p[0, 0]) * (p[1, 1] - p[0, 1])
            if area >= 0: continue
            x0, x1 = int(max(0, p[:, 0].min())), int(min(W - 1, p[:, 0].max() + 1))
            y0, y1 = int(max(0, p[:, 1].min())), int(min(Hh - 1, p[:, 1].max() + 1))
            if x0 > x1 or y0 > y1: continue
            X, Y = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            w0 = ((p[1, 0] - X) * (p[2, 1] - Y) - (p[2, 0] - X) * (p[1, 1] - Y)) / area
            w1 = ((p[2, 0] - X) * (p[0, 1] - Y) - (p[0, 0] - X) * (p[2, 1] - Y)) / area
            w2 = 1 - w0 - w1
            m = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
            if not m.any(): continue
            z = w0 * Vv[f[0], 2] + w1 * Vv[f[1], 2] + w2 * Vv[f[2], 2]
            ys, xs = np.nonzero(m); zz = z[m]; gy, gx = ys + y0, xs + x0
            ok = zz > zb[gy, gx]; gy, gx, zz = gy[ok], gx[ok], zz[ok]
            zb[gy, gx] = zz
            if hull:
                img[gy, gx] = 0
            else:
                t = uv[f]; a, b, c = w0[m][ok], w1[m][ok], w2[m][ok]
                uu = (a * t[0, 0] + b * t[1, 0] + c * t[2, 0]) * tw
                vv = (1 - (a * t[0, 1] + b * t[1, 1] + c * t[2, 1])) * th
                img[gy, gx] = tex[np.clip(vv.astype(int), 0, th - 1), np.clip(uu.astype(int), 0, tw - 1)]
    return Image.fromarray(img.clip(0, 255).astype(np.uint8))


def sheet(glb, src_pngs, kind, out):
    pitch = {'oblique': 34.06, 'slab': 89.9, 'lathe': 0.0}[kind]
    tiles = []
    for p in src_pngs[:3]:
        s = Image.open(p).convert('RGBA'); bg = Image.new('RGBA', s.size, (48, 48, 48, 255)); bg.alpha_composite(s)
        bg = bg.convert('RGB'); bg.thumbnail((240, 240)); t = Image.new('RGB', (240, 240), (32, 32, 32)); t.paste(bg, ((240 - bg.width) // 2, (240 - bg.height) // 2)); tiles.append(t)
    views = [(0, pitch), (-35, 30), (35, 30), (145, 30)] if kind != 'lathe' else [(0, 0), (60, 15), (0, 35), (90, 0)]
    rs = [render(glb, y, p, 240, 240) for y, p in views]
    n = max(len(tiles), len(rs))
    im = Image.new('RGB', (240 * n, 480), (32, 32, 32))
    for i, t in enumerate(tiles): im.paste(t, (i * 240, 0))
    for i, r in enumerate(rs): im.paste(r, (i * 240, 240))
    im.save(out)

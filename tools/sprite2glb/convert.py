"""RimWorld sprite -> low-poly GLB, textures projected through the sprite cameras.

Building / directional: oblique prism (pitch asin(0.56)) from the south view; side faces
from east (mirrored for west), back faces from north.  Item (single view): top-down slab.
Plant: lathe (front orthographic projection).  Materials are KHR_materials_unlit, plus an
inverted-hull black outline node.  Model frame: +X east, +Y up, +Z south (front), 1 unit = 1 cell.
"""
import math, re, json, sys, os
import numpy as np, cv2, trimesh
from PIL import Image
from scipy import ndimage
from shapely.geometry import Polygon, MultiPolygon
from shapely.validation import make_valid

A = 0.56
B = math.cos(math.asin(A))
DIRS = ('south', 'east', 'north', 'west')


# ---------------------------------------------------------------- texture prep
def load_view(path):
    rgba = np.array(Image.open(path).convert('RGBA'))
    h, w = rgba.shape[:2]
    mask = rgba[..., 3] > 128
    lum = rgba[..., :3].astype(np.float32) @ np.array([0.299, 0.587, 0.114])
    kmax = max(2, round(max(w, h) / 25))
    cur, k = mask, 0
    for i in range(1, kmax + 1):
        nxt = ndimage.binary_erosion(cur)
        ring = cur & ~nxt
        if not nxt.any() or nxt.sum() < 0.4 * mask.sum():
            break
        if ring.any() and np.median(lum[ring]) > 45 and i > 1:
            break
        cur, k = nxt, i
    er = cur
    if er.sum() < 0.35 * mask.sum():
        k, er = 0, mask
    src = er if er.any() else mask
    _, (iy, ix) = ndimage.distance_transform_edt(~src, return_indices=True)
    tex = rgba[iy, ix].copy()
    tex[..., 3] = 255
    return dict(tex=tex, mask=src, w=w, h=h, k=k, path=path)


def bbox(mask):
    ys, xs = np.nonzero(mask)
    return xs.min(), xs.max() + 1, ys.min(), ys.max() + 1


def front_band(v, want_ok=False):
    tex, mask = v['tex'], v['mask']
    lum = tex[..., :3].astype(np.float32) @ np.array([0.299, 0.587, 0.114])
    x0, x1, y0, y1 = bbox(mask)
    Hs = y1 - y0
    cand, strength = [], []
    for x in range(x0, x1, max(1, (x1 - x0) // 40)):
        col = np.nonzero(mask[:, x])[0]
        if len(col) < 0.5 * Hs:
            continue
        t, b = col.min(), col.max() + 1
        prof = ndimage.uniform_filter1d(lum[t:b, x], 3)
        n = len(prof)
        best, by = 0, None
        for y in range(int(n * 0.4), int(n * 0.92)):
            d = prof[max(0, y - 3):y].mean() - prof[y:y + 3].mean()
            if d > best:
                best, by = d, y
        if by is not None:
            cand.append(n - by)
            strength.append(best)
    ok = bool(cand) and np.median(strength) > 8
    band = float(np.median(cand)) if ok else 0.25 * Hs
    band = float(np.clip(band, 0.08 * Hs, 0.6 * Hs))
    return (band, ok) if want_ok else band


# ---------------------------------------------------------------- mesh helpers
def extrude_poly(poly, y0, y1):
    """poly in (x, z) model px; returns prism mesh, y up."""
    p = Polygon([(x, -z) for x, z in poly.exterior.coords],
                [[(x, -z) for x, z in r.coords] for r in poly.interiors])
    m = trimesh.creation.extrude_polygon(p, y1 - y0)
    v = m.vertices.copy()
    m.vertices = np.c_[v[:, 0], y0 + v[:, 2], -v[:, 1]]
    if m.volume < 0:
        m.invert()
    return m


def largest(geom):
    geom = make_valid(geom)
    if isinstance(geom, Polygon):
        return [geom]
    polys = [g for g in getattr(geom, 'geoms', []) if isinstance(g, Polygon)]
    polys.sort(key=lambda g: -g.area)
    return [g for g in polys if g.area > 0.02 * polys[0].area] if polys else []


def hull_of(mesh, off):
    h = trimesh.Trimesh(mesh.vertices.copy(), mesh.faces.copy())
    h.merge_vertices()
    hv = h.vertices + h.vertex_normals * off
    return trimesh.Trimesh(hv, h.faces[:, ::-1], process=False)


class Atlas:
    def __init__(self, views):
        self.views = views
        self.off = {}
        x = 0
        for name, v in views.items():
            self.off[name] = x
            x += v['w']
        self.sw_x = x
        x += 8
        self.W, self.H = x, max(v['h'] for v in views.values())
        img = np.zeros((self.H, self.W, 4), np.uint8)
        for name, v in views.items():
            img[:v['h'], self.off[name]:self.off[name] + v['w']] = v['tex']
        s = next(iter(views.values()))
        dark = (s['tex'][s['mask']][:, :3].mean(0) * 0.55).astype(np.uint8)
        img[:, self.sw_x:, :3] = dark
        img[:, self.sw_x:, 3] = 255
        img[self.H - max(v['h'] for v in views.values()):, :, 3] = 255
        self.img = Image.fromarray(img)

    def uv(self, name, u, v):
        vw = self.views[name]
        u = np.clip(u, 0.5, vw['w'] - 0.5) + self.off[name]
        v = np.clip(v, 0.5, vw['h'] - 0.5)
        return np.c_[u / self.W, 1 - v / self.H]

    def swatch(self, n):
        return np.tile([[(self.sw_x + 4) / self.W, 0.5]], (n, 1))


def finish(V, F, UV, atlas_img, hulls, ppu, center_xz, out_path, extras):
    cx, cz = center_xz
    def tw(P):
        return np.c_[(P[:, 0] - cx) / ppu, P[:, 1] / ppu, (P[:, 2] - cz) / ppu]
    mat = trimesh.visual.material.PBRMaterial(baseColorTexture=atlas_img, metallicFactor=0.0, roughnessFactor=1.0)
    body = trimesh.Trimesh(tw(V), F, visual=trimesh.visual.TextureVisuals(uv=UV, material=mat), process=False)
    sc = trimesh.Scene()
    sc.add_geometry(body, node_name='Body', geom_name='Body')
    if hulls:
        hm = trimesh.util.concatenate(hulls)
        hm = trimesh.Trimesh(tw(hm.vertices), hm.faces, process=False)
        hm.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
            baseColorFactor=[0, 0, 0, 255], metallicFactor=0, roughnessFactor=1))
        sc.add_geometry(hm, node_name='Outline', geom_name='Outline')
    glb = sc.export(file_type='glb')
    import pygltflib
    g = pygltflib.GLTF2.load_from_bytes(glb)
    g.extensionsUsed = ['KHR_materials_unlit']
    for m in g.materials:
        m.extensions = {'KHR_materials_unlit': {}}
    for s in g.samplers or []:
        pass
    g.asset.extras = extras
    g.save_binary(out_path)
    return body


def unshare(mesh):
    V = mesh.vertices[mesh.faces].reshape(-1, 3)
    F = np.arange(len(V)).reshape(-1, 3)
    return V, F, mesh.face_normals


# ---------------------------------------------------------------- building (oblique prism)
def build_oblique(views, out_path, extras):
    main = 'south' if 'south' in views else ('east' if 'east' in views else next(iter(views)))
    S = views[main]
    mask = S['mask']
    x0, x1, y0, y1 = bbox(mask)
    band = front_band(S)
    H = band / B
    V0 = float(y1)
    step = max(1, (x1 - x0) // 40)
    front, back = [], []
    xs = list(range(x0, x1, step)) + [x1 - 1]
    for x in xs:
        col = np.nonzero(mask[:, x])[0]
        if not len(col):
            continue
        t, b = col.min(), col.max() + 1
        zf = (b - V0) / A
        zb = (t - V0 + H * B) / A
        if zb > zf - 1:
            zb = zf - 1
        front.append((x, zf)); back.append((x, zb))
    front[0] = (x0, front[0][1]); front[-1] = (x1, front[-1][1])
    back[0] = (x0, back[0][1]); back[-1] = (x1, back[-1][1])
    poly = Polygon(front + back[::-1]).buffer(0)
    tol = max(0.75, (x1 - x0) / 120)
    polys = largest(poly.simplify(tol, preserve_topology=True))
    meshes = [extrude_poly(p, 0, H) for p in polys]
    mesh = trimesh.util.concatenate(meshes) if len(meshes) > 1 else meshes[0]

    atlas_views = {main: S}
    E = views.get('east') if main != 'east' else None
    N = views.get('north')
    W = views.get('west')
    E = E if (E is not None and front_band(E, True)[1]) else None
    W = W if (W is not None and front_band(W, True)[1]) else None
    N = N if (N is not None and front_band(N, True)[1]) else None
    for nm, vv in (('east', E), ('north', N), ('west', W)):
        if vv is not None:
            atlas_views[nm] = vv
    at = Atlas(atlas_views)
    V, F, n = unshare(mesh)
    zmin, zmax = V[:, 2].min(), V[:, 2].max()
    xmin, xmax = V[:, 0].min(), V[:, 0].max()
    UV = np.zeros((len(V), 2))

    def side_map(vv, z, y, mirror):
        lx, rx, ty, by = bbox(vv['mask'])
        bandv = front_band(vv)
        t = (z - zmin) / max(zmax - zmin, 1e-6)
        u = (rx - t * (rx - lx)) if mirror else (lx + t * (rx - lx))
        v = by - (y / max(H, 1e-6)) * bandv
        return u, v

    cache = {}
    for i, tri in enumerate(F):
        P, nn = V[tri], n[i]
        if nn[1] < -0.5:
            UV[tri] = at.swatch(3); continue
        if nn[0] < -0.5 and E is not None:
            u, v = side_map(E, P[:, 2], P[:, 1], False); UV[tri] = at.uv('east', u, v); continue
        if nn[0] > 0.5 and (W is not None or E is not None):
            if W is not None:
                u, v = side_map(W, P[:, 2], P[:, 1], True); UV[tri] = at.uv('west', u, v)
            else:
                u, v = side_map(E, P[:, 2], P[:, 1], True); UV[tri] = at.uv('east', u, v)
                # mirrored strip of the east view, as RimWorld draws west
            continue
        if nn[2] < -0.5 and nn[1] < 0.5:
            if N is not None:
                lx, rx, ty, by = bbox(N['mask'])
                bandn = front_band(N)
                t = (P[:, 0] - xmin) / max(xmax - xmin, 1e-6)
                u = rx - t * (rx - lx)
                v = by - (P[:, 1] / max(H, 1e-6)) * bandn
                UV[tri] = at.uv('north', u, v)
            else:
                UV[tri] = at.uv(main, P[:, 0], V0 - P[:, 1] * B)
            continue
        UV[tri] = at.uv(main, P[:, 0], V0 + P[:, 2] * A - P[:, 1] * B)
    hulls = [hull_of(m, max(1.0, S['k'] * 1.0)) for m in meshes] if S['k'] else []
    ppu = 128.0 if max(S['w'], S['h']) >= 128 else 64.0
    cxz = ((xmin + xmax) / 2, (zmin + zmax) / 2)
    extras.update(kind='oblique', views=list(atlas_views), pitch_deg=round(math.degrees(math.asin(A)), 2), px_per_unit=ppu)
    finish(V, F, UV, at.img, hulls, ppu, cxz, out_path, extras)
    return dict(V=V, F=F, UV=UV, img=at.img, main=main, V0=V0, ppu=ppu, cxz=cxz)


# ---------------------------------------------------------------- item (top-down slab)
def build_slab(views, out_path, extras):
    S = next(iter(views.values()))
    mask = S['mask'].astype(np.uint8)
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    eps = max(0.8, max(S['w'], S['h']) / 80)
    polys = []
    for c in cnts:
        if cv2.contourArea(c) < 4:
            continue
        ap = cv2.approxPolyDP(c, eps, True)[:, 0, :].astype(float)
        if len(ap) < 3:
            continue
        polys += largest(Polygon(ap).buffer(0))
    if not polys:
        raise ValueError('empty')
    x0, x1, y0, y1 = bbox(S['mask'])
    T = max(2.0, 0.06 * max(x1 - x0, y1 - y0))
    meshes = [extrude_poly(Polygon([(x, z) for x, z in p.exterior.coords]), 0, T) for p in polys]
    mesh = trimesh.util.concatenate(meshes)
    at = Atlas({'top': S})
    V, F, n = unshare(mesh)
    UV = np.zeros((len(V), 2))
    for i, tri in enumerate(F):
        if n[i][1] < -0.5:
            UV[tri] = at.swatch(3)
        else:
            UV[tri] = at.uv('top', V[tri][:, 0], V[tri][:, 2])
    hulls = [hull_of(m, 1.0) for m in meshes] if S['k'] else []
    ppu = 128.0 if max(S['w'], S['h']) >= 128 else 64.0
    cxz = ((V[:, 0].min() + V[:, 0].max()) / 2, (V[:, 2].min() + V[:, 2].max()) / 2)
    extras.update(kind='slab', views=['top'], px_per_unit=ppu)
    finish(V, F, UV, at.img, hulls, ppu, cxz, out_path, extras)


# ---------------------------------------------------------------- plant (lathe)
def build_lathe(views, out_path, extras, seg=8, levels=14):
    S = next(iter(views.values()))
    mask = S['mask']
    x0, x1, y0, y1 = bbox(mask)
    rows = np.linspace(y0, y1 - 1, levels).round().astype(int)
    rings = []
    for r in rows:
        xs = np.nonzero(mask[r])[0]
        if not len(xs):
            continue
        rings.append((r, (xs.min() + xs.max() + 1) / 2, max(0.5, (xs.max() + 1 - xs.min()) / 2)))
    Vb = float(y1)
    verts, faces, uvsrc = [], [], []
    ang = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    for (r, c, rad) in rings:
        for a in ang:
            verts.append((c + rad * math.cos(a), Vb - r, rad * math.sin(a)))
    verts = np.array(verts)
    for i in range(len(rings) - 1):
        for j in range(seg):
            a, b = i * seg + j, i * seg + (j + 1) % seg
            c, d = a + seg, b + seg
            faces += [(a, c, b), (b, c, d)]
    top_c = len(verts); verts = np.vstack([verts, [rings[0][1], Vb - rings[0][0], 0]])
    bot_c = len(verts); verts = np.vstack([verts, [rings[-1][1], Vb - rings[-1][0], 0]])
    last = (len(rings) - 1) * seg
    for j in range(seg):
        faces.append((top_c, j, (j + 1) % seg))
        faces.append((bot_c, last + (j + 1) % seg, last + j))
    mesh = trimesh.Trimesh(verts, faces, process=False)
    mesh.fix_normals()
    at = Atlas({'front': S})
    V, F, n = unshare(mesh)
    UV = at.uv('front', V[:, 0], Vb - V[:, 1])
    hulls = [hull_of(mesh, 1.0)] if S['k'] else []
    ppu = 128.0 if max(S['w'], S['h']) >= 128 else 64.0
    cx = rings[-1][1]
    extras.update(kind='lathe', views=['front'], px_per_unit=ppu)
    finish(V, F, UV, at.img, hulls, ppu, (cx, 0.0), out_path, extras)


# ---------------------------------------------------------------- grouping
SKIP = re.compile(r'(Snowy|_m|_eastm|_southm|_northm|_westm|MenuIcon|Glow|Atlas)$', re.I)


def groups(repo):
    man = json.load(open(os.path.join(repo, 'MANIFEST.json')))
    out = {}
    for defname, info in man.items():
        for t in info['textures']:
            stem = t[:-4]
            if SKIP.search(stem) or 'Glow' in stem or 'Snowy' in stem:
                continue
            m = re.match(r'(.*)_(south|east|north|west)$', stem)
            key, d = (m.group(1), m.group(2)) if m else (stem, None)
            g = out.setdefault(key, dict(def_=defname, label=info.get('label'), cat=info['category'],
                                         dlc=info.get('DLC'), views={}))
            g['views'][d or 'single'] = t
    return out


def convert(repo, key, g, out_path):
    views = {d: load_view(os.path.join(repo, f)) for d, f in g['views'].items()}
    extras = dict(defName=g['def_'], label=g['label'], category=g['cat'], dlc=g['dlc'],
                  sources=list(g['views'].values()))
    if g['cat'] == 'Item':
        main = 'south' if 'south' in views else ('single' if 'single' in views else next(iter(views)))
        return build_slab({'top': views[main]}, out_path, extras)
    directional = any(d in DIRS for d in views)
    if directional:
        views = {d: v for d, v in views.items() if d in DIRS}
        return build_oblique(views, out_path, extras)
    if g['cat'] == 'Plant':
        return build_lathe(views, out_path, extras)
    if g['cat'] == 'Item':
        return build_slab(views, out_path, extras)
    return build_oblique({'south': views['single']}, out_path, extras)

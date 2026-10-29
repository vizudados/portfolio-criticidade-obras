#!/usr/bin/env python
"""PNG de traço (preto sobre branco) -> SVG de traços vetoriais (stroke), prontos para animar.

Uso (sempre com python -I, caminhos como argumento):
    python -I vetorizar_traco.py ENTRADA.png SAIDA.svg [--comparacao COMP.png] [--calibrar]

Pipeline:
  1. amplia 2x (bicúbica) e binariza com limiar adaptativo + limiar absoluto; tira pontinhos e furinhos;
  2. esqueletiza (skimage) e remove cantos em L que criam junções falsas;
  3. percorre o grafo do esqueleto (percurso próprio; o skan depende do numba, bloqueado nesta máquina),
     quebra nas junções, poda espinhos curtos e reemenda na junção os ramos que seguem em linha reta;
  4. suaviza (gaussiana com reflexão no ponto final), simplifica (RDP) e escreve Catmull-Rom centrípeta
     como Bézier cúbica;
  5. descarta fragmentos curtos;
  6. espessura de cada traço = mediana da transformada de distância ao longo do esqueleto, com um fator
     global calibrado para a tinta do vetor igualar a tinta do original;
  7. SVG com fill=none, stroke=#0B0B0C, pontas e juntas redondas, viewBox do original, pathLength=1.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage as ndi
from skimage.morphology import skeletonize

OFFS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
COR = "#0B0B0C"


# ------------------------------------------------------------------ leitura e binarização
def ler_cinza(caminho: Path) -> np.ndarray:
    dados = np.fromfile(str(caminho), dtype=np.uint8)
    img = cv2.imdecode(dados, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise SystemExit(f"não consegui ler {caminho}")
    return img


def remover_componentes(mask: np.ndarray, area_max: int, conectividade: int) -> np.ndarray:
    """Remove componentes com área <= area_max."""
    n, lab, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), connectivity=conectividade)
    pequenos = np.zeros(n, bool)
    pequenos[1:] = stats[1:, cv2.CC_STAT_AREA] <= area_max
    return mask & ~pequenos[lab]


def binarizar(gray_up: np.ndarray, p) -> np.ndarray:
    adapt = cv2.adaptiveThreshold(gray_up, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY_INV, p.bloco, p.c) > 0
    ink = (adapt & (gray_up < p.claro)) | (gray_up < p.escuro)
    s2 = p.escala * p.escala
    if p.mediana:
        ink = cv2.medianBlur(ink.astype(np.uint8) * 255, 3) > 0       # serrilhado -> menos espinhos
    ink = remover_componentes(ink, int(p.area_min * s2), 8)             # pontinhos isolados
    furos = remover_componentes(~ink, int(p.furo_max * s2), 4)          # furinhos (gera laço falso)
    ink = ~furos
    return ink


# ------------------------------------------------------------------ esqueleto -> grafo
def limpar_cantos(sk: np.ndarray) -> np.ndarray:
    """Remove pixel de canto em L (2 vizinhos ortogonais que se tocam na diagonal)."""
    sk = sk.copy()
    H, W = sk.shape
    nb = ndi.convolve(sk.astype(np.uint8), np.ones((3, 3), np.uint8), mode="constant") - sk
    ys, xs = np.nonzero(sk & (nb == 2))
    for y, x in zip(ys.tolist(), xs.tolist()):
        if not sk[y, x]:
            continue
        viz = [(y + dy, x + dx) for dy, dx in OFFS
               if 0 <= y + dy < H and 0 <= x + dx < W and sk[y + dy, x + dx]]
        if len(viz) != 2:
            continue
        (y1, x1), (y2, x2) = viz
        orto1 = (y1 == y) or (x1 == x)
        orto2 = (y2 == y) or (x2 == x)
        if orto1 and orto2 and abs(y1 - y2) == 1 and abs(x1 - x2) == 1:
            sk[y, x] = False
    return sk


def tracar(sk: np.ndarray):
    """Percorre o esqueleto. Devolve (arestas, n_junc, shape_pad).
    aresta = [no_a, no_b, lista_de_indices_planos]; no = id de cluster de junção (< n_junc) ou de ponta."""
    P = np.pad(sk, 1).astype(np.uint8)
    Wp = P.shape[1]
    flat = P.ravel()
    offs = [dy * Wp + dx for dy, dx in OFFS]
    idx = np.flatnonzero(flat)
    nb = np.zeros(flat.size, np.int16)
    for o in offs:
        nb[idx] += flat[idx + o]
    nb = nb * flat
    junc = (nb >= 3) & (flat > 0)
    lab, n_junc = ndi.label(junc.reshape(P.shape), structure=np.ones((3, 3)))
    node = np.full(flat.size, -1, np.int64)
    labf = lab.ravel()
    node[junc] = labf[junc] - 1
    pontas = np.flatnonzero((nb == 1) & (flat > 0))
    node[pontas] = n_junc + np.arange(len(pontas))

    fl = flat.tolist()
    nl = node.tolist()
    visit = bytearray(flat.size)
    arestas = []
    vistos = set()
    nos_pix = np.flatnonzero(node >= 0).tolist()
    for p in nos_pix:
        for o in offs:
            q = p + o
            if not fl[q]:
                continue
            if nl[q] >= 0:
                if nl[q] == nl[p]:
                    continue
                k = (p, q) if p < q else (q, p)
                if k in vistos:
                    continue
                vistos.add(k)
                arestas.append([nl[p], nl[q], [p, q]])
                continue
            if visit[q]:
                continue
            caminho = [p, q]
            visit[q] = 1
            ant, cur = p, q
            fim = -1
            while True:
                nxt = -1
                for o2 in offs:
                    r = cur + o2
                    if r != ant and fl[r]:
                        nxt = r
                        break
                if nxt < 0:          # não deveria acontecer
                    break
                caminho.append(nxt)
                if nl[nxt] >= 0:
                    fim = nl[nxt]
                    break
                if visit[nxt]:
                    break
                visit[nxt] = 1
                ant, cur = cur, nxt
            if fim >= 0:
                arestas.append([nl[p], fim, caminho])
    # ciclos puros (sem nó)
    resto = np.flatnonzero((nb == 2) & (node < 0)).tolist()
    for s in resto:
        if visit[s]:
            continue
        visit[s] = 1
        viz = [s + o for o in offs if fl[s + o]]
        ant, cur = viz[0], s
        caminho = [s]
        while True:
            nxt = -1
            for o2 in offs:
                r = cur + o2
                if r != ant and fl[r]:
                    nxt = r
                    break
            if nxt < 0:
                break
            if nxt == s:
                caminho.append(s)
                break
            if visit[nxt]:
                break
            visit[nxt] = 1
            caminho.append(nxt)
            ant, cur = cur, nxt
        if len(caminho) > 2:
            arestas.append([-1, -1, caminho])
    return arestas, n_junc, P.shape


def podar(sk: np.ndarray, dt: np.ndarray, p) -> np.ndarray:
    """Tira espinhos (ponta -> junção) curtos demais para a espessura local. Repete 3x."""
    for _ in range(3):
        sk = limpar_cantos(sk)
        arestas, n_junc, shp = tracar(sk)
        Wp = shp[1]
        removeu = 0
        for a, b, cam in arestas:
            if a < 0:
                continue
            ponta_a, ponta_b = a >= n_junc, b >= n_junc
            if ponta_a == ponta_b:
                continue
            L = len(cam) - 1
            pj = cam[0] if not ponta_a else cam[-1]
            yj, xj = pj // Wp - 1, pj % Wp - 1
            lim = p.espinho_k * dt[yj, xj] + p.espinho_c * p.escala
            if L < lim:
                miolo = cam[1:] if not ponta_a else cam[:-1]
                for q in miolo:
                    sk[q // Wp - 1, q % Wp - 1] = False
                removeu += 1
        if removeu == 0:
            break
        sk = skeletonize(sk)
    return limpar_cantos(sk)


# ------------------------------------------------------------------ emendas na junção
def direcao(pts: np.ndarray, k: int) -> np.ndarray:
    j = min(k, len(pts) - 1)
    v = pts[j] - pts[0]
    n = math.hypot(v[0], v[1])
    return v / n if n > 1e-9 else np.zeros(2)


def montar_cadeias(arestas, n_junc, shp, dt, p):
    Wp = shp[1]
    E = []
    for a, b, cam in arestas:
        arr = np.array(cam, np.int64)
        pts = np.stack([arr // Wp - 1, arr % Wp - 1], 1).astype(float)  # (y, x)
        L = len(cam) - 1
        if a >= 0 and a == b and L < p.laco_min * p.escala:
            continue  # laço minúsculo na junção
        w = float(np.median(dt[pts[:, 0].astype(int), pts[:, 1].astype(int)]))
        E.append({"a": a, "b": b, "pts": pts, "w": w, "L": L})
    # pontas de aresta por nó de junção
    por_no = {}
    for i, e in enumerate(E):
        if e["a"] < 0:
            continue
        if e["a"] < n_junc:
            por_no.setdefault(e["a"], []).append((i, 0))
        if e["b"] < n_junc:
            por_no.setdefault(e["b"], []).append((i, 1))
    k = int(p.tangente * p.escala)
    link = {}
    for no, ends in por_no.items():
        if len(ends) < 2:
            continue
        dirs = []
        for i, lado in ends:
            pts = E[i]["pts"] if lado == 0 else E[i]["pts"][::-1]
            dirs.append(direcao(pts, k))
        lim = p.desvio_max if len(ends) > 2 else 170.0
        cand = []
        for x in range(len(ends)):
            for y in range(x + 1, len(ends)):
                if ends[x][0] == ends[y][0]:
                    continue
                c = float(np.dot(dirs[x], -dirs[y]))
                desvio = math.degrees(math.acos(max(-1.0, min(1.0, c))))
                wa, wb = E[ends[x][0]]["w"], E[ends[y][0]]["w"]
                if max(wa, wb) / max(min(wa, wb), 0.5) > p.razao_w and len(ends) > 2:
                    continue
                if desvio <= lim:
                    cand.append((desvio, x, y))
        cand.sort()
        usado = set()
        for _, x, y in cand:
            if x in usado or y in usado:
                continue
            usado.add(x)
            usado.add(y)
            link[ends[x]] = ends[y]
            link[ends[y]] = ends[x]
    # percorre os elos
    feito = [False] * len(E)
    cadeias = []

    def andar(i0, lado0):
        seq = []
        i, lado = i0, lado0
        while True:
            feito[i] = True
            pts = E[i]["pts"] if lado == 0 else E[i]["pts"][::-1]
            seq.append((pts, E[i]["w"], E[i]["L"]))
            saida = (i, 1 - lado)
            if saida not in link:
                return seq, False
            j, lj = link[saida]
            if feito[j]:
                return seq, (j == i0)
            i, lado = j, lj

    for i, e in enumerate(E):
        if feito[i]:
            continue
        for lado in (0, 1):
            if (i, lado) not in link:
                seq, fech = andar(i, lado)
                cadeias.append((seq, fech))
                break
    for i, e in enumerate(E):
        if not feito[i]:
            seq, fech = andar(i, 0)
            cadeias.append((seq, True))
    saida = []
    for seq, fech in cadeias:
        pts = np.concatenate([s[0] if n == 0 else s[0][1:] for n, s in enumerate(seq)])
        w = float(np.median(dt[pts[:, 0].astype(int), pts[:, 1].astype(int)]))  # mediana ao longo do esqueleto
        fechado = fech or (len(pts) > 3 and np.hypot(*(pts[0] - pts[-1])) < 1.5)
        saida.append({"pts": pts, "w": w, "fechado": fechado})
    return saida


# ------------------------------------------------------------------ suavizar, simplificar, Bézier
def suavizar(pts: np.ndarray, sigma: float, fechado: bool) -> np.ndarray:
    n = len(pts)
    if n < 4 or sigma <= 0:
        return pts.copy()
    if fechado:
        return ndi.gaussian_filter1d(pts, sigma, axis=0, mode="wrap")
    pad = min(int(3 * sigma) + 1, n - 1)
    ini = 2 * pts[0] - pts[1:pad + 1][::-1]
    fim = 2 * pts[-1] - pts[-pad - 1:-1][::-1]
    ext = np.concatenate([ini, pts, fim])
    sm = ndi.gaussian_filter1d(ext, sigma, axis=0, mode="nearest")
    return sm[pad:pad + n]


def rdp(pts: np.ndarray, eps: float, fechado: bool) -> np.ndarray:
    c = pts[:, ::-1].astype(np.float32).reshape(-1, 1, 2)   # (x, y)
    s = cv2.approxPolyDP(c, eps, False).reshape(-1, 2).astype(float)
    if len(s) < 2:
        s = np.array([pts[0, ::-1], pts[-1, ::-1]], float)
    return s  # (x, y)


def catmull_bezier(P: np.ndarray, fechado: bool, alpha: float = 0.5):
    """Catmull-Rom centrípeta -> lista de (c1, c2, p2) para cada segmento."""
    n = len(P)
    segs = []
    for i in range(n - 1):
        p1, p2 = P[i], P[i + 1]
        if i > 0:
            p0 = P[i - 1]
        else:
            p0 = P[-2] if fechado and n > 2 else p1
        if i + 2 < n:
            p3 = P[i + 2]
        else:
            p3 = P[1] if fechado and n > 2 else p2
        d1 = np.linalg.norm(p1 - p0)
        d2 = np.linalg.norm(p2 - p1)
        d3 = np.linalg.norm(p3 - p2)
        d1a, d2a, d3a = d1 ** alpha, d2 ** alpha, d3 ** alpha
        d12a, d22a, d32a = d1a * d1a, d2a * d2a, d3a * d3a
        if d1a > 1e-6:
            a = 2 * d12a + 3 * d1a * d2a + d22a
            b = 3 * d1a * (d1a + d2a)
            c1 = (p1 * a - p0 * d22a + p2 * d12a) / b
        else:
            c1 = p1 + (p2 - p1) / 3
        if d3a > 1e-6:
            m = 2 * d32a + 3 * d3a * d2a + d22a
            nn = 3 * d3a * (d3a + d2a)
            c2 = (p2 * m + p1 * d32a - p3 * d22a) / nn
        else:
            c2 = p2 - (p2 - p1) / 3
        segs.append((c1, c2, p2))
    return segs


def fmt(v: float) -> str:
    s = f"{v:.1f}"
    if s.endswith(".0"):
        s = s[:-2]
    if s == "-0":
        s = "0"
    if s.startswith("0."):
        s = s[1:]
    elif s.startswith("-0."):
        s = "-" + s[2:]
    return s


def juntar(nums) -> str:
    out = []
    for i, n in enumerate(nums):
        s = fmt(n)
        if i > 0 and not s.startswith("-"):
            out.append(" ")
        out.append(s)
    return "".join(out)


def path_d(P: np.ndarray, fechado: bool) -> str:
    """P em coordenadas do original (x, y). Comandos relativos, 1 casa, sem deriva de arredondamento."""
    segs = catmull_bezier(P, fechado)
    r = lambda v: np.round(v * 10) / 10
    cur = r(P[0])
    d = ["M" + juntar([cur[0], cur[1]])]
    partes = []
    for c1, c2, p2 in segs:
        c1, c2, p2 = r(c1), r(c2), r(p2)
        partes.extend([c1[0] - cur[0], c1[1] - cur[1], c2[0] - cur[0], c2[1] - cur[1],
                       p2[0] - cur[0], p2[1] - cur[1]])
        cur = p2
    d.append("c" + juntar(partes))
    return "".join(d)


# ------------------------------------------------------------------ vetorizar
def regioes_cheias(ink: np.ndarray, gray_up: np.ndarray, p) -> np.ndarray:
    """Manchas = áreas de tom escuro (hachura densa, cabelo, miolo de cano): o escuro médio na vizinhança
    (gaussiana de mancha_sigma px) passa de mancha_tom, OU cabe um disco de raio mancha_r na tinta.
    Depois abre com disco de mancha_r (tira franjas e cruzamentos) e descarta as pequenas."""
    S = p.escala
    escuro = (255.0 - gray_up.astype(np.float32)) / 255.0
    tom = cv2.GaussianBlur(escuro, (0, 0), p.mancha_sigma * S)
    r = max(1, int(round(p.mancha_r * S)))
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
    fech = cv2.morphologyEx(ink.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)) > 0
    cand = (tom > p.mancha_tom) & fech
    R = cv2.morphologyEx(cand.astype(np.uint8), cv2.MORPH_OPEN, k) > 0
    return remover_componentes(R, int(p.mancha_area * S * S), 8)


def hachurar(R: np.ndarray, p, rng: random.Random, gray_up: np.ndarray):
    """Preenche cada mancha com hachura em zigue-zague, dentro da mancha. O passo segue o tom da mancha no
    original (mancha cinza-escura = hachura aberta), para não virar borrão chapado."""
    S = p.escala
    wh = p.hachura_w * S
    er = max(0, int(round(wh / 2 - 0.5)))
    if er:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * er + 1, 2 * er + 1))
        Ri = cv2.erode(R.astype(np.uint8), k) > 0
    else:
        Ri = R
    n, lab, stats, _ = cv2.connectedComponentsWithStats(R.astype(np.uint8), connectivity=8)
    tracos = []
    for c in range(1, n):
        x0, y0, w, h = stats[c, :4]
        comp_c = lab[y0:y0 + h, x0:x0 + w] == c
        sub = Ri[y0:y0 + h, x0:x0 + w] & comp_c
        if not sub.any():
            sub = comp_c
        tom = float(np.mean(255.0 - gray_up[y0:y0 + h, x0:x0 + w][comp_c])) / 255.0
        passo = wh / max(tom * p.hachura_tom, 1e-3)
        passo = min(max(passo, wh * p.hachura_passo), wh * 3.5)
        ang = math.radians(p.hachura_ang + rng.uniform(-p.hachura_var, p.hachura_var))
        ca, sa = math.cos(ang), math.sin(ang)
        ys, xs = np.nonzero(sub)
        u = xs * ca + ys * sa
        v = -xs * sa + ys * ca
        us = np.arange(u.min() - 1, u.max() + 1.5, 0.5)
        segs_por_linha = []
        for j in range(int(math.floor(v.min() / passo)), int(math.ceil(v.max() / passo)) + 1):
            vj = j * passo
            xx = us * ca - vj * sa
            yy = us * sa + vj * ca
            xi = np.round(xx).astype(int)
            yi = np.round(yy).astype(int)
            ok = (xi >= 0) & (xi < w) & (yi >= 0) & (yi < h)
            dentro = np.zeros(len(us), bool)
            dentro[ok] = sub[yi[ok], xi[ok]]
            if not dentro.any():
                continue
            d = np.diff(np.concatenate([[0], dentro.astype(np.int8), [0]]))
            a_idx = np.flatnonzero(d == 1)
            b_idx = np.flatnonzero(d == -1) - 1
            segs = [[np.array([xx[a_] + x0, yy[a_] + y0]), np.array([xx[b_] + x0, yy[b_] + y0])]
                    for a_, b_ in zip(a_idx, b_idx)]
            segs_por_linha.append(segs)
        # zigue-zague: liga o fim de um segmento ao começo mais próximo da linha seguinte
        abertos = []
        for segs in segs_por_linha:
            novos = []
            livres = list(range(len(segs)))
            for pl in abertos:
                fimp = pl[-1]
                melhor, dist = None, 1e9
                for i in livres:
                    for lado in (0, 1):
                        dd = float(np.linalg.norm(segs[i][lado] - fimp))
                        if dd < dist:
                            melhor, dist = (i, lado), dd
                if melhor is not None and dist <= p.hachura_liga * passo:
                    i, lado = melhor
                    livres.remove(i)
                    a_, b_ = (segs[i][0], segs[i][1]) if lado == 0 else (segs[i][1], segs[i][0])
                    pl.extend([a_, b_])
                    novos.append(pl)
                else:
                    tracos.append(pl)
            for i in livres:
                novos.append([segs[i][0], segs[i][1]])
            abertos = novos
        tracos.extend(abertos)
    out = []
    for pl in tracos:
        P = np.array(pl) / S
        out.append({"P": P, "fechado": False, "w_fixo": p.hachura_w, "reta": True})
    return out


def largura_por_tinta(lista_pts, esc: np.ndarray, p) -> list:
    """Largura de cada traço = tinta integrada no perfil perpendicular (do miolo até o vale ou o papel),
    dividida pela tinta do traço cheio. Mediana ao longo do traço. Px do original."""
    S = p.escala
    R = p.perfil_r * S
    passo = 0.5
    offs = np.arange(-R, R + 1e-6, passo)
    c = len(offs) // 2
    Ys, Xs, NY, NX, dono = [], [], [], [], []
    for i, pts in enumerate(lista_pts):
        n = len(pts)
        if n < 2:
            continue
        tg = np.gradient(pts, axis=0)
        nrm = np.hypot(tg[:, 0], tg[:, 1])
        nrm[nrm < 1e-9] = 1
        tg = tg / nrm[:, None]
        k = max(1, n // 60)
        sel = np.arange(0, n, k) if n > 4 else np.arange(n)
        sel = sel[(sel >= min(2, n - 1)) & (sel <= max(n - 3, 0))] if n > 6 else sel
        Ys.append(pts[sel, 0]); Xs.append(pts[sel, 1])
        NY.append(tg[sel, 1]); NX.append(-tg[sel, 0])
        dono.append(np.full(len(sel), i))
    Y = np.concatenate(Ys)[:, None] + np.concatenate(NY)[:, None] * offs[None, :]
    X = np.concatenate(Xs)[:, None] + np.concatenate(NX)[:, None] * offs[None, :]
    dono = np.concatenate(dono)
    P = ndi.map_coordinates(esc, [Y.ravel(), X.ravel()], order=1, mode="constant", cval=0.0).reshape(Y.shape)
    jan = int(round(1.5 / passo))
    k0 = c - jan + np.argmax(P[:, c - jan:c + jan + 1], axis=1)
    rows = np.arange(len(P))[:, None]
    tot = P[np.arange(len(P)), k0].copy()
    for sentido in (1, -1):
        ks = k0[:, None] + sentido * np.arange(1, len(offs))[None, :]
        dentro = (ks >= 0) & (ks < len(offs))
        ksc = np.clip(ks, 0, len(offs) - 1)
        Pk = P[rows, ksc]
        ant = np.concatenate([P[np.arange(len(P)), k0][:, None], Pk[:, :-1]], 1)
        ok = dentro & (Pk <= ant + p.perfil_tol) & (Pk > p.perfil_piso)
        ok = np.cumprod(ok, axis=1).astype(bool)
        tot += np.where(ok, Pk, 0).sum(1)
    w = tot * passo / S / p.tinta_traco
    out = [None] * len(lista_pts)
    ordem = np.argsort(dono, kind="stable")
    dono_o, w_o = dono[ordem], w[ordem]
    cortes = np.flatnonzero(np.diff(dono_o)) + 1
    for grupo_d, grupo_w in zip(np.split(dono_o, cortes), np.split(w_o, cortes)):
        if len(grupo_d):
            out[int(grupo_d[0])] = float(np.median(grupo_w))
    return out


def van_der_corput(n: np.ndarray, base: int = 2) -> np.ndarray:
    """Sequência de baixa discrepância em [0, 1): limiar de pontilhado de cada linha da hachura."""
    n = np.asarray(n, np.int64).copy()
    out = np.zeros(n.shape, float)
    den = 1.0
    while np.any(n > 0):
        den *= base
        out += (n % base) / den
        n //= base
    return out


def hachura_tom(esc: np.ndarray, fundo: np.ndarray, p, rng: random.Random):
    """Sombreado do original (o 'fundo' da abertura morfológica: textura fina, hachura que a resolução
    não separa) vira hachura de gravura: linhas paralelas na direção dominante da textura local, com
    densidade igual ao tom (pontilhado ordenado entre as linhas). Coordenadas de saída no original."""
    S = p.escala
    fundo = np.clip(fundo.astype(np.float32) - p.tom_piso, 0, 1)   # tira o cinza claro do papel
    sh = cv2.GaussianBlur(fundo, (0, 0), p.tom_sigma * S)
    regiao = sh > p.tom_min
    n, lab, stats, _ = cv2.connectedComponentsWithStats(regiao.astype(np.uint8), connectivity=8)
    # tensor de estrutura (orientação da textura)
    g = cv2.GaussianBlur(esc.astype(np.float32), (0, 0), 0.8 * S)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
    jxx, jyy, jxy = gx * gx, gy * gy, gx * gy
    wh = p.tom_w * S
    passo = wh * p.tom_passo
    tracos = []
    for c in range(1, n):
        x0, y0, w, h = stats[c, :4]
        if stats[c, cv2.CC_STAT_AREA] < p.tom_area * S * S:
            continue
        m = lab[y0:y0 + h, x0:x0 + w] == c
        pw = fundo[y0:y0 + h, x0:x0 + w][m]
        a = float((jxx[y0:y0 + h, x0:x0 + w][m] * pw).sum())
        b = float((jyy[y0:y0 + h, x0:x0 + w][m] * pw).sum())
        cxy = float((jxy[y0:y0 + h, x0:x0 + w][m] * pw).sum())
        coer = math.hypot(a - b, 2 * cxy) / max(a + b, 1e-9)
        if coer > 0.15:
            ang = 0.5 * math.atan2(2 * cxy, a - b) + math.pi / 2     # linha = perpendicular ao gradiente
        else:
            ang = math.radians(p.hachura_ang + rng.uniform(-p.hachura_var, p.hachura_var))
        tom_reg = sh[y0:y0 + h, x0:x0 + w]
        cob = p.tinta_traco * wh / passo            # tinta de uma camada cheia de hachura
        ys, xs = np.nonzero(m)
        semente = rng.randrange(1 << 12)
        for camada in range(p.tom_camadas):
            # camada 0 leva o tom até a cobertura de uma camada; o resto vai para a camada cruzada
            resto = np.clip(tom_reg * p.tom_ganho - camada * cob, 0, cob) / cob
            if not np.any(resto[m] > 0.02):
                break
            angc = ang + camada * math.pi / 2
            ca, sa = math.cos(angc), math.sin(angc)
            u = xs * ca + ys * sa
            v = -xs * sa + ys * ca
            js = np.arange(int(math.floor(v.min() / passo)), int(math.ceil(v.max() / passo)) + 1)
            us = np.arange(u.min() - 1, u.max() + 1.5, 0.5)
            vv = js[:, None] * passo
            xx = us[None, :] * ca - vv * sa
            yy = us[None, :] * sa + vv * ca
            xi = np.round(xx).astype(int)
            yi = np.round(yy).astype(int)
            ok = (xi >= 0) & (xi < w) & (yi >= 0) & (yi < h)
            xi_c, yi_c = np.clip(xi, 0, w - 1), np.clip(yi, 0, h - 1)
            dentro = ok & m[yi_c, xi_c]
            limiar = van_der_corput(js + semente + 977 * camada)[:, None]
            manter = dentro & (resto[yi_c, xi_c] >= limiar)
            d = np.diff(np.concatenate([np.zeros((len(js), 1), np.int8), manter.astype(np.int8),
                                        np.zeros((len(js), 1), np.int8)], 1), axis=1)
            ri, ci = np.nonzero(d == 1)
            rf, cf = np.nonzero(d == -1)
            for r_, a_, b_ in zip(ri, ci, cf - 1):
                if (b_ - a_) * 0.5 < p.tom_comp_min * S:
                    continue
                P = np.array([[xx[r_, a_] + x0, yy[r_, a_] + y0], [xx[r_, b_] + x0, yy[r_, b_] + y0]]) / S
                tracos.append({"P": P, "fechado": False, "w_fixo": p.tom_w, "reta": True})
    return tracos


def vetorizar(caminho: Path, p):
    t0 = time.time()
    gray = ler_cinza(caminho)
    H, W = gray.shape
    S = p.escala
    gray_up = cv2.resize(gray, (W * S, H * S), interpolation=cv2.INTER_CUBIC)
    ink = binarizar(gray_up, p)          # máscara por limiar: tom, manchas e escuro da faixa
    if p.modo == "crista":
        # linha = crista escura (Hessiana multiescala, Sato): separa traços paralelos que o limiar funde
        from skimage.filters import sato
        sig = [float(x) * S for x in p.sigmas.split(",")]
        rr = sato(gray_up.astype(np.float32) / 255.0, sigmas=sig, black_ridges=True, mode="reflect")
        lin = (rr > p.crista) & (gray_up < p.claro)
        lin = cv2.medianBlur(lin.astype(np.uint8) * 255, 3) > 0
        lin = remover_componentes(lin, int(p.area_min * S * S), 8)
        lin = ~remover_componentes(~lin, int(p.furo_max * S * S), 4)
    else:
        lin = ink
    dt = ndi.distance_transform_edt(lin)
    R = regioes_cheias(ink, gray_up, p) if p.mancha_r > 0 else np.zeros_like(ink)
    sk = skeletonize(lin)
    if R.any():
        Rd = cv2.dilate(R.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        sk &= ~Rd
    sk = podar(sk, dt, p)
    arestas, n_junc, shp = tracar(sk)
    cadeias = montar_cadeias(arestas, n_junc, shp, dt, p)
    # escuro médio da tinta na faixa do traço: linha dupla fundida ou traço cinza -> traço mais fino
    esc = (255.0 - gray_up.astype(np.float32)) / 255.0
    inkf = ink.astype(np.float32)
    sg = p.faixa_sigma * S
    media_esc = cv2.GaussianBlur(esc * inkf, (0, 0), sg) / np.maximum(cv2.GaussianBlur(inkf, (0, 0), sg), 1e-3)
    lisos = [suavizar(c["pts"], p.sigma * S, c["fechado"]) for c in cadeias]
    esc_w = contraste(esc, p.fundo_r * S) if p.fundo_r > 0 else esc   # só o contraste de linha
    w_tinta = largura_por_tinta(lisos, esc_w, p) if p.largura == "tinta" else [None] * len(cadeias)
    tracos = []
    for ci, c in enumerate(cadeias):
        pts = c["pts"]
        sm = lisos[ci]
        comp = float(np.sum(np.hypot(*np.diff(sm, axis=0).T))) / S if len(sm) > 1 else 0.0
        w_base = max(2 * c["w"] - 0.5, 1.0) / S          # largura binária estimada, px do original
        if comp < p.comp_min and not (comp >= 1.0 and w_base >= p.ponto_w):
            continue
        if w_tinta[ci] is not None:
            w_base, m = w_tinta[ci], 1.0
            if w_base < p.w_desc:          # risco de textura sem contraste: o tom vai para a hachura
                continue
        else:
            escuro = float(np.median(media_esc[pts[:, 0].astype(int), pts[:, 1].astype(int)]))
            m = min(max(escuro / p.escuro_ref, p.escuro_piso), 1.15) if p.escuro_ref > 0 else 1.0
        simp = rdp(sm, p.rdp * S, c["fechado"]) / S       # (x, y) no original
        if len(simp) < 2:
            continue
        tracos.append({"P": simp, "fechado": c["fechado"], "w_base": w_base * m, "comp": comp})
    n_linhas = len(tracos)
    if R.any():
        tracos.extend(hachurar(R, p, random.Random(11), gray_up))
    if p.tom:
        fundo = esc - esc_w if p.fundo_r > 0 else contraste(esc, 3 * S) * 0
        tracos.extend(hachura_tom(esc, fundo, p, random.Random(13)))
    info = {"W": W, "H": H, "arestas": len(arestas), "cadeias": len(cadeias),
            "tracos": len(tracos), "tracos_linha": n_linhas, "tracos_hachura": len(tracos) - n_linhas,
            "manchas_px": int(R.sum() / (S * S)),
            "seg_vetorizar": round(time.time() - t0, 1),
            "tinta_bin_px": int(ink.sum() / (S * S))}
    return tracos, info, gray


def path_reta(P: np.ndarray) -> str:
    r = lambda v: np.round(v * 10) / 10
    cur = r(P[0])
    d = ["M" + juntar([cur[0], cur[1]])]
    partes = []
    for q in P[1:]:
        q = r(q)
        partes.extend([q[0] - cur[0], q[1] - cur[1]])
        cur = q
    d.append("l" + juntar(partes))
    return "".join(d)


def comprimento(t) -> float:
    """Comprimento real do traço como o navegador mede (Bézier amostrada; reta exata), px."""
    P = t["P"]
    if t.get("reta") or len(P) < 3:
        return float(np.sum(np.hypot(*np.diff(P, axis=0).T)))
    r = lambda v: np.round(v * 10) / 10
    tt = np.linspace(0, 1, 13)[:, None]
    tot, p0 = 0.0, r(P[0])
    for c1, c2, p2 in catmull_bezier(P, t["fechado"]):
        c1, c2, p2 = r(c1), r(c2), r(p2)
        B = ((1 - tt) ** 3) * p0 + 3 * ((1 - tt) ** 2) * tt * c1 + 3 * (1 - tt) * tt * tt * c2 + tt ** 3 * p2
        tot += float(np.sum(np.hypot(*np.diff(B, axis=0).T)))
        p0 = p2
    return tot


def orientar(t: dict) -> dict:
    """Sentido de desenho de baixo para cima: o traço começa na ponta de baixo. Quase horizontal
    (menos de ~20 graus), da esquerda para a direita. Fechado (roda, argola): começa no ponto mais baixo."""
    P = t["P"]
    if len(P) < 2:
        return t
    if t["fechado"] and len(P) > 3:
        i = int(np.argmax(P[:-1, 1]))
        Q = np.concatenate([P[i:-1], P[:i], P[i:i + 1]])
        return {**t, "P": Q}
    dx, dy = P[-1, 0] - P[0, 0], P[-1, 1] - P[0, 1]
    if abs(dy) < 0.34 * math.hypot(dx, dy):
        inverter = dx < 0
    else:
        inverter = P[0, 1] < P[-1, 1]       # y cresce para baixo: começo acima do fim -> inverte
    return {**t, "P": P[::-1].copy()} if inverter else t


def tempos_de_baixo(tracos, Ls, p, rng: random.Random):
    """Atraso e duração de cada traço: uma frente sobe da base do desenho (t = 0) ao topo; cada traço
    começa quando a frente chega à sua ponta mais baixa (com jitter) e dura de dur_min a dur_max conforme
    o comprimento. Tudo termina até p.total. Quantizado em passos para virar classes de CSS."""
    ybaixo = np.array([float(np.max(t["P"][:, 1])) for t in tracos])
    ytopo = np.array([float(np.min(t["P"][:, 1])) for t in tracos])
    y0, y1 = float(np.max(ybaixo)), float(np.min(ytopo))     # base e topo da tinta
    altura = max(y0 - y1, 1.0)
    Lref = p.dur_ref * altura
    out = []
    span = p.total - p.dur_max
    for yb, L in zip(ybaixo, Ls):
        h = (y0 - yb) / altura                                   # 0 = chão, 1 = topo
        u = p.dur_min + (p.dur_max - p.dur_min) * min(1.0, math.sqrt(L / Lref))
        u = min(max(u + rng.uniform(-0.08, 0.08), p.dur_min), p.dur_max)
        d = h ** p.frente_gama * span + rng.uniform(-p.jitter, p.jitter)
        d = min(max(d, 0.0), p.total - u)
        dq = round(d / p.passo_tempo) * p.passo_tempo
        uq = round(u / 0.1) * 0.1
        if dq + uq > p.total + 1e-9:
            dq = math.floor((p.total - uq) / p.passo_tempo + 1e-9) * p.passo_tempo
        out.append((round(dq, 3), round(uq, 2)))
    return out


def escrever_svg(tracos, W, H, fator, p, destino: Path | None = None, semente=7) -> str:
    """Um <path> por grupo (classe de tempo, largura, faixa de comprimento). O navegador recomeça o
    tracejado em cada subcaminho, então com pathLength = soma / maior comprimento do grupo todos os
    subcaminhos crescem juntos e o mais longo leva a duração da classe; os outros, entre 1/agrupar e 1
    dela. Menos elementos animados = animação mais leve.

    ordem "baixo": cada traço se desenha da ponta de baixo para a de cima e começa quando uma frente que
    sobe pela cena chega à sua base (chão primeiro, topo das gruas por último).
    ordem "junto": todos começam juntos (atraso 0–0,4 s, duração 2,4–2,8 s)."""
    rng = random.Random(semente)
    q = max(p.agrupar, 1.0)
    if p.ordem == "baixo":
        tracos = [orientar(t) for t in tracos]
    Ls = [max(comprimento(t), 0.05) for t in tracos]
    if p.ordem == "baixo":
        pares = tempos_de_baixo(tracos, Ls, p, rng)
    else:
        base = classes_tempo()
        pares = [base[rng.randrange(len(base))] for _ in tracos]
    classes = sorted(set(pares))
    indice = {c: i for i, c in enumerate(classes)}
    grupos = {}
    for t, L, par in zip(tracos, Ls, pares):
        w = t["w_fixo"] if "w_fixo" in t else min(max(t["w_base"] * fator, p.w_min), p.w_max)
        wq = round(w * 20) / 20     # passo de .05 px
        k = indice[par]
        faixa = int(math.floor(math.log(L) / math.log(q))) if q > 1 else id(t)
        grupos.setdefault((wq, k, faixa), []).append((t, L))
    linhas = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
              f'fill="none" stroke="{COR}" stroke-linecap="round" stroke-linejoin="round" class="traco" '
              f'data-ordem="{p.ordem}" data-tempos="{";".join(f"{d:g},{u:g}" for d, u in classes)}">']
    por_w = {}
    for (wq, k, faixa), itens in grupos.items():
        por_w.setdefault(wq, []).append((k, itens))
    for wq in sorted(por_w):
        linhas.append(f'<g stroke-width="{f"{wq:.2f}".rstrip("0").rstrip(".")}">')
        blocos = por_w[wq]
        rng.shuffle(blocos)
        for k, itens in blocos:
            d = "".join(path_reta(t["P"]) if t.get("reta") else path_d(t["P"], t["fechado"]) for t, _ in itens)
            soma = sum(L for _, L in itens)
            maior = max(L for _, L in itens) * 1.01           # folga: o mais longo nunca passa de 1
            pl = soma / maior
            pl_txt = "1" if len(itens) == 1 else f"{pl:.4f}".rstrip("0").rstrip(".")
            linhas.append(f'<path class="k{k}" pathLength="{pl_txt}" d="{d}"/>')
        linhas.append("</g>")
    linhas.append("</svg>")
    svg = "\n".join(linhas)
    if destino is not None:
        destino.write_text(svg, encoding="utf-8")
    return svg


def classes_tempo():
    """Pares (atraso, duração) em s: atraso 0–0,4; duração 2,4–2,8; fim <= 3,0."""
    out = []
    for d in (0.0, 0.1, 0.2, 0.3, 0.4):
        for u in (2.4, 2.5, 2.6, 2.7, 2.8):
            if d + u <= 3.0 + 1e-9:
                out.append((d, u))
    return out


# ------------------------------------------------------------------ render e comparação
def renderizar_svg(svg: str, W: int, H: int, pagina) -> np.ndarray:
    pagina.set_viewport_size({"width": W, "height": H})
    pagina.set_content(f'<!doctype html><html><body style="margin:0;background:#fff">{svg}</body></html>')
    png = pagina.screenshot(clip={"x": 0, "y": 0, "width": W, "height": H})
    return cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_GRAYSCALE)


def contraste(esc: np.ndarray, raio_px: float) -> np.ndarray:
    """Escuro acima do fundo local (abertura morfológica com disco de raio_px): tira o tom de
    sombreado/textura e deixa só o que é linha."""
    r = max(1, int(round(raio_px)))
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
    fundo = cv2.morphologyEx(esc.astype(np.float32), cv2.MORPH_OPEN, k)
    return np.clip(esc - fundo, 0, 1)


def tinta_contraste(g: np.ndarray, raio_px: float) -> float:
    c = contraste((255.0 - g.astype(np.float32)) / 255.0, raio_px)
    return float(c[c > 0.04].sum())


def tinta(g: np.ndarray) -> float:
    v = (255.0 - g.astype(float)) / 255.0
    v[g > 245] = 0
    return float(v.sum())


def razao_local(orig: np.ndarray, vec: np.ndarray, raio=3, fundo_r=0.0) -> float:
    """Tinta do vetor / tinta do original, só na vizinhança do que o vetor desenhou (o que se perdeu
    não engrossa o resto). Com fundo_r > 0, compara só o contraste de linha (sem o tom de fundo)."""
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * raio + 1, 2 * raio + 1))
    m = cv2.dilate((vec < 235).astype(np.uint8), k) > 0
    o = orig.copy()
    o[~m] = 255
    if fundo_r > 0:
        return tinta_contraste(vec, fundo_r) / max(tinta_contraste(o, fundo_r), 1)
    return tinta(vec) / max(tinta(o), 1)


def metricas(orig: np.ndarray, vec: np.ndarray, tol=2):
    mo = orig < 190
    mv = vec < 190
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * tol + 1, 2 * tol + 1))
    dv = cv2.dilate(mv.astype(np.uint8), ker) > 0
    do = cv2.dilate(mo.astype(np.uint8), ker) > 0
    falta = mo & ~dv
    sobra = mv & ~do
    return {"tinta_orig_px": int(mo.sum()), "tinta_vet_px": int(mv.sum()),
            "faltando_pct": round(100 * falta.sum() / max(mo.sum(), 1), 2),
            "sobrando_pct": round(100 * sobra.sum() / max(mv.sum(), 1), 2),
            "razao_tinta": round(tinta(vec) / max(tinta(orig), 1), 3)}


def comparacao(orig: np.ndarray, vec: np.ndarray, com_sobreposicao=True, empilhar=False) -> np.ndarray:
    o = (255.0 - orig.astype(float)) / 255.0
    v = (255.0 - vec.astype(float)) / 255.0
    pain = [cv2.cvtColor(orig, cv2.COLOR_GRAY2BGR), cv2.cvtColor(vec, cv2.COLOR_GRAY2BGR)]
    if com_sobreposicao:
        # só original = vermelho, só vetor = azul, os dois = preto
        R = 255 * (1 - v)
        B = 255 * (1 - o)
        G = 255 * (1 - np.maximum(o, v))
        pain.append(np.clip(np.stack([B, G, R], 2), 0, 255).astype(np.uint8))
    H, W = orig.shape
    sep = np.full((8, W, 3), 200, np.uint8) if empilhar else np.full((H, 8, 3), 200, np.uint8)
    out = []
    for i, x in enumerate(pain):
        if i:
            out.append(sep)
        out.append(x)
    img = np.concatenate(out, 0 if empilhar else 1)
    rot = ["original (PNG)", "vetor (stroke)", "sobreposicao: vermelho=so original, azul=so vetor"]
    x0 = y0 = 0
    for i, x in enumerate(pain):
        cv2.putText(img, rot[i], (x0 + 12, y0 + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (40, 40, 200) if i == 2 else (60, 60, 60), 2, cv2.LINE_AA)
        if empilhar:
            y0 += x.shape[0] + 8
        else:
            x0 += x.shape[1] + 8
    return img


def salvar_png(img: np.ndarray, destino: Path):
    ok, buf = cv2.imencode(".png", img)
    if not ok:
        raise SystemExit("falha ao codificar PNG")
    destino.parent.mkdir(parents=True, exist_ok=True)
    buf.tofile(str(destino))


# ------------------------------------------------------------------ CLI
def argumentos(argv=None):
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("entrada", type=Path)
    a.add_argument("saida", type=Path)
    a.add_argument("--comparacao", type=Path)
    a.add_argument("--sem-sobreposicao", action="store_true")
    a.add_argument("--empilhar", action="store_true", help="comparação em coluna (imagens largas)")
    a.add_argument("--recortes", type=Path, help="pasta para recortes ampliados (QA)")
    a.add_argument("--calibrar", action="store_true", help="ajusta o fator de espessura pela tinta (Edge headless)")
    a.add_argument("--fator", type=float, default=1.0, help="fator de espessura inicial")
    a.add_argument("--calibracao", choices=["local", "global"], default="local")
    a.add_argument("--escala", type=int, default=3)
    a.add_argument("--modo", choices=["crista", "limiar"], default="limiar")
    a.add_argument("--sigmas", default="0.6,1.0,1.75", help="escalas do Sato, px do original")
    a.add_argument("--crista", type=float, default=0.05, help="limiar da resposta de crista")
    a.add_argument("--bloco", type=int, default=31)
    a.add_argument("--mediana", type=int, default=0, help="mediana 3x3 na máscara (1/0)")
    a.add_argument("--c", type=float, default=10)
    a.add_argument("--claro", type=int, default=215)
    a.add_argument("--escuro", type=int, default=110)
    a.add_argument("--area-min", type=float, default=2)
    a.add_argument("--furo-max", type=float, default=2)
    a.add_argument("--espinho-k", type=float, default=1.4)
    a.add_argument("--espinho-c", type=float, default=0.6)
    a.add_argument("--laco-min", type=float, default=4)
    a.add_argument("--tangente", type=float, default=5)
    a.add_argument("--desvio-max", type=float, default=35)
    a.add_argument("--razao-w", type=float, default=1.8)
    a.add_argument("--sigma", type=float, default=0.9)
    a.add_argument("--rdp", type=float, default=0.25)
    a.add_argument("--comp-min", type=float, default=2)
    a.add_argument("--ponto-w", type=float, default=2.5)
    a.add_argument("--w-min", type=float, default=0.5)
    a.add_argument("--w-max", type=float, default=4.0)
    a.add_argument("--ordem", choices=["baixo", "junto"], default="baixo",
                   help="baixo = frente que sobe do chão ao topo; junto = todos ao mesmo tempo")
    a.add_argument("--total", type=float, default=3.0, help="tempo total do desenho, s")
    a.add_argument("--dur-min", type=float, default=0.8)
    a.add_argument("--dur-max", type=float, default=1.4)
    a.add_argument("--dur-ref", type=float, default=0.35, help="comprimento (fração da altura) da duração máxima")
    a.add_argument("--jitter", type=float, default=0.12, help="± s no início de cada traço")
    a.add_argument("--frente-gama", type=float, default=1.0, help="<1 a frente sobe mais rápido no começo")
    a.add_argument("--passo-tempo", type=float, default=0.05)
    a.add_argument("--agrupar", type=float, default=1.2,
                   help="razão da faixa de comprimento para juntar traços num só path; 1 = um path por traço")
    a.add_argument("--escuro-ref", type=float, default=0.7, help="escuro medio do traco cheio; 0 desliga")
    a.add_argument("--faixa-sigma", type=float, default=1.0)
    a.add_argument("--largura", choices=["tinta", "dt"], default="tinta",
                   help="tinta = integral do perfil perpendicular; dt = transformada de distância")
    a.add_argument("--perfil-r", type=float, default=3.0)
    a.add_argument("--fundo-r", type=float, default=3.0,
                   help="raio (px) do fundo local tirado antes de medir a tinta do traço; 0 desliga")
    a.add_argument("--perfil-tol", type=float, default=0.03)
    a.add_argument("--perfil-piso", type=float, default=0.04)
    a.add_argument("--tinta-traco", type=float, default=0.957)
    a.add_argument("--mancha-tom", type=float, default=0.6)
    a.add_argument("--mancha-sigma", type=float, default=3.0)
    a.add_argument("--escuro-piso", type=float, default=0.45)
    a.add_argument("--mancha-r", type=float, default=0, help="raio (px) que define mancha; 0 desliga")
    a.add_argument("--mancha-area", type=float, default=100)
    a.add_argument("--tom", type=int, default=1, help="sombreado do original vira hachura de gravura (1/0)")
    a.add_argument("--tom-sigma", type=float, default=0.8)
    a.add_argument("--tom-min", type=float, default=0.12)
    a.add_argument("--tom-piso", type=float, default=0.08, help="tom de papel/cinza claro descontado")
    a.add_argument("--tom-area", type=float, default=30)
    a.add_argument("--tom-w", type=float, default=0.9)
    a.add_argument("--tom-passo", type=float, default=2.4, help="espaço entre linhas da hachura, em larguras")
    a.add_argument("--tom-camadas", type=int, default=2, help="2 = hachura cruzada no tom mais escuro")
    a.add_argument("--tom-ganho", type=float, default=1.3)
    a.add_argument("--tom-comp-min", type=float, default=2.0)
    a.add_argument("--w-desc", type=float, default=0.3, help="traço com largura de contraste abaixo disso sai")
    a.add_argument("--hachura-w", type=float, default=1.5)
    a.add_argument("--hachura-passo", type=float, default=0.9, help="passo mínimo, em larguras")
    a.add_argument("--hachura-tom", type=float, default=1.0, help="ganho do tom sobre a densidade")
    a.add_argument("--hachura-ang", type=float, default=40)
    a.add_argument("--hachura-var", type=float, default=12)
    a.add_argument("--hachura-liga", type=float, default=2.6)
    return a.parse_args(argv)


def main(argv=None):
    p = argumentos(argv)
    tracos, info, gray = vetorizar(p.entrada, p)
    W, H = info["W"], info["H"]
    fator = p.fator
    precisa_render = p.calibrar or p.comparacao or p.recortes
    vec = None
    if precisa_render:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            nav = pw.chromium.launch(channel="msedge", headless=True)
            pag = nav.new_page(device_scale_factor=1)
            t_o = tinta(gray)
            linhas_so = [t for t in tracos if "w_fixo" not in t]   # a hachura tem largura fixa
            for it in range(3 if p.calibrar else 1):
                svg = escrever_svg(linhas_so if p.calibrar else tracos, W, H, fator, p)
                vec = renderizar_svg(svg, W, H, pag)
                r = (razao_local(gray, vec, fundo_r=p.fundo_r) if p.calibracao == "local"
                     else tinta(vec) / max(t_o, 1))
                info.setdefault("calibracao", []).append({"fator": round(fator, 3), "razao_tinta": round(r, 3)})
                if not p.calibrar or abs(r - 1) < 0.02:
                    break
                fator = fator / r
            if p.calibrar:
                svg = escrever_svg(tracos, W, H, fator, p)
                vec = renderizar_svg(svg, W, H, pag)
                info["calibracao"].append({"fator": round(fator, 3), "razao_tinta": round(tinta(vec) / t_o, 3),
                                           "razao_local": round(razao_local(gray, vec, fundo_r=p.fundo_r), 3)})
            nav.close()
    escrever_svg(tracos, W, H, fator, p, destino=p.saida)
    info["fator_espessura"] = round(fator, 3)
    info["svg_bytes"] = p.saida.stat().st_size
    if vec is not None:
        info["metricas"] = metricas(gray, vec)
        if p.comparacao:
            salvar_png(comparacao(gray, vec, not p.sem_sobreposicao, p.empilhar), p.comparacao)
        if p.recortes:
            salvar_png(vec, p.recortes / (p.saida.stem + "-render.png"))
    print(json.dumps(info, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

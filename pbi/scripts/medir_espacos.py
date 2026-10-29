#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""medir_espacos — prova de espaçamento de uma tela inteira (handoff §12.6: "render headless + medição das caixas: menor
distância entre irmãos, nada fora do contêiner, nada cortado").

Compõe a página FORA do Power BI, na escala de página (1920 × 1080):
  - papel de parede (assets/wallpapers/wp-tN.svg, o mesmo do PBIP);
  - cada visual HTML Content na árvore real do visual (html > body > #sandbox-host > #htmlViewer > .os-* > #htmlContent >
    .htmlViewerEntry > div; molde do render_html.py do painel de referência), num iframe srcdoc do tamanho exato, com o texto que a medida
    devolve agora no Desktop aberto (estado final das animações);
  - cada Deneb renderizado pelo Vega 6.4 (render_deneb.renderizar, com --caixas).
Mede a TINTA de todo texto (canvas measureText: actualBoundingBox*, na linha de base real) e a caixa de toda forma
visível; as caixas da casca saem do SVG (o texto do Figma vem em contorno, então a caixa é a tinta).

Acusa, por cartão (moldura do papel de parede):
  ERRO     sobreposição de texto com texto/forma; tinta para fora do visual (cortada); vizinho a menos de 8 px;
           texto menor que 14 px; menos de 24 px até a borda do cartão (padding)
  ATENÇÃO  vizinho vertical entre 8 e 16 px (lista de irmãos pode; título → conteúdo não pode: olhar a imagem)

    python -X utf8 pbi/scripts/medir_espacos.py T1                 # frente dos cartões
    python -X utf8 pbi/scripts/medir_espacos.py T1 --verso         # verso (flip) dos cartões de KPI
    python -X utf8 pbi/scripts/medir_espacos.py T1 --escala 2      # captura a 2x (para recortar e olhar de perto)

Saídas em pbi/qa/espacos/: <tela>[-verso].png (composição), .marcado.png (caixas + distâncias acusadas), .caixas.json,
.relatorio.txt. Somente leitura do modelo (consulta no Desktop aberto); não grava nada no PBIP.
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from dax import ErroDax, consultar  # noqa: E402
import render_deneb  # noqa: E402

RAIZ = AQUI.parent
PAGINAS = RAIZ / "pbip" / "VP.Report" / "definition" / "pages"
WALL = RAIZ / "assets" / "wallpapers"
QA = RAIZ / "qa" / "espacos"
EDGE = os.environ.get("VIZU_EDGE", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
FUNDO_PAGINA = "#E6EDF4"
W_PAG, H_PAG = 1920, 1080

MIN_VIZINHO = 8          # irmãos: nunca menos
MIN_TITULO = 16          # título → conteúdo (e o que não for lista)
MIN_PADDING = 24         # conteúdo → borda do cartão
MIN_FONTE = 14           # texto no painel
FOLGA_SIDEBAR = 312      # x < 312 é o trilho (arte e navegação do Figma): fora da prova

# Árvore do HTML Content (render_html.py do painel de referência; medida no Desktop em 07/09/2026)
CSS_BASE = """html,body{margin:0;padding:0}
#htmlViewer{width:100vw;height:100vh;overflow:auto}
#htmlViewer li{list-style:unset}
.os-host{position:relative;overflow:visible !important}
.os-padding{box-sizing:inherit;direction:inherit;position:absolute;overflow:hidden;padding:0;margin:0;left:0;top:0;bottom:0;right:0;width:auto !important;height:auto !important;z-index:0}
.os-viewport{direction:inherit !important;box-sizing:inherit !important;resize:none !important;outline:none !important;position:absolute;overflow:auto;top:0;left:0;bottom:0;right:0;padding:0;margin:0;scrollbar-width:none}
.os-viewport::-webkit-scrollbar{display:none !important;width:0 !important;height:0 !important}
.os-content{direction:inherit;box-sizing:border-box !important;position:relative;display:block;min-height:100%;width:100%;visibility:visible}"""
ESTILO_PADRAO = ("font-family: 'Segoe UI', wf_segoe-ui_normal, helvetica, arial, sans-serif; "
                 "font-size: 11pt; color: rgb(0, 0, 0); text-align: left; user-select: none;")
CSS_VERSO = ".kc__gira{transform:rotateY(180deg) !important;transition:none !important}"

JS_MEDIR = r"""(function () {
  var NOME = __NOME__, VERSO = __VERSO__;
  function todas() { try { return document.getAnimations(); } catch (e) { return []; } }
  function finalizar() { todas().forEach(function (a) { try { a.finish(); } catch (e) { } }); }
  function oculto(el) {
    for (var e = el; e && e.nodeType === 1; e = e.parentElement) {
      var cs = getComputedStyle(e);
      if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) < 0.05) { return true; }
      if (e.tagName === 'O-T' || e.tagName === 'STYLE' || e.tagName === 'SCRIPT') { return true; }
      if (e.classList && (VERSO ? e.classList.contains('kc__frente') : e.classList.contains('kc__verso'))) { return true; }
    }
    return false;
  }
  /* lista rolável do próprio desenho (ex.: tabela da T6): o que está fora da janela de rolagem não aparece e não é
     corte. A rolagem do visual (#htmlViewer, OverlayScrollbars) não conta: transbordar dela é erro. */
  function rolado(el, r) {
    for (var e = el.parentElement; e && e.nodeType === 1; e = e.parentElement) {
      if (e.id === 'htmlViewer' || e.id === 'htmlContent' || (e.classList && (e.classList.contains('os-viewport') ||
          e.classList.contains('os-padding') || e.classList.contains('os-content')))) { return false; }
      var oy = getComputedStyle(e).overflowY;
      if (oy === 'auto' || oy === 'scroll') {
        var a = e.getBoundingClientRect();
        return r.bottom <= a.top + 0.5 || r.top >= a.bottom - 0.5 || r.right <= a.left + 0.5 || r.left >= a.right - 0.5;
      }
    }
    return false;
  }
  function alfa(c) {
    if (!c || c === 'transparent') { return 0; }
    var m = /rgba?\(([^)]+)\)/.exec(c); if (!m) { return 1; }
    var p = m[1].split(','); return p.length > 3 ? parseFloat(p[3]) : 1;
  }
  function desc(el) {
    var s = el.tagName.toLowerCase(), c = el.getAttribute && el.getAttribute('class');
    if (c) { s += '.' + String(c).trim().split(/\s+/).slice(0, 2).join('.'); }
    return s;
  }
  var idSeq = 0;
  function idDe(el) { if (!el.__mid) { el.__mid = ++idSeq; } return el.__mid; }
  function medir() {
    var W = window.innerWidth, H = window.innerHeight, out = [], cv = document.createElement('canvas').getContext('2d');
    var raiz = document.getElementById('htmlContent') || document.body;
    var tw = document.createTreeWalker(raiz, NodeFilter.SHOW_TEXT), n;
    while ((n = tw.nextNode())) {
      var t = n.textContent || ''; if (!t.trim()) { continue; }
      var el = n.parentElement; if (!el || oculto(el)) { continue; }
      var cs = getComputedStyle(el);
      cv.font = cs.fontStyle + ' ' + cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily;
      var i0 = t.search(/\S/), i1 = t.length - (t.length - t.replace(/\s+$/, '').length);
      var rg = document.createRange(); rg.setStart(n, i0); rg.setEnd(n, i1);
      var rects = Array.prototype.filter.call(rg.getClientRects(), function (r) { return r.width > 0.5 && !rolado(el, r); });
      var tt = t.trim(), m = cv.measureText(tt);
      var asc = m.fontBoundingBoxAscent, des = m.fontBoundingBoxDescent;
      var bloco = el.closest('p,div,li,section,article,td,th,h1,h2,h3,h4,figure') || el;
      rects.forEach(function (r) {
        var base = r.top + (r.height - (asc + des)) / 2 + asc;
        out.push({ tipo: 'texto', texto: tt.slice(0, 60), fonte: cs.fontWeight + ' ' + cs.fontSize, px: parseFloat(cs.fontSize),
          x1: r.left - m.actualBoundingBoxLeft, x2: r.left + m.actualBoundingBoxRight * (r.width / Math.max(m.width, 0.01)),
          y1: base - m.actualBoundingBoxAscent, y2: base + m.actualBoundingBoxDescent, base: base,
          el: desc(el), pai: idDe(el), bloco: idDe(bloco) });
      });
    }
    Array.prototype.forEach.call(raiz.querySelectorAll('*'), function (el) {
      if (oculto(el)) { return; }
      var b = el.getBoundingClientRect(); if (b.width < 0.5 || b.height < 0.5 || rolado(el, b)) { return; }
      var cs = getComputedStyle(el), forma = false;
      if (el instanceof SVGGraphicsElement) {
        var tag = el.tagName.toLowerCase();
        if (/^(rect|circle|ellipse|path|line|polyline|polygon)$/.test(tag)) {
          forma = (cs.fill !== 'none' && alfa(cs.fill) > 0.05 && parseFloat(cs.fillOpacity) > 0.05) ||
                  (cs.stroke !== 'none' && alfa(cs.stroke) > 0.05 && parseFloat(cs.strokeWidth) > 0);
        }
      } else {
        forma = alfa(cs.backgroundColor) > 0.05 || (parseFloat(cs.borderTopWidth) > 0 && alfa(cs.borderTopColor) > 0.05);
      }
      if (!forma) { return; }
      var bl = el.closest('p,div,li,section,article,td,th,figure') || el;
      out.push({ tipo: 'forma', el: desc(el), x1: b.left, y1: b.top, x2: b.right, y2: b.bottom, pai: idDe(el.parentElement || el), bloco: idDe(bl) });
    });
    return { nome: NOME, viewport: { w: W, h: H }, caixas: out };
  }
  window.addEventListener('load', function () {
    setTimeout(finalizar, 50); setTimeout(finalizar, 900); setTimeout(finalizar, 1800);
    setTimeout(function () {
      finalizar();
      var d; try { d = medir(); } catch (e) { d = { nome: NOME, erro: String(e) }; }
      parent.postMessage({ tipo: 'bev-medidas', dados: d }, '*');
    }, 2200);
  });
})();"""

MOLDE_INNER = """<!doctype html><html><head><meta charset="utf-8">
<style>{css_base}{css_extra}</style>
<style id="visualUserStylesheet">{css_usuario}</style>
<script>{js}</script>
</head><body class="visual-sandbox"><div id="sandbox-host" class="visual"><div id="htmlViewer" class="os-host" style="{estilo}"><div class="os-padding"><div class="os-viewport"><div class="os-content"><div id="landingPage"></div><div id="statusMessage"></div><div tabindex="0" id="htmlContent">{entradas}</div></div></div></div></div></div></body></html>"""

MOLDE_PAGINA = """<!doctype html><html><head><meta charset="utf-8"><title>{titulo}</title>
<style>html,body{{margin:0;padding:0;width:{W}px;height:{H}px;overflow:hidden;background:{fundo}}}
.wp{{position:absolute;left:0;top:0;width:{W}px;height:{H}px}}.v{{position:absolute;border:0;display:block;background:transparent}}</style>
</head><body>
<img class="wp" src="{wall}">
{deneb}
{iframes}
<pre id="__medidas__" hidden></pre>
<script>(function () {{
  var esperados = {n}, recebidos = [];
  window.addEventListener('message', function (e) {{
    if (!e.data || e.data.tipo !== 'bev-medidas') {{ return; }}
    recebidos.push(e.data.dados);
    if (recebidos.length >= esperados) {{
      document.getElementById('__medidas__').textContent = btoa(unescape(encodeURIComponent(JSON.stringify(recebidos))));
    }}
  }});
  if (esperados === 0) {{ document.getElementById('__medidas__').textContent = btoa('[]'); }}
}})();</script>
</body></html>"""


def url(p: Path) -> str:
    return "file:///" + str(p.resolve()).replace("\\", "/").replace(" ", "%20").replace("#", "%23")


def ler_visuais(tela: str) -> list[dict]:
    """Visuais da tela pelas DECLARAÇÕES (paginas/*.py), não pelo PBIR gravado: a prova vale para o que vai ser montado."""
    import montar_pbip
    ctx = montar_pbip.carregar_contexto()
    docs = [it.doc for it in montar_pbip.carregar_declaracoes(ctx)
            if type(it).__name__ == "Visual" and it.pagina == tela]
    vis = []
    for d in sorted(docs, key=lambda x: x["name"]):
        v = d.get("visual") or {}
        tipo = v.get("visualType", "")
        pos = d["position"]
        item = {"nome": d["name"], "tipo": tipo, "x": pos["x"], "y": pos["y"], "w": pos["width"], "h": pos["height"],
                "doc": d, "oculto": bool(d.get("isHidden"))}
        if tipo.startswith("STANDALONEhtmlContent"):
            qs = (v.get("query") or {}).get("queryState") or {}
            proj = (qs.get("content") or {}).get("projections") or []
            if proj and "Measure" in proj[0]["field"]:
                item["medida"] = proj[0]["field"]["Measure"]["Property"]
            item["outros_papeis"] = [k for k in qs if k != "content"]
            # granularidade (papel sampling, ex.: dLote[Lote] da tabela em lotes da T6): uma entrada por linha
            amos = (qs.get("sampling") or {}).get("projections") or []
            if amos and "Column" in amos[0]["field"]:
                c = amos[0]["field"]["Column"]
                item["granularidade"] = (c["Expression"]["SourceRef"]["Entity"], c["Property"])
            vis.append(item)
        elif tipo.startswith("STANDALONEdeneb"):
            vis.append(item)
    return vis


def avaliar_html(visuais: list[dict], do_disco: bool, filtros: list[str] = ()) -> dict:
    """Texto de cada medida HTML no motor do Desktop aberto. Com do_disco, as medidas de pbi/dax/** entram como DEFINE
    MEASURE (sobrescrevem as do modelo só nesta consulta): mede o que está no disco sem fechar o Desktop. `filtros` =
    o contexto do hover numa página de tooltip (ex.: dCalendario[Data] = DATE ( 2026, 8, 12 ))."""
    alvo = [v for v in visuais if v.get("medida") and not v["outros_papeis"]]
    lotes = [v for v in visuais if v.get("medida") and v.get("granularidade") and v["outros_papeis"] == ["sampling"]]
    if not alvo and not lotes:
        return {}
    cols = ",\n    ".join(f'"h{i}", [{v["medida"]}]' for i, v in enumerate(alvo))
    prefixo = ""
    if do_disco:
        import testar_dax
        arqs = sorted(p for p in (RAIZ / "dax").rglob("*.dax") if "_modelo" not in p.parts)
        prefixo = testar_dax.define(arqs)
    out = {}
    filtros = list(filtros) + ['Filtros[Item] = "Aplicar"']     # grupo de cálculo do drawer, como nos visuais
    if alvo:
        linha = f"ROW (\n    {cols}\n)"
        if filtros:
            linha = f"CALCULATETABLE (\n    {linha},\n    " + ",\n    ".join(filtros) + "\n)"
        linhas = consultar(f"{prefixo}EVALUATE {linha}")
        r = linhas[0]
        out = {v["nome"]: r.get(f"[h{i}]") or "" for i, v in enumerate(alvo)}
    # visual com granularidade: uma entrada por linha da coluna, na ordem dela (como o HTML Content empilha as
    # .htmlViewerEntry); linha com a medida vazia não vira entrada
    for v in lotes:
        t, c = v["granularidade"]
        tab = f"SUMMARIZECOLUMNS ( '{t}'[{c}], \"h\", [{v['medida']}] )"
        if filtros:
            tab = f"CALCULATETABLE ( {tab}, " + ", ".join(filtros) + " )"
        linhas = consultar(f"{prefixo}EVALUATE {tab} ORDER BY '{t}'[{c}]")
        out[v["nome"]] = [l.get("[h]") for l in linhas if l.get("[h]")]
    return out


def _nome_svg(e) -> str:
    n = e.values.get("id") or ""
    try:
        n = n.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    return n


def caixas_casca(tela: str) -> list[dict]:
    """Folhas visíveis do papel de parede, com o nome do grupo nomeado mais próximo (o Figma não nomeia os retângulos
    de um botão, mas nomeia o grupo 'Botão · como ler'). Texto do Figma vem em contorno: a caixa já é a tinta."""
    import svgelements as se
    svg = se.SVG.parse(str(WALL / f"wp-{tela.lower()}.svg"))
    out = []

    def andar(el, grupo):
        for e in el:
            if isinstance(e, se.Group):
                andar(e, _nome_svg(e) or grupo)
                continue
            if not isinstance(e, se.Shape):
                continue
            fill_ok = e.fill is not None and e.fill.value is not None and e.fill.alpha > 0.05
            stroke_ok = (e.stroke is not None and e.stroke.value is not None and e.stroke.alpha > 0.05
                         and (e.stroke_width or 0) > 0)
            if not (fill_ok or stroke_ok):
                continue
            try:
                b = e.bbox()
            except Exception:
                b = None
            if not b:
                continue
            x1, y1, x2, y2 = (float(v) for v in b)
            if x2 - x1 < 0.3 and y2 - y1 < 0.3:
                continue
            nome = _nome_svg(e) or grupo
            moldura = isinstance(e, se.Rect) and x2 - x1 >= 300 and y2 - y1 >= 120
            out.append({"origem": "casca", "tipo": "moldura" if moldura else "casca", "texto": nome, "grupo": grupo,
                        "x1": x1, "y1": y1, "x2": x2, "y2": y2})

    andar(svg, "")
    return out


def compor(tela: str, visuais: list[dict], htmls: dict, verso: bool, deneb_png: dict, W: int = W_PAG, H: int = H_PAG,
           fundo: str = FUNDO_PAGINA, com_papel: bool = True) -> str:
    iframes = []
    for v in visuais:
        if v["nome"] not in htmls:
            continue
        js = JS_MEDIR.replace("__NOME__", json.dumps(v["nome"])).replace("__VERSO__", "true" if verso else "false")
        conteudo = htmls[v["nome"]]
        partes = conteudo if isinstance(conteudo, list) else [conteudo]
        interno = MOLDE_INNER.format(css_base=CSS_BASE, css_extra=CSS_VERSO if verso else "", css_usuario="", js=js,
                                     estilo=ESTILO_PADRAO,
                                     entradas="".join(f'<div class="htmlViewerEntry"><div>{h}</div></div>'
                                                      for h in partes))
        iframes.append(f'<iframe class="v" title="{html.escape(v["nome"])}" style="left:{v["x"]}px;top:{v["y"]}px;'
                       f'width:{v["w"]}px;height:{v["h"]}px" width="{round(v["w"])}" height="{round(v["h"])}" '
                       f'srcdoc="{html.escape(interno, quote=True)}"></iframe>')
    deneb = [f'<img class="v" src="{url(p)}" style="left:{v["x"]}px;top:{v["y"]}px;width:{v["w"]}px;height:{v["h"]}px">'
             for v in visuais for nome, p in deneb_png.items() if nome == v["nome"]]
    texto = MOLDE_PAGINA.format(titulo=f"{tela} composta", W=W, H=H, fundo=fundo,
                                wall=url(WALL / f"wp-{tela.lower()}.svg") if com_papel else "", deneb="\n".join(deneb),
                                iframes="\n".join(iframes), n=len(iframes))
    return texto if com_papel else texto.replace('<img class="wp" src="">\n', "")


def rodar_edge(pagina: Path, png: Path, escala: int, W: int = W_PAG, H: int = H_PAG) -> list[dict]:
    perfil = tempfile.mkdtemp(prefix="bev_edge_")
    args = {"edge": EDGE, "url": url(pagina), "perfil": perfil, "janela_w": W + 80, "janela_h": H + 240,
            "escala": escala, "virtual_ms": 3500, "reduzir": False, "timeout_ms": 120000, "png": str(png),
            "recorte": {"x": 0, "y": 0, "w": W, "h": H}}
    try:
        r = subprocess.run(["node", str(AQUI / "edge_cdp.mjs"), json.dumps(args)], capture_output=True, timeout=180)
    finally:
        time.sleep(0.6)
        shutil.rmtree(perfil, ignore_errors=True)
    if r.returncode:
        raise SystemExit("edge_cdp falhou: " + (r.stderr or b"").decode("utf-8", "replace")[-600:])
    bruto = (r.stdout or b"").decode("utf-8", "replace").strip()
    if not bruto:
        raise SystemExit("a medição não chegou (nenhum iframe respondeu)")
    return json.loads(base64.b64decode(bruto).decode("utf-8"))


# ---------------------------------------------------------------------------------------------------------- análise
def contem(a, b, folga=0.5) -> bool:
    return a["x1"] - folga <= b["x1"] and a["y1"] - folga <= b["y1"] and a["x2"] + folga >= b["x2"] and a["y2"] + folga >= b["y2"]


def sobrepoe(a, b) -> bool:
    return a["x1"] < b["x2"] - 0.5 and b["x1"] < a["x2"] - 0.5 and a["y1"] < b["y2"] - 0.5 and b["y1"] < a["y2"] - 0.5


def rotulo(c) -> str:
    t = c.get("texto") or c.get("el") or c.get("marca") or c.get("tipo")
    return f"{c['origem']}:{t!s}"[:70]


CANTO = ("Botão · como ler",)   # "?" do cartão: alinhado ao centro do título (Figma), fora da prova de padding
MIN_MARCADOR = 7                # quadradinho de legenda → rótulo (Figma: 7,4)
MARCAS_FUNDO = ("faixa", "rot_fundo")       # marcas Deneb que são fundo (faixa de fim de semana, faixa do hover)


def area(c) -> float:
    return max(0.0, c["x2"] - c["x1"]) * max(0.0, c["y2"] - c["y1"])


def analisar(caixas: list[dict], min_padding: float = MIN_PADDING, min_fonte: float = MIN_FONTE,
             x_min: float = FOLGA_SIDEBAR) -> tuple[list[dict], list[dict]]:
    """Regras (px de página, sobre a TINTA):
    - unidade = texto solto, ou a forma que contém texto (pílula, célula): o miolo não é vizinho do recipiente;
    - mesma frase = textos da mesma origem na mesma linha de base, separados por até 0,6 em (palavra, número e
      unidade, '75,1' e '%'): não são vizinhos;
    - mesmo parágrafo (mesmo bloco HTML) empilhado: entrelinha, não vizinho;
    - fundo = forma 15 vezes maior que o texto que ela cruza (faixa de fim de semana): não é sobreposição;
    - forma pequena (≤ 14 px) à esquerda do texto na mesma linha = marcador de legenda: mínimo MIN_MARCADOR;
    - séries: unidade e forma da MESMA marca (células do mapa, barras) não se medem entre si."""
    molduras = [c for c in caixas if c["tipo"] == "moldura"]
    itens = [c for c in caixas if c["tipo"] != "moldura" and c["x1"] >= x_min - 0.5]
    achados = []

    def cartao(c):
        cx, cy = (c["x1"] + c["x2"]) / 2, (c["y1"] + c["y2"]) / 2
        dentro = [m for m in molduras if m["x1"] <= cx <= m["x2"] and m["y1"] <= cy <= m["y2"]]
        return min(dentro, key=area) if dentro else None

    def add(nivel, regra, px, a, b=None):
        achados.append({"nivel": nivel, "regra": regra, "px": round(px, 1), "a": rotulo(a),
                        "b": rotulo(b) if b is not None else None, "caixa": a, "outra": b})

    def faixa_de_linha(c):
        """Faixa de zebra/destaque de tabela (tb-z) ou faixa larga e baixa atrás de uma linha: é fundo da linha."""
        el = str(c.get("el", ""))
        w, h = c["x2"] - c["x1"], c["y2"] - c["y1"]
        # barras de dado e trilhos (lt-bar, tv-bar, tb-b, f-k, tb-t) não são fundo: 02/10, "3.075" encostado numa barra
        # de 226 px passava porque toda forma larga e baixa saía da prova
        if any(k in el for k in ("bar", "tb-b", "tb-t", "f-k", "lt-col", "tv-col")):
            return False
        # linha do extrato da T6 (div.xr, 48 px: linha de tabela >= 44 px, handoff §12.3) também é fundo da linha
        return c["tipo"] != "texto" and ("tb-z" in el or el.startswith("div.xr") or (w >= 200 and h <= 34 and w >= 6 * h))

    for c in itens:
        c["_cartao"] = cartao(c)
    todas = list(itens)                               # com as faixas: barra larga e baixa também apaga a grade
    itens = [c for c in itens if not faixa_de_linha(c)]
    textos = [c for c in itens if c["tipo"] == "texto"]
    formas = [c for c in itens if c["tipo"] != "texto" and not str(c.get("marca") or "").startswith(MARCAS_FUNDO)]
    for t in textos:
        conts = [f for f in formas if f["_cartao"] is t["_cartao"] and contem(f, t) and area(f) < 40 * max(area(t), 1)]
        t["_recip"] = min(conts, key=area) if conts else None
        if t["_recip"] is not None:
            t["_recip"]["_rotulada"] = True
    # 1) texto pequeno e tinta fora do visual
    for c in textos:
        if c.get("px") and c["px"] < min_fonte - 0.01:
            add("ERRO", "fonte", c["px"], c)
        if c.get("fora"):
            add("ERRO", "cortado", c["fora"], c)
    # 2) padding até a borda do cartão (a folha inteira não é cartão)
    for c in itens:
        m = c["_cartao"]
        if m is None or (m["x2"] - m["x1"]) > 1500 and (m["y2"] - m["y1"]) > 1000:
            continue
        if any(c.get("grupo", "").startswith(k) or str(c.get("texto", "")).startswith(k) for k in CANTO) \
                or str(c.get("el", "")).startswith("div.lt-x"):
            continue                                          # "?" do cartão e o × da leitura (mesmo lugar)
        # base: até a linha de base do texto (convenção do painel de referência: "linha de base da última linha em altura − 33")
        fundo_y = c["base"] if c["tipo"] == "texto" and c.get("base") is not None else c["y2"]
        lados = [c["x1"] - m["x1"], m["x2"] - c["x2"], c["y1"] - m["y1"], m["y2"] - fundo_y]
        d = min(lados)
        lado = ['esquerda', 'direita', 'topo', 'base'][lados.index(d)]
        if d < min_padding - 0.5:
            # gancho de glifo (J, j, f…) que passa 1 px da caixa do texto: alinhamento óptico, não aperto
            if c["tipo"] == "texto" and lado in ("esquerda", "direita") and d >= min_padding - 1.5:
                add("ATENÇÃO", f"padding ({lado}, sobra do glifo)", d, c)
            else:
                add("ERRO", f"padding ({lado})", d, c)

    # 3) vizinhos e sobreposição, por unidade
    def unidade(c):
        return c["_recip"] if c["tipo"] == "texto" and c.get("_recip") is not None else c

    def mesma_frase(a, b):
        if a["tipo"] != "texto" or b["tipo"] != "texto" or a["origem"] != b["origem"]:
            return False
        if a.get("base") is None or b.get("base") is None or abs(a["base"] - b["base"]) > 1.5:
            return False
        # HTML: blocos diferentes (duas células, dois rótulos) nunca são a mesma frase, por mais perto que fiquem
        # (02/10: "Doca" e "Veículos" a 4 px passavam como palavras da mesma frase)
        if isinstance(a.get("bloco"), int) and isinstance(b.get("bloco"), int) and a["bloco"] != b["bloco"]:
            return False
        gap = b["x1"] - a["x2"] if b["x1"] >= a["x2"] else a["x1"] - b["x2"]
        return gap < 0.6 * max(a.get("px") or 16, b.get("px") or 16)

    def mesmo_paragrafo(a, b):
        return (a["tipo"] == "texto" and b["tipo"] == "texto" and a["origem"] == b["origem"]
                and a.get("bloco") is not None and a.get("bloco") == b.get("bloco"))

    def mesma_serie(a, b):
        """Unidade e forma da mesma marca (células do mapa entre si). Texto com texto da mesma marca SE mede (linhas)."""
        if a["tipo"] == "texto" and b["tipo"] == "texto":
            return False
        return a["origem"] == b["origem"] and a.get("marca") and a.get("marca") == b.get("marca")

    def ligados(a, b):
        """Pílula e o fio que a liga à coluna (x_pil ↔ x_fio): encostam por desenho."""
        ma, mb = str(a.get("marca") or ""), str(b.get("marca") or "")
        return a["origem"] == b["origem"] and (
            (ma.endswith("_pil") and mb == ma[:-4] + "_fio") or (mb.endswith("_pil") and ma == mb[:-4] + "_fio"))

    def fio_fino(c):
        return c["tipo"] != "texto" and min(c["x2"] - c["x1"], c["y2"] - c["y1"]) <= 2.5

    def base_ou_fundo(c):
        return c["base"] if c["tipo"] == "texto" and c.get("base") is not None else c["y2"]

    def escondido(a, b):
        """Fio (grade, referência) atrás de uma forma opaca desenhada depois dele que contém o texto: a barra ou o fundo
        do rótulo apagam o fio em volta do texto, então fio e texto não se tocam na tela (Deneb: z = ordem de desenho)."""
        if a["tipo"] != "texto" or not fio_fino(b) or b.get("z") is None:
            return False
        vertical = (b["x2"] - b["x1"]) <= (b["y2"] - b["y1"])
        for c in todas:
            if (c is a or c is b or c["tipo"] == "texto" or not c.get("opaco") or c.get("z") is None
                    or c["z"] <= b["z"] or c["origem"] != a["origem"] or fio_fino(c) or not contem(c, a)):
                continue
            if (vertical and c["x1"] - 0.5 <= b["x1"] and b["x2"] <= c["x2"] + 0.5) or \
                    (not vertical and c["y1"] - 0.5 <= b["y1"] and b["y2"] <= c["y2"] + 0.5):
                return True
        return False

    unidades = []
    for c in itens:
        u = unidade(c)
        if u is c and (c["tipo"] == "texto" or c.get("_rotulada")) and c not in unidades:
            unidades.append(c)
    alvos = [c for c in itens if not (c["tipo"] == "texto" and c.get("_recip") is not None)]
    for a in unidades:
        melhor = {}
        for b in alvos:
            if b is a or b["_cartao"] is not a["_cartao"] or mesma_serie(a, b) or ligados(a, b):
                continue
            if b["tipo"] != "texto" and (
                    contem(b, a, folga=0)
                    or not b.get("_rotulada") and (area(b) > 15 * max(area(a), 1)
                                                   or str(b.get("marca") or "").startswith(MARCAS_FUNDO))):
                continue                                      # fundo atrás da unidade (caixa de nota que a contém)
            if a["tipo"] != "texto" and contem(a, b, folga=0):
                continue                                      # o que está dentro da caixa (texto e ícone da nota)
            if (mesma_frase(a, b) or mesmo_paragrafo(a, b)) and not sobrepoe(a, b):
                continue                                      # palavra da mesma frase: só não pode encostar
            if (mesma_frase(a, b) or mesmo_paragrafo(a, b)) and \
                    min(a["x2"], b["x2"]) - max(a["x1"], b["x1"]) <= 1.5:
                continue                                      # pedaços da mesma linha corrida: tinta de "(" e "3"
            if escondido(a, b):
                continue                                      # fio apagado pela barra/fundo opaco em volta do texto
            if sobrepoe(a, b):
                if b in unidades and id(b) < id(a):
                    continue
                if a.get("_rotulada") and fio_fino(b):
                    continue                                  # pílula opaca por cima da linha de grade/referência
                add("ERRO", "sobreposição", 0, a, b)
                continue
            sx = min(a["x2"], b["x2"]) - max(a["x1"], b["x1"])
            sy = min(a["y2"], b["y2"]) - max(a["y1"], b["y1"])
            if sx > 0.5 and b["y1"] >= a["y2"] - 0.5:
                k, gap = "baixo", b["y1"] - base_ou_fundo(a)
            elif sx > 0.5 and a["y1"] >= b["y2"] - 0.5 and b not in unidades:
                k, gap = "cima", a["y1"] - b["y2"]
            elif sy > 0.5 and b["x1"] >= a["x2"] - 0.5:
                k, gap = "direita", b["x1"] - a["x2"]
            elif sy > 0.5 and a["x1"] >= b["x2"] - 0.5 and b not in unidades:
                k, gap = "esquerda", a["x1"] - b["x2"]
            else:
                continue
            if a.get("_rotulada") and fio_fino(b) and gap < 1:
                continue                                      # pílula pousada na própria linha (média, grade)
            if k not in melhor or gap < melhor[k][0]:
                melhor[k] = (gap, b)
        for k, (gap, b) in melhor.items():
            if k in ("direita", "esquerda"):
                marcador = (b["tipo"] != "texto" and k == "esquerda" and (b["x2"] - b["x1"]) <= 14.5
                            and (b["y2"] - b["y1"]) <= 14.5)
                minimo = MIN_MARCADOR if marcador else MIN_VIZINHO
                if gap < minimo - 0.01:
                    add("ERRO", "marcador → texto" if marcador else "vizinho horizontal", gap, a, b)
            else:
                if gap < MIN_VIZINHO - 0.01:
                    add("ERRO", "vizinho vertical", gap, a, b)
                elif gap < MIN_TITULO - 0.01:
                    add("ATENÇÃO", "vizinho vertical", gap, a, b)
    vistos, unicos = set(), []
    for f in achados:
        k = (f["regra"], f["a"], f.get("b"), f["px"])
        if k not in vistos:
            vistos.add(k)
            unicos.append(f)
    unicos.sort(key=lambda f: (f["nivel"] != "ERRO", f["regra"], f["px"]))
    return unicos, itens


def marcar(png: Path, destino: Path, itens: list[dict], achados: list[dict], escala: int) -> None:
    from PIL import Image, ImageDraw
    im = Image.open(png).convert("RGB")
    dr = ImageDraw.Draw(im, "RGBA")
    s = escala
    for c in itens:
        cor = (0, 160, 220, 150) if c["tipo"] == "texto" else (200, 0, 200, 90)
        dr.rectangle([c["x1"] * s, c["y1"] * s, c["x2"] * s, c["y2"] * s], outline=cor, width=1)
    for f in achados:
        a, b = f["caixa"], f.get("outra")
        cor = (230, 0, 0, 255) if f["nivel"] == "ERRO" else (255, 140, 0, 255)
        dr.rectangle([a["x1"] * s, a["y1"] * s, a["x2"] * s, a["y2"] * s], outline=cor, width=2)
        if b is not None:
            dr.rectangle([b["x1"] * s, b["y1"] * s, b["x2"] * s, b["y2"] * s], outline=cor, width=2)
        dr.text((a["x1"] * s, max(0, a["y1"] * s - 12)), f"{f['regra']} {f['px']}", fill=cor)
    im.save(destino)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("tela")
    ap.add_argument("--verso", action="store_true", help="mede o verso (flip) dos cartões de KPI")
    ap.add_argument("--escala", type=int, default=1)
    ap.add_argument("--saida", default=str(QA))
    ap.add_argument("--modelo", action="store_true",
                    help="usa as medidas do modelo aberto (padrão: as de pbi/dax/** injetadas como DEFINE MEASURE)")
    ap.add_argument("--filtro", action="append", default=[],
                    help="contexto do hover numa página de tooltip, ex. \"dCalendario[Data] = DATE ( 2026, 8, 12 )\"")
    ap.add_argument("--sufixo", default="", help="sufixo dos arquivos de saída (ex.: o item do hover)")
    ap.add_argument("--so", action="append", default=[],
                    help="mede só estes visuais (ex.: T1_Mov_Leitura, uma leitura do ? aberta sobre o papel de parede)")
    a = ap.parse_args()
    if not Path(EDGE).exists():
        raise SystemExit(f"Edge não encontrado: {EDGE} (defina VIZU_EDGE)")
    saida = Path(a.saida)
    saida.mkdir(parents=True, exist_ok=True)
    nome = a.tela.lower() + ("-verso" if a.verso else "") + (f"-{a.sufixo}" if a.sufixo else "")
    tooltip = a.tela.startswith("tt")
    # página de tooltip: balão 720 × 480 no branco da página, margem 32 (medida na tinta), nada abaixo de 16 px
    W, H = (720, 480) if tooltip else (W_PAG, H_PAG)
    visuais = ler_visuais(a.tela)
    # visual oculto (leitura do "?", botão Fechar) fica de fora da página; --so escolhe o que medir (inclusive oculto)
    visuais = [v for v in visuais if v["nome"] in a.so] if a.so else [v for v in visuais if not v["oculto"]]
    leitura = bool(a.so) and all(v["nome"].endswith("_Leitura") for v in visuais)
    try:
        htmls = avaliar_html(visuais, not a.modelo, a.filtro)
    except ErroDax as e:
        raise SystemExit("ERRO DO MOTOR: " + e.mensagem)
    deneb_png, deneb_cx = {}, {}
    define = ""
    if not a.modelo and any(v["tipo"].startswith("STANDALONEdeneb") for v in visuais):
        import testar_dax
        define = testar_dax.define(sorted(p for p in (RAIZ / "dax").rglob("*.dax") if "_modelo" not in p.parts))
    for v in visuais:
        if v["tipo"].startswith("STANDALONEdeneb"):
            r = render_deneb.renderizar(a.tela, v["nome"], escala=str(max(2, a.escala)), caixas=True, fundo="transparente",
                                        sufixo="espacos", doc=v["doc"], define=define, filtros=a.filtro)
            if r["codigo"]:
                raise SystemExit(f"render do Deneb {v['nome']} falhou: {r['stderr'][-800:]}")
            deneb_png[v["nome"]] = r["png"]
            deneb_cx[v["nome"]] = json.loads(Path(r["caixas"]).read_text(encoding="utf-8"))
    pagina = saida / f"{nome}.composto.html"
    pagina.write_text(compor(a.tela, visuais, htmls, a.verso, deneb_png, W, H, "#FFFFFF" if tooltip else FUNDO_PAGINA,
                             com_papel=not tooltip), encoding="utf-8")
    png = saida / f"{nome}.png"
    medidas = rodar_edge(pagina, png, a.escala, W, H)
    caixas = ([{"origem": "pagina", "tipo": "moldura", "texto": "balão", "x1": 0, "y1": 0, "x2": W, "y2": H}]
              if tooltip else caixas_casca(a.tela))
    pos = {v["nome"]: v for v in visuais}
    for m in medidas:
        v = pos.get(m.get("nome"))
        if not v:
            continue
        if m.get("erro"):
            print(f"ERRO de medição em {m['nome']}: {m['erro']}")
            continue
        W, H = m["viewport"]["w"], m["viewport"]["h"]
        for c in m["caixas"]:
            fora = max(0 - c["x1"], 0 - c["y1"], c["x2"] - W, c["y2"] - H)
            c.update({"origem": v["nome"], "x1": c["x1"] + v["x"], "x2": c["x2"] + v["x"], "y1": c["y1"] + v["y"],
                      "y2": c["y2"] + v["y"]})
            if "base" in c:
                c["base"] += v["y"]
            if c["tipo"] == "texto" and fora > 0.5:
                c["fora"] = round(fora, 1)
            caixas.append(c)
    for nome_v, lst in deneb_cx.items():
        v = pos[nome_v]
        for c in lst:
            if c["tipo"] == "grupo":
                continue
            fora = max(0 - c["x1"], 0 - c["y1"], c["x2"] - v["w"], c["y2"] - v["h"])
            c2 = {**c, "origem": nome_v, "tipo": "texto" if c["tipo"] == "texto" else "forma",
                  "x1": c["x1"] + v["x"], "x2": c["x2"] + v["x"], "y1": c["y1"] + v["y"], "y2": c["y2"] + v["y"],
                  "bloco": f"{nome_v}:{c.get('marca')}"}
            if c["tipo"] == "texto":
                c2["px"] = float(str(c.get("fonte", "0 0px")).split()[-1].rstrip("px") or 0)
                if fora > 0.5:
                    c2["fora"] = round(fora, 1)
            caixas.append(c2)
    if leitura:
        # a leitura cobre o cartão: o cartão é a moldura (a casca embaixo fica de fora, e o fundo branco da própria
        # leitura, div.bv.lt, é a moldura e não um vizinho), margem 32, texto ≥ 16
        caixas = [c for c in caixas if c.get("origem") != "casca" and not str(c.get("el", "")).startswith("div.bv.lt")]
        for v in visuais:
            caixas.append({"origem": "cartão", "tipo": "moldura", "texto": v["nome"], "x1": v["x"], "y1": v["y"],
                           "x2": v["x"] + v["w"], "y2": v["y"] + v["h"]})
        achados, itens = analisar(caixas, min_padding=32, min_fonte=16, x_min=0)
    else:
        achados, itens = (analisar(caixas, min_padding=32, min_fonte=16, x_min=0) if tooltip else analisar(caixas))
    limpo = [{k: v for k, v in c.items() if not k.startswith("_")} for c in caixas]
    (saida / f"{nome}.caixas.json").write_text(json.dumps(limpo, ensure_ascii=False, indent=0), encoding="utf-8")
    marcar(png, saida / f"{nome}.marcado.png", itens, achados, a.escala)
    linhas = [f"{a.tela}{' (verso)' if a.verso else ''}: {len(itens)} caixas medidas ({sum(c['tipo'] == 'texto' for c in itens)} "
              f"textos) · {sum(f['nivel'] == 'ERRO' for f in achados)} ERRO · {sum(f['nivel'] != 'ERRO' for f in achados)} ATENÇÃO"]
    for f in achados:
        linhas.append(f"{f['nivel']:8} {f['regra']:20} {f['px']!s:>6}  {f['a']}" + (f"  ↔  {f['b']}" if f.get("b") else ""))
    (saida / f"{nome}.relatorio.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("\n".join(linhas))
    print(f"\nimagem: {png}\nmarcada: {saida / (nome + '.marcado.png')}")
    return 1 if any(f["nivel"] == "ERRO" for f in achados) else 0


if __name__ == "__main__":
    sys.exit(main())

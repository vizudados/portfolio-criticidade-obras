#!/usr/bin/env python
"""Monta a prévia HTML (autocontida) do traço se desenhando e, se pedido, tira quadros congelados.

Uso (sempre com python -I):
    python -I montar_preview.py SAIDA.html --cena A.svg:5 [--cena B.svg:5:0.93 ...]
        [--quadro DESTINO.png:INDICE_DA_CENA:SEGUNDOS ...] [--titulo "..."] [--medir]

--cena SVG:JANELA[:ESCALA]. Cada SVG vem do vetorizar_traco.py: cada <path> tem pathLength e uma classe
kN, e a raiz traz data-tempos="atraso,duracao;..." (um par por kN). Na sua janela, a cena desenha de
0 a 3 s (cada traço com o atraso e a duração da sua classe; com --ordem baixo, uma frente sobe do chão
ao topo e cada traço vai da ponta de baixo à de cima) e fica parada até o fim da janela. Depois some
de uma vez (papel em branco) e entra a próxima; ao fim da última, o laço recomeça. ESCALA < 1 encolhe
a cena ancorada no topo e centralizada na horizontal.

Cada cena tem a própria linha do tempo: o contêiner liga e desliga com `display` (as cenas fora do ar
não custam nada) e, ao voltar, as animações dos traços recomeçam do zero.

Palco 1920x640, fundo branco, desenho centralizado e cabendo na altura. Sem números: eles entram por
HTML por cima, na implementação. Os quadros congelam o tempo com animation-play-state: paused e
animation-delay negativo, no Edge (Playwright).
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

PALCO_W, PALCO_H = 1920, 640
EASE = "cubic-bezier(.4,.05,.55,1)"
OCULTO = "1.001"


def ler_svg(caminho: Path) -> tuple[str, list[tuple[float, float]], str]:
    svg = caminho.read_text(encoding="utf-8")
    svg = re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", svg)
    m = re.search(r'data-tempos="([^"]+)"', svg)
    if not m:
        raise SystemExit(f"{caminho}: SVG sem data-tempos (gere com vetorizar_traco.py)")
    tempos = [tuple(float(x) for x in par.split(",")) for par in m.group(1).split(";")]
    o = re.search(r'data-ordem="([^"]+)"', svg)
    return svg, tempos, (o.group(1) if o else "junto")


def pct(t: float, T: float) -> str:
    return f"{100.0 * t / T:.4f}".rstrip("0").rstrip(".") + "%"


def montar(cenas: list[tuple[Path, float, float]], titulo: str) -> tuple[str, list[float]]:
    T = sum(d for _, d, _ in cenas)
    inicios, acc = [], 0.0
    for _, d, _ in cenas:
        inicios.append(acc)
        acc += d
    css = [f"""
:root {{ color-scheme: light; }}
html, body {{ margin: 0; background: #fff; }}
body {{ font: 13px/1.4 system-ui, sans-serif; color: #555; }}
.palco {{ position: relative; width: min(100vw, {PALCO_W}px); aspect-ratio: {PALCO_W} / {PALCO_H};
  margin: 0 auto; background: #fff; overflow: hidden; }}
.palco > svg {{ position: absolute; inset: 0; width: 100%; height: 100%; display: block; }}
.palco path {{ stroke-dasharray: 1 2; stroke-dashoffset: {OCULTO};
  animation-iteration-count: infinite; animation-timing-function: {EASE}; animation-fill-mode: both; }}
.legenda {{ max-width: {PALCO_W}px; margin: 8px auto; padding: 0 16px; }}
"""]
    corpo, ordens = [], []
    for i, ((cam, dur, esc), ini) in enumerate(zip(cenas, inicios)):
        svg, tempos, ordem = ler_svg(cam)
        ordens.append(ordem)
        css.append(f"#c{i} path {{ animation-duration: {dur:g}s; }}")
        for k, (atraso, du) in enumerate(tempos):
            a, b = atraso, atraso + du
            css.append(f"@keyframes s{i}k{k} {{ 0%, {pct(a, dur)} {{ stroke-dashoffset: {OCULTO}; }} "
                       f"{pct(b, dur)}, 100% {{ stroke-dashoffset: 0; }} }}")
            css.append(f"#c{i} path.k{k} {{ animation-name: s{i}k{k}; }}")
        if abs(esc - 1) > 1e-6:
            css.append(f"#c{i} {{ transform: scale({esc:g}); transform-origin: 50% 0; }}")
        if len(cenas) > 1:
            fim = ini + dur
            ultimo = abs(fim - T) < 1e-9
            if ini == 0:
                vis = f"0%, {pct(fim - 0.002, T)} {{ display: block; }} {pct(fim, T)}, 100% {{ display: none; }}"
            elif ultimo:
                vis = f"0%, {pct(ini - 0.002, T)} {{ display: none; }} {pct(ini, T)}, 100% {{ display: block; }}"
            else:
                vis = (f"0%, {pct(ini - 0.002, T)} {{ display: none; }} {pct(ini, T)}, {pct(fim - 0.002, T)} "
                       f"{{ display: block; }} {pct(fim, T)}, 100% {{ display: none; }}")
            css.append(f"@keyframes v{i} {{ {vis} }}")
            css.append(f"#c{i} {{ animation: v{i} {T:g}s step-end infinite both; }}")
        svg = svg.replace("<svg ", f'<svg id="c{i}" aria-hidden="true" preserveAspectRatio="xMidYMid meet" ', 1)
        corpo.append(svg)
    ultimo_id = f"c{len(cenas) - 1}"
    css.append(f"""
@media (prefers-reduced-motion: reduce) {{
  .palco path, .palco > svg {{ animation: none !important; }}
  .palco path {{ stroke-dashoffset: 0; }}
  .palco > svg {{ display: none; }}
  #{ultimo_id} {{ display: block; }}
}}""")
    janelas = " · ".join(f"{cam.stem} {ini:g}–{ini + d:g} s" + (f" (escala {e:g})" if abs(e - 1) > 1e-6 else "")
                         for (cam, d, e), ini in zip(cenas, inicios))
    modo = ("de baixo para cima (cada traço sai da ponta de baixo; a frente sobe do chão ao topo)"
            if all(o == "baixo" for o in ordens) else "todos os traços juntos")
    html = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<style>{"".join(c + chr(10) for c in css)}</style>
</head>
<body>
<div class="palco" role="img" aria-label="Cenário em traço de caneta se desenhando">
{chr(10).join(corpo)}
</div>
<p class="legenda">Prévia · {titulo} · cada cena desenha em 3 s, {modo}, e fica parada até o fim da
janela · laço de {T:g} s · {janelas}</p>
</body>
</html>
"""
    return html, inicios


FPS_JS = """(ms) => new Promise(res => { let n = 0; const t0 = performance.now();
  function f(t) { n++; if (t - t0 < ms) requestAnimationFrame(f); else res(n / ((t - t0) / 1000)); }
  requestAnimationFrame(f); })"""


def quadros(html_path: Path, pedidos: list[tuple[Path, int, float]], medir: bool) -> float | None:
    from playwright.sync_api import sync_playwright
    url = html_path.resolve().as_uri()
    fps = None
    with sync_playwright() as pw:
        nav = pw.chromium.launch(channel="msedge", headless=True)
        pag = nav.new_page(viewport={"width": PALCO_W, "height": PALCO_H + 60}, device_scale_factor=1)
        pag.goto(url)
        pag.wait_for_timeout(300)
        if medir:
            fps = pag.evaluate(FPS_JS, 3000)
            print(f"quadros por segundo (Edge, primeiros 3 s, desenhando): {fps:.1f}")
        html = html_path.read_text(encoding="utf-8")
        for destino, cena, t in pedidos:
            # a regra de congelar entra na folha ANTES de a animação começar (página nova a cada quadro):
            # só a cena pedida fica no ar, com o relógio dos traços parado em t
            congela = (f".palco > svg {{ animation: none !important; display: none !important; }} "
                       f"#c{cena} {{ display: block !important; }} "
                       f"#c{cena} path {{ animation-play-state: paused !important; "
                       f"animation-delay: -{t:g}s !important; }}")
            pag.set_content(html.replace("</style>", congela + "</style>", 1))
            pag.wait_for_timeout(200)
            destino.parent.mkdir(parents=True, exist_ok=True)
            pag.locator(".palco").screenshot(path=str(destino))
            print(f"quadro {destino.name}: cena {cena}, t = {t:g} s")
        nav.close()
    return fps


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("saida", type=Path)
    a.add_argument("--cena", action="append", required=True, help="SVG:janela_em_s[:escala]")
    a.add_argument("--quadro", action="append", default=[], help="DESTINO.png:indice_da_cena:segundos")
    a.add_argument("--titulo", default="Traço se desenhando")
    a.add_argument("--medir", action="store_true")
    p = a.parse_args(argv)
    cenas = []
    for c in p.cena:
        m = re.match(r"^(.*\.svg):([\d.]+)(?::([\d.]+))?$", c, re.I)
        if not m:
            raise SystemExit(f"--cena inválida: {c}")
        cenas.append((Path(m.group(1)), float(m.group(2)), float(m.group(3) or 1)))
    html, _ = montar(cenas, p.titulo)
    p.saida.write_text(html, encoding="utf-8")
    print(f"{p.saida.name}: {p.saida.stat().st_size / 1e6:.2f} MB, laço de {sum(d for _, d, _ in cenas):g} s")
    pedidos = []
    for q in p.quadro:
        dest, cena, t = q.rsplit(":", 2)
        pedidos.append((Path(dest), int(cena), float(t)))
    if pedidos or p.medir:
        return quadros(p.saida, pedidos, p.medir)
    return None


if __name__ == "__main__":
    main()

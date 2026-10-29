#!/usr/bin/env python
"""Protótipo HTML local da capa v2 do painel Criticidade de Obras (1920x1080, autocontido) — só para o Alisson ver.

Fiel ao Figma v2 (FjBWDk5odF9HaZ2pwhGosl, seção "Capa · v2 · proposta" 467:1504; base "Capa · base v2" 467:1542).
Não toca no PBIP nem nos geradores compartilhados: lê os SVGs de ..\\animacao\\, o logo de assets\\logos\\ e a Barlow
de mockup\\fonts\\, e grava capa-v2.html nesta pasta.

    python -I montar_capa_v2.py                       # grava capa-v2.html
    python -I montar_capa_v2.py --capturas            # + capturas 1920x1080 em pbi\\qa\\capa\\prototipo\\
    python -I montar_capa_v2.py --medir               # + quadros por segundo no Edge (Playwright, headless)

    # versão com o filme em MP4 (o mais perto do HTML Content): grava capa-v2-video.html; a saída padrão não muda
    python -I montar_capa_v2.py --video ../remotion/renders/capa-filme-2560x854-60fps.mp4
    python -I montar_capa_v2.py --video ../remotion/renders/capa-filme-2560x854-60fps.mp4 --capturas --medir
        # prova no Edge headless com o vídeo tocando (servidor local com Range): capturas, defasagem número × take,
        # quadros por segundo, emenda do laço, continuidade, src inválido, movimento reduzido e autoplay recusado,
        # comparadas com as do protótipo SVG; tudo em pbi\\qa\\capa\\prototipo-video\\ (medicoes.json)

Arquitetura (a mesma do HTML Content do painel de referência, para o passo do PBIP):
  - o FILME é um único elemento (.filme, 1920x640) — aqui, os 6 SVGs de traço animados por CSS (técnica do
    montar_preview.py: laço de 33 s, takes de 5 s e final de 8 s, cada cena desenha de baixo para cima em ~3 s);
    em produção ele vira <video class="filme" autoplay muted loop playsinline> com o MP4 do laço;
  - tudo o que é HTML por cima (régua, recortes, números) segue UMA linha do tempo de 33 s com animation-delay
    var(--tm). No protótipo --tm = 0 (tempo zero = carregamento da página); na versão MP4 (--video) o JS crava cada
    animação no mediaTime do quadro do vídeo a cada 'playing'/'seeked' (JS_SINC_VIDEO; --tm só segura o zero);
  - os números vêm de um bloco de dados (JSON) no topo do HTML — o que a DAX vai injetar —; o JS monta o HTML
    (em produção, a própria DAX emite o mesmo HTML, com os 25 quadros do odômetro em aritmética inteira);
  - toda medida em px do palco vira calc(var(--u)*N), como no painel de referência: o palco escala com o iframe do visual.
"""
from __future__ import annotations

import argparse
import base64
import json
import re
from pathlib import Path

AQUI = Path(__file__).resolve().parent              # pbi\spec\capa\prototipo
CAPA = AQUI.parent                                  # pbi\spec\capa
ANIM = CAPA / "animacao"
PBI = AQUI.parents[2]                               # pbi
REPO = PBI.parent                                   # criticidade-obras-bi
QA = PBI / "qa" / "capa" / "prototipo"
FONTES = REPO / "mockup" / "fonts"
LOGO = REPO / "assets" / "logos" / "vizu-dados-icone.svg"        # só o ícone "VD" (viewBox justo no contorno)
SAIDA = AQUI / "capa-v2.html"
# versão com o filme em MP4 (--video): o .filme vira <video>, com caminhos RELATIVOS ao HTML (nada embutido)
SAIDA_VIDEO = AQUI / "capa-v2-video.html"
QA_VIDEO = PBI / "qa" / "capa" / "prototipo-video"
POSTER_PADRAO = "capa-filme-poster.webp"            # na pasta do MP4 (último quadro = cena final desenhada)
ESPERA_MS = 5000                                    # sem tocar até aqui: pôster com os 5 números

W, H, FAIXA = 1920, 1080, 640
T = 33.0                                            # laço do filme (s)
EASE_TRACO = "cubic-bezier(.4,.05,.55,1)"           # o mesmo do montar_preview.py
EASE_ENTRA = "cubic-bezier(.2,.7,.2,1)"
OCULTO = "1.001"
EPS_TRACO = 0.002                                   # s: troca de visibilidade/tracejado nas pontas do crescimento
ESPERA = f"visibility:hidden;stroke-dasharray:1 2;stroke-dashoffset:{OCULTO}"
CRESCE = "visibility:visible;stroke-dasharray:1 2;stroke-dashoffset"
PRONTO = "visibility:visible;stroke-dasharray:none;stroke-dashoffset:0"
EPS = 0.002                                         # corte "de uma vez" (como o montar_preview)

# Takes: (svg, início, janela, x, y, escala) — posição e escala da arte no palco de 1920×640. Cenas de Natal (Codex CLI,
# vetorizadas por animacao/processar_cena.py), aprovadas em 28/10/2026; o filme do Remotion (../remotion/src/cenas.ts)
# repete esta lista. Take 3 a 0,97 em (50, 13): a grua fica longe do texto do mês, com o chão no mesmo y ~420.
CENAS = [
    ("take1-obras.svg", 0, 5, 0, 0, 1.0),
    ("take2-resultado.svg", 5, 5, 0, 0, 1.0),
    ("take3-fisico.svg", 10, 5, 50, 13, 0.97),
    ("take4-desembolso.svg", 15, 5, 0, 0, 1.0),
    ("take5-sem-estoque.svg", 20, 5, 0, 0, 1.0),
    ("final-natal.svg", 25, 8, 0, 0, 1.0),
]
# recorte branco liso atrás da identidade e da régua, por take (Figma: 474:2390 … 474:2400; x 66, y 18)
RECORTE_ID = [(456, 98), (468, 98), (468, 98), (468, 92), (450, 98), (468, 98)]
REGUA = ["01 · Obras", "02 · Resultado", "03 · Físico", "04 · Desembolso", "05 · Sem estoque", "06 · Final"]

# Linha de números (Figma 471:2389 … 471:2434): x do bloco; o recorte branco é o próprio bloco com 12/14 px de folga
# (Figma: recorte = bloco + 28 de largura, 135 de altura, topo 469; pé do bloco em 592)
NUM_X = [80, 555, 980, 1264, 1595]
NUM_TOPO = 481
# Ritmo dos números (s): no take k o número entra em 5k + 3 (sobe 0,5 s, conta 1,0 s) e sai com o take (5k + 5);
# na cena final os 5 entram escalonados de 26 a 28 s (o último termina de contar em 29 s) e ficam até 33 s.
ENTRA, SOBE, CONTA = 3.0, 0.5, 1.0
FINAL = [26.0, 26.5, 27.0, 27.5, 28.0]
PASSOS = 24
LH_NUM = 60                                         # linha do algarismo (px): o odômetro anda 60 px por quadro

# Valores de exemplo de set/26 (dados fictícios de Natal, somados do gabarito dados/_gabarito/), como a DAX vai injetar:
# textos já formatados em pt-BR. Em produção cada campo vem de uma medida (capa_medidas.py).
DADOS = {
    "_doc": ("Bloco de dados de exemplo do protótipo (set/26, dados fictícios). Em produção cada campo vem de uma "
             "medida (pbi/spec/capa/prototipo/NOTAS-IMPLEMENTACAO.md); o resto da capa é desenho fixo."),
    "mes": "setembro de 2026",
    "indicadores": [
        {"id": "obras", "rotulo": "Obras em andamento", "valor": "7", "negativo": False,
         "status": {"criticas": 2, "atencao": 1, "estaveis": 4},
         "apoio": [["R$ 203,4 mi em orçamento", False]]},
        {"id": "resultado", "rotulo": "Resultado da carteira", "valor": "\u2212R$ 1,89 mi", "negativo": True,
         "apoio": [["\u22120,93%", True], [" do orçamento", False]]},
        {"id": "fisico", "rotulo": "Físico acumulado", "valor": "63,4%", "negativo": False,
         "apoio": [["68,5% previsto · ", False], ["\u22125,1 p.p.", True]]},
        {"id": "desembolso", "rotulo": "Desembolso do mês", "valor": "R$ 10,02 mi", "negativo": False,
         "apoio": [["R$ 9,77 mi previsto", False]]},
        {"id": "sem_estoque", "rotulo": "Resultado sem estoque", "valor": "\u2212R$ 4,86 mi", "negativo": True,
         "apoio": [["R$ 2,97 mi pagos e ainda não aplicados", False]]},
    ],
}

# Identidade: o ícone "VD" da Vizu na altura do fio vertical (y 34–78), largura pela proporção do viewBox
# (809,94 × 364,219); o fio e o bloco de texto ao lado guardam o respiro de antes (12 px do logo ao fio, 12 do fio ao
# texto). A régua segue alinhada ao texto.
LOGO_X, LOGO_Y, LOGO_H = 80, 34, 44
LOGO_W = round(LOGO_H * 809.94 / 364.219, 2)                    # 97,85
FIO_X = 190                                         # ≈ 80 + 97,85 + 12
TEXTO_X = FIO_X + 12                                # kicker, mês de referência e régua

# Cartões (Figma 467:1567 … 467:1570; componente 467:1527): título Barlow 23/28. A borda de 1 px é sombra interna (não
# desloca nada): posições medidas da borda de fora, como no componente (nome 72,19; pergunta 24,58; selo 24,15; Abrir
# no canto de baixo à direita, 92 × 34). Cinco cartões (as cinco telas) na faixa que os quatro ocupavam (x 96–1824), com
# os mesmos 24 px entre eles: 326,4 de largura cada. A pergunta cai de Segoe UI 19/24 para 18/23 para caber em duas
# linhas na largura nova (a mais longa, a do Canteiro, tem 264 px na linha mais cheia de 278,4)
CARTOES = [
    ("Visão geral", "Quais obras pedem atenção neste mês, e por quê?"),
    ("Análise crítica", "Por que a obra tem essa nota?"),
    ("Avanço físico", "A obra está no ritmo do que foi previsto?"),
    ("Resultado no tempo", "Está piorando? Gastou fora do previsto no mês e justificou?"),
    ("Canteiro", "Está seguro, faz certo da primeira vez e recebe material no prazo?"),
]
CARTAO_X, CARTAO_Y, CARTAO_W, CARTAO_H = [96, 446.4, 796.8, 1147.2, 1497.6], 836, 326.4, 168
CTA = (1556, 681, 268, 60)

# Ícones das páginas (Figma 467:1512, 467:1517, 467:1522, 467:1526; traço creme 1,90 no selo preto de 36 px):
# caminhos exportados do Figma, já deslocados para a caixa de 21 × 21 do ícone (inset do grupo − folga do traço)
ICONES = [
    (1.383, 1.383, "M7.3675 0.950833H0.950833V7.3675H7.3675V0.950833Z M17.2842 0.950833H10.8675V7.3675H17.2842V0.950833Z"
                   " M7.3675 10.8675H0.950833V17.2842H7.3675V10.8675Z M17.2842 10.8675H10.8675V17.2842H17.2842V10.8675Z"),
    (2.549, 0.799, "M14.9508 0.950833H0.950833V18.4508H14.9508V0.950833Z M4.45083 6.20083H11.4508M4.45083 9.70083H11.4508"
                   "M4.45083 13.2008H9.1175"),
    (2.333, 2.581, "M7.94729e-08 16.0854H16.3333 M0.583333 14.3354C5.83333 13.7521 7 3.25206 15.75 0.918728"),
    (2.333, 4.667, "M0 14H16.3333M2.91667 10.5V4.66667M8.16667 10.5V0M13.4167 10.5V7"),
    # Canteiro: capacete de obra de linha (aba de 17,5, casco em meia-volta de raio 7 e a crista em dois traços), no
    # mesmo traço dos outros quatro
    (1.75, 5.833, "M0 9.917H17.5M1.75 9.917V7A7 7 0 0 1 15.75 7V9.917M7 0.222V5.833M10.5 0.222V5.833"),
]
SETA_CTA = ("<svg class='sc' viewBox='0 0 20 20' aria-hidden='true' focusable='false'><path d='M3.125 10H16.25M11.25 "
            "4.375L16.875 10L11.25 15.625'/></svg>")
SETA_ABRIR = ("<svg class='sa' viewBox='0 0 16 16' aria-hidden='true' focusable='false'><path d='M2.5 8H13M9 3.5L13.5 "
              "8L9 12.5'/></svg>")


# ------------------------------------------------------------------------------------------------------------- util
def pct(t: float) -> str:
    return f"{100.0 * t / T:.4f}".rstrip("0").rstrip(".") + "%"


def pct_local(t: float, dur: float) -> str:
    return f"{100.0 * t / dur:.4f}".rstrip("0").rstrip(".") + "%"


_PX = re.compile(r"(?<![\w.])(-?(?:\d*\.\d+|\d+))px\b")


def U(css: str) -> str:
    """Toda medida em px do palco vira calc(var(--u)*N) — o palco de 1920×1080 escala com o iframe (como no painel de referência)."""
    return _PX.sub(lambda m: "0" if float(m.group(1)) == 0 else f"calc(var(--u)*{m.group(1)})", css)


def ler_cena(caminho: Path) -> tuple[str, list[tuple[float, float]]]:
    svg = caminho.read_text(encoding="utf-8")
    svg = re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", svg)
    m = re.search(r'\sdata-tempos="([^"]+)"', svg)
    if not m:
        raise SystemExit(f"{caminho}: SVG sem data-tempos (gere com vetorizar_traco.py)")
    tempos = [tuple(float(x) for x in par.split(",")) for par in m.group(1).split(";")]
    svg = svg.replace(m.group(0), "", 1)
    svg = re.sub(r'\s(?:width|height)="\d+"', "", svg[:400], count=2) + svg[400:]
    return (agrupar_por_classe(svg) if AGRUPAR else svg), tempos


AGRUPAR = True                                      # animação por grupo de classe (False: por <path>)


def ALVO() -> str:
    return "g[class]" if AGRUPAR else "path"


def agrupar_por_classe(svg: str) -> str:
    """Reagrupa os traços: um <g class="kN"> por classe de tempo (≈ 200 por cena), com os grupos de espessura dentro.
    A animação passa do <path> (4–8 mil por cena) para o grupo, e o stroke-dashoffset — propriedade herdada — desce
    para os traços: o mesmo desenho, quadro a quadro, com ~40× menos animações (medido: a cena final de 12–15 para
    ~35 quadros/s). A ordem de pintura muda, mas todo traço é da mesma tinta preta opaca."""
    cab = re.match(r"<svg[^>]*>", svg).group(0)
    por: dict[str, dict[str, list[str]]] = {}
    for larg, corpo in re.findall(r'<g stroke-width="([^"]+)">(.*?)</g>', svg, flags=re.S):
        for pth in re.findall(r"<path [^>]*/>", corpo):
            c = re.search(r'\sclass="(k\d+)"', pth)
            por.setdefault(c.group(1), {}).setdefault(larg, []).append(pth.replace(c.group(0), "", 1))
    n_antes, n_depois = svg.count("<path"), sum(len(v) for g in por.values() for v in g.values())
    if n_antes != n_depois:
        raise SystemExit(f"agrupar_por_classe: {n_antes} traços no SVG e {n_depois} reagrupados")
    grupos = []
    for c in sorted(por, key=lambda x: int(x[1:])):
        grupos.append(f'<g class="{c}">' + "".join(f'<g stroke-width="{w}">' + "".join(v) + "</g>"
                                                  for w, v in por[c].items()) + "</g>")
    return cab + "\n" + "\n".join(grupos) + "\n</svg>"


def ler_panoramica() -> str:
    svg = (ANIM / "panoramica-base.svg").read_text(encoding="utf-8")
    svg = re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", svg)
    svg = re.sub(r'\sdata-tempos="[^"]*"', "", svg)
    svg = re.sub(r'\s(?:data-ordem|class)="[^"]*"', "", svg)       # estática: sem classes de animação
    svg = re.sub(r'\spathLength="[^"]*"', "", svg)
    svg = re.sub(r'\s(?:width|height)="\d+"', "", svg[:300], count=2) + svg[300:]
    return svg.replace("<svg ", "<svg class='pano' aria-hidden='true' focusable='false' "
                                "preserveAspectRatio='none' ", 1)


def ler_logo() -> str:
    svg = LOGO.read_text(encoding="utf-8")
    svg = re.sub(r"<defs>.*?</defs>", "", svg, flags=re.S)
    svg = svg.replace(' clip-path="url(#clip0_1_3)"', "")
    svg = re.sub(r'\s(?:width|height)="\d+"', "", svg[:200], count=2) + svg[200:]
    svg = re.sub(r'\sid="[^"]*"', "", svg)
    return svg.replace("<svg ", "<svg aria-hidden='true' focusable='false' ", 1)


def fontes() -> str:
    regras = []
    for peso in (400, 600, 700):
        b64 = base64.b64encode((FONTES / f"barlow-{peso}.woff2").read_bytes()).decode("ascii")
        regras.append("@font-face{font-family:'Barlow U';font-style:normal;font-weight:%d;font-display:block;"
                      "src:url(data:font/woff2;base64,%s) format('woff2')}" % (peso, b64))
    return "\n".join(regras)


# ------------------------------------------------------------------------------------------------------- folha (CSS)
def css_filme(tempos_por_cena: list[list[tuple[float, float]]]) -> str:
    r = [
        # as cenas ficam display:block na base e a animação v{i} as liga e desliga (um elemento display:none na base
        # nunca começa a animação que o ligaria); os traços repousam desenhados (dashoffset 0). Sem movimento, a
        # folha de movimento reduzido deixa só a cena final (o quadro do PDF)
        ".filme{position:absolute;left:0;top:0;width:1920px;height:640px;overflow:hidden;background:#FFFFFF;"
        "z-index:1}",
        ".filme>svg{position:absolute;left:0;top:0;width:1920px;height:640px;display:block;transform-origin:0 0;"
        "overflow:visible}",
        # cada grupo de classe anima UMA vez (duração = fim do desenho da cena, ~3 s) e para: a cena parada não custa
        # nada. A repetição vem do display — ao voltar ao ar a cena recomeça do zero (o montar_preview usava
        # 'infinite' com a janela inteira). O dashoffset mora no grupo e desce por herança: o <path> não pode
        # declarar stroke-dashoffset, senão corta a herança
        # repouso = traço inteiro e SEM tracejado (o tracejado só existe enquanto o traço cresce: um traço pronto com
        # dasharray ainda passa pelo cálculo de tracejado a cada rasterização); o traço que ainda não começou fica
        # invisível (não é rasterizado). visibility, dasharray e dashoffset são herdados no SVG
        f".filme {ALVO()}{{stroke-dashoffset:0;stroke-dasharray:none;animation-iteration-count:1;"
        f"animation-timing-function:{EASE_TRACO};animation-fill-mode:both}}",
        # o filme é a única camada que repinta: contida, para não sujar a base nem os números
        ".filme{contain:strict}",
    ]
    for i, ((_, ini, dur, x, y, esc), tempos) in enumerate(zip(CENAS, tempos_por_cena)):
        tr = []
        if x or y:
            tr.append(f"translate({x}px,{y}px)")
        if abs(esc - 1) > 1e-9:
            tr.append(f"scale({esc:.6f})")
        if tr:
            r.append(f"#c{i}{{transform:{' '.join(tr)}}}")
        desenho = max(a + b for a, b in tempos)           # ~2,8–3,0 s
        r.append(f"#c{i} {ALVO()}{{animation-duration:{desenho:g}s}}")
        for k, (atraso, du) in enumerate(tempos):
            a_, b_ = atraso, atraso + du
            r.append(f"@keyframes s{i}k{k}{{0%,{pct_local(a_, desenho)}{{{ESPERA}}}"
                     f"{pct_local(a_ + EPS_TRACO, desenho)}{{{CRESCE}:{OCULTO}}}"
                     f"{pct_local(b_, desenho)}{{{CRESCE}:0}}"
                     f"{pct_local(b_ + EPS_TRACO, desenho)},100%{{{PRONTO}}}}}"
                     f"#c{i} {'g' if AGRUPAR else 'path'}.k{k}{{animation-name:s{i}k{k}}}")
        fim = ini + dur
        if ini == 0:
            vis = f"0%,{pct(fim - EPS)}{{display:block}}{pct(fim)},100%{{display:none}}"
        elif abs(fim - T) < 1e-9:
            vis = f"0%,{pct(ini - EPS)}{{display:none}}{pct(ini)},100%{{display:block}}"
        else:
            vis = (f"0%,{pct(ini - EPS)}{{display:none}}{pct(ini)},{pct(fim - EPS)}{{display:block}}"
                   f"{pct(fim)},100%{{display:none}}")
        r.append(f"@keyframes v{i}{{{vis}}}#c{i}{{animation:v{i} {T:g}s step-end infinite both;"
                 "animation-delay:var(--tm,0s)}")
    return "\n".join(r)


def css_palco() -> str:
    """Folha do palco em px (U() converte para calc(var(--u)*N)). Repouso de toda camada = a cena final."""
    return f"""
/* reset só nos elementos HTML: os 33 mil traços do filme não passam por regra universal (cada quadro do desenho
   recalcula o estilo de milhares deles) */
.uc,.uc :where(div,section,p,h1,h2,span,strong,i,o-d,o-v,o-w,o-t){{box-sizing:border-box;margin:0;padding:0}}
.uc{{--u:min(calc(100vw / 1920),calc(100vh / 1080));position:fixed;inset:0;overflow:hidden;background:#F7F4EE;
  font-family:'Segoe UI',system-ui,sans-serif;color:#0B0B0C;-webkit-font-smoothing:antialiased;
  text-rendering:optimizeLegibility;font-synthesis:none}}
.uc .st{{position:absolute;left:50%;top:50%;width:1920px;height:1080px;transform:translate(-50%,-50%);
  overflow:hidden;background:#F7F4EE}}
.uc .b{{font-family:'Barlow U','Barlow','Segoe UI',sans-serif}}

/* faixa do filme (0–640, branca) e a divisa: fio de 1 px #E1E1E1 na borda de baixo da faixa (Figma: traço
   interno do 467:1546, linha 639) */
.uc .fx{{position:absolute;left:0;top:0;width:1920px;height:640px;overflow:hidden;background:#FFFFFF;
  isolation:isolate}}
.uc .fio{{position:absolute;left:0;top:639px;width:1920px;height:1px;background:#E1E1E1;z-index:5}}

/* identidade (Figma 467:1547 … 467:1587) e o recorte branco liso atrás dela, com a largura de cada take */
.uc .rid{{position:absolute;left:66px;top:18px;width:468px;height:98px;background:#FFFFFF;z-index:2;
  animation:rid {T:g}s step-end infinite both;animation-delay:var(--tm,0s)}}
.uc .logo{{position:absolute;left:{LOGO_X}px;top:{LOGO_Y}px;width:{LOGO_W}px;height:{LOGO_H}px;z-index:3}}
.uc .logo svg{{display:block;width:{LOGO_W}px;height:{LOGO_H}px}}
.uc .dv{{position:absolute;left:{FIO_X}px;top:34px;width:1px;height:44px;background:#3B3B3F;opacity:.35;z-index:3}}
.uc .kk{{position:absolute;left:{TEXTO_X}px;top:36px;font-size:12px;line-height:15px;font-weight:600;letter-spacing:1.2px;
  text-transform:uppercase;color:#3B3B3F;white-space:nowrap;z-index:3}}
.uc .ms{{position:absolute;left:{TEXTO_X}px;top:56px;font-size:19px;line-height:normal;font-weight:400;color:#3B3B3F;
  white-space:nowrap;z-index:3}}
.uc .ms strong{{font-weight:600;color:#0B0B0C}}
.uc .rg{{position:absolute;left:{TEXTO_X}px;top:92px;height:16px;display:flex;align-items:center;gap:12px;z-index:3}}
.uc .ps{{display:flex;align-items:center;gap:4px;height:3px}}
.uc .ps i{{display:block;width:22px;height:2px;background:#3B3B3F;opacity:.3;
  animation-duration:{T:g}s;animation-timing-function:step-end;animation-iteration-count:infinite;
  animation-fill-mode:both;animation-delay:var(--tm,0s)}}
.uc .ps i.p5{{height:3px;background:#0B0B0C;opacity:1}}
.uc .rl{{display:grid;font-size:13px;line-height:16px;font-weight:600;color:#0B0B0C;white-space:nowrap}}
.uc .rl span{{grid-area:1/1;opacity:0;animation-duration:{T:g}s;animation-timing-function:step-end;
  animation-iteration-count:infinite;animation-fill-mode:both;animation-delay:var(--tm,0s)}}
.uc .rl span.l5{{opacity:1}}

/* linha de números: o recorte branco liso é o próprio bloco (12/14 px de folga, como no Figma) */
.uc .nm{{position:absolute;top:469px;padding:12px 14px;background:#FFFFFF;z-index:3;display:flex;
  flex-direction:column;align-items:flex-start;gap:6px;white-space:nowrap;
  animation-duration:{T:g}s;animation-iteration-count:infinite;animation-fill-mode:both;
  animation-delay:var(--tm,0s);animation-timing-function:linear}}
.uc .nm .ro{{font-size:17px;line-height:20px;font-weight:600;color:#0B0B0C}}
.uc .nm .vl{{display:flex;align-items:center;gap:16px;height:60px}}
.uc .nm .v{{font-size:60px;line-height:60px;font-weight:600;color:#0B0B0C;white-space:nowrap}}
.uc .nm .v .un{{font-size:36px;line-height:0}}
.uc .nm .v.ng{{color:#C43737}}
.uc .nm .ap{{font-family:'Segoe UI',system-ui,sans-serif;font-size:14px;line-height:19px;color:#3B3B3F}}
.uc .nm .ap .ng{{color:#C43737}}
/* chips de status a 72 % (Figma 471:2450: 10,8 px, folga 5,04 × 8,64, marca 6,48, raio 2,88) */
.uc .nm .cs{{display:flex;align-items:flex-start;gap:5.76px}}
.uc .nm .ch{{display:flex;align-items:center;gap:5.76px;padding:5.04px 8.64px;border-radius:2.88px;
  font-size:10.8px;line-height:12.96px;font-weight:600;letter-spacing:.864px;text-transform:uppercase;
  color:#FFFFFF;white-space:nowrap}}
.uc .nm .ch i{{display:block;width:6.48px;height:6.48px;background:#FFFFFF}}
.uc .nm .ch.c2{{background:#C43737}}.uc .nm .ch.c1{{background:#C9821F}}
.uc .nm .ch.c0{{background:#A9CDB9;color:#1E5C43}}.uc .nm .ch.c0 i{{background:#1E5C43}}

/* odômetro (o do painel: texto final <o-v> no fluxo, tira <o-t> por cima só durante a contagem). Cada quadro é o
   valor INTEIRO ("−R$ 208 mil"), como no painel de referência: a tira cresce para a direita, alinhada à esquerda do bloco, e nunca
   pisa no prefixo. A janela <o-w> recorta a tira na linha de 60 (a vírgula da Barlow desce 5 px abaixo da base, em 59).
   O transform FINAL fica no estilo base: sem animação aparece o valor certo, nunca zero. */
.uc o-d{{position:relative;display:inline-block;vertical-align:top;height:60px}}
.uc o-v{{opacity:1}}
.uc o-w{{position:absolute;left:0;top:0;height:60px;overflow:hidden;opacity:0;pointer-events:none}}
.uc o-t{{display:block;white-space:pre;text-align:left;line-height:60px;font-variant-numeric:tabular-nums;
  transform:translateY(-1440px)}}
/* algarismos tabulares só enquanto conta (o sufixo não treme); os dois últimos quadros já vêm proporcionais, como o
   texto final e o Figma (o "1" da Barlow é estreito): a troca acontece no meio do giro, nunca no repouso */
.uc o-t .pr{{font-variant-numeric:normal}}
.uc o-v,.uc o-w,.uc o-t{{animation-duration:{T:g}s;animation-iteration-count:infinite;animation-fill-mode:both;
  animation-delay:var(--tm,0s)}}
.uc o-v,.uc o-w{{animation-timing-function:step-end}}

/* base offwhite (640–1080), igual ao Figma v2 */
.uc .bs{{position:absolute;left:0;top:640px;width:1920px;height:440px;overflow:hidden;background:#F7F4EE;
  isolation:isolate}}
/* panorâmica de Natal em traço (1916×821 → 1920×822,7 em x 0, y 436; a faixa branca cobre até 640), multiply a .12 e a
   máscara da ponta esquerda: 7 % da força de x 0 a 480, de volta a 100 % em x 630 (Figma 470:2401) */
.uc .pano{{position:absolute;left:0;top:-204px;width:1920px;height:822.714px;opacity:.12;mix-blend-mode:multiply;
  -webkit-mask-image:linear-gradient(90deg,rgba(0,0,0,.07) 0,rgba(0,0,0,.07) 480px,#000 630px);
  mask-image:linear-gradient(90deg,rgba(0,0,0,.07) 0,rgba(0,0,0,.07) 480px,#000 630px)}}
.uc .ti{{position:absolute;left:96px;top:672px;font-size:40px;line-height:normal;font-weight:400;color:#3B3B3F;
  white-space:nowrap}}
.uc .ti strong{{font-size:64px;font-weight:700;color:#0B0B0C}}
.uc .su{{position:absolute;left:96px;top:762px;font-size:24px;line-height:normal;font-weight:400;color:#3B3B3F;
  white-space:nowrap}}
.uc .ct{{position:absolute;left:{CTA[0]}px;top:{CTA[1]}px;width:{CTA[2]}px;height:{CTA[3]}px;border-radius:30px;
  background:#0B0B0C;display:flex;align-items:center;justify-content:center;gap:12px;font-size:21px;
  line-height:normal;font-weight:600;color:#FFFFFF;white-space:nowrap;box-shadow:0 8px 24px rgba(11,11,12,.18)}}
.uc .ct .sc{{display:block;width:20px;height:20px;fill:none;stroke:#FFFFFF;stroke-width:2.25;stroke-linecap:round;
  stroke-linejoin:round}}
.uc .ca{{position:absolute;top:{CARTAO_Y}px;width:{CARTAO_W}px;height:{CARTAO_H}px;border-radius:16px;
  background:#FFFFFF;box-shadow:inset 0 0 0 1px #E1E1E1,0 8px 24px rgba(11,11,12,.18)}}
{"".join(f".uc .ca.k{i}{{left:{x}px}}" for i, x in enumerate(CARTAO_X))}
.uc .ca .se{{position:absolute;left:24px;top:15px;width:36px;height:36px;border-radius:9px;background:#0B0B0C}}
.uc .ca .se svg{{position:absolute;left:7.5px;top:7.5px;width:21px;height:21px;overflow:visible;fill:none;
  stroke:#E9E0CF;stroke-width:1.90167}}
.uc .ca h2{{position:absolute;left:72px;top:19px;font-size:23px;line-height:28px;font-weight:600;color:#0B0B0C;
  white-space:nowrap}}
.uc .ca p{{position:absolute;left:24px;top:58px;width:{CARTAO_W - 48:g}px;font-size:18px;line-height:23px;color:#3B3B3F}}
.uc .ca .ab{{position:absolute;right:24px;bottom:18px;display:flex;align-items:center;gap:8px;
  padding:8px 16px 8px 18px;border-radius:18px;background:#0B0B0C;font-size:15px;line-height:normal;
  font-weight:600;color:#FFFFFF;white-space:nowrap}}
.uc .ca .sa{{display:block;width:16px;height:16px;fill:none;stroke:#FFFFFF;stroke-width:1.8;stroke-linecap:round;
  stroke-linejoin:round}}
.uc .ft{{position:absolute;left:96px;top:1036px;font-size:13px;line-height:normal;font-weight:400;color:#6B6B70;
  white-space:nowrap}}
"""


def css_tempo() -> str:
    """Linha do tempo única de 33 s (régua, recorte da identidade, números), relativa a var(--tm)."""
    r = []
    # recorte da identidade: largura e altura de cada take
    passos = [f"{pct(5 * k if k < 5 else 25)}{{width:{w}px;height:{h}px}}" for k, (w, h) in enumerate(RECORTE_ID)]
    r.append("@keyframes rid{" + "".join(passos) + f"100%{{width:{RECORTE_ID[-1][0]}px;"
             f"height:{RECORTE_ID[-1][1]}px}}}}")
    # régua: o tracinho do take vira preto 3 px; o rótulo troca junto
    ativo, inativo = "background:#0B0B0C;height:3px;opacity:1", "background:#3B3B3F;height:2px;opacity:.3"
    for j in range(6):
        a, b = (5 * j, 5 * j + 5) if j < 5 else (25, 33)
        if j == 0:
            kf_p = f"0%{{{ativo}}}{pct(b)},100%{{{inativo}}}"
            kf_l = f"0%{{opacity:1}}{pct(b)},100%{{opacity:0}}"
        elif j == 5:
            kf_p = f"0%{{{inativo}}}{pct(a)},100%{{{ativo}}}"
            kf_l = f"0%{{opacity:0}}{pct(a)},100%{{opacity:1}}"
        else:
            kf_p = f"0%{{{inativo}}}{pct(a)}{{{ativo}}}{pct(b)},100%{{{inativo}}}"
            kf_l = f"0%{{opacity:0}}{pct(a)}{{opacity:1}}{pct(b)},100%{{opacity:0}}"
        r.append(f"@keyframes p{j}{{{kf_p}}}.uc .ps i.p{j}{{animation-name:p{j}}}")
        r.append(f"@keyframes l{j}{{{kf_l}}}.uc .rl span.l{j}{{animation-name:l{j}}}")
    # números
    escondido, visivel = "opacity:0;transform:translateY(8px)", "opacity:1;transform:none"
    for i in range(5):
        a, c, f = 5 * i + ENTRA, 5 * i + 5, FINAL[i]
        r.append(f"@keyframes n{i}{{0%{{{escondido}}}{pct(a)}{{{escondido};animation-timing-function:{EASE_ENTRA}}}"
                 f"{pct(a + SOBE)},{pct(c - EPS)}{{{visivel}}}{pct(c)}{{{escondido}}}"
                 f"{pct(f)}{{{escondido};animation-timing-function:{EASE_ENTRA}}}{pct(f + SOBE)},100%{{{visivel}}}}}"
                 f".uc .nm.n{i}{{left:{NUM_X[i] - 14}px;animation-name:n{i}}}")
        # janela da tira (visível só contando) e o texto final (invisível só contando)
        r.append(f"@keyframes w{i}{{0%{{opacity:0}}{pct(a)}{{opacity:1}}{pct(a + CONTA)}{{opacity:0}}"
                 f"{pct(f)}{{opacity:1}}{pct(f + CONTA)},100%{{opacity:0}}}}"
                 f"@keyframes o{i}{{0%{{opacity:1}}{pct(a)}{{opacity:0}}{pct(a + CONTA)}{{opacity:1}}"
                 f"{pct(f)}{{opacity:0}}{pct(f + CONTA)},100%{{opacity:1}}}}"
                 f".uc .n{i} o-w{{animation-name:w{i}}}.uc .n{i} o-v{{animation-name:o{i}}}")
        # tira: parada no quadro 0 até a entrada, 24 passos em CONTA s, parada no último quadro até a final
        top = -PASSOS * LH_NUM
        r.append(f"@keyframes t{i}{{0%{{transform:translateY(0);animation-timing-function:step-end}}"
                 f"{pct(a)}{{transform:translateY(0);animation-timing-function:steps({PASSOS},end)}}"
                 f"{pct(a + CONTA)}{{transform:translateY({top}px);animation-timing-function:step-end}}"
                 f"{pct(f)}{{transform:translateY(0);animation-timing-function:steps({PASSOS},end)}}"
                 f"{pct(f + CONTA)},100%{{transform:translateY({top}px)}}}}"
                 f".uc .n{i} o-t{{animation-name:t{i}}}")
    return "\n".join(r)


CSS_REDUZIDO = """
/* movimento reduzido e impressão: só a cena final parada, com os 5 números (o quadro do PDF) */
@media (prefers-reduced-motion:reduce){
  .uc *,.uc *::before,.uc *::after{animation:none!important;transition:none!important}
  .uc .filme>svg{display:none!important}.uc .filme>svg:last-child{display:block!important}
}
@media print{
  .uc *,.uc *::before,.uc *::after{animation:none!important;transition:none!important}
  .uc .filme>svg{display:none!important}.uc .filme>svg:last-child{display:block!important}
  .uc{position:absolute}
}
/* filme com erro (em produção, o <video>): a capa para no quadro final, com os 5 números */
html.uo-parado .uc *{animation:none!important;transition:none!important}
html.uo-parado .uc .filme>svg{display:none!important}html.uo-parado .uc .filme>svg:last-child{display:block!important}
"""


# ------------------------------------------------------------------------------------------ filme em MP4 (--video)
def css_filme_video() -> str:
    """O <video> ocupa a faixa de 1920×640 (passa por U()). A fonte tem 2560×854 (= 1920×640 × 4/3, com 853,33
    arredondado para 854, a linha a mais é branca embaixo): object-fit cover escala por 0,75, dá 1920×640,5, e
    object-position 50% 0 prende o topo; o meio pixel branco de baixo fica fora da faixa."""
    return (".uc .filme{position:absolute;left:0;top:0;width:1920px;height:640px;display:block;object-fit:cover;"
            "object-position:50% 0;z-index:1;pointer-events:none}")


def css_reduzido_video(poster: str) -> str:
    """Estados do filme em MP4. Parado = pôster (a cena final desenhada) como fundo da faixa + os 5 números (o repouso
    de toda a folha), com o mesmo enquadramento do vídeo; o <video> some (opacity, para o autoplay não ser travado
    por visibilidade)."""
    fundo = f".uc .fx{{background:#FFFFFF url('{poster}') 50% 0/cover no-repeat}}"
    return f"""
/* filme em MP4: até o 1º quadro tocar, a faixa fica no papel em branco (o quadro 0 do filme); a linha do tempo
   espera no zero pelo atraso (--tm 1000 s, posto pelo JS), sem pausar as animações */
html.uo-espera .uc .filme{{opacity:0}}
/* movimento reduzido e impressão: o pôster com os 5 números (sem vídeo: o JS também desliga o download) */
@media (prefers-reduced-motion:reduce){{
  .uc *,.uc *::before,.uc *::after{{animation:none!important;transition:none!important}}
  .uc .filme{{opacity:0!important}}{fundo}
}}
@media print{{
  .uc *,.uc *::before,.uc *::after{{animation:none!important;transition:none!important}}
  .uc .filme{{opacity:0!important}}{fundo}
  .uc .fx{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
  .uc{{position:absolute}}
}}
/* vídeo com erro, autoplay recusado ou sem tocar a tempo: a capa para no pôster, com os 5 números */
html.uo-parado .uc *{{animation:none!important;transition:none!important}}
html.uo-parado .uc .filme{{opacity:0!important}}
html.uo-parado {fundo}
"""


def tag_video(video: str, poster: str) -> str:
    return (f'<video class="filme" src="{video}" poster="{poster}" muted autoplay loop playsinline preload="auto" '
            'disablepictureinpicture disableremoteplayback aria-hidden="true"></video>')


def url_relativa(caminho: str) -> str:
    """Caminho relativo (do HTML) como URL: barras normais, sem base64, escapado para atributo e url('…')."""
    from urllib.parse import quote
    c = caminho.replace("\\", "/")
    if re.match(r"^[a-zA-Z]:|^/|^[a-z]+:", c):
        raise SystemExit(f"--video/--poster: use caminho RELATIVO ao HTML (recebi {caminho!r})")
    return quote(c, safe="/._-~")


# ------------------------------------------------------------------------------------------------------------ corpo
COMENTARIO_SVG = "<!-- FILME: elemento único, trocável por <video class=\"filme\" autoplay muted loop playsinline> em produção -->"
COMENTARIO_VIDEO = ("<!-- FILME: o MP4 de 2560×854 (60 q/s, laço de 33 s) mostrado em 1920×640; caminhos relativos, nada "
                    "embutido. A linha do tempo do HTML segue o currentTime do vídeo (JS no fim do corpo) -->")


def corpo_html(cenas_svg: list[str], video: str | None = None) -> str:
    """video: a tag <video class="filme"> pronta (versão MP4); None = o filme em SVG (saída padrão)."""
    regua = ("<div class='rg' aria-hidden='true'><div class='ps'>"
             + "".join(f"<i class='p{j}'></i>" for j in range(6)) + "</div><div class='rl b'>"
             + "".join(f"<span class='l{j}'>{t}</span>" for j, t in enumerate(REGUA)) + "</div></div>")
    filme = video or ("<div class='filme' aria-hidden='true'>\n" + "\n".join(cenas_svg) + "\n</div>")
    cartoes = "".join(
        f"<div class='ca k{i}'><div class='se' aria-hidden='true'><svg viewBox='0 0 21 21' focusable='false'>"
        f"<path transform='translate({dx} {dy})' d='{d}'/></svg></div><h2 class='b'>{t}</h2><p>{q}</p>"
        f"<div class='ab b' aria-hidden='true'>Abrir{SETA_ABRIR}</div></div>"
        for i, ((t, q), (dx, dy, d)) in enumerate(zip(CARTOES, ICONES)))
    numeros = "".join(f"<div class='nm n{i} b' data-ind='{x['id']}'></div>" for i, x in enumerate(DADOS["indicadores"]))
    return f"""<div class="uc" lang="pt-BR">
<div class="st">
<section class="fx" aria-label="Acompanhamento de obras · mês de referência e indicadores principais">
<div class="rid" aria-hidden="true"></div>
<div class="logo" role="img" aria-label="Vizu Dados">{ler_logo()}</div>
<div class="dv" aria-hidden="true"></div>
<p class="kk b">Acompanhamento de obras</p>
<p class="ms b">Mês de referência · <strong data-campo="mes"></strong></p>
{regua}
<div class="ln">{numeros}</div>
{COMENTARIO_VIDEO if video else COMENTARIO_SVG}
{filme}
</section>
<div class="fio" aria-hidden="true"></div>
<section class="bs" aria-label="Entrada do painel">
{ler_panoramica()}
</section>
<h1 class="ti b"><strong>Criticidade de Obras</strong> · Acompanhamento e análise crítica</h1>
<p class="su b">Quais obras pedem atenção neste mês, e por quê.</p>
<div class="ct b" aria-hidden="true">Entrar no painel{SETA_CTA}</div>
{cartoes}
<p class="ft b">Planilhas Análise Crítica de cada obra · tratamento em Power Query · <span data-campo="mes"></span></p>
</div>
</div>"""


# --------------------------------------------------------------------------------------------------------------- JS
def js_texto(video: bool = False) -> str:
    """Números (odômetro) + sincronia. video=False: a sincronia do protótipo SVG (saída padrão, inalterada);
    video=True: a sincronia com o <video class="filme"> (JS_SINC_VIDEO)."""
    fracoes = [round(1000 * (1 - (1 - k / PASSOS) ** 3)) for k in range(PASSOS + 1)]
    numeros = """(function(){
'use strict';
var d=document,R=d.documentElement,W=window;
var dados=JSON.parse(d.getElementById('uo-dados').textContent);
/* odômetro em aritmética inteira (o mesmo do painel e do painel de referência): quadro k = ROUND(T·f_k/1000) na unidade do último
   dígito, f_k = milésimos de 1−(1−k/24)³; o quadro 24 é o próprio texto final */
var F=%(fr)s,N=%(n)d;
function arred(num,den){var q=Math.floor(num/den),r=num-q*den;return q+(2*r>=den?1:0);}
function fmt(x,casas,milhar){var b=Math.pow(10,casas),i=Math.floor(x/b),f=x-i*b;
  var t=milhar?String(i).replace(/\\B(?=(\\d{3})+(?!\\d))/g,'.'):String(i);
  return t+(casas?','+String(f).padStart(casas,'0'):'');}
function quadros(nucleo){var s=nucleo.replace(/[.,]/g,'');if(!/^\\d+$/.test(s)){return null;}
  var t=parseInt(s,10);if(t<2){return null;}var v=nucleo.indexOf(','),casas=v<0?0:nucleo.length-v-1;
  var mil=nucleo.indexOf('.')>=0,q=[];
  for(var k=0;k<=N;k++){q.push(k===N?nucleo:fmt(arred(t*F[k],1000),casas,mil));}return q;}
function el(tag,cls,txt){var e=d.createElement(tag);if(cls){e.className=cls;}if(txt!=null){e.textContent=txt;}return e;}
function plural(n,um,varios){return n+' '+(n===1?um:varios);}
function valor(ind){var p=el('p','v'+(ind.negativo?' ng':''));
  var m=/^(\\D*)(\\d(?:[\\d.,]*\\d)?)(\\D*)$/.exec(ind.valor);
  if(!m){p.textContent=ind.valor;return p;}
  /* prefixo e sufixo (R$, mil, mi, %%) a 36 px; o núcleo a 60 px */
  var poe=function(alvo,num){if(m[1]){alvo.appendChild(el('span','un',m[1]));}alvo.appendChild(d.createTextNode(num));
    if(m[3]){alvo.appendChild(el('span','un',m[3]));}};
  var od=el('o-d'),ov=el('o-v'),q=quadros(m[2]);poe(ov,m[2]);od.appendChild(ov);
  if(q){var w=el('o-w'),t=el('o-t');w.setAttribute('aria-hidden','true');
    q.forEach(function(x,k){var ln=el('span',k>=N-1?'pr':null);poe(ln,x);t.appendChild(ln);
      if(k<N){t.appendChild(d.createTextNode('\\n'));}});
    w.appendChild(t);od.appendChild(w);}
  p.appendChild(od);return p;}
dados.indicadores.forEach(function(ind){
  var c=d.querySelector(".nm[data-ind='"+ind.id+"']");if(!c){return;}
  c.appendChild(el('p','ro',ind.rotulo));
  var vl=el('div','vl');vl.appendChild(valor(ind));
  if(ind.status){var cs=el('div','cs'),s=ind.status;
    [[s.criticas,'c2',plural(s.criticas,'crítica','críticas')],[s.atencao,'c1',s.atencao+' em atenção'],
     [s.estaveis,'c0',plural(s.estaveis,'estável','estáveis')]].forEach(function(x){
      if(x[0]>0){var ch=el('span','ch '+x[1]);ch.appendChild(el('i'));ch.appendChild(d.createTextNode(x[2]));cs.appendChild(ch);}});
    vl.appendChild(cs);}
  c.appendChild(vl);
  var ap=el('p','ap');(ind.apoio||[]).forEach(function(x){ap.appendChild(x[1]?el('span','ng',x[0]):d.createTextNode(x[0]));});
  c.appendChild(ap);});
Array.prototype.forEach.call(d.querySelectorAll("[data-campo='mes']"),function(e){e.textContent=dados.mes;});
""" % {"fr": json.dumps(fracoes), "n": PASSOS}
    if video:
        return numeros + JS_SINC_VIDEO % {"T": f"{T:g}", "espera": ESPERA_MS}
    return numeros + JS_SINC_SVG


JS_SINC_SVG = """/* sincronia com o filme: o tempo zero da linha de 33 s é o carregamento da página (--tm = 0). Quando o .filme for
   um <video>, cada 'playing' e cada volta do laço ('seeked') reescrevem --tm = decorrido − currentTime, com o
   "decorrido" lido do relógio da própria animação (startTime da linha do tempo); vídeo com erro = capa parada no
   quadro final (a mesma folha do movimento reduzido) */
var T0=(W.performance&&performance.now)?performance.now():Date.now();
var decorrido=function(){try{var a=d.getAnimations?d.getAnimations().filter(function(x){return x.animationName==='rid';})[0]:null;
  if(a&&a.startTime!=null&&d.timeline){return (d.timeline.currentTime-a.startTime)/1000;}}catch(x){}
  return (((W.performance&&performance.now)?performance.now():Date.now())-T0)/1000;};
var f=d.querySelector('.filme');
if(f&&f.tagName==='VIDEO'){var sinc=function(){if(!f.isConnected||f.paused){return;}
  R.style.setProperty('--tm',(decorrido()-f.currentTime).toFixed(3)+'s');};
  f.addEventListener('playing',sinc);f.addEventListener('seeked',sinc);
  f.addEventListener('error',function(){R.classList.add('uo-parado');});}
})();"""

# Sincronia com o MP4 (porte da capa do painel de referência: gerar_capa_v3.JS). Formatada com % (T, espera): '%%' = módulo.
JS_SINC_VIDEO = """/* sincronia com o filme em MP4 (<video class="filme">). A linha de 33 s do HTML (régua, recorte da identidade,
   números) é feita de animações CSS de 33 s. A cada 'playing' e 'seeked' (a volta do laço também dispara 'seeked'),
   o JS espera o quadro na tela (requestVideoFrameCallback; sem ele, currentTime) e crava CADA animação da capa no
   mediaTime desse quadro (Web Animations, currentTime). Uma a uma, e não por um atraso comum: as animações que o
   compositor roda (opacidade e transform: números, odômetro, rótulos da régua) ganham o relógio um quadro depois das
   outras (largura do recorte, tracinhos da régua) sempre que começam ou recomeçam, e um --tm único não desfaz essa
   diferença. No quadro seguinte confere todas; a cada 'timeupdate' corrige se alguma passar de meio quadro. Nada é
   pausado: pausar e retomar recria a diferença.
   Estados no <html>: uo-espera (até o 1º quadro tocar: o vídeo some, a faixa fica no papel em branco, que é o quadro
   0, e a linha do tempo fica segura no zero por um atraso enorme, --tm 1000 s); uo-parado (movimento reduzido, erro
   do vídeo, autoplay recusado ou %(espera)d ms sem tocar: pôster com os 5 números; se o vídeo tocar depois, volta).
   Sem JS, --tm 0: o CSS roda sozinho desde a carga.
   Continuidade (painel de referência, __cpT): quando o Power BI recria o HTML (filtro, redimensionar), a janela e o <html>
   sobrevivem; W.__uoT = [currentTime, relógio] e o vídeo novo retoma onde o filme estaria, com a linha do tempo já
   no ponto. */
var f=d.querySelector('video.filme'),uc=d.querySelector('.uc');
if(f&&uc){
var T=%(T)s,Q=1/60,cl=R.classList;
var agora=function(){return (W.performance&&performance.now)?performance.now():Date.now();};
cl.remove('uo-parado','uo-espera');R.style.removeProperty('--tm');clearTimeout(W.__uoEsp);
var vivo=function(){return f.isConnected;};
var parado=function(){if(vivo()){cl.remove('uo-espera');cl.add('uo-parado');}};
var desliga=function(){f.removeAttribute('autoplay');f.setAttribute('preload','none');try{f.pause();}catch(e){}
  f.removeAttribute('src');try{f.load();}catch(e){}};
if((W.matchMedia&&W.matchMedia('(prefers-reduced-motion: reduce)').matches)||f.error){parado();desliga();}
else{
cl.add('uo-espera');R.style.setProperty('--tm','1000s');f.muted=true;f.defaultMuted=true;
var lista=function(){var l=d.getAnimations?d.getAnimations():[],r=[];
  for(var i=0;i<l.length;i++){var e=l[i].effect&&l[i].effect.target;if(l[i].animationName&&e&&uc.contains(e)){r.push(l[i]);}}
  return r;};
var crava=function(mt){R.style.setProperty('--tm','0s');var l=lista();
  for(var i=0;i<l.length;i++){try{l[i].currentTime=mt*1000;}catch(e){}}};
var defasagem=function(mt){var l=lista(),pior=0;for(var i=0;i<l.length;i++){var c=l[i].effect.getComputedTiming();
  if(c.progress==null){continue;}var x=((c.progress*T-mt)%%T+T)%%T;if(x>T/2){x-=T;}if(Math.abs(x)>Math.abs(pior)){pior=x;}}
  return pior;};
var quadro=function(fn){if(f.requestVideoFrameCallback){f.requestVideoFrameCallback(function(n,md){if(vivo()){fn(md.mediaTime);}});}
  else{fn(f.currentTime);}};
var sinc=function(){if(!vivo()||f.paused){return;}quadro(function(mt){if(f.paused){return;}clearTimeout(W.__uoEsp);
  cl.remove('uo-espera','uo-parado');crava(mt);
  quadro(function(m2){if(Math.abs(defasagem(m2))>Q/4){crava(m2);}});});};
f.addEventListener('playing',sinc);f.addEventListener('seeked',sinc);
f.addEventListener('timeupdate',function(){if(!vivo()){return;}W.__uoT=[f.currentTime,agora()];
  if(f.paused||cl.contains('uo-espera')||cl.contains('uo-parado')){return;}
  quadro(function(mt){if(Math.abs(defasagem(mt))>Q/2){crava(mt);}});});
f.addEventListener('error',function(){parado();desliga();});
var c=W.__uoT;
if(c&&c[0]>0){var t0=(c[0]+(agora()-c[1])/1000)%%T;crava(t0);
  var vai=function(){try{f.currentTime=t0;}catch(e){}};
  if(f.readyState>=1){vai();}else{f.addEventListener('loadedmetadata',vai,{once:true});}}
try{var p=f.play();if(p&&p.catch){p.catch(function(x){if(x&&x.name==='NotAllowedError'){parado();}});}}catch(x){}
W.__uoEsp=setTimeout(function(){if(vivo()&&cl.contains('uo-espera')){parado();}},%(espera)d);
}
}
})();"""


# ------------------------------------------------------------------------------------------------------------ montar
def montar(video: str | None = None, poster: str | None = None) -> tuple[str, dict]:
    """video/poster: URLs relativas ao HTML (versão MP4). Sem video: o protótipo SVG de sempre."""
    cenas_svg, tempos = [], []
    if video:
        folha = (U(css_palco()) + "\n" + U(css_filme_video()) + "\n" + U(css_tempo()) + "\n"
                 + css_reduzido_video(poster))
        tag, titulo = tag_video(video, poster), "Capa v2 · Criticidade de Obras · protótipo com o filme em MP4"
    else:
        for i, (nome, *_r) in enumerate(CENAS):
            svg, tp = ler_cena(ANIM / nome)
            cenas_svg.append(svg.replace("<svg ", f'<svg id="c{i}" aria-hidden="true" focusable="false" '
                                                  'preserveAspectRatio="xMidYMid meet" ', 1))
            tempos.append(tp)
        folha = U(css_palco()) + "\n" + U(css_filme(tempos)) + "\n" + U(css_tempo()) + "\n" + CSS_REDUZIDO
        tag, titulo = None, "Capa v2 · Criticidade de Obras · protótipo"
    dados = json.dumps(DADOS, ensure_ascii=False, indent=2)
    html = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<!-- ==== DADOS · o que a DAX vai injetar (set/26) ======================================================== -->
<script type="application/json" id="uo-dados">
{dados}
</script>
<!-- ======================================================================================================== -->
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<style>
:root{{color-scheme:light}}
html,body{{margin:0;height:100%;background:#F7F4EE;overflow:hidden}}
{fontes()}
{folha}
</style>
</head>
<body>
{corpo_html(cenas_svg, tag)}
<script>{js_texto(bool(video))}</script>
</body>
</html>
"""
    info = {"bytes": len(html.encode("utf-8")), "paths_filme": sum(s.count("<path") for s in cenas_svg)}
    return html, info


# ---------------------------------------------------------------------------------------------------- provas locais
def cena_em(t: float) -> tuple[int, float]:
    for i in range(len(CENAS) - 1, -1, -1):
        if t >= CENAS[i][1]:
            return i, t - CENAS[i][1]
    return 0, t


def congela_css(t: float) -> str:
    """Congela a capa no instante t do laço (técnica do montar_preview: paused + animation-delay negativo)."""
    i, tl = cena_em(t)
    return (f".filme>svg{{animation:none!important;display:none!important}}#c{i}{{display:block!important}}"
            f"#c{i} {ALVO()}{{animation-play-state:paused!important;animation-delay:-{tl:g}s!important}}"
            f".uc *{{animation-play-state:paused!important}}"
            f":root{{--tm:-{t:g}s!important}}")


CAPTURAS = [  # (arquivo, t em s) — as 5 pedidas e quatro de apoio (takes 3–5 e a contagem)
    ("capa-v2-t01_5-take1-desenhando.png", 1.5),
    ("capa-v2-t04_5-take1-numero.png", 4.5),
    ("capa-v2-t09_5-take2-numero.png", 9.5),
    ("capa-v2-t31_0-final-5-numeros.png", 31.0),
    ("apoio-t03_5-take1-contando.png", 3.5),
    ("apoio-t14_5-take3-numero.png", 14.5),
    ("apoio-t19_5-take4-numero.png", 19.5),
    ("apoio-t24_5-take5-numero.png", 24.5),
    ("apoio-t27_2-final-entrando.png", 27.2),
]

FPS_JS = """(ms) => new Promise(res => { const ts = []; const t0 = performance.now();
  function f(t) { ts.push(t); if (t - t0 < ms) requestAnimationFrame(f); else {
    const dt = ts.slice(1).map((x, i) => x - ts[i]).sort((a, b) => a - b);
    res({fps: (ts.length - 1) / ((ts[ts.length - 1] - ts[0]) / 1000), p95: dt[Math.floor(dt.length * .95)] || 0,
         max: dt[dt.length - 1] || 0}); } }
  requestAnimationFrame(f); })"""


def provas(html_path: Path, capturas: bool, medir: bool) -> dict:
    from playwright.sync_api import sync_playwright
    out = {}
    html = html_path.read_text(encoding="utf-8")
    with sync_playwright() as pw:
        nav = pw.chromium.launch(channel="msedge", headless=True)
        pag = nav.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        if capturas:
            QA.mkdir(parents=True, exist_ok=True)
            for nome, t in CAPTURAS:
                pag.set_content(html.replace("</style>", congela_css(t) + "</style>", 1))
                pag.evaluate("document.fonts.ready")
                pag.wait_for_timeout(250)
                pag.screenshot(path=str(QA / nome))
                print(f"captura {nome}: t = {t:g} s")
            ctx = nav.new_context(viewport={"width": W, "height": H}, device_scale_factor=1,
                                  reduced_motion="reduce")
            p2 = ctx.new_page()
            p2.goto(html_path.resolve().as_uri())
            p2.evaluate("document.fonts.ready")
            p2.wait_for_timeout(1500)
            p2.screenshot(path=str(QA / "capa-v2-movimento-reduzido.png"))
            print("captura capa-v2-movimento-reduzido.png (prefers-reduced-motion: reduce, 1,5 s depois de abrir)")
            ctx.close()
        if medir:
            p3 = nav.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
            p3.goto(html_path.resolve().as_uri())
            t0 = p3.evaluate("performance.now()")
            janelas = [("take 1 desenhando (0,3–3,0 s)", 0.3, 2.7), ("take 1 número contando (3,0–4,1 s)", 3.0, 1.1),
                       ("take 1 parado (4,1–4,9 s)", 4.1, 0.8),
                       ("take 5 desenhando (20,2–23,0 s)", 20.2, 2.8),
                       ("final desenhando + números (25,2–28,2 s)", 25.2, 3.0),
                       ("final parado (29,5–32,5 s)", 29.5, 3.0)]
            for nome, ini, dur in janelas:
                agora = (p3.evaluate("performance.now()") - t0) / 1000
                if ini > agora:
                    p3.wait_for_timeout(int((ini - agora) * 1000))
                r = p3.evaluate(FPS_JS, int(dur * 1000))
                out[nome] = r
                print(f"{nome}: {r['fps']:.1f} q/s · p95 {r['p95']:.1f} ms · pior {r['max']:.1f} ms")
        nav.close()
    return out


# ------------------------------------------------------------------------------------ provas do filme em MP4 (--video)
CAPTURAS_VIDEO = [  # (arquivo, t pedido em s, captura do protótipo SVG no mesmo t, em pbi\qa\capa\prototipo\)
    ("capa-v2-video-t01_5-take1-desenhando.png", 1.5, "capa-v2-t01_5-take1-desenhando.png"),
    ("capa-v2-video-t04_5-take1-numero.png", 4.5, "capa-v2-t04_5-take1-numero.png"),
    ("capa-v2-video-t09_5-take2-numero.png", 9.5, "capa-v2-t09_5-take2-numero.png"),
    ("capa-v2-video-t31_0-final-5-numeros.png", 31.0, "capa-v2-t31_0-final-5-numeros.png"),
    ("apoio-video-t03_5-take1-contando.png", 3.5, "apoio-t03_5-take1-contando.png"),
    ("apoio-video-t14_5-take3-numero.png", 14.5, "apoio-t14_5-take3-numero.png"),
    ("apoio-video-t19_5-take4-numero.png", 19.5, "apoio-t19_5-take4-numero.png"),
    ("apoio-video-t24_5-take5-numero.png", 24.5, "apoio-t24_5-take5-numero.png"),
    ("apoio-video-t27_2-final-entrando.png", 27.2, "apoio-t27_2-final-entrando.png"),
]
JANELAS_FPS = [("take 1 desenhando (0,3–3,0 s)", 0.3, 3.0), ("take 1 número contando (3,0–4,1 s)", 3.0, 4.1),
               ("take 1 parado (4,1–4,9 s)", 4.1, 4.9), ("take 5 desenhando (20,2–23,0 s)", 20.2, 23.0),
               ("final desenhando + números (25,2–28,2 s)", 25.2, 28.2), ("final parado (29,5–32,5 s)", 29.5, 32.5),
               ("laço inteiro (0–33 s)", 0.0, 33.0)]
QUADRO = 1 / 60

# Instrumentos da prova, injetados depois da carga. rVFC entrega cada quadro novo do vídeo (mediaTime) e roda antes do
# rAF no mesmo quadro da página: o rAF lê o estado já desenhado (opacidade dos 5 números, janela do odômetro, tempo da
# linha do tempo pela própria animação 'n0') ao lado do quadro do vídeo que está na tela.
QA_JS = r"""(() => {
  const d = document, R = d.documentElement;
  const el = () => { const v = d.querySelector('video.filme'), nm = Array.from(d.querySelectorAll('.nm'));
    return {v, nm, ow: nm.map(n => n.querySelector('o-w'))}; };
  const ev = [];
  const escuta = v => ['loadedmetadata', 'canplay', 'playing', 'seeking', 'seeked', 'waiting', 'pause', 'error']
    .forEach(n => v.addEventListener(n, () => ev.push([n, performance.now(), v.currentTime])));
  escuta(el().v);
  const anim = nome => d.getAnimations().find(a => a.animationName === nome && a.effect && a.effect.target
    && a.effect.target.isConnected);
  const tcss = () => { const a = anim('n0'); if (!a) return null; const c = a.effect.getComputedTiming();
    return c.progress == null ? null : c.progress * 33; };
  const op = x => x ? +getComputedStyle(x).opacity : -1;
  window.__qa = { ev, escuta, tcss,
    log(ms, leve) { const {v, nm, ow} = el(); return new Promise(res => {
      const vf = [], rf = []; let mt = null, nv = -1, fim = false; const t0 = performance.now();
      const q0 = v.getVideoPlaybackQuality();
      const g = (now, md) => { if (fim) return; mt = md.mediaTime; nv = now;
        vf.push([now, md.mediaTime, md.presentedFrames]); v.requestVideoFrameCallback(g); };
      const f = now => {
        if (now - t0 >= ms) { fim = true; const q1 = v.getVideoPlaybackQuality();
          res({vf, rf, total: q1.totalVideoFrames - q0.totalVideoFrames,
               perdidos: q1.droppedVideoFrames - q0.droppedVideoFrames}); return; }
        rf.push(leve ? [now, v.currentTime] : [now, mt, nv === now ? 1 : 0, tcss(), nm.map(op), ow.map(op),
                                              R.style.getPropertyValue('--tm'), R.className]);
        requestAnimationFrame(f); };
      v.requestVideoFrameCallback(g); requestAnimationFrame(f); }); },
    vai(t, n) { const {v} = el(); return new Promise(res => { v.addEventListener('seeked', () => { let k = 0;
      const g = (now, md) => { if (++k >= n) res(md.mediaTime); else v.requestVideoFrameCallback(g); };
      v.requestVideoFrameCallback(g); }, {once: true}); v.currentTime = t; }); },
    agora() { return [performance.now(), el().v.currentTime]; },
  };
})()"""

# Continuidade: o Power BI recria o HTML do visual (filtro, redimensionar) e roda o script de novo, na mesma janela
CONTINUIDADE_JS = r"""async () => {
  const doc = new DOMParser().parseFromString(await (await fetch(location.href, {cache: 'no-store'})).text(), 'text/html');
  const uc = doc.querySelector('.uc').outerHTML, scr = Array.from(doc.querySelectorAll('body script')).pop().textContent;
  const R = document.documentElement, v0 = document.querySelector('video.filme');
  await new Promise(r => v0.addEventListener('timeupdate', r, {once: true}));
  const t0 = v0.currentTime, a0 = performance.now();
  document.querySelector('.uc').remove();
  document.body.insertAdjacentHTML('afterbegin', uc);
  const s = document.createElement('script'); s.textContent = scr; document.body.appendChild(s);
  const v = document.querySelector('video.filme'); __qa.escuta(v);
  const ini = {cls: R.className, tc: __qa.tcss()};
  const retomou = await new Promise(r => v.addEventListener('playing', () => r(v.currentTime), {once: true}));
  const a1 = performance.now();
  const [now, mt] = await new Promise(res => { let k = 0; const g = (n, md) => {
    if (++k >= 3) res([n, md.mediaTime]); else v.requestVideoFrameCallback(g); }; v.requestVideoFrameCallback(g); });
  let dd = ((__qa.tcss() - mt) % 33 + 33) % 33; if (dd > 16.5) dd -= 33;
  return {t_antes: t0, video_retomou_em: retomou, linha_no_inicio: ini.tc, classes_no_inicio: ini.cls,
          ate_tocar_ms: a1 - a0, quadro: mt, passou_s: (now - a0) / 1000, defasagem_ms: dd * 1000, classes: R.className};
}"""

ESTADO_JS = r"""(() => { const v = document.querySelector('video.filme'), R = document.documentElement;
  return {classes: R.className, src: v.getAttribute('src'), autoplay: v.hasAttribute('autoplay'),
          networkState: v.networkState, readyState: v.readyState, paused: v.paused, currentTime: v.currentTime,
          erro: window.__erroVideo || null, ms: performance.now()}; })()"""
ERRO_INIT = ("document.addEventListener('error', e => { if (e.target && e.target.tagName === 'VIDEO') "
             "window.__erroVideo = [performance.now(), e.target.error ? e.target.error.code : null]; }, true);")


def _servidor(raiz: Path, extras: dict[str, bytes]):
    """Servidor local com Range (206), como o host do MP4 em produção; 'extras' = páginas em memória."""
    import http.server
    import mimetypes
    import threading
    from urllib.parse import unquote, urlsplit
    raiz = raiz.resolve()

    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            caminho = unquote(urlsplit(self.path).path)
            corpo, arq = extras.get(caminho), None
            if corpo is None:
                arq = (raiz / caminho.lstrip("/")).resolve()
                if raiz not in arq.parents or not arq.is_file():
                    self.send_error(404)
                    return
                tam = arq.stat().st_size
            else:
                tam = len(corpo)
            tipo = mimetypes.guess_type(caminho)[0] or "application/octet-stream"
            tipo += "; charset=utf-8" if tipo.startswith("text/") else ""
            ini, fim, status = 0, tam - 1, 200
            m = re.match(r"bytes=(\d*)-(\d*)$", self.headers.get("Range", ""))
            if m and (m.group(1) or m.group(2)):
                if m.group(1):
                    ini, fim = int(m.group(1)), min(int(m.group(2)) if m.group(2) else tam - 1, tam - 1)
                else:
                    ini = max(0, tam - int(m.group(2)))
                if ini > fim:
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{tam}")
                    self.end_headers()
                    return
                status = 206
            self.send_response(status)
            self.send_header("Content-Type", tipo)
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(fim - ini + 1))
            if status == 206:
                self.send_header("Content-Range", f"bytes {ini}-{fim}/{tam}")
            self.end_headers()
            try:
                if corpo is not None:
                    self.wfile.write(corpo[ini:fim + 1])
                    return
                with open(arq, "rb") as fh:
                    fh.seek(ini)
                    falta = fim - ini + 1
                    while falta > 0:
                        b = fh.read(min(1 << 16, falta))
                        if not b:
                            break
                        self.wfile.write(b)
                        falta -= len(b)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def _gira(x: float) -> float:
    """Diferença de tempo no laço, em (−T/2, T/2]."""
    x = (x + T / 2) % T - T / 2
    return x + T if x <= -T / 2 else x


def _taxa(ts: list[float]) -> dict | None:
    if len(ts) < 3:
        return None
    dt = sorted(b - a for a, b in zip(ts, ts[1:]))
    return {"qps": round((len(ts) - 1) / ((ts[-1] - ts[0]) / 1000), 1), "p95_ms": round(dt[int(len(dt) * .95)], 1),
            "pior_ms": round(dt[-1], 1)}


def _ate_a_volta(xs: list, idx: int) -> list:
    """Corta o registro na volta do laço (o tempo do vídeo cai)."""
    for i in range(1, len(xs)):
        if xs[i][idx] is not None and xs[i - 1][idx] is not None and xs[i][idx] < xs[i - 1][idx] - 10:
            return xs[:i]
    return xs


def _fps(r: dict) -> dict:
    rf, vf = _ate_a_volta(r["rf"], 1), _ate_a_volta(r["vf"], 1)
    res = {}
    for nome, a, b in JANELAS_FPS:
        res[nome] = {"pagina_rAF": _taxa([x[0] for x in rf if a <= x[1] < b]),
                     "video_quadros_novos": _taxa([x[0] for x in vf if a <= x[1] < b])}
    res["video_quadros_entregues"], res["video_quadros_perdidos"] = r["total"], r["perdidos"]
    return res


def _sinc(r: dict) -> dict:
    """Defasagem linha do tempo × vídeo e a entrada de cada número, no 1º laço do registro."""
    rf = r["rf"]
    volta = next((i for i in range(1, len(rf)) if rf[i][1] is not None and rf[i - 1][1] is not None
                  and rf[i][1] < rf[i - 1][1] - 10), len(rf))
    um, dois = rf[:volta], rf[volta:]

    def defas(xs):
        d = [1000 * _gira(x[3] - x[1]) for x in xs if x[2] and x[3] is not None and x[1] is not None
             and "uo-" not in x[7]]
        if not d:
            return None
        ab = sorted(abs(v) for v in d)
        return {"quadros": len(d), "media_ms": round(sum(d) / len(d), 2), "p99_abs_ms": round(ab[int(len(ab) * .99)], 2),
                "max_abs_ms": round(ab[-1], 2), "acima_de_1_quadro": sum(v > 1000 * QUADRO for v in ab)}

    def marco(xs, k, de, ate, chave, cond):
        for i, x in enumerate(xs):
            if x[1] is not None and de <= x[1] < ate and cond(x[chave][k]):
                return i
        return None

    takes = []
    for k in range(5):
        base = 5 * k
        e = marco(um, k, base + 2.5, base + 3.6, 4, lambda o: o > 0)
        c0 = marco(um, k, base + 2.5, base + 3.6, 5, lambda o: o > 0)
        c1 = marco(um, k, base + 3.5, base + 4.6, 5, lambda o: o == 0) if c0 is not None else None
        s = marco(um, k, base + 4.5, base + 5.5, 4, lambda o: o == 0)
        takes.append({
            "take": k + 1,
            "entra_no_quadro_s": round(um[e][1] - base, 4) if e is not None else None,
            "quadro_anterior_s": round(um[e - 1][1] - base, 4) if e else None,
            "linha_do_tempo_na_entrada_s": round(um[e][3] - base, 4) if e is not None else None,
            "conta_de_s": round(um[c0][1] - base, 4) if c0 is not None else None,
            "conta_ate_s": round(um[c1][1] - base, 4) if c1 is not None else None,
            "sai_no_quadro_s": round(um[s][1] - base, 4) if s is not None else None,
            "ultimo_quadro_com_numero_s": round(um[s - 1][1] - base, 4) if s else None,
            "defasagem": defas([x for x in um if x[1] is not None and base + 2.5 <= x[1] < base + 5.0]),
        })
    final = []
    for k in range(5):
        e = marco(um, k, 25.5, 29.0, 4, lambda o: o > 0)
        c1 = marco(um, k, FINAL[k] + 0.5, 30.0, 5, lambda o: o == 0)
        final.append({"numero": k + 1, "previsto_s": FINAL[k],
                      "entra_no_quadro_s": round(um[e][1], 4) if e is not None else None,
                      "conta_ate_s": round(um[c1][1], 4) if c1 is not None else None})
    return {"laco_1": defas(um), "depois_da_volta": defas(dois), "takes": takes, "final": final,
            "quadros_da_pagina": len(rf), "com_quadro_novo_do_video": sum(x[2] for x in rf)}


def _emenda(r: dict, eventos: list) -> dict:
    rf = r["rf"]
    i = next((j for j in range(1, len(rf)) if rf[j][1] is not None and rf[j - 1][1] is not None
              and rf[j][1] < rf[j - 1][1] - 10), None)
    if i is None:
        return {"erro": "o registro não passou pela volta do laço"}
    resumo = lambda x: {"t_ms": round(x[0], 1), "quadro_s": round(x[1], 4), "linha_s": None if x[3] is None else round(x[3], 4),
                        "numeros": [round(o, 3) for o in x[4]], "odometro": [round(o, 3) for o in x[5]], "tm": x[6],
                        "classes": x[7]}
    antes, depois = [x for x in rf[:i] if x[1] is not None], rf[i:]
    # quadros da página com a cena final na tela e os números já fora; papel em branco com números ainda na tela
    final_sem_numeros = [x for x in antes if x[1] >= 32.9 and min(x[4]) < 1]
    branco_com_numeros = [x for x in depois if x[1] < 0.5 and max(x[4]) > 0]
    e0 = next((j for j, x in enumerate(depois) if x[1] >= 2.5 and x[4][0] > 0), None)
    c0 = next((j for j, x in enumerate(depois) if x[1] >= 2.5 and x[5][0] > 0), None)
    c1 = next((j for j, x in enumerate(depois) if c0 is not None and j > c0 and x[5][0] == 0), None)
    t_volta = rf[i][0]
    return {
        "ultimos_antes": [resumo(x) for x in antes[-3:]], "primeiros_depois": [resumo(x) for x in depois[:4]],
        "quadros_pagina_cena_final_sem_numeros": len(final_sem_numeros),
        "quadros_pagina_papel_branco_com_numeros": len(branco_com_numeros),
        "eventos_na_volta": [[n, round(t - t_volta, 1), round(c, 4)] for n, t, c in eventos if abs(t - t_volta) < 300],
        "take1_reentra_no_quadro_s": round(depois[e0][1], 4) if e0 is not None else None,
        "take1_conta_de_ate_s": [round(depois[c0][1], 4) if c0 is not None else None,
                                 round(depois[c1][1], 4) if c1 is not None else None],
        "defasagem_depois_da_volta": _sinc({"rf": depois})["laco_1"],
    }


def _compara(a: Path, b: Path, dif: Path) -> dict:
    """Diferença por pixel (máximo dos 3 canais). Imagem: branco = igual, escuro = diferença × 4."""
    import numpy as np
    from PIL import Image
    x = np.asarray(Image.open(a).convert("RGB"), dtype=np.int16)
    y = np.asarray(Image.open(b).convert("RGB"), dtype=np.int16)
    dd = np.abs(x - y).max(axis=2)
    dif.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.clip(255 - dd * 4, 0, 255).astype(np.uint8)).save(dif)

    def st(m):
        return {"media": round(float(m.mean()), 3), "px_acima_16_pct": round(100 * float((m > 16).mean()), 3),
                "px_acima_64_pct": round(100 * float((m > 64).mean()), 3), "max": int(m.max())}
    return {"ref": b.name, "tudo": st(dd), "faixa_0_640": st(dd[:640]), "base_640_1080": st(dd[640:])}


def provas_video(html_path: Path, video: str, poster: str, capturas: bool, medir: bool) -> dict:
    """Prova da versão MP4 no Edge headless, com o vídeo tocando de verdade (servidor local com Range)."""
    import os
    from urllib.parse import quote, unquote
    from playwright.sync_api import sync_playwright
    html_path = html_path.resolve()
    pasta = html_path.parent
    alvo_v, alvo_p = (pasta / unquote(video)).resolve(), (pasta / unquote(poster)).resolve()
    raiz = Path(os.path.commonpath([pasta, alvo_v.parent, alvo_p.parent]))
    rel = "/" + html_path.relative_to(raiz).as_posix()
    rel_falha = rel[:-5] + "-falha.html"
    texto = html_path.read_text(encoding="utf-8")
    invalido = (video.rsplit("/", 1)[0] + "/" if "/" in video else "") + "nao-existe.mp4"
    falha = texto.replace(f'src="{video}"', f'src="{invalido}"', 1)
    if falha == texto:
        raise SystemExit("provas_video: não achei o src do vídeo no HTML")
    srv = _servidor(raiz, {rel_falha: falha.encode("utf-8")})
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    url, url_falha = base + quote(rel), base + quote(rel_falha)
    QA_VIDEO.mkdir(parents=True, exist_ok=True)
    dif = QA_VIDEO / "dif"
    out: dict = {"pagina": url, "video": video, "poster": poster, "invalido": invalido}
    tela = {"width": W, "height": H}
    try:
        with sync_playwright() as pw:
            nav = pw.chromium.launch(channel="msedge", headless=True)
            out["navegador"] = f"Edge {nav.version} headless"
            print(f"{out['navegador']} · {url}")
            pag = nav.new_page(viewport=tela, device_scale_factor=1)
            pag.goto(url)
            pag.evaluate(QA_JS)
            pag.wait_for_function("!document.documentElement.classList.contains('uo-espera')", timeout=20000)
            out["tocando_apos_ms"] = round(pag.evaluate("performance.now()"))
            pag.evaluate("document.fonts.ready")
            if medir:
                pag.evaluate("__qa.vai(0, 2)")
                out["fps"] = _fps(pag.evaluate("ms => __qa.log(ms, true)", 33300))
                for nome, v in out["fps"].items():
                    if isinstance(v, dict):
                        print(f"q/s {nome}: página {v['pagina_rAF']} · vídeo {v['video_quadros_novos']}")
                print(f"vídeo: {out['fps']['video_quadros_entregues']} quadros, "
                      f"{out['fps']['video_quadros_perdidos']} perdidos")
                pag.evaluate("__qa.vai(0, 2)")
                n_ev = pag.evaluate("__qa.ev.length")
                reg = pag.evaluate("ms => __qa.log(ms, false)", 38000)
                eventos = pag.evaluate("__qa.ev.slice()")[n_ev:]
                out["sinc"] = _sinc(reg)
                out["emenda"] = _emenda(reg, eventos)
                print("defasagem (linha - vídeo), laço 1:", out["sinc"]["laco_1"])
                for tk in out["sinc"]["takes"]:
                    print(f"  take {tk['take']}: entra no quadro {tk['entra_no_quadro_s']} s (anterior "
                          f"{tk['quadro_anterior_s']}), conta {tk['conta_de_s']}–{tk['conta_ate_s']} s, sai em "
                          f"{tk['sai_no_quadro_s']} s (último com número {tk['ultimo_quadro_com_numero_s']})")
                for fn in out["sinc"]["final"]:
                    print(f"  final, número {fn['numero']}: previsto {fn['previsto_s']} s, entra no quadro "
                          f"{fn['entra_no_quadro_s']} s, termina de contar em {fn['conta_ate_s']} s")
                em = out["emenda"]
                print(f"emenda: {em.get('quadros_pagina_cena_final_sem_numeros')} quadros da página com a cena final "
                      f"sem números, {em.get('quadros_pagina_papel_branco_com_numeros')} com papel branco e números; "
                      f"take 1 reentra em {em.get('take1_reentra_no_quadro_s')} s e conta "
                      f"{em.get('take1_conta_de_ate_s')}; eventos {em.get('eventos_na_volta')}")
            if capturas:
                caps = []
                for nome, t, ref in CAPTURAS_VIDEO:
                    mt = pag.evaluate("t => __qa.vai(t, 2)", t)
                    a = pag.evaluate("__qa.agora()")
                    pag.screenshot(path=str(QA_VIDEO / nome))
                    b = pag.evaluate("__qa.agora()")
                    caps.append({"arquivo": nome, "t": t, "quadro_entregue_s": round(mt, 4),
                                 "tempo_antes_s": round(a[1], 4), "tempo_depois_s": round(b[1], 4),
                                 "ms": round(b[0] - a[0])})
                    print(f"captura {nome}: pedido {t:g} s, quadro {mt:.3f} s, tela entre {a[1]:.3f} e {b[1]:.3f} s")
                out["capturas"] = caps
                # continuidade (o visual recriado no meio do take 3)
                pag.evaluate("__qa.vai(12.0, 2)")
                pag.wait_for_timeout(400)
                out["continuidade"] = pag.evaluate(CONTINUIDADE_JS)
                pag.screenshot(path=str(QA_VIDEO / "estado-continuidade-visual-recriado.png"))
                print("continuidade:", out["continuidade"])
                # src inválido
                ctx = nav.new_context(viewport=tela, device_scale_factor=1)
                ctx.add_init_script(ERRO_INIT)
                p2 = ctx.new_page()
                p2.goto(url_falha)
                p2.wait_for_function("document.documentElement.classList.contains('uo-parado')", timeout=10000)
                est = p2.evaluate(ESTADO_JS)
                p2.evaluate("document.fonts.ready")
                p2.wait_for_timeout(1500)
                p2.screenshot(path=str(QA_VIDEO / "estado-falha-src-invalido.png"))
                out["falha"] = est
                print("falha (src inválido):", est)
                ctx.close()
                # movimento reduzido
                ctx = nav.new_context(viewport=tela, device_scale_factor=1, reduced_motion="reduce")
                p3 = ctx.new_page()
                p3.goto(url)
                p3.evaluate("document.fonts.ready")
                p3.wait_for_timeout(1500)
                out["reduzido"] = p3.evaluate(ESTADO_JS)
                p3.screenshot(path=str(QA_VIDEO / "estado-movimento-reduzido.png"))
                print("movimento reduzido:", out["reduzido"])
                ctx.close()
            nav.close()
            if capturas:
                # autoplay recusado (política que exige gesto, como um navegador travado)
                nav2 = pw.chromium.launch(channel="msedge", headless=True,
                                          args=["--autoplay-policy=user-gesture-required"])
                p4 = nav2.new_page(viewport=tela, device_scale_factor=1)
                p4.goto(url)
                p4.wait_for_function("document.documentElement.classList.contains('uo-parado')", timeout=10000)
                out["autoplay_recusado"] = p4.evaluate(ESTADO_JS)
                p4.evaluate("document.fonts.ready")
                p4.wait_for_timeout(1500)
                p4.screenshot(path=str(QA_VIDEO / "estado-autoplay-recusado.png"))
                print("autoplay recusado:", out["autoplay_recusado"])
                nav2.close()
                # referência SVG no mesmo instante, quando a tela caiu fora do quadro pedido (desenho ou conta em curso)
                nav3 = pw.chromium.launch(channel="msedge", headless=True)
                p5 = nav3.new_page(viewport=tela, device_scale_factor=1)
                svg_html = SAIDA.read_text(encoding="utf-8") if SAIDA.is_file() else None
                comps = []
                for c, (nome, t, ref) in zip(out["capturas"], CAPTURAS_VIDEO):
                    item = {"captura": nome, "svg_mesmo_t": _compara(QA_VIDEO / nome, QA / ref,
                                                                      dif / f"dif-{nome}")}
                    tt = c["tempo_antes_s"]
                    if svg_html and abs(tt - t) > QUADRO:
                        rnome = f"ref-svg-t{tt:06.3f}.png".replace(".", "_", 1)
                        p5.set_content(svg_html.replace("</style>", congela_css(round(tt * 60) / 60) + "</style>", 1))
                        p5.evaluate("document.fonts.ready")
                        p5.wait_for_timeout(250)
                        p5.screenshot(path=str(dif / rnome))
                        item["svg_no_t_da_tela"] = _compara(QA_VIDEO / nome, dif / rnome, dif / f"dif-tela-{nome}")
                    comps.append(item)
                for nome, ref in (("estado-falha-src-invalido.png", "capa-v2-t31_0-final-5-numeros.png"),
                                  ("estado-movimento-reduzido.png", "capa-v2-movimento-reduzido.png"),
                                  ("estado-autoplay-recusado.png", "capa-v2-movimento-reduzido.png")):
                    comps.append({"captura": nome, "svg": _compara(QA_VIDEO / nome, QA / ref, dif / f"dif-{nome}")})
                nav3.close()
                out["comparacao_svg"] = comps
                for c in comps:
                    print("comparação", c["captura"], {k: v for k, v in c.items() if k != "captura"})
    finally:
        srv.shutdown()
    (QA_VIDEO / "medicoes.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"medições em {QA_VIDEO / 'medicoes.json'}")
    return out


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--capturas", action="store_true")
    a.add_argument("--medir", action="store_true")
    a.add_argument("--por-traco", action="store_true", help="uma animação por <path> (comparação de desempenho)")
    a.add_argument("--saida", type=Path, default=None,
                   help="padrão: capa-v2.html (ou capa-v2-video.html com --video)")
    a.add_argument("--video", metavar="CAMINHO_RELATIVO",
                   help="gera a versão com o filme em MP4 (caminho relativo ao HTML, ex.: "
                        "../remotion/renders/capa-filme-2560x854-60fps.mp4); --capturas/--medir passam a provar o vídeo "
                        "em pbi\\qa\\capa\\prototipo-video\\")
    a.add_argument("--poster", metavar="CAMINHO_RELATIVO",
                   help=f"pôster (relativo ao HTML); padrão: {POSTER_PADRAO} na pasta do MP4")
    p = a.parse_args(argv)
    global AGRUPAR
    AGRUPAR = not p.por_traco
    if p.poster and not p.video:
        a.error("--poster só vale com --video")
    video = poster = None
    if p.video:
        v = p.video.replace("\\", "/")
        video = url_relativa(v)
        poster = url_relativa(p.poster or (v.rsplit("/", 1)[0] + "/" if "/" in v else "") + POSTER_PADRAO)
    saida = p.saida or (SAIDA_VIDEO if video else SAIDA)
    html, info = montar(video, poster)
    saida.write_text(html, encoding="utf-8", newline="\n")
    if video:
        for rotulo, rel in (("vídeo", video), ("pôster", poster)):
            alvo = (saida.parent / rel).resolve()
            print(f"  {rotulo}: {rel} -> {alvo} ({'ok' if alvo.is_file() else 'NÃO ENCONTRADO'})")
        print(f"{saida.name}: {info['bytes'] / 1e3:.0f} KB (sem o filme embutido), laço de {T:g} s")
    else:
        print(f"{saida.name}: {info['bytes'] / 1e6:.2f} MB, {info['paths_filme']} traços no filme, laço de {T:g} s")
    if p.capturas or p.medir:
        if video:
            provas_video(saida, video, poster, p.capturas, p.medir)
        else:
            provas(saida, p.capturas, p.medir)


if __name__ == "__main__":
    main()

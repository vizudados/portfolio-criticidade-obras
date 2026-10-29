#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""capa_medidas — medidas da capa v2 do painel Criticidade de Obras (pbi/dax/capa/**), a partir do protótipo aprovado.

Fontes: pbi/spec/capa/prototipo/NOTAS-IMPLEMENTACAO.md (o plano), montar_capa_v2.py (CSS, linha do tempo, logo, ícones
e a sincronia JS_SINC_VIDEO, reaproveitados daqui sem cópia) e capa_publicar.py (as URLs do GitHub Pages).

Contas (pasta Capa\\Contas): o texto de cada número que a capa mostra, com a MESMA regra dos cartões da T1
(desenho_projeto.rs/pct/pp/inteiro: R$ mil/mi, sinal U+2212, p.p.). A capa só lê esses textos; os cartões da T1 não foram
refatorados (a igualdade é provada no motor por capa_provar.py).

Desenho (pasta Capa):
  CO Capa · HTML        o palco inteiro num lote só (< 29.000 caracteres): faixa do filme (<video> MP4 publicado), régua,
                        identidade, os 5 números com odômetro (técnica do contador.py, com as duas diferenças das notas:
                        cada quadro é o valor inteiro com prefixo e sufixo em spans de 36 px, e os quadros 23–24
                        proporcionais), base com a panorâmica publicada, título, CTA e cartões desenhados, e o JS
                        (sincronia cravada no mediaTime do quadro, estados uo-espera/uo-parado, autoplay recusado,
                        continuidade e o botão discreto de pausar o filme)
  CO Capa · CSS         folha do visual: [CO Capa · CSS fontes] + palco + linha do tempo de 33 s + estados
  CO Capa · CSS fontes  Barlow 400/600/700 (woff2 do mockup, base64) como 'Barlow U'
  CO Capa · ALT         texto alternativo (≤ 250)

    python -I -X utf8 pbi/scripts/capa_medidas.py              # grava os .dax em pbi/dax/capa
    python -I -X utf8 pbi/scripts/capa_medidas.py --previa     # + prévia local (árvore real do visual) em pbi/qa/capa/pbip/previa
    python -I -X utf8 pbi/scripts/capa_medidas.py --fundo      # + fundo da página (pôster + números de set/26) em
                                                               #   pbi/assets/wallpapers/wp-capa.jpg
    ... --previa --fundo --local                               # o mesmo, com as mídias locais (antes de publicar);
                                                               #   a medida continua com os endereços do Pages
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
AQUI = Path(__file__).resolve().parent                     # pbi/scripts
RAIZ = AQUI.parent                                          # pbi
sys.path.insert(0, str(AQUI))
import capa_publicar as PUB  # noqa: E402
import contador as C  # noqa: E402
import desenho_projeto as D  # noqa: E402
from contas_lib_projeto import Medida, gravar  # noqa: E402

GERADO = "pbi/scripts/capa_medidas.py"
DESTINO = RAIZ / "dax" / "capa"
QA = RAIZ / "qa" / "capa" / "pbip"
FUNDO = RAIZ / "assets" / "wallpapers" / "wp-capa.jpg"
MENOS = D.MENOS
LOTE_MAX = 29000                                            # notas §1: cada lote abaixo de 29.000 caracteres
DAX_ITENS_MAX, DAX_GRUPO = 800, 400                         # tour_lib._dax: cadeia de & com ~1.000 termos é recusada


def _prototipo():
    arq = RAIZ / "spec" / "capa" / "prototipo" / "montar_capa_v2.py"
    spec = importlib.util.spec_from_file_location("capa_prototipo_v2", arq)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


P = _prototipo()
# Mídias da capa (cenas de Natal, 28/10/2026): o filme do Remotion codificado pela NVENC, o pôster e a panorâmica, nos
# endereços do GitHub Pages que o capa_publicar.py monta (nome = arquivo + 12 hex do SHA-256). Com os arquivos na
# máquina, a URL sai do SHA local; sem eles (outra máquina, pasta publicacao fora do git), ficam os endereços abaixo,
# os do render de 28/10/2026. Enquanto o repositório público não existe, eles dão 404 e a capa para no estado parado.
MIDIAS_SEM_ARQUIVO = {
    "mp4": PUB.ASSETS_URL + "capa-filme-2560x854-60fps-cba382839b4c.mp4",
    "poster": PUB.ASSETS_URL + "capa-filme-poster-d0910e567a60.webp",
    "pano": PUB.ASSETS_URL + "panoramica-base-792749d224fb.svg",
}
ARQUIVO_LOCAL = {"mp4": PUB.MP4, "poster": PUB.POSTER, "pano": PUB.PANO}


def _midia(chave: str) -> str:
    try:
        return PUB.url(chave)
    except FileNotFoundError:
        return MIDIAS_SEM_ARQUIVO[chave]


VIDEO, POSTER, PANO = _midia("mp4"), _midia("poster"), _midia("pano")


def com_midias_locais(texto: str) -> str:
    """Só para a prévia e o fundo antes da publicação: troca cada endereço publicado pelo arquivo local (file://)."""
    for chave, u in (("mp4", VIDEO), ("poster", POSTER), ("pano", PANO)):
        arq = ARQUIVO_LOCAL[chave]
        if not arq.is_file():
            raise SystemExit(f"--local: falta {arq} (rode o render do Remotion e capa_publicar.py --montar)")
        texto = texto.replace(u, arq.resolve().as_uri())
    return texto

# ================================================================================================== contas (texto)
# (nome, medida lida, formatador da T1, peça do cartão da T1 que diz o mesmo número)
CONTAS = [
    ("Capa · obras · valor (texto)", "Obras com análise · ref", "inteiro",
     "número do cartão 'Obras em andamento' da T1"),
    ("Capa · obras · orçamento (texto)", "Orçamento · ref", "rs",
     "valor ao lado do número no cartão 'Obras em andamento' da T1"),
    ("Capa · resultado · valor (texto)", "Resultado da obra · ref", "rs",
     "número do cartão 'Resultado da carteira' da T1"),
    ("Capa · resultado · % do orçamento (texto)", "Resultado % · ref", "pct2+",
     "percentual ao lado do número no cartão 'Resultado da carteira' da T1"),
    ("Capa · resultado · variação (texto)", "Resultado · variação no mês · ref", "rs+",
     "variação sobre o mês anterior, na linha de baixo do cartão 'Resultado da carteira' da T1"),
    ("Capa · físico · valor (texto)", "Físico · executado acumulado · com previsto · ref", "pct",
     "número do cartão 'Físico acumulado · ponderado' da T1"),
    ("Capa · físico · previsto (texto)", "Físico · previsto acumulado · ref", "pct",
     "previsto na linha de baixo do cartão 'Físico acumulado · ponderado' da T1"),
    ("Capa · físico · desvio (texto)", "Físico · desvio acumulado p.p. · ref", "pp",
     "desvio em p.p. na linha de baixo do cartão 'Físico acumulado · ponderado' da T1"),
    ("Capa · desembolso · valor (texto)", "Desembolso · realizado no mês · ref", "rs",
     "número do cartão 'Desembolso do mês' da T1"),
    ("Capa · desembolso · previsto (texto)", "Desembolso · previsto no mês · ref", "rs",
     "previsto na linha de baixo do cartão 'Desembolso do mês' da T1"),
    ("Capa · sem estoque · valor (texto)", "Resultado sem ativos · ref", "rs",
     "número do cartão 'Resultado sem estoque' da T1"),
    ("Capa · sem estoque · pagos não aplicados (texto)", "Ativos não consumidos · ref", "rs",
     "valor pago e não aplicado na linha de baixo do cartão 'Resultado sem estoque' da T1"),
]
FORMATADORES = {
    "inteiro": lambda v: D.inteiro(v, "_t"),
    "rs": lambda v: D.rs(v, "_t"),
    "rs+": lambda v: D.rs(v, "_t", mais=True),
    "pct": lambda v: D.pct(v, "_t"),
    "pct2+": lambda v: D.pct(v, "_t", casas=2, mais=True),
    "pp": lambda v: D.pp(v, "_t"),
}
REGRA = {
    "inteiro": "inteiro com ponto de milhar (vazio = 0)",
    "rs": "R$ com mil/mi (≥ 100 mi uma casa; 1 a 100 mi duas; mil a 1 mi inteiro), sinal U+2212 antes do R$",
    "rs+": "R$ com mil/mi e sinal (+ ou U+2212)",
    "pct": "percentual com uma casa, sinal U+2212",
    "pct2+": "percentual com duas casas e sinal (+ ou U+2212)",
    "pp": "pontos percentuais com uma casa e sinal (+ ou U+2212)",
}


def medidas_contas() -> list[Medida]:
    saida = []
    for nome, leitura, fmt, peca in CONTAS:
        dax = "\n".join(
            ["VAR _v = [" + leitura + "]",
             "-- texto na regra dos cartões da T1 (desenho_projeto: " + REGRA[fmt] + "); vazio = '—'"]
            + FORMATADORES[fmt]("_v") + ["RETURN", "    _tTxt"])
        saida.append(Medida(
            nome, r"Capa\Contas", "texto",
            f"Texto do número da capa: [{leitura}] escrito com a regra dos cartões da T1 ({REGRA[fmt]}). A capa "
            "só lê este texto; o cartão da T1 escreve o mesmo número com a mesma regra.",
            dax, oraculo=f"o texto da T1 ({peca}); prova no motor por pbi/scripts/capa_provar.py"))
    return saida


# ============================================================================================ desenho: o palco (HTML)
# Os 5 números (rótulos do Figma v2 471:2389 … 471:2434); tipo diz como separar prefixo, núcleo e sufixo do texto
NUMEROS = [
    ("obras", "Obras em andamento", "_o1", "int"),
    ("resultado", "Resultado da carteira", "_r1", "rs"),
    ("fisico", "Físico acumulado", "_f1", "pct"),
    ("desembolso", "Desembolso do mês", "_d1", "rs"),
    ("sem_estoque", "Resultado sem estoque", "_s1", "rs"),
]
LEITURAS = [
    ("_mes", "Mês de referência · longo"), ("_mesAnt", "Mês anterior à referência · nome"),
    ("_ant", "Resultado · mês anterior · ref"),
    # Fase 2 da régua antiga: as quatro contagens da carteira pela Nota da obra (a pendente, sem nota, tracejada como na gaveta)
    ("_crit", "Nota · carteira · obras críticas · ref"), ("_aten", "Nota · carteira · obras em atenção · ref"),
    ("_est", "Nota · carteira · obras estáveis · ref"), ("_pend", "Nota · carteira · obras pendentes · ref"),
    ("_o1", "Capa · obras · valor (texto)"), ("_o2", "Capa · obras · orçamento (texto)"),
    ("_r1", "Capa · resultado · valor (texto)"), ("_r2", "Capa · resultado · % do orçamento (texto)"),
    ("_r3", "Capa · resultado · variação (texto)"),
    ("_f1", "Capa · físico · valor (texto)"), ("_f2", "Capa · físico · previsto (texto)"),
    ("_f3", "Capa · físico · desvio (texto)"),
    ("_d1", "Capa · desembolso · valor (texto)"), ("_d2", "Capa · desembolso · previsto (texto)"),
    ("_s1", "Capa · sem estoque · valor (texto)"), ("_s2", "Capa · sem estoque · pagos não aplicados (texto)"),
]
SEM_ANTERIOR = "sem mês anterior para comparar"            # a frase do cartão da T1


def _sem_quebras(html: str) -> str:
    """HTML estático sem quebras de linha nem recuo entre as tags (o texto não muda)."""
    return re.sub(r">\s+<", "><", html.replace("\r", "")).replace("\n", "")


def _logo() -> str:
    return _sem_quebras(P.ler_logo())


def _cartoes() -> str:
    return "".join(
        f"<div class='ca k{i}'><div class='se' aria-hidden='true'><svg viewBox='0 0 21 21' focusable='false'>"
        f"<path transform='translate({dx} {dy})' d='{d}'/></svg></div><h2 class='b'>{t}</h2><p>{q}</p>"
        f"<div class='ab b' aria-hidden='true'>Abrir{P.SETA_ABRIR}</div></div>"
        for i, ((t, q), (dx, dy, d)) in enumerate(zip(P.CARTOES, P.ICONES)))


def _regua() -> str:
    return ("<div class='rg' aria-hidden='true'><div class='ps'>" + "".join(f"<i class='p{j}'></i>" for j in range(6))
            + "</div><div class='rl b'>" + "".join(f"<span class='l{j}'>{t}</span>" for j, t in enumerate(P.REGUA))
            + "</div></div>")


def tag_video() -> str:
    """O filme publicado (MP4 2560×854 mostrado em 1920×640) e o pôster (a cena final desenhada)."""
    return (f'<video class="filme" src="{VIDEO}" poster="{POSTER}" muted autoplay loop playsinline preload="auto" '
            'disablepictureinpicture disableremoteplayback aria-hidden="true"></video>')


def corpo_partes() -> list:
    """O palco em partes: texto fixo ou ('v', VAR do DAX). A mesma árvore e as mesmas classes do protótipo
    (montar_capa_v2.corpo_html), com o filme e a panorâmica pelos links publicados e os números escritos pelo DAX."""
    pano = f"<img class='pano' src='{PANO}' alt='' aria-hidden='true' decoding='async'>"
    return [
        '<div class="uc" lang="pt-BR"><div class="st">'
        '<section class="fx" aria-label="Acompanhamento de obras · mês de referência e indicadores principais">'
        '<div class="rid" aria-hidden="true"></div>'
        f'<div class="logo" role="img" aria-label="Vizu Dados">{_logo()}</div>'
        '<div class="dv" aria-hidden="true"></div><p class="kk b">Acompanhamento de obras</p>'
        '<p class="ms b">Mês de referência · <strong data-campo="mes">', ("v", "_mesH"), "</strong></p>"
        + _regua() + '<div class="ln">',
        *[("v", f"_blk{i}") for i in range(len(NUMEROS))],
        "</div>" + tag_video() + '</section><div class="fio" aria-hidden="true"></div>'
        f'<section class="bs" aria-label="Entrada do painel">{pano}</section>'
        '<h1 class="ti b"><strong>Criticidade de Obras</strong> · Acompanhamento e análise crítica</h1>'
        '<p class="su b">Quais obras pedem atenção neste mês, e por quê.</p>'
        f'<div class="ct b" aria-hidden="true">Entrar no painel{P.SETA_CTA}</div>' + _cartoes()
        + '<p class="ft b">Planilhas Análise Crítica de cada obra · tratamento em Power Query · <span data-campo="mes">',
        ("v", "_mesH"), "</span></p></div></div>",
        "<script>" + js_capa() + "</script>",
    ]


# ------------------------------------------------------------------------------------------------------------ JS
# Porte do JS_SINC_VIDEO do protótipo (a sincronia aprovada: cada animação da capa cravada no mediaTime do quadro do
# vídeo, a cada 'playing'/'seeked', conferida no quadro seguinte e a cada 'timeupdate'; estados uo-espera e uo-parado;
# autoplay recusado; continuidade W.__uoT quando o visual refaz o HTML) com o botão discreto de pausar:
#   - o botão é criado pelo JS (sem JS ou com movimento reduzido ele não existe, como o "Pausar filme" do painel de referência), fica
#     na faixa do filme, no canto de cima à esquerda, sob o logo e na linha da régua (dentro do recorte branco da
#     identidade, livre nos 6 takes), aria-label "Pausar o filme" / "Tocar o filme";
#   - pausado, o vídeo para e CADA animação da capa é cravada no currentTime do quadro parado e pausada pela Web
#     Animations API (o mesmo cravamento; sem animation-play-state); ao tocar, o 'playing' recrava e retoma;
#   - o estado sobrevive ao visual refazendo o HTML (W.__uoPausa): o vídeo novo nasce parado no mesmo quadro;
#   - qualquer pausa do vídeo (inclusive a do navegador) congela os números junto.
JS_CAPA = """(function(){'use strict';
var d=document,R=d.documentElement,W=window;
var f=d.querySelector('video.filme'),uc=d.querySelector('.uc'),fx=d.querySelector('.uc .fx');
if(!f||!uc){return;}
var T=%(T)s,Q=1/60,cl=R.classList;
var agora=function(){return (W.performance&&performance.now)?performance.now():Date.now();};
cl.remove('uo-parado','uo-espera','uo-pausa');R.style.removeProperty('--tm');clearTimeout(W.__uoEsp);
var vivo=function(){return f.isConnected;};
var parado=function(){if(vivo()){cl.remove('uo-espera','uo-pausa');cl.add('uo-parado');}};
var desliga=function(){f.removeAttribute('autoplay');f.setAttribute('preload','none');try{f.pause();}catch(e){}
f.removeAttribute('src');try{f.load();}catch(e){}};
if((W.matchMedia&&W.matchMedia('(prefers-reduced-motion: reduce)').matches)||f.error){parado();desliga();return;}
var pausa=W.__uoPausa===1&&!!W.__uoT;
if(pausa){f.removeAttribute('autoplay');try{f.pause();}catch(e){}}
cl.add('uo-espera');R.style.setProperty('--tm','1000s');f.muted=true;f.defaultMuted=true;
var lista=function(){var l=d.getAnimations?d.getAnimations():[],r=[];
for(var i=0;i<l.length;i++){var e=l[i].effect&&l[i].effect.target;if(l[i].animationName&&e&&uc.contains(e)){r.push(l[i]);}}
return r;};
var crava=function(mt,para){R.style.setProperty('--tm','0s');var l=lista();
for(var i=0;i<l.length;i++){try{if(para){l[i].pause();}else if(l[i].playState==='paused'){l[i].play();}
l[i].currentTime=mt*1000;}catch(e){}}};
var defasagem=function(mt){var l=lista(),pior=0;for(var i=0;i<l.length;i++){var c=l[i].effect.getComputedTiming();
if(c.progress==null){continue;}var x=((c.progress*T-mt)%%T+T)%%T;if(x>T/2){x-=T;}if(Math.abs(x)>Math.abs(pior)){pior=x;}}
return pior;};
var quadro=function(fn){if(f.requestVideoFrameCallback){f.requestVideoFrameCallback(function(n,md){if(vivo()){fn(md.mediaTime);}});}
else{fn(f.currentTime);}};
var sinc=function(){if(!vivo()||f.paused){return;}quadro(function(mt){if(f.paused){return;}clearTimeout(W.__uoEsp);
cl.remove('uo-espera','uo-parado');crava(mt,false);
quadro(function(m2){if(Math.abs(defasagem(m2))>Q/4){crava(m2,false);}});});};
var congela=function(){if(!vivo()){return;}var t=f.currentTime;W.__uoT=[t,agora()];crava(t,true);};
f.addEventListener('playing',sinc);
f.addEventListener('seeked',function(){if(!f.paused){sinc();return;}
if(pausa&&vivo()){clearTimeout(W.__uoEsp);cl.remove('uo-espera','uo-parado');congela();}});
f.addEventListener('pause',function(){if(!vivo()||cl.contains('uo-parado')||cl.contains('uo-espera')){return;}congela();});
f.addEventListener('timeupdate',function(){if(!vivo()){return;}if(!f.paused){W.__uoT=[f.currentTime,agora()];}
if(f.paused||cl.contains('uo-espera')||cl.contains('uo-parado')){return;}
quadro(function(mt){if(Math.abs(defasagem(mt))>Q/2){crava(mt,false);}});});
f.addEventListener('error',function(){parado();desliga();});
var bt=d.createElement('button');bt.type='button';bt.className='pz';
var marca=function(){var r=pausa?'Tocar o filme':'Pausar o filme';bt.setAttribute('aria-label',r);bt.title=r;
if(pausa){cl.add('uo-pausa');}else{cl.remove('uo-pausa');}};
bt.addEventListener('click',function(e){e.preventDefault();e.stopPropagation();pausa=!pausa;W.__uoPausa=pausa?1:0;marca();
if(pausa){try{f.pause();}catch(x){}congela();}
else{try{var p=f.play();if(p&&p.catch){p.catch(function(){});}}catch(x){}}});
marca();(fx||uc).appendChild(bt);
var c=W.__uoT;
if(c&&c[0]>0){var t0=pausa?c[0]:(c[0]+(agora()-c[1])/1000)%%T;crava(t0,pausa);
var vai=function(){try{f.currentTime=t0;}catch(e){}};
if(f.readyState>=1){vai();}else{f.addEventListener('loadedmetadata',vai,{once:true});}}
if(!pausa){try{var p=f.play();if(p&&p.catch){p.catch(function(x){if(x&&x.name==='NotAllowedError'){parado();}});}}catch(x){}}
W.__uoEsp=setTimeout(function(){if(vivo()&&cl.contains('uo-espera')){parado();}},%(espera)d);
})();"""


def js_capa() -> str:
    linhas = (JS_CAPA % {"T": f"{P.T:g}", "espera": P.ESPERA_MS}).splitlines()
    js = "".join(l.strip() for l in linhas)
    if "//" in js.replace("://", "") or "</script" in js.lower():
        raise SystemExit("JS da capa: comentário de linha ou </script> dentro do script")
    return js


# --------------------------------------------------------------------------------------------------------- CSS
# Botão de pausar (fora do U(): o alvo tem no mínimo 24 px de verdade, mesmo com o palco reduzido). Desenho 28 × 28 px do
# palco, centro em (85, 100): na linha da régua (y 92–108) e sob o logo (x 80–178, y 34–78), dentro do recorte branco
# da identidade (x 66–516, y 18–110 no take mais estreito). Ícone em CSS: duas barras (pausar) / triângulo (tocar);
# grafite #3B3B3F a .6 (contraste 3,4:1 sobre o branco, WCAG 1.4.11), cheio no hover e no foco.
CSS_PAUSA = (
    ".uc .pz{position:absolute;left:calc(var(--u)*71);top:calc(var(--u)*86);width:max(24px,calc(var(--u)*28));"
    "height:max(24px,calc(var(--u)*28));display:flex;align-items:center;justify-content:center;margin:0;padding:0;"
    "border:0;border-radius:50%;background:transparent;color:#3B3B3F;opacity:.6;cursor:pointer;z-index:6;"
    "-webkit-appearance:none;appearance:none;-webkit-tap-highlight-color:transparent}"
    ".uc .pz::before{content:'';display:block;box-sizing:border-box;width:calc(var(--u)*10);"
    "height:calc(var(--u)*12);border-left:calc(var(--u)*3.5) solid currentColor;"
    "border-right:calc(var(--u)*3.5) solid currentColor}"
    "html.uo-pausa .uc .pz::before{width:0;height:0;margin-left:calc(var(--u)*2);border-right:0;"
    "border-left:calc(var(--u)*10) solid currentColor;border-top:calc(var(--u)*6) solid transparent;"
    "border-bottom:calc(var(--u)*6) solid transparent}"
    ".uc .pz:hover{opacity:1;background:rgba(11,11,12,.06)}"
    ".uc .pz:focus{outline:none}"
    ".uc .pz:focus-visible{opacity:1;outline:2px solid #0B0B0C;outline-offset:2px}"
    "html.uo-parado .uc .pz{display:none}"
    "@media print{.uc .pz{display:none}}"
)
# o visual: corpo e html no papel offwhite, sem barras do OverlayScrollbars; a panorâmica é um <img> (o SVG publicado)
CSS_VISUAL = ("html,body{margin:0;padding:0;background:#F7F4EE;overflow:hidden}"
              "#htmlContent{margin:0!important;padding:0!important}.os-scrollbar{display:none!important}"
              ".uc img.pano{display:block;max-width:none}"
              # chip da obra PENDENTE na nota (Fase 2): tracejado grafite, como a marca .mkm do painel e a gaveta; a
              # borda de 1 px sai da folga, para o chip ter a mesma altura dos outros
              ".uc .nm .ch.cm{background:#FFFFFF;color:#0B0B0C;border:1px dashed #3B3B3F;padding:4.04px 7.64px}"
              ".uc .nm .ch.cm i{background:transparent;border:1px dashed #3B3B3F;width:6.48px;height:6.48px;"
              "box-sizing:border-box}")


def _css_compacta(css: str) -> str:
    """Sem comentários e sem quebras de linha (o CSS não muda de sentido)."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s*\n\s*", " ", css)
    return re.sub(r" {2,}", " ", css).strip()


def css_capa() -> str:
    """A folha do visual sem as fontes (o lote literal de CO Capa · CSS)."""
    return (":root{color-scheme:light}" + CSS_VISUAL
            + _css_compacta(P.U(P.css_palco()) + P.U(P.css_filme_video()) + P.U(P.css_tempo())
                            + P.css_reduzido_video(POSTER))
            + CSS_PAUSA)


def css_fontes() -> str:
    return P.fontes().replace("\n", "")


# --------------------------------------------------------------------------------------------- DAX do palco
def _lits(s: str, n: int = 100) -> list[str]:
    return ['"' + s[i:i + n].replace('"', '""') + '"' for i in range(0, len(s), n)] or ['""']


def _cadeia(termos: list[str], recuo: str = "    ") -> str:
    if len(termos) > DAX_ITENS_MAX:
        grupos = [termos[i:i + DAX_GRUPO] for i in range(0, len(termos), DAX_GRUPO)]
        return f"\n{recuo}& ".join("(\n" + recuo + "    " + f"\n{recuo}    & ".join(g) + f"\n{recuo})" for g in grupos)
    return f"\n{recuo}& ".join(termos)


def _termos(partes: list) -> list[str]:
    t = []
    for p in partes:
        if isinstance(p, tuple):
            t.append(p[1])
        else:
            t += _lits(p)
    return t


def _esc(x: str) -> str:
    return D.esc(x)


def _dax_numero(i: int, ident: str, rotulo: str, var: str, tipo: str) -> list[str]:
    n = f"_n{i}"
    linhas = [f"VAR {n} = {_esc(var)}", f'VAR {n}Ng = LEFT ( {n}, 1 ) = "{MENOS}"']
    if tipo == "int":
        linhas += [f'VAR {n}Pre = ""', f'VAR {n}Suf = ""', f"VAR {n}Nuc = {n}"]
    elif tipo == "rs":
        linhas += [
            f'VAR {n}I = SEARCH ( "R$ ", {n}, 1, 0 )',
            f'VAR {n}Pre = IF ( {n}I > 0, LEFT ( {n}, {n}I + 2 ), "" )',
            f"VAR {n}Re = MID ( {n}, LEN ( {n}Pre ) + 1, LEN ( {n} ) )",
            f'VAR {n}Suf = SWITCH ( TRUE (), RIGHT ( {n}Re, 4 ) = " mil", " mil", RIGHT ( {n}Re, 3 ) = " mi", " mi", "" )',
            f"VAR {n}Nuc = LEFT ( {n}Re, LEN ( {n}Re ) - LEN ( {n}Suf ) )",
        ]
    elif tipo == "pct":
        linhas += [
            f'VAR {n}Pre = IF ( LEFT ( {n}, 1 ) IN {{ "{MENOS}", "+" }}, LEFT ( {n}, 1 ), "" )',
            f'VAR {n}Suf = IF ( RIGHT ( {n}, 1 ) = "%", "%", "" )',
            f"VAR {n}Nuc = MID ( {n}, LEN ( {n}Pre ) + 1, LEN ( {n} ) - LEN ( {n}Pre ) - LEN ( {n}Suf ) )",
        ]
    linhas += [
        f'VAR {n}S = SUBSTITUTE ( SUBSTITUTE ( {n}Nuc, ".", "" ), ",", "" )',
        f"VAR {n}T = IFERROR ( VALUE ( {n}S ), -1 )",
        f'VAR {n}Num = LEN ( {n}S ) > 0 && {n}T >= 0 && FORMAT ( {n}T, REPT ( "0", LEN ( {n}S ) ) ) = {n}S',
        f"VAR {n}Ok = {n}Num && {n}T >= {C.T_MINIMO}",
        f'VAR {n}D = IF ( CONTAINSSTRING ( {n}Nuc, "," ), LEN ( {n}Nuc ) - SEARCH ( ",", {n}Nuc ), 0 )',
        f'VAR {n}M = IF ( CONTAINSSTRING ( {n}Nuc, "." ), "#,##0", "0" ) & IF ( {n}D > 0, "." & REPT ( "0", {n}D ) )',
        f"VAR {n}PreH = IF ( {n}Pre = \"\", \"\", \"<span class='un'>\" & {n}Pre & \"</span>\" )",
        f"VAR {n}SufH = IF ( {n}Suf = \"\", \"\", \"<span class='un'>\" & {n}Suf & \"</span>\" )",
        f"VAR {n}Od =",
        "    SWITCH (",
        "        TRUE (),",
        f"        NOT {n}Num, {n},",
        f"        NOT {n}Ok, \"<o-d><o-v>\" & {n}PreH & {n}Nuc & {n}SufH & \"</o-v></o-d>\",",
        f"        \"<o-d><o-v>\" & {n}PreH & {n}Nuc & {n}SufH & \"</o-v><o-w aria-hidden='true'><o-t>\"",
        "            & CONCATENATEX (",
        "                _odQ,",
        f"                \"<span\" & IF ( [@odk] >= {C.PASSOS - 1}, \" class='pr'\", \"\" ) & \">\" & {n}PreH",
        f"                    & IF ( [@odk] = {C.PASSOS}, {n}Nuc, FORMAT ( ROUND ( {n}T * [@odf] / 1000, 0 ) "
        f"/ POWER ( 10, {n}D ), {n}M, \"pt-BR\" ) )",
        f"                    & {n}SufH & \"</span>\",",
        "                UNICHAR ( 10 ),",
        "                [@odk], ASC",
        "            )",
        "            & \"</o-t></o-w></o-d>\"",
        "    )",
    ]
    chips = " & _chips" if ident == "obras" else ""
    ap = {"obras": "_apObras", "resultado": "_apRes", "fisico": "_apFis", "desembolso": "_apDes",
          "sem_estoque": "_apSem"}[ident]
    linhas.append(
        f"VAR _blk{i} = \"<div class='nm n{i} b' data-ind='{ident}'><p class='ro'>{rotulo}</p><div class='vl'>"
        f"<p class='v\" & IF ( {n}Ng, \" ng\", \"\" ) & \"'>\" & {n}Od & \"</p>\"{chips} & \"</div><p class='ap'>\" "
        f"& {ap} & \"</p></div>\"")
    return linhas


def _ng(v: str) -> str:
    return f"IF ( LEFT ( {v}, 1 ) = \"{MENOS}\", \"<span class='ng'>\" & {v} & \"</span>\", {v} )"


def dax_html() -> str:
    textos = [
        f"VAR _mesH = {_esc('_mes')}",
        f"VAR _mesAntH = {_esc('_mesAnt')}",
        "VAR _c = _crit + 0",
        "VAR _a = _aten + 0",
        "VAR _e = _est + 0",
        "VAR _p = _pend + 0",
        "VAR _chips =",
        "    \"<div class='cs'>\"",
        "        & IF ( _c > 0, \"<span class='ch c2'><i></i>\" & FORMAT ( _c, \"0\" ) "
        "& IF ( _c = 1, \" crítica\", \" críticas\" ) & \"</span>\" )",
        "        & IF ( _a > 0, \"<span class='ch c1'><i></i>\" & FORMAT ( _a, \"0\" ) & \" em atenção</span>\" )",
        "        & IF ( _e > 0, \"<span class='ch c0'><i></i>\" & FORMAT ( _e, \"0\" ) "
        "& IF ( _e = 1, \" estável\", \" estáveis\" ) & \"</span>\" )",
        "        & IF ( _p > 0, \"<span class='ch cm'><i></i>\" & FORMAT ( _p, \"0\" ) "
        "& IF ( _p = 1, \" pendente\", \" pendentes\" ) & \"</span>\" )",
        "        & \"</div>\"",
    ]
    for v in ("_o2", "_r2", "_r3", "_f2", "_f3", "_d2", "_s2"):
        textos.append(f"VAR {v}H = {_esc(v)}")
    textos += [
        'VAR _apObras = _o2H & " em orçamento"',
        "VAR _apRes =",
        f"    {_ng('_r2H')}",
        '        & " do orçamento · "',
        f'        & IF ( ISBLANK ( _ant ), "{SEM_ANTERIOR}", {_ng("_r3H")} & " sobre " & _mesAntH )',
        f'VAR _apFis = _f2H & " previsto · " & {_ng("_f3H")}',
        'VAR _apDes = _d2H & " previsto"',
        'VAR _apSem = _s2H & " pagos e ainda não aplicados"',
        C.bloco_tabela().rstrip(),
    ]
    for i, (ident, rotulo, var, tipo) in enumerate(NUMEROS):
        textos += _dax_numero(i, ident, rotulo, var, tipo)
    return "\n".join(
        ["-- 1 · Leituras"] + [f"VAR {v} = [{m}]" for v, m in LEITURAS]
        + ["-- 2 · Textos"] + textos
        + ["-- 4 · Marcação", "RETURN", "    " + _cadeia(_termos(corpo_partes()))])


def dax_alt() -> str:
    return "\n".join([
        "-- 1 · Leituras",
        "VAR _mes = [Mês de referência · longo]",
        "VAR _crit = [Nota · carteira · obras críticas · ref]",
        "VAR _aten = [Nota · carteira · obras em atenção · ref]",
        "VAR _est = [Nota · carteira · obras estáveis · ref]",
        "VAR _pend = [Nota · carteira · obras pendentes · ref]",
        "VAR _o1 = [Capa · obras · valor (texto)]",
        "VAR _r1 = [Capa · resultado · valor (texto)]",
        "VAR _f1 = [Capa · físico · valor (texto)]",
        "VAR _d1 = [Capa · desembolso · valor (texto)]",
        "VAR _s1 = [Capa · sem estoque · valor (texto)]",
        "-- 2 · Textos",
        "VAR _c = _crit + 0",
        "VAR _a = _aten + 0",
        "VAR _e = _est + 0",
        "VAR _p = _pend + 0",
        'VAR _status = FORMAT ( _c, "0" ) & IF ( _c = 1, " crítica, ", " críticas, " ) & FORMAT ( _a, "0" ) '
        '& " em atenção, " & FORMAT ( _e, "0" ) & IF ( _e = 1, " estável, ", " estáveis, " ) & FORMAT ( _p, "0" ) '
        '& IF ( _p = 1, " pendente na nota", " pendentes na nota" )',
        "-- 4 · Marcação",
        "RETURN",
        '    "Capa do Criticidade de Obras, " & _mes & ": " & _o1 & IF ( _o1 = "1", " obra (", " obras (" ) & _status',
        '        & "), resultado " & _r1',
        '        & ", físico " & _f1 & ", desembolso " & _d1 & ", sem estoque " & _s1',
        '        & ". Entrar no painel e os 5 cartões abrem as telas."',
    ])


def medidas_desenho() -> list[Medida]:
    css = css_capa()
    return [
        Medida("CO Capa · CSS fontes", "Capa", "texto",
               "Barlow 400, 600 e 700 (woff2 do mockup, base64) como 'Barlow U', só para a capa. Licença OFL "
               "(mockup/fonts/OFL-Barlow.txt).",
               "-- 4 · Marcação\n" + _cadeia(_lits(css_fontes(), 180), "")),
        Medida("CO Capa · CSS", "Capa", "texto",
               "Folha de estilo do visual da capa (formatação condicional do HTML Content): fontes, palco 1920 × 1080 "
               "em calc(var(--u)*N), faixa do filme, base, cartões, a linha do tempo de 33 s (régua, recorte da "
               "identidade, números e odômetro) e os estados uo-espera, uo-parado (pôster com os 5 números), "
               "movimento reduzido, impressão e o botão de pausar.",
               "-- 4 · Marcação\n[CO Capa · CSS fontes]\n    & " + _cadeia(_lits(css, 180))),
        Medida("CO Capa · HTML", "Capa", "texto",
               "Capa do painel num lote só: faixa do filme (MP4 publicado no GitHub Pages, sincronizado pelo JS com a "
               "linha do tempo do HTML), identidade, régua, os 5 números com odômetro (textos de Capa\\Contas, a regra "
               "dos cartões da T1), base com a panorâmica, título, CTA e cartões (desenho; os cliques são botões "
               "nativos) e o botão de pausar o filme. Só lê contas; não calcula.",
               dax_html()),
        Medida("CO Capa · ALT", "Capa", "texto",
               "Texto alternativo da capa: mês, obras por status e os 4 números principais (≤ 250 caracteres).",
               dax_alt()),
    ]


# ========================================================================================== espelho Python (prova)
def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#39;")


def _ng_py(s: str) -> str:
    return f"<span class='ng'>{s}</span>" if s[:1] == MENOS else s


def _separa(t: str, tipo: str) -> tuple[str, str, str]:
    if tipo == "int":
        return "", t, ""
    if tipo == "rs":
        i = t.find("R$ ")
        pre = t[:i + 3] if i >= 0 else ""
        re_ = t[len(pre):]
        suf = " mil" if re_[-4:].lower() == " mil" else (" mi" if re_[-3:].lower() == " mi" else "")
        return pre, re_[:len(re_) - len(suf)], suf
    pre = t[:1] if t[:1] in (MENOS, "+") else ""
    suf = "%" if t[-1:] == "%" else ""
    return pre, t[len(pre):len(t) - len(suf)], suf


def od_capa(t: str, tipo: str) -> str:
    """Espelho do odômetro da capa (o DAX de _dax_numero) para o texto t já escapado."""
    pre, nuc, suf = _separa(t, tipo)
    s = nuc.replace(".", "").replace(",", "")
    num = bool(s) and s.isascii() and s.isdigit()
    ph = f"<span class='un'>{pre}</span>" if pre else ""
    sh = f"<span class='un'>{suf}</span>" if suf else ""
    if not num:
        return t
    q = C.quadros(nuc)
    if q is None:
        return f"<o-d><o-v>{ph}{nuc}{sh}</o-v></o-d>"
    linhas = "\n".join(f"<span{' class=' + chr(39) + 'pr' + chr(39) if k >= C.PASSOS - 1 else ''}>{ph}{x}{sh}</span>"
                       for k, x in enumerate(q))
    return f"<o-d><o-v>{ph}{nuc}{sh}</o-v><o-w aria-hidden='true'><o-t>{linhas}</o-t></o-w></o-d>"


def valores_vars(v: dict) -> dict:
    """VARs do palco a partir das leituras (o que o motor devolve): v = {'_mes': …, '_o1': …, '_crit': 1, …}."""
    c, a, e, pe = (int(v.get(k) or 0) for k in ("_crit", "_aten", "_est", "_pend"))
    chips = "<div class='cs'>"
    if c > 0:
        chips += f"<span class='ch c2'><i></i>{c}{' crítica' if c == 1 else ' críticas'}</span>"
    if a > 0:
        chips += f"<span class='ch c1'><i></i>{a} em atenção</span>"
    if e > 0:
        chips += f"<span class='ch c0'><i></i>{e}{' estável' if e == 1 else ' estáveis'}</span>"
    if pe > 0:
        chips += f"<span class='ch cm'><i></i>{pe}{' pendente' if pe == 1 else ' pendentes'}</span>"
    chips += "</div>"
    h = {k: esc(v[k]) for k in ("_o2", "_r2", "_r3", "_f2", "_f3", "_d2", "_s2")}
    ap = {
        "obras": h["_o2"] + " em orçamento",
        "resultado": _ng_py(h["_r2"]) + " do orçamento · "
                     + (SEM_ANTERIOR if v.get("_ant") is None else _ng_py(h["_r3"]) + " sobre " + esc(v["_mesAnt"])),
        "fisico": h["_f2"] + " previsto · " + _ng_py(h["_f3"]),
        "desembolso": h["_d2"] + " previsto",
        "sem_estoque": h["_s2"] + " pagos e ainda não aplicados",
    }
    out = {"_mesH": esc(v["_mes"])}
    for i, (ident, rotulo, var, tipo) in enumerate(NUMEROS):
        t = esc(v[var])
        ng = " ng" if t[:1] == MENOS else ""
        out[f"_blk{i}"] = (f"<div class='nm n{i} b' data-ind='{ident}'><p class='ro'>{rotulo}</p><div class='vl'>"
                           f"<p class='v{ng}'>{od_capa(t, tipo)}</p>{chips if ident == 'obras' else ''}</div>"
                           f"<p class='ap'>{ap[ident]}</p></div>")
    return out


def html_capa(v: dict) -> str:
    vals = valores_vars(v)
    return "".join(vals[p[1]] if isinstance(p, tuple) else p for p in corpo_partes())


def alt_capa(v: dict) -> str:
    c, a, e, pe = (int(v.get(k) or 0) for k in ("_crit", "_aten", "_est", "_pend"))
    st = (f"{c}{' crítica, ' if c == 1 else ' críticas, '}{a} em atenção, {e}{' estável, ' if e == 1 else ' estáveis, '}"
          f"{pe}{' pendente na nota' if pe == 1 else ' pendentes na nota'}")
    obras = " obra (" if v["_o1"] == "1" else " obras ("
    return (f"Capa do Criticidade de Obras, {v['_mes']}: {v['_o1']}{obras}{st}), resultado {v['_r1']}, físico {v['_f1']}, "
            f"desembolso {v['_d1']}, sem estoque {v['_s1']}. Entrar no painel e os 5 cartões abrem as telas.")


# Os valores de set/26 dos dados fictícios de Natal (somados do gabarito dados/_gabarito/), como o motor devolve as
# leituras; estados pela nota prévia de set/26 (REDINHA e POTENGI críticas, JANGADA em atenção, 4 estáveis). O --previa e
# o --fundo usam este dict: o fundo da página (wp-capa.jpg) é o pôster da cena final com estes 5 números.
SET26 = {
    "_mes": "setembro de 2026", "_mesAnt": "agosto", "_ant": -1510158.69, "_crit": 2, "_aten": 1, "_est": 4, "_pend": 0,
    "_o1": "7", "_o2": "R$ 203,4 mi", "_r1": f"{MENOS}R$ 1,89 mi", "_r2": f"{MENOS}0,93%", "_r3": f"{MENOS}R$ 376 mil",
    "_f1": "63,4%", "_f2": "68,5%", "_f3": f"{MENOS}5,1 p.p.", "_d1": "R$ 10,02 mi", "_d2": "R$ 9,77 mi",
    "_s1": f"{MENOS}R$ 4,86 mi", "_s2": "R$ 2,97 mi",
}

# ========================================================================================== prévia local e fundo
ARVORE = ("<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><title>{titulo}</title>"
          "<meta name='viewport' content='width=device-width, initial-scale=1'><style>{css}</style></head><body>"
          "<div id='sandbox-host'><div id='htmlViewer'><div class='os-padding'><div class='os-viewport'>"
          "<div class='os-content'><div id='htmlContent'><div class='htmlViewerEntry'><div>{html}</div></div></div>"
          "</div></div></div></div></div></body></html>")


def previa(html: str, css: str, titulo: str = "Capa · prévia") -> str:
    """A árvore real do HTML Content (L037) com a folha do visual e o conteúdo da medida."""
    return ARVORE.format(titulo=titulo, css=css, html=html)


def gravar_previa(v: dict | None = None, nome: str = "previa-capa.html", local: bool = False) -> Path:
    """local=True: as mídias pelos arquivos da máquina (antes da publicação); só nesta cópia, nunca na medida."""
    pasta = QA / "previa"
    pasta.mkdir(parents=True, exist_ok=True)
    arq = pasta / nome
    texto = previa(html_capa(v or SET26), css_fontes() + css_capa())
    arq.write_text(com_midias_locais(texto) if local else texto, encoding="utf-8", newline="\n")
    return arq


def render_fundo(v: dict | None = None, local: bool = False) -> dict:
    """Fundo da página (V4I-01 do painel de referência): o estado parado da capa — pôster da cena final na faixa e os 5 números de
    set/26 — como JPEG 1920 × 1080. É o que o PDF/PPT mostra quando o HTML Content não é exportado e o que aparece
    enquanto o visual carrega."""
    from PIL import Image
    from playwright.sync_api import sync_playwright
    arq = gravar_previa(v, "previa-capa-fundo.html", local)
    poster = ARQUIVO_LOCAL["poster"].resolve().as_uri() if local else POSTER
    png = QA / "previa" / "fundo-capa.png"
    with sync_playwright() as pw:
        nav = pw.chromium.launch(channel="msedge", headless=True)
        ctx = nav.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=1, reduced_motion="reduce")
        pg = ctx.new_page()
        pg.goto(arq.resolve().as_uri())
        pg.wait_for_function("document.documentElement.classList.contains('uo-parado')", timeout=15000)
        pg.evaluate("document.fonts.ready")
        pg.wait_for_function("Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)", timeout=30000)
        # o pôster é fundo CSS da faixa: espera a imagem carregar antes da foto
        pg.evaluate(f"new Promise(r => {{ const i = new Image(); i.onload = i.onerror = r; i.src = {poster!r}; }})")
        pg.wait_for_timeout(1200)
        pg.screenshot(path=str(png))
        ctx.close()
        nav.close()
    im = Image.open(png).convert("RGB")
    if im.size != (1920, 1080):
        raise SystemExit(f"fundo com {im.size}")
    FUNDO.parent.mkdir(parents=True, exist_ok=True)
    im.save(FUNDO, "JPEG", quality=90, optimize=True, progressive=True)
    return {"arquivo": str(FUNDO.relative_to(RAIZ)), "bytes": FUNDO.stat().st_size}


# ================================================================================================= main
def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--previa", action="store_true")
    ap.add_argument("--fundo", action="store_true")
    ap.add_argument("--local", action="store_true",
                    help="prévia e fundo com as mídias locais (antes de publicar); a medida segue com os endereços")
    a = ap.parse_args(argv)
    medidas = medidas_contas() + medidas_desenho()
    rc = gravar(medidas, DESTINO, GERADO)
    html = html_capa(SET26)
    css = css_capa()
    fontes = css_fontes()
    print(f"lote único (CO Capa · HTML; set/26): {len(html):,} caracteres (teto {LOTE_MAX:,})".replace(",", "."))
    print(f"CO Capa · CSS: {len(css):,} + fontes {len(fontes):,} = {len(css) + len(fontes):,} caracteres"
          .replace(",", "."))
    print(f"ALT (set/26): {len(alt_capa(SET26))} caracteres · {alt_capa(SET26)}")
    termos = len(_termos(corpo_partes()))
    print(f"termos na cadeia do palco: {termos}")
    if len(html) >= LOTE_MAX or len(alt_capa(SET26)) > 250:
        print("[ERRO] lote ou ALT acima do teto")
        rc = 2
    if a.previa:
        print("prévia:", gravar_previa(local=a.local))
    if a.fundo:
        print("fundo:", render_fundo(local=a.local))
    return rc


if __name__ == "__main__":
    sys.exit(main())

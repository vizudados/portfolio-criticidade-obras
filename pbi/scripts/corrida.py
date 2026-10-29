# -*- coding: utf-8 -*-
"""corrida — animação "racing" das barras, colunas e linhas do painel Criticidade de Obras (HTML Content 2.0, renderMode
rebuild: o DOM é refeito a cada atualização e a janela do visual guarda a memória).

Contrato (marcação que o DAX emite; o JS nunca calcula número, só anima a geometria que o DAX já escreveu inline):
  · data-rk="<chave>"       elemento que corre (barra, segmento de coluna); a chave é estável entre atualizações
                            (obra, indicador, mês|status). Lê do style inline as propriedades de data-rp.
  · data-rp="width"         propriedades animadas (padrão width; colunas: "top,height").
  · data-r0-<prop>="0px"    valor de partida na PRIMEIRA aparição (padrão 0px; coluna empilhada parte da base).
  · data-rd="120"           atraso em ms só na primeira aparição (a cascata da largada, por posição).
  · data-rr="<chave>"       linha que pode trocar de lugar (ranking): desliza da posição anterior até a nova (FLIP).
  · path[data-rl]           linha de SVG que se desenha da esquerda para a direita (stroke-dasharray) na primeira vez; aceita data-rd (atraso em ms).
Primeira aparição: cresce do zero com a cascata. Atualização (filtro, mês): sai do valor anterior para o novo, sem
cascata; linha que mudou de posição desliza. Sem JS, sem Web Animations ou com movimento reduzido: o estado final,
que é o próprio HTML. Página escondida: toda animação vai ao fim (FIM_OCULTO_JS); e, de todo jeito, 2,5 s
depois de criadas (REDE_JS). Sem '//', sem '--' e com ';' em todo comando (os portões dos geradores).
"""
from __future__ import annotations

MARCA = "/*corrida*/"
# Página escondida (Desktop minimizado ou coberto, foto, exportação): o navegador para o relógio das animações e o que
# fica na tela é o quadro do meio (número contando, barra pela metade, célula ainda clara). Então, com a página
# escondida, toda animação do documento vai direto ao fim (finish), na hora em que é criada e quando a página some.
# Rede de segurança (retorno das fotos, 28/10/2026): a janela coberta segue "visible" e o relógio das animações para
# do mesmo jeito; um setTimeout de REDE_MS depois de criar as animações (o timer roda mesmo com a janela coberta, no
# mínimo uma vez por segundo) leva ao fim tudo o que ainda estiver rodando. Protege também as exportações do serviço
# (PDF, PowerPoint, assinaturas), que fotografam o relatório. A animação infinita recusa finish: cada uma num try.
REDE_MS = 2500
FIM_OCULTO_JS = (
    "var Fz=function(){try{if(d.getAnimations){d.getAnimations().forEach(function(a){try{a.finish();}catch(y){}});}}"
    "catch(x){}};"
    "if(!W.__fimO){W.__fimO=1;d.addEventListener('visibilitychange',function(){if(d.visibilityState==='hidden'){Fz();}});}"
)
REDE_JS = f"setTimeout(Fz,{REDE_MS});"
DURACAO_MS = 700
EASING = "cubic-bezier(.2,.7,.2,1)"
PASSO_MS = 60                  # cascata da largada: atraso por posição


def js_texto() -> str:
    return (
        f"<script>{MARCA}(function(){{try{{var W=window,d=document;{FIM_OCULTO_JS}if(W.__rcP){{return;}}W.__rcP=1;"
        "setTimeout(function(){W.__rcP=0;try{"
        "var M=W.__rcM||{},N={},R=W.__rcR||{},Q={},"
        "red=!!(W.matchMedia&&W.matchMedia('(prefers-reduced-motion: reduce)').matches),"
        f"ez='{EASING}',du={DURACAO_MS},sl=Array.prototype.slice;"
        "sl.call(d.querySelectorAll('[data-rk]')).forEach(function(e){"
        "var k=e.getAttribute('data-rk'),ps=(e.getAttribute('data-rp')||'width').split(','),"
        "novo=!Object.prototype.hasOwnProperty.call(M,k),vs={},kf={},muda=false;"
        "ps.forEach(function(p){var v=e.style[p]||'0px';vs[p]=v;"
        "var de=novo?(e.getAttribute('data-r0-'+p)||'0px'):(M[k][p]||v);if(de!==v){muda=true;}kf[p]=[de,v];});"
        "N[k]=vs;if(red||!e.animate||!muda){return;}"
        "e.animate(kf,{duration:du,delay:novo?(+e.getAttribute('data-rd')||0):0,easing:ez,fill:'backwards'});});"
        "sl.call(d.querySelectorAll('[data-rr]')).forEach(function(e){"
        "var k=e.getAttribute('data-rr'),t=e.getBoundingClientRect().top;Q[k]=t;"
        "if(!red&&e.animate&&Object.prototype.hasOwnProperty.call(R,k)&&Math.abs(R[k]-t)>1){"
        "e.animate([{transform:'translateY('+(R[k]-t)+'px)'},{transform:'none'}],{duration:du,easing:ez});}});"
        "sl.call(d.querySelectorAll('path[data-rl]')).forEach(function(e){"
        "if(red||!e.getTotalLength||!e.animate){return;}var L=e.getTotalLength();"
        "e.style.strokeDasharray=L;"
        "e.animate([{strokeDashoffset:L},{strokeDashoffset:0}],{duration:du+300,delay:(+e.getAttribute('data-rd')||0),"
        "easing:ez,fill:'backwards'});});"
        f"W.__rcM=N;W.__rcR=Q;if(d.visibilityState==='hidden'){{Fz();}}{REDE_JS}}}catch(x){{}}}},0);}}catch(x){{}}}})();</script>"
    )


def atributos(chave: str, atraso_ms: str | None = None, props: str | None = None,
              partida: dict[str, str] | None = None) -> str:
    """Trecho DAX (concatenação) com os atributos data-r* de um elemento que corre. `chave` e `atraso_ms` são
    expressões DAX (texto e inteiro); `props`/`partida` são fixos."""
    s = "\" data-rk='\" & " + chave + " & \"'"
    if props:
        s += f" data-rp='{props}'"
    for p, v in (partida or {}).items():
        s += f" data-r0-{p}='{v}'"
    if atraso_ms:
        s += "\" & \" data-rd='\" & " + atraso_ms + " & \"'"
    return s + "\""

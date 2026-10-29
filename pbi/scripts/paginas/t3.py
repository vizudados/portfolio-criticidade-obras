# -*- coding: utf-8 -*-
"""Tela 03 · Avanço físico — a obra está no ritmo do que foi previsto?

Redesenho v2 (Figma FjBWDk5odF9HaZ2pwhGosl, página 04 · Redesenho v2, Tela 03 · v2 387:5627, prancheta em 300,12;
geometria em pbi/spec/redesenho/t03.md §2). Sem "FOLHA 03" no cabeçalho. Cartões em y 109 (302 × 140, x 352 · 654 · 955
· 1257 · 1558). Painéis no canvas: Curva S 352,273 900 × 370 · PPC mês a mês 1292,273 568 × 290 (F3, no lugar do Ritmo
do mês) · Avanço das obras 1292,603 568 × 437 · Linha do tempo das obras 352,683 900 × 357. Em cada painel um HTML de cabeçalho (subtítulo e
legenda, y 0–54) e o conteúdo a partir de y 68. O papel de parede (Casca v2 · T3 408:11772 →
pbi/spec/casca/_fonte_v2/T3.svg) traz só o estático: títulos, "?", traços, divisórias e o fundo do cartão escuro.

Curva S: um HTML sem granularidade desenha o gráfico e, por cima, um HTML com granularidade dMes[Mes] de colunas
invisíveis é o alvo do mouse que abre o tooltip do mês (L012). Linha do tempo: a grade embaixo e as obras por cima.
"""
from __future__ import annotations

import pbip_lib as lib
from pbip_lib import Visual

Z = lib.CAMADAS["conteudo"]
# F3 (docs/08 §5): atraso em meses (o escuro) · executado acumulado (previsto e desvio no contexto) · no mês · PPC do
# mês · término projetado (com a entrega contratual e os 180 dias)
CARTOES = [("Atraso", "T3 · Cartão atraso · HTML", "Atraso da obra em foco em meses e os pontos do item prazo da nota"),
           ("Executado", "T3 · Cartão executado · HTML", "Executado acumulado da obra em foco, com o previsto e o desvio"),
           ("NoMes", "T3 · Cartão no mês · HTML", "Executado e previsto da obra em foco só no mês de referência"),
           ("Ppc", "T3 · Cartão PPC · HTML", "PPC do mês da obra em foco, a meta e os pontos do item PPC da nota"),
           ("Termino", "T3 · Cartão término · HTML", "Término projetado da obra em foco, a entrega contratual e os 180 dias")]
CARTAO_X = [352, 654, 955, 1257, 1558]
CARTAO_Y, CARTAO_W, CARTAO_H = 109, 302, 140
CURVA = (352, 273, 900, 370)
PPC = (1292, 273, 568, 290)          # PPC mês a mês (era o Ritmo do mês)
AVANCO = (1292, 603, 568, 437)
LINHA = (352, 683, 900, 357)
CAB_H = 54          # cabeçalho HTML do painel (legenda na linha do título e subtítulo em y 32)
CONTEUDO_Y = 68     # conteúdo do painel


def declarar(ctx):
    v = []
    for i, (chave, medida, alt) in enumerate(CARTOES):
        v.append(lib.visual_html(f"T3_Kpi_{chave}", CARTAO_X[i], CARTAO_Y, CARTAO_W, CARTAO_H, medida,
                                 folha_de_estilo="T3 · Cartão · CSS", alt=alt + " (passe o mouse para ver a regra)",
                                 tab=100 + i))
    # ---- Curva S
    cx, cy, cw, _ = CURVA
    v.append(lib.visual_html("T3_Curva_Cabecalho", cx, cy, cw - 42, CAB_H, "T3 · Curva S · HTML cabeçalho",
                             folha_de_estilo="T3 · Painel · CSS cabeçalho",
                             alt="Meses da curva S e legenda: executado, previsto e executado abaixo do previsto",
                             tab=110))
    v.append(lib.visual_html("T3_Curva_Grafico", cx, cy + CONTEUDO_Y, cw, 302, "T3 · Curva S · HTML gráfico",
                             folha_de_estilo="T3 · Curva S · CSS", z=Z,
                             alt="Curva S da obra em foco: previsto e executado acumulados, mês a mês, em % do orçamento",
                             tab=111))
    v.append(lib.visual_html(
        "T3_Curva_Meses", cx, cy + CONTEUDO_Y, 860, 302, "T3 · Curva S · HTML mês", granularidade=("dMes", "Mes"),
        ordenacao=[(lib.campo_coluna_expr("dMes", "Mes"), "Ascending")], folha_de_estilo="T3 · Curva S · CSS mês",
        tooltip_pagina="ttT3Curva", z=Z + 10,
        alt="Meses da curva S: passe o mouse para ver o acumulado, o ritmo e o dinheiro do mês", tab=112))
    # ---- PPC mês a mês (era o Ritmo do mês)
    rx, ry, rw, rh = PPC
    v.append(lib.visual_html("T3_Ppc_Cabecalho", rx, ry, rw - 42, CAB_H, "T3 · PPC · HTML cabeçalho",
                             folha_de_estilo="T3 · Painel · CSS cabeçalho",
                             alt="PPC mês a mês: a meta, a janela e a legenda das cores pelos pontos do item PPC", tab=119))
    v.append(lib.visual_html(
        "T3_Ppc_Colunas", rx, ry + CONTEUDO_Y, rw, rh - CONTEUDO_Y, "T3 · PPC · HTML coluna",
        granularidade=("dMes", "Mes"), ordenacao=[(lib.campo_coluna_expr("dMes", "Mes"), "Ascending")],
        folha_de_estilo="T3 · PPC · CSS", tooltip_pagina="ttT3Ppc",
        alt="PPC da obra em foco mês a mês, na cor dos pontos do item PPC da nota, com a linha da meta", tab=120))
    # ---- Avanço das obras
    ax, ay, aw, _ = AVANCO
    v.append(lib.visual_html("T3_Avanco_Cabecalho", ax, ay, aw - 42, CAB_H, "T3 · Avanço · HTML cabeçalho",
                             folha_de_estilo="T3 · Painel · CSS cabeçalho",
                             alt="Avanço das obras: executado e previsto acumulados e o desvio em pontos percentuais",
                             tab=129))
    v.append(lib.visual_html(
        "T3_Avanco_Lista", ax, ay + 72, aw, 294, "T3 · Avanço · HTML linha", granularidade=("dObra", "Obra"),
        ordenacao=[(lib.campo_medida_expr("T3 · Avanço · posição"), "Ascending")], tooltips=["T3 · Avanço · posição"],
        folha_de_estilo="T3 · Avanço · CSS", tooltip_pagina="ttT3Avanco",
        alt="Avanço das obras: executado na cor do item prazo da nota, previsto, a marca e o atraso em meses; a "
            "obra em foco destacada", tab=130))
    v.append(lib.visual_html("T3_Avanco_Legenda", ax, ay + 368, aw, 61, "T3 · Avanço · HTML legenda",
                             folha_de_estilo="T3 · Avanço · CSS",
                             alt="Legenda: a barra é o executado na cor do item prazo da nota; o traço é o previsto; o "
                                 "número é o atraso em meses",
                             tab=131))
    # ---- Linha do tempo das obras
    lx, ly, lw, _ = LINHA
    v.append(lib.visual_html("T3_Linha_Cabecalho", lx, ly, lw - 42, CAB_H, "T3 · Linha do tempo · HTML cabeçalho",
                             folha_de_estilo="T3 · Painel · CSS cabeçalho",
                             alt="Linha do tempo das obras: início, término previsto, executado e previsto", tab=139))
    v.append(lib.visual_html("T3_Linha_Grade", lx, ly + CONTEUDO_Y, lw, 289, "T3 · Linha do tempo · HTML grade",
                             folha_de_estilo="T3 · Linha do tempo · CSS grade", z=Z,
                             alt="Anos da linha do tempo, mês de referência e legenda do item prazo da nota",
                             tab=140))
    v.append(lib.visual_html(
        "T3_Linha_Obras", lx, ly + 96, lw, 230, "T3 · Linha do tempo · HTML obra", granularidade=("dObra", "Obra"),
        ordenacao=[(lib.campo_medida_expr("T3 · Linha do tempo · posição"), "Ascending")],
        tooltips=["T3 · Linha do tempo · posição"], folha_de_estilo="T3 · Linha do tempo · CSS",
        tooltip_pagina="ttT3Linha", z=Z + 10,
        alt="Linha do tempo das obras: início, término previsto, executado na cor do item prazo da nota, previsto, o "
            "término projetado e os 180 dias depois da entrega; tracejadas as obras a entrar", tab=141))
    return [Visual("T3", d) for d in v]

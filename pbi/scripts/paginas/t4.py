# -*- coding: utf-8 -*-
"""Tela 04 · Resultado no tempo — está piorando? Gastou fora do previsto no mês e justificou?

Redesenho v2 (07/10/2026): Figma FjBWDk5odF9HaZ2pwhGosl, página 04 · Redesenho v2 (372:685), componente Tela 04 · v2
387:5688 (prancheta em 300,12); geometria no canvas em pbi/spec/redesenho/t04.md §2. Cartões em y 109 (302 × 140;
x 352 · 654 · 955 · 1257 · 1558). Fase 5 (07/10/2026): os dois gráficos de colunas com a mesma largura à esquerda e
a coluna da direita comprimida — Resultado da carteira, mês a mês 352,273 · 1068 × 380 (gráfico de y 341, 1068 × 312);
Desembolso da carteira 352,693 · 1068 × 347 (gráfico de y 761, 1068 × 279); Resultado por obra 1460,273 · 400 × 380
(subtítulo em y 305, cabeçalhos em y 341, linhas de 48 a partir de y 365); Desembolso de ago/26 por obra 1460,693 ·
400 × 347 (título em y 693, cabeçalhos em y 761, linhas de 42 a partir de y 785). A tendência por obra e a
justificativa do mês foram para os tooltips das obras. O papel de parede (Casca v2 · T4,
pbi/spec/casca/_fonte_v2/T4.svg → wp-t4.svg pela sessão principal) traz títulos, "?", subtítulos e legendas fixos;
aqui ficam os HTML.

F3 (28/10/2026, docs/08 §5): o cartão "Mês anterior" virou o IDC da carteira; o mês a mês tem uma série (resultado
aplicado) com o traço do resultado da planilha, e subtítulo e legenda em HTML (fundo branco por cima dos fixos da
casca); Resultado por obra e Desembolso por obra viram a tabela Obras no mês, na coluna da direita inteira
(1460,273 · 400 × 767: cabeçalho em y 305, sete linhas de 92 a partir de y 365), com o tooltip da obra do desembolso.
"""
from __future__ import annotations

import pbip_lib as lib
from pbip_lib import Visual

PX, PY = 300, 12          # origem da prancheta
CARTOES = [
    ("Resultado", "T4 · Cartão resultado · HTML", "Resultado da carteira no mês, % do orçamento, obras e orçamento"),
    ("Idc", "T4 · Cartão IDC · HTML", "IDC da carteira, resultado aplicado, variação no mês e obras abaixo de 1"),
    ("SemEstoque", "T4 · Cartão sem estoque · HTML", "Resultado sem estoque e adiantamentos e o que foi pago"),
    ("Desembolso", "T4 · Cartão desembolso · HTML", "Desembolso do mês, desvio sobre o previsto e previsto"),
    ("Justificativas", "T4 · Cartão justificativas · HTML", "Justificativas preenchidas entre as exigidas e as em branco"),
]
CARTAO_X = [352, 654, 955, 1257, 1558]
CARTAO_Y, CARTAO_W, CARTAO_H = 109, 302, 140
POSICAO = "T1 · Obras · posição"      # ordem da nota: mais pontos perdidos primeiro (a mesma lista da Visão geral)
# Obras no mês: sete obras em andamento (set/26) em linhas de 92; a lista vai até o pé (y 1040) com fundo branco


def declarar(ctx):
    v = []
    for i, (chave, medida, alt) in enumerate(CARTOES):
        v.append(lib.visual_html(f"T4_Kpi_{chave}", CARTAO_X[i], CARTAO_Y, CARTAO_W, CARTAO_H, medida,
                                 folha_de_estilo="T4 · Cartões · CSS", alt=alt + " (passe o mouse para ver a regra)",
                                 tab=100 + i))
    # ---- Resultado da carteira, mês a mês (painel 352,273 · 1068 × 380): legenda, subtítulo e o gráfico
    v.append(lib.visual_html("T4_Mes_Legenda", 940, 277, 432, 24, "T4 · Mês a mês · HTML legenda",
                             folha_de_estilo="T4 · Mês a mês · CSS cabeçalho",
                             alt="Legenda: resultado aplicado (barra) e resultado da planilha (traço)", tab=109))
    v.append(lib.visual_html("T4_Mes_Subtitulo", 352, 305, 1030, 24, "T4 · Mês a mês · HTML subtítulo",
                             folha_de_estilo="T4 · Mês a mês · CSS cabeçalho",
                             alt="O que a barra e o traço mostram", tab=109))
    v.append(lib.visual_html(
        "T4_Mes_Colunas", 352, 341, 1068, 312, "T4 · Mês a mês · HTML coluna", granularidade=("dMes", "Mes"),
        ordenacao=[(lib.campo_coluna_expr("dMes", "Mes"), "Ascending")], folha_de_estilo="T4 · Mês a mês · CSS",
        tooltip_pagina="ttT4Mes",
        alt="Resultado aplicado da carteira mês a mês, com o traço do resultado da planilha, até o mês de referência",
        tab=110))
    # ---- Obras no mês (F3: a coluna da direita inteira, 1460,273 · 400 × 767)
    v.append(lib.visual_html("T4_Obras_Cabecalho", 1460, 305, 400, 56, "T4 · Obras · HTML cabeçalho",
                             folha_de_estilo="T4 · Obras · CSS",
                             alt="Mês de referência e os nomes das colunas da tabela Obras no mês", tab=120))
    v.append(lib.visual_html(
        "T4_Obras_Lista", 1460, 365, 400, 675, "T4 · Obras · HTML linha",
        granularidade=("dObra", "Obra"), ordenacao=[(lib.campo_medida_expr(POSICAO), "Ascending")], tooltips=[POSICAO],
        folha_de_estilo="T4 · Obras · CSS", tooltip_pagina="ttT4ObraDes",
        alt="Obras no mês: IDC com a marca dos pontos do custo, variação do IDC no mês, desvio de caixa com a marca da "
            "faixa e a justificativa da planilha (passe o mouse numa obra para ver o caixa mês a mês)", tab=121))
    # ---- Desembolso da carteira (painel 352,693 · 1068 × 347)
    v.append(lib.visual_html(
        "T4_DesCart_Colunas", 352, 761, 1068, 279, "T4 · Desembolso · HTML coluna", granularidade=("dMes", "Mes"),
        ordenacao=[(lib.campo_coluna_expr("dMes", "Mes"), "Ascending")], folha_de_estilo="T4 · Desembolso · CSS",
        tooltip_pagina="ttT4MesDes", alt="Previsto e desembolsado da carteira mês a mês, com o desvio", tab=130))
    return [Visual("T4", d) for d in v]

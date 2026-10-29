# -*- coding: utf-8 -*-
"""Tela 02 · Análise crítica — por que a obra tem essa nota? (obra em foco)

F3 (28/10/2026, docs/08 §5), sobre a geometria v2 (Figma FjBWDk5odF9HaZ2pwhGosl, Tela 02 · v2 386:847; prancheta em
300,12): cartões em y 109 (302 × 140) em x 352 · 654 · 955 · 1257 · 1558 (Nota da obra, o escuro · Custo · Resultado ·
Sem estoque · Prazo); Itens da nota 352,273 (548 × 767: subtítulo +32, nove linhas de 76 a partir de +68, eixo
dItemNota) no lugar do quadradinho e do "com e sem estoque"; Como o resultado se forma 940,273 (508 × 350, degraus em
+68); IDC, mês a mês 940,663 (508 × 377: subtítulo +32, colunas +96); A nota, mês a mês 1488,273 (372 × 388, miolo em
+68); Desembolso do mês 1488,701 (372 × 339, miolo +68). O desenho estático (títulos, subtítulos fixos, "?", molduras e
divisórias) está no papel de parede; os títulos novos dos painéis esperam a casca nova da sessão local.
"""
from __future__ import annotations

from pathlib import Path

import pbip_lib as lib
from pbip_lib import Visual

CARTOES = [("Nota", "T2 · Cartão nota da obra · HTML", "Nota da obra e o status (ou pendente com os pontos)"),
           ("Custo", "T2 · Cartão custo · HTML", "Custo: IDC da obra e resultado aplicado"),
           ("Resultado", "T2 · Cartão resultado · HTML", "Resultado da planilha, % do orçamento e o que falta realizar"),
           ("SemEstoque", "T2 · Cartão sem estoque · HTML", "Resultado sem estoque e adiantamentos e o que foi pago"),
           ("Prazo", "T2 · Cartão prazo · HTML", "Prazo: atraso em meses, término projetado e executado")]
CARTAO_X = [352, 654, 955, 1257, 1558]
TOOLTIPS = {"degrau": "ttT2Degrau", "mes": "ttT2Mes", "indicador": "ttT2Indicador"}
ITENS = (352, 273)         # Itens da nota 548 × 767 (era o quadradinho + com e sem estoque)
CAS = (940, 273)           # Como o resultado se forma 508 × 350
MES = (940, 663)           # IDC, mês a mês 508 × 377
NOTA = (1488, 273)         # A nota, mês a mês 372 × 388 (era Itens da nota)
DESEMB = (1488, 701)       # Desembolso do mês 372 × 339


def declarar(ctx):
    # as páginas de tooltip ficam em tt_t2.py; enquanto ele não existe, os visuais saem sem tooltip de página
    com_tt = Path(__file__).with_name("tt_t2.py").is_file()
    tt = {k: (v if com_tt else None) for k, v in TOOLTIPS.items()}
    v = []
    for i, (chave, medida, alt) in enumerate(CARTOES):
        v.append(lib.visual_html(f"T2_Kpi_{chave}", CARTAO_X[i], 109, 302, 140, medida,
                                 folha_de_estilo="T2 · Cartão · CSS", alt=alt + " (passe o mouse para ver a regra)",
                                 tab=100 + i))
    # ---- Itens da nota (no lugar do quadradinho)
    ix, iy = ITENS
    v.append(lib.visual_html("T2_Itens_Subtitulo", ix, iy + 32, 548, 20, "T2 · Itens · HTML subtítulo",
                             folha_de_estilo="T2 · Itens · CSS", alt="Quantos pontos a obra perde na nota", tab=110))
    v.append(lib.visual_html(
        "T2_Itens_Lista", ix, iy + 68, 548, 699, "T2 · Itens · HTML linha",
        granularidade=("dItemNota", "Item"),
        ordenacao=[(lib.campo_medida_expr("T2 · Itens · posição"), "Ascending")], tooltips=["T2 · Itens · posição"],
        folha_de_estilo="T2 · Itens · CSS", tooltip_pagina=tt["indicador"],
        alt="Os nove itens da nota com o valor, a faixa atingida, os pontos e os pontos mês a mês", tab=111))
    # ---- Como o resultado se forma
    v.append(lib.visual_html(
        "T2_Cas_Degraus", CAS[0], CAS[1] + 68, 508, 282, "T2 · Cascata · HTML degrau",
        granularidade=("dDegrau", "Degrau"), ordenacao=[(lib.campo_medida_expr("Cascata · degrau · ordem"), "Ascending")],
        tooltips=["Cascata · degrau · ordem"],
        folha_de_estilo="T2 · Cascata · CSS", tooltip_pagina=tt["degrau"],
        alt="Como o resultado se forma: valor agregado, custo aplicado, resultado aplicado, a realizar e o resultado da planilha",
        tab=130))
    # ---- IDC, mês a mês (era Resultado da obra, mês a mês)
    v.append(lib.visual_html("T2_Mes_Subtitulo", MES[0], MES[1] + 32, 508, 20, "T2 · Mês a mês · HTML subtítulo",
                             folha_de_estilo="T2 · Mês a mês · CSS", alt="A régua e a janela do IDC mês a mês", tab=139))
    v.append(lib.visual_html(
        "T2_Mes_Colunas", MES[0], MES[1] + 96, 508, 281, "T2 · Mês a mês · HTML coluna",
        granularidade=("dMes", "Mes"), ordenacao=[(lib.campo_coluna_expr("dMes", "Mes"), "Ascending")],
        folha_de_estilo="T2 · Mês a mês · CSS", tooltip_pagina=tt["mes"],
        alt="IDC da obra mês a mês, com as linhas de 1,00 e da trava", tab=140))
    # ---- A nota, mês a mês (era Itens da nota)
    v.append(lib.visual_html("T2_Nota_Mes", NOTA[0], NOTA[1] + 68, 372, 300, "T2 · Nota mês a mês · HTML",
                             folha_de_estilo="T2 · Nota mês a mês · CSS",
                             alt="A nota da obra mês a mês, na cor do status, com os limites de atenção e de estável",
                             tab=150))
    # ---- Desembolso do mês
    v.append(lib.visual_html("T2_Des_Html", DESEMB[0], DESEMB[1] + 68, 372, 271, "T2 · Desembolso · HTML",
                             folha_de_estilo="T2 · Desembolso · CSS",
                             alt="Desembolso do mês: previsto, desembolsado, diferença, desvio e justificativa", tab=160))
    return [Visual("T2", d) for d in v]

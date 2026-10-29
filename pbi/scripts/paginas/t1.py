# -*- coding: utf-8 -*-
"""Tela 01 · Visão geral — quais obras e itens da nota pedem atenção neste mês, e por quê?

Geometria v2 (Figma 04 · Redesenho v2, Tela 01 · v2 387:4824, prancheta em 300,12; pbi/spec/redesenho/t01.md §2):
cartões em y 97 da prancheta, 302 × 140 (x 52 · 354 · 655 · 957 · 1258); Obras por criticidade 52,261 · 1004 × 631
(subtítulo em +32; linhas de 88 a partir de +96; cabeçalho de colunas, legenda e regras no papel de parede v2); O que
pesa 1096,261 · 464 × 406 (linhas de 70 a partir de +68); Como os meses evoluíram 1096,707 · 464 × 321 (colunas de +68 a
+274, mês em +284; janela de 1 a 12 meses); faixa-síntese 52,932 · 1004 × 96 (só na largura da lista, aprovado em
07/10/2026). Vão de 40 com divisória creme entre os painéis (no papel de parede).
"""
from __future__ import annotations

import pbip_lib as lib
from pbip_lib import Visual

PX, PY = 300, 12          # origem da prancheta
# F3 (docs/08 §5): um cartão por dimensão. Os nomes dos visuais (T1_Kpi_Resultado, …) ficam: o escuro continua o 2º
CARTOES = [("Obras", "T1 · Cartão obras · HTML", "Obras em andamento, orçamento somado e obras por status da nota"),
           ("Resultado", "T1 · Cartão custo · HTML", "Custo: IDC da carteira, resultado aplicado e obras abaixo de 1"),
           ("Fisico", "T1 · Cartão prazo · HTML", "Prazo: atraso médio em meses e a obra de maior atraso"),
           ("Desembolso", "T1 · Cartão caixa · HTML", "Caixa: desembolso do mês, desvio sobre o previsto e obras fora"),
           ("SemEstoque", "T1 · Cartão canteiro · HTML", "Canteiro: taxa de frequência de acidentes, 1.ª inspeção e NR-18")]


CARTAO_X = (52, 354, 655, 957, 1258)


def declarar(ctx):
    v = []
    for i, (chave, medida, alt) in enumerate(CARTOES):
        v.append(lib.visual_html(f"T1_Kpi_{chave}", PX + CARTAO_X[i], PY + 97, 302, 140, medida,
                                 folha_de_estilo="Comum · CSS cartão", alt=alt + " (passe o mouse para ver a regra)",
                                 tab=100 + i))
    # ---- Obras por criticidade (painel 52,261)
    ox, oy = PX + 52, PY + 261
    v.append(lib.visual_html("T1_Obras_Cabecalho", ox, oy + 32, 600, 20, "T1 · Obras · HTML cabeçalho",
                             folha_de_estilo="T1 · Obras · CSS cabeçalho",
                             alt="Mês de referência e escala da Nota da obra na lista de obras", tab=110))
    v.append(lib.visual_html(
        "T1_Obras_Lista", ox, oy + 96, 1004, 535, "T1 · Obras · HTML linha", granularidade=("dObra", "Obra"),
        ordenacao=[(lib.campo_medida_expr("T1 · Obras · posição"), "Ascending")],
        tooltips=["T1 · Obras · posição"], folha_de_estilo="T1 · Obras · CSS lista", tooltip_pagina="ttT1Obra",
        alt="Obras pela nota: status ou pendente, nota de 0 a 10 e a nota por dimensão em sete quadradinhos", tab=111))
    # ---- Onde a carteira perde pontos (painel 1096,261; F3: eixo dItemNota[Dimensao], 7 linhas de 48)
    px_, py_ = PX + 1096, PY + 261
    v.append(lib.visual_html("T1_Pesa_Subtitulo", px_, py_ + 32, 420, 20, "T1 · Pesa · HTML subtítulo",
                             folha_de_estilo="Comum · CSS base", alt="Quantas obras somam os pontos", tab=120))
    v.append(lib.visual_html(
        "T1_Pesa_Lista", px_, py_ + 68, 464, 338, "T1 · Pesa · HTML linha", granularidade=("dItemNota", "Dimensao"),
        ordenacao=[(lib.campo_medida_expr("T1 · Pesa · posição"), "Ascending")], tooltips=["T1 · Pesa · posição"],
        folha_de_estilo="T1 · Pesa · CSS lista", tooltip_pagina="ttT1Indicador",
        alt="Onde a carteira perde pontos: pontos perdidos somados por dimensão da nota e quantas obras perderam", tab=121))
    # ---- Como os meses evoluíram (painel 1096,707): subtítulo com a janela + o mapa obra × mês (uma entrada por mês)
    sx, sy = PX + 1096, PY + 707
    v.append(lib.visual_html("T1_Semestre_Subtitulo", sx, sy + 32, 420, 20, "T1 · Semestre · HTML subtítulo",
                             folha_de_estilo="Comum · CSS base", alt="Janela mostrada nas colunas", tab=129))
    v.append(lib.visual_html(
        "T1_Semestre_Colunas", sx, sy + 68, 464, 236, "T1 · Semestre · HTML coluna", granularidade=("dMes", "Mes"),
        ordenacao=[(lib.campo_coluna_expr("dMes", "Mes"), "Ascending")], folha_de_estilo="T1 · Semestre · CSS lista",
        tooltip_pagina="ttT1Mes",
        alt="Mapa obra × mês: o status e a nota de cada obra, mês a mês, na janela escolhida até o mês de referência", tab=130))
    # ---- síntese (52,932 · 1004 × 96: só na largura da lista)
    v.append(lib.visual_html("T1_Sintese_Texto", PX + 52, PY + 932, 1004, 96, "T1 · Síntese · HTML",
                             folha_de_estilo="T1 · Síntese · CSS",
                             alt="Leitura do mês: obras por status da nota e a obra que mais perde pontos", tab=140))
    return [Visual("T1", d) for d in v]

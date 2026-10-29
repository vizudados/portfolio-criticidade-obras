# -*- coding: utf-8 -*-
"""Tela 05 · Canteiro — está seguro, faz certo da primeira vez e recebe material no prazo?

Tela nova da F3 (docs/08 §6), na grade da T4 (prancheta em 300,12): cartões em y 109 (302 × 140; x 352 · 654 · 955 ·
1257 · 1558, o primeiro escuro); Qualidade, mês a mês 352,273 · 1068 × 380 (subtítulo em y 305, gráfico 1068 × 312 de
y 341); Chuva e ritmo 352,693 · 1068 × 347 (subtítulo em y 725, colunas 1068 × 279 de y 761); Segurança por obra
1460,273 · 400 × 380 (cabeçalho em y 305, sete linhas de 42 de y 365); Suprimentos por obra 1460,693 · 400 × 347
(cabeçalho em y 725, sete linhas de 36 de y 785). Títulos, "?" e divisórias estão na casca (wp-t5.svg, casca única da
sessão local); subtítulos, legendas e nomes de coluna vêm em HTML.
"""
from __future__ import annotations

import pbip_lib as lib
from pbip_lib import Visual

CARTOES = [
    ("Acidentes", "T5 · Cartão acidentes · HTML", "Meses seguidos sem acidente com afastamento e o último acidente"),
    ("Frequencia", "T5 · Cartão frequência · HTML",
     "Taxa de frequência de acidentes da carteira em 12 meses, a média do setor e as obras acima dela"),
    ("Nr18", "T5 · Cartão NR-18 · HTML", "Conformidade NR-18 da carteira no mês, a meta e as obras abaixo dela"),
    ("Inspecao", "T5 · Cartão inspeção · HTML",
     "Aprovação na 1.ª inspeção da carteira no mês, a meta e as obras abaixo dela"),
    ("Entregas", "T5 · Cartão entregas · HTML",
     "Entregas no prazo e completas da carteira no mês, a meta e as obras abaixo dela"),
]
CARTAO_X = [352, 654, 955, 1257, 1558]
CARTAO_Y, CARTAO_W, CARTAO_H = 109, 302, 140


def declarar(ctx):
    v = []
    for i, (chave, medida, alt) in enumerate(CARTOES):
        v.append(lib.visual_html(f"T5_Kpi_{chave}", CARTAO_X[i], CARTAO_Y, CARTAO_W, CARTAO_H, medida,
                                 folha_de_estilo="T5 · Cartões · CSS", alt=alt + " (passe o mouse para ver a regra)",
                                 tab=100 + i))
    # ---- Qualidade, mês a mês (352,273 · 1068 × 380)
    v.append(lib.visual_html("T5_Qua_Subtitulo", 352, 305, 1030, 24, "T5 · Qualidade · HTML subtítulo",
                             folha_de_estilo="T5 · Cabeçalho · CSS",
                             alt="O que as linhas mostram: obras, carteira, a obra em destaque e a meta", tab=109))
    v.append(lib.visual_html(
        "T5_Qua_Grafico", 352, 341, 1068, 312, "T5 · Qualidade · HTML gráfico", folha_de_estilo="T5 · Qualidade · CSS",
        alt="Aprovação na 1.ª inspeção mês a mês: uma linha por obra, a carteira em preto, a obra com a menor aprovação no "
            "mês em grafite e a meta tracejada", tab=110))
    # ---- Segurança por obra (1460,273 · 400 × 380)
    v.append(lib.visual_html("T5_Seg_Cabecalho", 1460, 305, 400, 56, "T5 · Segurança · HTML cabeçalho",
                             folha_de_estilo="T5 · Cabeçalho · CSS",
                             alt="Mês de referência, a média do setor e os nomes das colunas de Segurança por obra",
                             tab=120))
    v.append(lib.visual_html(
        "T5_Seg_Lista", 1460, 365, 400, 294, "T5 · Segurança · HTML linha", granularidade=("dObra", "Obra"),
        ordenacao=[(lib.campo_medida_expr("T5 · Segurança · ordem"), "Ascending")], tooltips=["T5 · Segurança · ordem"],
        folha_de_estilo="T5 · Segurança · CSS",
        alt="Segurança por obra: taxa de frequência de acidentes em 12 meses com o traço da média do setor e a "
            "conformidade NR-18 do mês, da maior taxa para a menor", tab=121))
    # ---- Chuva e ritmo (352,693 · 1068 × 347)
    v.append(lib.visual_html("T5_Chuva_Subtitulo", 352, 725, 1030, 24, "T5 · Chuva · HTML subtítulo",
                             folha_de_estilo="T5 · Cabeçalho · CSS",
                             alt="O que as duas metades da coluna mostram", tab=129))
    v.append(lib.visual_html(
        "T5_Chuva_Colunas", 352, 761, 1068, 279, "T5 · Chuva · HTML coluna", granularidade=("dMes", "Mes"),
        ordenacao=[(lib.campo_coluna_expr("dMes", "Mes"), "Ascending")], folha_de_estilo="T5 · Chuva · CSS",
        tooltip_pagina="ttT5Mes",
        alt="Dias impraticáveis por chuva por obra (em cima) e executado no mês da carteira (embaixo), mês a mês, até "
            "o mês de referência", tab=130))
    # ---- Suprimentos por obra (1460,693 · 400 × 347)
    v.append(lib.visual_html("T5_Sup_Cabecalho", 1460, 725, 400, 56, "T5 · Suprimentos · HTML cabeçalho",
                             folha_de_estilo="T5 · Cabeçalho · CSS",
                             alt="Mês de referência, a meta e os nomes das colunas de Suprimentos por obra", tab=139))
    v.append(lib.visual_html(
        "T5_Sup_Lista", 1460, 785, 400, 252, "T5 · Suprimentos · HTML linha", granularidade=("dObra", "Obra"),
        ordenacao=[(lib.campo_medida_expr("T5 · Entregas · ordem"), "Ascending")], tooltips=["T5 · Entregas · ordem"],
        folha_de_estilo="T5 · Suprimentos · CSS",
        alt="Suprimentos por obra: entregas no prazo e completas do mês com o traço da meta e os pedidos, da menor taxa "
            "para a maior", tab=140))
    return [Visual("T5", d) for d in v]

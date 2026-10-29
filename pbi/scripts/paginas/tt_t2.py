# -*- coding: utf-8 -*-
"""Páginas de tooltip da Tela 02 (redesenho v2, Figma 386:790: Tooltip · T2 · v2 · Item 389:1908, Degrau 390:1918, Mês
390:2052, Indicador 390:2509; pbi/spec/redesenho/t02.md §2). Cada uma é um HTML Content do tamanho da página; o Power BI
passa o ponto sob o mouse (item, degrau, mês ou indicador) como filtro. Largura 560 (as colunas da série crescem em
largura); a altura é a do estado mais alto (a lista cresce em altura; o rodapé fica preso ao pé): item com 8 linhas da
tabela anexada e cabeçalho de 94 · degrau com seis itens e série de sinais mistos · mês com a meta na 2ª linha, o
bloco "desde" e a justificativa · item da nota (era o indicador; o nome da página fica) com as sete faixas do
orçamento em duas colunas, a série de pontos e o rodapé "desde"."""
from __future__ import annotations

import pbip_lib as lib
from pbip_lib import Pagina, Visual

LARGURA = 560
# F4 (28/10/2026): o mês da obra passa a 620 — a conta (nome, valor e detalhe) cabe inteira com a escala
LARGURAS = {"ttT2Mes": 620}
TOOLTIPS = [  # (página, título, altura, visual, medida, alt)
    ("ttT2Degrau", "Tooltip · degrau", 480, "TT_T2Degrau_Html", "T2 · Tooltip degrau · HTML",
     "As linhas da planilha que formam o degrau da cascata e o degrau mês a mês"),
    ("ttT2Mes", "Tooltip · mês da obra", 466, "TT_T2Mes_Html", "T2 · Tooltip mês · HTML",
     "O IDC e o resultado da obra no mês, como se formaram, o que mudou e o desembolso do mês"),
    ("ttT2Indicador", "Tooltip · item da nota", 440, "TT_T2Ind_Html", "T2 · Tooltip item da nota · HTML",
     "As faixas do item da nota, a faixa atingida, os pontos mês a mês e o que mudou desde o mês anterior"),
]


def declarar(ctx):
    itens = []
    for i, (pag, titulo, alt_pag, nome, medida, alt) in enumerate(TOOLTIPS):
        larg = LARGURAS.get(pag, LARGURA)
        itens.append(Pagina(lib.pagina_tooltip(pag, titulo, altura=alt_pag, largura=larg, cor_fundo="#FFFFFF"),
                            ordem=94 + i))
        itens.append(Visual(pag, lib.visual_html(nome, 0, 0, larg, alt_pag, medida,
                                                 folha_de_estilo="T2 · Tooltip · CSS", alt=alt,
                                                 pagina_wh=(larg, alt_pag), tab=1)))
    return itens

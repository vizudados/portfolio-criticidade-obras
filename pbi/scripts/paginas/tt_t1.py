# -*- coding: utf-8 -*-
"""Páginas de tooltip da Tela 01 (Figma v2, seção 379:788: Tooltip · T1 · v2 · Obra 389:1618, Indicador 390:1528,
Mês 390:1741; pbi/spec/redesenho/t01.md). Cada uma é um HTML Content do tamanho da página; o Power BI passa o ponto sob
o mouse (obra, item da nota ou mês) como filtro. v2: 560 de largura.

F3 (docs/08 §5): obra 568 (cabeçalho 72 + os 9 itens da nota × 28 + a nota mês a mês + pé), dimensão da nota 540
(as faixas dos itens da dimensão + até 8 obras, tooltips_t1.ITEM_MAX) e mês 456 (quatro estados, 10 obras por coluna,
tooltips_t1.LISTA_MAX). O pé fica preso à base do cartão."""
from __future__ import annotations

import pbip_lib as lib
from pbip_lib import Pagina, Visual

LARGURA = 560
# F4 (28/10/2026): o mês passa a 760 de largura — quatro colunas de status com "PONTA NEGRA" e a nota sem reticências
LARGURAS = {"ttT1Mes": 760}
TOOLTIPS = [  # (página, título, altura, visual, medida, css, alt)
    ("ttT1Obra", "Tooltip · obra", 568, "TT_Obra_Html", "T1 · Tooltip obra · HTML", "T1 · Tooltip obra · CSS",
     "Os nove itens da nota da obra com os pontos, a nota mês a mês e o que mudou desde o mês anterior"),
    ("ttT1Indicador", "Tooltip · dimensão da nota", 540, "TT_Indicador_Html", "T1 · Tooltip indicador · HTML",
     "T1 · Tooltip indicador · CSS", "A dimensão da nota obra por obra, com as faixas dos itens e os pontos de cada obra"),
    ("ttT1Mes", "Tooltip · mês", 456, "TT_Mes_Html", "T1 · Tooltip mês · HTML", "T1 · Tooltip mês · CSS",
     "As obras em cada status da nota no mês e quem entrou, saiu ou abriu em crítico"),
]


def declarar(ctx):
    itens = []
    for i, (pag, titulo, alt_pag, nome, medida, css, alt) in enumerate(TOOLTIPS):
        larg = LARGURAS.get(pag, LARGURA)
        itens.append(Pagina(lib.pagina_tooltip(pag, titulo, altura=alt_pag, largura=larg, cor_fundo="#FFFFFF"),
                            ordem=90 + i))
        itens.append(Visual(pag, lib.visual_html(nome, 0, 0, larg, alt_pag, medida, folha_de_estilo=css, alt=alt,
                                                 pagina_wh=(larg, alt_pag), tab=1)))
    return itens

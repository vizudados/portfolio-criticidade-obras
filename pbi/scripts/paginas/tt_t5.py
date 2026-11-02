# -*- coding: utf-8 -*-
"""Páginas de tooltip da Tela 05 · Canteiro (560 de largura, fundo branco, só o cabeçalho preto; tooltips_t5.py). O Power
BI passa o ponto sob o mouse como filtro: o mês (Chuva e ritmo; Qualidade, mês a mês, pela camada T5_Qua_Meses) ou a
obra (Segurança e Suprimentos por obra). Uma altura por página, a do pior caso (12 meses ou 10 obras na lista, pé de
duas linhas): a lista ocupa o corpo e escala pela contagem (tooltip_lib). As alturas são as de tooltips_t5 (ALTURA,
ALTURA_QUA, ALTURA_SEG e ALTURA_SUP)."""
from __future__ import annotations

import pbip_lib as lib
from pbip_lib import Pagina, Visual

LARGURA = 560
TOOLTIPS = [  # (página, título, altura, visual, medida, alt)
    ("ttT5Mes", "Tooltip · T5 · mês", 400, "TT_T5Mes_Html", "T5 · Tooltip mês · HTML",
     "Dias impraticáveis por chuva e executado de cada obra no mês"),
    ("ttT5Qua", "Tooltip · T5 · qualidade do mês", 440, "TT_T5Qua_Html", "T5 · Tooltip qualidade · HTML",
     "Aprovação na 1.ª inspeção de cada obra no mês, com os serviços aprovados de verificados, a carteira e a meta"),
    ("ttT5Seg", "Tooltip · T5 · segurança da obra", 500, "TT_T5Seg_Html", "T5 · Tooltip segurança · HTML",
     "Acidentes e conformidade NR-18 da obra mês a mês, os números de 12 meses e os pontos dos itens na nota"),
    ("ttT5Sup", "Tooltip · T5 · suprimentos da obra", 480, "TT_T5Sup_Html", "T5 · Tooltip suprimentos · HTML",
     "Entregas no prazo e completas da obra mês a mês, o total da janela, a meta e os pontos do item na nota"),
]


def declarar(ctx):
    itens = []
    for i, (pag, titulo, alt_pag, nome, medida, alt) in enumerate(TOOLTIPS):
        itens.append(Pagina(lib.pagina_tooltip(pag, titulo, altura=alt_pag, largura=LARGURA, cor_fundo="#FFFFFF"),
                            ordem=150 + i))
        itens.append(Visual(pag, lib.visual_html(nome, 0, 0, LARGURA, alt_pag, medida, folha_de_estilo="T5 · Tooltip · CSS",
                                                 alt=alt, pagina_wh=(LARGURA, alt_pag), tab=1)))
    return itens

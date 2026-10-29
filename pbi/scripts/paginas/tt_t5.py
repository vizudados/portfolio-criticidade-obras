# -*- coding: utf-8 -*-
"""Página de tooltip da Tela 05 · Canteiro: o mês de Chuva e ritmo (560 × 400, fundo branco, só o cabeçalho preto;
tooltips_t5.py). O Power BI passa o mês sob o mouse como filtro."""
from __future__ import annotations

import pbip_lib as lib
from pbip_lib import Pagina, Visual

LARGURA, ALTURA = 560, 400


def declarar(ctx):
    return [Pagina(lib.pagina_tooltip("ttT5Mes", "Tooltip · T5 · mês", altura=ALTURA, largura=LARGURA,
                                      cor_fundo="#FFFFFF"), ordem=150),
            Visual("ttT5Mes", lib.visual_html("TT_T5Mes_Html", 0, 0, LARGURA, ALTURA, "T5 · Tooltip mês · HTML",
                                              folha_de_estilo="T5 · Tooltip · CSS",
                                              alt="Dias impraticáveis por chuva e executado de cada obra no mês",
                                              pagina_wh=(LARGURA, ALTURA), tab=1))]

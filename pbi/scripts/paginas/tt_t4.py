# -*- coding: utf-8 -*-
"""Páginas de tooltip da Tela 04 — v2 (Figma 389:1528, t04.md): fundo branco (só o cabeçalho é preto); 560 de largura; alturas mês 480, obra 324, mês do
desembolso 480, obra do desembolso 596 (fase 5: a obra traz a trajetória do resultado % que saiu do painel, e a obra do
desembolso, a justificativa do mês de referência e o histórico dos 5 meses anteriores). Texto da v1: (Figma: Tooltip · T4 · Mês 306:3416, Obra 307:3713, Mês do desembolso 308:3713, Obra
do desembolso 309:3713; docs/06-interacoes-spec-t4.md §3). Cada uma é um HTML Content do tamanho da página; o Power BI
passa o ponto sob o mouse (mês ou obra) como filtro. Uma altura por página — a do estado mais alto, medida no render
(tooltips_t4.ALTURA): mês 402, obra 271 (obra com meses positivos e negativos), mês do desembolso 402, obra do
desembolso 407 (linha de resumo + os seis meses mais recentes de justificativa; janela de até 12 meses, Figma
350:16499). Mês e mês do desembolso listam uma obra por linha: 402 é o pior caso de 10 obras (de 11 em diante entra
"e mais N obras"), com o pé preso à base (Figma 362:8044 e 362:8288, nota 362:8377)."""
from __future__ import annotations

import pbip_lib as lib
from pbip_lib import Pagina, Visual

LARGURA = 560     # v2 (07/10/2026): largura padrão dos tooltips das quatro telas; o gráfico de colunas pode passar disso

# F3: o tooltip da obra (Resultado por obra) saiu com o painel; a linha de Obras no mês usa o da obra do desembolso
TOOLTIPS = [  # (página, título, altura, visual, medida, alt)
    ("ttT4Mes", "Tooltip · T4 · mês", 480, "TT_T4Mes_Html", "T4 · Tooltip mês · HTML",
     "A contribuição de cada obra para o resultado do mês, os pagos e não aplicados e quantas obras caíram"),
    ("ttT4MesDes", "Tooltip · T4 · desembolso do mês", 480, "TT_T4MesDes_Html", "T4 · Tooltip mês do desembolso · HTML",
     "Previsto e desembolsado de cada obra no mês, o desvio e as justificativas exigidas"),
    ("ttT4ObraDes", "Tooltip · T4 · desembolso da obra", 596, "TT_T4ObraDes_Html",
     "T4 · Tooltip obra do desembolso · HTML",
     "O desvio do desembolso da obra mês a mês, a justificativa do mês e o histórico das justificativas"),
]


def declarar(ctx):
    itens = []
    for i, (pag, titulo, alt_pag, nome, medida, alt) in enumerate(TOOLTIPS):
        itens.append(Pagina(lib.pagina_tooltip(pag, titulo, altura=alt_pag, largura=LARGURA, cor_fundo="#FFFFFF"),
                            ordem=140 + i))
        itens.append(Visual(pag, lib.visual_html(nome, 0, 0, LARGURA, alt_pag, medida, folha_de_estilo="T4 · Tooltip · CSS",
                                                 alt=alt, pagina_wh=(LARGURA, alt_pag), tab=1)))
    return itens

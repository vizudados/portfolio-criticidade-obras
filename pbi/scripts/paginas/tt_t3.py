# -*- coding: utf-8 -*-
"""Páginas de tooltip da Tela 03 (Figma v2, seção 379:790, Fileira · Tooltips 388:4064; pbi/spec/redesenho/t03.md):
Mês da curva 390:2268, Mês do ritmo 391:4199 (F3: virou o mês do PPC, 330), Obra na linha do tempo 391:4387
(F3: 430, com a linha do prazo), Obra no avanço 391:6395. Cada uma é um
HTML Content do tamanho da página; o Power BI passa o ponto sob o mouse (mês ou obra) como filtro. v2: 560 de largura
(o avanço, com o mini gráfico de colunas, 600); altura do maior estado de cada peça no Figma com o cabeçalho de 72
(nenhum título da T3 desce a meta para a 2.ª linha): curva 352, ritmo 381, linha do tempo 362 (era 331: o conteúdo,
de 345, encostava o pé na borda; auditoria da Fase 2, minor 7), avanço 340. O rodapé é
preso ao pé; nos estados menores sobra fundo entre o corpo e o rodapé."""
from __future__ import annotations

import pbip_lib as lib
from pbip_lib import Pagina, Visual

FUNDO = "#FFFFFF"          # fundo branco; só o cabeçalho é preto (Alisson, 07/10)
TOOLTIPS = [  # (página, título, largura, altura, visual, medida, alt)
    ("ttT3Curva", "Tooltip · mês da curva S", 560, 352, "TT_T3Curva_Html", "T3 · Tooltip curva · HTML",
     "O mês da curva S: acumulado, ritmo do mês, crédito × desembolsado e o que mudou desde o mês anterior"),
    ("ttT3Ppc", "Tooltip · mês do PPC", 560, 330, "TT_T3Ppc_Html", "T3 · Tooltip PPC · HTML",
     "O mês do PPC: PPC e pontos do item, atraso ao fim do mês, ritmo do mês e o PPC do mês anterior"),
    # 454 (era 430): o detalhe do prazo ("até a entrega: entrega mai/27, com 180 dias nov/27") desce inteiro para a
    # 2.ª linha em vez de sair com reticências, e o status precisa dos 24 px a mais para não encostar no rodapé
    ("ttT3Linha", "Tooltip · obra na linha do tempo", 560, 454, "TT_T3Linha_Html", "T3 · Tooltip linha · HTML",
     "A obra na linha do tempo: prazo, término projetado, orçamento, físico × financeiro e status desde quando"),
    ("ttT3Avanco", "Tooltip · obra no avanço", 600, 340, "TT_T3Avanco_Html", "T3 · Tooltip avanço · HTML",
     "A obra no avanço: o mês, o desvio acumulado mês a mês na cor do item prazo da nota e o que mudou desde o mês anterior"),
]


def declarar(ctx):
    itens = []
    for i, (pag, titulo, larg, alt_pag, nome, medida, alt) in enumerate(TOOLTIPS):
        itens.append(Pagina(lib.pagina_tooltip(pag, titulo, altura=alt_pag, largura=larg, cor_fundo=FUNDO),
                            ordem=130 + i))
        itens.append(Visual(pag, lib.visual_html(nome, 0, 0, larg, alt_pag, medida, folha_de_estilo="T3 · Tooltip · CSS",
                                                 alt=alt, pagina_wh=(larg, alt_pag), tab=1)))
    return itens

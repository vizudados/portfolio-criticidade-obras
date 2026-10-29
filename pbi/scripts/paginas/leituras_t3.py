# -*- coding: utf-8 -*-
"""Leituras do "?" e guia da Tela 03 (regra L065: a leitura cobre o painel que explica). Geometria v2 do Figma
FjBWDk5odF9HaZ2pwhGosl (Tela 03 · v2 387:5627; Fileira · Leituras e guia 388:4067; pbi/spec/redesenho/t03.md §2).
Painéis no canvas: Curva S 352,273 900 × 370 ("?" 26 px no canto, centro 1228,293; recuo −11, +6), Ritmo do mês 1292,273 568 × 290
(centro 1836,293), Avanço das obras 1292,603 568 × 437 (centro 1836,623), Linha do tempo das obras 352,683 900 × 357
(centro 1228,703). A mecânica (botões, marcadores, camadas) está em pbi/scripts/leituras_lib.py."""
from __future__ import annotations

from leituras_lib import declarar_tela

LEITURAS = [  # (chave, painel, (x, y, w, h) do painel, centro do "?", medida)
    ("Curva", "Curva S", (352, 273, 900, 370), (1228, 293), "T3 · Leitura curva · HTML"),
    ("Ppc", "PPC mês a mês", (1292, 273, 568, 290), (1836, 293), "T3 · Leitura PPC · HTML"),
    ("Avanco", "Avanço das obras", (1292, 603, 568, 437), (1836, 623), "T3 · Leitura avanço · HTML"),
    ("Linha", "Linha do tempo das obras", (352, 683, 900, 357), (1228, 703), "T3 · Leitura linha · HTML"),
]


def declarar(ctx):
    return declarar_tela("T3", LEITURAS, "T3 · Leitura · CSS")

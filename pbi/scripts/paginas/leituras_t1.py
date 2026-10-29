# -*- coding: utf-8 -*-
"""Leituras do "?" e guia da Tela 01 (regra L065: a leitura cobre o painel que explica). Geometria v2 do Figma
FjBWDk5odF9HaZ2pwhGosl, seção v2 · Tela 01 (379:788: leituras 391:4305, 391:4352, 391:4369; "?" do Ajuda · v2, 26 px,
em (x + w − 24, y + 20): recuo −11, +6 do dia 07/10); spec em pbi/spec/redesenho/t01.md §2. A mecânica (botões, marcadores, camadas) está
em pbi/scripts/leituras_lib.py."""
from __future__ import annotations

from leituras_lib import declarar_tela

LEITURAS = [  # (chave, painel, (x, y, w, h) do painel, centro do "?", medida)
    ("Obras", "Obras pela nota", (352, 273, 1004, 631), (1332, 293), "T1 · Leitura obras · HTML"),
    ("Pesa", "Onde a carteira perde pontos", (1396, 273, 464, 406), (1836, 293), "T1 · Leitura pesa · HTML"),
    ("Semestre", "Como os meses evoluíram", (1396, 719, 464, 321), (1836, 739), "T1 · Leitura semestre · HTML"),
]


def declarar(ctx):
    return declarar_tela("T1", LEITURAS, "T1 · Leitura · CSS")

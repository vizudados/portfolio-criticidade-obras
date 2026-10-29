# -*- coding: utf-8 -*-
"""Leituras do "?" e guia da Tela 02 (regra L065: a leitura cobre o painel que explica). Redesenho v2: geometria dos
painéis da Tela 02 · v2 (Figma 386:847; pbi/spec/redesenho/t02.md §2); "?" (Ajuda · v2, 26 × 26) em (x + w − 24, y + 20) de cada
painel, centro em (x + w − 24, y + 20) (recuo −11, +6 do dia 07/10). A mecânica está em pbi/scripts/leituras_lib.py."""
from __future__ import annotations

from leituras_lib import declarar_tela

LEITURAS = [  # (chave, painel, (x, y, w, h) do painel, centro do "?", medida) · F3: disposição do docs/08 §5
    ("Itens", "Itens da nota", (352, 273, 548, 767), (876, 293), "T2 · Leitura itens da nota · HTML"),
    ("Forma", "Como o resultado se forma", (940, 273, 508, 350), (1424, 293), "T2 · Leitura forma · HTML"),
    ("Mes", "IDC, mês a mês", (940, 663, 508, 377), (1424, 683), "T2 · Leitura mês a mês · HTML"),
    ("Nota", "A nota, mês a mês", (1488, 273, 372, 388), (1836, 293), "T2 · Leitura nota mês a mês · HTML"),
]


def declarar(ctx):
    return declarar_tela("T2", LEITURAS, "T2 · Leitura · CSS")

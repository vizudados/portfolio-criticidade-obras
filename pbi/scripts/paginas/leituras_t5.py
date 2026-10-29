# -*- coding: utf-8 -*-
"""Leituras do "?" e guia da Tela 05 · Canteiro (regra L065: a leitura cobre o painel que explica). Painéis na grade
da T4 e "?" (26 × 26) no canto superior direito de cada um, nos centros desenhados pela casca (wp-t5.svg). A mecânica
(botões, marcadores, camadas) está em pbi/scripts/leituras_lib.py."""
from __future__ import annotations

from leituras_lib import declarar_tela

LEITURAS = [  # (chave, painel, (x, y, w, h) do painel, centro do "?", medida)
    ("Qua", "Qualidade, mês a mês", (352, 273, 1068, 380), (1396, 293), "T5 · Leitura qualidade · HTML"),
    ("Seg", "Segurança por obra", (1460, 273, 400, 380), (1836, 293), "T5 · Leitura segurança · HTML"),
    ("Chuva", "Chuva e ritmo", (352, 693, 1068, 347), (1396, 713), "T5 · Leitura chuva · HTML"),
    ("Sup", "Suprimentos por obra", (1460, 693, 400, 347), (1836, 713), "T5 · Leitura suprimentos · HTML"),
]


def declarar(ctx):
    return declarar_tela("T5", LEITURAS, "T5 · Leitura · CSS")

# -*- coding: utf-8 -*-
"""Leituras do "?" e guia da Tela 04 (regra L065: a leitura cobre o painel que explica). V2 (07/10/2026): painéis da
Tela 04 · v2 387:5688 no canvas (t04.md §2; fase 5: 1068 à esquerda, 400 à direita) e "?" (Ajuda · v2, 26 × 26) no
canto superior direito de cada um. Texto da
v1: geometria do Figma
FjBWDk5odF9HaZ2pwhGosl, Tela 04 281:723 (painéis 289:7880/7884/7888/7892, "?" 289:7881/7885/7889/7893, relida em
06/10/2026 depois que o rodapé saiu: nenhum painel mudou) e seção Interações · Tela 04 (304:3105); spec em
docs/06-interacoes-spec-t4.md §4 e §5. A mecânica (botões, marcadores, camadas) está em pbi/scripts/leituras_lib.py."""
from __future__ import annotations

from leituras_lib import declarar_tela

LEITURAS = [  # (chave, painel, (x, y, w, h) do painel, centro do "?", medida)
    ("Mes", "Resultado da carteira, mês a mês", (352, 273, 1068, 380), (1396, 293), "T4 · Leitura mês · HTML"),
    ("Obras", "Obras no mês", (1460, 273, 400, 767), (1836, 293), "T4 · Leitura obras · HTML"),
    ("DesCart", "Desembolso da carteira", (352, 693, 1068, 347), (1396, 713), "T4 · Leitura desembolso · HTML"),
]


def declarar(ctx):
    return declarar_tela("T4", LEITURAS, "T4 · Leitura · CSS")

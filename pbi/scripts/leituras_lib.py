# -*- coding: utf-8 -*-
"""leituras_lib — leituras do "?" e guia da página (padrão Vizu; regra L065: a leitura cobre o painel que explica).

Para cada painel com "?": um HTML Content com o retângulo exato do painel (x, y, w, h: sem margem e sem sombra), um botão
transparente sobre o "?" que abre (marcador <T>_LEITURA_<P>_01), um × desenhado (SVG, X_SVG) igual ao "?" da casca e um
botão de fechar (<T>_LeiX_<P>) com o mesmo retângulo e o mesmo raio do botão do "?" (BOTAO_AJ), e um botão do tamanho da
tela, por baixo da leitura, que fecha com clique fora (<T>_LEITURA_00). O "?" redondo do cabeçalho (1816,38, 44 × 44 na
v2) abre o tour guiado da tela (<T>_TOUR_01, pbi/scripts/paginas/tour.py). O guia antigo (Gui_Html, Gui_Fora,
<T>_GUIA_01) saiu. Marcadores só de exibição (não mexem em filtro, dado nem página).

Geometria (canvas 1920 × 1080) lida do Figma FjBWDk5odF9HaZ2pwhGosl, seções Interações · Tela 0X; spec em
docs/06-interacoes-spec*.md §4 (leituras) e §5 (guia).
"""
from __future__ import annotations

import os

import pbip_lib as lib
from pbip_lib import Bookmark, Visual

BOTAO_AJ = 15                                               # raio do "?" (Aj) e do × (LeiX): 30 × 30, redondo
Z_FORA, Z_LEITURA, Z_X = 3990, 4000, 4050

# × desenhado na leitura: o mesmo círculo do "?" da casca (centro em (w − 24, 20) do visual, recuo −11, +6 de 07/10;
# r 12,375; contorno 1,25 px #3B3B3F; glifo × de 8 px, traço 1,5 px #0B0B0C). SVG de 26 × 26: right 11 px, top 7 px.
# Só aspas simples: o texto vai dentro de uma medida DAX.
X_SVG = ("<svg class='x' width='26' height='26' viewBox='0 0 26 26' aria-hidden='true'>"
         "<circle cx='13' cy='13' r='12.375' fill='#FFFFFF' stroke='#3B3B3F' stroke-width='1.25'/>"
         "<path d='M9 9L17 17M17 9L9 17' fill='none' stroke='#0B0B0C' stroke-width='1.5' stroke-linecap='round'/>"
         "</svg>")
CSS_X = ".lv svg.x{position:absolute;right:11px;top:7px;width:26px;height:26px;display:block;z-index:5}"


def declarar_tela(tela: str, leituras: list, css: str) -> list:
    """leituras = [(chave, nome do painel, (x, y, w, h) do painel no canvas, (cx, cy) centro do "?", medida HTML)];
    css = medida da folha de estilo das leituras. O visual da leitura é o retângulo do painel; o botão de fechar tem o
    retângulo do "?" (cx − 15, cy − 15, 30 × 30)."""
    itens = []
    if True:
        nomes = []
        v = []
        v.append(lib.visual_botao(f"{tela}_Lei_Fora", 0, 0, 1920, 1080, lib.acao_bookmark(f"{tela}_LEITURA_00"),
                                  dica="Fechar a leitura", z=Z_FORA, tab=700, oculto=True))
        for k, (chave, painel, (x, y, w, h), (cx, cy), medida) in enumerate(leituras):
            v.append(lib.visual_html(
                f"{tela}_Lei_{chave}", x, y, w, h, medida, folha_de_estilo=css,
                alt=f"Leitura de {painel}: o que o gráfico mostra, por quê e como ler", z=Z_LEITURA + k,
                tab=701 + 2 * k, oculto=True))
            v.append(lib.visual_botao(
                f"{tela}_LeiX_{chave}", cx - BOTAO_AJ, cy - BOTAO_AJ, 2 * BOTAO_AJ, 2 * BOTAO_AJ,
                lib.acao_bookmark(f"{tela}_LEITURA_00"), dica="Fechar a leitura", z=Z_X + k, tab=702 + 2 * k,
                oculto=True, realce="#E9E0CF", raio=BOTAO_AJ))
            # o "?" do painel (desenhado no papel de parede): sempre visível
            itens.append(Visual(tela, lib.visual_botao(
                f"{tela}_Aj_{chave}", cx - BOTAO_AJ, cy - BOTAO_AJ, 2 * BOTAO_AJ, 2 * BOTAO_AJ,
                lib.acao_bookmark(f"{tela}_LEITURA_{chave.upper()}_01"),
                dica=f"Leitura de {painel}", z=lib.CAMADAS["acao"] + 50 + k, tab=40 + k, realce="#E9E0CF",
                raio=BOTAO_AJ)))
        # "?" redondo do cabeçalho: abre o tour guiado da tela (pbi/scripts/paginas/tour.py)
        itens.append(Visual(tela, lib.visual_botao(f"{tela}_Aj_Guia", 1816, 38, 44, 44,
                                                   lib.acao_bookmark(f"{tela}_TOUR_01"), dica="Tour guiado desta tela",
                                                   z=lib.CAMADAS["acao"] + 60, tab=32, realce="#E9E0CF", raio=10)))
        nomes = [d["name"] for d in v]
        if os.environ.get("QA_LEITURA") == tela:            # só para fotografar as leituras abertas; nunca no final
            for d in v:
                if "_Lei_" in d["name"] and not d["name"].endswith("_Fora") or "_LeiX_" in d["name"]:
                    d.pop("isHidden", None)
        itens += [Visual(tela, d) for d in v]
        # marcadores: um por leitura, o do guia e o que fecha tudo
        for chave, painel, *_ in leituras:
            mostra = {f"{tela}_Lei_Fora", f"{tela}_Lei_{chave}", f"{tela}_LeiX_{chave}"}
            itens.append(Bookmark(lib.bookmark_exibicao(
                f"{tela}_LEITURA_{chave.upper()}_01", tela, {n: n in mostra for n in nomes},
                titulo=f"{tela} · leitura · {painel}"), grupo=("leituras", "Leituras")))
        itens.append(Bookmark(lib.bookmark_exibicao(f"{tela}_LEITURA_00", tela, {n: False for n in nomes},
                                                    titulo=f"{tela} · leituras fechadas"), grupo=("leituras", "Leituras")))
    return itens

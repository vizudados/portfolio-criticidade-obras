# -*- coding: utf-8 -*-
"""Tour guiado por passos do painel Criticidade de Obras (brief pbi/spec/tour/brief-tour.md, §6). Substitui o "Guia da página".

Por tela (T1..T4) e passo NN:
- T<n>_Tour_PNN: HTML Content 1920 × 1080 em (0, 0), oculto na base, z 7000. Desenha véu com recorte, anel, cantoneiras,
  cota, card (comum ou grande), personagem e controles (medida 'T<n> · Tour · Passo NN · HTML').
- T<n>_TourAnt_PNN, T<n>_TourProx_PNN, T<n>_TourFecha_PNN: botões transparentes sobre os controles desenhados, com área
  de clique de 56 px de altura, z 7010, ocultos na base. Anterior ou "Pular tour"; Próximo ou "Concluir"; Fechar (×).
- Marcadores só de exibição (bookmark_exibicao, grupo ("tour", "Tour")): T<n>_TOUR_00 (fechado: oculta o tour e as
  leituras) e T<n>_TOUR_NN (mostra só os quatro visuais do passo NN).

Navegação: Próximo n → n+1; Próximo do último → _00; Anterior n → n−1; Pular (passo 1) → _00; Fechar → _00.
O "?" do cabeçalho (T<n>_Aj_Guia, em leituras_lib.py) abre T<n>_TOUR_01.
Geometria e textos: pbi/scripts/tour_lib.py (passos.json é a fonte).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent          # pbi/scripts
sys.path.insert(0, str(AQUI))
import pbip_lib as lib  # noqa: E402
import tour_lib as T  # noqa: E402
from pbip_lib import Bookmark, Visual  # noqa: E402

Z_HTML = lib.CAMADAS["tour"]
Z_BOTAO = Z_HTML + 10
GRUPO = ("tour", "Tour")


def _nomes_leitura(tela: str) -> list[str]:
    """Visuais de leitura da tela (Lei_<chave>, LeiX_<chave>, Lei_Fora), lidos da declaração de leituras_t<n>.py."""
    arq = AQUI / "paginas" / f"leituras_{tela.lower()}.py"
    spec = importlib.util.spec_from_file_location(f"_tour_leituras_{tela.lower()}", arq)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    nomes = [f"{tela}_Lei_Fora"]
    for chave, *_ in mod.LEITURAS:
        nomes += [f"{tela}_Lei_{chave}", f"{tela}_LeiX_{chave}"]
    return nomes


def _nomes_passo(tela: str, n: int) -> list[str]:
    s = f"{n:02d}"
    return [f"{tela}_Tour_P{s}", f"{tela}_TourAnt_P{s}", f"{tela}_TourProx_P{s}", f"{tela}_TourFecha_P{s}"]


def declarar(ctx):
    itens: list = []
    for tela in T.TELAS:
        passos = T.passos_da_tela(tela)
        total = len(passos)
        nome_pagina = T.TELAS[tela].split(" ", 1)[1]
        todos_tour: list[str] = []
        for passo in passos:
            n = passo["n"]
            geo = T.geometria(tela, passo, total)
            s = f"{n:02d}"
            ant_alvo = f"{tela}_TOUR_{(n - 1 if n > 1 else 0):02d}"
            prox_alvo = f"{tela}_TOUR_{(n + 1 if n < total else 0):02d}"
            ant_dica = "Pular o tour" if n == 1 else "Passo anterior"
            prox_dica = "Concluir o tour" if n == total else "Próximo passo"
            alt = f"Tour guiado de {nome_pagina}, passo {n} de {total}: {passo['titulo']}"
            itens.append(Visual(tela, lib.visual_html(
                f"{tela}_Tour_P{s}", 0, 0, lib.LARGURA, lib.ALTURA, T.nome_medida(tela, n), folha_de_estilo=T.NOME_CSS,
                alt=alt, z=Z_HTML, oculto=True)))
            hit_ant, hit_prox, hit_fecha = geo["hits"]["ant"], geo["hits"]["prox"], geo["hits"]["fecha"]
            for nome, (x, y, w, h), acao, dica in (
                    (f"{tela}_TourAnt_P{s}", hit_ant, lib.acao_bookmark(ant_alvo), ant_dica),
                    (f"{tela}_TourProx_P{s}", hit_prox, lib.acao_bookmark(prox_alvo), prox_dica),
                    (f"{tela}_TourFecha_P{s}", hit_fecha, lib.acao_bookmark(f"{tela}_TOUR_00"), "Fechar o tour")):
                itens.append(Visual(tela, lib.visual_botao(nome, x, y, w, h, acao, dica=dica, z=Z_BOTAO, oculto=True)))
            todos_tour += _nomes_passo(tela, n)
        leitura = _nomes_leitura(tela)
        todos = todos_tour + leitura
        # fechado: nada do tour nem leitura aberto por baixo
        itens.append(Bookmark(lib.bookmark_exibicao(f"{tela}_TOUR_00", tela, {v: False for v in todos},
                                                    titulo=f"{tela} · tour fechado"), grupo=GRUPO))
        for passo in passos:
            n = passo["n"]
            mostra = set(_nomes_passo(tela, n))
            itens.append(Bookmark(lib.bookmark_exibicao(
                f"{tela}_TOUR_{n:02d}", tela, {v: v in mostra for v in todos},
                titulo=f"{tela} · tour · passo {n} de {total} · {passo['titulo']}"), grupo=GRUPO))
    return itens

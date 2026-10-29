# -*- coding: utf-8 -*-
"""pagina_comum — peças repetidas das declarações de página (scripts/paginas/t<n>.py): subtítulos dinâmicos, leituras
do "?" (HTML oculto + Abrir/Fechar + bookmarks só de exibição, L029) e páginas de tooltip HTML."""
from __future__ import annotations

import unicodedata

import gerar_subtitulos as GS
import gerar_tooltips as GT
import pbip_lib as lib
from pbip_lib import Bookmark, Pagina, Visual


def slug(txt: str) -> str:
    sem = "".join(c for c in unicodedata.normalize("NFD", txt) if unicodedata.category(c) != "Mn")
    return "".join(w[0].upper() + w[1:] for w in sem.split())


def subtitulos(tela: str, tab0: int = 101) -> list:
    itens = []
    for i, (t, _pasta, cartao, x, y, w, _modelo) in enumerate(s for s in GS.SUBTITULOS if s[0] == tela):
        gx, gy, gw, gh = GS.geometria(x, y, w)
        itens.append(Visual(tela, lib.visual_html(f"{tela}_{slug(cartao)}_Subtitulo", gx, gy, gw, gh,
                                                  GS.medida(t, cartao), alt=f"Subtítulo do cartão {cartao}",
                                                  tab=tab0 + i)))
    return itens


def leituras(tela: str, lista: list[tuple]) -> list:
    """lista = [(chave, x, y, w, h do cartão, base da medida, indicador do bookmark, título)]. O HTML cobre o cartão;
    Abrir fica sobre o "?" do papel de parede (centro em x+w−34, y+30) e Fechar sobre o × que a leitura desenha."""
    itens = []
    todos = {}
    for chave, *_r in lista:
        todos[f"{tela}_{chave}_Leitura"] = False
        todos[f"{tela}_{chave}_LeituraFechar"] = False
    for i, (chave, x, y, w, h, base, ind, titulo) in enumerate(lista):
        bx, by = x + w - 34 - 20, y + 30 - 20
        itens.append(Visual(tela, lib.visual_html(
            f"{tela}_{chave}_Leitura", x, y, w, h, f"{base} · HTML", alt=lib.medida(f"{base} · ALT"),
            z=lib.CAMADAS["leitura"] + 2 * i, oculto=True, tab=200 + i)))
        itens.append(Visual(tela, lib.visual_botao(
            f"{tela}_{chave}_LeituraAbrir", bx, by, 40, 40, lib.acao_bookmark(f"{tela}_LEITURA_{ind}_01"),
            dica=f"Como ler: {titulo}", tab=210 + i, realce="#1F4094", raio=20)))
        itens.append(Visual(tela, lib.visual_botao(
            f"{tela}_{chave}_LeituraFechar", bx, by, 40, 40, lib.acao_bookmark(f"{tela}_LEITURA_00"),
            dica="Fechar a leitura", z=lib.CAMADAS["leitura"] + 2 * i + 1, oculto=True, tab=220 + i,
            realce="#1F4094", raio=20)))
        aberto = dict(todos)
        aberto[f"{tela}_{chave}_Leitura"] = True
        aberto[f"{tela}_{chave}_LeituraFechar"] = True
        itens.append(Bookmark(lib.bookmark_exibicao(f"{tela}_LEITURA_{ind}_01", tela, aberto,
                                                    titulo=f"Leitura · {titulo}")))
    itens.append(Bookmark(lib.bookmark_exibicao(f"{tela}_LEITURA_00", tela, todos, titulo="Leituras fechadas")))
    return itens


def tooltips(nomes: list[str], ordem0: int) -> list:
    itens = []
    for i, nome in enumerate(nomes):
        titulo, medida_html, *_r = GT.PAGINAS[nome]
        w, h = GT.tamanho(nome)
        itens.append(Pagina(lib.pagina_tooltip(nome, titulo, altura=h, largura=w), ordem=ordem0 + i))
        itens.append(Visual(nome, lib.visual_html(
            f"TT_{nome[2:]}_Conteudo", 0, 0, w, h, medida_html,
            alt=lib.medida(medida_html.replace("· HTML", "· ALT")), pagina_wh=(w, h))))
    return itens

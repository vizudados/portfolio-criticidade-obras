# -*- coding: utf-8 -*-
"""Capa v2 do painel Criticidade de Obras (pbi/spec/capa/handoff-capa.md §9–§10; plano em
pbi/spec/capa/prototipo/NOTAS-IMPLEMENTACAO.md). Primeira página do relatório e a que ele abre (ordem 0).

  visual          o quê                                                               caixa (x, y, w, h)       z     tab
  CP_Capa_Filme   HTML Content [CO Capa · HTML] (lote único), folha [CO Capa · CSS],   0, 0, 1920, 1080         100   100
                  alt [CO Capa · ALT]: filme MP4 publicado, régua, os 5 números com
                  odômetro, base, título, CTA e cartões desenhados e o botão de pausar
  CP_Nav_Entrar   botão nativo invisível → T1 (sobre o CTA "Entrar no painel")        1556, 681, 268, 60       1020  200
  CP_Nav_T1…T5    botão nativo invisível → T1…T5 (sobre o cartão inteiro)             x 96/446,4/796,8/        1021… 201–205
                                                                                      1147,2/1497,6, y 836,    1025
                                                                                      326,4 × 168

Fundo da página = o estado parado da capa (pôster da cena final + os 5 números de ago/26), assets/wallpapers/wp-capa.jpg
(capa_medidas.py --fundo): é o que o PDF/PPT mostra se o HTML Content não for exportado (V4I-01 do painel de referência).
Os botões não têm desenho (fundo e borda a 0 %): o desenho é do HTML. A geometria é a das notas §5 e a do desenho
(capa_medidas.P.CTA / CARTAO_*), conferida aqui na declaração.
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent          # pbi/scripts
sys.path.insert(0, str(AQUI))
import pbip_lib as lib  # noqa: E402
from pbip_lib import Pagina, Recurso, Visual  # noqa: E402

PAGINA, TITULO = "Capa", "Capa"
FUNDO_COR = "#F7F4EE"
FUNDO = ("wp-capa.jpg", lib.RAIZ / "assets" / "wallpapers" / "wp-capa.jpg")
Z_HTML, Z_BOTAO = 100, lib.CAMADAS["acao"]            # como no painel de referência: HTML 100, botões 1020
CTA = (1556, 681, 268, 60)
# cinco cartões na faixa x 96–1824 (a dos quatro de antes), 24 px entre eles: 326,4 de largura cada
CARTAO_X, CARTAO_Y, CARTAO_W, CARTAO_H = (96, 446.4, 796.8, 1147.2, 1497.6), 836, 326.4, 168
CARTOES = [("T1", "Visão geral", "Quais obras pedem atenção neste mês, e por quê?"),
           ("T2", "Análise crítica", "Por que a obra tem essa nota?"),
           ("T3", "Avanço físico", "A obra está no ritmo do que foi previsto?"),
           ("T4", "Resultado no tempo", "Está piorando? Gastou fora do previsto no mês e justificou?"),
           ("T5", "Canteiro", "Está seguro, faz certo da primeira vez e recebe material no prazo?")]


def _confere_desenho() -> None:
    """A caixa de cada botão = a caixa desenhada pelo HTML (protótipo aprovado, montar_capa_v2)."""
    import importlib.util
    arq = lib.RAIZ / "spec" / "capa" / "prototipo" / "montar_capa_v2.py"
    spec = importlib.util.spec_from_file_location("capa_prototipo_v2_decl", arq)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if tuple(mod.CTA) != CTA or tuple(mod.CARTAO_X) != CARTAO_X or (mod.CARTAO_Y, mod.CARTAO_W, mod.CARTAO_H) != (
            CARTAO_Y, CARTAO_W, CARTAO_H):
        raise lib.ErroDeclaracao("capa: caixas dos botões diferentes do desenho do HTML (montar_capa_v2)")
    if [(t, q) for _c, t, q in CARTOES] != list(mod.CARTOES):
        raise lib.ErroDeclaracao("capa: títulos ou perguntas dos cartões diferentes do desenho do HTML")


def declarar(ctx):
    _confere_desenho()
    itens: list = [Recurso(*FUNDO), Pagina(lib.pagina_relatorio(PAGINA, TITULO, FUNDO_COR, FUNDO[0]), ordem=0)]
    itens.append(Visual(PAGINA, lib.visual_html(
        "CP_Capa_Filme", 0, 0, lib.LARGURA, lib.ALTURA, "CO Capa · HTML", folha_de_estilo="CO Capa · CSS",
        alt=lib.medida("CO Capa · ALT"), z=Z_HTML, tab=100)))
    itens.append(Visual(PAGINA, lib.visual_botao(
        "CP_Nav_Entrar", *CTA, lib.acao_navegar("T1"), dica="Entrar no painel: abre a Visão geral",
        alt="Abrir Visão geral: entrar no painel", z=Z_BOTAO, tab=200)))
    for i, (cod, titulo, pergunta) in enumerate(CARTOES):
        itens.append(Visual(PAGINA, lib.visual_botao(
            f"CP_Nav_{cod}", CARTAO_X[i], CARTAO_Y, CARTAO_W, CARTAO_H, lib.acao_navegar(cod),
            dica=f"Abrir {titulo}", alt=f"Abrir {titulo}: {pergunta}", z=Z_BOTAO + 1 + i, tab=201 + i)))
    return itens

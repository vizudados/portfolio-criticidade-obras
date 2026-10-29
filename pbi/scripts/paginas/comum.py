# -*- coding: utf-8 -*-
"""Casca comum das quatro telas do painel Criticidade de Obras e análise crítica.

Geometria do Figma FjBWDk5odF9HaZ2pwhGosl, página 03 · Mockup (269:685), Tela 01 281:720: sidebar x 12 (330 × 1056),
prancheta x 300, y 12 (1608 × 1056). Itens da navegação em x 32, a partir de y 234, a cada 52 (248 × 44). Cabeçalho
v2 (Figma 04 · Redesenho v2, 372:685; sem FOLHA): recorte em uso terminando em x 1732 (y 48, 24 de altura), filtro
1760,38 e guia 1816,38 (44 × 44). O desenho está no papel de
parede (pbi/spec/casca/_fonte → gerar_casca.py); aqui ficam os botões transparentes e os HTML dinâmicos.

F3 (28/10/2026, docs/08 §6): entra a T5 · Canteiro, item 05 da navegação (y 442). A casca única (pbi/spec/casca/
_fonte_v2/T1…T5 e D1…D5 → gerar_casca.py) desenha o item 05 nas dez cascas; o bloco "Mês de referência" desceu para
y 550, a 64 do fim do último item, como antes da T5.
"""
from __future__ import annotations

import pbip_lib as lib
from pbip_lib import Pagina, Recurso, Visual

TELAS = [("T1", "Visão geral"), ("T2", "Análise crítica"), ("T3", "Avanço físico"), ("T4", "Resultado no tempo"),
         ("T5", "Canteiro")]
FUNDO = "#F7F4EE"
NAV_X, NAV_Y0, NAV_PASSO, NAV_W, NAV_H = 32, 234, 52, 248, 44
TELAS_DE_OBRA = {"T2", "T3"}
CASCAS_PRONTAS = {"T1", "T2", "T3", "T4", "T5"}   # pbi/spec/casca/_fonte_v2/T<n>.svg → gerar_casca.py
CASCAS_PROVISORIAS = {}   # tela sem casca própria: {"T<n>": "wp-….svg"}; sem entrada, cai no wp-provisorio.svg
NAV_T5_NA_CASCA = {"T1", "T2", "T3", "T4", "T5"}   # cascas que desenham o item 05 · Canteiro; nas outras, rótulo em HTML


def declarar(ctx):
    itens = []
    itens.append(Recurso("wp-provisorio.svg", lib.RAIZ / "assets" / "wallpapers" / "wp-provisorio.svg"))
    for i, (cod, titulo) in enumerate(TELAS):
        wp = f"wp-{cod.lower()}.svg" if cod in CASCAS_PRONTAS else CASCAS_PROVISORIAS.get(cod, "wp-provisorio.svg")
        if cod in CASCAS_PRONTAS or cod in CASCAS_PROVISORIAS:
            itens.append(Recurso(wp, lib.RAIZ / "assets" / "wallpapers" / wp))
        itens.append(Pagina(lib.pagina_relatorio(cod, titulo, FUNDO, wp), ordem=i + 1))
        # navegação: um botão transparente por item; a própria página não ganha botão (L052)
        for k, (dest, nome_dest) in enumerate(TELAS):
            if dest == cod:
                continue
            itens.append(Visual(cod, lib.visual_botao(
                f"{cod}_Nav_{dest}", NAV_X, NAV_Y0 + NAV_PASSO * k, NAV_W, NAV_H, lib.acao_navegar(dest),
                dica=f"Ir para {nome_dest}", z=lib.CAMADAS["navegacao"] + k, tab=10 + k,
                realce="#E9E0CF", raio=12)))
        if cod not in NAV_T5_NA_CASCA:
            # item 05 · Canteiro que a casca ainda não desenha: só o rótulo, por baixo do botão (que dá o realce) e por
            # cima do drawer, cuja casca também não o tem
            k5 = [c for c, _ in TELAS].index("T5")
            itens.append(Visual(cod, lib.visual_html(
                f"{cod}_Side_NavT5", NAV_X, NAV_Y0 + NAV_PASSO * k5, NAV_W, NAV_H, "Sidebar · HTML nav Canteiro",
                folha_de_estilo="Sidebar · CSS", alt="Item 05 da navegação: Canteiro", tab=19,
                z=lib.CAMADAS["drawer"] + 390)))
        # bloco "Mês de referência" da sidebar
        itens.append(Visual(cod, lib.visual_html(
            f"{cod}_Side_Mes", 48, 550, 232, 96, "Sidebar · HTML mês", folha_de_estilo="Sidebar · CSS",
            alt="Mês de referência do painel e quantas obras têm planilha no mês", tab=20,
            z=lib.CAMADAS["drawer"] + 400)))       # acima do drawer, que estende a sidebar por baixo dele
        # recorte em uso no cabeçalho (só informa; os seletores ficam no drawer)
        medida = "Cabeçalho · HTML recorte obra" if cod in TELAS_DE_OBRA else "Cabeçalho · HTML recorte carteira"
        # caixa começa em 1232 (era 1180, com 552 de largura): o texto é alinhado à direita e usa de ~320 a ~440 px
        # (medido pelo auditor em 7 recortes), e o foco do passo 1 do tour, que cobre a pergunta da tela (até 1218 na
        # T4), não pode avançar sobre ela (auditoria da Fase 3). Nome de obra longo leva reticências (.cab .v.nm).
        itens.append(Visual(cod, lib.visual_html(
            f"{cod}_Cab_Recorte", 1232, 48, 500, 24, medida, folha_de_estilo="Cabeçalho · CSS",
            alt="Recorte em uso: mês de referência e obras", tab=30)))
        # rodapé (fonte e selo de origem) saiu em 06/10/2026, a pedido do Alisson: o selo ILUSTR./REAL fica em cada obra
    return itens

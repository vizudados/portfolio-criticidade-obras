# -*- coding: utf-8 -*-
"""Drawer de filtros das cinco telas (Figma: Tela 01 · Filtros abertos 281:724; cascas Casca · Drawer T1–T4 na página
PBI · Casca, 310:4772 / 310:5689 / 310:6606 / 310:7523).

A sidebar se estende até x 692 sobre a prancheta (v2: 680 de largura), com véu; os seletores são segmentações nativas dentro das caixas
desenhadas (L056) e sincronizadas entre as telas. Carteira (T1, T4): mês de referência + janela + obras. Telas de uma
obra (T2, T3): mês de referência + janela + obra em foco. A janela (dJanela: 12 · 9 · 6 · 3 meses) é um seletor de
botões nativo sobre o trilho da casca; a nota embaixo diz de que mês a que mês as séries vão. Abre pelo funil do
cabeçalho (marcador <T>_FILTROS_01) e fecha pelo ×, por clique no véu ou pelo próprio funil (<T>_FILTROS_00).
Marcadores só de exibição: não mexem em filtro nem página.
"""
from __future__ import annotations


import pbip_lib as lib
from pbip_lib import Bookmark, Recurso, Visual

TELAS = ["T1", "T2", "T3", "T4", "T5"]
# casca do drawer fora do padrão wp-d<n>.svg: {"T<n>": "wp-….svg"} (a T5 · Canteiro já tem a wp-d5.svg da casca única)
WP_PROVISORIO = {}
TELAS_DE_OBRA = {"T2", "T3"}
Z = lib.CAMADAS["drawer"]
# v2: o contorno grafite da caixa vem da casca (wp-d*.svg); a segmentação não desenha borda, senão fica dupla (foto do canvas, 07/10/2026)
ESCURO = {"fundo": "#0B0B0C", "texto": "#F7F4EE", "borda": "#0B0B0C", "seta": "#F7F4EE", "marca": "#E9E0CF"}
LISTA = {"fundo": "#0B0B0C", "texto": "#F7F4EE", "borda": "#0B0B0C", "seta": "#F7F4EE", "marca": "#E9E0CF"}
# geometria v2 (Figma Tela 01 · v2 · Filtros abertos 387:5503, drawer 387:5391 de 680 × 1056 em 12,12; cascas
# Casca v2 · Drawer T1…T4 na página PBI · Casca v2, 406:685; pbi/spec/redesenho/t01.md §2): coluna dos filtros de
# x 358 a 668 (310); as caixas têm 44 de altura e o contorno grafite está no papel de parede (o seletor nativo entra
# 1 px para dentro, para o contorno aparecer)
X0 = 358          # coluna do drawer (sidebar em 12 + 346)
LARG = 310
DRAWER_W = 680    # a sidebar estendida vai de 12 a 692
MES_Y = 180       # seletor de mês (rótulo MÊS DE REFERÊNCIA em 160, na casca)
JANELA_Y = 264    # trilho 310 × 42 (rótulo JANELA em 244, na casca); nota da janela em 314
OBRA_Y = 394      # caixa de obras / obra em foco (rótulo em 374, na casca); lista ou nota 52 abaixo
# lista de obras recolhida por padrão (pedido do Alisson, 07/10/2026: "tem que poder recolher… e se chegam mais obras?"):
# aberta, desce por cima do espaço livre até 12 obras (12 × 32 + 8 de respiro = 392) e rola acima disso. O VizuFilter
# só desenha dentro da própria caixa, então a caixa vai do seletor ao fim da lista máxima (394 + 44 + 8 + 392 = 838) e
# nada clicável fica debaixo dela: status e "Limpar filtros" descem para o pé do drawer (Figma 387:5391 e 428:10675)
LISTA_MAX = 12
LISTA_H = LISTA_MAX * 32 + 8                    # 392
OBRAS_H = 44 + 8 + LISTA_H                      # 444: a caixa do VizuFilter (seletor + vão + lista máxima)
STATUS_Y = 862    # status por obra (carteira): rótulo + atalhos de 36 (drawer 850, abaixo da lista máxima)
# 4 contagens da nota em 2 × 2 (Fase 2): rótulo 15 + 8 + 19 + 6 + 19 = 67 (antes 58, uma linha); termina em 934
STATUS_H = 72
LIMPAR_Y = 942    # estado + Limpar filtros (140 × 38), o mesmo nas quatro telas (drawer 930)
BOTOES = {"fundo": "#1A1A1B", "fundo_hover": "#2A2A2C", "fundo_marcado": "#E9E0CF", "texto": "#D9D6D0",
          "texto_marcado": "#0B0B0C"}


def declarar(ctx):
    itens = []
    for i, cod in enumerate(TELAS):
        wp = WP_PROVISORIO.get(cod, f"wp-d{i + 1}.svg")
        itens.append(Recurso(wp, lib.RAIZ / "assets" / "wallpapers" / wp))
        v = []
        v.append(lib.visual_imagem(f"{cod}_Drw_Fundo", 0, 0, 1920, 1080, wp,
                                   alt="Filtros abertos: sidebar estendida sobre a página", z=Z, oculto=True))
        v.append(lib.visual_botao(f"{cod}_Drw_Fora", 12 + DRAWER_W, 12, 1908 - 12 - DRAWER_W, 1056,
                                  lib.acao_bookmark(f"{cod}_FILTROS_00"), dica="Fechar os filtros", z=Z + 1, tab=600,
                                  oculto=True))
        v.append(lib.visual_botao(f"{cod}_Drw_Fechar", 632, 48, 36, 36, lib.acao_bookmark(f"{cod}_FILTROS_00"),
                                  dica="Fechar os filtros", z=Z + 2, tab=601, oculto=True, realce="#F7F4EE", raio=9))
        recorte = "Drawer · HTML recorte obra" if cod in TELAS_DE_OBRA else "Drawer · HTML recorte"
        v.append(lib.visual_html(f"{cod}_Drw_Recorte", X0, 96, LARG, 44, recorte, folha_de_estilo="Drawer · CSS",
                                 alt="Recorte em uso", z=Z + 3, tab=602, oculto=True))
        v.append(lib.segmentacao(f"{cod}_Drw_Mes", X0 + 1, MES_Y + 1, LARG - 2, 42, tabela="dMesRef", coluna="MesRefLongo",
                                 rotulo="Mês de referência", alt="Mês de referência (sem escolha, o último mês)",
                                 grupo="mesref", modo="Dropdown", unica=True, tokens=ESCURO, corpo_pt=12,
                                 padding_itens=10, raio=10, seta_visivel=False, z=Z + 4, tab=603, oculto=True))
        # janela das séries (12 · 9 · 6 · 3 meses): botões nativos sobre o trilho da casca (L056), escolha única
        # estrita (sem escolha, a 1ª linha, 12 meses) e sincronizada entre as quatro telas como o mês
        v.append(lib.segmentacao_botoes(f"{cod}_Drw_Janela", X0 + 1, JANELA_Y + 1, LARG - 2, 40, tabela="dJanela",
                                        coluna="Janela", padrao="12 meses", grupo="janela", linhas=1, colunas=4,
                                        cores=BOTOES, alt="Janela das séries mês a mês: 12, 9, 6 ou 3 meses até o mês "
                                        "de referência", z=Z + 5, tab=604, oculto=True, raio=7, corpo_pt=11.25,
                                        forcar=True, espaco=4, fundo={"cor": ESCURO["fundo"], "raio": 9, "padding": 3},
                                        marcado_semibold=True))
        v.append(lib.visual_html(f"{cod}_Drw_JanelaNota", X0, JANELA_Y + 50, LARG, 40, "Drawer · HTML janela",
                                 folha_de_estilo="Drawer · CSS", alt="De que mês a que mês as séries vão", z=Z + 6,
                                 tab=605, oculto=True))
        if cod in TELAS_DE_OBRA:
            v.append(lib.segmentacao(f"{cod}_Drw_Foco", X0 + 1, OBRA_Y + 1, LARG - 2, 42, tabela="dObraFoco", coluna="ObraFoco",
                                     rotulo="Obra em foco", alt="Obra em foco (sem escolha, a mais crítica do mês)",
                                     grupo="obrafoco", modo="Dropdown", unica=True, tokens=ESCURO, corpo_pt=12,
                                     padding_itens=10, raio=10, seta_visivel=False, z=Z + 7, tab=606, oculto=True))
            v.append(lib.visual_html(f"{cod}_Drw_FocoNota", X0, OBRA_Y + 52, LARG, 40, "Drawer · HTML foco",
                                     folha_de_estilo="Drawer · CSS", alt="Qual obra está em foco", z=Z + 8, tab=607,
                                     oculto=True))
        else:
            # lista de obras: VizuFilter 2.10 (marca, rótulo e ordem por medida, que a segmentação nativa não faz);
            # recolhida por padrão (abre pelo seletor, até LISTA_MAX obras e rola acima disso), seleção múltipla,
            # sincronizada entre as telas da carteira e recortada às obras com aba
            # (predefinição em pbi/visuais/vizufilter/VizuFilter-2.10.0/propriedades-criticidade-obras.json)
            vf = lib.visual_vizufilter(
                f"{cod}_Drw_Obras", X0, OBRA_Y, LARG, OBRAS_H, categoria=("dObra", "Obra", "Obras"),
                geral={"mode": "dropdown", "singleSelect": False, "sortAscending": True, "alwaysOpen": False,
                       # aberta só no modo de foto (montar_pbip --gaveta-aberta), para a lista aparecer na foto
                       "startOpen": getattr(ctx, "gaveta_aberta", None) == cod,
                       "showSearch": False, "showSelectAll": False, "showReset": False, "showSelectedCount": True,
                       "showSelectedValue": True, "selectedValueOnly": True,
                       "placeholderText": "Todas as obras ({n})", "syncSelectionWithHost": True},
                layout={"controlWidth": LARG, "controlHeight": 44, "dropdownWidth": LARG, "dropdownHeight": LISTA_H,
                        "gap": 8, "optionHeight": 32, "borderRadius": 8, "checkboxSize": 16, "checkboxRadius": 3,
                        "scrollbarWidth": 6},
                estilo={"fontSize": 15, "fontFamily": "Segoe UI", "textColor": "#F7F4EE",
                        "backgroundColor": "#0B0B0C", "dropdownBackgroundColor": "#0B0B0C",
                        "selectedBackgroundColor": "#1A1A1B", "hoverBackgroundColor": "#1A1A1B",
                        "hoverTextColor": "#F7F4EE", "borderColor": "#6B6B70", "activeBorderColor": "#6B6B70",
                        "checkboxColor": "#E9E0CF", "checkboxMarkColor": "#0B0B0C", "enableHoverAnimations": False,
                        "showShadow": False, "counterBadgeRadius": 10, "counterBackgroundColor": "#E9E0CF",
                        "counterTextColor": "#0B0B0C", "clearActionColor": "#E9E0CF"},
                medidas={"itemMarker": "Drawer · obra · marca", "itemLabel": "Drawer · obra · rótulo",
                         "itemSort": "Nota · pontos perdidos · ref"},   # ordem da nota (Fase 2)
                # Fase 2: o rótulo da nota chega a "pendente · 7,75 de 8,5" (22 caracteres): coluna do nome 88 e rótulo 13
                extras={"labelPosition": "column", "nameColumnWidth": 88, "markerSize": 11, "markerGap": 6,
                        "labelFontFamily": "Segoe UI", "labelFontSize": 13, "labelColor": "#E9E0CF",
                        "labelOpacity": 65, "sortDirection": "desc"},
                alt="Obras da carteira, da que mais perde pontos na nota para a que menos perde, com a marca e o "
                    "status do mês ao lado de cada nome. Marque uma ou mais para recortar o painel; sem marca, todas.",
                z=Z + 8, tab=607, oculto=True, sincronia=lib.grupo_sincronia("obras"),
                filtros=lib.filtro_visual_categorico(f"{cod}_Drw_ObrasComAba", "dObra", "TemAnaliseCritica", [True]))
            v.append(vf)
            v.append(lib.visual_html(f"{cod}_Drw_Status", X0, STATUS_Y, LARG, STATUS_H, "Drawer · HTML status",
                                     folha_de_estilo="Drawer · CSS", alt="Obras por status no mês de referência",
                                     z=Z + 9, tab=608, oculto=True))
        v.append(lib.visual_html(f"{cod}_Drw_Estado", X0, LIMPAR_Y, 160, 38, "Drawer · HTML estado",
                                 folha_de_estilo="Drawer · CSS", alt="Filtros aplicados", z=Z + 10, tab=609, oculto=True))
        v.append(lib.visual_botao(f"{cod}_Drw_Limpar", X0 + LARG - 140, LIMPAR_Y, 140, 38, lib.acao_limpar_filtros(),
                                  dica="Limpar filtros", z=Z + 11, tab=610, oculto=True, realce="#F7F4EE", raio=9))
        nomes = [d["name"] for d in v]
        if getattr(ctx, "gaveta_aberta", None) == cod:  # só para fotografar o estado aberto; nunca no arquivo final
            for d in v:
                d.pop("isHidden", None)
        itens += [Visual(cod, d) for d in v]
        # funil do cabeçalho abre; ×, véu e o próprio funil (por cima do drawer) fecham
        itens.append(Visual(cod, lib.visual_botao(f"{cod}_Cab_Filtros", 1760, 38, 44, 44,
                                                  lib.acao_bookmark(f"{cod}_FILTROS_01"), dica="Abrir os filtros",
                                                  tab=31, realce="#E9E0CF", raio=10)))
        itens.append(Bookmark(lib.bookmark_exibicao(f"{cod}_FILTROS_01", cod, {n: True for n in nomes},
                                                    titulo=f"{cod} · filtros abertos"), grupo=("filtros", "Filtros")))
        itens.append(Bookmark(lib.bookmark_exibicao(f"{cod}_FILTROS_00", cod, {n: False for n in nomes},
                                                    titulo=f"{cod} · filtros fechados"), grupo=("filtros", "Filtros")))
    return itens

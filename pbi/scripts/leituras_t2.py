#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""leituras_t2 — leituras do "?" e guia da Tela 02 · Análise crítica (pbi/dax/T2/Leituras/**). Só leem contas.

Redesenho v2 (07/10/2026): Figma FjBWDk5odF9HaZ2pwhGosl, seção v2 · Tela 02 (379:789) › Fileira · Leituras e guia
(386:791): Leitura · T2 · v2 · O quadradinho 391:4564 (352,273 · 548 × 584), Como o resultado se forma 391:4581
(940,273 · 508 × 350), Resultado da obra, mês a mês 391:4596 (940,663 · 508 × 377), Sinais do mês 391:4613
(1488,273 · 372 × 388; Itens da nota desde a Fase 2 da régua antiga, 13/10/2026); Guia · T2 · v2 391:6704 (1120 × 771, duas colunas, centrado). Regras em
pbi/spec/redesenho/t02.md §3 e §5: com a fonte maior saíram blocos (quadradinho: detalhe e como ler; cascata: o que
explica; mês a mês: o que explica e como ler; sinais: explicação e destaques) — os que saíram não voltam.
Regra L065 (a leitura cobre o painel; o visual tem a margem da sombra de leituras_lib), L058 (nenhum número repetido).
Mecânica (botões e marcadores) em paginas/leituras_t2.py via leituras_lib. CSS própria (não depende da T1).
F4 (pedido do Alisson, 28/10/2026): todo número do texto conta (C.marca; o desenho() converte com C.envolver_marcas) e
os meses do cabeçalho da matriz aparecem em cascata com as marcas.

    python -X utf8 pbi/scripts/leituras_t2.py
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import contador as C  # noqa: E402
import desenho_projeto as D  # noqa: E402
from contas_lib_projeto import Medida, gravar  # noqa: E402
from desenho_comum import dax_lit  # noqa: E402
import desenho_comum as DC  # noqa: E402
from desenho_t2 import span_ng  # noqa: E402
from leituras_lib import CSS_X, X_SVG  # noqa: E402

RAIZ = AQUI.parent
GERADO = "pbi/scripts/leituras_t2.py"
DES = r"T2 Análise crítica\Leituras"
MEDIDAS: list[Medida] = []
MENOS = D.MENOS
X = X_SVG


def desenho(nome, descricao, dax):
    """Medida de desenho; os valores marcados com C.marca() viram odômetro no fim (F4)."""
    MEDIDAS.append(Medida(nome, DES, "texto", descricao, C.envolver_marcas(dax)))


def linhas(*ls) -> str:
    def plano(x):
        for g in x:
            if isinstance(g, list):
                yield from plano(g)
            else:
                yield g
    return "\n".join(plano(ls))


def ext(v: str, fem: bool = False) -> str:
    nomes = (["nenhuma", "uma", "duas"] if fem else ["nenhum", "um", "dois"]) + \
        ["três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez"]
    casos = ", ".join(f'{i}, "{n}"' for i, n in enumerate(nomes))
    return f'SWITCH ( {v}, {casos}, FORMAT ( {v}, "0" ) )'


def DC_FMT(v: str) -> str:
    """DAX: pontos da nota em texto ("7,75")."""
    return f'FORMAT ( {v}, "{DC.FMT_PTS}", "pt-BR" )'


def cap(v: str) -> str:
    return f"UPPER ( LEFT ( {v}, 1 ) ) & MID ( {v}, 2, LEN ( {v} ) )"


def nome_mes(v: str) -> str:
    return f'FORMAT ( {v}, "mmmm", "pt-BR" )'


def lista_e(v: str, p: str) -> list[str]:
    return [
        f'VAR {p}N = IF ( ISBLANK ( {v} ) || {v} = "", 0, PATHLENGTH ( {v} ) )',
        f'VAR {p}Pos = IF ( {p}N >= 2, FIND ( "§", SUBSTITUTE ( {v}, "|", "§", {p}N - 1 ) ) )',
        f'VAR {p}Txt = SWITCH ( TRUE (), {p}N = 0, "", {p}N = 1, {v}, '
        f'SUBSTITUTE ( LEFT ( {v}, {p}Pos - 1 ), "|", ", " ) & " e " & MID ( {v}, {p}Pos + 1, 999 ) )',
    ]


def painel(classe: str, aria: str, corpo: str) -> str:
    return (f'"<div class=\'u lv\' role=\'dialog\' aria-label=\'" & {aria} & "\'><div class=\'pn {classe}\'>" '
            f'& {corpo} & "</div>{X}</div>" & [Comum · JS contador tooltip] & [Comum · JS corrida]')


def bloco(rotulo: str, conteudo: str) -> str:
    return f'"<div class=\'sec\'><span class=\'vs\'>{rotulo}</span>" & {conteudo} & "</div>"'


def nw(x: str) -> str:
    """Número que não quebra de linha (R$ 259 mil, −0,92 p.p.)."""
    return f"\"<span class='nw'>\" & {x} & \"</span>\""


def destaque(num: str, rot: str) -> str:
    return f'"<div><b>" & {num} & "</b><span>" & {rot} & "</span></div>"'


def fracao(v: str) -> str:
    """Fração do orçamento em palavras (o desembolsado e o executado)."""
    return (f'SWITCH ( TRUE (), {v} < 0.25, "menos de um quarto", {v} < 0.5, "mais de um quarto", '
            f'{v} < 0.75, "mais da metade", "mais de três quartos" )')


def sw(cod: str, mapa: dict, outro: str = '""') -> str:
    return "SWITCH ( " + cod + ", " + ", ".join(f'"{k}", {D.texto(v)}' for k, v in mapa.items()) + f", {outro} )"


def trocar_codigos(v: str, mapa: dict, nome: str) -> list[str]:
    """Lista de códigos de item separada por '|' (conta de lista) virando palavras na VAR `nome`: um SUBSTITUTE por
    código, três por VAR (aninhamento ≤ 3). Nenhum código contém outro, então a troca não encosta em item errado; a
    ordem da lista é a da conta."""
    pares = list(mapa.items())
    grupos = [pares[i:i + 3] for i in range(0, len(pares), 3)]
    linhas, atual = [], v
    for n, grupo in enumerate(grupos, 1):
        expr = atual
        for k, t in grupo:
            expr = f'SUBSTITUTE ( {expr}, "{k}", {D.texto(t)} )'
        atual = nome if n == len(grupos) else f"{nome}{n}"
        linhas.append(f"VAR {atual} = {expr}")
    return linhas


# ===================================================================================================== CSS
# Superfície (L065): o visual é o retângulo do painel da tela (sem margem nem sombra). Offwhite, contorno 1 px preto,
# cantos retos. × = X_SVG de leituras_lib (26 px, igual ao "?" da casca, a 1 px do topo e encostado à direita; o
# sobretítulo reserva 32 px à direita: raio 24 + folga). Escala v2: sobretítulo versalete 12,
# achado Barlow SemiBold 23/28 (grande) ou 21/26 (pequenas), explicação Segoe 17/26 grafite, destaques Barlow
# SemiBold 23 + Segoe 14/19 sobre creme, seções versalete 12 + Segoe 15/21.
CSS_LEITURA = (
    ".lv{position:fixed;inset:0}"
    ".lv .pn{position:absolute;inset:0;background:#FFFFFF;border:1px solid #0B0B0C;border-radius:16px;"
    "overflow:hidden;color:#0B0B0C;padding:18px 20px}"
    ".lv .pn.q{padding:18px 24px}.lv .pn.e{padding:18px 18px}"
    ".lv .sob{display:block;padding-right:32px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
    ".lv .ach span,.lv .exp span,.lv .nw{white-space:nowrap}"
    ".lv .ach{margin-top:12px;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:21px;"
    "line-height:26px}"
    ".lv .pn.q .ach{font-size:23px;line-height:28px}"
    ".lv .exp{margin-top:10px;font-size:17px;line-height:26px;color:#3B3B3F}"
    ".lv .dst{margin-top:14px;background:#E9E0CF;display:grid;grid-template-columns:repeat(3,1fr);column-gap:14px;"
    "padding:12px 16px}"
    ".lv .dst b{display:block;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:23px;"
    "line-height:28px;white-space:nowrap;font-variant-numeric:tabular-nums}"
    ".lv .dst>div>span{display:block;margin-top:2px;font-size:14px;line-height:19px;color:#3B3B3F}"
    ".lv .sec{margin-top:14px}.lv .sec>.vs{display:block;margin-bottom:4px}"
    ".lv .oqe{font-size:15px;line-height:21px}"
    # matriz dos itens da nota (8 itens + a obra × n meses), só marcas; linhas de 15 para caber no painel de 388
    ".lv .mx{display:grid;align-items:center;row-gap:2px;margin-top:8px;font-size:14px;line-height:19px}"
    ".lv .mx .h{text-align:center;font-size:13px;line-height:16px;white-space:nowrap;color:#3B3B3F}"
    ".lv .mx .h.ref{font-weight:600;color:#0B0B0C}"
    ".lv .mx .r{white-space:nowrap}"
    ".lv .mx .c{display:flex;justify-content:center}"
    ".lv .mx .ob{border-top:1px solid #E1E1E1;padding-top:5px;margin-top:4px}"
    ".lv .mx .r.ob{font-weight:600;font-size:15px;line-height:21px}"
    ".lv .mx .c .mk{animation:mxEntra .25s ease-out backwards}"
    "@keyframes mxEntra{from{opacity:0;transform:scale(.4)}}"
    "@media (prefers-reduced-motion:reduce){.lv .mx .c .mk{animation:none}}"
    ".lv .pn.e.it{padding:14px 18px}.lv .pn.e.it .ach{margin-top:8px}"
    ".lv .mx.c8{row-gap:0;margin-top:4px;font-size:13px;line-height:15px}.lv .mx.c8 .r.ob{font-size:14px;line-height:19px}"
    ".lv .mk.mkn{box-shadow:inset 0 0 0 1px #C9C9CC}"
    ".lv .mk.mkx{border:1px dashed #C43737}"
    ".lv .lg{display:flex;align-items:center;gap:5px;margin-top:6px;font-size:13px;line-height:16px;color:#3B3B3F;"
    "white-space:nowrap}.lv .lg .mk{margin-left:8px}.lv .lg .mk:first-child{margin-left:0}"
) + CSS_X
# Guia (o único que cobre a tela): véu 55%, painel 1120 centrado (raio 20, sombra v2/Sombra · guia 0, 24, 60, 35%),
# duas colunas de 500 (itens 1–5 · 6–9 + régua); título Barlow SemiBold 38/44, introdução e descrições Segoe 17/26.
desenho("T2 · Leitura · CSS", "CSS v2 das leituras do \"?\" (superfície do tamanho do painel, achado, explicação, "
        "destaques, seções e a matriz dos itens da nota) e do guia da Tela 02 (1120, duas colunas). Não depende da CSS da T1.",
        "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(CSS_LEITURA))

CURTO_ITEM = {"Credito": "crédito", "SaldoContrato": "saldo de contrato", "AdiantServicos": "adiantamento de serviços",
              "AdiantMateriais": "adiantamento de materiais", "Estoque": "estoque", "Equipamentos": "equipamentos",
              "ReceitaPersonalizacao": "receita de personalizações", "ContasPagar": "contas a pagar", "Desembolsado": "desembolso",
              "Divida": "dívida da obra"}

# ===================================================================================================== O quadradinho
desenho(
    "T2 · Leitura quadradinho · HTML",
    "Leitura do \"?\" de O quadradinho, sobre o painel (548 × 584): o resultado frente ao pago e não aplicado, como a "
    "conta se forma, três destaques que contam (crédito, desembolsado, sem estoque) e o que explica. Com a fonte maior "
    "saíram o detalhe (está no tooltip do item) e o como ler (está no guia). L058: o 'o que explica' conta os meses de "
    "alta do estoque sem repetir o número de itens da explicação. Só lê contas.",
    linhas(
        "-- 1 · Leituras",
        "VAR _obra = [Nota · obra em foco]",
        "VAR _mesL = [Mês de referência · longo]",
        "VAR _mesN = [Mês de referência · nome]",
        "VAR _res = [Resultado da obra · foco]",
        "VAR _sem = [Resultado sem ativos · foco]",
        "VAR _at = [Ativos não consumidos · foco]",
        "VAR _est = [Estoque de materiais · foco]",
        "VAR _cred = [Crédito do orçamento · foco]",
        "VAR _exec = [Físico · executado acumulado · foco]",
        "VAR _des = [Desembolsado acumulado · foco]",
        "VAR _desPct = CALCULATE ( [Item · % do orçamento · foco], dItem[Item] = \"Desembolsado\" )",
        "VAR _nValor = [Quadradinho · itens com valor · foco]",
        "VAR _altasEst = [T2 · Leitura · meses com alta do estoque · foco]",
        "VAR _nMeses = [T2 · Leitura · meses com aba · foco]",
        "VAR _ini = [T2 · Leitura · primeiro mês com aba · foco]",
        "VAR _nuncaCod = [T2 · Leitura quadradinho · itens que nunca tiveram valor (lista) · foco]",
        "VAR _zeroCod = [T2 · Leitura quadradinho · itens que zeraram no mês (lista) · foco]",
        "VAR _comCod = [T2 · Leitura quadradinho · itens com valor (lista) · foco]",
        "-- 2 · Textos",
        D.od_tabela(),
        D.rs("_res", "_tr"), D.rs("_at", "_ta"), D.rs("_sem", "_ts"), D.od_rs("_sem", "_ts"),
        D.rs("_cred", "_tc"), D.od_rs("_cred", "_tc"), D.rs("_des", "_td"), D.od_rs("_des", "_td"),
        D.pct("_exec", "_te"), D.pct("_desPct", "_tdp"),
        "VAR _txtSob = \"LEITURA · O QUADRADINHO · \" & UPPER ( _obra ) & \" · \" & UPPER ( _mesL )",
        "VAR _hRes = " + span_ng("_tr"),
        "VAR _txtAchado =",
        "    SWITCH (",
        "        TRUE (),",
        "        _res < 0, \"A obra fecha \" & _mesN & \" com \" & " + nw("SUBSTITUTE ( _trTxt, \"" + MENOS + "\", \"\" )")
        + " & \" de prejuízo, e isso já contando \" & " + nw("_taTxt") + " & \" em estoque e adiantamentos.\",",
        "        _sem >= 0, \"O resultado de \" & _mesN & \", \" & _hRes & \", fica positivo mesmo sem os \" & _taTxt"
        " & \" pagos e ainda não aplicados.\",",
        "        \"O resultado de \" & _mesN & \", \" & _hRes & \", é menor que o estoque que o sustenta: \" & _taTxt"
        " & \" comprados e ainda não aplicados.\"",
        "    )",
        "VAR _soEstoque = _at <> 0 && _at = _est",
        "VAR _txtExplica =",
        "    \"A conta começa pelo crédito do que foi executado e soma o que foi pago mas ainda não virou obra; depois\"",
        "        & \" desconta as medições a pagar e tudo o que a obra desembolsou. Em \" & _mesN & \", dos sete itens que\"",
        "        & \" somam, só \" & " + ext("_nValor") + " & IF ( _nValor = 1, \" tem valor\", \" têm valor\" )",
        "        & IF ( _est <> 0 && _nValor >= 2, \" — e um deles é o estoque\", \"\" ) & \". \"",
        "        & IF ( _sem < 0 && _res >= 0, IF ( _soEstoque, \"Sem ele, \", \"Sem eles, \" ) & \"a obra fecharia o mês no\""
        " & \" vermelho.\", IF ( _sem >= 0, \"Mesmo sem eles o resultado seguiria positivo.\", \"\" ) )",
        trocar_codigos("_nuncaCod", CURTO_ITEM, "_nunca"),
        trocar_codigos("_zeroCod", CURTO_ITEM, "_zeroAgora"),
        trocar_codigos("_comCod", CURTO_ITEM, "_comValor"),
        lista_e("_nunca", "_ln"), lista_e("_zeroAgora", "_lz"), lista_e("_comValor", "_lv"),
        "VAR _txtAltas =",
        "    IF ( _altasEst = 0, \"e o estoque não subiu desde \" & " + nome_mes("_ini") + ",",
        "        \"e o estoque subiu em \" & " + ext("_altasEst") + " & IF ( _altasEst = 1, \" mês\", \" meses\" ) & \" desde \" & "
        + nome_mes("_ini") + " )",
        "VAR _txtOqe =",
        "    IF ( _lnN > 0, IF ( _lnN > 2, " + cap(ext("_lnN")) + " & \" itens de pago e não aplicado\", " + cap("_lnTxt") + " )"
        " & IF ( _lnN = 1, \" não entrou\", \" não entraram\" ) & \" na conta desta obra no período\", \"\" )",
        "        & IF ( _lnN > 0 && _lzN > 0, \"; \", \"\" )",
        "        & IF ( _lzN > 0, IF ( _lnN > 0, _lzTxt, " + cap("_lzTxt") + " ) & IF ( _lzN = 1, \" está em zero\", \" estão em zero\" ), \"\" )",
        "        & IF ( _lnN + _lzN > 0, \". \", \"\" )",
        "        & IF (",
        "            _est <> 0 && _nMeses > 1,",
        "            \"O resultado vive de \" & " + ext("_lvN") + " & \" números — \" & _lvTxt & \" — \" & _txtAltas & \".\",",
        "            \"O resultado vive de \" & " + ext("_lvN") + " & \" números: \" & _lvTxt & \".\"",
        "        )",
        "-- 4 · Marcação",
        "VAR _htmlDst =",
        "    \"<div class='dst sobre-creme'>\"",
        "        & " + destaque("_tcOd", '"crédito pelos " & _teTxt & " executados: o que a obra podia ter gasto"'),
        "        & " + destaque("_tdOd", '"já desembolsados desde o início, " & _tdpTxt & " do orçamento"'),
        "        & " + destaque(span_ng("_ts", "_tsOd"), '"resultado sem estoque e adiantamentos: o consumo real"'),
        "    & \"</div>\"",
        "VAR _corpo =",
        "    \"<span class='vs sob'>\" & _txtSob & \"</span><h2 class='ach'>\" & _txtAchado & \"</h2>\"",
        "        & \"<p class='exp'>\" & _txtExplica & \"</p>\" & _htmlDst",
        "        & " + bloco("O que explica", "\"<p class='oqe'>\" & _txtOqe & \"</p>\""),
        "RETURN",
        "    IF ( NOT ISBLANK ( _res ), " + painel("q", '"Leitura de O quadradinho"', "_corpo") + " )",
    ))

# ===================================================================================================== Como o resultado se forma
# F3 (docs/08 §5): a cascata nova (valor agregado → custo aplicado → resultado aplicado → a realizar → resultado da
# planilha). Achado pelo IDC e pelo resultado aplicado; explicação pelo que a planilha soma e ainda não aconteceu.
desenho(
    "T2 · Leitura forma · HTML",
    "Leitura do \"?\" de Como o resultado se forma, sobre o painel (508 × 350, condensada): o que a obra agregou "
    "contra o que já virou obra (resultado aplicado e IDC), quanto da planilha ainda vai se realizar (saldo de contrato e "
    "equipamentos) e três destaques que contam. Só lê contas.",
    linhas(
        "-- 1 · Leituras",
        "VAR _obra = [Nota · obra em foco]",
        "VAR _va = [Crédito do orçamento · foco]",
        "VAR _ca = [Custo aplicado · foco]",
        "VAR _ra = [Resultado aplicado · foco]",
        "VAR _ar = [A realizar · foco]",
        "VAR _res = [Resultado da obra · foco]",
        "VAR _idc = [IDC · foco]",
        "VAR _divida = [Dívida da obra · foco]",
        "-- 2 · Textos",
        D.od_tabela(),
        D.rs("_va", "_tva"), D.rs("_ca", "_tca"), D.rs("_ra", "_tra", mais=True), D.rs("_ar", "_tar"),
        D.rs("_res", "_tres", mais=True), D.rs("_divida", "_tdv"),
        D.od_rs("_va", "_tva"), D.od_rs("_ca", "_tca"), D.od_rs("_ar", "_tar"),
        "VAR _txtIdc = FORMAT ( _idc, \"0.00\", \"pt-BR\" )",
        "VAR _txtSob = \"LEITURA · COMO O RESULTADO SE FORMA · \" & UPPER ( _obra ) & \" · \" & [Mês de referência · curto maiúsculo]",
        "VAR _txtAchado =",
        "    IF (",
        "        _ra >= 0,",
        "        \"A obra agregou mais do que gastou no que executou: resultado aplicado de \" & " + nw(C.marca("_traTxt"))
        + " & \", IDC \" & " + C.marca("_txtIdc") + " & \".\",",
        "        \"A obra gastou mais do que agregou no que executou: resultado aplicado de \" & "
        + nw("\"<span class='ng'>\" & " + C.marca("_traTxt") + " & \"</span>\"")
        + " & \", IDC \" & " + C.marca("_txtIdc") + " & \".\"",
        "    )",
        "VAR _txtExplica =",
        "    SWITCH (",
        "        TRUE (),",
        "        ISBLANK ( _ar ) || _ar = 0, \"A planilha não soma nada a realizar: o resultado dela é o aplicado.\",",
        "        _ra < 0 && _res >= 0, \"A planilha mostra \" & " + nw(C.marca("_tresTxt")) + " & \" porque soma \" & " + nw(C.marca("_tarTxt"))
        + " & \" a realizar (saldo de contrato e equipamentos), que ainda não aconteceu.\",",
        "        \"A planilha soma \" & " + nw(C.marca("_tarTxt")) + " & \" a realizar (saldo de contrato e equipamentos) e chega a \" & "
        + nw(C.marca("_tresTxt")) + " & \".\"",
        "    )",
        "    & IF ( _divida > 0, \" A dívida da obra (\" & " + nw(C.marca("_tdvTxt")) + " & \") entra no custo.\", \"\" )",
        "-- 4 · Marcação",
        "VAR _htmlDst =",
        "    \"<div class='dst sobre-creme'>\"",
        "        & " + destaque("_tvaOd", '"agregados: o executado vezes o orçamento"'),
        "        & " + destaque("_tcaOd", '"de custo do que já virou obra, com a dívida"'),
        "        & " + destaque("_tarOd", '"a realizar: a planilha conta e ainda não aconteceu"'),
        "    & \"</div>\"",
        "VAR _corpo =",
        "    \"<span class='vs sob'>\" & _txtSob & \"</span><h2 class='ach'>\" & _txtAchado & \"</h2>\"",
        "        & \"<p class='exp'>\" & _txtExplica & \"</p>\" & _htmlDst",
        "RETURN",
        "    IF ( NOT ISBLANK ( _res ), " + painel("", '"Leitura de Como o resultado se forma"', "_corpo") + " )",
    ))

# ===================================================================================================== IDC, mês a mês
desenho(
    "T2 · Leitura mês a mês · HTML",
    "Leitura do \"?\" de IDC, mês a mês, sobre o painel (508 × 377, condensada): de onde o IDC saiu e onde está, desde "
    "quando está abaixo de 1 (se estiver), quantos meses da janela ficaram abaixo, e três destaques que contam (IDC de "
    "agora, o menor da janela e a trava). Só lê contas.",
    linhas(
        "-- 1 · Leituras",
        "VAR _obra = [Nota · obra em foco]",
        "VAR _ref = [Mês de referência]",
        "VAR _ini = [T2 · Leitura · primeiro mês com aba · foco]",
        "VAR _idc = [IDC · foco]",
        "VAR _idcIni = [T2 · IDC · no primeiro mês com aba · foco]",
        "VAR _min = [T2 · IDC · mínimo na janela]",
        "VAR _mMin = [T2 · IDC · mês do menor]",
        "VAR _nAbx = [T2 · IDC · meses abaixo de 1 na janela] + 0",
        "VAR _desde = [T2 · IDC · abaixo de 1 desde]",
        "VAR _nMeses = [T2 · Leitura · meses com aba · foco] + 0",
        "VAR _trv = [Nota · limite custo · trava]",
        "-- 2 · Textos",
        "VAR _t = FORMAT ( _idc, \"0.00\", \"pt-BR\" )",
        "VAR _tIni = FORMAT ( _idcIni, \"0.00\", \"pt-BR\" )",
        "VAR _tMin = FORMAT ( _min, \"0.00\", \"pt-BR\" )",
        "VAR _tTrv = FORMAT ( _trv, \"0.00\", \"pt-BR\" )",
        "VAR _txtSob = \"LEITURA · IDC, MÊS A MÊS · \" & UPPER ( _obra ) & \" · \" & [Mês de referência · curto maiúsculo]",
        "VAR _txtAchado =",
        "    SWITCH (",
        "        TRUE (),",
        "        _ini = _ref || ISBLANK ( _idcIni ), \"IDC de \" & " + C.marca("_t") + " & \" no primeiro mês com planilha na janela.\",",
        "        ROUND ( _idc, 2 ) = ROUND ( _idcIni, 2 ), \"O IDC está em \" & " + C.marca("_t") + " & \", o mesmo de \" & " + nome_mes("_ini") + " & \".\",",
        "        \"O IDC foi de \" & " + C.marca("_tIni") + " & \" em \" & " + nome_mes("_ini") + " & \" para \" & " + C.marca("_t") + " & \" agora.\"",
        "    )",
        "VAR _txtExplica =",
        "    SWITCH (",
        "        TRUE (),",
        "        _nAbx = 0, \"Em nenhum mês da janela a obra gastou mais do que agregou.\",",
        "        NOT ISBLANK ( _desde ) && _desde = _ini, \"Abaixo de 1 em todos os meses com planilha: a obra gasta mais do que agrega.\",",
        "        NOT ISBLANK ( _desde ), \"Abaixo de 1 desde \" & " + nome_mes("_desde") + " & \": \" & " + C.marca("_nAbx") + " & IF ( _nAbx = 1, \" mês\", \" meses\" ) "
        "& \" da janela gastando mais do que agrega.\",",
        "        " + C.marca("_nAbx") + " & IF ( _nAbx = 1, \" mês\", \" meses\" ) & \" da janela abaixo de 1; agora a obra agrega o que gasta.\"",
        "    )",
        "    & IF ( _idc < _trv, \" Abaixo de \" & " + C.marca("_tTrv") + " & \", a obra fica crítica pela trava.\", \"\" )",
        "-- 4 · Marcação",
        "VAR _htmlDst =",
        "    \"<div class='dst sobre-creme'>\"",
        "        & " + destaque("\"<span class='\" & IF ( _idc < 1, \"ng\", \"\" ) & \"'>\" & " + C.marca("_t") + " & \"</span>\"", '"IDC no mês de referência"'),
        "        & " + destaque(C.marca("_tMin"), '"o menor da janela, em " & FORMAT ( _mMin, "mmm/yy", "pt-BR" )'),
        "        & " + destaque(C.marca("_nAbx") + " & \" de \" & " + C.marca("_nMeses"), '"meses abaixo de 1 na janela"'),
        "    & \"</div>\"",
        "VAR _corpo =",
        "    \"<span class='vs sob'>\" & _txtSob & \"</span><h2 class='ach'>\" & _txtAchado & \"</h2>\"",
        "        & \"<p class='exp'>\" & _txtExplica & \"</p>\" & _htmlDst",
        "RETURN",
        "    IF ( NOT ISBLANK ( _idc ), " + painel("", '"Leitura de IDC, mês a mês"', "_corpo") + " )",
    ))

# ===================================================================================================== A nota, mês a mês
desenho(
    "T2 · Leitura nota mês a mês · HTML",
    "Leitura do \"?\" de A nota, mês a mês, sobre o painel (372 × 388, estreita): de onde a nota saiu e onde está, o "
    "status e a trava, quantos meses da janela foram críticos, e dois destaques que contam. Só lê contas.",
    linhas(
        "-- 1 · Leituras",
        "VAR _obra = [Nota · obra em foco]",
        "VAR _ini = [T2 · Nota · primeiro mês com nota na janela · foco]",
        "VAR _ult = [T2 · Nota · último mês com nota na janela · foco]",
        "VAR _nIni = [T2 · Nota · no primeiro mês com nota na janela · foco]",
        "VAR _nota = [Nota · nota final · ranking · foco]",
        "VAR _st = [Nota · status · ranking · foco]",
        "VAR _pend = [Nota · pendente · ranking · foco]",
        "VAR _trv = [Nota · trava · motivo · foco] & \"\"",
        "VAR _nCrit = [T2 · Nota · meses críticos na janela · foco] + 0",
        "-- 2 · Textos",
        "VAR _t = " + DC_FMT("_nota"),
        "VAR _tIni = " + DC_FMT("_nIni"),
        "VAR _txtSob = \"LEITURA · A NOTA, MÊS A MÊS · \" & UPPER ( _obra )",
        "VAR _txtAchado =",
        "    SWITCH (",
        "        TRUE (),",
        "        _pend = 1, \"Sem nota no mês de referência: falta item.\",",
        "        ISBLANK ( _ini ) || _ini = _ult, \"Nota \" & " + C.marca("_t") + " & \", a primeira da janela.\",",
        "        ROUND ( _nota, 2 ) = ROUND ( _nIni, 2 ), \"Nota \" & " + C.marca("_t") + " & \", a mesma de \" & " + nome_mes("_ini") + " & \".\",",
        "        \"A nota foi de \" & " + C.marca("_tIni") + " & \" em \" & " + nome_mes("_ini") + " & \" para \" & " + C.marca("_t") + " & \".\"",
        "    )",
        "VAR _txtExplica =",
        "    IF ( _pend = 1, \"\",",
        "        \"Hoje está \" & " + DC.palavra_status("_st", "_pend") + "",
        "            & IF ( _trv <> \"\", \", pela trava de \" & SUBSTITUTE ( _trv, \"|\", \" e \" ), \"\" ) & \". \"",
        "            & SWITCH ( _nCrit, 0, \"Nenhum mês da janela foi crítico.\", 1, \"Um mês da janela foi crítico.\", "
        + C.marca("_nCrit") + " & \" meses da janela foram críticos.\" ) )",
        "-- 4 · Marcação",
        "VAR _corpo =",
        "    \"<span class='vs sob'>\" & _txtSob & \"</span><h2 class='ach'>\" & _txtAchado & \"</h2>\"",
        "        & \"<p class='exp'>\" & _txtExplica & \"</p>\"",
        "RETURN",
        "    IF ( NOT ISBLANK ( _ult ), " + painel("e", '"Leitura de A nota, mês a mês"', "_corpo") + " )",
    ))


# ===================================================================================================== Itens da nota
# Era a leitura de Sinais do mês. Achado: a nota e o status (ou pendente: quantos itens faltam e quanto já perde) e de
# onde vêm os pontos perdidos (os dois itens que mais perdem); embaixo, a matriz item × mês da obra em foco com as marcas
# dos pontos (cheio, parcial, zero, sem dado tracejado) e a linha da obra com o status de cada mês. L058: nenhum número
# se repete (perdas iguais viram "cada"; o total some quando é igual à nota).
def em_frase(v: str, prep: str) -> str:
    """'o orçamento' → 'no orçamento' (prep="em") ou 'do orçamento' (prep="de"), a partir de Nota · item · nome em frase."""
    d = {"em": ("no", "na", "nos", "nas"), "de": ("do", "da", "dos", "das")}[prep]
    return (f'SWITCH ( TRUE (), LEFT ( {v}, 3 ) = "os ", "{d[2]} " & MID ( {v}, 4, 99 ), LEFT ( {v}, 3 ) = "as ", '
            f'"{d[3]} " & MID ( {v}, 4, 99 ), LEFT ( {v}, 2 ) = "o ", "{d[0]} " & MID ( {v}, 3, 99 ), '
            f'LEFT ( {v}, 2 ) = "a ", "{d[1]} " & MID ( {v}, 3, 99 ), {v} )')


desenho(
    "T2 · Leitura itens da nota · HTML",
    "Leitura do \"?\" de Itens da nota, sobre o painel (548 × 767, desde a F3; era 372 × 388): a nota e o status da obra em foco (ou, "
    "pendente, quantos itens faltam e quanto já perde) e de onde vêm os pontos perdidos; a matriz item × mês com as "
    "marcas dos pontos e a linha da obra com o status de cada mês. Só lê contas.",
    linhas(
        "-- 1 · Leituras",
        "VAR _ref = [Mês de referência]",
        "VAR _obra = [Nota · obra em foco]",
        "VAR _mesC = [Mês de referência · curto maiúsculo]",
        "VAR _mesN = [Mês de referência · nome]",
        "VAR _nota = [Nota · nota final · ranking · foco]",
        "VAR _st = [Nota · status · ranking · foco]",
        "VAR _pend = [Nota · pendente · ranking · foco]",
        "VAR _pe = [Nota · pontos perdidos · ranking · foco]",
        "VAR _po = [Nota · pontos possíveis · ranking · foco]",
        "VAR _faltB = [Nota · itens faltando na base · foco] + 0",
        "VAR _faltP = [Nota · itens faltando na planilha · foco] + 0",
        # valor fora da faixa: já contado em "faltando na base", mas não é falta (auditoria da Fase 3, minor 1)
        "VAR _fora = [Nota · itens fora da faixa · foco] + 0",
        "VAR _fB = _faltB - _fora",
        "VAR _plL = [Nota · itens faltando na planilha (lista) · foco] & \"\"",
        "VAR _plF = CALCULATE ( [Nota · item · nome em frase], dItemNota[Item] = PATHITEM ( _plL, 1 ) )",
        "VAR _perdemCod = [T2 · Leitura · itens que perdem pontos (lista) · foco]",
        "VAR _nPerdem = IF ( _perdemCod = \"\", 0, PATHLENGTH ( _perdemCod ) ) /* geometria */",
        "VAR _c1 = PATHITEM ( _perdemCod, 1 )",
        "VAR _c2 = PATHITEM ( _perdemCod, 2 )",
        "VAR _c3 = PATHITEM ( _perdemCod, 3 )",
        "VAR _nTopo = [T2 · Leitura · itens que mais perdem (quantos) · foco] + 0",
        "VAR _mx = [T2 · Leitura · pontos de cada item, mês a mês (lista) · foco]",
        "VAR _p1 = CALCULATE ( [Nota · item · perdidos · foco], dItemNota[Item] = _c1 )",
        "VAR _p2 = CALCULATE ( [Nota · item · perdidos · foco], dItemNota[Item] = _c2 )",
        "VAR _f1 = CALCULATE ( [Nota · item · nome em frase], dItemNota[Item] = _c1 )",
        "VAR _f2 = CALCULATE ( [Nota · item · nome em frase], dItemNota[Item] = _c2 )",
        "VAR _p3 = CALCULATE ( [Nota · item · perdidos · foco], dItemNota[Item] = _c3 )",
        "VAR _f3 = CALCULATE ( [Nota · item · nome em frase], dItemNota[Item] = _c3 )",
        "VAR _itens =",
        "    ADDCOLUMNS (",
        "        VALUES ( dItemNota[Item] ),",
        '        "@o", [Nota · item · ordem],',
        '        "@rot", [Nota · item · nome curto]',
        "    )",
        "VAR _meses =",
        "    ADDCOLUMNS (",
        "        VALUES ( dMes[Mes] ),",
        '        "@ate", [Série · mês até a referência],',
        '        "@ord", [Mês · ordem],',
        '        "@rot", [Mês · abreviado]',
        "    )",
        "VAR _serie = FILTER ( _meses, [@ate] = 1 ) /* lista */",
        "VAR _nCol = COUNTROWS ( _serie ) /* geometria */",
        "-- 2 · Textos",
        DC.nota_txt("_n", "_nota", "[Nota · pontos obtidos · ranking · foco]", "_po", "_pend"),
        DC.pontos("_pe", "_tpe"), DC.pontos("_po", "_tpo"), DC.pontos("_p1", "_tp1"), DC.pontos("_p2", "_tp2"),
        "VAR _txtSob = \"LEITURA · ITENS DA NOTA · \" & UPPER ( _obra ) & \" · \" & _mesC",
        "VAR _de1 = " + em_frase("_f1", "de"),
        "VAR _de2 = " + em_frase("_f2", "de"),
        "VAR _de3 = " + em_frase("_f3", "de"),
        "VAR _em1 = " + em_frase("_f1", "em"),
        "VAR _em2 = " + em_frase("_f2", "em"),
        "VAR _em3 = " + em_frase("_f3", "em"),
        # empate no topo cita todos; topo único com o 2º empatado com o 3º: só o topo (auditoria da Fase 2, minor 2)
        "VAR _seg = _nTopo = 1 && _nPerdem >= 2 && ( _nPerdem = 2 || ROUND ( _p2 - _p3, 8 ) <> 0 )",
        "VAR _deTopo = SWITCH ( _nTopo, 1, _de1, 2, _de1 & \" e \" & _de2, 3, _de1 & \", \" & _de2 & \" e \" & _de3, "
        "\"de \" & " + ext("_nTopo", fem=False) + " & \" itens empatados\" )",
        "VAR _emTopo = SWITCH ( _nTopo, 1, _em1, 2, _em1 & \" e \" & _em2, 3, _em1 & \", \" & _em2 & \" e \" & _em3, "
        "\"em \" & " + ext("_nTopo", fem=False) + " & \" itens empatados\" )",
        # de onde vêm os pontos perdidos: os itens empatados no topo (perdas iguais: "cada"), ou o topo e o segundo
        # quando os dois são únicos
        "VAR _txtOnde =",
        "    SWITCH (",
        "        TRUE (),",
        "        _nPerdem = 1, \"todos \" & _de1,",
        "        _nTopo = _nPerdem, \"todos \" & _deTopo & \", \" & " + C.marca("_tp1Txt") + " & \" cada\",",
        # de quatro empatados em diante, sem "mais" ("vêm mais de quatro itens" lia "mais do que quatro"; N4)
        "        _nTopo > 3, _deTopo & \", \" & " + C.marca("_tp1Txt") + " & \" cada\",",
        "        _nTopo > 1, \"mais \" & _deTopo & \", \" & " + C.marca("_tp1Txt") + " & \" cada\",",
        "        _seg, \"mais \" & _de1 & \" (\" & " + C.marca("_tp1Txt") + " & \") e \" & _de2 & \" (\" & " + C.marca("_tp2Txt") + " & \")\",",
        "        \"mais \" & _de1 & \" (\" & " + C.marca("_tp1Txt") + " & \")\"",
        "    )",
        "VAR _txtTotal = IF ( _tpeTxt = _nN || _tpeTxt = _tp1Txt, \"Os pontos perdidos\", \"Os \" & " + C.marca("_tpeTxt") + " & \" pontos perdidos\" )",
        # o que falta pela fonte (auditoria da Fase 2, minor 4), curto para caber no painel de 372: "faltam seis itens,
        # um na planilha"; só a base: "faltam cinco itens na base"; só a planilha: "falta o físico-financeiro na
        # planilha". O valor fora da faixa vem à parte (Fase 3, minor 1): "falta um item na base; um está fora da faixa"
        "VAR _txtFalta =",
        "    SWITCH ( TRUE (),",
        "        _fB > 0 && _faltP > 0, \"faltam \" & " + ext("_fB + _faltP") + " & \" itens, \" & " + ext("_faltP") + " & \" na planilha\",",
        "        _fB > 0, IF ( _fB = 1, \"falta um item\", \"faltam \" & " + ext("_fB") + " & \" itens\" ) & \" na base\",",
        "        _faltP > 0, IF ( _faltP = 1, \"falta \" & _plF, \"faltam \" & " + ext("_faltP") + " & \" itens\" ) & \" na planilha\",",
        "        \"\"",
        "    )",
        "VAR _txtFora =",
        "    IF ( _fora = 0, \"\",",
        "        IF ( _txtFalta = \"\",",
        "            IF ( _fora = 1, \"um item está fora da faixa\", " + ext("_fora") + " & \" itens estão fora da faixa\" ),",
        "            \"; \" & IF ( _fora = 1, \"um está fora da faixa\", " + ext("_fora") + " & \" estão fora da faixa\" ) ) )",
        "VAR _txtAchado =",
        "    SWITCH (",
        "        TRUE (),",
        "        _pend = 1,",
        "            \"Pendente: \" & _txtFalta & _txtFora & \". \"",
        "            & IF ( _pe = 0, \"No que já dá para calcular, não perde ponto.\",",
        "                \"No que já dá para calcular, perde \" & " + C.marca("_tpeTxt") + " & \" de \" & " + C.marca("_tpoTxt")
        + " & \", mais \" & _emTopo & \".\" ),",
        "        _pe = 0, \"Nota \" & " + C.marca("_nN") + " & \", \" & " + DC.palavra_status("_st", "_pend") + " & \": não perde ponto em nenhum item.\",",
        "        \"Nota \" & " + C.marca("_nN") + " & \", \" & IF ( _st = 1, \"em \", \"\" ) & " + DC.palavra_status("_st", "_pend")
        + " & \". \" & _txtTotal & \" vêm \" & _txtOnde & \".\"",
        "    )",
        "VAR _htmlCab =",
        "    \"<span></span>\" & CONCATENATEX (",
        "        _serie,",
        "        VAR _vePar = _nCol <= 7 || MOD ( DATEDIFF ( dMes[Mes], _ref, MONTH ), 2 ) = 0",
        "        RETURN",
        "            \"<span class='h a-fd\" & IF ( dMes[Mes] = _ref, \" ref\", \"\" ) & \"' style='animation-delay:\" & ( [@ord] - 1 ) * 100 "
        "& \"ms'>\" & IF ( _vePar, [@rot], \"\" ) & \"</span>\",",
        "        \"\",",
        "        dMes[Mes], ASC",
        "    )",
        "VAR _htmlLinhas =",
        "    CONCATENATEX (",
        "        _itens,",
        "        VAR _i = dItemNota[Item]",
        "        RETURN",
        "            \"<span class='r'>\" & [@rot] & \"</span>\"",
        "                & CONCATENATEX (",
        "                    _serie,",
        "                    VAR _m = dMes[Mes]",
        # classe da célula lida da conta da matriz: cheio sálvia, parcial ocre, zero vermelho, sem dado tracejado, neutro
        "                    VAR _k = _i & \"@\" & FORMAT ( _m, \"yyyymm\" ) & \"=\"",
        "                    VAR _pk = SEARCH ( _k, _mx, 1, 0 )",
        "                    VAR _c = IF ( _pk = 0, \"f\", MID ( _mx, _pk + LEN ( _k ), 1 ) )",
        # valor fora da faixa (x): tracejado vermelho, à parte do "sem dado" (Fase 3, rodada 2, nit)
        "                    VAR _cls = SWITCH ( _c, \"c\", \"mk0\", \"p\", \"mk1\", \"z\", \"mk2\", \"n\", \"mkn\", \"x\", \"mkx\", \"mkm\" )",
        "                    VAR _atraso = ( [@ord] - 1 ) * 100 -- geometria",
        "                    RETURN",
        "                        \"<span class='c'><i class='mk \" & _cls & \"' style='animation-delay:\" & _atraso & \"ms'></i></span>\",",
        "                    \"\",",
        "                    dMes[Mes], ASC",
        "                ),",
        "        \"\",",
        "        [@o], ASC",
        "    )",
        "VAR _htmlObra =",
        "    \"<span class='r ob'>Obra</span>\" & CONCATENATEX (",
        "        _serie,",
        "        VAR _atraso = 600 + ( [@ord] - 1 ) * 100 -- geometria",
        "        VAR _k = \"obra@\" & FORMAT ( dMes[Mes], \"yyyymm\" ) & \"=\"",
        "        VAR _pk = SEARCH ( _k, _mx, 1, 0 )",
        "        VAR _c = IF ( _pk = 0, \"\", MID ( _mx, _pk + LEN ( _k ), 1 ) )",
        "        VAR _mk = IF ( _c IN { \"\", \"|\" }, \"\", \"<i class='mk mk\" & _c & \"'></i>\" )",
        "        RETURN",
        "            \"<span class='c ob'>\" & SUBSTITUTE ( _mk, \"'></i>\", \"' style='animation-delay:\" & _atraso & \"ms'></i>\" )"
        " & \"</span>\",",
        "        \"\",",
        "        dMes[Mes], ASC",
        "    )",
        "VAR _htmlLeg =",
        "    \"<p class='lg'><i class='mk mk0'></i>cheio<i class='mk mk1'></i>parcial<i class='mk mk2'></i>zero\"",
        "        & \"<i class='mk mkm'></i>sem dado\" & IF ( SEARCH ( \"=x\", _mx, 1, 0 ) > 0, \"<i class='mk mkx'></i>fora\", \"\" ) & \"</p>\"",
        "-- 4 · Marcação",
        "VAR _corpo =",
        "    \"<span class='vs sob'>\" & _txtSob & \"</span><h2 class='ach'>\" & _txtAchado & \"</h2>\"",
        "        & \"<div class='sec' style='margin-top:10px'><span class='vs'>Pontos de cada item, mês a mês</span>\"",
        "        & \"<div class='mx c8' style='grid-template-columns:132px repeat(\" & _nCol & \",1fr)'>\" & _htmlCab & _htmlLinhas & _htmlObra"
        " & \"</div>\" & _htmlLeg & \"</div>\"",
        "RETURN",
        "    IF ( NOT ISBLANK ( _po ), " + painel("e it", '"Leitura de Itens da nota"', "_corpo") + " )",
    ))

# Fase 2 da régua antiga (13/10/2026): a leitura dos sinais (régua antiga) virou a dos itens da nota. Fica fora da gravação; o
# gerador apaga o .dax que tinha escrito antes.
RETIRADAS = {"T2 · Leitura sinais · HTML",
             "T2 · Leitura quadradinho · HTML"}   # F3: o quadradinho saiu da tela

if __name__ == "__main__":
    sys.exit(gravar([x for x in MEDIDAS if x.nome not in RETIRADAS], RAIZ / "dax" / "T2" / "Leituras", GERADO))

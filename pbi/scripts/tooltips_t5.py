#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tooltips_t5 — desenho do tooltip de página da Tela 05 · Canteiro (pbi/dax/T5/Tooltips/**): o mês de Chuva e ritmo.
Mesma linguagem dos tooltips da T4 (tooltips_t4.CSS_T4: cabeçalho preto, corpo branco, cantos retos, pé preso à base):
uma obra por linha, da mais chuvosa para a menos, com os dias impraticáveis por chuva (barra creme, escala pelo maior
do mês, no mínimo 10 dias) e o executado no mês da obra; no pé, a carteira (média de dias por obra e executado
ponderado pelo orçamento). Página de 560 × 400: cabe até 9 obras.

F4 (pedido do Alisson, 28/10/2026; tooltip_lib): a lista ocupa o corpo inteiro, com linhas e fonte pela contagem de
obras; os números contam (marcas do contador.py), a barra de chuva cresce do zero em cascata (corrida) e cabeçalho,
linhas e pé entram na cascata C5.

    python -X utf8 pbi/scripts/tooltips_t5.py
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import contador as C  # noqa: E402
import desenho_projeto as D  # noqa: E402
import tooltip_lib as TL  # noqa: E402
from contas_lib_projeto import Medida, gravar  # noqa: E402
from desenho_comum import dax_lit  # noqa: E402
from tooltips_t4 import CSS_T4  # noqa: E402

RAIZ = AQUI.parent
GERADO = "pbi/scripts/tooltips_t5.py"
DES = r"T5 Canteiro\Tooltips"
MEDIDAS: list[Medida] = []
LARGURA, ALTURA = 560, 400
BARRA_X, BARRA_W = 150, 200      # barra dos dias de chuva na linha (corpo de 520)


def desenho(nome, descricao, dax):
    """Medida de desenho; os valores marcados com C.marca() viram odômetro no fim (F4)."""
    MEDIDAS.append(Medida(nome, DES, "texto", descricao, C.envolver_marcas(dax)))


def linhas(*ls) -> str:
    return "\n".join(l for g in ls for l in (g if isinstance(g, list) else [g]))


CSS_T5 = (
    ".tt .cr{position:relative;height:28px;white-space:nowrap}"
    ".tt .cr .nm{position:absolute;left:0;top:4px;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;"
    "font-size:16px;line-height:20px}"
    f".tt .cr .bc{{position:absolute;left:{BARRA_X}px;top:8px;height:12px;background:#E9E0CF}}"
    f".tt .cr .dc{{position:absolute;left:{BARRA_X + BARRA_W + 8}px;top:4px;font-size:14px;line-height:19px;"
    "color:#3B3B3F}"
    ".tt .cr .ex{position:absolute;right:0;top:4px;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;"
    "font-size:16px;line-height:20px}"
    # F4: linhas pela contagem (colunas em posição fixa: até 18 px), filhos centrados na altura da linha
    + TL.css_escala({".tt .ls .cr .nm": 16, ".tt .ls .cr .dc": 14, ".tt .ls .cr .ex": 16}, teto=18)
    + ".tt .ls .cr>*{top:50%;translate:0 -50%;line-height:1.25}"
    ".tt .ls .cr .bc{height:calc(12px * var(--k,1))}"
    + TL.entrada(".tt .ls>:nth-child({k})", [".tt .corpo>.bh"], pe=".tt .pe")
)
# linhas em grade dos tooltips de 02/11/2026 (qualidade do mês, segurança e suprimentos da obra): a fonte vai na linha
# (escala pela contagem, teto de 20 px) e os filhos e as colunas em em, então tudo cresce junto e nada sai da coluna;
# filhos no fluxo (sem position:absolute), entrelinha relativa. O que varia de largura fica à esquerda das colunas fixas
# da direita (marca e %), que assim alinham de uma linha para outra.
CSS_Q5 = (
    ".tt .q5{display:grid;align-items:center;column-gap:.6em;white-space:nowrap}"
    ".tt .q5>*{min-width:0;line-height:1.25}"
    ".tt .q5 .n{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:1.067em}"
    ".tt .q5 .d,.tt .q5 .a{font-size:.933em;color:#3B3B3F}"
    ".tt .q5 .d{text-align:right}.tt .q5 .a.z{color:#6B6B70}"
    ".tt .q5 .v{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:1.067em;text-align:right}"
    ".tt .q5>i{justify-self:center}"
    ".tt .qa{grid-template-columns:1em minmax(0,1fr) auto 4.6em}"
    ".tt .qs{grid-template-columns:4.4em minmax(0,1fr) auto 1em 4.6em}"
    ".tt .qp{grid-template-columns:4.4em minmax(0,1fr) 1em 4.6em}"
    ".tt .q5 .n.ref{text-decoration:underline;text-underline-offset:3px}"
    ".tt .pe .rod b{font-weight:600}"
    + TL.css_fontes({".tt .ls .q5": 15}, teto=20)
)
desenho("T5 · Tooltip · CSS", "CSS dos tooltips de página da T5: o dos tooltips da T4 (tooltips_t4.CSS_T4), as linhas de "
        "chuva e executado por obra e as linhas em grade da qualidade do mês, da segurança e dos suprimentos da obra.",
        "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(CSS_T4 + CSS_T5 + CSS_Q5))

desenho(
    "T5 · Tooltip mês · HTML",
    "Tooltip de página do mês (coluna de Chuva e ritmo): uma obra por linha, da mais chuvosa para a menos, com os dias "
    "impraticáveis por chuva (barra creme, escala pelo maior do mês, no mínimo 10) e o executado no mês da obra; no pé, "
    "a carteira (dias por obra, em média, e executado ponderado pelo orçamento).",
    linhas(
        "-- 1 · Leituras",
        "VAR _mesC = UPPER ( [Mês · rótulo curto] )",
        "VAR _mesL = [Mês · longo]",
        "VAR _chC = [Canteiro · dias de chuva]",
        "VAR _exC = [Físico · executado no mês]",
        "VAR _obras =",
        "    ADDCOLUMNS (",
        "        VALUES ( dObra[Obra] ),",
        '        "@ch", [Canteiro · dias de chuva],',
        '        "@ex", [Físico · executado no mês]',
        "    )",
        "VAR _comBase = FILTER ( _obras, NOT ISBLANK ( [@ch] ) || NOT ISBLANK ( [@ex] ) ) /* lista */",
        "-- 2 · Textos",
        D.numero("_chC", "_tc"), D.pct("_exC", "_te"),
        D.od_tabela(), D.od_num("_chC", "_tc"), D.od_pct("_exC", "_te"),
        "-- 3 · Geometria",
        "VAR _max = MAX ( 10, MAXX ( _comBase, [@ch] ) ) /* geometria */",
        "VAR _nLs = COUNTROWS ( _comBase ) /* lista */",
        "-- 4 · Marcação",
        "VAR _htmlLinhas =",
        "    CONCATENATEX (",
        "        _comBase,",
        "        VAR _ch = [@ch]",
        "        VAR _ex = [@ex]",
        f"        VAR _w = IF ( _ch > 0, MAX ( 2, ROUND ( DIVIDE ( _ch, _max ) * {BARRA_W}, 0 ) ), 0 ) -- geometria",
        '        VAR _txtCh = IF ( ISBLANK ( _ch ), "—", ' + C.marca('FORMAT ( _ch, "0", "pt-BR" )') + ' & IF ( _ch = 1, " dia", " dias" ) )',
        '        VAR _txtEx = IF ( ISBLANK ( _ex ), "—", ' + C.marca('FORMAT ( _ex * 100, "0.0", "pt-BR" )') + ' & "%" )',
        "        VAR _rd = ( RANKX ( _comBase, [@ch], _ch, DESC, Dense ) - 1 ) * 60 -- geometria",
        "        RETURN",
        "            \"<div class='cr'><span class='nm'>\" & " + D.esc("dObra[Obra]") + " & \"</span>\"",
        "                & IF ( _w > 0, \"<i class='bc' style='width:\" & _w & \"px' data-rk='ch|\" & dObra[Obra] "
        "& \"' data-rd='\" & _rd & \"'></i>\" ) /* geometria */",
        f"                & \"<span class='dc' style='left:\" & ( {BARRA_X} + _w + 8 ) & \"px'>\" & _txtCh & \"</span>\"",
        "                & \"<span class='ex'>\" & _txtEx & \"</span></div>\",",
        "        \"\",",
        "        [@ch], DESC,",
        "        dObra[Obra], ASC",
        "    )",
        "RETURN",
        "    IF (",
        "        NOT ISEMPTY ( _comBase ),",
        "        \"<div class='u tt'><div class='cab'><p class='vs'>CHUVA E RITMO · \" & _mesC & \"</p>\"",
        "            & \"<div class='lin1'><div class='tit'><b>\" & _mesL & \"</b></div></div></div>\"",
        "            & \"<div class='corpo lim'><div class='bh'><span class='vs'>DIAS IMPRATICÁVEIS POR CHUVA, POR OBRA</span>\"",
        "            & \"<span class='vs'>EXECUTADO</span></div><div class='lsc\" & " + TL.atributos("_nLs") + "'>\" "
        "& _htmlLinhas & \"</div></div>\"",
        "            & \"<div class='pe'><div class='dd'><span class='vs'>CARTEIRA</span><b>\" & _tcOd & \"</b>\"",
        "            & \"<span class='dt'>dias por obra, em média · </span><b>\" & _teOd & \"</b><span class='dt'>executado, \"",
        "            & \"pelo orçamento</span></div></div>\"",
        "        & \"</div>\" & [Comum · JS contador tooltip] & [Comum · JS corrida]",
        "    )",
    ))

# ===================================================================================================== 02/11/2026
# Pedido do Alisson: tooltip em todo gráfico da T5, com o ponto sob o mouse e sem repetir o que o gráfico já mostra.
# Qualidade, mês a mês (camada T5_Qua_Meses, mês sob o mouse): cada obra no mês. Segurança e Suprimentos por obra
# (linha sob o mouse): a obra mês a mês na janela e, no pé, o que a linha não mostra.

def cls_item(pts: str, poss: str) -> str:
    """Classe da marca pelos pontos de um item da nota: "0" cheio · "1" parcial · "2" zero · "" sem dado."""
    return f'IF ( ISBLANK ( {pts} ), "", IF ( {pts} >= {poss}, "0", IF ( {pts} = 0, "2", "1" ) ) )'


def marca_item(cls: str) -> str:
    """DAX: a marca do item (ou um <i> vazio, para a coluna da grade não andar)."""
    return f"IF ( {cls} = \"\", \"<i></i>\", \"<i class='mk mk\" & {cls} & \"'></i>\" )"


def pts(v: str) -> str:
    """DAX: pontos da nota ("0,25", "0,5", "1") contando."""
    return C.marca(f'FORMAT ( {v}, "0.##", "pt-BR" )')


def cabecalho(sob: str, tit: str) -> list[str]:
    return [
        "        \"<div class='u tt'><div class='cab'><p class='vs'>\" & " + sob + " & \"</p>\"",
        "            & \"<div class='lin1'><div class='tit'>\" & " + tit + " & \"</div></div></div>\"",
    ]


def titulo_obra() -> str:
    return ("\"<b>\" & " + D.esc("_obra") + " & \"</b>\" & IF ( _selo = \"\" || ISBLANK ( _selo ), \"\", "
            "\"<span class='selo \" & IF ( _selo = \"REAL\", \"selo-r\", \"selo-i\" ) & \"'>\" & _selo & \"</span>\" )")


LEITURAS_OBRA = [
    "VAR _obra = [Obra · nome]",
    "VAR _selo = [Obra · selo]",
    "VAR _ini = [Série · primeiro mês]",
    "VAR _ref = [Mês de referência]",
]
TEXTOS_OBRA = [
    'VAR _txtPer = UPPER ( FORMAT ( _ini, "mmm/yy", "pt-BR" ) ) & IF ( _ini = _ref, "", "–" & UPPER ( FORMAT ( _ref, '
    '"mmm/yy", "pt-BR" ) ) )',
    'VAR _txtRef = FORMAT ( _ref, "mmm/yy", "pt-BR" )',
]
ALTURA_QUA, ALTURA_SEG, ALTURA_SUP = 440, 500, 480

desenho(
    "T5 · Tooltip qualidade · HTML",
    "Tooltip de página do mês da Qualidade, mês a mês (camada T5_Qua_Meses): cada obra com base no mês, da menor "
    "aprovação na 1.ª inspeção para a maior, com a marca pelos pontos do item, os serviços aprovados de primeira de "
    "verificados e a aprovação (vermelha abaixo da meta); no pé, a carteira e quantas obras ficaram abaixo da meta (o "
    "ponto cheio do item). O gráfico só tem as linhas: os números de cada obra no mês aparecem só aqui.",
    linhas(
        "-- 1 · Leituras",
        "VAR _mesC = UPPER ( [Mês · rótulo curto] )",
        "VAR _mesL = [Mês · longo]",
        "VAR _cart = [Canteiro · aprovação na 1.ª inspeção]",
        "VAR _apC = [Canteiro · aprovados na 1.ª inspeção]",
        "VAR _vfC = [Canteiro · serviços verificados]",
        "VAR _lim = [Nota · limite inspeção · ponto cheio]",
        "VAR _abx = [T5 · Inspeção · obras abaixo da meta]",
        "VAR _obras =",
        "    ADDCOLUMNS (",
        "        VALUES ( dObra[Obra] ),",
        '        "@v", [Canteiro · aprovação na 1.ª inspeção],',
        '        "@ap", [Canteiro · aprovados na 1.ª inspeção],',
        '        "@vf", [Canteiro · serviços verificados],',
        '        "@pt", [Nota · pontos inspeção],',
        '        "@ps", [Nota · possíveis · inspeção]',
        "    )",
        "VAR _com = FILTER ( _obras, NOT ISBLANK ( [@v] ) ) /* lista */",
        "VAR _nLs = COUNTROWS ( _com ) /* lista */",
        "-- 2 · Textos",
        D.pct("_cart", "_tc"), D.pct("_lim", "_tl", casas=0),
        "VAR _txtAbx = SWITCH ( _abx, 0, \"nenhuma obra abaixo\", 1, " + C.marca("1") + " & \" obra abaixo\", "
        + C.marca("_abx") + " & \" obras abaixo\" )",
        "-- 4 · Marcação",
        "VAR _htmlLinhas =",
        "    CONCATENATEX (",
        "        _com,",
        "        VAR _v = [@v]",
        "        VAR _cls = " + cls_item("[@pt]", "[@ps]"),
        "        RETURN",
        "            \"<div class='q5 qa'>\" & " + marca_item("_cls") + " & \"<span class='n'>\" & "
        + D.esc("dObra[Obra]") + " & \"</span>\"",
        "                & \"<span class='d'>\" & " + C.marca('FORMAT ( [@ap], "#,0", "pt-BR" )') + " & \" de \" & "
        + C.marca('FORMAT ( [@vf], "#,0", "pt-BR" )') + " & \"</span>\"",
        "                & \"<span class='v\" & IF ( _v < _lim, \" ng\", \"\" ) & \"'>\" & "
        + C.marca('FORMAT ( _v * 100, "0.0", "pt-BR" )') + " & \"%</span></div>\",",
        "        \"\",",
        "        [@v], ASC,",
        "        dObra[Obra], ASC",
        "    )",
        "RETURN",
        "    IF (",
        "        NOT ISEMPTY ( _com ),",
        cabecalho("\"QUALIDADE, MÊS A MÊS · \" & _mesC", "\"<b>\" & _mesL & \"</b>\""),
        "            & \"<div class='corpo'><div class='bh'><span class='vs'>APROVAÇÃO NA 1.ª INSPEÇÃO, POR OBRA</span>\"",
        "            & \"<span class='vs'>APROVADOS DE VERIFICADOS</span></div><div class='lsq\" & "
        + TL.atributos("_nLs") + "'>\" & _htmlLinhas & \"</div></div>\"",
        "            & \"<div class='pe'><p class='rod'><b>Carteira:</b> \" & " + C.marca("_tcTxt") + " & \" (\" & "
        + C.marca('FORMAT ( _apC, "#,0", "pt-BR" )') + " & \" de \" & " + C.marca('FORMAT ( _vfC, "#,0", "pt-BR" )')
        + " & \" serviços aprovados de primeira).</p>\"",
        "            & \"<p class='rod'>Meta \" & " + C.marca("_tlTxt") + " & \", o ponto cheio do item · \" & _txtAbx "
        "& \".</p></div>\"",
        "        & \"</div>\" & [Comum · JS contador tooltip]",
        "    )",
    ))

desenho(
    "T5 · Tooltip segurança · HTML",
    "Tooltip de página da obra de Segurança por obra (linha sob o mouse): a obra mês a mês na janela, com os acidentes "
    "com afastamento do mês e a conformidade NR-18 (conformes de aplicáveis, a marca pelos pontos do item NR-18 no mês); "
    "no pé, os acidentes, as HHT e a taxa de gravidade de 12 meses e os pontos dos itens acidentes e NR-18 na nota do mês "
    "de referência. A linha já mostra a taxa de frequência de 12 meses e o NR-18 do mês: não se repetem.",
    linhas(
        "-- 1 · Leituras",
        LEITURAS_OBRA,
        "VAR _ac12 = [Canteiro · acidentes 12 meses · ref]",
        "VAR _hht = [Canteiro · HHT 12 meses · ref]",
        "VAR _tg = [Canteiro · taxa de gravidade (12 meses) · ref]",
        "VAR _pta = [Nota · pontos acidentes · ref]",
        "VAR _psa = [Nota · possíveis · acidentes · ref]",
        "VAR _ptn = [Nota · pontos NR-18 · ref]",
        "VAR _psn = [Nota · possíveis · NR-18 · ref]",
        "VAR _meses =",
        "    ADDCOLUMNS (",
        "        VALUES ( dMes[Mes] ),",
        '        "@ate", [Série · mês até a referência],',
        '        "@rot", [Mês · rótulo curto],',
        '        "@ac", [Canteiro · acidentes],',
        '        "@nr", [Canteiro · conformidade NR-18],',
        '        "@cf", [Canteiro · NR-18 conformes],',
        '        "@apl", [Canteiro · NR-18 aplicáveis],',
        '        "@pt", [Nota · pontos NR-18],',
        '        "@ps", [Nota · possíveis · NR-18]',
        "    )",
        "VAR _com = FILTER ( _meses, [@ate] = 1 && ( NOT ISBLANK ( [@ac] ) || NOT ISBLANK ( [@nr] ) ) ) /* lista */",
        "VAR _nLs = COUNTROWS ( _com ) /* lista */",
        "-- 2 · Textos",
        TEXTOS_OBRA,
        "VAR _txt12 =",
        "    IF (",
        "        ISBLANK ( _hht ),",
        "        \"Sem HHT na base nos 12 meses.\",",
        "        IF ( _ac12 > 0, " + C.marca('FORMAT ( _ac12, "0", "pt-BR" )') + " & IF ( _ac12 = 1, \" acidente\", "
        "\" acidentes\" ) & \" com afastamento em \", \"Nenhum acidente com afastamento em \" )",
        "            & " + C.marca('FORMAT ( _hht, "#,0", "pt-BR" )') + " & \" HHT\"",
        "            & IF ( _ac12 > 0 && NOT ISBLANK ( _tg ), \"; taxa de gravidade \" & "
        + C.marca('FORMAT ( _tg, "0.0", "pt-BR" )') + ", \"\" ) & \".\"",
        "    )",
        "VAR _txtPts =",
        "    \"Na nota de \" & _txtRef & \": acidentes \" & IF ( ISBLANK ( _pta ), \"sem dado\", " + pts("_pta")
        + " & \" de \" & " + pts("_psa") + " )",
        "        & \" · NR-18 \" & IF ( ISBLANK ( _ptn ), \"sem dado\", " + pts("_ptn") + " & \" de \" & " + pts("_psn")
        + " ) & \".\"",
        "-- 4 · Marcação",
        "VAR _htmlLinhas =",
        "    CONCATENATEX (",
        "        _com,",
        "        VAR _ac = [@ac]",
        "        VAR _nr = [@nr]",
        "        VAR _cls = " + cls_item("[@pt]", "[@ps]"),
        "        VAR _htmlAc =",
        "            SWITCH (",
        "                TRUE (),",
        "                ISBLANK ( _ac ), \"<span class='a z'>—</span>\",",
        "                _ac = 0, \"<span class='a z'>sem acidente</span>\",",
        "                \"<span class='a ng'>\" & " + C.marca('FORMAT ( _ac, "0", "pt-BR" )')
        + " & IF ( _ac = 1, \" acidente\", \" acidentes\" ) & \"</span>\"",
        "            )",
        "        RETURN",
        "            \"<div class='q5 qs'><span class='n\" & IF ( dMes[Mes] = _ref, \" ref\", \"\" ) & \"'>\" & [@rot] "
        "& \"</span>\" & _htmlAc",
        "                & \"<span class='d'>\" & IF ( ISBLANK ( _nr ), \"\", " + C.marca('FORMAT ( [@cf], "#,0", "pt-BR" )')
        + " & \" de \" & " + C.marca('FORMAT ( [@apl], "#,0", "pt-BR" )') + " ) & \"</span>\"",
        "                & " + marca_item("_cls") + " & \"<span class='v'>\" & IF ( ISBLANK ( _nr ), \"—\", "
        + C.marca('FORMAT ( _nr * 100, "0.0", "pt-BR" )') + " & \"%\" ) & \"</span></div>\",",
        "        \"\",",
        "        dMes[Mes], ASC",
        "    )",
        "RETURN",
        "    IF (",
        "        NOT ISEMPTY ( _com ) && HASONEVALUE ( dObra[Obra] ),",
        cabecalho("\"SEGURANÇA POR OBRA · \" & _txtPer", titulo_obra()),
        "            & \"<div class='corpo'><div class='bh'><span class='vs'>ACIDENTES COM AFASTAMENTO NO MÊS</span>\"",
        "            & \"<span class='vs'>NR-18 · CONFORMES DE APLICÁVEIS</span></div><div class='lsq\" & "
        + TL.atributos("_nLs") + "'>\" & _htmlLinhas & \"</div></div>\"",
        "            & \"<div class='pe'><p class='rod'><b>12 meses:</b> \" & _txt12 & \"</p>\"",
        "            & \"<p class='rod'>\" & _txtPts & \"</p></div>\"",
        "        & \"</div>\" & [Comum · JS contador tooltip]",
        "    )",
    ))

desenho(
    "T5 · Tooltip suprimentos · HTML",
    "Tooltip de página da obra de Suprimentos por obra (linha sob o mouse): a obra mês a mês na janela, com os pedidos "
    "entregues no prazo e completos de previstos e a taxa (marca pelos pontos do item entregas no mês; vermelha abaixo da "
    "meta); no pé, o total da janela e a meta com os pontos do item na nota do mês de referência. A linha já mostra o mês "
    "de referência: aqui ele é só a última linha da série.",
    linhas(
        "-- 1 · Leituras",
        LEITURAS_OBRA,
        "VAR _lim = [Nota · limite entregas · ponto cheio]",
        "VAR _npJ = [T5 · Entregas · pedidos no prazo na janela]",
        "VAR _ppJ = [T5 · Entregas · pedidos previstos na janela]",
        "VAR _xJ = [T5 · Entregas · taxa na janela]",
        "VAR _ptR = [Nota · pontos entregas · ref]",
        "VAR _psR = [Nota · possíveis · entregas · ref]",
        "VAR _meses =",
        "    ADDCOLUMNS (",
        "        VALUES ( dMes[Mes] ),",
        '        "@ate", [Série · mês até a referência],',
        '        "@rot", [Mês · rótulo curto],',
        '        "@x", [Canteiro · entregas no prazo],',
        '        "@np", [Canteiro · pedidos no prazo],',
        '        "@pp", [Canteiro · pedidos previstos],',
        '        "@pt", [Nota · pontos entregas],',
        '        "@ps", [Nota · possíveis · entregas]',
        "    )",
        "VAR _com = FILTER ( _meses, [@ate] = 1 && NOT ISBLANK ( [@x] ) ) /* lista */",
        "VAR _nLs = COUNTROWS ( _com ) /* lista */",
        "-- 2 · Textos",
        TEXTOS_OBRA,
        D.pct("_lim", "_tl", casas=0),
        "VAR _txtJan =",
        "    IF (",
        "        ISBLANK ( _xJ ),",
        "        \"Sem pedido previsto na janela.\",",
        "        " + C.marca('FORMAT ( _npJ, "#,0", "pt-BR" )') + " & \" de \" & " + C.marca('FORMAT ( _ppJ, "#,0", "pt-BR" )')
        + " & \" pedidos no prazo e completos (\" & " + C.marca('FORMAT ( _xJ * 100, "0.0", "pt-BR" )') + " & \"%).\"",
        "    )",
        "VAR _txtMeta =",
        "    \"Meta \" & " + C.marca("_tlTxt") + " & \" · na nota de \" & _txtRef & \": entregas \" & IF ( ISBLANK ( _ptR ), "
        "\"sem dado\", " + pts("_ptR") + " & \" de \" & " + pts("_psR") + " ) & \".\"",
        "-- 4 · Marcação",
        "VAR _htmlLinhas =",
        "    CONCATENATEX (",
        "        _com,",
        "        VAR _x = [@x]",
        "        VAR _cls = " + cls_item("[@pt]", "[@ps]"),
        "        RETURN",
        "            \"<div class='q5 qp'><span class='n\" & IF ( dMes[Mes] = _ref, \" ref\", \"\" ) & \"'>\" & [@rot] "
        "& \"</span>\"",
        "                & \"<span class='d'>\" & " + C.marca('FORMAT ( [@np], "#,0", "pt-BR" )') + " & \" de \" & "
        + C.marca('FORMAT ( [@pp], "#,0", "pt-BR" )') + " & IF ( [@pp] = 1, \" pedido\", \" pedidos\" ) & \"</span>\"",
        "                & " + marca_item("_cls") + " & \"<span class='v\" & IF ( _x < _lim, \" ng\", \"\" ) & \"'>\" & "
        + C.marca('FORMAT ( _x * 100, "0.0", "pt-BR" )') + " & \"%</span></div>\",",
        "        \"\",",
        "        dMes[Mes], ASC",
        "    )",
        "RETURN",
        "    IF (",
        "        NOT ISEMPTY ( _com ) && HASONEVALUE ( dObra[Obra] ),",
        cabecalho("\"SUPRIMENTOS POR OBRA · \" & _txtPer", titulo_obra()),
        "            & \"<div class='corpo'><div class='bh'><span class='vs'>PEDIDOS NO PRAZO E COMPLETOS, MÊS A MÊS</span>\"",
        "            & \"<span class='vs'>TAXA</span></div><div class='lsq\" & " + TL.atributos("_nLs")
        + "'>\" & _htmlLinhas & \"</div></div>\"",
        "            & \"<div class='pe'><p class='rod'><b>Na janela:</b> \" & _txtJan & \"</p>\"",
        "            & \"<p class='rod'>\" & _txtMeta & \"</p></div>\"",
        "        & \"</div>\" & [Comum · JS contador tooltip]",
        "    )",
    ))

if __name__ == "__main__":
    sys.exit(gravar(MEDIDAS, RAIZ / "dax" / "T5", GERADO))

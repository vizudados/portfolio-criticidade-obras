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
desenho("T5 · Tooltip · CSS", "CSS do tooltip de página da T5: o dos tooltips da T4 (tooltips_t4.CSS_T4) mais as linhas "
        "de chuva e executado por obra.",
        "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(CSS_T4 + CSS_T5))

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

if __name__ == "__main__":
    sys.exit(gravar(MEDIDAS, RAIZ / "dax" / "T5", GERADO))

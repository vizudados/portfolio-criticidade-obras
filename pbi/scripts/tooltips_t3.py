#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tooltips_t3 — desenho dos tooltips de página da Tela 03 · Avanço físico (pbi/dax/T3/Tooltips/**). As contas que eles
leem estão em contas_t3.py (pasta T3 Avanço físico\\…\\Contas) e em base/.

Redesenho v2 (Figma FjBWDk5odF9HaZ2pwhGosl, página 04 · Redesenho v2, seção 379:790, Fileira · Tooltips 388:4064;
pbi/spec/redesenho/t03.md): Mês da curva 390:2268 (· mês de referência 390:2296, · primeiro mês 390:2324, · sem
previsto 390:2348), Mês do ritmo 391:4199 (· sem previsto 391:4257, · primeiro mês 391:4283), Obra na linha do
tempo 391:4387 (· a iniciar 391:4422, · sem previsto 391:4476), Obra no avanço 391:6395 (adiantada; · atrás 391:6438,
· sem previsto 391:6501). Cartão branco de
cantos retos e contorno preto; cabeçalho preto de 72 px (sobretítulo, título 21 com código e selo, meta à direita em
flex-wrap: quando não cabe com 24 px de folga, desce para a 2.ª linha e o cabeçalho vai a 94); corpo em fluxo (três
colunas de valor 21, linhas Segoe 15 e valores Barlow 16); rodapé de uma linha preso ao pé (margin-top:auto, L019).
CSS próprio da T3 sobre [Comum · CSS base] (não depende de [Comum · CSS tooltip]). Larguras: 560 (avanço 600: o mini
gráfico de colunas cresce em largura, 560 ÷ n por mês).

Janela (dJanela, 1 a 12 meses): o mini gráfico do avanço põe cada mês em [Série · posição na janela], coluna = 560 ÷ n,
rótulos em todos os meses quando cabem (coluna ≥ 40 px), senão só referência, máximo e mínimo. Barras na cor do
item prazo da nota ([T3 · Status desvio físico]: dentro do limite sálvia, fora vermelho); desvio físico negativo com .ng (rótulo vermelho); desvio de desembolso negativo em preto. Obra sem previsto na
planilha (JANGADA): "sem previsto na planilha", sem desvio nem faixa (nada vira 0).

Troca da régua pela nota (13/10/2026): o status do físico é o do item prazo da nota (dentro ou fora do limite);
a mobilização e a trava saem; o desembolso do mês mostra os pontos do fluxo de caixa; a obra da linha do tempo mostra
a Nota da obra (ou "pendente · X de Y") e os itens em que mais perde pontos.

    python -X utf8 pbi/scripts/tooltips_t3.py
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import desenho_comum as DC  # noqa: E402
import desenho_projeto as D  # noqa: E402
import contador as C  # noqa: E402
import tooltip_lib as TL  # noqa: E402
from contas_lib_projeto import Medida, gravar  # noqa: E402
from desenho_comum import GRAFITE, PRETO, REGRA, SALVIA, TERC, VERM, CREME, dax_lit  # noqa: E402

RAIZ = AQUI.parent
GERADO = "pbi/scripts/tooltips_t3.py"
MEDIDAS: list[Medida] = []
DES = r"T3 Avanço físico\Tooltips"
SEM_P = "sem previsto na planilha"


def desenho(nome, descricao, dax):
    """Medida de desenho; os valores marcados com C.marca() viram odômetro no fim (F4)."""
    MEDIDAS.append(Medida(nome, DES, "texto", descricao, C.envolver_marcas(dax)))


def linhas(*ls) -> str:
    return "\n".join(l for g in ls for l in (g if isinstance(g, list) else [g]))


def faixa_vs(s: str) -> str:
    """Versalete do status do físico na nota ([T3 · Status desvio físico]: 0 dentro do limite, 2 fora)."""
    return f'SWITCH ( {s}, 2, "FORA DO LIMITE", 0, "NO LIMITE", "" )'


def faixa(s: str) -> str:
    return f'SWITCH ( {s}, 2, "fora do limite", "dentro do limite" )'


def mudou(de: str, para: str) -> str:
    """Frase da troca de status do físico na nota (os dois meses com status)."""
    return f'IF ( {para} = 2, "passou do limite da nota", "voltou para dentro do limite" )'


def ordinal(n: str) -> str:
    casos = ", ".join(f'{i}, "{t}"' for i, t in enumerate(
        ["", "primeiro", "segundo", "terceiro", "quarto", "quinto", "sexto", "sétimo", "oitavo", "nono", "décimo"]) if i)
    return f'SWITCH ( {n}, {casos}, FORMAT ( {n}, "0" ) & ".º" )'


def extenso(n: str) -> str:
    casos = ", ".join(f'{i}, "{t}"' for i, t in enumerate(
        ["zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez", "onze", "doze"]))
    return f'SWITCH ( {n}, {casos}, FORMAT ( {n}, "0" ) )'


def em_meses(n: str) -> str:
    """'em oito meses' (n = meses da obra na janela): substitui o 'do semestre' fixo."""
    return f'"em " & {extenso(n)} & " meses"'


def mes_curto(d: str) -> str:
    return f'FORMAT ( {d}, "mmm/yy", "pt-BR" )'


def mes_nome(d: str) -> str:
    return f'FORMAT ( {d}, "mmmm", "pt-BR" )'


def desde(d: str) -> str:
    """Mês de um 'desde': por extenso; mês/ano quando bate no começo da janela (_jan) ou cai em outro ano que a
    referência (_ref) — 'desde jan/26'. A medida precisa das VAR _jan e _ref."""
    return f'IF ( {d} = _jan || YEAR ( {d} ) <> YEAR ( _ref ), {mes_curto(d)}, {mes_nome(d)} )'


def selo(var_selo: str) -> str:
    return (f"IF ( {var_selo} = \"\", \"\", \"<span class='selo \" & IF ( {var_selo} = \"REAL\", \"selo-r\", \"selo-i\" ) "
            f"& \"'>\" & {var_selo} & \"</span>\" )")


def col(rotulo: str, valor: str) -> str:
    """Uma coluna das três: versalete (DAX) e valor HTML (DAX) dentro de <b>."""
    return f"\"<div><span class='vs'>\" & {rotulo} & \"</span><b>\" & {valor} & \"</b></div>\""


def col_sem(rotulo: str) -> str:
    """Coluna sem o valor na planilha: o versalete e a nota no lugar do número."""
    return f"\"<div><span class='vs'>\" & {rotulo} & \"</span><b class='sp'>{SEM_P}</b></div>\""


def col3(*cols: tuple[str, str]) -> str:
    """Três colunas: [(versalete DAX, valor HTML DAX)]."""
    return "\"<div class='c3'>\" & " + " & ".join(col(r, v) for r, v in cols) + " & \"</div>\""


def cab(sob: str, tit: str, dir_: str) -> str:
    """Cabeçalho preto: sobretítulo; título (HTML DAX) e meta à direita na mesma linha, em flex-wrap."""
    return (f"\"<div class='cab'><p class='vs sob'>\" & {sob} & \"</p><div class='tl'><div class='tit'>\" & {tit} "
            f"& \"</div><p class='vs dir'>\" & {dir_} & \"</p></div></div>\"")


def rod(rotulo: str, texto: str) -> str:
    """Rodapé preso ao pé (uma linha): regra, versalete e a frase."""
    return (f"\"<div class='rod'><div class='r3'></div><span class='vs'>\" & {rotulo} & \"</span><p class='l1'>\" & "
            f"{texto} & \"</p></div>\"")


def li(*itens: tuple[str, str]) -> str:
    """Uma linha 'Rótulo valor · Rótulo valor': [(rótulo fixo, valor HTML DAX)]."""
    return ("\"<div class='li'>\" & " + " & ".join(
        f"\"<span class='n'>{r}</span><span class='v'>\" & {v} & \"</span>\"" for r, v in itens) + " & \"</div>\"")


CSS_T3 = (
    # cartão: branco (pedido do Alisson, 07/10: só o cabeçalho é preto), contorno 1 px preto, cantos retos; coluna flexível para o rodapé ficar preso ao pé
    f".tt{{position:fixed;inset:0;display:flex;flex-direction:column;background:#FFFFFF;border:1px solid {PRETO};"
    "overflow:hidden}"
    f".tt .cab{{flex:none;background:{PRETO};padding:14px 20px 12px}}"
    f".tt .cab .vs{{color:{CREME}}}"
    ".tt .cab .tl{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;column-gap:24px;"
    "row-gap:6px;margin-top:5px}"
    ".tt .cab .tit{display:flex;align-items:center;gap:10px;white-space:nowrap;min-height:26px}"
    ".tt .cab .tit b{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:21px;line-height:26px;"
    "color:#FFFFFF}"
    ".tt .cab .tit em{font-style:normal;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:12px;"
    f"letter-spacing:1.2px;text-transform:uppercase;color:{CREME}}}"
    f".tt .cab .tit .selo-i{{border:1px dashed {CREME};color:{CREME}}}"
    f".tt .cab .tit .selo-r{{background:{CREME};color:{PRETO}}}"
    ".tt .cab .dir{white-space:nowrap}"
    ".tt .corpo{flex:none;padding:16px 20px 0}"
    ".tt .rod{margin-top:auto;padding:0 20px 16px}"
    ".tt .rod.sr{padding-top:0}"
    ".tt .vs{display:block}"
    # três colunas de valor (Destaque · nome 21/26) ou a nota "sem previsto na planilha"
    ".tt .c3{display:grid;grid-template-columns:minmax(155px,auto) minmax(155px,auto) 1fr;column-gap:18px}"
    ".tt .c3 .vs{white-space:nowrap}"
    ".tt .c3 b{display:block;margin-top:6px;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;"
    "font-size:21px;line-height:26px;white-space:nowrap}"
    f".tt .c3 b.sp{{font-family:'Segoe UI',sans-serif;font-weight:400;font-size:15px;line-height:20px;color:{GRAFITE};"
    "margin-top:9px}"
    ".tt .c3 b .mk{margin-right:6px;vertical-align:2px}"
    f".tt .r3{{height:1px;background:{REGRA};margin:12px 0}}"
    ".tt .rod .r3{margin-top:0}"
    # linhas "Rótulo valor · Rótulo valor · detalhe" (Texto · forte 15, Valor 16, Texto 15)
    ".tt .li{display:flex;align-items:baseline;white-space:nowrap;margin-top:6px;line-height:21px}"
    ".tt .li .n{font-size:15px;font-weight:600;margin-right:6px}"
    ".tt .li .v{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:16px;margin-right:22px}"
    ".tt .li .v .mk,.tt .st .v .mk{margin-right:6px;vertical-align:0}"
    f".tt .li .d{{font-size:15px;color:{GRAFITE};overflow:hidden;text-overflow:ellipsis}}"
    ".tt .l1{font-size:15px;line-height:21px;margin-top:6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
    ".tt .corpo .c3+.l1{margin-top:8px}"
    # status da obra: chip, pontos e desde quando
    ".tt .st{display:flex;align-items:center;white-space:nowrap;margin-top:6px;height:25px}"
    ".tt .st .chip{margin-right:12px}"
    ".tt .st .v{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:16px;margin-right:6px}"
    f".tt .st .pt{{font-size:15px;color:{GRAFITE};margin-right:22px}}"
    f".tt .st .d{{font-size:15px;color:{GRAFITE}}}"
    # mini gráfico do avanço: uma série, sem eixo nem legenda; colunas de 560 ÷ n px (n = meses da janela)
    ".tt .mc{position:relative;margin-top:8px}"
    f".tt .mc .ms{{position:absolute;text-align:center;font-size:13px;line-height:16px;white-space:nowrap;color:{GRAFITE}}}"
    f".tt .mc .ms.ref{{font-weight:600;color:{PRETO}}}.tt .mc .ms.sem{{opacity:.45;color:{TERC}}}"
    ".tt .mc .b{position:absolute}"
    f".tt .mc .b.s0{{background:{SALVIA}}}.tt .mc .b.s1{{background:{DC.OCRE}}}.tt .mc .b.s2{{background:{VERM}}}"
    f".tt .mc .b.se{{background:{PRETO}}}.tt .mc .b.z{{background:{REGRA}}}"
    ".tt .mc .vl{position:absolute;text-align:center;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;"
    f"font-size:14px;line-height:17px;white-space:nowrap;color:{GRAFITE}}}"
    f".tt .mc .vl.ref{{color:{PRETO}}}"
    "@keyframes ttFim{from{opacity:0}}"
    ".tt .fim{animation:ttFim .2s ease-out backwards}"
    "@media (prefers-reduced-motion:reduce){.tt .fim{animation:none}}"
)
# F4 (28/10/2026): estrutura fixa (colunas de valor, linhas, status, mini gráfico) e páginas do tamanho do conteúdo; o
# corpo passa a ocupar a altura até o rodapé e distribui os blocos (sem a faixa vazia quando um bloco não vem), e cada
# bloco entra em cascata (C5), com marcas e pílulas crescendo
CSS_F4 = (".tt .corpo{flex:1 1 auto;min-height:0;display:flex;flex-direction:column;justify-content:space-evenly;"
          "padding-bottom:8px}.tt .corpo>*{flex:none}"
          + TL.entrada(".tt .corpo>:nth-child({k})", pe=".tt .rod"))
desenho("T3 · Tooltip · CSS", "CSS dos tooltips de página da Tela 03 (v2): cartão branco de cantos retos, cabeçalho "
        "preto de 72 px com a meta em flex-wrap, três colunas de valor (ou a nota 'sem previsto na planilha'), linhas de "
        "rótulo e valor, status com chip, mini gráfico do avanço (atraso em meses na cor dos pontos do item prazo ou, sem "
        "curva prevista, executado acumulado) e rodapé de uma linha preso ao pé.",
        "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(CSS_T3 + CSS_F4))

FIM = "& \"</div>\" & [Comum · JS contador tooltip]"

# ===================================================================================================== 3.1 Mês da curva
desenho(
    "T3 · Tooltip curva · HTML",
    "Tooltip de página do mês da Curva S (obra em foco; o mês sob o mouse): acumulado previsto e executado com o desvio "
    "e o status do físico na nota (dentro ou fora do limite), o mês (previsto e executado, com a posição na janela: 'o mês mais fraco em oito meses'), crédito × "
    "desembolsado até o mês e o que mudou desde o mês anterior. Estados: completo, primeiro mês do histórico ou primeira "
    "aba da obra (sem o 'desde' quando não há mês anterior), mês sem previsto na planilha (a coluna do previsto vira a "
    "nota, o desvio some e o 'desde' fala do executado).",
    linhas(
        "-- 1 · Leituras",
        "VAR _na = [T3 · Série · mês na série · foco no mês]",
        "VAR _obra = [Nota · obra em foco]",
        "VAR _aba = [T3 · Aba · foco no mês]",
        "VAR _mes = [Mês · data]",
        "VAR _mesL = [Mês · longo]",
        "VAR _mesN = [Mês · nome]",
        "VAR _mesAntN = [Mês anterior · nome]",
        "VAR _primeiroHist = [Mês · é o primeiro do histórico]",
        "VAR _primeiraAba = [T3 · Obra · primeira aba · foco]",
        "VAR _n = [T3 · Série · meses da obra · foco]",
        "VAR _ini = [T3 · Foco · início]",
        "VAR _fim = [T3 · Foco · término previsto]",
        "VAR _pa = [Físico · previsto acumulado · foco no mês]",
        "VAR _ea = [Físico · executado acumulado · foco no mês]",
        "VAR _d = [T3 · Desvio físico p.p. · foco no mês]",
        "VAR _s = [T3 · Status desvio físico · foco no mês]",
        "VAR _pm = [Físico · previsto no mês · foco no mês]",
        "VAR _em = [Físico · executado no mês · foco no mês]",
        "VAR _dest = [T3 · Mês · destaque no ritmo · foco no mês]",
        "VAR _cred = [Crédito do orçamento · foco no mês]",
        "VAR _des = [Desembolsado acumulado · foco no mês]",
        "VAR _dAnt = [T3 · Desvio físico p.p. · mês anterior · foco no mês]",
        "VAR _sAnt = [T3 · Status desvio físico · mês anterior · foco no mês]",
        "VAR _eaAnt = [T3 · Executado acumulado · mês anterior · foco no mês]",
        "VAR _seg = [T3 · Físico · meses seguidos na faixa · foco no mês]",
        "-- 2 · Textos",
        D.pct("_pa", "_tpa") + D.pct("_ea", "_tea") + D.pp("_d", "_td") + D.pct("_pm", "_tpm", casas=2)
        + D.pct("_em", "_tem", casas=2) + D.rs("_cred", "_tcr") + D.rs("_des", "_tds") + D.pp("_dAnt", "_tda")
        + D.pct("_eaAnt", "_tea2"),
        D.od_tabela(),
        D.od_pct("_pa", "_tpa") + D.od_pct("_ea", "_tea") + D.od_pp("_d", "_td") + D.od_pct("_pm", "_tpm")
        + D.od_pct("_em", "_tem") + D.od_rs("_cred", "_tcr") + D.od_rs("_des", "_tds"),
        "VAR _semP = ISBLANK ( _pa )",
        "VAR _txtSob = \"CURVA S · \" & " + D.esc("UPPER ( _obra )") + " & IF ( ISBLANK ( _aba ), \"\", \" · ABA \" & _aba )",
        "    & SWITCH ( TRUE (), _primeiroHist = 1, \" · PRIMEIRO MÊS DO HISTÓRICO\", _mes = _primeiraAba, "
        "\" · PRIMEIRA ABA DA OBRA\", \"\" )",
        "VAR _txtDir = IF ( ISBLANK ( _ini ), \"\", \"INÍCIO \" & UPPER ( " + mes_curto("_ini") + " ) )",
        "    & IF ( ISBLANK ( _fim ), \"\", \" · TÉRMINO \" & UPPER ( " + mes_curto("_fim") + " ) )",
        "VAR _txtDest =",
        "    SWITCH (",
        "        _dest,",
        "        \"exec_min\", \"o mês mais fraco \",",
        "        \"exec_max\", \"o melhor mês \",",
        "        \"prev_max\", \"o maior previsto \",",
        "        \"prev_min\", \"o menor previsto \"",
        "    ) & " + em_meses("_n"),
        "VAR _htmlDest = IF ( ISBLANK ( _dest ), \"\", \"<span class='d'>\" & _txtDest & \"</span>\" )",
        "VAR _txtDesde =",
        "    IF (",
        "        _semP,",
        f"        \"Era \" & " + C.marca("_tea2Txt") + " & \" executado em \" & _mesAntN & \"; sem previsto, não há desvio a comparar.\",",
        "        \"Era \" & " + C.marca("_tdaTxt") + " & \" em \" & _mesAntN",
        "            & IF (",
        "                _s = _sAnt,",
        "                \"; \" & " + ordinal("_seg") + " & \" mês seguido \" & " + faixa("_s") + " & \".\",",
        "                \"; \" & " + mudou("_sAnt", "_s") + " & \".\"",
        "            )",
        "    )",
        "VAR _temDesde = IF ( _semP, NOT ISBLANK ( _eaAnt ), NOT ISBLANK ( _dAnt ) )",
        "VAR _htmlCol =",
        "    IF (",
        "        _semP,",
        "        \"<div class='c3'>\" & " + col_sem('"PREVISTO ACUMULADO"') + " & " + col('"EXECUTADO ACUMULADO"', "_teaOd")
        + " & \"</div>\",",
        "        " + col3(('"PREVISTO ACUMULADO"', "_tpaOd"), ('"EXECUTADO ACUMULADO"', "_teaOd"),
                         ('"DESVIO · " & ' + faixa_vs("_s"), "\"<i class='mk mk\" & _s & \"'></i><span class='\" & IF ( ROUND ( _d, 1 ) < 0, \"ng\", \"\" ) & \"'>\" & _tdOd & \"</span>\"")),
        "    )",
        "VAR _htmlMes =",
        "    IF (",
        "        ISBLANK ( _pm ),",
        "        \"<div class='li'><span class='n'>Executado</span><span class='v'>\" & _temOd & \"</span>\" & _htmlDest & \"</div>\",",
        "        \"<div class='li'><span class='n'>Previsto</span><span class='v'>\" & _tpmOd & \"</span>\"",
        "            & \"<span class='n'>Executado</span><span class='v'>\" & _temOd & \"</span>\" & _htmlDest & \"</div>\"",
        "    )",
        "-- 4 · Marcação",
        "RETURN",
        "    IF (",
        "        _na = 1,",
        "        \"<div class='u tt'>\" & " + cab("_txtSob", "\"<b>\" & _mesL & \"</b>\"", "_txtDir"),
        "            & \"<div class='corpo'>\" & _htmlCol",
        "            & \"<div class='r3'></div><span class='vs'>NO MÊS</span>\" & _htmlMes",
        "            & \"<div class='r3'></div><span class='vs'>CRÉDITO × DESEMBOLSO ATÉ \" & UPPER ( _mesN ) & \"</span>\"",
        "            & " + li(("Crédito do executado", "_tcrOd"), ("Desembolsado", "_tdsOd")),
        "            & \"</div>\" & IF ( _temDesde, " + rod('"DESDE " & UPPER ( _mesAntN )', "_txtDesde") + " )",
        "        " + FIM,
        "    )",
    ))

# ===================================================================================================== 3.2 Mês do PPC
# F3 (docs/08 §5): o Ritmo do mês saiu da tela; o tooltip do mês do PPC mês a mês traz o PPC e os pontos do item, o
# atraso ao fim do mês e, numa linha, o ritmo do mês (previsto × executado), que continua também no tooltip da curva.
def cls_pts(pts: str, poss: str) -> str:
    return f'IF ( ISBLANK ( {pts} ), "", IF ( {pts} >= {poss}, "0", IF ( {pts} = 0, "2", "1" ) ) )'


def marca_pts(pts: str, poss: str) -> str:
    c = cls_pts(pts, poss)
    return f'IF ( {c} = "", "", "<i class=\'mk mk" & {c} & "\'></i>" )'


def atraso_txt(v: str, p: str) -> list[str]:
    """{p}Txt = "1,4 mês" · "3,6 meses" · "−0,5 mês" (à frente); {p}A (módulo) e {p}S (sinal) para o odômetro."""
    return [f"VAR {p}A = ROUND ( ABS ( {v} ), 1 )",
            f'VAR {p}N = FORMAT ( {p}A, "0.0", "pt-BR" )',
            f'VAR {p}S = IF ( ROUND ( {v}, 1 ) < 0, "{D.MENOS}", "" )',
            f'VAR {p}Un = IF ( {p}A <= 1, " mês", " meses" )',
            f'VAR {p}Txt = IF ( ISBLANK ( {v} ), "—", {p}S & {p}N & {p}Un )']


desenho(
    "T3 · Tooltip PPC · HTML",
    "Tooltip de página do mês do PPC mês a mês (obra em foco): o PPC do mês com a marca dos pontos, os pontos do item "
    "PPC na nota e o atraso em meses ao fim do mês; o ritmo do mês (previsto × executado, em % do orçamento) e o "
    "acumulado numa linha; no pé, o PPC do mês anterior. Sem PPC na base: 'falta na base' no lugar do número.",
    linhas(
        "-- 1 · Leituras",
        "VAR _noRecorte = [Série · mês até a referência]",
        "VAR _obra = [Nota · obra em foco]",
        "VAR _aba = [T3 · Aba · foco no mês]",
        "VAR _mesL = [Mês · longo]",
        "VAR _mesN = [Mês · nome]",
        "VAR _mesAntN = [Mês anterior · nome]",
        "VAR _ppc = [Canteiro · PPC · foco no mês]",
        "VAR _pt = [Nota · pontos PPC · foco no mês]",
        "VAR _ps = [Nota · possíveis · PPC · foco no mês]",
        "VAR _meta = [Nota · limite PPC · ponto cheio]",
        "VAR _atr = [Prazo · atraso (meses) · foco no mês]",
        "VAR _ptA = [Nota · pontos prazo · foco no mês]",
        "VAR _psA = [Nota · possíveis · prazo · foco no mês]",
        "VAR _pm = [Físico · previsto no mês · foco no mês]",
        "VAR _em = [Físico · executado no mês · foco no mês]",
        "VAR _pa = [Físico · previsto acumulado · foco no mês]",
        "VAR _ea = [Físico · executado acumulado · foco no mês]",
        "VAR _ppcAnt = [T3 · PPC · mês anterior · foco no mês]",
        "-- 2 · Textos",
        D.pct("_ppc", "_tc", casas=0) + D.pct("_meta", "_tm", casas=0) + D.pct("_pm", "_tpm", casas=2)
        + D.pct("_em", "_tem", casas=2) + D.pct("_pa", "_tpa") + D.pct("_ea", "_tea") + D.pct("_ppcAnt", "_tca", casas=0),
        atraso_txt("_atr", "_ta"),
        DC.item_txt("_tk", "_pt", "_ps"),
        D.od_tabela(),
        D.od_pct("_ppc", "_tc") + D.od_pct("_pm", "_tpm") + D.od_pct("_em", "_tem")
        + D._od("_ta", "_taN", "_taS & ", " & _taUn", "ISBLANK ( _atr )"),
        "VAR _txtSob = \"PPC MÊS A MÊS · \" & " + D.esc("UPPER ( _obra )") + " & IF ( ISBLANK ( _aba ), \"\", \" · ABA \" & _aba )",
        "VAR _txtDir = \"META \" & _tmTxt",
        "VAR _htmlPpc = IF ( ISBLANK ( _ppc ), \"<b class='sp'>" + DC.FALTA_NA_BASE + "</b>\", \"<b>\" & "
        + marca_pts("_pt", "_ps") + " & _tcOd & \"</b>\" )",
        "VAR _htmlAtr = IF ( ISBLANK ( _atr ), \"<b class='sp'>sem curva prevista</b>\", \"<b>\" & "
        + marca_pts("_ptA", "_psA") + " & \"<span class='\" & IF ( _ptA = 0, \"ng\", \"\" ) & \"'>\" & _taOd & \"</span></b>\" )",
        "VAR _htmlCol =",
        "    \"<div class='c3'><div><span class='vs'>PPC DO MÊS</span>\" & _htmlPpc & \"</div>\"",
        "        & \"<div><span class='vs'>NA NOTA · ITEM PPC</span><b>\" & " + C.marca("_tkTxt") + " & \"</b></div>\"",
        "        & \"<div><span class='vs'>ATRASO AO FIM DO MÊS</span>\" & _htmlAtr & \"</div></div>\"",
        "VAR _htmlRitmo =",
        "    \"<div class='li'>\"",
        "        & IF ( ISBLANK ( _pm ), \"\", \"<span class='n'>Previsto</span><span class='v'>\" & _tpmOd & \"</span>\" )",
        "        & \"<span class='n'>Executado</span><span class='v'>\" & _temOd & \"</span>\"",
        f"        & IF ( ISBLANK ( _pm ), \"<span class='d'>{SEM_P}</span>\", \"\" )",
        "    & \"</div>\"",
        "VAR _txtAcum =",
        "    IF (",
        "        ISBLANK ( _pa ),",
        f"        \"Acumulado ao fim de \" & _mesN & \": \" & " + C.marca("_teaTxt") + " & \" executado; {SEM_P}.\",",
        "        \"Acumulado ao fim de \" & _mesN & \": \" & " + C.marca("_tpaTxt") + " & \" previsto × \" & " + C.marca("_teaTxt") + " & \" executado.\"",
        "    )",
        "VAR _verbo = IF ( ROUND ( _ppc, 2 ) > ROUND ( _ppcAnt, 2 ), \"subiu\", IF ( ROUND ( _ppc, 2 ) < ROUND ( _ppcAnt, 2 ), \"caiu\", \"repetiu\" ) )",
        "VAR _txtDesde = \"Era \" & " + C.marca("_tcaTxt") + " & \" em \" & _mesAntN & \": o PPC \" & _verbo & IF ( _ppc >= _meta, \" e está na meta.\", "
        "\" e está abaixo da meta.\" )",
        "VAR _temAnt = NOT ISBLANK ( _ppcAnt ) && NOT ISBLANK ( _ppc )",
        "VAR _rotDesde = \"DESDE \" & UPPER ( _mesAntN )",
        "-- 4 · Marcação",
        "RETURN",
        "    IF (",
        "        _noRecorte = 1,",
        "        \"<div class='u tt'>\" & " + cab("_txtSob", "\"<b>\" & _mesL & \"</b>\"", "_txtDir"),
        "            & \"<div class='corpo'>\" & _htmlCol",
        "            & \"<div class='r3'></div><span class='vs'>RITMO DO MÊS · % DO ORÇAMENTO</span>\" & _htmlRitmo",
        "            & \"<p class='l1'>\" & _txtAcum & \"</p>\"",
        "            & \"</div>\" & IF ( _temAnt, " + rod("_rotDesde", "_txtDesde") + " )",
        "        " + FIM,
        "    )",
    ))

# ===================================================================================================== 3.3 Obra na linha do tempo
desenho(
    "T3 · Tooltip linha · HTML",
    "Tooltip de página da obra da Linha do tempo: ficha de prazo (início, término e orçamento com o tipo), o prazo no "
    "mês de referência (F3: atraso em meses, término projetado e onde ele cai diante da entrega contratual e dos 180 "
    "dias de tolerância), físico × "
    "financeiro até o mês de referência (com o status do físico na nota) e o status da obra na nota desde quando, com a "
    "nota (ou 'pendente · X de Y') e, no pé, os itens em que a obra mais perde pontos; obra sem previsto na planilha só "
    "com o executado e a nota; obra a iniciar só com o cadastro da cronograma.",
    linhas(
        "-- 1 · Leituras",
        "VAR _sit = [T3 · Obra · situação]",
        "VAR _obra = [Obra · nome]",
        "VAR _cod = [Obra · código]",
        "VAR _selo = [Obra · selo]",
        "VAR _spe = [T3 · Obra · SPE]",
        "VAR _m2 = [T3 · Obra · m² NBR]",
        "VAR _ini = [Obra · início]",
        "VAR _fim = [Obra · término previsto]",
        "VAR _aba = [Aba · ref]",
        "VAR _mesCM = [Mês de referência · curto maiúsculo]",
        "VAR _orc = [Orçamento · ref]",
        "VAR _tipo = [Tipo de orçamento · ref]",
        "VAR _orcG = [T3 · Obra · orçamento cronograma]",
        "VAR _tipoG = [T3 · Obra · tipo de orçamento cronograma]",
        "VAR _e = [Físico · executado acumulado · ref]",
        "VAR _p = [Físico · previsto acumulado · ref]",
        "VAR _d = [Físico · desvio acumulado p.p. · ref]",
        "VAR _sF = [T3 · Status desvio físico · ref]",
        "VAR _cred = [Crédito do orçamento · ref]",
        "VAR _des = [Desembolsado acumulado · ref]",
        "VAR _st = [Nota · status · ranking · ref]",
        "VAR _pend = [Nota · pendente · ranking · ref]",
        "VAR _nota = [Nota · nota final · ranking · ref]",
        "VAR _obt = [Nota · pontos obtidos · ranking · ref]",
        "VAR _poss = [Nota · pontos possíveis · ranking · ref]",
        "VAR _stIni = [T3 · Status · início da sequência]",
        "VAR _itens = [T3 · Tooltip linha · itens que perdem pontos (lista)]",
        "VAR _ref = [Mês de referência]",
        "VAR _jan = [Série · primeiro mês]",
        "VAR _atr = [Prazo · atraso (meses) · ref]",
        "VAR _ptA = [Nota · pontos prazo · ref]",
        "VAR _psA = [Nota · possíveis · prazo · ref]",
        "VAR _proj = [Prazo · término projetado · ref]",
        "VAR _ent = [Prazo · entrega contratual]",
        "VAR _tol = [Prazo · entrega com tolerância]",
        "VAR _sitT = [T3 · Término · situação · ref]",
        "-- 2 · Textos",
        "VAR _andamento = NOT ISBLANK ( _e )",
        "VAR _orcUso = IF ( _andamento, _orc, _orcG )",
        D.rs("_orcUso", "_to") + D.pct("_e", "_te") + D.pct("_p", "_tp") + D.pp("_d", "_tdv") + D.rs("_cred", "_tcr")
        + D.rs("_des", "_tds"),
        DC.nota_txt("_nt", "_nota", "_obt", "_poss", "_pend"),
        atraso_txt("_atr", "_ta"),
        D.od_tabela(),
        D.od_rs("_orcUso", "_to") + D.od_pct("_e", "_te") + D.od_pct("_p", "_tp") + D.od_pp("_d", "_tdv")
        + D.od_rs("_cred", "_tcr") + D.od_rs("_des", "_tds") + D._od("_ta", "_taN", "_taS & ", " & _taUn", "ISBLANK ( _atr )"),
        "VAR _txtOnde = SWITCH ( _sitT, 0, \"até a entrega\", 1, \"nos 180 dias\", 2, \"depois dos 180 dias\", \"\" )",
        "VAR _htmlPrazo =",
        "    IF (",
        "        ISBLANK ( _atr ),",
        "        \"<div class='li'><span class='n'>Atraso</span><span class='d'>sem curva prevista</span></div>\",",
        "        \"<div class='li'><span class='n'>Atraso</span><span class='v'>\" & " + marca_pts("_ptA", "_psA")
        + " & _taOd & \"</span><span class='n'>Término projetado</span><span class='v'><i class='mk mk\" & _sitT & \"'></i>\"",
        "            & " + mes_curto("_proj") + " & \"</span><span class='d'>\" & _txtOnde & \": entrega \" & " + mes_curto("_ent")
        + " & \", com 180 dias \" & " + mes_curto("_tol") + " & \"</span></div>\"",
        "    )",
        "VAR _tipoUso = UPPER ( IF ( _andamento, _tipo, _tipoG ) )",
        "VAR _txtSob =",
        "    IF (",
        "        _andamento,",
        "        \"LINHA DO TEMPO · OBRA EM ANDAMENTO\" & IF ( ISBLANK ( _aba ), \"\", \" · ABA \" & _aba ),",
        "        IF ( _sit = \"A iniciar\", \"LINHA DO TEMPO · OBRA A INICIAR · cronograma \" & UPPER ( [T3 · cronograma · versão] ), "
        "\"LINHA DO TEMPO · OBRA SEM ABA EM \" & _mesCM )",
        "    )",
        "VAR _posC = SEARCH ( \" CONSTRU\", _spe, 1, 0 )",
        "VAR _txtSpe = IF ( ISBLANK ( _spe ) || _spe = \"—\", \"\", IF ( _posC > 0, LEFT ( _spe, _posC - 1 ), _spe ) & \" SPE · \" )",
        "VAR _txtDir = IF ( _andamento, _txtSpe, \"\" ) & IF ( ISBLANK ( _m2 ), \"\", " + C.marca('FORMAT ( _m2, "#,0", "pt-BR" )') + " & \" M² NBR\" )",
        "VAR _seloUso = IF ( _selo = \"\" || ISBLANK ( _selo ), IF ( _sit = \"A iniciar\", \"cronograma\", \"\" ), _selo )",
        "VAR _txtCod = IF ( ISBLANK ( _cod ) || _cod = \"—\", \"\", _cod )",
        "VAR _txtIni = IF ( ISBLANK ( _ini ), \"—\", " + mes_curto("_ini") + " )",
        "VAR _txtFim = IF ( ISBLANK ( _fim ), \"—\", " + mes_curto("_fim") + " )",
        "VAR _txtStatus =",
        "    SWITCH ( TRUE (), _pend = 1, \"pendente\", _st = 2, \"crítica\", _st = 1, \"em atenção\", \"estável\" )",
        "        & IF ( _stIni = _ref, \" em \" & " + mes_nome("_stIni") + ", \" desde \" & " + desde("_stIni") + " )",
        "VAR _nIt = IF ( _itens = \"\" || ISBLANK ( _itens ), 0, PATHLENGTH ( _itens ) )",
        "VAR _txtLinha =",
        "    SWITCH (",
        "        _nIt,",
        "        0, \"\",",
        "        1, \"Só perde pontos em \" & PATHITEM ( _itens, 1 ) & \".\",",
        "        \"Onde mais perde pontos: \" & PATHITEM ( _itens, 1 ) & \" e \" & PATHITEM ( _itens, 2 ) & \".\"",
        "    )",
        "VAR _htmlStatus =",
        "    \"<div class='st'>\" & " + DC.chip_status("_st", "_pend") + " & \"<span class='v'>\"",
        "        & IF ( _pend = 1, " + C.marca("_ntOb") + " & \" de \" & _ntPo, " + C.marca("_ntN") + " ) & \"</span><span class='pt'>\"",
        "        & IF ( _pend = 1, \"pontos até agora\", \"Nota da obra\" ) & \"</span><span class='d'>\" & _txtStatus & \"</span></div>\"",
        "VAR _htmlFisico =",
        "    IF (",
        "        ISBLANK ( _p ),",
        f"        \"<div class='li'><span class='n'>Executado</span><span class='v'>\" & _teOd & \"</span><span class='d'>{SEM_P}\"",
        "            & \"</span></div>\",",
        "        \"<div class='li'><span class='n'>Executado</span><span class='v'>\" & _teOd & \"</span>\"",
        "            & \"<span class='n'>Previsto</span><span class='v'>\" & _tpOd & \"</span>\"",
        "            & \"<span class='v'><i class='mk mk\" & _sF & \"'></i><span class='\" & IF ( ROUND ( _d, 1 ) < 0, \"ng\", \"\" ) "
        "& \"'>\" & _tdvOd & \"</span></span><span class='d'>\" & "
        + faixa("_sF") + " & \"</span></div>\"",
        "    )",
        "VAR _htmlCorpo =",
        "    IF (",
        "        _andamento,",
        "        \"<div class='r3'></div><span class='vs'>PRAZO EM \" & _mesCM & \"</span>\" & _htmlPrazo",
        "            & \"<div class='r3'></div><span class='vs'>FÍSICO × FINANCEIRO ATÉ \" & _mesCM & \"</span>\" & _htmlFisico",
        "            & " + li(("Crédito do executado", "_tcrOd"), ("Desembolsado", "_tdsOd")),
        "            & \"<div class='r3'></div><span class='vs'>STATUS DA OBRA EM \" & _mesCM & \"</span>\" & _htmlStatus,",
        "        \"\"",
        "    )",
        "VAR _htmlRod =",
        "    IF (",
        "        _andamento,",
        "        IF ( _txtLinha = \"\", \"\", \"<div class='rod sr'><p class='l1'>\" & _txtLinha & \"</p></div>\" ),",
        "        " + rod('"AINDA SEM PLANILHA ANÁLISE CRÍTICA"', '"Previsto, executado e status chegam com a primeira aba da obra."'),
        "    )",
        "-- 4 · Marcação",
        "RETURN",
        "    IF (",
        "        /* sem obra única no contexto (cálculo fora do visual, filtro com várias): vazio, sem chegar nos textos */",
        "        HASONEVALUE ( dObra[Obra] ) && _sit IN { \"Em andamento\", \"A iniciar\" },",
        "        \"<div class='u tt'>\" & " + cab("_txtSob", "\"<b>\" & " + D.esc("_obra") + " & \"</b><em>\" & _txtCod & \"</em>\" & "
                                              + selo("_seloUso"), "_txtDir"),
        "            & \"<div class='corpo'>\" & " + col3(
            ('IF ( _andamento, "INÍCIO", "INÍCIO PREVISTO" )', "_txtIni"), ('"TÉRMINO PREVISTO"', "_txtFim"),
            ('"ORÇAMENTO" & IF ( _tipoUso = "", "", " · " & _tipoUso )', "_toOd")),
        "            & _htmlCorpo & \"</div>\" & _htmlRod",
        "        " + FIM,
        "    )",
    ))

# ===================================================================================================== 3.4 Obra no avanço
# mini gráfico: n colunas de 444 ÷ n px (n = meses da janela) a partir de x 1 do corpo, barra de mín(40, coluna − 10);
# 10 px por p.p. (desvio). Toda negativa: meses no alto e barras pendem da linha-base (26); mista: base a 63 e meses a
# 98; toda positiva (ou, sem previsto, o executado acumulado com o máximo em 40 px): base a 61 e meses logo embaixo (67).
desenho(
    "T3 · Tooltip avanço · HTML",
    "Tooltip de página da obra do Avanço das obras: o mês de referência (previsto e executado, com a posição na janela "
    "'em n meses' ou 'acima/abaixo do previsto'), a série do atraso em meses mês a mês na janela (F3; barras a partir de "
    "uma linha-base invisível, cor dos pontos do item prazo da nota no mês, x pela posição na janela, rótulo em todos os "
    "meses quando cabe, senão só referência, máximo e mínimo; as barras correm do primeiro ao último mês) e o que mudou "
    "desde o mês anterior (com a tendência do atraso ou o lado do cronograma; o status do físico é o da nota, no ponto "
    "cheio ou não). Obra sem curva prevista: o executado acumulado mês a mês no lugar do atraso e a nota 'sem curva "
    "prevista' no rodapé.",
    linhas(
        "-- 1 · Leituras",
        "VAR _obra = [Obra · nome]",
        "VAR _cod = [Obra · código]",
        "VAR _selo = [Obra · selo]",
        "VAR _ini = [Obra · início]",
        "VAR _fim = [Obra · término previsto]",
        "VAR _aba = [Aba · ref]",
        "VAR _ref = [Mês de referência]",
        "VAR _jan = [Série · primeiro mês]",
        "VAR _nJan = [Série · meses até a referência]",
        "VAR _mesCM = [Mês de referência · curto maiúsculo]",
        "VAR _mesAntN = [Mês anterior à referência · nome]",
        "VAR _pm = [Físico · previsto no mês · ref]",
        "VAR _em = [Físico · executado no mês · ref]",
        "VAR _e = [Físico · executado acumulado · ref]",
        "VAR _s = [T3 · Status desvio físico · ref]",
        "VAR _sAnt = [T3 · Status desvio físico · mês anterior · ref]",
        "VAR _dest = [T3 · Mês · destaque no ritmo · ref]",
        "VAR _abx = [T3 · Ritmo · abaixo do previsto em toda a série]",
        "VAR _n = [T3 · Série · meses da obra]",
        "VAR _pm1 = [T3 · Série · primeiro mês da obra]",
        "VAR _seg = [T3 · Físico · meses seguidos na faixa · ref]",
        "VAR _td = [T3 · Físico · tendência da distância]",
        "VAR _tdd = [T3 · Físico · tendência da distância desde]",
        "VAR _sg = [T3 · Físico · sinal · início da sequência]",
        "VAR _ld = [T3 · Físico · lado do cronograma · ref]",
        "VAR _a = [Prazo · atraso (meses) · ref]",
        "VAR _mMaxD = [T3 · Série · mês do maior atraso]",
        "VAR _mMinD = [T3 · Série · mês do menor atraso]",
        "VAR _mMaxE = [T3 · Série · mês do maior executado acumulado]",
        "VAR _mMinE = [T3 · Série · mês do menor executado acumulado]",
        "VAR _meses =",
        "    ADDCOLUMNS (",
        "        VALUES ( dMes[Mes] ),",
        "        \"@ate\", [Série · mês até a referência],",
        "        \"@pj\", [Série · posição na janela],",
        "        \"@d\", [Prazo · atraso (meses)],",
        "        \"@e\", [Físico · executado acumulado],",
        "        \"@pt\", [Nota · pontos prazo],",
        "        \"@ps\", [Nota · possíveis · prazo],",
        "        \"@ab\", [Mês · abreviado]",
        "    )",
        "-- 2 · Textos",
        D.pct("_pm", "_tpm", casas=2) + D.pct("_em", "_tem", casas=2),
        D.od_tabela(),
        D.od_pct("_pm", "_tpm") + D.od_pct("_em", "_tem"),
        "VAR _semP = ISBLANK ( _a )",
        "VAR _txtSob = \"AVANÇO FÍSICO · \" & _mesCM & IF ( ISBLANK ( _aba ), \"\", \" · ABA \" & _aba )",
        "VAR _txtDir = IF ( ISBLANK ( _ini ), \"\", \"INÍCIO \" & UPPER ( " + mes_curto("_ini") + " ) )",
        "    & IF ( ISBLANK ( _fim ), \"\", \" · TÉRMINO \" & UPPER ( " + mes_curto("_fim") + " ) )",
        "VAR _txtDet =",
        "    SWITCH (",
        "        TRUE (),",
        f"        ISBLANK ( _pm ), IF ( _semP, \"{SEM_P}\", \"sem previsto do mês na planilha\" ),",
        "        _dest = \"exec_min\", \"o mês mais fraco \" & " + em_meses("_n") + ",",
        "        _dest = \"exec_max\", \"o melhor mês \" & " + em_meses("_n") + ",",
        "        _dest = \"prev_max\", \"o maior previsto \" & " + em_meses("_n") + ",",
        "        _dest = \"prev_min\", \"o menor previsto \" & " + em_meses("_n") + ",",
        "        _em > _pm, \"acima do previsto\",",
        "        _abx = 1, \"abaixo do previsto desde \" & " + mes_curto("_pm1") + ",",
        "        \"\"",
        "    )",
        "VAR _txtTend =",
        "    SWITCH (",
        "        _ld,",
        "        -1, \"; o atraso \" & SWITCH ( _td, \"cresce\", \"cresce\", \"cai\", \"vem caindo\", \"oscila\" ) & \" desde \"",
        "            & " + desde("_tdd") + ",",
        "        0, IF ( _sg = _pm1 && _n > 1, \"; no previsto nos \" & " + extenso("_n") + " & \" meses\", \"; no previsto desde \" & "
        + desde("_sg") + " ),",
        "        1, IF ( _sg = _pm1 && _n > 1, \"; à frente nos \" & " + extenso("_n") + " & \" meses\", \"; à frente desde \" & "
        + desde("_sg") + " ),",
        "        \"\"",
        "    )",
        "VAR _txtMudou =",
        "    SWITCH (",
        "        TRUE (),",
        "        _s <> _sAnt, UPPER ( LEFT ( " + mudou("_sAnt", "_s") + ", 1 ) ) & MID ( " + mudou("_sAnt", "_s")
        + ", 2, 99 ) & _txtTend & \".\",",
        "        _seg >= _n, \"Nada mudou: \" & " + faixa("_s") + " & \" nos \" & " + extenso("_n") + " & \" meses\" & _txtTend & \".\",",
        "        \"Nada mudou: \" & " + faixa("_s") + " & \" desde \" & " + desde("EDATE ( _ref, 1 - _seg )")
        + " & _txtTend & \".\"",
        "    )",
        "VAR _rotMudou = \"O QUE MUDOU DESDE \" & UPPER ( _mesAntN )",
        "VAR _rotGrafico = IF ( _semP, \"EXECUTADO ACUMULADO, MÊS A MÊS · %\", \"ATRASO, MÊS A MÊS · MESES\" )",
        "VAR _htmlRodape =",
        "    IF (",
        "        _semP,",
        "        " + rod('"SEM CURVA PREVISTA"', '"Sem a curva prevista da cronograma, o atraso em meses não sai."') + ",",
        "        IF ( NOT ISBLANK ( _sAnt ), " + rod("_rotMudou", "_txtMudou") + " )",
        "    )",
        "VAR _cruza = YEAR ( _jan ) <> YEAR ( _ref )",
        "-- 3 · Geometria",
        "VAR _serie = FILTER ( _meses, [@ate] = 1 ) /* lista */",
        "VAR _com = FILTER ( _serie, NOT ISBLANK ( IF ( _semP, [@e], [@d] ) ) ) /* lista */",
        "VAR _temPos = _semP || COUNTROWS ( FILTER ( _com, [@d] > 0 ) ) > 0 /* geometria */",
        "VAR _temNeg = NOT _semP && COUNTROWS ( FILTER ( _com, [@d] < 0 ) ) > 0 /* geometria */",
        "VAR _modo = IF ( _temPos && _temNeg, \"misto\", IF ( _temPos, \"positivo\", \"negativo\" ) ) -- geometria",
        "VAR _base = SWITCH ( _modo, \"misto\", 57, \"positivo\", 57, 22 ) -- geometria",
        "VAR _yMes = SWITCH ( _modo, \"misto\", 96, \"positivo\", 63, 0 ) -- geometria",
        "VAR _alt = SWITCH ( _modo, \"misto\", 112, \"positivo\", 79, 83 ) -- geometria",
        "VAR _tetoNeg = IF ( _modo = \"misto\", 16, 40 ) -- geometria",
        "VAR _maxE = MAXX ( _com, [@e] ) /* geometria */",
        "VAR _slot = INT ( DIVIDE ( 560, _nJan ) ) /* geometria */",
        "VAR _bw = MIN ( 40, _slot - 14 ) -- geometria",
        "VAR _cabe = _slot >= 40 -- geometria",
        "VAR _mMax = IF ( _semP, _mMaxE, _mMaxD ) -- geometria",
        "VAR _mMin = IF ( _semP, _mMinE, _mMinD ) -- geometria",
        "VAR _dMaxRef = ABS ( DATEDIFF ( MIN ( _mMax, _ref ), MAX ( _mMax, _ref ), MONTH ) ) -- geometria",
        "VAR _dMinRef = ABS ( DATEDIFF ( MIN ( _mMin, _ref ), MAX ( _mMin, _ref ), MONTH ) ) -- geometria",
        "VAR _dMinMax = ABS ( DATEDIFF ( MIN ( _mMin, _mMax ), MAX ( _mMin, _mMax ), MONTH ) ) -- geometria",
        "VAR _htmlSerie =",
        "    CONCATENATEX (",
        "        _serie,",
        "        VAR _v = IF ( _semP, [@e], [@d] )",
        "        VAR _tem = NOT ISBLANK ( _v )",
        "        VAR _x = ( [@pj] - 1 ) * _slot + 1 /* geometria */",
        "        -- zero sobe nos modos misto e positivo e pende no negativo (o rótulo não cai sobre os meses do alto)",
        "        VAR _sobe = _v > 0 || ( _v = 0 && _modo <> \"negativo\" ) -- geometria",
        "        VAR _hD = MAX ( 1, ROUND ( MIN ( ABS ( _v ) * 11, IF ( _sobe, 40, _tetoNeg ) ), 0 ) ) /* geometria */",
        "        VAR _hE = MAX ( 1, ROUND ( DIVIDE ( _v, _maxE ) * 40, 0 ) ) /* geometria */",
        "        VAR _zero = _tem && NOT _semP && ROUND ( _v, 1 ) = 0 -- geometria",
        "        VAR _h = IF ( _tem, IF ( _zero, 2, IF ( _semP, _hE, _hD ) ), 0 ) -- geometria",
        "        VAR _ehRef = dMes[Mes] = _ref",
        "        VAR _cls = " + cls_pts("[@pt]", "[@ps]"),
        "        VAR _mostra =",
        "            _tem",
        "                && ( _cabe || _ehRef || ( dMes[Mes] = _mMax && _dMaxRef > 1 )",
        "                    || ( dMes[Mes] = _mMin && _dMinRef > 1 && NOT ( _dMaxRef > 1 && _dMinMax <= 1 ) ) ) -- geometria",
        "        VAR _atraso = ( [@pj] - 1 ) * 120 /* geometria */",
        "        VAR _txtV =",
        "            IF (",
        "                _semP,",
        "                FORMAT ( _v * 100, \"0.0\", \"pt-BR\" ),",
        "                IF ( ROUND ( _v, 1 ) < 0, \"−\", \"\" ) & FORMAT ( ABS ( _v ), \"0.0\", \"pt-BR\" )",
        "            )",
        "        VAR _yRot = IF ( _sobe, _base - _h - 19, _base + 1 + _h + 2 ) /* geometria */",
        "        VAR _mesTxt = IF ( _cruza && MONTH ( dMes[Mes] ) = 1, " + mes_curto("dMes[Mes]") + ", [@ab] )",
        "        VAR _barra =",
        "            IF (",
        "                _tem,",
        "                \"<i class='b \" & IF ( _zero, \"z\", IF ( _semP, \"se\", \"s\" & _cls ) ) & \"' style='left:\" & ( _x + INT ( ( _slot - _bw ) / 2 ) )",
        "                    & \"px;width:\" & _bw & \"px;\"",
        "                    & IF ( _sobe, \"top:auto;bottom:\" & ( _alt - _base ), \"top:\" & ( _base + 1 ) ) & \"px;height:\" & _h",
        "                    & \"px' data-rk='m\" & [@pj] & \"' data-rp='height' data-rd='\" & _atraso & \"'></i>\"",
        "            )",
        "        VAR _rot =",
        "            IF (",
        "                _mostra,",
        "                \"<span class='vl \" & IF ( _ehRef, \"ref fim\", \"ini\" ) & IF ( NOT _semP && _cls = \"2\", \" ng\", \"\" ) & \"' style='left:\" & ( _x - 6 ) & \"px;width:\"",
        "                    & ( _slot + 12 ) & \"px;top:\" & _yRot & \"px\"",
        "                    & IF ( _ehRef, \";animation-delay:\" & ( _atraso + 700 ) & \"ms\", \"\" ) & \"'>\" & " + C.marca("_txtV") + " & \"</span>\"",
        "            )",
        "        RETURN",
        "            _barra & _rot",
        "                & \"<span class='ms\" & IF ( _ehRef, \" ref\", IF ( _tem, \"\", \" sem\" ) ) & \"' style='left:\" & ( _x - 6 )",
        "                & \"px;width:\" & ( _slot + 12 ) & \"px;top:\" & _yMes & \"px'>\" & _mesTxt & \"</span>\",",
        "        \"\",",
        "        dMes[Mes], ASC",
        "    )",
        "-- 4 · Marcação",
        "VAR _htmlMes =",
        "    \"<div class='li'>\"",
        "        & IF ( ISBLANK ( _pm ), \"\", \"<span class='n'>Previsto</span><span class='v'>\" & _tpmOd & \"</span>\" )",
        "        & \"<span class='n'>Executado</span><span class='v'>\" & _temOd & \"</span>\"",
        "        & IF ( _txtDet = \"\", \"\", \"<span class='d'>\" & _txtDet & \"</span>\" )",
        "    & \"</div>\"",
        "RETURN",
        "    IF (",
        "        NOT ISBLANK ( _e ),",
        "        \"<div class='u tt'>\" & " + cab("_txtSob", "\"<b>\" & " + D.esc("_obra") + " & \"</b><em>\" & _cod & \"</em>\" & "
                                              + selo("_selo"), "_txtDir"),
        "            & \"<div class='corpo'><span class='vs'>NO MÊS · \" & _mesCM & \"</span>\" & _htmlMes",
        "            & \"<div class='r3'></div><span class='vs'>\" & _rotGrafico & \"</span>\"",
        "            & \"<div class='mc' style='height:\" & _alt & \"px'>\" & _htmlSerie & \"</div></div>\"",
        "            & _htmlRodape",
        "        & \"</div>\" & [Comum · JS contador tooltip] & [Comum · JS corrida]",
        "    )",
    ))

if __name__ == "__main__":
    sys.exit(gravar(MEDIDAS, RAIZ / "dax" / "T3", GERADO))

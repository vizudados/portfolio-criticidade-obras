#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""leituras_t4 — desenho das leituras do "?" e do guia da Tela 04 · Resultado no tempo (pbi/dax/T4/Leituras/**). As
contas estão em contas_t4.py (pasta T4 Resultado no tempo\\Leituras\\Contas) e em base/.

Figma: seção Interações · Tela 04 (304:3105) — Leitura · T4 · Resultado da carteira, mês a mês 310:4276 ("?" 289:7881),
Resultado por obra 310:7994 ("?" 289:7885), Desembolso da carteira 312:3713 ("?" 289:7889), Desembolso de jun/26 por
obra 312:3768 ("?" 289:7893), Guia · T4 313:3713 ("?" 279:1085). Gramática: docs/06-interacoes-spec.md §1.7–1.8 e
docs/06-interacoes-spec-t4.md §4–5 (L058: cada número aparece uma vez por leitura; L065: a leitura cobre o painel que
explica). Fase 5 (07/10/2026, Figma 391:4681): os dois painéis da esquerda têm 1068 e recebem a leitura completa em
duas colunas (600 | 371: achado, explicação, destaques e "como ler" à esquerda; detalhe e "o que explica" à direita,
abaixo do ×); os dois da direita têm 400 e recebem a condensada (sobretítulo em duas linhas, achado, explicação e
destaques). A grade das justificativas no período passou de Desembolso por obra para Desembolso da carteira.

F4 (pedido do Alisson, 28/10/2026: todo número conta e todo elemento de gráfico entra animado): os números das
frases e dos rótulos que ainda eram estáticos vão marcados com C.marca() e viram odômetro no fim da medida
(C.envolver_marcas); os rótulos e meses do detalhe entram com as classes genéricas do CSS base (.a-fd), em cascata
depois da coluna; a régua do detalhe aparece. A grade das justificativas ganhou 100 px de nome (PONTA NEGRA inteiro, sem
reticências).

    python -X utf8 pbi/scripts/leituras_t4.py
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
from leituras_lib import CSS_X, X_SVG  # noqa: E402

RAIZ = AQUI.parent
GERADO = "pbi/scripts/leituras_t4.py"
DES = r"T4 Resultado no tempo\Leituras"
MEDIDAS: list[Medida] = []
MENOS = D.MENOS
CAUSAS = ["efetivo", "aditivo", "medicao", "postergada", "compra", "sinal", "outra"]   # = contas_t4.CAUSAS + outra
CAUSA_PLURAL = {"efetivo": "efetivo", "aditivo": "aditivos", "medicao": "medições concentradas",
                "postergada": "medições postergadas", "compra": "compras antecipadas", "sinal": "pagamentos de sinal de contrato",
                "outra": "outras causas"}
CAUSA_OBRA = {"efetivo": "efetivo reforçado", "aditivo": "aditivo", "medicao": "medição concentrada",
              "postergada": "medição postergada", "compra": "compra antecipada", "sinal": "sinal de contrato",
              "outra": "outros motivos"}


X = X_SVG


def painel(classe: str, aria: str, corpo: str, script: str = "") -> str:
    """Superfície da leitura v2 (L065): o retângulo do painel, offwhite, contorno 1 px preto, cantos retos, sem sombra;
    o × (X_SVG) é irmão do painel, por cima dele."""
    fim = f' & {script}' if script else ""
    return (f'"<div class=\'u lv\' role=\'dialog\' aria-label=\'" & {aria} & "\'><div class=\'pn {classe}\'>" '
            f'& {corpo} & "</div>{X}</div>"{fim}')


def bloco(rotulo: str, conteudo: str) -> str:
    return f'"<div class=\'sec\'><span class=\'vs\'>{rotulo}</span>" & {conteudo} & "</div>"'


def destaque(num: str, rot: str) -> str:
    return f'"<div><b>" & {num} & "</b><span>" & {rot} & "</span></div>"'


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


def ext(v: str, fem: bool = True) -> str:
    nomes = (["nenhuma", "uma", "duas"] if fem else ["nenhum", "um", "dois"]) + \
        ["três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez", "onze", "doze"]
    casos = ", ".join(f'{i}, "{n}"' for i, n in enumerate(nomes))
    return f'SWITCH ( {v}, {casos}, FORMAT ( {v}, "0" ) )'


def cap(v: str) -> str:
    return f"UPPER ( LEFT ( {v}, 1 ) ) & MID ( {v}, 2, LEN ( {v} ) )"


def nm(v: str) -> str:
    return f'FORMAT ( {v}, "mmmm", "pt-BR" )'


def art(obra: str) -> str:
    return f"CALCULATE ( [T4 · Obra · artigo], dObra[Obra] = {obra} )"


def lista_e(v: str, p: str) -> list[str]:
    """{p}Txt = "A, B e C" a partir de "A|B|C"; {p}N = quantos (só decide o texto)."""
    return [
        f'VAR {p}N = IF ( ISBLANK ( {v} ) || {v} = "", 0, PATHLENGTH ( {v} ) )',
        f'VAR {p}Pos = IF ( {p}N >= 2, FIND ( "§", SUBSTITUTE ( {v}, "|", "§", {p}N - 1 ) ) )',
        f'VAR {p}Txt = SWITCH ( TRUE (), {p}N = 0, "", {p}N = 1, {v}, '
        f'SUBSTITUTE ( LEFT ( {v}, {p}Pos - 1 ), "|", ", " ) & " e " & MID ( {v}, {p}Pos + 1, 999 ) )',
    ]


def periodo(n: str, janela: str = "_nJan") -> str:
    """Nome do período da série: 3 meses "trimestre", 6 "semestre", os demais "período" — só quando o recorte tem aba em
    todos os meses da janela (n = meses com aba, janela = [Série · meses até a referência]); senão "período"."""
    return f'IF ( {n} = {janela}, SWITCH ( {janela}, 3, "trimestre", 6, "semestre", "período" ), "período" )'


QUARTOS = """    SWITCH (
        ROUND ( {e} * 4, 0 ),
        0, "com a obra ainda no começo",
        1, "com um quarto da obra executado",
        2, "com metade da obra executada",
        3, "com três quartos da obra executados",
        "com a obra quase toda executada"
    )"""

# ===================================================================================================== 4.1 mês a mês
# F3 (docs/08 §5): o gráfico tem uma série (resultado aplicado) e o traço do resultado da planilha; a leitura fala do
# aplicado no período (achado), de quem caiu e das negativas (explicação), da distância até a planilha (o que falta
# realizar) no detalhe e do que separa os dois resultados (o que explica).
desenho(
    "T4 · Leitura mês · HTML",
    "Leitura do \"?\" de Resultado da carteira, mês a mês, sobre o próprio painel (L065, 1068 × 380, completa em duas "
    "colunas; F3): o sentido do resultado aplicado no período e onde a planilha fecha (achado), quantas obras caíram no "
    "aplicado e as negativas, três destaques que contam, e, à direita, o que falta realizar mês a mês (a distância "
    "entre a barra e o traço) e o que separa o aplicado da planilha. Só lê contas.",
    linhas(
        "-- 1 · Leituras",
        "VAR _ref = [Mês de referência]",
        "VAR _mesL = [Mês de referência · longo]",
        "VAR _mesN = [Mês de referência · nome]",
        "VAR _mesAntN = [Mês anterior à referência · nome]",
        "VAR _ini = [T4 · Primeiro mês com aba]",
        "VAR _nAba = [T4 · Meses com aba]",
        "VAR _nComp = [T4 · Leitura mês · meses comparáveis]",
        "VAR _nQueda = [T4 · Leitura mês · meses com queda]",
        "VAR _nSemQueda = [T4 · Leitura mês · meses sem queda]",
        "VAR _seqIni = [T4 · Leitura mês · sequência · início]",
        "VAR _var = [T4 · Resultado aplicado · variação no mês · ref]",
        "VAR _ap = [Resultado aplicado · ref]",
        "VAR _res = [Resultado da obra · ref]",
        "VAR _ar = [A realizar · ref]",
        "VAR _pct = [Resultado aplicado % · ref]",
        "VAR _obrasCairam = [T4 · Obras que caíram no mês · ref]",
        "VAR _obrasComp = [T4 · Obras comparáveis no mês · ref]",
        "VAR _neg = [T4 · Leitura mês · obras negativas (lista)]",
        "VAR _negCairam = [T4 · Leitura mês · negativas que caíram]",
        "VAR _arSeq = [T4 · Leitura mês · a realizar · sequência · início]",
        "VAR _arVar = [T4 · A realizar · variação no mês · ref]",
        "VAR _pctIni = [T4 · Leitura mês · resultado % no primeiro mês]",
        "VAR _oMaior = [T4 · Leitura mês · obra de maior resultado]",
        "VAR _rMaior = CALCULATE ( [Resultado aplicado · ref], dObra[Obra] = _oMaior )",
        "VAR _negRef = [T4 · Obras com resultado negativo · ref] + 0",
        "VAR _negIni = [T4 · Obras com resultado negativo · no primeiro mês] + 0",
        "VAR _meses =",
        "    ADDCOLUMNS (",
        "        VALUES ( dMes[Mes] ),",
        "        \"@ate\", [Série · mês até a referência],",
        "        \"@pos\", [Série · posição na janela],",
        "        \"@rot\", [Mês · abreviado],",
        "        \"@a\", [A realizar]",
        "    )",
        "VAR _det = FILTER ( _meses, [@ate] = 1 ) /* lista */",
        "VAR _detCom = FILTER ( _det, NOT ISBLANK ( [@a] ) ) /* lista */",
        "VAR _detMax = MAXX ( _detCom, ABS ( [@a] ) ) /* geometria */",
        "VAR _detIni = MINX ( _detCom, dMes[Mes] ) /* geometria */",
        "-- 2 · Textos",
        D.od_tabela(),
        "VAR _iniN = " + nm("_ini"),
        "VAR _iniL = _iniN & IF ( YEAR ( _ini ) <> YEAR ( _ref ), \" de \" & YEAR ( _ini ), \"\" )",
        "VAR _txtSob = \"LEITURA · RESULTADO DA CARTEIRA, MÊS A MÊS · \" & UPPER ( IF ( _ini = _ref, _mesL, _iniL & \" a \" "
        "& _mesL ) )",
        D.rs("_ap", "_tap"), D.od_rs("_ap", "_tap"), D.rs("_res", "_tr"), D.rs("_ar", "_tar"),
        "VAR _txtTend =",
        "    SWITCH (",
        "        TRUE (),",
        "        _nComp = 0, \"Primeiro mês do histórico\",",
        "        _var < 0 && _nQueda = _nComp, \"O resultado aplicado cai todo mês desde \" & _iniN,",
        "        _var < 0 && _seqIni < _ref, \"O resultado aplicado cai desde \" & " + nm("_seqIni") + ",",
        "        _var < 0, \"O resultado aplicado caiu em \" & " + ext("_nQueda", fem=False) + " & \" dos \" & "
        + ext("_nComp", fem=False) + " & \" meses\",",
        "        _var > 0 && _nQueda = 0, \"O resultado aplicado sobe todo mês desde \" & _iniN,",
        "        _var > 0 && _seqIni < _ref, \"O resultado aplicado sobe desde \" & " + nm("_seqIni") + ",",
        "        _var > 0, \"O resultado aplicado subiu em \" & " + ext("_nSemQueda", fem=False) + " & \" dos \" & "
        + ext("_nComp", fem=False) + " & \" meses\",",
        "        \"O resultado aplicado fica estável em \" & _mesN",
        "    )",
        "VAR _txtAchado = _txtTend & \"; em \" & _mesN & \" fecha em <span class='\" "
        f"& IF ( _tapS = \"{MENOS}\", \"ng\", \"\" ) & \"'>\" & _tapOd & \"</span>, e a planilha, com o que ainda vai se \" "
        f"& \"realizar, em <span class='\" & IF ( _trS = \"{MENOS}\", \"ng\", \"\" ) & \"'>\" & " + C.marca("_trTxt") + " & \"</span>.\"",
        lista_e("_neg", "_ln"),
        "VAR _txtObras =",
        "    IF (",
        "        _obrasComp = 0,",
        "        \"\",",
        "        " + cap(ext("_obrasCairam")) + " & \" das \" & " + ext("_obrasComp") + " & IF ( _obrasCairam = 1, \" fechou \", "
        "\" fecharam \" ) & _mesN & \" abaixo de \" & _mesAntN & \" no aplicado\"",
        "    )",
        "VAR _txtNeg =",
        "    SWITCH (",
        "        TRUE (),",
        "        _obrasComp = 0, \"\",",
        "        _lnN = 0, \"; nenhuma obra fecha o mês com o aplicado no negativo\",",
        "        _negCairam = _lnN && _lnN = 1, \"; a negativa, \" & _lnTxt & \", pesa cada vez mais\",",
        "        _negCairam = _lnN, \"; as \" & " + ext("_lnN") + " & \" negativas, \" & _lnTxt & \", pesam cada vez mais\",",
        "        \"; \" & _lnTxt & IF ( _lnN = 1, \" segue negativa\", \" seguem negativas\" )",
        "    )",
        "VAR _txtExplica = _txtObras & _txtNeg & IF ( _txtObras = \"\", \"\", \".\" )",
        D.pct("_pctIni", "_tpi", casas=2, mais=True), D.od_pct("_pctIni", "_tpi"),
        D.pct("_pct", "_tp", casas=2, mais=True),
        D.rs("_rMaior", "_trm"), D.od_rs("_rMaior", "_trm"),
        D.inteiro("_negRef", "_tng"), D.od_num("_negRef", "_tng"),
        f"VAR _txtD1 = \"do orçamento no aplicado em \" & _iniN & IF ( _ini = _ref, \"\", \"; <span class='\" & IF ( _tpS = \"{MENOS}\", \"ng\", \"\" ) "
        "& \"'>\" & " + C.marca("_tpTxt") + " & \"</span> em \" & _mesN )",
        "VAR _txtD2 = _oMaior & \" em \" & _mesN & IF ( _rMaior > 0, \", o maior aplicado\", \", a menor perda\" )",
        "VAR _txtD3 = IF ( _negRef = 1, \"obra\", \"obras\" ) & \" com o aplicado negativo em \" & _mesN & IF ( _ini = _ref, \"\", \"; \" "
        "& IF ( _negIni = 0, \"nenhuma\", " + ext("_negIni") + " ) & \" em \" & _iniN )",
        "VAR _txtDist =",
        "    IF (",
        "        ISBLANK ( _arSeq ),",
        "        \"\",",
        "        \" A distância entre a barra e o traço \" & IF ( _arVar > 0, \"cresce\", \"encolhe\" )",
        "            & IF ( _arSeq = EDATE ( _ini, 1 ), \" todo mês\", \" desde \" & " + nm("_arSeq") + " ) & \".\"",
        "    )",
        "VAR _txtOqe =",
        "    \"A planilha soma ao resultado o que ainda vai se realizar: saldo de contrato, adiantamentos, estoque e \"",
        "        & \"equipamentos, pagos e ainda não aplicados. O resultado aplicado é só o que já virou obra: valor agregado \"",
        "        & \"− custo aplicado. Em \" & _mesN & \", faltam \" & " + C.marca("_tarTxt") + " & \" para chegar ao da planilha.\" & _txtDist",
        "-- 3 · Geometria",
        "VAR _hMax = 50 -- geometria",
        "-- 4 · Marcação",
        "VAR _htmlDet =",
        "    CONCATENATEX (",
        "        _det,",
        "        VAR _a = [@a]",
        "        VAR _tem = NOT ISBLANK ( _a )",
        "        VAR _h = IF ( _tem, MAX ( 2, ROUND ( DIVIDE ( ABS ( _a ), _detMax ) * _hMax, 0 ) ), 0 ) -- geometria",
        "        VAR _ehRef = dMes[Mes] = _ref",
        "        VAR _ehIni = dMes[Mes] = _detIni",
        "        VAR _aA = ABS ( _a )",
        f"        VAR _txtA = IF ( _a < 0, \"{MENOS}\", \"\" ) & \"R$ \" & IF ( _aA >= 999500, FORMAT ( _aA / 1000000, \"0.00\", \"pt-BR\" ) & \" mi\", "
        "FORMAT ( _aA / 1000, \"0\", \"pt-BR\" ) & \" mil\" )",
        "        VAR _atraso = 600 + ( [@pos] - 1 ) * 80 -- geometria",
        "        VAR _clsVal = IF ( _ehIni, \" ini\", \"\" ) & IF ( _ehRef, \" fim\", \"\" )",
        "        RETURN",
        "            \"<div class='c'>\"",
        "                & IF ( _tem && ( _ehRef || _ehIni ), \"<span class='val a-fd\" & _clsVal & \"' style='animation-delay:\" "
        "& ( _atraso + 400 ) & \"ms;top:\" & ( 84 - _h - 21 ) & \"px'>\" & " + C.marca("_txtA") + " & \"</span>\" )",
        "                & IF ( _tem, \"<i style='top:\" & ( 84 - _h ) & \"px;height:\" & _h & \"px' data-rk='a\" "
        "& [@pos] & \"' data-rp='top,height' data-r0-top='84px' data-r0-height='0px' data-rd='\" & _atraso "
        "& \"'></i>\" )",
        "                & \"<span class='ms a-fd\" & IF ( _ehRef, \" ref\", \"\" ) & \"' style='animation-delay:\" & _atraso "
        "& \"ms;top:88px'>\" & [@rot] & \"</span>\"",
        "            & \"</div>\",",
        "        \"\",",
        "        dMes[Mes], ASC",
        "    )",
        "VAR _htmlDst =",
        "    \"<div class='dst sobre-creme'>\"",
        "        & " + destaque(f"\"<span class='\" & IF ( _tpiS = \"{MENOS}\", \"ng\", \"\" ) & \"'>\" & _tpiOd & \"</span>\"", "_txtD1"),
        "        & " + destaque("_trmOd", "_txtD2"),
        "        & " + destaque("_tngOd", "_txtD3"),
        "    & \"</div>\"",
        "VAR _esq =",
        "    \"<div class='esq'><span class='vs sob'>\" & _txtSob & \"</span>\"",
        "        & \"<h2 class='ach'>\" & _txtAchado & \"</h2>\"",
        "        & IF ( _txtExplica = \"\", \"\", \"<p class='exp'>\" & " + D.esc("_txtExplica") + " & \"</p>\" )",
        "        & _htmlDst",
        "        & " + bloco("Como ler", D.texto("<p class='cl'>Passe o mouse num mês para ver o aplicado de cada obra.</p>")),
        "    & \"</div>\"",
        "VAR _dir =",
        "    \"<div class='dir'><span class='vs'>Detalhe</span>\"",
        "        & \"<p class='sub'>o que falta realizar, mês a mês · a distância entre a barra e o traço</p>\"",
        "        & \"<div class='mb'>\" & _htmlDet & \"</div>\"",
        "        & " + bloco("O que explica", "\"<p class='oqe'>\" & " + D.esc("_txtOqe") + " & \"</p>\""),
        "    & \"</div>\"",
        "VAR _corpo = \"<div class='cols'>\" & _esq & \"<i class='div'></i>\" & _dir & \"</div>\"",
        "RETURN",
        "    IF ( NOT ISBLANK ( _ap ), " + painel("pn-2c", '"Leitura de Resultado da carteira, mês a mês"', "_corpo",
                                              "[Comum · JS contador tooltip] & [Comum · JS corrida]") + " )",
    ))

# ===================================================================================================== 4.2 obras no mês
# F3 (docs/08 §5): as leituras de Resultado por obra e de Desembolso por obra viram uma, a da tabela Obras no mês
# (painel 1460,273 · 400 × 767): o custo (IDC abaixo de 1 e quem mais caiu no mês), o caixa (justificativas exigidas,
# preenchidas e em branco, com os nomes) e três destaques.
desenho(
    "T4 · Leitura obras · HTML",
    "Leitura do \"?\" de Obras no mês, sobre o próprio painel (L065, 400 × 767, condensada; F3): quantas obras estão com "
    "IDC abaixo de 1 e qual mais caiu no mês (achado), as justificativas de caixa exigidas, preenchidas e em branco, com "
    "os nomes (explicação), e três destaques: o IDC da carteira, a maior queda do IDC e as justificativas em branco. "
    "Só lê contas.",
    linhas(
        "-- 1 · Leituras",
        "VAR _mesL = [Mês de referência · longo]",
        "VAR _mesN = [Mês de referência · nome]",
        "VAR _mesAntN = [Mês anterior à referência · nome]",
        "VAR _nObras = [Obras com análise · ref] + 0",
        "VAR _abx = [T1 · Custo · obras com IDC abaixo de 1 · ref] + 0",
        "VAR _nQueda = [T4 · Leitura obras · obras com IDC em queda] + 0",
        "VAR _oQueda = [T4 · Leitura obras · obra de maior queda do IDC]",
        "VAR _vQueda = [T4 · Leitura obras · maior queda do IDC]",
        "VAR _idc = [IDC · ref]",
        "VAR _ex = [Carteira · justificativas exigidas · ref] + 0",
        "VAR _pre = [Carteira · justificativas preenchidas · ref] + 0",
        "VAR _br = [Carteira · justificativas em branco · ref] + 0",
        "VAR _lBr = [Recorte · justificativas em branco (lista) · ref]",
        "VAR _lim = [Nota · limite caixa · ponto inteiro]",
        "-- 2 · Textos",
        D.od_tabela(),
        "VAR _txtSob = \"LEITURA · OBRAS NO MÊS<br>\" & UPPER ( _mesL )",
        "VAR _txtLim = \"±\" & FORMAT ( _lim, \"0%\", \"pt-BR\" )",
        "VAR _txtAbx =",
        "    SWITCH (",
        "        TRUE (),",
        "        _abx = 0, \"Nenhuma das \" & " + ext("_nObras") + " & \" obras está com IDC abaixo de 1\",",
        "        _abx = _nObras, \"As \" & " + ext("_nObras") + " & \" obras estão com IDC abaixo de 1\",",
        "        " + cap(ext("_abx")) + " & \" das \" & " + ext("_nObras") + " & IF ( _abx = 1, \" obras está\", \" obras estão\" ) "
        "& \" com IDC abaixo de 1: gastam mais do que agregam\"",
        "    )",
        "VAR _txtQueda =",
        "    IF (",
        "        ISBLANK ( _oQueda ),",
        "        \"; nenhuma perdeu IDC desde \" & _mesAntN & \".\",",
        "        \"; \" & IF ( _nQueda = 1, \"só \", \"\" ) & " + art("_oQueda") + " & \" \" & _oQueda & IF ( _nQueda = 1, "
        "\" perdeu IDC desde \", \" foi a que mais perdeu IDC desde \" ) & _mesAntN & \".\"",
        "    )",
        "VAR _achado = _txtAbx & _txtQueda",
        "VAR _txtBr = SUBSTITUTE ( _lBr & \"\", \"|\", \", \" )",
        "VAR _explica =",
        "    SWITCH (",
        "        TRUE (),",
        "        _ex = 0, \"No caixa, nenhuma obra passou de \" & " + C.marca("_txtLim") + " & \" sobre o previsto em \" & _mesN & \": nenhuma \"",
        "            & \"justificativa foi exigida.\",",
        "        _br = 0, \"No caixa, \" & " + ext("_ex") + " & IF ( _ex = 1, \" obra passou\", \" obras passaram\" ) & \" de \" & " + C.marca("_txtLim"),
        "            & \" sobre o previsto e \" & IF ( _ex = 1, \"justificou\", \"todas justificaram\" ) & \" na planilha.\",",
        "        \"No caixa, \" & " + ext("_ex") + " & IF ( _ex = 1, \" obra passou\", \" obras passaram\" ) & \" de \" & " + C.marca("_txtLim"),
        "            & \" sobre o previsto; \" & IF ( _br = 1, \"ficou em branco a justificativa de \", \"ficaram em branco as de \" ) "
        "& _txtBr & \".\"",
        "    )",
        'VAR _tiN = FORMAT ( _idc, "0.00", "pt-BR" )',
        'VAR _tiTxt = IF ( ISBLANK ( _idc ), "—", _tiN )',
        D.od_num("_idc", "_ti"),
        f'VAR _tqTxt = IF ( ISBLANK ( _vQueda ), "—", "{MENOS}" & FORMAT ( ABS ( _vQueda ), "0.00", "pt-BR" ) )',
        "VAR _txtD2 = IF ( ISBLANK ( _oQueda ), \"nenhuma obra perdeu IDC no mês\", \"no IDC da \" & _oQueda & \", a maior queda do mês\" )",
        "VAR _txtD3 = IF ( _br = 1, \"justificativa em branco\", \"justificativas em branco\" ) & \" de \" & " + C.marca("_ex") + " & IF ( _ex = 1, \" exigida\", \" exigidas\" )",
        "-- 4 · Marcação",
        "VAR _corpo =",
        "    \"<span class='vs sob'>\" & _txtSob & \"</span><h2 class='ach'>\" & _achado & \"</h2>\"",
        "        & \"<p class='exp'>\" & " + D.esc("_explica") + " & \"</p>\"",
        "        & \"<div class='dst sobre-creme'>\"",
        "        & " + destaque("_tiOd", "\"IDC da carteira em \" & _mesN"),
        "        & " + destaque("\"<span class='ng'>\" & " + C.marca("_tqTxt") + " & \"</span>\"", "_txtD2"),
        "        & " + destaque(C.marca("_br"), "_txtD3"),
        "        & \"</div>\"",
        "        & " + bloco("Como ler", D.texto("<p class='cl'>Cada linha é uma obra, na ordem da nota: o IDC com a marca dos "
                                               "pontos do custo, a variação dele no mês, o desvio de caixa com a marca da "
                                               "faixa e a justificativa da planilha. Passe o mouse numa obra para ver o "
                                               "caixa mês a mês e as justificativas anteriores.</p>")),
        "RETURN",
        "    IF ( _nObras > 0, " + painel("pn-t4p", '"Leitura de Obras no mês"', "_corpo",
                                         "[Comum · JS contador tooltip]") + " )",
    ))

# ===================================================================================================== 4.3 desembolso da carteira
desenho(
    "T4 · Leitura desembolso · HTML",
    "Leitura do \"?\" de Desembolso da carteira, sobre o próprio painel (L065, Figma 391:6596, 1068 × 347, completa em "
    "duas colunas): em quantos meses a carteira gastou acima do previsto e para onde vai o desvio (achado), quem está "
    "na faixa crítica da previsão de caixa da nota (fora do previsto além do limite, para mais ou para menos), três destaques que contam e o 'como ler'; à direita, a grade das "
    "justificativas no período (exigida e preenchida · em branco · não exigida · sem aba) e as causas mais repetidas "
    "nas justificativas. Só lê contas.",
    linhas(
        "-- 1 · Leituras",
        "VAR _ref = [Mês de referência]",
        "VAR _mesL = [Mês de referência · longo]",
        "VAR _mesN = [Mês de referência · nome]",
        "VAR _ini = [T4 · Primeiro mês com aba]",
        "VAR _nAba = [T4 · Meses com aba] + 0",
        "VAR _nJan = [Série · meses até a referência]",
        "VAR _nAcima = [T4 · Leitura desembolso · meses acima do previsto] + 0",
        "VAR _desde = [T4 · Leitura desembolso · acima do previsto desde]",
        "VAR _seq = [T4 · Leitura desembolso · desvio · sequência · início]",
        "VAR _varDes = [T4 · Leitura desembolso · desvio · variação no mês]",
        "VAR _crit = [T4 · Leitura desembolso · obras na faixa crítica (lista)]",
        "VAR _lim = [T4 · Desembolso · limite da faixa crítica]",
        "VAR _exc = [T4 · Leitura desembolso · obra de maior excesso]",
        "VAR _excRs = CALCULATE ( [Desembolso · diferença no mês · ref], dObra[Obra] = _exc )",
        "VAR _excBranco = CALCULATE ( [Justificativa · em branco · ref], dObra[Obra] = _exc )",
        "VAR _artExc = " + art("_exc"),
        "VAR _prevIni = [T4 · Leitura desembolso · previsto no primeiro mês]",
        "VAR _desIni = [T4 · Leitura desembolso · desembolsado no primeiro mês]",
        "VAR _pico = [T4 · Leitura desembolso · pico do desvio]",
        "VAR _picoObra = [T4 · Leitura desembolso · obra do pico]",
        "VAR _picoMes = [T4 · Leitura desembolso · mês do pico]",
        "VAR _artPico = " + art("_picoObra"),
        "VAR _causas = [T4 · Leitura desembolso · causas mais frequentes (lista)]",
        "VAR _semJus = [T4 · Leitura desembolso · obras sem nenhuma justificativa (lista)]",
        "VAR _brancoPer = [T4 · Leitura desembolso · justificativas em branco no período] + 0",
        "VAR _sj1 = PATHITEM ( _semJus, 1 )",
        "VAR _sj1Ex = CALCULATE ( [T4 · Obra · justificativas exigidas no período], dObra[Obra] = _sj1 )",
        "VAR _artSj1 = " + art("_sj1"),
        "/* grade das justificativas no período (coluna da direita; veio da leitura de Desembolso por obra na fase 5) */",
        "VAR _obrasG =",
        "    ADDCOLUMNS (",
        "        VALUES ( dObra[Obra] ),",
        "        \"@pos\", [T1 · Obras · posição],",
        "        \"@hist\", [T4 · Meses com aba],",
        "        \"@ex\", [T4 · Obra · justificativas exigidas no período],",
        "        \"@pre\", [T4 · Obra · justificativas preenchidas no período]",
        "    )",
        "VAR _naGrade = FILTER ( _obrasG, [@hist] > 0 ) /* lista */",
        "VAR _prePer = [T4 · Leitura desembolso · justificativas preenchidas no período]",
        "VAR _mesesTodos =",
        "    ADDCOLUMNS ( VALUES ( dMes[Mes] ), \"@ate\", [Série · mês até a referência], \"@mp\", [Série · posição na janela] )",
        "VAR _meses = FILTER ( _mesesTodos, [@ate] = 1 ) /* lista */",

        "-- 2 · Textos",
        D.od_tabela(),
        "VAR _iniN = " + nm("_ini"),
        "VAR _per = " + periodo("_nAba"),
        "VAR _iniL = _iniN & IF ( YEAR ( _ini ) <> YEAR ( _ref ), \" de \" & YEAR ( _ini ), \"\" )",
        "VAR _txtSob = \"LEITURA · DESEMBOLSO DA CARTEIRA · \" & UPPER ( IF ( _ini = _ref, _mesL, _iniL & \" a \" & _mesL ) )",
        D.inteiro("_nAcima", "_tna"), D.od_num("_nAcima", "_tna"),
        "VAR _txtSeq = IF ( _seq = _ref, \" em \" & _mesN, \" desde \" & " + nm("_seq") + " )",
        "VAR _txtAchado =",
        "    IF (",
        "        _nAcima = 0,",
        "        IF ( _nAba <= 1, \"Não passou do previsto em \" & _mesN & \".\", \"Não passou do previsto em nenhum dos \" "
        "& " + C.marca("_nAba") + " & \" meses do \" & _per & \".\" ),",
        "        \"Acima do previsto \" & IF ( _nAcima = _nAba, \"nos \" & _tnaOd & \" meses do \" & _per, \"em \" & _tnaOd "
        "& \" dos \" & " + C.marca("_nAba") + " & \" meses\" )",
        "            & SWITCH (",
        "                TRUE (),",
        "                ISBLANK ( _seq ), \", e estável.\",",
        "                _varDes > 0, \", e piorando: o desvio da carteira sobe\" & _txtSeq & \".\",",
        "                \", mas melhorando: o desvio da carteira cai\" & _txtSeq & \".\"",
        "            )",
        "    )",
        lista_e("_crit", "_lc"),
        "VAR _critSem = SUBSTITUTE ( SUBSTITUTE ( \"|\" & _crit & \"|\", \"|\" & _exc & \"|\", \"|\" ), \"||\", \"|\" )",
        "VAR _critSemL = MID ( _critSem, 2, MAX ( 0, LEN ( _critSem ) - 2 ) )",
        "VAR _excNaCrit = _exc <> \"\" && _lcN > 0 && PATHCONTAINS ( _crit, _exc )",
        lista_e("_critSemL", "_lcs"),
        "VAR _txtExc = _artExc & \" \" & _exc & \", com o maior excesso em reais\" & IF ( _excBranco = 1, \" e sem justificativa\", \"\" )",
        "/* faixa crítica da previsão de caixa da nota: fora do previsto além do limite, para mais ou para menos */",
        "VAR _txtFora = \"fora do previsto em mais de \" & " + C.marca("_lim") + " & \", para mais ou para menos\"",
        "VAR _txtCrit =",
        "    SWITCH (",
        "        TRUE (),",
        "        _lcN = 0, \"nenhuma obra está \" & _txtFora,",
        "        _excNaCrit && _lcN = 1, \"uma obra está \" & _txtFora & \": \" & _txtExc,",
        "        _excNaCrit, " + ext("_lcN") + " & \" obras estão \" & _txtFora & \" — \" & SUBSTITUTE ( _critSemL, \"|\", "
        "\", \" ) & \" e \" & _txtExc,",
        "        _lcN = 1, \"uma obra está \" & _txtFora & \": \" & _lcTxt,",
        "        " + ext("_lcN") + " & \" obras estão \" & _txtFora & \": \" & _lcTxt",
        "    )",
        "VAR _txtExplica =",
        "    IF (",
        "        _nAcima = 0,",
        "        \"Em \" & _mesN & \", \" & _txtCrit & \".\",",
        "        \"Em \" & _mesN & \", \" & _txtCrit & \".\"",
        "    )",
        D.rs("_excRs", "_tex"), D.od_rs("_excRs", "_tex"),
        D.rs("_desIni", "_tdi"), D.od_rs("_desIni", "_tdi"), D.rs("_prevIni", "_tpi"),
        D.pct("_pico", "_tpc", casas=0, mais=True), D.od_pct("_pico", "_tpc"),
        "VAR _txtD1 = \"maior excesso sobre o previsto em \" & _mesN & \": \" & _artExc & \" \" & _exc",
        "VAR _txtD2 = \"desembolsados em \" & _iniN & \"; previstos \" & " + C.marca('SUBSTITUTE ( _tpiTxt, " ", UNICHAR ( 160 ) )') + "",
        "VAR _txtD3 = \"desvio d\" & _artPico & \" \" & _picoObra & \" em \" & " + nm("_picoMes")
        + " & IF ( _nAba > 1, \", o pico do \" & _per, \"\" )",
        "VAR _nC = IF ( ISBLANK ( _causas ) || _causas = \"\", 0, PATHLENGTH ( _causas ) )",
        "VAR _causasTxt =",
        "    SUBSTITUTE (",
        "        " + "".join("SUBSTITUTE ( " for _ in CAUSAS) + "\"|\" & _causas & \"|\", "
        + ", ".join(f"\"|{c}|\", \"|{CAUSA_PLURAL[c]}|\" )" for c in CAUSAS) + ",",
        "        \"|\", \"\", 1",
        "    )",
        "VAR _causasL = LEFT ( _causasTxt, MAX ( 0, LEN ( _causasTxt ) - 1 ) )",
        lista_e("_causasL", "_lca"),
        "VAR _txtCausas =",
        "    SWITCH (",
        "        _nC,",
        "        0, IF ( _prePer = 0, \"Nenhum excesso exigido trouxe justificativa no período\", "
        "\"Nenhuma causa se repete nas justificativas preenchidas\" ),",
        "        1, \"As justificativas repetem uma causa — \" & _lcaTxt,",
        "        \"As justificativas repetem \" & " + ext("_nC") + " & \" causas — \" & _lcaTxt",
        "    )",
        lista_e("_semJus", "_lsj"),
        "VAR _txtSemJus =",
        "    SWITCH (",
        "        TRUE (),",
        "        _lsjN = 1, \"só \" & _artSj1 & \" \" & _sj1 & \" não explicou nenhum dos \" & " + ext("_sj1Ex", fem=False)
        + " & IF ( _sj1Ex = 1, \" mês exigido\", \" meses exigidos\" ),",
        "        _lsjN > 1, _lsjTxt & \" não explicaram nenhum dos meses exigidos\",",
        "        _brancoPer = 0, \"todas as justificativas exigidas foram preenchidas\",",
        "        " + ext("_brancoPer") + " & IF ( _brancoPer = 1, \" ficou em branco\", \" ficaram em branco\" )",
        "    )",
        "VAR _txtOqe = _txtCausas & \".\"",
        "-- 3 · Geometria",
        "/* grade na coluna da direita (371): nome 100 px (Segoe 14; PONTA NEGRA ≈ 91, F4: sem reticências), coluna do mês =",
        "   mín(24; (371 − 100 − 52) ÷ n), o resto para 'de exigidas'; cabeçalho com a inicial do mês */",
        "VAR _cw = MIN ( 24, INT ( 219 / _nJan ) ) -- geometria",
        "VAR _resto = 271 - _nJan * _cw -- geometria",
        "VAR _grid = \" style='grid-template-columns:100px repeat(\" & _nJan & \",\" & _cw & \"px) 1fr'\"",
        "VAR _txtDe = IF ( _resto >= 100, \"DE EXIGIDAS\", \"DE EXIG.\" )",
        "-- 4 · Marcação",
        "VAR _htmlDst =",
        "    \"<div class='dst sobre-creme'>\"",
        "        & IF ( _exc <> \"\", " + destaque("_texOd", "_txtD1") + ", \"<div></div>\" )",
        "        & " + destaque("_tdiOd", "_txtD2"),
        "        & " + destaque("_tpcOd", "_txtD3"),
        "    & \"</div>\"",
        "VAR _htmlGrade =",
        "    CONCATENATEX (",
        "        _naGrade,",
        "        VAR _o = dObra[Obra]",
        "        VAR _cel =",
        "            CONCATENATEX (",
        "                ADDCOLUMNS ( _meses, \"@t\", [Obras com análise], \"@e\", [Justificativa · exigida], "
        "\"@b\", [Justificativa · em branco] ),",
        "                \"<i class='\" & SWITCH ( TRUE (), ISBLANK ( [@t] ), \"v\", [@b] = 1, \"b\", [@e] = 1, \"p\", \"n\" ) "
        "& \"' style='animation-delay:\" & ( [@pos] * 12 + [@mp] ) * 30 & \"ms'></i>\",",
        "                \"\",",
        "                dMes[Mes], ASC",
        "            )",
        "        RETURN",
        "            \"<div class='r'\" & _grid & \"><b>\" & _o & \"</b>\" & _cel & \"<em>\" "
        "& IF ( [@ex] = 0, \"—\", " + C.marca("[@pre]") + " & \" de \" & " + C.marca("[@ex]") + " ) & \"</em></div>\",",
        "        \"\",",
        "        [@pos], ASC",
        "    )",
        "VAR _htmlCabGrade =",
        "    \"<div class='h'\" & _grid & \"><span></span>\"",
        "        & CONCATENATEX (",
        "            _meses,",
        "            VAR _m = UPPER ( FORMAT ( dMes[Mes], \"mmm\", \"pt-BR\" ) )",
        "            RETURN",
        "                \"<span\" & IF ( dMes[Mes] = _ref, \" class='rf'\", \"\" ) & \">\" & LEFT ( _m, 1 ) & \"</span>\",",
        "            \"\",",
        "            dMes[Mes], ASC",
        "        ) /* lista */",
        "        & \"<span class='de'>\" & _txtDe & \"</span></div>\"",
        "VAR _esq =",
        "    \"<div class='esq'><span class='vs sob'>\" & _txtSob & \"</span>\"",
        "        & \"<h2 class='ach'>\" & _txtAchado & \"</h2>\"",
        "        & \"<p class='exp'>\" & " + D.esc("_txtExplica") + " & \"</p>\"",
        "        & _htmlDst",
        "        & " + bloco("Como ler", D.texto("<p class='cl'>Passe o mouse num mês para ver previsto, desembolsado e "
                                         "desvio de cada obra.</p>")),
        "    & \"</div>\"",
        "VAR _dir =",
        "    \"<div class='dir'><span class='vs'>Detalhe · justificativas no \" & " + 'SWITCH ( _nJan, 3, "trimestre", 6, "semestre", "período" )'
        + " & \"</span>\"",
        "        & \"<div class='gj'>\" & _htmlCabGrade & _htmlGrade",
        "        & \"<div class='lg'><span><i class='p'></i>preenchida</span><span><i class='b'></i>em branco</span>\"",
        "        & \"<span><i class='n'></i>não exigida</span></div></div>\"",
        "        & " + bloco("O que explica", "\"<p class='oqe'>\" & " + D.esc("_txtOqe") + " & \"</p>\""),
        "    & \"</div>\"",
        "VAR _corpo = \"<div class='cols'>\" & _esq & \"<i class='div'></i>\" & _dir & \"</div>\"",
        "RETURN",
        "    IF ( _nAba > 0, " + painel("pn-2c", '"Leitura de Desembolso da carteira"', "_corpo",
                                        "[Comum · JS contador tooltip]") + " )",
    ))

# ===================================================================================================== CSS
# Leituras v2 (Figma 391:4681, t04.md §2–§3): a leitura cobre o retângulo do painel (L065), offwhite, contorno 1 px
# preto, cantos retos, sem sombra; × de 26 px (X_SVG, igual ao "?" da casca); sobretítulo versalete 12 grafite; achado Barlow SemiBold 23/28; explicação
# Segoe 17/26; destaques em faixa creme (número Barlow SemiBold 34/40, rótulo Segoe 14/19; negativo sobre creme
# #A82C2C pela camada comum); "o que explica" e "como ler" Segoe 14/19. Margens 24 (as duas colunas, 1068) e 20 (as
# condensadas, 400).
# O visual é o retângulo exato do painel (sem margem nem sombra); o × é X_SVG de leituras_lib (CSS_X, no fim).
CSS_LEI = (
    ".lv{position:fixed;inset:0}"
    ".lv .pn{position:absolute;inset:0;background:#FFFFFF;border:1px solid #0B0B0C;border-radius:16px;"
    "overflow:hidden;color:#0B0B0C}"
    ".lv .sob{display:block;padding-right:44px}"
    ".lv .ach{margin-top:7px;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:23px;"
    "line-height:28px}"
    ".lv .exp{margin-top:10px;font-size:17px;line-height:26px}"
    ".lv .dst{margin-top:12px;display:flex;gap:12px;padding:12px;background:#E9E0CF}"
    ".lv .dst>div{flex:1 1 0;min-width:0}.lv .dst>div:empty{display:none}"
    ".lv .dst b{display:block;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:34px;"
    "line-height:40px;white-space:nowrap;font-variant-numeric:tabular-nums}"
    ".lv .dst span{display:block;margin-top:4px;font-size:14px;line-height:19px}"
    ".lv .dst b span,.lv .dst span span{display:inline;margin:0;font-size:inherit;line-height:inherit}"
    ".lv .sec{margin-top:12px}.lv .sec>.vs{display:block;margin-bottom:4px}"
    ".lv .oqe,.lv .cl{font-size:14px;line-height:19px}"
    # 4.1 e 4.3 · completas em duas colunas (1068 × 380 e 1068 × 347, margem 24): 600 | 371; "como ler" no pé da
    # coluna da esquerda; a da direita começa abaixo do × (Figma 391:4685 e 391:6596)
    ".pn-2c{padding:22px 24px 24px}"
    ".pn-2c .cols{display:grid;grid-template-columns:600px 1px 1fr;column-gap:24px;height:100%}"
    ".pn-2c .div{display:block;background:#E9E0CF;margin-bottom:2px}"
    ".pn-2c .esq{display:flex;flex-direction:column;min-height:0}"
    ".pn-2c .esq>.sec:last-child{margin-top:auto;padding-top:12px}"
    ".pn-2c .dir{padding-top:30px}"
    ".pn-2c .dir .sub{margin-top:5px;font-size:14px;line-height:19px;color:#3B3B3F}"
    ".pn-2c .dir .sec{margin-top:14px}"
    ".lv .mb{position:relative;display:flex;height:104px;margin-top:8px}"
    ".lv .mb .c{position:relative;flex:1 1 0}"
    ".lv .mb .c i{position:absolute;left:0;right:0;margin:0 auto;width:min(26px,70%);background:#E9E0CF}"
    ".lv .mb .c .val{position:absolute;left:-30px;right:-30px;text-align:center;font-family:'Barlow U','Segoe UI',"
    "sans-serif;font-weight:600;font-size:14px;line-height:17px;white-space:nowrap;color:#3B3B3F}"
    ".lv .mb .c .val.ini{left:0;right:auto;text-align:left}"
    ".lv .mb .c .val.fim{left:auto;right:0;text-align:right;color:#0B0B0C}"
    ".lv .mb .c .val.ini.fim{left:0;right:auto;text-align:left}"
    ".lv .mb .c .ms{position:absolute;left:0;right:0;text-align:center;font-size:13px;line-height:16px;"
    "color:#3B3B3F;white-space:nowrap}"
    ".lv .mb .c .ms.ref{font-weight:600;color:#0B0B0C}"
    ".lv .mb::after{content:'';position:absolute;left:0;right:0;top:84px;height:1px;background:#6B6B70;"
    "animation:cbFd .45s ease-out .5s backwards}"
    # 4.2 e 4.4 · condensadas (400 × 380 e 400 × 347, margem 20; sobretítulo em duas linhas)
    ".pn-t4p{padding:20px}"
    ".pn-t4p .ach{padding-right:0}"
    # grade das justificativas no período (4.3, coluna da direita de 371)
    ".lv .gj{margin-top:7px}"
    # colunas da grade vêm da medida (nome 100 px, mês = mín(24; 219 ÷ n)); este é só o padrão de 8 meses
    ".lv .gj .h,.lv .gj .r{display:grid;grid-template-columns:100px repeat(8,24px) 1fr;align-items:center}"
    ".lv .gj .h span{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:12px;line-height:15px;"
    "letter-spacing:1.2px;color:#3B3B3F;text-align:center}"
    ".lv .gj .h span.rf{color:#0B0B0C}"
    ".lv .gj .h .de{text-align:right;white-space:nowrap}"
    ".lv .gj .h{margin-bottom:6px}"
    ".lv .gj .r{height:21px}"
    ".lv .gj .r b{font-weight:400;font-size:14px;line-height:19px;white-space:nowrap}"
    ".lv .gj .r i{display:block;width:12px;height:12px;justify-self:center;animation:ttFim .2s ease-out backwards}"
    ".lv .gj i.p{background:#A9CDB9;box-shadow:inset 0 0 0 1px #6E9F85}"
    ".lv .gj i.b{background:#FFFFFF;border:1.25px dashed #C43737}"
    ".lv .gj i.n{background:#EFEFEF}"
    ".lv .gj i.v{visibility:hidden}"
    ".lv .gj .r em{font-style:normal;text-align:right;font-size:14px;line-height:19px;white-space:nowrap}"
    ".lv .gj .lg{display:flex;gap:14px;margin-top:4px;font-size:14px;line-height:19px;color:#3B3B3F}"
    ".lv .gj .lg span{display:inline-flex;align-items:center;gap:5px}"
    ".lv .gj .lg i{display:block;width:12px;height:12px}"
    "@keyframes ttFim{from{opacity:0}}"
    "@media (prefers-reduced-motion:reduce){.lv .gj .r i,.lv .mb::after{animation:none}}"
) + CSS_X

if __name__ == "__main__":
    desenho("T4 · Leitura · CSS", "CSS v2 das leituras do \"?\" da Tela 04 (sobre o painel: superfície, completa em duas "
            "colunas, condensada, grade das justificativas) e do guia da página em duas colunas (independe da T1).",
            "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(CSS_LEI))
    sys.exit(gravar(MEDIDAS, RAIZ / "dax" / "T4", GERADO))

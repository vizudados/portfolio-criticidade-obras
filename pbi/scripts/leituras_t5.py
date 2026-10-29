#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""leituras_t5 — desenho das leituras do "?" da Tela 05 · Canteiro (pbi/dax/T5/Leituras/**). As contas estão em
contas_t5.py (pasta T5 Canteiro\\Leituras\\Contas) e em base/.

Mesma gramática da T4 (docs/06-interacoes-spec.md §1.7–1.8; L058: cada número aparece uma vez por leitura; L065: a
leitura cobre o painel que explica): os dois painéis da esquerda (1068 de largura) recebem a leitura completa em duas
colunas (achado, explicação, destaques e "como ler" à esquerda; detalhe e "o que explica" à direita); os dois da
direita (400) recebem a condensada (sobretítulo numa linha, achado, explicação e destaques). Superfície, × e mecânica
em leituras_lib.py; o CSS da superfície é o da T4 (leituras_t4.CSS_LEI).

F4 (pedido do Alisson, 28/10/2026: todo número conta e todo elemento entra animado): os números das frases que ainda
eram estáticos vão marcados com C.marca() e viram odômetro no fim da medida (C.envolver_marcas); as linhas do detalhe
da qualidade entram em cascata (.a-fd) com a marca crescendo (.a-pop).

    python -X utf8 pbi/scripts/leituras_t5.py
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
from leituras_t4 import CSS_LEI, bloco, cap, destaque, ext, lista_e, nm, painel  # noqa: E402

RAIZ = AQUI.parent
GERADO = "pbi/scripts/leituras_t5.py"
DES = r"T5 Canteiro\Leituras"
MEDIDAS: list[Medida] = []
TF_REF = "Canteiro · taxa de frequência (12 meses) · ref"


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


def flex(n: str, sing: str, plur: str) -> str:
    return f'IF ( {n} = 1, "{sing}", "{plur}" )'


# ===================================================================================================== qualidade
desenho(
    "T5 · Leitura qualidade · HTML",
    "Leitura do \"?\" de Qualidade, mês a mês, sobre o próprio painel (1068 × 380, completa em duas colunas): a "
    "aprovação da carteira no mês contra a meta (achado), as obras abaixo da meta e há quantos meses a menor está "
    "abaixo (explicação), dois destaques (a menor obra e os meses da carteira na meta) e, à direita, a aprovação de cada "
    "obra no mês e o que o indicador mede. Só lê contas.",
    linhas(
        "-- 1 · Leituras",
        "VAR _mesN = [Mês de referência · nome]",
        "VAR _mesC = [Mês de referência · curto maiúsculo]",
        "VAR _c = [Canteiro · aprovação na 1.ª inspeção · ref]",
        "VAR _lim = [Nota · limite inspeção · ponto cheio]",
        "VAR _lAbx = [T5 · Leitura qualidade · obras abaixo da meta (lista) · ref]",
        "VAR _dest = [T5 · Qualidade · obra em destaque · ref]",
        "VAR _vDest = [T5 · Leitura qualidade · aprovação da obra em destaque · ref]",
        "VAR _mDest = [T5 · Leitura qualidade · meses da obra em destaque abaixo da meta] + 0",
        "VAR _nMeta = [T5 · Leitura qualidade · meses da carteira na meta] + 0",
        "VAR _nMeses = [T5 · Leitura qualidade · meses com base] + 0",
        "VAR _obras =",
        "    ADDCOLUMNS (",
        "        VALUES ( dObra[Obra] ),",
        '        "@v", [Canteiro · aprovação na 1.ª inspeção · ref],',
        '        "@pt", [Nota · pontos inspeção · ref],',
        '        "@ps", [Nota · possíveis · inspeção · ref]',
        "    )",
        "VAR _det = FILTER ( _obras, NOT ISBLANK ( [@v] ) ) /* lista */",
        "-- 2 · Textos",
        D.pct("_c", "_tc"), D.pct("_lim", "_tl", casas=0), D.pct("_vDest", "_td"),
        D.od_tabela(), D.od_pct("_vDest", "_td"),
        "VAR _txtSob = \"LEITURA · QUALIDADE, MÊS A MÊS · \" & _mesC",
        "VAR _achado =",
        "    \"A carteira aprovou \" & " + C.marca("_tcTxt") + " & \" dos serviços na primeira inspeção em \" & _mesN",
        "        & IF ( _c >= _lim, \", na meta de \", \", abaixo da meta de \" ) & " + C.marca("_tlTxt") + " & \".\"",
        lista_e("_lAbx", "_la"),
        "VAR _txtAbx =",
        "    SWITCH (",
        "        TRUE (),",
        "        _laN = 0, \"Nenhuma obra ficou abaixo da meta no mês.\",",
        "        _laN = 1, \"Só \" & _laTxt & \" ficou abaixo da meta no mês.\",",
        "        " + cap(ext("_laN")) + " & \" obras ficaram abaixo da meta: \" & _laTxt & \".\"",
        "    )",
        "VAR _txtDest =",
        "    IF (",
        "        _laN = 0 || ISBLANK ( _dest ),",
        "        \"\",",
        "        \" A menor do mês, \" & _dest & \", ficou \" & IF ( _mDest = _nMeses, \"abaixo em todos os \" & " + C.marca("_nMeses")
        + " & \" meses da janela.\", \"abaixo em \" & " + C.marca("_mDest") + " & \" dos \" & " + C.marca("_nMeses")
        + " & \" meses da janela.\" )",
        "    )",
        "VAR _explica = _txtAbx & _txtDest",
        "VAR _txtD1 = IF ( ISBLANK ( _dest ), \"\", _dest & \", a menor do mês\" )",
        "VAR _txtD2 = " + flex("_nMeta", "mês da carteira na meta", "meses da carteira na meta") + " & \" na janela\"",
        "VAR _txtOqe =",
        "    \"Serviço reprovado na primeira inspeção (FVS) volta para ser refeito: é retrabalho, que pesa no custo e no \"",
        "        & \"prazo. Na nota, o ponto cheio do item começa em \" & " + C.marca("_tlTxt") + " & \".\"",
        "-- 4 · Marcação",
        "VAR _htmlDet =",
        "    CONCATENATEX (",
        "        _det,",
        "        VAR _cls = IF ( ISBLANK ( [@pt] ), \"\", IF ( [@pt] >= [@ps], \"0\", IF ( [@pt] = 0, \"2\", \"1\" ) ) )",
        "        VAR _d = 300 + ( RANKX ( _det, [@v], , ASC, Dense ) - 1 ) * 60 -- geometria",
        "        RETURN",
        "            \"<div class='r a-fd' style='animation-delay:\" & _d & \"ms'><b>\" & " + D.esc("dObra[Obra]")
        + " & \"</b><span>\" & IF ( _cls = \"\", \"\", "
        "\"<i class='mk a-pop mk\" & _cls & \"' style='animation-delay:\" & ( _d + 100 ) & \"ms'></i>\" ) & "
        + C.marca('FORMAT ( [@v] * 100, "0.0", "pt-BR" )') + " & \"%</span></div>\",",
        "        \"\",",
        "        [@v], ASC, dObra[Obra], ASC",
        "    )",
        "VAR _esq =",
        "    \"<div class='esq'><span class='vs sob'>\" & _txtSob & \"</span>\"",
        "        & \"<h2 class='ach'>\" & _achado & \"</h2>\"",
        "        & \"<p class='exp'>\" & " + D.esc("_explica") + " & \"</p>\"",
        "        & \"<div class='dst sobre-creme'>\"",
        "        & IF ( ISBLANK ( _dest ), \"\", " + destaque("_tdOd", "_txtD1") + " )",
        "        & " + destaque(C.marca("_nMeta") + " & \" de \" & " + C.marca("_nMeses"), "_txtD2"),
        "        & \"</div>\"",
        "        & " + bloco("Como ler", D.texto("<p class='cl'>Cada linha fina é uma obra; a preta é a carteira (aprovados ÷ "
                                               "verificados, com as obras somadas) e a grafite, a obra com a menor "
                                               "aprovação no mês. O tracejado é a meta.</p>")),
        "    & \"</div>\"",
        "VAR _dir =",
        "    \"<div class='dir'><span class='vs'>Detalhe</span>\"",
        "        & \"<p class='sub'>aprovação na 1.ª inspeção em \" & _mesN & \", da menor para a maior</p>\"",
        "        & \"<div class='dl'>\" & _htmlDet & \"</div>\"",
        "        & " + bloco("O que explica", "\"<p class='oqe'>\" & " + D.esc("_txtOqe") + " & \"</p>\""),
        "    & \"</div>\"",
        "VAR _corpo = \"<div class='cols'>\" & _esq & \"<i class='div'></i>\" & _dir & \"</div>\"",
        "RETURN",
        "    IF ( NOT ISBLANK ( _c ), " + painel("pn-2c", '"Leitura de Qualidade, mês a mês"', "_corpo",
                                             "[Comum · JS contador tooltip]") + " )",
    ))

# ===================================================================================================== chuva e ritmo
desenho(
    "T5 · Leitura chuva · HTML",
    "Leitura do \"?\" de Chuva e ritmo, sobre o próprio painel (1068 × 347, completa em duas colunas): se a carteira "
    "executou menos nos meses de chuva (achado), o mês mais chuvoso e o ritmo dele (explicação), três destaques (o "
    "executado médio nos meses de chuva e nos outros e o do mês mais chuvoso) e, à direita, a quadra chuvosa de Natal e "
    "o que é dia impraticável. Só lê contas.",
    linhas(
        "-- 1 · Leituras",
        "VAR _mesC = [Mês de referência · curto maiúsculo]",
        "VAR _nCh = [T5 · Leitura chuva · meses chuvosos] + 0",
        "VAR _nJan = [Série · meses até a referência]",
        "VAR _prim = [T5 · Leitura chuva · primeiro mês chuvoso]",
        "VAR _ult = [T5 · Leitura chuva · último mês chuvoso]",
        "VAR _exCh = [T5 · Leitura chuva · executado médio nos meses chuvosos]",
        "VAR _exOut = [T5 · Leitura chuva · executado médio nos outros meses]",
        "VAR _mMax = [T5 · Leitura chuva · mês mais chuvoso]",
        "VAR _dMax = [T5 · Leitura chuva · dias no mês mais chuvoso]",
        "VAR _exMax = [T5 · Leitura chuva · executado no mês mais chuvoso]",
        "VAR _exMin = [T5 · Leitura chuva · menor executado]",
        "VAR _lim = [T5 · Chuva · limite de mês chuvoso]",
        "-- 2 · Textos",
        D.pct("_exCh", "_tch"), D.pct("_exOut", "_tou"), D.pct("_exMax", "_tmx"),
        D.od_tabela(), D.od_pct("_exCh", "_tch"), D.od_pct("_exOut", "_tou"), D.od_pct("_exMax", "_tmx"),
        D.numero("_dMax", "_tdm"),
        "VAR _nOut = _nJan - _nCh",
        "VAR _txtSob = \"LEITURA · CHUVA E RITMO · \" & _mesC",
        "VAR _txtPer = IF ( _prim = _ult, \"No mês de chuva, \" & " + nm("_prim") + ", \"Nos meses de chuva, de \" & "
        + nm("_prim") + " & \" a \" & " + nm("_ult") + ")",
        "VAR _achado =",
        "    SWITCH (",
        "        TRUE (),",
        "        _nCh = 0, \"Nenhum mês da janela teve \" & " + C.marca("_lim") + " & \" ou mais dias de chuva por obra.\",",
        "        _nOut <= 0 || ISBLANK ( _exOut ), \"Todos os meses da janela tiveram \" & " + C.marca("_lim")
        + " & \" ou mais dias de chuva por obra.\",",
        "        _txtPer & \", a carteira executou \" & IF ( _exCh < _exOut, \"menos\", \"mais\" ) & \" que nos outros meses.\"",
        "    )",
        "VAR _explica =",
        "    IF (",
        "        ISBLANK ( _mMax ) || _dMax = 0,",
        "        \"\",",
        "        " + cap(nm("_mMax")) + " & \" foi o mês mais chuvoso, com \" & " + C.marca("_tdmTxt") + " & \" dias parados por obra\"",
        "            & IF ( _exMax = _exMin, \", e teve o menor ritmo do período.\", \".\" )",
        "    )",
        "VAR _txtD1 = \"executado por mês \" & IF ( _nCh = 1, \"no mês de chuva\", \"nos \" & " + C.marca("_nCh") + " & \" meses de chuva\" )",
        "VAR _txtD2 = IF ( _nOut = 1, \"no outro mês\", \"nos outros \" & " + C.marca("_nOut") + " & \" meses\" )",
        "VAR _txtD3 = \"executado em \" & " + nm("_mMax"),
        "VAR _txtOqe =",
        "    \"A quadra chuvosa de Natal vai de março a julho, com pico em abril (normal do INMET para abril: \" & "
        + C.marca('"240,5"') + " & \" mm). \"",
        "        & \"Dia impraticável é o dia em que a chuva para o serviço externo; a base complementar registra quantos \"",
        "        & \"houve no mês em cada obra. Mês de chuva, aqui, é o que tem \" & " + C.marca("_lim") + " & \" ou mais por obra.\"",
        "-- 4 · Marcação",
        "VAR _esq =",
        "    \"<div class='esq'><span class='vs sob'>\" & _txtSob & \"</span>\"",
        "        & \"<h2 class='ach'>\" & _achado & \"</h2>\"",
        "        & IF ( _explica = \"\", \"\", \"<p class='exp'>\" & " + D.esc("_explica") + " & \"</p>\" )",
        "        & \"<div class='dst sobre-creme'>\"",
        "        & IF ( _nCh > 0, " + destaque("_tchOd", "_txtD1") + " )",
        "        & IF ( _nOut > 0 && NOT ISBLANK ( _exOut ), " + destaque("_touOd", "_txtD2") + " )",
        "        & IF ( _nCh > 0, " + destaque("_tmxOd", "_txtD3") + " )",
        "        & \"</div>\"",
        "    & \"</div>\"",
        "/* painel de 347: o 'como ler' curto vai para a coluna da direita, abaixo do 'o que explica' */",
        "VAR _dir =",
        "    \"<div class='dir'>\" & " + bloco("O que explica", "\"<p class='oqe'>\" & " + D.esc("_txtOqe") + " & \"</p>\"")
        + " & " + bloco("Como ler", D.texto("<p class='cl'>Passe o mouse num mês para ver a chuva e o executado de cada "
                                            "obra.</p>")) + " & \"</div>\"",
        "VAR _corpo = \"<div class='cols'>\" & _esq & \"<i class='div'></i>\" & _dir & \"</div>\"",
        "RETURN",
        "    IF ( _nJan > 0, " + painel("pn-2c", '"Leitura de Chuva e ritmo"', "_corpo",
                                     "[Comum · JS contador tooltip]") + " )",
    ))

# ===================================================================================================== segurança por obra
desenho(
    "T5 · Leitura segurança · HTML",
    "Leitura do \"?\" de Segurança por obra, sobre o próprio painel (400 × 380, condensada): quantas obras tiveram "
    "acidente com afastamento em 12 meses e quais passam da média do setor (achado), as obras abaixo da meta no "
    "checklist NR-18 do mês (explicação) e dois destaques (a taxa de frequência da carteira e a conformidade NR-18 da "
    "carteira). Só lê contas.",
    linhas(
        "-- 1 · Leituras",
        "VAR _mesN = [Mês de referência · nome]",
        "VAR _mesC = [Mês de referência · curto maiúsculo]",
        "VAR _n = [T5 · Obras com base · ref]",
        "VAR _nAc = [T5 · Segurança · obras com acidente em 12 meses · ref]",
        "VAR _lAcima = [T5 · Leitura segurança · obras acima do setor (lista) · ref]",
        "VAR _lNr = [T5 · Leitura segurança · obras abaixo da meta (lista) · ref]",
        f"VAR _tf = [{TF_REF}]",
        "VAR _nr = [Canteiro · conformidade NR-18 · ref]",
        "VAR _limNr = [Nota · limite NR-18 · ponto cheio]",
        "-- 2 · Textos",
        D.numero("_tf", "_ttf"), D.pct("_nr", "_tnr"), D.pct("_limNr", "_tl", casas=0),
        D.od_tabela(), D.od_num("_tf", "_ttf"), D.od_pct("_nr", "_tnr"),
        lista_e("_lAcima", "_la"), lista_e("_lNr", "_ln"),
        "VAR _txtSob = \"LEITURA · SEGURANÇA · \" & _mesC",
        "VAR _txtAc =",
        "    SWITCH (",
        "        TRUE (),",
        "        _nAc = 0, \"Nenhuma das \" & " + ext("_n") + " & \" obras teve acidente com afastamento em 12 meses\",",
        "        _nAc = 1, \"Uma das \" & " + ext("_n") + " & \" obras teve acidente com afastamento em 12 meses\",",
        "        " + cap(ext("_nAc")) + " & \" das \" & " + ext("_n") + " & \" obras tiveram acidente com afastamento em 12 meses\"",
        "    )",
        "VAR _achado =",
        "    _txtAc & SWITCH (",
        "        TRUE (),",
        "        _nAc = 0, \".\",",
        "        _laN = 0, IF ( _nAc = 1, \", dentro da média do setor.\", \", todas dentro da média do setor.\" ),",
        "        \"; \" & _laTxt & IF ( _laN = 1, \" passa\", \" passam\" ) & \" da média do setor.\"",
        "    )",
        "VAR _explica =",
        "    IF (",
        "        _lnN = 0,",
        "        \"No checklist NR-18 de \" & _mesN & \", todas as obras ficaram com \" & " + C.marca("_tlTxt") + " & \" ou mais.\",",
        "        \"No checklist NR-18 de \" & _mesN & \", \" & _lnTxt & IF ( _lnN = 1, \" ficou\", \" ficaram\" ) & \" abaixo de \" "
        "& " + C.marca("_tlTxt") + " & \".\"",
        "    )",
        "-- 4 · Marcação",
        "VAR _corpo =",
        "    \"<span class='vs sob'>\" & _txtSob & \"</span><h2 class='ach'>\" & _achado & \"</h2>\"",
        "        & \"<p class='exp'>\" & " + D.esc("_explica") + " & \"</p>\"",
        "        & \"<div class='dst sobre-creme'>\"",
        "        & " + destaque("_ttfOd", "\"acidentes por milhão de HHT na carteira\""),
        "        & " + destaque("_tnrOd", "\"da NR-18 conforme na carteira\""),
        "        & \"</div>\"",
        "RETURN",
        "    IF ( _n > 0, " + painel("pn-t4p pn-t5p", '"Leitura de Segurança por obra"', "_corpo",
                                   "[Comum · JS contador tooltip]") + " )",
    ))

# ===================================================================================================== suprimentos por obra
desenho(
    "T5 · Leitura suprimentos · HTML",
    "Leitura do \"?\" de Suprimentos por obra, sobre o próprio painel (400 × 347, condensada): quantas obras receberam "
    "menos que a meta de pedidos no prazo e completos e quais (achado), os pedidos da carteira (explicação) e dois "
    "destaques (a taxa da carteira e a da pior obra). Só lê contas.",
    linhas(
        "-- 1 · Leituras",
        "VAR _mesN = [Mês de referência · nome]",
        "VAR _mesC = [Mês de referência · curto maiúsculo]",
        "VAR _n = [T5 · Obras com base · ref]",
        "VAR _lAbx = [T5 · Leitura suprimentos · obras abaixo da meta (lista) · ref]",
        "VAR _np = [Canteiro · pedidos no prazo · ref] + 0",
        "VAR _pp = [Canteiro · pedidos previstos · ref] + 0",
        "VAR _x = [Canteiro · entregas no prazo · ref]",
        "VAR _pior = [T5 · Leitura suprimentos · pior obra · ref]",
        "VAR _xPior = [T5 · Leitura suprimentos · pior entrega · ref]",
        "VAR _lim = [Nota · limite entregas · ponto cheio]",
        "-- 2 · Textos",
        D.pct("_x", "_tx"), D.pct("_xPior", "_tp"), D.pct("_lim", "_tl", casas=0),
        D.od_tabela(), D.od_pct("_x", "_tx"), D.od_pct("_xPior", "_tp"),
        lista_e("_lAbx", "_la"),
        "VAR _txtSob = \"LEITURA · SUPRIMENTOS · \" & _mesC",
        "VAR _achado =",
        "    SWITCH (",
        "        TRUE (),",
        "        _laN = 0, \"Todas as \" & " + ext("_n") + " & \" obras receberam pelo menos \" & " + C.marca("_tlTxt") + " & \" dos pedidos no prazo e \"",
        "            & \"completos em \" & _mesN & \".\",",
        "        _laN = 1, \"Só \" & _laTxt & \" recebeu menos de \" & " + C.marca("_tlTxt") + " & \" dos pedidos no prazo e completos em \" & _mesN & \".\",",
        "        " + cap(ext("_laN")) + " & \" obras receberam menos de \" & " + C.marca("_tlTxt") + " & \" dos pedidos no prazo e completos: \" & _laTxt & \".\"",
        "    )",
        "VAR _explica = \"Na carteira, \" & " + C.marca("_np") + " & \" de \" & " + C.marca("_pp") + " & IF ( _pp = 1, \" pedido chegou\", \" pedidos chegaram\" ) "
        "& \" no prazo e completos.\"",
        "VAR _txtD2 = IF ( ISBLANK ( _pior ), \"\", \"na \" & _pior & \", a menor do mês\" )",
        "-- 4 · Marcação",
        "VAR _corpo =",
        "    \"<span class='vs sob'>\" & _txtSob & \"</span><h2 class='ach'>\" & " + D.esc("_achado") + " & \"</h2>\"",
        "        & \"<p class='exp'>\" & _explica & \"</p>\"",
        "        & \"<div class='dst sobre-creme'>\"",
        "        & " + destaque("_txOd", "\"da carteira no prazo e completos\""),
        "        & IF ( ISBLANK ( _pior ), \"\", " + destaque("_tpOd", "_txtD2") + " )",
        "        & \"</div>\"",
        "RETURN",
        "    IF ( _pp > 0, " + painel("pn-t4p pn-t5p", '"Leitura de Suprimentos por obra"', "_corpo",
                                    "[Comum · JS contador tooltip]") + " )",
    ))

CSS_T5 = (
    # condensadas da T5: sobretítulo numa linha
    ".pn-t5p .sob{white-space:nowrap}"
    # detalhe da qualidade: uma obra por linha (nome à esquerda, marca e aprovação à direita)
    ".lv .dl{margin-top:6px}"
    ".lv .dl .r{display:flex;justify-content:space-between;align-items:center;height:22px;white-space:nowrap}"
    ".lv .dl .r b{font-weight:400;font-size:14px;line-height:19px}"
    ".lv .dl .r span{display:flex;align-items:center;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;"
    "font-size:15px;line-height:19px}"
    ".lv .dl .r .mk{margin-right:6px}"
)

if __name__ == "__main__":
    desenho("T5 · Leitura · CSS", "CSS das leituras do \"?\" da Tela 05: a superfície, a completa em duas colunas e a "
            "condensada da T4 (leituras_t4.CSS_LEI), o sobretítulo numa linha das condensadas e a lista do detalhe.",
            "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(CSS_LEI + CSS_T5))
    sys.exit(gravar(MEDIDAS, RAIZ / "dax" / "T5", GERADO))

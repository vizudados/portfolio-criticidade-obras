#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""contas_t5 — contas da Tela 05 · Canteiro (pbi/dax/T5/**/Contas). Tela nova da F3 (docs/08 §6): o canteiro está
seguro, fazendo certo da primeira vez e recebendo material no prazo? Só o que é próprio da tela; o resto vem de base/
(Canteiro · … no contexto e · ref, limites da nota e séries da janela). Idempotente; apaga os .dax gerados por ele que
saíram da lista.

A T5 é da carteira, como a T4: recorte de obras do drawer (dObra) e mês de referência em dMesRef (desconectada; sem
escolha, o último mês). Séries mês a mês vão do primeiro mês da janela ([Série · primeiro mês]) ao de referência. A base
complementar é mensal: não traz o dia do acidente, então o cartão conta meses sem acidente com afastamento (não dias).
As metas são os limites de ponto cheio da nota ([Nota · limite … · ponto cheio]) e a média do setor da taxa de
frequência ([Nota · limite acidentes · setor]); nenhum número da nota fica escrito aqui. Oráculo: dados/_gabarito
(base_complementar.csv e fato_analise_critica.csv), set/26 com a janela de 12 meses.

    python -X utf8 pbi/scripts/contas_t5.py
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from contas_lib_projeto import Medida, gravar  # noqa: E402

PCT = "0.00%"
INT = "0"
TXT = "texto"
DATA = "dd/mm/yyyy"
NUM = "0.00"
MEDIDAS: list[Medida] = []
GAB = "dados/_gabarito (base_complementar.csv, fato_analise_critica.csv)"

TELA = "T5 Canteiro"
CART = rf"{TELA}\Cartões\Contas"
SEG = rf"{TELA}\Segurança por obra\Contas"
QUA = rf"{TELA}\Qualidade mês a mês\Contas"
SUP = rf"{TELA}\Suprimentos por obra\Contas"
CHU = rf"{TELA}\Chuva e ritmo\Contas"
LEI = rf"{TELA}\Leituras\Contas"

# indicadores da base com a meta da nota: (código, medida no contexto, medida · ref, limite do ponto cheio)
ITENS = {
    "NR-18": ("Canteiro · conformidade NR-18", "Canteiro · conformidade NR-18 · ref", "Nota · limite NR-18 · ponto cheio"),
    "Inspeção": ("Canteiro · aprovação na 1.ª inspeção", "Canteiro · aprovação na 1.ª inspeção · ref",
                 "Nota · limite inspeção · ponto cheio"),
    "Entregas": ("Canteiro · entregas no prazo", "Canteiro · entregas no prazo · ref",
                 "Nota · limite entregas · ponto cheio"),
}
TF_REF = "Canteiro · taxa de frequência (12 meses) · ref"


def m(nome, pasta, formato, descricao, dax, oraculo=""):
    MEDIDAS.append(Medida(nome, pasta, formato, descricao, dax.strip("\n"), oraculo))


def janela(expr: str) -> str:
    """Tabela dos meses da janela (do primeiro mês da série ao de referência) com @v = expr no mês."""
    return f"""ADDCOLUMNS (
        FILTER ( ALL ( dMes[Mes] ), dMes[Mes] >= _ini && dMes[Mes] <= _ref ),
        "@v", {expr}
    )"""


JANELA_VARS = """VAR _ini = [Série · primeiro mês]
VAR _ref = [Mês de referência]"""


# ======================================================================================================== cartões
m("T5 · Acidentes · último mês", CART, DATA,
  "Último mês, até o de referência, com acidente com afastamento em alguma obra do recorte (todo o histórico da base). "
  "Vazio quando nenhum. Ex. set/26: jul/26 (REDINHA).",
  """VAR _ref = [Mês de referência]
RETURN
    CALCULATE ( MAX ( fBaseObra[Mes] ), REMOVEFILTERS ( dMes ), fBaseObra[Mes] <= _ref, fBaseObra[Acidentes] > 0 )""",
  GAB + " · set/26: 01/07/2026")
m("T5 · Acidentes · início do histórico", CART, DATA,
  "Primeiro mês com base complementar das obras do recorte no histórico do painel. Ex.: out/25.",
  "CALCULATE ( MIN ( fBaseObra[Mes] ), REMOVEFILTERS ( dMes ) )", GAB + ": 01/10/2025")
m("T5 · Acidentes · meses sem acidente", CART, INT,
  "Meses seguidos sem acidente com afastamento no recorte, contados depois do último mês com acidente até o de "
  "referência (a base é mensal: não dá o dia). Sem acidente no histórico, os meses do histórico até o de referência. "
  "Ex. set/26: 2 (ago e set, depois do de REDINHA em jul/26).",
  """VAR _ref = [Mês de referência]
VAR _ult = [T5 · Acidentes · último mês]
VAR _ini = [T5 · Acidentes · início do histórico]
RETURN
    IF (
        NOT ISBLANK ( _ref ) && NOT ISBLANK ( _ini ),
        IF ( ISBLANK ( _ult ), DATEDIFF ( _ini, _ref, MONTH ) + 1, DATEDIFF ( _ult, _ref, MONTH ) )
    )""", GAB + " · set/26: 2")
m("T5 · Acidentes · obras do último (lista)", CART, TXT,
  "Obras com acidente com afastamento no último mês com acidente, em ordem alfabética, separadas por '|'. Ex. set/26: "
  "REDINHA.",
  """VAR _ult = [T5 · Acidentes · último mês]
RETURN
    IF (
        NOT ISBLANK ( _ult ),
        CONCATENATEX (
            FILTER (
                VALUES ( dObra[Obra] ),
                CALCULATE ( SUM ( fBaseObra[Acidentes] ), REMOVEFILTERS ( dMes ), fBaseObra[Mes] = _ult ) > 0
            ),
            dObra[Obra], "|", dObra[Obra], ASC
        )
    )""", GAB + " · set/26: REDINHA")
m("T5 · Obras com base · ref", CART, INT,
  "Obras do recorte com base complementar no mês de referência. Ex. set/26: 7.",
  """VAR _ref = [Mês de referência]
RETURN
    CALCULATE ( DISTINCTCOUNT ( fBaseObra[Obra] ), REMOVEFILTERS ( dMes ), fBaseObra[Mes] = _ref ) + 0""",
  GAB + " · set/26: 7")
m("T5 · Segurança · obras acima do setor · ref", CART, INT,
  "Obras com taxa de frequência de 12 meses acima da média do setor ([Nota · limite acidentes · setor]) no mês de "
  "referência: as que zeram o item acidentes da nota. Ex. set/26: 2 (REDINHA 11,0 e POTENGI 8,0).",
  f"""VAR _lim = [Nota · limite acidentes · setor]
RETURN
    COUNTROWS ( FILTER ( VALUES ( dObra[Obra] ), [{TF_REF}] > _lim ) ) + 0""", GAB + " · set/26: 2")
m("T5 · Segurança · obras com acidente em 12 meses · ref", CART, INT,
  "Obras com algum acidente com afastamento nos 12 meses até o de referência. Ex. set/26: 3 (JANGADA, POTENGI e "
  "REDINHA).",
  """COUNTROWS ( FILTER ( VALUES ( dObra[Obra] ), [Canteiro · acidentes 12 meses · ref] > 0 ) ) + 0""",
  GAB + " · set/26: 3")
for cod, (base_, ref_, lim) in ITENS.items():
    m(f"T5 · {cod} · obras abaixo da meta · ref", CART, INT,
      f"Obras com [{base_}] no mês de referência abaixo do ponto cheio da nota ([{lim}]); sem dado não conta. "
      "Ex. set/26: 3 (JANGADA, POTENGI e REDINHA).",
      f"""VAR _lim = [{lim}]
RETURN
    COUNTROWS ( FILTER ( VALUES ( dObra[Obra] ), VAR _x = [{ref_}] RETURN NOT ISBLANK ( _x ) && _x < _lim ) ) + 0""",
      GAB + " · set/26: 3")

# ======================================================================================================== segurança por obra
m("T5 · Segurança · ordem", SEG, NUM,
  "Ordem das linhas de Segurança por obra (crescente): a maior taxa de frequência de 12 meses primeiro e, no empate "
  "(zero acidente), a menor conformidade NR-18 do mês. Vazio sem base no mês de referência (a linha some). Ex. set/26: "
  "REDINHA, POTENGI, JANGADA, TIROL, PONTA NEGRA, DUNAS, CAJUEIRO.",
  f"""VAR _tf = [{TF_REF}]
VAR _nr = [Canteiro · conformidade NR-18 · ref]
RETURN
    IF ( NOT ISBLANK ( _tf ) || NOT ISBLANK ( _nr ), - _tf * 100 + _nr )""", GAB + " · set/26: REDINHA −1095,6")
m("T5 · Segurança · topo da escala", SEG, NUM,
  "Topo da escala das barras da taxa de frequência: o dobro da média do setor ou o maior valor das obras do visual "
  "arredondado para cima de 5 em 5 (a linha do setor fica na metade ou antes). Ex. set/26: 15.",
  f"""VAR _lim = [Nota · limite acidentes · setor]
VAR _mx = MAXX ( ALLSELECTED ( dObra[Obra] ), [{TF_REF}] )
RETURN
    MAX ( 2 * _lim, CEILING ( _mx, 5 ) )""", GAB + " · set/26: 15")

# ======================================================================================================== suprimentos por obra
m("T5 · Entregas · ordem", SUP, PCT,
  "Ordem das linhas de Suprimentos por obra (crescente): a menor taxa de entregas no prazo e completas do mês primeiro. "
  "Vazio sem pedido previsto (a linha some). Ex. set/26: POTENGI 76,9%, REDINHA 85,2%, JANGADA 86,4%.",
  "[Canteiro · entregas no prazo · ref]", GAB + " · set/26: POTENGI 0,769")
m("T5 · Entregas · base da escala", SUP, PCT,
  "Começo da trilha das entregas (o fim é 100%): 60%, ou menos quando alguma obra do visual fica abaixo disso "
  "(arredondado para baixo de 10 em 10 pontos, com 5 de folga). Ex. set/26: 60%.",
  """VAR _mn =
    MINX (
        FILTER ( ALLSELECTED ( dObra[Obra] ), NOT ISBLANK ( [Canteiro · entregas no prazo · ref] ) ),
        [Canteiro · entregas no prazo · ref]
    )
RETURN
    MIN ( 0.6, FLOOR ( _mn - 0.05, 0.1 ) )""", GAB + " · set/26: 0,6")

# ======================================================================================================== qualidade mês a mês
m("T5 · Qualidade · base da escala", QUA, PCT,
  "Piso do eixo da aprovação na 1.ª inspeção (o teto é 100%): 85%, ou menos quando alguma obra do recorte fica abaixo "
  "na janela (arredondado para baixo de 5 em 5 pontos, com 1 de folga). Ex. set/26: 85% (o menor é REDINHA em ago/26, "
  "87,5%).",
  JANELA_VARS + """
VAR _t =
    FILTER (
        ADDCOLUMNS (
            CROSSJOIN ( VALUES ( dObra[Obra] ), FILTER ( ALL ( dMes[Mes] ), dMes[Mes] >= _ini && dMes[Mes] <= _ref ) ),
            "@v", [Canteiro · aprovação na 1.ª inspeção]
        ),
        NOT ISBLANK ( [@v] )
    )
VAR _mn = MINX ( _t, [@v] )
RETURN
    IF ( NOT ISBLANK ( _mn ), MIN ( 0.85, FLOOR ( _mn - 0.01, 0.05 ) ) )""", GAB + " · set/26: 0,85")
m("T5 · Qualidade · obra em destaque · ref", QUA, TXT,
  "A obra do recorte com a menor aprovação na 1.ª inspeção no mês de referência (no empate, a primeira em ordem "
  "alfabética): a linha que o gráfico destaca. Ex. set/26: REDINHA (89,6%).",
  """VAR _t =
    FILTER (
        ADDCOLUMNS ( VALUES ( dObra[Obra] ), "@v", [Canteiro · aprovação na 1.ª inspeção · ref] ),
        NOT ISBLANK ( [@v] )
    )
VAR _mn = MINX ( _t, [@v] )
RETURN
    CONCATENATEX ( TOPN ( 1, FILTER ( _t, [@v] = _mn ), dObra[Obra], ASC ), dObra[Obra] )""",
  GAB + " · set/26: REDINHA")

# ======================================================================================================== chuva e ritmo
m("T5 · Chuva · topo da escala", CHU, NUM,
  "Topo da escala dos dias impraticáveis por chuva (média por obra) na janela: o maior mês arredondado para cima de 2 "
  "em 2, no mínimo 10. Ex. set/26: 10 (abr/26, 9,6).",
  JANELA_VARS + f"""
VAR _mx = MAXX ( {janela("[Canteiro · dias de chuva]")}, [@v] )
RETURN
    MAX ( 10, CEILING ( _mx, 2 ) )""", GAB + " · set/26: 10")
m("T5 · Ritmo · topo da escala", CHU, PCT,
  "Topo da escala do executado no mês da carteira na janela: o maior mês arredondado para cima de 1 em 1 ponto, no "
  "mínimo 2%. Ex. set/26: 5% (set/26, 4,7%).",
  JANELA_VARS + f"""
VAR _mx = MAXX ( {janela("[Físico · executado no mês]")}, [@v] )
RETURN
    MAX ( 0.02, CEILING ( _mx, 0.01 ) )""", GAB + " · set/26: 0,05")

# ======================================================================================================== leituras
m("T5 · Chuva · limite de mês chuvoso", LEI, NUM,
  "Dias impraticáveis por chuva (média por obra) a partir dos quais o mês conta como chuvoso nas leituras. Constante.",
  "5", "constante")


def lista_obras(nome, pasta, descricao, filtro, ordem, oraculo):
    m(nome, pasta, TXT, descricao,
      f"""CONCATENATEX (
    FILTER ( VALUES ( dObra[Obra] ), {filtro} ),
    dObra[Obra], "|", {ordem}, ASC, dObra[Obra], ASC
)""", oraculo)


lista_obras("T5 · Leitura segurança · obras com acidente em 12 meses (lista) · ref", LEI,
            "Obras com acidente com afastamento nos 12 meses até o de referência, da maior para a menor taxa de "
            "frequência. Ex. set/26: REDINHA|POTENGI|JANGADA.",
            "[Canteiro · acidentes 12 meses · ref] > 0", f"- [{TF_REF}]", GAB + " · set/26: REDINHA|POTENGI|JANGADA")
lista_obras("T5 · Leitura segurança · obras acima do setor (lista) · ref", LEI,
            "Obras com taxa de frequência de 12 meses acima da média do setor, da maior para a menor. Ex. set/26: "
            "REDINHA|POTENGI.",
            f"[{TF_REF}] > [Nota · limite acidentes · setor]", f"- [{TF_REF}]", GAB + " · set/26: REDINHA|POTENGI")
for cod, (base_, ref_, lim) in ITENS.items():
    rot = {"NR-18": "segurança", "Inspeção": "qualidade", "Entregas": "suprimentos"}[cod]
    lista_obras(f"T5 · Leitura {rot} · obras abaixo da meta (lista) · ref", LEI,
                f"Obras com [{base_}] no mês de referência abaixo do ponto cheio da nota, da menor para a maior. "
                "Ex. set/26: " + {"NR-18": "POTENGI|REDINHA|JANGADA", "Inspeção": "REDINHA|POTENGI|JANGADA",
                                  "Entregas": "POTENGI|REDINHA|JANGADA"}[cod] + ".",
                f"VAR _x = [{ref_}] RETURN NOT ISBLANK ( _x ) && _x < [{lim}]", f"[{ref_}]",
                GAB + " · set/26")
m("T5 · Leitura qualidade · meses da carteira na meta", LEI, INT,
  "Meses da janela em que a carteira (soma ÷ soma) aprovou na 1.ª inspeção pelo menos o ponto cheio da nota. Ex. "
  "set/26, 12 meses: 1 (mar/26, 95,0%).",
  JANELA_VARS + f"""
VAR _lim = [Nota · limite inspeção · ponto cheio]
RETURN
    COUNTROWS ( FILTER ( {janela("[Canteiro · aprovação na 1.ª inspeção]")}, NOT ISBLANK ( [@v] ) && [@v] >= _lim ) ) + 0""",
  GAB + " · set/26: 1")
m("T5 · Leitura qualidade · meses com base", LEI, INT,
  "Meses da janela com base complementar de alguma obra do recorte. Ex. set/26, 12 meses: 12.",
  JANELA_VARS + f"""
RETURN
    COUNTROWS ( FILTER ( {janela("[Canteiro · serviços verificados]")}, [@v] > 0 ) ) + 0""", GAB + " · set/26: 12")
m("T5 · Leitura qualidade · meses da obra em destaque abaixo da meta", LEI, INT,
  "Meses da janela em que a obra em destaque ficou abaixo do ponto cheio da 1.ª inspeção. Ex. set/26: 12 (REDINHA).",
  JANELA_VARS + f"""
VAR _obra = [T5 · Qualidade · obra em destaque · ref]
VAR _lim = [Nota · limite inspeção · ponto cheio]
RETURN
    IF (
        NOT ISBLANK ( _obra ),
        CALCULATE (
            COUNTROWS ( FILTER ( {janela("[Canteiro · aprovação na 1.ª inspeção]")}, NOT ISBLANK ( [@v] ) && [@v] < _lim ) ),
            dObra[Obra] = _obra
        ) + 0
    )""", GAB + " · set/26: 12")
m("T5 · Leitura qualidade · aprovação da obra em destaque · ref", LEI, PCT,
  "Aprovação na 1.ª inspeção da obra em destaque no mês de referência. Ex. set/26: 89,6% (REDINHA).",
  """VAR _obra = [T5 · Qualidade · obra em destaque · ref]
RETURN
    IF ( NOT ISBLANK ( _obra ), CALCULATE ( [Canteiro · aprovação na 1.ª inspeção · ref], dObra[Obra] = _obra ) )""",
  GAB + " · set/26: 0,896")
m("T5 · Leitura suprimentos · pior obra · ref", LEI, TXT,
  "A obra com a menor taxa de entregas no prazo e completas no mês de referência (no empate, a primeira em ordem "
  "alfabética). Ex. set/26: POTENGI.",
  """VAR _t =
    FILTER ( ADDCOLUMNS ( VALUES ( dObra[Obra] ), "@v", [Canteiro · entregas no prazo · ref] ), NOT ISBLANK ( [@v] ) )
VAR _mn = MINX ( _t, [@v] )
RETURN
    CONCATENATEX ( TOPN ( 1, FILTER ( _t, [@v] = _mn ), dObra[Obra], ASC ), dObra[Obra] )""", GAB + " · set/26: POTENGI")
m("T5 · Leitura suprimentos · pior entrega · ref", LEI, PCT,
  "Entregas no prazo e completas da pior obra no mês de referência. Ex. set/26: 76,9% (POTENGI, 20 de 26).",
  """VAR _obra = [T5 · Leitura suprimentos · pior obra · ref]
RETURN
    IF ( NOT ISBLANK ( _obra ), CALCULATE ( [Canteiro · entregas no prazo · ref], dObra[Obra] = _obra ) )""",
  GAB + " · set/26: 0,769")


def chuva_conta(nome, formato, descricao, ret, oraculo):
    m(nome, LEI, formato, descricao,
      JANELA_VARS + f"""
VAR _lim = [T5 · Chuva · limite de mês chuvoso]
VAR _t =
    FILTER (
        ADDCOLUMNS (
            FILTER ( ALL ( dMes[Mes] ), dMes[Mes] >= _ini && dMes[Mes] <= _ref ),
            "@ch", [Canteiro · dias de chuva],
            "@ex", [Físico · executado no mês]
        ),
        NOT ISBLANK ( [@ch] ) && NOT ISBLANK ( [@ex] )
    )
VAR _chuv = FILTER ( _t, [@ch] >= _lim )
VAR _out = FILTER ( _t, [@ch] < _lim )
RETURN
    {ret}""", oraculo)


chuva_conta("T5 · Leitura chuva · meses chuvosos", INT,
            "Meses da janela (com base e planilha) com pelo menos [T5 · Chuva · limite de mês chuvoso] dias impraticáveis "
            "por obra. Ex. set/26: 5 (mar a jul/26).", "COUNTROWS ( _chuv ) + 0", GAB + " · set/26: 5")
chuva_conta("T5 · Leitura chuva · primeiro mês chuvoso", DATA, "Primeiro mês chuvoso da janela. Ex. set/26: mar/26.",
            "MINX ( _chuv, dMes[Mes] )", GAB + " · set/26: 01/03/2026")
chuva_conta("T5 · Leitura chuva · último mês chuvoso", DATA, "Último mês chuvoso da janela. Ex. set/26: jul/26.",
            "MAXX ( _chuv, dMes[Mes] )", GAB + " · set/26: 01/07/2026")
chuva_conta("T5 · Leitura chuva · executado médio nos meses chuvosos", PCT,
            "Média simples do executado no mês da carteira nos meses chuvosos da janela. Ex. set/26: 3,1%.",
            "AVERAGEX ( _chuv, [@ex] )", GAB + " · set/26: 0,03128")
chuva_conta("T5 · Leitura chuva · executado médio nos outros meses", PCT,
            "Média simples do executado no mês da carteira nos meses da janela que não foram chuvosos. Ex. set/26: "
            "4,1%.", "AVERAGEX ( _out, [@ex] )", GAB + " · set/26: 0,04115")
chuva_conta("T5 · Leitura chuva · mês mais chuvoso", DATA,
            "O mês da janela com mais dias impraticáveis por chuva (no empate, o mais recente). Ex. set/26: abr/26.",
            "MAXX ( TOPN ( 1, _t, [@ch], DESC, dMes[Mes], DESC ), dMes[Mes] )", GAB + " · set/26: 01/04/2026")
chuva_conta("T5 · Leitura chuva · dias no mês mais chuvoso", NUM,
            "Dias impraticáveis por chuva (média por obra) no mês mais chuvoso da janela. Ex. set/26: 9,6.",
            "MAXX ( _t, [@ch] )", GAB + " · set/26: 9,57")
chuva_conta("T5 · Leitura chuva · executado no mês mais chuvoso", PCT,
            "Executado no mês da carteira no mês mais chuvoso da janela. Ex. set/26: 2,8% (abr/26).",
            "MAXX ( TOPN ( 1, _t, [@ch], DESC, dMes[Mes], DESC ), [@ex] )", GAB + " · set/26: 0,02842")
chuva_conta("T5 · Leitura chuva · menor executado", PCT,
            "O menor executado no mês da carteira na janela (com base e planilha). Ex. set/26: 2,8% (abr/26).",
            "MINX ( _t, [@ex] )", GAB + " · set/26: 0,02842")

if __name__ == "__main__":
    sys.exit(gravar(MEDIDAS, AQUI.parent / "dax" / "T5", "pbi/scripts/contas_t5.py"))

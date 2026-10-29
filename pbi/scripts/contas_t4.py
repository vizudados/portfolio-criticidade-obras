#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""contas_t4 — contas da Tela 04 · Resultado no tempo (pbi/dax/T4/**/Contas). Só o que é próprio da tela; o resto vem
de base/ (contas no contexto e · ref) e de poucas contas genéricas de T1 (posição da obra, sequência da variação, lista
de justificativas em branco). Idempotente; apaga os .dax gerados por ele que saíram da lista.

A T4 é da carteira no tempo: recorte de obras do drawer (dObra) e mês de referência em dMesRef (desconectada; sem
escolha, o último mês). Séries mês a mês vão do primeiro mês da janela ([Série · primeiro mês]: a janela de 12, 9, 6
ou 3 meses do drawer, nunca antes de jan/26) ao de referência. Toda conta que descreve a série (sequências, "em x de y
meses", "desde", melhor mês, pico, meses acima do previsto, justificativas no período) olha só a janela; comparação
mês a mês só entre dois meses da janela (o primeiro mês da janela não se compara com o anterior). As contas de mês
anterior (cartão, tooltip do mês, variação no mês) não mudam. Oráculo:
mockup/data/criticidade-obras.json (carteira.serie[], obras[].serie[], obras[].ultimo; jun/26). Spec:
docs/06-interacoes-spec-t4.md (§3 tooltips, §4 leituras, §7 números e campos que faltavam no JSON).

    python -X utf8 pbi/scripts/contas_t4.py
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from contas_lib_projeto import Medida, gravar  # noqa: E402
from justificativas_rodape import RODAPE_NOMES  # noqa: E402

F = "fAnaliseCritica"
RS = '"R$" #,0.00;-"R$" #,0.00;"R$" 0.00'
PCT = "0.00%"
PP = "+0.00;-0.00;0.00"
INT = "0"
TXT = "texto"
DATA = "dd/mm/yyyy"
NUM = "0.00"
MEDIDAS: list[Medida] = []

# Retiradas do modelo em 08/10/2026 (auditoria: dependencias-pos-telas.json e dependencias-final.json, chave mortas).
# Nenhum visual alcança estas contas e nenhum script de QA as lê (o conferir_contas.py, que lia as 16 'Criticidade ·
# … · ref' e o rótulo, saiu do projeto nesta data). Fora da gravação: o gerador não escreve o nome e apaga o .dax que
# tinha escrito antes. Para reativar, tire o nome do conjunto.
RETIRADAS = {
    # F3 (28/10/2026): sem leitor depois que o "Mês anterior" virou o IDC, o mês a mês passou ao resultado aplicado e
    # Resultado por obra e Desembolso por obra viraram a tabela Obras no mês (com uma leitura e um tooltip só)
    "T4 · Ativos não consumidos · mês anterior · ref",
    "T4 · Cartões · mês anterior",
    "T4 · Leitura desembolso por obra · meses seguidos sem justificativa",
    "T4 · Leitura desembolso por obra · obra em destaque",
    "T4 · Leitura desembolso por obra · obras justificadas por causa · aditivo (lista)",
    "T4 · Leitura desembolso por obra · obras justificadas por causa · compra (lista)",
    "T4 · Leitura desembolso por obra · obras justificadas por causa · efetivo (lista)",
    "T4 · Leitura desembolso por obra · obras justificadas por causa · medicao (lista)",
    "T4 · Leitura desembolso por obra · obras justificadas por causa · outra (lista)",
    "T4 · Leitura desembolso por obra · obras justificadas por causa · postergada (lista)",
    "T4 · Leitura desembolso por obra · obras justificadas por causa · sinal (lista)",
    "T4 · Leitura desembolso por obra · silêncio é o maior excesso",
    "T4 · Leitura mês · alta dos ativos (razão)",
    "T4 · Leitura mês · ativos · sequência · início",
    "T4 · Leitura mês · início do detalhe",
    "T4 · Leitura mês · meses com alta dos ativos",
    "T4 · Leitura mês · obras que puxam os ativos (lista)",
    "T4 · Leitura mês · sem estoque no primeiro mês",
    "T4 · Leitura obra · acima do início (lista)",
    "T4 · Leitura obra · obra que mais caiu",
    "T4 · Leitura obra · obra que mais subiu",
    "T4 · Leitura obra · obras que melhoraram",
    "T4 · Leitura obra · obras que pioraram",
    "T4 · Leitura obra · seguem negativas (lista)",
    "T4 · Leitura obra · viraram negativas (lista)",
    "T4 · Por obra · faixa do custo · ref",
    "T4 · Por obra · máximo do custo",
    "T4 · Resultado % · melhor mês",
    "T4 · Sem estoque · meses negativos",
    "T4 · Sem estoque · sequência · início",
    "T4 · Variação · sequência · início",
    "T4 · Ativos não consumidos · mês anterior",
    "T4 · Ativos não consumidos · variação no mês",
    "T4 · Justificativa · causa · ref",
    "T4 · Leitura desembolso por obra · obra há mais meses sem justificativa",
    "T4 · Leitura mês · alta dos ativos por obra",
    "T4 · Leitura mês · ativos no primeiro mês",
    "T4 · Por obra · faixa do custo",
    "T4 · Resultado % · no primeiro mês com aba",
    "T4 · Desembolso por obra · aba do mês",
    "T4 · Leitura desembolso por obra · maior excesso justificado · obra",
    "T4 · Leitura obra · desembolso consumiu o ganho (lista)",
    "T4 · Leitura obra · físico atrasado e caindo (lista)",
    "T4 · Leitura obra · obra em mobilização",
    "T4 · Leitura obra · obras que perdem pontos pela variação",
    "T4 · Obras com resultado estável",
    "T4 · Obras com resultado estável · no primeiro mês",
    "T4 · Obras com resultado estável · ref",
    "T4 · Por obra · maior resultado % absoluto",
}


TELA = "T4 Resultado no tempo"
CART = rf"{TELA}\Cartões\Contas"
MES = rf"{TELA}\Resultado mês a mês\Contas"
OBRA = rf"{TELA}\Resultado por obra\Contas"
DESC = rf"{TELA}\Desembolso da carteira\Contas"
DOB = rf"{TELA}\Desembolso por obra\Contas"
COM = rf"{TELA}\Comum\Contas"
TT = rf"{TELA}\Tooltips\Contas"
LEI = rf"{TELA}\Leituras\Contas"


def m(nome, pasta, formato, descricao, dax, oraculo=""):
    MEDIDAS.append(Medida(nome, pasta, formato, descricao, dax.strip("\n"), oraculo))


def ref(nome, base_, pasta, formato, oraculo=""):
    """[base_] no mês de referência."""
    m(nome, pasta, formato, f"[{base_}] no mês de referência (seletor do drawer; sem escolha, o último mês).",
      f"""VAR _mes = [Mês de referência]
RETURN
    CALCULATE ( [{base_}], REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )""", oraculo)


def primeiro(nome, base_, pasta, formato, oraculo=""):
    """[base_] no primeiro mês com aba do recorte (jan/26 na carteira)."""
    m(nome, pasta, formato, f"[{base_}] no primeiro mês com aba do recorte, até o de referência.",
      f"""VAR _ini = [T4 · Primeiro mês com aba]
RETURN
    CALCULATE ( [{base_}], REMOVEFILTERS ( dMes ), dMes[Mes] = _ini )""", oraculo)


# Meses da janela (do primeiro mês da janela ao de referência) e meses comparáveis com o anterior dentro dela. Quem usa
# declara _ref e _ini (JANELA_VARS).
JANELA_VARS = "VAR _ref = [Mês de referência]\nVAR _ini = [Série · primeiro mês]"
MESES_JANELA = "FILTER ( ALL ( dMes[Mes] ), dMes[Mes] >= _ini && dMes[Mes] <= _ref )"
MESES_COMPARA = "FILTER ( ALL ( dMes[Mes] ), dMes[Mes] > _ini && dMes[Mes] <= _ref )"
MESES_ATE_REF = MESES_JANELA


def obras_ref(colunas: str) -> str:
    """Tabela das obras com aba no mês de referência (recorte do drawer), com as colunas pedidas."""
    return f"""CALCULATETABLE (
        ADDCOLUMNS ( VALUES ( {F}[Obra] ), {colunas} ),
        REMOVEFILTERS ( dMes ),
        dMes[Mes] = _mes
    )"""


def obras_ref_pos(colunas: str) -> str:
    """Como obras_ref, pelo eixo dObra (as contas da nota não seguem um filtro só na coluna do fato) e com "@pos" =
    [T1 · Obras · posição]: a ordem da mais à menos crítica de todas as telas (mais pontos perdidos, menor nota, nome;
    contrato da camada comum §3). Quem lista ordena por [@pos] e nunca recalcula a regra."""
    return f"""CALCULATETABLE (
        ADDCOLUMNS (
            FILTER ( VALUES ( dObra[Obra] ), [Obras com análise] > 0 ),
            {colunas},
            "@pos", [T1 · Obras · posição]
        ),
        REMOVEFILTERS ( dMes ),
        dMes[Mes] = _mes
    )"""


def sequencia(valor: str, cond: str, descricao: str, nome: str, pasta: str, oraculo: str = "") -> None:
    """Primeiro mês da sequência que termina no mês de referência em que `cond` (sobre [@v]; _vRef = o valor no mês de
    referência) vale sem interrupção; mês sem valor interrompe. Vazio quando a condição não vale no mês de
    referência."""
    m(nome, pasta, DATA, descricao,
      f"""{JANELA_VARS}
VAR _meses = ADDCOLUMNS ( {MESES_ATE_REF}, "@v", {valor} )
VAR _vRef = MAXX ( FILTER ( _meses, dMes[Mes] = _ref ), [@v] )
VAR _vale = ADDCOLUMNS ( _meses, "@ok", IF ( NOT ISBLANK ( [@v] ) && {cond}, 1, 0 ) )
VAR _noRef = MAXX ( FILTER ( _vale, dMes[Mes] = _ref ), [@ok] ) = 1
VAR _quebra = MAXX ( FILTER ( _vale, [@ok] = 0 ), dMes[Mes] )
VAR _inicio = MINX ( FILTER ( _vale, ISBLANK ( _quebra ) || dMes[Mes] > _quebra ), dMes[Mes] )
RETURN
    IF ( _noRef, _inicio )""", oraculo)


# ===================================================================================================== comum
m("T4 · Primeiro mês com aba", COM, DATA,
  "Primeiro mês da janela ([Série · primeiro mês] ao de referência) em que o recorte do contexto (carteira do drawer "
  "ou uma obra) tem aba na Análise Crítica. É o começo das comparações 'desde janeiro' das leituras.",
  f"""{JANELA_VARS}
RETURN
    MINX ( FILTER ( {MESES_ATE_REF}, CALCULATE ( [Obras com análise] ) > 0 ), dMes[Mes] )""",
  "carteira.serie[0].mes (2026-01-01) · TIROL: obras[].serie[0].mes (2026-03-01)")
m("T4 · Meses com aba", COM, INT,
  "Meses da janela, até o de referência, em que o recorte do contexto tem aba (6 na carteira em jun/26; 4 na "
  "TIROL; 8 em ago/26 com a janela de 12).",
  f"""{JANELA_VARS}
RETURN
    COUNTROWS ( FILTER ( {MESES_ATE_REF}, CALCULATE ( [Obras com análise] ) > 0 ) ) + 0""",
  "len(carteira.serie) · len(obras[].serie)")
# Faixas de dois itens da nota que a T4 desenha (régua antiga, Fase 2, 13/10/2026): o nível sai dos pontos do item contra o
# máximo possível — nenhum limite da nota aqui (eles ficam no dicionário NOTA de contas_base.py). 0 = pontos cheios, 1 =
# parte dos pontos, 2 = nenhum ponto (a faixa crítica). Uma obra no contexto; vazio sem dado.
m("T4 · Desembolso · faixa do fluxo de caixa", COM, INT,
  "Faixa da previsão de caixa da nota em que a obra caiu no mês do contexto, pelos pontos do item: 0 com os pontos "
  "cheios, 1 com parte deles, 2 sem ponto (a faixa crítica: o desembolso fugiu do previsto para mais ou para menos). "
  "Vazio sem previsto ou com mais de uma obra no contexto.",
  """VAR _x = [Nota · X caixa]
VAR _p = [Nota · pontos caixa]
VAR _max = [Nota · possíveis · caixa]
RETURN
    IF ( NOT ISBLANK ( _x ) && NOT ISBLANK ( _p ), SWITCH ( TRUE (), _p >= _max, 0, _p = 0, 2, 1 ) )""",
  "ago/26 (bases de teste): POTENGI e JANGADA 2 (−21% e −31%) · REDINHA e CAJUEIRO 1 · DUNAS e TIROL 0")
ref("T4 · Desembolso · faixa do fluxo de caixa · ref", "T4 · Desembolso · faixa do fluxo de caixa", COM, INT,
    "ago/26: POTENGI 2 · REDINHA 1 · TIROL 0")
# rótulos curtos das faixas do fluxo de caixa para o verso do cartão e as leituras, montados das constantes comuns do
# nota (geradas do dicionário em contas_base.py): nenhum limite é reescrito aqui. "> 20%|10% a 20%|< 10%", da faixa
# crítica (sem ponto) para a de pontos cheios; o X está em módulo (para mais ou para menos).
PCT_ROT = ('IF ( ROUND ( {v} * 100, 2 ) = ROUND ( {v} * 100, 0 ), FORMAT ( {v} * 100, "0" ), '
           'FORMAT ( {v} * 100, "0.0#", "pt-BR" ) ) & "%"')
m("T4 · Desembolso · faixas do fluxo de caixa (lista)", COM, TXT,
  "Rótulos curtos das faixas da previsão de caixa da nota, da faixa crítica (sem ponto) para a de pontos cheios, "
  "separados por '|' ('> 20%|10% a 20%|< 10%'), montados das constantes 'Nota · limite caixa · ponto inteiro' "
  "e '· meio ponto'. O desvio conta em módulo: o verso diz 'para mais ou para menos'.",
  f"""VAR _inteiro = [Nota · limite caixa · ponto inteiro]
VAR _meio = [Nota · limite caixa · meio ponto]
VAR _tInteiro = {PCT_ROT.format(v="_inteiro")}
VAR _tMeio = {PCT_ROT.format(v="_meio")}
RETURN
    IF (
        NOT ISBLANK ( _inteiro ) && NOT ISBLANK ( _meio ),
        "> " & _tMeio & "|" & _tInteiro & " a " & _tMeio & "|< " & _tInteiro
    )""", "> 20%|10% a 20%|< 10%")
m("T4 · Desembolso · limite da faixa crítica", COM, TXT,
  "Limite da faixa crítica da previsão de caixa da Nota da obra, como texto ('20%'), da constante 'Nota · limite caixa · "
  "meio ponto' (acima dele, nenhum ponto). As leituras dizem 'mais de 20%, para mais ou para menos'.",
  f"""VAR _meio = [Nota · limite caixa · meio ponto]
RETURN
    IF ( NOT ISBLANK ( _meio ), {PCT_ROT.format(v="_meio")} )""", "20%")
m("T4 · Por obra · faixa do custo", COM, INT,
  "Faixa do custo (IDC) da Nota da obra em que a obra caiu no mês do contexto, pelos pontos do item: 0 com os pontos "
  "cheios, 1 com parte deles, 2 sem ponto. Vazio sem dado ou com mais de uma obra no contexto.",
  """VAR _x = [Nota · X custo]
VAR _p = [Nota · pontos custo]
VAR _max = [Nota · possíveis · custo]
RETURN
    IF ( NOT ISBLANK ( _x ) && NOT ISBLANK ( _p ), SWITCH ( TRUE (), _p >= _max, 0, _p = 0, 2, 1 ) )""",
  "ago/26: DUNAS (3,0), JANGADA (3,5) e REDINHA (4,0) 1 · CAJUEIRO, POTENGI e TIROL 0")
ref("T4 · Por obra · faixa do custo · ref", "T4 · Por obra · faixa do custo", COM, INT,
    "ago/26: DUNAS 1 · CAJUEIRO 0")
m("T4 · Por obra · máximo do custo", COM, NUM,
  "Pontos máximos do item custo (IDC) na Nota da obra (lido de dItemNota): o verso do cartão Resultado diz quanto o "
  "custo vale na nota de cada obra.",
  """CALCULATE ( [Nota · item · máximo], dItemNota[Item] = "custo" )""", "3")
m("T4 · Obra · artigo", COM, TXT,
  "Artigo do nome da obra nas frases ('a CAJUEIRO', 'o JANGADA'). O cadastro não traz o gênero; JANGADA é o único "
  "masculino das obras em andamento (a confirmar com a Construtora).",
  """VAR _obra = SELECTEDVALUE ( dObra[Obra] )
RETURN
    IF ( _obra IN { "JANGADA" }, "o", "a" )""")

# ===================================================================================================== F3: aplicado e IDC
def mes_anterior(base_: str) -> str:
    """[base_] no mês anterior ao do contexto (o mês do eixo ou o de referência, pela tabela de meses)."""
    return f"""VAR _mes = EDATE ( MAX ( dMes[Mes] ), -1 )
RETURN
    CALCULATE ( [{base_}], REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )"""


def variacao_mesmas_obras(base_: str) -> str:
    """[base_] do mês menos o do mês anterior só com as obras que têm valor nos dois meses (a regra de 'Resultado ·
    variação no mês': somar meses com conjuntos de obras diferentes mistura a obra que abre a aba com variação)."""
    return f"""VAR _mesAnt = EDATE ( MAX ( dMes[Mes] ), -1 )
VAR _comp =
    FILTER (
        VALUES ( fAnaliseCritica[Obra] ),
        NOT ISBLANK ( [{base_}] )
            && NOT ISBLANK ( CALCULATE ( [{base_}], REMOVEFILTERS ( dMes ), dMes[Mes] = _mesAnt ) )
    )
RETURN
    IF (
        NOT ISEMPTY ( _comp ),
        SUMX ( _comp, [{base_}] - CALCULATE ( [{base_}], REMOVEFILTERS ( dMes ), dMes[Mes] = _mesAnt ) )
    )"""


m("T4 · Resultado aplicado · variação no mês", COM, RS,
  "Resultado aplicado do mês menos o do mês anterior, só das obras com aba nos dois meses (vazio sem nenhuma).",
  variacao_mesmas_obras("Resultado aplicado"), "resultado aplicado de cada obra, mês − mês anterior")
m("T4 · A realizar · variação no mês", COM, RS,
  "O que falta realizar (planilha − aplicado) no mês menos o do mês anterior, só das obras com aba nos dois meses.",
  variacao_mesmas_obras("A realizar"))
m("T4 · A realizar · mês anterior", COM, RS,
  "O que ainda vai se realizar (resultado da planilha − resultado aplicado) no mês anterior ao do contexto.",
  mes_anterior("A realizar"))
m("T4 · IDC · mês anterior", COM, "0.000", "IDC do recorte no mês anterior ao do contexto (na carteira, soma ÷ soma).",
  mes_anterior("IDC"), "nota_previa.csv x_idc do mês anterior (por obra)")
m("T4 · IDC · variação no mês", COM, "+0.00;-0.00;0.00",
  "IDC do mês menos o do mês anterior, arredondados em 2 casas como a tela mostra (vazio sem um dos dois).",
  """VAR _a = [IDC]
VAR _b = [T4 · IDC · mês anterior]
RETURN
    IF ( NOT ISBLANK ( _a ) && NOT ISBLANK ( _b ), ROUND ( _a, 2 ) - ROUND ( _b, 2 ) )""",
  "nota_previa.csv: x_idc set/26 − ago/26, em 2 casas")
for _b, _fmt in (("T4 · IDC · variação no mês", "+0.00;-0.00;0.00"), ("T4 · Resultado aplicado · variação no mês", RS)):
    ref(_b + " · ref", _b, COM, _fmt)


# ===================================================================================================== cartões
m("T4 · Cartões · mês anterior", CART, DATA,
  "Mês anterior ao de referência (primeiro dia), também quando fica antes do histórico (dez/25 para jan/26): o "
  "cartão 'Mês anterior' lê a aba anterior de cada planilha.",
  "EDATE ( [Mês de referência], -1 )", "carteira.serie[-2].mes (2026-05-01)")
# a lista das obras em branco do cartão Justificativas do mês é a Recorte · justificativas em branco (lista) · ref
# (tooltips_t1.py), e o "e mais M" é a Recorte · justificativas em branco fora da lista curta · ref

# ===================================================================================================== mês a mês
# F3 (docs/08 §5): uma série só, o resultado aplicado (barra), com o resultado da planilha como traço sobre a coluna
# (a distância entre os dois é o que ainda vai se realizar). A escala cobre os dois.
m("T4 · Mês a mês · topo da escala", MES, RS,
  "Maior valor entre o resultado aplicado e o resultado da planilha nos meses da janela (zero quando todos são "
  "negativos): o topo da escala das colunas do painel Resultado da carteira, mês a mês.",
  f"""{JANELA_VARS}
VAR _meses = ADDCOLUMNS ( {MESES_ATE_REF}, "@a", [Resultado aplicado], "@r", [Resultado da obra] )
RETURN
    MAX ( 0, MAX ( MAXX ( _meses, [@a] ), MAXX ( _meses, [@r] ) ) )""",
  "max(resultado aplicado, resultado da planilha, 0) da carteira na janela")
m("T4 · Mês a mês · base da escala", MES, RS,
  "Menor valor entre o resultado aplicado e o resultado da planilha nos meses da janela (zero quando todos são "
  "positivos): a base da escala das colunas.",
  f"""{JANELA_VARS}
VAR _meses = ADDCOLUMNS ( {MESES_ATE_REF}, "@a", [Resultado aplicado], "@r", [Resultado da obra] )
RETURN
    MIN ( 0, MIN ( MINX ( _meses, [@a] ), MINX ( _meses, [@r] ) ) )""",
  "min(resultado aplicado, resultado da planilha, 0) da carteira na janela")
for base_, serie_, orac_mx, orac_mn in (
        ("Resultado aplicado", "aplicado", "mês do maior resultado aplicado da carteira", "mês do menor"),):
    for nome, ordem, orac in (("maior", "DESC", orac_mx), ("menor", "ASC", orac_mn)):
        m(f"T4 · Mês a mês · mês do {nome} {serie_}", MES, DATA,
          f"Mês da janela com o {nome} [{base_}] do recorte (empate: o mais recente). Com 9 meses ou mais na janela, "
          "o painel só escreve o valor no mês de referência e nos meses de máximo e mínimo de cada série.",
          f"""{JANELA_VARS}
VAR _meses = FILTER ( ADDCOLUMNS ( {MESES_JANELA}, "@v", [{base_}] ), NOT ISBLANK ( [@v] ) )
RETURN
    MAXX ( TOPN ( 1, _meses, [@v], {ordem}, dMes[Mes], DESC ), dMes[Mes] )""", orac)

# ===================================================================================================== por obra
m("T4 · Por obra · maior resultado % absoluto", OBRA, PCT,
  "Maior |resultado % do orçamento| entre as obras do recorte e os meses da janela: a escala vertical comum "
  "das linhas de tendência. Ignora a linha do visual (uma obra) e respeita o drawer.",
  f"""{JANELA_VARS}
VAR _pares =
    CALCULATETABLE (
        ADDCOLUMNS ( SUMMARIZE ( {F}, {F}[Obra], {F}[Mes] ), "@p", [Resultado %] ),
        REMOVEFILTERS ( dMes ),
        dMes[Mes] >= _ini && dMes[Mes] <= _ref,
        ALLSELECTED ( dObra )
    )
RETURN
    MAXX ( _pares, ABS ( [@p] ) )""", "max |obras[].serie[].resultado_pct| = 2,30% (DUNAS jun)")

# ===================================================================================================== desembolso da carteira
m("T4 · Desembolso · topo da escala", DESC, RS,
  "Maior valor entre o previsto e o desembolsado do mês nos meses da janela: o topo da escala das colunas.",
  f"""{JANELA_VARS}
VAR _meses =
    ADDCOLUMNS ( {MESES_ATE_REF}, "@p", [Desembolso · previsto no mês], "@d", [Desembolso · realizado no mês] )
RETURN
    MAX ( MAXX ( _meses, [@p] ), MAXX ( _meses, [@d] ) )""", "max(carteira.serie[].desembolsado_mes_rs) = 6.206.432,30")

# regra "sem previsto" no desembolso da carteira (defeito achado no redesenho v2, 07/10/2026: em jun/26 o desvio da
# carteira somava o desembolsado da TIROL, que não tinha previsto, e dava +34% em vez de +26%): o previsto e o desvio
# da carteira só contam as obras que têm previsto no mês. Na obra, igual ao desvio da obra.
m("T4 · Desembolso · realizado com previsto no mês", DESC, RS,
  "Desembolsado no mês só das obras do contexto que têm previsto no mês (regra 'sem previsto': a obra sem previsto "
  "fica fora do previsto e do desvio da carteira). Igual ao desembolsado quando todas têm previsto.",
  f"""SUMX (
    VALUES ( {F}[Obra] ),
    IF ( NOT ISBLANK ( [Desembolso · previsto no mês] ), [Desembolso · realizado no mês] )
)""", "jun/26 real: R$ 4,90 mi (sem os R$ 296 mil da TIROL, sem previsto) · ago/26: R$ 5,10 mi")
m("T4 · Desembolso · desvio no mês · com previsto", DESC, PCT,
  "Desvio do desembolso do mês sobre o previsto só com as obras que têm previsto: desembolsado dessas obras ÷ previsto "
  "− 1 (vazio sem previsto). Na obra, igual a [Desembolso · desvio no mês].",
  """VAR _prev = [Desembolso · previsto no mês]
VAR _real = [T4 · Desembolso · realizado com previsto no mês]
RETURN
    IF ( NOT ISBLANK ( _prev ) && NOT ISBLANK ( _real ), DIVIDE ( _real, _prev ) - 1 )""",
  "jun/26 real: 4,90 ÷ 3,88 − 1 = +26% (era +34% com a TIROL) · ago/26: 0%")
ref("T4 · Desembolso · desvio no mês · com previsto · ref", "T4 · Desembolso · desvio no mês · com previsto", DESC, PCT,
    "ago/26 real: 0%")

# ===================================================================================================== desembolso por obra
m("T4 · Desembolso por obra · aba do mês", DOB, TXT,
  "Nome da aba do mês de referência quando todas as obras do recorte usam o mesmo (JUN26); vazio quando divergem "
  "(MAIO26 × MAI26), e o cabeçalho diz 'aba do mês'.",
  f"""VAR _mes = [Mês de referência]
VAR _abas = CALCULATETABLE ( VALUES ( {F}[Aba] ), REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )
RETURN
    IF ( COUNTROWS ( _abas ) = 1, MAXX ( _abas, {F}[Aba] ) )""", "obras[].ultimo.aba (JUN26 em todas)")

# ===================================================================================================== tooltips · mês
m("T4 · Ativos não consumidos · mês anterior", TT, RS,
  "Pagos e ainda não aplicados do recorte no mês anterior ao do contexto (o mês sob o mouse).",
  """VAR _mes = EDATE ( MAX ( dMes[Mes] ), -1 )
RETURN
    CALCULATE ( [Ativos não consumidos], REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )""",
  "carteira.serie[m−1].ativos_nao_consumidos (mai/26: 2.620.953)")
for nome, cond, desc, orac in (
        ("caíram", "[@v] < 0", "com resultado aplicado (R$) menor que o do mês anterior", "contagem no mês"),
        ("subiram", "[@v] > 0", "com resultado aplicado (R$) maior que o do mês anterior", "contagem no mês")):
    m(f"T4 · Obras que {nome} no mês", TT, INT,
      f"Obras do recorte {desc}, no mês do contexto.",
      f"""VAR _obras = ADDCOLUMNS ( VALUES ( {F}[Obra] ), "@v", [T4 · Resultado aplicado · variação no mês] )
RETURN
    COUNTROWS ( FILTER ( _obras, {cond} ) ) + 0""", f"sinal do resultado aplicado − o do mês anterior ({orac})")
    m(f"T4 · Obras que {nome} no mês (lista)", TT, TXT,
      f"Nomes das obras {desc}, no mês do contexto, em ordem alfabética, separados por '|'.",
      f"""VAR _obras = ADDCOLUMNS ( VALUES ( {F}[Obra] ), "@v", [T4 · Resultado aplicado · variação no mês] )
RETURN
    CONCATENATEX ( FILTER ( _obras, {cond} ), {F}[Obra], "|", {F}[Obra], ASC )""", orac)
m("T4 · Obras comparáveis no mês", TT, INT,
  "Obras do recorte com aba no mês do contexto e na aba anterior (a base de 'caiu em cinco das sete').",
  f"""COUNTROWS ( FILTER ( VALUES ( {F}[Obra] ), NOT ISBLANK ( [T4 · Resultado aplicado · variação no mês] ) ) ) + 0""",
  "7 em jun/26")
# listas de uma obra por linha nos tooltips de mês: até 10 obras todas aparecem; de 11 em diante, as 9 de maior peso e
# a linha "e mais N obras" (mesma regra dos tooltips da T1, tooltips_t1.LISTA_MAX / LISTA_MOSTRA)
LISTA_MAX, LISTA_MOSTRA = 10, 9
for nome, cond, oq, linha in (
        ("T4 · Tooltip mês · obras fora da lista", "NOT ISBLANK ( [Resultado aplicado] )", "com resultado no mês",
         "e mais N obras, com resultado mais perto de zero"),
        ("T4 · Tooltip mês do desembolso · obras fora da lista", "[Obras com análise] > 0", "com aba no mês",
         "e mais N obras, com desvio mais perto de zero")):
    m(nome, TT, INT,
      f"Obras do recorte {oq} (as linhas do tooltip) que não cabem na lista: vazio com até {LISTA_MAX} obras (todas "
      f"aparecem); com mais, as que passam das {LISTA_MOSTRA} mostradas (o N da linha '{linha}').",
      f"""VAR _n = COUNTROWS ( FILTER ( VALUES ( dObra[Obra] ), {cond} ) )
RETURN
    IF ( _n > {LISTA_MAX}, _n - {LISTA_MOSTRA} )""", f"vazio com até {LISTA_MAX} obras (jun/26: vazio)")
m("T4 · Obras com resultado negativo", TT, INT,
  "Obras do recorte com resultado aplicado negativo no mês do contexto.",
  f"""COUNTROWS ( FILTER ( VALUES ( {F}[Obra] ), [Resultado aplicado] < 0 ) ) + 0""",
  "obras[].serie[m].resultado < 0 (jun/26: 2 · jan/26: 0)")

# ===================================================================================================== tooltips · desembolso do mês
m("T4 · Justificativas em branco no mês (lista)", TT, TXT,
  "Obras do recorte com justificativa exigida e em branco no mês do contexto, do maior para o menor |desvio| do "
  "desembolso (empate: ordem alfabética), separadas por '|'. O rodapé do tooltip escreve quantas couberem numa linha.",
  f"""VAR _obras =
    ADDCOLUMNS (
        VALUES ( {F}[Obra] ),
        "@b", [Justificativa · em branco],
        "@d", ABS ( [Desembolso · desvio no mês] )
    )
RETURN
    CONCATENATEX ( FILTER ( _obras, [@b] = 1 ), {F}[Obra], "|", [@d], DESC, {F}[Obra], ASC )""",
  "obras[].serie[m] com |desvio| > 10% e justificativa vazia (jun e jan/26: CAJUEIRO · ago/26 real: "
  "JANGADA|POTENGI|REDINHA|CAJUEIRO)")
# rodapé de uma linha (justificativas_rodape.py): os RODAPE_NOMES primeiros nomes e "e mais M" quando os nomes não cabem
m("T4 · Tooltip mês do desembolso · em branco fora do rodapé", TT, INT,
  f"Justificativas exigidas e em branco no mês do contexto além das {RODAPE_NOMES} primeiras obras da lista (o M de "
  f"'em branco: A, B e mais M' no rodapé do tooltip); vazio com até {RODAPE_NOMES} em branco.",
  f"""VAR _n = [Carteira · justificativas em branco] + 0
RETURN
    IF ( _n > {RODAPE_NOMES}, _n - {RODAPE_NOMES} )""",
  "ago/26 real: 2 (4 em branco) · jun/26: vazio (1 em branco)")
m("T4 · Desembolso · status · mês anterior", TT, INT,
  "Faixa da previsão de caixa da nota (0/1/2, 'T4 · Desembolso · faixa do fluxo de caixa') da obra na aba anterior ao mês "
  "do contexto.",
  """VAR _mes = EDATE ( MAX ( dMes[Mes] ), -1 )
RETURN
    CALCULATE ( [T4 · Desembolso · faixa do fluxo de caixa], REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )""",
  "faixa do fluxo de caixa da obra no mês anterior")
m("T4 · Desembolso · desvio · mês anterior", TT, PCT,
  "Desembolsado ÷ previsto − 1 da obra no mês anterior ao do contexto.",
  """VAR _mes = EDATE ( MAX ( dMes[Mes] ), -1 )
RETURN
    CALCULATE ( [Desembolso · desvio no mês], REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )""",
  "obras[].serie[m−1].indicadores.desvio_desembolso (JANGADA mai/26: +53%)")
# faixa crítica do desembolso = sem ponto na previsão de caixa da nota (o desvio passou do limite para mais ou para menos)
for nome, cond, orac in (("saíram da faixa crítica", "[@a] = 2 && NOT ISBLANK ( [@s] ) && [@s] < 2", "ago/26 (teste)"),
                         ("entraram na faixa crítica", "[@s] = 2 && NOT ISBLANK ( [@a] ) && [@a] < 2", "ago/26 (teste)")):
    m(f"T4 · Desembolso · {nome} (lista)", TT, TXT,
      f"Obras do recorte que {nome} da previsão de caixa da nota (sem ponto: desvio fora do limite, para mais ou para "
      "menos) no mês do contexto, em relação ao mês anterior; ordem alfabética, separadas por '|'.",
      """VAR _obras =
    ADDCOLUMNS (
        FILTER ( VALUES ( dObra[Obra] ), [Obras com análise] > 0 ),
        "@s", [T4 · Desembolso · faixa do fluxo de caixa],
        "@a", [T4 · Desembolso · status · mês anterior]
    )
RETURN
    CONCATENATEX ( FILTER ( _obras, """ + cond + """ ), dObra[Obra], "|", dObra[Obra], ASC )""", orac)
m("T4 · Desembolso · seguem na faixa crítica", TT, INT,
  "Obras do recorte na faixa crítica da previsão de caixa da nota (sem ponto) no mês do contexto e no anterior.",
  """VAR _obras =
    ADDCOLUMNS (
        FILTER ( VALUES ( dObra[Obra] ), [Obras com análise] > 0 ),
        "@s", [T4 · Desembolso · faixa do fluxo de caixa],
        "@a", [T4 · Desembolso · status · mês anterior]
    )
RETURN
    COUNTROWS ( FILTER ( _obras, [@s] = 2 && [@a] = 2 ) ) + 0""", "ago/26 (teste)")

# ===================================================================================================== tooltips · obra
m("T4 · Resultado % · melhor mês", TT, DATA,
  "Mês da janela, até o de referência, com o maior resultado % do orçamento (empate: o primeiro).",
  f"""{JANELA_VARS}
VAR _meses = FILTER ( ADDCOLUMNS ( {MESES_ATE_REF}, "@p", [Resultado %] ), NOT ISBLANK ( [@p] ) )
VAR _max = MAXX ( _meses, [@p] )
RETURN
    MINX ( FILTER ( _meses, [@p] = _max ), dMes[Mes] )""", "argmax obras[].serie[].resultado_pct (REDINHA: jan/26)")
m("T4 · Sem estoque · meses negativos", TT, INT,
  "Meses da janela, até o de referência, com o resultado sem estoque e adiantamentos negativo (obra ou carteira do contexto).",
  f"""{JANELA_VARS}
VAR _meses = ADDCOLUMNS ( {MESES_ATE_REF}, "@v", [Resultado sem ativos] )
RETURN
    COUNTROWS ( FILTER ( _meses, NOT ISBLANK ( [@v] ) && [@v] < 0 ) ) + 0""",
  "serie[].resultado_sem_ativos < 0 (REDINHA e carteira: 6)")
sequencia("[Resultado sem ativos]", "( [@v] < 0 ) = ( _vRef < 0 )",
          "Primeiro mês da sequência, na janela e até o de referência, em que o resultado sem estoque tem o mesmo sinal do mês de "
          "referência ('negativo desde abril').", "T4 · Sem estoque · sequência · início", TT,
          "serie[].resultado_sem_ativos (CAJUEIRO: abr/26)")
m("T4 · Obra · justificativas exigidas no período", TT, INT,
  "Meses da janela, até o de referência, em que a obra passou de ±10% de desvio no desembolso (justificativa exigida).",
  f"""{JANELA_VARS}
RETURN
    SUMX ( {MESES_ATE_REF}, [Justificativa · exigida] ) + 0""",
  "obras[].serie[] com |desvio_desembolso| > 10% (REDINHA 6 · CAJUEIRO 4 · DUNAS 0)")
m("T4 · Obra · justificativas em branco no período", TT, INT,
  "Meses da janela, até o de referência, com a justificativa exigida e o campo da planilha vazio.",
  f"""{JANELA_VARS}
RETURN
    SUMX ( {MESES_ATE_REF}, [Justificativa · em branco] ) + 0""",
  "obras[].serie[] exigida e sem texto (CAJUEIRO 4)")
m("T4 · Obra · justificativas preenchidas no período", TT, INT,
  "Meses da janela, até o de referência, com a justificativa exigida e preenchida.",
  "[T4 · Obra · justificativas exigidas no período] - [T4 · Obra · justificativas em branco no período]",
  "REDINHA 6 de 6 · POTENGI 4 de 4 · CAJUEIRO 0 de 4")
m("T4 · Obra · meses seguidos em branco", TT, INT,
  "Quantos meses seguidos da janela, terminando no de referência, a obra deixou a justificativa exigida em branco.",
  f"""{JANELA_VARS}
VAR _meses = ADDCOLUMNS ( {MESES_ATE_REF}, "@b", [Justificativa · em branco] )
VAR _quebra = MAXX ( FILTER ( _meses, [@b] <> 1 ), dMes[Mes] )
RETURN
    COUNTROWS ( FILTER ( _meses, ISBLANK ( _quebra ) || dMes[Mes] > _quebra ) ) + 0""",
  "CAJUEIRO: abr, mai e jun/26 = 3")
sequencia("[T4 · Desembolso · faixa do fluxo de caixa]", "[@v] = 2",
          "Primeiro mês da sequência, na janela e terminando no de referência, em que o desembolso da obra está na faixa crítica "
          "da previsão de caixa da nota (sem ponto, para mais ou para menos); vazio fora dela.",
          "T4 · Obra · faixa crítica do desembolso · início", TT, "ago/26 (teste)")
sequencia("[Desembolso · desvio no mês]", "[@v] < 0",
          "Primeiro mês da sequência, na janela e terminando no de referência, em que a obra desembolsou abaixo do previsto; vazio "
          "fora dela.", "T4 · Obra · abaixo do previsto · início", TT,
          "obras[].serie[].indicadores.desvio_desembolso (DUNAS: mar/26)")
m("T4 · Variação · sequência · início", TT, DATA,
  "Primeiro mês da sequência, na janela e terminando no de referência, em que a variação do resultado (p.p.) tem o "
  "mesmo sinal da do mês de referência ('cai desde abril'). A variação é a da planilha (aba do mês × aba anterior), "
  "conta de mês anterior: o primeiro mês da janela entra com a sua. Uma obra no contexto.",
  f"""{JANELA_VARS}
VAR _v = [Resultado · variação p.p. · ref]
VAR _sinal = SIGN ( ROUND ( _v, 2 ) )
VAR _meses =
    ADDCOLUMNS (
        {MESES_JANELA},
        "@s", SIGN ( ROUND ( [Resultado · variação p.p.], 2 ) ),
        "@tem", NOT ISBLANK ( [Resultado · variação p.p.] )
    )
VAR _quebra = MAXX ( FILTER ( _meses, [@s] <> _sinal || NOT [@tem] ), dMes[Mes] )
VAR _inicio = MINX ( FILTER ( _meses, ISBLANK ( _quebra ) || dMes[Mes] > _quebra ), dMes[Mes] )
RETURN
    IF ( NOT ISBLANK ( _v ) && _sinal <> 0, _inicio )""", "texto 'cai desde abril' do tooltip de obra (REDINHA jun/26)")
# Resumo das justificativas antes dos 6 meses mais recentes (o tooltip da obra do desembolso lista os 6 últimos meses
# da janela, um por linha; os anteriores da janela viram uma linha de resumo).
RESUMO = f"""{JANELA_VARS}
VAR _corte = EDATE ( _ref, -5 )
VAR _meses =
    FILTER (
        ADDCOLUMNS ( FILTER ( ALL ( dMes[Mes] ), dMes[Mes] >= _ini && dMes[Mes] < _corte ), "@tem", [Obras com análise] ),
        [@tem] > 0
    )
RETURN
    """
for nome, fmt, ret, desc, orac in (
        ("primeiro mês", DATA, "MINX ( _meses, dMes[Mes] )", "Primeiro mês com aba", "CAJUEIRO ago/26 · janela 12: jan/26"),
        ("último mês", DATA, "MAXX ( _meses, dMes[Mes] )", "Último mês com aba", "fev/26"),
        ("meses", INT, "COUNTROWS ( _meses ) + 0", "Meses com aba", "2"),
        ("exigidas", INT, "SUMX ( _meses, [Justificativa · exigida] ) + 0", "Justificativas exigidas (±10%)", "1 (jan)"),
        ("em branco", INT, "SUMX ( _meses, [Justificativa · em branco] ) + 0", "Justificativas exigidas e em branco",
         "1 (jan)"),
        ("não exigidas", INT, "COUNTROWS ( FILTER ( _meses, [Justificativa · exigida] = 0 ) ) + 0",
         "Meses dentro de ±10% (justificativa não exigida)", "1 (fev)")):
    m(f"T4 · Obra · resumo das justificativas · {nome}", TT, fmt,
      f"{desc} da obra nos meses da janela anteriores aos 6 mais recentes (a linha de resumo do tooltip da obra do "
      "desembolso); vazio ou zero quando a janela tem 6 meses ou menos.", RESUMO + ret, orac)
m("T4 · Obra · resumo das justificativas · preenchidas", TT, INT,
  "Justificativas exigidas e preenchidas da obra nos meses da janela anteriores aos 6 mais recentes.",
  "[T4 · Obra · resumo das justificativas · exigidas] - [T4 · Obra · resumo das justificativas · em branco]", "0 (jan)")

# ===================================================================================================== leituras · 4.1 mês a mês
# Comparações mês a mês da carteira usam só as obras com aba no mês e na anterior (a regra de 'Resultado · variação no
# mês', em base/). Somar o resultado de todas as obras de um mês contra o de outro, com menos obras com aba, mistura
# conjuntos diferentes (a obra que abre a aba entra inteira como "variação"). Uma obra no contexto: igual a antes.
m("T4 · Ativos não consumidos · variação no mês", COM, RS,
  "Pagos e não aplicados do mês menos os do mês anterior, em R$, só das obras com aba no mês e na anterior e com "
  "pagos e não aplicados nos dois (vazio sem nenhuma; jan/26 fica vazio, sem dezembro de ativos no modelo).",
  """VAR _mesAnt = EDATE ( MAX ( dMes[Mes] ), -1 )
VAR _comp =
    FILTER (
        VALUES ( fAnaliseCritica[Obra] ),
        NOT ISBLANK ( [Resultado · mês anterior] )
            && NOT ISBLANK ( CALCULATE ( [Ativos não consumidos], REMOVEFILTERS ( dMes ), dMes[Mes] = _mesAnt ) )
    )
RETURN
    IF (
        NOT ISEMPTY ( _comp ),
        SUMX (
            _comp,
            [Ativos não consumidos] - CALCULATE ( [Ativos não consumidos], REMOVEFILTERS ( dMes ), dMes[Mes] = _mesAnt )
        )
    )""", "obras[].serie[m].ativos_nao_consumidos − serie[m−1], só as obras com aba nos dois meses")
m("T4 · Desembolso · desvio · variação no mês", COM, PCT,
  "Desvio do desembolso do mês menos o do mês anterior, em fração (0,01 = 1 p.p.), só das obras com previsto nos dois "
  "meses (vazio sem nenhuma).",
  """VAR _mesAnt = EDATE ( MAX ( dMes[Mes] ), -1 )
VAR _comp =
    FILTER (
        VALUES ( fAnaliseCritica[Obra] ),
        NOT ISBLANK ( [Desembolso · previsto no mês] )
            && NOT ISBLANK ( CALCULATE ( [Desembolso · previsto no mês], REMOVEFILTERS ( dMes ), dMes[Mes] = _mesAnt ) )
    )
VAR _razaoMes =
    DIVIDE ( SUMX ( _comp, [Desembolso · realizado no mês] ), SUMX ( _comp, [Desembolso · previsto no mês] ) )
VAR _razaoAnt =
    DIVIDE (
        SUMX ( _comp, CALCULATE ( [Desembolso · realizado no mês], REMOVEFILTERS ( dMes ), dMes[Mes] = _mesAnt ) ),
        SUMX ( _comp, CALCULATE ( [Desembolso · previsto no mês], REMOVEFILTERS ( dMes ), dMes[Mes] = _mesAnt ) )
    )
RETURN
    IF ( NOT ISEMPTY ( _comp ) && NOT ISBLANK ( _razaoMes ) && NOT ISBLANK ( _razaoAnt ), _razaoMes - _razaoAnt )""",
  "carteira.serie[m].desvio_desembolso − serie[m−1], só as obras com previsto nos dois meses")
m("T4 · Leitura mês · meses comparáveis", LEI, INT,
  "Meses da janela, depois do primeiro dela e até o de referência, em que a carteira tem obra com aba no mês e na "
  "anterior (a variação existe; 5 em jun/26).",
  f"""{JANELA_VARS}
VAR _meses = ADDCOLUMNS ( {MESES_COMPARA}, "@v", [T4 · Resultado aplicado · variação no mês] )
RETURN
    COUNTROWS ( FILTER ( _meses, NOT ISBLANK ( [@v] ) ) ) + 0""", "len(carteira.serie) − 1")
m("T4 · Leitura mês · meses com queda", LEI, INT,
  "Meses da janela, até o de referência, em que a variação do resultado aplicado da carteira (só as obras com aba no "
  "mês e na anterior) ficou negativa.",
  f"""{JANELA_VARS}
VAR _meses = ADDCOLUMNS ( {MESES_COMPARA}, "@v", [T4 · Resultado aplicado · variação no mês] )
RETURN
    COUNTROWS ( FILTER ( _meses, NOT ISBLANK ( [@v] ) && [@v] < 0 ) ) + 0""",
  "carteira.serie[m].resultado < serie[m−1] mistura obras (mockup: 5 de 5 em jun/26); com as mesmas obras, jun/26: 3 de 5")
m("T4 · Leitura mês · sequência · início", LEI, DATA,
  "Primeiro mês da sequência, na janela e terminando no de referência, em que a variação do resultado aplicado da "
  "carteira (só as obras com aba no mês e na anterior) andou no mesmo sentido do último mês (cai desde / sobe desde).",
  f"""{JANELA_VARS}
VAR _meses = ADDCOLUMNS ( {MESES_COMPARA}, "@v", [T4 · Resultado aplicado · variação no mês] )
VAR _sentidos = ADDCOLUMNS ( _meses, "@s", IF ( ISBLANK ( [@v] ), BLANK (), SIGN ( [@v] ) ) )
VAR _sinal = MAXX ( FILTER ( _sentidos, dMes[Mes] = _ref ), [@s] )
VAR _quebra = MAXX ( FILTER ( _sentidos, ISBLANK ( [@s] ) || [@s] <> _sinal ), dMes[Mes] )
VAR _inicio = MINX ( FILTER ( _sentidos, ISBLANK ( _quebra ) || dMes[Mes] > _quebra ), dMes[Mes] )
RETURN
    IF ( NOT ISBLANK ( _sinal ) && _sinal <> 0, _inicio )""", "carteira.serie[].resultado mistura obras (mockup, jun/26: fev/26); com as mesmas obras, jun/26: desde mai/26")

for base_, nome, orac in (("T4 · Obras que caíram no mês", "T4 · Obras que caíram no mês · ref", "5"),
                          ("T4 · Obras comparáveis no mês", "T4 · Obras comparáveis no mês · ref", "7"),
                          ("T4 · Obras com resultado negativo", "T4 · Obras com resultado negativo · ref", "2")):
    ref(nome, base_, LEI, INT, f"jun/26: {orac}")
primeiro("T4 · Obras com resultado negativo · no primeiro mês", "T4 · Obras com resultado negativo", LEI, INT,
         "jan/26: 0")
primeiro("T4 · Leitura mês · resultado % no primeiro mês", "Resultado aplicado %", LEI, PCT,
         "resultado aplicado % da carteira no primeiro mês da janela")
primeiro("T4 · Leitura mês · ativos no primeiro mês", "Ativos não consumidos", LEI, RS,
         "carteira.serie[0].ativos_nao_consumidos 1.596.194,41")
primeiro("T4 · Leitura mês · sem estoque no primeiro mês", "Resultado sem ativos", LEI, RS,
         "carteira.serie[0].resultado_sem_ativos −15.140,09")
m("T4 · Leitura mês · obras negativas (lista)", LEI, TXT,
  "Obras do recorte com resultado aplicado negativo no mês de referência, da mais para a menos crítica ([T1 · Obras · "
  "posição]: mais pontos perdidos na nota primeiro), separadas por '|'.",
  f"""VAR _mes = [Mês de referência]
VAR _obras = {obras_ref_pos('"@r", [Resultado aplicado]')}
RETURN
    CONCATENATEX ( FILTER ( _obras, [@r] < 0 ), dObra[Obra], "|", [@pos], ASC )""",
  "ago/26 (teste): REDINHA|DUNAS|JANGADA (a ordem da posição)")
m("T4 · Leitura mês · negativas que caíram", LEI, INT,
  "Das obras com aplicado negativo no mês de referência, quantas fecharam abaixo do mês anterior ('pesam cada vez "
  "mais').",
  f"""VAR _mes = [Mês de referência]
VAR _obras = {obras_ref('"@r", [Resultado aplicado], "@v", [T4 · Resultado aplicado · variação no mês]')}
RETURN
    COUNTROWS ( FILTER ( _obras, [@r] < 0 && [@v] < 0 ) ) + 0""", "POTENGI e TIROL caíram: 2")
m("T4 · Leitura mês · alta dos ativos (razão)", LEI, NUM,
  "Pagos e ainda não aplicados no mês de referência ÷ os do primeiro mês com aba (1,83 = 'quase dobrou').",
  "DIVIDE ( [Ativos não consumidos · ref], [T4 · Leitura mês · ativos no primeiro mês] )",
  "carteira.serie[-1] ÷ serie[0] .ativos_nao_consumidos = 2.923.940 ÷ 1.596.194 = 1,83")
m("T4 · Leitura mês · meses com alta dos ativos", LEI, INT,
  "Meses da janela, até o de referência, em que os pagos e não aplicados da carteira subiram sobre o mês anterior (só as "
  "obras com aba nos dois meses).",
  f"""{JANELA_VARS}
VAR _meses = ADDCOLUMNS ( {MESES_COMPARA}, "@v", [T4 · Ativos não consumidos · variação no mês] )
RETURN
    COUNTROWS ( FILTER ( _meses, NOT ISBLANK ( [@v] ) && [@v] > 0 ) ) + 0""",
  "carteira.serie[].ativos_nao_consumidos mistura obras (mockup: 5 de 5 em jun/26); com as mesmas obras, jun/26: 4 de 5")
m("T4 · Leitura mês · ativos · sequência · início", LEI, DATA,
  "Primeiro mês da sequência, na janela e terminando no de referência, em que a variação dos pagos e não aplicados da "
  "carteira (só as obras com aba nos dois meses) andou no mesmo sentido do último mês ('a distância entre as barras "
  "cresce desde março').",
  f"""{JANELA_VARS}
VAR _meses = ADDCOLUMNS ( {MESES_COMPARA}, "@v", [T4 · Ativos não consumidos · variação no mês] )
VAR _sentidos = ADDCOLUMNS ( _meses, "@s", IF ( ISBLANK ( [@v] ), BLANK (), SIGN ( ROUND ( [@v], 0 ) ) ) )
VAR _sinal = MAXX ( FILTER ( _sentidos, dMes[Mes] = _ref ), [@s] )
VAR _quebra = MAXX ( FILTER ( _sentidos, ISBLANK ( [@s] ) || [@s] <> _sinal ), dMes[Mes] )
VAR _inicio = MINX ( FILTER ( _sentidos, ISBLANK ( _quebra ) || dMes[Mes] > _quebra ), dMes[Mes] )
RETURN
    IF ( NOT ISBLANK ( _sinal ) && _sinal <> 0, _inicio )""",
  "carteira.serie[].ativos_nao_consumidos: o oráculo sobe todo mês (fev/26); o modelo cai em fev (Equipamentos "
  "da CAJUEIRO, diferença conhecida) e sobe desde mar/26")

ref("T4 · Ativos não consumidos · mês anterior · ref", "T4 · Ativos não consumidos · mês anterior", LEI, RS,
    "carteira.serie[-2].ativos_nao_consumidos 2.620.953")
m("T4 · Leitura mês · alta dos ativos por obra", LEI, RS,
  "Pagos e não aplicados da obra no mês de referência menos os do seu primeiro mês com aba.",
  """VAR _ini = [T4 · Primeiro mês com aba]
VAR _aIni = CALCULATE ( [Ativos não consumidos], REMOVEFILTERS ( dMes ), dMes[Mes] = _ini )
VAR _aRef = [Ativos não consumidos · ref]
RETURN
    IF ( NOT ISBLANK ( _aRef ), _aRef - _aIni )""",
  "obras[].serie[-1] − serie[0] .ativos_nao_consumidos (CAJUEIRO +908.876 · REDINHA +446.390)")
m("T4 · Leitura mês · obras que puxam os ativos (lista)", LEI, TXT,
  "As duas obras do recorte com a maior alta dos pagos e não aplicados no período, da maior para a menor, "
  "separadas por '|'.",
  """VAR _obras = ADDCOLUMNS ( VALUES ( dObra[Obra] ), "@a", [T4 · Leitura mês · alta dos ativos por obra] )
VAR _altas = FILTER ( _obras, [@a] > 0 )
RETURN
    CONCATENATEX ( TOPN ( 2, _altas, [@a], DESC, dObra[Obra], ASC ), dObra[Obra], "|", [@a], DESC )""",
  "CAJUEIRO|REDINHA")
m("T4 · Leitura mês · obra de maior resultado", LEI, TXT,
  "Obra do recorte com o maior resultado aplicado (R$) no mês de referência.",
  f"""VAR _mes = [Mês de referência]
VAR _obras = {obras_ref('"@r", [Resultado aplicado]')}
RETURN
    MAXX ( TOPN ( 1, _obras, [@r], DESC, {F}[Obra], ASC ), {F}[Obra] )""", "max obras[].ultimo.resultado: DUNAS")

m("T4 · Leitura mês · a realizar · sequência · início", LEI, DATA,
  "Primeiro mês da sequência, na janela e terminando no de referência, em que o que falta realizar da carteira (só as "
  "obras com aba nos dois meses) andou no mesmo sentido do último mês ('a distância entre a barra e o traço cresce "
  "desde março').",
  f"""{JANELA_VARS}
VAR _meses = ADDCOLUMNS ( {MESES_COMPARA}, "@v", [T4 · A realizar · variação no mês] )
VAR _sentidos = ADDCOLUMNS ( _meses, "@s", IF ( ISBLANK ( [@v] ), BLANK (), SIGN ( ROUND ( [@v], 0 ) ) ) )
VAR _sinal = MAXX ( FILTER ( _sentidos, dMes[Mes] = _ref ), [@s] )
VAR _quebra = MAXX ( FILTER ( _sentidos, ISBLANK ( [@s] ) || [@s] <> _sinal ), dMes[Mes] )
VAR _inicio = MINX ( FILTER ( _sentidos, ISBLANK ( _quebra ) || dMes[Mes] > _quebra ), dMes[Mes] )
RETURN
    IF ( NOT ISBLANK ( _sinal ) && _sinal <> 0, _inicio )""")
ref("T4 · A realizar · variação no mês · ref", "T4 · A realizar · variação no mês", LEI, RS)

# ---- leitura de Obras no mês (F3: a tabela única)
m("T4 · Leitura obras · obra de maior queda do IDC", LEI, TXT,
  "Obra do recorte com a maior queda do IDC no mês de referência (empate pelo nome); vazio quando nenhuma caiu.",
  f"""VAR _mes = [Mês de referência]
VAR _obras = {obras_ref_pos('"@v", [T4 · IDC · variação no mês]')}
VAR _caiu = FILTER ( _obras, NOT ISBLANK ( [@v] ) && [@v] < 0 )
RETURN
    MAXX ( TOPN ( 1, _caiu, [@v], ASC, dObra[Obra], ASC ), dObra[Obra] )""", "nota_previa.csv: x_idc set − ago")
m("T4 · Leitura obras · maior queda do IDC", LEI, "+0.00;-0.00;0.00",
  "A queda do IDC da [T4 · Leitura obras · obra de maior queda do IDC] no mês de referência.",
  """VAR _obra = [T4 · Leitura obras · obra de maior queda do IDC]
RETURN
    IF ( NOT ISBLANK ( _obra ), CALCULATE ( [T4 · IDC · variação no mês · ref], dObra[Obra] = _obra ) )""")
m("T4 · Leitura obras · obras com IDC em queda", LEI, INT,
  "Obras do recorte com o IDC menor que o do mês anterior no mês de referência (em 2 casas).",
  f"""VAR _mes = [Mês de referência]
VAR _obras = {obras_ref_pos('"@v", [T4 · IDC · variação no mês]')}
RETURN
    COUNTROWS ( FILTER ( _obras, NOT ISBLANK ( [@v] ) && [@v] < 0 ) ) + 0""")

# ===================================================================================================== leituras · 4.2 por obra
m("T4 · Leitura obra · obras que pioraram", LEI, INT,
  "Obras do recorte com a variação do resultado (p.p. do orçamento) negativa no mês de referência.",
  f"""VAR _mes = [Mês de referência]
VAR _obras = {obras_ref('"@v", ROUND ( [Resultado · variação p.p.], 2 )')}
RETURN
    COUNTROWS ( FILTER ( _obras, [@v] < 0 ) ) + 0""", "obras[].ultimo.indicadores.variacao_resultado_pp < 0: 5")
m("T4 · Leitura obra · obras que melhoraram", LEI, INT,
  "Obras do recorte com a variação do resultado (p.p. do orçamento) positiva no mês de referência.",
  f"""VAR _mes = [Mês de referência]
VAR _obras = {obras_ref('"@v", ROUND ( [Resultado · variação p.p.], 2 )')}
RETURN
    COUNTROWS ( FILTER ( _obras, [@v] > 0 ) ) + 0""", "obras[].ultimo.indicadores.variacao_resultado_pp > 0: 2")
for nome, ordem, orac in (("que mais caiu", "ASC", "CAJUEIRO (−0,49 p.p.)"), ("que mais subiu", "DESC", "DUNAS (+0,04 p.p.)")):
    m(f"T4 · Leitura obra · obra {nome}", LEI, TXT,
      f"Obra do recorte com a variação do resultado (p.p.) {'mais negativa' if ordem == 'ASC' else 'mais positiva'} "
      "no mês de referência.",
      f"""VAR _mes = [Mês de referência]
VAR _obras = {obras_ref('"@v", [Resultado · variação p.p.]')}
VAR _com = FILTER ( _obras, NOT ISBLANK ( [@v] ) )
RETURN
    MAXX ( TOPN ( 1, _com, [@v], {ordem}, {F}[Obra], ASC ), {F}[Obra] )""", orac)
for nome, cond, orac in (("seguem negativas", "[@r] < 0 && NOT ISBLANK ( [@a] ) && [@a] < 0", "POTENGI|TIROL"),
                         ("viraram negativas", "[@r] < 0 && ( ISBLANK ( [@a] ) || [@a] >= 0 )", "vazio em jun/26")):
    m(f"T4 · Leitura obra · {nome} (lista)", LEI, TXT,
      f"Obras do recorte negativas no mês de referência que {'já eram' if 'seguem' in nome else 'não eram'} negativas "
      "na aba anterior, da mais para a menos crítica ([T1 · Obras · posição]), separadas por '|'.",
      f"""VAR _mes = [Mês de referência]
VAR _obras = {obras_ref_pos('"@r", [Resultado da obra], "@a", [Resultado · mês anterior]')}
RETURN
    CONCATENATEX ( FILTER ( _obras, {cond} ), dObra[Obra], "|", [@pos], ASC )""", orac)
primeiro("T4 · Resultado % · no primeiro mês com aba", "Resultado %", LEI, PCT,
         "obras[].serie[0].resultado_pct (TIROL: mar/26)")
m("T4 · Leitura obra · acima do início (lista)", LEI, TXT,
  "Obras do recorte que terminam o período (mês de referência) com resultado % acima do seu primeiro mês com aba, em "
  "ordem alfabética, separadas por '|'.",
  """VAR _obras =
    ADDCOLUMNS (
        VALUES ( dObra[Obra] ),
        "@r", ROUND ( [Resultado % · ref], 4 ),
        "@i", ROUND ( [T4 · Resultado % · no primeiro mês com aba], 4 )
    )
RETURN
    CONCATENATEX ( FILTER ( _obras, NOT ISBLANK ( [@r] ) && [@r] > [@i] ), dObra[Obra], "|", dObra[Obra], ASC )""",
  "obras[].serie[-1].resultado_pct > serie[0]: DUNAS|PONTA NEGRA")
# retiradas que liam a régua antiga (obra em mobilização, físico atrasado e caindo, desembolso consumiu o ganho, obras
# que perdem pontos pela variação): só o nome segue em RETIRADAS, para o gerador apagar o .dax antigo

# ===================================================================================================== leituras · 4.3 desembolso da carteira
m("T4 · Leitura desembolso · meses acima do previsto", LEI, INT,
  "Meses da janela, até o de referência, em que o desembolso da carteira passou do previsto.",
  f"""{JANELA_VARS}
VAR _meses = ADDCOLUMNS ( {MESES_ATE_REF}, "@d", [T4 · Desembolso · desvio no mês · com previsto] )
RETURN
    COUNTROWS ( FILTER ( _meses, NOT ISBLANK ( [@d] ) && [@d] > 0 ) ) + 0""",
  "carteira.serie[].desvio_desembolso > 0: 6")
sequencia("[T4 · Desembolso · desvio no mês · com previsto]", "[@v] > 0",
          "Primeiro mês da sequência, na janela e terminando no de referência, em que a carteira desembolsou acima do previsto; "
          "vazio quando o mês de referência ficou abaixo.", "T4 · Leitura desembolso · acima do previsto desde", LEI,
          "carteira.serie[].desvio_desembolso: jan/26")
m("T4 · Leitura desembolso · desvio · sequência · início", LEI, DATA,
  "Primeiro mês da sequência, na janela e terminando no de referência, em que o desvio do desembolso da carteira (só as "
  "obras com previsto nos dois meses) andou no mesmo sentido do último mês (sobe desde / cai desde).",
  f"""{JANELA_VARS}
VAR _meses = ADDCOLUMNS ( {MESES_COMPARA}, "@v", [T4 · Desembolso · desvio · variação no mês] )
VAR _sentidos = ADDCOLUMNS ( _meses, "@s", IF ( ISBLANK ( [@v] ), BLANK (), SIGN ( ROUND ( [@v], 4 ) ) ) )
VAR _sinal = MAXX ( FILTER ( _sentidos, dMes[Mes] = _ref ), [@s] )
VAR _quebra = MAXX ( FILTER ( _sentidos, ISBLANK ( [@s] ) || [@s] <> _sinal ), dMes[Mes] )
VAR _inicio = MINX ( FILTER ( _sentidos, ISBLANK ( _quebra ) || dMes[Mes] > _quebra ), dMes[Mes] )
RETURN
    IF ( NOT ISBLANK ( _sinal ) && _sinal <> 0, _inicio )""",
  "carteira.serie[].desvio_desembolso 12 · 5 · 6 · 11 · 17 · 19%: mockup sobe desde mar/26; com as mesmas obras, jun/26: desde jun/26")

m("T4 · Leitura desembolso · desvio · variação no mês", LEI, PP,
  "Desvio do desembolso da carteira no mês de referência menos o do mês anterior, em pontos percentuais (> 0: sobe), só "
  "com as obras que têm previsto nos dois meses.",
  """VAR _ref = [Mês de referência]
VAR _v = CALCULATE ( [T4 · Desembolso · desvio · variação no mês], REMOVEFILTERS ( dMes ), dMes[Mes] = _ref )
RETURN
    IF ( NOT ISBLANK ( _v ), _v * 100 )""", "ago/26: desvio −0,3% − 29,9% = −30,2 p.p. (igual ao de antes da regra das mesmas obras)")

m("T4 · Leitura desembolso · obras na faixa crítica (lista)", LEI, TXT,
  "Obras do recorte na faixa crítica da previsão de caixa da nota (sem ponto: o desembolso fugiu do previsto para mais ou "
  "para menos) no mês de referência, da mais para a menos crítica ([T1 · Obras · posição]), separadas por '|'.",
  f"""VAR _mes = [Mês de referência]
VAR _obras = {obras_ref_pos('"@s", [T4 · Desembolso · faixa do fluxo de caixa]')}
RETURN
    CONCATENATEX ( FILTER ( _obras, [@s] = 2 ), dObra[Obra], "|", [@pos], ASC )""",
  "ago/26 (teste): JANGADA|POTENGI (−31% e −21%)")
m("T4 · Leitura desembolso · obra de maior excesso", LEI, TXT,
  "Obra do recorte com o maior desembolso acima do previsto, em reais, no mês de referência.",
  f"""VAR _mes = [Mês de referência]
VAR _obras = {obras_ref('"@d", [Desembolso · diferença no mês]')}
RETURN
    MAXX ( TOPN ( 1, FILTER ( _obras, [@d] > 0 ), [@d], DESC, {F}[Obra], ASC ), {F}[Obra] )""",
  "max obras[].ultimo.diferenca_desembolso_rs: CAJUEIRO (496.406)")
primeiro("T4 · Leitura desembolso · previsto no primeiro mês", "Desembolso · previsto no mês", LEI, RS,
         "carteira.serie[0].previsto_mes_rs 4.471.267,08")
primeiro("T4 · Leitura desembolso · desembolsado no primeiro mês", "Desembolso · realizado no mês", LEI, RS,
         "carteira.serie[0].desembolsado_mes_rs 4.997.740,29")
PICO = f"""{JANELA_VARS}
VAR _pares =
    CALCULATETABLE (
        ADDCOLUMNS ( SUMMARIZE ( {F}, {F}[Obra], {F}[Mes] ), "@d", [Desembolso · desvio no mês] ),
        REMOVEFILTERS ( dMes ),
        dMes[Mes] >= _ini && dMes[Mes] <= _ref
    )
VAR _top = TOPN ( 1, FILTER ( _pares, NOT ISBLANK ( [@d] ) ), [@d], DESC, {F}[Mes], ASC, {F}[Obra], ASC )
RETURN
    """
m("T4 · Leitura desembolso · pico do desvio", LEI, "0%",
  "Maior desvio do desembolso de uma obra num mês, do primeiro mês da janela ao de referência.",
  PICO + "MAXX ( _top, [@d] )", "max obras[].serie[].indicadores.desvio_desembolso: +68% (JANGADA abr/26)")
m("T4 · Leitura desembolso · obra do pico", LEI, TXT, "Obra do maior desvio do desembolso na janela.",
  PICO + f"MAXX ( _top, {F}[Obra] )", "JANGADA")
m("T4 · Leitura desembolso · mês do pico", LEI, DATA, "Mês do maior desvio do desembolso na janela.",
  PICO + f"MAXX ( _top, {F}[Mes] )", "2026-04-01")
CAUSAS = [  # (código, trecho procurado no texto) — a ordem desempata
    ("efetivo", "efetivo"), ("aditivo", "aditivo"), ("medicao", "duas parcelas"), ("postergada", "postergad"),
    ("compra", "compra antecipada"), ("sinal", "sinal de contrato")]
m("T4 · Justificativa · causa", LEI, TXT,
  "Causa da justificativa do desembolso (uma obra e um mês no contexto), lida do texto da planilha: efetivo, aditivo, "
  "medicao (medição concentrada), postergada (medição postergada), compra (compra antecipada), sinal (sinal de "
  "contrato) ou outra; vazio sem texto.",
  """VAR _t = TRIM ( [Justificativa do desembolso] )
RETURN
    IF (
        NOT ISBLANK ( _t ) && _t <> "",
        SWITCH (
            TRUE (),
""" + "".join(f'            CONTAINSSTRING ( _t, "{t}" ), "{c}",\n' for c, t in CAUSAS) + """            "outra"
        )
    )""", "obras[].serie[].justificativa")
ref("T4 · Justificativa · causa · ref", "T4 · Justificativa · causa", LEI, TXT,
    "obras[].ultimo.justificativa (TIROL e JANGADA efetivo · REDINHA aditivo · POTENGI compra)")
m("T4 · Leitura desembolso · causas mais frequentes (lista)", LEI, TXT,
  "As três causas mais repetidas nas justificativas dos meses com desembolso acima de +10% (excesso exigido), na "
  "janela; códigos de 'T4 · Justificativa · causa' separados por '|', da mais para a menos frequente.",
  f"""{JANELA_VARS}
VAR _pares =
    CALCULATETABLE (
        ADDCOLUMNS (
            SUMMARIZE ( {F}, {F}[Obra], {F}[Mes] ),
            "@c", [T4 · Justificativa · causa],
            "@d", [Desembolso · desvio no mês]
        ),
        REMOVEFILTERS ( dMes ),
        dMes[Mes] >= _ini && dMes[Mes] <= _ref
    )
VAR _excesso = FILTER ( _pares, [@d] > 0.10 && NOT ISBLANK ( [@c] ) && [@c] <> "outra" )
VAR _ordem = DATATABLE ( "@c", STRING, "@o", INTEGER, {{ """
  + ", ".join(f'{{ "{c}", {i} }}' for i, (c, _t) in enumerate(CAUSAS, start=1)) + f""" }} )
VAR _contagem =
    ADDCOLUMNS (
        _ordem,
        "@n", VAR _c = [@c] RETURN COUNTROWS ( FILTER ( _excesso, [@c] = _c ) ) + 0
    )
VAR _top = TOPN ( 3, FILTER ( _contagem, [@n] > 0 ), [@n], DESC, [@o], ASC )
RETURN
    CONCATENATEX ( _top, [@c], "|", [@n], DESC, [@o], ASC )""",
  "obras[].serie[].justificativa com desvio > 10%: efetivo 7 · aditivo 5 · medição concentrada 4")
m("T4 · Leitura desembolso · obras sem nenhuma justificativa (lista)", LEI, TXT,
  "Obras do recorte que tiveram justificativa exigida na janela e não preencheram nenhuma, da que mais deixou em "
  "branco para a que menos, separadas por '|'.",
  """VAR _obras =
    ADDCOLUMNS (
        VALUES ( dObra[Obra] ),
        "@e", [T4 · Obra · justificativas exigidas no período],
        "@p", [T4 · Obra · justificativas preenchidas no período]
    )
RETURN
    CONCATENATEX ( FILTER ( _obras, [@e] > 0 && [@p] = 0 ), dObra[Obra], "|", [@e], DESC, dObra[Obra], ASC )""",
  "CAJUEIRO (0 de 4)")
m("T4 · Leitura desembolso · justificativas em branco no período", LEI, INT,
  "Justificativas exigidas e deixadas em branco na janela, somadas pelas obras do recorte.",
  "SUMX ( VALUES ( dObra[Obra] ), [T4 · Obra · justificativas em branco no período] ) + 0", "4 (todas da CAJUEIRO)")

# ===================================================================================================== leituras · 4.4 desembolso por obra
m("T4 · Leitura desembolso por obra · obra em destaque", LEI, TXT,
  "A obra que a leitura do desembolso por obra cita: a de maior desvio entre as que deixaram a justificativa exigida "
  "em branco no mês de referência; sem nenhuma em branco, a de maior desvio.",
  f"""VAR _mes = [Mês de referência]
VAR _obras = {obras_ref('"@b", [Justificativa · em branco], "@d", [Desembolso · desvio no mês]')}
VAR _com = FILTER ( _obras, NOT ISBLANK ( [@d] ) )
VAR _nBranco = COUNTROWS ( FILTER ( _com, [@b] = 1 ) ) + 0
VAR _lista = FILTER ( _com, [@b] = 1 || _nBranco = 0 )
RETURN
    MAXX ( TOPN ( 1, _lista, [@d], DESC, {F}[Obra], ASC ), {F}[Obra] )""", "CAJUEIRO")
m("T4 · Leitura desembolso por obra · maior excesso justificado · obra", LEI, TXT,
  "Entre as obras que justificaram o desvio no mês de referência, a de maior desembolso acima do previsto em reais.",
  f"""VAR _mes = [Mês de referência]
VAR _obras =
    {obras_ref('"@e", [Justificativa · exigida], "@b", [Justificativa · em branco], '
               '"@d", [Desembolso · diferença no mês]')}
VAR _lista = FILTER ( _obras, [@e] = 1 && [@b] = 0 && [@d] > 0 )
RETURN
    MAXX ( TOPN ( 1, _lista, [@d], DESC, {F}[Obra], ASC ), {F}[Obra] )""",
  "POTENGI (176.082) entre REDINHA, POTENGI, TIROL e JANGADA")

# ===================================================================================================== leituras · fatos que o desenho lia por conta própria
# O desenho só lê estas contas (texto idêntico ao de antes: a prova EXACT confere em todos os contextos).
CAUSAS_TODAS = ["efetivo", "aditivo", "medicao", "postergada", "compra", "sinal", "outra"]


def obras_da_causa(codigo: str) -> str:
    """Obras do recorte com justificativa exigida, preenchida e de uma causa, na ordem da posição, com o artigo."""
    return f"""VAR _obras =
    ADDCOLUMNS (
        VALUES ( dObra[Obra] ),
        "@tem", [Obras com análise · ref],
        "@e", [Justificativa · exigida · ref],
        "@b", [Justificativa · em branco · ref],
        "@c", [T4 · Justificativa · causa · ref],
        "@art", [T4 · Obra · artigo],
        "@pos", [T1 · Obras · posição]
    )
VAR _lista = FILTER ( _obras, [@tem] > 0 && [@e] = 1 && [@b] = 0 && [@c] = "{codigo}" )
RETURN
    CONCATENATEX ( _lista, "n" & [@art] & " " & dObra[Obra], "|", [@pos], ASC )"""


m("T4 · Leitura desembolso por obra · obra há mais meses sem justificativa", LEI, TXT,
  "Obra que está há mais meses seguidos com a justificativa exigida em branco, até o mês de referência, entre as obras "
  "com aba no mês (empate: maior desvio do mês); vazio se nenhuma está em branco. Ex. ago/26: CAJUEIRO.",
  """VAR _obras =
    ADDCOLUMNS (
        VALUES ( dObra[Obra] ),
        "@tem", [Obras com análise · ref],
        "@b", [Justificativa · em branco · ref],
        "@d", [Desembolso · desvio no mês · ref],
        "@seg", [T4 · Obra · meses seguidos em branco]
    )
VAR _brancos = FILTER ( _obras, [@tem] > 0 && [@b] = 1 )
RETURN
    MAXX ( TOPN ( 1, _brancos, [@seg], DESC, [@d], DESC ), dObra[Obra] )""")
m("T4 · Leitura desembolso por obra · meses seguidos sem justificativa", LEI, INT,
  "Meses seguidos, até o de referência, em que a obra de 'obra há mais meses sem justificativa' deixou a justificativa "
  "exigida em branco; 0 se nenhuma. Ex. ago/26: 5 (CAJUEIRO, abr a ago/26).",
  """VAR _obra = [T4 · Leitura desembolso por obra · obra há mais meses sem justificativa]
RETURN
    IF ( NOT ISBLANK ( _obra ), CALCULATE ( [T4 · Obra · meses seguidos em branco], dObra[Obra] = _obra ) + 0, 0 )""")
m("T4 · Leitura desembolso por obra · silêncio é o maior excesso", LEI, INT,
  "1 quando a obra de 'obra há mais meses sem justificativa' é também a de maior excesso do mês ('T4 · Leitura "
  "desembolso · obra de maior excesso'); 0 caso contrário. Ex. ago/26: 1 (CAJUEIRO é também a de maior excesso).",
  """VAR _obra = [T4 · Leitura desembolso por obra · obra há mais meses sem justificativa]
RETURN
    IF ( NOT ISBLANK ( _obra ) && _obra = [T4 · Leitura desembolso · obra de maior excesso], 1, 0 )""")
for _cod in CAUSAS_TODAS:
    m(f"T4 · Leitura desembolso por obra · obras justificadas por causa · {_cod} (lista)", LEI, TXT,
      f"Obras do recorte com justificativa exigida, preenchida e de causa '{_cod}' no mês de referência, na ordem da "
      "posição, com o artigo ('no CAJUEIRO|na POTENGI'), separadas por '|'; vazio se nenhuma. Ex. ago/26: vazio (as exigidas de ago/26 estão todas em branco).",
      obras_da_causa(_cod))
m("T4 · Leitura mês · meses sem queda", LEI, INT,
  "Meses comparáveis da janela (com variação do resultado da carteira) em que a variação não caiu: alta ou igual ao "
  "mês anterior (comparáveis menos meses com queda). Diz 'subiu em X dos Y meses' no 'o que explica'. Ex. ago/26: 3 (7 comparáveis, 4 com queda).",
  """VAR _comp = [T4 · Leitura mês · meses comparáveis]
VAR _queda = [T4 · Leitura mês · meses com queda]
RETURN
    _comp - _queda""")
m("T4 · Leitura mês · início do detalhe", LEI, DATA,
  "Primeiro mês da janela, até o de referência, com ativos não consumidos: é o mês que leva o rótulo de início no "
  "detalhe mês a mês. Vazio se nenhum. Ex. ago/26: 01/01/2026 (jan/26).",
  """VAR _meses = ADDCOLUMNS ( VALUES ( dMes[Mes] ), "@ate", [Série · mês até a referência], "@a", [Ativos não consumidos] )
VAR _detCom = FILTER ( _meses, [@ate] = 1 && NOT ISBLANK ( [@a] ) )
RETURN
    MINX ( _detCom, dMes[Mes] )""")
m("T4 · Leitura desembolso · justificativas preenchidas no período", LEI, INT,
  "Justificativas exigidas e preenchidas na janela, somadas pelas obras com aba no período (a grade do desembolso). "
  "Com 0, a frase diz 'nenhum excesso exigido trouxe justificativa no período'. Ex. ago/26: 6.",
  """VAR _obras =
    ADDCOLUMNS (
        VALUES ( dObra[Obra] ),
        "@hist", [T4 · Meses com aba],
        "@pre", [T4 · Obra · justificativas preenchidas no período]
    )
VAR _naGrade = FILTER ( _obras, [@hist] > 0 )
RETURN
    SUMX ( _naGrade, [@pre] ) + 0""")
m("T4 · Tooltip obra do desembolso · meses com aba nos 5 anteriores", TT, INT,
  "Meses com aba (análise) da obra nos 5 meses antes do de referência, dentro da janela; decide se o histórico das "
  "justificativas aparece no tooltip. Ex. ago/26 (CAJUEIRO): 5.",
  """VAR _ref = [Mês de referência]
VAR _meses =
    ADDCOLUMNS (
        VALUES ( dMes[Mes] ),
        "@ate", [Série · mês até a referência],
        "@tem", [Obras com análise]
    )
RETURN
    COUNTROWS ( FILTER ( _meses, [@ate] = 1 && [@tem] > 0 && dMes[Mes] >= EDATE ( _ref, -5 ) && dMes[Mes] < _ref ) ) + 0""")

if __name__ == "__main__":
    sys.exit(gravar([x for x in MEDIDAS if x.nome not in RETIRADAS], AQUI.parent / "dax" / "T4", "pbi/scripts/contas_t4.py"))

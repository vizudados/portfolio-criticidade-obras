#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""contas_t1 — contas da Tela 01 · Visão geral (pbi/dax/T1/**/Contas). Só o que é próprio da tela; o resto vem de
base/ (contas · ref). Idempotente; apaga os .dax gerados por ele que saíram da lista.

F3 (28/10/2026, docs/08 §5): a régua é a Nota da obra (pbi/dax/base/nota). A lista de obras mostra a nota por
dimensão; "Onde a carteira perde pontos" fica no eixo dItemNota[Dimensao]; os cartões são um por dimensão.

    python -X utf8 pbi/scripts/contas_t1.py
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from contas_lib_projeto import Medida, gravar  # noqa: E402

F = "fAnaliseCritica"
MEDIDAS: list[Medida] = []

# Fase 2 da régua antiga (13/10/2026): régua antiga (dIndicador, pesos, pontos de 0 a 100) fora da tela. Fora da gravação: o
# gerador não escreve o nome e apaga o .dax que tinha escrito antes.
RETIRADAS = {
    "T1 · Obras · sinal 1",
    "T1 · Obras · sinal 2",
    "T1 · Pesa · maior pontuação",
    "T1 · Pesa · pontos das obras críticas",
    "T1 · Pesa · pontos das obras em atenção",
    "T1 · Pesa · obras críticas (lista)",
    # F3 (docs/08 §5): "Como os meses evoluíram" virou o mapa obra × mês (sem escala de colunas)
    "T1 · Semestre · maior total",
}


def m(*a, **k):
    MEDIDAS.append(Medida(*a, **k))


# obras com aba da Análise Crítica no mês do contexto (o recorte da carteira da nota, como em Nota · carteira · …)
COM_ABA = f"FILTER ( VALUES ( dObra[Obra] ), NOT ISEMPTY ( RELATEDTABLE ( {F} ) ) )"
# itens da nota (todos podem perder pontos)
ITENS = "ALL ( dItemNota )"

OBRAS = r"T1 Visão geral\Obras pela nota\Contas"
# Fase 2 (camada comum, agente base): a ordem segue a nota. Compartilhada com a T4 ("Por obra" e leituras).
m("T1 · Obras · posição", OBRAS, "0",
  "Posição da obra no ranking do mês de referência pela nota: mais pontos perdidos primeiro; empate pela menor nota "
  "(pendente, sem nota, depois das que têm nota) e depois pelo nome. Entre as obras com aba no mês e no recorte. Lê o "
  "ranking guardado em dRankingNota (as mesmas medidas Nota, calculadas no refresh). Uma obra no contexto.",
  """VAR _obra = SELECTEDVALUE ( dObra[Obra] )
VAR _mes = [Mês de referência]
VAR _recorte = CALCULATETABLE ( VALUES ( dObra[Obra] ), ALLSELECTED ( dObra ) )
VAR _obras = FILTER ( dRankingNota, dRankingNota[Mes] = _mes && dRankingNota[TemAC] = 1 && dRankingNota[Obra] IN _recorte )
VAR _eu = FILTER ( _obras, dRankingNota[Obra] = _obra )
VAR _perd = MAXX ( _eu, dRankingNota[Perdidos] )
VAR _nota = MAXX ( _eu, dRankingNota[NotaOrdem] )
VAR _antes =
    COUNTROWS (
        FILTER (
            _obras,
            dRankingNota[Perdidos] > _perd
                || (
                    dRankingNota[Perdidos] = _perd
                        && ( dRankingNota[NotaOrdem] < _nota || ( dRankingNota[NotaOrdem] = _nota && dRankingNota[Obra] < _obra ) )
                )
        )
    )
RETURN
    IF ( NOT ISEMPTY ( _eu ), _antes + 1 )""",
  oraculo="conferir_real.py · oráculo da nota (lista por pontos perdidos)")

for n in (1, 2):
    m(f"T1 · Obras · item que mais perde {n}", OBRAS, "texto",
      f"Código (dItemNota) do {n}º item da nota em que a obra mais perde pontos no mês do contexto: mais pontos perdidos "
      "primeiro; empate pelo maior máximo e depois pela ordem da nota. Só itens com perda; vazio "
      f"quando a obra perde pontos em menos de {n} item(ns). Uma obra no contexto.",
      f"""VAR _itens =
    ADDCOLUMNS (
        {ITENS},
        "@p", [Nota · item · perdidos]
    )
VAR _perde = FILTER ( _itens, [@p] > 0 )
VAR _top = TOPN ( {n}, _perde, [@p], DESC, dItemNota[Maximo], DESC, dItemNota[Ordem], ASC )
VAR _escolhido = TOPN ( 1, _top, [@p], ASC, dItemNota[Maximo], ASC, dItemNota[Ordem], DESC )
RETURN
    IF ( HASONEVALUE ( dObra[Obra] ) && COUNTROWS ( _top ) = {n}, MAXX ( _escolhido, dItemNota[Item] ) )""",
      oraculo="oráculo da régua antiga · ago/26: REDINHA medio_prazo, orcamento; POTENGI fluxo_caixa e vazio")
    m(f"T1 · Obras · item que mais perde {n} · ref", OBRAS, "texto",
      f"[T1 · Obras · item que mais perde {n}] no mês de referência (seletor do drawer; sem escolha, o último mês).",
      f"""VAR _mes = [Mês de referência]
RETURN
    CALCULATE ( [T1 · Obras · item que mais perde {n}], REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )""",
      oraculo="oráculo da régua antiga")

# itens que a FRASE cita (auditoria da Fase 2, minor 2: empate no topo cita todos): empate no topo, todos os empatados;
# topo único, ele e o segundo se o segundo for único; segundo empatado, só o topo (nenhum empatado vira "o segundo")
m("T1 · Obras · itens que mais perdem (lista)", OBRAS, "texto",
  "Códigos (dItemNota) dos itens que a frase 'perde mais …' cita para a obra do contexto, separados por '|', do que mais "
  "perde ao que menos perde (empate: maior máximo, depois a ordem da nota). Empate no topo: todos os empatados. Topo "
  "único: ele e o segundo, se o segundo for único; com o segundo empatado, só o topo. Só itens com perda; vazio sem "
  "perda. Uma obra no contexto.",
  f"""VAR _itens = ADDCOLUMNS ( {ITENS}, "@p", ROUND ( [Nota · item · perdidos], 8 ) )
VAR _perde = FILTER ( _itens, [@p] > 0 )
VAR _p1 = MAXX ( _perde, [@p] )
VAR _nTopo = COUNTROWS ( FILTER ( _perde, [@p] = _p1 ) )
VAR _p2 = MAXX ( FILTER ( _perde, [@p] < _p1 ), [@p] )
VAR _n2 = COUNTROWS ( FILTER ( _perde, [@p] = _p2 ) )
VAR _cita = FILTER ( _perde, [@p] = _p1 || ( _nTopo = 1 && _n2 = 1 && [@p] = _p2 ) )
RETURN
    IF (
        HASONEVALUE ( dObra[Obra] ),
        CONCATENATEX ( _cita, dItemNota[Item], "|", [@p], DESC, dItemNota[Maximo], DESC, dItemNota[Ordem], ASC )
    )""", oraculo="bases de teste, ago/26: REDINHA medio_prazo (o 2º empata em 0,5 entre três itens)")
m("T1 · Obras · itens que mais perdem (lista) · ref", OBRAS, "texto",
  "[T1 · Obras · itens que mais perdem (lista)] no mês de referência (seletor do drawer; sem escolha, o último mês).",
  """VAR _mes = [Mês de referência]
RETURN
    CALCULATE ( [T1 · Obras · itens que mais perdem (lista)], REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )""")
# quais obras dependem de cada fonte (auditoria da Fase 3, minor 8: "falta item na base complementar e na planilha" valia
# para as 6 obras, mas só uma dependia da planilha). Na base, o valor fora da faixa não é falta.
for _rot, _cond in (("na base", "[Nota · itens faltando na base · ref] - [Nota · itens fora da faixa · ref] > 0"),
                    ("na planilha", "[Nota · itens faltando na planilha · ref] > 0")):
    m(f"T1 · Obras · com item faltando {_rot} (lista) · ref", OBRAS, "texto",
      f"Obras do recorte com item da nota faltando {_rot} no mês de referência, separadas por '|', em ordem de nome; "
      "vazio sem falta.",
      f"""CONCATENATEX (
    FILTER ( VALUES ( dObra[Obra] ), {_cond} ),
    dObra[Obra],
    "|",
    dObra[Obra], ASC
)""", oraculo="bases reais, ago/26: na base as 6 obras; na planilha só a JANGADA")
# e quais têm valor fora da faixa (auditoria da Fase 3, rodada 2, m3: a leitura de obras contava como falta)
m("T1 · Obras · com item fora da faixa (lista) · ref", OBRAS, "texto",
  "Obras do recorte com item da nota de valor fora da faixa válida no mês de referência, separadas por '|', em ordem de "
  "nome; vazio sem nenhuma.",
  """CONCATENATEX (
    FILTER ( VALUES ( dObra[Obra] ), [Nota · itens fora da faixa · ref] > 0 ),
    dObra[Obra],
    "|",
    dObra[Obra], ASC
)""", oraculo="pbi/qa/nota/casos_auditoria.py · bases de teste, ago/26: DUNAS (Médio Prazo e termômetros)")

PESA = r"T1 Visão geral\Onde a carteira perde pontos\Contas"
# F3 (docs/08 §5): o painel passa de item para DIMENSÃO (eixo dItemNota[Dimensao], 7 linhas); o item vai para o tooltip.
# As medidas Nota · item · … somam os itens do contexto, então valem para a dimensão da linha.
DIMS = "ALL ( dItemNota[Dimensao], dItemNota[OrdemDimensao] )"
m("T1 · Pesa · posição", PESA, "0",
  "Ordem da dimensão no painel 'Onde a carteira perde pontos' (eixo dItemNota[Dimensao], mês de referência): mais "
  "pontos perdidos somados primeiro; empate: a dimensão com dado antes da que falta em todas as obras, depois a ordem "
  "da dimensão na régua.",
  f"""VAR _p = [Nota · item · perdidos · ref] + 0
VAR _t = INT ( NOT ISBLANK ( [Nota · item · possíveis · ref] ) )
VAR _ord = SELECTEDVALUE ( dItemNota[OrdemDimensao] )
VAR _todos =
    ADDCOLUMNS (
        {DIMS},
        "@p", [Nota · item · perdidos · ref] + 0,
        "@t", INT ( NOT ISBLANK ( [Nota · item · possíveis · ref] ) )
    )
VAR _antes =
    COUNTROWS (
        FILTER (
            _todos,
            [@p] > _p
                || ( [@p] = _p && [@t] > _t )
                || ( [@p] = _p && [@t] = _t && dItemNota[OrdemDimensao] < _ord )
        )
    )
RETURN
    IF ( HASONEVALUE ( dItemNota[Dimensao] ), _antes + 1 )""",
  oraculo="dados/_gabarito/nota_previa.csv · set/26: prazo (REDINHA e POTENGI) primeiro")
m("T1 · Pesa · maior perda", PESA, "0.00",
  "Maior soma de pontos perdidos entre as dimensões da nota no mês de referência (escala das barras do painel).",
  f"""MAXX ( {DIMS}, [Nota · item · perdidos · ref] )""", oraculo="dados/_gabarito/nota_previa.csv")

# barra do painel: os pontos perdidos da dimensão, separados pelo status da obra no mês de referência (vermelho = obras
# críticas, ocre = em atenção, sálvia = estáveis, tracejado = pendentes); somados = [Nota · item · perdidos · ref]
for chave, rot, cond in (("críticas", "críticas", "[Nota · status · ranking · ref] == 2"),
                         ("em atenção", "em atenção", "[Nota · status · ranking · ref] == 1"),
                         ("estáveis", "estáveis", "[Nota · status · ranking · ref] == 0"),
                         ("pendentes", "pendentes", "[Nota · pendente · ranking · ref] == 1")):
    m(f"T1 · Pesa · perdidos das obras {chave}", PESA, "0.00",
      f"Pontos que as obras {rot} no mês de referência perderam na dimensão da linha (dItemNota[Dimensao]). Somadas "
      "as quatro, dá [Nota · item · perdidos · ref].",
      f"""VAR _mes = [Mês de referência]
VAR _obras = CALCULATETABLE ( {COM_ABA}, REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )
RETURN
    IF (
        HASONEVALUE ( dItemNota[Dimensao] ),
        SUMX ( _obras, IF ( {cond}, [Nota · item · perdidos · ref] ) )
    )""", oraculo="dados/_gabarito/nota_previa.csv")
m("T1 · Pesa · obras sem dado", PESA, "0",
  "Obras com aba no mês de referência em que falta dado em algum item da dimensão da linha (falta na base ou sem dado "
  "na planilha; o valor fora da faixa válida também conta, porque o item fica sem pontos).",
  f"""VAR _mes = [Mês de referência]
VAR _obras = CALCULATETABLE ( {COM_ABA}, REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )
VAR _max = [Nota · item · máximo]
RETURN
    IF (
        HASONEVALUE ( dItemNota[Dimensao] ),
        COUNTROWS ( FILTER ( _obras, NOT ( [Nota · item · possíveis · ref] >= _max ) ) ) + 0
    )""", oraculo="dados completos: 0 em todas as dimensões")
m("T1 · Pesa · item que mais perde", PESA, "texto",
  "Código (dItemNota) do item da dimensão da linha que mais perde pontos somados no mês de referência (empate: a ordem "
  "do item); vazio sem perda ou com um item só na dimensão.",
  """VAR _itens = ADDCOLUMNS ( VALUES ( dItemNota[Item] ), "@p", [Nota · item · perdidos · ref] + 0 )
VAR _top = TOPN ( 1, FILTER ( _itens, [@p] > 0 ), [@p], DESC, [Nota · item · ordem], ASC )
RETURN
    IF ( HASONEVALUE ( dItemNota[Dimensao] ) && COUNTROWS ( _itens ) > 1, MAXX ( _top, dItemNota[Item] ) )""",
  oraculo="dados/_gabarito/nota_previa.csv")

# ===================================================================================================== cartões
CART = r"T1 Visão geral\Cartões\Contas"
m("T1 · Custo · obras com IDC abaixo de 1 · ref", CART, "0",
  "Obras com aba no mês de referência e IDC abaixo de 1 (gastam mais do que agregam).",
  f"""VAR _mes = [Mês de referência]
VAR _obras = CALCULATETABLE ( {COM_ABA}, REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )
RETURN
    COUNTROWS ( FILTER ( _obras, CALCULATE ( [IDC] < 1, REMOVEFILTERS ( dMes ), dMes[Mes] = _mes ) ) ) + 0""",
  oraculo="dados/_gabarito/nota_previa.csv (x_idc < 1)")
for _nome, _fmt, _desc, _ret in (
        ("T1 · Prazo · obra de maior atraso · ref", "texto", "Obra do recorte com o maior atraso em meses no mês de "
         "referência (empate: ordem alfabética); vazio sem atraso.", "MAXX ( _top, dObra[Obra] )"),
        ("T1 · Prazo · maior atraso · ref", "0.0", "Maior atraso em meses entre as obras do recorte no mês de "
         "referência; vazio sem atraso.", "MAXX ( _top, [@a] )")):
    m(_nome, CART, _fmt, _desc,
      f"""VAR _mes = [Mês de referência]
VAR _obras =
    CALCULATETABLE (
        ADDCOLUMNS ( {COM_ABA}, "@a", [Prazo · atraso (meses)] ),
        REMOVEFILTERS ( dMes ),
        dMes[Mes] = _mes
    )
VAR _top = TOPN ( 1, FILTER ( _obras, [@a] > 0 ), [@a], DESC, dObra[Obra], ASC )
RETURN
    {_ret}""", oraculo="dados/_gabarito/nota_previa.csv (x_atraso)")
m("T1 · Caixa · obras fora da faixa cheia · ref", CART, "0",
  "Obras com aba no mês de referência que não levaram o ponto cheio da previsão de caixa (desvio do desembolso fora da "
  "primeira faixa, para mais ou para menos).",
  f"""VAR _mes = [Mês de referência]
VAR _obras = CALCULATETABLE ( {COM_ABA}, REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )
RETURN
    COUNTROWS (
        FILTER (
            _obras,
            CALCULATE ( [Nota · pontos caixa] < [Nota · possíveis · caixa], REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )
        )
    ) + 0""", oraculo="dados/_gabarito/nota_previa.csv (pts_caixa < 1)")

if __name__ == "__main__":
    sys.exit(gravar([x for x in MEDIDAS if x.nome not in RETIRADAS], AQUI.parent / "dax" / "T1",
                    "pbi/scripts/contas_t1.py"))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""leituras_t1 — contas e desenho das leituras do "?" e do guia da Tela 01 (pbi/dax/T1/Leituras/**).

Figma: seção Interações · Tela 01 (290:720) — Leitura · T1 · Obras por criticidade 294:1094 ("?" 288:7241), O que pesa
na carteira 294:1144 ("?" 288:7245), Como os meses evoluíram 294:1196 ("?" 288:7249), Guia · T1 294:1236 ("?" 271:742);
exemplos montados 295:1936 (leitura aberta) e 295:2364 (guia aberto). Gramática: docs/06-interacoes-spec.md §1.7–1.8,
§4 e §5 (L058: cada número aparece uma vez por leitura; a régua mora em "Como ler").

Regra L065 (pedido do Alisson, 06/10/2026): a leitura cobre o painel que explica. No Power BI cada leitura é um HTML
Content no retângulo exato do painel (sem margem nem sombra), aberto pelo "?" com um marcador de exibição; o × é um SVG
igual ao "?" da casca, com um botão de fechar do mesmo retângulo do "?", e um botão do tamanho da tela, por baixo da
leitura, fecha com clique fora. O guia da página é o único que cobre a tela inteira (véu + painel 760 + marcadores).

Fase 2 da régua antiga (13/10/2026; artefato plano-nota-painel/fase-2-telas): as três leituras falam da Nota da obra (quatro
estados: crítico, atenção, estável, pendente) e dos itens em que a carteira perde pontos; sem os pesos da régua antiga.
A ordem das obras é só a da nota (T1 · Obras · posição e Nota · recorte · obras por pontos perdidos (lista)). Entrou /
saiu / abriu em crítico pela regra nova: só conta entre dois meses com nota completa; a primeira nota completa da
obra, já crítica (antes, só meses pendentes ou sem planilha), é "abriu em crítico" (auditoria, M1).

    python -X utf8 pbi/scripts/leituras_t1.py
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import contador as C  # noqa: E402
import desenho_comum as DC  # noqa: E402
import desenho_projeto as D  # noqa: E402
from contas_lib_projeto import Medida, gravar  # noqa: E402
from leituras_lib import CSS_X, X_SVG  # noqa: E402
from contas_base import NOTA_ITENS  # noqa: E402

# quantos itens e de que fonte, do dicionário NOTA (texto do "como ler")
_EXTENSO = {1: "um", 2: "dois", 3: "três", 4: "quatro", 5: "cinco", 6: "seis", 7: "sete", 8: "oito", 9: "nove", 10: "dez"}
_N_ITENS = _EXTENSO[len(NOTA_ITENS)]
_N_AC = sum(it["fonte"] == "Análise Crítica" for it in NOTA_ITENS)
_N_FONTES = (f"{_EXTENSO[_N_AC]} vêm da Análise Crítica e {_EXTENSO[len(NOTA_ITENS) - _N_AC]} da base complementar, "
             "preenchida a cada mês")

RAIZ = AQUI.parent
GERADO = "pbi/scripts/leituras_t1.py"
F = "fAnaliseCritica"
MEDIDAS: list[Medida] = []
PTS = DC.FMT_PTS

# Retiradas do modelo em 08/10/2026 (auditoria: dependencias-pos-telas.json e dependencias-final.json, chave mortas) e
# na Fase 2 da régua antiga (13/10/2026: régua antiga — indicadores, pesos, sinais, pontos de 0 a 100 — fora das leituras).
# Fora da gravação: o gerador não escreve o nome e apaga o .dax que tinha escrito antes.
RETIRADAS = {
    "T1 · Leitura · indicador com mais atenção",
    "T1 · Leitura · indicador em pontos · 2",
    "T1 · Leitura · indicador em pontos · 3",
    "T1 · Leitura · meses com alta dos ativos",
    "T1 · Leitura · meses com resultado sem estoque negativo",
    "T1 · Leitura · obras em atenção no indicador (lista)",
    "T1 · Leitura · obras que deixaram a faixa estável (lista)",
    "T1 · Leitura · sinal principal no mês",
    # Fase 2 da régua antiga
    "T1 · Leitura · obras fora da faixa",
    "T1 · Leitura · indicador mais espalhado",
    "T1 · Leitura · indicador mais espalhado · obras",
    "T1 · Leitura · indicador mais espalhado · empate",
    "T1 · Leitura · indicador em pontos · 1",
    "T1 · Leitura · indicador de maior peso",
    "T1 · Leitura · estáveis sem sinal",
    "T1 · Leitura · obras positivas sem estoque (lista)",
    "T1 · Leitura · maior desvio de desembolso · obra",
    "T1 · Leitura · maior desvio de desembolso",
    "T1 · Leitura · sinais críticos no mês (lista)",
    "T1 · Leitura · resultado no primeiro mês",
    "T1 · Leitura · resultado da carteira · sequência · início",
}

CONTAS = r"T1 Visão geral\Leituras\Contas"
DES = r"T1 Visão geral\Leituras"
COM_ABA = f"FILTER ( VALUES ( dObra[Obra] ), NOT ISEMPTY ( RELATEDTABLE ( {F} ) ) )"
ITENS = "ALL ( dItemNota )"


def conta(nome, formato, descricao, dax, oraculo=""):
    MEDIDAS.append(Medida(nome, CONTAS, formato, descricao, dax, oraculo))


def desenho(nome, descricao, dax):
    """Medida de desenho; os valores marcados com C.marca() viram odômetro no fim (F4, contador.envolver_marcas)."""
    MEDIDAS.append(Medida(nome, DES, "texto", descricao, C.envolver_marcas(dax)))


def mk(expr: str) -> str:
    """DAX: o número {expr} marcado para o contador (F4); só em conteúdo, nunca em atributo."""
    return C.marca(expr)


def linhas(*ls) -> str:
    return "\n".join(l for g in ls for l in (g if isinstance(g, list) else [g]))


def fmt_pts(v: str) -> str:
    return f'FORMAT ( {v}, "{PTS}", "pt-BR" )'


def ext(v: str, fem: bool = True) -> str:
    """Expressão DAX: inteiro por extenso (0 a 10), senão o algarismo."""
    nomes = (["nenhuma", "uma", "duas"] if fem else ["nenhum", "um", "dois"]) + \
        ["três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez"]
    casos = ", ".join(f'{i}, "{n}"' for i, n in enumerate(nomes))
    return f'SWITCH ( {v}, {casos}, FORMAT ( {v}, "0" ) )'


def cap(v: str) -> str:
    return f"UPPER ( LEFT ( {v}, 1 ) ) & MID ( {v}, 2, LEN ( {v} ) )"


def nome_mes(v: str) -> str:
    return f'FORMAT ( {v}, "mmmm", "pt-BR" )'


def em_frase(v: str) -> str:
    """DAX: 'o orçamento' → 'no orçamento', 'a média PPC' → 'na média PPC', 'os termômetros' → 'nos termômetros'."""
    return (f'SWITCH ( TRUE (), LEFT ( {v}, 3 ) = "os ", "nos " & MID ( {v}, 4, 99 ), LEFT ( {v}, 3 ) = "as ", '
            f'"nas " & MID ( {v}, 4, 99 ), LEFT ( {v}, 2 ) = "o ", "no " & MID ( {v}, 3, 99 ), LEFT ( {v}, 2 ) = "a ", '
            f'"na " & MID ( {v}, 3, 99 ), "em " & {v} )')


DIM_FRASE = {"Custo": "o custo", "Prazo": "o prazo", "Caixa": "o caixa", "Qualidade": "a qualidade",
             "Segurança": "a segurança", "Suprimentos": "os suprimentos", "Gestão": "a gestão"}


def dim_frase(v: str) -> str:
    """DAX: 'o prazo' · 'a segurança' (com artigo) do nome da dimensão."""
    return "SWITCH ( " + v + ", " + ", ".join(f'"{k}", "{x}"' for k, x in DIM_FRASE.items()) + f", LOWER ( {v} ) )"


def dims_fr(lista: str, p: str) -> list[str]:
    """{p}Fr = 'no prazo e no custo' para as dimensões da lista (até três pelo nome; mais, por extenso); {p}N = quantas."""
    out = [f'VAR {p}N = IF ( {lista} = "", 0, PATHLENGTH ( {lista} ) )']
    for k, x in enumerate("abc", 1):
        out += [f"VAR {p}{x} = PATHITEM ( {lista}, {k} ) & \"\"",
                f"VAR {p}{x}Frase = {dim_frase(p + x)}",
                f'VAR {p}{x}Fr = IF ( {p}{x} = "", "", {em_frase(p + x + "Frase")} )']
    out.append(f'VAR {p}Fr = SWITCH ( {p}N, 0, "", 1, {p}aFr, 2, {p}aFr & " e " & {p}bFr, 3, {p}aFr & ", " & {p}bFr '
               f'& " e " & {p}cFr, "em " & {ext(p + "N", fem=True)} & " dimensões empatadas" )')
    return out


def lista_e(v: str, p: str) -> list[str]:
    """{p}Txt = "A, B e C" a partir de "A|B|C"; {p}N = quantos nomes (só decide o texto)."""
    return [
        f'VAR {p}N = IF ( ISBLANK ( {v} ) || {v} = "", 0, PATHLENGTH ( {v} ) )',
        f'VAR {p}Pos = IF ( {p}N >= 2, FIND ( "§", SUBSTITUTE ( {v}, "|", "§", {p}N - 1 ) ) )',
        f'VAR {p}Txt = SWITCH ( TRUE (), {p}N = 0, "", {p}N = 1, {v}, '
        f'SUBSTITUTE ( LEFT ( {v}, {p}Pos - 1 ), "|", ", " ) & " e " & MID ( {v}, {p}Pos + 1, 999 ) )',
    ]


# ===================================================================================================== contas
# itens da nota na carteira (mês de referência): onde mais perde em pontos e onde a perda mais se espalha
conta("T1 · Leitura · item que mais perde", "texto",
      "Código (dItemNota) do item em que a carteira mais perde pontos no mês de referência (empate: o de maior máximo, "
      "depois a ordem da nota); vazio quando nenhum item perdeu pontos.",
      f"""VAR _itens = ADDCOLUMNS ( {ITENS}, "@p", [Nota · item · perdidos · ref] )
VAR _top = TOPN ( 1, FILTER ( _itens, [@p] > 0 ), [@p], DESC, dItemNota[Maximo], DESC, dItemNota[Ordem], ASC )
RETURN
    MAXX ( _top, dItemNota[Item] )""", "oráculo da régua antiga · ago/26: orcamento (3,0; empata com o fluxo de caixa)")
conta("T1 · Leitura · itens que mais perdem (lista)", "texto",
      "Códigos (dItemNota) de todos os itens empatados no topo dos pontos perdidos pela carteira no mês de referência "
      "(empate: maior máximo, depois a ordem da nota), separados por '|'; vazio sem perda. A frase cita todos (auditoria "
      "da Fase 2, minor 2).",
      f"""VAR _itens = ADDCOLUMNS ( {ITENS}, "@p", ROUND ( [Nota · item · perdidos · ref], 8 ) )
VAR _max = MAXX ( FILTER ( _itens, [@p] > 0 ), [@p] )
RETURN
    CONCATENATEX ( FILTER ( _itens, [@p] > 0 && [@p] = _max ), dItemNota[Item], "|", dItemNota[Maximo], DESC,
        dItemNota[Ordem], ASC )""", "bases reais, ago/26: orcamento|fluxo_caixa (3,0 cada)")
conta("T1 · Leitura · item mais espalhado", "texto",
      "Código (dItemNota) do item em que mais obras perderam pontos no mês de referência (empate: mais pontos perdidos, "
      "depois a ordem da nota); vazio quando nenhum item perdeu pontos.",
      f"""VAR _itens =
    ADDCOLUMNS (
        {ITENS},
        "@o", [Nota · item · obras que perderam pontos · ref] + 0,
        "@p", [Nota · item · perdidos · ref] + 0
    )
VAR _top = TOPN ( 1, FILTER ( _itens, [@o] > 0 ), [@o], DESC, [@p], DESC, dItemNota[Ordem], ASC )
RETURN
    MAXX ( _top, dItemNota[Item] )""", "oráculo da régua antiga · ago/26: fluxo_caixa (4 obras)")
conta("T1 · Leitura · item mais espalhado · obras", "0",
      "Quantas obras perderam pontos no item mais espalhado (mês de referência).",
      """VAR _cod = [T1 · Leitura · item mais espalhado]
RETURN
    CALCULATE ( [Nota · item · obras que perderam pontos · ref], dItemNota[Item] = _cod ) + 0""",
      "oráculo da régua antiga · ago/26: 4")
# F3 (docs/08 §5): o painel "Onde a carteira perde pontos" fala de DIMENSÃO; a leitura dele também
DIMS = "ALL ( dItemNota[Dimensao], dItemNota[OrdemDimensao] )"
conta("T1 · Leitura · dimensões que mais perdem (lista)", "texto",
      "Dimensões da nota empatadas no topo dos pontos perdidos pela carteira no mês de referência (empate: a ordem da "
      "dimensão), separadas por '|'; vazio sem perda.",
      f"""VAR _dims = ADDCOLUMNS ( {DIMS}, "@p", ROUND ( [Nota · item · perdidos · ref], 8 ) )
VAR _max = MAXX ( FILTER ( _dims, [@p] > 0 ), [@p] )
RETURN
    CONCATENATEX ( FILTER ( _dims, [@p] > 0 && [@p] = _max ), dItemNota[Dimensao], "|", dItemNota[OrdemDimensao], ASC )""",
      "dados/_gabarito/nota_previa.csv · set/26: Prazo")
conta("T1 · Leitura · dimensão que mais perde", "texto",
      "A primeira das dimensões que mais perdem pontos na carteira no mês de referência; vazio sem perda.",
      """PATHITEM ( [T1 · Leitura · dimensões que mais perdem (lista)] & "", 1 )""",
      "dados/_gabarito/nota_previa.csv · set/26: Prazo")
conta("T1 · Leitura · dimensão mais espalhada", "texto",
      "Dimensão da nota em que mais obras perderam pontos no mês de referência (empate: mais pontos perdidos, depois a "
      "ordem da dimensão); vazio sem perda.",
      f"""VAR _dims =
    ADDCOLUMNS (
        {DIMS},
        "@o", [Nota · item · obras que perderam pontos · ref] + 0,
        "@p", [Nota · item · perdidos · ref] + 0
    )
VAR _top = TOPN ( 1, FILTER ( _dims, [@o] > 0 ), [@o], DESC, [@p], DESC, dItemNota[OrdemDimensao], ASC )
RETURN
    MAXX ( _top, dItemNota[Dimensao] )""", "dados/_gabarito/nota_previa.csv")
conta("T1 · Leitura · dimensão mais espalhada · obras", "0",
      "Quantas obras perderam pontos na dimensão mais espalhada (mês de referência).",
      """VAR _d = [T1 · Leitura · dimensão mais espalhada]
RETURN
    CALCULATE ( [Nota · item · obras que perderam pontos · ref], dItemNota[Dimensao] = _d ) + 0""",
      "dados/_gabarito/nota_previa.csv")
conta("T1 · Leitura · status que mais perde", "texto",
      "Estado da nota das obras que somam mais pontos perdidos no mês de referência: '2' crítico, '1' atenção, '0' "
      "estável, 'm' pendente; vazio sem perda.",
      f"""VAR _mes = [Mês de referência]
VAR _obras =
    CALCULATETABLE (
        ADDCOLUMNS (
            {COM_ABA},
            "@s", IF ( [Nota · pendente · um mês] == 1, "m", [Nota · status · um mês] & "" ),
            "@p", [Nota · pontos perdidos · um mês]
        ),
        REMOVEFILTERS ( dMes ),
        dMes[Mes] = _mes
    )
VAR _por =
    ADDCOLUMNS (
        DATATABLE ( "Estado", STRING, {{ {{ "2" }}, {{ "1" }}, {{ "0" }}, {{ "m" }} }} ),
        "@soma", VAR _e = [Estado] RETURN SUMX ( FILTER ( _obras, [@s] = _e ), [@p] )
    )
VAR _top = TOPN ( 1, FILTER ( _por, [@soma] > 0 ), [@soma], DESC, [Estado], ASC )
RETURN
    MAXX ( _top, [Estado] )""", "oráculo da régua antiga · ago/26: m (JANGADA 2,0 + DUNAS 1,75 + CAJUEIRO 0,75)")

conta("T1 · Leitura · itens sem dado na carteira", "0",
      "Itens da nota sem dado no mês de referência, somados pelas obras da carteira (as que têm aba da Análise Crítica "
      "no mês, como em Nota · carteira · …). O valor fora da faixa válida não falta (auditoria da Fase 3, "
      "rodada 2, m3).",
      f"""VAR _mes = [Mês de referência]
RETURN
    SUMX (
        CALCULATETABLE ( {COM_ABA}, REMOVEFILTERS ( dMes ), dMes[Mes] = _mes ),
        [Nota · itens faltando · ref] - [Nota · itens fora da faixa · ref]
    ) + 0""",
      "pbi/qa/nota/casos_auditoria.py teste · ago/26: 7 (CAJUEIRO 1, JANGADA 6; os 2 da DUNAS são fora da faixa)")

for nome, medida, fmt in (("obras críticas", "Nota · carteira · obras críticas", "0"),
                          ("obras pendentes", "Nota · carteira · obras pendentes", "0"),
                          ("ativos", "Ativos não consumidos", '"R$" #,0.00;-"R$" #,0.00'),
                          ("desvio físico", "Físico · desvio acumulado p.p.", "+0.00;-0.00;0.00")):
    conta(f"T1 · Leitura · {nome} no primeiro mês", fmt,
          f"[{medida}] no primeiro mês da janela das séries (recorte de obras do drawer).",
          f"""VAR _ini = [Série · primeiro mês]
RETURN
    CALCULATE ( [{medida}], REMOVEFILTERS ( dMes ), dMes[Mes] = _ini )""", "carteira.serie[0]")
conta("T1 · Leitura · pico de obras críticas", "0",
      "Maior número de obras críticas na nota num mês da janela (do primeiro mês da janela ao de referência).",
      """VAR _ref = [Mês de referência]
VAR _ini = [Série · primeiro mês]
VAR _meses =
    ADDCOLUMNS (
        FILTER ( ALL ( dMes[Mes] ), dMes[Mes] >= _ini && dMes[Mes] <= _ref ),
        "@c", [Nota · carteira · obras críticas] + 0
    )
RETURN
    MAXX ( _meses, [@c] )""", "oráculo da régua antiga · bases de teste: 1 (DUNAS, mai/26)")
conta("T1 · Leitura · mês do pico de obras críticas", "dd/mm/yyyy",
      "Primeiro mês da janela em que as obras críticas na nota chegaram ao pico (vazio quando nenhuma obra foi crítica).",
      """VAR _ref = [Mês de referência]
VAR _ini = [Série · primeiro mês]
VAR _pico = [T1 · Leitura · pico de obras críticas]
VAR _meses =
    ADDCOLUMNS (
        FILTER ( ALL ( dMes[Mes] ), dMes[Mes] >= _ini && dMes[Mes] <= _ref ),
        "@c", [Nota · carteira · obras críticas] + 0
    )
RETURN
    IF ( _pico > 0, MINX ( FILTER ( _meses, [@c] = _pico ), dMes[Mes] ) )""")

# Regra de "entrou em crítico" na nota (Fase 2, 13/10/2026): só conta entre dois meses com nota completa. Entra quem
# está crítico no mês e tinha nota completa abaixo de crítico no mês anterior; sai quem era crítico e tem nota completa
# abaixo de crítico no mês; quem chega à primeira nota completa já crítica (o mês anterior pendente ou sem planilha)
# "abriu em crítico", à parte (passar de pendente a crítico não é entrar). Lista e contagem saem das mesmas condições.
# Auditoria da Fase 2 (M1, 14/10/2026): "abriu" é a PRIMEIRA nota completa da obra (@ja = 0: nenhuma linha anterior de
# dRankingNota com aba e nota completa). Crítico → pendente → crítico não entra nem abre.
ENTROU = "[@s] == 2 && NOT ISBLANK ( [@a] ) && [@a] < 2"
SAIU = "[@a] == 2 && NOT ISBLANK ( [@s] ) && [@s] < 2"
ABRIU = "[@s] == 2 && [@ja] = 0"


def tabela_obras(com_ordem: bool) -> str:
    """Obras com aba no mês do contexto (um mês), no recorte, com o status do mês, o do mês anterior e se já tiveram nota
    completa antes (@ja, para "abriu em crítico"), lidos do ranking
    guardado (dRankingNota: as mesmas medidas Nota, calculadas no refresh; integração da Fase 2, desempenho). Sem linha
    no mês anterior = sem nota completa (sem aba da Análise Crítica não há nota), como o [Nota · status · ranking] daria."""
    cols = ['"@s", dRankingNota[Status]',
            '"@a",\n            VAR _o = dRankingNota[Obra]\n            RETURN\n                MAXX ( FILTER ( ALL ( '
            'dRankingNota ), dRankingNota[Obra] = _o && dRankingNota[Mes] = _ant && dRankingNota[TemAC] = 1 ), '
            'dRankingNota[Status] )',
            '"@ja",\n            VAR _o = dRankingNota[Obra]\n            RETURN\n                IF ( ISEMPTY ( FILTER ( ALL ( '
            'dRankingNota ), dRankingNota[Obra] = _o && dRankingNota[Mes] < _m && dRankingNota[TemAC] = 1 '
            '&& dRankingNota[Pendente] == 0 ) ), 0, 1 )']
    if com_ordem:
        cols += ['"@p", dRankingNota[Perdidos]', '"@n", dRankingNota[NotaOrdem]']
    return ("VAR _m = SELECTEDVALUE ( dMes[Mes] )\nVAR _ant = EDATE ( _m, -1 )\nVAR _recorte = VALUES ( dObra[Obra] )\n"
            "VAR _obras =\n    ADDCOLUMNS (\n        FILTER ( dRankingNota, dRankingNota[Mes] = _m && dRankingNota[TemAC] = 1 && dRankingNota[Obra] IN "
            "_recorte ),\n        " + ",\n        ".join(cols) + "\n    )")


def lista_obras(cond: str) -> str:
    return (tabela_obras(True) + "\nRETURN\n    CONCATENATEX ( FILTER ( _obras, " + cond
            + " ), dRankingNota[Obra], \"|\", [@p], DESC, [@n], ASC, dRankingNota[Obra], ASC )")


def conta_obras(cond: str) -> str:
    return tabela_obras(False) + f"\nRETURN\n    COUNTROWS ( FILTER ( _obras, {cond} ) ) + 0"


def soma_entradas_abriram() -> str:
    """Entraram + abriram em crítico com uma só ADDCOLUMNS sobre as obras (a série da piora custa uma varredura por
    mês, não duas)."""
    return (tabela_obras(False)
            + f"\nRETURN\n    COUNTROWS ( FILTER ( _obras, {ENTROU} ) ) + COUNTROWS ( FILTER ( _obras, {ABRIU} ) ) + 0")


conta("T1 · Leitura · obras que entraram em crítico (lista)", "texto",
      "Obras críticas na nota no mês do contexto que tinham nota completa abaixo de crítico no mês anterior; da que mais "
      "perde pontos para a que menos perde, separadas por '|'.",
      lista_obras(ENTROU), "oráculo da régua antiga (status mês a mês)")
conta("T1 · Leitura · obras que saíram de crítico (lista)", "texto",
      "Obras críticas na nota no mês anterior que têm nota completa abaixo de crítico no mês do contexto; da que mais "
      "perde pontos para a que menos perde, separadas por '|'. Bases de teste, jun/26: DUNAS.",
      lista_obras(SAIU), "oráculo da régua antiga (status mês a mês)")
conta("T1 · Leitura · obras que abriram em crítico (lista)", "texto",
      "Obras críticas na nota no mês do contexto cuja primeira nota completa é a deste mês (antes, só meses pendentes "
      "ou sem planilha). Não contam como entrada; crítico → pendente → crítico não abre. Bases de teste, mai/26: DUNAS.",
      lista_obras(ABRIU), "oráculo da régua antiga (status mês a mês)")
conta("T1 · Leitura · obras que entraram em crítico", "0",
      "Quantas obras entraram em crítico na nota no mês do contexto (mesma regra da lista: só entre notas completas).",
      conta_obras(ENTROU), "oráculo da régua antiga (status mês a mês)")
conta("T1 · Leitura · obras que saíram de crítico", "0",
      "Quantas obras saíram de crítico na nota no mês do contexto (mesma regra da lista).",
      conta_obras(SAIU), "oráculo da régua antiga (status mês a mês)")
conta("T1 · Leitura · obras que abriram em crítico", "0",
      "Quantas obras tiveram a primeira nota completa já crítica no mês do contexto (mesma regra da lista, fora de "
      "'entraram').",
      conta_obras(ABRIU), "oráculo da régua antiga (status mês a mês)")
conta("T1 · Leitura · obras que entraram ou abriram em crítico", "0",
      "Quantas obras entraram em crítico no mês do contexto ou abriram nele: a soma das duas contagens acima, numa só "
      "varredura das obras (a série da piora lê esta conta mês a mês).",
      soma_entradas_abriram(), "oráculo da régua antiga (status mês a mês)")
conta("T1 · Leitura · mês em que a piora começou", "dd/mm/yyyy",
      "Primeiro mês depois do primeiro da janela em que alguma obra entrou ou abriu em crítico na nota (vazio sem "
      "nenhum). Bases de teste, ago/26 com 12 meses: mai/26.",
      """VAR _ref = [Mês de referência]
VAR _ini = [Série · primeiro mês]
VAR _meses =
    ADDCOLUMNS (
        FILTER ( ALL ( dMes[Mes] ), dMes[Mes] > _ini && dMes[Mes] <= _ref ),
        "@n", [T1 · Leitura · obras que entraram ou abriram em crítico]
    )
RETURN
    MINX ( FILTER ( _meses, [@n] > 0 ), dMes[Mes] )""")
conta("T1 · Leitura · mês em que a piora se firmou", "dd/mm/yyyy",
      "Segundo mês depois do primeiro da janela em que alguma obra entrou ou abriu em crítico na nota (vazio sem ele).",
      """VAR _ref = [Mês de referência]
VAR _ini = [Série · primeiro mês]
VAR _meses =
    ADDCOLUMNS (
        FILTER ( ALL ( dMes[Mes] ), dMes[Mes] > _ini && dMes[Mes] <= _ref ),
        "@n", [T1 · Leitura · obras que entraram ou abriram em crítico]
    )
VAR _e1 = MINX ( FILTER ( _meses, [@n] > 0 ), dMes[Mes] )
RETURN
    IF ( NOT ISBLANK ( _e1 ), MINX ( FILTER ( _meses, [@n] > 0 && dMes[Mes] > _e1 ), dMes[Mes] ) )""")

# ===================================================================================================== desenho comum
# L065: a leitura cobre o painel que explica. O HTML Content tem o retângulo exato do painel (sem margem, sem sombra); o
# × é o SVG X_SVG de leituras_lib (o mesmo círculo do "?" da casca), irmão do painel e por cima dele.
X = X_SVG


def painel(classe: str, aria: str, corpo: str, script: str = "") -> str:
    fim = f' & {script}' if script else ""
    return (f'"<div class=\'u lv\' role=\'dialog\' aria-label=\'" & {aria} & "\'><div class=\'pn {classe}\'>" '
            f'& {corpo} & "</div>{X}</div>"{fim}')


def bloco(rotulo: str, conteudo: str) -> str:
    return f'"<div class=\'sec\'><span class=\'vs\'>{rotulo}</span>" & {conteudo} & "</div>"'


def destaque(num: str, rot: str) -> str:
    return f'"<div><b>" & {num} & "</b><span>" & {rot} & "</span></div>"'


def destaque_linha(num: str, rot: str) -> str:
    return f'"<div class=\'dl\'><b>" & {num} & "</b><span>" & {rot} & "</span></div>"'


def item_de(cod: str, p: str, obra: str | None = None, mes: str | None = None) -> list[str]:
    """{p}Fr = 'no orçamento' do item `cod` (e {p}Cod, o código)."""
    return [f"VAR {p}Frase = CALCULATE ( [Nota · item · nome em frase], dItemNota[Item] = {cod} )",
            f'VAR {p}Fr = IF ( {cod} = "", "", {em_frase(p + "Frase")} )']


def itens_fr(lista: str, p: str) -> list[str]:
    """{p}Fr = 'no orçamento e no fluxo de caixa' para os códigos da lista (até três pelo nome; mais, por extenso);
    {p}N = quantos (só decide o texto)."""
    out = [f'VAR {p}N = IF ( {lista} = "", 0, PATHLENGTH ( {lista} ) )']
    for k, x in enumerate("abc", 1):
        out += [f"VAR {p}{x} = PATHITEM ( {lista}, {k} ) & \"\""] + item_de(f"{p}{x}", f"{p}{x}")
    out.append(f'VAR {p}Fr = SWITCH ( {p}N, 0, "", 1, {p}aFr, 2, {p}aFr & " e " & {p}bFr, 3, {p}aFr & ", " & {p}bFr '
               f'& " e " & {p}cFr, "em " & {ext(p + "N", fem=False)} & " itens empatados" )')
    return out


# ===================================================================================================== 4.1 Obras
def obra_critica(k: int) -> list[str]:
    """Frase da k-ésima obra crítica: 'REDINHA tem nota 5,40 e perde mais no orçamento e no fluxo de caixa. '"""
    p = f"_c{k}"
    return [
        f"VAR {p} = PATHITEM ( _listaCrit, {k} )",
        f"VAR {p}Nota = CALCULATE ( [Nota · nota final · ranking · ref], dObra[Obra] = {p} )",
        f"VAR {p}L = CALCULATE ( [T1 · Obras · itens que mais perdem (lista) · ref], dObra[Obra] = {p} ) & \"\"",
    ] + itens_fr(f"{p}L", f"{p}I") + [
        f'VAR {p}Fr = IF ( {p} = "", "", {D.esc(p)} & " tem nota " & {mk(fmt_pts(p + "Nota"))} & " e perde mais " '
        f'& {p}IFr & ". " )',
    ]


# v2: coluna direita (340) = nomes + trilho (Figma Leitura · T1 · v2 391:4305: 96 + 244). F4 (28/10/2026): a coluna dos
# nomes foi a 108, para PONTA NEGRA (Segoe Semibold 15 ≈ 101 px) caber sem reticências
NOME_OBRAS = 108
TRILHO_OBRAS = 340 - NOME_OBRAS
PASSO_BARRA = 60            # cascata das barras do detalhe (ms por posição)

desenho("T1 · Leitura obras · HTML",
        "Leitura do \"?\" da lista de obras, sobre o próprio painel (L065, 1004 × 631, duas colunas): achado pelos "
        "estados da nota, explicação pelas obras críticas (ou pela que mais perde pontos) e pelas pendentes, três "
        "destaques que contam (pontos da obra que mais perde, pontos perdidos no item que mais pesa, itens sem dado), "
        "o que explica, a nota obra por obra com as linhas dos limites de atenção e de estável (pendente em "
        "tracejado) e a régua antiga lida das medidas. Ordem só a da nota. Só lê contas.",
        linhas(
            "-- 1 · Leituras",
            "VAR _mesN = [Mês de referência · nome]",
            "VAR _mesL = [Mês de referência · longo]",
            "VAR _c = [Nota · carteira · obras críticas · ref] + 0",
            "VAR _a = [Nota · carteira · obras em atenção · ref] + 0",
            "VAR _e = [Nota · carteira · obras estáveis · ref] + 0",
            "VAR _p = [Nota · carteira · obras pendentes · ref] + 0",
            "VAR _nObras = [Recorte · obras no recorte] + 0",
            "VAR _listaCrit = [Nota · recorte · obras críticas (lista)]",
            "VAR _listaAten = [Nota · recorte · obras em atenção (lista)]",
            "VAR _listaEst = [Nota · recorte · obras estáveis (lista)]",
            "VAR _listaPend = [Nota · recorte · obras pendentes (lista)]",
            "VAR _ranking = [Nota · recorte · obras por pontos perdidos (lista)]",
            "VAR _falta = [T1 · Leitura · itens sem dado na carteira]",
            *DC.onde_falta(),
            "VAR _max = [Nota · nota · máximo]",
            "VAR _limA = [Nota · status · nota mínima atenção]",
            "VAR _limE = [Nota · status · nota mínima estável]",
            "VAR _fxC = [Nota · status · faixa crítico]",
            "VAR _fxA = [Nota · status · faixa atenção]",
            "VAR _fxE = [Nota · status · faixa estável]",
            "VAR _trvC = [Nota · limite custo · trava]",
            "VAR _trvP = [Nota · limite prazo · trava]",
            "VAR _top = [T1 · Leitura · item que mais perde] & \"\"",
            "VAR _esp = [T1 · Leitura · item mais espalhado] & \"\"",
            "VAR _topPerd = CALCULATE ( [Nota · item · perdidos · ref], dItemNota[Item] = _top )",
            "VAR _o1 = PATHITEM ( _ranking, 1 )",
            "VAR _perd1 = CALCULATE ( [Nota · pontos perdidos · ranking · ref], dObra[Obra] = _o1 )",
            "VAR _pend1 = CALCULATE ( [Nota · pendente · ranking · ref], dObra[Obra] = _o1 )",
            "VAR _st1 = CALCULATE ( [Nota · status · ranking · ref], dObra[Obra] = _o1 )",
            "VAR _o1L = CALCULATE ( [T1 · Obras · itens que mais perdem (lista) · ref], dObra[Obra] = _o1 ) & \"\"",
            "VAR _tops = [T1 · Leitura · itens que mais perdem (lista)] & \"\"",
            "VAR _barras =",
            "    ADDCOLUMNS (",
            "        VALUES ( dObra[Obra] ),",
            '        "@pos", [T1 · Obras · posição],',
            '        "@s", [Nota · status · ranking · ref],',
            '        "@pend", [Nota · pendente · ranking · ref],',
            '        "@nota", [Nota · nota final · ranking · ref],',
            '        "@obt", [Nota · pontos obtidos · ranking · ref],',
            '        "@poss", [Nota · pontos possíveis · ranking · ref]',
            "    )",
            "VAR _comPos = FILTER ( _barras, NOT ISBLANK ( [@pos] ) ) /* lista */",
            obra_critica(1), obra_critica(2), obra_critica(3),
            item_de("_top", "_t"), item_de("_esp", "_s"), itens_fr("_o1L", "_j"), itens_fr("_tops", "_ts"),
            "-- 2 · Textos",
            D.od_tabela(),
            lista_e("_listaCrit", "_lc"), lista_e("_listaAten", "_la"), lista_e("_listaEst", "_le"),
            lista_e("_listaPend", "_lp"),
            "VAR _txtSob = \"LEITURA · OBRAS PELA NOTA · \" & UPPER ( _mesL )",
            # os outros estados pelo nome (até três) ou pela contagem por extenso: nenhum algarismo no achado (L058)
            'VAR _tA = IF ( _a = 0, "", IF ( _laN <= 3, _laTxt, ' + ext("_a") + ' & " obras" ) & IF ( _a = 1, '
            '" pede atenção", " pedem atenção" ) )',
            'VAR _tE = IF ( _e = 0, "", IF ( _leN <= 3, _leTxt, ' + ext("_e") + ' & " obras" ) & IF ( _e = 1, '
            '" segue estável", " seguem estáveis" ) )',
            'VAR _tP = IF ( _p = 0, "", IF ( _c + _a + _e = 0, "", "as outras " ) & IF ( _p = 1, "uma está pendente", '
            + ext("_p") + ' & " estão pendentes" ) )',
            'VAR _nOut = INT ( _a > 0 ) + INT ( _e > 0 ) + INT ( _p > 0 )',
            "VAR _txtOut =",
            "    SWITCH (",
            "        _nOut,",
            "        0, \"\",",
            "        1, _tA & _tE & _tP,",
            "        2, IF ( _a > 0, _tA & IF ( _e > 0, \" e \" & _tE, \"; \" & _tP ), _tE & \"; \" & _tP ),",
            "        _tA & \", \" & _tE & \"; \" & _tP",
            "    )",
            "VAR _txtAchado =",
            "    SWITCH (",
            "        TRUE (),",
            '        _c + _a + _e + _p = 0, "Nenhuma obra com planilha em " & _mesN & ".",',
            '        _c + _a + _e = 0, IF ( _p = 1, "A obra está pendente em ", "As " & ' + ext("_p")
            + ' & " obras estão pendentes em " ) & _mesN & ": " & IF ( _ondeSoFora, "há valor fora da faixa na base '
            'complementar", "falta item " & _onde & _ondeFora ) & ".",',
            '        _c = 0, "Nenhuma obra crítica em " & _mesN & ": " & _txtOut & ".",',
            '        _c = 1, "Uma obra crítica em " & _mesN & ": " & _lcTxt & "." & IF ( _txtOut = "", "", " "'
            ' & ' + cap("_txtOut") + ' & "." ),',
            '        ' + cap(ext("_c")) + ' & " obras críticas em " & _mesN & ": " & _lcTxt & "." & IF ( _txtOut = "",'
            ' "", " " & ' + cap("_txtOut") + ' & "." )',
            "    )",
            "VAR _txtO1 =",
            "    SWITCH (",
            "        TRUE (),",
            '        _o1 = "" || NOT ( _perd1 > 0 ), "Nenhuma obra perdeu pontos nos itens com dado.",',
            '        _pend1 = 1, "Nos itens que já têm dado, quem mais perde é a " & ' + D.esc("_o1")
            + ' & ", pendente: perde mais " & _jFr & ".",',
            '        "Quem mais perde pontos é a " & ' + D.esc("_o1") + ' & ", " & SWITCH ( _st1, 2, "crítica", 1, '
            '"em atenção", "estável" ) & ": perde mais " & _jFr & "."',
            "    )",
            'VAR _txtPend = IF ( _p = 0 || _c + _a + _e = 0, "", " " & IF ( _p = 1, "A pendente, ", "As pendentes, " ) '
            '& _lpTxt & IF ( _p = 1, ", ainda não tem nota", ", ainda não têm nota" ) & ": " & IF ( _ondeSoFora, '
            '"há valor fora da faixa na base complementar", "falta dado " & _onde & _ondeFora ) & "." )',
            "VAR _txtExplica =",
            "    IF (",
            "        _c > 0,",
            '        TRIM ( _c1Fr & _c2Fr & _c3Fr & IF ( _c > 3, "Há mais obras críticas na lista. ", "" ) ) & _txtPend,',
            "        _txtO1 & _txtPend",
            "    )",
            "VAR _txtOq =",
            "    SWITCH (",
            "        TRUE (),",
            '        _top = "", "Nenhum item da nota perdeu pontos no mês.",',
            '        _esp = _top && _tsN = 1, ' + cap("_tFrase") + ' & " é onde a carteira mais perde, em pontos e em obras atingidas.",',
            '        "A carteira perde mais pontos " & _tsFr & IF ( _tsN > 1, ", empatados", "" ) & "; a perda que atinge mais '
            'obras está " & _sFr & "."',
            "    )",
            fmt_pts("_perd1").join(["VAR _txtP1 = ", ""]),
            C.bloco_od("_p1K", "_txtP1").rstrip(),
            "VAR _txtTop = " + fmt_pts("_topPerd"),
            C.bloco_od("_tpK", "_txtTop").rstrip(),
            "VAR _txtFalta = FORMAT ( _falta, \"0\" )",
            C.bloco_od("_fK", "_txtFalta").rstrip(),
            "VAR _txtD1 = IF ( NOT ( _perd1 > 0 ), \"pontos perdidos: nenhuma obra perdeu\", \"pontos que a \" & "
            + D.esc("_o1") + " & \" perde, a maior perda da carteira\" )",
            "VAR _txtD2 = IF ( _top = \"\", \"pontos perdidos por item\", \"pontos perdidos \" & _tsFr & IF ( _tsN > 1, "
            "\", cada um\", \"\" ) & \", somadas as obras\" )",
            "VAR _txtD3 = IF ( _falta = 1, \"item ainda sem dado, somadas as obras\", \"itens ainda sem dado, somadas as obras\" )",
            "-- 3 · Geometria",
            "VAR _nLinhas = COUNTROWS ( _comPos ) /* geometria */",
            "VAR _alt = _nLinhas * 30 -- geometria",
            f"VAR _xA = {NOME_OBRAS} + ROUND ( _limA / _max * {TRILHO_OBRAS}, 0 ) -- geometria",
            f"VAR _xE = {NOME_OBRAS} + ROUND ( _limE / _max * {TRILHO_OBRAS}, 0 ) -- geometria",
            "-- 4 · Marcação",
            "VAR _htmlBarras =",
            "    CONCATENATEX (",
            "        _comPos,",
            "        VAR _pd = [@pend] = 1",
            f"        VAR _lN = MAX ( 2, ROUND ( MIN ( [@nota], _max ) / _max * {TRILHO_OBRAS}, 0 ) ) -- geometria",
            f"        VAR _lO = MAX ( 2, ROUND ( MIN ( [@obt], _max ) / _max * {TRILHO_OBRAS}, 0 ) ) -- geometria",
            f"        VAR _lP = ROUND ( MIN ( [@poss], _max ) / _max * {TRILHO_OBRAS}, 0 ) -- geometria",
            f"        VAR _atraso = 500 + ( [@pos] - 1 ) * {PASSO_BARRA} -- geometria",
            "        VAR _barra =",
            "            IF (",
            "                _pd,",
            "                \"<u class='a-gx' style='width:\" & _lP & \"px;animation-delay:\" & _atraso & \"ms'></u>\"",
            "                    & \"<i class='sm' style='width:\" & _lO & \"px' data-rk='\"",
            "                    & dObra[Obra] & \"' data-rd='\" & _atraso & \"'></i>\",",
            "                \"<i class='s\" & [@s] & \"' style='width:\" & _lN & \"px' data-rk='\" & dObra[Obra] & \"' data-rd='\"",
            "                    & _atraso & \"'></i>\"",
            "            )",
            "        RETURN",
            '            "<div class=\'r\'><b>" & dObra[Obra] & "</b><div class=\'tr\'>" & _barra & "</div></div>",',
            '        "",',
            "        [@pos], ASC",
            "    )",
            "VAR _htmlDet =",
            "    \"<span class='vs'>Detalhe · nota das \" & " + ext("_nObras") + " & \" obras</span>\"",
            "        & \"<p class='sub'>as linhas marcam onde começam a atenção e o estável; a pendente vai tracejada até "
            "o que já dá para calcular</p>\"",
            "        & \"<div class='bp' style='height:\" & ( _alt + 22 ) & \"px'>\" & _htmlBarras",
            "        & \"<i class='lim' style='left:\" & _xA & \"px;height:\" & _alt & \"px'></i>\"",
            "        & \"<i class='lim' style='left:\" & _xE & \"px;height:\" & _alt & \"px'></i>\"",
            "        & \"<span class='lr la a-fd' style='left:\" & _xA & \"px;top:\" & ( _alt + 4 ) & \"px;animation-delay:400ms'>atenção</span>\"",
            "        & \"<span class='lr le a-fd' style='left:\" & _xE & \"px;top:\" & ( _alt + 4 ) & \"px;animation-delay:400ms'>estável</span>\"",
            "        & \"</div>\"",
            "VAR _htmlDst =",
            "    \"<div class='dst sobre-creme'>\"",
            "        & " + destaque('IF ( NOT ( _perd1 > 0 ), "0", _p1KOd )', "_txtD1"),
            "        & " + destaque('IF ( _top = "", "0", _tpKOd )', "_txtD2"),
            "        & " + destaque("_fKOd", "_txtD3"),
            "    & \"</div>\"",
            # régua da nota: limites e máximos lidos das medidas; contagem de itens por fonte, do dicionário NOTA
            "VAR _txtComoLer =",
            "    \"<p class='cl'>A Nota da obra soma " + _N_ITENS + " itens, de 0 a \" & " + mk('FORMAT ( _max, "0", "pt-BR" )') + " & \" pontos: \"",
            "        & \"" + _N_FONTES + ". Estável com nota \" & " + D.esc("_fxE") + " & \"; atenção de \" & "
            + D.esc("_fxA") + " & \"; crítico com \" & " + D.esc("_fxC") + " & \". IDC abaixo de \" & " + mk('FORMAT ( _trvC, "0.00", "pt-BR" )')
            + " & \" ou atraso acima de \" & " + mk('FORMAT ( _trvP, "0", "pt-BR" )') + " & \" meses deixam a obra "
            "crítica, qualquer que seja a nota. Enquanto falta item, a obra fica pendente: mostra os pontos que já dá para "
            "calcular e não recebe status.</p>\"",
            "VAR _esq =",
            "    \"<div class='esq'><span class='vs sob'>\" & _txtSob & \"</span>\"",
            "        & \"<h2 class='ach'>\" & _txtAchado & \"</h2>\"",
            "        & \"<p class='exp'>\" & _txtExplica & \"</p>\"",
            "        & _htmlDst",
            "        & " + bloco("O que explica", "\"<p class='oqe'>\" & _txtOq & \"</p>\""),
            "    & \"</div>\"",
            "VAR _dir =",
            "    \"<div class='dir'>\" & _htmlDet",
            "        & " + bloco("Como ler", "_txtComoLer"),
            "    & \"</div>\"",
            "VAR _corpo = \"<div class='cols'>\" & _esq & \"<i class='div'></i>\" & _dir & \"</div>\"",
            "RETURN",
            "    IF ( _nObras > 0, " + painel("pn-obras", '"Leitura da lista de obras pela Nota da obra"', "_corpo",
                                          "[Comum · JS contador tooltip] & [Comum · JS corrida]") + " )",
        ))


# ===================================================================================================== 4.2 Onde perde
desenho("T1 · Leitura pesa · HTML",
        "Leitura do \"?\" de 'Onde a carteira perde pontos', sobre o próprio painel (L065, 464 × 406, condensada): a "
        "dimensão em que a perda mais se espalha e a que mais soma pontos perdidos, três destaques em linha que contam "
        "(pontos perdidos na dimensão que mais pesa, itens sem dado, justificativas do desembolso preenchidas) e de que "
        "obras vem a maior parte da perda. Faixas e conta obra por obra ficam no tooltip da dimensão. Só lê contas.",
        linhas(
            "-- 1 · Leituras",
            "VAR _mesC = [Mês de referência · curto maiúsculo]",
            "VAR _mesN = [Mês de referência · nome]",
            "VAR _nObras = [Recorte · obras no recorte] + 0",
            "VAR _top = [T1 · Leitura · dimensão que mais perde] & \"\"",
            "VAR _esp = [T1 · Leitura · dimensão mais espalhada] & \"\"",
            "VAR _espN = [T1 · Leitura · dimensão mais espalhada · obras] + 0",
            "VAR _stMais = [T1 · Leitura · status que mais perde] & \"\"",
            "VAR _topPerd = CALCULATE ( [Nota · item · perdidos · ref], dItemNota[Dimensao] = _top )",
            "VAR _falta = [T1 · Leitura · itens sem dado na carteira]",
            "VAR _jusEx = [Carteira · justificativas exigidas · ref] + 0",
            "VAR _jusPre = [Carteira · justificativas preenchidas · ref] + 0",
            "VAR _tNome = " + dim_frase("_top"),
            "VAR _tops = [T1 · Leitura · dimensões que mais perdem (lista)] & \"\"",
            dims_fr("_tops", "_ts"),
            "VAR _sNome = " + dim_frase("_esp"),
            "-- 2 · Textos",
            D.od_tabela(),
            "VAR _txtSob = \"LEITURA · ONDE A CARTEIRA PERDE PONTOS · \" & _mesC",
            "VAR _txtQuantas = IF ( _espN = _nObras, \"todas as \" & " + mk("_nObras") + " & \" obras\", " + mk("_espN")
            + " & \" das \" & " + mk("_nObras") + " & \" obras\" )",
            "VAR _txtAchado =",
            "    SWITCH (",
            "        TRUE (),",
            '        _top = "", "Nenhuma dimensão da nota perdeu pontos em " & _mesN & ".",',
            '        _esp = _top && _tsN = 1, ' + cap("_tNome") + ' & " é onde a carteira mais perde: em " & _txtQuantas & ".",',
            '        ' + cap("_sNome") + ' & " é a perda mais espalhada: " & _txtQuantas & "."',
            "    )",
            "VAR _txtExp =",
            "    SWITCH (",
            "        TRUE (),",
            '        _top = "", "",',
            '        _esp = _top && _tsN = 1, "É também a dimensão que mais soma pontos perdidos.",',
            '        "Em pontos somados, a carteira perde mais " & _tsFr & IF ( _tsN > 1, ", empatados", "" ) & "."',
            "    )",
            'VAR _txtFaltaExp = IF ( _falta > 0, " Onde falta dado, a perda ainda não aparece.", "" )',
            "VAR _txtOq =",
            "    SWITCH (",
            "        _stMais,",
            '        "2", "A maior parte da perda vem das obras críticas.",',
            '        "1", "A maior parte da perda vem das obras em atenção.",',
            '        "0", "A maior parte da perda vem das obras estáveis.",',
            '        "m", "A maior parte da perda vem das obras pendentes.",',
            '        "Nenhuma obra perdeu pontos no mês."',
            "    )",
            "VAR _txtTop = " + fmt_pts("_topPerd"),
            C.bloco_od("_tpK", "_txtTop").rstrip(),
            "VAR _txtFalta = FORMAT ( _falta, \"0\" )",
            C.bloco_od("_fK", "_txtFalta").rstrip(),
            D.inteiro("_jusPre", "_tjp"), D.od_num("_jusPre", "_tjp"),
            "VAR _txtD1 = IF ( _top = \"\", \"pontos perdidos no mês\", \"perdidos \" & _tsFr & IF ( _tsN > 1, "
            "\", cada uma, as maiores\", \", a maior perda\" ) )",
            "VAR _txtD2 = IF ( _falta = 1, \"item sem dado na carteira\", \"itens sem dado na carteira\" )",
            "VAR _txtD3 = IF ( _jusEx = 0, \"nenhum desembolso pediu justificativa\", \"justificativas do desembolso "
            "preenchidas\" )",
            "-- 4 · Marcação",
            "VAR _htmlDst =",
            "    \"<div class='dst dst-l'>\"",
            "        & " + destaque_linha('IF ( _top = "", "0", _tpKOd ) & " pts"', "_txtD1"),
            "        & " + destaque_linha("_fKOd", "_txtD2"),
            "        & " + destaque_linha('IF ( _jusEx = 0, "0", _tjpOd & " de " & ' + mk("_jusEx") + ' )', "_txtD3"),
            "    & \"</div>\"",
            "VAR _corpo =",
            "    \"<span class='vs sob'>\" & _txtSob & \"</span>\"",
            "        & \"<h2 class='ach'>\" & _txtAchado & \"</h2>\"",
            "        & \"<p class='exp'>\" & _txtExp & _txtFaltaExp & \"</p>\"",
            "        & _htmlDst",
            "        & " + bloco("O que explica", "\"<p class='oqe'>\" & _txtOq & \"</p>\""),
            "RETURN",
            "    IF ( _nObras > 0, " + painel("pn-peq", '"Leitura de Onde a carteira perde pontos"', "_corpo",
                                          "[Comum · JS contador tooltip]") + " )",
        ))


# ===================================================================================================== 4.3 Meses
desenho("T1 · Leitura semestre · HTML",
        "Leitura do \"?\" de Como os meses evoluíram, sobre o próprio painel (L065, 464 × 321, condensada mínima): "
        "obras críticas e pendentes na nota do primeiro mês da janela ao de referência, quando a piora começou e se "
        "firmou (entrou ou abriu em crítico, pela regra nova), o pico e quem saiu de crítico, e três destaques em linha "
        "que contam. A linha do tempo fica no tooltip do mês. Só lê contas.",
        linhas(
            "-- 1 · Leituras",
            "VAR _ref = [Mês de referência]",
            "VAR _ini = [Série · primeiro mês]",
            "VAR _nMeses = [Série · meses até a referência] + 0",
            "VAR _mesC = [Mês de referência · curto maiúsculo]",
            "VAR _mesN = [Mês de referência · nome]",
            "VAR _nObras = [Recorte · obras no recorte] + 0",
            "VAR _critIni = [T1 · Leitura · obras críticas no primeiro mês] + 0",
            "VAR _critRef = [Nota · carteira · obras críticas · ref] + 0",
            "VAR _pendIni = [T1 · Leitura · obras pendentes no primeiro mês] + 0",
            "VAR _pendRef = [Nota · carteira · obras pendentes · ref] + 0",
            "VAR _ativIni = [T1 · Leitura · ativos no primeiro mês]",
            "VAR _ativRef = [Ativos não consumidos · ref]",
            "VAR _fisIni = [T1 · Leitura · desvio físico no primeiro mês]",
            "VAR _fisRef = [Físico · desvio acumulado p.p. · ref]",
            "VAR _pico = [T1 · Leitura · pico de obras críticas] + 0",
            "VAR _picoMes = [T1 · Leitura · mês do pico de obras críticas]",
            # meses da piora e as listas do mês vêm das contas (T1 · Leitura · mês em que a piora começou / se firmou)
            "VAR _e1 = [T1 · Leitura · mês em que a piora começou]",
            "VAR _e2 = [T1 · Leitura · mês em que a piora se firmou]",
            "VAR _e1Obras = CALCULATE ( [T1 · Leitura · obras que entraram em crítico (lista)], dMes[Mes] = _e1 )",
            "VAR _e1Abriu = CALCULATE ( [T1 · Leitura · obras que abriram em crítico (lista)], dMes[Mes] = _e1 )",
            "VAR _e2Obras = CALCULATE ( [T1 · Leitura · obras que entraram em crítico (lista)], dMes[Mes] = _e2 )",
            "VAR _e2Abriu = CALCULATE ( [T1 · Leitura · obras que abriram em crítico (lista)], dMes[Mes] = _e2 )",
            "VAR _saiRef = IF ( _ref > _ini, CALCULATE ( [T1 · Leitura · obras que saíram de crítico (lista)], dMes[Mes] = _ref ) )",
            "VAR _e1O1 = PATHITEM ( _e1Obras, 1 )",
            "VAR _e2O1 = PATHITEM ( _e2Obras, 1 )",
            # os itens em que a primeira obra que entrou em crítico mais perde, no mês em que entrou: a lista que as frases
            # citam (empate no topo, todos; auditoria da Fase 2, rodada 2, N1)
            "VAR _e1L = CALCULATE ( [T1 · Obras · itens que mais perdem (lista)], dMes[Mes] = _e1, dObra[Obra] = _e1O1 ) & \"\"",
            "VAR _e2L = CALCULATE ( [T1 · Obras · itens que mais perdem (lista)], dMes[Mes] = _e2, dObra[Obra] = _e2O1 ) & \"\"",
            itens_fr("_e1L", "_i1"), itens_fr("_e2L", "_i2"),
            # quem entrou ou abriu em crítico no mês de referência, quando ele não é o da piora (N5: a saída do mês não
            # pode esconder a entrada do mesmo mês)
            "VAR _entRef = IF ( _ref > _ini && _ref <> _e1 && _ref <> _e2, CALCULATE ( [T1 · Leitura · obras que entraram em "
            "crítico (lista)], dMes[Mes] = _ref ) )",
            "VAR _abrRef = IF ( _ref > _ini && _ref <> _e1 && _ref <> _e2, CALCULATE ( [T1 · Leitura · obras que abriram em "
            "crítico (lista)], dMes[Mes] = _ref ) )",
            "VAR _saiO1 = PATHITEM ( _saiRef, 1 )",
            "VAR _saiSt = CALCULATE ( [Nota · status · ranking · ref], dObra[Obra] = _saiO1 )",
            "-- 2 · Textos",
            D.od_tabela(),
            lista_e("_e1Obras", "_l1"), lista_e("_e2Obras", "_l2"), lista_e("_saiRef", "_ls"),
            lista_e("_e1Abriu", "_a1"), lista_e("_e2Abriu", "_a2"), lista_e("_entRef", "_lr"), lista_e("_abrRef", "_lb"),
            "VAR _txtEntRef = IF ( _lrN = 0, \"\", _lrTxt & IF ( _lrN = 1, \" entrou em crítico\", \" entraram em crítico\" ) )"
            " & IF ( _lbN = 0, \"\", IF ( _lrN > 0, \" e \", \"\" ) & _lbTxt & IF ( _lbN = 1, \" abriu em crítico\", "
            "\" abriram em crítico\" ) )",
            "VAR _abrevIni = FORMAT ( _ini, \"mmm\", \"pt-BR\" )",
            "VAR _txtSob = \"LEITURA · COMO OS MESES EVOLUÍRAM · \" & IF ( _nMeses <= 1, _mesC, UPPER ( _abrevIni ) & \" A \" & _mesC )",
            D.rs("_ativRef", "_tar"), D.rs("_ativIni", "_tai"),
            D.pp("_fisRef", "_tfr"), D.pp("_fisIni", "_tfi"),
            D.od_rs("_ativRef", "_tar"), D.od_pp("_fisRef", "_tfr"),
            D.inteiro("_pico", "_tpc"), D.od_num("_pico", "_tpc"),
            # achado sem algarismos (L058: os números ficam nos destaques)
            "VAR _txtCrit = IF ( _critIni = _critRef, " + ext("_critRef") + " & \" no início e no fim\", \"de \" & "
            + ext("_critIni") + " & \" para \" & " + ext("_critRef") + " )",
            "VAR _txtPend = IF ( _pendIni = _pendRef, " + ext("_pendRef") + " & \" no início e no fim\", \"de \" & "
            + ext("_pendIni") + " & \" para \" & " + ext("_pendRef") + " )",
            "VAR _txtAchado =",
            "    SWITCH (",
            "        TRUE (),",
            '        _nMeses <= 1, "Primeiro mês do histórico: " & ' + ext("_critRef") + ' & IF ( _critRef <= 1, " crítica",'
            ' " críticas" ) & " e " & ' + ext("_pendRef") + ' & IF ( _pendRef = 1, " pendente.", " pendentes." ),',
            '        "Críticas: " & _txtCrit & "; pendentes, " & _txtPend & "."',
            "    )",
            # quem abriu em crítico vai à parte, depois de quem entrou: "(DUNAS, mais no orçamento; POTENGI já abriu crítica)"
            "VAR _p1 = IF ( _l1N > 0, _l1Txt & IF ( _i1Fr <> \"\", \", perdendo mais \" & _i1Fr, \"\" ), \"\" )",
            "VAR _q1 = IF ( _a1N = 0, \"\", _a1Txt & IF ( _a1N = 1, \" já abriu crítica\", \" já abriram críticas\" ) )",
            "VAR _par1 = \"(\" & _p1 & IF ( _p1 <> \"\" && _q1 <> \"\", \"; \", \"\" ) & _q1 & \")\"",
            "VAR _p2 = IF ( _l2N > 0, _l2Txt & IF ( _i2Fr <> \"\", \", perdendo mais \" & _i2Fr, \"\" ), \"\" )",
            "VAR _q2 = IF ( _a2N = 0, \"\", _a2Txt & IF ( _a2N = 1, \" já abriu crítica\", \" já abriram críticas\" ) )",
            "VAR _par2 = \"(\" & _p2 & IF ( _p2 <> \"\" && _q2 <> \"\", \"; \", \"\" ) & _q2 & \")\"",
            "VAR _txtPiora =",
            "    IF (",
            "        ISBLANK ( _e1 ),",
            '        "Nenhuma obra entrou em crítico no período.",',
            '        "A piora começou em " & ' + nome_mes("_e1") + ' & " " & _par1',
            '            & IF ( ISBLANK ( _e2 ), "", " e se firmou em " & ' + nome_mes("_e2") + ' & " " & _par2 ) & "."',
            "    )",
            "VAR _txtPico =",
            "    IF (",
            "        _pico = 0 || ISBLANK ( _picoMes ) || _picoMes = _e1,",
            '        "",',
            '        " " & ' + cap(nome_mes("_picoMes")) + ' & IF ( _picoMes = _ref, " é", " foi" ) & " o pico"',
            "    )",
            "VAR _txtSaida =",
            "    SWITCH (",
            "        TRUE (),",
            '        _lsN = 0 && _txtEntRef = "", IF ( _txtPico = "", "", "." ),',
            '        _lsN = 0, IF ( _txtPico = "", " Em ", "; em " ) & _mesN & " " & _txtEntRef & ".",',
            '        IF ( _txtPico = "", " Em ", "; em " ) & _mesN & " " & _lsTxt & IF ( _lsN = 1, " voltou", " voltaram" )'
            ' & IF ( _saiSt = 1, " para atenção", " para a faixa estável" ) & IF ( _txtEntRef = "", ".", ", e " & _txtEntRef'
            ' & "." )',
            "    )",
            "VAR _txtJanela = IF ( _nMeses <= 1, \"no mês\", \"nos últimos \" & " + mk("_nMeses") + " & \" meses\" )",
            "VAR _txtObrasCrit = IF ( _pico = 1, \"obra crítica\", \"obras críticas\" )",
            "VAR _txtD1 =",
            "    SWITCH (",
            "        TRUE (),",
            "        _pico = 0, \"obras críticas \" & _txtJanela,",
            "        _nMeses <= 1, _txtObrasCrit & \" em \" & " + nome_mes("_picoMes") + ",",
            "        _txtObrasCrit & \" em \" & " + nome_mes("_picoMes") + " & \", o pico dos \" & " + mk("_nMeses") + " & \" meses\"",
            "    )",
            "VAR _txtAbIni = _abrevIni & \".\"",
            # L058: com a janela curta o primeiro mês pode mostrar o mesmo número do de referência; aí diz "o mesmo"
            "VAR _txtAtivIni =",
            "    SWITCH (",
            "        TRUE (),",
            "        _nMeses <= 1, \"\",",
            "        _taiTxt = _tarTxt, \" (o mesmo de \" & _txtAbIni & \")\",",
            "        \" (\" & _txtAbIni & \": \" & " + mk("_taiTxt") + " & \")\"",
            "    )",
            "VAR _txtFisIni =",
            "    SWITCH (",
            "        TRUE (),",
            "        _nMeses <= 1, \"\",",
            "        _tfiTxt = _tfrTxt, \" (o mesmo de \" & _txtAbIni & \")\",",
            "        \" (\" & _txtAbIni & \": \" & IF ( ROUND ( _fisIni, 1 ) < 0, \"<span class='ng'>\" & " + mk("_tfiTxt")
            + " & \"</span>\", " + mk("_tfiTxt") + " ) & \")\"",
            "    )",
            "-- 4 · Marcação",
            "VAR _htmlDst =",
            "    \"<div class='dst dst-l'>\"",
            "        & " + destaque_linha("_tpcOd", "_txtD1"),
            "        & " + destaque_linha("_tarOd", '"pagos e não aplicados" & _txtAtivIni'),
            "        & " + destaque_linha('IF ( ROUND ( _fisRef, 1 ) < 0, "<span class=\'ng\'>" & _tfrOd & "</span>", _tfrOd )',
                                  '"físico ponderado" & _txtFisIni'),
            "    & \"</div>\"",
            "VAR _corpo =",
            "    \"<span class='vs sob'>\" & _txtSob & \"</span>\"",
            "        & \"<h2 class='ach'>\" & _txtAchado & \"</h2>\"",
            "        & \"<p class='exp'>\" & _txtPiora & _txtPico & _txtSaida & \"</p>\"",
            "        & _htmlDst",
            "RETURN",
            "    IF ( _nObras > 0, " + painel("pn-peq pn-meses", '"Leitura de Como os meses evoluíram"', "_corpo",
                                          "[Comum · JS contador tooltip]") + " )",
        ))


# ===================================================================================================== CSS
CSS_LEITURA = (
    # superfície comum (L065): o visual é o retângulo do painel; painel reto, contorno 1 px preto, sem sombra
    ".lv{position:fixed;inset:0}"
    ".lv .pn{position:absolute;inset:0;background:#FFFFFF;border:1px solid #0B0B0C;border-radius:16px;"
    "overflow:hidden;color:#0B0B0C}"
    ".lv .sob{display:block;padding-right:40px;color:#6B6B70}"
    ".lv .ach{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;color:#0B0B0C}"
    ".lv .exp{color:#3B3B3F}"
    ".lv .dst{background:#E9E0CF}"
    ".lv .dst b{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;white-space:nowrap;"
    "font-variant-numeric:tabular-nums}"
    ".lv .dst span{color:#3B3B3F}"
    ".lv .sec>.vs{display:block;margin-bottom:6px;color:#6B6B70}"
    # 4.1 · completa em duas colunas (v2: 1004 × 631; esquerda 560, divisor, direita 340)
    ".pn-obras{padding:28px}"
    ".pn-obras .cols{display:grid;grid-template-columns:560px 1px 1fr;column-gap:24px;height:100%}"
    ".pn-obras .div{display:block;background:#E1E1E1}"
    ".pn-obras .ach{margin-top:9px;font-size:23px;line-height:28px}"
    ".pn-obras .exp{margin-top:12px;font-size:17px;line-height:26px}"
    ".pn-obras .dst{margin-top:18px;display:grid;grid-template-columns:repeat(3,1fr);column-gap:16px;"
    "padding:18px 20px}"
    ".pn-obras .dst b{display:block;font-size:34px;line-height:40px}"
    ".pn-obras .dst span{display:block;margin-top:6px;font-size:14px;line-height:19px}"
    ".pn-obras .sec{margin-top:22px}"
    ".pn-obras .oqe{font-size:15px;line-height:21px}"
    ".pn-obras .dir .sub{margin-top:7px;font-size:14px;line-height:19px;color:#3B3B3F}"
    ".pn-obras .dir .sec{margin-top:24px}"
    ".pn-obras .cl{font-size:14px;line-height:19px;color:#3B3B3F}"
    ".lv .bp{position:relative;margin-top:14px}"
    f".lv .bp .r{{display:grid;grid-template-columns:{NOME_OBRAS}px 1fr;align-items:center;height:30px}}"
    ".lv .bp .r b{font-size:15px;font-weight:600;white-space:nowrap}"
    ".lv .bp .r .tr{position:relative;height:10px;background:#EFEFEF}"
    ".lv .bp .r .tr i{position:absolute;left:0;top:0;bottom:0;display:block}"
    ".lv .bp .r .tr i.s2{background:#C43737}"
    ".lv .bp .r .tr i.s1{background:#C9821F}"
    ".lv .bp .r .tr i.s0{background:#A9CDB9}"
    # pendente (nota): obtidos em cinza e o que já dá para calcular num contorno tracejado
    ".lv .bp .r .tr i.sm{background:#CFCCC6}"
    ".lv .bp .r .tr u{position:absolute;left:0;top:-2px;height:14px;border:1px dashed #3B3B3F;box-sizing:border-box}"
    ".lv .bp .lim{position:absolute;top:0;width:0;border-left:1px dashed #3B3B3F;transform-origin:top;"
    "animation:lvLim .4s ease-out backwards}"
    "@keyframes lvLim{from{transform:scaleY(0)}}"
    ".lv .bp .lr{position:absolute;font-size:13px;line-height:16px;color:#6B6B70;white-space:nowrap;"
    "transform:translateX(-50%)}"
    # as duas linhas da nota ficam perto (49 px): o rótulo da atenção encosta à esquerda da linha, o do estável à direita
    ".lv .bp .lr.la{transform:translateX(calc(-100% - 4px))}.lv .bp .lr.le{transform:translateX(4px)}"
    # 4.2 e 4.3 · condensadas (v2: 464 de largura; margens 20)
    ".pn-peq{padding:20px}"
    ".pn-peq .ach{margin-top:9px;font-size:21px;line-height:26px}"
    ".pn-peq .exp{margin-top:10px;font-size:15px;line-height:21px}"
    ".pn-meses .exp{margin-top:8px;font-size:14px;line-height:19px}"
    ".pn-peq .dst-l{margin-top:14px;padding:12px 16px}"
    ".pn-meses .dst-l{margin-top:10px}"
    ".lv .dl{display:grid;grid-template-columns:112px 1fr;column-gap:12px;align-items:baseline;margin-top:4px}"
    ".lv .dl:first-child{margin-top:0}"
    ".lv .dl b{text-align:right;font-size:21px;line-height:26px}"
    ".lv .dl span{font-size:14px;line-height:19px}"
    ".pn-peq .sec{margin-top:16px}"
    ".pn-peq .oqe{font-size:14px;line-height:19px}"
    "@media (prefers-reduced-motion:reduce){.lv .bp .lim{animation:none}}"
) + CSS_X

if __name__ == "__main__":
    from desenho_comum import HACH, dax_lit  # noqa: E402
    desenho("T1 · Leitura · CSS", "CSS das leituras do \"?\" da Tela 01 (sobre o painel: superfície, completa em duas "
            "colunas, condensadas) e do guia da página.",
            "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(f":root{{--hach:{HACH}}}" + CSS_LEITURA))
    sys.exit(gravar([x for x in MEDIDAS if x.nome not in RETIRADAS], RAIZ / "dax" / "T1" / "Leituras", GERADO))

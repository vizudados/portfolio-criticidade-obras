#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""contas_t3 — contas da Tela 03 · Avanço físico (pbi/dax/T3/**/Contas). A tela é de uma obra em foco (dObraFoco, sem
escolha a que mais perde pontos na nota: [Nota · obra em foco]) nos cartões, na curva S e no ritmo do mês, e da carteira no avanço das obras e na
linha do tempo. Quase tudo vem de base/ (contas · ref, · foco e · foco no mês); aqui fica o que é próprio da tela.
Todas levam o prefixo "T3 ·" para não colidir com as contas que as Telas 02 e 04 criam ao mesmo tempo.

Famílias (pasta T3 Avanço físico\\<bloco>\\Contas):
  Obra em foco     identidade da obra em foco (início, término, código, tipo de orçamento, aba)
  Foco no mês      a obra em foco no mês do eixo (desvio, status do físico na nota, fluxo de caixa, justificativa)
  Status do físico [T3 · Status desvio físico]: o item prazo da nota em dois estados, 0 dentro do limite
                   (ganha o ponto) e 2 fora dele; vazio sem previsto. Compara os pontos com os possíveis do item,
                   então nenhum limite fica escrito aqui.
  Série            os meses com aba da obra na janela (de [Série · primeiro mês] à referência; dJanela no drawer):
                   quantos, posição, extremos, tendências, sequências, desde quando. Tudo o que descreve a série
                   olha só a janela; mês anterior, valor da referência e status de hoje não mudam com ela.
  Avanço           posição na lista, contagens e listas da carteira (leitura do avanço)
  Linha do tempo   escala, posição, cadastro (cronograma) e listas da leitura da linha do tempo

Oráculo: mockup/data/criticidade-obras.json (obras[].ultimo, obras[].serie[], proximas[], carteira) — docs/06-interacoes-spec-t3.md §7.

    python -X utf8 pbi/scripts/contas_t3.py
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from contas_lib_projeto import Medida, gravar  # noqa: E402

RAIZ = AQUI.parent
GERADO = "pbi/scripts/contas_t3.py"
F = "fAnaliseCritica"
RS = '"R$" #,0.00;-"R$" #,0.00;"R$" 0.00'
PCT = "0.00%"
PP = "+0.00;-0.00;0.00"
INT = "0"
TXT = "texto"
DATA = "dd/mm/yyyy"
MEDIDAS: list[Medida] = []

# Retiradas do modelo em 08/10/2026 (auditoria: dependencias-pos-telas.json e dependencias-final.json, chave mortas).
# Nenhum visual alcança estas contas e nenhum script de QA as lê (o conferir_contas.py, que lia as 16 'Criticidade ·
# … · ref' e o rótulo, saiu do projeto nesta data). Fora da gravação: o gerador não escreve o nome e apaga o .dax que
# tinha escrito antes. Para reativar, tire o nome do conjunto.
RETIRADAS = {
    # F3 (28/10/2026): sem leitor depois que o Ritmo do mês virou o PPC mês a mês, o cartão do término virou o término
    # projetado e o avanço passou a falar de atraso em meses
    "T3 · Avanço · obras com previsto",
    "T3 · Desvio do desembolso · foco no mês",
    "T3 · Executado no mês · mês anterior · foco no mês",
    "T3 · Foco · tipo de orçamento",
    "T3 · Justificativa exigida · foco no mês",
    "T3 · Justificativa · foco no mês",
    "T3 · Orçamento · foco no mês",
    "T3 · Pontos do fluxo de caixa · foco no mês",
    "T3 · Possíveis do fluxo de caixa · foco no mês",
    "T3 · Previsto no mês · mês anterior · foco no mês",
    "T3 · Ritmo · maior % do mês · foco",
    "T3 · Ritmo · meses com previsto · foco",
    "T3 · Série · mês do maior desvio",
    "T3 · Série · mês do menor desvio",
    "T3 · Série · previsto no mês · máximo · foco",
    "T3 · Série · previsto no mês · mínimo · foco",
    "T3 · Série · previsto no primeiro mês · foco",
    "T3 · Avanço · obras à frente (lista)",          # integração da Fase 2: nenhum visual lê mais (mapa de dependências)
    "T3 · Avanço · obras no previsto (lista)",
    "T3 · Foco · aba",
    "T3 · Foco · código",
    "T3 · Físico · lado do cronograma · foco no mês",
    "T3 · Justificativa em branco · foco no mês",
    "T3 · Ritmo · abaixo do previsto em toda a série · foco",
    "T3 · Série · executado no mês · máximo · foco",
    "T3 · Série · executado no mês · mínimo · foco",
    "T3 · Série · posição do mês",
    "T3 · Série · posição do mês · foco no mês",
    # 13/10/2026 · troca da régua pela nota (artefato plano-nota-painel, Fase 2): a mobilização e a régua de 5 indicadores
    # saem. O status do físico passa a ser o do item prazo da nota ([T3 · Status desvio físico], binário).
    "T3 · Mobilização · foco no mês",
    "T3 · Pontos sem trava · foco no mês",
    "T3 · Status do desembolso · foco no mês",
    "T3 · Mobilização · início da sequência",
    "T3 · Indicador · início da sequência",
    "T3 · Físico · é o sinal crítico de maior peso · foco",
    "T3 · Avanço · obra mais no começo · em mobilização",
    "T3 · Avanço · obras fora da faixa do físico",
    "T3 · Avanço · obras críticas no físico (lista)",
    "T3 · Avanço · obras em atenção perto do fim (lista)",
    "T3 · Avanço · obras em atenção no meio (lista)",
    "T3 · Avanço · obras em atenção no começo (lista)",
    "T3 · Tooltip linha · sinais críticos (lista)",
}


P_FOCO = r"T3 Avanço físico\Obra em foco\Contas"
P_MES = r"T3 Avanço físico\Foco no mês\Contas"
P_SERIE = r"T3 Avanço físico\Série\Contas"
P_AVANCO = r"T3 Avanço físico\Avanço das sete obras\Contas"
P_LINHA = r"T3 Avanço físico\Linha do tempo das obras\Contas"
P_LEI = r"T3 Avanço físico\Leituras\Contas"
P_PPC = r"T3 Avanço físico\PPC mês a mês\Contas"
P_PRAZO = r"T3 Avanço físico\Prazo\Contas"


def m(nome, pasta, formato, descricao, dax, oraculo=""):
    MEDIDAS.append(Medida(nome, pasta, formato, descricao, dax.strip("\n"), oraculo))


def foco(base: str) -> str:
    """[base] para a obra em foco da nota (troca só a coluna da obra; o mês fica o do contexto)."""
    return f"""VAR _obra = [Nota · obra em foco]
RETURN
    CALCULATE ( [{base}], dObra[Obra] = _obra )"""


def ref(base: str) -> str:
    """[base] no mês de referência (troca só o mês; a obra fica a do contexto)."""
    return f"""VAR _mes = [Mês de referência]
RETURN
    CALCULATE ( [{base}], REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )"""


def no_mes(expr: str, desloc: int = 0) -> str:
    """Expressão avaliada no mês da linha (dMes[Mes] de uma tabela de meses), sem os outros filtros de mês."""
    alvo = "_m" if desloc == 0 else f"EDATE ( _m, {desloc} )"
    return f"VAR _m = dMes[Mes] RETURN CALCULATE ( {expr}, REMOVEFILTERS ( dMes ), dMes[Mes] = {alvo} )"


def meses_ate(fim: str, colunas: list[tuple[str, str]]) -> str:
    """VAR _jan e VAR _meses: os meses da janela (de [Série · primeiro mês] até `fim`) com as colunas pedidas, cada uma
    avaliada no mês da linha. A janela vem do drawer (dJanela: 12, 9, 6 ou 3 meses até a referência, nunca antes de
    jan/26): toda conta da série que descreve o que a tela mostra olha só esses meses."""
    cols = ",\n".join(f'        "{c}", {e}' for c, e in colunas)
    return f"""VAR _jan = [Série · primeiro mês]
VAR _meses =
    ADDCOLUMNS (
        FILTER ( ALL ( dMes[Mes] ), dMes[Mes] >= _jan && dMes[Mes] <= {fim} ),
{cols}
    )"""


def lado(d: str) -> str:
    """Lado do cronograma pelo desvio em p.p. arredondado a uma casa (como a tela mostra): −1 atrás, 0 no previsto,
    1 à frente; vazio sem desvio (obra sem previsto na planilha)."""
    return f"IF ( NOT ISBLANK ( {d} ), SIGN ( ROUND ( {d}, 1 ) ) )"


EXEC = "[Físico · executado acumulado]"           # tem valor = a obra tem aba no mês

# ===================================================================================================== obra em foco
for nome, col, desc in (("início", "Inicio", "Início da obra em foco (cadastro)."),
                        ("término previsto", "TerminoPrevisto", "Término previsto da obra em foco (cadastro).")):
    m(f"T3 · Foco · {nome}", P_FOCO, DATA, desc,
      f"""VAR _obra = [Nota · obra em foco]
RETURN
    LOOKUPVALUE ( dObra[{col}], dObra[Obra], _obra )""", f"obras[].{'inicio' if col == 'Inicio' else 'termino_previsto'}")
m("T3 · Foco · código", P_FOCO, TXT, "Código do empreendimento da obra em foco (AT).",
  """VAR _obra = [Nota · obra em foco]
RETURN
    LOOKUPVALUE ( dObra[Codigo], dObra[Obra], _obra )""", "obras[].codigo")
m("T3 · Foco · tipo de orçamento", P_FOCO, TXT,
  "Tipo do orçamento da obra em foco na aba do mês de referência, curto e minúsculo (preliminar).",
  foco("Tipo de orçamento · ref"), "obras[].tipo_orcamento")
m("T3 · Foco · aba", P_FOCO, TXT, "Aba da obra em foco no mês de referência (JUN26).", foco("Aba · ref"),
  "obras[].ultimo.aba")

# ===================================================================================================== status do físico na nota
m("T3 · Status desvio físico", P_MES, INT,
  "Status do físico pelo item prazo da Nota da obra, na obra e no mês do contexto: 0 quando o atraso em meses fica "
  "dentro da faixa cheia (ganha todos os pontos), 2 quando perde pontos; vazio sem curva prevista ou sem aba. "
  "Compara os pontos do item com o máximo dele ([T3 · Prazo · máximo na nota]), sem limite escrito. Uma obra no "
  "contexto.",
  """IF (
    HASONEVALUE ( dObra[Obra] ),
    VAR _pts = [Nota · pontos prazo]
    RETURN
        IF ( NOT ISBLANK ( _pts ), IF ( _pts < [T3 · Prazo · máximo na nota], 2, 0 ) )
)""",
  "conferir_real.py · oráculo da nota (coluna F-F)")
m("T3 · Status desvio físico · ref", P_MES, INT, "[T3 · Status desvio físico] no mês de referência.",
  ref("T3 · Status desvio físico"))
m("T3 · Status desvio físico · foco", P_MES, INT,
  "[T3 · Status desvio físico] da obra em foco da nota, no mês de referência.",
  """VAR _obra = [Nota · obra em foco]
RETURN
    CALCULATE ( [T3 · Status desvio físico · ref], dObra[Obra] = _obra )""")
m("T3 · Prazo · máximo na nota", P_MES, "0.0#",
  "Quanto o prazo (atraso em meses) vale na Nota da obra ([Nota · item · máximo] do item prazo: 2).",
  """CALCULATE ( [Nota · item · máximo], dItemNota[Item] = "prazo" )""", "dItemNota[Maximo] (2)")

# ===================================================================================================== foco no mês do eixo
m("T3 · Aba · foco no mês", P_MES, TXT, "Aba da obra em foco no mês do eixo (MAIO26).",
  f"""VAR _obra = [Nota · obra em foco]
RETURN
    CALCULATE ( SELECTEDVALUE ( {F}[Aba] ), dObra[Obra] = _obra )""", "obras[].serie[].aba")
for nome, base, fmt, orac in (
        ("Orçamento · foco no mês", "Orçamento", RS, "obras[].serie[].orcamento"),
        ("Desvio físico p.p. · foco no mês", "Físico · desvio acumulado p.p.", PP,
         "obras[].serie[].indicadores.desvio_fisico_pp"),
        ("Status desvio físico · foco no mês", "T3 · Status desvio físico", INT, "oráculo da nota (coluna F-F)"),
        ("Desvio do desembolso · foco no mês", "Desembolso · desvio no mês", PCT,
         "obras[].serie[].indicadores.desvio_desembolso"),
        ("Pontos do fluxo de caixa · foco no mês", "Nota · pontos caixa", "0.0#", "oráculo da nota (Fluxo)"),
        ("Possíveis do fluxo de caixa · foco no mês", "Nota · possíveis · caixa", "0.0#",
         "oráculo da nota (máximo do Fluxo com dado)"),
        ("Justificativa · foco no mês", "Justificativa do desembolso", TXT, "obras[].serie[].justificativa"),
        ("Justificativa exigida · foco no mês", "Justificativa · exigida", INT, "obras[].ultimo.justificativa_exigida"),
        ("Justificativa em branco · foco no mês", "Justificativa · em branco", INT,
         "obras[].ultimo.justificativa_ausente")):
    m(f"T3 · {nome}", P_MES, fmt, f"[{base}] da obra em foco no mês do eixo (tooltips do mês).", foco(base), orac)

# mês anterior ao do contexto (obra do contexto) e as versões da obra em foco
ANT = [("Desvio físico p.p. · mês anterior", "Físico · desvio acumulado p.p.", PP),
       ("Status desvio físico · mês anterior", "T3 · Status desvio físico", INT),
       ("Executado no mês · mês anterior", "Físico · executado no mês", PCT),
       ("Previsto no mês · mês anterior", "Físico · previsto no mês", PCT),
       ("Executado acumulado · mês anterior", "Físico · executado acumulado", PCT)]
for nome, base, fmt in ANT:
    m(f"T3 · {nome}", P_MES, fmt, f"[{base}] no mês anterior ao do contexto (vazio sem aba nesse mês).",
      f"""VAR _m = EDATE ( MAX ( dMes[Mes] ), -1 )
RETURN
    CALCULATE ( [{base}], REMOVEFILTERS ( dMes ), dMes[Mes] = _m )""", "obras[].serie[m-1]")
    m(f"T3 · {nome} · foco no mês", P_MES, fmt, f"[T3 · {nome}] da obra em foco.", foco(f"T3 · {nome}"))
m("T3 · Status desvio físico · mês anterior · ref", P_MES, INT,
  "Status do físico na nota (dentro ou fora do limite) da obra do contexto no mês anterior ao de referência.",
  ref("T3 · Status desvio físico · mês anterior"), "oráculo da nota (coluna F-F, mês anterior)")

# ===================================================================================================== série da obra
# A série de uma obra = os meses da janela (de [Série · primeiro mês] até a referência) em que ela tem aba. Uma obra no
# contexto. A janela vem do drawer (dJanela: 12, 9, 6 ou 3 meses; padrão 12; nunca antes de jan/26).
m("T3 · Série · meses da obra", P_SERIE, INT,
  "Meses com aba da obra do contexto na janela, do primeiro mês da janela ao de referência (8 na REDINHA em ago/26 "
  "com a janela de 12; 3 na TIROL).",
  "VAR _ref = [Mês de referência]\n" + meses_ate("_ref", [("@e", no_mes(EXEC))]) + """
RETURN
    COUNTROWS ( FILTER ( _meses, NOT ISBLANK ( [@e] ) ) )""", "len(obras[].serie)")
m("T3 · Série · primeiro mês da obra", P_SERIE, DATA,
  "Primeiro mês com aba da obra do contexto na janela (jan/26; jun/26 na TIROL; o primeiro mês da janela quando a "
  "obra já tinha aba antes dela).",
  "VAR _ref = [Mês de referência]\n" + meses_ate("_ref", [("@e", no_mes(EXEC))]) + """
RETURN
    MINX ( FILTER ( _meses, NOT ISBLANK ( [@e] ) ), dMes[Mes] )""", "obras[].serie[0].mes")
m("T3 · Obra · primeira aba", P_SERIE, DATA,
  "Primeiro mês com aba da obra do contexto em todo o histórico até a referência (não depende da janela): é o "
  "'PRIMEIRA ABA DA OBRA' do tooltip.",
  f"""VAR _ref = [Mês de referência]
RETURN
    CALCULATE ( MIN ( {F}[Mes] ), REMOVEFILTERS ( dMes ), dMes[Mes] <= _ref )""", "obras[].serie[0].mes")
m("T3 · Série · mês na série", P_SERIE, INT,
  "1 quando o mês do eixo está na janela (do primeiro mês da janela à referência) e a obra do contexto tem aba nele; "
  "vazio fora da série (L044).",
  f"""VAR _mes = MAX ( dMes[Mes] )
VAR _tem = NOT ISBLANK ( {EXEC} )
RETURN
    IF ( _mes >= [Série · primeiro mês] && _mes <= [Mês de referência] && _tem, 1 )""")
m("T3 · Série · posição do mês", P_SERIE, INT,
  "Posição do mês do eixo entre os meses com aba da obra do contexto na janela (1 = primeiro); vazio fora da série.",
  "VAR _mes = MAX ( dMes[Mes] )\n" + meses_ate("_mes", [("@e", no_mes(EXEC))]) + """
RETURN
    IF ( [T3 · Série · mês na série] = 1, COUNTROWS ( FILTER ( _meses, NOT ISBLANK ( [@e] ) ) ) )""")
m("T3 · Série · posição da aba anterior", P_SERIE, INT,
  "Posição na janela ([Série · posição na janela]) do último mês com aba da obra do contexto antes do mês do eixo; 0 "
  "quando não há (o primeiro mês da obra na janela). Diz quantos lugares vazios ficam antes da coluna do mês (TIROL "
  "em jun/26 na janela de jan a ago: 0, com cinco meses vazios antes).",
  "VAR _mes = MAX ( dMes[Mes] )\nVAR _ant = EDATE ( _mes, -1 )\n" + meses_ate("_ant", [("@e", no_mes(EXEC))]) + """
VAR _prev = MAXX ( FILTER ( _meses, NOT ISBLANK ( [@e] ) ), dMes[Mes] )
RETURN
    IF (
        [T3 · Série · mês na série] = 1,
        IF ( ISBLANK ( _prev ), 0, DATEDIFF ( _jan, _prev, MONTH ) + 1 )
    )""")

for nome, base, fun, desc in (
        ("executado no mês · mínimo", "Físico · executado no mês", "MINX", "Menor % executado no mês"),
        ("executado no mês · máximo", "Físico · executado no mês", "MAXX", "Maior % executado no mês"),
        ("previsto no mês · mínimo", "Físico · previsto no mês", "MINX", "Menor % previsto para o mês"),
        ("previsto no mês · máximo", "Físico · previsto no mês", "MAXX", "Maior % previsto para o mês")):
    m(f"T3 · Série · {nome}", P_SERIE, PCT, f"{desc} na série da obra do contexto, na janela (meses sem o valor na "
      "planilha ficam de fora).",
      "VAR _ref = [Mês de referência]\n" + meses_ate("_ref", [("@v", no_mes(f"[{base}]"))]) + f"""
RETURN
    {fun} ( FILTER ( _meses, NOT ISBLANK ( [@v] ) ), [@v] )""",
      f"{'min' if fun == 'MINX' else 'max'}(obras[].serie[].{'exec' if 'exec' in base else 'prev'}_mes)")
for nome, base, ext, desc in (
        ("mês de menor executado", "Físico · executado no mês", "T3 · Série · executado no mês · mínimo",
         "Primeiro mês da série (na janela) com o menor % executado no mês (o mês mais fraco)."),
        ("mês de maior executado", "Físico · executado no mês", "T3 · Série · executado no mês · máximo",
         "Primeiro mês da série (na janela) com o maior % executado no mês (o melhor mês).")):
    m(f"T3 · Série · {nome}", P_SERIE, DATA, desc,
      "VAR _ref = [Mês de referência]\n" + f"VAR _alvo = [{ext}]\n" + meses_ate("_ref", [("@v", no_mes(f"[{base}]"))])
      + """
RETURN
    MINX ( FILTER ( _meses, NOT ISBLANK ( [@v] ) && [@v] = _alvo ), dMes[Mes] )""", "obras[].serie[] (mês do extremo)")

for nome, base, fun, desc in (
        ("mês do maior desvio", "Físico · desvio acumulado p.p.", "MAXX", "maior desvio físico acumulado"),
        ("mês do menor desvio", "Físico · desvio acumulado p.p.", "MINX", "menor desvio físico acumulado"),
        ("mês do maior atraso", "Prazo · atraso (meses)", "MAXX", "maior atraso em meses"),
        ("mês do menor atraso", "Prazo · atraso (meses)", "MINX", "menor atraso em meses"),
        ("mês do maior executado acumulado", "Físico · executado acumulado", "MAXX", "maior executado acumulado"),
        ("mês do menor executado acumulado", "Físico · executado acumulado", "MINX", "menor executado acumulado")):
    m(f"T3 · Série · {nome}", P_SERIE, DATA,
      f"Primeiro mês da janela com o {desc} da obra do contexto (o rótulo do máximo e do mínimo no mini gráfico do "
      "tooltip do avanço quando os rótulos não cabem todos).",
      "VAR _ref = [Mês de referência]\n" + meses_ate("_ref", [("@v", no_mes(f"[{base}]"))]) + f"""
VAR _com = FILTER ( _meses, NOT ISBLANK ( [@v] ) )
VAR _alvo = {fun} ( _com, [@v] )
RETURN
    MINX ( FILTER ( _com, [@v] = _alvo ), dMes[Mes] )""", "obras[].serie[] (mês do extremo)")

m("T3 · Mês · destaque no ritmo", P_SERIE, TXT,
  "Posição do mês do contexto na série da obra na janela (estado de negócio): exec_min (o mês mais fraco), exec_max "
  "(o melhor mês), prev_max (o maior previsto), prev_min (o menor previsto), nessa ordem; vazio quando não é extremo "
  "ou quando a obra tem menos de três meses na janela (o 'em n meses' não diria nada).",
  """VAR _e = [Físico · executado no mês]
VAR _p = [Físico · previsto no mês]
VAR _n = [T3 · Série · meses da obra]
RETURN
    IF (
        NOT ISBLANK ( _e ) && _n >= 3,
        SWITCH (
            TRUE (),
            _e = [T3 · Série · executado no mês · mínimo], "exec_min",
            _e = [T3 · Série · executado no mês · máximo], "exec_max",
            NOT ISBLANK ( _p ) && _p = [T3 · Série · previsto no mês · máximo], "prev_max",
            NOT ISBLANK ( _p ) && _p = [T3 · Série · previsto no mês · mínimo], "prev_min"
        )
    )""", "spec §3.1 (detalhe 'o mês mais fraco em n meses')")
COM_P = [("@e", no_mes("[Físico · executado no mês]")), ("@p", no_mes("[Físico · previsto no mês]"))]
m("T3 · Ritmo · abaixo do previsto em toda a série", P_SERIE, INT,
  "1 quando o executado do mês ficou abaixo do previsto em todos os meses da janela que trazem o previsto (obra do "
  "contexto); 0 senão; vazio quando nenhum mês traz o previsto.",
  "VAR _ref = [Mês de referência]\n" + meses_ate("_ref", COM_P) + """
VAR _serie = FILTER ( _meses, NOT ISBLANK ( [@e] ) && NOT ISBLANK ( [@p] ) )
RETURN
    IF ( COUNTROWS ( _serie ) > 0, IF ( COUNTROWS ( FILTER ( _serie, [@e] >= [@p] ) ) = 0, 1, 0 ) )""",
  "obras[].serie[].exec_mes < prev_mes")
m("T3 · Ritmo · meses que alcançaram o previsto", P_SERIE, INT,
  "Meses da janela em que o executado do mês alcançou o previsto (executado ≥ previsto; só meses com previsto na "
  "planilha). Obra do contexto.",
  "VAR _ref = [Mês de referência]\n" + meses_ate("_ref", COM_P) + """
RETURN
    COUNTROWS ( FILTER ( _meses, NOT ISBLANK ( [@e] ) && NOT ISBLANK ( [@p] ) && [@e] >= [@p] ) ) + 0""",
  "contagem de obras[].serie[] com exec_mes >= prev_mes")
m("T3 · Ritmo · meses com previsto", P_SERIE, INT,
  "Meses da série da obra do contexto, na janela, que trazem o previsto do mês na planilha (a JANGADA traz só jan/26).",
  "VAR _ref = [Mês de referência]\n" + meses_ate("_ref", COM_P) + """
RETURN
    COUNTROWS ( FILTER ( _meses, NOT ISBLANK ( [@e] ) && NOT ISBLANK ( [@p] ) ) ) + 0""")
for nome, base, cod_sobe, cod_desce, cod_resto, desc in (
        ("tendência do previsto", "Físico · previsto no mês", "acelera", "desacelera", "varia",
         "O que o cronograma pede mês a mês: acelera (o previsto do mês nunca cai e sobe ao menos uma vez), desacelera, "
         "constante ou varia."),
        ("tendência do executado", "Físico · executado no mês", "cresce", "cai", "oscila",
         "Como o executado do mês andou: cresce (nunca cai), cai (nunca sobe) ou oscila.")):
    m(f"T3 · Ritmo · {nome}", P_SERIE, TXT, desc + " Pares de meses seguidos dentro da janela; obra do contexto.",
      "VAR _ref = [Mês de referência]\n" + meses_ate("_ref", [("@v", no_mes(f"[{base}]")),
                                                            ("@a", no_mes(f"[{base}]", -1))]) + f"""
VAR _pares = FILTER ( _meses, dMes[Mes] > _jan && NOT ISBLANK ( [@v] ) && NOT ISBLANK ( [@a] ) )
VAR _sobe = COUNTROWS ( FILTER ( _pares, ROUND ( [@v] - [@a], 6 ) > 0 ) ) + 0
VAR _desce = COUNTROWS ( FILTER ( _pares, ROUND ( [@v] - [@a], 6 ) < 0 ) ) + 0
RETURN
    IF (
        COUNTROWS ( _pares ) > 0,
        SWITCH (
            TRUE (),
            _sobe > 0 && _desce = 0, "{cod_sobe}",
            _desce > 0 && _sobe = 0, "{cod_desce}",
            _sobe = 0 && _desce = 0, "constante",
            "{cod_resto}"
        )
    )""", f"obras[].serie[].{'prev' if 'previsto' in base else 'exec'}_mes")
for nome, cond, desc in (("executa abaixo desde", "[@e] < [@p]", "abaixo do previsto"),
                         ("executa acima desde", "[@e] >= [@p]", "no previsto ou acima")):
    m(f"T3 · Ritmo · {nome}", P_SERIE, DATA,
      f"Primeiro mês da sequência, terminada na referência, em que o executado do mês ficou {desc} (vazio quando a "
      "referência não está nessa condição ou não traz o previsto). Meses da janela com previsto; obra do contexto.",
      "VAR _ref = [Mês de referência]\n" + meses_ate("_ref", COM_P) + f"""
VAR _serie = FILTER ( _meses, NOT ISBLANK ( [@e] ) && NOT ISBLANK ( [@p] ) )
VAR _quebra = MAXX ( FILTER ( _serie, NOT ( {cond} ) ), dMes[Mes] )
VAR _inicio = MINX ( FILTER ( _serie, ISBLANK ( _quebra ) || dMes[Mes] > _quebra ), dMes[Mes] )
VAR _naRef = COUNTROWS ( FILTER ( _serie, dMes[Mes] = _ref && {cond} ) ) > 0
RETURN
    IF ( _naRef, _inicio )""", "sinal de obras[].serie[].exec_mes − prev_mes")

# ---- desvio físico: status na nota (dentro ou fora do limite) e distância (uma obra no contexto; meses da janela)
STATUS_FIS = "[T3 · Status desvio físico]"
DESVIO = "[Físico · desvio acumulado p.p.]"
m("T3 · Físico · meses seguidos na faixa", P_SERIE, INT,
  "Quantos meses seguidos, terminando no mês do contexto e dentro da janela, o físico da obra ficou do mesmo lado do "
  "limite da nota ([T3 · Status desvio físico]: 3 = 'terceiro mês seguido dentro do limite').",
  f"""VAR _mes = MAX ( dMes[Mes] )
VAR _s = {STATUS_FIS}
""" + meses_ate("_mes", [("@s", no_mes(STATUS_FIS))]) + """
VAR _com = FILTER ( _meses, NOT ISBLANK ( [@s] ) )
VAR _quebra = MAXX ( FILTER ( _com, [@s] <> _s ), dMes[Mes] )
RETURN
    IF ( NOT ISBLANK ( _s ), COUNTROWS ( FILTER ( _com, ISBLANK ( _quebra ) || dMes[Mes] > _quebra ) ) )""",
  "oráculo da nota (coluna F-F, sequência)")
m("T3 · Físico · meses seguidos na faixa · foco no mês", P_MES, INT,
  "[T3 · Físico · meses seguidos na faixa] da obra em foco.", foco("T3 · Físico · meses seguidos na faixa"))
m("T3 · Físico · meses seguidos na faixa · ref", P_SERIE, INT,
  "[T3 · Físico · meses seguidos na faixa] no mês de referência.", ref("T3 · Físico · meses seguidos na faixa"))

DELTA = ('VAR _comDelta = ADDCOLUMNS ( _serie, "@sg", IF ( ISBLANK ( [@a] ) || dMes[Mes] = _jan, BLANK (), '
         'SIGN ( ROUND ( ABS ( [@d] ) - ABS ( [@a] ), 3 ) ) ) )')
m("T3 · Físico · tendência da distância", P_SERIE, TXT,
  "Como a distância ao cronograma (|desvio físico|) anda até a referência, dentro da janela: cresce ou cai quando os "
  "dois últimos meses ou mais vão no mesmo sentido; oscila quando o último mês inverteu o sentido. Uma obra no "
  "contexto.",
  "VAR _ref = [Mês de referência]\n" + meses_ate("_ref", [("@d", no_mes(DESVIO)), ("@a", no_mes(DESVIO, -1))]) + f"""
VAR _serie = FILTER ( _meses, NOT ISBLANK ( [@d] ) )
{DELTA}
VAR _sgRef = MAXX ( FILTER ( _comDelta, dMes[Mes] = _ref ), [@sg] )
VAR _quebra = MAXX ( FILTER ( _comDelta, ISBLANK ( [@sg] ) || [@sg] <> _sgRef ), dMes[Mes] )
VAR _passos = DATEDIFF ( _quebra, _ref, MONTH )
RETURN
    IF (
        NOT ISBLANK ( _sgRef ),
        SWITCH ( TRUE (), _passos >= 2 && _sgRef > 0, "cresce", _passos >= 2 && _sgRef < 0, "cai", "oscila" )
    )""", "obras[].serie[].indicadores.desvio_fisico_pp (|d| mês a mês)")
m("T3 · Físico · tendência da distância desde", P_SERIE, DATA,
  "Mês de partida da tendência da distância ao cronograma (o último mês antes da sequência; com 'oscila', o primeiro "
  "mês da série na janela). 'A distância cresce todo mês desde janeiro'.",
  "VAR _ref = [Mês de referência]\n" + meses_ate("_ref", [("@d", no_mes(DESVIO)), ("@a", no_mes(DESVIO, -1))]) + f"""
VAR _serie = FILTER ( _meses, NOT ISBLANK ( [@d] ) )
{DELTA}
VAR _sgRef = MAXX ( FILTER ( _comDelta, dMes[Mes] = _ref ), [@sg] )
VAR _quebra = MAXX ( FILTER ( _comDelta, ISBLANK ( [@sg] ) || [@sg] <> _sgRef ), dMes[Mes] )
VAR _passos = DATEDIFF ( _quebra, _ref, MONTH )
RETURN
    IF ( NOT ISBLANK ( _sgRef ), IF ( _passos >= 2, _quebra, MINX ( _serie, dMes[Mes] ) ) )""")
m("T3 · Físico · lado do cronograma", P_SERIE, INT,
  "Lado do cronograma pelo desvio físico acumulado arredondado a uma casa, como a tela mostra: −1 atrás, 0 no "
  "previsto (previsto igual ao executado na planilha), 1 à frente; vazio sem previsto (JANGADA). Obra do contexto.",
  "VAR _d = " + DESVIO + "\nRETURN\n    " + lado("_d"), "sinal de obras[].serie[].indicadores.desvio_fisico_pp")
m("T3 · Físico · lado do cronograma · ref", P_SERIE, INT,
  "[T3 · Físico · lado do cronograma] no mês de referência.", ref("T3 · Físico · lado do cronograma"))
LADO = lado("[@d]")
m("T3 · Físico · sinal · início da sequência", P_SERIE, DATA,
  "Primeiro mês da sequência, terminada na referência e dentro da janela, em que a obra ficou do mesmo lado do "
  "cronograma (atrás, no previsto ou à frente: [T3 · Físico · lado do cronograma]). 'Atrás desde fevereiro'.",
  "VAR _ref = [Mês de referência]\n" + meses_ate("_ref", [("@d", no_mes(DESVIO))]) + f"""
VAR _serie = ADDCOLUMNS ( FILTER ( _meses, NOT ISBLANK ( [@d] ) ), "@l", {LADO} )
VAR _ladoRef = MAXX ( FILTER ( _serie, dMes[Mes] = _ref ), [@l] )
VAR _quebra = MAXX ( FILTER ( _serie, [@l] <> _ladoRef ), dMes[Mes] )
RETURN
    IF ( NOT ISBLANK ( _ladoRef ), MINX ( FILTER ( _serie, ISBLANK ( _quebra ) || dMes[Mes] > _quebra ), dMes[Mes] ) )""",
  "sinal de obras[].serie[].indicadores.desvio_fisico_pp")
for nome, fim_ret, desc in (
        ("sinal · início da sequência anterior", "MINX ( FILTER ( _antes, ISBLANK ( _quebra ) || dMes[Mes] > _quebra ), "
         "dMes[Mes] )", "Primeiro mês da sequência anterior (de outro lado do cronograma) à que termina na referência, "
         "dentro da janela; vazio quando a obra ficou do mesmo lado em toda a série. 'Atrás em janeiro; à frente desde "
         "fevereiro'."),
        ("lado da sequência anterior", "_ladoAntes", "Lado do cronograma (−1, 0, 1) da sequência anterior à que termina "
         "na referência, dentro da janela; vazio quando não há.")):
    m(f"T3 · Físico · {nome}", P_SERIE, DATA if "início" in nome else INT, desc,
      "VAR _ref = [Mês de referência]\nVAR _ini = [T3 · Físico · sinal · início da sequência]\n"
      + meses_ate("_ref", [("@d", no_mes(DESVIO))]) + f"""
VAR _antes = ADDCOLUMNS ( FILTER ( _meses, NOT ISBLANK ( [@d] ) && dMes[Mes] < _ini ), "@l", {LADO} )
VAR _ladoAntes = MAXX ( FILTER ( _antes, dMes[Mes] = EDATE ( _ini, -1 ) ), [@l] )
VAR _quebra = MAXX ( FILTER ( _antes, [@l] <> _ladoAntes ), dMes[Mes] )
RETURN
    IF ( NOT ISBLANK ( _ladoAntes ), {fim_ret} )""")
m("T3 · Físico · maior status na série", P_SERIE, INT,
  "Pior status do físico na nota na série da obra do contexto, na janela (0 = sempre dentro do limite; 2 = passou "
  "dele em algum mês).",
  "VAR _ref = [Mês de referência]\n" + meses_ate("_ref", [("@s", no_mes(STATUS_FIS))]) + """
RETURN
    MAXX ( _meses, [@s] )""", "oráculo da nota (coluna F-F, pior mês)")
m("T3 · Físico · mudanças de faixa (lista)", P_SERIE, TXT,
  "Cada vez que o físico da obra do contexto cruzou o limite da nota, dentro da janela, da mais antiga à mais nova, "
  "separadas por '|': mês por extenso § mês abreviado § status de antes § status novo (0 dentro, 2 fora) § meses no "
  "status novo (até a mudança seguinte ou até a referência). Mudança vinda de antes da janela não conta.",
  "VAR _ref = [Mês de referência]\n" + meses_ate("_ref", [("@s", no_mes(STATUS_FIS)), ("@a", no_mes(STATUS_FIS, -1))])
  + """
VAR _mud = FILTER ( _meses, dMes[Mes] > _jan && NOT ISBLANK ( [@s] ) && NOT ISBLANK ( [@a] ) && [@s] <> [@a] )
VAR _lista =
    ADDCOLUMNS (
        _mud,
        "@prox", VAR _m = dMes[Mes] RETURN MINX ( FILTER ( _mud, dMes[Mes] > _m ), dMes[Mes] )
    )
RETURN
    CONCATENATEX (
        _lista,
        FORMAT ( dMes[Mes], "mmmm", "pt-BR" ) & "§" & FORMAT ( dMes[Mes], "mmm", "pt-BR" ) & "§" & [@a] & "§" & [@s]
            & "§" & DATEDIFF ( dMes[Mes], COALESCE ( [@prox], EDATE ( _ref, 1 ) ), MONTH ),
        "|",
        dMes[Mes], ASC
    )""", "oráculo da nota (coluna F-F, mudanças)")

# ---- status da obra na nota: desde quando (uma obra no contexto, mês de referência)
# pendente (−1) quebra a sequência; sempre num mês só (CALCULATE com dMes[Mes] = …): a leitura de um mês, sem a medida
# de reserva no plano (integração da Fase 2, desempenho; o mesmo valor, provado em pbi/qa/nota/provar_leituras_rapidas.py)
ST_ADO = "IF ( [Nota · pendente · um mês] = 1, -1, [Nota · status · um mês] )"
m("T3 · Status · início da sequência", P_SERIE, DATA,
  "Primeiro mês da sequência, terminada na referência e dentro da janela, em que a obra ficou no status da nota de hoje "
  "('crítica desde abril'); o mês pendente conta como um estado à parte, então passar de pendente a crítico abre uma "
  "sequência nova. Uma obra no contexto.",
  f"""VAR _ref = [Mês de referência]
VAR _hoje = CALCULATE ( {ST_ADO}, REMOVEFILTERS ( dMes ), dMes[Mes] = _ref )
""" + meses_ate("_ref", [("@s", no_mes(ST_ADO))]) + """
VAR _com = FILTER ( _meses, NOT ISBLANK ( [@s] ) )
VAR _quebra = MAXX ( FILTER ( _com, [@s] <> _hoje ), dMes[Mes] )
VAR _inicio = MINX ( FILTER ( _com, ISBLANK ( _quebra ) || dMes[Mes] > _quebra ), dMes[Mes] )
RETURN
    IF ( NOT ISBLANK ( _hoje ), _inicio )""", "oráculo da nota (status e pendente, sequência)")

# ---- versões da obra em foco (cartões, curva S, ritmo e as leituras deles)
FOCO_SERIE = ["T3 · Série · meses da obra", "T3 · Série · primeiro mês da obra", "T3 · Série · mês na série",
              "T3 · Série · posição do mês", "T3 · Série · executado no mês · mínimo",
              "T3 · Série · executado no mês · máximo", "T3 · Série · previsto no mês · mínimo",
              "T3 · Série · previsto no mês · máximo", "T3 · Série · mês de menor executado",
              "T3 · Série · mês de maior executado", "T3 · Mês · destaque no ritmo",
              "T3 · Ritmo · abaixo do previsto em toda a série", "T3 · Ritmo · meses que alcançaram o previsto",
              "T3 · Ritmo · tendência do previsto", "T3 · Ritmo · tendência do executado",
              "T3 · Ritmo · executa abaixo desde", "T3 · Ritmo · executa acima desde",
              "T3 · Físico · tendência da distância", "T3 · Físico · tendência da distância desde",
              "T3 · Físico · maior status na série", "T3 · Físico · mudanças de faixa (lista)",
              "T3 · Série · posição da aba anterior", "T3 · Obra · primeira aba", "T3 · Ritmo · meses com previsto",
              "T3 · Físico · lado do cronograma",
              # o "desde" do atraso na leitura da curva não começa antes do 1º mês atrás do cronograma (Fase 3, r3)
              "T3 · Físico · sinal · início da sequência"]
FMT = {x.nome: x.formato for x in MEDIDAS}
for base in FOCO_SERIE:
    nome = base + (" · foco no mês" if base in ("T3 · Série · mês na série", "T3 · Série · posição do mês",
                                                 "T3 · Mês · destaque no ritmo", "T3 · Série · posição da aba anterior",
                                                 "T3 · Físico · lado do cronograma") else " · foco")
    m(nome, P_SERIE, FMT[base], f"[{base}] da obra em foco.", foco(base))
m("T3 · Mês · destaque no ritmo · ref", P_SERIE, TXT,
  "[T3 · Mês · destaque no ritmo] no mês de referência (obra do contexto: tooltip do avanço).",
  ref("T3 · Mês · destaque no ritmo"))

m("T3 · Ritmo · maior % do mês · foco", P_SERIE, PCT,
  "Maior % previsto ou executado num mês da série da obra em foco, na janela (escala das colunas do Ritmo do mês).",
  "VAR _ref = [Mês de referência]\n" + meses_ate("_ref", [("@p", no_mes("[Físico · previsto no mês · foco no mês]")),
                                                        ("@e", no_mes("[Físico · executado no mês · foco no mês]"))])
  + """
RETURN
    MAXX ( _meses, MAX ( [@p], [@e] ) )""", "max(obras[0].serie[].prev_mes, exec_mes) = 3,33%")
m("T3 · Curva S · desvio no primeiro mês · foco", P_SERIE, PP,
  "Desvio físico da obra em foco no primeiro mês da série (−0,6 p.p. em janeiro).",
  """VAR _ini = [T3 · Série · primeiro mês da obra · foco]
RETURN
    CALCULATE ( [T3 · Desvio físico p.p. · foco no mês], REMOVEFILTERS ( dMes ), dMes[Mes] = _ini )""",
  "obras[0].serie[0].indicadores.desvio_fisico_pp")
m("T3 · Curva S · status no primeiro mês · foco", P_SERIE, INT,
  "Status do físico na nota (dentro ou fora do limite) da obra em foco no primeiro mês da série.",
  """VAR _ini = [T3 · Série · primeiro mês da obra · foco]
RETURN
    CALCULATE ( [T3 · Status desvio físico · foco no mês], REMOVEFILTERS ( dMes ), dMes[Mes] = _ini )""",
  "oráculo da nota (coluna F-F, primeiro mês)")
for nome, base in (("executado no mês de menor executado · foco", "T3 · Série · mês de menor executado · foco"),
                   ("executado no mês de maior executado · foco", "T3 · Série · mês de maior executado · foco")):
    m(f"T3 · Série · {nome}", P_SERIE, PCT, f"% executado da obra em foco no mês de [{base}].",
      f"""VAR _mes = [{base}]
RETURN
    CALCULATE ( [Físico · executado no mês · foco no mês], REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )""",
      "obras[0].serie[].exec_mes (extremo)")
m("T3 · Série · previsto no primeiro mês · foco", P_SERIE, PCT,
  "% previsto para o mês da obra em foco no primeiro mês da série (2,49% em janeiro).",
  """VAR _ini = [T3 · Série · primeiro mês da obra · foco]
RETURN
    CALCULATE ( [Físico · previsto no mês · foco no mês], REMOVEFILTERS ( dMes ), dMes[Mes] = _ini )""",
  "obras[0].serie[0].prev_mes")

# ---- justificativas do desembolso (o que explica a curva S)
JUS = [("@d", no_mes("[Desembolso · desvio no mês]")), ("@j", no_mes("TRIM ( [Justificativa do desembolso] )"))]
m("T3 · Justificativas · grupos (lista)", P_LEI, TXT,
  "Justificativas da planilha nos meses em que o desembolso passou do previsto (série da obra do contexto, na "
  "janela), agrupadas pelo texto, da mais repetida à menos: texto § meses, separadas por '|'.",
  "VAR _ref = [Mês de referência]\n" + meses_ate("_ref", JUS) + """
VAR _acima = FILTER ( _meses, [@d] > 0 && [@j] <> "" )
VAR _textos = DISTINCT ( SELECTCOLUMNS ( _acima, "@t", [@j] ) )
VAR _cont = ADDCOLUMNS ( _textos, "@n", VAR _t = [@t] RETURN COUNTROWS ( FILTER ( _acima, [@j] = _t ) ) )
RETURN
    CONCATENATEX ( _cont, SUBSTITUTE ( SUBSTITUTE ( [@t], "|", "/" ), "§", "" ) & "§" & [@n], "|", [@n], DESC, [@t], ASC )""",
  "obras[].serie[].justificativa (contagem dos textos iguais)")
m("T3 · Justificativas · meses acima do previsto", P_LEI, INT,
  "Meses da série da obra do contexto, na janela, em que o desembolso passou do previsto.",
  "VAR _ref = [Mês de referência]\n" + meses_ate("_ref", JUS) + """
RETURN
    COUNTROWS ( FILTER ( _meses, [@d] > 0 ) ) + 0""", "obras[].serie[].indicadores.desvio_desembolso > 0")
for base in ("T3 · Justificativas · grupos (lista)", "T3 · Justificativas · meses acima do previsto"):
    m(base + " · foco", P_LEI, FMT.get(base, TXT if "lista" in base else INT), f"[{base}] da obra em foco.", foco(base))

# ===================================================================================================== avanço das obras
m("T3 · Avanço · posição", P_AVANCO, INT,
  "Posição da obra na lista do avanço: a ordem da nota (mais pontos perdidos no mês de referência; empate pela menor "
  "nota, a pendente depois, e pelo nome), lida de [T1 · Obras · posição] sem recalcular. Uma obra no contexto; vazio "
  "sem aba no mês.",
  "[T1 · Obras · posição]", "conferir_real.py · oráculo da nota (lista por pontos perdidos)")
m("T3 · Avanço · é a obra em foco", P_AVANCO, INT,
  "1 na linha da obra em foco (a escolhida no drawer ou a que mais perde pontos na nota, sem o filtro da própria "
  "linha); 0 nas outras.",
  """VAR _obra = SELECTEDVALUE ( dObra[Obra] )
VAR _foco = CALCULATE ( [Nota · obra em foco], REMOVEFILTERS ( dObra[Obra] ) )
RETURN
    IF ( _obra = _foco, 1, 0 )""", "obras[0].obra (REDINHA)")

# colunas que pesam (o status do físico na nota e a posição da nota, que compara todas as obras) só entram quando a
# condição ou a ordem as usa
EXTRAS = {"@s": "[T3 · Status desvio físico · ref]", "@pos": "[T3 · Avanço · posição]",
          "@a": "[Prazo · atraso (meses) · ref]", "@sit": "[T3 · Término · situação · ref]"}


def obras_ref(*usos: str) -> str:
    """VAR _obras: as obras com aba no mês de referência e as colunas da carteira; @s, @pos, @a (atraso em meses) e
    @sit (situação do término projetado) só quando `usos` cita."""
    extras = "".join(f',\n            "{c}", {e}' for c, e in EXTRAS.items() if any(f"[{c}]" in u for u in usos))
    return f"""VAR _obras =
    FILTER (
        ADDCOLUMNS (
            VALUES ( dObra[Obra] ),
            "@e", [Físico · executado acumulado · ref],
            "@d", [Físico · desvio acumulado p.p. · ref],
            "@ini", [Obra · início],
            "@fim", [Obra · término previsto],
            "@orc", [Orçamento · ref],
            "@tipo", [Tipo de orçamento · ref]{extras}
        ),
        NOT ISBLANK ( [@e] )
    )"""


OBRAS_REF = obras_ref()


def lista(nome, pasta, desc, cond, ordem, orac=""):
    m(nome, pasta, TXT, desc + " Obras com aba no mês de referência, separadas por '|'.",
      obras_ref(cond, ordem) + f"""
RETURN
    CONCATENATEX ( FILTER ( _obras, {cond} ), dObra[Obra], "|", {ordem}, dObra[Obra], ASC )""", orac)


def contagem(nome, pasta, desc, cond, orac=""):
    m(nome, pasta, INT, desc + " Obras com aba no mês de referência.",
      obras_ref(cond) + f"""
RETURN
    COUNTROWS ( FILTER ( _obras, {cond} ) ) + 0""", orac)


def extremo(nome, pasta, fmt, desc, col, ordem, cond="TRUE ()", valor=None, orac=""):
    """Obra (texto) ou valor (`valor` = coluna) da primeira obra de `_obras` pela ordem pedida."""
    m(nome, pasta, fmt, desc,
      obras_ref(cond, col, valor or "") + f"""
VAR _top = TOPN ( 1, FILTER ( _obras, {cond} ), {col}, {ordem}, dObra[Obra], ASC )
RETURN
    MAXX ( _top, {valor or 'dObra[Obra]'} )""", orac)


contagem("T3 · Avanço · obras atrás do cronograma", P_AVANCO,
         "Obras atrás do cronograma: atraso em meses (cronograma agregado) acima de zero na casa decimal que a tela "
         "mostra.", "ROUND ( [@a], 1 ) > 0", "nota_previa.csv x_atraso > 0 (set/26: 7)")
contagem("T3 · Avanço · obras com atraso calculado", P_AVANCO,
         "Obras com o atraso em meses calculado (curva prevista e executado no mês de referência).",
         "NOT ISBLANK ( [@a] )", "nota_previa.csv x_atraso preenchido (set/26: 7)")
contagem("T3 · Avanço · obras fora do limite do físico", P_AVANCO,
         "Obras cujo atraso físico passa do limite do item prazo da nota (perdem os pontos do item).",
         "[@s] = 2", "oráculo da nota (coluna F-F = 0)")
lista("T3 · Avanço · obras fora do limite do físico (lista)", P_AVANCO,
      "Obras cujo atraso em meses passa do ponto cheio do item prazo da nota, do maior atraso para o menor.",
      "[@s] = 2", "[@a], DESC", "nota_previa.csv pts_atraso < 2")
lista("T3 · Avanço · obras à frente (lista)", P_AVANCO,
      "Obras com desvio físico acumulado positivo (na casa decimal que a tela mostra), da mais adiantada para a menos.",
      "ROUND ( [@d], 1 ) > 0", "[@d], DESC")
lista("T3 · Avanço · obras no previsto (lista)", P_AVANCO,
      "Obras com o executado igual ao previsto acumulado (desvio 0,0 p.p.), pela ordem da lista.",
      "NOT ISBLANK ( [@d] ) && ROUND ( [@d], 1 ) = 0", "[@pos], ASC")
lista("T3 · Avanço · obras sem previsto (lista)", P_AVANCO,
      "Obras cuja aba do mês de referência não traz o previsto acumulado (JANGADA): ficam fora do desvio da carteira.",
      "ISBLANK ( [@d] )", "[@pos], ASC")
contagem("T3 · Avanço · obras com previsto", P_AVANCO,
         "Obras com o previsto acumulado na aba do mês de referência (as que entram no desvio da carteira).",
         "NOT ISBLANK ( [@d] )")
m("T3 · Avanço · executado acumulado das obras com previsto", P_AVANCO, PCT,
  "Executado acumulado da carteira no mês de referência só com as abas que trazem o previsto, ponderado pelo orçamento "
  "como o previsto e o desvio da carteira (sem a JANGADA): o 'executado × previsto' da leitura compara o mesmo grupo.",
  f"""VAR _mes = [Mês de referência]
RETURN
    CALCULATE (
        [Físico · executado acumulado],
        REMOVEFILTERS ( dMes ),
        dMes[Mes] = _mes,
        FILTER (
            ALL ( {F}[PrevAcum], {F}[ExecAcum] ),
            NOT ISBLANK ( {F}[PrevAcum] ) && NOT ISBLANK ( {F}[ExecAcum] )
        )
    )""", "carteira.exec_acum_ponderado (obras com previsto)")
extremo("T3 · Avanço · obra de menor atraso", P_AVANCO, TXT, "Obra com o menor atraso em meses no mês de "
        "referência (a mais adiantada quando há atraso negativo).", "[@a]", "ASC", cond="NOT ISBLANK ( [@a] )",
        orac="nota_previa.csv min(x_atraso) set/26 → PONTA NEGRA")
extremo("T3 · Avanço · menor atraso", P_AVANCO, "0.0", "Menor atraso em meses entre as obras no mês de referência.",
        "[@a]", "ASC", cond="NOT ISBLANK ( [@a] )", valor="[@a]", orac="PONTA NEGRA 0,66")
m("T3 · Avanço · obra mais no começo", P_AVANCO, TXT,
  "Obra com o menor % executado acumulado no mês de referência.",
  OBRAS_REF + """
RETURN
    MAXX ( TOPN ( 1, _obras, [@e], ASC, dObra[Obra], ASC ), dObra[Obra] )""", "min(executado acumulado) → TIROL")
m("T3 · Avanço · executado da obra mais no começo", P_AVANCO, PCT,
  "% executado acumulado da [T3 · Avanço · obra mais no começo].",
  """VAR _obra = [T3 · Avanço · obra mais no começo]
RETURN
    CALCULATE ( [Físico · executado acumulado · ref], dObra[Obra] = _obra )""", "TIROL exec_acum 3,6%")

# ===================================================================================================== linha do tempo
SITUACOES = '{ "Em andamento", "A iniciar" }'
m("T3 · Obra · situação", P_LINHA, TXT, "Situação da obra no cadastro (Em andamento, A iniciar, Concluída).",
  "SELECTEDVALUE ( dObra[Situacao] )", "obras[].situacao · proximas[]")
m("T3 · Obra · SPE", P_LINHA, TXT, "SPE da obra (cadastro).", "SELECTEDVALUE ( dObra[SPE] )", "obras[].spe")
m("T3 · Obra · m² NBR", P_LINHA, "#,0", "Área da obra em m² NBR (cadastro).", "SELECTEDVALUE ( dObra[M2] )",
  "obras[].m2_nbr · proximas[].m2_nbr")
m("T3 · cronograma · versão", P_LINHA, TXT,
  "Versão da cronograma dos campos do cadastro, em mês e ano curtos (abr/26), a partir de dObra[VersaoCrono] (MM/AAAA da "
  "planilha de versão mais recente). Vazio sem cronograma.",
  """VAR _v = FIRSTNONBLANK ( dObra[VersaoCrono], 1 )
RETURN
    IF (
        ISBLANK ( _v ),
        BLANK (),
        MID (
            "janfevmarabrmaijunjulagosetoutnovdez",
            ( VALUE ( LEFT ( _v, 2 ) ) - 1 ) * 3 + 1,
            3
        ) & "/" & RIGHT ( _v, 2 )
    )""", "abr/26 (cronograma 04/2026)")
m("T3 · Obra · orçamento cronograma", P_LINHA, RS, "Orçamento da obra na cronograma, da versão do cadastro (T3 · cronograma · versão; obras a iniciar).",
  "SELECTEDVALUE ( dObra[OrcamentoCrono] )", "proximas[].orcamento_crono")
m("T3 · Obra · tipo de orçamento cronograma", P_LINHA, TXT, "Tipo do orçamento na cronograma, minúsculo (legal).",
  "LOWER ( SELECTEDVALUE ( dObra[TipoOrcamentoCrono] ) )", "proximas[].tipo_orcamento")
m("T3 · Linha do tempo · posição", P_LINHA, INT,
  "Ordem da obra na linha do tempo: as em andamento na ordem do avanço (as sem aba no mês depois delas, pelo início); "
  "depois as a iniciar, pelo início previsto. Vazio para as concluídas.",
  """VAR _sit = SELECTEDVALUE ( dObra[Situacao] )
VAR _obra = SELECTEDVALUE ( dObra[Obra] )
VAR _ini = SELECTEDVALUE ( dObra[Inicio] )
VAR _pos = [T3 · Avanço · posição]
VAR _mesma =
    CALCULATETABLE (
        SUMMARIZE ( dObra, dObra[Obra], dObra[Inicio] ),
        REMOVEFILTERS ( dObra[Obra] ),
        dObra[Situacao] = _sit
    )
VAR _antes = COUNTROWS ( FILTER ( _mesma, dObra[Inicio] < _ini || ( dObra[Inicio] = _ini && dObra[Obra] < _obra ) ) ) + 0
RETURN
    SWITCH (
        TRUE (),
        _sit = "Em andamento", IF ( NOT ISBLANK ( _pos ), _pos, 50 + _antes ),
        _sit = "A iniciar", 100 + _antes
    )""", "ordem de obras[] + proximas[] (Figma 277:1261…1297)")
m("T3 · Linha do tempo · linhas", P_LINHA, INT,
  "Quantas obras a Linha do tempo desenha no recorte do visual (posição, início e término preenchidos): a altura de "
  "cada linha sai daí (F4, a lista ocupa o painel inteiro).",
  """VAR _obras =
    CALCULATETABLE (
        ADDCOLUMNS (
            VALUES ( dObra[Obra] ),
            "@pos", [T3 · Linha do tempo · posição],
            "@ini", [Obra · início],
            "@fim", [Obra · término previsto]
        ),
        ALLSELECTED ( dObra[Obra] )
    )
RETURN
    COUNTROWS ( FILTER ( _obras, NOT ISBLANK ( [@pos] ) && NOT ISBLANK ( [@ini] ) && NOT ISBLANK ( [@fim] ) ) ) + 0""",
  "7 em set/26 (as sete obras em andamento)")
m("T3 · Linha do tempo · primeiro início", P_LINHA, DATA,
  "Início mais antigo entre as obras em andamento e a iniciar (escala).",
  f"""CALCULATE (
    MIN ( dObra[Inicio] ),
    REMOVEFILTERS ( dObra[Obra] ),
    dObra[Situacao] IN {SITUACOES}
)""", "min(cronograma início) out/23")
m("T3 · Linha do tempo · último término", P_LINHA, DATA,
  "O mês mais distante que a linha do tempo desenha (escala): o término previsto, a entrega com a tolerância de 180 "
  "dias e o término projetado no mês de referência, entre as obras em andamento e a iniciar.",
  f"""VAR _obras =
    CALCULATETABLE (
        ADDCOLUMNS (
            VALUES ( dObra[Obra] ),
            "@f", [Obra · término previsto],
            "@t", [Prazo · entrega com tolerância],
            "@p", [Prazo · término projetado · ref]
        ),
        REMOVEFILTERS ( dObra[Obra] ),
        dObra[Situacao] IN {SITUACOES}
    )
RETURN
    MAX ( MAXX ( _obras, [@f] ), MAX ( MAXX ( _obras, [@t] ), MAXX ( _obras, [@p] ) ) )""",
  "TIROL: tolerância jul/29 (set/26)")

A_INICIAR = """VAR _aIniciar =
    CALCULATETABLE (
        ADDCOLUMNS (
            VALUES ( dObra[Obra] ),
            "@ini", [Obra · início],
            "@tipo", [T3 · Obra · tipo de orçamento cronograma]
        ),
        REMOVEFILTERS ( dObra[Obra] ),
        dObra[Situacao] = "A iniciar"
    )"""
m("T3 · Linha do tempo · obras a iniciar", P_LINHA, INT, "Obras a iniciar no cadastro (cronograma).",
  A_INICIAR + "\nRETURN\n    COUNTROWS ( _aIniciar ) + 0", "len(proximas) = 4")
A_INICIAR_TELA = """VAR _aIniciar =
    CALCULATETABLE (
        ADDCOLUMNS (
            VALUES ( dObra[Obra] ),
            "@ini", [Obra · início]
        ),
        dObra[Situacao] = "A iniciar"
    )"""
m("T3 · Linha do tempo · obras a iniciar (lista)", P_LINHA, TXT,
  "Obras a iniciar que a tela lista, no contexto do visual (a mesma regra e ordem da tabela da leitura), pelo início "
  "previsto, separadas por '|'. Ex.: CANDELÁRIA|LAGOA NOVA (nomes ilustrativos).",
  A_INICIAR_TELA + '\nRETURN\n    CONCATENATEX ( _aIniciar, dObra[Obra], "|", [@ini], ASC, dObra[Obra], ASC )',
  "proximas[].obra")
m("T3 · Linha do tempo · tipo das obras a iniciar", P_LINHA, TXT,
  "Tipo de orçamento das obras a iniciar quando é o mesmo em todas (legal); vazio quando varia.",
  A_INICIAR + """
VAR _tipos = DISTINCT ( SELECTCOLUMNS ( _aIniciar, "@t", [@tipo] ) )
RETURN
    IF ( COUNTROWS ( _tipos ) = 1, MAXX ( _tipos, [@t] ) )""", "proximas[].tipo_orcamento")
m("T3 · Linha do tempo · último início a iniciar", P_LINHA, DATA, "Início previsto da última obra a iniciar (out/26).",
  A_INICIAR + "\nRETURN\n    MAXX ( _aIniciar, [@ini] )", "max(proximas[].inicio_previsto)")

extremo("T3 · Linha do tempo · obra mais antiga", P_LINHA, TXT, "Obra em andamento com o início mais antigo.",
        "[@ini]", "ASC", orac="PONTA NEGRA (set/23)")
extremo("T3 · Linha do tempo · primeiro início em andamento", P_LINHA, DATA,
        "Início mais antigo entre as obras em andamento.", "[@ini]", "ASC", valor="[@ini]", orac="set/23")
extremo("T3 · Linha do tempo · obra de término mais distante", P_LINHA, TXT,
        "Obra em andamento com o término previsto mais distante.", "[@fim]", "DESC", orac="TIROL (jan/29)")
extremo("T3 · Linha do tempo · término mais distante em andamento", P_LINHA, DATA,
        "Término previsto mais distante entre as obras em andamento.", "[@fim]", "DESC", valor="[@fim]", orac="jan/29")
extremo("T3 · Linha do tempo · obra de maior orçamento", P_LINHA, TXT,
        "Obra em andamento com o maior orçamento na aba do mês de referência.", "[@orc]", "DESC", orac="DUNAS")
extremo("T3 · Linha do tempo · maior orçamento", P_LINHA, RS,
        "Maior orçamento entre as obras em andamento (aba do mês de referência).", "[@orc]", "DESC", valor="[@orc]",
        orac="DUNAS 26.104.300")
m("T3 · Linha do tempo · obra que termina no mês", P_LINHA, TXT,
  "Obra em andamento cujo término previsto é o mês de referência (a de início mais antigo, se houver mais de uma).",
  "VAR _ref = [Mês de referência]\n" + OBRAS_REF + """
RETURN
    MAXX ( TOPN ( 1, FILTER ( _obras, [@fim] = _ref ), [@ini], ASC, dObra[Obra], ASC ), dObra[Obra] )""",
  "obras[] com termino_previsto = mes_ref → PONTA NEGRA")
m("T3 · Linha do tempo · próxima a terminar", P_LINHA, TXT,
  "Obra em andamento com o término previsto mais próximo depois do mês de referência.",
  "VAR _ref = [Mês de referência]\n" + OBRAS_REF + """
RETURN
    MAXX ( TOPN ( 1, FILTER ( _obras, [@fim] > _ref ), [@fim], ASC, dObra[Obra], ASC ), dObra[Obra] )""",
  "POTENGI (jan/27)")
m("T3 · Linha do tempo · término da próxima a terminar", P_LINHA, DATA,
  "Término previsto da [T3 · Linha do tempo · próxima a terminar].",
  """VAR _obra = [T3 · Linha do tempo · próxima a terminar]
RETURN
    LOOKUPVALUE ( dObra[TerminoPrevisto], dObra[Obra], _obra )""", "jan/27")
lista("T3 · Linha do tempo · obras no começo (lista)", P_LINHA,
      "Obras mais novas que mal começaram: menos de 25% executado e início nos 12 meses antes do mês de referência, "
      "pelo início.", "[@e] < 0.25 && [@ini] >= EDATE ( [Mês de referência], -12 )", "[@ini], ASC", "JANGADA|TIROL")
m("T3 · Linha do tempo · obras perto do fim com atraso (lista)", P_LINHA, TXT,
  "Obras com 70% ou mais executado, atrás do cronograma e com término depois do mês de referência, pelo término. "
  "Obras com aba no mês de referência, separadas por '|'.",
  "VAR _ref = [Mês de referência]\n" + OBRAS_REF + """
RETURN
    CONCATENATEX ( FILTER ( _obras, [@e] >= 0.70 && [@d] < 0 && [@fim] > _ref ), dObra[Obra], "|", [@fim], ASC, dObra[Obra], ASC )""",
  "POTENGI")
m("T3 · Linha do tempo · término da primeira perto do fim", P_LINHA, DATA,
  "Término previsto da primeira obra de [T3 · Linha do tempo · obras perto do fim com atraso (lista)].",
  """VAR _obra = PATHITEM ( [T3 · Linha do tempo · obras perto do fim com atraso (lista)], 1 )
RETURN
    LOOKUPVALUE ( dObra[TerminoPrevisto], dObra[Obra], _obra )""", "POTENGI jan/27")
m("T3 · Linha do tempo · obras com atraso cedo (lista)", P_LINHA, TXT,
  "Obras atrás do cronograma que só terminam dois anos ou mais depois do mês de referência, pelo início. Obras com aba "
  "no mês de referência, separadas por '|'.",
  "VAR _ref = [Mês de referência]\n" + OBRAS_REF + """
RETURN
    CONCATENATEX ( FILTER ( _obras, [@d] < 0 && [@fim] >= EDATE ( _ref, 24 ) ), dObra[Obra], "|", [@ini], ASC, dObra[Obra], ASC )""",
  "REDINHA|JANGADA|TIROL")
m("T3 · Linha do tempo · anos de término com atraso cedo (lista)", P_LINHA, TXT,
  "Anos de término das [T3 · Linha do tempo · obras com atraso cedo (lista)], sem repetir, separados por '|'.",
  "VAR _ref = [Mês de referência]\n" + OBRAS_REF + """
VAR _anos = DISTINCT ( SELECTCOLUMNS ( FILTER ( _obras, [@d] < 0 && [@fim] >= EDATE ( _ref, 24 ) ), "@a", YEAR ( [@fim] ) ) )
RETURN
    CONCATENATEX ( _anos, [@a], "|", [@a], ASC )""", "2028|2029")
# exemplos reais de ago/26 (contagem por tipo de orçamento entre as 6 obras em andamento)
EX_QTD = {"executivo": 3, "preliminar": 3, "legal": 0, "alvo": 0, "final": 0}
for tipo in ("executivo", "preliminar", "legal", "alvo", "final"):
    lista(f"T3 · Linha do tempo · obras com orçamento {tipo} (lista)", P_LINHA,
          f"Obras cujo orçamento na aba do mês de referência é do tipo {tipo}, da mais executada para a menos.",
          f'[@tipo] = "{tipo}"', "[@e], DESC", "obras[].tipo_orcamento")
    contagem(f"T3 · Linha do tempo · obras com orçamento {tipo} (quantidade)", P_LINHA,
             f"Quantas obras têm orçamento do tipo {tipo} na aba do mês de referência (as da lista de {tipo}). "
             f"Ex. ago/26: {EX_QTD[tipo]}.",
             f'[@tipo] = "{tipo}"', "contagem de obras[].tipo_orcamento")
    m(f"T3 · Linha do tempo · orçamento {tipo} · na maioria", P_LINHA, INT,
      f"1 quando as obras com orçamento {tipo} são mais da metade das obras em andamento e há mais de duas (a frase "
      f"'na maioria' da leitura); 0 nos outros casos. Ex. ago/26: {EX_QTD[tipo]} de 6 em andamento → 0.",
      f"""VAR _q = [T3 · Linha do tempo · obras com orçamento {tipo} (quantidade)]
VAR _n = [Obras com análise · ref] + 0
RETURN
    IF ( _q * 2 > _n && _n > 2, 1, 0 )""", "obras[].tipo_orcamento: mais da metade das em andamento")

m("T3 · Tooltip linha · itens que perdem pontos (lista)", P_LINHA, TXT,
  "Itens da nota em que a obra do item perdeu pontos no mês de referência, do que mais perdeu ao que menos (empate "
  "pela ordem do item), pelo nome médio e separados por '|'. Itens sem dado não entram. Ex. de teste ago/26: "
  "REDINHA → Médio Prazo|Fluxo de caixa|… .",
  """VAR _itens =
    FILTER (
        ADDCOLUMNS (
            VALUES ( dItemNota[Item] ),
            "@p", [Nota · item · perdidos · ref],
            "@o", [Nota · item · ordem],
            "@nm", [Nota · item · nome médio]
        ),
        [@p] > 0
    )
RETURN
    CONCATENATEX ( _itens, [@nm], "|", [@p], DESC, [@o], ASC )""",
  "oráculo da nota (itens com pontos abaixo do máximo)")

# ===================================================================================================== prazo: término projetado
# F3 (docs/08 §5): o cartão do término e a linha do tempo dizem onde o término projetado (Lipke, IEAC(t)) cai diante da
# entrega contratual e dos 180 dias de tolerância (Lei 4.591/64, art. 43-A).
m("T3 · Término · situação", P_PRAZO, INT,
  "Onde o término projetado cai, na obra e no mês do contexto: 0 até a entrega contratual, 1 depois dela mas dentro "
  "dos 180 dias de tolerância, 2 depois da tolerância; vazio sem término projetado. Uma obra.",
  """VAR _p = [Prazo · término projetado]
VAR _e = [Prazo · entrega contratual]
VAR _t = [Prazo · entrega com tolerância]
RETURN
    IF (
        NOT ISBLANK ( _p ) && NOT ISBLANK ( _e ),
        SWITCH ( TRUE (), _p <= _e, 0, _p <= _t, 1, 2 )
    )""", "set/26: JANGADA, POTENGI e TIROL 1; as outras 0")
m("T3 · Término · situação · ref", P_PRAZO, INT, "[T3 · Término · situação] no mês de referência.",
  ref("T3 · Término · situação"))
m("T3 · Término · situação · foco", P_PRAZO, INT, "[T3 · Término · situação · ref] da obra em foco.",
  foco("T3 · Término · situação · ref"))
m("T3 · Término · meses além da entrega · foco", P_PRAZO, INT,
  "Meses entre a entrega contratual e o término projetado da obra em foco no mês de referência (negativo: antes da "
  "entrega).",
  """VAR _p = [Prazo · término projetado · foco]
VAR _e = [Prazo · entrega contratual · foco]
RETURN
    IF ( NOT ISBLANK ( _p ) && NOT ISBLANK ( _e ), DATEDIFF ( _e, _p, MONTH ) )""", "REDINHA set/26: 0")
lista("T3 · Linha do tempo · obras depois da entrega (lista)", P_LINHA,
      "Obras cujo término projetado passa da entrega contratual mas fica nos 180 dias de tolerância, pela entrega.",
      "[@sit] = 1", "[@fim], ASC", "set/26: POTENGI|JANGADA|TIROL")
lista("T3 · Linha do tempo · obras além da tolerância (lista)", P_LINHA,
      "Obras cujo término projetado passa dos 180 dias de tolerância depois da entrega contratual, pela entrega.",
      "[@sit] = 2", "[@fim], ASC", "set/26: nenhuma")

# ===================================================================================================== PPC mês a mês
# F3 (docs/08 §5): o Ritmo do mês sai (é a derivada da curva S, que já está no tooltip do mês da curva) e entra o PPC
# da obra em foco mês a mês, com a linha na meta (o ponto cheio do item PPC da nota): o sinal que chega antes do atraso.
PPC_FM = "[Canteiro · PPC · foco no mês]"
JANELA_PPC = """VAR _ref = [Mês de referência]
VAR _ini = [Série · primeiro mês]
VAR _meses = ADDCOLUMNS ( FILTER ( ALL ( dMes[Mes] ), dMes[Mes] >= _ini && dMes[Mes] <= _ref ), "@v", VAR _v = """ + PPC_FM + """ RETURN IF ( NOT ISBLANK ( _v ), ROUND ( _v, 2 ) ) )
VAR _com = FILTER ( _meses, NOT ISBLANK ( [@v] ) )"""
for chave, agreg, desc in (("maior", "MAXX", "o maior"), ("menor", "MINX", "o menor")):
    m(f"T3 · PPC · mês do {chave} · foco", P_PPC, DATA,
      f"Mês da janela com {desc} PPC da obra em foco (empate: o mais recente); vazio sem base.",
      JANELA_PPC + f"""
VAR _x = {agreg} ( _com, [@v] )
RETURN
    MAXX ( FILTER ( _com, [@v] = _x ), dMes[Mes] )""", "dados/_gabarito/nota_previa.csv (x_ppc)")
    m(f"T3 · PPC · {chave} na janela · foco", P_PPC, PCT,
      f"{desc[0].upper() + desc[1:]} PPC da obra em foco nos meses da janela; vazio sem base.",
      JANELA_PPC + f"""
RETURN
    {agreg} ( _com, [@v] )""", "dados/_gabarito/nota_previa.csv (x_ppc)")
m("T3 · PPC · mês com rótulo", P_PPC, INT,
  "1 quando o mês do eixo é o do maior ou o do menor PPC da janela (o desenho escreve o valor nesses meses e no de "
  "referência quando não cabem todos); 0 nos demais.",
  """VAR _m = MAX ( dMes[Mes] )
RETURN
    IF ( HASONEVALUE ( dMes[Mes] ), INT ( _m = [T3 · PPC · mês do maior · foco] || _m = [T3 · PPC · mês do menor · foco] ) )""")
m("T3 · PPC · meses com PPC · foco", P_PPC, INT, "Meses da janela com o PPC da obra em foco na base complementar.",
  JANELA_PPC + """
RETURN
    COUNTROWS ( _com ) + 0""", "dados/_gabarito/nota_previa.csv (x_ppc)")
m("T3 · PPC · meses na meta · foco", P_PPC, INT,
  "Meses da janela em que o PPC da obra em foco chegou à meta (o ponto cheio do item PPC da nota).",
  JANELA_PPC + """
VAR _meta = [Nota · limite PPC · ponto cheio]
RETURN
    COUNTROWS ( FILTER ( _com, [@v] >= _meta ) ) + 0""", "dados/_gabarito/nota_previa.csv (x_ppc ≥ 0,80)")
m("T3 · PPC · abaixo da meta desde · foco", P_PPC, DATA,
  "Primeiro mês da sequência atual de PPC abaixo da meta que chega ao mês de referência (vazio quando o PPC de "
  "referência está na meta).",
  JANELA_PPC + """
VAR _meta = [Nota · limite PPC · ponto cheio]
VAR _ultimoOk = MAXX ( FILTER ( _com, [@v] >= _meta ), dMes[Mes] )
VAR _abaixo = FILTER ( _com, [@v] < _meta && ( ISBLANK ( _ultimoOk ) || dMes[Mes] > _ultimoOk ) )
RETURN
    IF ( MAXX ( FILTER ( _com, dMes[Mes] = _ref ), [@v] ) < _meta, MINX ( _abaixo, dMes[Mes] ) )""",
  "dados/_gabarito/nota_previa.csv (x_ppc)")
m("T3 · PPC · mês anterior · foco no mês", P_PPC, PCT,
  "PPC da obra em foco no mês anterior ao do eixo (vazio sem base nesse mês).",
  f"""VAR _m = EDATE ( MAX ( dMes[Mes] ), -1 )
RETURN
    CALCULATE ( {PPC_FM}, REMOVEFILTERS ( dMes ), dMes[Mes] = _m )""")
m("T3 · PPC · média das obras · ref", P_PPC, PCT,
  "PPC médio das obras com base no mês de referência (média simples, como a carteira lê o PPC).",
  """VAR _mes = [Mês de referência]
RETURN
    CALCULATE ( [Canteiro · PPC], REMOVEFILTERS ( dObra[Obra] ), REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )""",
  "média de x_ppc em set/26")

if __name__ == "__main__":
    sys.exit(gravar([x for x in MEDIDAS if x.nome not in RETIRADAS], RAIZ / "dax" / "T3", GERADO))

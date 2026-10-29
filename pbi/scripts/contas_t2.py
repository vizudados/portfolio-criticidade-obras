#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""contas_t2 — contas da Tela 02 · Análise crítica (pbi/dax/T2/**/Contas). A tela é da obra em foco (dObraFoco; sem
escolha, a que mais perde pontos na nota); quase tudo vem de base/ (contas · foco e · foco no mês). Aqui fica só o que é próprio
da tela: os 10 itens do quadradinho (dItem), a aba e o tipo de orçamento da obra em foco, a ordem dos itens da nota e o
degrau "pago e não aplicado" da cascata. Oráculo: mockup/data/criticidade-obras.json › obras[].ultimo, .composicao, .serie.

    python -X utf8 pbi/scripts/contas_t2.py
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from contas_lib_projeto import Medida, gravar  # noqa: E402

RAIZ = AQUI.parent
GERADO = "pbi/scripts/contas_t2.py"
F = "fAnaliseCritica"
RS = '"R$" #,0.00;-"R$" #,0.00;"R$" 0.00'
PCT = "0.00%"
MEDIDAS: list[Medida] = []

# Retiradas do modelo em 08/10/2026 (auditoria: dependencias-pos-telas.json e dependencias-final.json, chave mortas).
# Nenhum visual alcança estas contas e nenhum script de QA as lê (o conferir_contas.py, que lia as 16 'Criticidade ·
# … · ref' e o rótulo, saiu do projeto nesta data). Fora da gravação: o gerador não escreve o nome e apaga o .dax que
# tinha escrito antes. Para reativar, tire o nome do conjunto.
RETIRADAS = {
    # F3 (docs/08 §5): contas que só o quadradinho, o mês a mês antigo e as leituras deles liam
    "Cascata · pago e não aplicado · foco no mês",
    "Cascata · resultado sem o degrau · foco",
    "Item · % do orçamento · foco",
    "Item · linha · descrição · foco",
    "Item · linha · valor · foco",
    "Quadradinho · itens com valor · foco",
    "T2 · Leitura quadradinho · itens com valor (lista) · foco",
    "T2 · Leitura quadradinho · itens que nunca tiveram valor (lista) · foco",
    "T2 · Leitura quadradinho · itens que zeraram no mês (lista) · foco",
    "T2 · Leitura · estoque no primeiro mês · foco",
    "T2 · Leitura · menor variação do período · foco",
    "T2 · Leitura · meses com alta do estoque · foco",
    "T2 · Leitura · meses com alta do resultado · foco",
    "T2 · Leitura · meses com queda do resultado · foco",
    "T2 · Leitura · meses com sem estoque negativo · foco",
    "T2 · Leitura · resultado % no primeiro mês · foco",
    "T2 · Leitura · resultado no primeiro mês · foco",
    "T2 · Tooltip mês · grupos de ativos com valor · foco no mês",
    # F3 (docs/08 §5): o mês a mês da T2 virou o IDC (uma série só)
    "T2 · Mês a mês · máximo positivo", "T2 · Mês a mês · máximo negativo",
    "T2 · Mês a mês · mês do maior valor", "T2 · Mês a mês · mês do menor valor",
    "T2 · Mês a mês · série do maior valor", "T2 · Mês a mês · série do menor valor",
    "T2 · Mês a mês · resultado no mês do maior valor", "T2 · Mês a mês · resultado no mês do menor valor",
    "T2 · Mês a mês · sem estoque no mês do maior valor", "T2 · Mês a mês · sem estoque no mês do menor valor",
    "Ativos não consumidos · foco no mês",
    "Item · % do orçamento · foco no mês",
    "T2 · Leitura · ativos no primeiro mês · foco",
    "T2 · Leitura · meses com queda do estoque · foco",
    "T2 · Leitura · sinais estáveis · foco",
    "T2 · Leitura · sinais que mudaram · foco",
    # Fase 2 da régua antiga (13/10/2026): a régua antiga sai da tela (sinais, mobilização, faixas de dIndicador). As contas que
    # liam Criticidade · / Indicador · / dIndicador deixaram de ser escritas; o nome fica aqui como registro.
    "Criticidade · sinais críticos · foco",
    "Criticidade · sinais em atenção · foco",
    "T2 · Sinais · posição",
    "T2 · Sinais · pontos da obra",
    "Indicador · faixa do status · foco",
    "Criticidade · status desembolso · foco no mês",
    "Criticidade · em mobilização · foco no mês",
    "Indicador · valor · foco no mês",
    "Indicador · status · foco no mês",
    "Indicador · valor · mês anterior · foco",
    "Indicador · status · mês anterior · foco",
    "T2 · Leitura · pontos sem trava · foco",
    "T2 · Leitura · 1º sinal crítico · foco",
    "T2 · Leitura · 2º sinal crítico · foco",
    "T2 · Leitura · sinais críticos de ritmo · foco",
    "T2 · Tooltip indicador · meses na série · foco",
    "T2 · Tooltip indicador · comparações mês a mês · foco",
    "T2 · Tooltip indicador · comparações em que piorou · foco",
    "T2 · Tooltip indicador · todos os meses estáveis · foco",
    # trocadas por uma lista só (a obra em foco lida uma vez), na otimização da leitura de itens (13/10/2026)
    "T2 · Leitura · 1º item que mais perde · foco",
    "T2 · Leitura · 2º item que mais perde · foco",
    "T2 · Leitura · itens que perdem pontos · foco",
}



def m(nome, pasta, formato, descricao, dax, oraculo=""):
    MEDIDAS.append(Medida(nome, pasta, formato, descricao, dax, oraculo))


FOCO_OBRA = """VAR _obra = [Nota · obra em foco]
RETURN
    CALCULATE ( [{base}], dObra[Obra] = _obra )"""

# ------------------------------------------------------------------------------------------------ o quadradinho
QUAD = r"T2 Análise crítica\O quadradinho\Contas"
ITENS = [("Credito", "Crédito do orçamento"), ("SaldoContrato", "Saldo de contrato"),
         ("AdiantServicos", "Adiantamento de serviços"), ("AdiantMateriais", "Adiantamento de materiais"),
         ("Estoque", "Estoque de materiais"), ("Equipamentos", "Equipamentos (valor de mercado)"),
         ("ReceitaPersonalizacao", "Receita de personalizações"), ("ContasPagar", "Contas a pagar"),
         ("Desembolsado", "Desembolsado acumulado"), ("Divida", "Dívida da obra")]
casos = ",\n".join(f'    "{c}", [{n}]' for c, n in ITENS)
m("Item · valor", QUAD, RS,
  "Valor do item do quadradinho da linha (dItem), como a planilha imprime (sem o sinal da fórmula).",
  f"SWITCH (\n    SELECTEDVALUE ( dItem[Item] ),\n{casos}\n)", "obras[].composicao[].valor")
m("Item · % do orçamento", QUAD, PCT, "Valor do item sobre o orçamento projetado (coluna % do quadradinho).",
  "DIVIDE ( [Item · valor], [Orçamento] )", "obras[].composicao[].pct_orcamento")
for base in ("Item · valor", "Item · % do orçamento"):
    m(f"{base} · ref", QUAD, RS if "valor" in base else PCT, f"[{base}] no mês de referência.",
      f"""VAR _mes = [Mês de referência]
RETURN
    CALCULATE ( [{base}], REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )""")
    m(f"{base} · foco", QUAD, RS if "valor" in base else PCT,
      f"[{base}] da obra em foco no mês de referência.", FOCO_OBRA.format(base=f"{base} · ref"))
    m(f"{base} · foco no mês", QUAD, RS if "valor" in base else PCT,
      f"[{base}] da obra em foco no mês do eixo (séries do tooltip do item).", FOCO_OBRA.format(base=base))

# ------------------------------------------------------------------------------------------------ identidade da obra em foco
IDT = r"T2 Análise crítica\Cabeçalho\Contas"
for base, desc in (("Aba · ref", "Nome da aba da obra em foco no mês de referência (JUN26)."),
                   ("Tipo de orçamento · ref", "Tipo do orçamento da obra em foco (preliminar, legal, executivo)."),
                   ("Obra · código", "Código do empreendimento da obra em foco (AT).")):
    nome = base.replace(" · ref", "") + " · foco"
    m(nome, IDT, "texto", desc, FOCO_OBRA.format(base=base))

# ------------------------------------------------------------------------------------------------ itens da nota
# Painel "Itens da nota" (era "Sinais do mês"): eixo dItemNota, um item por linha. Ordem: os itens que perdem pontos
# primeiro (mais pontos perdidos antes; empate pela ordem da régua), depois os cheios e depois os que estão sem dado.
# É a mesma pergunta da tela — onde a obra perde — e mantém o
# "pior primeiro" que o painel de sinais já tinha.
ITN = r"T2 Análise crítica\Itens da nota\Contas"
m("T2 · Itens · posição", ITN, "0",
  "Ordem do item da nota da linha (dItemNota) no painel Itens da nota, para a obra em foco no mês de referência: primeiro "
  "os que perdem pontos (mais pontos perdidos antes), depois os cheios e depois os sem dado; empate pela ordem da "
  "régua.",
  """VAR _grupo =
    IF ( ISBLANK ( [Nota · item · pontos · foco] ), 2, IF ( [Nota · item · perdidos · foco] > 0, 0, 1 ) )
VAR _perd = [Nota · item · perdidos · foco] + 0
VAR _ordem = [Nota · item · ordem]
VAR _todos =
    ADDCOLUMNS (
        ALL ( dItemNota[Item] ),
        "@g", IF ( ISBLANK ( [Nota · item · pontos · foco] ), 2, IF ( [Nota · item · perdidos · foco] > 0, 0, 1 ) ),
        "@p", [Nota · item · perdidos · foco] + 0,
        "@o", [Nota · item · ordem]
    )
VAR _antes =
    COUNTROWS (
        FILTER (
            _todos,
            [@g] < _grupo || ( [@g] = _grupo && ( [@p] > _perd || ( [@p] = _perd && [@o] < _ordem ) ) )
        )
    )
RETURN
    IF ( HASONEVALUE ( dItemNota[Item] ), _antes + 1 )""", "oráculo da régua antiga (pontos por item)")
m("T2 · Leitura · itens que perdem pontos (lista) · foco", r"T2 Análise crítica\Leituras\Contas", "texto",
  "Códigos (dItemNota) dos itens que perdem pontos na obra em foco no mês de referência, do que mais perde ao que menos "
  "perde (empate pela ordem da régua), separados por '|'; vazio quando nenhum perde. A obra "
  "em foco é lida uma vez só (cada conta · foco a recalcula).",
  """VAR _obra = [Nota · obra em foco]
VAR _itens =
    ADDCOLUMNS (
        ALL ( dItemNota[Item] ),
        "@p", CALCULATE ( [Nota · item · perdidos · ref], dObra[Obra] = _obra ),
        "@o", [Nota · item · ordem]
    )
VAR _perdem = FILTER ( _itens, [@p] > 0 )
RETURN
    CONCATENATEX ( _perdem, dItemNota[Item], "|", [@p], DESC, [@o], ASC )""", "oráculo da régua antiga (pontos por item)")
m("T2 · Leitura · itens que mais perdem (quantos) · foco", r"T2 Análise crítica\Leituras\Contas", "0",
  "Quantos itens empatam no topo dos pontos perdidos da obra em foco no mês de referência (os primeiros da lista "
  "'itens que perdem pontos'); vazio quando nenhum perde. A frase cita todos os empatados (auditoria da Fase 2, minor 2).",
  """VAR _obra = [Nota · obra em foco]
VAR _itens =
    ADDCOLUMNS (
        ALL ( dItemNota[Item] ),
        "@p", ROUND ( CALCULATE ( [Nota · item · perdidos · ref], dObra[Obra] = _obra ), 8 )
    )
VAR _perdem = FILTER ( _itens, [@p] > 0 )
VAR _max = MAXX ( _perdem, [@p] )
RETURN
    COUNTROWS ( FILTER ( _perdem, [@p] = _max ) )""", "bases de teste, ago/26")
m("T2 · Leitura · pontos de cada item, mês a mês (lista) · foco", r"T2 Análise crítica\Leituras\Contas", "texto",
  "Matriz item × mês da obra em foco na janela (do primeiro mês da janela ao de referência), como lista "
  "'item@AAAAMM=classe' separada por '|': c cheio (todos os pontos possíveis), p parcial, z zero, f sem dado, x valor "
  "fora da faixa (sem pontos, mas não por falta; Fase 3, rodada 3), n neutro "
  "(item que vale 0 de 0); no fim, a linha da obra 'obra@AAAAMM=status' (2, 1, "
  "0, m pendente). A obra em foco é lida uma vez só: cada leitura de uma conta · foco no mês recalcula a obra em foco, "
  "e a matriz faria mais de 80 delas.",
  """VAR _obra = [Nota · obra em foco]
VAR _ref = [Mês de referência]
VAR _ini = [Série · primeiro mês]
VAR _cel =
    ADDCOLUMNS (
        CROSSJOIN ( FILTER ( ALL ( dMes[Mes] ), dMes[Mes] >= _ini && dMes[Mes] <= _ref ), ALL ( dItemNota[Item] ) ),
        "@pt", CALCULATE ( [Nota · item · pontos], dObra[Obra] = _obra ),
        "@ps", CALCULATE ( [Nota · item · possíveis], dObra[Obra] = _obra ),
        "@fx", CALCULATE ( [Nota · item · fora da faixa], dObra[Obra] = _obra )
    )
RETURN
    CONCATENATEX (
        _cel,
        dItemNota[Item] & "@" & FORMAT ( dMes[Mes], "yyyymm" ) & "="
            & SWITCH (
                TRUE (),
                ISBLANK ( [@pt] ) && [@fx] = 1, "x",
                ISBLANK ( [@pt] ), "f",
                [@ps] = 0, "n",
                [@pt] >= [@ps], "c",
                [@pt] = 0, "z",
                "p"
            ),
        "|"
    )
        & "|"
        & CONCATENATEX (
            FILTER ( ALL ( dMes[Mes] ), dMes[Mes] >= _ini && dMes[Mes] <= _ref ),
            VAR _st = CALCULATE ( [Nota · status · ranking], dObra[Obra] = _obra )
            VAR _pd = CALCULATE ( [Nota · pendente · ranking], dObra[Obra] = _obra )
            RETURN
                "obra@" & FORMAT ( dMes[Mes], "yyyymm" ) & "=" & IF ( _pd = 1, "m", IF ( ISBLANK ( _st ), "", _st & "" ) ),
            "|"
        )""", "oráculo da régua antiga (pontos por item e mês; status da obra)")
for base, desc in (("pontos", "pontos"), ("possíveis", "pontos possíveis")):
    m(f"T2 · Item da nota · {base} no mês anterior · foco", r"T2 Análise crítica\Tooltips\Contas", "0.00",
      f"{desc.capitalize()} do item da nota da linha (dItemNota) na obra em foco, no mês anterior ao de referência "
      "(rodapé do tooltip do item).",
      f"""VAR _mes = EDATE ( [Mês de referência], -1 )
RETURN
    CALCULATE ( [Nota · item · {base} · foco no mês], REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )""",
      "oráculo da régua antiga (pontos por item)")
# o rodapé separa "sem dado" de "valor fora da faixa" também no mês anterior (auditoria da Fase 3, minor 1)
m("T2 · Item da nota · fora da faixa no mês anterior · foco", r"T2 Análise crítica\Tooltips\Contas", "0",
  "1 quando o item da nota da linha (dItemNota) tinha, na obra em foco e no mês anterior ao de referência, valor na base "
  "fora da faixa válida; 0 nos demais casos (rodapé do tooltip do item).",
  """VAR _mes = EDATE ( [Mês de referência], -1 )
VAR _obra = [Nota · obra em foco]
RETURN
    CALCULATE ( [Nota · item · fora da faixa], dObra[Obra] = _obra, REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )""",
  "pbi/qa/nota/casos_auditoria.py teste · DUNAS, médio prazo em jul/26: 0 (sem dado, não fora da faixa)")

# ------------------------------------------------------------------------------------------------ cascata
CAS = r"T2 Análise crítica\Como o resultado se forma\Contas"
m("Cascata · pago e não aplicado", CAS, RS,
  "Degrau 'pago e não aplicado' da cascata: itens 02 a 07 do quadradinho (saldo de contrato, adiantamentos, estoque, "
  "equipamentos e receita de personalizações) — tudo o que soma no resultado sem ter virado obra pelo crédito.",
  "[Ativos não consumidos] + [Receita de personalizações]", "serie[].ativos_nao_consumidos (+ receita)")
m("Cascata · pago e não aplicado · ref", CAS, RS, "[Cascata · pago e não aplicado] no mês de referência.",
  """VAR _mes = [Mês de referência]
RETURN
    CALCULATE ( [Cascata · pago e não aplicado], REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )""")
m("Cascata · pago e não aplicado · foco", CAS, RS, "[Cascata · pago e não aplicado] da obra em foco no mês de referência.",
  FOCO_OBRA.format(base="Cascata · pago e não aplicado · ref"))
m("Cascata · pago e não aplicado · foco no mês", CAS, RS,
  "[Cascata · pago e não aplicado] da obra em foco no mês do eixo.", FOCO_OBRA.format(base="Cascata · pago e não aplicado"))
m("Ativos não consumidos · foco no mês", CAS, RS, "Pagos e ainda não aplicados da obra em foco no mês do eixo.",
  FOCO_OBRA.format(base="Ativos não consumidos"))
m("Cascata · degraus · foco", CAS, "0",
  "Quantos degraus a cascata da obra em foco tem no mês de referência: valor agregado, custo aplicado, resultado "
  "aplicado, a realizar e o resultado da planilha (sempre os cinco).", "5")

m("Dívida da obra · foco no mês", CAS, RS, "Dívida da obra (item 10) da obra em foco no mês do eixo.",
  FOCO_OBRA.format(base="Dívida da obra"))
for _b in ("Custo aplicado", "Resultado aplicado", "A realizar", "IDC"):
    m(f"{_b} · foco no mês", CAS, "0.00" if _b == "IDC" else RS, f"[{_b}] da obra em foco no mês do eixo.",
      FOCO_OBRA.format(base=_b))
# F3 (docs/08 §5): VA → custo aplicado → resultado aplicado → + a realizar → resultado da planilha
DEGRAUS = [("ValorAgregado", "Crédito do orçamento"), ("CustoAplicado", "Custo aplicado"),
           ("ResultadoAplicado", "Resultado aplicado"), ("ARealizar", "A realizar"), ("Resultado", "Resultado da obra")]
for suf, desc in ((" · foco", "no mês de referência"), (" · foco no mês", "no mês do eixo")):
    casos = ",\n".join(f'    "{c}", [{n}{suf}]' for c, n in DEGRAUS)
    m(f"Cascata · degrau · valor{suf}", CAS, RS,
      f"Valor do degrau da linha (dDegrau) da obra em foco {desc}, sem o sinal da conta (os resultados com o próprio "
      "sinal).", f"SWITCH (\n    SELECTEDVALUE ( dDegrau[Degrau] ),\n{casos}\n)", "dados/_gabarito (VA, CA, a realizar)")
m("Cascata · degrau · aparece · foco", CAS, "0",
  "1 quando o degrau da linha entra na cascata da obra em foco (todos, sempre que há degrau na linha).",
  """IF ( NOT ISBLANK ( SELECTEDVALUE ( dDegrau[Degrau] ) ), 1 )""")
_CAS_VARS = """VAR _deg = SELECTEDVALUE ( dDegrau[Degrau] )
VAR _va = [Crédito do orçamento · foco] + 0
VAR _ca = [Custo aplicado · foco] + 0
VAR _ra = [Resultado aplicado · foco] + 0
VAR _ar = [A realizar · foco] + 0
VAR _r = [Resultado da obra · foco] + 0"""
m("Cascata · degrau · base · foco", CAS, RS,
  "Onde o degrau da linha começa na cascata da obra em foco (o menor dos dois extremos da barra; os resultados partem "
  "de zero). Serve para posicionar a barra.",
  f"""{_CAS_VARS}
RETURN
    SWITCH (
        _deg,
        "ValorAgregado", MIN ( 0, _va ),
        "CustoAplicado", MIN ( _va, _va - _ca ),
        "ResultadoAplicado", MIN ( 0, _ra ),
        "ARealizar", MIN ( _ra, _ra + _ar ),
        "Resultado", MIN ( 0, _r )
    )""")
m("Cascata · degrau · topo · foco", CAS, RS,
  "Onde o degrau da linha termina na cascata da obra em foco (o maior dos dois extremos da barra).",
  f"""{_CAS_VARS}
RETURN
    SWITCH (
        _deg,
        "ValorAgregado", MAX ( 0, _va ),
        "CustoAplicado", MAX ( _va, _va - _ca ),
        "ResultadoAplicado", MAX ( 0, _ra ),
        "ARealizar", MAX ( _ra, _ra + _ar ),
        "Resultado", MAX ( 0, _r )
    )""")
for nome, agreg, campo, desc in (("máximo", "MAXX", "@t", "o topo mais alto"), ("mínimo", "MINX", "@b", "a base mais baixa")):
    m(f"Cascata · escala · {nome} · foco", CAS, RS,
      f"Escala da cascata da obra em foco: {desc} entre os degraus que aparecem (zero entra sempre).",
      f"""VAR _deg =
    ADDCOLUMNS (
        ALL ( dDegrau ),
        "@a", [Cascata · degrau · aparece · foco],
        "@t", [Cascata · degrau · topo · foco],
        "@b", [Cascata · degrau · base · foco]
    )
RETURN
    {agreg} ( FILTER ( _deg, [@a] = 1 ), [{campo}] )""")

MES = r"T2 Análise crítica\IDC, mês a mês\Contas"
# F3 (docs/08 §5): o mês a mês vira o IDC da obra em foco, uma série só, com as linhas em 1,00 (ponto cheio do custo)
# e na trava (0,90); os valores em R$ ficam no tooltip do mês.
JANELA = """VAR _ref = [Mês de referência]
VAR _ini = [Série · primeiro mês]"""
NA_JANELA = "FILTER ( ALL ( dMes[Mes] ), dMes[Mes] >= _ini && dMes[Mes] <= _ref )"
# IDC arredondado em 2 casas só quando existe (ROUND de vazio daria 0 e o mês sem aba viraria o menor IDC)
IDC_R2 = "VAR _v = [IDC · foco no mês] RETURN IF ( NOT ISBLANK ( _v ), ROUND ( _v, 2 ) )"
# transições mês a mês dentro da janela: do segundo mês da janela em diante (o anterior também está na janela)
TRANSICOES = "FILTER ( ALL ( dMes[Mes] ), dMes[Mes] > _ini && dMes[Mes] <= _ref )"
for nome, agreg, desc in (("máximo", "MAXX", "o maior IDC"), ("mínimo", "MINX", "o menor IDC")):
    m(f"T2 · IDC · {nome} na janela", MES, "0.000",
      f"{desc[0].upper() + desc[1:]} da obra em foco nos meses da janela (do primeiro ao de referência); vazio sem aba.",
      f"""{JANELA}
VAR _meses = ADDCOLUMNS ( {NA_JANELA}, "@i", [IDC · foco no mês] )
RETURN
    {agreg} ( FILTER ( _meses, NOT ISBLANK ( [@i] ) ), [@i] )""", "dados/_gabarito/nota_previa.csv (x_idc)")
for chave, agreg, desc in (("maior", "MAXX", "o maior"), ("menor", "MINX", "o menor")):
    m(f"T2 · IDC · mês do {chave}", MES, "dd/mm/yyyy",
      f"Mês da janela com {desc} IDC da obra em foco (empate: o mais recente); vazio sem aba.",
      f"""{JANELA}
VAR _meses = FILTER ( ADDCOLUMNS ( {NA_JANELA}, "@i", {IDC_R2} ), NOT ISBLANK ( [@i] ) )
VAR _x = {agreg} ( _meses, [@i] )
RETURN
    MAXX ( FILTER ( _meses, [@i] = _x ), dMes[Mes] )""", "dados/_gabarito/nota_previa.csv (x_idc)")

m("T2 · IDC · meses abaixo de 1 na janela", MES, "0",
  "Meses da janela em que o IDC da obra em foco ficou abaixo de 1 (gastou mais do que agregou).",
  f"""{JANELA}
VAR _meses = ADDCOLUMNS ( {NA_JANELA}, "@i", {IDC_R2} )
RETURN
    COUNTROWS ( FILTER ( _meses, NOT ISBLANK ( [@i] ) && [@i] < 1 ) ) + 0""", "dados/_gabarito/nota_previa.csv (x_idc)")
m("T2 · IDC · abaixo de 1 desde", MES, "dd/mm/yyyy",
  "Primeiro mês da sequência atual de IDC abaixo de 1 que chega ao mês de referência (vazio quando o IDC de referência "
  "não está abaixo de 1).",
  f"""{JANELA}
VAR _meses = ADDCOLUMNS ( {NA_JANELA}, "@i", {IDC_R2} )
VAR _ultimoOk = MAXX ( FILTER ( _meses, NOT ISBLANK ( [@i] ) && [@i] >= 1 ), dMes[Mes] )
VAR _abaixo = FILTER ( _meses, NOT ISBLANK ( [@i] ) && [@i] < 1 && ( ISBLANK ( _ultimoOk ) || dMes[Mes] > _ultimoOk ) )
RETURN
    IF ( MAXX ( FILTER ( _meses, dMes[Mes] = _ref ), [@i] ) < 1, MINX ( _abaixo, dMes[Mes] ) )""",
  "dados/_gabarito/nota_previa.csv (x_idc)")
for _nome, _cond, _desc in (("primeiro", "MINX", "primeiro"), ("último", "MAXX", "último")):
    m(f"T2 · Nota · {_nome} mês com nota na janela · foco", MES, "dd/mm/yyyy",
      f"O {_desc} mês da janela em que a obra em foco tem nota completa.",
      f"""{JANELA}
VAR _obra = [Nota · obra em foco]
VAR _meses = ADDCOLUMNS ( {NA_JANELA}, "@n", CALCULATE ( [Nota · nota final · um mês], dObra[Obra] = _obra ) )
RETURN
    {_cond} ( FILTER ( _meses, NOT ISBLANK ( [@n] ) ), dMes[Mes] )""")
m("T2 · Nota · meses críticos na janela · foco", MES, "0",
  "Meses da janela em que a obra em foco esteve crítica na nota.",
  f"""{JANELA}
VAR _obra = [Nota · obra em foco]
VAR _meses = ADDCOLUMNS ( {NA_JANELA}, "@s", CALCULATE ( [Nota · status · um mês], dObra[Obra] = _obra ) )
RETURN
    COUNTROWS ( FILTER ( _meses, [@s] == 2 ) ) + 0""")

m("T2 · IDC · mês com rótulo", MES, "0",
  "1 quando o mês do eixo é o do maior ou o do menor IDC da janela (o desenho escreve o valor nesses meses e no de "
  "referência); 0 nos demais.",
  """VAR _m = MAX ( dMes[Mes] )
RETURN
    IF ( HASONEVALUE ( dMes[Mes] ), INT ( _m = [T2 · IDC · mês do maior] || _m = [T2 · IDC · mês do menor] ) )""")
m("T2 · IDC · no primeiro mês com aba · foco", MES, "0.00",
  "IDC da obra em foco no primeiro mês da janela em que ela tem aba.",
  """VAR _ini = [T2 · Leitura · primeiro mês com aba · foco]
RETURN
    CALCULATE ( [IDC · foco no mês], REMOVEFILTERS ( dMes ), dMes[Mes] = _ini )""")
m("T2 · Nota · no primeiro mês com nota na janela · foco", MES, "0.00",
  "Nota da obra em foco no primeiro mês da janela em que ela tem nota completa.",
  """VAR _ini = [T2 · Nota · primeiro mês com nota na janela · foco]
RETURN
    CALCULATE ( [Nota · nota final · foco no mês], REMOVEFILTERS ( dMes ), dMes[Mes] = _ini )""")

m("Item · ordem", QUAD, "0", "Posição do item no quadradinho (1 a 10), para ordenar as linhas.",
  "SELECTEDVALUE ( dItem[Ordem] )")
m("Item · rótulo", QUAD, "texto", "Rótulo do item do quadradinho da linha, como na planilha.", "SELECTEDVALUE ( dItem[Rotulo] )")
m("Cascata · degrau · ordem", CAS, "0", "Posição do degrau na cascata, para ordenar as colunas.",
  "SELECTEDVALUE ( dDegrau[Ordem] )")
m("Quadradinho · itens com valor · foco", QUAD, "0",
  "Quantos dos sete itens que somam (01 a 07) têm valor diferente de zero na obra em foco no mês de referência.",
  """VAR _it = ADDCOLUMNS ( FILTER ( ALL ( dItem ), dItem[Ordem] <= 7 ), "@v", [Item · valor · foco] )
RETURN
    COUNTROWS ( FILTER ( _it, NOT ISBLANK ( [@v] ) && [@v] <> 0 ) ) + 0""", "composicao[] 01–07 com valor")
# ------------------------------------------------------------------------------------------------ tooltips
TT = r"T2 Análise crítica\Tooltips\Contas"
for base, fmt in (("Resultado % · mês anterior", PCT), ("Resultado · variação p.p.", "+0.00;-0.00;0.00"),
                  ("Desembolso · desvio no mês", "0%"), ("Justificativa do desembolso", "texto"),
                  ("Justificativa · exigida", "0"), ("Justificativa · em branco", "0")):
    m(f"{base} · foco no mês", TT, fmt, f"[{base}] da obra em foco no mês do eixo (tooltips e séries da T2).",
      FOCO_OBRA.format(base=base))
m("Aba · foco no mês", TT, "texto", "Nome da aba da obra em foco no mês do eixo (JUN26).",
  """VAR _obra = [Nota · obra em foco]
RETURN
    CALCULATE ( SELECTEDVALUE ( fAnaliseCritica[Aba] ), dObra[Obra] = _obra )""")
m("Cascata · degrau · % do orçamento · foco", TT, PCT,
  "Valor do degrau da linha sobre o orçamento da obra em foco, no mês de referência (3,60% no pago e não aplicado "
  "da REDINHA em jun/26).",
  "DIVIDE ( [Cascata · degrau · valor · foco], [Orçamento · foco] )", "composicao[].pct_orcamento (soma dos itens)")
m("Estoque de materiais · mês anterior · foco no mês", TT, RS,
  "Estoque de materiais da obra em foco no mês anterior ao do eixo (vazio sem aba no mês anterior).",
  """VAR _obra = [Nota · obra em foco]
VAR _mes = EDATE ( MAX ( dMes[Mes] ), -1 )
RETURN
    CALCULATE ( [Estoque de materiais], dObra[Obra] = _obra, REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )""")
m("Cascata · resultado sem o degrau · foco", TT, RS,
  "Resultado da obra em foco no mês de referência sem o degrau 'pago e não aplicado' (itens 02 a 07): o que a "
  "obra fecharia sem o dinheiro pago que ainda não virou obra.",
  "[Resultado da obra · foco] - [Cascata · pago e não aplicado · foco]", "ultimo.resultado_sem_ativos (+ receita)")
m("Item · linha · descrição · foco", TT, "texto",
  "Descrição da linha da tabela anexada (fItens[Linha] do contexto) que compõe o item da linha, na obra em foco e no "
  "mês de referência.",
  """VAR _obra = [Nota · obra em foco]
VAR _mes = [Mês de referência]
RETURN
    CALCULATE ( SELECTEDVALUE ( fItens[Descricao] ), dObra[Obra] = _obra, REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )""",
  "itens_ultimo_mes[].descricao")
m("Item · linha · valor · foco", TT, RS,
  "Valor da linha da tabela anexada (fItens[Linha] do contexto) que compõe o item da linha, na obra em foco e no mês "
  "de referência.",
  """VAR _obra = [Nota · obra em foco]
VAR _mes = [Mês de referência]
RETURN
    CALCULATE ( SUM ( fItens[Valor] ), dObra[Obra] = _obra, REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )""",
  "itens_ultimo_mes[].valor")

# ------------------------------------------------------------------------------------------------ leituras
# Toda conta que descreve a série mostrada olha só a janela do drawer (dMes[Mes] >= [Série · primeiro mês]); as
# transições (alta, queda) contam do segundo mês da janela em diante. As de mês anterior não mudam.
LEI = r"T2 Análise crítica\Leituras\Contas"
m("Item · meses com valor · foco", LEI, "0",
  "Em quantos meses da janela (do primeiro mês da janela ao de referência) o item da linha teve valor diferente de "
  "zero na obra em foco: zero = o item não entrou na conta desta obra no período.",
  f"""{JANELA}
VAR _meses = ADDCOLUMNS ( {NA_JANELA}, "@v", [Item · valor · foco no mês] )
RETURN
    COUNTROWS ( FILTER ( _meses, NOT ISBLANK ( [@v] ) && [@v] <> 0 ) ) + 0""")
for nome, medida, desc in (("estoque", "Estoque de materiais", "o estoque de materiais"),
                           ("resultado", "Resultado da obra", "o resultado")):
    for mov, cmp_ in (("alta", ">"), ("queda", "<")):
        m(f"T2 · Leitura · meses com {mov} do {nome} · foco", LEI, "0",
          f"Meses da janela (do segundo mês da janela ao de referência) em que {desc} da obra em foco "
          f"{'subiu' if mov == 'alta' else 'caiu'} sobre o mês anterior.",
          f"""{JANELA}
VAR _obra = [Nota · obra em foco]
VAR _meses =
    ADDCOLUMNS (
        {TRANSICOES},
        "@v", CALCULATE ( [{medida}], dObra[Obra] = _obra ),
        "@ant", VAR _m = dMes[Mes] RETURN CALCULATE ( [{medida}], dObra[Obra] = _obra, REMOVEFILTERS ( dMes ), dMes[Mes] = EDATE ( _m, -1 ) )
    )
RETURN
    COUNTROWS ( FILTER ( _meses, NOT ISBLANK ( [@v] ) && NOT ISBLANK ( [@ant] ) && [@v] {cmp_} [@ant] ) ) + 0""")
m("T2 · Leitura · meses com aba · foco", LEI, "0",
  "Em quantos meses da janela (do primeiro mês da janela ao de referência) a obra em foco tem aba Análise Crítica.",
  f"""{JANELA}
VAR _meses = ADDCOLUMNS ( {NA_JANELA}, "@r", [Resultado da obra · foco no mês] )
RETURN
    COUNTROWS ( FILTER ( _meses, NOT ISBLANK ( [@r] ) ) ) + 0""")
m("T2 · Leitura · primeiro mês com aba · foco", LEI, "dd/mm/yyyy",
  "Primeiro mês da janela em que a obra em foco tem aba (jan/26 na REDINHA com janela de 12 em ago/26; jun/26 na "
  "TIROL).",
  f"""{JANELA}
VAR _meses = ADDCOLUMNS ( {NA_JANELA}, "@r", [Resultado da obra · foco no mês] )
RETURN
    MINX ( FILTER ( _meses, NOT ISBLANK ( [@r] ) ), dMes[Mes] )""")
for nome, medida in (("resultado", "Resultado da obra · foco no mês"), ("resultado %", "Resultado % · foco no mês"),
                     ("estoque", "Estoque de materiais · foco no mês"), ("ativos", "Ativos não consumidos · foco no mês")):
    m(f"T2 · Leitura · {nome} no primeiro mês · foco", LEI, PCT if "%" in nome else RS,
      f"[{medida}] no primeiro mês da janela em que a obra em foco tem aba.",
      f"""VAR _ini = [T2 · Leitura · primeiro mês com aba · foco]
RETURN
    CALCULATE ( [{medida}], REMOVEFILTERS ( dMes ), dMes[Mes] = _ini )""")
m("T2 · Leitura · meses com sem estoque negativo · foco", LEI, "0",
  "Meses da janela em que o resultado sem estoque e adiantamentos da obra em foco foi negativo.",
  f"""{JANELA}
VAR _meses = ADDCOLUMNS ( {NA_JANELA}, "@s", [Resultado sem ativos · foco no mês] )
RETURN
    COUNTROWS ( FILTER ( _meses, NOT ISBLANK ( [@s] ) && [@s] < 0 ) ) + 0""")
m("T2 · Leitura · menor variação do período · foco", LEI, "+0.00;-0.00;0.00",
  "A menor variação do resultado (p.p.) da obra em foco entre os meses da janela.",
  f"""{JANELA}
VAR _meses = ADDCOLUMNS ( {NA_JANELA}, "@v", [Resultado · variação p.p. · foco no mês] )
RETURN
    MINX ( FILTER ( _meses, NOT ISBLANK ( [@v] ) ), [@v] )""")
# quadradinho: listas de itens (códigos separados por '|') da obra em foco no mês de referência
ITENS_LISTA = """VAR _itens =
    ADDCOLUMNS (
        VALUES ( dItem[Item] ),
        "@o", [Item · ordem],
        "@v", [Item · valor · foco],
        "@m", [Item · meses com valor · foco]
    )"""
m("T2 · Leitura quadradinho · itens que nunca tiveram valor (lista) · foco", LEI, "texto",
  "Códigos dos itens 02 a 07 do quadradinho que nunca tiveram valor na janela da obra em foco, na ordem do quadradinho, "
  "separados por '|' (ex.: ago/26 na REDINHA: SaldoContrato|ReceitaPersonalizacao; vazio se nenhum).",
  f"""{ITENS_LISTA}
RETURN
    CONCATENATEX ( FILTER ( _itens, [@o] >= 2 && [@o] <= 7 && [@m] = 0 ), dItem[Item], "|", [@o], ASC )""",
  "composicao[] 02–07 sem valor na janela")
m("T2 · Leitura quadradinho · itens que zeraram no mês (lista) · foco", LEI, "texto",
  "Códigos dos itens 02 a 07 do quadradinho que tiveram valor na janela e estão zerados no mês de referência, na ordem do "
  "quadradinho, separados por '|' (vazio se nenhum).",
  f"""{ITENS_LISTA}
RETURN
    CONCATENATEX (
        FILTER ( _itens, [@o] >= 2 && [@o] <= 7 && [@m] > 0 && ( ISBLANK ( [@v] ) || [@v] = 0 ) ),
        dItem[Item], "|", [@o], ASC
    )""", "composicao[] 02–07 zerados no mês")
m("T2 · Leitura quadradinho · itens com valor (lista) · foco", LEI, "texto",
  "Códigos de todos os itens do quadradinho com valor diferente de zero no mês de referência da obra em foco, na ordem "
  "do quadradinho, separados por '|' (ex.: ago/26 na REDINHA: Credito|AdiantMateriais|Estoque|Equipamentos|ContasPagar|Desembolsado).",
  f"""{ITENS_LISTA}
RETURN
    CONCATENATEX ( FILTER ( _itens, NOT ISBLANK ( [@v] ) && [@v] <> 0 ), dItem[Item], "|", [@o], ASC )""",
  "composicao[] com valor")

# ------------------------------------------------------------------------------------------------ tooltip de mês
GRUPOS_ATIVOS = [("SaldoContrato", "saldo de contrato"), ("AdiantServicos", "adiantamento de serviços"),
                 ("AdiantMateriais", "adiantamento de materiais"), ("Estoque", "estoque de materiais"),
                 ("Equipamentos", "equipamentos"), ("ReceitaPersonalizacao", "receita de personalizações")]
m("T2 · Tooltip mês · grupos de ativos com valor · foco no mês", TT, "0",
  "Quantos dos seis grupos de ativos (saldo de contrato a receita de personalizações) têm valor diferente de zero na obra em "
  "foco no mês do eixo. Ex.: ago/26 na REDINHA: 3.",
  "\n".join(f'VAR _g{i} = CALCULATE ( [Item · valor · foco no mês], dItem[Item] = "{c}" )'
            for i, (c, _t) in enumerate(GRUPOS_ATIVOS))
  + "\nVAR _todos = { " + ", ".join(f"( {i}, _g{i} )" for i in range(len(GRUPOS_ATIVOS))) + " }"
  + "\nVAR _comValor = FILTER ( _todos, NOT ISBLANK ( [Value2] ) && [Value2] <> 0 )"
  + "\nRETURN\n    COUNTROWS ( _comValor ) + 0", "composicao[] 02–07 com valor (grupos de ativos)")

if __name__ == "__main__":
    sys.exit(gravar([x for x in MEDIDAS if x.nome not in RETIRADAS], RAIZ / "dax" / "T2", GERADO))

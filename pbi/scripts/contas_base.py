#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""contas_base — escreve as medidas de CONTA reutilizáveis (pbi/dax/base/**.dax), uma por arquivo, no formato do
dax_para_tmdl (skill dax-conta-desenho). Idempotente: reescreve só os arquivos desta lista e apaga os .dax de
pbi/dax/base que ela não declara mais.

    python -X utf8 pbi/scripts/contas_base.py

Famílias:
  1. Base\\<assunto>          conta no contexto do visual (mês e obra do eixo/linha). Série mês a mês usa estas.
  2. Base\\Referência         a mesma conta presa ao mês de referência (seletor dMesRef; sem escolha, o último mês).
                              Cartões, rankings e listas por obra usam estas.
  3. Base\\Nota               a Nota da obra (docs/08, aprovada em 28/10/2026), gerada do dicionário NOTA (fonte única
                              de faixas, pontos e limites; também gera pbi/m/dItemNota.m, pbi/m/fxRegrasBase.m e as tabelas
                              calculadas dRankingNota e dItemRankingNota). Antes dela, a régua antiga (13/10 a 28/10/2026)
                              e a régua de criticidade da Vizu, que saíram. A régua antiga (Criticidade, Indicador,
                              dIndicador) saiu na integração da Fase 2 e as definições dela, na auditoria (14/10/2026).

Oráculo: planilhas reais (pipeline/extrair_analise_critica.py) — conferido por conferir_real.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]           # pbi/
DESTINO = RAIZ / "dax" / "base"
F = "fAnaliseCritica"

RS = '"R$" #,0.00;-"R$" #,0.00;"R$" 0.00'
PCT = "0.00%"
PP = "+0.00;-0.00;0.00"
INT = "0"
TXT = "texto"
DATA = "dd/mm/yyyy"
NUM = "0.0"

MEDIDAS: list[tuple[str, str, str, str, str, str]] = []   # (subpasta, nome, pasta, formato, descrição, dax)

# Retiradas do modelo em 08/10/2026 (auditoria: dependencias-pos-telas.json e dependencias-final.json, chave mortas).
# Nenhum visual alcança estas contas e nenhum script de QA as lê (o conferir_contas.py, que lia as 16 'Criticidade ·
# … · ref' e o rótulo, saiu do projeto nesta data). Fora da gravação: o gerador não escreve o nome e apaga o .dax que
# tinha escrito antes. Para reativar, tire o nome do conjunto.
RETIRADAS = {
    "Adiantamento de materiais · foco",
    "Adiantamento de materiais · ref",
    "Adiantamento de serviços · foco",
    "Adiantamento de serviços · ref",
    "Adiantamentos",
    "Adiantamentos · foco",
    "Adiantamentos · foco no mês",
    "Adiantamentos · ref",
    "Criticidade · obras críticas · desembolso · ref",
    "Criticidade · obras críticas · desvio físico · ref",
    "Criticidade · obras críticas · resultado · ref",
    "Criticidade · obras críticas · sem ativos · ref",
    "Criticidade · obras críticas · variação · ref",
    "Criticidade · obras em atenção · desembolso · ref",
    "Criticidade · obras em atenção · desvio físico · ref",
    "Criticidade · obras em atenção · resultado · ref",
    "Criticidade · obras em atenção · sem ativos · ref",
    "Criticidade · obras em atenção · variação · ref",
    "Criticidade · pontos desembolso · foco",
    "Criticidade · pontos desembolso · ref",
    "Criticidade · pontos desvio físico · foco",
    "Criticidade · pontos desvio físico · ref",
    "Criticidade · pontos resultado · foco",
    "Criticidade · pontos resultado · ref",
    "Criticidade · pontos sem ativos · foco",
    "Criticidade · pontos sem ativos · ref",
    "Criticidade · pontos variação · foco",
    "Criticidade · pontos variação · ref",
    "Criticidade · status · rótulo",
    "Criticidade · status · rótulo · foco",
    "Criticidade · status · rótulo · ref",
    "Desembolso · realizado com previsto no mês · foco",
    "Desembolso · realizado com previsto no mês · ref",
    "Equipamentos (valor de mercado) · foco",
    "Equipamentos (valor de mercado) · ref",
    "Físico · executado acumulado · com previsto · foco",
    "Físico · obras sem previsto (lista) · foco",
    "Indicador · obras críticas · foco",
    "Indicador · obras em atenção · foco",
    "Orçamento · mês anterior · foco",
    "Receita de personalizações · foco",
    "Receita de personalizações · ref",
    "Recorte · obras ilustrativas (lista)",
    "Recorte · obras reais (lista)",
    "Recorte · primeiro mês · curto",
    "Resultado · variação no mês · foco",
    "Saldo de contrato · foco",
    "Saldo de contrato · ref",
}



def m(sub: str, nome: str, pasta: str, formato: str, descricao: str, dax: str, oraculo: str = "") -> None:
    MEDIDAS.append((sub, nome, pasta, formato, descricao + (f"\n@oraculo: {oraculo}" if oraculo else ""), dax.strip("\n")))


# ---------------------------------------------------------------------------------------------------------------------
# 1. Mês de referência
# ---------------------------------------------------------------------------------------------------------------------
m("mes", "Mês de referência", r"Base\Mês", DATA,
  "Mês escolhido no seletor do drawer (dMesRef, desconectada); sem escolha, ou com a linha \"Último mês\", o mês "
  "dessa linha (o mais recente que pelo menos metade das obras já fechou).",
  """VAR _auto = SELECTEDVALUE ( dMesRef[Automatico], TRUE () )
VAR _ultimo = CALCULATE ( MAX ( dMesRef[MesRef] ), REMOVEFILTERS ( dMesRef ), dMesRef[Automatico] = TRUE () )
RETURN
    IF ( _auto, _ultimo, MAX ( dMesRef[MesRef] ) )""", "carteira.mes_ref")
m("mes", "Mês de referência · longo", r"Base\Mês", TXT,
  "Mês de referência por extenso (junho de 2026), para o cabeçalho e as frases.",
  """VAR _mes = [Mês de referência]
RETURN
    LOOKUPVALUE ( dMes[MesAnoLongo], dMes[Mes], _mes )""")
m("mes", "Mês de referência · curto", r"Base\Mês", TXT,
  "Mês de referência abreviado (jun/26).",
  """VAR _mes = [Mês de referência]
RETURN
    LOOKUPVALUE ( dMes[MesAno], dMes[Mes], _mes )""")
m("mes", "Mês anterior à referência · curto", r"Base\Mês", TXT,
  "Mês anterior ao de referência, abreviado (mai/26); vazio quando a referência é o primeiro mês do histórico.",
  """VAR _mes = EDATE ( [Mês de referência], -1 )
RETURN
    LOOKUPVALUE ( dMes[MesAno], dMes[Mes], _mes )""")
m("mes", "Mês anterior à referência · nome", r"Base\Mês", TXT,
  "Nome do mês anterior ao de referência, minúsculo (maio), para as frases de comparação.",
  """VAR _mes = EDATE ( [Mês de referência], -1 )
RETURN
    FORMAT ( _mes, "mmmm", "pt-BR" )""")
m("mes", "Mês de referência · curto maiúsculo", r"Base\Mês", TXT,
  "Mês de referência abreviado em caixa alta (JUN/26), para sobretítulos.",
  "UPPER ( [Mês de referência · curto] )")
m("mes", "Mês · rótulo curto", r"Base\Mês", TXT, "Mês do eixo abreviado (jun/26).",
  "SELECTEDVALUE ( dMes[MesAno] )")
m("mes", "Mês · abreviado", r"Base\Mês", TXT, "Mês do eixo abreviado sem ano (jun).",
  "SELECTEDVALUE ( dMes[MesAbrev] )")
m("mes", "Mês · nome", r"Base\Mês", TXT, "Mês do eixo por extenso, minúsculo (junho).",
  "SELECTEDVALUE ( dMes[MesNome] )")
m("mes", "Mês · longo", r"Base\Mês", TXT, "Mês do eixo com ano (junho de 2026).",
  "SELECTEDVALUE ( dMes[MesAnoLongo] )")
m("mes", "Mês de referência · nome", r"Base\Mês", TXT,
  "Nome do mês de referência, minúsculo (junho), para as frases das leituras.",
  """VAR _mes = [Mês de referência]
RETURN
    FORMAT ( _mes, "mmmm", "pt-BR" )""")
m("mes", "Série · janela (meses)", r"Base\Mês", INT,
  "Quantos meses a série olha até o mês de referência, escolhidos no drawer (dJanela, desconectada): 12, 9, 6 ou 3; "
  "sem escolha, 12.",
  "SELECTEDVALUE ( dJanela[Meses], 12 )")
m("mes", "Série · primeiro mês", r"Base\Mês", DATA,
  "Primeiro mês da janela: o mês de referência menos (janela − 1) meses, nunca antes do primeiro mês do histórico "
  "(jan/26). Ponto de partida das séries e das leituras (\"desde\", \"em x de y meses\").",
  """VAR _ref = [Mês de referência]
VAR _ini = CALCULATE ( MIN ( dMes[Mes] ), REMOVEFILTERS ( dMes ) )
VAR _janela = EDATE ( _ref, 1 - [Série · janela (meses)] )
RETURN
    IF ( NOT ISBLANK ( _ref ), MAX ( _ini, _janela ) )""")
m("mes", "Série · meses até a referência", r"Base\Mês", INT,
  "Quantos meses a série mostra: do primeiro mês da janela ao mês de referência (8 em ago/26 com janela de 12, "
  "porque o histórico começa em jan/26).",
  """VAR _ref = [Mês de referência]
VAR _ini = [Série · primeiro mês]
RETURN
    COUNTROWS ( FILTER ( ALL ( dMes[Mes] ), dMes[Mes] >= _ini && dMes[Mes] <= _ref ) )""")
m("mes", "Série · posição na janela", r"Base\Mês", INT,
  "Posição do mês do eixo dentro da janela (1 = primeiro mês da janela); vazio fora dela. Para a geometria das "
  "séries (x de cada coluna ou ponto).",
  """VAR _mes = MAX ( dMes[Mes] )
VAR _ini = [Série · primeiro mês]
RETURN
    IF ( _mes >= _ini && _mes <= [Mês de referência], DATEDIFF ( _ini, _mes, MONTH ) + 1 )""")
m("mes", "Mês · ordem", r"Base\Mês", INT, "Ordem do mês do eixo no histórico (1 = primeiro mês).",
  "SELECTEDVALUE ( dMes[Ordem] )")
m("mes", "Mês · data", r"Base\Mês", DATA, "Mês do eixo (primeiro dia), no contexto do gráfico ou do tooltip.",
  "MAX ( dMes[Mes] )")
m("mes", "Mês · é o primeiro do histórico", r"Base\Mês", INT,
  "1 quando o mês do contexto é o primeiro mês do histórico (sem comparação com o anterior); 0 nos outros.",
  """VAR _mes = MAX ( dMes[Mes] )
VAR _ini = CALCULATE ( MIN ( dMes[Mes] ), REMOVEFILTERS ( dMes ) )
RETURN
    IF ( _mes = _ini, 1, 0 )""")
m("mes", "Mês anterior · nome", r"Base\Mês", TXT,
  "Nome do mês anterior ao do contexto, minúsculo (maio), para as frases de comparação do tooltip do mês.",
  """VAR _mes = EDATE ( MAX ( dMes[Mes] ), -1 )
RETURN
    FORMAT ( _mes, "mmmm", "pt-BR" )""")
m("mes", "Série · é o mês de referência", r"Base\Mês", INT,
  "1 quando o mês do eixo é o mês de referência (destaque no eixo); 0 nos outros.",
  """VAR _mes = MAX ( dMes[Mes] )
RETURN
    IF ( _mes = [Mês de referência], 1, 0 )""")
m("mes", "Série · mês até a referência", r"Base\Mês", INT,
  "1 no mês do eixo que está na janela (do primeiro mês da janela ao de referência); vazio fora dela. Os gráficos "
  "mês a mês filtram por esta conta.",
  """VAR _mes = MAX ( dMes[Mes] )
RETURN
    IF ( _mes >= [Série · primeiro mês] && _mes <= [Mês de referência], 1 )""")

# ---------------------------------------------------------------------------------------------------------------------
# 2. Contas no contexto (mês e obra do visual)
# ---------------------------------------------------------------------------------------------------------------------
SOMAS = [  # (nome, coluna, formato, descrição)
    ("Orçamento", "Orcamento", RS, "Orçamento da obra projetado (passo 3), somado no recorte."),
    ("Resultado da obra", "Resultado", RS, "Resultado mensal da obra como a planilha apresenta (quadradinho, D155), somado no recorte."),
    ("Crédito do orçamento", "Credito", RS, "Item 1: executado acumulado × orçamento."),
    ("Saldo de contrato", "SaldoContrato", RS, "Item 2: saldo de contrato."),
    ("Adiantamento de serviços", "AdiantServicos", RS, "Item 3: adiantamento de serviços não medidos."),
    ("Adiantamento de materiais", "AdiantMateriais", RS, "Item 4: adiantamento de materiais não estocados."),
    ("Estoque de materiais", "Estoque", RS, "Item 5: estoque de materiais (almoxarifado)."),
    ("Equipamentos (valor de mercado)", "Equipamentos", RS, "Item 6: equipamentos (valor de mercado), como apresentado."),
    ("Receita de personalizações", "ReceitaPersonalizacao", RS, "Item 7: receita de personalizações."),
    ("Contas a pagar", "ContasPagar", RS, "Item 8: contas a pagar dos medidos (subtrai)."),
    ("Desembolsado acumulado", "Desembolsado", RS, "Item 9: valor desembolsado pela obra, corrigido dos itens irregulares (subtrai)."),
    ("Dívida da obra", "Divida", RS, "Item 10: dívida da obra a ser paga (soma, como na fórmula da planilha)."),
    ("Resultado · mês anterior", "ResultadoAnterior", RS, "Resultado apresentado na aba anterior de cada obra, somado."),
    ("Orçamento · mês anterior", "OrcamentoAnterior", RS, "Orçamento da aba anterior de cada obra, somado."),
    ("Desembolso · previsto no mês", "PrevistoMesRS", RS, "Valor previsto para o mês (tabela informativa), em R$."),
    ("Desembolso · realizado no mês", "DesembolsadoMesRS", RS, "Valor desembolsado no mês (tabela informativa), em R$."),
]
for nome, col, fmt, desc in SOMAS:
    m("contexto", nome, r"Base\Obra", fmt, desc, f"SUM ( {F}[{col}] )")

m("contexto", "Resultado %", r"Base\Obra", PCT, "Resultado ÷ orçamento (na carteira, soma ÷ soma).",
  "DIVIDE ( [Resultado da obra], [Orçamento] )", "obras[].ultimo.resultado_pct · carteira.resultado_pct")
m("contexto", "Resultado % · mês anterior", r"Base\Obra", PCT,
  "Resultado da aba anterior ÷ orçamento da aba anterior.",
  "DIVIDE ( [Resultado · mês anterior], [Orçamento · mês anterior] )", "obras[].ultimo.resultado_pct_mes_anterior")
# variação da carteira compara só as obras que têm aba no mês E no anterior (defeito de 08/10/2026: obra que abre a aba
# entrava inteira como "variação"; JANGADA jan, POTENGI mar, TIROL jun). Uma obra no contexto: igual a antes.
m("contexto", "Resultado · variação no mês", r"Base\Obra", RS,
  "Resultado − resultado do mês anterior, em R$; compara só as obras com aba no mês e no mês anterior (vazio sem "
  "nenhuma).",
  f"""VAR _comp = FILTER ( VALUES ( {F}[Obra] ), NOT ISBLANK ( [Resultado · mês anterior] ) )
RETURN
    IF ( NOT ISEMPTY ( _comp ), SUMX ( _comp, [Resultado da obra] - [Resultado · mês anterior] ) )""", "carteira.variacao_resultado")
m("contexto", "Resultado · variação p.p.", r"Base\Obra", PP,
  "Resultado % − resultado % do mês anterior, em pontos percentuais; compara só as obras com aba no mês e no mês "
  "anterior (vazio sem nenhuma).",
  f"""VAR _comp = FILTER ( VALUES ( {F}[Obra] ), NOT ISBLANK ( [Resultado · mês anterior] ) )
RETURN
    IF (
        NOT ISEMPTY ( _comp ),
        (
            DIVIDE ( SUMX ( _comp, [Resultado da obra] ), SUMX ( _comp, [Orçamento] ) )
                - DIVIDE ( SUMX ( _comp, [Resultado · mês anterior] ), SUMX ( _comp, [Orçamento · mês anterior] ) )
        ) * 100
    )""",
  "obras[].ultimo.indicadores.variacao_resultado_pp · carteira.variacao_resultado_pp")
m("contexto", "Adiantamentos", r"Base\Obra", RS, "Adiantamento de serviços + de materiais.",
  "[Adiantamento de serviços] + [Adiantamento de materiais]")
m("contexto", "Ativos não consumidos", r"Base\Obra", RS,
  "Pago e ainda não virou obra: saldo de contrato + adiantamentos + estoque + equipamentos.",
  "[Saldo de contrato] + [Adiantamento de serviços] + [Adiantamento de materiais] + [Estoque de materiais] + [Equipamentos (valor de mercado)]",
  "obras[].ultimo.ativos_nao_consumidos · carteira.ativos_nao_consumidos")
m("contexto", "Resultado sem ativos", r"Base\Obra", RS,
  "Resultado sem estoque e adiantamentos: resultado − ativos não consumidos.",
  "[Resultado da obra] - [Ativos não consumidos]", "obras[].ultimo.resultado_sem_ativos · carteira.resultado_sem_ativos")

for nome, col, desc, orac in (
        ("Físico · previsto acumulado", "PrevAcum", "% previsto acumulado (na carteira, ponderado pelo orçamento).",
         "obras[].ultimo.prev_acum · carteira.prev_acum_ponderado"),
        ("Físico · executado acumulado", "ExecAcum", "% executado acumulado (na carteira, ponderado pelo orçamento).",
         "obras[].ultimo.exec_acum · carteira.exec_acum_ponderado"),
        ("Físico · previsto no mês", "PrevMes", "% previsto do mês (na carteira, ponderado pelo orçamento).",
         "obras[].ultimo.prev_mes"),
        ("Físico · executado no mês", "ExecMes", "% executado do mês (na carteira, ponderado pelo orçamento).",
         "obras[].ultimo.exec_mes")):
    # previsto em branco (obra que não preenche o cronograma, ex.: JANGADA) fica fora da média, em vez de contar zero
    base = f"FILTER ( {F}, NOT ISBLANK ( {F}[{col}] ) )" if col.startswith("Prev") else F
    m("contexto", nome, r"Base\Físico", PCT, desc + (" Obra sem previsto na aba fica fora da média." if col.startswith("Prev") else ""),
      f"""DIVIDE (
    SUMX ( {base}, {F}[{col}] * {F}[Orcamento] ),
    SUMX ( {base}, {F}[Orcamento] )
)""", orac)
m("contexto", "Físico · desvio acumulado p.p.", r"Base\Físico", PP,
  "Executado acumulado − previsto acumulado, em pontos percentuais (< 0 = atrasada); na carteira, ponderado pelo "
  "orçamento das obras que têm previsto. Vazio quando a aba não traz o previsto.",
  f"""VAR _linhas = FILTER ( {F}, NOT ISBLANK ( {F}[PrevAcum] ) && NOT ISBLANK ( {F}[ExecAcum] ) )
VAR _orc = SUMX ( _linhas, {F}[Orcamento] )
RETURN
    IF ( _orc > 0, DIVIDE ( SUMX ( _linhas, ( {F}[ExecAcum] - {F}[PrevAcum] ) * {F}[Orcamento] ), _orc ) * 100 )""",
  "obras[].ultimo.indicadores.desvio_fisico_pp · carteira.desvio_fisico_pp")

m("contexto", "Físico · executado acumulado · com previsto", r"Base\Físico", PCT,
  "% executado acumulado só das abas que trazem o previsto, ponderado pelo orçamento: o mesmo grupo do previsto e do "
  "desvio da carteira (obra sem previsto, ex.: JANGADA, fica fora). Igual ao executado acumulado quando todas têm previsto.",
  f"""VAR _linhas = FILTER ( {F}, NOT ISBLANK ( {F}[PrevAcum] ) && NOT ISBLANK ( {F}[ExecAcum] ) )
RETURN
    DIVIDE ( SUMX ( _linhas, {F}[ExecAcum] * {F}[Orcamento] ), SUMX ( _linhas, {F}[Orcamento] ) )""",
  "carteira.exec_acum_ponderado (obras com previsto)")
m("contexto", "Físico · obras sem previsto (lista)", r"Base\Físico", TXT,
  "Obras com executado e sem previsto acumulado na aba (ficam fora do previsto e do desvio da carteira), em ordem "
  "alfabética; vazio quando todas têm previsto.",
  f"""VAR _obras =
    FILTER (
        ADDCOLUMNS (
            VALUES ( {F}[Obra] ),
            "@p", CALCULATE ( MAX ( {F}[PrevAcum] ) ),
            "@e", CALCULATE ( MAX ( {F}[ExecAcum] ) )
        ),
        ISBLANK ( [@p] ) && NOT ISBLANK ( [@e] )
    )
RETURN
    CONCATENATEX ( _obras, {F}[Obra], ", ", {F}[Obra], ASC )""")

# regra "sem previsto" (decisão de 06/10/2026; defeito achado no redesenho v2 em 07/10): na carteira, a diferença e o
# desvio do desembolso só contam o desembolsado das obras que têm previsto no mês (em jun/26 a TIROL, sem previsto,
# levava o desvio de +26% a +34%). Na obra, igual ao desembolsado dela.
m("contexto", "Desembolso · realizado com previsto no mês", r"Base\Desembolso", RS,
  "Desembolsado no mês só das obras do contexto que têm previsto no mês (regra 'sem previsto'). Na obra, igual ao "
  "desembolsado quando ela tem previsto; vazio quando não tem.",
  f"""SUMX (
    VALUES ( {F}[Obra] ),
    IF ( NOT ISBLANK ( [Desembolso · previsto no mês] ), [Desembolso · realizado no mês] )
)""", "jun/26 real: R$ 4,90 mi (sem os R$ 296 mil da TIROL) · ago/26: R$ 5,10 mi")
m("contexto", "Desembolso · diferença no mês", r"Base\Desembolso", RS,
  "Desembolsado no mês − previsto no mês, em R$, só com as obras que têm previsto (vazio sem um dos dois).",
  """VAR _prev = [Desembolso · previsto no mês]
VAR _real = [Desembolso · realizado com previsto no mês]
RETURN
    IF ( NOT ISBLANK ( _prev ) && NOT ISBLANK ( _real ), _real - _prev )""",
  "obras[].ultimo.diferenca_desembolso_rs")
m("contexto", "Desembolso · desvio no mês", r"Base\Desembolso", PCT,
  "Desembolsado no mês ÷ previsto no mês − 1, só com as obras que têm previsto (vazio sem um dos dois).",
  """VAR _prev = [Desembolso · previsto no mês]
VAR _real = [Desembolso · realizado com previsto no mês]
RETURN
    IF ( NOT ISBLANK ( _prev ) && NOT ISBLANK ( _real ), DIVIDE ( _real, _prev ) - 1 )""",
  "obras[].ultimo.indicadores.desvio_desembolso · carteira.desvio_desembolso")
m("contexto", "Justificativa do desembolso", r"Base\Desembolso", TXT,
  "Justificativa digitada na aba para a diferença do desembolso (uma obra e um mês no contexto).",
  f"SELECTEDVALUE ( {F}[Justificativa] )", "obras[].ultimo.justificativa")
m("contexto", "Justificativa · exigida", r"Base\Desembolso", INT,
  "1 quando o desvio do desembolso do mês passa de ±10% (regra proposta, a validar com a Construtora); 0 senão.",
  """VAR _desvio = [Desembolso · desvio no mês]
RETURN
    IF ( NOT ISBLANK ( _desvio ), IF ( ABS ( _desvio ) > 0.10, 1, 0 ) )""",
  "obras[].ultimo.justificativa_exigida")
m("contexto", "Justificativa · em branco", r"Base\Desembolso", INT,
  "1 quando a justificativa é exigida e a aba não traz texto; 0 senão.",
  """VAR _exigida = [Justificativa · exigida]
VAR _texto = TRIM ( [Justificativa do desembolso] )
RETURN
    IF ( NOT ISBLANK ( _exigida ), IF ( _exigida = 1 && ( ISBLANK ( _texto ) || _texto = "" ), 1, 0 ) )""",
  "obras[].ultimo.justificativa_ausente")

m("contexto", "Obras com análise", r"Base\Obra", INT,
  "Obras com aba no recorte (contexto de mês e de obra).",
  f"DISTINCTCOUNT ( {F}[Obra] )", "carteira.obras_em_andamento")

# ---------------------------------------------------------------------------------------------------------------------
# 3. Justificativas do desembolso na carteira
# ---------------------------------------------------------------------------------------------------------------------
for nome, base_ in (("exigidas", "Justificativa · exigida"), ("em branco", "Justificativa · em branco")):
    m("criticidade", f"Carteira · justificativas {nome}", r"Base\Desembolso", INT,
      f"Obras do recorte com justificativa {nome} no mês do contexto (desvio do desembolso acima de ±10%).",
      f"""SUMX ( VALUES ( {F}[Obra] ), [{base_}] )""",
      "carteira.justificativas_exigidas" if nome == "exigidas" else "carteira.justificativas_ausentes")
m("criticidade", "Carteira · justificativas preenchidas", r"Base\Desembolso", INT,
  "Justificativas exigidas no mês do contexto que estão preenchidas na planilha.",
  "[Carteira · justificativas exigidas] - [Carteira · justificativas em branco]",
  "carteira.justificativas_preenchidas")

# ---------------------------------------------------------------------------------------------------------------------
# 3b. Custo aplicado, prazo em meses e canteiro (contas de base da Nota da obra; docs/08 §3, aprovado em 28/10/2026)
# ---------------------------------------------------------------------------------------------------------------------
_ARRED = 8                  # casas do ROUND antes das faixas (o mesmo de NOTA["arred"])
F_BASE = "fBaseObra"        # base complementar 2.0, uma linha por obra × mês
F_CURVA = "fCurvaPrevista"  # curva prevista (linha de base) de cada obra, da cronograma; sem relação (lida por obra)
m("contexto", "Pago e não aplicado", r"Base\Obra", RS,
  "Pago e ainda não virou obra: estoque de materiais + adiantamentos de materiais e de serviços.",
  "[Estoque de materiais] + [Adiantamento de materiais] + [Adiantamento de serviços]")
m("contexto", "A realizar", r"Base\Obra", RS,
  "O que a planilha conta como ganho e ainda não aconteceu: saldo de contrato (desconto) + equipamentos (valor de "
  "mercado).",
  "[Saldo de contrato] + [Equipamentos (valor de mercado)]")
m("contexto", "Custo aplicado", r"Base\Obra", RS,
  "Custo do que já virou obra (CA): desembolsado corrigido + contas a pagar + dívida da obra − pago e não aplicado − "
  "receita de personalizações.",
  "[Desembolsado acumulado] + [Contas a pagar] + [Dívida da obra] - [Pago e não aplicado] - [Receita de personalizações]",
  "pipeline/conferir_ficticios.py (CA da prévia da nota)")
m("contexto", "Resultado aplicado", r"Base\Obra", RS,
  "Valor agregado (crédito do orçamento) − custo aplicado: o resultado da planilha sem o que ainda é promessa (saldo de "
  "contrato e equipamentos). Na carteira, soma.",
  """VAR _ca = [Custo aplicado]
RETURN
    IF ( NOT ISBLANK ( _ca ), [Crédito do orçamento] - _ca )""")
m("contexto", "Resultado aplicado %", r"Base\Obra", PCT, "Resultado aplicado ÷ orçamento (na carteira, soma ÷ soma).",
  "DIVIDE ( [Resultado aplicado], [Orçamento] )")
m("contexto", "IDC", r"Base\Obra", "0.000",
  "Índice de desempenho de custo: valor agregado ÷ custo aplicado (na carteira, soma ÷ soma). Acima de 1, a obra "
  "gastou menos do que o orçamento previa para o que executou.",
  """VAR _ca = [Custo aplicado]
RETURN
    IF ( _ca > 0, DIVIDE ( [Crédito do orçamento], _ca ) )""", "pipeline/conferir_ficticios.py (x_idc)")

PRZ = r"Base\Prazo"
m("contexto", "Prazo · meses decorridos", PRZ, "0",
  "Meses desde o início da obra até o mês do contexto, contando os dois (1 no mês de início). Uma obra com aba.",
  f"""VAR _ini = SELECTEDVALUE ( dObra[Inicio] )
VAR _mes = MAX ( dMes[Mes] )
RETURN
    IF ( HASONEVALUE ( dObra[Obra] ) && NOT ISBLANK ( _ini ) && NOT ISEMPTY ( {F} ), DATEDIFF ( _ini, _mes, MONTH ) + 1 )""")
m("contexto", "Prazo · meses agregados", PRZ, "0.00",
  "Cronograma agregado (Earned Schedule, Lipke): o ponto da curva prevista da obra (fCurvaPrevista) em que o previsto "
  "acumulado iguala o executado acumulado de hoje, interpolado entre os meses. Uma obra com aba.",
  f"""VAR _obra = SELECTEDVALUE ( dObra[Obra] )
VAR _e = [Físico · executado acumulado]
VAR _curva = FILTER ( ALL ( {F_CURVA} ), {F_CURVA}[Obra] = _obra )
VAR _k = MAXX ( FILTER ( _curva, {F_CURVA}[PrevAcum] <= _e ), {F_CURVA}[Indice] )
VAR _pk = MAXX ( FILTER ( _curva, {F_CURVA}[Indice] = _k ), {F_CURVA}[PrevAcum] )
VAR _pk1 = MAXX ( FILTER ( _curva, {F_CURVA}[Indice] = _k + 1 ), {F_CURVA}[PrevAcum] )
RETURN
    IF (
        HASONEVALUE ( dObra[Obra] ) && NOT ISBLANK ( _e ) && NOT ISEMPTY ( {F} ) && NOT ISBLANK ( _k ),
        IF ( ISBLANK ( _pk1 ) || _pk1 <= _pk, _k, _k + DIVIDE ( _e - _pk, _pk1 - _pk ) )
    )""")
m("contexto", "Prazo · atraso (meses)", PRZ, "0.0",
  f"Meses decorridos − meses agregados, arredondado em {_ARRED} casas: quantos meses a obra está atrás do "
  "cronograma (negativo: adiantada). Uma obra com aba.",
  f"""VAR _d = [Prazo · meses decorridos]
VAR _a = [Prazo · meses agregados]
RETURN
    IF ( NOT ISBLANK ( _d ) && NOT ISBLANK ( _a ), ROUND ( _d - _a, {_ARRED} ) )""",
  "pipeline/conferir_ficticios.py (x_atraso)")
m("contexto", "Prazo · IDP(t)", PRZ, "0.00",
  "Índice de desempenho de prazo pelo cronograma agregado: meses agregados ÷ meses decorridos (Lipke, SPI(t)).",
  "DIVIDE ( [Prazo · meses agregados], [Prazo · meses decorridos] )")
m("contexto", "Prazo · término projetado", PRZ, "mmm/yy",
  "Término projetado (Lipke, IEAC(t)): o início mais a duração prevista ÷ IDP(t), em meses inteiros. Uma obra.",
  """VAR _ini = SELECTEDVALUE ( dObra[Inicio] )
VAR _fim = SELECTEDVALUE ( dObra[TerminoPrevisto] )
VAR _idp = [Prazo · IDP(t)]
VAR _dur = DATEDIFF ( _ini, _fim, MONTH ) + 1
RETURN
    IF ( NOT ISBLANK ( _idp ) && _idp > 0 && NOT ISBLANK ( _fim ), EOMONTH ( EDATE ( _ini, ROUNDUP ( _dur / _idp, 0 ) - 1 ), -1 ) + 1 )""")
m("contexto", "Prazo · entrega contratual", PRZ, "mmm/yy", "Entrega contratual da obra (cadastro). Uma obra.",
  "SELECTEDVALUE ( dObra[EntregaContratual] )")
m("contexto", "Prazo · entrega com tolerância", PRZ, "mmm/yy",
  "Entrega contratual + 180 dias (6 meses) de tolerância (art. 43-A da Lei 4.591/64). Uma obra.",
  """VAR _e = SELECTEDVALUE ( dObra[EntregaContratual] )
RETURN
    IF ( NOT ISBLANK ( _e ), EDATE ( _e, 6 ) )""")
m("contexto", "Prazo · folga até a tolerância (meses)", PRZ, "0",
  "Meses entre o término projetado e a entrega com tolerância (negativo: o término projetado passa da tolerância).",
  """VAR _t = [Prazo · término projetado]
VAR _l = [Prazo · entrega com tolerância]
RETURN
    IF ( NOT ISBLANK ( _t ) && NOT ISBLANK ( _l ), DATEDIFF ( _t, _l, MONTH ) )""")
m("contexto", "Prazo · atraso médio (meses)", PRZ, "0.0",
  "Atraso em meses das obras do recorte com aba, ponderado pelo orçamento (na obra, o atraso dela).",
  f"""VAR _t =
    ADDCOLUMNS (
        FILTER ( VALUES ( dObra[Obra] ), NOT ISEMPTY ( RELATEDTABLE ( {F} ) ) ),
        "@a", [Prazo · atraso (meses)],
        "@o", [Orçamento]
    )
VAR _v = FILTER ( _t, NOT ISBLANK ( [@a] ) )
RETURN
    IF ( NOT ISEMPTY ( _v ), DIVIDE ( SUMX ( _v, [@a] * [@o] ), SUMX ( _v, [@o] ) ) )""")

CNT = r"Base\Canteiro"
for _nome, _col, _agr, _fmt, _desc in (
        ("Canteiro · PPC", "PPC", "AVERAGE", PCT, "PPC do mês (pacotes concluídos ÷ planejados); na carteira, a média"),
        ("Canteiro · serviços verificados", "ServicosVerificados", "SUM", INT, "Serviços verificados no mês (FVS)"),
        ("Canteiro · aprovados na 1.ª inspeção", "AprovadosPrimeira", "SUM", INT, "Serviços aprovados na primeira inspeção"),
        ("Canteiro · HHT", "HHT", "SUM", "#,0", "Horas-homem trabalhadas no mês"),
        ("Canteiro · acidentes", "Acidentes", "SUM", INT, "Acidentes com afastamento no mês"),
        ("Canteiro · dias perdidos", "DiasPerdidos", "SUM", INT, "Dias perdidos por acidente no mês (NBR 14280)"),
        ("Canteiro · NR-18 aplicáveis", "NR18Aplicaveis", "SUM", INT, "Itens aplicáveis do checklist NR-18"),
        ("Canteiro · NR-18 conformes", "NR18Conformes", "SUM", INT, "Itens conformes do checklist NR-18"),
        ("Canteiro · pedidos previstos", "PedidosPrevistos", "SUM", INT, "Pedidos com entrega prevista no mês"),
        ("Canteiro · pedidos no prazo", "PedidosNoPrazo", "SUM", INT, "Pedidos entregues no prazo e completos"),
        ("Canteiro · dias de chuva", "DiasChuva", "AVERAGE", NUM, "Dias impraticáveis por chuva; na carteira, a média"),
        ("Canteiro · acidentes 12 meses", "Acidentes12m", "SUM", INT, "Acidentes com afastamento nos 12 meses até o mês"),
        ("Canteiro · HHT 12 meses", "HHT12m", "SUM", "#,0", "Horas-homem trabalhadas nos 12 meses até o mês"),
        ("Canteiro · dias perdidos 12 meses", "DiasPerdidos12m", "SUM", INT, "Dias perdidos nos 12 meses até o mês")):
    m("contexto", _nome, CNT, _fmt, f"{_desc} (base complementar).", f"{_agr} ( {F_BASE}[{_col}] )")
for _nome, _num, _den, _desc in (
        ("Canteiro · aprovação na 1.ª inspeção", "Canteiro · aprovados na 1.ª inspeção", "Canteiro · serviços verificados",
         "Serviços aprovados na primeira inspeção ÷ serviços verificados"),
        ("Canteiro · conformidade NR-18", "Canteiro · NR-18 conformes", "Canteiro · NR-18 aplicáveis",
         "Itens conformes ÷ itens aplicáveis do checklist NR-18"),
        ("Canteiro · entregas no prazo", "Canteiro · pedidos no prazo", "Canteiro · pedidos previstos",
         "Pedidos entregues no prazo e completos ÷ pedidos com entrega prevista")):
    m("contexto", _nome, CNT, PCT, f"{_desc} (na carteira, soma ÷ soma); vazio sem o denominador.",
      f"""VAR _d = [{_den}]
RETURN
    IF ( _d > 0, DIVIDE ( [{_num}], _d ) )""")
m("contexto", "Canteiro · taxa de frequência (12 meses)", CNT, "0.0",
  "Taxa de frequência de acidentes com afastamento nos 12 meses até o mês (NBR 14280): acidentes × 1.000.000 ÷ HHT.",
  """VAR _h = [Canteiro · HHT 12 meses]
RETURN
    IF ( _h > 0, DIVIDE ( [Canteiro · acidentes 12 meses] * 1000000, _h ) )""")
m("contexto", "Canteiro · taxa de gravidade (12 meses)", CNT, "0",
  "Taxa de gravidade nos 12 meses até o mês (NBR 14280): dias perdidos × 1.000.000 ÷ HHT. Só informação.",
  """VAR _h = [Canteiro · HHT 12 meses]
RETURN
    IF ( _h > 0, DIVIDE ( [Canteiro · dias perdidos 12 meses] * 1000000, _h ) )""")


# ---------------------------------------------------------------------------------------------------------------------
# 3c. Régua: Nota da obra (docs/08 §3) — FONTE ÚNICA de faixas, pontos e limites (o dicionário NOTA)
# ---------------------------------------------------------------------------------------------------------------------
# O dicionário NOTA gera as medidas `Nota · …` abaixo, a tabela dItemNota (pbi/m/dItemNota.m), as regras de leitura da
# base (pbi/m/fxRegrasBase.m), a prévia da nota dos dados fictícios (pipeline/conferir_ficticios.py, o oráculo) e as
# tabelas calculadas dRankingNota e dItemRankingNota. Nenhum limite da régua fica escrito à mão em outro lugar.
#
# Faixa = (operador, limite, pontos), avaliadas de cima para baixo: vale a primeira que bate; ("resto", None, pontos)
# fecha a lista. O X é arredondado com ROUND(…, ARRED) antes de comparar.
NOTA: dict = {
    "arred": _ARRED,
    "versao_base": "BC 2.0",
    # campo da base: (coluna no modelo, rótulo na planilha, faixa válida)
    "base": [
        ("PPC", "PPC do mês", (0, 1)),
        ("ServicosVerificados", "Serviços verificados", (0, 100000)),
        ("AprovadosPrimeira", "Aprovados na primeira inspeção", (0, 100000)),
        ("HHT", "Horas-homem trabalhadas (HHT)", (0, 10000000)),
        ("Acidentes", "Acidentes com afastamento", (0, 1000)),
        ("DiasPerdidos", "Dias perdidos", (0, 100000)),
        ("NR18Aplicaveis", "Itens NR-18 aplicáveis", (0, 10000)),
        ("NR18Conformes", "Itens NR-18 conformes", (0, 10000)),
        ("PedidosPrevistos", "Pedidos com entrega prevista", (0, 100000)),
        ("PedidosNoPrazo", "Pedidos entregues no prazo e completos", (0, 100000)),
        ("DiasChuva", "Dias impraticáveis por chuva", (0, 31)),
    ],
    # X = VA ÷ CA (valor agregado ÷ custo aplicado)
    "idc": [(">=", 1.00, 3.0), (">=", 0.98, 2.5), (">=", 0.96, 2.0), (">=", 0.94, 1.5), (">=", 0.92, 1.0),
            (">=", 0.90, 0.5), ("resto", None, 0)],
    # X = meses decorridos − meses agregados (Earned Schedule, Lipke); obra adiantada (X < 0) leva o ponto cheio
    "atraso": [("<=", 0.5, 2.0), ("<=", 1, 1.5), ("<=", 2, 1.0), ("<=", 3, 0.5), ("resto", None, 0)],
    "ppc": [(">=", 0.80, 1.0), (">=", 0.70, 0.5), (">=", 0.60, 0.25), ("resto", None, 0)],
    # X = |desembolsado no mês ÷ previsto no mês − 1| (a conta do antigo Fluxo de caixa)
    "caixa": [("<", 0.10, 1.0), ("<=", 0.20, 0.5), ("resto", None, 0)],
    "inspecao": [(">=", 0.95, 1.0), (">=", 0.90, 0.75), (">=", 0.85, 0.5), (">=", 0.80, 0.25), ("resto", None, 0)],
    # X = taxa de frequência (NBR 14280) nos últimos `janela_acidentes` meses; 7,5 ≈ a média do setor (CBIC, 2018)
    "acidentes": [("<=", 0, 0.5), ("<=", 7.5, 0.25), ("resto", None, 0)],
    "nr18": [(">=", 0.95, 0.5), (">=", 0.85, 0.25), ("resto", None, 0)],
    "entregas": [(">=", 0.90, 0.5), (">=", 0.80, 0.25), ("resto", None, 0)],
    # X = checagens da aba que passam (de 3): conta fecha, justificativa quando exigida, previsto acumulado não caiu
    "analise": [(">=", 3, 0.5), (">=", 2, 0.25), ("resto", None, 0)],
    "janela_acidentes": 12,
    "status": [(">=", 8, 0), (">=", 6, 1), ("resto", None, 2)],
    # trava: crítico com qualquer nota
    "trava": {"idc_abaixo": 0.90, "atraso_acima": 3},
    # itens, na ordem de dItemNota: (código, chave das faixas, dimensão, rótulo, curto, médio, em frase, sufixo das
    # medidas, fonte, unidade do X, como a tela explica)
    "itens": [
        ("custo", "idc", "Custo", "Custo (IDC)", "Custo", "Custo · IDC", "o custo", "custo", "Análise Crítica", "indice",
         "Para cada R$ 1,00 aplicado, quanto de orçamento a obra entregou (valor agregado ÷ custo aplicado)."),
        ("prazo", "atraso", "Prazo", "Atraso em meses", "Atraso", "Prazo · atraso", "o atraso", "prazo", "Análise Crítica",
         "meses", "Quantos meses a obra está atrás do cronograma: o executado de hoje é o previsto de quantos meses atrás."),
        ("ppc", "ppc", "Prazo", "Plano semanal cumprido (PPC)", "PPC", "Prazo · PPC", "o plano semanal", "PPC",
         "Base complementar", "pct", "De cada 10 tarefas prometidas na semana, quantas foram feitas (média do mês)."),
        ("caixa", "caixa", "Caixa", "Acerto da previsão de caixa", "Caixa", "Previsão de caixa", "a previsão de caixa",
         "caixa", "Análise Crítica", "pct", "Quanto o desembolso do mês fugiu do previsto, para mais ou para menos."),
        ("inspecao", "inspecao", "Qualidade", "Aprovação na 1.ª inspeção", "1.ª inspeção", "Qualidade · 1.ª inspeção",
         "a aprovação na 1.ª inspeção", "inspeção", "Base complementar", "pct",
         "Serviços aprovados na primeira inspeção, sem retrabalho, entre os verificados no mês."),
        ("acidentes", "acidentes", "Segurança", "Frequência de acidentes", "Acidentes", "Segurança · acidentes",
         "a frequência de acidentes", "acidentes", "Base complementar", "taxa",
         "Acidentes com afastamento por milhão de horas trabalhadas, nos últimos 12 meses (NBR 14280)."),
        ("nr18", "nr18", "Segurança", "Canteiro conforme NR-18", "NR-18", "Segurança · NR-18", "o canteiro (NR-18)",
         "NR-18", "Base complementar", "pct", "Itens do checklist da NR-18 conformes, entre os aplicáveis no mês."),
        ("entregas", "entregas", "Suprimentos", "Entregas no prazo e completas", "Entregas", "Suprimentos · entregas",
         "as entregas de material", "entregas", "Base complementar", "pct",
         "Pedidos de material entregues no prazo e completos, entre os previstos no mês."),
        ("analise", "analise", "Gestão", "Análise crítica sem pendência", "Análise crítica", "Gestão · análise crítica",
         "a análise crítica", "análise crítica", "Análise Crítica", "checagens",
         "Checagens da planilha do mês: a conta fecha, há justificativa quando o caixa desvia e o previsto não caiu."),
    ],
}
NOTA_DIMENSOES = ["Custo", "Prazo", "Caixa", "Qualidade", "Segurança", "Suprimentos", "Gestão"]


def nota_pontos(faixas, x):
    """Pontos de X nas faixas (de cima para baixo; vale a primeira que bate). X vazio → None."""
    if x is None:
        return None
    x = round(x, NOTA["arred"])
    for op, lim, pts in faixas:
        if op == "resto" or (op == ">=" and x >= lim) or (op == "<=" and x <= lim) or (op == "<" and x < lim):
            return pts
    return None


def nota_item(cod: str) -> dict:
    """Registro do item do dicionário NOTA (chaves com nome)."""
    for c, fx, dim, rot, curto, medio, frase, suf, fonte, unid, explica in NOTA["itens"]:
        if c == cod:
            return {"cod": c, "faixas": NOTA[fx], "chave": fx, "dimensao": dim, "rotulo": rot, "curto": curto,
                    "medio": medio, "frase": frase, "suf": suf, "fonte": fonte, "unid": unid, "explica": explica}
    raise KeyError(cod)


NOTA_ITENS = [nota_item(c) for c, *_ in NOTA["itens"]]


def nota_maximo(cod: str) -> float:
    """Máximo do item: a maior pontuação das faixas."""
    return max(p for _o, _l, p in nota_item(cod)["faixas"])


def _n(v) -> str:
    """Número para a DAX e para o M (ponto decimal, sem zeros sobrando)."""
    return f"{v:.10g}"


def _br(v, pct: bool) -> str:
    """Número para o leitor: vírgula decimal, menos tipográfico; em % quando pct."""
    x = v * 100 if pct else v
    t = f"{x:.4f}".rstrip("0").rstrip(".").replace("-", "−").replace(".", ",")
    return (t if t != "−0" else "0") + ("%" if pct else "")


# como cada unidade escreve o X e os limites nas faixas
NOTA_VAR = {"indice": "IDC", "meses": "atraso", "pct": "X", "taxa": "TF", "checagens": "checagens"}
# nome do X nos rótulos das faixas, quando o da unidade não diz o que é ("X ≥ 80%" → "PPC ≥ 80%")
NOTA_VAR_ITEM = {"ppc": "PPC", "caixa": "desvio", "inspecao": "aprovação", "nr18": "conformidade",
                 "entregas": "entregas"}


def nota_valor(unid: str, v: float) -> str:
    """Limite de faixa para o leitor, na unidade do item (0,98 · 0,5 mês · 2 meses · 80% · 7,5 · 3 de 3)."""
    if unid == "indice":
        return f"{v:.2f}".replace(".", ",")
    if unid == "meses":
        return f"{_br(v, False)} {'mês' if abs(v) <= 1 else 'meses'}"
    if unid == "pct":
        return _br(v, True)
    if unid == "checagens":
        return f"{_n(v)} de 3"
    return _br(v, False)


def nota_rotulos(cod: str) -> list[str]:
    """Rótulo de cada faixa do item ("IDC ≥ 1,00", "0,98 ≤ IDC < 1,00", "atraso ≤ 0,5 mês", "TF = 0", "3 de 3")."""
    it = nota_item(cod)
    faixas, unid, var = it["faixas"], it["unid"], NOTA_VAR_ITEM.get(cod, NOTA_VAR[it["unid"]])
    b_ = lambda v: nota_valor(unid, v)  # noqa: E731
    if unid == "checagens":
        return ["3 de 3", "2 de 3", "0 ou 1 de 3"]
    out, ant = [], None
    for op, lim, _p in faixas:
        if op == "resto":
            out.append({">=": f"{var} < {b_(ant[1])}", "<=": f"{var} > {b_(ant[1])}", "<": f"{var} ≥ {b_(ant[1])}"}[ant[0]])
            continue
        if ant is None:
            out.append(f"{var} = 0" if (op == "<=" and lim == 0) else
                       {">=": f"{var} ≥ {b_(lim)}", "<=": f"{var} ≤ {b_(lim)}", "<": f"{var} < {b_(lim)}"}[op])
        elif op == ">=":
            out.append(f"{b_(lim)} ≤ {var} < {b_(ant[1])}")
        elif op == "<=":
            out.append(f"0 < {var} ≤ {b_(lim)}" if ant[1] == 0 and unid == "taxa" else
                       f"{b_(ant[1])} {'≤' if ant[0] == '<' else '<'} {var} ≤ {b_(lim)}")
        else:
            out.append(f"{b_(ant[1])} ≤ {var} < {b_(lim)}")
        ant = (op, lim)
    return out


def nota_texto_faixas(cod: str) -> str:
    """Texto das faixas para exibição (dItemNota[FaixaTexto]): rótulo → pontos, separados por " · "."""
    it = nota_item(cod)
    return " · ".join(f"{r} → {_br(p, False)}" for r, (_o, _l, p) in zip(nota_rotulos(cod), it["faixas"]))


def dax_faixas(x: str, faixas, valores=None, recuo: int = 12) -> str:
    """SWITCH ( TRUE (), x op limite, valor, …, resto ) — valores = pontos (padrão) ou os rótulos."""
    vals = valores if valores is not None else [_n(p) for _o, _l, p in faixas]
    pad = " " * recuo
    casos = [f"{pad}    {x} {op} {_n(lim)}, {v}," for (op, lim, _p), v in zip(faixas, vals) if op != "resto"]
    resto = [v for (op, _l, _p), v in zip(faixas, vals) if op == "resto"]
    return "SWITCH (\n" + f"{pad}    TRUE (),\n" + "\n".join(casos) + f"\n{pad}    {resto[0]}\n{pad})"


def m_ditem_nota() -> str:
    """pbi/m/dItemNota.m, gerado do dicionário NOTA."""
    linhas = []
    for i, it in enumerate(NOTA_ITENS, 1):
        vals = [f'"{it["cod"]}"', str(i), f'"{it["dimensao"]}"', str(NOTA_DIMENSOES.index(it["dimensao"]) + 1),
                f'"{it["rotulo"]}"', f'"{it["curto"]}"', f'"{it["medio"]}"', f'"{it["frase"]}"',
                _n(nota_maximo(it["cod"])), f'"{it["fonte"]}"', f'"{it["unid"]}"', f'"{nota_texto_faixas(it["cod"])}"',
                f'"{it["explica"]}"']
        linhas.append("            {" + ", ".join(vals) + "}")
    return f"""/*
@tipo: tabela
@descricao: Os {len(NOTA_ITENS)} itens da Nota da obra (docs/08 §3), com a dimensão, o máximo, a fonte, a unidade do X, o texto das faixas e a explicação de uma linha. Eixo das listas e dos tooltips por item (e, por Dimensao, das listas por dimensão). GERADA por pbi/scripts/contas_base.py a partir do dicionário NOTA (fonte única): não edite à mão.
@coluna: Item | texto | chave | Código do item.
@coluna: Ordem | inteiro | formato=0 | Ordem do item na régua (1 = custo).
@coluna: Dimensao | texto | ordenar=OrdemDimensao | Dimensão (Custo, Prazo, Caixa, Qualidade, Segurança, Suprimentos, Gestão).
@coluna: OrdemDimensao | inteiro | oculta; formato=0 | Ordem da dimensão.
@coluna: Rotulo | texto | ordenar=Ordem | Nome do item.
@coluna: RotuloCurto | texto | ordenar=Ordem | Nome curto, para listas.
@coluna: RotuloMedio | texto | ordenar=Ordem | Nome médio, para tabelas de tooltip.
@coluna: RotuloFrase | texto | | Nome dentro de frase, com artigo (o custo, a previsão de caixa).
@coluna: Maximo | decimal | formato=0.00 | Pontos máximos do item (a soma dá 10).
@coluna: Fonte | texto | | Análise Crítica ou Base complementar.
@coluna: Unidade | texto | | Unidade do X: indice, meses, pct, taxa ou checagens.
@coluna: FaixaTexto | texto | | Faixas → pontos, para exibição.
@coluna: Explica | texto | | O que o item mede, em uma linha.
*/
let
    Tabela = #table(
        type table [Item = text, Ordem = Int64.Type, Dimensao = text, OrdemDimensao = Int64.Type, Rotulo = text,
            RotuloCurto = text, RotuloMedio = text, RotuloFrase = text, Maximo = number, Fonte = text, Unidade = text,
            FaixaTexto = text, Explica = text],
        {{
{(","+chr(10)).join(linhas)}
        }})
in
    Tabela
"""


NOTA_P = r"Base\Nota"
PTS = "0.00"
AR = NOTA["arred"]
OBRAS = "VALUES ( dObra[Obra] )"          # iteração por obra (blank-safe: obra sem linha no mês não soma)
# obras da carteira no contexto (com aba da Análise Crítica). Itera dObra, e não fAnaliseCritica[Obra]: o filtro na
# coluna do fato não chega a fBaseObra, e as contas da base complementar veriam todas as obras.
OBRAS_AC = f"FILTER ( VALUES ( dObra[Obra] ), NOT ISEMPTY ( RELATEDTABLE ( {F} ) ) )"
SUF = {it["cod"]: it["suf"] for it in NOTA_ITENS}

# contas que só têm sentido com UMA obra no contexto: com várias (total, carteira), vazias em vez de somar ou pegar o
# máximo. Pontos, possíveis, obtidos, perdidos e itens faltando continuam somando.
UMA_OBRA = {f"Nota · X {SUF[c]}" for c in SUF} | {f"Nota · faixa atingida · {SUF[c]}" for c in SUF} | {
    "Nota · completa", "Nota · nota final", "Nota · status", "Nota · pendente", "Nota · trava", "Nota · trava · motivo",
    "Nota · análise crítica · checagens (lista)"}


def nota(nome: str, formato: str, descricao: str, dax: str,
         oraculo: str = "pipeline/conferir_ficticios.py · prévia da nota (dados/_gabarito/nota_previa.csv)") -> None:
    if nome in UMA_OBRA:
        corpo = "\n".join(("    " + l) if l.strip() else "" for l in dax.strip("\n").split("\n"))
        dax = f"IF (\n    HASONEVALUE ( dObra[Obra] ),    -- uma obra no contexto; com várias, vazio\n{corpo}\n)"
        descricao += " Só com uma obra no contexto (com várias, vazio)."
    m("nota", nome, NOTA_P, formato, descricao, dax, oraculo)


def _chave(t: str) -> str:
    import unicodedata
    return " ".join(unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower().split())


def m_regras_base() -> str:
    """pbi/m/fxRegrasBase.m: versão do modelo da base complementar, rótulo e faixa válida de cada campo numérico (do
    dicionário NOTA, base 2.0)."""
    campos = ", ".join(f'{{"{c}", {{"{_chave(r)}"}}, "{r}"}}' for c, r, _f in NOTA["base"])
    f_m = ", ".join(f"{c} = {{{_n(a)}, {_n(b)}}}" for c, _r, (a, b) in NOTA["base"])
    return f"""/*
@tipo: funcao
@descricao: Regras de leitura das bases complementares (modelo {NOTA['versao_base']}), GERADAS por pbi/scripts/contas_base.py a partir do dicionário NOTA (fonte única): a versão do modelo, o rótulo de cada campo na coluna B (normalizado, como fxNormaliza) com o rótulo para os avisos, e a faixa válida de cada campo numérico (fora dela, o campo fica sem dado e stgAbasBase avisa). Não edite à mão.
*/
() as record =>
    [
        Versao = "{NOTA['versao_base']}",
        Campos = {{{campos}}},
        Faixas = [{f_m}]
    ]
"""


def por_obra(corpo: str) -> str:
    """SUMX por obra: a regra vale para uma obra; com várias no contexto, soma (carteira)."""
    return f"SUMX (\n    {OBRAS},\n{corpo}\n)"


# ---- X de cada item (uma obra) ----
nota("Nota · obra presente", INT,
     "1 quando há aba da Análise Crítica ou da base complementar no contexto (obra × mês); vazio sem nenhuma.",
     f"IF ( NOT ISEMPTY ( {F} ) || NOT ISEMPTY ( {F_BASE} ), 1 )")
nota("Nota · gestor", TXT, "Gestor da obra, como a base complementar traz.", f"SELECTEDVALUE ( {F_BASE}[Gestor] )")
nota("Nota · X custo", "0.000", f"IDC da obra (valor agregado ÷ custo aplicado), arredondado em {AR} casas; vazio sem "
     "aba ou com custo aplicado zero.",
     f"""VAR _x = [IDC]
RETURN
    IF ( NOT ISBLANK ( _x ), ROUND ( _x, {AR} ) )""")
nota("Nota · X prazo", "0.0", "Atraso em meses (cronograma agregado): meses decorridos − meses agregados; negativo, "
     "adiantada. Vazio sem aba ou sem a curva prevista.", "[Prazo · atraso (meses)]")
nota("Nota · X PPC", PCT, f"PPC do mês (base), arredondado em {AR} casas; vazio fora de 0 a 100%.",
     f"""VAR _x = MAX ( {F_BASE}[PPC] )
RETURN
    IF ( NOT ISBLANK ( _x ) && _x >= 0 && _x <= 1, ROUND ( _x, {AR} ) )""")
nota("Nota · X caixa", PCT,
     f"|desembolsado no mês ÷ previsto no mês − 1|, arredondado em {AR} casas; vazio sem previsto (ou previsto 0) ou "
     "sem desembolsado no mês.",
     f"""VAR _prev = [Desembolso · previsto no mês]
VAR _real = [Desembolso · realizado no mês]
RETURN
    IF ( NOT ISBLANK ( _prev ) && _prev <> 0 && NOT ISBLANK ( _real ), ROUND ( ABS ( DIVIDE ( _real, _prev ) - 1 ), {AR} ) )""")
for _cod, _num, _den in (("inspecao", "AprovadosPrimeira", "ServicosVerificados"),
                         ("nr18", "NR18Conformes", "NR18Aplicaveis"),
                         ("entregas", "PedidosNoPrazo", "PedidosPrevistos")):
    nota(f"Nota · X {SUF[_cod]}", PCT,
         f"{_num} ÷ {_den} da base, arredondado em {AR} casas; vazio sem {_den} ou com a parte maior que o todo.",
         f"""VAR _n = SUM ( {F_BASE}[{_num}] )
VAR _d = SUM ( {F_BASE}[{_den}] )
RETURN
    IF ( _d > 0 && NOT ISBLANK ( _n ) && _n >= 0 && _n <= _d, ROUND ( DIVIDE ( _n, _d ), {AR} ) )""")
nota("Nota · X acidentes", "0.0",
     f"Taxa de frequência (NBR 14280) nos {NOTA['janela_acidentes']} meses até o mês, arredondada em {AR} casas; vazio "
     "sem horas trabalhadas.",
     f"""VAR _x = [Canteiro · taxa de frequência (12 meses)]
RETURN
    IF ( NOT ISBLANK ( _x ), ROUND ( _x, {AR} ) )""")
_CHECAGENS = f"""VAR _conta = INT ( ABS ( SUM ( {F}[Resultado] ) - SUM ( {F}[ResultadoRegra] ) ) < 1 )
VAR _just = INT ( NOT ( [Justificativa · em branco] = 1 ) )
VAR _prev = SELECTEDVALUE ( {F}[PrevAcum] )
VAR _ant = SELECTEDVALUE ( {F}[PrevAcumAnterior] )
VAR _naoCaiu = INT ( ISBLANK ( _prev ) || ISBLANK ( _ant ) || _prev >= _ant - 0.000001 )"""
nota("Nota · X análise crítica", INT,
     "Checagens da aba do mês que passam (de 3): a conta fecha (resultado apresentado = regra, ± R$ 1); há "
     "justificativa quando o caixa desvia mais de 10%; o previsto acumulado não caiu. Vazio sem aba.",
     f"""{_CHECAGENS}
RETURN
    IF ( NOT ISEMPTY ( {F} ), _conta + _just + _naoCaiu )""")
nota("Nota · análise crítica · checagens (lista)", TXT,
     "As checagens da aba do mês que falharam, separadas por '|' (conta|justificativa|previsto); vazio quando todas "
     "passam ou sem aba.",
     f"""{_CHECAGENS}
VAR _t = {{ ( "conta", _conta ), ( "justificativa", _just ), ( "previsto", _naoCaiu ) }}
RETURN
    IF ( NOT ISEMPTY ( {F} ), CONCATENATEX ( FILTER ( _t, [Value2] = 0 ), [Value1], "|" ) )""")

# ---- pontos, possíveis e faixa atingida de cada item ----
NOTA_ITEM_MEDIDAS = {}   # código → (pontos, possíveis, X, faixa atingida)


def _de(frase: str) -> str:
    """'de' + a frase do item, com a contração ('do custo', 'da previsão de caixa', 'das entregas')."""
    for art, contr in (("os ", "dos "), ("as ", "das "), ("o ", "do "), ("a ", "da ")):
        if frase.startswith(art):
            return contr + frase[len(art):]
    return "de " + frase


for it in NOTA_ITENS:
    c, s = it["cod"], it["suf"]
    _x, _pts, _poss, _fx = f"Nota · X {s}", f"Nota · pontos {s}", f"Nota · possíveis · {s}", f"Nota · faixa atingida · {s}"
    NOTA_ITEM_MEDIDAS[c] = (_pts, _poss, _x, _fx)
    nota(_pts, PTS,
         f"Pontos {_de(it['frase'])} (máx. {_br(nota_maximo(c), False)}): {nota_texto_faixas(c)}; vazio sem dado. Uma "
         "obra; com várias, soma.",
         por_obra(f"""    VAR _x = [{_x}]
    RETURN
        IF ( NOT ISBLANK ( _x ), {dax_faixas("_x", it["faixas"], recuo=8)} )"""))
    nota(_poss, PTS, f"Máximo {_de(it['frase'])} ({_br(nota_maximo(c), False)}) quando o item tem dado. Uma obra; com "
         "várias, soma.", por_obra(f"    IF ( NOT ISBLANK ( [{_pts}] ), {_n(nota_maximo(c))} )"))
    nota(_fx, TXT, f"Faixa {_de(it['frase'])} em que o X caiu (rótulo gerado dos limites).",
         f"""VAR _x = [{_x}]
RETURN
    IF ( NOT ISBLANK ( _x ), {dax_faixas("_x", it["faixas"], [f'"{r}"' for r in nota_rotulos(c)], recuo=4)} )""")

# ---- valor fora da faixa (base): o campo tem valor, mas o item fica sem pontos ----
_FORA = {  # código → (expressão que diz "tem valor cru na base")
    "ppc": f"NOT ISBLANK ( MAX ( {F_BASE}[PPC] ) )",
    "inspecao": f"NOT ISBLANK ( SUM ( {F_BASE}[AprovadosPrimeira] ) ) && SUM ( {F_BASE}[ServicosVerificados] ) > 0",
    "nr18": f"NOT ISBLANK ( SUM ( {F_BASE}[NR18Conformes] ) ) && SUM ( {F_BASE}[NR18Aplicaveis] ) > 0",
    "entregas": f"NOT ISBLANK ( SUM ( {F_BASE}[PedidosNoPrazo] ) ) && SUM ( {F_BASE}[PedidosPrevistos] ) > 0",
}
nota("Nota · itens fora da faixa", INT,
     "Itens com valor na base, mas fora da faixa válida (PPC fora de 0 a 100%; aprovados, conformes ou entregues maior "
     "que o total): ficam sem pontos e já contam em 'itens faltando na base'. Soma pelas obras presentes.",
     por_obra("""    IF (
        [Nota · obra presente] = 1,
        """ + "\n            + ".join(f"INT ( {expr} && ISBLANK ( [Nota · X {SUF[c]}] ) )" for c, expr in _FORA.items())
              + "\n    )"))

# ---- totais da obra ----
nota("Nota · pontos possíveis", PTS, "Soma dos máximos dos itens com dado (10 com tudo preenchido); vazio sem nenhum item.",
     f"""VAR _p =
    {(chr(10) + '        + ').join(f'[{NOTA_ITEM_MEDIDAS[c][1]}]' for c in NOTA_ITEM_MEDIDAS)}
RETURN
    IF ( NOT ISBLANK ( _p ), ROUND ( _p, {AR} ) )""")
nota("Nota · pontos obtidos", PTS, "Soma dos pontos dos itens com dado.",
     f"""VAR _p =
    {(chr(10) + '        + ').join(f'[{NOTA_ITEM_MEDIDAS[c][0]}]' for c in NOTA_ITEM_MEDIDAS)}
RETURN
    IF ( NOT ISBLANK ( _p ), ROUND ( _p, {AR} ) )""")
nota("Nota · pontos perdidos", PTS,
     "Pontos possíveis − pontos obtidos: ordem das obras, obra em foco e 'onde a carteira perde pontos'.",
     f"""VAR _p = [Nota · pontos possíveis]
RETURN
    IF ( NOT ISBLANK ( _p ), ROUND ( _p - [Nota · pontos obtidos], {AR} ) )""")
_com_dado = "\n                + ".join(f"INT ( NOT ISBLANK ( [{NOTA_ITEM_MEDIDAS[c][0]}] ) )" for c in NOTA_ITEM_MEDIDAS)
nota("Nota · itens faltando", INT,
     f"Itens da nota sem dado ({len(NOTA_ITEM_MEDIDAS)} no total). Soma pelas obras presentes no contexto.",
     por_obra(f"""    IF (
        [Nota · obra presente] = 1,
        {len(NOTA_ITEM_MEDIDAS)}
            - (
                {_com_dado}
            )
    )"""))
_FONTE_ITEM = {it["cod"]: it["fonte"] for it in NOTA_ITENS}
for _rot, _fonte in (("na base", "Base complementar"), ("na planilha", "Análise Crítica")):
    _cods = [c for c in NOTA_ITEM_MEDIDAS if _FONTE_ITEM[c] == _fonte]
    _soma = "\n                + ".join(f"INT ( NOT ISBLANK ( [{NOTA_ITEM_MEDIDAS[c][0]}] ) )" for c in _cods)
    nota(f"Nota · itens faltando {_rot}", INT,
         f"Itens da fonte '{_fonte}' sem dado ({len(_cods)} itens: "
         + ", ".join(nota_item(c)["curto"] for c in _cods) + "). Soma pelas obras presentes no contexto.",
         por_obra(f"""    IF (
        [Nota · obra presente] = 1,
        {len(_cods)}
            - (
                {_soma}
            )
    )"""))
_cods_pl = [c for c in NOTA_ITEM_MEDIDAS if _FONTE_ITEM[c] == "Análise Crítica"]
_tab_pl = ",\n        ".join(f'( "{c}", INT ( ISBLANK ( [{NOTA_ITEM_MEDIDAS[c][0]}] ) ) )' for c in _cods_pl)
nota("Nota · itens faltando na planilha (lista)", TXT,
     "Códigos (dItemNota) dos itens da Análise Crítica sem dado para a obra do contexto, na ordem da régua, separados "
     "por '|'; vazio sem falta ou sem obra. Uma obra no contexto.",
     f"""VAR _falta =
    {{
        {_tab_pl}
    }}
RETURN
    IF (
        HASONEVALUE ( dObra[Obra] ) && [Nota · obra presente] = 1,
        CONCATENATEX ( FILTER ( _falta, [Value2] = 1 ), [Value1], "|" )
    )""")
nota("Nota · completa", INT,
     f"1 quando a obra tem os {len(NOTA_ITEM_MEDIDAS)} itens com dado; 0 quando falta algum; vazio sem obra no contexto.",
     """VAR _f = [Nota · itens faltando]
RETURN
    IF ( NOT ISBLANK ( _f ), IF ( _f = 0, 1, 0 ) )""")
nota("Nota · nota final", PTS, "Nota da obra (0 a 10): a soma dos pontos, só com todos os itens com dado (senão, vazio "
     "e a obra fica pendente).",
     f"""IF (
    [Nota · completa] = 1,
    ROUND ( [Nota · pontos obtidos], {AR} )
)""")
_tv = NOTA["trava"]
nota("Nota · trava", INT,
     f"1 quando a trava da régua vale: IDC abaixo de {_br(_tv['idc_abaixo'], False)} ou atraso acima de "
     f"{_br(_tv['atraso_acima'], False)} meses (crítico com qualquer nota); 0 senão; vazio sem nota.",
     f"""VAR _idc = [Nota · X custo]
VAR _atraso = [Nota · X prazo]
RETURN
    IF (
        [Nota · completa] = 1,
        IF ( _idc < {_n(_tv['idc_abaixo'])} || _atraso > {_n(_tv['atraso_acima'])}, 1, 0 )
    )""")
nota("Nota · trava · motivo", TXT, "Por que a trava vale: 'custo' (IDC abaixo do limite), 'prazo' (atraso acima do "
     "limite) ou 'custo|prazo'; vazio sem trava.",
     f"""VAR _idc = [Nota · X custo]
VAR _atraso = [Nota · X prazo]
VAR _c = IF ( _idc < {_n(_tv['idc_abaixo'])}, "custo" )
VAR _p = IF ( _atraso > {_n(_tv['atraso_acima'])}, "prazo" )
RETURN
    IF ( [Nota · trava] = 1, _c & IF ( _c <> "" && _p <> "", "|" ) & _p )""")
_st_rot = ", ".join(f"{('≥ ' + _br(l, False)) if o != 'resto' else 'abaixo'} → {p}" for o, l, p in NOTA["status"])
nota("Nota · status", INT,
     f"Status pela nota: {_st_rot} (0 estável · 1 atenção · 2 crítico); com a trava, crítico. Vazio quando pendente.",
     f"""VAR _n = [Nota · nota final]
RETURN
    IF ( NOT ISBLANK ( _n ), IF ( [Nota · trava] = 1, 2, {dax_faixas("_n", NOTA["status"], recuo=4)} ) )""")
nota("Nota · pendente", INT, "1 quando a obra está no contexto e falta algum item (sem nota nem status); 0 quando completa.",
     """IF ( [Nota · obra presente] = 1, IF ( [Nota · completa] = 1, 0, 1 ) )""")

# Ranking da nota por obra × mês, guardado numa TABELA CALCULADA (calculada no refresh), por desempenho: a obra em
# foco, a posição, as listas e a carteira leem esta tabela, filtrada por mês e recorte (sem relação: as medidas que a
# calculam filtram dObra e dMes, e uma relação daria dependência circular). A regra continua só nas medidas.
_RANK_COLS = [("Perdidos", "Nota · pontos perdidos"), ("NotaOrdem", "Nota · nota final"), ("Status", "Nota · status"),
              ("Pendente", "Nota · pendente"), ("Obtidos", "Nota · pontos obtidos"),
              ("Possiveis", "Nota · pontos possíveis"), ("Trava", "Nota · trava")]


def _rank_col(col: str, medida: str) -> str:
    calc = (f"CALCULATE ( [{medida}], REMOVEFILTERS ( fAnaliseCritica ), REMOVEFILTERS ( {F_BASE} ), "
            "dObra[Obra] = _o, dMes[Mes] = _m )")
    if col == "NotaOrdem":
        calc = f"COALESCE (\n                    {calc},\n                    99\n                )"
    return f"""        "{col}",
            VAR _o = [Obra]
            VAR _m = [Mes]
            RETURN
                {calc}"""


RANKING_NOTA = f"""/*
@tipo: tabela-calculada
@descricao: Ranking da nota por obra × mês (obras com aba da Análise Crítica ou com a base complementar no mês): pontos perdidos, nota para desempate (pendente = 99), status, pendente, pontos obtidos e possíveis e a trava, copiados das medidas Nota no refresh. TemAC = 1 nas linhas com aba da Análise Crítica: a obra em foco, a posição, as listas e a carteira leem só essas; as leituras · ranking leem todas. GERADA por pbi/scripts/contas_base.py; a regra fica nas medidas.
@oculta: sim
@coluna: Obra | texto | | Obra.
@coluna: Mes | data | formato=dd/mm/yyyy | Mês.
@coluna: TemAC | inteiro | formato=0 | 1 quando a obra tem aba da Análise Crítica no mês.
@coluna: Perdidos | decimal | formato=0.00 | [Nota · pontos perdidos] da obra no mês.
@coluna: NotaOrdem | decimal | formato=0.00 | [Nota · nota final] da obra no mês; 99 quando pendente (desempate: a pendente vai depois).
@coluna: Status | inteiro | formato=0 | [Nota · status] (vazio quando pendente).
@coluna: Pendente | inteiro | formato=0 | [Nota · pendente].
@coluna: Obtidos | decimal | formato=0.00 | [Nota · pontos obtidos] da obra no mês.
@coluna: Possiveis | decimal | formato=0.00 | [Nota · pontos possíveis] da obra no mês.
@coluna: Trava | inteiro | formato=0 | [Nota · trava] da obra no mês.
*/
VAR _ac = SELECTCOLUMNS ( SUMMARIZE ( fAnaliseCritica, fAnaliseCritica[Obra], fAnaliseCritica[Mes] ),
    "Obra", fAnaliseCritica[Obra] & "", "Mes", fAnaliseCritica[Mes] + 0 )
VAR _base = SELECTCOLUMNS ( SUMMARIZE ( {F_BASE}, {F_BASE}[Obra], {F_BASE}[Mes] ), "Obra", {F_BASE}[Obra] & "", "Mes", {F_BASE}[Mes] + 0 )
VAR _obraMes =
    SELECTCOLUMNS (
        DISTINCT ( UNION ( _ac, _base ) ),
        "Obra", [Obra],
        "Mes", DATE ( YEAR ( [Mes] ), MONTH ( [Mes] ), 1 )
    )
RETURN
    SELECTCOLUMNS (
        _obraMes,
        "Obra", [Obra],
        "Mes", [Mes],
        "TemAC",
            VAR _o = [Obra]
            VAR _m = [Mes]
            RETURN
                IF ( NOT ISEMPTY ( FILTER ( fAnaliseCritica, fAnaliseCritica[Obra] = _o && fAnaliseCritica[Mes] = _m ) ), 1, 0 ),
{(',' + chr(10)).join(_rank_col(c, med) for c, med in _RANK_COLS)}
    )
"""


def ranking_itens_nota() -> str:
    """pbi/dax/_modelo/dItemRankingNota.dax: obra × mês (com aba da Análise Crítica ou da base) × item, com os pontos e
    os possíveis de cada item, pelas medidas da regra de NOTA_ITEM_MEDIDAS."""
    def sw(col: int) -> str:
        casos = "\n".join(f'                        "{c}", [{ms[col]}],' for c, ms in NOTA_ITEM_MEDIDAS.items()).rstrip(",")
        return f"SWITCH (\n                        _i,\n{casos}\n                    )"

    def calc(col: int) -> str:
        return f"""VAR _o = [Obra]
            VAR _m = [Mes]
            VAR _i = [Item]
            RETURN
                CALCULATE (
                    {sw(col)},
                    REMOVEFILTERS ( fAnaliseCritica ),
                    REMOVEFILTERS ( {F_BASE} ),
                    dObra[Obra] = _o,
                    dMes[Mes] = _m
                )"""
    return f"""/*
@tipo: tabela-calculada
@descricao: Pontos e possíveis de cada item da nota por obra × mês (obras com aba da Análise Crítica ou com a base complementar no mês), copiados das medidas da regra de cada item no refresh. As somas por item e por dimensão (Nota · item · …) leem esta tabela. GERADA por pbi/scripts/contas_base.py; a regra fica nas medidas.
@oculta: sim
@coluna: Obra | texto | | Obra.
@coluna: Mes | data | formato=dd/mm/yyyy | Mês.
@coluna: Item | texto | | Código do item (dItemNota).
@coluna: TemAC | inteiro | formato=0 | 1 quando a obra tem aba da Análise Crítica no mês.
@coluna: Pontos | decimal | formato=0.00 | Pontos do item.
@coluna: Possiveis | decimal | formato=0.00 | Máximo do item quando tem dado.
*/
VAR _obraMes =
    SELECTCOLUMNS ( dRankingNota, "Obra", dRankingNota[Obra], "Mes", dRankingNota[Mes], "TemAC", dRankingNota[TemAC] )
VAR _itens = SELECTCOLUMNS ( {{ {", ".join(f'"{c}"' for c in NOTA_ITEM_MEDIDAS)} }}, "Item", [Value] )
RETURN
    SELECTCOLUMNS (
        CROSSJOIN ( _obraMes, _itens ),
        "Obra", [Obra],
        "Mes", [Mes],
        "Item", [Item],
        "TemAC", [TemAC],
        "Pontos",
            {calc(0)},
        "Possiveis",
            {calc(1)}
    )
"""


# ---- leitura rápida pelo ranking (desempenho) ----
# Mesmo valor das medidas originais: com uma obra e um mês no contexto e a obra com dado nesse mês, lê a linha de
# dRankingNota (guardada no refresh a partir das próprias medidas); em qualquer outro contexto, cai na medida original.
_RANK_LEITURA = (("status", "Status", INT), ("pendente", "Pendente", INT), ("pontos perdidos", "Perdidos", PTS),
                 ("nota final", "NotaOrdem", PTS), ("pontos obtidos", "Obtidos", PTS),
                 ("pontos possíveis", "Possiveis", PTS), ("trava", "Trava", INT))
for _x, _col, _fmt in _RANK_LEITURA:
    _orig = f"[Nota · {_x}]"
    _val = (f"MAXX ( _linha, dRankingNota[{_col}] )" if _col != "NotaOrdem"
            else "VAR _n = MAXX ( _linha, dRankingNota[NotaOrdem] ) RETURN IF ( _n <> 99, _n )")
    nota(f"Nota · {_x} · ranking", _fmt,
         f"{_orig} lido de dRankingNota quando há uma obra e um mês no contexto e a obra tem dado no mês; senão, a própria "
         f"{_orig}. Mesmo valor, mais rápido nas listas que iteram obras × meses.",
         f"""VAR _o = SELECTEDVALUE ( dObra[Obra] )
VAR _m = SELECTEDVALUE ( dMes[Mes] )
VAR _linha = FILTER ( dRankingNota, dRankingNota[Obra] = _o && dRankingNota[Mes] = _m )
RETURN
    IF (
        NOT ISBLANK ( _o ) && NOT ISBLANK ( _m ) && NOT ISEMPTY ( _linha ),
        {_val},
        {_orig}
    )""")
    nota(f"Nota · {_x} · um mês", _fmt,
         f"{_orig} de uma obra num mês, lido de dRankingNota (a mesma medida, guardada no refresh). Uma obra e um mês no "
         "contexto; senão, vazio.",
         f"""VAR _o = SELECTEDVALUE ( dObra[Obra] )
VAR _m = SELECTEDVALUE ( dMes[Mes] )
VAR _linha = FILTER ( dRankingNota, dRankingNota[Obra] = _o && dRankingNota[Mes] = _m )
RETURN
    IF ( HASONEVALUE ( dObra[Obra] ) && HASONEVALUE ( dMes[Mes] ), {_val} )""")

# ---- carteira (obras com aba da Análise Crítica no mês) ----
_CARTEIRA = """IF (
    HASONEVALUE ( dMes[Mes] ),
    COUNTROWS (
        FILTER (
            dRankingNota,
            dRankingNota[Mes] = VALUES ( dMes[Mes] )
                && dRankingNota[TemAC] = 1
                && dRankingNota[Obra] IN VALUES ( dObra[Obra] )
                && {cond}
        )
    )
)"""
for _cod, _rot in ((2, "críticas"), (1, "em atenção"), (0, "estáveis")):
    nota(f"Nota · carteira · obras {_rot}", INT,
         f"Obras do recorte com status {_rot.replace('em ', '')} no mês do contexto (só as com nota; a pendente não "
         "entra). Conta as linhas de dRankingNota. Um mês no contexto; com mais de um, vazio.",
         _CARTEIRA.format(cond=f"dRankingNota[Status] == {_cod}"))
nota("Nota · carteira · obras pendentes", INT,
     "Obras do recorte pendentes no mês do contexto (falta algum item; sem nota). Conta as linhas de dRankingNota. Um "
     "mês no contexto; com mais de um, vazio.",
     _CARTEIRA.format(cond="dRankingNota[Pendente] == 1"))
nota("Nota · carteira · obras na trava", INT,
     "Obras do recorte em crítico pela trava (custo ou prazo) no mês do contexto. Um mês no contexto.",
     _CARTEIRA.format(cond="dRankingNota[Trava] == 1"))

# ---- por item e por dimensão (granularidade dItemNota[Item] ou dItemNota[Dimensao]) ----


def switch_item(col: int) -> str:
    casos = "\n".join(f'    "{c}", [{ms[col]}],' for c, ms in NOTA_ITEM_MEDIDAS.items() if ms[col]).rstrip(",")
    return f"""SWITCH (
    SELECTEDVALUE ( dItemNota[Item] ),
{casos}
)"""


_ITENS_DO_CONTEXTO = """FILTER (
        dItemRankingNota,
        dItemRankingNota[Item] IN VALUES ( dItemNota[Item] )
            && dItemRankingNota[Obra] IN VALUES ( dObra[Obra] )
            && dItemRankingNota[Mes] IN VALUES ( dMes[Mes] )
    )"""
for _nome, _col, _desc in (("Nota · item · pontos", "Pontos",
                            "Pontos dos itens do contexto (um item da linha ou os itens de uma dimensão), somados pelas obras do recorte."),
                           ("Nota · item · possíveis", "Possiveis",
                            "Máximo dos itens do contexto nas obras com dado, somado.")):
    nota(_nome, PTS, _desc + " Lidos de dItemRankingNota (as medidas da regra de cada item, guardadas no refresh).",
         f"""VAR _p =
    SUMX (
        {_ITENS_DO_CONTEXTO},
        dItemRankingNota[{_col}]
    )
RETURN
    IF ( NOT ISBLANK ( _p ), ROUND ( _p, {AR} ) )""")
nota("Nota · item · perdidos", PTS, "Possíveis − pontos dos itens do contexto (item da linha ou dimensão).",
     f"""VAR _p = [Nota · item · possíveis]
RETURN
    IF ( NOT ISBLANK ( _p ), ROUND ( _p - [Nota · item · pontos], {AR} ) )""")
for _nome, _col, _fmt, _desc in (
        ("Nota · item · nome", "Rotulo", TXT, "Nome do item da linha (Custo (IDC), Atraso em meses)."),
        ("Nota · item · nome curto", "RotuloCurto", TXT, "Nome curto do item da linha, para listas (Custo, PPC)."),
        ("Nota · item · nome médio", "RotuloMedio", TXT, "Nome médio do item da linha, para tabelas de tooltip."),
        ("Nota · item · nome em frase", "RotuloFrase", TXT, "Nome do item dentro de frase, com artigo (o custo)."),
        ("Nota · item · ordem", "Ordem", INT, "Ordem do item na régua (1 = custo), para desempate nas listas."),
        ("Nota · item · fonte", "Fonte", TXT, "Fonte do item da linha: Análise Crítica ou Base complementar."),
        ("Nota · item · unidade", "Unidade", TXT, "Unidade do X do item da linha: indice, meses, pct, taxa ou checagens."),
        ("Nota · item · faixas", "FaixaTexto", TXT, "Faixas → pontos do item da linha, gerado do dicionário NOTA."),
        ("Nota · item · explica", "Explica", TXT, "O que o item da linha mede, em uma linha."),
        ("Nota · item · dimensão", "Dimensao", TXT, "Dimensão do item (ou a dimensão da linha)."),
        ("Nota · item · ordem da dimensão", "OrdemDimensao", INT, "Ordem da dimensão (1 = Custo).")):
    nota(_nome, _fmt, _desc, f"SELECTEDVALUE ( dItemNota[{_col}] )", oraculo="dItemNota (gerada do dicionário NOTA)")
nota("Nota · item · máximo", PTS, "Máximo dos itens do contexto (item da linha ou dimensão): soma de dItemNota[Maximo].",
     "SUM ( dItemNota[Maximo] )", oraculo="dItemNota (gerada do dicionário NOTA)")
nota("Nota · item · X", "0.0000",
     "X do item da linha: IDC (custo), meses (prazo), fração (PPC, caixa, inspeção, NR-18, entregas), taxa (acidentes) "
     "ou checagens (análise crítica). Uma obra.", switch_item(2))
nota("Nota · item · faixa atingida", TXT, "Faixa em que o item da linha caiu.", switch_item(3))
nota("Nota · item · fora da faixa", INT,
     "1 quando o item da linha tem valor na base, mas fora da faixa válida (fica sem pontos, mas não por falta); 0 nos "
     "demais casos. Uma obra e um item no contexto.",
     f"""VAR _i = SELECTEDVALUE ( dItemNota[Item] )
RETURN
    IF (
        HASONEVALUE ( dItemNota[Item] ) && HASONEVALUE ( dObra[Obra] ),
        SWITCH (
            _i,
{chr(10).join(f'            "{c}", INT ( {expr} && ISBLANK ( [Nota · X {SUF[c]}] ) ),' for c, expr in _FORA.items())}
            0
        )
    )""")
nota("Nota · item · obras que perderam pontos", INT,
     "Obras do recorte (com aba da Análise Crítica) que perderam pontos nos itens do contexto (item ou dimensão). Lido "
     "de dItemRankingNota.",
     f"""VAR _t =
    GROUPBY (
        FILTER ( {_ITENS_DO_CONTEXTO}, dItemRankingNota[TemAC] = 1 ),
        dItemRankingNota[Obra],
        "@perde", SUMX ( CURRENTGROUP (), dItemRankingNota[Possiveis] - dItemRankingNota[Pontos] )
    )
RETURN
    COUNTROWS ( FILTER ( _t, ROUND ( [@perde], {AR} ) > 0 ) )""")

# ---- constantes do dicionário para os textos das telas: nenhum limite escrito à mão na tela ----
_nota_max = sum(nota_maximo(c) for c in NOTA_ITEM_MEDIDAS)
assert abs(_nota_max - 10) < 1e-9, _nota_max
nota("Nota · nota · máximo", "0.0", "Nota máxima: a soma dos máximos dos itens (10). Constante.", _n(_nota_max),
     oraculo="dicionário NOTA (itens)")
_st_nome = {0: "estável", 1: "atenção", 2: "crítico"}
_st_txt, _ant = {}, None
for _op, _lim, _cod in NOTA["status"]:
    if _op == "resto":
        _st_txt[_cod] = f"< {_br(_ant, False)}"
    elif _ant is None:
        _st_txt[_cod] = f"≥ {_br(_lim, False)}"
    else:
        _st_txt[_cod] = f"{_br(_lim, False)} a {_br(round(_ant - 0.01, 2), False)}"
    _ant = _lim if _op != "resto" else _ant
for _cod in (2, 1, 0):
    nota(f"Nota · status · faixa {_st_nome[_cod]}", TXT,
         f"Faixa da nota para o status {_st_nome[_cod]} ({_st_txt[_cod]}), gerada do dicionário NOTA. Constante.",
         f'"{_st_txt[_cod]}"', oraculo="dicionário NOTA (status)")
_st_lim = {_cod: _lim for _op, _lim, _cod in NOTA["status"] if _op != "resto"}
for _cod, _nome in ((1, "Nota · status · nota mínima atenção"), (0, "Nota · status · nota mínima estável")):
    nota(_nome, "0.0#", f"Menor nota com o status {_st_nome[_cod]} ({_br(_st_lim[_cod], False)}), do dicionário NOTA. "
         "Constante.", _n(_st_lim[_cod]), oraculo="dicionário NOTA (status)")
_fc = NOTA["caixa"]
for _i, _nome, _regra in ((0, "Nota · limite caixa · ponto inteiro", "abaixo dele (X <) vale o ponto inteiro"),
                          (1, "Nota · limite caixa · meio ponto", "até ele (X ≤) vale meio ponto; acima, zero")):
    nota(_nome, "0%", f"Limite do desvio do desembolso sobre o previsto, em módulo ({_br(_fc[_i][1], True)}): {_regra}. "
         "Do dicionário NOTA. Constante.", _n(_fc[_i][1]), oraculo="dicionário NOTA (caixa)")
for _nome, _fmt, _val, _desc in (
        ("Nota · limite custo · trava", "0.00", _tv["idc_abaixo"], "IDC abaixo do qual a obra fica crítica (trava)"),
        ("Nota · limite custo · ponto cheio", "0.00", NOTA["idc"][0][1], "IDC a partir do qual o custo vale o máximo"),
        ("Nota · limite prazo · trava", "0", _tv["atraso_acima"], "Atraso (meses) acima do qual a obra fica crítica (trava)"),
        ("Nota · limite prazo · ponto cheio", "0.0", NOTA["atraso"][0][1], "Atraso (meses) até o qual o prazo vale o máximo"),
        ("Nota · limite PPC · ponto cheio", "0%", NOTA["ppc"][0][1], "PPC a partir do qual o item vale o máximo"),
        ("Nota · limite inspeção · ponto cheio", "0%", NOTA["inspecao"][0][1], "Aprovação na 1.ª inspeção que vale o máximo"),
        ("Nota · limite NR-18 · ponto cheio", "0%", NOTA["nr18"][0][1], "Conformidade NR-18 que vale o máximo"),
        ("Nota · limite entregas · ponto cheio", "0%", NOTA["entregas"][0][1], "Entregas no prazo que valem o máximo"),
        ("Nota · limite acidentes · setor", "0.0", NOTA["acidentes"][1][1],
         "Taxa de frequência até a qual o item vale metade (≈ média do setor)"),
        ("Nota · janela de acidentes (meses)", "0", NOTA["janela_acidentes"], "Meses da janela da taxa de frequência")):
    nota(_nome, _fmt, f"{_desc}. Do dicionário NOTA. Constante.", _n(_val), oraculo="dicionário NOTA")
# só leem dItemNota ou o dicionário (não dependem de mês nem de obra): sem as variantes · ref e · foco
NOTA_SEM_VARIANTE = {n for (_s, n, *_r) in MEDIDAS if n.startswith(("Nota · limite", "Nota · status · faixa",
                                                                      "Nota · status · nota mínima", "Nota · janela"))} | {
    f"Nota · {x} · um mês" for x, _c, _f in _RANK_LEITURA} | {
    "Nota · nota · máximo", "Nota · item · nome", "Nota · item · nome curto", "Nota · item · nome médio",
    "Nota · item · nome em frase", "Nota · item · ordem", "Nota · item · fonte", "Nota · item · faixas",
    "Nota · item · unidade", "Nota · item · explica", "Nota · item · dimensão", "Nota · item · ordem da dimensão",
    "Nota · item · máximo"}


# ---------------------------------------------------------------------------------------------------------------------
# 4. As mesmas contas no mês de referência (cartões, rankings, listas por obra)
# ---------------------------------------------------------------------------------------------------------------------
REF = [n for (_s, n, *_r) in MEDIDAS if not n.startswith(("Mês", "Série")) and n not in NOTA_SEM_VARIANTE]
FORMATOS = {n: f for (_s, n, _p, f, _d, _x) in MEDIDAS}
# integração da Fase 2 (desempenho): as leituras · ranking no mês de referência leem dRankingNota direto, sem a medida
# original de reserva. Com o mês fixo, a linha de dRankingNota é o valor da medida para cada obra com dado no mês (sem
# dado, as duas dão vazio): status, pendente e nota exigem uma obra (com várias, vazio, como a medida); pontos obtidos,
# possíveis e perdidos somam as obras do recorte, como as medidas (SUMX por obra).
_RANKING_REF_UMA = {"Nota · status · ranking": "Status", "Nota · pendente · ranking": "Pendente",
                    "Nota · nota final · ranking": "NotaOrdem", "Nota · trava · ranking": "Trava"}
_RANKING_REF_SOMA = {"Nota · pontos obtidos · ranking": "Obtidos", "Nota · pontos possíveis · ranking": "Possiveis",
                     "Nota · pontos perdidos · ranking": "Perdidos"}
for nome in REF:
    if nome in _RANKING_REF_UMA:
        _c = _RANKING_REF_UMA[nome]
        _v = (f"MAXX ( _linha, dRankingNota[{_c}] )" if _c != "NotaOrdem"
              else "VAR _n = MAXX ( _linha, dRankingNota[NotaOrdem] ) RETURN IF ( _n <> 99, _n )")
        expr = f"""VAR _mes = [Mês de referência]
VAR _o = SELECTEDVALUE ( dObra[Obra] )
VAR _linha = FILTER ( dRankingNota, dRankingNota[Obra] = _o && dRankingNota[Mes] = _mes )
RETURN
    IF ( HASONEVALUE ( dObra[Obra] ), {_v} )"""
    elif nome in _RANKING_REF_SOMA:
        expr = f"""VAR _mes = [Mês de referência]
VAR _p =
    SUMX (
        FILTER ( dRankingNota, dRankingNota[Mes] = _mes && dRankingNota[Obra] IN VALUES ( dObra[Obra] ) ),
        dRankingNota[{_RANKING_REF_SOMA[nome]}]
    )
RETURN
    IF ( NOT ISBLANK ( _p ), ROUND ( _p, 8 ) )"""
    else:
        expr = f"""VAR _mes = [Mês de referência]
RETURN
    CALCULATE ( [{nome}], REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )"""
    m("referencia", f"{nome} · ref", r"Base\Referência", FORMATOS[nome],
      (f"[{nome.removesuffix(' · ranking')}] no mês de referência (seletor do drawer; sem escolha, o último mês), lida "
       "da linha de dRankingNota (a mesma medida, guardada no refresh), sem recalcular os itens."
       if nome in _RANKING_REF_UMA or nome in _RANKING_REF_SOMA
       else f"[{nome}] no mês de referência (seletor do drawer; sem escolha, o último mês)."), expr)


# ---------------------------------------------------------------------------------------------------------------------
# 5. Obra em foco (telas Análise crítica e Avanço físico)
# ---------------------------------------------------------------------------------------------------------------------
FOCO = r"Base\Obra em foco"
m("foco", "Obra em foco · selo", FOCO, TXT, "REAL ou ILUSTR. da obra em foco (critério da nota).",
  """VAR _obra = [Nota · obra em foco]
RETURN
    LOOKUPVALUE ( dObra[Selo], dObra[Obra], _obra )""")
m("foco", "Nota · obra em foco", FOCO, TXT,
  "Obra escolhida no seletor de obra (dObraFoco); na linha automática (ou sem escolha), a que mais perde pontos na nota "
  "no mês de referência entre as obras do recorte (empate: menor nota, com a pendente depois das que têm nota; depois "
  "o nome). Lê o ranking guardado em dRankingNota (as mesmas medidas, calculadas no refresh): uma conta só por chamada.",
  """VAR _auto = SELECTEDVALUE ( dObraFoco[Automatico], TRUE () )
VAR _escolha = IF ( _auto, BLANK (), SELECTEDVALUE ( dObraFoco[ObraFoco] ) )
VAR _mes = [Mês de referência]
VAR _recorte = VALUES ( dObra[Obra] )
VAR _obras = FILTER ( dRankingNota, dRankingNota[Mes] = _mes && dRankingNota[TemAC] = 1 && dRankingNota[Obra] IN _recorte )
VAR _maisPerde =
    MAXX (
        TOPN ( 1, _obras, dRankingNota[Perdidos], DESC, dRankingNota[NotaOrdem], ASC, dRankingNota[Obra], ASC ),
        dRankingNota[Obra]
    )
RETURN
    COALESCE ( _escolha, _maisPerde )""", "pipeline/conferir_ficticios.py · prévia da nota (obra em foco)")
FOCO_REF = [n for (_s, n, *_r) in MEDIDAS if n.endswith(" · ref")]
for nome in FOCO_REF:
    base_ = nome[: -len(" · ref")]
    if base_.startswith(("Carteira ·", "Obras com análise", "Nota · carteira", "Nota · item · obras")):
        continue
    # integração da Fase 2: todas as variantes · foco leem a obra em foco da nota (o alias Obra em foco saiu)
    m("foco", f"{base_} · foco", FOCO, FORMATOS[base_],
      f"[{base_.removesuffix(' · ranking')}] da obra em foco (a que mais perde pontos na nota, ou a escolhida), no mês "
      "de referência" + (" (lida de dRankingNota, por [" + nome + "])." if base_.endswith(" · ranking") else "."),
      f"""VAR _obra = [Nota · obra em foco]
RETURN
    CALCULATE ( [{nome}], dObra[Obra] = _obra )""")
# ---------------------------------------------------------------------------------------------------------------------
# 6. Identidade da obra e recorte (textos lidos do modelo, para linhas, cabeçalho e selo de origem)
# ---------------------------------------------------------------------------------------------------------------------
IDT = r"Base\Obra"
m("identidade", "Obra · nome", IDT, TXT, "Nome da obra do contexto (uma obra).",
  "SELECTEDVALUE ( dObra[Obra] )")
m("identidade", "Obra · código", IDT, TXT, "Código do empreendimento no Fluxo de Caixa (uma obra).",
  "SELECTEDVALUE ( dObra[Codigo] )")
m("identidade", "Obra · selo", IDT, TXT, "REAL ou ILUSTR. (uma obra).", "SELECTEDVALUE ( dObra[Selo] )")
m("identidade", "Obra · início", IDT, "mmm/yy", "Início da obra (cadastro).", "SELECTEDVALUE ( dObra[Inicio] )")
m("identidade", "Obra · término previsto", IDT, "mmm/yy", "Término previsto da obra (cadastro).",
  "SELECTEDVALUE ( dObra[TerminoPrevisto] )")
m("identidade", "Aba · ref", IDT, TXT, "Nome da aba da planilha no mês de referência (JUN26).",
  f"""VAR _mes = [Mês de referência]
RETURN
    CALCULATE ( SELECTEDVALUE ( {F}[Aba] ), REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )""")
m("identidade", "Tipo de orçamento · ref", IDT, TXT,
  "Tipo do orçamento na aba do mês de referência, curto e minúsculo (preliminar, legal, executivo).",
  f"""VAR _mes = [Mês de referência]
VAR _tipo =
    CALCULATE ( SELECTEDVALUE ( {F}[TipoOrcamento] ), REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )
RETURN
    LOWER ( TRIM ( SUBSTITUTE ( SUBSTITUTE ( _tipo, "Orçamento", "" ), "orçamento", "" ) ) )""")
REC = r"Base\Recorte"
m("identidade", "Recorte · obras no recorte", REC, INT,
  "Obras com aba no mês de referência dentro do recorte (seletor de obras do drawer).",
  "[Obras com análise · ref]")
m("identidade", "Recorte · obras no total", REC, INT,
  "Obras com aba no mês de referência, sem o seletor de obras.",
  """CALCULATE ( [Obras com análise · ref], REMOVEFILTERS ( dObra ) )""")
m("identidade", "Recorte · obras (lista)", REC, TXT,
  "Nomes das obras do recorte no mês de referência, em ordem alfabética, separados por vírgula.",
  f"""VAR _mes = [Mês de referência]
RETURN
    CALCULATE (
        CONCATENATEX ( VALUES ( {F}[Obra] ), {F}[Obra], ", ", {F}[Obra], ASC ),
        REMOVEFILTERS ( dMes ),
        dMes[Mes] = _mes
    )""")
m("identidade", "Recorte · mês escolhido", REC, INT,
  "1 quando o seletor de mês do drawer tem um mês escolhido; 0 quando vale o último mês (linha automática).",
  """VAR _auto = SELECTEDVALUE ( dMesRef[Automatico], TRUE () )
RETURN
    IF ( ISFILTERED ( dMesRef ) && NOT _auto, 1, 0 )""")
m("identidade", "Recorte · obras escolhidas", REC, INT,
  "1 quando o seletor de obras do drawer recorta a carteira; 0 com todas as obras.",
  "IF ( ISFILTERED ( dObra ), 1, 0 )")
m("identidade", "Recorte · obra em foco escolhida", REC, INT,
  "1 quando a obra em foco foi escolhida no drawer; 0 quando vale a mais crítica do mês (linha automática).",
  """VAR _auto = SELECTEDVALUE ( dObraFoco[Automatico], TRUE () )
RETURN
    IF ( ISFILTERED ( dObraFoco ) && NOT _auto, 1, 0 )""")
m("identidade", "Recorte · janela escolhida", REC, INT,
  "1 quando a janela das séries escolhida no drawer (dJanela) não é a padrão de 12 meses; 0 com 12 meses ou sem "
  "escolha. O contador de filtros do funil soma esta conta.",
  """VAR _janela = [Série · janela (meses)]
RETURN
    IF ( _janela <> 12, 1, 0 )""")
m("identidade", "Recorte · primeiro mês · curto", REC, TXT, "Primeiro mês do histórico (jan/26).",
  "CALCULATE ( SELECTEDVALUE ( dMes[MesAno] ), REMOVEFILTERS ( dMes ), dMes[Ordem] = 1 )")
for fonte, rot in (("Ilustrativo", "ilustrativas"), ("Real", "reais")):
    m("identidade", f"Recorte · obras {rot} (lista)", REC, TXT,
      f"Obras {rot} (dObra[Fonte] = {fonte}) do recorte, em ordem alfabética, para o selo de origem do rodapé.",
      f"""VAR _mes = [Mês de referência]
RETURN
    CALCULATE (
        CONCATENATEX ( VALUES ( dObra[Obra] ), dObra[Obra], ", ", dObra[Obra], ASC ),
        REMOVEFILTERS ( dMes ),
        dMes[Mes] = _mes,
        dObra[Fonte] = "{fonte}",
        {F}
    )""")
# Nota: a ordem é a dos pontos perdidos (empate: menor nota, pendente depois; depois o nome)
# (ranking guardado em dRankingNota no refresh, das mesmas medidas: ver RANKING_NOTA)
_NOTA_ORDEM = """VAR _mes = [Mês de referência]
VAR _recorte = VALUES ( dObra[Obra] )
VAR _obras = FILTER ( dRankingNota, dRankingNota[Mes] = _mes && dRankingNota[TemAC] = 1 && dRankingNota[Obra] IN _recorte )
RETURN
    CONCATENATEX (
        {filtro},
        dRankingNota[Obra], "|",
        dRankingNota[Perdidos], DESC, dRankingNota[NotaOrdem], ASC, dRankingNota[Obra], ASC
    )"""
for codigo, rot in ((2, "críticas"), (1, "em atenção"), (0, "estáveis")):
    m("identidade", f"Nota · recorte · obras {rot} (lista)", REC, TXT,
      f"Obras {rot} na nota no mês de referência, da que mais perde pontos para a que menos perde, separadas por '|'.",
      _NOTA_ORDEM.format(F=F, OBRAS_AC=OBRAS_AC, filtro=f"FILTER ( _obras, dRankingNota[Status] == {codigo} )"), "pipeline/conferir_ficticios.py · prévia da nota")
m("identidade", "Nota · recorte · obras pendentes (lista)", REC, TXT,
  "Obras pendentes na nota (falta algum item) no mês de referência, da que mais perde pontos nos itens com dado para a "
  "que menos perde, separadas por '|'.",
  _NOTA_ORDEM.format(F=F, OBRAS_AC=OBRAS_AC, filtro="FILTER ( _obras, dRankingNota[Pendente] == 1 )"), "pipeline/conferir_ficticios.py · prévia da nota")
m("identidade", "Nota · recorte · obras por pontos perdidos (lista)", REC, TXT,
  "Obras com aba no mês de referência, da que mais perde pontos na nota para a que menos perde (empate: menor nota, "
  "pendente depois; depois o nome), separadas por '|'.",
  _NOTA_ORDEM.format(F=F, OBRAS_AC=OBRAS_AC, filtro="_obras"), "pipeline/conferir_ficticios.py · prévia da nota")

for nome in ("Resultado da obra", "Resultado sem ativos", "Resultado %", "Físico · previsto acumulado",
             "Físico · executado acumulado", "Físico · previsto no mês", "Físico · executado no mês",
             "Estoque de materiais", "Adiantamentos", "Crédito do orçamento", "Desembolsado acumulado",
             "Contas a pagar", "Desembolso · previsto no mês", "Desembolso · realizado no mês",
             "Canteiro · PPC", "Prazo · atraso (meses)"):     # PPC mês a mês e tooltip da T3
    m("foco", f"{nome} · foco no mês", FOCO, FORMATOS[nome],
      f"[{nome}] da obra em foco (a que mais perde pontos na nota, ou a escolhida) no mês do eixo (séries da obra em foco).",
      f"""VAR _obra = [Nota · obra em foco]
RETURN
    CALCULATE ( [{nome}], dObra[Obra] = _obra )""")


for nome in ("Nota · pontos possíveis", "Nota · pontos obtidos", "Nota · pontos perdidos", "Nota · itens faltando",
             "Nota · nota final", "Nota · status", "Nota · pendente", "Nota · trava",
             "Nota · item · pontos", "Nota · item · possíveis",    # item × mês da obra em foco (pedido da T2)
             "Nota · pontos PPC", "Nota · possíveis · PPC", "Nota · pontos prazo", "Nota · possíveis · prazo"):  # T3
    m("foco", f"{nome} · foco no mês", FOCO, FORMATOS[nome],
      f"[{nome}] da obra em foco da nota no mês do eixo (séries da obra em foco).",
      f"""VAR _obra = [Nota · obra em foco]
RETURN
    CALCULATE ( [{nome}], dObra[Obra] = _obra )""")


# ---------------------------------------------------------------------------------------------------------------------
# Variantes · ref / · foco que nenhum visual lê: as telas leem as leituras · ranking · ref / · ranking · foco e · um
# mês; as originais no mês de referência e na obra em foco ficariam sem leitor. Para reativar, tire o nome do conjunto.
NOTA_SEM_USO = {f"Nota · {x} · {v}" for x in ("status", "pendente", "nota final", "pontos obtidos", "pontos possíveis",
                                               "trava") for v in ("ref", "foco")} | {
    "Nota · pontos perdidos · foco", "Nota · nota final · ranking", "Nota · pontos obtidos · ranking",
    "Nota · pontos possíveis · ranking", "Nota · pontos perdidos · ranking", "Nota · trava · ranking"}
SEM_LEITOR_FASE2 = {"Orçamento · mês anterior · ref"}
RETIRADAS |= NOTA_SEM_USO | SEM_LEITOR_FASE2


# ---------------------------------------------------------------------------------------------------------------------
# Gravação
# ---------------------------------------------------------------------------------------------------------------------
PROIBIDOS = set('/\\:*?"<>|')


def nome_arquivo(nome: str) -> str:
    return "".join("_" if c in PROIBIDOS else c for c in nome) + ".dax"


def main() -> int:
    nomes = [n for (_s, n, *_r) in MEDIDAS]
    repetidos = {n for n in nomes if nomes.count(n) > 1}
    if repetidos:
        print("[ERRO] nomes repetidos:", sorted(repetidos))
        return 2
    escritos = set()
    for sub, nome, pasta, formato, descricao, dax in MEDIDAS:
        if nome in RETIRADAS:
            continue
        arq = DESTINO / sub / nome_arquivo(nome)
        arq.parent.mkdir(parents=True, exist_ok=True)
        cab = [f"@pasta: {pasta}", f"@formato: {formato}", f"@descricao: {descricao}"]
        if nome_arquivo(nome)[:-4] != nome:
            cab.append(f"@nome: {nome}")
        cab.append("@gerado: pbi/scripts/contas_base.py")
        texto = "/*\n" + "\n".join(cab) + "\n*/\n" + dax + "\n"
        if not arq.is_file() or arq.read_text(encoding="utf-8") != texto:
            arq.write_text(texto, encoding="utf-8", newline="\n")
        escritos.add(arq.resolve())
    # tabela dos itens da nota e regras de leitura das bases, do mesmo dicionário (fonte única)
    for nome_m, texto_m in (("dItemNota.m", m_ditem_nota()), ("fxRegrasBase.m", m_regras_base())):
        m_ado = RAIZ / "m" / nome_m
        if not m_ado.is_file() or m_ado.read_text(encoding="utf-8") != texto_m:
            m_ado.write_text(texto_m, encoding="utf-8", newline="\n")
    # rankings da nota calculados no refresh (desempenho; a regra fica nas medidas)
    for nome_t, texto_t in (("dRankingNota.dax", RANKING_NOTA), ("dItemRankingNota.dax", ranking_itens_nota())):
        rk = RAIZ / "dax" / "_modelo" / nome_t
        rk.parent.mkdir(parents=True, exist_ok=True)
        if not rk.is_file() or rk.read_text(encoding="utf-8") != texto_t:
            rk.write_text(texto_t, encoding="utf-8", newline="\n")
    sobras = [p for p in DESTINO.rglob("*.dax") if p.resolve() not in escritos]
    for p in sobras:
        p.unlink()
    print(f"{len(MEDIDAS)} medidas em {DESTINO.relative_to(RAIZ.parent)} · {len(sobras)} removidas")
    return 0


if __name__ == "__main__":
    sys.exit(main())

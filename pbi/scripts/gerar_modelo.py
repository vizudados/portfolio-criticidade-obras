#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gerar_modelo — gera o SemanticModel (TMDL) do painel Criticidade de Obras e análise crítica a partir de pbi/m/*.m,
pbi/dax/_modelo/*.dax (tabelas calculadas) e pbi/dax/**/*.dax (medidas, via dax_para_tmdl da skill dax-conta-desenho).

Copiado de outro projeto (a origem fica intocada) e estendido com funções e consultas
auxiliares não carregadas (@tipo funcao | consulta → expressions.tmdl). Escreve só em pbi/pbip/CO.SemanticModel/ e
pbi/_backups/ (zip datado antes de gravar).

    python -X utf8 pbi/scripts/gerar_modelo.py               # simulação: plano + lint (texto e TOM); nada gravado
    python -X utf8 pbi/scripts/gerar_modelo.py --aplicar     # backup datado + grava (idempotente)
    python -X utf8 pbi/scripts/gerar_modelo.py --conferir    # disco × plano
    python -X utf8 pbi/scripts/gerar_modelo.py --aplicar --perfil local   # neste computador (desenvolvimento)

Perfis: o padrão (construtora, sem a opção) é o PBIP de entrega, com os dados embutidos (pbi/m/fxDadosEmbutidos.m,
gerada de dados/ por pipeline/embutir_dados.py) e nenhuma fonte externa no M: o --aplicar recusa a gravação se o
expressions.tmdl citar Folder.Files, SharePoint, Expression.Evaluate ou #shared. A opção --perfil local troca, na
geração, as funções de origem pelas de pbi/m/_local (pOrigem = Pasta, SharePoint ou Embutido; pPastaDados,
pSiteSharePoint e pPastaSharePoint) e os valores que estiverem em pbi/scripts/perfil_local.json: o PBIP sai com os
caminhos deste computador e não é a entrega. Os demais parâmetros não mudam nunca.

Fontes:
  pbi/m/<nome>.m          cabeçalho /* @tipo (parametro|funcao|consulta|tabela) @descricao [@categoria] [@oculta] @coluna … */ + M
                          @coluna: Nome | tipo | propriedades (chave; oculta; ordenar=Col; formato=…) | descrição
  pbi/dax/_modelo/*.dax   /* @tipo: tabela-calculada @descricao @coluna … */ + DAX da tabela
  pbi/dax/**/*.dax        medidas (fora de _modelo), cabeçalho /* @pasta @formato @descricao [@oraculo] [@oculta] */

Rode com o Power BI Desktop FECHADO neste projeto: com ele aberto, o próximo salvamento sobrescreve o TMDL gerado.
Códigos de saída: 0 ok · 1 conferência com diferença · 2 bloqueio (nada gravado) · 3 Desktop aberto neste projeto.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import uuid
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

sys.dont_write_bytecode = True
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import dax_para_tmdl as dpt  # noqa: E402

RAIZ = AQUI.parent                                          # pbi/
NOME = "Criticidade de Obras - Analise Critica"                     # displayName (.platform) e nome do .pbip
PBIP_DIR = RAIZ / "pbip"
PASTA_MODELO_NOME = "CO.SemanticModel"                     # pastas curtas (L045)
PASTA_REPORT_NOME = "CO.Report"
PASTA_MODELO = PBIP_DIR / PASTA_MODELO_NOME
M_DIR = RAIZ / "m"
DAX_DIR = RAIZ / "dax"
BACKUPS = RAIZ / "_backups"
QA = RAIZ / "qa" / "modelo"
LINT_PS1 = AQUI / "lint_tmdl.ps1"
NS_MEDIDAS = "criticidade-obras"                             # namespace dos lineageTag das medidas (dax_para_tmdl)
NL = "\r\n"                                                 # o Desktop grava TMDL em CRLF, sem BOM

_NS = uuid.uuid5(uuid.NAMESPACE_URL, "https://vizudados.com.br/construtora/obras-analise-critica")


def id_estavel(chave: str) -> str:
    return str(uuid.uuid5(_NS, "modelo:" + chave))


class ErroGerador(Exception):
    pass


# =====================================================================================================================
# 1. Plano do modelo
# =====================================================================================================================
# Só as origens (quatro pastas e o cadastro) variam por computador: ver aplicar_perfil() e perfil_local.json.
PARAMETROS = ["pOrigem", "pPastaPlanilhas", "pCadastroObras", "pInicioHistorico", "pPastaBases", "pPastaCrono",
              "pPrefixoCrono"]
# Perfil local (só neste computador; nunca vai para o serviço nem para o portfólio): as origens "Pasta" e "SharePoint"
# entram pelos arquivos de pbi/m/_local, que trocam os de mesmo nome e acrescentam os parâmetros de pasta e de site. No
# perfil padrão (a entrega) o M só tem a origem embutida: o serviço recusa o modelo inteiro quando acha fonte dinâmica
# (Expression.Evaluate) e pede credencial ou gateway de toda fonte citada, mesmo num ramo de "if" que não roda.
PARAMETROS_LOCAIS = ["pPastaDados", "pSiteSharePoint", "pPastaSharePoint"]
TROCAS_LOCAIS = ["pOrigem", "fxArquivosOrigem", "fxCaminhoOrigem"]
PROIBIDO_NA_ENTREGA = ("Folder.Files", "SharePoint", "Expression.Evaluate", "#shared")
PERFIL = "construtora"


def parametros() -> list[str]:
    """Os parâmetros do perfil em uso (o local acrescenta os de pasta e de site)."""
    return PARAMETROS + (PARAMETROS_LOCAIS if PERFIL == "local" else [])
EXPRESSOES = ["fxNormaliza", "fxMesDaAba", "fxCaminhoOrigem", "fxDadosEmbutidos", "fxArquivosOrigem", "fxConteudoOrigem", "fxLerAba",
              "fxArquivosPlanilhas", "stgCadastro", "stgAbas",
              "fxRegrasBase", "fxArquivosBases", "stgAbasBase", "fxArquivosCrono", "stgCrono", "fConferencia"]   # funções e consultas auxiliares (não carregadas; fConferencia é o relatório de conferência)
# régua: Nota da obra (28/10/2026); o eixo dos itens é dItemNota (fCurvaPrevista: curva do atraso, sem relação)
TABELAS_M = ["fAnaliseCritica", "fItens", "fBaseObra", "fCurvaPrevista", "dObra", "dMes", "dMesRef", "dItem", "dItemNota",
             "dObraFoco", "dDegrau", "dJanela"]
RELACOES = [  # (de tabela, de coluna, para tabela, para coluna) — many → one, filtro de direção única
    ("fAnaliseCritica", "Obra", "dObra", "Obra"),
    ("fAnaliseCritica", "Mes", "dMes", "Mes"),
    ("fItens", "Obra", "dObra", "Obra"),
    ("fItens", "Mes", "dMes", "Mes"),
    ("fItens", "Item", "dItem", "Item"),
    ("fBaseObra", "Obra", "dObra", "Obra"),     # bases complementares: as mesmas relações de fAnaliseCritica
    ("fBaseObra", "Mes", "dMes", "Mes"),
    # dRankingNota e dItemRankingNota (tabelas calculadas do ranking da nota) ficam SEM relação: ela é calculada por medidas que filtram dObra e
    # dMes, e uma relação com eles dá dependência circular no refresh. As medidas filtram a tabela por IN / igualdade.
]
TIPOS = {"texto": "string", "inteiro": "int64", "decimal": "double", "data": "dateTime", "datahora": "dateTime",
         "logico": "boolean"}


@dataclass
class Coluna:
    nome: str
    tipo: str
    descricao: str
    oculta: bool = False
    chave: bool = False
    ordenar_por: str | None = None
    formato: str | None = None


@dataclass
class Fonte:
    nome: str
    arquivo: Path
    tipo: str
    descricao: str
    corpo: str
    colunas: list[Coluna] = field(default_factory=list)
    oculta: bool = False
    categoria: str | None = None
    precedencia: int = 0
    item: str | None = None


def ler_fonte(caminho: Path) -> Fonte:
    rel = caminho.relative_to(RAIZ).as_posix()
    texto = caminho.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    if not texto.lstrip().startswith("/*") or "*/" not in texto:
        raise ErroGerador(f"{rel}: o arquivo tem de começar com o cabeçalho /* @… */")
    ini = texto.index("/*")
    fim = texto.index("*/", ini)
    vals: dict[str, str] = {}
    colunas: list[Coluna] = []
    for l in texto[ini + 2:fim].split("\n"):
        if not l.strip():
            continue
        m = re.match(r"^\s*@(\w+)\s*:\s*(.*)$", l)
        if not m:
            raise ErroGerador(f"{rel}: linha de cabeçalho fora do formato '@chave: valor': {l.strip()!r}")
        chave, valor = m.group(1).lower(), m.group(2).strip()
        if chave == "coluna":
            partes = [p.strip() for p in valor.split("|")]
            if len(partes) < 4:
                raise ErroGerador(f"{rel}: @coluna precisa de 'Nome | tipo | propriedades | descrição': {valor!r}")
            nome, tipo, props, desc_ = partes[0], partes[1], partes[2], " | ".join(partes[3:])
            if tipo not in TIPOS:
                raise ErroGerador(f"{rel}: tipo desconhecido '{tipo}' em {nome}")
            c = Coluna(nome, tipo, desc_)
            for p in [x.strip() for x in props.split(";") if x.strip()]:
                if p == "oculta":
                    c.oculta = True
                elif p == "chave":
                    c.chave = True
                elif p.startswith("ordenar="):
                    c.ordenar_por = p.split("=", 1)[1].strip()
                elif p.startswith("formato="):
                    c.formato = p.split("=", 1)[1].strip()
                else:
                    raise ErroGerador(f"{rel}: propriedade de coluna desconhecida '{p}' em {nome}")
            colunas.append(c)
        else:
            if chave in vals:
                raise ErroGerador(f"{rel}: @{chave} repetida")
            vals[chave] = valor
    tipo = vals.get("tipo")
    if tipo not in ("parametro", "funcao", "consulta", "tabela", "tabela-calculada", "grupo-calculo"):
        raise ErroGerador(f"{rel}: @tipo inválido ({tipo!r})")
    if not vals.get("descricao"):
        raise ErroGerador(f"{rel}: falta @descricao")
    if tipo == "grupo-calculo":
        if not vals.get("item") or not vals.get("precedencia", "").isdigit():
            raise ErroGerador(f"{rel}: grupo de cálculo pede @item e @precedencia (inteiro)")
    elif tipo not in ("parametro", "funcao", "consulta") and not colunas:
        raise ErroGerador(f"{rel}: tabela sem @coluna")
    corpo = texto[fim + 2:].strip("\n")
    if not corpo.strip():
        raise ErroGerador(f"{rel}: corpo vazio depois do cabeçalho")
    if "\t" in corpo:
        raise ErroGerador(f"{rel}: tab no corpo — use espaços (o TMDL usa tab como estrutura)")
    return Fonte(caminho.stem, caminho, tipo, vals["descricao"], corpo, colunas,
                 vals.get("oculta", "não").lower() in ("sim", "true", "1"), vals.get("categoria"),
                 int(vals.get("precedencia") or 0), vals.get("item"))


PERFIL_LOCAL = AQUI / "perfil_local.json"     # caminhos deste computador (desenvolvimento); só afeta a geração
PARAMETROS_DE_PASTA = ["pPastaDados"]                 # a raiz dos dados; as subpastas são relativas a ela
PARAMETROS_DE_ORIGEM = ["pOrigem", "pSiteSharePoint", "pPastaSharePoint"]   # opcionais no perfil local


def aplicar_perfil(params: dict[str, Fonte], perfil: str) -> list[str]:
    """Perfil "construtora" (o padrão, o da entrega): pbi/m como está. Perfil "local": troca o valor de pPastaDados (a
    raiz dos dados neste computador) e, se estiverem em perfil_local.json, os de origem (pOrigem, pSiteSharePoint,
    pPastaSharePoint). Devolve os nomes trocados."""
    if perfil == "construtora":
        return []
    dados = json.loads(PERFIL_LOCAL.read_text(encoding="utf-8"))["parametros"]
    trocados = []
    for nome in PARAMETROS_DE_PASTA + [n for n in PARAMETROS_DE_ORIGEM if n in dados]:
        if nome not in dados:
            raise ErroGerador(f"{PERFIL_LOCAL.name}: falta o caminho de {nome}")
        f = params[nome]
        novo = '"' + dados[nome].replace('"', '""') + '"'
        corpo, n = re.subn(r'\A"(?:[^"]|"")*"', lambda m: novo, f.corpo, count=1)
        if n != 1:
            raise ErroGerador(f"{f.arquivo.name}: o valor do parâmetro não começa com um texto entre aspas")
        f.corpo = corpo
        trocados.append(nome)
    return trocados


def ler_fontes() -> tuple[dict[str, Fonte], dict[str, Fonte], list[Fonte]]:
    params, tabelas = {}, {}
    local = PERFIL == "local"
    for nome in parametros() + EXPRESSOES + TABELAS_M:
        arq = (M_DIR / "_local" if local and nome in PARAMETROS_LOCAIS + TROCAS_LOCAIS else M_DIR) / f"{nome}.m"
        if not arq.is_file():
            raise ErroGerador(f"falta {arq.relative_to(RAIZ)}")
        f = ler_fonte(arq)
        esperado = ("parametro",) if nome in parametros() else ("funcao", "consulta") if nome in EXPRESSOES else ("tabela",)
        if f.tipo not in esperado:
            raise ErroGerador(f"{arq.relative_to(RAIZ)}: @tipo {f.tipo} (esperado {' ou '.join(esperado)})")
        (tabelas if f.tipo == "tabela" else params)[nome] = f
    sobras = sorted(p.name for p in M_DIR.glob("*.m") if p.stem not in PARAMETROS + EXPRESSOES + TABELAS_M)
    if sobras:
        raise ErroGerador(f"m/ tem consultas fora do plano do gerador: {', '.join(sobras)}")
    calcs = []
    pasta_calc = DAX_DIR / "_modelo"
    for arq in sorted(pasta_calc.glob("*.dax")) if pasta_calc.is_dir() else []:
        f = ler_fonte(arq)
        if f.tipo not in ("tabela-calculada", "grupo-calculo"):
            raise ErroGerador(f"{arq.relative_to(RAIZ)}: @tipo {f.tipo} (esperado tabela-calculada ou grupo-calculo)")
        calcs.append(f)
    return params, tabelas, calcs


# =====================================================================================================================
# 2. Escrita TMDL
# =====================================================================================================================
_RE_SIMPLES = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def citar(nome: str) -> str:
    return nome if _RE_SIMPLES.match(nome) else "'" + nome.replace("'", "''") + "'"


def desc(texto: str, tabs: int) -> list[str]:
    t = re.sub(r"\s+", " ", texto or "").strip()
    return [("\t" * tabs) + "/// " + t] if t else []


def expressao(texto: str, tabs: int) -> list[str]:
    linhas = texto.replace("\r\n", "\n").split("\n")
    while linhas and not linhas[-1].strip():
        linhas.pop()
    while linhas and not linhas[0].strip():
        linhas.pop(0)
    return [(("\t" * tabs) + l.rstrip()) if l.strip() else "" for l in linhas]


def bloco_coluna(tab: str, c: Coluna, calculada: bool = False) -> list[str]:
    linhas = desc(c.descricao, 1)
    linhas.append("\tcolumn " + citar(c.nome))
    linhas.append("\t\tdataType: " + TIPOS[c.tipo])
    if c.oculta:
        linhas.append("\t\tisHidden")
    if c.chave:
        linhas.append("\t\tisKey")
    if c.formato:
        linhas.append("\t\tformatString: " + c.formato)
    linhas.append("\t\tlineageTag: " + id_estavel(f"coluna:{tab}.{c.nome}"))
    linhas.append("\t\tsummarizeBy: none")
    if calculada:
        linhas.append("\t\tisNameInferred")
        linhas.append("\t\tsourceColumn: [" + c.nome + "]")
    else:
        linhas.append("\t\tsourceColumn: " + c.nome)
    if c.ordenar_por:
        linhas.append("\t\tsortByColumn: " + citar(c.ordenar_por))
    linhas += ["", "\t\tannotation SummarizationSetBy = Automatic"]
    if c.tipo == "data":
        linhas += ["", "\t\tannotation UnderlyingDateTimeDataType = Date"]
    linhas.append("")
    return linhas


def tmdl_tabela_m(f: Fonte) -> str:
    linhas = desc(f.descricao, 0) + ["table " + citar(f.nome), "\tlineageTag: " + id_estavel("tabela:" + f.nome)]
    if f.oculta:
        linhas.append("\tisHidden")
    if f.categoria:
        linhas.append("\tdataCategory: " + f.categoria)
    linhas.append("")
    for c in f.colunas:
        linhas += bloco_coluna(f.nome, c)
    linhas += ["\tpartition " + citar(f.nome) + " = m", "\t\tmode: import", "\t\tsource ="]
    linhas += expressao(f.corpo, 4)
    linhas += ["", "\tannotation PBI_ResultType = Table", ""]
    return NL.join(linhas) + NL


def tmdl_tabela_calc(f: Fonte) -> str:
    linhas = desc(f.descricao, 0) + ["table " + citar(f.nome), "\tlineageTag: " + id_estavel("tabela:" + f.nome)]
    if f.oculta:
        linhas.append("\tisHidden")
    linhas.append("")
    for c in f.colunas:
        linhas += bloco_coluna(f.nome, c, calculada=True)
    linhas += ["\tpartition " + citar(f.nome) + " = calculated", "\t\tmode: import", "\t\tsource ="]
    linhas += expressao(f.corpo, 4)
    linhas.append("")
    return NL.join(linhas) + NL


def tmdl_grupo_calculo(f: Fonte) -> str:
    """Grupo de cálculo de um item só (padrão do painel de referência): o item é o corpo do arquivo; Item e Ordinal ocultos."""
    linhas = desc(f.descricao, 0) + ["table " + citar(f.nome)]
    if f.oculta:
        linhas.append("	isHidden")
    linhas += ["	lineageTag: " + id_estavel("tabela:" + f.nome), "", "	calculationGroup",
               f"		precedence: {f.precedencia}", ""]
    linhas += desc(f.descricao, 2)
    linhas.append("		calculationItem " + citar(f.item) + " =")
    linhas += expressao(f.corpo, 4)
    linhas += ["", "	column Item", "		dataType: string", "		isHidden",
               "		lineageTag: " + id_estavel(f"coluna:{f.nome}.Item"), "		summarizeBy: none",
               "		sourceColumn: Name", "		sortByColumn: Ordinal", "",
               "		annotation SummarizationSetBy = Automatic", "",
               "	column Ordinal", "		dataType: int64", "		isHidden",
               "		lineageTag: " + id_estavel(f"coluna:{f.nome}.Ordinal"), "		summarizeBy: sum",
               "		sourceColumn: Ordinal", "", "		annotation SummarizationSetBy = Automatic", ""]
    return NL.join(linhas) + NL


def tmdl_relacoes() -> str:
    linhas = []
    for de_t, de_c, para_t, para_c in RELACOES:
        linhas += [f"relationship {citar(f'rel_{de_t}_{de_c}_{para_t}')}",
                   "\tcrossFilteringBehavior: oneDirection",
                   f"\tfromColumn: {citar(de_t)}.{citar(de_c)}",
                   f"\ttoColumn: {citar(para_t)}.{citar(para_c)}", ""]
    return NL.join(linhas) + NL


def tmdl_modelo(calcs: list[Fonte]) -> str:
    ordem = parametros() + EXPRESSOES + TABELAS_M
    linhas = desc("Construtora fictícia de Natal/RN · Acompanhamento de obras e análise crítica, Vizu Dados. Fonte: uma planilha Análise Crítica "
                  "por obra, uma aba por mês, lida pelo Power Query (stgAbas → fAnaliseCritica, fItens; fConferencia é consulta auxiliar, não carregada), "
                  "e uma base complementar por obra (stgAbasBase → fBaseObra); a cronograma (stgCrono → dObra: situação, orçamento, datas; fCurvaPrevista). "
                  "Mês de referência pelo seletor dMesRef (desconectado). Gerado pelo gerador do modelo.", 0)
    linhas += ["model Model", "\tculture: pt-BR", "\tdefaultPowerBIDataSourceVersion: powerBI_V3",
               "\tdiscourageImplicitMeasures", "\tsourceQueryCulture: pt-BR", "\tvalueFilterBehavior: independent",
               "\tdataAccessOptions", "\t\tfastCombine", "\t\tlegacyRedirects", "",
               "annotation __PBI_TimeIntelligenceEnabled = 0", "",
               "annotation PBI_QueryOrder = [" + ",".join(f'"{n}"' for n in ordem) + "]", ""]
    linhas += ["ref table " + citar(t) for t in TABELAS_M + [c.nome for c in calcs] + ["_Medidas"]]
    linhas += ["", "ref cultureInfo pt-BR", ""]
    return NL.join(linhas) + NL


def tmdl_expressoes(params: dict[str, Fonte]) -> str:
    linhas = []
    for nome in parametros() + EXPRESSOES:
        f = params[nome]
        linhas += desc(f.descricao, 0)
        if f.tipo == "parametro":
            corpo = " ".join(l.strip() for l in f.corpo.split("\n") if l.strip())
            if "IsParameterQuery" not in corpo:
                raise ErroGerador(f"{f.arquivo.name}: parâmetro sem meta IsParameterQuery")
            m = re.search(r'Type\s*=\s*"(\w+)"', corpo)
            tipo = {"Date": "Date", "Number": "Number", "Logical": "Logical"}.get(m.group(1) if m else "", "Text")
            linhas += [f"expression {citar(nome)} = {corpo}"]
        else:
            tipo = "Function" if f.tipo == "funcao" else "Table"
            linhas += [f"expression {citar(nome)} ="] + expressao(f.corpo, 2)
        linhas += ["\tlineageTag: " + id_estavel("expressao:" + nome), "",
                   f"\tannotation PBI_ResultType = {tipo}", ""]
    return NL.join(linhas) + NL


def json_bytes(obj) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def plano_arquivos(params, tabelas, calcs, medidas_tmdl: str) -> dict[str, bytes]:
    arq: dict[str, bytes] = {}

    def txt(rel, s):
        arq[rel] = s.encode("utf-8")

    arq["definition.pbism"] = json_bytes({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
        "version": "4.2", "settings": {}})
    arq[".platform"] = json_bytes({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "SemanticModel", "displayName": NOME},
        "config": {"version": "2.0", "logicalId": id_estavel("platform:SemanticModel:" + NOME)}})
    arq[".pbi/editorSettings.json"] = json_bytes({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/editorSettings/1.0.0/schema.json",
        "autodetectRelationships": False, "parallelQueryLoading": True, "typeDetectionEnabled": False,
        "relationshipImportEnabled": False, "relationshipRefreshEnabled": False, "runBackgroundAnalysis": False,
        "shouldNotifyUserOfNameConflictResolution": True})
    txt("definition/database.tmdl", NL.join(["database", "\tcompatibilityLevel: 1606", ""]) + NL)
    txt("definition/model.tmdl", tmdl_modelo(calcs))
    txt("definition/expressions.tmdl", tmdl_expressoes(params))
    txt("definition/relationships.tmdl", tmdl_relacoes())
    txt("definition/cultures/pt-BR.tmdl", NL.join(["cultureInfo pt-BR", ""]) + NL)
    for nome in TABELAS_M:
        txt(f"definition/tables/{nome}.tmdl", tmdl_tabela_m(tabelas[nome]))
    for f in calcs:
        txt(f"definition/tables/{f.nome}.tmdl",
            tmdl_grupo_calculo(f) if f.tipo == "grupo-calculo" else tmdl_tabela_calc(f))
    txt("definition/tables/_Medidas.tmdl", medidas_tmdl)
    return arq


# =====================================================================================================================
# 3. Lint de texto, caminhos, referências
# =====================================================================================================================
LIMITE_ARQUIVO = 256          # margem sobre o limite do Desktop (arquivo < 260, pasta < 248; L045)
LIMITE_PASTA = 248


def lint_caminhos(arq: dict[str, bytes], base: Path) -> list[str]:
    erros = []
    extras = [".pbi/cache.abf", ".pbi/localSettings.json", ".pbi/unappliedChanges.json", "diagramLayout.json"]
    for rel in list(arq) + extras:
        caminho = str(base / rel)
        if len(caminho) >= LIMITE_ARQUIVO:
            erros.append(f"caminho com {len(caminho)} caracteres (limite {LIMITE_ARQUIVO - 1}): {caminho}")
        pasta = str((base / rel).parent)
        if len(pasta) >= LIMITE_PASTA:
            erros.append(f"pasta com {len(pasta)} caracteres (limite {LIMITE_PASTA - 1}): {pasta}")
    return sorted(set(erros))


def lint_tmdl_texto(arq: dict[str, bytes]) -> list[str]:
    erros = lint_caminhos(arq, PASTA_MODELO)
    for rel, dados in arq.items():
        if not rel.endswith(".tmdl"):
            continue
        if dados.startswith(b"\xef\xbb\xbf"):
            erros.append(f"{rel}: BOM")
        s = dados.decode("utf-8")
        linhas = s.split(NL)
        for i, l in enumerate(linhas, 1):
            if "\n" in l or "\r" in l:
                erros.append(f"{rel}:{i}: quebra de linha fora de CRLF")
                break
            if l != l.rstrip():
                erros.append(f"{rel}:{i}: espaço no fim da linha")
            if l.startswith(" "):
                erros.append(f"{rel}:{i}: indentação com espaço (TMDL do Desktop usa tab)")
            if l.lstrip("\t").startswith("///") and i < len(linhas) and not linhas[i].strip():
                erros.append(f"{rel}:{i}: '///' seguido de linha vazia (a descrição tem de colar no objeto)")
    return erros


def conferir_referencias(tabelas: dict[str, Fonte], calcs: list[Fonte]) -> list[str]:
    erros = []
    todas = {**tabelas, **{c.nome: c for c in calcs}}
    for f in todas.values():
        nomes = {c.nome for c in f.colunas}
        for c in f.colunas:
            if c.ordenar_por and c.ordenar_por not in nomes:
                erros.append(f"{f.nome}.{c.nome}: ordenar={c.ordenar_por} não existe na tabela")
    for de_t, de_c, para_t, para_c in RELACOES:
        if de_t not in todas or para_t not in todas:
            erros.append(f"relação {de_t} → {para_t}: tabela inexistente")
            continue
        cols_de = {c.nome: c for c in todas[de_t].colunas}
        cols_para = {c.nome: c for c in todas[para_t].colunas}
        if de_c not in cols_de or para_c not in cols_para:
            erros.append(f"relação {de_t}[{de_c}] → {para_t}[{para_c}] com coluna inexistente")
        elif cols_de[de_c].tipo != cols_para[para_c].tipo:
            erros.append(f"relação {de_t}[{de_c}] → {para_t}[{para_c}] com tipos diferentes")
    return erros


def lint_tom(pasta_definition: Path, saida_json: Path) -> tuple[bool, dict]:
    cmd = ["pwsh", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(LINT_PS1),
           "-Pasta", str(pasta_definition), "-Saida", str(saida_json)]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=300)
    except (OSError, subprocess.SubprocessError) as e:
        return False, {"erro": f"lint_tmdl.ps1 não rodou: {e}"}
    if saida_json.is_file():
        try:
            doc = json.loads(saida_json.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as e:
            doc = {"erro": f"saída ilegível: {e}"}
    else:
        doc = {"erro": (r.stdout or b"").decode("utf-8", "replace")[-2000:] + (r.stderr or b"").decode("utf-8", "replace")[-2000:]}
    return (r.returncode == 0 and doc.get("ok") is True), doc


def lint_tom_plano(arq: dict[str, bytes]) -> tuple[bool, dict]:
    import shutil
    tmp = QA / "_lint-plano"
    if tmp.exists():
        shutil.rmtree(tmp)
    for rel, dados in arq.items():
        if rel.startswith("definition/"):
            destino = tmp / rel
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(dados)
    return lint_tom(tmp / "definition", QA / "lint-tom-plano.json")


# =====================================================================================================================
# 4. Disco, backup, Desktop aberto
# =====================================================================================================================
def ler_disco(pasta: Path) -> dict[str, bytes]:
    disco = {}
    if pasta.is_dir():
        for p in sorted(pasta.rglob("*")):
            if p.is_file():
                rel = p.relative_to(pasta).as_posix()
                if rel in (".pbi/cache.abf", ".pbi/localSettings.json") or rel.startswith(".pbi/unapplied"):
                    continue
                disco[rel] = p.read_bytes()
    return disco


def desktop_aberto_neste_projeto() -> list[str] | None:
    # o console do PowerShell escreve em cp850; em UTF-8 o caminho com acento chega inteiro (auditoria da Fase 2)
    comando = ("[Console]::OutputEncoding = [Text.Encoding]::UTF8; "
               "Get-CimInstance Win32_Process -Filter \"Name='PBIDesktop.exe'\" | "
               "ForEach-Object { if ($_.CommandLine) { $_.CommandLine } else { '<sem linha de comando>' } }")
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", comando],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    linhas = [l.strip() for l in r.stdout.splitlines() if l.strip()]
    alvo = str(PBIP_DIR).lower()
    return [l for l in linhas if alvo in l.lower() or l == "<sem linha de comando>"]


def fazer_backup(pasta: Path, nome_pasta: str, rotulo: str) -> Path | None:
    disco = ler_disco(pasta)
    if not disco:
        return None
    BACKUPS.mkdir(parents=True, exist_ok=True)
    caminho = BACKUPS / f"{rotulo}-{dt.datetime.now():%Y%m%d-%H%M%S}.zip"
    with zipfile.ZipFile(caminho, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for rel, dados in disco.items():
            z.writestr(f"{nome_pasta}/{rel}", dados)
    return caminho


def gravar_atomico(caminho: Path, dados: bytes) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    tmp = caminho.with_name(caminho.name + ".tmp-gerar")
    tmp.write_bytes(dados)
    for tentativa in range(6):
        try:
            os.replace(tmp, caminho)
            return
        except PermissionError:
            if tentativa == 5:
                raise
            import time
            time.sleep(0.5 * (tentativa + 1))


GERENCIADOS = re.compile(r"^(definition\.pbism|\.platform|\.pbi/editorSettings\.json|definition/.*\.tmdl)$")


# =====================================================================================================================
# 5. main
# =====================================================================================================================
def _embutir():
    """pipeline/embutir_dados.py como módulo (gera pbi/m/fxDadosEmbutidos.m a partir de dados/)."""
    import importlib.util
    arq = RAIZ.parent / "pipeline" / "embutir_dados.py"
    spec = importlib.util.spec_from_file_location("embutir_dados", arq)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    modo = ap.add_mutually_exclusive_group()
    modo.add_argument("--aplicar", action="store_true")
    modo.add_argument("--conferir", action="store_true")
    ap.add_argument("--sem-tom", action="store_true", help="pula o lint pelo TOM (mais rápido)")
    ap.add_argument("--perfil", choices=["construtora", "local"], default="construtora",
                    help="construtora (padrão, o da entrega): caminhos da Construtora em pbi/m; local: os quatro caminhos de perfil_local.json")
    ap.add_argument("--sem-pasta", action="append", default=[],
                    help="deixa de fora as medidas de pbi/dax/<pasta> (tela em obra de outro agente; ex.: T3)")
    a = ap.parse_args(argv)

    # pOrigem = "Embutido": os arquivos de dados/ vão para pbi/m/fxDadosEmbutidos.m antes da montagem (só grava se mudou)
    emb = _embutir()
    if a.aplicar:
        emb.main()
    elif emb.DESTINO.is_file() and emb.DESTINO.read_text(encoding="utf-8") != emb.gerar():
        print("[AVISO] pbi/m/fxDadosEmbutidos.m não bate com dados/: o --aplicar regrava (pipeline/embutir_dados.py)")

    global PERFIL
    PERFIL = a.perfil
    try:
        params, tabelas, calcs = ler_fontes()
        trocados = aplicar_perfil(params, a.perfil)
        print(f"perfil: {a.perfil}" + (f" · caminhos de perfil_local.json: {', '.join(trocados)} (não é a entrega)"
                                       if trocados else " · caminhos da Construtora (entrega)"))
        medidas = dpt.coletar(DAX_DIR)
        if a.sem_pasta:
            fora = set(a.sem_pasta)
            antes = len(medidas)
            medidas = [x for x in medidas if Path(x["arquivo"]).relative_to(DAX_DIR).parts[0] not in fora]
            print(f"--sem-pasta {sorted(fora)}: {antes - len(medidas)} medidas de fora")
    except (ErroGerador, dpt.ErroEntrada) as e:
        print(f"[BLOQUEIO] {e}")
        return 2
    medidas_tmdl = dpt.gerar(medidas, "_Medidas", NS_MEDIDAS,
                             "Medidas do relatório (contas e desenho). Gerada a partir de pbi/dax/**/*.dax; não edite à mão.")
    plano = plano_arquivos(params, tabelas, calcs, medidas_tmdl)
    erros = lint_tmdl_texto(plano) + conferir_referencias(tabelas, calcs)
    if PERFIL == "construtora":   # a entrega não cita fonte externa nenhuma (nem em descrição)
        for rel, texto in plano.items():
            if rel.endswith("expressions.tmdl") or rel.endswith("model.tmdl"):
                achados = [x for x in PROIBIDO_NA_ENTREGA if x in (texto if isinstance(texto, str) else texto.decode("utf-8"))]
                if achados:
                    erros.append(f"{rel}: o perfil padrão não pode citar {', '.join(achados)} (fonte externa)")
    print(f"plano: {len(plano)} arquivos · {len(TABELAS_M)} tabelas M · {len(calcs)} calculadas · "
          f"{len(medidas)} medidas · {len(RELACOES)} relações")
    if erros:
        for e in erros:
            print("  [ERRO]", e)
        return 2
    if not a.sem_tom:
        ok, doc = lint_tom_plano(plano)
        print(f"lint TOM (plano): ok={ok} erros={len(doc.get('erros', []) or [])} avisos={len(doc.get('avisos', []) or [])}")
        for e in (doc.get("erros") or [])[:20]:
            print("  [TOM]", e)
        if doc.get("erro"):
            print("  [TOM]", doc["erro"])
        if not ok:
            return 2

    disco = ler_disco(PASTA_MODELO)
    mudam = sorted(rel for rel, dados in plano.items() if disco.get(rel) != dados)
    sobram = sorted(rel for rel in disco if GERENCIADOS.match(rel) and rel not in plano)
    print(f"disco: {len(mudam)} arquivos mudam · {len(sobram)} sobram (gerenciados, fora do plano)")
    for rel in mudam[:40]:
        print("  ~", rel)
    for rel in sobram:
        print("  -", rel)
    if a.conferir:
        return 1 if (mudam or sobram) else 0
    if not a.aplicar:
        print("simulação: nada gravado (use --aplicar)")
        return 0
    abertos = desktop_aberto_neste_projeto()
    if abertos:
        print("[BLOQUEIO] Power BI Desktop aberto neste projeto: feche antes de gerar o modelo.")
        for l in abertos:
            print("   ", l[:200])
        return 3
    if not mudam and not sobram:
        print("nada a gravar")
        return 0
    bak = fazer_backup(PASTA_MODELO, PASTA_MODELO_NOME, "modelo")
    if bak:
        print(f"backup: {bak}")
    for rel in mudam:
        gravar_atomico(PASTA_MODELO / rel, plano[rel])
    for rel in sobram:
        (PASTA_MODELO / rel).unlink(missing_ok=True)
    print(f"gravado: {len(mudam)} arquivos · removidos: {len(sobram)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

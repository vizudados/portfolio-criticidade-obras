#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lint estático da separação conta × desenho em medidas DAX.

Lê uma árvore de arquivos .dax (um por medida, com cabeçalho /* @pasta @formato @descricao */) ou arquivos .tmdl
(blocos `measure`), classifica cada medida como DESENHO (pelo nome) ou CONTA, e aponta:

  ERRO   desenho que agrega, muda contexto de filtro ou tem marcação numa conta; cabeçalho .dax incompleto;
         FORMAT de número exibido sem a cultura ("pt-BR"): no serviço o decimal sairia com ponto;
         nome de medida repetido; VAR que só difere de outra na caixa (o DAX não diferencia); aspas desbalanceadas
         numa linha (string que não fecha); FILTER/COUNTROWS/SUMX… sobre a lista que o próprio desenho montou numa VAR sem a
         marca "-- lista" (ou "-- geometria") na linha — a marca declara que o resultado não aparece como número.
  AVISO  aritmética entre medidas, DIVIDE/MINX/MAXX sem a marca "-- geometria", conta de tela fora da pasta
         "\\Contas", conta sem @oraculo, tab, linha longa, duas VAR na mesma linha, aninhamento > 3.

Só lê; não grava nada além do --json pedido. Código de saída: 0 sem ERRO, 1 com ERRO, 2 uso errado.

    python lint_conta_desenho.py pbi/dax
    python lint_conta_desenho.py pbip/X.SemanticModel/definition/tables/_Medidas.tmdl --json lint.json
    python lint_conta_desenho.py pbi/dax --desenho "· (HTML|ALT|SVG)\\b|· rótulo" --largura 120 --so-erros
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# "· HTML…" no fim (padrão desta skill) ou "HTML …" no começo (padrão antigo do painel de referência). Prefixos como "Drawer ·" ficam
# de fora de propósito: medidas de contagem do drawer são contas.
DESENHO_PADRAO = r"· (HTML|ALT|SVG|CSS|JS|Vega)\b|· textos?$|· rótulo|· legenda$|^(HTML|ALT|SVG|CSS|JS)\b"

AGREGA = re.compile(
    r"\b(SUM|SUMX|COUNT|COUNTA|COUNTAX|COUNTBLANK|COUNTROWS|COUNTX|DISTINCTCOUNT|DISTINCTCOUNTNOBLANK|AVERAGE|"
    r"AVERAGEA|AVERAGEX|MEDIAN|MEDIANX|PERCENTILE\.INC|PERCENTILE\.EXC|PERCENTILEX\.INC|PERCENTILEX\.EXC|PRODUCT|"
    r"PRODUCTX|RANKX|RANK|STDEV\.S|STDEV\.P|STDEVX\.S|STDEVX\.P|VAR\.S|VAR\.P|VARX\.S|VARX\.P|GEOMEAN|GEOMEANX)\s*\(",
    re.I)
MINMAX_COLUNA = re.compile(r"\b(MIN|MAX|MINA|MAXA)\s*\(\s*'?[\w][\w \-]*'?\s*\[[^\]]+\]\s*\)", re.I)
CONTEXTO = re.compile(
    r"\b(REMOVEFILTERS|ALL|ALLEXCEPT|ALLSELECTED|ALLNOBLANKROW|ALLCROSSFILTERED|KEEPFILTERS|FILTER|USERELATIONSHIP|"
    r"CROSSFILTER|TREATAS|DATEADD|DATESYTD|DATESMTD|DATESQTD|DATESBETWEEN|DATESINPERIOD|SAMEPERIODLASTYEAR|"
    r"PARALLELPERIOD|PREVIOUSDAY|PREVIOUSMONTH|PREVIOUSYEAR|NEXTDAY|NEXTMONTH|TOTALYTD|TOTALMTD|TOTALQTD|"
    r"OFFSET|WINDOW|INDEX)\s*\(", re.I)
GEOMETRIA = re.compile(r"\b(DIVIDE|MINX|MAXX)\s*\(", re.I)
ARIT_MEDIDAS = re.compile(r"\]\s*[-/*]\s*\[|\]\s*[-/*]\s*\(?\s*\[")
MARCACAO = re.compile(r"<\s*/?\s*(div|span|p|b|i|svg|path|rect|circle|text|section|article|header|footer|ul|li|"
                      r"table|tr|td|th|style|script|small|strong|em|g|line|polyline|polygon)\b", re.I)
NOME_TELA = re.compile(r"^T\d+\s·")
VAR_LINHA = re.compile(r"\bVAR\b", re.I)
# Marcas aceitas no fim da linha: comentário de linha (-- geometria) ou de bloco (/* geometria */), para projetos cujo
# gerador proíbe comentário de linha na medida.
MARCA_GEO = re.compile(r"(--|//)\s*geometria\b|/\*\s*(--\s*)?geometria\s*\*/")
MARCA_LISTA = re.compile(r"(--|//)\s*lista\b|/\*\s*(--\s*)?lista\s*\*/")
CAB = re.compile(r"@(\w+)\s*:\s*(.*?)(?=\s+@\w+\s*:|\s*\*/|$)", re.S)
CHAVES_OBRIG = ("pasta", "formato", "descricao")


@dataclass
class Medida:
    nome: str
    origem: str
    linha0: int
    corpo: str
    cab: dict = field(default_factory=dict)
    tipo: str = "dax"


@dataclass
class Achado:
    nivel: str
    medida: str
    origem: str
    linha: int
    regra: str
    texto: str


def mascarar(t: str) -> str:
    """Troca o conteúdo de strings e comentários por espaços, preservando quebras de linha e posições."""
    out = []
    i, n = 0, len(t)
    while i < n:
        c = t[i]
        if c == '"':
            out.append('"')
            i += 1
            while i < n:
                if t[i] == '"' and i + 1 < n and t[i + 1] == '"':
                    out.append("  ")
                    i += 2
                    continue
                if t[i] == '"':
                    out.append('"')
                    i += 1
                    break
                out.append("\n" if t[i] == "\n" else " ")
                i += 1
            continue
        if t.startswith("--", i) or t.startswith("//", i):
            j = t.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
            continue
        if t.startswith("/*", i):
            j = t.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append("".join("\n" if ch == "\n" else " " for ch in t[i:j]))
            i = j
            continue
        out.append(c)
        i += 1
    return "".join(out)


def literais(t: str) -> str:
    """Só o conteúdo das strings (para procurar marcação HTML)."""
    return " ".join(m.group(1) for m in re.finditer(r'"((?:[^"]|"")*)"', t))


def separar_cabecalho(texto: str) -> tuple[dict, str, int]:
    t = texto.lstrip("﻿").replace("\r\n", "\n")
    s = t.lstrip()
    if s.startswith("/*") and "*/" in s:
        ini = t.index("/*")
        fim = t.index("*/", ini) + 2
        bloco = t[ini:fim]
        cab = {k.lower(): re.sub(r"\s+", " ", v).strip() for k, v in CAB.findall(bloco)}
        if cab:
            return cab, t[fim:], t[:fim].count("\n")
    return {}, t, 0


def ler_dax(raiz: Path) -> list[Medida]:
    arquivos = [raiz] if raiz.is_file() else sorted(raiz.rglob("*.dax"))
    out = []
    for p in arquivos:
        if "_modelo" in p.parts:
            continue
        cab, corpo, desloc = separar_cabecalho(p.read_text(encoding="utf-8"))
        out.append(Medida(cab.get("nome") or p.stem, str(p), desloc + 1, corpo, cab, "dax"))
    return out


RE_MEDIDA_TMDL = re.compile(r"^\tmeasure\s+('(?:[^']|'')+'|[^\s=]+)\s*=\s*(.*)$")


def ler_tmdl(p: Path) -> list[Medida]:
    linhas = p.read_text(encoding="utf-8").lstrip("﻿").replace("\r\n", "\n").split("\n")
    out = []
    i = 0
    while i < len(linhas):
        m = RE_MEDIDA_TMDL.match(linhas[i])
        if not m:
            i += 1
            continue
        nome = m.group(1)
        if nome.startswith("'"):
            nome = nome[1:-1].replace("''", "'")
        corpo = [m.group(2)] if m.group(2).strip() and m.group(2).strip() != "```" else []
        ini = i + 1
        j = i + 1
        while j < len(linhas):
            l = linhas[j]
            if l.startswith("\t\t\t") or (not l.strip() and j + 1 < len(linhas)
                                          and linhas[j + 1].startswith("\t\t\t")):
                corpo.append(l[3:] if l.startswith("\t\t\t") else "")
                j += 1
                continue
            break
        pasta = ""
        k = j
        while k < len(linhas) and linhas[k].startswith("\t\t") and not linhas[k].startswith("\t\t\t"):
            mm = re.match(r"\t\tdisplayFolder:\s*(.*)$", linhas[k])
            if mm:
                pasta = mm.group(1).strip()
            k += 1
        out.append(Medida(nome, str(p), ini, "\n".join(corpo), {"pasta": pasta}, "tmdl"))
        i = max(j, i + 1)
    return out


# Lista do desenho (contrato, "montar a lista a desenhar"): FILTER, COUNTROWS, SUMX, MINX, MAXX e afins sobre uma tabela
# que a própria medida montou numa VAR (_serie, _pts, DISTINCT ( SELECTCOLUMNS ( _maq, … ) ), FILTER ( _sh, … )) não
# tocam o modelo: só decidem o que desenhar e onde. São aceitos quando a linha leva a marca "-- lista" ou
# "-- geometria" — a marca é a declaração de que o resultado não aparece como número. Sobre tabela ou coluna do
# modelo (VALUES ( fOrdens[…] ), FILTERS, SUM ( col )) continuam ERRO, com ou sem marca.
ENVOLTORIOS = ("DISTINCT", "SELECTCOLUMNS", "ADDCOLUMNS", "FILTER", "VALUES", "TOPN")
RE_TOKEN = re.compile(r"\s*([A-Za-z_][\w.]*)\s*(\()?")


def arg_lista(masc: str, pos: int, prof: int = 0) -> bool:
    """True quando o primeiro argumento da chamada cujo '(' fecha em masc[pos-1] é tabela de VAR da medida."""
    m = RE_TOKEN.match(masc, pos)
    if not m or prof > 4:
        return False
    nome, abre = m.group(1), m.group(2)
    if nome.startswith("_") and not abre:
        return True
    if abre and nome.upper() == "GENERATESERIES":   # série montada na medida (posições de caractere, índices): não é dado
        return True
    if abre and nome.upper() in ENVOLTORIOS:
        if nome.upper() == "TOPN":       # TOPN ( n, tabela, … ): a tabela é o 2º argumento
            i, d = m.end(), 0
            while i < len(masc):
                c = masc[i]
                if c == "(":
                    d += 1
                elif c == ")":
                    if d == 0:
                        return False
                    d -= 1
                elif c == "," and d == 0:
                    return arg_lista(masc, i + 1, prof + 1)
                i += 1
            return False
        return arg_lista(masc, m.end(), prof + 1)
    return False


def profundidade_max(masc: str) -> int:
    prof = pico = 0
    for c in masc:
        if c == "(":
            prof += 1
            pico = max(pico, prof)
        elif c == ")":
            prof -= 1
    return pico


def args_format(texto: str, ini: int) -> list[str]:
    """Os argumentos (texto cru) do FORMAT ( … ) que abre em `ini` (logo depois do '('), atento a strings e parênteses."""
    args, atual, prof, j = [], [], 1, ini
    while j < len(texto) and prof:
        c = texto[j]
        if c == '"':
            k = j + 1
            while k < len(texto):
                if texto[k] == '"' and texto[k + 1:k + 2] == '"':
                    k += 2
                    continue
                if texto[k] == '"':
                    break
                k += 1
            atual.append(texto[j:k + 1])
            j = k + 1
            continue
        if c == "(":
            prof += 1
        elif c == ")":
            prof -= 1
        elif c == "," and prof == 1:
            args.append("".join(atual).strip())
            atual = []
            j += 1
            continue
        if prof:
            atual.append(c)
        j += 1
    args.append("".join(atual).strip())
    return args


FORMAT_RX = re.compile(r"\bFORMAT\s*\(", re.I)
INTEIRO_RX = re.compile(r'^"0+"$|^REPT\s*\(\s*"0"', re.I)


def format_sem_cultura(corpo: str) -> list[tuple[int, str]]:
    """FORMAT com padrão que depende da cultura (decimal, milhar, %, data, ou padrão em variável) sem o 3º argumento:
    no serviço ele segue a cultura de quem abre o relatório, e o decimal sai com ponto (retorno da sessão local,
    28/10/2026). Padrão só de zeros ("0", REPT ( "0", … )) e linha marcada geometria (número para o CSS) passam."""
    achados = []
    for m in FORMAT_RX.finditer(corpo):
        a = args_format(corpo, m.end())
        if len(a) != 2:
            continue
        lin = corpo.count("\n", 0, m.start())
        linha = corpo.split("\n")[lin]
        if MARCA_GEO.search(linha) or INTEIRO_RX.search(a[1]) or a[1].lower() == '"yyyymm"':
            continue
        achados.append((lin, f"FORMAT ( …, {a[1][:24]} ) sem \"pt-BR\""))
    return achados


def checar(med: Medida, eh_desenho: bool, largura: int, aninhamento: int) -> list[Achado]:
    ach: list[Achado] = []

    def add(nivel, linha, regra, texto):
        ach.append(Achado(nivel, med.nome, med.origem, linha, regra, texto))

    if med.tipo == "dax":
        faltam = [k for k in CHAVES_OBRIG if not med.cab.get(k)]
        if faltam:
            add("ERRO", 1, "cabecalho", "faltam @" + ", @".join(faltam))
    original = med.corpo.split("\n")
    masc_txt = mascarar(med.corpo)
    masc = masc_txt.split("\n")
    inicio, acc = [], 0
    for lin in masc:
        inicio.append(acc)
        acc += len(lin) + 1
    for idx, (orig, lin) in enumerate(zip(original, masc)):
        nlin = med.linha0 + idx
        geo = bool(MARCA_GEO.search(orig))
        marcada = geo or bool(MARCA_LISTA.search(orig))
        if eh_desenho:
            for regra, rx, txt in (("agregacao-no-desenho", AGREGA, "agregação vira conta"),
                                   ("contexto-no-desenho", CONTEXTO, "mudança de contexto vira conta")):
                for m in rx.finditer(lin):
                    fn = m.group(1).upper()
                    if arg_lista(masc_txt, inicio[idx] + m.end()):
                        if not marcada:
                            add("ERRO", nlin, "lista-sem-marca",
                                f"{fn}( sobre a lista do desenho — se só decide o desenho, marque '/* lista */'; "
                                "se o número aparece, vira conta")
                        continue
                    add("ERRO", nlin, regra, f"{fn}( — {txt}")
            for m in MINMAX_COLUNA.finditer(lin):
                add("ERRO", nlin, "agregacao-no-desenho", f"{m.group(1).upper()} de coluna — vira conta")
            if not marcada:
                for m in GEOMETRIA.finditer(lin):
                    add("AVISO", nlin, "geometria-sem-marca",
                        f"{m.group(1).upper()}( — se só posiciona, marque '/* geometria */'; se aparece, vira conta")
                if ARIT_MEDIDAS.search(lin):
                    add("AVISO", nlin, "aritmetica-entre-medidas",
                        "conta entre medidas no desenho — se o resultado aparece, vira conta")
        if "\t" in orig and med.tipo == "dax":
            add("AVISO", nlin, "tab", "tab no .dax — use 4 espaços")
        if len(orig.rstrip()) > largura:
            add("AVISO", nlin, "linha-longa", f"{len(orig.rstrip())} colunas (> {largura})")
        if len(VAR_LINHA.findall(lin)) > 1:
            add("AVISO", nlin, "var-na-mesma-linha", "uma VAR por linha")
    # decimal com ponto no serviço: todo FORMAT de número exibido leva a cultura (F4, 28/10/2026)
    for lin, txt in format_sem_cultura(med.corpo):
        add("ERRO", med.linha0 + lin, "format-sem-cultura", txt)
    # a mesma VAR declarada duas vezes no nível de cima: o DAX recusa a medida e o visual mostra "Há algo errado em um
    # ou mais campos" (a linha do tempo da T3, 28/10/2026)
    vistas: dict[str, int] = {}
    for idx, lin in enumerate(masc):
        mv = re.match(r"VAR (_?\w+) =", lin)
        if mv:
            if mv.group(1) in vistas:
                add("ERRO", med.linha0 + idx, "var-repetida",
                    f"VAR {mv.group(1)} já declarada na linha {vistas[mv.group(1)]}")
            else:
                vistas[mv.group(1)] = med.linha0 + idx
    # o DAX não diferencia caixa: _mck e _mcK são a mesma variável (o bloco de marcas, 28/10/2026: toda marca virava "a
    # última" e repetia o resto do HTML na tela). Qualquer par de VAR que só difere na caixa é erro, em qualquer nível.
    grafias: dict[str, tuple[str, int]] = {}
    for idx, lin in enumerate(masc):
        for mv in re.finditer(r"\bVAR\s+(_?\w+)\s*=", lin, re.I):
            nome_v, chave = mv.group(1), mv.group(1).lower()
            if chave in grafias and grafias[chave][0] != nome_v:
                add("ERRO", med.linha0 + idx, "var-caixa",
                    f"VAR {nome_v} e VAR {grafias[chave][0]} (linha {grafias[chave][1]}) são a mesma variável no DAX, "
                    "que não diferencia caixa")
            else:
                grafias.setdefault(chave, (nome_v, med.linha0 + idx))
    # aspa sobrando: string que atravessa a quebra de linha ou não fecha (Sidebar · HTML mês, 28/10/2026: QueryUserError
    # no serviço). Os geradores daqui nunca quebram string literal em duas linhas, então número ímpar de aspas numa linha
    # fora de comentário (com "" contando como escape) é erro.
    for idx, lin in enumerate(masc):
        if lin.count('"') % 2:
            add("ERRO", med.linha0 + idx, "aspas-desbalanceadas",
                "string que não fecha na mesma linha — aspa sobrando ou faltando")
    if not eh_desenho and MARCACAO.search(literais(med.corpo)):
        add("ERRO", med.linha0, "marcacao-na-conta",
            "conta com marcação HTML/SVG — renomeie como desenho ou separe")
    prof = profundidade_max("\n".join(masc))
    if prof > aninhamento + 2:
        add("AVISO", med.linha0, "aninhamento",
            f"{prof} níveis de parênteses — quebre em VAR (alvo: lógica com ≤ {aninhamento} níveis)")
    if not eh_desenho:
        pasta = med.cab.get("pasta", "")
        if NOME_TELA.match(med.nome) and pasta and not pasta.rstrip("\\").endswith("Contas"):
            add("AVISO", med.linha0, "pasta-da-conta", f"conta de tela fora de '\\Contas' (pasta: {pasta})")
        if med.tipo == "dax" and not med.cab.get("oraculo") and not med.cab.get("oculta"):
            add("AVISO", med.linha0, "sem-oraculo", "conta sem @oraculo")
    return ach


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("caminhos", nargs="+", help="pastas com .dax, arquivos .dax ou .tmdl")
    ap.add_argument("--desenho", default=DESENHO_PADRAO, help="regex do nome das medidas de desenho")
    ap.add_argument("--largura", type=int, default=120, help="colunas máximas por linha (padrão 120)")
    ap.add_argument("--aninhamento", type=int, default=3, help="níveis lógicos de aninhamento tolerados (padrão 3)")
    ap.add_argument("--so-erros", action="store_true", help="mostra só ERRO")
    ap.add_argument("--detalhe", action="store_true", help="lista cada AVISO (padrão: resumo por regra)")
    ap.add_argument("--json", help="grava o relatório completo neste arquivo")
    a = ap.parse_args(argv)

    try:
        re_desenho = re.compile(a.desenho)
    except re.error as e:
        print(f"regex --desenho inválida: {e}", file=sys.stderr)
        return 2

    medidas: list[Medida] = []
    for c in a.caminhos:
        p = Path(c)
        if not p.exists():
            print(f"não existe: {p}", file=sys.stderr)
            return 2
        if p.is_dir():
            medidas += ler_dax(p)
            for t in sorted(p.rglob("*.tmdl")):
                medidas += ler_tmdl(t)
        elif p.suffix.lower() == ".tmdl":
            medidas += ler_tmdl(p)
        else:
            medidas += ler_dax(p)

    achados: list[Achado] = []
    vistos: dict[str, str] = {}
    n_desenho = 0
    for m in medidas:
        chave = m.nome.casefold()
        if chave in vistos:
            achados.append(Achado("ERRO", m.nome, m.origem, m.linha0, "nome-repetido", f"também em {vistos[chave]}"))
        vistos.setdefault(chave, m.origem)
        eh = bool(re_desenho.search(m.nome))
        n_desenho += eh
        achados += checar(m, eh, a.largura, a.aninhamento)

    erros = [x for x in achados if x.nivel == "ERRO"]
    avisos = [x for x in achados if x.nivel == "AVISO"]

    def mostrar(x: Achado) -> None:
        print(f"{x.nivel:5} {x.regra:26} {x.medida} ({Path(x.origem).name}:{x.linha}) — {x.texto}")

    for x in erros:
        mostrar(x)
    if not a.so_erros:
        if a.detalhe:
            for x in avisos:
                mostrar(x)
        else:
            por_regra: dict[str, list[Achado]] = {}
            for x in avisos:
                por_regra.setdefault(x.regra, []).append(x)
            for regra, lista in sorted(por_regra.items(), key=lambda kv: -len(kv[1])):
                medidas_r = len({x.medida for x in lista})
                print(f"AVISO {regra:26} {len(lista)} ocorrências em {medidas_r} medidas; ex.:")
                for x in lista[:3]:
                    print(f"      {x.medida} ({Path(x.origem).name}:{x.linha}) — {x.texto}")
            if avisos:
                print("      (--detalhe lista todos os avisos)")
    print(f"\n{len(medidas)} medidas ({n_desenho} desenho, {len(medidas) - n_desenho} conta) · "
          f"{len(erros)} ERRO · {len(avisos)} AVISO")
    if a.json:
        Path(a.json).write_text(json.dumps({
            "medidas": len(medidas), "desenho": n_desenho, "erros": len(erros), "avisos": len(avisos),
            "achados": [x.__dict__ for x in achados]}, ensure_ascii=False, indent=1), encoding="utf-8")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())

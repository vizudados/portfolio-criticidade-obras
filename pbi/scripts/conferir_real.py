#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""conferir_real — confere as contas do modelo (Desktop aberto, porta em pbi/qa/porta.txt) contra as planilhas da pasta
de dados (dados fictícios de Natal, pPastaDados).

    python -I -X utf8 pbi/scripts/conferir_real.py             # extrai, recalcula e confere; sai 1 se houver diferença nova
    python -I -X utf8 pbi/scripts/conferir_real.py --sem-extrair   # reaproveita pbi/qa/conferencia-real/fato_analise_critica.csv
    python -I -X utf8 pbi/scripts/conferir_real.py --so-nota        # só a Nota da obra

Passos:
  1. O extrator Python (pipeline/extrair_analise_critica.py, a especificação das regras do Power Query) lê a pasta e o
     cadastro que o modelo usa (pPastaPlanilhas e pCadastroObras) e grava o fato em pbi/qa/conferencia-real/.
  2. As contas que não são régua são recalculadas do zero sobre esse fato: resultado, resultado %, variação (aba
     anterior), desvio físico, desembolso, ativos e sem ativos.
  3. O motor devolve as mesmas 7 contas por obra × mês e a carteira no mês automático e mês a mês (variação só com as
     obras que têm aba nos dois meses).
  4. Nota da obra (docs/08 §3): o oráculo é o pipeline/conferir_ficticios.py, que lê planilhas, bases complementares e
     cronograma com openpyxl (regras reescritas lá, independentes do Power Query) e calcula a nota com as faixas do
     dicionário NOTA de contas_base.py. Aqui ele é comparado com as medidas `Nota ·` por obra × mês, por item, a
     carteira mês a mês, as listas e a obra em foco. Antes, os casos-limite da régua (transcritos à mão de docs/08)
     são conferidos no dicionário (Python) e na DAX gerada (motor).
Diferença aceita: Ativos e Resultado sem ativos nas abas em que a soma das tabelas anexadas não fecha com o quadradinho
(coluna `conferido` = False no extrator). O painel lê o quadradinho, como a planilha apresenta; o extrator soma as tabelas.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from dax import consultar  # noqa: E402
from contas_base import NOTA, NOTA_ITEM_MEDIDAS, NOTA_ITENS, dax_faixas, nota_maximo, nota_rotulos  # noqa: E402  (dicionário NOTA: fonte única)

PBI = AQUI.parent
RAIZ = PBI.parent
SAIDA = PBI / "qa" / "conferencia-real"
INICIO = "2025-10-01"


PERFIL_LOCAL = Path(__file__).resolve().parent / "perfil_local.json"  # caminhos deste computador (desenvolvimento)


def parametro(nome: str) -> str:
    """Valor do parâmetro: o de perfil_local.json, se o parâmetro estiver nele (este computador); senão o de pbi/m."""
    if PERFIL_LOCAL.is_file():
        local = json.loads(PERFIL_LOCAL.read_text(encoding="utf-8")).get("parametros", {})
        if nome in local:
            return local[nome]
    arq = PBI / "m" / f"{nome}.m"
    if not arq.is_file():                                   # parâmetros só do perfil local (pPastaDados, …)
        arq = PBI / "m" / "_local" / f"{nome}.m"
    texto = arq.read_text(encoding="utf-8")
    return re.search(r'^"([^"]+)"\s+meta', texto, re.M).group(1)


def caminho_dados(nome: str) -> str:
    """Caminho absoluto de um parâmetro de pasta ou arquivo, relativo à raiz dos dados (pPastaDados, origem Pasta)."""
    return str(Path(parametro("pPastaDados")) / Path(*re.split(r"[\\/]", parametro(nome))))


def f(x):
    x = (x or "").strip()
    return None if x == "" else float(x)


def extrair() -> Path:
    SAIDA.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-I", "-X", "utf8", str(RAIZ / "pipeline" / "extrair_analise_critica.py"),
           caminho_dados("pPastaPlanilhas"), "--cadastro", caminho_dados("pCadastroObras"), "--saida", str(SAIDA),
           "--desde", "2025-09"]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    print(r.stdout.strip().splitlines()[-2:] if r.stdout else r.stderr[-400:])
    if r.returncode:
        raise SystemExit(f"extrator falhou: {r.stderr[-600:]}")
    return SAIDA / "fato_analise_critica.csv"


def oraculo(csv_fato: Path) -> dict:
    linhas = list(csv.DictReader(open(csv_fato, encoding="utf-8-sig"), delimiter=";"))
    por_obra = defaultdict(list)
    for r in linhas:
        por_obra[r["obra"]].append(r)
    obras = {}
    for obra, rs in por_obra.items():
        rs.sort(key=lambda r: r["mes"])
        ant = None
        for r in rs:
            orc, res = f(r["orcamento"]), f(r["resultado"])
            pct = res / orc if orc else None
            pct_ant = (f(ant["resultado"]) / f(ant["orcamento"])) if ant else None
            var = (pct - pct_ant) * 100 if (pct is not None and pct_ant is not None) else None
            pa, ea = f(r["prev_acum"]), f(r["exec_acum"])
            fis = (ea - pa) * 100 if (pa is not None and ea is not None) else None
            prs, drs = f(r["previsto_mes_rs"]), f(r["desembolsado_mes_rs"])
            des = (drs / prs - 1) if (prs and drs is not None) else None
            ativos = sum(f(r[k]) or 0 for k in ("saldo_contrato", "adiant_servicos", "adiant_materiais", "estoque",
                                                   "equipamentos"))
            sem = res - ativos
            if r["mes"] >= INICIO:
                obras[f'{obra}|{r["mes"]}'] = {
                    "obra": obra, "mes": r["mes"], "orcamento": orc, "resultado": res, "pct": pct, "var_pp": var,
                    "res_ant": f(ant["resultado"]) if ant else None, "orc_ant": f(ant["orcamento"]) if ant else None,
                    "desvio_fis_pp": fis, "desvio_desemb": des, "ativos": ativos, "sem_ativos": sem,
                    "quadradinho_fecha": r["conferido"] == "True"}
            ant = r
    meses = defaultdict(list)
    for v in obras.values():
        meses[v["mes"]].append(v)
    auto = max(m for m, vs in meses.items() if len(vs) >= len(por_obra) / 2)
    carteira = {}
    for m, vs in sorted(meses.items()):
        comp = [v for v in vs if v["res_ant"] is not None]
        carteira[m] = {
            "resultado": sum(v["resultado"] for v in vs),
            "orcamento": sum(v["orcamento"] for v in vs), "ativos": sum(v["ativos"] for v in vs),
            "ativos_aceito": all(v["quadradinho_fecha"] for v in vs),
            "var_rs": sum(v["resultado"] - v["res_ant"] for v in comp) if comp else None,
            "var_pp": ((sum(v["resultado"] for v in comp) / sum(v["orcamento"] for v in comp)
                        - sum(v["res_ant"] for v in comp) / sum(v["orc_ant"] for v in comp)) * 100) if comp else None}
    return {"mes_auto": auto, "obras": obras, "carteira": carteira}


CAMPOS = [  # (alias, medida, chave, tolerância, aceita diferença quando o quadradinho não fecha)
    ("res", "Resultado da obra", "resultado", 0.01, False),
    ("pct", "Resultado %", "pct", 1e-9, False),
    ("var", "Resultado · variação p.p.", "var_pp", 1e-7, False),
    ("fis", "Físico · desvio acumulado p.p.", "desvio_fis_pp", 1e-7, False),
    ("des", "Desembolso · desvio no mês", "desvio_desemb", 1e-9, False),
    ("ati", "Ativos não consumidos", "ativos", 0.01, True),
    ("sem", "Resultado sem ativos", "sem_ativos", 0.01, True),

]


def difere(vm, vo, tol) -> bool:
    if vm is None and vo is None:
        return False
    return vm is None or vo is None or abs(float(vm) - float(vo)) > tol


# =====================================================================================================================
# Nota da obra · oráculo independente (docs/08 §3)
# =====================================================================================================================
# Casos-limite transcritos À MÃO da régua aprovada (docs/08 §3): provam o dicionário NOTA (Python) e a DAX que o gerador
# escreve a partir dele (motor). (X, pontos esperados).
CASOS_LIMITE = {
    "idc": [(1.05, 3), (1.0, 3), (0.99999, 2.5), (0.98, 2.5), (0.97999, 2), (0.96, 2), (0.95999, 1.5), (0.94, 1.5),
            (0.93999, 1), (0.92, 1), (0.91999, 0.5), (0.90, 0.5), (0.89999, 0), (0.5, 0)],
    "atraso": [(-1, 2), (0, 2), (0.5, 2), (0.50001, 1.5), (1, 1.5), (1.00001, 1), (2, 1), (2.00001, 0.5), (3, 0.5),
               (3.00001, 0), (8, 0)],
    "ppc": [(1, 1), (0.8, 1), (0.79999, 0.5), (0.7, 0.5), (0.69999, 0.25), (0.6, 0.25), (0.59999, 0), (0, 0)],
    "caixa": [(0, 1), (0.09999, 1), (0.1, 0.5), (0.2, 0.5), (0.20001, 0), (1, 0)],
    "inspecao": [(1, 1), (0.95, 1), (0.94999, 0.75), (0.9, 0.75), (0.89999, 0.5), (0.85, 0.5), (0.84999, 0.25),
                 (0.8, 0.25), (0.79999, 0)],
    "acidentes": [(0, 0.5), (0.00001, 0.25), (7.5, 0.25), (7.50001, 0), (30, 0)],
    "nr18": [(1, 0.5), (0.95, 0.5), (0.94999, 0.25), (0.85, 0.25), (0.84999, 0)],
    "entregas": [(1, 0.5), (0.9, 0.5), (0.89999, 0.25), (0.8, 0.25), (0.79999, 0)],
    "analise": [(3, 0.5), (2, 0.25), (1, 0), (0, 0)],
    "status": [(10, 0), (8, 0), (7.99, 1), (6, 1), (5.99999, 2), (0, 2)],
}
NOTA_INICIO = INICIO
STATUS_COD = {"estável": 0, "atenção": 1, "crítico": 2}


def pela_faixa(x: float, faixas) -> tuple[float, int]:
    """(pontos, índice da faixa): a primeira faixa que bate, de cima para baixo."""
    x = round(x, NOTA["arred"])
    for i, (op, lim, p) in enumerate(faixas):
        if op == "resto":
            return p, i
        if (op == ">=" and x >= lim) or (op == "<=" and x <= lim) or (op == "<" and x < lim) or (op == ">" and x > lim):
            return p, i
    raise ValueError("faixas sem resto")


def conferir_casos_limite(motor: bool) -> list[tuple]:
    erros = []
    for chave, casos in CASOS_LIMITE.items():
        faixas = NOTA[chave]
        for x, esperado in casos:
            p, _i = pela_faixa(x, faixas)
            if abs(p - esperado) > 1e-12:
                erros.append(("régua × dicionário", chave, x, p, esperado))
        if motor:
            q = "EVALUATE ROW ( " + ", ".join(
                f'"c{k}", VAR _x = {x!r} RETURN {dax_faixas("_x", faixas, recuo=0)}' for k, (x, _e) in enumerate(casos)) + " )"
            r = consultar(q)[0]
            for k, (x, esperado) in enumerate(casos):
                if difere(r[f"[c{k}]"], esperado, 1e-12):
                    erros.append(("régua × DAX gerada", chave, x, r[f"[c{k}]"], esperado))
    return erros


def _r(x):
    return None if x is None else round(x, NOTA["arred"])


def oraculo_nota(mes_auto: str) -> dict:
    """Roda pipeline/conferir_ficticios.py (lê as planilhas, as bases e o cronograma com openpyxl, sem o Power Query) e
    monta, de dados/_gabarito/nota_previa.csv, a nota por obra × mês, a carteira, as listas e a obra em foco."""
    subprocess.run([sys.executable, "-I", "-X", "utf8", str(RAIZ / "pipeline" / "conferir_ficticios.py")], check=True,
                   stdout=subprocess.DEVNULL)
    linhas = csv.DictReader(open(RAIZ / "dados" / "_gabarito" / "nota_previa.csv", encoding="utf-8-sig"), delimiter=";")
    obras = {}
    for l in linhas:
        if l["mes"] < NOTA_INICIO:
            continue
        o = {"obra": l["obra"], "mes": l["mes"], "tem_ac": True, "itens": {}}
        for it in NOTA_ITENS:
            x = f(l[f"x_{it['chave']}"])
            pts, i = pela_faixa(x, it["faixas"]) if x is not None else (None, None)
            o["itens"][it["cod"]] = {"x": _r(x), "pontos": pts, "possiveis": nota_maximo(it["cod"]) if pts is not None else None,
                                     "faixa": nota_rotulos(it["cod"])[i] if i is not None else None}
            if pts is not None and abs(pts - f(l[f"pts_{it['chave']}"])) > 1e-9:
                raise SystemExit(f"oráculo: pontos de {it['cod']} em {l['obra']} {l['mes']} não batem com a prévia")
        pts = [v["pontos"] for v in o["itens"].values()]
        o["faltando"] = sum(p is None for p in pts)
        o["completa"] = int(o["faltando"] == 0)
        o["pendente"] = 1 - o["completa"]
        o["possiveis"] = _r(sum(v["possiveis"] for v in o["itens"].values() if v["possiveis"] is not None))
        o["obtidos"] = _r(sum(p for p in pts if p is not None))
        o["perdidos"] = _r(o["possiveis"] - o["obtidos"])
        o["nota"] = o["obtidos"] if o["completa"] else None
        o["trava"] = int(l["trava"]) if o["completa"] else None
        o["status"] = STATUS_COD[l["status"]] if o["completa"] else None
        obras[f"{l['obra']}|{l['mes']}"] = o
    carteira = defaultdict(lambda: {"criticas": 0, "atencao": 0, "estaveis": 0, "pendentes": 0, "trava": 0})
    for o in obras.values():
        c = carteira[o["mes"]]
        c["criticas"] += o["status"] == 2
        c["atencao"] += o["status"] == 1
        c["estaveis"] += o["status"] == 0
        c["pendentes"] += o["pendente"] == 1
        c["trava"] += o["trava"] == 1
    no_mes = sorted((o for o in obras.values() if o["mes"] == mes_auto),
                    # como o TOPN/CONCATENATEX da DAX: perdidos DESC com o vazio no fim, nota ASC (pendente = 99), nome
                    key=lambda o: (o["perdidos"] is None, -(o["perdidos"] or 0),
                                   o["nota"] if o["nota"] is not None else 99, o["obra"]))
    listas = {"criticas": [o["obra"] for o in no_mes if o["status"] == 2],
              "atencao": [o["obra"] for o in no_mes if o["status"] == 1],
              "estaveis": [o["obra"] for o in no_mes if o["status"] == 0],
              "pendentes": [o["obra"] for o in no_mes if o["pendente"] == 1],
              "todas": [o["obra"] for o in no_mes]}
    return {"mes_auto": mes_auto, "obras": obras, "carteira": dict(carteira), "listas": listas,
            "foco": no_mes[0]["obra"] if no_mes else None}


CAMPOS_NOTA = [  # (alias, medida, chave do oráculo, tolerância; None = texto)
    ("poss", "Nota · pontos possíveis", "possiveis", 1e-9), ("obt", "Nota · pontos obtidos", "obtidos", 1e-9),
    ("perd", "Nota · pontos perdidos", "perdidos", 1e-9), ("falt", "Nota · itens faltando", "faltando", 0),
    ("comp", "Nota · completa", "completa", 0), ("nota", "Nota · nota final", "nota", 1e-9),
    ("trv", "Nota · trava", "trava", 0), ("st", "Nota · status", "status", 0), ("pend", "Nota · pendente", "pendente", 0),
] + [c for i, (cod, (pts, poss, x, fx)) in enumerate(NOTA_ITEM_MEDIDAS.items()) for c in (
    (f"x{i}", x, ("item", cod, "x"), 1e-6), (f"p{i}", pts, ("item", cod, "pontos"), 1e-9),
    (f"ps{i}", poss, ("item", cod, "possiveis"), 1e-9), (f"fx{i}", fx, ("item", cod, "faixa"), None))]


def _valor(o: dict, chave):
    return o["itens"][chave[1]][chave[2]] if isinstance(chave, tuple) else o[chave]


def _difere_nota(vm, vo, tol) -> bool:
    if tol is None:
        return (vm or None) != (vo or None)
    return difere(vm, vo, tol)


def conferir_nota(mes_auto: str) -> tuple[list, int, dict]:
    novas, n = list(conferir_casos_limite(motor=True)), sum(len(c) * 2 for c in CASOS_LIMITE.values())
    ora = oraculo_nota(mes_auto)
    # obra × mês
    vistos = set()
    for ini in range(0, len(CAMPOS_NOTA), 18):
        lote = CAMPOS_NOTA[ini:ini + 18]
        q = "EVALUATE SUMMARIZECOLUMNS ( dObra[Obra], dMes[Mes], " + ", ".join(
            f'"{al}", [{m}]' for al, m, *_ in lote) + " )"
        for l in consultar(q):
            chave = f'{l["dObra[Obra]"]}|{l["dMes[Mes]"][:10]}'
            o = ora["obras"].get(chave)
            if o is None:
                if any(l.get(f"[{al}]") not in (None, "") for al, *_ in lote):
                    novas.append((chave, "linha no motor sem obra × mês no oráculo", "", ""))
                continue
            vistos.add(chave)
            for al, m, k, tol in lote:
                n += 1
                if _difere_nota(l.get(f"[{al}]"), _valor(o, k), tol):
                    novas.append((chave, m, l.get(f"[{al}]"), _valor(o, k)))
    novas += [(k, "obra × mês do oráculo sem linha no motor", "", "") for k in ora["obras"] if k not in vistos]
    # por item × mês (pontos e possíveis somados pelas obras; obras que perderam pontos)
    for l in consultar('EVALUATE SUMMARIZECOLUMNS ( dItemNota[Item], dMes[Mes], "p", [Nota · item · pontos], '
                       '"poss", [Nota · item · possíveis], "perd", [Nota · item · perdidos], '
                       '"n", [Nota · item · obras que perderam pontos] )'):
        item, mes = l["dItemNota[Item]"], l["dMes[Mes]"][:10]
        os_ = [o["itens"][item] for o in ora["obras"].values() if o["mes"] == mes and o["itens"][item]["pontos"] is not None]
        p = _r(sum(v["pontos"] for v in os_)) if os_ else None
        poss = _r(sum(v["possiveis"] for v in os_)) if os_ else None
        perd = _r(poss - p) if os_ else None
        nper = sum(1 for v in os_ if _r(v["possiveis"] - v["pontos"]) > 0) or None
        for al, vo, tol in (("p", p, 1e-9), ("poss", poss, 1e-9), ("perd", perd, 1e-9), ("n", nper, 0)):
            n += 1
            if difere(l[f"[{al}]"], vo, tol):
                novas.append((f"item {item} {mes}", al, l[f"[{al}]"], vo))
    # carteira mês a mês
    for l in consultar('EVALUATE SUMMARIZECOLUMNS ( dMes[Mes], "c", [Nota · carteira · obras críticas], '
                       '"a", [Nota · carteira · obras em atenção], "e", [Nota · carteira · obras estáveis], '
                       '"p", [Nota · carteira · obras pendentes], "t", [Nota · carteira · obras na trava] )'):
        mes = l["dMes[Mes]"][:10]
        c = ora["carteira"].get(mes, {})
        for al, k in (("c", "criticas"), ("a", "atencao"), ("e", "estaveis"), ("p", "pendentes"), ("t", "trava")):
            n += 1
            if difere(l[f"[{al}]"], c.get(k) or None, 0):
                novas.append((f"carteira {mes}", k, l[f"[{al}]"], c.get(k)))
    # mês de referência: contagens · ref, listas, obra em foco e as contas · foco
    r = consultar("""EVALUATE ROW ( "mes", [Mês de referência],
 "c", [Nota · carteira · obras críticas · ref], "a", [Nota · carteira · obras em atenção · ref],
 "e", [Nota · carteira · obras estáveis · ref], "p", [Nota · carteira · obras pendentes · ref],
 "lc", [Nota · recorte · obras críticas (lista)], "la", [Nota · recorte · obras em atenção (lista)],
 "le", [Nota · recorte · obras estáveis (lista)], "lp", [Nota · recorte · obras pendentes (lista)],
 "lt", [Nota · recorte · obras por pontos perdidos (lista)], "foco", [Nota · obra em foco],
 "fnota", [Nota · nota final · ranking · foco], "fperd", [Nota · pontos perdidos · ranking · foco],
 "fst", [Nota · status · ranking · foco], "fpend", [Nota · pendente · ranking · foco] )""")[0]
    c = ora["carteira"].get(mes_auto, {})
    fo = ora["obras"].get(f'{ora["foco"]}|{mes_auto}', {})
    for al, vo, tol in (("c", c.get("criticas") or None, 0), ("a", c.get("atencao") or None, 0),
                        ("e", c.get("estaveis") or None, 0), ("p", c.get("pendentes") or None, 0),
                        ("lc", "|".join(ora["listas"]["criticas"]), None), ("la", "|".join(ora["listas"]["atencao"]), None),
                        ("le", "|".join(ora["listas"]["estaveis"]), None), ("lp", "|".join(ora["listas"]["pendentes"]), None),
                        ("lt", "|".join(ora["listas"]["todas"]), None), ("foco", ora["foco"], None),
                        ("fnota", fo.get("nota"), 1e-9), ("fperd", fo.get("perdidos"), 1e-9), ("fst", fo.get("status"), 0),
                        ("fpend", fo.get("pendente"), 0)):
        n += 1
        if _difere_nota(r[f"[{al}]"], vo, tol):
            novas.append((f"referência {mes_auto}", al, r[f"[{al}]"], vo))
    # a ordem compartilhada (T1 · Obras · posição, lida também pela T4)
    pos = sorted(((l["[pos]"], l["dObra[Obra]"]) for l in consultar(
        'EVALUATE SUMMARIZECOLUMNS ( dObra[Obra], "pos", [T1 · Obras · posição] )') if l["[pos]"] is not None))
    n += 2
    if [o for _p, o in pos] != ora["listas"]["todas"] or [p for p, _o in pos] != list(range(1, len(pos) + 1)):
        novas.append((f"referência {mes_auto}", "T1 · Obras · posição", pos, ora["listas"]["todas"]))
    # entrou / saiu / abriu em crítico, mês a mês (T1: leitura, tooltip do mês, série da piora). Entrou e saiu comparam
    # com a nota completa do mês anterior; abriu = a primeira nota completa da obra já crítica. Ordem: mais pontos
    # perdidos primeiro.
    meses = sorted({o["mes"] for o in ora["obras"].values()})
    def _ant(m):
        a, mm = int(m[:4]), int(m[5:7]) - 1
        return f"{a - (mm == 0)}-{12 if mm == 0 else mm:02d}-01"
    def _ordem(os_):
        return "|".join(o["obra"] for o in sorted(os_, key=lambda o: (-(o["perdidos"] or 0), 99 if o["nota"] is None
                                                                       else o["nota"], o["obra"])))
    motor = {l["dMes[Mes]"][:10]: l for l in consultar(
        'EVALUATE SUMMARIZECOLUMNS ( dMes[Mes], "e", [T1 · Leitura · obras que entraram em crítico (lista)], '
        '"s", [T1 · Leitura · obras que saíram de crítico (lista)], '
        '"ab", [T1 · Leitura · obras que abriram em crítico (lista)] )')}
    for mes in meses:
        no_mes = [o for o in ora["obras"].values() if o["mes"] == mes]
        ant = {o["obra"]: o for o in ora["obras"].values() if o["mes"] == _ant(mes)}
        ja = {o["obra"] for o in ora["obras"].values() if o["mes"] < mes and o["pendente"] == 0}
        st_ant = lambda o: ant[o["obra"]]["status"] if o["obra"] in ant else None  # noqa: E731
        esp = {"e": _ordem([o for o in no_mes if o["status"] == 2 and st_ant(o) is not None and st_ant(o) < 2]),
               "s": _ordem([o for o in no_mes if st_ant(o) == 2 and o["status"] is not None and o["status"] < 2]),
               "ab": _ordem([o for o in no_mes if o["status"] == 2 and o["obra"] not in ja])}
        for al, vo in esp.items():
            n += 1
            vm = (motor.get(mes) or {}).get(f"[{al}]")
            if (vm or "") != vo:
                novas.append((f"entrou/saiu/abriu {mes}", al, vm, vo))
    # contas de uma obra com DUAS obras no contexto: vazias (não somam). As duas primeiras obras do mês automático.
    duas = sorted(o["obra"] for o in ora["obras"].values() if o["mes"] == mes_auto)[:2]
    if len(duas) == 2:
        r = consultar(f"""EVALUATE CALCULATETABLE (
    ROW ( "nota", [Nota · nota final], "st", [Nota · status], "pend", [Nota · pendente], "comp", [Nota · completa],
          "trv", [Nota · trava], "x", [Nota · X custo], "fx", [Nota · faixa atingida · caixa] ),
    TREATAS ( {{ "{duas[0]}", "{duas[1]}" }}, dObra[Obra] ), dMes[Mes] = DATE ( {mes_auto[:4]}, {int(mes_auto[5:7])}, 1 )
)""")[0]
        for al, vm in r.items():
            n += 1
            if vm not in (None, ""):
                novas.append((f"duas obras {duas} {mes_auto}", al, vm, None))
    return novas, n, ora


def tabela_nota(ora: dict) -> str:
    """Tabela do oráculo (obra × mês: pontos por item, nota, trava, status) em Markdown, para o relatório."""
    cab = "| Obra | Mês | " + " | ".join(it["curto"] for it in NOTA_ITENS) + " | Nota | Trava | Status |"
    linhas = [cab, "|" + "---|" * (len(NOTA_ITENS) + 5)]
    st = {0: "estável", 1: "atenção", 2: "crítico", None: "pendente"}
    fmt = lambda v: "—" if v is None else f"{v:.2f}".replace(".", ",")  # noqa: E731
    for o in sorted(ora["obras"].values(), key=lambda o: (o["obra"], o["mes"])):
        linhas.append("| " + " | ".join([o["obra"], o["mes"][:7]] + [fmt(o["itens"][it["cod"]]["pontos"]) for it in NOTA_ITENS]
                                        + [fmt(o["nota"]), "sim" if o["trava"] else "", st[o["status"]]]) + " |")
    return "\n".join(linhas) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sem-extrair", action="store_true")
    ap.add_argument("--so-nota", action="store_true", help="só a Nota da obra (pula as contas que não são régua)")
    a = ap.parse_args()
    fato = SAIDA / "fato_analise_critica.csv" if a.sem_extrair else extrair()
    ora = oraculo(fato)
    (SAIDA / "oraculo.json").write_text(json.dumps(ora, ensure_ascii=False, indent=1), encoding="utf-8")

    novas_nota, n_nota, ora_nota = conferir_nota(ora["mes_auto"])
    (SAIDA / "oraculo_nota.json").write_text(json.dumps(ora_nota, ensure_ascii=False, indent=1), encoding="utf-8")
    (SAIDA / "oraculo_nota.md").write_text(tabela_nota(ora_nota), encoding="utf-8")
    print(f"Nota da obra · {len(ora_nota['obras'])} obra×mês · {n_nota} valores · {len(novas_nota)} diferenças · "
          f"foco {ora_nota['foco']} · carteira {ora['mes_auto']}: {ora_nota['carteira'].get(ora['mes_auto'])}")
    for d in novas_nota:
        print("   NOTA:", " | ".join(str(x) for x in d))
    if a.so_nota:
        return 1 if novas_nota else 0

    novas, aceitas, n = [], [], 0
    q = "EVALUATE SUMMARIZECOLUMNS ( dObra[Obra], dMes[Mes], " + ", ".join(
        f'"{al}", [{m}]' for al, m, *_ in CAMPOS) + " )"
    vistos = set()
    for l in consultar(q):
        chave = f'{l["dObra[Obra]"]}|{l["dMes[Mes]"][:10]}'
        o = ora["obras"].get(chave)
        if o is None:
            novas.append((chave, "linha no motor sem aba na planilha", "", ""))
            continue
        vistos.add(chave)
        for al, m, k, tol, aceita in CAMPOS:
            n += 1
            if difere(l.get(f"[{al}]"), o[k], tol):
                alvo = aceitas if (aceita and not o["quadradinho_fecha"]) else novas
                alvo.append((chave, m, l.get(f"[{al}]"), o[k]))
    novas += [(k, "aba na planilha sem linha no motor", "", "") for k in ora["obras"] if k not in vistos]

    mes = ora["mes_auto"]
    car = ora["carteira"][mes]
    r = consultar(f"""DEFINE VAR _m = [Mês de referência]
EVALUATE ROW ( "mes", _m, "res", [Resultado da obra · ref], "ati", [Ativos não consumidos · ref],
 "orc", CALCULATE ( [Orçamento], dMes[Mes] = _m ) )""")[0]
    if r["[mes]"][:10] != mes:
        novas.append(("carteira", "mês automático", r["[mes]"][:10], mes))
    for al, k, tol, aceita in (("res", "resultado", 0.01, False), ("orc", "orcamento", 0.01, False),
                               ("ati", "ativos", 0.01, True)):
        n += 1
        if difere(r[f"[{al}]"], car[k], tol):
            (aceitas if (aceita and not car["ativos_aceito"]) else novas).append((f"carteira {mes}", k, r[f"[{al}]"], car[k]))
    for l in consultar('EVALUATE SUMMARIZECOLUMNS ( dMes[Mes], "rs", [Resultado · variação no mês], '
                       '"pp", [Resultado · variação p.p.] )'):
        m = l["dMes[Mes]"][:10]
        c = ora["carteira"].get(m)
        if not c:
            continue
        # o extrator grava o resultado em centavos: a soma de várias obras acumula até ± R$ 0,005 por obra
        for al, k, tol in (("rs", "var_rs", 0.05), ("pp", "var_pp", 1e-7)):
            n += 1
            if difere(l[f"[{al}]"], c[k], tol):
                novas.append((f"carteira {m}", f"variação {k}", l[f"[{al}]"], c[k]))

    print(f"mês automático {mes} · {len(vistos)} obra×mês · {n} valores · {len(aceitas)} diferenças aceitas · "
          f"{len(novas)} diferenças novas")
    for d in aceitas:
        print("   aceita (quadradinho ≠ soma das tabelas):", " | ".join(str(x) for x in d))
    for d in novas:
        print("   NOVA:", " | ".join(str(x) for x in d))
    return 1 if (novas or novas_nota) else 0


if __name__ == "__main__":
    sys.exit(main())

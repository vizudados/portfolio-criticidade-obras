#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""render_deneb — renderiza um visual Deneb do PBIP fora do Power BI, com os dados reais do motor do Desktop aberto:
lê o visual.json (spec, campos e caixa), monta a consulta SUMMARIZECOLUMNS dos campos (colunas agrupam, medidas viram
colunas nomeadas com o apelido), consulta o motor (dax.py) e chama render_vega.mjs na caixa exata do visual.

    python -X utf8 pbi/scripts/render_deneb.py T1 T1_Dia_Grafico [--filtro "dCalendario[Data] = DATE(2026,8,12)"]
                                               [--escala 1] [--quadro-inicial] [--sinal nome=valor]
Saída: pbi/qa/deneb/<visual>.png (+ .json com o relatório do render).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from dax import executar as consultar_bruto  # noqa: E402  (resultado bruto do dax.ps1: colunas, tipos, linhas)

RAIZ = AQUI.parent
REPORT = RAIZ / "pbip" / "VP.Report" / "definition" / "pages"
QA = RAIZ / "qa" / "deneb"


def literal(prop):
    return prop["expr"]["Literal"]["Value"]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("pagina")
    ap.add_argument("visual")
    ap.add_argument("--filtro", action="append", default=[], help="filtro DAX extra (CALCULATETABLE)")
    ap.add_argument("--escala", default="1")
    ap.add_argument("--quadro-inicial", action="store_true")
    ap.add_argument("--sinal", action="append", default=[])
    ap.add_argument("--sufixo", default="")
    ap.add_argument("--spec", help="usa este spec (pbi/deneb/...) em vez do gravado no visual.json")
    ap.add_argument("--caixas", action="store_true", help="grava <saida>.caixas.json (tinta dos textos e caixas das marcas)")
    ap.add_argument("--fundo", default=None, help="cor de fundo do render (padrão do render_vega: #FFFFFF; 'transparente')")
    a = ap.parse_args()
    r = renderizar(a.pagina, a.visual, escala=a.escala, filtros=a.filtro, quadro_inicial=a.quadro_inicial,
                   sinais=a.sinal, sufixo=a.sufixo, spec=a.spec, caixas=a.caixas, fundo=a.fundo)
    print(r["stdout"])
    if r["codigo"]:
        print(r["stderr"])
    print(f"linhas do dataset: {r['linhas']}")
    return r["codigo"]


def renderizar(pagina, visual, escala="1", filtros=(), quadro_inicial=False, sinais=(), sufixo="", spec=None,
               caixas=False, fundo=None, doc=None, define: str = "") -> dict:
    """Consulta os campos do visual no motor e renderiza o spec na caixa exata. Devolve caminhos e o código de saída.
    `doc` = visual.json já montado (declaração de paginas/*.py) no lugar do gravado no PBIR. `define` = bloco DEFINE
    MEASURE (testar_dax.define) para medir com as medidas do disco antes de regravar o modelo."""
    vj = doc or json.loads((REPORT / pagina / "visuals" / visual / "visual.json").read_text(encoding="utf-8"))
    pos = vj["position"]
    v = vj["visual"]
    spec_txt = literal(v["objects"]["vega"][0]["properties"]["jsonSpec"])
    spec_txt = spec_txt[1:-1].replace("''", "'")
    if spec:
        spec_txt = (RAIZ / spec).read_text(encoding="utf-8")
    projs = v["query"]["queryState"]["dataset"]["projections"]
    colunas, medidas, campos = [], [], []
    for p in projs:
        alias = p["nativeQueryRef"]
        f = p["field"]
        if "Column" in f:
            t, c = f["Column"]["Expression"]["SourceRef"]["Entity"], f["Column"]["Property"]
            colunas.append(f"'{t}'[{c}]")
            campos.append(f"{alias}={t}[{c}]")
        else:
            m = f["Measure"]["Property"]
            medidas.append(f'"{alias}", [{m}]')
    corpo = "SUMMARIZECOLUMNS ( " + ", ".join(colunas + medidas) + " )"
    for filtro in filtros:
        corpo = f"CALCULATETABLE ( {corpo}, {filtro} )"
    # grupo de cálculo do seletor do drawer, como nos visuais (filtro de relatório Filtros[Item] = "Aplicar")
    corpo = f'CALCULATETABLE ( {corpo}, Filtros[Item] = "Aplicar" )'
    # ordem das linhas igual à do Desktop: sem sortDefinition, o Power BI entrega o dataset ordenado pelas colunas
    # agrupadoras na ordem da projeção (crescente). Sem isso o render local herda a ordem livre do SUMMARIZECOLUMNS e
    # esconde spec que depende da 1ª linha (T4 · Tipo: a nota Contábil sumiu no Desktop, 02/10)
    ordem = []
    for s_ in v["query"].get("sortDefinition", {}).get("sort", []):
        f = s_["field"]
        dir_ = " DESC" if str(s_.get("direction", "")).lower().startswith("desc") else ""
        if "Column" in f:
            ordem.append(f"'{f['Column']['Expression']['SourceRef']['Entity']}'[{f['Column']['Property']}]{dir_}")
        else:
            ref = next((p["nativeQueryRef"] for p in projs if p["field"] == f), None)
            if ref:
                ordem.append(f"[{ref}]{dir_}")
    if not ordem:
        ordem = list(colunas)
    if ordem:
        corpo += " ORDER BY " + ", ".join(ordem)
    consulta = define + "EVALUATE " + corpo
    QA.mkdir(parents=True, exist_ok=True)
    nome = visual + (("-" + sufixo) if sufixo else "")
    dados = QA / f"{nome}.dados.json"
    arq_spec = QA / f"{nome}.spec.json"
    res = consultar_bruto(consulta)
    dados.write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
    arq_spec.write_text(spec_txt, encoding="utf-8")
    cmd = ["node", str(AQUI / "render_vega.mjs"), "--spec", str(arq_spec), "--dados", str(dados),
           "--caixa", f"{pos['width']}x{pos['height']}", "--saida", str(QA / nome), "--escala", str(escala),
           "--campos", ",".join(campos), "--cultura", "pt-BR"]
    if quadro_inicial:
        cmd.append("--quadro-inicial")
    if caixas:
        cmd.append("--caixas")
    if fundo:
        cmd += ["--fundo", fundo]
    for s_ in sinais:
        cmd += ["--sinal", s_]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    linhas = len(res["resultados"][0]["linhas"]) if res.get("resultados") else 0
    return {"codigo": r.returncode, "stdout": (r.stdout or "").strip(), "stderr": (r.stderr or "").strip()[-3000:],
            "linhas": linhas, "png": QA / f"{nome}.png", "caixas": QA / f"{nome}.caixas.json", "posicao": pos}


if __name__ == "__main__":
    sys.exit(main())

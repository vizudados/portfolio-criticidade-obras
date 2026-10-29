#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""smoke_medidas — avalia TODAS as medidas do modelo no motor do Desktop do projeto (L039): uma consulta por medida,
no total da carteira; com --obras, também por obra × mês. Erro de motor numa medida = defeito; para tudo.

    python -X utf8 pbi/scripts/smoke_medidas.py [--obras] [--filtro texto]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from dax import ErroDax, consultar  # noqa: E402

TMDL = AQUI.parent / "pbip" / "CO.SemanticModel" / "definition" / "tables" / "_Medidas.tmdl"


def medidas() -> list[str]:
    nomes = []
    for l in TMDL.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\tmeasure\s+('(?:[^']|'')*'|[^\s=]+)\s*=", l)
        if m:
            n = m.group(1)
            nomes.append(n[1:-1].replace("''", "'") if n.startswith("'") else n)
    return nomes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--obras", action="store_true")
    ap.add_argument("--filtro", default="")
    a = ap.parse_args()
    nomes = [n for n in medidas() if a.filtro.lower() in n.lower()]
    erros = []
    for i in range(0, len(nomes), 40):
        lote = nomes[i:i + 40]
        q = "EVALUATE ROW ( " + ", ".join(f'"m{k}", [{n.replace("]", "]]")}]' for k, n in enumerate(lote)) + " )"
        try:
            consultar(q)
        except ErroDax:
            for n in lote:
                try:
                    consultar(f'EVALUATE ROW ( "m", [{n.replace("]", "]]")}] )')
                except ErroDax as e:
                    erros.append(f"{n}: {str(e).splitlines()[0][:220]}")
    if a.obras and not erros:
        for i in range(0, len(nomes), 25):
            lote = nomes[i:i + 25]
            q = ("EVALUATE SUMMARIZECOLUMNS ( dObra[Obra], dMes[Mes], "
                 + ", ".join(f'"m{k}", [{n.replace("]", "]]")}]' for k, n in enumerate(lote)) + " )")
            try:
                consultar(q)
            except ErroDax as e:
                erros.append(f"lote {i}–{i + len(lote)} por obra × mês: {str(e).splitlines()[0][:220]}")
    print(f"{len(nomes)} medidas avaliadas · {len(erros)} com erro")
    for e in erros:
        print("  [ERRO]", e)
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""testar_dax — roda uma consulta no motor do Desktop aberto com as medidas de .dax do disco injetadas como DEFINE
MEASURE (nomes reais: sobrescrevem as do modelo só nesta consulta). Serve para conferir contas novas ou alteradas sem
fechar o Desktop nem regravar o TMDL. Somente leitura.

    python -X utf8 pbi/scripts/testar_dax.py --dax "pbi/dax/T1/**/*.dax" --consulta "EVALUATE ROW(\\"x\\", [Minha conta])"
    python -X utf8 pbi/scripts/testar_dax.py --alteradas 30 --consulta-arquivo q.dax   # .dax mudados nos últimos 30 min
"""
from __future__ import annotations

import argparse
import glob
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import dax_para_tmdl as dpt  # noqa: E402
from dax import ErroDax, consultar  # noqa: E402

RAIZ = AQUI.parent


def define(arquivos: list[Path]) -> str:
    blocos = []
    for p in arquivos:
        m = dpt.ler(p)
        corpo = "\n".join("        " + l if l.strip() else "" for l in m["linhas"])
        nome = m["nome"].replace("]", "]]")
        blocos.append(f"    MEASURE _Medidas[{nome}] =\n{corpo}")
    return "DEFINE\n" + "\n".join(blocos) + "\n" if blocos else ""


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--dax", action="append", default=[], help="glob de .dax (relativo à pasta do projeto)")
    ap.add_argument("--alteradas", type=float, help="inclui os .dax de pbi/dax mudados nos últimos N minutos")
    ap.add_argument("--consulta")
    ap.add_argument("--consulta-arquivo")
    ap.add_argument("--max", type=int, default=60, help="linhas impressas (padrão 60)")
    a = ap.parse_args()
    arqs: list[Path] = []
    for g in a.dax:
        arqs += [Path(x) for x in glob.glob(str(RAIZ.parent / g), recursive=True)]
    if a.alteradas:
        limite = time.time() - a.alteradas * 60
        arqs += [p for p in (RAIZ / "dax").rglob("*.dax") if "_modelo" not in p.parts and p.stat().st_mtime >= limite]
    arqs = sorted(set(arqs))
    consulta = a.consulta or Path(a.consulta_arquivo).read_text(encoding="utf-8")
    texto = define(arqs) + consulta
    print(f"{len(arqs)} medidas injetadas")
    try:
        linhas = consultar(texto)
    except ErroDax as e:
        print("ERRO DO MOTOR:", e.mensagem)
        if e.linha:
            ls = texto.split("\n")
            ini = max(0, e.linha - 4)
            for i in range(ini, min(len(ls), e.linha + 3)):
                print(f"{i + 1:5}: {ls[i]}")
        return 2
    for l in linhas[:a.max]:
        print(l)
    return 0


if __name__ == "__main__":
    sys.exit(main())

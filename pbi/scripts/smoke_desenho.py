#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""smoke_desenho — L039: avalia LEN() de cada medida de desenho (HTML, ALT, CSS, JS, Vega, rótulo) no motor do Desktop
aberto, uma por consulta, para nenhum visual abrir em erro. Mostra o tamanho (limite de 32.760 caracteres só importa com
grupo de cálculo, L048; o painel não tem grupo de cálculo, mas o número fica registrado).

    python -X utf8 pbi/scripts/smoke_desenho.py [--filtro T1]
Código de saída: 0 todas avaliam, 1 alguma em erro.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from dax import ErroDax, consultar  # noqa: E402
import lint_conta_desenho as lint  # noqa: E402

DAX_DIR = AQUI.parent / "dax"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--filtro", default="")
    a = ap.parse_args()
    re_desenho = re.compile(lint.DESENHO_PADRAO)
    medidas = [m for m in lint.ler_dax(DAX_DIR) if re_desenho.search(m.nome) and a.filtro in m.nome]
    erros = 0
    for m in sorted(medidas, key=lambda x: x.nome):
        try:
            # no total da carteira e o maior texto entre as obras × meses (o filtro "Filtros[Item]" era de outro projeto)
            r = consultar(f'EVALUATE ROW ( "n", LEN ( [{m.nome}] ), "max", MAXX ( SUMMARIZECOLUMNS ( dObra[Obra], '
                          f'dMes[Mes], "t", LEN ( [{m.nome}] ) ), [t] ) )')
            n, mx = r[0].get("[n]"), r[0].get("[max]")
            print(f"ok   {n!s:>7} {mx!s:>7}  {m.nome}")
        except ErroDax as e:
            erros += 1
            print(f"ERRO {m.nome}: {e.mensagem[:300]}")
    print(f"\n{len(medidas)} medidas de desenho · {erros} em erro")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""contas_lib — grava medidas de CONTA (um .dax por medida, cabeçalho @pasta/@formato/@descricao/@oraculo) a partir de
listas declaradas nos scripts contas_t<n>.py. Regrava sempre; não apaga nada fora da lista."""
from __future__ import annotations

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DAX = RAIZ / "dax"


def gravar(subpasta: str, pasta: str, contas: list[tuple], gerado: str) -> int:
    """contas = [(nome, formato, descrição, oráculo, expressão)]. subpasta relativa a pbi/dax."""
    destino = DAX / subpasta
    destino.mkdir(parents=True, exist_ok=True)
    for nome, fmt, desc, orac, expr in contas:
        cab = ["/*", f"@pasta: {pasta}", f"@formato: {fmt}", f"@descricao: {desc}", f"@oraculo: {orac}",
               f"@gerado: {gerado}", "*/"]
        (destino / f"{nome}.dax").write_text("\n".join(cab) + "\n" + expr.strip() + "\n", encoding="utf-8")
    return len(contas)

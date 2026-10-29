#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""inventario_svg — lista a árvore de camadas nomeadas de um export SVG do Figma (spec/casca/_fonte/*.svg).

O Figma grava o nome da camada no atributo id com os bytes UTF-8 escritos como entidades (&#194;&#183; = "·"); este
script desfaz isso. Serve para classificar cada camada em estática (casca) ou dinâmica (visual do Power BI).

    python -X utf8 pbi/scripts/inventario_svg.py T1 [--profundidade 4]
"""
from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FONTE = RAIZ / "spec" / "casca" / "_fonte"
NS = "http://www.w3.org/2000/svg"


def nome(el) -> str | None:
    i = el.get("id")
    if not i:
        return None
    try:
        return i.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return i


def local(tag) -> str:
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def andar(el, prof: int, limite: int, saida: list) -> None:
    for f in el:
        n = nome(f)
        if local(f.tag) in ("defs",):
            continue
        if n is not None:
            saida.append(("  " * prof) + f"{local(f.tag)} {n}")
            if prof + 1 < limite:
                andar(f, prof + 1, limite, saida)
        else:
            andar(f, prof, limite, saida)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("tela")
    ap.add_argument("--profundidade", type=int, default=4)
    a = ap.parse_args()
    arv = ET.parse(FONTE / f"{a.tela}.svg")
    saida: list[str] = []
    andar(arv.getroot(), 0, a.profundidade, saida)
    print("\n".join(saida))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""render_tela — renderiza os Deneb de uma tela a partir da DECLARAÇÃO (scripts/paginas/t<n>.py) e das medidas do disco
(DEFINE de base/, comum/ e da pasta da tela), com os dados do Desktop aberto, sem regravar modelo nem relatório.

    python -X utf8 pbi/scripts/render_tela.py T2 [T2_Mapa_Lojas ...] [--sem "Tooltip loja · bairro"] [--filtro DAX]
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from render_deneb import renderizar  # noqa: E402
from testar_dax import define  # noqa: E402

DAX = AQUI.parent / "dax"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("tela")
    ap.add_argument("visuais", nargs="*")
    ap.add_argument("--sem", action="append", default=[])
    ap.add_argument("--filtro", action="append", default=[])
    ap.add_argument("--sufixo", default="")
    a = ap.parse_args()
    spec = importlib.util.spec_from_file_location("decl", AQUI / "paginas" / f"{a.tela.lower()}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    docs = {d["name"]: d for d in mod.visuais() if "Deneb" in str(d.get("visual", {}).get("visualType", "")) or
            "deneb" in str(d.get("visual", {}).get("visualType", "")).lower()}
    arqs = sorted(p for d in (DAX / "base", DAX / "comum", DAX / a.tela) for p in d.rglob("*.dax")
                  if not any(s in p.name for s in a.sem))
    df = define(arqs)
    rc = 0
    for nome in a.visuais or list(docs):
        r = renderizar(a.tela, nome, escala="1", doc=docs[nome], define=df, filtros=a.filtro, sufixo=a.sufixo)
        print(nome, r["codigo"], r["linhas"], r["png"], r["stderr"][-600:])
        rc = rc or r["codigo"]
    return rc


if __name__ == "__main__":
    sys.exit(main())

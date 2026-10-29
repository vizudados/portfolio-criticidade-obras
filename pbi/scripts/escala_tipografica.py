#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""escala_tipografica — levanta a escala tipográfica de cada tela a partir das medições do medir_espacos.py
(<pasta>/tN.caixas.json): por visual, os pares peso × tamanho do texto vivo, e as distâncias título → subtítulo →
conteúdo de cada cartão (o título e o subtítulo fixos vêm da casca; o resto, dos visuais).

    python -X utf8 pbi/scripts/escala_tipografica.py pbi/qa/refino/antes

Somente leitura. Imprime uma tabela por tela e um resumo de pares peso × tamanho entre as telas.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    pasta = Path(sys.argv[1])
    geral = defaultdict(Counter)
    for n in range(1, 7):
        arq = pasta / f"t{n}.caixas.json"
        if not arq.exists():
            continue
        caixas = json.loads(arq.read_text(encoding="utf-8"))
        textos = [c for c in caixas if c.get("tipo") == "texto" and c.get("origem") != "casca" and c["x1"] > 312]
        por_visual = defaultdict(Counter)
        for c in textos:
            fonte = c.get("fonte", "?")
            peso, tam = (fonte.split() + ["?"])[:2]
            tam = tam.replace("px", "")
            try:
                tam = f"{float(tam):g}"
            except ValueError:
                pass
            chave = f"{'SB' if peso in ('600', 'bold', '700') else 'R '}{tam}"
            por_visual[c["origem"]][chave] += 1
            geral[chave][f"T{n}"] += 1
        print(f"\n== T{n}")
        for v, cont in sorted(por_visual.items()):
            print(f"  {v:28} " + "  ".join(f"{k}×{q}" for k, q in sorted(cont.items(), key=lambda x: -float(x[0][2:] or 0))))
    print("\n== pares peso × tamanho (SB = Semibold, R = Regular) por tela")
    for k in sorted(geral, key=lambda x: (-float(x[2:] or 0), x)):
        print(f"  {k:6} " + "  ".join(f"{t}:{q}" for t, q in sorted(geral[k].items())))
    print("\n== distâncias por cartão (tinta): topo do cartão → título · título → subtítulo · subtítulo → conteúdo")
    for n in range(1, 7):
        arq = pasta / f"t{n}.caixas.json"
        if arq.exists():
            distancias(n, json.loads(arq.read_text(encoding="utf-8")))
    return 0


def distancias(n: int, caixas: list[dict]) -> None:
    cards = {}
    for c in caixas:
        if c.get("origem") == "casca" and c.get("tipo") == "moldura" and str(c.get("texto", "")).startswith("Card"):
            cards.setdefault(c["texto"], c)
    for nome, m in cards.items():
        dentro = [c for c in caixas if c is not m and c.get("tipo") in ("texto", "forma", "casca")
                  and c["x1"] >= m["x1"] - 0.5 and c["x2"] <= m["x2"] + 0.5 and c["y1"] >= m["y1"] - 0.5
                  and c["y2"] <= m["y2"] + 0.5 and c.get("tipo") != "moldura"]
        tit = [c for c in dentro if c.get("origem") == "casca" and str(c.get("texto", "")).startswith("Título")]
        tit += [c for c in dentro if str(c.get("origem", "")).endswith("_Titulo") and c["tipo"] == "texto"]
        if not tit:
            continue
        t = min(tit, key=lambda c: c["y1"])
        sub = [c for c in dentro if (c.get("origem") == "casca" and str(c.get("texto", "")).startswith("Subtítulo"))
               or (c["tipo"] == "texto" and (str(c.get("origem", "")).endswith("_Subtitulo")
                                            or c.get("marca") == "subtitulo")
                   or (str(c.get("origem", "")).endswith("_Titulo") and c["tipo"] == "texto" and c.get("px") == 17))]
        sub = [c for c in sub if c["y1"] > t["y1"] + 5]
        s = min(sub, key=lambda c: c["y1"]) if sub else None
        base = s or t
        resto = [c for c in dentro if c["y1"] > base["y2"] + 1 and c is not s and c.get("origem") != "casca"
                 and not str(c.get("texto", "")).startswith(("Botão", "Divisor"))]
        cont = min(resto, key=lambda c: c["y1"]) if resto else None
        print(f"  T{n} {nome[:44]:44} topo→título {t['y1'] - m['y1']:5.1f} · título→sub "
              f"{(s['y1'] - t['y2']) if s else float('nan'):5.1f} · sub→conteúdo "
              f"{(cont['y1'] - base['y2']) if cont else float('nan'):5.1f}"
              + (f"  ({str(cont.get('texto') or cont.get('marca') or cont.get('el'))[:30]})" if cont else ""))


if __name__ == "__main__":
    sys.exit(main())

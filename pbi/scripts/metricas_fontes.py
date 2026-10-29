#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""metricas_fontes — tabela das larguras de caractere das fontes que o tour mede (pbi/spec/tour/metricas-fontes.json).

Por quê (retorno da sessão local, 28/10/2026): o tour_lib media o texto com os arquivos de fonte da máquina. Onde há
Segoe UI (a máquina local) o selo "Passo N de M" e as quebras estimadas saíam com a largura real; onde não há (a nuvem),
com a largura média de 0,56 em. A montagem de cada lado punha os botões do tour num x diferente (591 × 611) e as duas
brigavam a cada entrega. Com a tabela no repositório, o tour_lib mede igual nos dois lados, sem depender da fonte
instalada.

A tabela guarda, por fonte, o avanço de cada caractere em milésimos de em (PIL a 1000 px, sem kerning: a soma dos
avanços, o mesmo número em qualquer máquina). Conjunto: ASCII imprimível, Latin-1, a tipografia de uso corrente e todo
caractere que aparece em pbi/spec/tour/passos.json. Cada execução mede as fontes que acha e mantém na tabela as que não
acha (a Segoe UI só existe no Windows: rode na máquina local uma vez e suba o .json; a Barlow vem de assets/fontes).

    python -X utf8 pbi/scripts/metricas_fontes.py            # mede e grava
    python -X utf8 pbi/scripts/metricas_fontes.py --conferir # sai 1 se a tabela estiver velha para as fontes daqui
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent                     # pbi/
ARQ = RAIZ / "spec" / "tour" / "metricas-fontes.json"
PASSOS = RAIZ / "spec" / "tour" / "passos.json"
FONTE_ARQ = {
    "segoe": r"C:\Windows\Fonts\segoeui.ttf",
    "segoe_sb": r"C:\Windows\Fonts\seguisb.ttf",
    "barlow": str(RAIZ / "assets" / "fontes" / "barlow-600.woff"),
}
EXTRAS = "–—‘’‚“”„…·•→←↑↓≤≥±×÷€§ªº°½¼¾−✓"
TAMANHO = 1000


def conjunto() -> str:
    cs = {chr(c) for c in range(32, 127)} | {chr(c) for c in range(160, 256)} | set(EXTRAS)
    if PASSOS.is_file():
        cs |= set(PASSOS.read_text(encoding="utf-8"))
    return "".join(sorted(c for c in cs if c.isprintable() or c == " "))


def medir_fonte(arq: str, chars: str) -> dict[str, float] | None:
    from PIL import ImageFont
    try:
        f = ImageFont.truetype(arq, TAMANHO)
    except OSError:
        return None
    return {c: round(f.getlength(c), 2) for c in chars}


def tabela() -> tuple[dict, list[str]]:
    atual = json.loads(ARQ.read_text(encoding="utf-8")) if ARQ.is_file() else {}
    fontes = dict(atual.get("fontes", {}))
    chars, medidas = conjunto(), []
    for nome, arq in FONTE_ARQ.items():
        t = medir_fonte(arq, chars)
        if t is not None:
            fontes[nome] = t
            medidas.append(nome)
    return {"_leia": "avanço de cada caractere em milésimos de em (PIL a 1000 px, sem kerning); "
                     "gerado por pbi/scripts/metricas_fontes.py",
            "fontes": {k: fontes[k] for k in sorted(fontes)}}, medidas


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--conferir", action="store_true")
    a = ap.parse_args()
    nova, medidas = tabela()
    texto = json.dumps(nova, ensure_ascii=False, indent=1, sort_keys=False) + "\n"
    if a.conferir:
        velho = ARQ.read_text(encoding="utf-8") if ARQ.is_file() else ""
        ok = velho == texto
        print(("ok" if ok else "VELHA") + f" · medidas aqui: {', '.join(medidas) or 'nenhuma'}")
        return 0 if ok else 1
    ARQ.write_text(texto, encoding="utf-8")
    faltam = sorted(set(FONTE_ARQ) - set(nova["fontes"]))
    print(f"{ARQ.relative_to(RAIZ.parent)} · medidas aqui: {', '.join(medidas) or 'nenhuma'}"
          + (f" · sem tabela: {', '.join(faltam)} (rode onde a fonte existe)" if faltam else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())

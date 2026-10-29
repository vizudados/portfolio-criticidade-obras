#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gerar_casca — papéis de parede das telas do painel Criticidade de Obras e análise crítica.

Fonte: exports SVG (download_assets do MCP do Figma, texto em contorno) dos frames 'Casca · T1'…'Casca · T4' da página
'PBI · Casca · Criticidade de Obras' (298:685) do arquivo FjBWDk5odF9HaZ2pwhGosl, gravados em pbi/spec/casca/_fonte/T<n>.svg.
A limpeza (L047: só sidebar, prancheta, título e pergunta, botões do cabeçalho, contêineres e título dos painéis, "?",
rodapé de fonte) é feita no próprio Figma. Depois do export, as fontes v2 foram editadas à mão com o texto regerado em
contorno na mesma fonte e posição (Barlow 600, Segoe UI 400/700): títulos sem ADO (T1, T2), item 05 · Canteiro nas
dez cascas, T3 "PPC mês a mês", T4 "Obras no mês" e a T5/D5, feitas na grade da T4 (28/10/2026). Aqui:
  · sai o retângulo #F5F5F5 que o export põe atrás de tudo;
  · as artes do Magnific embutidas (PNG grandes) são reduzidas à metade e quantizadas — o <image> mantém width/height,
    então a geometria não muda; só cai o peso do arquivo;
  · recusa SVG com <text> (o export precisa vir com texto em contorno).

    python -X utf8 pbi/scripts/gerar_casca.py
"""
from __future__ import annotations

import base64
import io
import re
import sys
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parents[1]
# v2 (07/10/2026): cascas do redesenho, página Figma "PBI · Casca v2 · Criticidade de Obras" (406:685); a v1 ficou em
# spec/casca/_fonte e num zip em pbi/_backups
FONTE = RAIZ / "spec" / "casca" / "_fonte_v2"
DESTINO = RAIZ / "assets" / "wallpapers"
FUNDO_EXPORT = re.compile(r'<rect width="1920" height="1080" fill="#F5F5F5"/>\s*')
IMAGEM = re.compile(r'(xlink:href="data:image/png;base64,)([A-Za-z0-9+/=]+)(")')


def reduzir(m: re.Match) -> str:
    img = Image.open(io.BytesIO(base64.b64decode(m.group(2)))).convert("RGBA")
    img = img.resize((max(1, img.width // 2), max(1, img.height // 2)), Image.LANCZOS)
    img = img.quantize(colors=48, method=Image.Quantize.FASTOCTREE)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return m.group(1) + base64.b64encode(buf.getvalue()).decode("ascii") + m.group(3)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    DESTINO.mkdir(parents=True, exist_ok=True)
    fontes = sorted(list(FONTE.glob("T*.svg")) + list(FONTE.glob("D*.svg")))   # T = tela, D = drawer
    if not fontes:
        print(f"[ERRO] nenhum T<n>.svg em {FONTE}")
        return 2
    for src in fontes:
        txt = src.read_text(encoding="utf-8")
        novo, k = FUNDO_EXPORT.subn("", txt, count=1)
        if k != 1:
            print(f"[ERRO] {src.name}: retângulo de fundo do export não encontrado")
            return 2
        if "<text" in novo:
            print(f"[ERRO] {src.name}: há <text> no SVG (o export precisa vir com texto em contorno)")
            return 2
        novo = IMAGEM.sub(reduzir, novo)
        destino = DESTINO / f"wp-{src.stem.lower()}.svg"
        destino.write_text(novo, encoding="utf-8")
        print(f"{destino.name}  {len(txt.encode('utf-8')) / 1024:,.0f} KB → {len(novo.encode('utf-8')) / 1024:,.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())

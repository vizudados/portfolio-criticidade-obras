#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""foto_medida — fotografa uma medida HTML como o visual HTML Content a desenharia: avalia a medida no Desktop aberto
(todas as medidas de pbi/dax injetadas por DEFINE, sem regravar o modelo), grava qa/medidas/<arquivo>.html no tamanho
do visual e tira o PNG no Edge headless (4 s de tempo virtual: animações no estado final). Somente leitura do modelo.

    python -X utf8 pbi/scripts/foto_medida.py "T4 · Cascata · HTML" 720 332 --saida t4-cascata
    python -X utf8 pbi/scripts/foto_medida.py "Drawer · HTML estado" 272 40 --fundo "#121316" \
        --filtro 'TREATAS ( { "Bairro › Tibiri" }, dFiltro[Caminho] )'
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from dax import consultar  # noqa: E402
from testar_dax import define  # noqa: E402

RAIZ = AQUI.parent
DAX = RAIZ / "dax"
SAIDA = RAIZ / "qa" / "medidas"
EDGE = os.environ.get("EDGE_EXE", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


def arquivos_dax(medida: str, telas: list[str], sem: list[str] = ()) -> list[Path]:
    """base/ e comum/ sempre; mais a pasta da tela da medida (T<n> · …) e as pedidas em --tela (as telas em obra de
    outro agente ficam de fora: uma medida inválida derruba a consulta inteira)."""
    pastas = [DAX / "base", DAX / "comum"]
    fora = {x for x in os.environ.get("FOTO_SEM_TELA", "").split(",") if x}
    for t in [d.name for d in DAX.iterdir() if d.is_dir() and d.name[:1] == "T" and d.name not in fora] + telas:
        pastas.append(DAX / t)
    return sorted(p for d in pastas if d.is_dir() for p in d.rglob("*.dax") if not any(s in p.name for s in sem))


def avaliar(medida: str, filtros: list[str], telas: list[str], sem: list[str] = (), extra: list[Path] = (),
            css: str | None = None) -> tuple[str, str]:
    filt = "".join(f", {f}" for f in filtros)
    linha_css = f', "c", [{css}]' if css else ""
    q = (define(arquivos_dax(medida, telas, sem) + list(extra))
         + f'EVALUATE CALCULATETABLE ( ROW ( "h", [{medida}]{linha_css} ){filt} )')
    linhas = consultar(q)
    if not linhas:
        return "", ""
    return (linhas[0].get("[h]") or ""), (linhas[0].get("[c]") or "")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("medida")
    ap.add_argument("largura", type=int)
    ap.add_argument("altura", type=int)
    ap.add_argument("--saida", help="nome do arquivo (sem extensão)")
    ap.add_argument("--filtro", action="append", default=[], help="filtro DAX extra do CALCULATETABLE")
    ap.add_argument("--fundo", default="#FFFFFF")
    ap.add_argument("--tela", action="append", default=[], help="pasta de tela extra a injetar (ex.: T1)")
    ap.add_argument("--sem", action="append", default=[], help="não injeta .dax cujo nome contém este trecho")
    ap.add_argument("--extra", action="append", default=[], type=Path, help=".dax extra a injetar (substitutos de teste)")
    ap.add_argument("--css", help="medida da folha de estilo do visual (propriedade stylesheet do HTML Content)")
    a = ap.parse_args()
    html, css = avaliar(a.medida, a.filtro, a.tela, a.sem, a.extra, a.css)
    if css:
        # a folha de estilo do visual entra antes do conteúdo; o conteúdo fica dentro de #htmlContent, como no visual
        html = f"<style>{css}</style><div id='htmlContent'><div class='htmlViewerEntry'>{html}</div></div>"
    print(f"LEN {len(html)}")
    SAIDA.mkdir(parents=True, exist_ok=True)
    nome = a.saida or "medida"
    # o HTML vai num iframe do tamanho exato do visual (position:fixed passa a valer para a caixa do visual, como no
    # Power BI; a janela do Edge headless tem largura mínima de ~500 px)
    interno = (f"<!doctype html><html><head><meta charset='utf-8'><style>html,body{{margin:0;background:{a.fundo}}}"
               f"</style></head><body>{html}</body></html>")
    srcdoc = interno.replace("&", "&amp;").replace('"', "&quot;")
    w, h = max(a.largura, 520), max(a.altura, 120)
    pagina = (f"<!doctype html><html><head><meta charset='utf-8'><style>html,body{{margin:0;background:#FFFFFF}}"
              f"iframe{{display:block;border:0;width:{a.largura}px;height:{a.altura}px}}</style></head><body>"
              f"<iframe srcdoc=\"{srcdoc}\"></iframe></body></html>")
    arq = SAIDA / f"{nome}.html"
    arq.write_text(pagina, encoding="utf-8")
    # Edge headless chamado direto (o mesmo comando do foto_html.sh): sem depender de bash no PATH, que não existe no
    # PowerShell e dava FileNotFoundError [WinError 2] no passo do PNG (Fase 3 da régua antiga, 14/10/2026)
    png = arq.with_suffix(".png")
    # apaga a foto anterior: se o Edge falhar, não sobra um PNG velho aceito como novo (auditoria da Fase 3, minor 5)
    png.unlink(missing_ok=True)
    perfil = Path(os.environ.get("TEMP", str(SAIDA))) / f"edge_foto_{os.getpid()}"
    try:
        r = subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--virtual-time-budget=9000",
                            f"--user-data-dir={perfil}", f"--window-size={w},{h}", f"--screenshot={png}",
                            arq.resolve().as_uri()], capture_output=True, text=True, timeout=180)
    except FileNotFoundError:
        print(f"Edge não encontrado em {EDGE}")
        return 2
    r = subprocess.CompletedProcess(r.args, 0 if png.is_file() else (r.returncode or 1), str(png) if png.is_file() else "",
                                    r.stderr)
    if r.returncode == 0 and png.is_file() and (w, h) != (a.largura, a.altura):
        try:
            from PIL import Image
            Image.open(png).crop((0, 0, a.largura, a.altura)).save(png)
        except ImportError:
            pass
    print(r.stdout.strip() or r.stderr.strip())
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())

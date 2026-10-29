# -*- coding: utf-8 -*-
"""medir_linhas_tour — mede no Edge quantas linhas ocupa cada texto que o tour_lib quebra (o navegador manda).

A quebra estimada pelo tour_lib (largura da fonte no PIL) erra por 1 a 2 px quando o texto quase enche a coluna: no
T4 passo 6 a dica cabia em 1 linha na conta e quebrou em 2 no navegador, encostando nos controles (08/10). Este script:

1. roda a geometria dos 32 passos registrando toda chamada a tour_lib.linhas() (texto, largura, fonte, px);
2. monta uma página com um bloco por chamada, com o mesmo CSS do tour (fontes embutidas, CSS base, CSS do tour, dentro
   de <div class='u tr'>), e mede no Edge headless (edge_cdp.mjs) a altura de cada bloco, depois de document.fonts.ready;
3. grava pbi/spec/tour/linhas-navegador.json (chave: fonte|px|largura|texto → linhas). O tour_lib usa esse número no
   lugar da estimativa;
4. repete até nenhuma chamada nova aparecer (o número de linhas muda a altura do balão e a busca pode pedir larguras novas).

    python -X utf8 pbi/scripts/medir_linhas_tour.py
"""
from __future__ import annotations

import html
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import contador as C  # noqa: E402
import desenho_comum as DC  # noqa: E402
import tour_lib as t  # noqa: E402

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
CDP = AQUI / "edge_cdp.mjs"
FAMILIA = {"segoe": ("'Segoe UI',system-ui,sans-serif", 400), "segoe_sb": ("'Segoe UI',system-ui,sans-serif", 600),
           "barlow": ("'Barlow U','Segoe UI',sans-serif", 600)}


def _registrar() -> list:
    t.REGISTRO_LINHAS = set()
    for tela in t.TELAS:
        passos = t.passos_da_tela(tela)
        for p in passos:
            t.geometria(tela, p, len(passos))
    itens = sorted(t.REGISTRO_LINHAS)
    t.REGISTRO_LINHAS = None
    return itens


def _pagina(itens: list) -> str:
    blocos = []
    for i, (texto, largura, fonte, px) in enumerate(itens):
        fam, peso = FAMILIA[fonte]
        lh = 2 * px
        blocos.append(f"<div id='m{i}' style=\"position:absolute;left:0;top:0;width:{largura}px;font-family:{fam};"
                      f"font-weight:{peso};font-size:{px}px;line-height:{lh}px;white-space:normal\">{html.escape(texto)}</div>")
    css = DC.css_fontes() + DC.CSS_BASE + C.css_texto() + t.CSS_TOUR
    script = ("<script>document.fonts.ready.then(function(){var r=[];var n=" + str(len(itens)) + ";"
              "for(var i=0;i<n;i++){var e=document.getElementById('m'+i);var lh=parseFloat(getComputedStyle(e).lineHeight);"
              "r.push(Math.round(e.getBoundingClientRect().height/lh));}"
              "document.getElementById('__medidas__').textContent=JSON.stringify(r);});</script>")
    return ("<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><style>" + css + "</style></head><body>"
            "<div class='u tr'>" + "".join(blocos) + "</div><pre id='__medidas__'></pre>" + script + "</body></html>")


def _medir(itens: list) -> list:
    pasta = Path(tempfile.mkdtemp(prefix="medir_linhas_"))
    try:
        arq = pasta / "linhas.html"
        arq.write_text(_pagina(itens), encoding="utf-8")
        cfg = {"edge": EDGE, "url": arq.as_uri(), "perfil": str(pasta / "perfil"), "janela_w": 1920, "janela_h": 1080,
               "escala": 1, "virtual_ms": 3000, "reduzir": False, "timeout_ms": 120000}
        r = subprocess.run(["node", str(CDP), json.dumps(cfg)], capture_output=True, text=True, timeout=200,
                           encoding="utf-8", errors="replace")
        saida = (r.stdout or "").strip()
        if not saida:
            raise SystemExit("medição vazia no Edge: " + (r.stderr or "")[-300:])
        medidos = json.loads(saida)
        if any(not isinstance(n, int) or n < 1 for n in medidos):
            raise SystemExit("medição inválida no Edge (linha sem número)")
        return medidos
    finally:
        shutil.rmtree(pasta, ignore_errors=True)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    arq = t.LINHAS_NAVEGADOR_ARQ
    cache = json.loads(arq.read_text(encoding="utf-8")) if arq.is_file() else {}
    for rodada in range(1, 5):
        itens = _registrar()
        novos = [it for it in itens if t.chave_linhas(*it) not in cache]
        print(f"rodada {rodada}: {len(itens)} chamadas, {len(novos)} sem medida")
        if not novos:
            break
        medidos = _medir(novos)
        difere = 0
        for (texto, largura, fonte, px), n in zip(novos, medidos):
            estimado = t.linhas_estimadas(texto, largura, fonte, px)
            if n != estimado:
                difere += 1
                print(f"  navegador {n} × estimativa {estimado}: {fonte} {px} px em {largura} px · {texto[:70]}")
            cache[t.chave_linhas(texto, largura, fonte, px)] = n
        print(f"  {len(novos)} medidas, {difere} diferentes da estimativa")
        arq.write_text(json.dumps(dict(sorted(cache.items())), ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                       newline="\n")
        t.linhas_navegador.cache_clear()
    print(f"gravado: {arq} ({len(cache)} medidas)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

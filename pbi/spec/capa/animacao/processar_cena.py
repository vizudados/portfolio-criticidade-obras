#!/usr/bin/env python
"""Um comando por cena larga (1920x640): PNG do Magnific -> SVG de traço + comparação + quadros.

Uso (sempre com python -I, de qualquer pasta que não seja magnific\\):
    python -I processar_cena.py "...\\pbi\\spec\\capa\\magnific\\cenario-1-obras.png" [--janela 5] [--escala 1]

Gera, com o nome da imagem (sem .png):
    pbi\\spec\\capa\\animacao\\<nome>.svg                (traços de baixo para cima, desenho em 3 s)
    pbi\\qa\\capa\\animacao\\<nome>-comparacao.png       (original em cima, vetor embaixo)
    pbi\\qa\\capa\\animacao\\<nome>-t150.png e -t300.png (quadros no meio e no fim do desenho)
e imprime traços, <path>, tamanho e quadros por segundo no Edge. --janela é só para a medição (5 s
nos takes, 8 s na cena final); --escala reproduz a escala do take na sequência (ex.: 0.93 no take 3).
Outros parâmetros do vetorizar_traco.py podem vir no fim (ex.: --tom 0 tira a hachura de tom).
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))           # só a pasta dos scripts (python -I não a põe no caminho)

import montar_preview  # noqa: E402
import vetorizar_traco  # noqa: E402

QA = AQUI.parents[2] / "qa" / "capa" / "animacao"

# preset das cenas largas (traço fino e denso, 1920x640); o cenário B usa os padrões do script.
# comp-min 3: some o pó de traços < 3 px, que pesava na animação sem mudar o desenho a 1:1.
PRESET_LARGO = ["--sigma", "0.6", "--comp-min", "3", "--rdp", "0.2", "--espinho-k", "1.2",
                "--espinho-c", "0.3", "--area-min", "1", "--furo-max", "0.5"]


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("png", type=Path)
    a.add_argument("--janela", type=float, default=5.0)
    a.add_argument("--escala", type=float, default=1.0)
    p, extra = a.parse_known_args(argv)
    png = p.png.resolve()
    nome = png.stem
    svg = AQUI / f"{nome}.svg"
    QA.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    with redirect_stdout(buf):
        vetorizar_traco.main([str(png), str(svg), "--calibrar", "--empilhar", "--sem-sobreposicao",
                              "--comparacao", str(QA / f"{nome}-comparacao.png")] + PRESET_LARGO + extra)
    info = json.loads(buf.getvalue())
    with tempfile.TemporaryDirectory() as tmp:
        html = Path(tmp) / f"{nome}.html"
        with redirect_stdout(io.StringIO()):
            fps = montar_preview.main([str(html), "--cena", f"{svg}:{p.janela:g}:{p.escala:g}", "--titulo", nome,
                                       "--medir",
                                       "--quadro", f"{QA / (nome + '-t150.png')}:0:1.5",
                                       "--quadro", f"{QA / (nome + '-t300.png')}:0:3"])
    m = info["metricas"]
    n_paths = svg.read_text(encoding="utf-8").count("<path")
    print(json.dumps({"cena": nome, "tracos": info["tracos"], "tracos_linha": info["tracos_linha"],
                      "tracos_hachura": info["tracos"] - info["tracos_linha"], "paths": n_paths,
                      "svg_kb": round(info["svg_bytes"] / 1024), "fps_edge": round(fps or 0, 1),
                      "tinta_nao_coberta_pct": m["faltando_pct"], "sobra_pct": m["sobrando_pct"],
                      "fator_espessura": info["fator_espessura"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()

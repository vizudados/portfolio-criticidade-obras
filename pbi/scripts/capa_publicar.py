#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""capa_publicar — mídias da capa do Criticidade de Obras no GitHub Pages do próprio repositório do portfólio
(vizudados/portfolio-criticidade-obras, ramo órfão capa-midia: o repositório segue privado, só esse ramo é servido).

Padrão do painel de referência ((publicação de outro projeto) nome publicado = arquivo + 12 hex do SHA-256,
README dizendo que são só mídias, index.html simples e assets/manifest.json. Só três mídias, nada além disso:

  - o filme  pbi/spec/capa/remotion/renders/capa-filme-2560x854-60fps.mp4 (Remotion + NVENC; ver remotion/README.md)
  - o pôster pbi/spec/capa/remotion/renders/capa-filme-poster.webp (a cena final desenhada)
  - a panorâmica da base, pbi/spec/capa/animacao/panoramica-base.svg LIMPA para <img> (sem as classes e tempos de
    animação, sem width/height; a mesma limpeza do ler_panoramica() do protótipo), gravada em
    pbi/spec/capa/publicacao/fonte/panoramica-base.svg

    python -I -X utf8 pbi/scripts/capa_publicar.py --montar     # monta a pasta do repositório (não publica)
    python -I -X utf8 pbi/scripts/capa_publicar.py --conferir   # GET com Range → 206, SHA servido = local, Content-Type
    python -I -X utf8 pbi/scripts/capa_publicar.py --url mp4    # imprime a URL publicada (mp4 | poster | pano)

A pasta pbi/spec/capa/publicacao/ fica fora do git do main: o conteúdo dela é o ramo órfão capa-midia, publicado à
mão (push só desse ramo; Pages em capa-midia /), com o aval do Alisson. Um repositório só (pedido dele, 28/10/2026).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import sys
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent                    # pbi/scripts
PBI = AQUI.parent
CAPA = PBI / "spec" / "capa"
REPO = CAPA / "publicacao" / "criticidade-obras-capa"             # pasta do repositório git
FONTE = CAPA / "publicacao" / "fonte"
BASE_URL = "https://vizudados.github.io/portfolio-criticidade-obras/"
ASSETS_URL = BASE_URL + "assets/"

MP4 = CAPA / "remotion" / "renders" / "capa-filme-2560x854-60fps.mp4"
POSTER = CAPA / "remotion" / "renders" / "capa-filme-poster.webp"
PANO_ORIGEM = CAPA / "animacao" / "panoramica-base.svg"
PANO = FONTE / "panoramica-base.svg"

TIPOS = {".mp4": "video/mp4", ".webp": "image/webp", ".svg": "image/svg+xml"}
ORIGEM = {
    "mp4": ("filme da capa em laço de 33 s: 5 takes e a cena final em traço de caneta desenhado de baixo para cima "
            "(cenas de Natal geradas por IA no Codex CLI, vetorizadas em traço localmente), quadros pelo Remotion "
            "4.0.539 (Chrome com a GPU) e codificação H.264 pela NVENC (h264_nvenc, p7, VBR CQ 30); 2560x854, 60 fps, "
            "1.980 quadros, yuv420p, mudo, faststart. Os números do painel entram por cima, no HTML; não estão no "
            "vídeo."),
    "poster": "pôster do filme: o último quadro (a cena final desenhada), 2560x854, WebP sem perda",
    "pano": ("panorâmica da base: horizonte de Natal em traço de caneta (gerado por IA no Codex CLI e vetorizado em "
             "traço), limpa para <img> (sem classes e tempos de animação); viewBox 1916x821, traço #0B0B0C"),
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def publicado(p: Path) -> str:
    return f"{p.stem}-{sha(p)[:12]}{p.suffix}"


def url(chave: str) -> str:
    return ASSETS_URL + publicado({"mp4": MP4, "poster": POSTER, "pano": PANO}[chave])


def limpar_panoramica() -> str:
    """O SVG de traço da panorâmica, sem o que só servia à animação (como ler_panoramica() do protótipo)."""
    svg = PANO_ORIGEM.read_text(encoding="utf-8")
    svg = re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", svg)
    svg = re.sub(r'\sdata-tempos="[^"]*"', "", svg)
    svg = re.sub(r'\s(?:data-ordem|class)="[^"]*"', "", svg)
    svg = re.sub(r'\spathLength="[^"]*"', "", svg)
    svg = re.sub(r'\s(?:width|height)="\d+"', "", svg[:300], count=2) + svg[300:]
    if 'xmlns="http://www.w3.org/2000/svg"' not in svg[:200] or "viewBox=" not in svg[:200]:
        raise SystemExit("panorâmica: cabeçalho do SVG inesperado")
    return svg.replace("<svg ", "<svg preserveAspectRatio=\"none\" ", 1)


README = """# Criticidade de Obras · mídias da capa

Ativos públicos da capa de um painel Power BI de acompanhamento de obras (visual HTML Content). O repositório guarda
**apenas as mídias da capa**: não há dado, texto, marca nem pessoas identificáveis nos arquivos. Os números do painel
são desenhados pelo próprio relatório, por cima do filme; nada aqui contém número de obra ou de empresa.

- `assets/capa-filme-2560x854-60fps-*.mp4`: filme em laço de 33 s, com cenas de obra em traço de caneta que se
  desenham de baixo para cima; 2560×854, 60 fps, H.264, mudo.
- `assets/capa-filme-poster-*.webp`: pôster do filme (a cena final desenhada).
- `assets/panoramica-base-*.svg`: ilustração vetorial de traço (horizonte de Natal com prédios em obra), usada em
  baixa opacidade na base da capa.
- `assets/manifest.json`: tamanho, SHA-256 e origem de cada arquivo.

Os cenários foram gerados por IA a partir de roteiro próprio, vetorizados em traço e animados localmente (Remotion).
O nome de cada arquivo leva os 12 primeiros dígitos do SHA-256 do conteúdo: um arquivo publicado nunca muda; uma
versão nova entra com outro nome. Servidos pelo GitHub Pages para que o `<video>` receba `Accept-Ranges` e respostas
`206`.

© Vizu Dados. Uso restrito ao painel a que pertencem.
"""

INDEX = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Criticidade de Obras · mídias da capa</title>
<meta name="viewport" content="width=device-width, initial-scale=1"><style>body{font-family:'Segoe UI',system-ui,sans-serif;
color:#0B0B0C;background:#F7F4EE;margin:48px;max-width:760px}a{color:#3B3B3F}li{margin:6px 0}small{color:#6B6B70}</style>
</head><body><h1>Criticidade de Obras · mídias da capa</h1><p>Ativos servidos pelo GitHub Pages para o visual HTML Content de um
painel Power BI. Ver <a href="assets/manifest.json">manifest.json</a>.</p><ul id="lista"></ul><small>Cenas de obra em traço
geradas por IA e animadas; sem dados, texto, marca ou pessoas identificáveis.</small><script>fetch('assets/manifest.json')
.then(r=>r.json()).then(m=>{const ul=document.getElementById('lista');m.arquivos.forEach(a=>{const li=document.createElement('li');
const l=document.createElement('a');l.href=a.file;l.textContent=a.file;li.appendChild(l);li.appendChild(document.createTextNode(
' · '+Math.round(a.bytes/1024)+' KB'));ul.appendChild(li);});}).catch(()=>{});</script></body></html>
"""


def montar() -> dict:
    FONTE.mkdir(parents=True, exist_ok=True)
    texto = limpar_panoramica()
    if not PANO.is_file() or PANO.read_text(encoding="utf-8") != texto:
        PANO.write_text(texto, encoding="utf-8", newline="\n")
    destino = REPO / "assets"
    destino.mkdir(parents=True, exist_ok=True)
    arquivos = []
    for chave, p in (("mp4", MP4), ("poster", POSTER), ("pano", PANO)):
        nome = publicado(p)
        alvo = destino / nome
        if not alvo.is_file() or sha(alvo) != sha(p):
            shutil.copyfile(p, alvo)
        arquivos.append({"file": f"assets/{nome}", "bytes": p.stat().st_size, "sha256": sha(p),
                         "content_type": TIPOS[p.suffix], "origem": ORIGEM[chave]})
    manifesto = {"projeto": "criticidade-obras-capa", "gerado_em": dt.datetime.now().isoformat(timespec="seconds"),
                 "base_url": BASE_URL, "arquivos": arquivos}
    anterior = destino / "manifest.json"
    if anterior.is_file():
        velho = json.loads(anterior.read_text(encoding="utf-8"))
        if velho.get("arquivos") == arquivos:
            manifesto["gerado_em"] = velho.get("gerado_em", manifesto["gerado_em"])
    (destino / "manifest.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=1) + "\n",
                                           encoding="utf-8", newline="\n")
    (REPO / "README.md").write_text(README, encoding="utf-8", newline="\n")
    (REPO / "index.html").write_text(INDEX, encoding="utf-8", newline="\n")
    (REPO / ".nojekyll").write_text("", encoding="utf-8")
    sobras = [x.name for x in destino.iterdir() if x.name != "manifest.json"
              and x.name not in {a["file"].split("/", 1)[1] for a in arquivos}]
    for a in arquivos:
        print(f"  {a['file']}  {a['bytes']:>9,} B  {a['sha256'][:12]}  {a['content_type']}".replace(",", "."))
    if sobras:
        print("  [aviso] arquivos fora do manifesto em assets/:", sobras)
    return manifesto


def _get(u: str, faixa: str | None = None) -> tuple[int, dict, bytes]:
    req = urllib.request.Request(u, headers={"User-Agent": "vizu-capa-conferir/1.0", "Cache-Control": "no-cache",
                                             **({"Range": faixa} if faixa else {})})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.status, {k.lower(): v for k, v in r.headers.items()}, r.read()


def conferir() -> int:
    """GET com Range → 206 (e Content-Range), GET inteiro → SHA servido = local e Content-Type certo."""
    falhas = 0
    saida = []
    for chave, p in (("mp4", MP4), ("poster", POSTER), ("pano", PANO)):
        u = url(chave)
        try:
            st, cab, corpo = _get(u, "bytes=0-1023")
            st2, cab2, tudo = _get(u)
        except Exception as e:  # noqa: BLE001 - relatar e seguir para o próximo
            print(f"  FALHA {chave}: {u} → {e}")
            falhas += 1
            continue
        tam = p.stat().st_size
        ok_206 = st == 206 and len(corpo) == 1024 and cab.get("content-range", "").startswith("bytes 0-1023/")
        ok_sha = hashlib.sha256(tudo).hexdigest() == sha(p) and len(tudo) == tam
        tipo = cab2.get("content-type", "")
        ok_tipo = tipo.split(";")[0].strip() == TIPOS[p.suffix]
        linha = {"chave": chave, "url": u, "range_status": st, "content_range": cab.get("content-range"),
                 "accept_ranges": cab2.get("accept-ranges"), "status": st2, "content_type": tipo,
                 "bytes_servidos": len(tudo), "sha256_servido": hashlib.sha256(tudo).hexdigest(),
                 "sha256_local": sha(p), "cache_control": cab2.get("cache-control"),
                 "ok": ok_206 and ok_sha and ok_tipo}
        saida.append(linha)
        falhas += 0 if linha["ok"] else 1
        print(f"  {'ok   ' if linha['ok'] else 'FALHA'} {chave:<6} Range → {st} ({cab.get('content-range')}) · "
              f"SHA {'=' if ok_sha else '≠'} local · {tipo} · {u}")
    rel = PBI / "qa" / "capa" / "pbip" / "publicacao-conferencia.json"
    rel.parent.mkdir(parents=True, exist_ok=True)
    rel.write_text(json.dumps({"quando": dt.datetime.now().isoformat(timespec="seconds"), "arquivos": saida},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"conferência em {rel} · {falhas} falha(s)")
    return 1 if falhas else 0


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--montar", action="store_true")
    ap.add_argument("--conferir", action="store_true")
    ap.add_argument("--url", choices=("mp4", "poster", "pano"))
    a = ap.parse_args(argv)
    if a.url:
        print(url(a.url))
        return 0
    if a.montar:
        montar()
    if a.conferir:
        return conferir()
    if not (a.montar or a.conferir):
        ap.error("diga --montar, --conferir ou --url")
    return 0


if __name__ == "__main__":
    sys.exit(main())

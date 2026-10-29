#!/usr/bin/env python
"""Codifica o filme da capa pela placa de vídeo (NVENC) a partir dos quadros sem perda do Remotion, e grava o pôster.

    npx remotion render CapaFilme renders/quadros --sequence --image-format=png --gl=angle \\
        --image-sequence-pattern="quadro_[frame].[ext]"          # 1.980 PNG de 2560×854 (Chrome na GPU, ANGLE)
    python -I codificar_mp4.py [--cq 21] [--medir]                # MP4 H.264 pela h264_nvenc + pôster WebP

O Remotion no Windows não codifica pela GPU (a aceleração de hardware dele é só VideoToolbox, no macOS); por isso o
render sai em PNG e o ffmpeg codifica com a h264_nvenc: preset p7, tune hq, VBR por qualidade constante (--cq),
quadros B, AQ espacial e temporal, BT.709 em faixa de TV, yuv420p, faststart, sem áudio. Os quadros-chave caem só
nas viradas de cena (0/5/10/15/20/25 s), onde o quadro é papel em branco: dentro das cenas paradas não há quadro-chave
e o desenho não "pulsa".

Saídas em renders/: capa-filme-2560x854-60fps.mp4 e capa-filme-poster.webp (o último quadro, a cena final desenhada,
sem perda). --medir imprime o PSNR do MP4 contra os PNG (média e o pior quadro).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RENDERS = AQUI / "renders"
QUADROS = RENDERS / "quadros"
MP4 = RENDERS / "capa-filme-2560x854-60fps.mp4"
POSTER = RENDERS / "capa-filme-poster.webp"
FPS, TOTAL = 60, 33 * 60
CENAS_S = (0, 5, 10, 15, 20, 25)                 # viradas de cena = únicos quadros-chave
CQ = 30                                         # 8,4 MB, PSNR médio 42 dB (pior quadro 38,8) contra os PNG


def padrao() -> str:
    arqs = sorted(QUADROS.glob("quadro_*.png"))
    if len(arqs) != TOTAL:
        raise SystemExit(f"{QUADROS}: {len(arqs)} quadros (esperava {TOTAL})")
    m = re.match(r"quadro_(\d+)\.png$", arqs[0].name)
    if not m or int(m.group(1)) != 0:
        raise SystemExit(f"primeiro quadro inesperado: {arqs[0].name}")
    return str(QUADROS / f"quadro_%0{len(m.group(1))}d.png")


def codificar(cq: int) -> None:
    ff = shutil.which("ffmpeg") or "ffmpeg"
    subprocess.run([
        ff, "-v", "error", "-y", "-framerate", str(FPS), "-i", padrao(),
        "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
        "-c:v", "h264_nvenc", "-preset", "p7", "-tune", "hq", "-rc", "vbr", "-cq", str(cq), "-b:v", "0",
        "-profile:v", "high", "-bf", "3", "-b_ref_mode", "middle", "-spatial-aq", "1", "-temporal-aq", "1",
        "-rc-lookahead", "32", "-g", str(TOTAL), "-forced-idr", "1",
        "-force_key_frames", ",".join(str(s) for s in CENAS_S),
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
        "-movflags", "+faststart", "-an", str(MP4)], check=True)


def poster() -> None:
    from PIL import Image
    ultimo = sorted(QUADROS.glob("quadro_*.png"))[-1]
    Image.open(ultimo).convert("RGB").save(POSTER, lossless=True, method=6)
    print(f"pôster: {ultimo.name} -> {POSTER.name} ({POSTER.stat().st_size / 1e3:.0f} KB)")


def medir() -> dict:
    ff = shutil.which("ffmpeg") or "ffmpeg"
    r = subprocess.run([ff, "-hide_banner", "-i", str(MP4), "-framerate", str(FPS), "-i", padrao(),
                        "-lavfi", "[1:v]scale=out_color_matrix=bt709:out_range=tv,format=yuv420p[ref];"
                                  "[0:v][ref]psnr=stats_file=-", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    vals = [float(x) for x in re.findall(r"psnr_avg:([\d.]+|inf)", r.stdout) if x != "inf"]
    media = re.search(r"PSNR y:[\d.inf]+ u:[\d.inf]+ v:[\d.inf]+ average:([\d.inf]+)", r.stderr)
    return {"psnr_medio_db": float(media.group(1)) if media else None,
            "psnr_pior_quadro_db": round(min(vals), 2) if vals else None, "quadros": len(vals)}


def info() -> dict:
    fp = shutil.which("ffprobe") or "ffprobe"
    r = subprocess.run([fp, "-v", "error", "-show_entries",
                        "format=duration,size:stream=codec_name,profile,level,width,height,pix_fmt,r_frame_rate,nb_frames",
                        "-of", "json", str(MP4)], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def main(argv=None) -> None:
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--cq", type=int, default=CQ)
    a.add_argument("--medir", action="store_true")
    p = a.parse_args(argv)
    codificar(p.cq)
    poster()
    print(f"{MP4.name}: {MP4.stat().st_size / 1e6:.2f} MB · cq {p.cq}")
    print(json.dumps(info(), ensure_ascii=False))
    if p.medir:
        print(json.dumps(medir(), ensure_ascii=False))


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""poses_busto — gera o busto (corte na cintura) das poses (P1 a P11) da narradora do tour (Lia de obra), sem tocar nos originais.

Entrada: assets/personagem/poses/P<n>-*.png (corpo inteiro, PNG com alfa).
Saída:   assets/personagem/poses/busto/P<n>-*.png (mesmo nome; largura toda, do topo até a cintura).

Regra da cintura: a partir de 40 % da altura da figura, a primeira linha em que os pixels grafite da calça
(máximo do RGB < 110 e máximo − mínimo < 22: cinza escuro sem cor, o que separa do cabelo castanho-escuro e da botina
marrom) passam de LIMIAR_CALCA dos pixels opacos da faixa central (centro do capacete ± 150 px). O corte fica
MARGEM_CORTE px acima dessa linha, para a calça não aparecer. Lia (28/10/2026): a calça começa em y 893 a 908 do quadro
de 1308 × 1590 (0,54 da altura de pé).

    python -X utf8 pbi/scripts/poses_busto.py            # grava as 11 versões (busto/, lido só para saber se a pose existe)
    python -X utf8 pbi/scripts/poses_busto.py --info     # só mostra a linha de corte de cada pose
    python -X utf8 pbi/scripts/poses_busto.py --narrador # recorte do narrador (v5): corpo inteiro até a fração de cada pose

O narrador (balão do tour, v5) usa o recorte do corpo inteiro em assets/personagem/poses/narrador/: topo da cabeça no
topo da imagem, corte na fração NARRADOR_FRAC da altura da figura (meio do peito), sem cortar os gestos.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from PIL import Image

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent                      # raiz do repositório
POSES = RAIZ / "assets" / "personagem" / "poses"
BUSTO = POSES / "busto"
MARGEM_CORTE = 4                               # px acima da primeira linha de calça (pedido: 2 a 4)
INICIO_FRAC = 0.40                             # a busca começa em 40 % da altura da figura
LIMIAR_CALCA = 0.25                            # a calça "aparece" quando é 25 % dos pixels opacos da faixa central
FAIXA_MEIA = 150                               # meia largura da faixa central (px do quadro), em volta do capacete
NARRADOR = POSES / "narrador"
# Fração da altura da figura (caixa do alfa, que inclui a mão erguida da P7 e da P8) em que cai o corte da narradora.
# Lia de obra (28/10/2026), medida no quadro de 1308 × 1590: de pé ela vai do topo do capacete (y 136 a 139) à sola
# (y 1550), 1413 px; queixo em y 450 a 470, ombros em ~525, logo VD em ~612, primeira faixa refletiva em ~740, calça em
# ~900. Meio do peito: y 690 (logo inteiro, acima da faixa refletiva) para P1, P2, P3, P5, P9 e P10 (mão erguida ou
# braço estendido acima do corte: a mão da P1 desce até 723 só no cotovelo; os braços da P2/P3 até 612; o punho da P5
# até ~665); a P7 e a P8 cortam no mesmo y 690, mas a caixa delas começa na ponta do dedo (y 40 e 79), daí 0,43 e 0,415.
# P4 desce a 830 (palmas abertas ao lado da cintura até ~815); P6 a 787 (prendedor, dedo em ~717 e o terço de cima da
# prancheta); P11 a 801 (caneta em ~627, a prancheta e a mão que a segura até ~800).
NARRADOR_FRAC = {1: 0.39, 2: 0.39, 3: 0.39, 4: 0.49, 5: 0.39, 6: 0.46, 7: 0.43, 8: 0.415, 9: 0.39, 10: 0.39,
                 11: 0.47}


def caixa_figura(alfa: Image.Image) -> tuple[int, int, int, int]:
    """Caixa das linhas e colunas com figura de verdade (ignora pixels soltos de borda)."""
    w, h = alfa.size
    px = alfa.load()
    colunas = [x for x in range(w) if sum(1 for y in range(0, h, 4) if px[x, y] > 128) >= 3]
    linhas = [y for y in range(h) if sum(1 for x in range(0, w, 4) if px[x, y] > 128) >= 3]
    return colunas[0], linhas[0], colunas[-1] + 1, linhas[-1] + 1


def centro_capacete(im: Image.Image) -> int:
    """x do centro do capacete: a média das colunas com pixel branco sem cor (mínimo do RGB > 150, máximo − mínimo < 20)
    no terço de cima da figura. A camisa creme (#E9E0CF, máximo − mínimo 26) fica de fora; sem capacete, o meio da caixa."""
    import numpy as np
    a = np.asarray(im.convert("RGBA")).astype(int)
    alfa = a[..., 3] >= 128
    ys = np.nonzero(alfa.any(axis=1))[0]
    topo = int(ys[0] + (ys[-1] - ys[0]) // 3)
    rgb = a[:topo, :, :3]
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    branco = alfa[:topo] & (mn > 150) & (mx - mn < 20)
    cols = np.nonzero(branco)[1]
    if cols.size < 200:
        xs = np.nonzero(alfa.any(axis=0))[0]
        return int((xs[0] + xs[-1]) // 2)
    return int(round(cols.mean()))


def linha_da_cintura(im: Image.Image) -> tuple[int, int, int, int]:
    """(linha de corte, y0 da figura, y1 da figura, largura da faixa central analisada)."""
    alfa = im.getchannel("A")
    x0, y0, x1, y1 = caixa_figura(alfa)
    altura = y1 - y0
    centro = centro_capacete(im)
    faixa_x0, faixa_x1 = max(x0, centro - FAIXA_MEIA), min(x1, centro + FAIXA_MEIA)
    largura_faixa = faixa_x1 - faixa_x0
    px = im.load()
    inicio = y0 + int(altura * INICIO_FRAC)
    for y in range(inicio, y1):
        opacos = grafite = 0
        for x in range(faixa_x0, faixa_x1, 2):
            r, g, b, a = px[x, y]
            if a > 128:
                opacos += 1
                if max(r, g, b) < 110 and max(r, g, b) - min(r, g, b) < 22:
                    grafite += 1
        if opacos and grafite / opacos >= LIMIAR_CALCA:
            return y - MARGEM_CORTE, y0, y1, largura_faixa
    raise RuntimeError("linha da calça não encontrada")


def gerar(arquivo: Path, somente_info: bool) -> tuple[int, int, int, int]:
    im = Image.open(arquivo).convert("RGBA")
    corte, y0, y1, _ = linha_da_cintura(im)
    if not somente_info:
        BUSTO.mkdir(parents=True, exist_ok=True)
        busto = im.crop((0, 0, im.size[0], corte))
        busto.save(BUSTO / arquivo.name, "PNG", optimize=True)
    return corte, y0, y1, im.size[1]


def numero_pose(arquivo: Path) -> int:
    """Número da pose pelo nome do arquivo (P1-…, P11-…)."""
    return int(re.match(r"^P(\d+)-", arquivo.name).group(1))


def arquivos_poses() -> list:
    """As poses de corpo inteiro (P1…P11-*.png), em ordem de número."""
    return sorted((a for a in POSES.glob("P*-*.png") if re.match(r"^P\d+-", a.name)), key=numero_pose)


def gerar_narrador(arquivo: Path, somente_info: bool) -> tuple[int, int, int, int]:
    """Recorte do narrador: da caixa do alfa (topo da cabeça até NARRADOR_FRAC da altura), toda a largura da figura."""
    im = Image.open(arquivo).convert("RGBA")
    x0, y0, x1, y1 = im.getchannel("A").getbbox()
    n = numero_pose(arquivo)
    corte = y0 + round(NARRADOR_FRAC[n] * (y1 - y0))
    if not somente_info:
        NARRADOR.mkdir(parents=True, exist_ok=True)
        im.crop((x0, y0, x1, corte)).save(NARRADOR / arquivo.name, "PNG", optimize=True)
    return corte, y0, y1, x1 - x0


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--info", action="store_true")
    ap.add_argument("--narrador", action="store_true", help="recorte do narrador (corpo inteiro até o peito)")
    a = ap.parse_args(argv)
    arquivos = arquivos_poses()
    if not arquivos:
        print("nenhuma pose em", POSES)
        return 2
    if a.narrador:
        for arq in arquivos:
            corte, y0, y1, largura = gerar_narrador(arq, a.info)
            print(f"{arq.name}: narrador até y={corte} (altura {corte - y0} de {y1 - y0}, {NARRADOR_FRAC[numero_pose(arq)]:.2f}); "
                  f"largura {largura} px")
        return 0
    for arq in arquivos:
        corte, y0, y1, h = gerar(arq, a.info)
        pct = (corte - y0) / (y1 - y0) * 100
        print(f"{arq.name}: figura {y0}..{y1} (altura {y1 - y0}); corte na cintura em y={corte} "
              f"({pct:.0f} % da figura); busto {corte} px de altura")
    return 0


if __name__ == "__main__":
    sys.exit(main())

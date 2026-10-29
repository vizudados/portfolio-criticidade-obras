# -*- coding: utf-8 -*-
"""tour_lib — tour guiado por passos do painel Criticidade de Obras, v3 (brief pbi/spec/tour/brief-tour.md, §2.2 a §3): cabeçalho, corpo branco e palco no rodapé; card grande com palco embaixo ou faixa lateral.

Lê pbi/spec/tour/passos.json (somente leitura) e gera:
- por tela e passo: a medida de DESENHO 'T<n> · Tour · Passo NN · HTML' em pbi/dax/T<n>/Tour/ (texto estático: véu com
  recorte, anel, cantoneiras com curva, cota, card nos layouts "lado a lado", "empilhado" ou "grande", personagem e
  controles desenhados). Não lê medida de conta; só lê as medidas de pose;
- por pose: a medida 'Comum · Tour · Pose Pn · HTML' em pbi/dax/comum/Desenho/, só para as poses que algum passo
  referencia (a imagem PNG em base64, uma vez só);
- a folha de estilo 'Comum · Tour · CSS' (lê [Comum · CSS base]).

Geometria: o card, o layout e o personagem do passos.json têm prioridade quando o Figma gravar os campos 'card',
'layout' e 'personagem'. Sem eles, a regra do brief §3 escolhe lado e layout. Altura do card: pelo conteúdo, medida com
as larguras de caractere da Segoe UI e da Barlow e 6 % de folga; o HTML não corta texto. As larguras vêm da tabela
pbi/spec/tour/metricas-fontes.json (metricas_fontes.py), não da fonte instalada: a nuvem e a máquina local medem igual e
põem os botões do tour no mesmo x (28/10/2026). Fonte fora da tabela: o arquivo da máquina, se houver; senão 0,56 em.

    python -X utf8 pbi/scripts/tour_lib.py             # grava os .dax (sem tocar o PBIP)
    python -X utf8 pbi/scripts/tour_lib.py --previa    # grava pbi/qa/tour/html/t<n>-NN.html (prévia para foto)
"""
from __future__ import annotations

import argparse
import base64
import functools
import html
import io
import json
import math
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import contador as C  # noqa: E402
import contas_base as CB  # noqa: E402  (dicionário NOTA: itens, faixas, máximos; fonte única)
import desenho_comum as DC  # noqa: E402
import pbip_lib as lib  # noqa: E402
from contas_lib_projeto import Medida, gravar, nome_arquivo  # noqa: E402
from PIL import Image, ImageFont  # noqa: E402

RAIZ = AQUI.parent                     # pbi/
PROJETO = RAIZ.parent                  # criticidade-obras-bi/
PASSOS = RAIZ / "spec" / "tour" / "passos.json"
GERADO = "pbi/scripts/tour_lib.py"
LARGURA, ALTURA = 1920, 1080
MARGEM = 16                            # card e cabeça do personagem ficam entre 16 e 1904 (x) e 16 e 1064 (y)
AFASTA = 40                            # distância card–anel (é onde corre a cota)
FOLGA = 8                              # foco → recorte e anel
CANTO_FORA = 6                         # cantoneiras, para fora do anel
BRACO = 24                             # braço da cantoneira
RAIO_CANTO = 20                        # curva do L
RAIO_RECORTE = 14
RAIO_CARD = 16
CABECALHO = 56
TIQUE = 10
ALTURA_MAX = ALTURA - 2 * MARGEM       # 1048: altura útil do canvas para um balão
BALAO_W = 560                          # balão comum (brief v5 §2.2)
BALAO_W_GRANDE = 760                   # balão do card grande: até 760 (cai para 560 se o foco pedir)
BALAO_RAIO = 24
BALAO_PAD_T = 28                       # topo do balão: selo
BALAO_PAD_X = 32                       # laterais do balão
BALAO_PAD_B = 24                       # base do balão: abaixo da linha de controles
BALAO_MARGEM = 24                      # o balão fica a 24 px das bordas da tela
BALAO_ANEL = 40                        # balão ao lado do foco: 40 px do anel
BALAO_CABECA = 24                      # biquinho chega a ~24 px da cabeça
SELO_H = 26                            # pílula "Passo n de N": Segoe UI SemiBold 13, padding 4 × 12
SELO_GAP = 14                          # selo → título
TITULO_TEXTO = 12                      # título → texto
TEXTO_DICA = 14                        # texto (ou infográfico) → dica/nota
INF_GAP = 20                           # abertura → infográfico (card grande)
COL_GAP = 32                           # vão entre colunas do infográfico
COL_MIN_W = 300                        # coluna do infográfico não fica mais estreita que isso
CONTROLES_GAP = 22                     # último bloco → linha de controles
BOTAO_H = 44                           # "Voltar" e "Seguir →": desenho 44 de altura
VOLTAR_W = 92
SEGUIR_W = 124
PULAR_W, PULAR_H = 64, 56              # "Pular": link sem caixa, área de clique 64 × 56
CONTROLES_VAO = 10
BIQUINHO_W, BIQUINHO_H = 22, 14        # biquinho do balão (triângulo 22 × 14)
REGUA_TRACO_W, REGUA_TRACO_H = 26, 4   # régua de passos: traços 26 × 4
REGUA_VAO = 6
REGUA_TRACO_MIN = 10
NARRADOR_CABECA = 198                  # cabeça da narradora no card comum (px); topo do capacete ao queixo
NARRADOR_CABECA_GRANDE = 216           # no card grande
NARRADOR_CABECA_MIN = 153              # se tocar o foco, a cabeça encolhe até aqui
# Cabeça (topo do capacete ao queixo) ÷ altura da caixa do alfa da pose, medida em cada pose da Lia de obra (28/10/2026)
# no quadro de 1308 × 1590: capacete em y 136 a 139, queixo em y 463 a 470 (cabeça de 326 a 332 px; caixa de 1413 a
# 1416). P7 e P8: a caixa começa na ponta do dedo erguido (1513 e 1473 px) e a cabeça inclina para trás (queixo em 449
# e 458, cabeça de 310 e 319), daí 0,205 e 0,217. O capacete conta como cabeça: é o contorno de cima do rosto.
CABECA_FRAC = {1: 0.235, 2: 0.233, 3: 0.230, 4: 0.235, 5: 0.231, 6: 0.235, 7: 0.205, 8: 0.217,
               9: 0.234, 10: 0.231, 11: 0.228}
POSES = tuple(range(1, 12))            # P1 a P11 (P11: vistoria, extra da tela Canteiro)
POSES_SEM_DIRECAO = (1, 11)            # no passo 1 vale a do passos.json entre estas (P1 acenando; P11 vistoria na T5)
# Direção do dedo de cada pose (x para a direita, y para baixo), medida na Lia de obra (28/10/2026): da mão (centróide da
# pele entre 50 e 150 px da ponta, no recorte) à ponta do dedo. P2 sobe 25° acima da horizontal, P3 23°; P7 e P8 quase
# na vertical (96° e 83°); P9 33° acima da horizontal, P10 53°. P6: para a prancheta (fora da busca).
DIRECAO_DEDO = {2: (-0.906, -0.423), 3: (0.921, -0.391), 7: (-0.105, -0.995), 8: (0.122, -0.993),
                9: (-0.545, -0.839), 10: (0.602, -0.799), 6: (0.9578, 0.2873)}
ANG_DEDO_MAX = 45                      # o dedo aponta para o foco: ângulo da direção ao vetor ponta → foco ≤ 45°
RAIO_FOLGA = 16                        # e o raio do dedo (ponta + DIRECAO_DEDO) cruza o foco aumentado em 16 px (o anel)
FOCO_INVASAO_MAX = 40                  # último recurso: o gesto pode entrar até 40 px no recorte do foco
ANG_LATERAL = 25                       # θ < 25°: aponta para o lado (P2, P3)
ANG_CIMA = 65                          # 25° ≤ θ < 65°: diagonal (P9, P10); θ ≥ 65°: para cima (P7, P8)
from poses_busto import NARRADOR_FRAC  # noqa: E402  (recorte: corte no peito, fração do corpo; uma fonte só)
NARRADOR_DIR = PROJETO / "assets" / "personagem" / "poses" / "narrador"
NARRADOR_MARGEM = 40                   # 40 px da borda lateral da tela
NARRADOR_FOLGA = 24                    # folga entre o gestor e o recorte do foco
ALTURA_LIMITADA_IDS = {"CURVA", "MES", "QUALIDADE"}  # T3, T4 e T5 passo 3: abaixo do gráfico, colunas internas no corpo
# T1 passo 3: à esquerda os itens da nota e a regra; à direita o exemplo, as faixas da nota, o pendente e a trava
COLUNAS_FIXAS = {"PONTUACAO": (["itens", "regra"], ["exemplo", "faixas", "pendente", "nota"])}
COLUNA_ESQ_PONTUACAO = 400             # T1 passo 3: largura da coluna da esquerda (os itens em grade)
BIQUINHO_CAUDA = 80                    # card grande: a cauda do biquinho sai até 80 px
BIQUINHO_DIST = 120                    # distância ponta–cabeça: card comum
BIQUINHO_DIST_GRANDE = 260             # distância ponta–cabeça: card grande
CAUDA_BASE = 30                         # largura da base da cauda, na borda do balão
CAUDA_CANTO = 28                        # a base fica a pelo menos 28 px dos cantos arredondados
CAUDA_BOCA = 0.84                       # altura da boca, contando do topo do capacete (fração da cabeça; Lia: 0,82 na P7 a 0,85 na P1)
CAUDA_BOCA_SOBE = 0.05                  # o contorno da ponta é o mais largo do rosto de 5 % da cabeça acima da boca até ela
CAUDA_FORA = 12                         # a ponta fica 12 px para fora do contorno do rosto, na altura da boca
CAUDA_FOLGA = 8                         # folga mínima entre a cauda e qualquer pixel opaco do gestor
CAUDA_FOCO = 16                         # folga mínima entre a cauda e o recorte do foco
# comprimento da cauda, da base ao alvo. Lia: a boca fica a 0,84 da cabeça contando do topo do capacete (no narrador
# antigo, a 0,75 do topo do cabelo); do balão acima do capacete até a boca são ~18 px a mais, e o teto sobe de 180
# para 200 (com 180, 34 dos 37 passos perdiam a cabeça de 198 por falta de cauda e caíam para 180)
CAUDA_COMP = (36, 200)
CAUDA_PONTA = 2.5                       # largura da ponta da cauda
CAUDA_ENTRA = 4                         # a base entra 4 px no balão, para emendar sem linha na junção
PONTO_R = 3                            # ponto final da ligação: 8 px com o contorno de 2
POSE_ALTURA_PX = 600                   # busto embutido a 600 px (≥ 1x da altura exibida: 520 e 560)
POSE_MAX_BYTES = 150_000
DAX_ITENS_MAX = 800                    # acima disso a medida vai em grupos de DAX_GRUPO termos entre parênteses
DAX_GRUPO = 400
POSE_BITS = 5                          # bits por canal de cor da pose embutida (5: Lia de 107 a 142 KB, sem paleta; sem diferença visível)
OPOSTO = {"abaixo": "acima", "acima": "abaixo", "direita": "esquerda", "esquerda": "direita"}
PERPENDICULARES = {"abaixo": ("direita", "esquerda"), "acima": ("direita", "esquerda"),
                   "direita": ("abaixo", "acima"), "esquerda": ("abaixo", "acima")}
TELAS = {"T1": "T1 Visão geral", "T2": "T2 Análise crítica", "T3": "T3 Avanço físico", "T4": "T4 Resultado no tempo",
         "T5": "T5 Canteiro"}
DA_TELA = {"T5": "do"}   # "tour do Canteiro"; as outras telas são femininas
NOME_CSS = "Comum · Tour · CSS"

# --------------------------------------------------------------------------------------------- métricas de texto
FONTE_ARQ = {
    "segoe": r"C:\Windows\Fonts\segoeui.ttf",
    "segoe_sb": r"C:\Windows\Fonts\seguisb.ttf",
    "barlow": str(RAIZ / "assets" / "fontes" / "barlow-600.woff"),
}
FOLGA_TEXTO = 1.06                     # a largura medida ganha 6 %: a quebra estimada é de propósito um pouco maior
LARG_MEDIA_EM = 0.56                   # fallback sem as fontes: largura média por caractere, em em


METRICAS_ARQ = RAIZ / "spec" / "tour" / "metricas-fontes.json"


@functools.lru_cache(maxsize=None)
def _metricas() -> dict:
    """Avanço de cada caractere (milésimos de em) por fonte, da tabela do repositório (metricas_fontes.py)."""
    if METRICAS_ARQ.is_file():
        return json.loads(METRICAS_ARQ.read_text(encoding="utf-8")).get("fontes", {})
    return {}


@functools.lru_cache(maxsize=None)
def _fonte(nome: str, px: float):
    try:
        return ImageFont.truetype(FONTE_ARQ[nome], px)
    except OSError:
        return None


def medir(texto: str, fonte: str, px: float) -> float:
    """Largura estimada do texto (px), com a folga de FOLGA_TEXTO."""
    return _medir_cru(texto, fonte, px) * FOLGA_TEXTO


def _medir_cru(texto: str, fonte: str, px: float) -> float:
    """Largura do texto sem folga: a quebra de linhas usa a largura da fonte (o navegador quebra assim). Primeiro a
    tabela do repositório (igual em qualquer máquina); fora dela, o arquivo da fonte; sem ele, 0,56 em por caractere."""
    tab = _metricas().get(fonte)
    if tab:
        media = LARG_MEDIA_EM * 1000
        return sum(tab.get(c, media) for c in texto) * px / 1000
    f = _fonte(fonte, px)
    if f is None:
        return len(texto) * LARG_MEDIA_EM * px
    return f.getlength(texto)


LINHAS_NAVEGADOR_ARQ = RAIZ / "spec" / "tour" / "linhas-navegador.json"
REGISTRO_LINHAS = None                 # medir_linhas_tour.py liga para registrar as chamadas de linhas()


def chave_linhas(texto: str, largura: float, fonte: str, px: float) -> str:
    return f"{fonte}|{round(px, 3):g}|{round(largura, 2):g}|{texto}"


@functools.lru_cache(maxsize=None)
def linhas_navegador() -> dict:
    """Linhas medidas no Edge por medir_linhas_tour.py (o navegador manda; a estimativa erra por 1–2 px na borda)."""
    if LINHAS_NAVEGADOR_ARQ.is_file():
        return json.loads(LINHAS_NAVEGADOR_ARQ.read_text(encoding="utf-8"))
    return {}


def linhas(texto: str, largura: float, fonte: str, px: float) -> int:
    """Linhas que o texto ocupa numa coluna de `largura`: a medida do navegador (linhas-navegador.json), se houver; senão
    a estimativa por palavra com a largura real da fonte."""
    if not texto.strip():
        return 0
    if REGISTRO_LINHAS is not None:
        REGISTRO_LINHAS.add((texto, round(largura, 2), fonte, round(px, 3)))
    n = linhas_navegador().get(chave_linhas(texto, largura, fonte, px))
    if n is not None:
        return n
    return linhas_estimadas(texto, largura, fonte, px)


def linhas_estimadas(texto: str, largura: float, fonte: str, px: float) -> int:
    """Estimativa: quebra por palavra, gulosa, com a largura real da fonte (PIL)."""
    if not texto.strip():
        return 0
    espaco = _medir_cru(" ", fonte, px)
    n, atual = 1, 0.0
    for palavra in texto.split():
        w = _medir_cru(palavra, fonte, px)
        if atual == 0:
            atual = w
        elif atual + espaco + w <= largura:
            atual += espaco + w
        else:
            n += 1
            atual = w
    return n


# ----------------------------------------------------------------------------------------------------------- passos
def valores_nota() -> dict:
    """Valores da Nota da obra que os textos do tour citam, do dicionário NOTA de contas_base (fonte única)."""
    st = {s_: lim for _op, lim, s_ in CB.NOTA["status"] if lim is not None}
    tv = CB.NOTA["trava"]
    # exemplo do card do T1 03: IDC de 0,97 e 1,5 mês de atraso, com o resto cheio; pontos e status saem do dicionário
    ex_idc, ex_atraso = 0.97, 1.5
    p_idc, p_atr = CB.nota_pontos(CB.NOTA["idc"], ex_idc), CB.nota_pontos(CB.NOTA["atraso"], ex_atraso)
    max_c, max_p = CB.nota_maximo("custo"), CB.nota_maximo("prazo")
    nota_max = sum(CB.nota_maximo(c) for c in CB.NOTA_ITEM_MEDIDAS)
    ex_nota = nota_max - (max_c - p_idc) - (max_p - p_atr)
    ex_st = next(s_ for op, lim, s_ in CB.NOTA["status"] if lim is None or ex_nota >= lim)
    return {"nota_max": CB._br(nota_max, False), "n_itens": {9: "nove"}.get(len(CB.NOTA_ITENS), str(len(CB.NOTA_ITENS))),
            "estavel": CB._br(st[0], False), "atencao": CB._br(st[1], False),
            "idc_trava": CB.nota_valor("indice", tv["idc_abaixo"]), "atraso_trava": CB._br(tv["atraso_acima"], False),
            "prazo_cheio": CB.nota_valor("meses", CB.NOTA["atraso"][0][1]), "custo_max": CB._br(max_c, False),
            "prazo_max": CB._br(max_p, False), "caixa_lim": CB._br(CB.NOTA["caixa"][0][1], True),
            "ppc_meta": CB._br(CB.NOTA["ppc"][0][1], True),
            "inspecao_meta": CB._br(CB.NOTA["inspecao"][0][1], True), "nr18_meta": CB._br(CB.NOTA["nr18"][0][1], True),
            "entregas_meta": CB._br(CB.NOTA["entregas"][0][1], True),
            "acid_setor": CB._br(CB.NOTA["acidentes"][1][1], False),
            "ex_idc": CB.nota_valor("indice", ex_idc), "ex_p_idc": CB._br(p_idc, False),
            "ex_atraso": CB.nota_valor("meses", ex_atraso), "ex_p_atraso": CB._br(p_atr, False),
            "ex_nota": CB._br(ex_nota, False), "ex_status": {0: "estável", 1: "atenção", 2: "crítico"}[ex_st]}


def _troca_nota(v, val: dict):
    if isinstance(v, str):
        for k_, x in val.items():
            v = v.replace("{NOTA:" + k_ + "}", x)
        if "{NOTA:" in v:
            raise KeyError(f"marcador da nota sem valor: {v}")
        return v
    if isinstance(v, list):
        return [_troca_nota(x, val) for x in v]
    if isinstance(v, dict):
        return {k_: _troca_nota(x, val) for k_, x in v.items()}
    return v


@functools.lru_cache(maxsize=None)
def _passos_cache() -> str:
    return json.dumps(_troca_nota(json.loads(PASSOS.read_text(encoding="utf-8")), valores_nota()), ensure_ascii=False)


def carregar_passos() -> dict:
    """passos.json com os marcadores {NOTA:…} trocados pelos valores do dicionário NOTA."""
    return json.loads(_passos_cache())


def passos_da_tela(tela: str) -> list[dict]:
    return carregar_passos()["telas"][tela]["passos"]


def nome_medida(tela: str, n: int) -> str:
    return f"{tela} · Tour · Passo {n:02d} · HTML"


def nome_pose(n: int) -> str:
    return f"Comum · Tour · Pose P{n} · HTML"


def _e(s) -> str:
    """Escape de HTML de um texto fixo (& primeiro)."""
    return html.escape(str(s), quote=False)


def _n(v) -> str:
    return f"{v:g}"


def _caixa(x, y, w, h) -> str:
    return f"left:{_n(x)}px;top:{_n(y)}px;width:{_n(w)}px;height:{_n(h)}px"


# -------------------------------------------------------------------------------------------- recorte e cantoneiras
def recorte(foco: dict) -> dict:
    """Recorte e anel: o retângulo do foco com 8 px de folga em cada lado."""
    x, y, w, h = foco["x"] - FOLGA, foco["y"] - FOLGA, foco["w"] + 2 * FOLGA, foco["h"] + 2 * FOLGA
    return {"x": x, "y": y, "w": w, "h": h, "x2": x + w, "y2": y + h}


def _espaco(lado: str, R: dict) -> float:
    """Folga livre do lado, entre a borda do canvas (margem) e o anel (com AFASTA)."""
    if lado == "abaixo":
        return (ALTURA - MARGEM) - (R["y2"] + AFASTA)
    if lado == "acima":
        return (R["y"] - AFASTA) - MARGEM
    if lado == "direita":
        return (LARGURA - MARGEM) - (R["x2"] + AFASTA)
    return (R["x"] - AFASTA) - MARGEM


def _posicao(lado: str, R: dict, w: float, h: float) -> tuple[float, float]:
    if lado == "abaixo":
        return min(max(R["x"], MARGEM), LARGURA - MARGEM - w), R["y2"] + AFASTA
    if lado == "acima":
        return min(max(R["x"], MARGEM), LARGURA - MARGEM - w), R["y"] - AFASTA - h
    if lado == "direita":
        return R["x2"] + AFASTA, min(max(R["y"], MARGEM), ALTURA - MARGEM - h)
    return R["x"] - AFASTA - w, min(max(R["y"], MARGEM), ALTURA - MARGEM - h)


def caminho_cantoneiras(R: dict) -> str:
    """Quatro cantos em L com a curva de raio 20 no canto, braço 24, 6 px para fora do anel."""
    x0, y0 = R["x"] - CANTO_FORA, R["y"] - CANTO_FORA
    x1, y1 = R["x2"] + CANTO_FORA, R["y2"] + CANTO_FORA
    b, r = BRACO, RAIO_CANTO
    return (f"M{_n(x0 + b)} {_n(y0)}H{_n(x0 + r)}A{r} {r} 0 0 0 {_n(x0)} {_n(y0 + r)}V{_n(y0 + b)}"
            f"M{_n(x1 - b)} {_n(y0)}H{_n(x1 - r)}A{r} {r} 0 0 1 {_n(x1)} {_n(y0 + r)}V{_n(y0 + b)}"
            f"M{_n(x0 + b)} {_n(y1)}H{_n(x0 + r)}A{r} {r} 0 0 1 {_n(x0)} {_n(y1 - r)}V{_n(y1 - b)}"
            f"M{_n(x1 - b)} {_n(y1)}H{_n(x1 - r)}A{r} {r} 0 0 0 {_n(x1)} {_n(y1 - r)}V{_n(y1 - b)}")


# ----------------------------------------------------------------------------------------------- personagem (poses)
def pose_arquivo(n: int):
    rel = carregar_passos()["poses_arquivos"][f"P{n}"]
    arq = PROJETO / rel
    return arq if arq.is_file() else None


@functools.lru_cache(maxsize=None)
def pose_proporcao(n: int) -> float:
    """Largura / altura da pose (2:3 se o arquivo ainda não existe)."""
    arq = pose_arquivo(n)
    if arq is None:
        return 2 / 3
    w, h = Image.open(arq).size
    return w / h


@functools.lru_cache(maxsize=None)
def pose_dados(n: int) -> tuple[str, int]:
    """(data URI PNG, bytes) do gestor: recorte do narrador na altura de 1x do card grande (cabeça de 216 px); não
    amplia. As cores vão a POSE_BITS bits por canal (alfa intacto) em todas as poses, para o peso ficar parecido e
    abaixo de POSE_MAX_BYTES sem paleta: a paleta (FASTOCTREE) manchava a pele do narrador NB de cinza. A paleta fica só
    como último recurso."""
    import numpy as np
    im = Image.open(narrador_arquivo(n)).convert("RGBA")
    alvo = round(NARRADOR_FRAC[n] * NARRADOR_CABECA_GRANDE / CABECA_FRAC[n])
    if im.size[1] > alvo:
        im = im.resize((round(im.size[0] * alvo / im.size[1]), alvo), Image.Resampling.LANCZOS)
    a = np.asarray(im).copy()
    c = a[..., :3] & ((0xFF << (8 - POSE_BITS)) & 0xFF)
    a[..., :3] = c | (c >> POSE_BITS)
    im = Image.fromarray(a, "RGBA")
    for cores in (None, 160, 96, 64):
        saida = im if cores is None else im.quantize(colors=cores, method=Image.Quantize.FASTOCTREE)
        buf = io.BytesIO()
        saida.save(buf, "PNG", optimize=True)
        dados = buf.getvalue()
        if len(dados) <= POSE_MAX_BYTES:
            break
    return "data:image/png;base64," + base64.b64encode(dados).decode("ascii"), len(dados)


@functools.lru_cache(maxsize=None)
def pose_html(n: int) -> str:
    """Conteúdo da medida da pose: imagem em data URI, ou o espaço reservado em SVG se a pose não existe."""
    if pose_arquivo(n) is not None:
        uri, _ = pose_dados(n)
        return f"<img class='pp' alt='' src='{uri}'>"
    rotulo = carregar_passos()["poses"][f"P{n}"]
    return ("<div class='ph' role='img' aria-label='" + html.escape(f"Gestor da Construtora, pose {rotulo} (espaço reservado)", quote=True)
            + "'><svg viewBox='0 0 230 345' preserveAspectRatio='xMidYMax meet' aria-hidden='true' focusable='false'>"
            "<circle cx='115' cy='104' r='40' fill='#F7F4EE'/>"
            "<path d='M40 250C40 180 70 160 115 160C160 160 190 180 190 250L190 345L40 345Z' fill='#F7F4EE'/></svg>"
            f"<p>{_e(rotulo)}</p></div>")


# ---------------------------------------------------------------------- narrador, balão e ligação (v5, §2.2 e §3)
def narrador_arquivo(n: int) -> Path:
    arqs = sorted(NARRADOR_DIR.glob(f"P{n}-*.png"))
    if not arqs:
        raise lib.ErroDeclaracao(f"recorte do narrador P{n} não existe: rode poses_busto.py --narrador")
    return arqs[0]


# Recorte provisório (28/10/2026): a narradora nova (Lia) e os recortes dela vêm da sessão local. Enquanto a pasta
# NARRADOR_DIR não tem o recorte de uma pose, a geometria do tour usa uma silhueta em memória com a proporção do recorte
# (cabeça escura no topo, tronco e o braço na direção do gesto da pose): só para as contas de posição, colisão e dedo,
# nunca gravada nem exibida. Com o recorte no disco, ele vale sozinho.
PROVISORIO_ALTURA = 900        # px da silhueta provisória


def _recorte_provisorio(n: int) -> Image.Image:
    """Silhueta provisória da pose n (RGBA): cabeça escura (o "cabelo" que gestor_geometria procura), tronco e o braço
    do gesto em outra cor (P2/P3 para o lado, P1/P7/P8 erguido, P9/P10 na diagonal, P6 para a prancheta)."""
    from PIL import ImageDraw
    h = PROVISORIO_ALTURA
    cab = CABECA_FRAC[n] / NARRADOR_FRAC[n] * h      # altura da cabeça no recorte
    hw = 0.80 * cab                                   # largura da cabeça
    ombro = 1.9 * hw                                  # largura do tronco
    braco = 0.17 * cab                                # espessura do braço
    estende = 1.3 * cab                               # quanto o braço sai do tronco
    if n in (2, 9):
        w, cx = ombro + estende, ombro + estende - ombro / 2
    elif n in (3, 10):
        w, cx = ombro + estende, ombro / 2
    elif n in (1, 7):
        w, cx = ombro + 0.5 * cab, ombro + 0.5 * cab - ombro / 2
    elif n == 8:
        w, cx = ombro + 0.5 * cab, ombro / 2
    elif n == 6:
        w, cx = ombro + 0.8 * estende, ombro / 2
    else:
        w, cx = ombro, ombro / 2
    w = round(w)
    im = Image.new("RGBA", (w, round(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pele, roupa, cabelo = (214, 170, 140, 255), (120, 135, 160, 255), (40, 36, 34, 255)
    d.rounded_rectangle((cx - ombro / 2, cab * 0.95, cx + ombro / 2, h), radius=round(cab * 0.35), fill=roupa)
    ys = cab * 1.02                                   # altura do ombro
    if n == 2:
        d.rectangle((0, ys, cx - ombro / 2 + braco, ys + braco), fill=pele)
    elif n == 3:
        d.rectangle((cx + ombro / 2 - braco, ys, w, ys + braco), fill=pele)
    elif n in (1, 7):
        x = cx - hw / 2 - 0.25 * cab
        d.rectangle((x - braco, 0.05 * cab, x, ys + braco), fill=pele)
    elif n == 8:
        x = cx + hw / 2 + 0.25 * cab
        d.rectangle((x, 0.05 * cab, x + braco, ys + braco), fill=pele)
    elif n == 9:
        d.line((cx - ombro / 2, ys, 2, 0.08 * cab), fill=pele, width=round(braco))
    elif n == 10:
        d.line((cx + ombro / 2, ys, w - 2, 0.08 * cab), fill=pele, width=round(braco))
    elif n == 6:
        d.line((cx + ombro / 2 - braco, ys + braco, w - 2, ys + braco + 0.29 * (w - cx - ombro / 2)), fill=pele,
               width=round(braco))
    d.ellipse((cx - hw / 2, 0, cx + hw / 2, cab), fill=cabelo)
    return im


@functools.lru_cache(maxsize=None)
def _imagem_narrador(n: int) -> Image.Image:
    """Recorte do narrador da pose n (RGBA): o arquivo de NARRADOR_DIR ou, sem ele, a silhueta provisória."""
    if _pose_existe(n):
        return Image.open(narrador_arquivo(n)).convert("RGBA")
    return _recorte_provisorio(n)


@functools.lru_cache(maxsize=None)
def gestor_geometria(n: int) -> dict:
    """Recorte da narradora (corpo inteiro até o peito), em frações do recorte: proporção, topo e centro da cabeça,
    faixa do rosto e a altura do corpo inteiro (px do recorte). A cabeça é achada pelo capacete branco (Lia de obra,
    28/10/2026): a regra antiga do cabelo escuro na faixa de cima errava, porque no topo agora fica o capacete e, na P7
    e na P8, a mão erguida acima dele. Sem capacete (silhueta provisória), vale o cabelo escuro do topo."""
    frac = NARRADOR_FRAC[n]
    im = _imagem_narrador(n)
    W, H = im.size
    corpo = H / frac
    import numpy as np
    arr = np.asarray(im).astype(int)
    opaco = arr[..., 3] >= 128
    cab_px = CABECA_FRAC[n] * corpo
    # capacete: branco sem cor (mínimo do RGB > 150, máximo − mínimo < 20; a camisa creme tem 26) na parte de cima
    lim = min(H, round(1.2 * cab_px + 0.12 * corpo))
    rgb = arr[:lim, :, :3]
    branco = opaco[:lim] & (rgb.min(axis=2) > 150) & (rgb.max(axis=2) - rgb.min(axis=2) < 20)
    linhas = np.nonzero(branco.sum(axis=1) >= max(8, round(0.05 * cab_px)))[0]
    if linhas.size:
        topo = int(linhas[0])
        faixa = branco[topo:topo + round(0.45 * cab_px)]
        c5, c95 = np.percentile(np.nonzero(faixa)[1], (5, 95))    # meio da largura do capacete (a média puxa para o
        cx = float(c5 + c95) / 2 / W                              # lado iluminado, ~18 px no quadro)
    else:
        topo = 0
        sh = max(1, round(0.05 * corpo))
        escuro = opaco[:sh] & (arr[:sh, :, :3].max(axis=2) < 90)
        if escuro.sum() >= 50:
            cx = float(np.nonzero(escuro)[1].mean()) / W
        else:
            cols = np.nonzero(opaco[:sh].any(axis=0))[0]
            cx = (cols[0] + cols[-1] + 1) / 2 / W if cols.size else 0.5
    t = topo / H
    meia_face = 0.40 * CABECA_FRAC[n] * corpo / W
    return {"asp": W / H, "frac": frac, "corpo": corpo, "cx": cx, "cy": t + (CABECA_FRAC[n] / 2) / frac,
            "esq": cx - meia_face, "dir": cx + meia_face, "topo": t, "rosto": t + CABECA_FRAC[n] / frac}


def _narrador_rect(n: int, cabeca: float, canto: str) -> tuple[int, int, int, int]:
    """Retângulo (x, y, w, h) do gestor com a cabeça de `cabeca` px: a base do recorte encosta na base da tela, e o
    recorte fica a 40 px da borda lateral do canto indicado."""
    g = gestor_geometria(n)
    nh = round(g["frac"] * cabeca / CABECA_FRAC[n])
    nw = round(nh * g["asp"])
    x = LARGURA - NARRADOR_MARGEM - nw if canto == "direita" else NARRADOR_MARGEM
    return x, ALTURA - nh, nw, nh


def _sobrepoe(a, b) -> bool:
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


def _area(a, b) -> float:
    w = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
    h = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    return max(0.0, w) * max(0.0, h)


def _expande(r: dict, f: float) -> tuple:
    return r["x"] - f, r["y"] - f, r["w"] + 2 * f, r["h"] + 2 * f


def _expande_t(r: tuple, f: float) -> tuple:
    return r[0] - f, r[1] - f, r[2] + 2 * f, r[3] + 2 * f


def _ajusta(v: float, lo: float, hi: float) -> float:
    return max(lo, min(v, hi))


def _pose_do_passo(passo: dict, total: int, canto: str) -> int:
    """P1 no passo 1, P5 no último, P6 no card grande; nos demais, a pose do passos.json, trocada se apontar para
    fora da tela (P3 com o gestor à direita; P2 com o gestor à esquerda)."""
    pn = int(passo["pose"][1:])
    if passo["n"] == 1:
        return _pose_inicial(passo)
    if passo["n"] == total:
        return 5
    if passo["tipo"] == "grande":
        return 6
    if (canto == "direita" and pn == 3) or (canto == "esquerda" and pn == 2):
        return 4
    return pn


def _regua_medida(total: int, disponivel: float) -> tuple[int, int]:
    """Traços da régua de passos (26 × 4, vão 6), reduzidos até caber na faixa livre à esquerda dos botões."""
    t, v = REGUA_TRACO_W, REGUA_VAO
    while total * t + (total - 1) * v > disponivel and t > REGUA_TRACO_MIN:
        t -= 1
    while total * t + (total - 1) * v > disponivel and v > 3:
        v -= 1
    return t, v


def _controles(passo_n: int, total: int, w: int, bh: int, tela: str) -> dict:
    """Linha de controles: régua à esquerda; Pular, Voltar e Seguir → (ou Concluir ✓) à direita, centrados."""
    row_y = bh - BALAO_PAD_B - BOTAO_H
    row_cy = row_y + BOTAO_H / 2
    seguir_x = w - BALAO_PAD_X - SEGUIR_W
    ctl = {"seguir": {"x": seguir_x, "y": row_y, "w": SEGUIR_W, "h": BOTAO_H}}
    x_ref = seguir_x
    if passo_n > 1:
        ctl["voltar"] = {"x": x_ref - CONTROLES_VAO - VOLTAR_W, "y": row_y, "w": VOLTAR_W, "h": BOTAO_H}
        x_ref = ctl["voltar"]["x"]
    if passo_n < total:
        ctl["pular"] = {"x": x_ref - CONTROLES_VAO - PULAR_W, "y": row_cy - PULAR_H / 2, "w": PULAR_W, "h": PULAR_H}
        x_ref = ctl["pular"]["x"]
    disponivel = x_ref - 16 - BALAO_PAD_X
    t, v = _regua_medida(total, disponivel)
    if t < REGUA_TRACO_W:
        msg = f"{tela} passo {passo_n}: régua reduzida para traços de {t} px (vão {v}) para caber com os botões"
        if msg not in REGISTROS:
            REGISTROS.append(msg)
    ctl["regua"] = {"x": BALAO_PAD_X, "y": row_cy - REGUA_TRACO_H / 2, "t": t, "v": v, "n": total,
                    "w": total * t + (total - 1) * v}
    return ctl


@functools.lru_cache(maxsize=None)
def _alfa_gestor(n: int) -> Image.Image:
    """Canal alfa do recorte do gestor, em resolução total (o provisório, enquanto o recorte não existe)."""
    return _imagem_narrador(n).getchannel("A")


def _gestor_toca(n: int, nar: tuple, zona: tuple) -> bool:
    """True se algum pixel opaco (alfa ≥ 32) do recorte do gestor cai dentro de `zona` (x, y, w, h). É o teste pixel a
    pixel: a caixa do recorte não conta, só o que é gesto ou corpo."""
    x, y, w, h = nar
    zx, zy, zw, zh = zona
    ix0, iy0 = max(x, zx), max(y, zy)
    ix1, iy1 = min(x + w, zx + zw), min(y + h, zy + zh)
    if ix0 >= ix1 or iy0 >= iy1:
        return False
    alfa = _alfa_gestor(n)
    W, H = alfa.size
    sx, sy = W / w, H / h
    cx0, cy0 = max(0, int((ix0 - x) * sx)), max(0, int((iy0 - y) * sy))
    cx1, cy1 = min(W, math.ceil((ix1 - x) * sx)), min(H, math.ceil((iy1 - y) * sy))
    if cx0 >= cx1 or cy0 >= cy1:
        return False
    sub = alfa.crop((cx0, cy0, cx1, cy1)).point(lambda v: 255 if v >= 32 else 0)
    return sub.getbbox() is not None


def _conteudo_balao(passo: dict, w: int, c_max: int) -> dict:
    """Conteúdo do balão numa largura: altura de cada bloco e a altura total (bh). Card grande com colunas fixas (T1
    passo 3): os itens da nota e a regra à esquerda; exemplo, faixas da nota, pendente e trava à direita."""
    tw = w - 2 * BALAO_PAD_X
    fim, tipo = _texto_palco(passo)
    D = linhas(fim, tw - (24 if tipo == "dica" else 0), "segoe", 15) if fim else 0
    if passo["tipo"] == "grande":
        cab = _cabecalho(passo, tw, 1.0)
        if passo["id"] in COLUNAS_FIXAS:
            esq, dir_ = COLUNAS_FIXAS[passo["id"]]
            wl = COLUNA_ESQ_PONTUACAO
            wr = tw - wl - COL_GAP
            colunas = [_infog_itens(passo, wl, 1.0, esq), _infog_itens(passo, wr, 1.0, dir_)]
            inf_h = max(c.h for c in colunas)
            inf = {"c": 2, "tw": wl, "larguras": [wl, wr], "colunas": colunas}
        else:
            inf_h, inf = _infog_colunas(passo, tw, c_max,
                                        col_min=200 if passo["id"] in ALTURA_LIMITADA_IDS else COL_MIN_W)
        cabeca, T, L = cab.h, 0, 0
    else:
        cab, inf, inf_h = None, None, 0.0
        T = linhas(passo["titulo"], tw, "barlow", 30)
        L = linhas(passo.get("texto") or "", tw, "segoe", 17)
        cabeca = T * 36 + (TITULO_TEXTO + L * 26 if L else 0)
    bh = (BALAO_PAD_T + SELO_H + SELO_GAP + cabeca + (INF_GAP + inf_h if inf else 0)
          + (TEXTO_DICA + D * 22 if D else 0) + CONTROLES_GAP + BOTAO_H + BALAO_PAD_B)
    return {"w": w, "tw": tw, "bh": math.ceil(bh), "cab": cab, "inf": inf, "inf_h": inf_h, "T": T, "L": L,
            "D": D, "fim": fim, "tipo": tipo, "cabeca": cabeca}


def _cabeca_de(pn: int, nar: tuple) -> float:
    """Altura da cabeça, em px de tela, a partir da altura do recorte do gestor (pose pn)."""
    return nar[3] * CABECA_FRAC[pn] / gestor_geometria(pn)["frac"]


@functools.lru_cache(maxsize=None)
def _mascara_gestor(pn: int, nh: int) -> dict:
    """Máscara do gestor na altura nh (px de tela): opaco (alfa >= 32) e o mesmo opaco engordado em CAUDA_FOLGA px, em
    matrizes [linha, coluna] relativas ao canto superior esquerdo do gestor. topo: primeira linha com pixel opaco."""
    import numpy as np
    nw = round(nh * gestor_geometria(pn)["asp"])
    op = np.asarray(_alfa_gestor(pn).resize((nw, nh), Image.BILINEAR)) >= 32
    dil = np.zeros_like(op)
    r = CAUDA_FOLGA
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy > r * r:
                continue
            dst = (slice(max(0, dy), min(nh, nh + dy)), slice(max(0, dx), min(nw, nw + dx)))
            src = (slice(max(0, -dy), min(nh, nh - dy)), slice(max(0, -dx), min(nw, nw - dx)))
            dil[dst] |= op[src]
    return {"nw": nw, "op": op, "dil": dil, "topo": int(np.nonzero(op.any(axis=1))[0][0])}


def _boca(M: dict, cabeca: float, cx_rel: float, topo_rel: float | None = None):
    """Linha da boca (CAUDA_BOCA da altura da cabeça, contando do topo do capacete, `topo_rel`; sem ele, a primeira
    linha opaca) e o trecho opaco do rosto nela: (linha, coluna esquerda, coluna direita), relativos à narradora. None
    se a linha não tem pixel opaco. Na P7 e na P8 a primeira linha opaca é a mão erguida, não a cabeça."""
    import numpy as np
    op = M["op"]
    r = int(round((M["topo"] if topo_rel is None else topo_rel) + CAUDA_BOCA * cabeca))
    if not 0 <= r < op.shape[0]:
        return None
    linha = op[r]
    cols = np.nonzero(linha)[0]
    if cols.size == 0:
        return None
    c0 = int(cols[np.argmin(np.abs(cols - cx_rel))])
    # contorno: o trecho mais largo do rosto entre CAUDA_BOCA_SOBE da cabeça acima da boca e a boca. No narrador NB a
    # barba afina o rosto justo na linha da boca e a bochecha logo acima é mais larga: com a ponta medida só na linha
    # da boca, a cauda que desce do balão encostava na bochecha (folga de 8 px) em todas as bases.
    xl, xr = c0, c0
    for rr in range(max(0, r - int(round(CAUDA_BOCA_SOBE * cabeca))), r + 1):
        lin = op[rr]
        if not lin[c0]:
            continue
        a = b = c0
        while a > 0 and lin[a - 1]:
            a -= 1
        while b < lin.size - 1 and lin[b + 1]:
            b += 1
        xl, xr = min(xl, a), max(xr, b)
    return r, xl, xr


def _bezier(P0: tuple, P1: tuple, P2: tuple, t: float) -> tuple:
    u = 1.0 - t
    return (u * u * P0[0] + 2 * u * t * P1[0] + t * t * P2[0], u * u * P0[1] + 2 * u * t * P1[1] + t * t * P2[1])


def _bases(bal: tuple, T: tuple, lado_cauda: str) -> list:
    """Bases possíveis da cauda na borda do balão mais próxima do alvo T, de 8 em 8 px e a 28 px dos cantos. A preferida
    fica no canto do lado de onde a cauda vem (lado_cauda 'dir': canto direito; 'esq': canto esquerdo)."""
    bx, by, bw, bh = bal
    L, k = CAUDA_BASE, CAUDA_CANTO
    if T[1] >= by + bh or T[1] <= by:
        horiz = True
        aresta, nf = ("baixo", (0, 1)) if T[1] >= by + bh else ("cima", (0, -1))
        y = by + bh if aresta == "baixo" else by
        vaos = [bx + k + i * 8 for i in range(int((bw - 2 * k - L) // 8) + 1)]
        ideal = bx + bw - k - L if lado_cauda == "dir" else bx + k
        pontos = [((x, y), (x + L, y)) for x in vaos]
    else:
        horiz = False
        if T[0] >= bx + bw:
            aresta, nf = "direita", (1, 0)
            x = bx + bw
        else:
            aresta, nf = "esquerda", (-1, 0)
            x = bx
        vaos = [by + k + i * 8 for i in range(int((bh - 2 * k - L) // 8) + 1)]
        ideal = by + bh - k - L if T[1] >= by + bh / 2 else by + k
        pontos = [((x, y), (x, y + L)) for y in vaos]
    pontos.sort(key=lambda p: abs((p[0][0] if horiz else p[0][1]) - ideal))
    return [(p[0], p[1], aresta, nf) for p in pontos]


def _monta_cauda(bal: tuple, B1: tuple, B2: tuple, aresta: str, T: tuple):
    """Cauda curva da base B1–B2 até o alvo T: duas quadráticas que saem da base e se afinam até a ponta, curvadas para
    fora do balão. Devolve o dicionário da cauda (caminho SVG em coordenadas da tela, pontos da amostra, comprimento)
    ou None se o eixo base–alvo sai de CAUDA_COMP."""
    import numpy as np
    bx, by, bw, bh = bal
    M0 = ((B1[0] + B2[0]) / 2, (B1[1] + B2[1]) / 2)
    A = (T[0] - M0[0], T[1] - M0[1])
    comp = math.hypot(A[0], A[1])
    if not CAUDA_COMP[0] <= comp <= CAUDA_COMP[1]:
        return None
    px, py = -A[1] / comp, A[0] / comp
    cen = (bx + bw / 2, by + bh / 2)
    if px * (M0[0] - cen[0]) + py * (M0[1] - cen[1]) < 0:
        px, py = -px, -py
    lado1 = 1.0 if (B1[0] - M0[0]) * px + (B1[1] - M0[1]) * py >= 0 else -1.0
    meia = CAUDA_PONTA / 2
    Ta = (T[0] + px * meia * lado1, T[1] + py * meia * lado1)
    Tb = (T[0] - px * meia * lado1, T[1] - py * meia * lado1)
    k = 0.18 * comp
    Q1 = ((B1[0] + Ta[0]) / 2 + px * k, (B1[1] + Ta[1]) / 2 + py * k)
    Q2 = ((B2[0] + Tb[0]) / 2 + px * k, (B2[1] + Tb[1]) / 2 + py * k)
    dx, dy = {"baixo": (0, -1), "cima": (0, 1), "direita": (-1, 0), "esquerda": (1, 0)}[aresta]
    B1i = (B1[0] + dx * CAUDA_ENTRA, B1[1] + dy * CAUDA_ENTRA)
    B2i = (B2[0] + dx * CAUDA_ENTRA, B2[1] + dy * CAUDA_ENTRA)
    ts = np.linspace(0.0, 1.0, 41)
    ea = np.array([_bezier(B1, Q1, Ta, t) for t in ts])
    eb = np.array([_bezier(Tb, Q2, B2, t) for t in ts])
    amostra = np.vstack([ea, eb, (ea + eb) / 2])
    caminho = (f"M{_n(B1i[0])} {_n(B1i[1])}L{_n(B1[0])} {_n(B1[1])}Q{_n(Q1[0])} {_n(Q1[1])} {_n(Ta[0])} {_n(Ta[1])}"
               f"L{_n(Tb[0])} {_n(Tb[1])}Q{_n(Q2[0])} {_n(Q2[1])} {_n(B2[0])} {_n(B2[1])}"
               f"L{_n(B2i[0])} {_n(B2i[1])}Z")
    return {"aresta": aresta, "base": (B1, B2), "tip": T, "comp": comp, "path": caminho, "amostra": amostra}


def _livre(cau: dict, M: dict, nar: tuple, R: dict) -> bool:
    """A cauda fica dentro da tela, sem pixel opaco do gestor a menos de CAUDA_FOLGA e a CAUDA_FOCO ou mais do recorte."""
    import numpy as np
    S = cau["amostra"]
    if (S[:, 0] < 0).any() or (S[:, 0] > LARGURA).any() or (S[:, 1] < 0).any() or (S[:, 1] > ALTURA).any():
        return False
    ri = np.round(S[:, 1] - nar[1]).astype(int)
    ci = np.round(S[:, 0] - nar[0]).astype(int)
    dentro = (ri >= 0) & (ri < M["dil"].shape[0]) & (ci >= 0) & (ci < M["dil"].shape[1])
    if dentro.any() and M["dil"][ri[dentro], ci[dentro]].any():
        return False
    x0, y0, w0, h0 = R["x"], R["y"], R["w"], R["h"]
    ddx = np.maximum(np.maximum(x0 - S[:, 0], S[:, 0] - (x0 + w0)), 0)
    ddy = np.maximum(np.maximum(y0 - S[:, 1], S[:, 1] - (y0 + h0)), 0)
    return bool((np.sqrt(ddx * ddx + ddy * ddy) >= CAUDA_FOCO).all())


def _cauda(bal: tuple, nar: tuple, pn: int, R: dict, cab_x: float):
    """Cauda curva do balão `bal` para a cabeça do gestor `nar` (pose pn). A ponta fica CAUDA_FORA px para fora do rosto,
    na altura da boca, do lado do rosto voltado para o balão. A base fica na borda do balão mais próxima e se desloca
    ao longo dela até achar um caminho livre. Devolve a cauda, ou None se nenhuma combinação atende às restrições."""
    M = _mascara_gestor(pn, nar[3])
    lin = _boca(M, _cabeca_de(pn, nar), cab_x - nar[0], gestor_geometria(pn)["topo"] * nar[3])
    if lin is None:
        return None
    r, xl, xr = lin
    ym = nar[1] + r + 0.5
    bx, by, bw, bh = bal
    lado_cauda = "dir" if bx + bw / 2 > cab_x else "esq"
    for face in (["dir", "esq"] if lado_cauda == "dir" else ["esq", "dir"]):
        if face == "dir":
            T, contorno = (nar[0] + xr + 1 + CAUDA_FORA, ym), (nar[0] + xr + 1, ym)
        else:
            T, contorno = (nar[0] + xl - CAUDA_FORA, ym), (nar[0] + xl, ym)
        for B1, B2, aresta, _nf in _bases(bal, T, lado_cauda):
            cau = _monta_cauda(bal, B1, B2, aresta, T)
            if cau is not None and _livre(cau, M, nar, R):
                cau["contorno"] = contorno
                cau["lado_rosto"] = face
                return cau
    return None


def _anexa_cauda(geo: dict, cau) -> None:
    """Põe no biquinho do passo o caminho da cauda e os dados que a checagem confere."""
    bq = geo["biquinho"]
    bq["path"] = cau["path"] if cau else None
    bq["base"] = [tuple(p) for p in cau["base"]] if cau else None
    bq["comp"] = cau["comp"] if cau else None
    bq["contorno"] = cau["contorno"] if cau else None
    bq["amostra"] = [(float(x), float(y)) for x, y in cau["amostra"]] if cau else None


def _dist_retangulos(a: tuple, b: tuple) -> float:
    """Distância entre dois retângulos (x, y, w, h); 0 se encostam ou se cruzam."""
    dx = max(b[0] - (a[0] + a[2]), a[0] - (b[0] + b[2]), 0)
    dy = max(b[1] - (a[1] + a[3]), a[1] - (b[1] + b[3]), 0)
    return (dx * dx + dy * dy) ** 0.5


def _coloca_balao(R: dict, nar: tuple, rosto: dict, canto: str, w_opcoes: list, bh_de, longo: bool = False,
                  pn: int = 0) -> dict:
    """Balão entre o gestor e o foco: cinco posições em volta da cabeça (acima, acima-esquerda, acima-direita, à esquerda
    e à direita). Valida: margens de 24; a 16 px ou mais do foco; sem cobrir o rosto do gestor; e cauda curva válida
    (_cauda). Escolhe a de menor custo: distância balão–foco + comprimento da cauda."""
    cab = (rosto["cx"], rosto["cy"])
    hx, hy = cab
    zona_foco = (R["x"], R["y"], R["w"], R["h"])
    zona_cabeca = _expande_t((nar[0], nar[1], nar[2], 0.3 * nar[3]), 8)
    topo = rosto["topo"]
    esq, dir_ = rosto["esq"], rosto["dir"]

    def posicoes(w: int, bh: int):
        y_acima = topo - 18 - bh
        y_meio = _ajusta(hy - bh / 2, BALAO_MARGEM, ALTURA - BALAO_MARGEM - bh)
        return [
            ("cima", hx - w / 2, y_acima),
            ("cima-esq", hx - w + 72, y_acima),
            ("cima-dir", hx - 72, y_acima),
            ("esq", esq - BIQUINHO_H - 24 - w, y_meio),
            ("dir", dir_ + BIQUINHO_H + 24, y_meio),
        ]

    melhor = None
    primeiro = None
    for w in w_opcoes:
        bh = bh_de(w)
        for nome, bx_, by_ in posicoes(w, bh):
            bal = (round(_ajusta(bx_, BALAO_MARGEM, LARGURA - BALAO_MARGEM - w)),
                   round(_ajusta(by_, BALAO_MARGEM, ALTURA - BALAO_MARGEM - bh)), w, bh)
            gap = _dist_retangulos(bal, zona_foco)
            basico = (BALAO_MARGEM <= bal[0] and bal[0] + w <= LARGURA - BALAO_MARGEM
                      and BALAO_MARGEM <= bal[1] and bal[1] + bh <= ALTURA - BALAO_MARGEM
                      and gap >= 16 and not _sobrepoe(bal, zona_cabeca))
            cau = _cauda(bal, nar, pn, R, hx) if basico else None
            if cau is not None:
                custo = gap + cau["comp"]
                if melhor is None or custo < melhor["custo"]:
                    melhor = {"cand": nome, "w": w, "bh": bh, "x": bal[0], "y": bal[1], "lado": cau["aresta"],
                              "tip": cau["tip"], "valido": True, "custo": custo, "cauda": cau}
            elif primeiro is None:
                ponta = (_ajusta(hx, bal[0], bal[0] + w), bal[1] + bh if hy > bal[1] + bh else bal[1])
                primeiro = {"cand": nome, "w": w, "bh": bh, "x": bal[0], "y": bal[1], "lado": "", "tip": ponta,
                            "valido": False, "custo": 1e9, "cauda": None}
    return melhor or primeiro


def _ligacao(bal: tuple, R: dict) -> dict:
    """Ponto de partida na borda do balão, mais próximo do foco, e o ponto de chegada no anel."""
    bx, by, bw, bh = bal
    cx, cy = R["x"] + R["w"] / 2, R["y"] + R["h"] / 2
    if R["x2"] <= bx:
        p = (bx, _ajusta(cy, by + 24, by + bh - 24))
        q = (R["x2"], _ajusta(p[1], R["y"], R["y2"]))
    elif R["x"] >= bx + bw:
        p = (bx + bw, _ajusta(cy, by + 24, by + bh - 24))
        q = (R["x"], _ajusta(p[1], R["y"], R["y2"]))
    elif R["y2"] <= by:
        p = (_ajusta(cx, bx + 24, bx + bw - 24), by)
        q = (_ajusta(p[0], R["x"], R["x2"]), R["y2"])
    else:
        p = (_ajusta(cx, bx + 24, bx + bw - 24), by + bh)
        q = (_ajusta(p[0], R["x"], R["x2"]), R["y"])
    return {"P": p, "Q": q}


# ---------------------------------------------------------------------------------------------- layout "grande"
class Coluna:
    """Coluna de blocos: HTML, altura e registro (html, altura, margem) de cada bloco, para dividir em colunas."""

    def __init__(self, k: float):
        self.k = k
        self.partes: list[str] = []
        self.h = 0.0
        self.registro: list[tuple[str, float, float]] = []

    def bloco(self, conteudo: str, h: float, mt: float = 0):
        mt = mt * self.k if self.partes else 0
        self.h += mt + h
        estilo = f" style='margin-top:{_n(round(mt, 2))}px'" if mt else ""
        self.partes.append(f"<div{estilo}>{conteudo}</div>")
        self.registro.append((conteudo, h, mt))
        return self

    def html(self) -> str:
        return "".join(self.partes)


ORDEM_CABECALHO = {"PONTUACAO": ["abertura"], "QUADRADINHO": ["abertura"], "CASCATA": ["abertura"], "CURVA": ["abertura"],
                   "MES": ["abertura", "leitura"], "QUALIDADE": ["abertura", "leitura"]}
ORDEM_INFOG = {
    "PONTUACAO": ["itens", "regra", "exemplo", "faixas", "pendente", "nota", "dica"],
    "QUADRADINHO": ["conta", "fecho", "dica"],
    "CASCATA": ["conta", "fecho", "dica"],   # T2 desde a F3 (a conta da cascata nova, no lugar do quadradinho)
    "CURVA": ["faixas", "fecho", "dica"],
    "MES": ["fecho", "dica"],
    "QUALIDADE": ["fecho", "dica"],   # T5 passo 3: o mesmo card do mês a mês da T4
}
RUBRICA_FAIXAS = {"PONTUACAO": "Faixas da nota"}
AVISOS: list[str] = []
REGISTROS: list[str] = []   # ajustes feitos (pose trocada, gestor encolhido, régua reduzida)


def _gx(col: Coluna, texto: str, tw: float, mt: float = 12):
    k = col.k
    col.bloco(f"<p class='gx'>{_e(texto)}</p>", linhas(texto, tw, "segoe", 17 * k) * 26 * k, mt=mt)


def _ga(col: Coluna, texto: str, tw: float, mt: float = 8):
    k = col.k
    col.bloco(f"<p class='ga'>{_e(texto)}</p>", linhas(texto, tw, "segoe", 15 * k) * 22 * k, mt=mt)


def _pendente(col: Coluna, texto: str, tw: float, mt: float = 12):
    """O estado pendente da nota, com a marca tracejada das telas."""
    k = col.k
    col.bloco(f"<p class='ga'><i class='mm'></i>{_e(texto)}</p>",
              linhas(texto, tw - 22 * k, "segoe", 15 * k) * 22 * k, mt=mt)


def _caixa_fecho(col: Coluna, texto: str, tw: float, mt: float = 16):
    k = col.k
    col.bloco(f"<p class='fch'>{_e(texto)}</p>", 28 * k + linhas(texto, tw - 32 * k, "segoe", 17 * k) * 26 * k, mt=mt)


def _caixa_exemplo(col: Coluna, texto: str, tw: float, mt: float = 14):
    k = col.k
    col.bloco(f"<p class='exm'>{_e(texto)}</p>", 24 * k + linhas(texto, tw - 28 * k, "segoe", 15 * k) * 22 * k, mt=mt)


def _dica(col: Coluna, texto: str, tw: float, mt: float = 14):
    k = col.k
    html_ = ("<div class='dc'><svg class='cur' width='18' height='18' viewBox='0 0 18 18' aria-hidden='true'>"
             "<path d='M4 2L4 14L7.2 11L9.4 16L11.3 15.2L9.1 10.3L13.6 10.3Z' fill='#0B0B0C'/></svg>"
             f"<p class='dt'>{_e(texto)}</p></div>")
    col.bloco(html_, 20 * k + linhas(texto, tw - 54 * k, "segoe", 15 * k) * 22 * k, mt=mt)


def _marcas(n: int) -> tuple:
    """Marcas e cores das faixas: três (estável, atenção, crítico) ou duas (dentro e fora do limite)."""
    if n == 2:
        return ("mk0", "mk2"), ["#A9CDB9", "#C43737"]
    return ("mk0", "mk1", "mk2"), ["#A9CDB9", "#C9821F", "#C43737"]


def _barra_faixas(col: Coluna, n: int = 3, mt: float = 8):
    cores = _marcas(n)[1]
    col.bloco("<div class='rgf'>" + "".join(f"<i style='width:{100 / n:.2f}%;background:{c}'></i>" for c in cores)
              + "</div>", 12 * col.k, mt=mt)


def _faixas_status_nota() -> list:
    """Faixas da nota, do dicionário (contas_base.NOTA["status"]): ("Estável", "nota 8 ou mais")…"""
    nome = {0: "Estável", 1: "Atenção", 2: "Crítico"}  # como a legenda do painel
    out, ant = [], None
    for op, lim, st in CB.NOTA["status"]:
        if op == ">=" and ant is None:
            out.append((nome[st], f"nota {CB._br(lim, False)} ou mais"))
        elif op == ">=":
            out.append((nome[st], f"de {CB._br(lim, False)} a {CB._br(round(ant - 0.01, 2), False)}"))
        else:
            out.append((nome[st], f"abaixo de {CB._br(ant, False)}, ou na trava"))
        ant = lim
    return out


def _faixas(col: Coluna, rubrica: str, faixas, tw: float):
    k = col.k
    if faixas == "status_nota":
        faixas = _faixas_status_nota()
    marcas = _marcas(len(faixas))[0]
    sub = Coluna(k)
    sub.bloco(f"<p class='gr'>{_e(rubrica)}</p>", 16 * k)
    _barra_faixas(sub, len(faixas), mt=8)
    itens, h = [], 0.0
    for (a, b), m in zip(faixas, marcas):
        itens.append(f"<li><i class='mk {m}'></i><span><b>{_e(a)}</b> {_e(b)}</span></li>")
        h += linhas(f"{a} {b}", tw - 19 * k, "segoe", 15 * k) * 22 * k
    h += 4 * k * (len(faixas) - 1)
    sub.bloco(f"<ul class='fx'>{''.join(itens)}</ul>", h, mt=8)
    col.bloco(sub.html(), sub.h, mt=12)


def _itens_nota(col: Coluna, tw: float):
    """Os itens da Nota da obra, do dicionário (contas_base.NOTA["itens"]): nome médio (dimensão · item), fonte (planilha
    ou base) e o máximo (T1 passo 3)."""
    k = col.k
    linhas_, h = [], 0.0
    for it in CB.NOTA_ITENS:
        fonte_txt = "planilha" if it["fonte"] == "Análise Crítica" else "base"
        maximo = "até " + CB._br(CB.nota_maximo(it["cod"]), False)
        linhas_.append(f"<span><b>{_e(it['medio'])}</b></span><span class='f'>{fonte_txt}</span><span class='m'>{maximo}</span>")
        h += 22 * k
    h += 4 * k * (len(linhas_) - 1)
    sub = Coluna(k)
    sub.bloco(f"<p class='gr'>Os {valores_nota()['n_itens']} itens</p>", 16 * k)
    sub.bloco(f"<div class='ia'>{''.join(linhas_)}</div>", h, mt=8)
    col.bloco(sub.html(), sub.h, mt=14)


def _conta(col: Coluna, conta: list, tw: float):
    k = col.k
    itens, h = [], 0.0
    for i, (nome, expl, sinal) in enumerate(conta):
        hn = linhas(nome, tw - 36 * k, "barlow", 18 * k) * 24 * k
        he = linhas(expl, tw - 36 * k, "segoe", 15 * k) * 22 * k
        itens.append(f"<li><span class='sg'>{_e(sinal)}</span><div><b class='gn'>{_e(nome)}</b>"
                     f"<span class='ga'>{_e(expl)}</span></div></li>")
        h += hn + he + (10 * k if i else 0)
    col.bloco(f"<ol class='cta'>{''.join(itens)}</ol>", h, mt=16)


def _legenda_curva(col: Coluna):
    k = col.k
    leg = ("<div class='lg2'>"
           "<span><svg width='34' height='12' aria-hidden='true'><line x1='0' y1='6' x2='34' y2='6' stroke='#3B3B3F' "
           "stroke-width='2' stroke-dasharray='5 3'/></svg>previsto (tracejado)</span>"
           "<span><svg width='34' height='12' aria-hidden='true'><line x1='0' y1='6' x2='34' y2='6' stroke='#0B0B0C' "
           "stroke-width='2.5'/></svg>executado (sólido)</span>"
           "<span><i class='hach' style='display:inline-block;width:34px;height:12px;vertical-align:middle;margin-right:6px'></i>"
           "atraso, entre as linhas</span></div>")
    col.bloco(leg, 2 * 22 * k + 6 * k, mt=14)


def _legenda_mes(col: Coluna):
    k = col.k
    leg = ("<div class='lg1'><span><i class='sw' style='background:#0B0B0C'></i>barra cheia: resultado</span>"
           "<span><i class='hach sw'></i>hachurada: sem estoque e adiantamentos</span></div>")
    col.bloco(leg, 2 * 22 * k + 6 * k, mt=14)


def _cabecalho(passo: dict, tw: float, k: float) -> Coluna:
    """Cabeçalho do card grande, na largura toda: título e abertura (e a leitura, no mês)."""
    c = passo.get("conteudo") or {}
    col = Coluna(k)
    titulo = passo["titulo"]
    col.bloco(f"<h2 class='gt'>{_e(titulo)}</h2>", linhas(titulo, tw, "barlow", 30 * k) * 36 * k)
    for item in ORDEM_CABECALHO[passo["id"]]:
        if item == "legenda_curva":
            _legenda_curva(col)
        elif c.get(item):
            _gx(col, c[item], tw, mt=12)
    return col


def _texto_palco(passo: dict) -> tuple[str, str]:
    """Texto do fim do balão: a dica (com ícone de cursor); sem dica, a nota (sem ícone). Nos cards com colunas fixas, a
    nota já está na coluna, e o fim fica vazio."""
    if passo["id"] in COLUNAS_FIXAS:
        return "", ""
    c = passo.get("conteudo") or {}
    dica = c.get("dica") or passo.get("dica") or ""
    if dica:
        return dica, "dica"
    if c.get("nota"):
        return c["nota"], "nota"
    return "", ""


def _infog_itens(passo: dict, tw: float, k: float, itens: list) -> Coluna:
    """Infográfico do card grande com os campos dados, na ordem de leitura. Todo campo é opcional. A dica e, sem dica, a
    nota vão ao fim do balão (ver _texto_palco), por isso não entram aqui."""
    c = passo.get("conteudo") or {}
    rubrica = c.get("faixas_titulo") or RUBRICA_FAIXAS.get(passo["id"], "Faixas")
    col = Coluna(k)
    for item in itens:
        if item == "itens" and c.get("itens_nota"):
            _itens_nota(col, tw)
        elif item == "regra" and c.get("regra_sinal"):
            _gx(col, c["regra_sinal"], tw, mt=14)
        elif item == "exemplo" and c.get("exemplo"):
            _caixa_exemplo(col, c["exemplo"], tw, mt=14)
        elif item == "faixas" and c.get("faixas"):
            _faixas(col, rubrica, c["faixas"], tw)
        elif item == "pendente" and c.get("pendente"):
            _pendente(col, c["pendente"], tw, mt=12)
        elif item == "nota" and c.get("nota") and _texto_palco(passo)[1] != "nota":
            _ga(col, c["nota"], tw, mt=8)
        elif item == "conta" and c.get("conta"):
            _conta(col, c["conta"], tw)
        elif item == "fecho" and c.get("fecho"):
            _caixa_fecho(col, c["fecho"], tw, mt=14 if passo["id"] == "CURVA" else 16)
        elif item == "legenda_curva":
            _legenda_curva(col)
        elif item == "legenda_mes":
            _legenda_mes(col)
    return col


def _infog(passo: dict, tw: float, k: float) -> Coluna:
    """Infográfico do card grande, na ordem de leitura de ORDEM_INFOG."""
    return _infog_itens(passo, tw, k, ORDEM_INFOG[passo["id"]])


def _altura_trecho(blocos: list, i: int, j: int) -> float:
    """Altura de blocos[i:j] numa coluna: as margens valem entre blocos (não no primeiro)."""
    return sum(h + (mt if k > i else 0) for k, (_, h, mt) in zip(range(i, j), blocos[i:j]))


def _cortes(blocos: list, i: int, j: int, c: int) -> tuple[float, list]:
    """Divide blocos[i:j] em c colunas contíguas, com a menor altura para a mais alta. Devolve (altura, [(a, b)...])."""
    if c == 1:
        return _altura_trecho(blocos, i, j), [(i, j)]
    melhor = None
    for m in range(i + 1, j - c + 2):
        h1 = _altura_trecho(blocos, i, m)
        h2, resto = _cortes(blocos, m, j, c - 1)
        if melhor is None or max(h1, h2) < melhor[0]:
            melhor = (max(h1, h2), [(i, m)] + resto)
    return melhor


def _montar_colunas(blocos: list, trechos: list) -> list:
    colunas = []
    for a, b in trechos:
        col = Coluna(1.0)
        for html_, h, mt in blocos[a:b]:
            col.bloco(html_, h, mt)
        colunas.append(col)
    return colunas


def _infog_colunas(passo: dict, tw_total: float, c_max: int, col_min: float = COL_MIN_W) -> tuple[float, dict | None]:
    """Infográfico (sem a dica) em 1 ou até c_max colunas: a disposição de menor altura; em empate, a de menos colunas."""
    melhor = None
    for c in range(1, c_max + 1):
        tw_c = (tw_total - COL_GAP * (c - 1)) / c
        if c > 1 and tw_c < col_min:
            break
        avisos_antes = len(AVISOS)
        blocos = _infog(passo, tw_c, 1.0).registro
        if len(AVISOS) > avisos_antes and c > 1:   # pastilha não cabe nesta largura: descarta a disposição
            del AVISOS[avisos_antes:]
            continue
        if not blocos:
            return 0.0, None
        if c > len(blocos):
            break
        h, trechos = _cortes(blocos, 0, len(blocos), c)
        if melhor is None or h < melhor[0] - 1:
            melhor = (h, {"c": c, "tw": tw_c, "larguras": [tw_c] * c, "colunas": _montar_colunas(blocos, trechos)})
    return melhor


def _hits(ctl: dict, bx: int, by: int) -> dict:
    """Botões transparentes do Power BI, no canvas: exatamente sobre o desenho (centro igual, altura 56, sem sobreposição).
    Voltar → anterior; Seguir/Concluir → próximo; Pular → fecha. Sem o botão, a área é 1 × 1 e fica oculta."""
    def area(b, w, h, cy_b):
        return (round(bx + b["x"]), round(by + cy_b - 28), w, h)
    seg = ctl["seguir"]
    prox = area(seg, SEGUIR_W, 56, seg["y"] + BOTAO_H / 2)
    ant = area(ctl["voltar"], VOLTAR_W, 56, ctl["voltar"]["y"] + BOTAO_H / 2) if "voltar" in ctl else (0, 0, 1, 1)
    if "pular" in ctl:
        p = ctl["pular"]
        fecha = (round(bx + p["x"]), round(by + p["y"]), PULAR_W, PULAR_H)
    else:
        fecha = (0, 0, 1, 1)
    return {"ant": ant, "prox": prox, "fecha": fecha}


def _saida_geo(tela, passo, total, R, pn, nar, rosto, bal, texto, lado_bq, tip, ctl, hits, canto, encolheu, lig,
               cand="", valido=True):
    bx, by, w, bh = bal
    tx, ty = tip[0] - bx, tip[1] - by
    return {"n": passo["n"], "id": passo["id"], "tipo": passo["tipo"], "total": total, "recorte": R, "tela": tela,
            "pose": pn, "narrador": {"x": nar[0], "y": nar[1], "w": nar[2], "h": nar[3]}, "rosto": rosto,
            "balao": {"x": bx, "y": by, "w": w, "h": bh}, "biquinho": {"lado": lado_bq, "tx": tx, "ty": ty},
            "ligacao": lig, "texto": texto, "controles": ctl, "hits": hits, "canto": canto,
            "layout": "grande" if passo["tipo"] == "grande" else "comum", "cand": cand, "valido": valido,
            "card": {"x": bx, "y": by, "w": w, "h": bh}, "lado": lado_bq, "lado_pedido": passo.get("lado"),
            "personagem": canto, "k": 1.0, "reduzido": encolheu, "cota": lig, "forma": "balao"}


def _rosto(nar: tuple, pn: int) -> dict:
    g = gestor_geometria(pn)
    return {"esq": nar[0] + g["esq"] * nar[2], "dir": nar[0] + g["dir"] * nar[2], "topo": nar[1] + g["topo"] * nar[3],
            "rosto": nar[1] + g["rosto"] * nar[3], "cx": nar[0] + g["cx"] * nar[2], "cy": nar[1] + g["cy"] * nar[3]}




@functools.lru_cache(maxsize=None)
def _pontos_gestor(n: int, nh: int) -> tuple:
    """Pontos opacos (alfa ≥ 32) do recorte do gestor na altura nh, em grade de 2 px, relativos ao canto superior esquerdo."""
    import numpy as np
    alfa = _alfa_gestor(n)
    nw = round(nh * gestor_geometria(n)["asp"])
    arr = np.asarray(alfa.resize((nw, nh), Image.BILINEAR))
    ys, xs = np.nonzero(arr[::2, ::2] >= 32)
    return xs * 2.0, ys * 2.0


def _pose_existe(n: int) -> bool:
    """A pose n tem recorte do narrador gerado (poses_busto.py --narrador)."""
    return bool(sorted(NARRADOR_DIR.glob(f"P{n}-*.png")))


def _pose_disponivel(n: int) -> bool:
    """A pose n entra na busca: tem recorte, ou nenhuma pose tem (silhuetas provisórias de todas, ver
    _recorte_provisorio). Com parte das poses recortada, vale só o que existe, como antes."""
    return _pose_existe(n) or not any(_pose_existe(k) for k in POSES)


def angulo_foco(R: dict, pn: int, x: int, nh: int, nw: int) -> tuple[float, str]:
    """Ângulo θ (graus) da linha do centro do rosto do gestor ao CENTRO do foco: 0° na horizontal, 90° para cima
    (negativo se o centro do foco está abaixo do rosto). Devolve (θ, lado do foco: "esq" ou "dir"). Só registro."""
    g = gestor_geometria(pn)
    ox, oy = x + g["cx"] * nw, ALTURA - nh + g["cy"] * nh
    fx, fy = R["x"] + R["w"] / 2, R["y"] + R["h"] / 2
    lado = "esq" if fx < ox else "dir"
    if fx == ox and fy == oy:
        return 90.0, lado
    return math.degrees(math.atan2(oy - fy, abs(fx - ox))), lado


def faixa_do_passo(R: dict, pn: int, nar: tuple) -> tuple[str, str]:
    """Faixa da pose pela relação entre o foco e o gestor na posição de base (a mais perto do foco sem cobri-lo, entre
    todas as poses que apontam), regra do Alisson (08/10):
    - "cima" (P7/P8): o centro do foco está acima do topo da cabeça e o x do foco cobre o centro do rosto;
    - "diagonal" (P9/P10): o centro do foco está acima do topo da cabeça e deslocado para o lado;
    - "lateral" (P2/P3): o centro do foco está na altura do gestor ou abaixo do topo da cabeça.
    Devolve (faixa, lado do foco)."""
    x, y, nw, nh = nar
    hx = x + gestor_geometria(pn)["cx"] * nw
    topo = y + gestor_geometria(pn)["topo"] * nh      # topo do capacete (na P7/P8 o recorte começa na mão)
    fx, fy = R["x"] + R["w"] / 2, R["y"] + R["h"] / 2
    lado = "esq" if fx < hx else "dir"
    if fy < topo:
        return ("cima" if R["x"] <= hx <= R["x2"] else "diagonal"), lado
    return "lateral", lado


def _aponta_certo(direcao: str, R: dict, pn: int, x: int, nh: int, nw: int, cabeca: float) -> bool:
    """Lado do dedo: "lado-esq" (P2, P9) só com o centro do foco à esquerda do rosto, "lado-dir" (P3, P10) à direita;
    "cima" (P7, P8) em qualquer posição. (`cabeca` fica na assinatura para a checagem.)"""
    if direcao == "cima":
        return True
    hx = x + gestor_geometria(pn)["cx"] * nw
    fx = R["x"] + R["w"] / 2
    return fx < hx if direcao == "lado-esq" else fx > hx


def _anota_angulo(geo: dict, R: dict, pn: int, nar: tuple, ges: dict | None = None) -> None:
    """Grava no passo θ ao centro do foco, a faixa decidida na posição de base e se a diagonal ficou com a P2/P3 por
    falta da P9/P10."""
    theta, lado = angulo_foco(R, pn, nar[0], nar[3], nar[2])
    geo["angulo"] = round(theta, 1)
    geo["lado_foco"] = lado
    geo["faixa"] = (ges or {}).get("faixa")
    geo["base"] = (ges or {}).get("base")
    geo["faixa_nao_cabe"] = bool((ges or {}).get("faixa_nao_cabe"))
    geo["diagonal_faltando"] = geo["faixa"] == "diagonal" and pn in (2, 3)


def _poses_do_passo(passo: dict, total: int, grande: bool, fixas=None) -> list:
    """Poses que o gestor pode usar, com a direção do dedo. Regra do Alisson (08/10): em todo passo o dedo aponta para o
    foco; só o passo 1 (P1, acenando) e o último (P5, polegar) fogem dela. Nos demais, só as poses que apontam, pela
    faixa (faixa_do_passo): P2/P3 (lateral), P9/P10 (diagonal), P7/P8 (para cima). A P6 (prancheta) e a P4 (sem direção)
    não entram mais: o dedo da P6 aponta para a prancheta, à direita, e no card grande o foco ficava à esquerda."""
    if isinstance(fixas, tuple) and fixas[0] == "faixa":
        _, faixa, lado = fixas
        if faixa == "cima":
            return [(n, "cima") for n in (7, 8) if _pose_disponivel(n)]
        n = 9 if lado == "esq" else 10
        if faixa == "diagonal" and _pose_disponivel(n):
            return [(n, "lado-" + lado)]
        return [(2 if lado == "esq" else 3, "lado-" + lado)]
    if fixas is not None and fixas != "aponta":
        return [(p, None) for p in fixas]
    if fixas is None:
        if passo["n"] == total:
            return [(5, None)]
        if passo["n"] == 1:
            return [(_pose_inicial(passo), None)]
    lista = [(2, "lado-esq"), (3, "lado-dir")]
    for n, direcao in ((7, "cima"), (8, "cima"), (9, "lado-esq"), (10, "lado-dir")):
        if _pose_disponivel(n):
            lista.append((n, direcao))
    return lista


def _pose_preferida(passo: dict, total: int, grande: bool, fixas=None):
    """Pose preferida do passo: P1 no passo 1, P5 no último, P6 no card grande (ganha 16 px de desconto na busca)."""
    if fixas is not None:
        return None
    if passo["n"] == 1:
        return _pose_inicial(passo)
    if passo["n"] == total:
        return 5
    return 6 if grande else None


def _pose_inicial(passo: dict) -> int:
    """Pose do passo 1: a do passos.json se for uma das poses sem direção (P1 acenando; P11 vistoria, na T5); senão P1."""
    pn = int(passo["pose"][1:])
    return pn if pn in POSES_SEM_DIRECAO and _pose_disponivel(pn) else 1


@functools.lru_cache(maxsize=None)
def ponta_dedo(pn: int, nh: int) -> tuple[float, float]:
    """Ponta do dedo (x, y) relativa ao canto do gestor na altura nh: P2 o pixel mais à esquerda, P3 o mais à direita,
    P7/P8 o mais alto da mão erguida (fora da faixa da cabeça), P9/P10 o mais extremo na diagonal, P6 o mais extremo
    na direção (1; 0,3) entre os pixels de pele à direita do rosto."""
    import numpy as np
    nw = round(nh * gestor_geometria(pn)["asp"])
    ox, oy = _pontos_gestor(pn, nh)
    cab = nh * CABECA_FRAC[pn] / gestor_geometria(pn)["frac"]
    if pn == 2:
        k = int(np.argmin(ox))
    elif pn == 3:
        k = int(np.argmax(ox))
    elif pn in (1, 7, 8):
        cx_px = gestor_geometria(pn)["cx"] * nw
        mao = (ox > cx_px + 0.45 * cab) if pn == 8 else (ox < cx_px - 0.45 * cab)
        if mao.any():
            idx = np.nonzero(mao)[0]
            k = int(idx[int(np.argmin(oy[idx]))])
        else:
            k = int(np.argmax((ox if pn == 8 else -ox) - oy))
    elif pn in (9, 10):
        k = int(np.argmax((-ox if pn == 9 else ox) - oy))
    else:
        k = int(np.argmax(0.9578 * ox + 0.2873 * oy))
    return float(ox[k]), float(oy[k])


def angulo_dedo(pn: int, nar: tuple, R: dict) -> float:
    """Ângulo (graus) entre a direção do dedo da pose e o vetor da ponta do dedo ao ponto mais próximo do foco. 0 se a
    ponta está dentro do foco; 180 para pose sem direção (P1, P4, P5)."""
    if pn not in DIRECAO_DEDO:
        return 180.0
    tx, ty = ponta_dedo(pn, nar[3])
    tx, ty = nar[0] + tx, nar[1] + ty
    vx, vy = _ajusta(tx, R["x"], R["x2"]) - tx, _ajusta(ty, R["y"], R["y2"]) - ty
    n = math.hypot(vx, vy)
    if n < 1e-6:
        return 0.0
    dx, dy = DIRECAO_DEDO[pn]
    c = (vx * dx + vy * dy) / (n * math.hypot(dx, dy))
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def raio_no_foco(pn: int, nar: tuple, R: dict, folga: float = RAIO_FOLGA) -> bool:
    """Condição do dono (28/10/2026, Lia): o dedo aponta para o visual em foco. O raio que sai da ponta do dedo na
    direção medida da pose (DIRECAO_DEDO) tem de cruzar o recorte do foco aumentado em `folga` px. Só o ângulo ao ponto
    mais perto (angulo_dedo) deixava passar foco largo com o dedo apontando para o lado dele (T1 passo 8: a P9 apontava
    para o título, à esquerda do funil)."""
    if pn not in DIRECAO_DEDO:
        return True
    tx, ty = ponta_dedo(pn, nar[3])
    tx, ty = nar[0] + tx, nar[1] + ty
    dx, dy = DIRECAO_DEDO[pn]
    t0, t1 = 0.0, float("inf")
    for p, d, lo, hi in ((tx, dx, R["x"] - folga, R["x2"] + folga), (ty, dy, R["y"] - folga, R["y2"] + folga)):
        if abs(d) < 1e-9:
            if not lo <= p <= hi:
                return False
            continue
        a, b = (lo - p) / d, (hi - p) / d
        t0, t1 = max(t0, min(a, b)), min(t1, max(a, b))
    return t0 <= t1


def _candidatos(pn: int, cabeca: float, R: dict, obstaculos: list) -> dict:
    """Para a pose pn e a cabeça dada, por posição x (borda esquerda do gestor, de 2 em 2 px): a distância do gesto ao
    recorte e se o gestor cabe, sem pixel opaco na caixa do recorte + 24 e com a folga de cada obstáculo."""
    import numpy as np
    nh = round(gestor_geometria(pn)["frac"] * cabeca / CABECA_FRAC[pn])
    nw = round(nh * gestor_geometria(pn)["asp"])
    ox, oy = _pontos_gestor(pn, nh)
    xs = np.arange(BALAO_MARGEM, LARGURA - BALAO_MARGEM - nw + 1, 2)
    if xs.size == 0 or ox.size == 0:
        return {"nh": nh, "nw": nw, "xs": xs, "d": np.zeros(0), "ok": np.zeros(0, dtype=bool)}
    px = xs[:, None] + ox[None, :]
    py = (ALTURA - nh) + oy[None, :]
    if pn == 2:
        g = ox <= ox.min() + 12
    elif pn == 3:
        g = ox >= ox.max() - 12
    elif pn in (1, 7, 8):
        # ponta do dedo: o pixel mais alto da mão erguida, que fica ao lado da cabeça (P1 e P7 à esquerda, P8 à
        # direita). Nas poses do narrador NB a mão fica abaixo do topo do cabelo, então "o pixel mais alto" do recorte
        # seria o cabelo: só contam as colunas a mais de 0,45 cabeça do centro da cabeça. Sem pixel ali, vale a diagonal.
        cx_px = gestor_geometria(pn)["cx"] * nw
        mao = (ox > cx_px + 0.45 * cabeca) if pn == 8 else (ox < cx_px - 0.45 * cabeca)
        g = np.zeros(ox.shape, dtype=bool)
        if mao.any():
            idx = np.nonzero(mao)[0]
            g[idx[int(np.argmin(oy[idx]))]] = True
        else:
            direcao_ponta = (1.0, -1.0) if pn == 8 else (-1.0, -1.0)
            g[int(np.argmax(direcao_ponta[0] * ox + direcao_ponta[1] * oy))] = True
    elif pn in (9, 10):
        # ponta do dedo na diagonal: o pixel mais extremo para cima e para o lado (máximo de −x − y na P9, x − y na P10)
        g = np.zeros(ox.shape, dtype=bool)
        g[int(np.argmax((-ox if pn == 9 else ox) - oy))] = True
    else:
        g = np.ones(ox.shape, dtype=bool)

    def dist(rect, qx, qy):
        x, y, w, h = rect
        ddx = np.maximum(np.maximum(x - qx, qx - (x + w)), 0)
        ddy = np.maximum(np.maximum(y - qy, qy - (y + h)), 0)
        return np.sqrt(ddx * ddx + ddy * ddy)

    d = dist((R["x"], R["y"], R["w"], R["h"]), px[:, g], py[:, g]).min(axis=1)
    F = R.get("folga", NARRADOR_FOLGA)   # negativo no último recurso: o gesto pode entrar até FOCO_INVASAO_MAX px
    dentro = (px >= R["x"] - F) & (px <= R["x"] + R["w"] + F) & (py >= R["y"] - F) & (py <= R["y"] + R["h"] + F)
    ok = ~dentro.any(axis=1)
    for rect, folga in obstaculos:
        ok &= dist(rect, px, py).min(axis=1) >= folga
    return {"nh": nh, "nw": nw, "xs": xs, "d": d, "ok": ok}


def _escolhe_com_cabeca(passo: dict, total: int, R: dict, grande: bool, obstaculos: list, aceita, fixas, cab,
                        limite_chave=None):
    """Melhor posição do gestor com a cabeça `cab`. Para cada pose permitida, varre as posições por distância crescente e
    fica com a primeira em que o balão e a cauda passam em `aceita`. A chave é a distância menos 16 px quando a pose
    aponta para o foco ou é a preferida; vence a menor chave. Com `limite_chave`, só aceita chaves menores (prova)."""
    import numpy as np
    preferida = _pose_preferida(passo, total, grande, fixas)
    teto = float("inf") if limite_chave is None else limite_chave
    melhor = None
    for pn, direcao in _poses_do_passo(passo, total, grande, fixas):
        c = _candidatos(pn, cab, R, obstaculos)
        bonus = 16 if (pn == preferida or direcao) else 0
        nw, nh = c["nw"], c["nh"]
        for i in np.argsort(c["d"], kind="stable"):
            if not c["ok"][i]:
                continue
            x = int(c["xs"][i])
            dv = float(c["d"][i])
            chave = dv - bonus
            corte = teto if melhor is None else min(teto, melhor["chave"])
            if chave >= corte:
                break
            if direcao is not None and not _aponta_certo(direcao, R, pn, x, nh, nw, cab):
                continue
            nar = (x, ALTURA - nh, nw, nh)
            if direcao is not None and angulo_dedo(pn, nar, R) > ANG_DEDO_MAX:
                continue
            if direcao is not None and not raio_no_foco(pn, nar, R):
                continue
            if aceita is None or aceita(pn, cab, nar):
                melhor = {"chave": chave, "pn": pn, "cabeca": cab, "nar": nar, "d": dv}
                break
    return melhor


def _escolhe_gestor(passo: dict, total: int, R: dict, grande: bool, obstaculos: list, aceita=None, fixas=None):
    """Gestor na base da tela: a posição mais perto do foco, com balão e cauda válidos (aceita(pose, cabeça, retângulo)).
    Cabeça de 198 (216 no grande); se a melhor ficar a mais de 120 px do foco, reduz a cabeça em degraus (180, 165, 153)
    e repete a busca."""
    base = NARRADOR_CABECA_GRANDE if grande else NARRADOR_CABECA
    melhor_geral = None
    for cab in [base] + [t for t in (180, 165, 153) if t < base]:
        escolha = _escolhe_com_cabeca(passo, total, R, grande, obstaculos, aceita, fixas, cab)
        if escolha is None:
            continue
        escolha["fixas"] = fixas
        if escolha["d"] <= 120:
            melhor_geral = escolha
            break
        if melhor_geral is None or escolha["d"] < melhor_geral["d"]:
            melhor_geral = escolha
    if melhor_geral is not None and fixas in (None, "aponta") and _poses_do_passo(passo, total, grande, fixas)[0][1]:
        # posição de base (a mais perto do foco entre as poses que apontam) -> faixa -> busca só com a pose da faixa
        faixa, lado = faixa_do_passo(R, melhor_geral["pn"], melhor_geral["nar"])
        base = (melhor_geral["pn"], tuple(melhor_geral["nar"]))
        restrita = _escolhe_gestor(passo, total, R, grande, obstaculos, aceita, fixas=("faixa", faixa, lado))
        if restrita is not None:
            melhor_geral = restrita
        else:
            melhor_geral["faixa_nao_cabe"] = True
        melhor_geral["faixa"], melhor_geral["base"] = faixa, base
    return melhor_geral


def _prova_de(passo, total, R, grande, obstaculos, aceita, fixas, ges) -> dict:
    """Dados para a prova do mínimo, guardados no passo."""
    return {"passo": passo, "total": total, "R": R, "grande": grande, "obstaculos": obstaculos, "aceita": aceita,
            "fixas": fixas, "cabeca": ges["cabeca"], "d": ges["d"], "chave": ges["chave"]}


def prova_minimo(geo: dict):
    """Prova do mínimo: repete a busca do passo com as mesmas poses, cabeça, obstáculos e aceite, e procura posição válida
    com chave menor que a escolhida (varredura de 2 px). Devolve {d, x, pn} da melhor, ou None se não existe."""
    c = geo["_prova"]
    r = _escolhe_com_cabeca(c["passo"], c["total"], c["R"], c["grande"], c["obstaculos"], c["aceita"], c["fixas"],
                            c["cabeca"], limite_chave=c["chave"] - 0.5)
    return None if r is None else {"d": r["d"], "x": r["nar"][0], "pn": r["pn"]}


def _texto_de(passo: dict, total: int, cont: dict, grande: bool) -> dict:
    """Blocos de texto do balão, em posições relativas ao balão: selo, título, texto, dica e infográfico."""
    y0 = BALAO_PAD_T + SELO_H + SELO_GAP
    tw = cont["tw"]
    texto: dict = {"selo_w": medir(f"Passo {passo['n']} de {total}", "segoe_sb", 13) + 24}
    if grande:
        texto["cab"] = (BALAO_PAD_X, y0, tw)
        y_fim = y0 + cont["cab"].h
        texto["infog"] = []
        if cont["inf"]:
            y_inf = y_fim + INF_GAP
            x = BALAO_PAD_X
            for col, lw in zip(cont["inf"]["colunas"], cont["inf"]["larguras"]):
                texto["infog"].append((x, y_inf, lw, col.html()))
                x += lw + COL_GAP
            y_fim = y_inf + cont["inf_h"]
    else:
        texto["titulo"] = (BALAO_PAD_X, y0, tw)
        y_fim = y0 + cont["T"] * 36
        if cont["L"]:
            texto["texto"] = (BALAO_PAD_X, y_fim + TITULO_TEXTO, tw)
            y_fim = y_fim + TITULO_TEXTO + cont["L"] * 26
    if cont["D"]:
        # a caixa da dica tem a largura toda do texto: o cursor (16 + 8 de vão) fica dentro dela e o texto quebra em
        # tw − 24, que é a largura usada na conta das linhas. Antes a caixa já descontava os 24 e o cursor descontava de
        # novo: o texto quebrava em tw − 48 e, no T4 passo 6, a dica foi para 2 linhas e encostou nos controles (08/10).
        texto["dica"] = (BALAO_PAD_X, y_fim + TEXTO_DICA, tw, cont["tipo"], cont["fim"], cont["D"])
    return texto


def _geometria_abaixo(tela: str, passo: dict, total: int, R: dict) -> dict:
    """T4 passo 3 (MES): balão abaixo do foco, de x do foco até 1420 (largura ≤ 1068; estreita se a pose da faixa não
    couber ao lado) e y = base do anel + 40. Conteúdo:
    à esquerda título, abertura e leitura (ou legenda); à direita o infográfico em 1 a 3 colunas internas e a dica. O
    gestor é posto pela busca, sem tocar o balão nem o foco. Cauda curva para a cabeça."""
    bx = passo["foco"]["x"]
    by = R["y2"] + AFASTA
    bh_max = ALTURA - MARGEM - by
    fim, tipo = _texto_palco(passo)
    w0 = min(1420 - bx, 1068)
    R0 = R
    escolhido = None
    # o balão estreita de 40 em 40 px (até 900) enquanto a pose da faixa não couber ao lado dele: no T4 passo 3 a P9
    # (foco acima e à esquerda) precisa de ~470 px à direita do balão
    opcoes = [("esq", w) for w in range(w0, min(w0, 900) - 1, -40)] + [("dir", w) for w in range(w0, min(w0, 900) - 1, -40)]
    for ancora, w in opcoes:
        # "esq": o balão começa no x do foco (o gestor fica à direita dele); "dir": o balão encosta na margem direita e o
        # gestor fica à esquerda, embaixo do foco (é o que deixa o dedo apontar para o foco quando ele está acima e à esquerda)
        bx = passo["foco"]["x"] if ancora == "esq" else LARGURA - BALAO_MARGEM - w
        melhor = None
        for col_l in (480, 520, 560, 600, 640, 680):
            col_r = w - 2 * BALAO_PAD_X - col_l - COL_GAP
            if col_r < COL_MIN_W:
                continue
            cab = _cabecalho(passo, col_l, 1.0)
            h_r, inf = _infog_colunas(passo, col_r, 3, col_min=200)
            D = linhas(fim, col_r - (24 if tipo == "dica" else 0), "segoe", 15) if fim else 0
            cont_h = max(cab.h, h_r + (TEXTO_DICA + D * 22 if D else 0))
            bh_c = math.ceil(BALAO_PAD_T + SELO_H + SELO_GAP + cont_h + CONTROLES_GAP + BOTAO_H + BALAO_PAD_B)
            if melhor is None or bh_c < melhor[0]:
                melhor = (bh_c, col_l, col_r, cab, inf, h_r, D)
        if melhor is None or melhor[0] > bh_max:
            continue
        bal = (bx, by, w, melhor[0])
        obst = [(bal, 16)]
        for Rf in (R0, dict(R0, folga=-FOCO_INVASAO_MAX)):   # último recurso: o gesto pode entrar até 40 px no foco

            def aceita_abaixo(pn, cabeca, nar, bal=bal, Rf=Rf):
                return _cauda(bal, nar, pn, Rf, _rosto(nar, pn)["cx"]) is not None

            g_ = _escolhe_gestor(passo, total, Rf, True, obst, aceita_abaixo)
            if g_ is not None:
                break
        if g_ is None:
            continue
        if escolhido is None:
            escolhido = (w, melhor, bal, obst, Rf, aceita_abaixo, g_)
        if not g_.get("faixa_nao_cabe"):
            escolhido = (w, melhor, bal, obst, Rf, aceita_abaixo, g_)
            break
    if escolhido is None:
        raise lib.ErroDeclaracao(f"{tela} passo {passo['n']}: sem posição para o gestor abaixo do foco")
    w, melhor, bal, obst, R, aceita_abaixo, ges = escolhido
    bx = bal[0]
    bh, col_l, col_r, cab, inf, h_r, D = melhor
    pn, nar, cabeca = ges["pn"], ges["nar"], ges["cabeca"]
    rosto = _rosto(nar, pn)
    cau = _cauda(bal, nar, pn, R, rosto["cx"])
    ctl = _controles(passo["n"], total, w, bh, tela)
    hits = _hits(ctl, bx, by)
    lig = _ligacao(bal, R)
    y0 = BALAO_PAD_T + SELO_H + SELO_GAP
    texto: dict = {"selo_w": medir(f"Passo {passo['n']} de {total}", "segoe_sb", 13) + 24}
    texto["cab"] = (BALAO_PAD_X, y0, col_l)
    texto["infog"] = []
    if inf:
        x = BALAO_PAD_X + col_l + COL_GAP
        for col, lw in zip(inf["colunas"], inf["larguras"]):
            texto["infog"].append((x, y0, lw, col.html()))
            x += lw + COL_GAP
    if D:
        texto["dica"] = (BALAO_PAD_X + col_l + COL_GAP, y0 + h_r + TEXTO_DICA, col_r, tipo, fim, D)
    canto = "direita" if nar[0] + nar[2] / 2 > 960 else "esquerda"
    geo = _saida_geo(tela, passo, total, R, pn, nar, rosto, bal, texto, cau["aresta"] if cau else "baixo",
                     cau["tip"] if cau else (bx, by), ctl, hits, canto, cabeca < NARRADOR_CABECA_GRANDE, lig,
                     cand="ABAIXO", valido=cau is not None and bh <= bh_max)
    _anexa_cauda(geo, cau)
    geo["distancia_gestor"] = ges["d"]
    geo["_prova"] = _prova_de(passo, total, R, True, obst, aceita_abaixo, ges.get("fixas"), ges)
    geo["foco_tocado"] = "folga" in R
    _anota_angulo(geo, R, pn, nar, ges)
    return geo


def _geometria_direita(tela: str, passo: dict, total: int, R: dict) -> dict:
    """T3 passo 3 (CURVA): balão à direita do anel, 40 px depois da borda direita do foco, até a margem direita (24).
    O gestor aponta para o foco (à esquerda): sem a P6, a cauda não alcança uma cabeça na base com o balão no topo, então
    o balão desce de 20 em 20 px a partir do topo (y 24) até achar gestor e cauda válidos. Cauda curva para a cabeça."""
    bx = R["x"] + R["w"] + 40
    bw = int(LARGURA - BALAO_MARGEM - bx)
    cont = _conteudo_balao(passo, bw, 2)
    bh = int(cont["bh"])
    ges = None
    for folga in (None, -FOCO_INVASAO_MAX):
        Rf = R if folga is None else dict(R, folga=folga)   # último recurso: o gesto pode entrar até 40 px no foco
        for by in range(BALAO_MARGEM, ALTURA - BALAO_MARGEM - bh + 1, 20):
            bal = (bx, by, bw, bh)
            obst = [(bal, 16)]

            def aceita_fixo(pn, cabeca, nar, bal=bal, Rf=Rf):
                return _cauda(bal, nar, pn, Rf, _rosto(nar, pn)["cx"]) is not None

            ges = _escolhe_gestor(passo, total, Rf, True, obst, aceita_fixo)
            if ges is not None:
                break
        if ges is not None:
            R = Rf
            break
    if ges is None:
        raise lib.ErroDeclaracao(f"{tela} passo {passo['n']}: nenhuma pose que aponta para o foco cabe abaixo do balão")
    pn, nar, cabeca = ges["pn"], ges["nar"], ges["cabeca"]
    rosto = _rosto(nar, pn)
    cau = _cauda(bal, nar, pn, R, rosto["cx"])
    ctl = _controles(passo["n"], total, bw, bh, tela)
    hits = _hits(ctl, bx, by)
    lig = _ligacao(bal, R)
    texto = _texto_de(passo, total, cont, True)
    canto = "direita" if nar[0] + nar[2] / 2 > 960 else "esquerda"
    geo = _saida_geo(tela, passo, total, R, pn, nar, rosto, bal, texto, cau["aresta"] if cau else "baixo",
                     cau["tip"] if cau else (bx, by), ctl, hits, canto, cabeca < NARRADOR_CABECA_GRANDE, lig,
                     cand="DIREITA", valido=ges["d"] >= 0 and cau is not None and by + bh <= ALTURA - BALAO_MARGEM)
    _anexa_cauda(geo, cau)
    geo["distancia_gestor"] = ges["d"]
    geo["_prova"] = _prova_de(passo, total, R, True, obst, aceita_fixo, ges.get("fixas"), ges)
    geo["foco_tocado"] = "folga" in R
    _anota_angulo(geo, R, pn, nar, ges)
    return geo


def geometria(tela: str, passo: dict, total: int) -> dict:
    """Geometria de um passo: o gestor na base da tela, o mais perto do foco com balão e cauda válidos. O dedo aponta
    para o foco (faixa_do_passo e angulo_dedo ≤ 45°); só o passo 1 (P1) e o último (P5) fogem da regra. Cabeça de 198
    (216 no grande), reduzida em degraus até 153 se o foco ficar longe. T3 passo 3 (CURVA): balão à direita."""
    if tela == "T3" and passo["n"] == 3 and passo["id"] == "CURVA":
        return _geometria_direita(tela, passo, total, recorte(passo["foco"]))
    if tela in ("T3", "T4", "T5") and passo["n"] == 3 and passo["id"] in ("CURVA", "MES", "QUALIDADE"):
        return _geometria_abaixo(tela, passo, total, recorte(passo["foco"]))
    foco = passo["foco"]
    R = recorte(foco)
    grande = passo["tipo"] == "grande"
    c_max = 3 if passo["id"] in ALTURA_LIMITADA_IDS else 2
    w_opcoes = [BALAO_W_GRANDE, 700, 640, 600, BALAO_W] if grande else [BALAO_W, 520, 480]
    cache: dict = {}

    def conteudo(w: int) -> dict:
        if w not in cache:
            cache[w] = _conteudo_balao(passo, w, c_max)
        return cache[w]

    def bh_de(w: int) -> int:
        return conteudo(w)["bh"]

    def aceita_balao(pn, cabeca, nar):
        return _coloca_balao(R, nar, _rosto(nar, pn), "", w_opcoes, bh_de, longo=grande, pn=pn)["valido"]

    ges = _escolhe_gestor(passo, total, R, grande, [], aceita_balao)
    if ges is None:
        # último recurso (T4 passo 5: foco largo na base): o gesto pode entrar até 40 px no foco e o balão pode ir a 440
        R = dict(R, folga=-FOCO_INVASAO_MAX)
        w_opcoes.append(440)
        ges = _escolhe_gestor(passo, total, R, grande, [], aceita_balao)
    if ges is None:
        ges = _escolhe_gestor(passo, total, R, grande, [])
        AVISOS.append(f"{tela} passo {passo['n']}: nenhuma posição do gestor com balão válido")
    if ges is None:
        raise lib.ErroDeclaracao(f"{tela} passo {passo['n']}: sem posição para o gestor na base da tela")
    pn, nar, cabeca = ges["pn"], ges["nar"], ges["cabeca"]
    rosto = _rosto(nar, pn)
    loc = _coloca_balao(R, nar, rosto, "", w_opcoes, bh_de, longo=grande, pn=pn)
    if not loc["valido"]:
        AVISOS.append(f"{tela} passo {passo['n']}: balão sem posição válida (candidato {loc['cand']})")
    pn_json = int(passo["pose"][1:])
    if pn != pn_json:
        msg = f"{tela} passo {passo['n']}: pose P{pn_json} trocada por P{pn} (o gestor fica o mais perto do foco)"
        if msg not in REGISTROS:
            REGISTROS.append(msg)
    if cabeca < (NARRADOR_CABECA_GRANDE if grande else NARRADOR_CABECA):
        msg = f"{tela} passo {passo['n']}: cabeça do gestor reduzida para {cabeca} px (foco a mais de 120 px)"
        if msg not in REGISTROS:
            REGISTROS.append(msg)
    w, bh, bx, by = loc["w"], loc["bh"], loc["x"], loc["y"]
    cont = conteudo(w)
    ctl = _controles(passo["n"], total, w, bh, tela)
    hits = _hits(ctl, bx, by)
    lig = _ligacao((bx, by, w, bh), R)
    texto = _texto_de(passo, total, cont, grande)
    canto = "direita" if nar[0] + nar[2] / 2 > 960 else "esquerda"
    geo = _saida_geo(tela, passo, total, R, pn, nar, rosto, (bx, by, w, bh), texto, loc["lado"], loc["tip"], ctl,
                     hits, canto, cabeca < (NARRADOR_CABECA_GRANDE if grande else NARRADOR_CABECA), lig,
                     cand=loc["cand"], valido=loc["valido"])
    _anexa_cauda(geo, loc["cauda"])
    geo["distancia_gestor"] = ges["d"]
    geo["_prova"] = _prova_de(passo, total, R, grande, [], aceita_balao, ges.get("fixas"), ges)
    geo["foco_tocado"] = "folga" in R
    _anota_angulo(geo, R, pn, nar, ges)
    return geo


def _x_glifo() -> str:
    return ("<span class='xb' aria-hidden='true'><svg width='16' height='16' viewBox='0 0 16 16'>"
            "<path d='M2 2L14 14M14 2L2 14' stroke='#FFFFFF' stroke-width='2' fill='none' stroke-linecap='round'/>"
            "</svg></span>")


def _check() -> str:
    return ("<svg width='16' height='16' viewBox='0 0 16 16' aria-hidden='true'><path d='M3 8.5L6.5 12L13 4.5' "
            "stroke='currentColor' stroke-width='2.2' fill='none' stroke-linecap='round' stroke-linejoin='round'/></svg>")


def html_passo(passo: dict, geo: dict) -> list:
    """Partes do HTML do passo (v5): véu com recorte, cantoneiras e ligação ao anel; gestor fora do balão; balão com
    selo, título, texto, dica e linha de controles. A pose entra como ('pose', n)."""
    pa, total = passo["n"], geo["total"]
    R, B, N = geo["recorte"], geo["balao"], geo["narrador"]
    partes: list = [
        "<div class='u tr'>",
        f"<div class='rc' style='{_caixa(R['x'], R['y'], R['w'], R['h'])}'></div>",
    ]
    lig = geo["ligacao"]
    trecho = (f"<path d='M{_n(lig['P'][0])} {_n(lig['P'][1])}L{_n(lig['Q'][0])} {_n(lig['Q'][1])}' fill='none' "
              "stroke='#E9E0CF' stroke-width='2' stroke-dasharray='2 6' stroke-linecap='round'/>"
              f"<circle cx='{_n(lig['Q'][0])}' cy='{_n(lig['Q'][1])}' r='{PONTO_R}' fill='#E9E0CF' stroke='#0B0B0C' "
              "stroke-width='2'/>")
    partes.append("<svg class='sv' width='1920' height='1080' viewBox='0 0 1920 1080' aria-hidden='true' focusable='false'>"
                  f"<path d='{caminho_cantoneiras(R)}' fill='none' stroke='#FFFFFF' stroke-width='3' stroke-linecap='round'/>"
                  f"{trecho}</svg>")
    partes.append(f"<div class='nr' style='{_caixa(N['x'], N['y'], N['w'], N['h'])}'>")
    partes.append(("pose", geo["pose"]))
    partes.append("</div>")
    if geo["biquinho"].get("path"):
        partes.append("<svg class='bq' width='1920' height='1080' viewBox='0 0 1920 1080' aria-hidden='true' "
                      f"focusable='false'><path d='{geo['biquinho']['path']}' fill='#FFFFFF'/></svg>")
    partes.append(
        f"<section class='bl' role='dialog' aria-label='{html.escape(f'Tour guiado, passo {pa} de {total}: {passo['titulo']}', quote=True)}'"
        f" style='{_caixa(B['x'], B['y'], B['w'], B['h'])}'>")
    partes.append(f"<span class='sl' style='left:{BALAO_PAD_X}px;top:{BALAO_PAD_T}px'>Passo {pa} de {total}</span>")
    tx = geo["texto"]
    if geo["layout"] == "comum":
        x, y, w = tx["titulo"]
        partes.append(f"<h2 class='tt' style='left:{_n(x)}px;top:{_n(y)}px;width:{_n(w)}px'>{_e(passo['titulo'])}</h2>")
        if "texto" in tx:
            x, y, w = tx["texto"]
            partes.append(f"<p class='tx' style='left:{_n(x)}px;top:{_n(y)}px;width:{_n(w)}px'>{_e(passo['texto'])}</p>")
    else:
        x, y, w = tx["cab"]
        partes.append(f"<div class='gh' style='left:{_n(x)}px;top:{_n(y)}px;width:{_n(w)}px'>"
                      f"{passo_cabecalho_html(passo, w)}</div>")
        for x, y, w, conteudo in tx["infog"]:
            partes.append(f"<div class='gi' style='left:{_n(x)}px;top:{_n(y)}px;width:{_n(w)}px'>{conteudo}</div>")
    if "dica" in tx:
        x, y, w, tipo, texto_dc, _ = tx["dica"]
        cursor = ("<svg class='cur' width='16' height='16' viewBox='0 0 18 18' aria-hidden='true'>"
                  "<path d='M4 2L4 14L7.2 11L9.4 16L11.3 15.2L9.1 10.3L13.6 10.3Z' fill='#0B0B0C'/></svg>"
                  if tipo == "dica" else "")
        partes.append(f"<div class='dc' style='left:{_n(x)}px;top:{_n(y)}px;width:{_n(w)}px'>"
                      f"{cursor}<p class='dt'>{_e(texto_dc)}</p></div>")
    ctl = geo["controles"]
    r = ctl["regua"]
    traços = []
    for k in range(1, r["n"] + 1):
        cor = "#0B0B0C" if k == pa else ("rgba(11,11,12,.45)" if k < pa else "#E1E1E1")
        traços.append(f"<i style='width:{r['t']}px;background:{cor}'></i>")
    partes.append(f"<div class='rg' style='left:{_n(r['x'])}px;top:{_n(r['y'])}px;width:{_n(r['w'])}px;gap:{r['v']}px'>"
                  f"{''.join(traços)}</div>")
    if "pular" in ctl:
        p = ctl["pular"]
        partes.append(f"<span class='bt pl' style='left:{_n(p['x'])}px;top:{_n(p['y'])}px;width:{_n(p['w'])}px;"
                      f"height:{_n(p['h'])}px'>Pular</span>")
    if "voltar" in ctl:
        v = ctl["voltar"]
        partes.append(f"<span class='bt s' style='left:{_n(v['x'])}px;top:{_n(v['y'])}px;width:{_n(v['w'])}px'>← Voltar</span>")
    sg = ctl["seguir"]
    rotulo = f"Concluir {_check()}" if pa == total else "Seguir →"
    partes.append(f"<span class='bt p' style='left:{_n(sg['x'])}px;top:{_n(sg['y'])}px;width:{_n(sg['w'])}px'>{rotulo}</span>")
    partes.append("</section></div>")
    return partes


def passo_cabecalho_html(passo: dict, w: float) -> str:
    """Título e abertura (e leitura, no mês) do card grande, sem a coluna do infográfico."""
    col = _cabecalho(passo, w, 1.0)
    return col.html()


def partes_para_html(partes: list) -> str:
    """Documento sem as referências: a pose entra inline (prévia)."""
    return "".join(p if isinstance(p, str) else pose_html(p[1]) for p in partes)


# ----------------------------------------------------------------------------------------------------------- CSS
CSS_TOUR = (
    ".tr{position:fixed;inset:0;color:#0B0B0C;--k:1}"
    ".tr h2,.tr p,.tr ol,.tr ul,.tr li{margin:0;padding:0;list-style:none;font-weight:inherit;font-size:inherit}"
    ".tr .rc{position:absolute;box-sizing:border-box;border:2px solid #E9E0CF;border-radius:14px;"
    "box-shadow:0 0 0 4000px rgba(11,11,12,.6)}"
    ".tr .sv{position:absolute;left:0;top:0;overflow:visible}"
    ".tr .cd{position:absolute;box-sizing:border-box;background:#FFFFFF;border-radius:16px;"
    "box-shadow:0 0 0 1px #0B0B0C,0 12px 32px rgba(0,0,0,.22);color:#0B0B0C}"
    ".tr .cb{position:absolute;left:0;top:0;right:0;height:56px;background:#0B0B0C;border-radius:15px 15px 0 0}"
    ".tr .ch{position:absolute;left:0;top:0;right:0;height:56px}"
    ".tr .pl{position:absolute;top:0;height:56px;display:flex;align-items:center;gap:14px;white-space:nowrap}"
    ".tr .ps{font-family:'Segoe UI',system-ui,sans-serif;font-weight:600;font-size:14px;line-height:18px;"
    "letter-spacing:1.2px;text-transform:uppercase;color:#E9E0CF}"
    ".tr .rg{display:flex;gap:5px}.tr .rg i{display:block;width:18px;height:5px;border-radius:2.5px;background:#3B3B3F}"
    ".tr .rg .f{background:#E9E0CF}.tr .rg .a{background:#FFFFFF}"
    ".tr .xc{position:absolute;width:44px;height:44px}"
    ".tr .xb{position:absolute;left:0;top:0;width:44px;height:44px;border-radius:50%;display:flex;align-items:center;"
    "justify-content:center}"
    ".tr .xc:hover .xb{background:#3B3B3F}"
    ".tr .pe{position:absolute;overflow:visible}"
    ".tr .pp{display:block;width:100%;height:100%;object-fit:contain}"
    ".tr .pe-e .pp{object-position:right bottom}.tr .pe-d .pp{object-position:left bottom}"
    ".tr .ph{position:relative;width:100%;height:100%;background:#E9E0CF;border-radius:16px;overflow:hidden}"
    ".tr .ph svg{position:absolute;left:0;top:0;width:100%;height:100%}"
    ".tr .ph p{position:absolute;left:8px;right:8px;bottom:10px;font-family:'Segoe UI',system-ui,sans-serif;"
    "font-size:15px;line-height:22px;color:#3B3B3F;text-align:center}"
    ".tr .tt{position:absolute;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:30px;line-height:36px;"
    "color:#0B0B0C}"
    ".tr .tx{position:absolute;font-size:17px;line-height:26px;color:#3B3B3F}"
    ".tr .dc{position:absolute;box-sizing:border-box;display:flex;align-items:flex-start;gap:8px}"
    ".tr .dc svg{flex:none;margin-top:2px}"
    ".tr .dt{font-size:calc(15px*var(--k));line-height:calc(22px*var(--k));color:#0B0B0C}"
    ".tr .bt{position:absolute;box-sizing:border-box;height:44px;border-radius:10px;display:flex;align-items:center;"
    "justify-content:center;gap:6px;font-size:16px;line-height:22px;font-weight:600;white-space:nowrap}"
    ".tr .bt.p{background:#0B0B0C;color:#FFFFFF}"
    ".tr .bt.s{background:#FFFFFF;color:#0B0B0C;border:1.5px solid #0B0B0C}"
    ".tr .gc{position:absolute;box-sizing:border-box}"
    ".tr .gt{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:calc(30px*var(--k));"
    "line-height:calc(36px*var(--k));color:#0B0B0C}"
    ".tr .gx{font-size:calc(17px*var(--k));line-height:calc(26px*var(--k));color:#3B3B3F}"
    ".tr .ga{font-size:calc(15px*var(--k));line-height:calc(22px*var(--k));color:#3B3B3F}"
    ".tr .gr{font-family:'Segoe UI',sans-serif;font-weight:600;font-size:calc(13px*var(--k));"
    "line-height:calc(16px*var(--k));letter-spacing:1px;text-transform:uppercase;color:#3B3B3F}"
    ".tr .gn{display:block;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:calc(18px*var(--k));"
    "line-height:calc(24px*var(--k));color:#0B0B0C}"
    ".tr .bar2{display:flex;height:22px;border-radius:6px;overflow:hidden;border:1px solid #0B0B0C}"
    ".tr .bar2 i{display:flex;align-items:center;justify-content:center;font-family:'Barlow U','Segoe UI',sans-serif;"
    "font-style:normal;font-weight:600;font-size:13px;line-height:16px;min-width:0}"
    ".tr .lgn{display:grid;grid-template-columns:1fr 1fr;gap:4px 16px}"
    ".tr .lgn span{display:block;font-size:calc(15px*var(--k));line-height:calc(22px*var(--k));color:#3B3B3F}"
    ".tr .lgn b{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;color:#0B0B0C;white-space:nowrap}"
    ".tr .sw{display:inline-block;width:11px;height:11px;margin-right:6px;vertical-align:-1px}"
    ".tr .lg1{display:grid;grid-template-columns:1fr;gap:6px}"
    ".tr .lg2{display:grid;grid-template-columns:1fr 1fr;gap:6px 16px}"
    ".tr .lg2 span{display:flex;align-items:center;font-size:calc(15px*var(--k));line-height:calc(22px*var(--k));color:#3B3B3F}"
    ".tr .lg2 svg{margin-right:6px;flex:none}"
    ".tr .lg1 span{display:flex;align-items:center;font-size:calc(15px*var(--k));line-height:calc(22px*var(--k));color:#3B3B3F}"
    ".tr .lg1 svg{margin-right:6px;flex:none}"
    ".tr .pls{display:flex;gap:calc(6px*var(--k))}"
    ".tr .pls span{flex:0 0 auto;white-space:nowrap;box-sizing:border-box;border-radius:10px;padding:calc(6px*var(--k)) calc(6px*var(--k));font-size:calc(15px*var(--k));"
    "line-height:calc(22px*var(--k));color:#0B0B0C}"
    ".tr .pls .p0{background:#E1EFE7}.tr .pls .p1{background:#F6E7CF}"
    ".tr .pls .p2{background:#F7E3E3;color:#0B0B0C}"
    ".tr .pls b{display:block;font-family:'Segoe UI',system-ui,sans-serif;font-weight:600;font-size:calc(17px*var(--k));"
    "line-height:calc(22px*var(--k))}"
    ".tr .rgf{display:flex;height:12px;border-radius:6px;overflow:hidden;border:1px solid #0B0B0C}"
    ".tr .rgf i{display:block;height:100%}"
    ".tr .rgl2{position:relative;height:16px}"
    ".tr .rgl2 span{position:absolute;top:0;transform:translateX(-50%);font-size:13px;line-height:16px;color:#3B3B3F}"
    ".tr .fx{display:flex;flex-direction:column;gap:4px}"
    ".tr .fx li{display:flex;align-items:flex-start;gap:8px;font-size:calc(15px*var(--k));line-height:calc(22px*var(--k));"
    "color:#3B3B3F}"
    ".tr .fx b{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;color:#0B0B0C}"
    ".tr .exm{background:#E9E0CF;border-radius:10px;padding:12px 14px;font-size:calc(15px*var(--k));"
    "line-height:calc(22px*var(--k));color:#0B0B0C}"
    ".tr .fch{background:#E9E0CF;border-radius:10px;padding:14px 16px;font-size:calc(17px*var(--k));"
    "line-height:calc(26px*var(--k));color:#0B0B0C}"
    ".tr .cta{display:flex;flex-direction:column;gap:10px}"
    ".tr .cta li{display:grid;grid-template-columns:28px 1fr;column-gap:8px;align-items:start}"
    ".tr .cta .sg{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:calc(24px*var(--k));"
    "line-height:calc(24px*var(--k));color:#0B0B0C}"
    ".tr .cta .ga{display:block}"
    ".tr .gh,.tr .gi{position:absolute;box-sizing:border-box}"
    ".tr .ia{display:grid;grid-template-columns:1fr auto auto;column-gap:calc(12px*var(--k));row-gap:calc(4px*var(--k))}"
    ".tr .ia span{font-size:calc(15px*var(--k));line-height:calc(22px*var(--k));color:#3B3B3F;white-space:nowrap}"
    ".tr .ia b{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;color:#0B0B0C}"
    ".tr .ia .f{color:#6B6B70}"
    ".tr .ia .m{text-align:right;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;color:#0B0B0C}"
    ".tr .mm{display:inline-block;box-sizing:border-box;width:14px;height:14px;border:1px dashed #3B3B3F;"
    "margin-right:8px;vertical-align:-2px}"
    ".tr .g2{display:grid;grid-template-columns:1fr 1fr;column-gap:calc(32px*var(--k))}"
    ".tr .g2>div{min-width:0}"
    ".tr .bl{position:absolute;box-sizing:border-box;background:#FFFFFF;border-radius:24px;"
    "box-shadow:0 18px 48px rgba(11,11,12,.28);color:#0B0B0C}"
    ".tr .bq{position:absolute;left:0;top:0;overflow:visible;pointer-events:none;filter:drop-shadow(0 18px 48px rgba(11,11,12,.28))}"
    ".tr .nr{position:absolute;overflow:visible}"
    ".tr .sl{position:absolute;display:inline-flex;align-items:center;height:26px;padding:0 12px;box-sizing:border-box;"
    "border-radius:999px;background:#E9E0CF;color:#0B0B0C;font-family:'Segoe UI',system-ui,sans-serif;"
    "font-weight:600;font-size:13px;line-height:18px;white-space:nowrap}"
    ".tr .rg{position:absolute;height:4px;display:flex;align-items:center}"
    ".tr .rg i{display:block;height:4px;border-radius:2px}"
    ".tr .bt{border-radius:12px}"
    ".tr .bt.pl{background:transparent;color:#6B6B70;font-weight:400;font-size:15px;border:0}"
    ".tr .dc{position:absolute;box-sizing:border-box;display:flex;align-items:flex-start;gap:8px}"
    ".tr .dc svg{flex:none;margin-top:2px}"    ".tr .st{position:absolute;box-sizing:border-box;background:#F7F4EE;border-radius:0 0 0 16px}"
    ".tr .fo{position:absolute;box-sizing:border-box;border-top:1px solid #E9E0CF}"
    ".tr .pal{position:absolute;box-sizing:border-box;background:#F7F4EE;border-top:1px solid #E9E0CF;"
    "border-radius:0 0 16px 16px}"
)


# ---------------------------------------------------------------------------------------------- DAX e gravação
def _dax(partes: list) -> str:
    """Corpo DAX: literais de até 100 caracteres (corta antes de dobrar as aspas) e referências às medidas de pose."""
    itens = []
    for p in partes:
        if isinstance(p, tuple):
            itens.append(f"[{nome_pose(p[1])}]")
            continue
        for i in range(0, len(p), 100):
            itens.append('"' + p[i:i + 100].replace('"', '""') + '"')
    if len(itens) > DAX_ITENS_MAX:
        # o motor recusa uma cadeia de & com ~1.000 termos ("query is too complex"; testado em 08/10: 900 passa, 1.000
        # não). As poses do narrador NB passam disso: os termos vão em grupos entre parênteses.
        grupos = [itens[i:i + DAX_GRUPO] for i in range(0, len(itens), DAX_GRUPO)]
        return "-- 4 · Marcação\n" + "\n    & ".join("(\n        " + "\n        & ".join(g) + "\n    )" for g in grupos)
    return "-- 4 · Marcação\n" + "\n    & ".join(itens)


def _descricao_passo(tela: str, passo: dict, total: int, geo: dict) -> str:
    return (f"Passo {passo['n']} de {total} do tour {DA_TELA.get(tela, 'da')} {TELAS[tela].split(' ', 1)[1]} "
            f"({passo['titulo']}): gestor "
            f"(pose P{geo['pose']}) no canto {geo['canto']}, balão de {geo['balao']['w']} px, ligação ao anel. Só desenha; "
            "lê a medida da pose.")


def medidas_tela(tela: str) -> list[Medida]:
    pasta = f"{TELAS[tela]}\\Tour"
    saida = []
    passos = passos_da_tela(tela)
    total = len(passos)
    for passo in passos:
        geo = geometria(tela, passo, total)
        partes = html_passo(passo, geo)
        saida.append(Medida(nome_medida(tela, passo["n"]), pasta, "texto",
                            _descricao_passo(tela, passo, total, geo), _dax(partes)))
    return saida


def poses_referidas(medidas: list[Medida]) -> list[int]:
    """Poses que algum passo referencia no DAX ([Comum · Tour · Pose Pn · HTML]). Só essas entram no modelo: uma pose
    que nenhum passo lê não vira medida (cada imagem embutida pesa de 70 a 110 KB)."""
    texto = "\n".join(m.dax for m in medidas)
    return [n for n in POSES if f"[{nome_pose(n)}]" in texto]


def _pose_guardada(n: int) -> str | None:
    """Corpo DAX da pose já gravada em pbi/dax (a imagem que a sessão local pôs lá), para quando o recorte não existe
    nesta máquina: a silhueta provisória (_recorte_provisorio) só serve à geometria e nunca vira medida."""
    arq = RAIZ / "dax" / "comum" / "Desenho" / nome_arquivo(nome_pose(n))
    if not arq.is_file():
        return None
    texto = arq.read_text(encoding="utf-8")
    return texto.split("*/\n", 1)[1] if "*/\n" in texto else None


def medidas_poses(usadas: list[int]) -> list[Medida]:
    saida = []
    for n in POSES:
        if n not in usadas:
            continue
        if not _pose_existe(n):
            guardada = _pose_guardada(n)
            if guardada is not None:
                saida.append(Medida(nome_pose(n), r"Comum\Desenho", "texto",
                                    f"Pose P{n} do personagem do tour (imagem embutida, base64). Medida de desenho: só "
                                    "lida pelos passos.", guardada))
            continue
        conteudo = pose_html(n)
        saida.append(Medida(nome_pose(n), r"Comum\Desenho", "texto",
                            f"Pose P{n} do personagem do tour (imagem embutida, base64). Medida de desenho: só lida pelos "
                            "passos.", _dax([conteudo])))
    return saida


def medida_css() -> Medida:
    dax = "-- 4 · Marcação\n[Comum · CSS base]\n    & " + "\n    & ".join(
        '"' + CSS_TOUR[i:i + 100].replace('"', '""') + '"' for i in range(0, len(CSS_TOUR), 100))
    return Medida(NOME_CSS, r"Comum\Desenho", "texto",
                  "Folha de estilo do tour guiado (véu, card, cabeçalho, controles, marcas e componentes do card grande). "
                  "Inclui o CSS base da casa.", dax)


def html_completo_previa(tela: str, n: int) -> str:
    """Documento para foto: o passo sobre o papel de parede da tela (sem os demais visuais)."""
    passos = passos_da_tela(tela)
    passo = next(p for p in passos if p["n"] == n)
    geo = geometria(tela, passo, len(passos))
    corpo = partes_para_html(html_passo(passo, geo))
    css = DC.css_fontes() + DC.CSS_BASE + C.css_texto() + CSS_TOUR
    wp = (RAIZ / "assets" / "wallpapers" / f"wp-{tela.lower()}.svg").as_uri()
    return ("<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><title>tour " + tela + " " + f"{n:02d}"
            + "</title><meta name='viewport' content='width=1920'>"
            "<style>html,body{margin:0;width:1920px;height:1080px;overflow:hidden}"
            f".fundo{{position:fixed;inset:0;background:url('{wp}') 0 0/1920px 1080px no-repeat}}"
            f"{css}</style></head><body><div class='fundo'></div>{corpo}</body></html>")


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--previa", action="store_true", help="grava as prévias HTML em pbi/qa/tour/html")
    a = ap.parse_args(argv)
    if a.previa:
        pasta = PROJETO / "pbi" / "qa" / "tour" / "html"
        pasta.mkdir(parents=True, exist_ok=True)
        for tela in TELAS:
            for passo in passos_da_tela(tela):
                arq = pasta / f"{tela.lower()}-{passo['n']:02d}.html"
                arq.write_text(html_completo_previa(tela, passo["n"]), encoding="utf-8", newline="\n")
        print(f"prévias em {pasta}")
        return 0
    codigo = 0
    maior = (0, "")
    passos_por_tela = {tela: medidas_tela(tela) for tela in TELAS}
    usadas = poses_referidas([m for medidas in passos_por_tela.values() for m in medidas])
    for tela in TELAS:
        medidas = passos_por_tela[tela]
        codigo |= gravar(medidas, RAIZ / "dax" / tela, GERADO)
        for m in medidas:
            tam = len(m.dax.encode("utf-8"))
            if tam > maior[0]:
                maior = (tam, m.nome)
    codigo |= gravar(medidas_poses(usadas) + [medida_css()], RAIZ / "dax" / "comum", GERADO)
    print(f"maior medida de passo: {maior[0] / 1024:.1f} KB ({maior[1]})")
    print("poses embutidas (as que os passos referenciam): " + (", ".join(f"P{n}" for n in usadas) or "nenhuma"))
    for n in usadas:
        _, nb = pose_dados(n) if pose_arquivo(n) else ("", 0)
        if nb:
            print(f"  pose P{n}: {nb / 1024:.0f} KB")
    print("\nlayout (lado pedido → final · layout · tamanho · personagem):")
    for tela in TELAS:
        passos = passos_da_tela(tela)
        for p in passos:
            g = geometria(tela, p, len(passos))
            cd = g["card"]
            print(f"  {tela} {p['n']:02d} {p['id']:<13} {g['lado_pedido']!s:>8} → {g['lado']:<8} {g['layout']:<10} "
                  f"{cd['w']:g}×{cd['h']:g} em ({cd['x']:g},{cd['y']:g}) pessoa {g['personagem']} k={g['k']}"
                  f"{' · reduzido' if g['reduzido'] else ''}{'' if g['cota'] else ' · sem cota'}")
    for aviso in AVISOS:
        print("[aviso]", aviso)
    for registro in REGISTROS:
        print("[registro]", registro)
    return codigo


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""desenho_t5 — medidas de DESENHO da Tela 05 · Canteiro (pbi/dax/T5/**). Só leem contas (base/** e T5/**/Contas);
formatam, escapam e posicionam.

Tela nova da F3 (docs/08 §6): o canteiro está seguro, faz certo da primeira vez e recebe material no prazo? Grade da
T4 (prancheta em 300,12): cartões em y 109 (302 × 140; x 352 · 654 · 955 · 1257 · 1558, o primeiro escuro); à esquerda,
Qualidade, mês a mês (352,273 · 1068 × 380: subtítulo em y 305, gráfico 1068 × 312 a partir de y 341) e Chuva e ritmo
(352,693 · 1068 × 347: subtítulo em y 725, colunas 1068 × 279 a partir de y 761); à direita, Segurança por obra
(1460,273 · 400 × 380: cabeçalho em y 305, sete linhas de 42 a partir de y 365) e Suprimentos por obra (1460,693 ·
400 × 347: cabeçalho em y 725, sete linhas de 36 a partir de y 785). Títulos e "?" estão na casca (wp-t5.svg, casca
única da sessão local); subtítulos, legendas e nomes de coluna vêm daqui.

Cores: as marcas e as barras seguem os pontos do item da nota (cheio sálvia · parte ocre · nenhum vermelho); as metas
são os limites de ponto cheio do modelo e a média do setor da taxa de frequência ([Nota · limite acidentes · setor]):
nenhum número da nota fica escrito aqui. Chuva em creme, executado em preto (o par previsto × realizado da T4).

Geometria em px sempre inteira (o modelo é pt-BR: decimal sairia com vírgula e o CSS ignoraria).

F4 (pedido do Alisson, 28/10/2026: todo número conta e todo elemento de gráfico entra animado): os números que ainda
eram estáticos (contexto dos cartões, metas dos subtítulos, taxa e NR-18 de Segurança, taxa e pedidos de Suprimentos,
rótulos finais e eixo da Qualidade) vão marcados com C.marca() e viram odômetro no fim da medida (C.envolver_marcas);
as linhas da Qualidade se desenham (pathLength 1000), os pontos da carteira entram quando a linha passa por eles, o
ponto de Suprimentos corre do começo da trilha (corrida) e traços, trilhas, grade, eixos e marcas entram com as
classes genéricas do CSS base (.a-pop, .a-fd, .a-gx).

    python -X utf8 pbi/scripts/desenho_t5.py
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import contador as C  # noqa: E402
import desenho_projeto as D  # noqa: E402
from contas_lib_projeto import Medida, gravar  # noqa: E402
from desenho_comum import dax_lit  # noqa: E402

RAIZ = AQUI.parent
GERADO = "pbi/scripts/desenho_t5.py"
TELA = "T5 Canteiro"
MEDIDAS: list[Medida] = []
MENOS = D.MENOS
TF_REF = "Canteiro · taxa de frequência (12 meses) · ref"


def m(nome, pasta, descricao, dax):
    """Medida de desenho; os valores marcados com C.marca() viram odômetro no fim (F4)."""
    MEDIDAS.append(Medida(nome, pasta, "texto", descricao, C.envolver_marcas(dax)))


def css(nome, pasta, descricao, texto, base="[Comum · CSS base]"):
    m(nome, pasta, descricao, "-- 4 · Marcação\n" + base + "\n    & " + dax_lit(texto))


def linhas(*ls) -> str:
    return "\n".join(l for g in ls for l in (g if isinstance(g, list) else [g]))


def cls_item(pts: str, poss: str) -> str:
    """Classe da marca pelos pontos de um item da nota: "0" cheio · "1" parcial · "2" zero · "" sem dado."""
    return f'IF ( ISBLANK ( {pts} ), "", IF ( {pts} >= {poss}, "0", IF ( {pts} = 0, "2", "1" ) ) )'


def faixas_item(cod: str, p: str) -> list[str]:
    """VARs {p}1 e {p}N: a primeira e a última faixa do item com os pontos (texto do modelo, < e > escapados)."""
    def h(x: str) -> str:
        return f'SUBSTITUTE ( SUBSTITUTE ( {x}, "<", "&lt;" ), ">", "&gt;" )'
    return [f'VAR {p} = SUBSTITUTE ( CALCULATE ( [Nota · item · faixas], dItemNota[Item] = "{cod}" ), " · ", "|" )',
            f'VAR {p}a = PATHITEM ( {p}, 1 )', f'VAR {p}z = PATHITEM ( {p}, PATHLENGTH ( {p} ) )',
            f'VAR {p}1 = {h(p + "a")}', f'VAR {p}N = {h(p + "z")}']


def obras_txt(n: str, p: str) -> list[str]:
    return [f'VAR {p}Txt = IF ( {n} = 0, "nenhuma obra abaixo", IF ( {n} = 1, "1 obra abaixo", '
            f'{C.marca(n)} & " obras abaixo" ) )']


# ======================================================================================================== cartões
CARTOES = rf"{TELA}\Cartões"
css("T5 · Cartões · CSS", CARTOES,
    "CSS dos cartões da T5: o do cartão com flip comum mais a marca no começo do contexto.",
    ".kc .ctx .mk{margin-right:6px;vertical-align:-1px}", base="[Comum · CSS cartão]")


def cartao(chave: str, eb: str, leituras: list[tuple[str, str]], textos: list[str], hero: str, lado: str | None,
           ctx: str, regra: str, origem: str, regua: list | None, anima: list[str], escuro: bool = False,
           desc: str = "") -> None:
    """Cartão com flip (o mesmo desenho dos cartões da T3 e da T4): `eb`, `hero`, `lado`, `ctx` e `regra` são
    expressões DAX de texto já formatado; `regua` = [(classe da marca, texto)], texto pode ter '" & _var & "'."""
    topo_ond = 82 if regua else 106
    verso = ("\"<div class='lado verso sobre-creme'>\"\n"
             "            & \"<p class='ab vs v1'>COMO É CALCULADO</p>\"\n"
             f"            & \"<p class='regra'>\" & {regra} & \"</p>\"\n"
             f"            & \"<div class='ond' style='top:{topo_ond}px'><span class='vs'>DE ONDE VEM</span>"
             f"<span>{origem}</span></div>\"\n")
    if regua:
        itens = "".join(f"<i class='mk {c}'></i><span>{t}</span>" for c, t in regua)
        verso += f"            & \"<div class='regua'>{itens}</div>\"\n"
    verso += "        & \"</div>\""
    lado_html = f" & \"<span class='b5 lado2'>\" & {lado} & \"</span>\"" if lado else ""
    dax = linhas(
        "-- 1 · Leituras", [f"VAR {v} = [{x}]" for v, x in leituras],
        "-- 2 · Textos", textos,
        [D.od_tabela()] + anima,
        "-- 4 · Marcação",
        "RETURN",
        f"    \"<div class='u kc{' escuro' if escuro else ''}' tabindex='0'>\"",
        "        & \"<div class='lado frente'>\"",
        f"            & \"<p class='ab vs eb'>\" & {eb} & \"</p>\"",
        f"            & \"<div class='linha1'><span class='b6 hero'>\" & {hero} & \"</span>\"{lado_html} & \"</div>\"",
        f"            & \"<p class='ctx'>\" & {ctx} & \"</p>\"",
        "        & \"</div>\"",
        "        & " + verso,
        "    & \"</div>\" & [Comum · JS contador]",
    )
    m(f"T5 · Cartão {chave} · HTML", CARTOES, desc or f"Cartão '{chave}' (frente e verso). Só lê contas · ref.", dax)


cartao(
    "acidentes", '"Sem acidente com afastamento"',
    [("_n", "T5 · Acidentes · meses sem acidente"), ("_ult", "T5 · Acidentes · último mês"),
     ("_ini", "T5 · Acidentes · início do histórico"), ("_lst", "T5 · Acidentes · obras do último (lista)")],
    D.inteiro("_n", "_tn", vazio="—") + [
        'VAR _txtLado = IF ( ISBLANK ( _n ), "", IF ( _n = 1, "mês", "meses" ) )',
        'VAR _txtObras = SUBSTITUTE ( _lst, "|", ", " )',
        "VAR _txtCtx = SWITCH ( TRUE (), ISBLANK ( _ini ), \"" + "falta na base" + "\", ISBLANK ( _ult ), \"nenhum desde \" "
        "& FORMAT ( _ini, \"mmm/yy\", \"pt-BR\" ), \"o último em \" & FORMAT ( _ult, \"mmm/yy\", \"pt-BR\" ) & \" · \" & "
        + D.esc("_txtObras") + " )",
        'VAR _txtRegra = "Meses seguidos sem acidente com afastamento em nenhuma obra, depois do último mês com acidente. '
        'A base é mensal: não traz o dia."'],
    "_tnOd", "_txtLado", "_txtCtx", "_txtRegra", "Base complementar · NBR 14280", None,
    D.od_num("_n", "_tn"), escuro=True,
    desc="Cartão escuro 'Sem acidente com afastamento' (a resposta de 'o canteiro está seguro?'): meses seguidos sem "
         "acidente com afastamento no recorte, com o último mês com acidente e as obras dele (ou 'nenhum desde' o "
         "começo do histórico). A base é mensal: conta meses, não dias. Só lê contas.")

cartao(
    "frequência", '"Frequência de acidentes · 12 meses"',
    [("_tf", TF_REF), ("_set", "Nota · limite acidentes · setor"), ("_ac", "Canteiro · acidentes 12 meses · ref"),
     ("_acima", "T5 · Segurança · obras acima do setor · ref")],
    D.numero("_tf", "_tt") + D.numero("_set", "_ts") + [
        'VAR _a = _ac + 0',
        'VAR _txtAc = IF ( _a = 1, "1 acidente", ' + C.marca("_a") + ' & " acidentes" )',
        'VAR _txtAcima = IF ( _acima = 0, "nenhuma obra acima", IF ( _acima = 1, "1 obra acima", ' + C.marca("_acima")
        + ' & " obras acima" ) )',
        "VAR _txtCtx = IF ( ISBLANK ( _tf ), \"falta na base\", _txtAc & \" · setor \" & " + C.marca("_tsTxt")
        + " & \" · \" & _txtAcima )",
        'VAR _txtRegra = "Acidentes com afastamento × 1.000.000 ÷ horas-homem trabalhadas nos 12 meses até o mês, com as '
        'obras somadas (NBR 14280). Na nota, por obra:"'] + faixas_item("acidentes", "_fx"),
    "_ttOd", '"por milhão de HHT"', "_txtCtx", "_txtRegra", "Base complementar · NBR 14280",
    [("mk0", '" & _fx1 & "'), ("mk2", '" & _fxN & "')], D.od_num("_tf", "_tt"),
    desc="Cartão da taxa de frequência de 12 meses da carteira (acidentes com afastamento por milhão de horas-homem), "
         "com os acidentes no período, a média do setor e quantas obras passam dela; o verso traz a regra e a primeira "
         "e a última faixa do item acidentes (lidas do modelo). Só lê contas.")


def cartao_pct(chave, eb, x_ref, lim, n_abx, cod, regra, origem, desc):
    cartao(
        chave, f'"{eb}"', [("_x", x_ref), ("_lim", lim), ("_abx", n_abx)],
        D.pct("_x", "_tx") + D.pct("_lim", "_tl", casas=0) + obras_txt("_abx", "_to") + [
            "VAR _txtCtx = IF ( ISBLANK ( _x ), \"falta na base\", \"meta \" & " + C.marca("_tlTxt") + " & \" · \" & _toTxt )",
            f'VAR _txtRegra = "{regra} Na nota, por obra:"'] + faixas_item(cod, "_fx"),
        "_txOd", None, "_txtCtx", "_txtRegra", origem, [("mk0", '" & _fx1 & "'), ("mk2", '" & _fxN & "')],
        D.od_pct("_x", "_tx"), desc=desc)


cartao_pct("NR-18", "Canteiro conforme NR-18", "Canteiro · conformidade NR-18 · ref", "Nota · limite NR-18 · ponto cheio",
           "T5 · NR-18 · obras abaixo da meta · ref", "nr18",
           "Itens conformes ÷ itens aplicáveis do checklist NR-18 do mês, com as obras somadas.",
           "Base complementar · checklist NR-18",
           "Cartão da conformidade NR-18 da carteira no mês (soma ÷ soma), com a meta (o ponto cheio do item NR-18 da nota) "
           "e quantas obras ficam abaixo dela; o verso traz a regra e a primeira e a última faixa. Só lê contas.")
cartao_pct("inspeção", "Aprovação na 1.ª inspeção", "Canteiro · aprovação na 1.ª inspeção · ref",
           "Nota · limite inspeção · ponto cheio", "T5 · Inspeção · obras abaixo da meta · ref", "inspecao",
           "Serviços aprovados na primeira verificação (FVS) ÷ serviços verificados no mês, com as obras somadas.",
           "Base complementar · FVS",
           "Cartão da aprovação na 1.ª inspeção da carteira no mês (soma ÷ soma), com a meta (o ponto cheio do item da "
           "nota) e quantas obras ficam abaixo dela; o verso traz a regra e a primeira e a última faixa. Só lê contas.")
cartao_pct("entregas", "Entregas no prazo e completas", "Canteiro · entregas no prazo · ref",
           "Nota · limite entregas · ponto cheio", "T5 · Entregas · obras abaixo da meta · ref", "entregas",
           "Pedidos entregues no prazo e completos ÷ pedidos com entrega prevista no mês, com as obras somadas.",
           "Base complementar · pedidos",
           "Cartão das entregas no prazo e completas da carteira no mês (soma ÷ soma), com a meta (o ponto cheio do item "
           "da nota) e quantas obras ficam abaixo dela; o verso traz a regra e a primeira e a última faixa. Só lê contas.")

# ======================================================================================================== cabeçalhos
# subtítulo (e nomes de coluna nas tabelas da direita) em HTML com fundo branco, como na T4
CAB = rf"{TELA}\Comum"
css("T5 · Cabeçalho · CSS", CAB, "CSS dos subtítulos e dos nomes de coluna dos painéis da T5.",
    ".hsb{position:fixed;inset:0;background:#FFFFFF;font-size:15px;line-height:22px;color:#3B3B3F;white-space:nowrap;"
    "overflow:hidden}"
    ".hsb .lg{display:inline-block;vertical-align:-1px;margin:0 6px 0 0}"
    ".hsb .sep{margin:0 8px;color:#6B6B70}"
    ".obc{position:fixed;inset:0;background:#FFFFFF;white-space:nowrap}"
    ".obc .sub{position:absolute;left:0;top:0;font-size:15px;line-height:20px;color:#3B3B3F}"
    ".obc .vs{position:absolute;top:36px;font-size:12px;line-height:16px;letter-spacing:1px;text-transform:uppercase;"
    "color:#6B6B70}")

QUA = rf"{TELA}\Qualidade mês a mês"
SEG = rf"{TELA}\Segurança por obra"
SUP = rf"{TELA}\Suprimentos por obra"
CHU = rf"{TELA}\Chuva e ritmo"

m("T5 · Qualidade · HTML subtítulo", QUA,
  "Subtítulo de Qualidade, mês a mês: o que as linhas mostram e a meta (o ponto cheio do item 1.ª inspeção da nota).",
  linhas(
      "-- 1 · Leituras",
      "VAR _lim = [Nota · limite inspeção · ponto cheio]",
      "VAR _dest = [T5 · Qualidade · obra em destaque · ref]",
      "-- 2 · Textos",
      D.pct("_lim", "_tl", casas=0),
      'VAR _txtDest = IF ( ISBLANK ( _dest ), "", "<span class=\'sep\'>·</span><svg class=\'lg\' width=\'18\' height=\'3\'>'
      '<path d=\'M0 1.5H18\' stroke=\'#3B3B3F\' stroke-width=\'2\'/></svg>" & ' + D.esc("_dest") + ' & ", a menor no mês" )',
      "-- 4 · Marcação",
      "RETURN",
      "    \"<p class='u hsb'>aprovação na 1.ª inspeção por obra<span class='sep'>·</span><svg class='lg' width='18' \"",
      "        & \"height='3'><path d='M0 1.5H18' stroke='#0B0B0C' stroke-width='3'/></svg>carteira\" & _txtDest",
      "        & \"<span class='sep'>·</span><svg class='lg' width='18' height='2'><path d='M0 1H18' stroke='#6B6B70' \"",
      "        & \"stroke-width='1.5' stroke-dasharray='4 3'/></svg>meta \" & " + C.marca("_tlTxt") + " & \"</p>\"",
      "        & [Comum · JS contador]",
  ))
m("T5 · Chuva · HTML subtítulo", CHU,
  "Subtítulo de Chuva e ritmo: o que cada metade da coluna mostra.",
  "-- 4 · Marcação\n" + dax_lit("<p class='u hsb'><svg class='lg' width='12' height='12'><rect width='12' height='12' "
                                "fill='#E9E0CF'/></svg>dias impraticáveis por chuva, média por obra (em cima)"
                                "<span class='sep'>·</span><svg class='lg' width='12' height='12'><rect width='12' "
                                "height='12' fill='#0B0B0C'/></svg>executado no mês da carteira, % do orçamento "
                                "(embaixo)</p>"))
m("T5 · Segurança · HTML cabeçalho", SEG,
  "Cabeçalho de Segurança por obra: o mês, a média do setor (o traço) e os nomes das colunas (OBRA, FREQUÊNCIA 12 MESES, "
  "NR-18).",
  linhas(
      "-- 1 · Leituras",
      "VAR _mesC = [Mês de referência · curto]",
      "VAR _set = [Nota · limite acidentes · setor]",
      "-- 2 · Textos",
      D.numero("_set", "_ts"),
      "-- 4 · Marcação",
      "RETURN",
      "    \"<div class='u obc'><span class='sub'>\" & _mesC & \" · por milhão de HHT · traço = setor (\" & " + C.marca("_tsTxt"),
      "        & \")</span><span class='vs' style='left:14px'>obra</span><span class='vs' style='left:116px'>frequência \"",
      "        & \"12 meses</span><span class='vs' style='right:14px'>NR-18</span></div>\" & [Comum · JS contador]",
  ))
m("T5 · Suprimentos · HTML cabeçalho", SUP,
  "Cabeçalho de Suprimentos por obra: o mês, a meta (o ponto cheio do item entregas) e os nomes das colunas.",
  linhas(
      "-- 1 · Leituras",
      "VAR _mesC = [Mês de referência · curto]",
      "VAR _lim = [Nota · limite entregas · ponto cheio]",
      "-- 2 · Textos",
      D.pct("_lim", "_tl", casas=0),
      "-- 4 · Marcação",
      "RETURN",
      "    \"<div class='u obc'><span class='sub'>\" & _mesC & \" · no prazo e completos · traço = meta \" & " + C.marca("_tlTxt"),
      "        & \"</span><span class='vs' style='left:14px'>obra</span><span class='vs' style='left:116px'>no prazo</span>\"",
      "        & \"<span class='vs' style='left:258px'>pedidos</span><span class='vs' style='right:14px'>%</span></div>\"",
      "        & [Comum · JS contador]",
  ))

# ======================================================================================================== segurança por obra
# linhas de 42 (sete obras = 294, de y 365 a 659): nome (Barlow 15), barra da taxa de frequência de 12 meses de x 116 a
# 256 (escala de 0 ao topo, com o traço da média do setor), o valor e, à direita, a conformidade NR-18 do mês com a
# marca dos pontos do item. Barra na cor dos pontos do item acidentes (parte ocre · nenhum vermelho); zero acidente
# fica só com a trilha.
SEG_LINHA, SEG_X0, SEG_W = 42, 116, 140
css("T5 · Segurança · CSS", SEG, "CSS do cabeçalho e das linhas de Segurança por obra.",
    ".htmlViewerEntry{display:block!important;margin:0!important;padding:0!important}"
    f".sg{{position:relative;height:{SEG_LINHA - 1}px;border-bottom:1px solid #E1E1E1;background:#FFFFFF;"
    "transition:background .15s}"
    ".sg:hover,.htmlViewerEntry.hover .sg{background:#F7F4EE}"
    ".sg .nm{position:absolute;left:14px;top:10px;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;"
    "font-size:15px;line-height:20px;white-space:nowrap}"
    f".sg .tr{{position:absolute;left:{SEG_X0}px;top:14px;width:{SEG_W}px;height:12px;background:#EFEFEF}}"
    ".sg .br{position:absolute;left:0;top:0;height:12px}"
    ".sg .br.s1{background:#C9821F}.sg .br.s2{background:#C43737}"
    ".sg .st{position:absolute;top:-5px;width:2px;height:22px;background:#0B0B0C}"
    f".sg .v{{position:absolute;left:{SEG_X0 + SEG_W + 8}px;top:10px;font-family:'Barlow U','Segoe UI',sans-serif;"
    "font-weight:600;font-size:15px;line-height:20px;white-space:nowrap}"
    ".sg .nr{position:absolute;right:14px;top:10px;display:flex;align-items:center;white-space:nowrap;"
    "font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:15px;line-height:20px}"
    ".sg .nr .mk{margin-right:6px}")
m("T5 · Segurança · HTML linha", SEG,
  "Uma linha por obra com base no mês de referência (granularidade dObra[Obra], ordem T5 · Segurança · ordem): nome, "
  "barra da taxa de frequência de 12 meses (cor dos pontos do item acidentes; zero acidente só com a trilha) com o traço "
  "da média do setor, o valor e a conformidade NR-18 do mês com a marca dos pontos do item NR-18. A barra corre do zero.",
  linhas(
      "-- 1 · Leituras",
      "VAR _obra = [Obra · nome]",
      f"VAR _tf = [{TF_REF}]",
      "VAR _ac = [Canteiro · acidentes 12 meses · ref]",
      "VAR _nr = [Canteiro · conformidade NR-18 · ref]",
      "VAR _pta = [Nota · pontos acidentes · ref]",
      "VAR _psa = [Nota · possíveis · acidentes · ref]",
      "VAR _ptn = [Nota · pontos NR-18 · ref]",
      "VAR _psn = [Nota · possíveis · NR-18 · ref]",
      "VAR _set = [Nota · limite acidentes · setor]",
      "VAR _topo = [T5 · Segurança · topo da escala]",
      "VAR _pos = [T5 · Segurança · ordem]",
      "-- 2 · Textos",
      "VAR _chave = " + D.esc("_obra"),
      D.numero("_tf", "_tt"),
      D.pct("_nr", "_tn"),
      "VAR _clsA = " + cls_item("_pta", "_psa"),
      "VAR _clsN = " + cls_item("_ptn", "_psn"),
      "-- 3 · Geometria",
      f"VAR _u = DIVIDE ( {SEG_W}, _topo ) -- geometria",
      f"VAR _w = IF ( _tf > 0, MAX ( 3, MIN ( {SEG_W}, ROUND ( _tf * _u, 0 ) ) ), 0 ) -- geometria",
      "VAR _xS = ROUND ( _set * _u, 0 ) - 1 -- geometria",
      "VAR _corre = \"' data-rp='width' data-r0-width='0px' data-rd='100'\"",
      "-- 4 · Marcação",
      "RETURN",
      "    IF (",
      "        NOT ISBLANK ( _pos ),",
      "        \"<div class='u sg'><b class='nm'>\" & _chave & \"</b>\"",
      "            & \"<span class='tr a-fd'>\" & IF ( _w > 0, \"<i class='br s\" & _clsA & \"' style='width:\" & _w & \"px' \"",
      "                & \"data-rk='\" & _chave & \"|tf\" & _corre & \"></i>\" )",
      "            & \"<i class='st a-pop' style='animation-delay:600ms;left:\" & _xS & \"px'></i></span>\"",
      "            & \"<span class='v'>\" & IF ( ISBLANK ( _tf ), \"—\", " + C.marca("_ttTxt") + " ) & \"</span>\"",
      "            & \"<span class='nr'>\" & IF ( _clsN = \"\", \"\", \"<i class='mk a-pop mk\" & _clsN & \"' \"",
      "                & \"style='animation-delay:400ms'></i>\" ) & IF ( ISBLANK ( _nr ), \"—\", " + C.marca("_tnTxt") + " ) & \"</span>\"",
      "        & \"</div>\" & [Comum · JS contador] & [Comum · JS corrida]",
      "    )",
  ))

# ======================================================================================================== suprimentos por obra
# linhas de 36 (sete obras = 252, de y 785 a 1037): nome, trilha das entregas de x 116 a 250 (da base da escala a 100%)
# com o traço da meta e o ponto da obra na cor dos pontos do item, os pedidos ("20 de 26") e a taxa à direita.
SUP_LINHA, SUP_X0, SUP_W = 36, 116, 134
css("T5 · Suprimentos · CSS", SUP, "CSS das linhas de Suprimentos por obra.",
    ".htmlViewerEntry{display:block!important;margin:0!important;padding:0!important}"
    f".sp{{position:relative;height:{SUP_LINHA - 1}px;border-bottom:1px solid #E1E1E1;background:#FFFFFF;"
    "transition:background .15s}"
    ".sp:hover,.htmlViewerEntry.hover .sp{background:#F7F4EE}"
    ".sp .nm{position:absolute;left:14px;top:7px;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;"
    "font-size:15px;line-height:20px;white-space:nowrap}"
    f".sp .tr{{position:absolute;left:{SUP_X0}px;top:17px;width:{SUP_W}px;height:2px;background:#E1E1E1}}"
    ".sp .mt{position:absolute;top:-8px;width:2px;height:18px;background:#0B0B0C}"
    ".sp .pt{position:absolute;top:-5px;width:12px;height:12px;border-radius:50%;box-sizing:border-box}"
    ".sp .pt.s0{background:#A9CDB9;border:1px solid #6E9F85}.sp .pt.s1{background:#C9821F}"
    ".sp .pt.s2{background:#C43737}"
    f".sp .pd{{position:absolute;left:{SUP_X0 + SUP_W + 8}px;top:8px;font-size:13px;line-height:18px;color:#3B3B3F;"
    "white-space:nowrap}"
    ".sp .v{position:absolute;right:14px;top:7px;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;"
    "font-size:15px;line-height:20px;white-space:nowrap}")
m("T5 · Suprimentos · HTML linha", SUP,
  "Uma linha por obra com pedido previsto no mês de referência (granularidade dObra[Obra], ordem T5 · Entregas · ordem: "
  "a menor taxa primeiro): nome, trilha das entregas no prazo e completas (da base da escala a 100%) com o traço da meta "
  "(o ponto cheio do item entregas) e o ponto da obra na cor dos pontos do item, os pedidos no prazo de previstos e a "
  "taxa.",
  linhas(
      "-- 1 · Leituras",
      "VAR _obra = [Obra · nome]",
      "VAR _x = [Canteiro · entregas no prazo · ref]",
      "VAR _np = [Canteiro · pedidos no prazo · ref]",
      "VAR _pp = [Canteiro · pedidos previstos · ref]",
      "VAR _pt = [Nota · pontos entregas · ref]",
      "VAR _ps = [Nota · possíveis · entregas · ref]",
      "VAR _lim = [Nota · limite entregas · ponto cheio]",
      "VAR _base = [T5 · Entregas · base da escala]",
      "-- 2 · Textos",
      "VAR _chave = " + D.esc("_obra"),
      D.pct("_x", "_tx"),
      "VAR _cls = " + cls_item("_pt", "_ps"),
      'VAR _txtPd = ' + C.marca('FORMAT ( _np, "0", "pt-BR" )') + ' & " de " & ' + C.marca('FORMAT ( _pp, "0", "pt-BR" )'),
      "-- 3 · Geometria",
      f"VAR _u = DIVIDE ( {SUP_W}, 1 - _base ) -- geometria",
      f"VAR _xP = MAX ( 0, MIN ( {SUP_W}, ROUND ( ( _x - _base ) * _u, 0 ) ) ) - 6 -- geometria",
      "VAR _xM = ROUND ( ( _lim - _base ) * _u, 0 ) - 1 -- geometria",
      "-- 4 · Marcação",
      "RETURN",
      "    IF (",
      "        NOT ISBLANK ( _x ),",
      "        \"<div class='u sp'><b class='nm'>\" & _chave & \"</b>\"",
      "            & \"<span class='tr a-fd'><i class='mt a-pop' style='animation-delay:500ms;left:\" & _xM & \"px'></i>\"",
      "            & \"<i class='pt a-pop s\" & _cls & \"' style='left:\" & _xP & \"px' data-rk='\" & _chave & \"|sp' \"",
      "            & \"data-rp='left' data-r0-left='-6px' data-rd='100'></i></span>\"",
      "            & \"<span class='pd'>\" & _txtPd & \"</span><span class='v'>\" & " + C.marca("_txTxt") + " & \"</span>\"",
      "        & \"</div>\" & [Comum · JS contador] & [Comum · JS corrida]",
      "    )",
  ))

# ======================================================================================================== qualidade mês a mês
# gráfico 1068 × 312 (de y 341): eixo de 100% (y 14) até a base da escala (y 262), grade de 5 em 5 pontos com o
# rótulo à esquerda (até x 44); meses de x 64 a 900 (passo 836 ÷ (n − 1)) e rótulo do mês em y 278; rótulos finais a
# partir de x último + 14. Uma linha fina por obra (cinza), a obra em destaque (a menor no mês) em grafite e a carteira
# (soma ÷ soma) em preto com os pontos; a meta tracejada.
Q_X0, Q_X1, Q_TOPO, Q_BASE, Q_MES = 64, 900, 14, 262, 278
css("T5 · Qualidade · CSS", QUA, "CSS do gráfico de linhas de Qualidade, mês a mês.",
    ".ql{position:fixed;inset:0}"
    ".ql svg{position:absolute;left:0;top:0;overflow:visible}"
    ".ql .lo{fill:none;stroke:#C9C5BD;stroke-width:1.5;stroke-linejoin:round;stroke-linecap:round}"
    ".ql .ld{fill:none;stroke:#3B3B3F;stroke-width:2;stroke-linejoin:round;stroke-linecap:round}"
    ".ql .lc{fill:none;stroke:#0B0B0C;stroke-width:2.6;stroke-linejoin:round;stroke-linecap:round}"
    ".ql .mt{stroke:#6B6B70;stroke-width:1.5;stroke-dasharray:4 3}"
    ".ql circle{fill:#0B0B0C}"
    ".ql .ey{position:absolute;left:0;width:44px;text-align:right;font-size:13px;line-height:16px;color:#6B6B70}"
    ".ql .gr{position:absolute;left:52px;width:860px;height:1px;background:#EFEFEF}"
    ".ql .ex{position:absolute;width:60px;text-align:center;font-size:13px;line-height:16px;color:#3B3B3F;"
    "white-space:nowrap}"
    ".ql .ex.ref{font-weight:600;color:#0B0B0C}"
    ".ql .fl{position:absolute;font-size:14px;line-height:18px;white-space:nowrap;color:#3B3B3F}"
    ".ql .fl b{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:16px;margin-right:6px}"
    ".ql .fl.c{color:#0B0B0C}"
    ".ql .vz{position:absolute;left:64px;top:120px;font-size:15px;color:#3B3B3F}"
    # F4: as linhas finas das obras também se desenham; pathLength='1000' no path deixa o traço do tamanho certo em
    # qualquer comprimento (antes, 2000 px fixos)
    "@keyframes qlIn{from{stroke-dashoffset:1000}to{stroke-dashoffset:0}}"
    ".ql .lc,.ql .ld,.ql .lo{stroke-dasharray:1000;animation:qlIn 1.2s ease-out backwards}"
    ".ql .ld{animation-delay:.15s}.ql .lc{animation-delay:.3s}"
    "@media (prefers-reduced-motion:reduce){.ql .lc,.ql .ld,.ql .lo{animation:none;stroke-dasharray:none}}")


def q_x(pos: str) -> str:
    return f"ROUND ( IF ( _n > 1, {Q_X0} + ( {pos} - 1 ) * _passoX, {Q_X1} ), 0 )"


def q_y(v: str) -> str:
    return f"ROUND ( {Q_BASE} - ( {v} - _base ) * _escY, 0 )"


m("T5 · Qualidade · HTML gráfico", QUA,
  "Aprovação na 1.ª inspeção mês a mês na janela (1 a 12 meses), sem granularidade: uma linha fina por obra do recorte "
  "(cinza), a obra com a menor aprovação no mês de referência em grafite e a carteira (soma ÷ soma) em preto com os "
  "pontos; a meta (o ponto cheio do item 1.ª inspeção) tracejada. Eixo de 100% até a base da escala (T5 · Qualidade · "
  "base da escala), grade de 5 em 5 pontos; rótulos finais da carteira e da obra em destaque (afastados quando se "
  "encostam). As linhas se desenham da esquerda para a direita.",
  linhas(
      "-- 1 · Leituras",
      "VAR _ref = [Mês de referência]",
      "VAR _n = [Série · meses até a referência]",
      "VAR _base = [T5 · Qualidade · base da escala]",
      "VAR _lim = [Nota · limite inspeção · ponto cheio]",
      "VAR _dest = [T5 · Qualidade · obra em destaque · ref]",
      "VAR _cRef = [Canteiro · aprovação na 1.ª inspeção · ref]",
      "VAR _dRef = [T5 · Leitura qualidade · aprovação da obra em destaque · ref]",
      "VAR _meses =",
      "    ADDCOLUMNS (",
      "        VALUES ( dMes[Mes] ),",
      '        "@ate", [Série · mês até a referência],',
      '        "@pj", [Série · posição na janela],',
      '        "@v", [Canteiro · aprovação na 1.ª inspeção],',
      '        "@rot", [Mês · rótulo curto]',
      "    )",
      "VAR _janela = FILTER ( _meses, [@ate] = 1 ) /* lista */",
      "VAR _cart = FILTER ( _janela, NOT ISBLANK ( [@v] ) ) /* lista */",
      "VAR _obras =",
      "    ADDCOLUMNS (",
      "        CROSSJOIN ( VALUES ( dObra[Obra] ), VALUES ( dMes[Mes] ) ),",
      '        "@ate", [Série · mês até a referência],',
      '        "@pj", [Série · posição na janela],',
      '        "@v", [Canteiro · aprovação na 1.ª inspeção]',
      "    )",
      "VAR _pts = FILTER ( _obras, [@ate] = 1 && NOT ISBLANK ( [@v] ) ) /* lista */",
      "-- 2 · Textos",
      D.pct("_cRef", "_tc"), D.pct("_dRef", "_td"), D.pct("_lim", "_tl", casas=0),
      "-- 3 · Geometria",
      f"VAR _passoX = IF ( _n > 1, DIVIDE ( {Q_X1 - Q_X0}, _n - 1 ), 0 ) /* geometria */",
      f"VAR _escY = DIVIDE ( {Q_BASE - Q_TOPO}, 1 - _base ) /* geometria */",
      f"VAR _xU = {Q_X1} -- geometria",
      f"VAR _yC = IF ( NOT ISBLANK ( _cRef ), {q_y('_cRef')} ) -- geometria",
      f"VAR _yD = IF ( NOT ISBLANK ( _dRef ), {q_y('_dRef')} ) -- geometria",
      f"VAR _yM = {q_y('_lim')} -- geometria",
      "VAR _temD = NOT ISBLANK ( _dRef ) && _dest <> \"\" -- geometria",
      "VAR _gap = IF ( _temD, ABS ( _yC - _yD ), 99 ) -- geometria",
      "VAR _meio = IF ( _temD, ROUND ( ( _yC + _yD ) / 2, 0 ), _yC ) -- geometria",
      "VAR _yLC = IF ( _gap < 20, IF ( _yC <= _yD, _meio - 20, _meio ), _yC - 9 ) -- geometria",
      "VAR _yLD = IF ( _gap < 20, IF ( _yC <= _yD, _meio, _meio - 20 ), _yD - 9 ) -- geometria",
      "VAR _nLinhas = ROUND ( ( 1 - _base ) / 0.05, 0 ) -- geometria",
      "-- 4 · Marcação",
      "VAR _linhas =",
      "    CONCATENATEX (",
      "        VALUES ( dObra[Obra] ),",
      "        VAR _o = dObra[Obra]",
      "        VAR _p = FILTER ( _pts, dObra[Obra] = _o ) /* lista */",
      f"        VAR _d = CONCATENATEX ( _p, {q_x('[@pj]')} & \",\" & {q_y('[@v]')}, \" L\", [@pj], ASC )",
      "        RETURN",
      "            IF ( NOT ISEMPTY ( _p ), \"<path class='\" & IF ( _o = _dest, \"ld\", \"lo\" ) & \"' pathLength='1000' d='M\" & _d & \"'/>\" ),",
      "        \"\",",
      "        IF ( dObra[Obra] = _dest, 1, 0 ), ASC, dObra[Obra], ASC",
      "    )",
      f"VAR _dCart = \"M\" & CONCATENATEX ( _cart, {q_x('[@pj]')} & \",\" & {q_y('[@v]')}, \" L\", [@pj], ASC )",
      "VAR _pontos =",
      "    CONCATENATEX (",
      "        _cart,",
      f"        \"<circle class='a-pop' cx='\" & {q_x('[@pj]')} & \"' cy='\" & {q_y('[@v]')} & \"' r='3.5' style='animation-delay:\" "
      "& ( 300 + ROUND ( ( [@pj] - 1 ) * 1000 / MAX ( 1, _n - 1 ), 0 ) ) & \"ms'/>\",",
      "        \"\",",
      "        [@pj], ASC",
      "    )",
      "VAR _grade =",
      "    CONCATENATEX (",
      "        GENERATESERIES ( 0, _nLinhas ),",
      f"        VAR _y = ROUND ( {Q_BASE} - [Value] * 0.05 * _escY, 0 ) /* geometria */",
      "        RETURN",
      "            \"<i class='gr a-fd' style='top:\" & _y & \"px'></i><span class='ey a-fd' style='top:\" & ( _y - 8 ) & \"px'>\"",
      "                & " + C.marca('FORMAT ( ( _base + [Value] * 0.05 ) * 100, "0", "pt-BR" )') + " & \"%</span>\",",
      "        \"\",",
      "        [Value], ASC",
      "    )",
      "VAR _eixoX =",
      "    CONCATENATEX (",
      "        _janela,",
      f"        VAR _x = {q_x('[@pj]')} /* geometria */",
      "        RETURN",
      "            \"<span class='ex a-fd\" & IF ( dMes[Mes] = _ref, \" ref\", \"\" ) & \"' style='animation-delay:\" "
      "& ROUND ( ( [@pj] - 1 ) * 1000 / MAX ( 1, _n - 1 ), 0 ) & \"ms;left:\" & ( _x - 30 )",
      f"                & \"px;top:{Q_MES}px'>\" & [@rot] & \"</span>\",",
      "        \"\",",
      "        [@pj], ASC",
      "    )",
      "VAR _svg =",
      f"    \"<svg width='1068' height='{Q_MES}' viewBox='0 0 1068 {Q_MES}' aria-hidden='true'>\"",
      f"        & \"<path class='mt a-gx' d='M52,\" & _yM & \" H912'/>\" & _linhas",
      "        & IF ( NOT ISEMPTY ( _cart ), \"<path class='lc' pathLength='1000' d='\" & _dCart & \"'/>\" & _pontos )",
      "    & \"</svg>\"",
      "RETURN",
      "    IF (",
      "        NOT ISEMPTY ( _pts ),",
      "        \"<div class='u ql'>\" & _grade & _svg & _eixoX",
      "            & IF ( NOT ISBLANK ( _cRef ), \"<span class='fl c a-fd' style='animation-delay:1.3s;left:\" & ( _xU + 14 ) "
      "& \"px;top:\" & _yLC",
      "                & \"px'><b>\" & " + C.marca("_tcTxt") + " & \"</b>carteira</span>\" )",
      "            & IF ( _temD, \"<span class='fl a-fd' style='animation-delay:1.2s;left:\" & ( _xU + 14 ) & \"px;top:\" & _yLD "
      "& \"px'><b>\" & " + C.marca("_tdTxt"),
      "                & \"</b>\" & " + D.esc("_dest") + " & \"</span>\" )",
      "        & \"</div>\" & [Comum · JS contador],",
      "        \"<div class='u ql'><p class='vz'>Sem base complementar das obras na janela.</p></div>\"",
      "    )",
  ))

# ======================================================================================================== chuva e ritmo
# colunas 1068 × 279 (de y 761), uma por mês da janela (coluna = 1068 ÷ n): em cima, os dias impraticáveis por chuva
# (média por obra, creme) crescendo da linha de y 118 para cima (até 88 px no topo da escala); o mês em y 124; embaixo,
# o executado no mês da carteira (preto) crescendo de y 146 para baixo (até 100 px). Valores por fora das barras.
CH_W, CH_H, CH_BASE, CH_ALT, CH_MES, EX_TOPO, EX_ALT = 1068, 279, 118, 88, 124, 146, 100
CH_BARRA = 44
css("T5 · Chuva · CSS", CHU, "CSS das colunas espelhadas de Chuva e ritmo (uma entrada por mês da janela).",
    "#htmlContent{display:flex!important;align-items:flex-start;width:100vw;height:100vh;margin:0!important;"
    "padding:0!important}"
    ".htmlViewerEntry{display:block!important;flex:1 1 0;min-width:0;margin:0!important;padding:0!important}"
    f".cr{{position:relative;height:{CH_H}px;transition:background .15s}}"
    ".cr:hover,.htmlViewerEntry.hover .cr{background:rgba(233,224,207,.3)}"
    f".cr .b0{{position:absolute;left:0;right:0;top:{CH_BASE}px;height:1px;background:#E1E1E1}}"
    f".cr .b1{{position:absolute;left:0;right:0;top:{EX_TOPO - 1}px;height:1px;background:#6B6B70}}"
    ".cr .bc{position:absolute;background:#E9E0CF}.cr .be{position:absolute;background:#0B0B0C}"
    ".cr .vl{position:absolute;left:0;right:0;text-align:center;font-family:'Barlow U','Segoe UI',sans-serif;"
    "font-weight:600;font-size:14px;line-height:17px;white-space:nowrap;color:#0B0B0C}"
    ".cr .vl.c{color:#3B3B3F}"
    f".cr .ms{{position:absolute;left:0;right:0;top:{CH_MES}px;text-align:center;font-size:13px;line-height:16px;"
    "color:#3B3B3F;white-space:nowrap}"
    ".cr .ms.ref{font-weight:600;color:#0B0B0C}.cr .ms.sem{opacity:.35}")
m("T5 · Chuva · HTML coluna", CHU,
  "Uma coluna por mês da janela (granularidade dMes[Mes]; coluna = 1068 ÷ n, barra = mín(44; 0,36 × coluna)): em cima, os "
  "dias impraticáveis por chuva (média por obra, creme) com o valor; no meio, o mês; embaixo, o executado no mês da "
  "carteira (preto, % do orçamento) com o valor. Escalas pelo maior mês da janela (T5 · Chuva · topo da escala e T5 · "
  "Ritmo · topo da escala). Mês de referência em semibold; o ano entra no primeiro mês e em janeiro quando a janela "
  "cruza a virada. As barras correm da linha do meio em cascata.",
  linhas(
      "-- 1 · Leituras",
      "VAR _noRecorte = [Série · mês até a referência]",
      "VAR _ch = [Canteiro · dias de chuva]",
      "VAR _ex = [Físico · executado no mês]",
      "VAR _topoC = [T5 · Chuva · topo da escala]",
      "VAR _topoE = [T5 · Ritmo · topo da escala]",
      "VAR _mes = [Mês · abreviado]",
      "VAR _mesAno = [Mês · rótulo curto]",
      "VAR _data = [Mês · data]",
      "VAR _ehRef = [Série · é o mês de referência]",
      "VAR _pos = [Série · posição na janela]",
      "VAR _n = [Série · meses até a referência]",
      "VAR _ini = [Série · primeiro mês]",
      "VAR _ref = [Mês de referência]",
      "-- 2 · Textos",
      D.numero("_ch", "_tc"), D.pct("_ex", "_te"),
      D.od_tabela(), D.od_num("_ch", "_tc"), D.od_pct("_ex", "_te"),
      "VAR _cruza = YEAR ( _ini ) <> YEAR ( _ref )",
      'VAR _txtMes = _mes & IF ( _cruza && ( _pos = 1 || MONTH ( _data ) = 1 ), RIGHT ( _mesAno, 3 ), "" )',
      'VAR _clsMes = IF ( _ehRef = 1, " ref", "" ) & IF ( ISBLANK ( _ch ) && ISBLANK ( _ex ), " sem", "" )',
      "-- 3 · Geometria",
      f"VAR _b = MIN ( {CH_BARRA}, ROUND ( 0.36 * {CH_W} / _n, 0 ) ) -- geometria",
      f"VAR _hC = IF ( _ch > 0, MAX ( 2, ROUND ( DIVIDE ( _ch, _topoC ) * {CH_ALT}, 0 ) ), 0 ) -- geometria",
      f"VAR _hE = IF ( _ex > 0, MAX ( 2, ROUND ( DIVIDE ( _ex, _topoE ) * {EX_ALT}, 0 ) ), 0 ) -- geometria",
      f"VAR _yC = {CH_BASE} - _hC -- geometria",
      "VAR _atraso = ( _pos - 1 ) * 100 -- geometria",
      "-- 4 · Marcação",
      "VAR _htmlC =",
      "    IF (",
      "        NOT ISBLANK ( _ch ),",
      "        \"<i class='bc' style='top:\" & _yC & \"px;height:\" & _hC & \"px;left:calc(50% - \" & INT ( _b / 2 ) & \"px);width:\"",
      f"            & _b & \"px' data-rk='\" & _mes & \"|c' data-rp='top,height' data-r0-top='{CH_BASE}px' \"",
      "            & \"data-r0-height='0px' data-rd='\" & _atraso & \"'></i>\"",
      "            & \"<span class='vl c a-fd' style='animation-delay:\" & ( _atraso + 250 ) & \"ms;top:\" & ( _yC - 20 ) "
      "& \"px'>\" & _tcOd & \"</span>\"",
      "    )",
      "VAR _htmlE =",
      "    IF (",
      "        NOT ISBLANK ( _ex ),",
      f"        \"<i class='be' style='top:{EX_TOPO}px;height:\" & _hE & \"px;left:calc(50% - \" & INT ( _b / 2 ) & \"px);width:\"",
      "            & _b & \"px' data-rk='\" & _mes & \"|e' data-rp='height' data-r0-height='0px' data-rd='\" & ( _atraso + 50 )",
      "            & \"'></i>\"",
      f"            & \"<span class='vl a-fd' style='animation-delay:\" & ( _atraso + 300 ) & \"ms;top:\" & ( {EX_TOPO} + _hE + 4 ) "
      "& \"px'>\" & _teOd & \"</span>\"",
      "    )",
      "RETURN",
      "    IF (",
      "        _noRecorte = 1,",
      "        \"<div class='u cr'><i class='b0 a-fd'></i><i class='b1 a-fd'></i>\" & _htmlC & _htmlE",
      "            & \"<p class='ms a-fd\" & _clsMes & \"' style='animation-delay:\" & _atraso & \"ms'>\" & _txtMes & \"</p>\"",
      "        & \"</div>\" & [Comum · JS contador] & [Comum · JS corrida]",
      "    )",
  ))

if __name__ == "__main__":
    sys.exit(gravar(MEDIDAS, RAIZ / "dax" / "T5", GERADO))

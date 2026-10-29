#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""desenho_t3 — medidas de DESENHO da Tela 03 · Avanço físico (pbi/dax/T3/**). Só leem contas (base/** e
T3/**/Contas); formatam, escapam e posicionam.

Redesenho v2 (Figma FjBWDk5odF9HaZ2pwhGosl, página 04 · Redesenho v2, Tela 03 · v2 387:5627; spec em
pbi/spec/redesenho/t03.md): cartões em y 109 (302 × 140), painéis Curva S (352,273 900 × 370), Ritmo do mês
(1292,273 568 × 290), Avanço das obras (1292,603 568 × 437) e Linha do tempo das obras (352,683 900 × 357); cabeçalho
de cada painel em HTML (subtítulo e legenda, y 0–54 do painel), conteúdo a partir de y 68. O papel de parede
(Casca v2 · T3 408:11772 → pbi/spec/casca/_fonte_v2/T3.svg) só traz o estático: títulos, "?", traços, divisórias e o
fundo preto do cartão escuro. Barras de executado (avanço e linha do tempo) na cor do PRAZO DA NOTA
([T3 · Status desvio físico]: dentro do limite sálvia · fora vermelho), sem previsto em grafite. O limite vem de
[Nota · limite prazo · ponto cheio]: nenhum número da nota fica escrito aqui. Vermelho de negativo só no desvio físico
(atraso): número e rótulo com .ng; o desvio de desembolso negativo fica em preto.

Animação (pedido do Alisson): contador nos números (contador.py, {p}Od), corrida das barras e colunas (corrida.py,
data-rk/data-rd/data-rp) e as linhas da curva S que se desenham da esquerda para a direita. A linha do previsto é
tracejada: as duas linhas se revelam por um recorte que cresce (CSS, 1 s), o previsto primeiro.

F4 (pedido do Alisson, 28/10/2026: "todo número com o odômetro" e "todo elemento de gráfico animado"): os números que
ainda eram texto fixo (pontos do item, meta, previsto × executado, rótulos do eixo, faixas da nota nas legendas e no
verso) entram marcados com C.marca() e o m() converte a medida com C.envolver_marcas(); pontos, marcas, traços,
trilhas e grade entram com as classes genéricas do CSS base (.a-pop, .a-fd, .a-gx) em cascata pelo atraso inline.
Ficam fixos os números que são rótulo e não dado: anos da grade, datas, "1.ª" e os 180 dias da lei no texto.

    python -X utf8 pbi/scripts/desenho_t3.py
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import contador as C  # noqa: E402
import desenho_projeto as D  # noqa: E402
import desenho_comum as DC  # noqa: E402
from contas_lib_projeto import Medida, gravar  # noqa: E402
from desenho_comum import GRAFITE, OFF, PRETO, REGRA, SALVIA, SALVIA_BORDA, TERC, TRILHA, VERM, VERM_CLARO, dax_lit  # noqa: E402

RAIZ = AQUI.parent
GERADO = "pbi/scripts/desenho_t3.py"
MEDIDAS: list[Medida] = []
MENOS = D.MENOS
TELA = "T3 Avanço físico"


def m(nome, pasta, descricao, dax):
    """Medida de desenho; os valores marcados com C.marca() viram odômetro no fim (F4)."""
    MEDIDAS.append(Medida(nome, pasta, "texto", descricao, C.envolver_marcas(dax)))


def linhas(*ls) -> str:
    return "\n".join(l for grupo in ls for l in (grupo if isinstance(grupo, list) else [grupo]))


def css(nome, pasta, descricao, texto, base="[Comum · CSS base]"):
    m(nome, pasta, descricao, "-- 4 · Marcação\n" + base + "\n    & " + dax_lit(texto))


# ======================================================================================================== cartões
CSS_CARTAO_T3 = (
    # marca da faixa no começo do contexto (Figma: Marca · v2 sálvia sobre o cartão preto, antes de "estável · …")
    ".kc .ctx .mk{margin-right:6px;vertical-align:-1px}"
)
css("T3 · Cartão · CSS", rf"{TELA}\Cartões",
    "CSS dos cartões da Tela 03: o do cartão com flip (Comum · CSS cartão) mais a marca da faixa no contexto.",
    CSS_CARTAO_T3, base="[Comum · CSS cartão]")


def regua(itens: list[tuple[str, str]]) -> str:
    return "".join(f"<i class='mk {c}'></i><span>{t}</span>" for c, t in itens)


def cartao(chave: str, eyebrow: str, leituras: list[tuple[str, str]], textos: list[str], hero: str, lado: str | None,
           ctx: str, regra: str, origem: str, regua_itens: list | None, escuro: bool = False, desc: str = "",
           anima: list[str] | None = None, hero_ng: str | None = None) -> None:
    """Cartão com flip (o mesmo desenho de desenho_t1.cartao). `eyebrow` é uma expressão DAX de texto (o do 'No mês'
    traz o mês); `hero`, `lado` e `ctx` são expressões DAX de texto já formatado; `anima` = linhas D.od_*."""
    topo_ond = 82 if regua_itens else 106          # verso v2: "DE ONDE VEM" em y 82 com régua, 106 sem
    verso = ("\"<div class='lado verso sobre-creme'>\"\n"
             "            & \"<p class='ab vs v1'>COMO É CALCULADO</p>\"\n"
             f"            & \"<p class='regra'>\" & {D.texto(regra)} & \"</p>\"\n"
             f"            & \"<div class='ond' style='top:{topo_ond}px'><span class='vs'>DE ONDE VEM</span>"
             f"<span>{origem}</span></div>\"\n")
    if regua_itens:
        verso += f"            & \"<div class='regua'>{regua(regua_itens)}</div>\"\n"
    verso += "        & \"</div>\""
    lado_html = f" & \"<span class='b5 lado2'>\" & {lado} & \"</span>\"" if lado else ""
    dax = linhas(
        "-- 1 · Leituras", [f"VAR {v} = [{x}]" for v, x in leituras],
        "-- 2 · Textos", textos,
        [D.od_tabela()] + anima if anima else [],
        "-- 4 · Marcação",
        "RETURN",
        f"    \"<div class='u kc{' escuro' if escuro else ''}' tabindex='0'>\"",
        "        & \"<div class='lado frente'>\"",
        f"            & \"<p class='ab vs eb'>\" & {eyebrow} & \"</p>\"",
        (f"            & \"<div class='linha1'><span class='b6 hero\" & IF ( {hero_ng}, \" ng\", \"\" ) & \"'>\" & {hero} & \"</span>\""
         if hero_ng else f"            & \"<div class='linha1'><span class='b6 hero'>\" & {hero} & \"</span>\"") + f"{lado_html} & \"</div>\"",
        f"            & \"<p class='ctx'>\" & {ctx} & \"</p>\"",
        "        & \"</div>\"",
        "        & " + verso,
        "    & \"</div>\"" + (" & [Comum · JS contador]" if anima else ""),
    )
    m(f"T3 · Cartão {chave} · HTML", rf"{TELA}\Cartões",
      desc or f"Cartão '{chave}' da obra em foco (frente e verso). Só lê contas · foco.", dax)


# F3 (docs/08 §5): Desvio, Executado e Previsto eram a mesma conta. Ficam cinco cartões da obra em foco: o atraso em
# meses (o escuro, a resposta de "a obra está no ritmo?"), o executado acumulado (com o previsto e o desvio no
# contexto), o mês, o PPC do mês e o término projetado (com a entrega contratual e os 180 dias de tolerância).
# Os nomes dos visuais da página mudam com os cartões; as marcas seguem os pontos do item da nota (cheio, parcial,
# zero) e os limites vêm do modelo (nenhum número da nota fica escrito aqui).
def cls_item(pts: str, poss: str) -> str:
    """Classe da marca pelos pontos de um item da nota: "0" cheio · "1" parcial · "2" zero · "" sem dado."""
    return f'IF ( ISBLANK ( {pts} ), "", IF ( {pts} >= {poss}, "0", IF ( {pts} = 0, "2", "1" ) ) )'


def marca_item(pts: str, poss: str) -> str:
    c = cls_item(pts, poss)
    return f'IF ( {c} = "", "", "<i class=\'mk mk" & {c} & "\'></i>" )'


def faixas_item(cod: str, p: str) -> list[str]:
    """VARs {p}1 e {p}N: a primeira e a última faixa do item com os pontos ("atraso ≤ 0,5 mês → 2"); {p}1s e {p}Ns
    sem os pontos ("atraso ≤ 0,5 mês"). Texto do modelo, < e > escapados para HTML."""
    def h(x: str) -> str:
        return f'SUBSTITUTE ( SUBSTITUTE ( {x}, "<", "&lt;" ), ">", "&gt;" )'

    def sem(x: str) -> str:
        return f'LEFT ( {x}, SEARCH ( " →", {x}, 1, LEN ( {x} ) + 1 ) - 1 )'
    return [f'VAR {p} = SUBSTITUTE ( CALCULATE ( [Nota · item · faixas], dItemNota[Item] = "{cod}" ), " · ", "|" )',
            f'VAR {p}a = PATHITEM ( {p}, 1 )', f'VAR {p}z = PATHITEM ( {p}, PATHLENGTH ( {p} ) )',
            f'VAR {p}1 = {h(p + "a")}', f'VAR {p}N = {h(p + "z")}',
            f'VAR {p}1s = {h(sem(p + "a"))}', f'VAR {p}Ns = {h(sem(p + "z"))}']


def pts_txt(p: str, pts: str, poss: str) -> list[str]:
    """{p}Txt = "1,5 de 2" com os dois números marcados para o contador (só vai para o conteúdo, nunca a atributo)."""
    return [f'VAR {p}Txt = ' + C.marca(f'FORMAT ( {pts}, "{DC.FMT_PTS}", "pt-BR" )') + ' & " de " & '
            + C.marca(f'FORMAT ( {poss}, "{DC.FMT_PTS}", "pt-BR" )')]


# faixas da nota (texto do modelo, "atraso ≤ 0,5 mês → 2") na régua do verso: o primeiro número conta
REGUA_FX = [("mk0", '" & ' + C.marca("_fx1") + ' & "'), ("mk2", '" & ' + C.marca("_fxN") + ' & "')]


cartao(
    "atraso", '"Atraso · cronograma"',
    [("_atr", "Prazo · atraso (meses) · foco"), ("_ptf", "Nota · pontos prazo · foco"),
     ("_psf", "Nota · possíveis · prazo · foco")],
    ['VAR _taA = ROUND ( ABS ( _atr ), 1 )',
     'VAR _taN = FORMAT ( _taA, "0.0", "pt-BR" )', 'VAR _taTxt = IF ( ISBLANK ( _atr ), "—", _taN )',
     'VAR _txtUn = IF ( _taA <= 1, "mês", "meses" )',
     'VAR _txtLado = IF ( ISBLANK ( _atr ), "", IF ( ROUND ( _atr, 1 ) < 0, _txtUn & " à frente", _txtUn ) )']
    + pts_txt("_tk", "_ptf", "_psf") + faixas_item("prazo", "_fx") + [
        "VAR _txtCtx = IF ( ISBLANK ( _atr ), \"sem curva prevista\", " + marca_item("_ptf", "_psf")
        + " & \"item prazo da nota: \" & _tkTxt )"],
    "_taOd", "_txtLado", "_txtCtx",
    "Meses decorridos menos meses agregados: o executado de hoje é o previsto de quantos meses atrás.",
    "Planilha e cronograma", REGUA_FX, escuro=True,
    desc="Cartão escuro do atraso da obra em foco em meses (cronograma agregado, Lipke), a resposta da pergunta da "
         "tela, com a marca e os pontos do item prazo da nota; o verso traz a regra e a primeira e a última faixa do "
         "item (lidas do modelo). Sem curva prevista: '—'. Só lê contas · foco.",
    anima=D.od_num("_atr", "_ta"))
cartao(
    "executado", '"Executado acumulado"',
    [("_e", "Físico · executado acumulado · foco"), ("_p", "Físico · previsto acumulado · foco"),
     ("_d", "Físico · desvio acumulado p.p. · foco")],
    D.pct("_e", "_te") + D.pct("_p", "_tp") + D.pp("_d", "_td") + [
        "VAR _txtCtx = SWITCH ( TRUE (), ISBLANK ( _e ), \"sem aba no mês\", ISBLANK ( _p ), \"sem previsto na planilha\", "
        "\"previsto \" & " + C.marca("_tpTxt") + " & \" · <span class='\" & IF ( ROUND ( _d, 1 ) < 0, \"ng\", \"\" ) & \"'>\" & "
        + C.marca("_tdTxt") + " & \"</span>\" )"],
    "_teOd", None, "_txtCtx",
    "Quanto da obra já foi feito até o mês, em % do orçamento; ao lado, o previsto da planilha e a diferença.",
    "% executado e % previsto acumulados", None, anima=D.od_pct("_e", "_te"),
    desc="Cartão do executado acumulado da obra em foco, com o previsto acumulado da planilha e o desvio em p.p. no "
         "contexto (negativo em vermelho). Só lê contas · foco.")
cartao(
    "no mês", '"No mês · " & _mesC',
    [("_e", "Físico · executado no mês · foco"), ("_p", "Físico · previsto no mês · foco"),
     ("_mesC", "Mês de referência · curto")],
    D.pct("_e", "_te", casas=2) + D.pct("_p", "_tp", casas=2),
    "_teOd", '"executado"', 'IF ( ISBLANK ( _p ) && NOT ISBLANK ( _e ), "sem previsto na planilha", _tpOd & " previsto" )',
    "Fatia da obra executada só neste mês, ao lado do que o cronograma previa para ele.", "Previsto e executado, mês",
    None, anima=D.od_pct("_e", "_te") + D.od_pct("_p", "_tp"))
cartao(
    "PPC", '"PPC do mês · " & _mesC',
    [("_ppc", "Canteiro · PPC · foco"), ("_pt", "Nota · pontos PPC · foco"), ("_ps", "Nota · possíveis · PPC · foco"),
     ("_meta", "Nota · limite PPC · ponto cheio"), ("_mesC", "Mês de referência · curto")],
    D.pct("_ppc", "_tc", casas=0) + D.pct("_meta", "_tm", casas=0) + pts_txt("_tk", "_pt", "_ps")
    + faixas_item("ppc", "_fx") + [
        "VAR _txtCtx = IF ( ISBLANK ( _ppc ), \"" + DC.FALTA_NA_BASE + "\", " + marca_item("_pt", "_ps")
        + " & \"meta \" & " + C.marca("_tmTxt") + " & \" · na nota, \" & _tkTxt )"],
    "_tcOd", None, "_txtCtx",
    "Tarefas concluídas ÷ prometidas no plano semanal, na média do mês: o sinal que chega antes do atraso.",
    "Base complementar", REGUA_FX, anima=D.od_pct("_ppc", "_tc"),
    desc="Cartão do PPC do mês da obra em foco (plano semanal cumprido), com a meta (o ponto cheio do item PPC da nota) "
         "e os pontos do item; o verso traz a regra e a primeira e a última faixa (lidas do modelo). Sem a base: 'falta "
         "na base'. Só lê contas · foco.")
cartao(
    "término", '"Término projetado"',
    [("_proj", "Prazo · término projetado · foco"), ("_ent", "Prazo · entrega contratual · foco"),
     ("_tol", "Prazo · entrega com tolerância · foco"), ("_sit", "T3 · Término · situação · foco"),
     ("_alem", "T3 · Término · meses além da entrega · foco")],
    ['VAR _txtProj = IF ( ISBLANK ( _proj ), "—", FORMAT ( _proj, "mmm/yy", "pt-BR" ) )',
     'VAR _txtEnt = FORMAT ( _ent, "mmm/yy", "pt-BR" )',
     'VAR _txtTol = FORMAT ( _tol, "mmm/yy", "pt-BR" )',
     "VAR _txtCtx = SWITCH ( TRUE (), ISBLANK ( _ent ), \"sem entrega no cadastro\", ISBLANK ( _proj ), "
     "\"sem curva prevista · entrega \" & _txtEnt, \"<i class='mk mk\" & _sit & \"'></i>entrega \" & _txtEnt & \" · limite \" & _txtTol )"],
    "_txtProj", None, "_txtCtx",
    "Início + duração prevista ÷ IDP(t), o ritmo de prazo pelo cronograma agregado. Limite: a entrega + 180 dias.",
    "Cronograma, planilha e cadastro", [("mk0", "até a entrega"), ("mk1", "nos 180 dias"), ("mk2", "depois deles")],
    desc="Cartão do término projetado da obra em foco (Lipke, IEAC(t)), com a entrega contratual e a entrega com os 180 "
         "dias de tolerância (Lei 4.591/64, art. 43-A) no contexto; a marca diz onde o término projetado cai: até a "
         "entrega, nos 180 dias ou depois deles. Datas não contam. Só lê contas · foco.")

# ======================================================================================================== Curva S
CURVA = rf"{TELA}\Curva S"
PAINEIS = rf"{TELA}\Painéis"
# painel v2 (Figma 387:4403, 900 × 370): cabeçalho HTML em y 0–54 (legenda na linha do título até x 858, subtítulo em
# y 32); gráfico de y 68 a 370 do painel (visual 900 × 302): 0% em y 262, eixo y à esquerda (rótulos até x 44, grade de
# x 52 a 744), meses de x 64 a 736 (passo 672 ÷ (n − 1)), rótulos finais a partir de x último + 16, meses em y 272.
# Janela de 1 a 12 meses (dJanela): x = [Série · posição na janela]; mês da janela sem aba da obra fica vazio (rótulo
# a 50%).
X0, X1 = 64, 736                 # primeiro e último mês da janela
Y_BASE, Y_TETO = 262, 28
# cabeçalho dos painéis (subtítulo e legenda): o título e o "?" estão no papel de parede
CSS_PAINEL_CAB = (
    ".pc{position:fixed;inset:0;white-space:nowrap}"
    f".pc .sub{{position:absolute;left:0;top:32px;font-size:15px;line-height:20px;color:{GRAFITE}}}"
    ".pc .lg{position:absolute;right:0;top:4px;height:20px;display:flex;align-items:center;font-size:14px;"
    f"line-height:19px;color:{GRAFITE}}}"
    ".pc .lg svg,.pc .lg i{display:block;flex:none;margin-right:6px}"
    ".pc .lg span{margin-right:18px}.pc .lg span:last-child{margin-right:0}"
    f".pc .lg .ar{{width:14px;height:12px;background:{VERM_CLARO}}}"
    ".pc .lg .sw{width:12px;height:12px}"
    f".pc .lg .sp{{color:{TERC};margin-left:-12px}}"
)
css("T3 · Painel · CSS cabeçalho", PAINEIS, "CSS do cabeçalho dos painéis da Tela 03 (subtítulo e legenda).", CSS_PAINEL_CAB)
m("T3 · Curva S · HTML cabeçalho", CURVA,
  "Subtítulo da Curva S com os meses da série da obra em foco na janela (jan/26 a ago/26) e a legenda na linha do "
  "título (executado, previsto, executado abaixo do previsto), Figma 387:4403. Obra sem previsto na planilha "
  "(JANGADA): o subtítulo fala só do executado e a legenda diz 'sem previsto na planilha'.",
  linhas(
      "-- 1 · Leituras",
      "VAR _ini = [T3 · Série · primeiro mês da obra · foco]",
      "VAR _ref = [Mês de referência]",
      "VAR _p = [Físico · previsto acumulado · foco]",
      "VAR _e = [Físico · executado acumulado · foco]",
      "-- 2 · Textos",
      'VAR _txtIni = FORMAT ( _ini, "mmm/yy", "pt-BR" )',
      'VAR _txtRef = FORMAT ( _ref, "mmm/yy", "pt-BR" )',
      'VAR _txtMeses = IF ( ISBLANK ( _ini ) || _ini = _ref, _txtRef, _txtIni & " a " & _txtRef )',
      "VAR _semP = ISBLANK ( _p ) && NOT ISBLANK ( _e )",
      'VAR _txtSub = IF ( _semP, "executado acumulado, ", "previsto × executado acumulado, " ) & _txtMeses '
      '& " · % do orçamento"',
      "-- 4 · Marcação",
      "VAR _lgExec =",
      "    \"<svg width='18' height='3'><path d='M0 1.5H18' stroke='#0B0B0C' stroke-width='3'/></svg><span>executado</span>\"",
      "VAR _lgPrev =",
      "    \"<svg width='18' height='2'><path d='M0 1H18' stroke='#3B3B3F' stroke-width='2' stroke-dasharray='5 4'/></svg>\"",
      "        & \"<span>previsto</span><i class='ar'></i><span>executado abaixo do previsto</span>\"",
      "RETURN",
      "    \"<div class='u pc'><span class='sub'>\" & _txtSub & \"</span><div class='lg'>\" & _lgExec",
      "        & IF ( _semP, \"<span class='sp'>· sem previsto na planilha</span>\", _lgPrev )",
      "    & \"</div></div>\"",
  ))
for chave, pasta, texto_sub, desc, leg in [
        ("Avanço", rf"{TELA}\Avanço das obras", "executado × previsto acumulado · à direita, o atraso em meses",
         "Subtítulo do Avanço das obras, Figma 387:4415 (F3: o número da direita é o atraso em meses).", ""),
        ("Linha do tempo", rf"{TELA}\Linha do tempo das obras",
         "início → término previsto · preenchido = executado · ◆ = término projetado · hachura = 180 dias após a entrega",
         "Subtítulo da Linha do tempo das obras, Figma 387:4421 (a legenda da faixa fica no pé do gráfico; F3: a marca "
         "do término projetado e a faixa dos 180 dias de tolerância).", "")]:
    corpo = (f"<div class='u pc'><span class='sub'>{texto_sub}</span>" + (f"<div class='lg'>{leg}</div>" if leg else "")
             + "</div>")
    m(f"T3 · {chave} · HTML cabeçalho", pasta, desc, "-- 4 · Marcação\n" + dax_lit(corpo))

CSS_CURVA = (
    ".cs{position:fixed;inset:0}"
    ".cs svg{position:absolute;left:0;top:0;overflow:visible}"
    f".cs .ey{{position:absolute;left:0;width:44px;text-align:right;font-size:13px;line-height:16px;color:{TERC}}}"
    f".cs .ex{{position:absolute;width:60px;text-align:center;font-size:13px;line-height:16px;color:{GRAFITE}}}"
    f".cs .ex.ref{{font-weight:600;color:{PRETO}}}.cs .ex.sem{{opacity:.5}}"
    f".cs .vz{{position:absolute;left:64px;top:110px;font-size:14px;line-height:19px;color:{GRAFITE}}}"
    ".cs .fp{position:absolute;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:14px;"
    f"line-height:17px;color:{GRAFITE};white-space:nowrap}}"
    ".cs .fe{position:absolute;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:14px;"
    f"line-height:17px;color:{PRETO};white-space:nowrap}}"
    ".cs .dv{position:absolute;height:17px;padding:0 4px;background:#FFFFFF;"
    "font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:14px;line-height:17px;white-space:nowrap}"
    # o recorte que revela cada linha da esquerda para a direita (o previsto primeiro)
    ".cs .rv{transform-box:fill-box;transform-origin:left center;animation:t3Rv 1s cubic-bezier(.2,.7,.2,1) backwards}"
    ".cs .rv.e{animation-delay:.25s}"
    "@keyframes t3Rv{from{transform:scaleX(0)}}"
    ".cs .ar{animation:t3Fd .5s ease-out 1.1s backwards}"
    # F4: os pontos entram crescendo do centro (cbPop do CSS base), cada um quando a linha passa por ele
    ".cs .pt{transform-box:fill-box;transform-origin:center;animation:cbPop .3s cubic-bezier(.2,.7,.2,1) backwards}"
    ".cs .fp,.cs .fe,.cs .dv,.cs .ch{animation:t3Fd .3s ease-out 1.1s backwards}"
    "@keyframes t3Fd{from{opacity:0}}"
)
css("T3 · Curva S · CSS", CURVA, "CSS do gráfico da Curva S (eixos, linhas, área, pontos e rótulos finais).", CSS_CURVA)

GEO_CURVA = [
    "VAR _passoX = IF ( _n > 1, DIVIDE ( " + str(X1 - X0) + ", _n - 1 ), 0 ) /* geometria */",
    "VAR _maxV = MAXX ( _serie, MAX ( [@p], [@e] ) ) /* geometria */",
    "VAR _passoY = SWITCH ( TRUE (), _maxV <= 0.4, 0.1, _maxV <= 0.8, 0.2, 0.25 ) -- geometria",
    "VAR _teto = MAX ( _passoY, CEILING ( _maxV / _passoY, 1 ) * _passoY ) -- geometria",
    f"VAR _escY = DIVIDE ( {Y_BASE - Y_TETO:.2f}, _teto ) /* geometria */",
]


def ponto_x(pos: str) -> str:
    """x do mês na janela; com um mês só (referência = jan/26), o ponto fica na ponta direita, como a referência."""
    return f"ROUND ( IF ( _n > 1, {X0} + ( {pos} - 1 ) * _passoX, {X1} ), 0 )"


def ponto_y(v: str) -> str:
    return f"ROUND ( {Y_BASE} - {v} * _escY, 0 )"


m("T3 · Curva S · HTML gráfico", CURVA,
  "Curva S da obra em foco (Figma 289:7413) na janela escolhida (1 a 12 meses): previsto acumulado (tracejado, só "
  "nos meses que o trazem) e executado acumulado (sólido) nos meses com aba (L044), x pela posição na janela; a área "
  "do executado abaixo do previsto (só quando todos os meses trazem o previsto), a grade em % do orçamento com escala "
  "pelo maior valor, todos os meses da janela no eixo (sem aba a 50%), os rótulos finais (contam) e a chave do desvio. "
  "Obra sem previsto na planilha: só o executado, sem área, rótulo do previsto nem chave. Sem granularidade: o "
  "tooltip do mês vem do visual de cima (T3 · Curva S · HTML mês).",
  linhas(
      "-- 1 · Leituras",
      "VAR _ref = [Mês de referência]",
      "VAR _n = [Série · meses até a referência]",
      "VAR _meses =",
      "    ADDCOLUMNS (",
      "        VALUES ( dMes[Mes] ),",
      '        "@ate", [Série · mês até a referência],',
      '        "@pj", [Série · posição na janela],',
      '        "@na", [T3 · Série · mês na série · foco no mês],',
      '        "@p", [Físico · previsto acumulado · foco no mês],',
      '        "@e", [Físico · executado acumulado · foco no mês],',
      '        "@rot", [Mês · rótulo curto]',
      "    )",
      "VAR _janela = FILTER ( _meses, [@ate] = 1 ) /* lista */",
      "VAR _serie = FILTER ( _janela, [@na] = 1 ) /* lista */",
      "VAR _pRef = [Físico · previsto acumulado · foco]",
      "VAR _eRef = [Físico · executado acumulado · foco]",
      "VAR _dRef = [Físico · desvio acumulado p.p. · foco]",
      "-- 2 · Textos",
      D.pct("_pRef", "_tpr") + D.pct("_eRef", "_ter") + D.pp("_dRef", "_tdr"),
      D.od_tabela(), D.od_pct("_pRef", "_tpr"), D.od_pct("_eRef", "_ter"), D.od_pp("_dRef", "_tdr"),
      "-- 3 · Geometria",
      GEO_CURVA,
      "VAR _pts = ADDCOLUMNS ( _serie, \"@x\", " + ponto_x("[@pj]") + ", \"@ye\", " + ponto_y("[@e]") + " ) /* geometria */",
      "VAR _ptsP = ADDCOLUMNS ( FILTER ( _pts, NOT ISBLANK ( [@p] ) ), \"@yp\", " + ponto_y("[@p]") + " ) /* geometria */",
      "VAR _nObra = COUNTROWS ( _pts ) -- geometria",
      "VAR _nP = COUNTROWS ( _ptsP ) + 0 -- geometria",
      "VAR _cheia = _nP > 0 && _nP = _nObra -- geometria",
      "VAR _pU = MAXX ( _pts, [@pj] ) /* geometria */",
      "VAR _p1 = MINX ( _pts, [@pj] ) /* geometria */",
      f"VAR _xU = {ponto_x('_pU')} -- geometria",
      f"VAR _x1 = {ponto_x('_p1')} -- geometria",
      f"VAR _yP = IF ( NOT ISBLANK ( _pRef ), {ponto_y('_pRef')} ) -- geometria",
      f"VAR _yE = {ponto_y('_eRef')} -- geometria",
      "VAR _temChave = NOT ISBLANK ( _pRef ) && NOT ISBLANK ( _eRef ) -- geometria",
      "VAR _gap = IF ( _temChave, ABS ( _yE - _yP ), 99 ) -- geometria",
      "VAR _meioY = IF ( _temChave, ROUND ( ( _yP + _yE ) / 2, 0 ), _yE ) -- geometria",
      "VAR _yLP = IF ( _gap < 18, IF ( _yP <= _yE, _meioY - 18, _meioY ), _yP - 9 ) -- geometria",
      "VAR _yLE = IF ( _gap < 18, IF ( _yP <= _yE, _meioY, _meioY - 18 ), _yE - 9 ) -- geometria",
      "VAR _xCh = _xU - 12 -- geometria",
      "VAR _nLinhas = ROUND ( _teto / _passoY, 0 ) -- geometria",
      "-- 4 · Marcação",
      "VAR _dPrev =",
      "    CONCATENATEX (",
      "        _ptsP,",
      "        VAR _k = [@pj]",
      "        VAR _segue = NOT ISEMPTY ( FILTER ( _ptsP, [@pj] = _k - 1 ) ) /* geometria */",
      "        RETURN",
      "            IF ( _segue, \" L\", \" M\" ) & [@x] & \",\" & [@yp],",
      "        \"\",",
      "        [@pj], ASC",
      "    )",
      "VAR _dExec = \"M\" & CONCATENATEX ( _pts, [@x] & \",\" & [@ye], \" L\", [@pj], ASC )",
      "VAR _dExecInv = CONCATENATEX ( _pts, [@x] & \",\" & [@ye], \" L\", [@pj], DESC )",
      f"VAR _clipSob = _dPrev & \" L\" & _xU & \",{Y_BASE} L\" & _x1 & \",{Y_BASE} Z\"",
      "VAR _area = \"M\" & _x1 & \",0 L\" & _xU & \",0 L\" & _dExecInv & \" Z\"",
      "VAR _grade =",
      "    CONCATENATEX (",
      "        GENERATESERIES ( 0, _nLinhas ),",
      f"        VAR _y = ROUND ( {Y_BASE} - [Value] * _passoY * _escY, 0 ) /* geometria */",
      "        VAR _txt = " + C.marca('FORMAT ( [Value] * _passoY * 100, \"0\", \"pt-BR\" )') + " & \"%\"",
      "        RETURN",
      f"            \"<i class='a-fd' style='position:absolute;left:52px;top:\" & _y & \"px;width:692px;height:1px;background:\"",
      "                & IF ( [Value] = 0, \"#E1E1E1\", \"#EFEFEF\" ) & \"'></i>\"",
      "                & \"<span class='ey' style='top:\" & ( _y - 8 ) & \"px'>\" & _txt & \"</span>\",",
      "        \"\",",
      "        [Value], ASC",
      "    )",
      "VAR _pontos =",
      "    CONCATENATEX (",
      "        _pts,",
      "        VAR _atraso = ROUND ( 100 + DIVIDE ( [@x] - " + str(X0) + ", " + str(X1 - X0) + " ) * 900, 0 ) /* geometria */",
      "        RETURN",
      "            \"<circle class='pt' cx='\" & [@x] & \"' cy='\" & [@ye] & \"' r='4.5' fill='#0B0B0C' \"",
      "                & \"style='animation-delay:\" & ( _atraso + 250 ) & \"ms'/>\",",
      "        \"\",",
      "        [@pj], ASC",
      "    )",
      "VAR _pontosP =",
      "    CONCATENATEX (",
      "        _ptsP,",
      "        VAR _atraso = ROUND ( 100 + DIVIDE ( [@x] - " + str(X0) + ", " + str(X1 - X0) + " ) * 900, 0 ) /* geometria */",
      "        RETURN",
      "            \"<circle class='pt' cx='\" & [@x] & \"' cy='\" & [@yp] & \"' r='3.75' fill='#FFFFFF' stroke='#3B3B3F' \"",
      "                & \"stroke-width='1.5' style='animation-delay:\" & _atraso & \"ms'/>\",",
      "        \"\",",
      "        [@pj], ASC",
      "    )",
      "VAR _eixoX =",
      "    CONCATENATEX (",
      "        _janela,",
      f"        VAR _x = {ponto_x('[@pj]')} /* geometria */",
      f"        VAR _atraso = ROUND ( DIVIDE ( _x - {X0}, {X1 - X0} ) * 600, 0 ) /* geometria */",
      "        RETURN",
      "            \"<span class='ex a-fd\" & IF ( dMes[Mes] = _ref, \" ref\", IF ( [@na] = 1, \"\", \" sem\" ) ) & \"' style='left:\"",
      "                & ( _x - 30 ) & \"px;top:272px;animation-delay:\" & _atraso & \"ms'>\" & [@rot] & \"</span>\",",
      "        \"\",",
      "        [@pj], ASC",
      "    )",
      "VAR _svg =",
      "    \"<svg width='900' height='302' viewBox='0 0 900 302' aria-hidden='true'><defs>\"",
      "        & IF ( _cheia, \"<clipPath id='t3cs'><path d='\" & _clipSob & \"'/></clipPath>\" )",
      "        & \"<clipPath id='t3rp'><rect class='rv' x='0' y='0' width='900' height='302'/></clipPath>\"",
      "        & \"<clipPath id='t3re'><rect class='rv e' x='0' y='0' width='900' height='302'/></clipPath></defs>\"",
      "        & IF ( _cheia, \"<path class='ar' d='\" & _area & \"' fill='#F7E3E3' clip-path='url(#t3cs)'/>\" )",
      "        & IF ( _nP > 0, \"<path d='\" & _dPrev & \"' fill='none' stroke='#3B3B3F' stroke-width='2' \"",
      "            & \"stroke-linecap='round' stroke-linejoin='round' stroke-dasharray='6 5' clip-path='url(#t3rp)'/>\" )",
      "        & \"<path d='\" & _dExec & \"' fill='none' stroke='#0B0B0C' stroke-width='2.6' stroke-linecap='round' \"",
      "        & \"stroke-linejoin='round' clip-path='url(#t3re)'/>\"",
      "        & IF ( _temChave && _gap >= 2, \"<path class='ch' d='M\" & ( _xCh + 4 ) & \",\" & _yP & \" H\" & _xCh & \" V\" & _yE",
      "            & \" H\" & ( _xCh + 4 ) & \"' fill='none' stroke='#0B0B0C' stroke-width='1.2' stroke-linecap='round' \"",
      "            & \"stroke-linejoin='round'/>\" )",
      "        & _pontosP & _pontos",
      "    & \"</svg>\"",
      "RETURN",
      "    IF (",
      "        _nObra > 0,",
      "        \"<div class='u cs'>\" & _grade & _svg & _eixoX",
      "            & IF ( _temChave, \"<span class='fp' style='left:\" & ( _xU + 16 ) & \"px;top:\" & _yLP & \"px'>\" & _tprOd",
      "                & \" previsto</span>\" )",
      "            & \"<span class='fe' style='left:\" & ( _xU + 16 ) & \"px;top:\" & _yLE & \"px'>\" & _terOd & \" executado</span>\"",
      "            & IF ( _temChave, \"<span class='dv\" & IF ( ROUND ( _dRef, 1 ) < 0, \" ng\", \"\" ) & \"' style='right:\" & ( 906 - _xCh ) & \"px;top:\" & MAX ( 0, MIN ( _yP, _yE ) - 22 )",
      "                & \"px'>\" & _tdrOd & \"</span>\" )",
      "        & \"</div>\" & [Comum · JS contador],",
      "        \"<div class='u cs'><p class='vz'>Sem aba da obra na janela: a série começa na primeira aba da planilha.</p></div>\"",
      "    )",
  ))

CSS_CURVA_MES = (
    "#htmlContent{display:flex!important;align-items:stretch;height:100vh}"
    ".htmlViewerEntry{display:block!important;flex:none;margin:0!important;padding:0!important;height:100vh}"
    ".hm{position:relative;height:100vh;cursor:default}"
    f".hm i{{position:absolute;top:{round(Y_TETO)}px;height:{Y_BASE - round(Y_TETO)}px;width:1px;"
    "background:rgba(11,11,12,.3);opacity:0;transition:opacity .15s}"
    ".hm:hover i,.htmlViewerEntry.hover .hm i{opacity:1}"
)
css("T3 · Curva S · CSS mês", CURVA, "CSS das colunas invisíveis da Curva S (uma por mês: alvo do tooltip).",
    CSS_CURVA_MES)
m("T3 · Curva S · HTML mês", CURVA,
  "Uma coluna invisível por mês da série (granularidade dMes[Mes]) sobre a Curva S: é o alvo estável do mouse que abre "
  "o tooltip do mês (L012) e mostra a linha-guia no mês. x pela posição na janela; a coluna vai da metade do caminho "
  "desde o mês anterior com aba (ou da borda, no primeiro) até a metade do caminho para o seguinte (ou a borda, na "
  "referência), então os meses vazios da janela ficam com o mês seguinte; vazio fora da série.",
  linhas(
      "-- 1 · Leituras",
      "VAR _na = [T3 · Série · mês na série · foco no mês]",
      "VAR _pj = [Série · posição na janela]",
      "VAR _ant = [T3 · Série · posição da aba anterior · foco no mês]",
      "VAR _n = [Série · meses até a referência]",
      "-- 3 · Geometria",
      f"VAR _passoX = IF ( _n > 1, DIVIDE ( {X1 - X0}, _n - 1 ), 0 ) /* geometria */",
      f"VAR _x = ROUND ( IF ( _n > 1, {X0} + ( _pj - 1 ) * _passoX, {X1} ), 0 ) -- geometria",
      f"VAR _b0 = IF ( _ant = 0, 0, ROUND ( {X0} + ( _ant - 0.5 ) * _passoX, 0 ) ) -- geometria",
      f"VAR _b1 = IF ( _pj = _n, 860, ROUND ( {X0} + ( _pj - 0.5 ) * _passoX, 0 ) ) -- geometria",
      "-- 4 · Marcação",
      "RETURN",
      "    IF (",
      "        _na = 1,",
      "        \"<div class='u hm' style='width:\" & ( _b1 - _b0 ) & \"px'><i style='left:\" & ( _x - _b0 ) & \"px'></i></div>\"",
      "    )",
  ))

# ======================================================================================================== PPC mês a mês
# F3 (docs/08 §5): o Ritmo do mês (previsto × executado de cada mês) é a derivada da curva S e já está no tooltip do mês
# da curva; sai. No lugar (painel 1292,273, 568 × 290) entra o PPC da obra em foco mês a mês: o plano semanal cumprido,
# o sinal que chega antes do atraso. Cabeçalho HTML em y 0–54 (legenda na linha do título, subtítulo em y 32); colunas
# de y 68 a 290 do painel (visual 568 × 222), uma entrada por mês da janela (granularidade dMes, colunas iguais), base em
# y 190 e meses em y 198. Escala fixa: 100% = 150 px, então a linha da meta (o ponto cheio do item PPC da nota, lido do
# modelo) fica no mesmo lugar para todas as obras. Barra na cor dos pontos do item no mês (cheio sálvia, parcial ocre,
# zero vermelho); rótulo em todos os meses até oito, senão na referência, no maior e no menor. Mês sem base: só o mês,
# apagado.
PPC = rf"{TELA}\PPC mês a mês"
P_BASE, P_ESC = 190, 150
HALO = ("text-shadow:1px 0 0 #FFF,-1px 0 0 #FFF,0 1px 0 #FFF,0 -1px 0 #FFF,1px 1px 0 #FFF,-1px -1px 0 #FFF,"
        "1px -1px 0 #FFF,-1px 1px 0 #FFF,0 0 3px #FFF")
CSS_PPC = (
    "#htmlContent{display:flex!important;align-items:flex-start;width:100vw;height:100vh;margin:0!important;"
    "padding:0!important;box-sizing:border-box!important}"
    ".htmlViewerEntry{display:block!important;flex:1 1 0;min-width:0;margin:0!important;padding:0!important}"
    f".pm{{position:relative;height:222px;transition:background .15s}}"
    ".pm:hover,.htmlViewerEntry.hover .pm{background:rgba(233,224,207,.35)}"
    f".pm .l0{{position:absolute;left:0;right:0;top:{P_BASE}px;height:1px;background:{REGRA}}}"
    f".pm .lm{{position:absolute;left:0;right:0;height:0;border-top:1px dashed {PRETO}}}"
    f".pm .b{{position:absolute;bottom:{222 - P_BASE}px;left:calc(50% - 11px);width:22px}}"
    f".pm .b.q0{{background:{SALVIA}}}.pm .b.q1{{background:{DC.OCRE}}}.pm .b.q2{{background:{VERM}}}"
    ".pm .v{position:absolute;left:-30px;right:-30px;text-align:center;font-family:'Barlow U','Segoe UI',sans-serif;"
    f"font-weight:600;font-size:14px;line-height:17px;white-space:nowrap;font-variant-numeric:tabular-nums;color:{PRETO};{HALO}}}"
    f".pm .v.ng{{color:{VERM}}}"
    f".pm .ms{{position:absolute;left:-12px;right:-12px;top:{P_BASE + 8}px;text-align:center;font-size:13px;line-height:16px;"
    f"white-space:nowrap;color:{GRAFITE}}}"
    f".pm .ms.ref{{font-weight:600;color:{PRETO}}}.pm .ms.sem{{opacity:.35}}"
    f".pm .vz{{position:absolute;left:4px;top:60px;font-size:14px;line-height:19px;color:{GRAFITE};white-space:nowrap}}"
)
css("T3 · PPC · CSS", PPC, "CSS do PPC mês a mês (uma entrada por mês da janela; colunas iguais).", CSS_PPC)
m("T3 · PPC · HTML cabeçalho", PPC,
  "Subtítulo do PPC mês a mês com a meta e a janela em uso (média do mês · tracejado na meta, 80% · jan–set/26) e, "
  "na linha do título, a legenda das cores pelos pontos do item PPC da nota. A meta vem de [Nota · "
  "limite PPC · ponto cheio].",
  linhas(
      "-- 1 · Leituras",
      "VAR _ini = [Série · primeiro mês]",
      "VAR _ref = [Mês de referência]",
      "VAR _n = [Série · meses até a referência]",
      "VAR _meta = [Nota · limite PPC · ponto cheio]",
      "-- 2 · Textos",
      "VAR _txtRef = FORMAT ( _ref, \"mmm/yy\", \"pt-BR\" )",
      "VAR _txtIni = IF ( YEAR ( _ini ) = YEAR ( _ref ), FORMAT ( _ini, \"mmm\", \"pt-BR\" ), FORMAT ( _ini, \"mmm/yy\", \"pt-BR\" ) )",
      "VAR _txtJanela = IF ( _n <= 1, _txtRef, _txtIni & \"–\" & _txtRef )",
      "VAR _txtSub = \"média do mês · tracejado na meta, \" & " + C.marca('FORMAT ( _meta, \"0%\", \"pt-BR\" )') + " "
      "& \" · \" & _txtJanela",
      "-- 4 · Marcação",
      "RETURN",
      "    \"<div class='u pc'><span class='sub'>\" & _txtSub & \"</span><div class='lg'>\"",
      f"        & \"<i class='sw' style='background:{SALVIA}'></i><span>na meta</span><i class='sw' style='background:{DC.OCRE}'>\"",
      f"        & \"</i><span>perde parte</span><i class='sw' style='background:{VERM}'></i><span>zera</span></div></div>\"",
      "        & [Comum · JS contador]",
  ))
m("T3 · PPC · HTML coluna", PPC,
  "PPC da obra em foco mês a mês: uma entrada por mês da janela (granularidade dMes, colunas iguais), a barra de 0 ao "
  "PPC (escala fixa, 100% = 150 px) na cor dos pontos do item PPC da nota no mês (cheio sálvia, parcial ocre, zero "
  "vermelho), a linha tracejada da meta atravessando as colunas, o valor no mês de referência, no maior e no menor (em "
  "todos até oito meses) e o mês no eixo (com mais de oito meses, só a sigla; o ano no primeiro mês e em janeiro). Mês "
  "sem base: só o mês, apagado. As barras correm do primeiro ao último mês; o mouse abre o tooltip do mês.",
  linhas(
      "-- 1 · Leituras",
      "VAR _noRecorte = [Série · mês até a referência]",
      "VAR _n = [Série · meses até a referência]",
      "VAR _pos = [Série · posição na janela]",
      "VAR _mesAno = [Mês · rótulo curto]",
      "VAR _mesAbrev = [Mês · abreviado]",
      "VAR _ehRef = [Série · é o mês de referência]",
      "VAR _ppc = [Canteiro · PPC · foco no mês]",
      "VAR _pt = [Nota · pontos PPC · foco no mês]",
      "VAR _ps = [Nota · possíveis · PPC · foco no mês]",
      "VAR _extremo = [T3 · PPC · mês com rótulo]",
      "VAR _meta = [Nota · limite PPC · ponto cheio]",
      "VAR _nCom = [T3 · PPC · meses com PPC · foco]",
      "-- 3 · Geometria",
      f"VAR _yMeta = {P_BASE} - ROUND ( _meta * {P_ESC}, 0 ) -- geometria",
      f"VAR _h = MAX ( 2, ROUND ( MIN ( _ppc, 1 ) * {P_ESC}, 0 ) ) -- geometria",
      f"VAR _yRot = {P_BASE} - _h - 20 -- geometria",
      "VAR _atraso = ( _pos - 1 ) * ROUND ( DIVIDE ( 420, _n ), 0 ) -- geometria",
      "-- 2 · Textos",
      "VAR _cls = IF ( ISBLANK ( _pt ), \"\", \"q\" & IF ( _pt >= _ps, \"0\", IF ( _pt = 0, \"2\", \"1\" ) ) )",
      "VAR _rotula = NOT ISBLANK ( _ppc ) && ( _ehRef = 1 || _extremo = 1 || _n <= 8 )",
      "VAR _txtV = FORMAT ( _ppc, \"0%\", \"pt-BR\" )",
      "VAR _comAno = _n <= 8 || _pos = 1 || _mesAbrev = \"jan\"",
      "VAR _rotMes = IF ( _comAno, _mesAno, _mesAbrev )",
      "-- 4 · Marcação",
      "RETURN",
      "    IF (",
      "        _noRecorte = 1,",
      "        \"<div class='u pm'><i class='l0 a-fd'></i>\"",
      "            & IF ( _nCom > 0, \"<i class='lm a-gx' style='top:\" & _yMeta & \"px;animation-delay:\" & _atraso & \"ms'></i>\" )",
      "            & IF ( ISBLANK ( _ppc ), \"\", \"<i class='b \" & _cls & \"' style='height:\" & _h",
      "                & \"px' data-rk='m\" & _pos & \"' data-rp='height' data-rd='\" & _atraso & \"'></i>\" )",
      "            & IF ( _rotula, \"<span class='v\" & IF ( _cls = \"q2\", \" ng\", \"\" ) & \"' style='top:\" & _yRot & \"px'>\" & "
      + C.marca("_txtV") + " & \"</span>\" )",
      "            & \"<span class='ms a-fd\" & IF ( _ehRef = 1, \" ref\", IF ( ISBLANK ( _ppc ), \" sem\", \"\" ) ) & \"' style='animation-delay:\" "
      "& _atraso & \"ms'>\" & _rotMes & \"</span>\"",
      "            & IF ( _nCom = 0 && _pos = 1, \"<p class='vz'>Sem PPC da obra na base complementar da janela.</p>\" )",
      "        & \"</div>\" & [Comum · JS contador] & [Comum · JS corrida]",
      "    )",
  ))

# ======================================================================================================== Avanço das obras
AVANCO = rf"{TELA}\Avanço das obras"


def css_faixa(sel: str) -> str:
    """Cor da barra de executado pelos pontos do ITEM PRAZO DA NOTA (F3): s0 ponto cheio sálvia · s1 perde parte ocre ·
    s2 zera vermelho · sx sem curva prevista, neutra (grafite)."""
    return (f"{sel}.s0{{background:{SALVIA}}}{sel}.s1{{background:{DC.OCRE}}}{sel}.s2{{background:{VERM}}}"
            f"{sel}.sx{{background:{GRAFITE}}}")


CLS_PRAZO = 'IF ( ISBLANK ( _pt ), "x", IF ( _pt >= _ps, "0", IF ( _pt = 0, "2", "1" ) ) )'


def legenda_prazo() -> list[str]:
    """VAR _lgMk: as quatro marcas da cor do item prazo (primeira faixa, perde parte, última faixa, sem curva)."""
    return faixas_item("prazo", "_fx") + [
        "VAR _lgMk = \"<span><i class='mk mk0'></i>\" & " + C.marca("_fx1s") + " & \"</span><span><i class='mk mk1'></i>perde parte</span>\"",
        "    & \"<span><i class='mk mk2'></i>\" & " + C.marca("_fxNs") + " & \"</span><span><i class='mk mkx'></i>sem curva prevista</span>\""]


# painel v2 (Figma 387:4415, 568 × 437): cabeçalho HTML em y 0–54; linhas de 42 px a partir de y 72 (visual 568 × 294:
# as sete obras da F2; eram seis linhas de 48): nome Barlow 18 em x 14 (PONTA NEGRA cabe), trilho de 282 px em x 140
# (y 8, 12 de altura),
# traço do previsto (y 4, 20 de altura), "executado × previsto" Segoe 14 sob a barra (y 23), marca + atraso em meses
# Barlow 16 à direita (x 556); obra em foco
# com fundo offwhite e filete preto de 3 px à esquerda. Legenda de três linhas no pé (y 368, 568 × 61).
CSS_AVANCO = (
    ".htmlViewerEntry{display:block!important;margin:0!important;padding:0!important}"
    ".av{position:relative;height:42px;transition:background .15s}"
    f".av.foco{{background:{OFF};box-shadow:inset 3px 0 0 {PRETO}}}"
    ".av:hover,.htmlViewerEntry.hover .av{background:rgba(233,224,207,.4)}"
    ".av .nm{position:absolute;left:14px;top:9px;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;"
    "font-size:18px;line-height:22px;white-space:nowrap}"
    f".av .tr{{position:absolute;left:140px;top:8px;width:282px;height:12px;background:{TRILHA}}}"
    ".av .fl{position:absolute;left:140px;top:8px;height:12px}"
    + css_faixa(".av .fl") +
    f".av .pv{{position:absolute;top:4px;width:2px;height:20px;background:{PRETO}}}"
    f".av .tx{{position:absolute;left:140px;top:23px;font-size:14px;line-height:19px;color:{GRAFITE};white-space:nowrap}}"
    ".av .dr{position:absolute;right:12px;top:11px;display:flex;align-items:center;gap:8px;white-space:nowrap}"
    ".av .dv{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:16px;line-height:20px}"
    f".av .sp{{position:absolute;right:12px;top:12px;font-size:14px;line-height:19px;color:{TERC};white-space:nowrap}}"
)
css("T3 · Avanço · CSS", AVANCO, "CSS da lista Avanço das obras (uma entrada por obra) e da legenda do pé.",
    CSS_AVANCO + (".lga{position:fixed;inset:0;font-size:14px;line-height:19px;white-space:nowrap}"
                  f".lga p{{display:flex;align-items:center;height:21px;color:{GRAFITE}}}"
                  ".lga span{display:inline-flex;align-items:center;gap:6px;margin-right:16px}"
                  f".lga .mk.mkx{{background:{GRAFITE}}}"))
m("T3 · Avanço · HTML legenda", AVANCO,
  "Legenda do Avanço das obras (pé do painel): a barra é o executado na cor dos pontos do item prazo da nota, o traço "
  "é o previsto e o número é o atraso em meses; marcas da primeira e da última faixa do item (lidas do modelo), de "
  "quem perde parte dos pontos e de sem curva prevista.",
  linhas(
      "-- 2 · Textos",
      legenda_prazo(),
      "-- 4 · Marcação",
      "RETURN",
      "    \"<div class='u lga'><p>barra = executado na cor do item prazo · traço = previsto · número = atraso (meses)</p><p>\"",
      "        & _lgMk & \"</p></div>\" & [Comum · JS contador]",
  ))
m("T3 · Avanço · HTML linha", AVANCO,
  "Uma linha por obra com aba no mês de referência (granularidade dObra[Obra], ordem T3 · Avanço · posição): nome, "
  "trilho com o executado acumulado na cor dos pontos do item prazo da nota (cheio sálvia, perde parte ocre, zera "
  "vermelho; grafite sem curva prevista), traço do previsto (quando a aba traz), 'executado × previsto', a marca e o "
  "atraso em meses (conta; vermelho quando zera o item); a obra em foco vem destacada (Figma 289:7425). A ordem é a "
  "da nota (pontos perdidos). Sem curva prevista: 'sem curva prevista' no lugar do atraso.",
  linhas(
      "-- 1 · Leituras",
      "VAR _pos = [T3 · Avanço · posição]",
      "VAR _obra = [Obra · nome]",
      "VAR _e = [Físico · executado acumulado · ref]",
      "VAR _p = [Físico · previsto acumulado · ref]",
      "VAR _a = [Prazo · atraso (meses) · ref]",
      "VAR _pt = [Nota · pontos prazo · ref]",
      "VAR _ps = [Nota · possíveis · prazo · ref]",
      "VAR _foco = [T3 · Avanço · é a obra em foco]",
      "-- 2 · Textos",
      D.pct("_e", "_te") + D.pct("_p", "_tp"),
      "VAR _aA = ROUND ( ABS ( _a ), 1 )",
      "VAR _taN = FORMAT ( _aA, \"0.0\", \"pt-BR\" )",
      "VAR _taS = IF ( ROUND ( _a, 1 ) < 0, \"" + MENOS + "\", \"\" )",
      "VAR _taTxt = _taS & _taN & IF ( _aA <= 1, \" mês\", \" meses\" )",
      D.od_tabela(),
      D._od("_ta", "_taN", "_taS & ", " & IF ( _aA <= 1, \" mês\", \" meses\" )", "ISBLANK ( _a )"),
      "VAR _chave = " + D.esc("_obra"),
      "VAR _cls = " + CLS_PRAZO,
      "-- 3 · Geometria",
      "VAR _larg = ROUND ( MIN ( _e, 1 ) * 282, 0 ) -- geometria",
      "VAR _xPrev = 140 + ROUND ( MIN ( _p, 1 ) * 282, 0 ) - 1 -- geometria",
      "VAR _atraso = ( _pos - 1 ) * 60 -- geometria",
      "-- 4 · Marcação",
      "RETURN",
      "    IF (",
      "        NOT ISBLANK ( _e ),",
      "        \"<div class='u av\" & IF ( _foco = 1, \" foco\", \"\" ) & \"' data-rr='\" & _chave & \"'>\"",
      "            & \"<b class='nm'>\" & _chave & \"</b><i class='tr a-gx' style='animation-delay:\" & _atraso & \"ms'></i>\"",
      "            & \"<i class='fl s\" & _cls & \"' style='width:\" & _larg & \"px' data-rk='\" & _chave & \"' data-rd='\"",
      "            & _atraso & \"'></i>\"",
      "            & IF ( NOT ISBLANK ( _p ), \"<i class='pv a-pop' style='left:\" & _xPrev & \"px;animation-delay:\" & ( _atraso + 600 ) & \"ms'></i>\" )",
      "            & \"<span class='tx'>\" & " + C.marca("_teTxt") + " & \" × \" & IF ( ISBLANK ( _p ), \"sem previsto\", " + C.marca("_tpTxt") + " ) & \"</span>\"",
      "            & IF (",
      "                ISBLANK ( _a ),",
      "                \"<span class='sp'>sem curva prevista</span>\",",
      "                \"<div class='dr'><i class='mk a-pop mk\" & _cls & \"' style='animation-delay:\" & ( _atraso + 700 ) & \"ms'></i>\"",
      "                    & \"<b class='dv\" & IF ( _cls = \"2\", \" ng\", \"\" ) & \"'>\" & _taOd & \"</b></div>\"",
      "            )",
      "        & \"</div>\" & [Comum · JS contador] & [Comum · JS corrida]",
      "    )",
  ))

# ======================================================================================================== Linha do tempo
LINHA = rf"{TELA}\Linha do tempo das obras"
# painel v2 (Figma 387:4421, 900 × 357): cabeçalho HTML em y 0–54; gráfico de y 68 (visual da grade 900 × 289): anos em
# y 2, grade de y 22 a 262, selo do mês de referência em y 0, legenda da faixa em y 266; linhas das obras de 23 px a
# partir de y 96 do painel (visual 900 × 230), nomes Barlow 16 alinhados em x 92, barras de 12 px. Escala: jan do
# primeiro ano da grade em x 152,24 e jan do ano depois do último término em x 875,84 (12,06 px por mês em 2025–2029).
LX0, LX1 = 152.24, 875.84        # jan do primeiro ano da grade e jan do ano depois do último término
# F4 (retorno visual a4806f3: "usa só o topo do painel"): as linhas dividem a altura inteira do visual das obras
# (LT_ALT, paginas/t3.py) pela contagem de obras ([T3 · Linha do tempo · linhas]), em px inteiros (a soma dá LT_ALT),
# até LT_MAX por linha; nome, barra, traço, faixa e losango crescem na proporção da linha de antes (LT_BASE), com teto
# (nome 17 px: PONTA NEGRA ≈ 109 px cabe à direita de x 112, antes da barra mais antiga em x 122; barra 20 px).
LT_ALT, LT_BASE, LT_MAX = 230, 23, 46
HACH_TOL = DC.HACH.replace("%230B0B0C", "%233B3B3F")   # hachura grafite da faixa dos 180 dias


def escala_linha() -> list[str]:
    return [
        "VAR _y0 = YEAR ( _pi ) + IF ( MONTH ( _pi ) = 1, 0, 1 ) -- geometria",
        "VAR _y1 = YEAR ( _ut ) + 1 -- geometria",
        f"VAR _pxm = DIVIDE ( {LX1 - LX0:.2f}, ( _y1 - _y0 ) * 12 ) /* geometria */",
        "VAR _jan0 = DATE ( _y0, 1, 1 ) -- geometria",
    ]


CSS_LINHA_GRADE = (
    ".lg{position:fixed;inset:0}"
    f".lg .gl{{position:absolute;top:22px;width:1px;height:240px;background:{REGRA}}}"
    f".lg .gl.ref{{background:{PRETO}}}"
    f".lg .an{{position:absolute;top:2px;width:40px;text-align:center;font-size:13px;line-height:16px;color:{TERC}}}"
    f".lg .bd{{position:absolute;top:0;height:20px;padding:0 8px;transform:translateX(-50%);background:{PRETO};"
    "color:#FFFFFF;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:13px;line-height:20px;"
    "letter-spacing:1.04px;text-transform:uppercase;white-space:nowrap}"
    f".lg .le{{position:absolute;left:0;top:266px;display:flex;align-items:center;font-size:14px;line-height:19px;"
    f"color:{GRAFITE};white-space:nowrap}}"
    ".lg .le span{display:inline-flex;align-items:center;gap:6px;margin-left:12px}"
    f".lg .le .mk.mkx{{background:{GRAFITE}}}"
    # F3: a marca do término projetado (losango contornado) e a faixa dos 180 dias depois da entrega (hachura)
    f".lg .le .tp{{display:block;width:9px;height:9px;transform:rotate(45deg);background:#FFFFFF;border:1.5px solid {PRETO}}}"
    ".lg .le .tl{display:block;width:16px;height:12px;background-image:" + HACH_TOL + ";opacity:.55}"
)
css("T3 · Linha do tempo · CSS grade", LINHA, "CSS da grade da Linha do tempo (anos, mês de referência e legenda da faixa).",
    CSS_LINHA_GRADE)
m("T3 · Linha do tempo · HTML grade", LINHA,
  "Grade da Linha do tempo das obras (Figma 289:7417): anos do primeiro ao último da carteira (o último inclui o "
  "término projetado e os 180 dias de tolerância), a linha e o selo do mês de referência e, no pé, a legenda: a cor "
  "do executado pelos pontos do item prazo da nota (primeira e última faixa lidas do modelo), a marca do término "
  "projetado e a faixa dos 180 dias depois da entrega. Fica por baixo das linhas das obras.",
  linhas(
      "-- 1 · Leituras",
      "VAR _pi = [T3 · Linha do tempo · primeiro início]",
      "VAR _ut = [T3 · Linha do tempo · último término]",
      "VAR _ref = [Mês de referência]",
      "VAR _refCM = [Mês de referência · curto maiúsculo]",
      "-- 2 · Textos",
      faixas_item("prazo", "_fx"),
      "-- 3 · Geometria",
      escala_linha(),
      f"VAR _xRef = ROUND ( {LX0} + ( DATEDIFF ( _jan0, _ref, MONTH ) + 0.5 ) * _pxm, 0 ) -- geometria",
      "-- 4 · Marcação",
      "VAR _anos =",
      "    CONCATENATEX (",
      "        GENERATESERIES ( _y0, _y1 ),",
      f"        VAR _x = ROUND ( {LX0} + ( [Value] - _y0 ) * 12 * _pxm, 0 ) /* geometria */",
      "        RETURN",
      "            \"<i class='gl a-fd' style='left:\" & _x & \"px'></i>\"",
      "                & IF ( ABS ( _x - _xRef ) < 52, \"\", \"<span class='an a-fd' style='left:\" & ( _x - 20 ) & \"px'>\" & [Value] & \"</span>\" ),",
      "        \"\",",
      "        [Value], ASC",
      "    )",
      "RETURN",
      "    IF (",
      "        NOT ISBLANK ( _pi ),",
      "        \"<div class='u lg'>\" & _anos",
      "            & \"<i class='gl ref a-gy' style='left:\" & _xRef & \"px;animation-delay:300ms'></i>\"",
      "            & \"<span class='bd a-fd' style='left:\" & _xRef & \"px;animation-delay:500ms'>\" & _refCM & \"</span>\"",
      "            & \"<p class='le'>executado:<span><i class='mk mk0'></i>\" & " + C.marca("_fx1s") + " & \"</span><span><i class='mk mk1'></i>\"",
      "            & \"perde parte</span><span><i class='mk mk2'></i>\" & " + C.marca("_fxNs") + " & \"</span><span><i class='mk mkx'></i>sem curva\"",
      "            & \"</span><span><i class='tp'></i>término projetado</span><span><i class='tl'></i>tolerância de 180 \"",
      "            & \"dias</span></p>\"",
      "        & \"</div>\" & [Comum · JS contador]",
      "    )",
  ))

# F4: a altura da linha e o fator --k (em centésimos da linha de 23 px) vêm do style inline da medida; tudo centrado
# na altura da linha (translate, que não briga com o rotate do losango nem com o scale da entrada)
BARRA_LT = f"min(20px,max(8px,calc(12px * var(--k,100) / 100)))"
CSS_LINHA = (
    ".htmlViewerEntry{display:block!important;margin:0!important;padding:0!important}"
    f".lt{{position:relative;height:{LT_BASE}px;transition:background .15s}}"
    ".lt:hover,.htmlViewerEntry.hover .lt{background:rgba(233,224,207,.45)}"
    ".lt>*{top:50%;translate:0 -50%}"
    ".lt .nm{position:absolute;left:0;width:112px;text-align:right;font-family:'Barlow U','Segoe UI',sans-serif;"
    "font-weight:600;font-size:min(17px,max(13px,calc(16px * var(--k,100) / 100)));line-height:1.2;white-space:nowrap}"
    f".lt.ai .nm{{color:{TERC}}}"
    f".lt .tk{{position:absolute;height:{BARRA_LT};background:{TRILHA}}}"
    f".lt.ai .tk{{background:transparent;border:1px dashed {GRAFITE};box-sizing:border-box}}"
    f".lt .fl{{position:absolute;height:{BARRA_LT}}}"
    + css_faixa(".lt .fl") +
    f".lt .pv{{position:absolute;width:2px;height:calc({BARRA_LT} + 6px);background:{PRETO}}}"
    # F3: faixa dos 180 dias depois da entrega (por baixo da barra) e o losango do término projetado na cor de onde cai
    f".lt .tl{{position:absolute;height:calc({BARRA_LT} + 4px);background-image:" + HACH_TOL + ";opacity:.55}"
    ".lt .tp{position:absolute;width:min(13px,max(7px,calc(9px * var(--k,100) / 100)));aspect-ratio:1;"
    f"transform:rotate(45deg);border:1.5px solid {PRETO}}}"
    f".lt .tp.t0{{background:{SALVIA}}}.lt .tp.t1{{background:{DC.OCRE}}}.lt .tp.t2{{background:{VERM}}}"
)
css("T3 · Linha do tempo · CSS", LINHA, "CSS das linhas da Linha do tempo das obras (uma entrada por obra).", CSS_LINHA)
m("T3 · Linha do tempo · HTML obra", LINHA,
  "Uma linha por obra em andamento e a iniciar (granularidade dObra[Obra], ordem T3 · Linha do tempo · posição): "
  "nome, a faixa hachurada dos 180 dias depois da entrega contratual (por baixo), barra do início ao término "
  "previsto, preenchimento do executado (cor pelos pontos do item prazo da nota: cheio sálvia, perde parte ocre, zera "
  "vermelho; grafite sem curva prevista), traço do previsto (só quando a aba traz o previsto) e o losango do término "
  "projetado na cor de onde cai (até a entrega sálvia, nos 180 dias ocre, depois vermelho); as a iniciar só com o "
  "contorno tracejado. A barra corre do início ao término, o executado corre em seguida e o losango aparece no fim.",
  linhas(
      "-- 1 · Leituras",
      "VAR _pos = [T3 · Linha do tempo · posição]",
      "VAR _sit = [T3 · Obra · situação]",
      "VAR _obra = [Obra · nome]",
      "VAR _ini = [Obra · início]",
      "VAR _fim = [Obra · término previsto]",
      "VAR _pi = [T3 · Linha do tempo · primeiro início]",
      "VAR _ut = [T3 · Linha do tempo · último término]",
      "VAR _e = [Físico · executado acumulado · ref]",
      "VAR _p = [Físico · previsto acumulado · ref]",
      "VAR _pt = [Nota · pontos prazo · ref]",
      "VAR _ps = [Nota · possíveis · prazo · ref]",
      "VAR _proj = [Prazo · término projetado · ref]",
      "VAR _ent = [Prazo · entrega contratual]",
      "VAR _sitT = [T3 · Término · situação · ref]",
      "VAR _nAnd = [Obras com análise · ref]",
      "VAR _nL = [T3 · Linha do tempo · linhas]",
      "-- 2 · Textos",
      "VAR _chave = " + D.esc("_obra"),
      'VAR _aIniciar = _sit = "A iniciar"',
      "VAR _clsFl = \"s\" & " + CLS_PRAZO,
      "-- 3 · Geometria",
      escala_linha(),
      f"VAR _x = ROUND ( {LX0} + DATEDIFF ( _jan0, _ini, MONTH ) * _pxm, 0 ) -- geometria",
      "VAR _w = ROUND ( ( DATEDIFF ( _ini, _fim, MONTH ) + 1 ) * _pxm, 0 ) -- geometria",
      "VAR _wf = ROUND ( _w * MIN ( _e, 1 ), 0 ) -- geometria",
      "VAR _xp = _x + ROUND ( _w * MIN ( _p, 1 ), 0 ) - 1 -- geometria",
      f"VAR _xEnt = ROUND ( {LX0} + ( DATEDIFF ( _jan0, _ent, MONTH ) + 1 ) * _pxm, 0 ) -- geometria",
      "VAR _wTol = ROUND ( 6 * _pxm, 0 ) -- geometria",
      f"VAR _xProj = ROUND ( {LX0} + ( DATEDIFF ( _jan0, _proj, MONTH ) + 1 ) * _pxm, 0 ) -- geometria",
      "VAR _ordem = IF ( _pos >= 100, _nAnd + _pos - 99, _pos ) -- geometria",
      "VAR _atraso = ( _ordem - 1 ) * 60 -- geometria",
      "/* F4: a linha k ocupa de INT((k−1)·A/n) a INT(k·A/n), até o teto por linha; --k em centésimos da linha de antes */",
      f"VAR _hU = MIN ( {LT_MAX}, DIVIDE ( {LT_ALT}, MAX ( 1, _nL ) ) ) -- geometria",
      "VAR _h = INT ( _ordem * _hU ) - INT ( ( _ordem - 1 ) * _hU ) -- geometria",
      f"VAR _k = ROUND ( _hU / {LT_BASE} * 100, 0 ) -- geometria",
      "-- 4 · Marcação",
      "RETURN",
      "    IF (",
      "        NOT ISBLANK ( _pos ) && NOT ISBLANK ( _ini ) && NOT ISBLANK ( _fim ),",
      "        \"<div class='u lt\" & IF ( _aIniciar, \" ai\", \"\" ) & \"' style='height:\" & _h & \"px;--k:\" & _k & \"'>\"",
      "            & \"<b class='nm'>\" & _chave & \"</b>\"",
      "            & IF ( ISBLANK ( _ent ), \"\", \"<i class='tl a-gx' style='left:\" & _xEnt & \"px;width:\" & _wTol",
      "                & \"px;animation-delay:\" & ( _atraso + 300 ) & \"ms'></i>\" )",
      "            & \"<i class='tk' style='left:\" & _x & \"px;width:\" & _w & \"px' data-rk='t|\" & _chave & \"' data-rd='\"",
      "            & _atraso & \"'></i>\"",
      "            & IF (",
      "                NOT _aIniciar && NOT ISBLANK ( _e ),",
      "                \"<i class='fl \" & _clsFl & \"' style='left:\" & _x & \"px;width:\" & _wf & \"px' data-rk='f|\" & _chave",
      "                    & \"' data-rd='\" & ( _atraso + 500 ) & \"'></i>\"",
      "                    & IF ( NOT ISBLANK ( _p ), \"<i class='pv a-pop' style='left:\" & _xp & \"px;animation-delay:\" & ( _atraso + 1000 ) "
      "& \"ms'></i>\" )",
      "            )",
      "            & IF ( _aIniciar || ISBLANK ( _proj ), \"\", \"<i class='tp a-pop t\" & _sitT & \"' style='left:\" & ( _xProj - 6 ) "
      "& \"px;animation-delay:\" & ( _atraso + 1200 ) & \"ms'></i>\" )",
      "        & \"</div>\" & [Comum · JS corrida]",
      "    )",
  ))

if __name__ == "__main__":
    sys.exit(gravar(MEDIDAS, RAIZ / "dax" / "T3", GERADO))

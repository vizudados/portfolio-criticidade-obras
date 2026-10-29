#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""desenho_t1 — medidas de DESENHO da Tela 01 · Visão geral (pbi/dax/T1/**). Só leem contas (base/** e
T1/**/Contas); formatam, escapam e posicionam.

Geometria e estilos do Figma FjBWDk5odF9HaZ2pwhGosl, Tela 01 (281:720): cartões 288:7235…7239, Obras por
criticidade 288:7240, O que pesa 288:7244, Como os meses evoluíram 288:7248, síntese 271:1041. Versos da seção
Interações · Tela 01 (291:1094…1138; docs/06-interacoes-spec.md §2).

F3 (28/10/2026, docs/08): a régua é a Nota da obra, de 0 a 10, com trava e quatro estados (crítico · atenção ·
estável · pendente). Os helpers de status e pontos vêm do desenho_comum (DC);
nenhum limite da nota é escrito aqui: faixas, máximos e limites saem das medidas Nota · ….

    python -X utf8 pbi/scripts/desenho_t1.py
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import contador as C  # noqa: E402
import desenho_comum as DC  # noqa: E402
import desenho_projeto as D  # noqa: E402
from contas_lib_projeto import Medida, gravar  # noqa: E402
from desenho_comum import dax_lit  # noqa: E402

from contas_base import NOTA_DIMENSOES  # noqa: E402

RAIZ = AQUI.parent
GERADO = "pbi/scripts/desenho_t1.py"
# siglas das dimensões nos quadradinhos da lista de obras (a ordem e os nomes vêm do dicionário NOTA)
SIGLAS = {"Custo": "CUS", "Prazo": "PRA", "Caixa": "CAI", "Qualidade": "QUA", "Segurança": "SEG",
          "Suprimentos": "SUP", "Gestão": "GES"}
DIMENSOES = [(d, SIGLAS[d]) for d in NOTA_DIMENSOES]
MEDIDAS: list[Medida] = []
MENOS = D.MENOS
PTS = DC.FMT_PTS


def m(nome, pasta, descricao, dax, passos=C.PASSOS):
    """Medida de desenho; os valores marcados com C.marca() viram odômetro no fim (F4, contador.envolver_marcas;
    passos=C.PASSOS_DENSO nas tabelas densas, C8)."""
    MEDIDAS.append(Medida(nome, pasta, "texto", descricao, C.envolver_marcas(dax, passos)))


def mk(expr: str) -> str:
    """DAX: o número {expr} marcado para o contador (F4); só em conteúdo, nunca em atributo."""
    return C.marca(expr)


def linhas(*ls) -> str:
    return "\n".join(l for grupo in ls for l in (grupo if isinstance(grupo, list) else [grupo]))


def fmt_pts(v: str) -> str:
    """DAX: pontos da nota em texto ("7,75" · "4,0" · "0,5")."""
    return f'FORMAT ( {v}, "{PTS}", "pt-BR" )'


def em_frase(v: str) -> str:
    """DAX: 'o orçamento' → 'no orçamento', 'a média PPC' → 'na média PPC', 'os termômetros' → 'nos termômetros'."""
    return (f'SWITCH ( TRUE (), LEFT ( {v}, 3 ) = "os ", "nos " & MID ( {v}, 4, 99 ), LEFT ( {v}, 3 ) = "as ", '
            f'"nas " & MID ( {v}, 4, 99 ), LEFT ( {v}, 2 ) = "o ", "no " & MID ( {v}, 3, 99 ), LEFT ( {v}, 2 ) = "a ", '
            f'"na " & MID ( {v}, 3, 99 ), "em " & {v} )')


def html_lim(v: str) -> str:
    """DAX: texto de faixa com < e > escapados para HTML ("< 6" → "&lt; 6")."""
    return f'SUBSTITUTE ( SUBSTITUTE ( {v}, "<", "&lt;" ), ">", "&gt;" )'


# ======================================================================================================== cartões
# Fase 2 da régua antiga: a régua antiga por indicador (limites da Vizu escritos à mão) saiu de todos os versos. Ficam só as
# réguas da nota, lidas das medidas: obras (status pela nota), físico (limite do físico-financeiro) e desembolso (faixas
# do fluxo de caixa); resultado e sem estoque ficam sem régua (geometria comum: regra em até 3 linhas, origem em y 106).
def regua(itens: list[tuple[str, str]]) -> str:
    """HTML estático da régua do verso: [(classe da marca, texto)]."""
    return "".join(f"<i class='mk {c}'></i><span>{t}</span>" for c, t in itens)


def ng_span(txt: str, cond: str) -> str:
    """DAX: o texto {txt} dentro de <span class='ng'> quando {cond}."""
    return f"IF ( {cond}, \"<span class='ng'>\" & {txt} & \"</span>\", {txt} )"


def cls_ng(cond: str | None) -> str:
    """Trecho para dentro de um class='…' literal: ' ng' quando {cond} (DAX)."""
    return f"\" & IF ( {cond}, \" ng\", \"\" ) & \"" if cond else ""


def cartao(chave: str, titulo_eb: str, leituras: list[tuple[str, str]], textos: list[str], hero: str, lado: str | None,
           ctx: str, regra: str, origem: str, regua_itens: list | str | None, escuro: bool = False, desc: str = "",
           anima: list[str] | None = None, hero_ng: str | None = None, lado_ng: str | None = None) -> None:
    """Cartão com flip. `hero`, `lado` e `ctx` são expressões DAX de texto já formatado (VARs de `textos`). `anima` =
    linhas D.od_* que definem os {p}Od usados em `hero`/`lado` (contador dos números). `hero_ng`/`lado_ng`: condição
    DAX do negativo em vermelho (todo negativo, menos desvio de desembolso; limite de régua nunca). `regua_itens`: lista
    estática [(marca, texto)] ou uma expressão DAX que já devolve o HTML da régua (limites lidos das medidas). Verso v2
    (geometria comum, Figma 07/10/2026): "DE ONDE VEM" em y 82 com régua e 106 sem."""
    topo_ond = 82 if regua_itens else 106
    verso = ("\"<div class='lado verso sobre-creme'>\"\n"
             "            & \"<p class='ab vs v1'>COMO É CALCULADO</p>\"\n"
             f"            & \"<p class='regra'>\" & {regra} & \"</p>\"\n"
             f"            & \"<div class='ond' style='top:{topo_ond}px'><span class='vs'>DE ONDE VEM</span>"
             f"<span>{origem}</span></div>\"\n")
    if isinstance(regua_itens, str):
        verso += f"            & \"<div class='regua'>\" & {regua_itens} & \"</div>\"\n"
    elif regua_itens:
        verso += f"            & \"<div class='regua'>{regua(regua_itens)}</div>\"\n"
    verso += "        & \"</div>\""
    lado_html = f" & \"<span class='b5 lado2{cls_ng(lado_ng)}'>\" & {lado} & \"</span>\"" if lado else ""
    conta = bool(anima) or any(C.MARCA_ABRE in t for t in textos)
    dax = linhas(
        "-- 1 · Leituras", [f"VAR {v} = [{x}]" for v, x in leituras],
        "-- 2 · Textos", textos,
        [D.od_tabela()] + anima if anima else [],
        "-- 4 · Marcação",
        "RETURN",
        f"    \"<div class='u kc{' escuro' if escuro else ''}' tabindex='0'>\"",
        "        & \"<div class='lado frente'>\"",
        f"            & \"<p class='ab vs eb'>{titulo_eb}</p>\"",
        f"            & \"<div class='linha1'><span class='b6 hero{cls_ng(hero_ng)}'>\" & {hero} & \"</span>\"{lado_html} & \"</div>\"",
        f"            & \"<p class='ctx'>\" & {ctx} & \"</p>\"",
        "        & \"</div>\"",
        "        & " + verso,
        "    & \"</div>\"" + (" & [Comum · JS contador]" if conta else ""),
    )
    m(f"T1 · Cartão {chave} · HTML", rf"T1 Visão geral\Cartões",
      desc or f"Cartão '{titulo_eb.lower()}' (frente e verso). Só lê contas · ref.", dax)


# contagem do cartão obras, na ordem crítico → pendente, só dos estados com obra: "1 crítica · 2 atenção · 3 pendentes"
# (sem marcas, como na v2). Com os quatro estados as palavras não cabem em 262 px: vão as marcas com os números (a régua
# do verso e a legenda da lista dizem o que cada marca é)
CTX_OBRAS = [
    'VAR _c = _crit + 0', 'VAR _a = _aten + 0', 'VAR _e = _est + 0', 'VAR _p = _pend + 0',
    'VAR _quatro = _c > 0 && _a > 0 && _e > 0 && _p > 0',
    'VAR _wC = IF ( _c > 0, ' + mk("_c") + ' & IF ( _c = 1, " crítica", " críticas" ) )',
    'VAR _wA = IF ( _a > 0, ' + mk("_a") + ' & " atenção" )',
    'VAR _wE = IF ( _e > 0, ' + mk("_e") + ' & IF ( _e = 1, " estável", " estáveis" ) )',
    'VAR _wP = IF ( _p > 0, ' + mk("_p") + ' & IF ( _p = 1, " pendente", " pendentes" ) )',
    'VAR _palavras = _wC & IF ( _wC <> "" && _wA & _wE & _wP <> "", " · " ) & _wA & IF ( _wA <> "" && _wE & _wP <> "", '
    '" · " ) & _wE & IF ( _wE <> "" && _wP <> "", " · " ) & _wP',
    # F4: as marcas entram crescendo em cascata, depois do número grande
    """VAR _marcas = "<i class='mk mk2 a-pop' style='animation-delay:300ms'></i>" & """ + mk("_c")
    + """ & "<i class='mk mk1 a-pop' style='margin-left:14px;animation-delay:350ms'></i>" & """ + mk("_a")
    + """ & "<i class='mk mk0 a-pop' style='margin-left:14px;animation-delay:400ms'></i>" & """ + mk("_e")
    + """ & "<i class='mk mkm a-pop' style='margin-left:14px;animation-delay:450ms'></i>" & """ + mk("_p"),
    'VAR _txtCtx = SWITCH ( TRUE (), _c + _a + _e + _p = 0, "nenhuma obra no mês", _quatro, _marcas, _palavras )',
    'VAR _txtMax = FORMAT ( _max, "0", "pt-BR" )',
    'VAR _txtTrvC = FORMAT ( _trvC, "0.00", "pt-BR" )',
    'VAR _txtTrvP = FORMAT ( _trvP, "0", "pt-BR" )',
    # o verso tem duas linhas de 262 px: a trava vai com os sinais (&lt; e &gt; já escapados para o HTML)
    'VAR _txtRegra = "De 0 a " & _txtMax & ". IDC &lt; " & _txtTrvC & " ou atraso &gt; " & _txtTrvP '
    '& " meses: crítica. Sem item: pendente."',
    'VAR _htmlRegua = "<i class=\'mk mk2\'></i><span>" & ' + html_lim("_fxC") + ' & "</span>"'
    ' & "<i class=\'mk mk1\'></i><span>" & ' + html_lim("_fxA") + ' & "</span>"'
    ' & "<i class=\'mk mk0\'></i><span>" & ' + html_lim("_fxE") + ' & "</span>"'
    ' & "<i class=\'mk mkm\'></i><span>pendente</span>"',
]

cartao(
    "obras", "Obras em andamento",
    [("_n", "Obras com análise · ref"), ("_orc", "Orçamento · ref"), ("_crit", "Nota · carteira · obras críticas · ref"),
     ("_aten", "Nota · carteira · obras em atenção · ref"), ("_est", "Nota · carteira · obras estáveis · ref"),
     ("_pend", "Nota · carteira · obras pendentes · ref"), ("_max", "Nota · nota · máximo"),
     ("_fxC", "Nota · status · faixa crítico"), ("_fxA", "Nota · status · faixa atenção"),
     ("_fxE", "Nota · status · faixa estável"), ("_trvC", "Nota · limite custo · trava"),
     ("_trvP", "Nota · limite prazo · trava")],
    D.inteiro("_n", "_tn") + D.rs("_orc", "_to") + CTX_OBRAS,
    "_tnOd", "_toOd", "_txtCtx", "_txtRegra", "Análise Crítica + base", "_htmlRegua",
    desc="Cartão 'obras em andamento' (frente e verso): obras com aba no mês, orçamento somado e as obras por status da "
         "nota (crítico, atenção, estável, pendente). O verso explica a Nota da obra, a trava e a régua dos status, "
         "lidas das medidas Nota · status · faixa … e Nota · limite … · trava. Só lê contas · ref.",
    anima=D.od_num("_n", "_tn") + D.od_rs("_orc", "_to"))

# F3 (docs/08 §5): um cartão por dimensão. O escuro (2º, a resposta) é o custo; os nomes dos visuais da página ficam
# (T1_Kpi_Resultado, …) porque o papel de parede e o tour falam de posição, não de nome.
def num2(v: str, p: str) -> list[str]:
    """{p}N / {p}Txt = "0,97" (duas casas, sempre; o IDC 1 é "1,00")."""
    return [f'VAR {p}N = FORMAT ( {v}, "0.00", "pt-BR" )', f'VAR {p}Txt = IF ( ISBLANK ( {v} ), "—", {p}N )']


def num1(v: str, p: str) -> list[str]:
    """{p}N / {p}Txt = "1,4" (uma casa, sempre)."""
    return [f'VAR {p}N = FORMAT ( {v}, "0.0", "pt-BR" )', f'VAR {p}Txt = IF ( ISBLANK ( {v} ), "—", {p}N )']


def meses(v: str, conta: bool = False) -> str:
    """DAX: "0,5 mês" · "3 meses" (sem casa quando inteiro); conta=True marca o número para o contador (F4)."""
    n = f'FORMAT ( {v}, IF ( {v} = INT ( {v} ), "0", "0.0" ), "pt-BR" )'
    return (mk(n) if conta else n) + f' & IF ( {v} <= 1, " mês", " meses" )'


cartao(
    "custo", "Custo · IDC da carteira",
    [("_idc", "IDC · ref"), ("_resA", "Resultado aplicado · ref"), ("_nAbx", "T1 · Custo · obras com IDC abaixo de 1 · ref"),
     ("_n", "Obras com análise · ref"), ("_cheio", "Nota · limite custo · ponto cheio"),
     ("_trv", "Nota · limite custo · trava")],
    num2("_idc", "_ti") + D.rs("_resA", "_tr", mais=True) + [
        'VAR _txtCtx = SWITCH ( TRUE (), _n = 0, "nenhuma obra no mês", _nAbx = 0, '
        'IF ( _n = 1, "a obra agrega o que gasta", "todas agregam o que gastam" ), '
        + mk("_nAbx") + ' & IF ( _nAbx = 1, " obra abaixo de ", " obras abaixo de " ) & '
        + mk('FORMAT ( _cheio, "0.00", "pt-BR" )') + ' )',
        'VAR _txtRegra = "Valor agregado ÷ custo aplicado (com a dívida). Ao lado, a diferença em R$."',
        'VAR _tCheio = FORMAT ( _cheio, "0.00", "pt-BR" )',
        'VAR _tTrv = FORMAT ( _trv, "0.00", "pt-BR" )',
        """VAR _htmlRegua = "<i class='mk mk0'></i><span>≥ " & _tCheio & "</span>"
            & "<i class='mk mk1'></i><span>" & _tTrv & " a " & _tCheio & "</span>"
            & "<i class='mk mk2'></i><span>&lt; " & _tTrv & "</span>" """],
    "_tiOd", "_trOd", "_txtCtx", "_txtRegra", "Análise Crítica · item custo", "_htmlRegua", escuro=True,
    desc="Cartão de custo (o escuro, a resposta): IDC da carteira (valor agregado ÷ custo aplicado, soma ÷ soma) e, ao "
         "lado, o resultado aplicado em R$; quantas obras estão abaixo de 1,00. Verso com a régua do item custo (ponto "
         "cheio e trava, lidos das medidas Nota · limite custo · …). Só lê contas · ref.",
    anima=D.od_num("_idc", "_ti") + D.od_rs("_resA", "_tr"),
    hero_ng="ROUND ( _idc, 2 ) < 1", lado_ng='_resA < 0 && _trTxt <> "—"')

cartao(
    "prazo", "Prazo · atraso médio",
    [("_atr", "Prazo · atraso médio (meses) · ref"), ("_oMax", "T1 · Prazo · obra de maior atraso · ref"),
     ("_vMax", "T1 · Prazo · maior atraso · ref"), ("_lim", "Nota · limite prazo · ponto cheio"),
     ("_trv", "Nota · limite prazo · trava")],
    num1("_atr", "_ta") + [
        'VAR _txtLado = IF ( ISBLANK ( _atr ), "", IF ( ROUND ( _atr, 1 ) <= 1, "mês", "meses" ) )',
        'VAR _txtCtx = IF ( _oMax = "", "nenhuma obra atrasada", "maior: " & ' + D.esc("_oMax") + ' & ", " & '
        + meses("ROUND ( _vMax, 1 )", conta=True) + " )",
        'VAR _txtRegra = "Atraso das obras pelo cronograma, em meses, ponderado pelo orçamento."',
        "VAR _txtLim = " + meses("_lim"),
        "VAR _txtTrv = " + meses("_trv"),
        """VAR _htmlRegua = "<i class='mk mk0'></i><span>até " & _txtLim & "</span>"
            & "<i class='mk mk2'></i><span>&gt; " & _txtTrv & ": crítica</span>" """],
    "_taOd", "_txtLado", "_txtCtx", "_txtRegra", "Planilha e cronograma", "_htmlRegua",
    desc="Cartão de prazo: atraso médio da carteira em meses (cronograma agregado, ponderado pelo orçamento) e a obra "
         "de maior atraso. Verso com a régua do item prazo (ponto cheio e trava, das medidas Nota · limite prazo · …). "
         "Só lê contas · ref.",
    anima=D.od_num("_atr", "_ta"))

cartao(
    "caixa", "Caixa · desembolso do mês",
    [("_des", "Desembolso · realizado no mês · ref"), ("_prev", "Desembolso · previsto no mês · ref"),
     ("_desv", "Desembolso · desvio no mês · ref"), ("_nFora", "T1 · Caixa · obras fora da faixa cheia · ref"),
     ("_limInt", "Nota · limite caixa · ponto inteiro"), ("_limMeio", "Nota · limite caixa · meio ponto")],
    D.rs("_des", "_td") + D.rs("_prev", "_tp") + D.pct("_desv", "_tv", casas=0, mais=True) + [
        'VAR _txtCtx = ' + mk("_tpTxt") + ' & " previsto" & IF ( _nFora > 0, " · " & ' + mk("_nFora")
        + ' & " fora de " & ' + mk('FORMAT ( _limInt * 100, "0", "pt-BR" )') + ' & "%", "" )',
        'VAR _txtRegra = "Desvio = desembolsado ÷ previsto − 1. Na nota conta para mais e para menos."',
        # item caixa (desvio em módulo): ponto inteiro abaixo do 1º limite, meio ponto até o 2º
        'VAR _txtInt = FORMAT ( _limInt * 100, "0", "pt-BR" ) & "%"',
        'VAR _txtMeio = FORMAT ( _limMeio * 100, "0", "pt-BR" ) & "%"',
        """VAR _htmlRegua = "<i class='mk mk2'></i><span>|desvio| &gt; " & _txtMeio & "</span>"
            & "<i class='mk mk1'></i><span>≤ " & _txtMeio & "</span>"
            & "<i class='mk mk0'></i><span>&lt; " & _txtInt & "</span>" """],
    "_tdOd", "_tvOd", "_txtCtx", "_txtRegra", "Previsto e desembolsado", "_htmlRegua",
    desc="Cartão de caixa: desembolso do mês somado, desvio sobre o previsto e quantas obras saíram da faixa cheia do "
         "item caixa (para mais ou para menos). Verso com a régua do item (Nota · limite caixa · …). Só lê contas · ref.",
    anima=D.od_rs("_des", "_td") + D.od_pct("_desv", "_tv"))

cartao(
    "canteiro", "Canteiro · acidentes",
    [("_tf", "Canteiro · taxa de frequência (12 meses) · ref"), ("_insp", "Canteiro · aprovação na 1.ª inspeção · ref"),
     ("_nr", "Canteiro · conformidade NR-18 · ref"), ("_setor", "Nota · limite acidentes · setor")],
    num1("_tf", "_tt") + D.pct("_insp", "_tin", casas=0) + D.pct("_nr", "_tnr", casas=0) + [
        'VAR _txtCtx = "1.ª inspeção " & ' + mk("_tinTxt") + ' & " · NR-18 " & ' + mk("_tnrTxt"),
        'VAR _txtRegra = "Acidentes com afastamento por milhão de horas, em 12 meses (NBR 14280)."',
        'VAR _tSetor = FORMAT ( _setor, "0.0", "pt-BR" )',
        """VAR _htmlRegua = "<i class='mk mk0'></i><span>TF = 0</span>"
            & "<i class='mk mk1'></i><span>até " & _tSetor & " (setor)</span>"
            & "<i class='mk mk2'></i><span>&gt; " & _tSetor & "</span>" """],
    "_ttOd", '"TF"', "_txtCtx", "_txtRegra", "Base complementar", "_htmlRegua",
    desc="Cartão do canteiro: taxa de frequência de acidentes com afastamento nos 12 meses (NBR 14280) e, no contexto, a "
         "aprovação na 1.ª inspeção e a conformidade NR-18 do mês. Verso com a régua do item acidentes (média do setor, "
         "Nota · limite acidentes · setor). Só lê contas · ref.",
    anima=D.od_num("_tf", "_tt"))


# ======================================================================================================== Obras pela nota
OBRAS = r"T1 Visão geral\Obras pela nota"
# v2 (Figma Tela 01 · v2 387:4824, painel 387:3719; t01.md §2): linhas de 76 (F3; eram 88) a partir de y 96 do painel (o cabeçalho de
# colunas, a legenda e as regras estão no papel de parede v2). Colunas: posição 14 · obra 48 · status 356 (chip
# centrado na linha) · trilho da nota 500 (200 × 10, de 0 ao máximo da nota, marcas nos limites de atenção e de estável)
# · nota à direita em 756 · itens que mais perdem 784.
# Pendente (régua antiga, 13/10/2026): a barra cinza vai até os pontos obtidos e o contorno tracejado até os possíveis (o que já
# dá para calcular); à direita, "4,5" e "de 6,0" embaixo.
TRILHO = 200
DM_X, DM_Q, DM_VAO = 784, 24, 6     # quadradinhos das dimensões: x, lado e vão (7 × 24 + 6 × 6 = 204, até 988)
CSS_OBRAS = (
    ".htmlViewerEntry{display:block!important;margin:0!important;padding:0!important}"
    # F3: sete obras nos 535 px da lista: linhas de 76 (eram 88, com seis obras)
    ".ln{position:relative;height:76px;border-bottom:1px solid #E1E1E1;transition:background .15s}"
    ".ln.crit{background:#F7E3E3}"
    ".ln:not(.crit):hover,.htmlViewerEntry.hover .ln:not(.crit){background:#F7F4EE}"
    ".ln .ix{left:14px;top:16px;color:#6B6B70}"
    ".ln .nm{position:absolute;left:48px;top:10px;display:flex;align-items:baseline;gap:8px;white-space:nowrap}"
    ".ln .nm b{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:21px;line-height:26px}"
    ".ln .nm em{font-style:normal;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:12px;"
    "line-height:15px;letter-spacing:1.2px;color:#6B6B70}"
    ".ln .nm .selo{margin-left:3px}"
    ".ln .sub{left:48px;top:40px;font-size:14px;line-height:19px;color:#3B3B3F}"
    ".ln .chips{position:absolute;left:356px;top:50%;transform:translateY(-50%);display:flex;flex-direction:column;"
    "gap:6px}"
    f".ln .cota{{position:absolute;left:500px;top:33px;width:{TRILHO}px;height:10px;background:#EFEFEF}}"
    ".ln .cota i{position:absolute;left:0;top:0;bottom:0}"
    ".ln .cota i.s2{background:#C43737}.ln .cota i.s1{background:#C9821F}.ln .cota i.s0{background:#A9CDB9}"
    # pendente: obtidos em cinza e o que já dá para calcular num contorno tracejado grafite
    ".ln .cota i.sm{background:#CFCCC6}"
    ".ln .cota u{position:absolute;left:0;top:-2px;height:14px;border:1px dashed #3B3B3F;box-sizing:border-box}"
    ".ln .cota b{position:absolute;top:-4px;width:1px;height:18px;background:#6B6B70;opacity:.55}"
    ".ln .pt{left:690px;top:28px;width:66px;text-align:right;font-size:16px;line-height:20px}"
    ".ln .pt.pd{top:18px}"
    ".ln .de{left:690px;top:40px;width:66px;text-align:right;font-size:14px;line-height:19px;color:#3B3B3F}"
    # F3 (docs/08 §5): sete quadradinhos, um por dimensão, na ordem da régua; o preenchimento sobe com a fração dos
    # pontos obtidos (cheio sálvia, parcial ocre, zero vazio com contorno vermelho, sem dado tracejado); a sigla embaixo
    f".ln .dm{{position:absolute;left:{DM_X}px;top:16px;display:flex;gap:{DM_VAO}px}}"
    f".ln .dm span{{position:relative;display:block;width:{DM_Q}px}}"
    f".ln .dm i{{position:relative;display:block;width:{DM_Q}px;height:{DM_Q}px;box-sizing:border-box;"
    "background:#F2F0EB;border:1px solid #CFCCC6;overflow:hidden}"
    ".ln .dm i u{position:absolute;left:0;right:0;bottom:0}"
    ".ln .dm .q0 u{background:#A9CDB9}.ln .dm .q1 u{background:#C9821F}"
    ".ln .dm .q2{background:#FFFFFF;border-color:#C43737}"
    ".ln .dm .qf{background:#FFFFFF;border:1px dashed #3B3B3F}"
    ".ln .dm em{display:block;margin-top:5px;text-align:center;font-style:normal;font-family:'Barlow U','Segoe UI',"
    "sans-serif;font-weight:600;font-size:10px;line-height:12px;letter-spacing:.6px;color:#6B6B70}"
    ".ln .dm em.z{color:#C43737}"
)
m("T1 · Obras · CSS lista", OBRAS, "CSS da lista de obras pela Nota da obra (uma entrada por obra).",
  "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(CSS_OBRAS))

CSS_OBRAS_CAB = (
    ".oc{position:fixed;inset:0}"
    ".oc .sub{left:0;top:0;font-size:15px;line-height:20px;color:#3B3B3F}"
)
m("T1 · Obras · CSS cabeçalho", OBRAS, "CSS do subtítulo da lista de obras.",
  "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(CSS_OBRAS_CAB))
m("T1 · Obras · HTML cabeçalho", OBRAS,
  "Subtítulo da lista de obras (mês de referência · Nota da obra, de 0 ao máximo). A legenda dos status e o cabeçalho "
  "das colunas são fixos e ficam no papel de parede v2.",
  linhas("-- 1 · Leituras", "VAR _mes = [Mês de referência · curto]", "VAR _max = [Nota · nota · máximo]",
         "-- 2 · Textos", 'VAR _txt = _mes & " · Nota da obra, de 0 a " & ' + mk('FORMAT ( _max, "0", "pt-BR" )'),
         "-- 4 · Marcação", "RETURN",
         "    \"<div class='u oc'><p class='ab sub'>\" & _txt & \"</p></div>\" & [Comum · JS contador]"))


def dim_quadro(k: int, dim: str, sigla: str) -> list[str]:
    """VARs do k-ésimo quadradinho (dimensão `dim`): pontos e possíveis da obra no mês de referência, a classe pela
    fração e o HTML (preenchimento = fração × lado; vazio sem dado)."""
    p = f"_d{k}"
    f = f'dItemNota[Dimensao] = "{dim}"'
    return [
        f"VAR {p}Pts = CALCULATE ( [Nota · item · pontos · ref], {f} )",
        f"VAR {p}Poss = CALCULATE ( [Nota · item · possíveis · ref], {f} )",
        f"VAR {p}Max = CALCULATE ( [Nota · item · máximo], {f} )",
        f'VAR {p}Cls = SWITCH ( TRUE (), NOT ( {p}Poss >= {p}Max ), "qf", {p}Pts >= {p}Poss, "q0", {p}Pts = 0, "q2", "q1" )',
        f"VAR {p}H = IF ( {p}Poss > 0, ROUND ( DIVIDE ( {p}Pts, {p}Poss ) * {DM_Q - 2}, 0 ), 0 ) -- geometria",
        # F4: o quadradinho entra crescendo depois da barra da nota (cascata pela posição da obra e pela dimensão) e o
        # preenchimento sobe da base
        f"VAR {p}At = ( _pos - 1 ) * 60 + {300 + 40 * k} -- geometria",
        f'VAR {p}Html = "<span><i class=\'a-pop " & {p}Cls & "\' style=\'animation-delay:" & {p}At & "ms\'>'
        f'<u class=\'a-gy\' style=\'height:" & {p}H & "px;animation-delay:" & ( {p}At + 150 ) & "ms\'></u></i><em" '
        f'& IF ( {p}Cls = "q2", " class=\'z\'", "" ) & ">{sigla}</em></span>"',
    ]


m("T1 · Obras · HTML linha", OBRAS,
  "Uma linha por obra (granularidade dObra[Obra], ordem por T1 · Obras · posição): posição, nome, código, selo, "
  "orçamento · executado · IDC, chip do status da nota (ou pendente), barra da nota de 0 ao máximo na cor "
  "do status com as marcas dos limites de atenção e de estável (pendente: pontos obtidos em cinza e o que já dá para "
  "calcular em tracejado, 'X de Y'), e os sete quadradinhos das dimensões da nota, na ordem da régua, preenchidos pela "
  "fração dos pontos obtidos (cheio, parcial, zero, sem dado). Fundo vermelho-claro na obra crítica. Vazio para obra "
  "sem aba no mês.",
  linhas(
      "-- 1 · Leituras",
      "VAR _pos = [T1 · Obras · posição]",
      "VAR _obra = [Obra · nome]",
      "VAR _cod = [Obra · código]",
      "VAR _selo = [Obra · selo]",
      "VAR _orc = [Orçamento · ref]",
      "VAR _exec = [Físico · executado acumulado · ref]",
      "VAR _idc = [IDC · ref]",
      "VAR _st = [Nota · status · ranking · ref]",
      "VAR _pend = [Nota · pendente · ranking · ref]",
      "VAR _nota = [Nota · nota final · ranking · ref]",
      "VAR _obt = [Nota · pontos obtidos · ranking · ref]",
      "VAR _poss = [Nota · pontos possíveis · ranking · ref]",
      "VAR _max = [Nota · nota · máximo]",
      "VAR _limA = [Nota · status · nota mínima atenção]",
      "VAR _limE = [Nota · status · nota mínima estável]",
      [l for k, (dim, sig) in enumerate(DIMENSOES, 1) for l in dim_quadro(k, dim, sig)],
      "-- 3 · Geometria",
      f"VAR _largNota = MAX ( 2, ROUND ( MIN ( _nota, _max ) / _max * {TRILHO}, 0 ) ) -- geometria",
      f"VAR _largObt = MAX ( 2, ROUND ( MIN ( _obt, _max ) / _max * {TRILHO}, 0 ) ) -- geometria",
      f"VAR _largPoss = ROUND ( MIN ( _poss, _max ) / _max * {TRILHO}, 0 ) -- geometria",
      f"VAR _xA = ROUND ( _limA / _max * {TRILHO}, 0 ) -- geometria",
      f"VAR _xE = ROUND ( _limE / _max * {TRILHO}, 0 ) -- geometria",
      "VAR _atraso = ( _pos - 1 ) * 60 -- geometria",
      "-- 2 · Textos",
      D.rs("_orc", "_to") + D.pct("_exec", "_te"),
      D.od_tabela(),
      "VAR _txtNota = IF ( _pend = 1, " + fmt_pts("_obt") + ", " + fmt_pts("_nota") + " )",
      C.bloco_od("_nK", "_txtNota").rstrip(),
      "VAR _txtDe = \"de \" & " + mk(fmt_pts("_poss")),
      "VAR _chave = " + D.esc("_obra"),
      'VAR _txtPos = FORMAT ( _pos, "00" )',
      'VAR _txtSub = ' + mk("_toTxt") + ' & " · " & ' + mk("_teTxt") + ' & " exec." & IF ( ISBLANK ( _idc ), "", '
      '" · IDC " & ' + mk('FORMAT ( _idc, "0.00", "pt-BR" )') + ' )',
      'VAR _clsSelo = IF ( _selo = "REAL", "selo selo-r", "selo selo-i" )',
      "VAR _htmlChip = " + DC.chip_status("_st", "_pend"),
      "VAR _htmlDim = \"<div class='dm'>\" & " + " & ".join(f"_d{k}Html" for k in range(1, len(DIMENSOES) + 1))
      + " & \"</div>\"",
      "VAR _htmlBarra =",
      "    IF (",
      "        _pend = 1,",
      "        \"<u class='a-gx' style='width:\" & _largPoss & \"px;animation-delay:\" & _atraso & \"ms'></u>\"",
      "            & \"<i class='sm' style='width:\" & _largObt & \"px' data-rk='\"",
      "            & _chave & \"' data-rd='\" & _atraso & \"'></i>\",",
      "        \"<i class='s\" & _st & \"' style='width:\" & _largNota & \"px' data-rk='\" & _chave & \"' data-rd='\" & _atraso",
      "            & \"'></i>\"",
      "    )",
      "VAR _htmlNota =",
      "    IF (",
      "        _pend = 1,",
      "        \"<p class='ab b6 pt pd'>\" & _nKOd & \"</p><p class='ab de'>\" & _txtDe & \"</p>\",",
      "        \"<p class='ab b6 pt'>\" & _nKOd & \"</p>\"",
      "    )",
      "-- 4 · Marcação",
      "RETURN",
      "    IF (",
      "        NOT ISBLANK ( _pos ) && NOT ISBLANK ( _pend ),",
      "        \"<div class='u ln\" & IF ( _st == 2, \" crit\", \"\" ) & \"' data-rr='\" & _chave & \"'>\"",
      "            & \"<p class='ab vs ix'>\" & _txtPos & \"</p>\"",
      "            & \"<div class='nm'><b>\" & " + D.esc("_obra") + " & \"</b><em>\" & _cod & \"</em>\"",
      "            & \"<span class='\" & _clsSelo & \"'>\" & _selo & \"</span></div>\"",
      "            & \"<p class='ab sub'>\" & _txtSub & \"</p>\"",
      "            & \"<div class='chips a-pop' style='animation-delay:\" & ( _atraso + 200 ) & \"ms'>\" & _htmlChip & \"</div>\"",
      "            & \"<div class='cota'>\" & _htmlBarra",
      "            & \"<b class='a-fd' style='left:\" & _xA & \"px;animation-delay:\" & ( _atraso + 500 ) & \"ms'></b>\"",
      "            & \"<b class='a-fd' style='left:\" & _xE & \"px;animation-delay:\" & ( _atraso + 500 ) & \"ms'></b></div>\"",
      "            & _htmlNota",
      "            & _htmlDim",
      "        & \"</div>\" & [Comum · JS contador] & [Comum · JS corrida]",
      "    )",
  ))

# ======================================================================================================== Onde a carteira perde pontos
PESA = r"T1 Visão geral\Onde a carteira perde pontos"
# F3 (docs/08 §5): o painel fica no eixo das DIMENSÕES (dItemNota[Dimensao], 7 linhas de 48 a partir de y 68 do painel:
# 336 dos 338): nome da dimensão (Segoe SB 15) + versalete com as obras que perderam pontos, onde falta dado e, nas
# dimensões de dois itens, o item que mais perde; pontos perdidos somados à direita (Barlow SB 16); trilho de 464 × 8
# em y 27 com os pontos perdidos separados pelo status da obra (vermelho, ocre, sálvia, tracejado), escala = a dimensão
# que mais perde. Dimensão sem dado em nenhuma obra: um fio tracejado no lugar do trilho e "falta na base".
CSS_PESA = (
    ".htmlViewerEntry{display:block!important;margin:0!important;padding:0!important}"
    ".pl{position:relative;height:48px;transition:background .15s}"
    ".pl:hover,.htmlViewerEntry.hover .pl{background:rgba(247,244,238,.9)}"
    ".pl .rt{position:absolute;left:0;top:0;display:flex;align-items:baseline;gap:10px;white-space:nowrap}"
    ".pl .rt span{font-size:15px;line-height:21px;font-weight:600}"
    ".pl .rt em{font-style:normal;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:12px;"
    "line-height:15px;letter-spacing:1.2px;color:#6B6B70}"
    ".pl .pt{right:0;top:0;font-size:16px;line-height:20px}"
    ".pl .pt.vz{color:#6B6B70}"
    ".pl .tr{position:absolute;left:0;top:27px;width:464px;height:8px;background:#EFEFEF}"
    # item sem dado em nenhuma obra: só um fio tracejado no lugar do trilho (a barra tracejada é a das obras pendentes)
    ".pl .tr.f{top:31px;height:0;background:transparent;border-top:1px dashed #9A9A9E}"
    ".pl .tr i{position:absolute;top:0;bottom:0}"
    ".pl .tr i.c{background:#C43737}.pl .tr i.a{background:#C9821F}.pl .tr i.e{background:#A9CDB9}"
    ".pl .tr i.p{background:#FFFFFF;border:1px dashed #3B3B3F;box-sizing:border-box}"
)
m("T1 · Pesa · CSS lista", PESA, "CSS da lista 'Onde a carteira perde pontos' (uma entrada por dimensão da nota).",
  "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(CSS_PESA))
m("T1 · Pesa · HTML subtítulo", PESA, "Subtítulo do painel 'Onde a carteira perde pontos' (quantas obras somam).",
  linhas("-- 1 · Leituras", "VAR _n = [Obras com análise · ref]",
         "-- 2 · Textos", 'VAR _txt = IF ( _n = 1, "pontos que a obra perde, por dimensão da nota", '
         '"pontos perdidos somados das " & ' + mk("_n") + ' & " obras, por dimensão" )',
         "-- 4 · Marcação", "RETURN",
         "    \"<div class='u' style='position:fixed;inset:0'><p class='ab' style='left:0;top:0;font-size:15px;"
         "line-height:20px;color:#3B3B3F'>\" & _txt & \"</p></div>\" & [Comum · JS contador]"))
m("T1 · Pesa · HTML linha", PESA,
  "Uma linha por dimensão da nota (granularidade dItemNota[Dimensao], ordem T1 · Pesa · posição): nome, quantas "
  "obras perderam pontos, em quantas falta dado e, com dois itens, o item que mais perde; pontos perdidos somados e a "
  "barra na escala da dimensão que mais perde, separada pelo status da obra (crítico, atenção, estável, pendente). "
  "Dimensão sem dado em nenhuma obra: trilho tracejado e 'falta na base' (ou 'sem dado na planilha', na Análise "
  "Crítica).",
  linhas(
      "-- 1 · Leituras",
      "VAR _pos = [T1 · Pesa · posição]",
      "VAR _rot = [Nota · item · dimensão]",
      "VAR _fonte = [Nota · item · fonte]",
      "VAR _itTop = [T1 · Pesa · item que mais perde] & \"\"",
      "VAR _itRot = IF ( _itTop = \"\", \"\", CALCULATE ( [Nota · item · nome curto], dItemNota[Item] = _itTop ) )",
      "VAR _perd = [Nota · item · perdidos · ref]",
      "VAR _poss = [Nota · item · possíveis · ref]",
      "VAR _nOb = [Nota · item · obras que perderam pontos · ref] + 0",
      "VAR _nSem = [T1 · Pesa · obras sem dado] + 0",
      "VAR _pC = [T1 · Pesa · perdidos das obras críticas] + 0",
      "VAR _pA = [T1 · Pesa · perdidos das obras em atenção] + 0",
      "VAR _pE = [T1 · Pesa · perdidos das obras estáveis] + 0",
      "VAR _pP = [T1 · Pesa · perdidos das obras pendentes] + 0",
      "VAR _max = [T1 · Pesa · maior perda]",
      "-- 3 · Geometria",
      "VAR _k = IF ( _max > 0, 464 / _max, 0 ) -- geometria",
      "VAR _xA = ROUND ( _pC * _k, 0 ) -- geometria",
      "VAR _xE = ROUND ( ( _pC + _pA ) * _k, 0 ) -- geometria",
      "VAR _xP = ROUND ( ( _pC + _pA + _pE ) * _k, 0 ) -- geometria",
      "VAR _xF = ROUND ( ( _pC + _pA + _pE + _pP ) * _k, 0 ) -- geometria",
      "VAR _atraso = ( _pos - 1 ) * 60 -- geometria",
      "-- 2 · Textos",
      "VAR _semDado = ISBLANK ( _poss )",
      f'VAR _txtFalta = IF ( _fonte = "Análise Crítica", "{DC.SEM_DADO_AC}", "{DC.FALTA_NA_BASE}" )',
      "VAR _txtOb = IF ( _nOb = 0, \"nenhuma obra\", IF ( _nOb = 1, \"1 obra\", " + mk("_nOb") + " & \" obras\" ) )",
      "VAR _txtSem = IF ( _fonte = \"Análise Crítica\", \"sem dado em \", \"falta em \" ) & " + mk("_nSem"),
      "VAR _txtEm = IF ( _semDado, _txtFalta, _txtOb & IF ( _nSem > 0, \" · \" & _txtSem, \"\" ) "
      "& IF ( _itRot = \"\", \"\", \" · mais em \" & _itRot ) )",
      "VAR _txtPts = IF ( _semDado, \"—\", " + fmt_pts("_perd") + " & \" pts\" )",
      D.od_tabela(),
      "VAR _nuPts = IF ( _semDado, \"\", " + fmt_pts("_perd") + " )",
      C.bloco_od("_pK", "_nuPts").rstrip(),
      "VAR _odPts = IF ( _semDado, _txtPts, _pKOd & \" pts\" )",
      "-- 4 · Marcação",
      "VAR _seg = \"' data-rd='\" & _atraso & \"'></i>\"",
      "VAR _htmlTr =",
      "    IF (",
      "        _semDado,",
      "        \"<div class='tr f a-gx' style='animation-delay:\" & _atraso & \"ms'></div>\",",
      "        \"<div class='tr a-fd' style='animation-delay:\" & _atraso & \"ms'>\"",
      "            & IF ( _xA > 0, \"<i class='c' style='left:0;width:\" & _xA & \"px' data-rk='\" & _rot & \"|c\" & _seg )",
      "            & IF ( _xE > _xA, \"<i class='a' style='left:\" & _xA & \"px;width:\" & ( _xE - _xA ) & \"px' data-rk='\""
      " & _rot & \"|a\" & _seg )",
      "            & IF ( _xP > _xE, \"<i class='e' style='left:\" & _xE & \"px;width:\" & ( _xP - _xE ) & \"px' data-rk='\""
      " & _rot & \"|e\" & _seg )",
      "            & IF ( _xF > _xP, \"<i class='p' style='left:\" & _xP & \"px;width:\" & ( _xF - _xP ) & \"px' data-rk='\""
      " & _rot & \"|p\" & _seg )",
      "        & \"</div>\"",
      "    )",
      "RETURN",
      "    IF (",
      "        NOT ISBLANK ( _pos ),",
      "        \"<div class='u pl' data-rr='\" & _rot & \"'>\"",
      "            & \"<div class='rt'><span>\" & _rot & \"</span><em>\" & UPPER ( _txtEm ) & \"</em></div>\"",
      "            & \"<p class='ab b6 pt\" & IF ( _semDado, \" vz\", \"\" ) & \"'>\" & _odPts & \"</p>\"",
      "            & _htmlTr",
      "        & \"</div>\" & [Comum · JS contador] & [Comum · JS corrida]",
      "    )",
  ))

# ======================================================================================================== Como os meses evoluíram
SEM = r"T1 Visão geral\Como os meses evoluíram"
# F3 (docs/08 §5): a contagem empilhada virou o MAPA obra × mês, no mesmo visual de 464 × 236 (y 68 do painel) e no
# mesmo eixo (dMes[Mes], uma entrada por mês da janela de 1 a 12 meses, para o tooltip do mês seguir valendo). Cada
# entrada desenha a coluna do mês: uma célula por obra, na ordem da lista (pontos perdidos no mês de referência), na
# cor do status da obra naquele mês, com a nota dentro quando cabe. A primeira coluna também escreve o nome das obras.
#   nomes em x 0 (MAPA_NOME de largura) · células de x MAPA_X0 a 464: vaga = (464 − MAPA_X0) ÷ n, célula = vaga − 2
#   linha = mín(28, 196 ÷ obras) · rótulo do mês embaixo da última linha (Segoe 13; o de referência em Semibold preto)
MAPA_X0, MAPA_NOME = 104, 98
CSS_SEM = (
    "#htmlContent{display:block!important;height:100vh;padding:0!important}"
    ".htmlViewerEntry{display:block!important;margin:0!important;padding:0!important}"
    # cada mês se posiciona pela posição na janela (o x vem do DAX)
    ".cm{position:fixed;top:0;height:236px}"
    ".cm .cl{position:absolute;display:flex;align-items:center;justify-content:center;box-sizing:border-box;"
    "font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:12px;line-height:14px;"
    "font-variant-numeric:tabular-nums;font-style:normal;transition:filter .15s;animation:mpEnt .3s ease-out backwards}"
    ".cm:hover .cl,.htmlViewerEntry.hover .cm .cl{filter:brightness(.94)}"
    ".cm .s2{background:#C43737;color:#FFFFFF}"
    ".cm .s1{background:#C9821F;color:#0B0B0C}"
    ".cm .s0{background:#A9CDB9;color:#1E5C43}"
    # pendente: branco com contorno tracejado grafite; sem aba no mês: só o fundo creme
    ".cm .sm{background:#FFFFFF;border:1px dashed #3B3B3F;color:#3B3B3F}"
    ".cm .sx{background:#F2F0EB}"
    f".cm .nm{{position:absolute;left:-{MAPA_X0}px;width:{MAPA_NOME}px;display:flex;align-items:center;"
    "font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:12px;line-height:14px;letter-spacing:.6px;"
    "color:#0B0B0C;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
    ".cm .ms{position:absolute;left:-12px;right:-12px;text-align:center;font-size:13px;line-height:16px;"
    "color:#6B6B70;white-space:nowrap}"
    ".cm .ms.ref{font-weight:600;color:#0B0B0C}"
    "@keyframes mpEnt{from{opacity:0}}"
    "@media (prefers-reduced-motion:reduce){.cm .cl{animation:none}}"
)
m("T1 · Semestre · CSS lista", SEM, "CSS do mapa obra × mês de Como os meses evoluíram (uma entrada por mês da janela).",
  "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(CSS_SEM))
m("T1 · Semestre · HTML subtítulo", SEM,
  "Subtítulo do painel Como os meses evoluíram: o que o mapa mostra e a janela (nota de cada obra, mês a mês · out/25 "
  "a set/26).",
  linhas("-- 1 · Leituras", "VAR _ini = [Série · primeiro mês]", "VAR _ref = [Mês de referência]",
         "VAR _n = [Série · meses até a referência]",
         "-- 2 · Textos",
         'VAR _txtIni = FORMAT ( _ini, "mmm/yy", "pt-BR" )',
         'VAR _txtRef = FORMAT ( _ref, "mmm/yy", "pt-BR" )',
         'VAR _txt = "nota de cada obra, mês a mês · " & IF ( _n = 1, _txtRef, _txtIni & " a " & _txtRef )',
         "-- 4 · Marcação", "RETURN",
         "    IF (",
         "        NOT ISBLANK ( _ref ),",
         "        \"<div class='u' style='position:fixed;inset:0'><p class='ab' style='left:0;top:0;font-size:15px;"
         "line-height:20px;color:#3B3B3F'>\" & _txt & \"</p></div>\"",
         "    )"))
m("T1 · Semestre · HTML coluna", SEM,
  "Mapa obra × mês: uma entrada por mês da janela (granularidade dMes[Mes], de 1 a 12 meses até o de referência) com a "
  "coluna do mês, uma célula por obra na ordem da lista de obras (Nota · recorte · obras por pontos perdidos (lista), "
  "mês de referência), pintada pelo status da obra no mês (crítico, atenção, estável, pendente tracejado, sem aba em "
  "creme) e com a nota (ou os pontos obtidos, na pendente) quando a célula tem 24 px ou mais. A primeira coluna "
  "escreve os nomes das obras à esquerda; o rótulo do mês segue a regra da janela e o de referência fica em Semibold "
  "preto.",
  linhas(
      "-- 1 · Leituras",
      "VAR _noRecorte = [Série · mês até a referência]",
      "VAR _lista = [Nota · recorte · obras por pontos perdidos (lista)]",
      "VAR _n = [Série · meses até a referência]",
      "VAR _pos = [Série · posição na janela]",
      "VAR _mesAno = [Mês · rótulo curto]",
      "VAR _mesAbrev = [Mês · abreviado]",
      "VAR _ehRef = [Série · é o mês de referência]",
      "VAR _nOb = IF ( _lista = \"\", 0, PATHLENGTH ( _lista ) )",
      "-- 3 · Geometria",
      f"VAR _slot = DIVIDE ( {464 - MAPA_X0}, _n ) -- geometria",
      f"VAR _x = {MAPA_X0} + ROUND ( ( _pos - 1 ) * _slot, 0 ) -- geometria",
      "VAR _w = ROUND ( _slot, 0 ) -- geometria",
      "VAR _cw = MAX ( 4, ROUND ( _slot, 0 ) - 2 ) -- geometria",
      "VAR _h = MIN ( 28, INT ( DIVIDE ( 196, _nOb ) ) ) -- geometria",
      "VAR _yMes = _nOb * _h + 6 -- geometria",
      "VAR _passo = ROUND ( DIVIDE ( 420, _n ), 0 ) -- geometria",
      "VAR _atraso = ( _pos - 1 ) * _passo -- geometria",
      "-- 2 · Textos",
      "VAR _comAno = _slot >= 48 || _pos = 1 || _mesAbrev = \"jan\"",
      "VAR _mostraMes = _slot >= 40 || MOD ( _n - _pos, 2 ) = 0",
      "VAR _rotMes = IF ( _mostraMes, IF ( _comAno, _mesAno, _mesAbrev ), \"\" )",
      "VAR _cabe = _cw >= 24 && _h >= 18",
      "-- 4 · Marcação",
      "VAR _celulas =",
      "    CONCATENATEX (",
      "        GENERATESERIES ( 1, _nOb ),",
      "        VAR _o = PATHITEM ( _lista, [Value] )",
      "        VAR _st = CALCULATE ( [Nota · status · um mês], dObra[Obra] = _o )",
      "        VAR _pd = CALCULATE ( [Nota · pendente · um mês], dObra[Obra] = _o )",
      "        VAR _nt = CALCULATE ( [Nota · nota final · um mês], dObra[Obra] = _o )",
      "        VAR _ob = CALCULATE ( [Nota · pontos obtidos · um mês], dObra[Obra] = _o )",
      "        VAR _cls = SWITCH ( TRUE (), _pd = 1, \"sm\", NOT ISBLANK ( _st ), \"s\" & _st, \"sx\" )",
      "        VAR _v = IF ( _pd = 1, _ob, _nt )",
      "        VAR _txt = IF ( _cabe && NOT ISBLANK ( _v ), " + mk("IF ( ROUND ( _v, 1 ) >= 10, \"10\", FORMAT ( _v, \"0.0\", \"pt-BR\" ) )") + ", \"\" )",
      "        VAR _y = ( [Value] - 1 ) * _h /* geometria */",
      "        RETURN",
      "            IF ( _pos = 1, \"<p class='nm a-fd' style='top:\" & _y & \"px;height:\" & ( _h - 2 ) "
      "& \"px;animation-delay:\" & ( [Value] - 1 ) * 30 & \"ms'>\" & "
      + D.esc("_o") + " & \"</p>\" )",
      "                & \"<i class='cl \" & _cls & \"' style='left:0;top:\" & _y & \"px;width:\" & _cw & \"px;height:\" & ( _h - 2 )",
      "                & \"px;animation-delay:\" & ( _atraso + ( [Value] - 1 ) * 30 ) & \"ms' data-rk='\" & _mesAno & \"|\" & [Value]",
      "                & \"'>\" & _txt & \"</i>\",",
      "        \"\",",
      "        [Value], ASC",
      "    )",
      "RETURN",
      "    IF (",
      "        _noRecorte = 1 && _nOb > 0,",
      "        \"<div class='u cm' style='left:\" & _x & \"px;width:\" & _w & \"px'>\" & _celulas",
      "            & \"<p class='ms a-fd\" & IF ( _ehRef = 1, \" ref\", \"\" ) & \"' style='top:\" & _yMes "
      "& \"px;animation-delay:\" & _atraso & \"ms'>\" & _rotMes & \"</p>\"",
      "        & \"</div>\" & [Comum · JS contador]",
      "    )",
  ), passos=C.PASSOS_DENSO)

# ======================================================================================================== síntese
SIN = r"T1 Visão geral\Síntese"
# v2 (Figma Faixa · Leitura do mês 387:3985): só na largura da lista, 1004 × 96 (aprovado pelo Alisson em 07/10/2026);
# rótulo em 24,16 e texto Segoe 15/21 em 24,37 (956 de largura, duas linhas)
CSS_SIN = (".si{position:fixed;inset:0}"
           ".si .vs{left:24px;top:16px;color:rgba(233,224,207,.7)}"
           ".si .tx{position:absolute;left:24px;top:37px;width:956px;font-size:15px;line-height:21px;color:#F7F4EE}"
           # F4: texto longo demais para duas linhas (mais de SIN_MAX caracteres) cai para 14/19 em até três, sem cortar
           ".si .tx.t3{top:34px;font-size:14px;line-height:19px}")
SIN_MAX = 245   # duas linhas de 956 px em Segoe 15 (≈ 7,3 px por caractere, com folga)
m("T1 · Síntese · CSS", SIN, "CSS da faixa-síntese (leitura do mês).",
  "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(CSS_SIN))

N_CRIT = 3   # obras críticas citadas pelo nome (e a nota); acima disso, "e mais N"


def obra_critica(k: int) -> list[str]:
    p = f"_c{k}"
    return [
        f"VAR {p} = PATHITEM ( _listaCrit, {k} )",
        f"VAR {p}Nota = CALCULATE ( [Nota · nota final · ranking · ref], dObra[Obra] = {p} )",
        # crítica pela trava (nota de atenção ou estável): a frase diz o porquê
        f'VAR {p}Trv = CALCULATE ( [Nota · trava · motivo · ref], dObra[Obra] = {p} ) & ""',
        f'VAR {p}Fr = IF ( {p} = "", "", ' + D.esc(p) + f' & " (" & IF ( {k} = 1, "nota ", "" ) & '
        + mk(fmt_pts(f"{p}Nota")) + f' & IF ( {p}Trv = "", "", ", trava de " & SUBSTITUTE ( {p}Trv, "|", " e " ) ) & ")" )',
    ]


def item_frase(n: int) -> list[str]:
    """'no médio prazo (0,5 de 1,5)' do n-ésimo item que a frase cita para a obra que mais perde (a lista
    T1 · Obras · itens que mais perdem: empate no topo cita todos; auditoria da Fase 2, minor 2)."""
    p = f"_i{n}"
    f = f"dItemNota[Item] = {p}Cod"
    return [
        f"VAR {p}Cod = PATHITEM ( _iL, {n} ) & \"\"",
        f"VAR {p}Frase = CALCULATE ( [Nota · item · nome em frase], {f} )",
        f"VAR {p}Pts = CALCULATE ( [Nota · item · pontos · ref], {f}, dObra[Obra] = _o1 )",
        f"VAR {p}Poss = CALCULATE ( [Nota · item · possíveis · ref], {f}, dObra[Obra] = _o1 )",
        f'VAR {p}Fr = IF ( {p}Cod = "", "", {em_frase(p + "Frase")} & " (" & {mk(fmt_pts(p + "Pts"))} & " de " '
        f'& {mk(fmt_pts(p + "Poss"))} & ")" )',
    ]


m("T1 · Síntese · HTML", SIN,
  "Leitura do mês na faixa preta, pela nota: as obras críticas (até 3, com a nota e, se for o caso, a trava) e quantas "
  "estão em atenção, estáveis "
  "e pendentes; depois a obra que mais perde pontos no mês e os dois itens em que mais perde (pontos de possíveis). "
  "Com todas pendentes, diz que falta item na base e quem mais perde nos itens que já dá para calcular.",
  linhas(
      "-- 1 · Leituras",
      "VAR _mesC = [Mês de referência · curto]",
      "VAR _mesCM = [Mês de referência · curto maiúsculo]",
      "VAR _c = [Nota · carteira · obras críticas · ref] + 0",
      "VAR _a = [Nota · carteira · obras em atenção · ref] + 0",
      "VAR _e = [Nota · carteira · obras estáveis · ref] + 0",
      "VAR _p = [Nota · carteira · obras pendentes · ref] + 0",
      "VAR _listaCrit = [Nota · recorte · obras críticas (lista)]",
      "VAR _ranking = [Nota · recorte · obras por pontos perdidos (lista)]",
      "VAR _o1 = PATHITEM ( _ranking, 1 )",
      "VAR _perd1 = CALCULATE ( [Nota · pontos perdidos · ranking · ref], dObra[Obra] = _o1 )",
      "VAR _pend1 = CALCULATE ( [Nota · pendente · ranking · ref], dObra[Obra] = _o1 )",
      "VAR _poss1 = CALCULATE ( [Nota · pontos possíveis · ranking · ref], dObra[Obra] = _o1 )",
      [l for k in range(1, N_CRIT + 1) for l in obra_critica(k)],
      "VAR _iL = CALCULATE ( [T1 · Obras · itens que mais perdem (lista) · ref], dObra[Obra] = _o1 ) & \"\"",
      *DC.onde_falta(),
      "VAR _iN = IF ( _iL = \"\", 0, PATHLENGTH ( _iL ) )",
      item_frase(1), item_frase(2),
      "-- 2 · Textos",
      "VAR _frasesCrit = " + " & ".join(
          f'IF ( _c{k}Fr <> "", IF ( {k} = 1, "", IF ( {k} = MIN ( _c, {N_CRIT} ), " e ", ", " ) ) & _c{k}Fr, "" )'
          for k in range(1, N_CRIT + 1)) + f' & IF ( _c > {N_CRIT}, " e mais " & {mk(f"( _c - {N_CRIT} )")}, "" )',
      # os outros estados, na ordem da régua: "1 em atenção, 2 estáveis e 3 pendentes"
      'VAR _tA = IF ( _a > 0, ' + mk("_a") + ' & " em atenção" )',
      'VAR _tE = IF ( _e > 0, ' + mk("_e") + ' & IF ( _e = 1, " estável", " estáveis" ) )',
      'VAR _tP = IF ( _p > 0, ' + mk("_p") + ' & IF ( _p = 1, " pendente", " pendentes" ) )',
      'VAR _nOutros = INT ( _a > 0 ) + INT ( _e > 0 ) + INT ( _p > 0 )',
      "VAR _txtOutros =",
      "    SWITCH (",
      "        _nOutros,",
      "        0, \"\",",
      "        1, _tA & _tE & _tP,",
      "        2, IF ( _a > 0, _tA & \" e \" & _tE & _tP, _tE & \" e \" & _tP ),",
      "        _tA & \", \" & _tE & \" e \" & _tP",
      "    )",
      "VAR _txtAbre =",
      "    SWITCH (",
      "        TRUE (),",
      "        _c + _a + _e + _p = 0, \"Nenhuma obra com planilha em \" & _mesC & \".\",",
      "        _c + _a + _e = 0, IF ( _p = 1, \"A obra está pendente em \", \"As \" & " + mk("_p") + " & \" obras estão pendentes em \" )",
      # "sem nota" vem antes da fonte, para a frase caber em 2 linhas com "(na JANGADA, também na planilha)" (Fase 3, r2)
      "            & _mesC & \", sem nota: \" & IF ( _ondeSoFora, \"há valor fora da faixa na base complementar\", "
      "\"falta item \" & _onde & _ondeFora ) & \".\",",
      "        _c = 0, \"Nenhuma obra crítica em \" & _mesC & \": \" & _txtOutros & \".\",",
      "        IF ( _c = 1, \"1 obra crítica em \", " + mk("_c") + " & \" obras críticas em \" ) & _mesC & \": \" & _frasesCrit",
      "            & IF ( _txtOutros = \"\", \".\", \"; \" & _txtOutros & \".\" )",
      "    )",
      "VAR _txtPerde =",
      "    SWITCH (",
      "        TRUE (),",
      "        _o1 = \"\", \"\",",
      "        NOT ( _perd1 > 0 ), \" Nenhuma obra perdeu pontos nos itens com dado.\",",
      "        IF ( _c + _a + _e = 0, \" No que já dá para calcular, quem mais perde é a \", "
      "\" Quem mais perde pontos é a \" )",
      "            & " + D.esc("_o1") + " & \" (\" & " + mk(fmt_pts("_perd1"))
      + " & IF ( _pend1 = 1, \" dos \" & " + mk(fmt_pts("_poss1")) + " & \" possíveis\", \"\" ) & \")\"",
      # de 3 itens em diante, "em N itens empatados": com os três nomes a síntese ia a 3 linhas (Fase 3, rodada 2, m2)
      "            & \", mais \" & SWITCH ( _iN, 1, _i1Fr, 2, _i1Fr & \" e \" & _i2Fr, \"em \" & " + mk("_iN") + " & \" itens empatados\" ) & \".\"",
      "    )",
      "VAR _txtSin = _txtAbre & _txtPerde",
      f"VAR _nSin = LEN ( SUBSTITUTE ( SUBSTITUTE ( _txtSin, \"{C.MARCA_ABRE}\", \"\" ), \"{C.MARCA_FECHA}\", \"\" ) )",
      "-- 4 · Marcação",
      "RETURN",
      "    \"<div class='u si escuro'><p class='ab vs'>LEITURA DE \" & _mesCM & \"</p>\"",
      f"        & \"<p class='tx\" & IF ( _nSin > {SIN_MAX}, \" t3\", \"\" ) & \"'>\" & _txtSin & \"</p>\"",
      "    & \"</div>\" & [Comum · JS contador]",
  ))

# Fase 2 da régua antiga (13/10/2026): nada retirado deste gerador (os HTML seguem com os mesmos nomes, lendo a nota)
RETIRADAS: set[str] = set()

if __name__ == "__main__":
    sys.exit(gravar([x for x in MEDIDAS if x.nome not in RETIRADAS], RAIZ / "dax" / "T1", GERADO))

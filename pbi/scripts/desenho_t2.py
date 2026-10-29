#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""desenho_t2 — desenho da Tela 02 · Análise crítica (pbi/dax/T2/**, menos Contas). A tela é da obra em foco; só lê
contas (base · foco e contas_t2.py).

Redesenho v2 (07/10/2026): Figma FjBWDk5odF9HaZ2pwhGosl, página 04 · Redesenho v2 (372:685), Tela 02 · v2 386:847;
geometria e regras em pbi/spec/redesenho/t02.md §2–§5. Canvas 1920 × 1080 (prancheta em 300,12):
  cartões y 109 (302 × 140) em x 352 · 654 · 955 · 1257 · 1558 · O quadradinho 352,273 (548 × 584): entradas y +68
  (548 × 108), itens y +184 (10 × 30), resultado y +494 (44 + 4 + 40) · Com e sem estoque 352,897 (548 × 143), texto em
  +20,+39 · Como o resultado se forma 940,273 (508 × 350): degraus y +68 (508 × 282, colunas de 508 ÷ n) · Resultado
  da obra, mês a mês 940,663 (508 × 377): subtítulo y +32, legenda no papel de parede (y +68), colunas y +96 (grade de
  488 ÷ n e 20 de margem para os rótulos do mês de referência, 508 × 281) · Itens da nota (era Sinais do mês)
  1488,273 (372 × 388): subtítulo y +32, linhas y +68 (8 × 40) · Desembolso do mês 1488,701 (372 × 339): miolo y +68
  (372 × 271).
Fase 2 da régua antiga (13/10/2026): a régua antiga (sinais, pesos, mobilização) saiu. O cartão Nota da obra e Itens da nota leem
as contas Nota · … · foco; o status do desembolso e as marcas do resultado e do físico seguem os pontos dos itens
Fluxo de caixa, Orçamento e item prazo da nota. Faixas e máximos vêm do modelo (nenhum limite escrito aqui).
Negativo em vermelho (.ng) em todo número, rótulo e barra, inclusive o desvio físico; a única exceção é o desvio (e a
diferença) de desembolso negativo, que fica em preto; limite de régua nunca é vermelho. Status por cor (marcas e chips v2 e helpers da nota da camada comum); hachura só na série sem estoque.

F4 (pedido do Alisson, 28/10/2026): todo número exibido conta com o odômetro (os que não têm bloco Od vão marcados
com C.marca e o m() converte com C.envolver_marcas) e todo elemento de gráfico entra animado: barras e colunas pela
corrida (inclusive a minissérie de Itens e as barras da nota mês a mês), linhas de referência e ligações crescendo da
esquerda (.a-gx), marcas e pílulas crescendo (.a-pop) e eixo e grade aparecendo (.a-fd), em cascata pelo style inline.

    python -X utf8 pbi/scripts/desenho_t2.py
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import contador as C  # noqa: E402
import desenho_projeto as D  # noqa: E402
from contas_lib_projeto import Medida, gravar  # noqa: E402
import desenho_comum as DC  # noqa: E402
from desenho_comum import dax_lit  # noqa: E402

RAIZ = AQUI.parent
GERADO = "pbi/scripts/desenho_t2.py"
MEDIDAS: list[Medida] = []
MENOS = D.MENOS


def m(nome, pasta, descricao, dax, passos=C.PASSOS):
    """Medida de desenho; os valores marcados com C.marca() viram odômetro no fim (F4)."""
    MEDIDAS.append(Medida(nome, pasta, "texto", descricao, C.envolver_marcas(dax, passos)))


def linhas(*ls) -> str:
    def plano(x):
        for g in x:
            if isinstance(g, list):
                yield from plano(g)
            else:
                yield g
    return "\n".join(plano(ls))


def ng(p: str) -> str:
    """Trecho para dentro de um literal de class: ' ng' quando o texto formatado com o prefixo `p` saiu negativo."""
    return f"\" & IF ( {p}S = \"{MENOS}\", \" ng\", \"\" ) & \""


def span_ng(p: str, txt: str | None = None) -> str:
    """Expressão DAX: o texto do prefixo `p` (ou `txt`) num <span>, vermelho quando negativo."""
    return f"\"<span class='\" & IF ( {p}S = \"{MENOS}\", \"ng\", \"\" ) & \"'>\" & {txt or p + 'Txt'} & \"</span>\""


def marca(st: str) -> str:
    """Expressão DAX: <i> da marca de status v2 (0/1/2)."""
    return f'"<i class=\'mk mk" & {st} & "\'></i>"'


def cls_item(pts: str, poss: str) -> str:
    """Classe da marca pelos pontos de um item da nota: "0" cheio · "1" parcial · "2" zero · "" sem dado (desenho:
    só escolhe a classe a partir das contas)."""
    return f'IF ( ISBLANK ( {pts} ), "", IF ( {pts} >= {poss}, "0", IF ( {pts} = 0, "2", "1" ) ) )'


def marca_item(pts: str, poss: str, ms: int | None = None) -> str:
    """Expressão DAX: marca v2 na cor dos pontos do item (cheio sálvia, parcial ocre, zero vermelho); vazia sem dado.
    Com `ms` (telas, F4), entra crescendo (.a-pop) `ms` depois do número; sem `ms` (tooltips_t2, que têm a cascata C5
    própria, sem animation-delay), a marca de sempre."""
    c = cls_item(pts, poss)
    if ms is None:
        return f'IF ( {c} = "", "", "<i class=\'mk mk" & {c} & "\'></i>" )'
    return f'IF ( {c} = "", "", "<i class=\'a-pop mk mk" & {c} & "\' style=\'animation-delay:{ms}ms\'></i>" )'


def item_txt_m(p: str, pts: str, poss: str, fonte: str = "base") -> list[str]:
    """DC.item_txt com os dois números marcados para o odômetro (F4): {p}Txt = "4,25 de 4,5" contando."""
    falta = DC.FALTA_NA_BASE if fonte == "base" else DC.SEM_DADO_AC
    return [f'VAR {p}Txt = IF ( ISBLANK ( {pts} ), "{falta}", '
            + C.marca(f'FORMAT ( {pts}, "{DC.FMT_PTS}", "pt-BR" )') + ' & " de " & '
            + C.marca(f'FORMAT ( {poss}, "{DC.FMT_PTS}", "pt-BR" )') + ' )']


def chip_item_m(p: str, pts: str, poss: str, fonte: str = "base", ms: str = "0") -> list[str]:
    """DC.chip_item com os números contando e a pílula entrando crescendo (.a-pop) `ms` (DAX) depois (F4). O texto vai
    num <span> dentro da pílula: a pílula é inline-flex, e sem ele os espaços em volta dos números (<o-n>) somem
    ("0,5de2,0")."""
    return item_txt_m(p, pts, poss, fonte) + [
        f'VAR {p}Cls = SWITCH ( TRUE (), ISBLANK ( {pts} ), "f", {pts} >= {poss}, "c", {pts} = 0, "z", "p" )',
        f'VAR {p}Html = "<span class=\'a-pop chi chi-" & {p}Cls & "\' style=\'animation-delay:" & {ms} & "ms\'><span>" '
        f'& {p}Txt & "</span></span>"',
    ]


def fmt_pts_dax(v: str) -> str:
    """DAX: pontos da nota em texto ("7,75" · "4,0" · "0,5")."""
    return f'FORMAT ( {v}, "{DC.FMT_PTS}", "pt-BR" )'


def faixa_html(expr: str) -> str:
    """Texto de faixa vindo do modelo, pronto para HTML (só os sinais < e > escapados)."""
    return f'SUBSTITUTE ( SUBSTITUTE ( {expr}, "<", "&lt;" ), ">", "&gt;" )'


# ======================================================================================================== cartões
def regua(itens) -> str:
    """Expressão DAX da régua do verso. Cada item é (classe da marca, texto): o texto é um literal ou, quando começa
    com '=', uma expressão DAX (faixas lidas do modelo; nenhum limite da nota fica escrito aqui)."""
    partes = []
    for c, t in itens:
        mk = f"<i class='mk {c}'></i>" if c else ""
        if t.startswith("="):
            partes.append(f"\"{mk}<span>\" & {t[1:]} & \"</span>\"")
        else:
            partes.append(f"\"{mk}<span>{t}</span>\"")
    return " & ".join(partes)


def cartao(chave, eb, leituras_, textos, hero, lado, ctx, regra, origem, regua_itens, escuro=False, anima=(), desc="",
           hero_p=None, lado_p=None, nome=None):
    """Cartão v2 com flip (frente e verso no mesmo visual; CSS 'T2 · Cartão · CSS'). `eb`, `hero`, `lado` e `ctx` são
    expressões DAX de texto (ctx já com a marca ou o chip em HTML). `hero_p`/`lado_p`: prefixo do formatador cujo sinal
    decide o vermelho (.ng). Verso na geometria comum: "DE ONDE VEM" em y 82 com régua e 106 sem régua."""
    topo_ond = 82 if regua_itens else 106
    verso = ("\"<div class='lado verso sobre-creme'>\"\n"
             "            & \"<p class='ab vs v1'>COMO É CALCULADO</p>\"\n"
             f"            & \"<p class='regra'>{regra}</p>\"\n"
             f"            & \"<div class='ond' style='top:{topo_ond}px'><span class='vs'>DE ONDE VEM</span>"
             f"<span>{origem}</span></div>\"\n")
    if regua_itens:
        verso += f"            & \"<div class='regua'>\" & {regua(regua_itens)} & \"</div>\"\n"
    verso += "        & \"</div>\""
    cls_hero = ng(hero_p) if hero_p else ""
    cls_lado = ng(lado_p) if lado_p else ""
    lado_html = f" & \"<span class='b5 lado2{cls_lado}'>\" & {lado} & \"</span>\"" if lado else ""
    dax = linhas(
        "-- 1 · Leituras", [f"VAR {v} = [{x}]" for v, x in leituras_],
        "-- 2 · Textos", textos,
        [D.od_tabela()] + list(anima) if anima else [],
        "-- 4 · Marcação",
        "RETURN",
        f"    \"<div class='u kc{' escuro' if escuro else ''}' tabindex='0'>\"",
        "        & \"<div class='lado frente'>\"",
        f"            & \"<p class='ab vs eb'>\" & {eb} & \"</p>\"",
        f"            & \"<div class='linha1'><span class='b6 hero{cls_hero}'>\" & {hero} & \"</span>\"{lado_html} & \"</div>\"",
        f"            & \"<p class='ctx'>\" & {ctx} & \"</p>\"",
        "        & \"</div>\"",
        "        & " + verso,
        "    & \"</div>\" & [Comum · JS contador]",
    )
    m(nome or f"T2 · Cartão {chave} · HTML", r"T2 Análise crítica\Cartões", desc or f"Cartão '{chave}' da obra em foco "
      "(frente e verso). Só lê contas · foco.", dax)


CARTOES = r"T2 Análise crítica\Cartões"
m("T2 · Cartão · CSS", CARTOES, "CSS dos cartões da T2: o do cartão v2 com flip (camada comum) mais a marca de status "
  "antes do contexto (as cores da marca são as mesmas no cartão escuro) e o chip de status do cartão Nota da obra.",
  "-- 4 · Marcação\n[Comum · CSS cartão]\n    & " + dax_lit(".kc .ctx .mk{margin-right:7px;vertical-align:-1px}"
                                                    ".kc .ctx .chip{height:21px;margin:-1px 8px 0 0;vertical-align:top}"))

# F3 (docs/08 §5): cinco cartões da obra em foco. O escuro (1º, a resposta de "por que a obra tem essa nota?") é a
# nota; depois custo (IDC), resultado da planilha, sem estoque e prazo. O cartão "Mês anterior" saiu (repetia o mês a
# mês). Os nomes dos visuais da página ficam (T2_Kpi_Resultado, …): o tour fala de posição.
# Nota da obra: a nota e o chip de status; pendente mostra os pontos que já dá para calcular; trava diz o motivo
cartao(
    "nota da obra", '"Nota da obra · " & _mesC',
    [("_nota", "Nota · nota final · ranking · foco"), ("_st", "Nota · status · ranking · foco"), ("_pend", "Nota · pendente · ranking · foco"),
     ("_ob", "Nota · pontos obtidos · ranking · foco"), ("_po", "Nota · pontos possíveis · ranking · foco"),
     ("_pe", "Nota · pontos perdidos · ranking · foco"), ("_faltB", "Nota · itens faltando na base · foco"),
     ("_faltP", "Nota · itens faltando na planilha · foco"), ("_fora", "Nota · itens fora da faixa · foco"),
     ("_trv", "Nota · trava · motivo · foco"),
     ("_fxC", "Nota · status · faixa crítico"), ("_fxA", "Nota · status · faixa atenção"),
     ("_fxE", "Nota · status · faixa estável"), ("_mesC", "Mês de referência · curto")],
    DC.nota_txt("_n", "_nota", "_ob", "_po", "_pend") + DC.pontos("_pe", "_tpe") + [
        "VAR _semObra = ISBLANK ( _nota ) && _pend <> 1",
        "VAR _txtFalt = " + DC.falta_curto("( _faltB + 0 )", "( _faltP + 0 )", "( _fora + 0 )"),
        "VAR _chip = SUBSTITUTE ( " + DC.chip_status("_st", "_pend") + ", \"<span class='chip \", "
        "\"<span style='animation-delay:450ms' class='a-pop chip \" )",
        "VAR _txtCtx =",
        "    SWITCH (",
        "        TRUE (),",
        "        _semObra, \"sem aba no mês\",",
        "        _pend = 1, _chip & " + C.marca("_txtFalt") + ",",
        "        _trv & \"\" <> \"\", _chip & \"trava de \" & SUBSTITUTE ( _trv, \"|\", \" e \" ),",
        "        _chip & IF ( _pe = 0, \"não perde ponto\", \"perde \" & " + C.marca("_tpeTxt") + " & \" pontos\" )",
        "    )",
        # no pendente o número grande são os pontos obtidos (sem nota); o "de Y" vai ao lado
        "VAR _odV = IF ( _pend = 1, _ob, _nota )",
        f"VAR _tnN = FORMAT ( _odV, \"{DC.FMT_PTS}\", \"pt-BR\" )",
        "VAR _tnTxt = IF ( _semObra, \"—\", _tnN )"],
    "_tnOd", "IF ( _pend = 1, \"de \" & " + C.marca("_nPo") + ", \"\" )", "_txtCtx",
    "Soma dos nove itens, de 0 a 10; IDC &lt; 0,90 ou atraso &gt; 3 meses: crítica.", "Planilha, base e cronograma",
    [("mk2", "=" + faixa_html("_fxC")), ("mk1", "=" + faixa_html("_fxA")), ("mk0", "=" + faixa_html("_fxE")),
     ("mkm", "pendente")],
    escuro=True, anima=D.od_num("_odV", "_tn"), nome="T2 · Cartão nota da obra · HTML",
    desc="Cartão 'Nota da obra' da obra em foco no mês de referência (o escuro): a nota e o chip de status (crítico, "
         "atenção, estável; com a trava, o motivo) ou, sem a base completa, pendente com os pontos obtidos de quantos já "
         "dá para calcular. O verso diz a régua e as faixas de status (lidas das medidas). Só lê contas · foco.")

# Custo: IDC da obra e o resultado aplicado; a marca e o "X de Y" vêm dos pontos do item custo
cartao(
    "custo", '"Custo · IDC"',
    [("_idc", "IDC · foco"), ("_ra", "Resultado aplicado · foco"), ("_pto", "Nota · pontos custo · foco"),
     ("_pso", "Nota · possíveis · custo · foco")],
    ['VAR _tiN = FORMAT ( _idc, "0.00", "pt-BR" )', 'VAR _tiTxt = IF ( ISBLANK ( _idc ), "—", _tiN )']
    + D.rs("_ra", "_tra", mais=True) + item_txt_m("_tk", "_pto", "_pso", fonte="ac") + [
        "VAR _txtCtx = IF ( ISBLANK ( _idc ), \"sem aba no mês\", " + marca_item("_pto", "_pso", 450) + " & \"na nota, \" & _tkTxt )"],
    "_tiOd", "_traOd", "_txtCtx",
    "Valor agregado ÷ custo aplicado (com a dívida). Ao lado, a diferença em R$.", "Análise Crítica",
    [], anima=D.od_num("_idc", "_ti") + D.od_rs("_ra", "_tra"), hero_p=None, lado_p="_tra",
    desc="Cartão de custo da obra em foco: IDC (valor agregado ÷ custo aplicado) e o resultado aplicado em R$, com a "
         "marca e os pontos do item custo da nota. Só lê contas · foco.")

# Resultado da planilha: aplicado + a realizar; o % do orçamento vai para o contexto
cartao(
    "resultado", '"Resultado da planilha · " & _mesC',
    [("_res", "Resultado da obra · foco"), ("_pct", "Resultado % · foco"), ("_ar", "A realizar · foco"),
     ("_mesC", "Mês de referência · curto")],
    D.rs("_res", "_tr") + D.pct("_pct", "_tp", casas=2, mais=True) + D.rs("_ar", "_tar") + [
        # retorno visual a4806f3 ("−10,32% do orçamento · R$ 119 mil a re…"): "do orç." cabe nos 262 da linha até
        # com "−10,32% do orç. · −R$ 1,23 mi a realizar" (~252 px)
        "VAR _txtCtx = IF ( ISBLANK ( _res ), \"sem aba no mês\", " + span_ng("_tp", C.marca("_tpTxt"))
        + " & \" do orç. · \" & " + C.marca("_tarTxt") + " & \" a realizar\" )"],
    "_trOd", None, "_txtCtx",
    "Como a planilha apresenta: o resultado aplicado mais o que ainda vai se realizar.", "Quadradinho da aba",
    [], anima=D.od_rs("_res", "_tr"), hero_p="_tr")

cartao(
    "sem estoque", '"Sem estoque e adiantamentos"',
    [("_sem", "Resultado sem ativos · foco"), ("_at", "Ativos não consumidos · foco")],
    D.rs("_sem", "_ts") + D.rs("_at", "_tat") + [
        "VAR _txtCtx = IF ( ISBLANK ( _sem ), \"sem aba no mês\", " + C.marca("_tatTxt")
        + " & \" pagos e ainda não aplicados\" )"],
    "_tsOd", None, "_txtCtx",
    "Resultado menos o pago e não aplicado: adiantamentos, estoque, equipamentos.", "Resultado menos itens 2 a 6",
    [], anima=D.od_rs("_sem", "_ts"), hero_p="_ts")

# Prazo (era o físico): atraso em meses pelo cronograma; a marca segue o item prazo; a régua mostra a 1ª e a última faixa
FX_FF = 'SUBSTITUTE ( CALCULATE ( [Nota · item · faixas], dItemNota[Item] = "prazo" ), " · ", "|" )'
cartao(
    "prazo", '"Prazo · atraso"',
    [("_atr", "Prazo · atraso (meses) · foco"), ("_term", "Prazo · término projetado · foco"),
     ("_exec", "Físico · executado acumulado · foco"), ("_ptf", "Nota · pontos prazo · foco"),
     ("_psf", "Nota · possíveis · prazo · foco")],
    ['VAR _taN = FORMAT ( _atr, "0.0", "pt-BR" )', 'VAR _taTxt = IF ( ISBLANK ( _atr ), "—", _taN )']
    + D.pct("_exec", "_te") + [
        "VAR _txtLado = IF ( ISBLANK ( _atr ), \"\", IF ( ROUND ( _atr, 1 ) <= 1 && ROUND ( _atr, 1 ) >= -1, \"mês\", \"meses\" ) )",
        "VAR _txtCtx = IF ( ISBLANK ( _atr ), \"sem curva prevista\", " + marca_item("_ptf", "_psf", 450)
        + " & \"término \" & FORMAT ( _term, \"mmm/yy\", \"pt-BR\" ) & \" · \" & " + C.marca("_teTxt") + " & \" exec.\" )",
        # faixas do item (texto do modelo): "atraso ≤ 0,5 mês → 2 · … · atraso > 3 meses → 0"; na régua do verso sai
        # a palavra "atraso" (F4: as duas faixas com as marcas passavam dos 262 da linha e eram cortadas)
        f"VAR _fx = {FX_FF}",
        "VAR _fx1 = SUBSTITUTE ( PATHITEM ( _fx, 1 ), \"atraso \", \"\" )",
        "VAR _fx2c = SUBSTITUTE ( PATHITEM ( _fx, PATHLENGTH ( _fx ) ), \"atraso \", \"\" )"],
    "_taOd", "_txtLado", "_txtCtx",
    "Meses atrás do cronograma: o executado de hoje é o previsto de quando.", "Planilha e cronograma",
    [("mk0", "=" + faixa_html("_fx1")), ("mk2", "=" + faixa_html("_fx2c"))],
    anima=D.od_num("_atr", "_ta"),
    desc="Cartão de prazo da obra em foco: atraso em meses (cronograma agregado), término projetado e o executado "
         "acumulado, com a marca e a régua do item prazo da nota. Só lê contas · foco.")

# ======================================================================================================== o quadradinho
QUAD = r"T2 Análise crítica\O quadradinho"
CSS_QUAD = (
    # entradas (caixa offwhite do topo, 548 × 108): duas colunas de rótulo + valor, linhas de 21
    ".qe{position:fixed;inset:0;background:#F7F4EE;border-radius:6px;display:grid;grid-template-columns:254px 238px;"
    "column-gap:24px;padding:12px 16px 0;align-content:start}"
    ".qe .l{display:flex;justify-content:space-between;height:21px;font-size:15px;line-height:21px;white-space:nowrap}"
    ".qe .l span:first-child{color:#3B3B3F}"
    ".qe .l b{font-weight:600;font-variant-numeric:tabular-nums}"
    # itens (uma entrada por item, linhas de 30)
    "#htmlContent{padding:0!important}"
    ".htmlViewerEntry{display:block!important;margin:0!important;padding:0!important}"
    ".qi{position:relative;height:30px;border-bottom:1px solid #E1E1E1;white-space:nowrap}"
    ".qi .n{position:absolute;left:12px;top:7px;font-size:13px;line-height:16px;color:#6B6B70}"
    ".qi .s{position:absolute;left:38px;top:4px;font-size:15px;line-height:21px;font-weight:600}"
    ".qi .r{position:absolute;left:58px;top:4px;font-size:15px;line-height:21px}"
    ".qi .v{position:absolute;right:102px;top:5px;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;"
    "font-size:16px;line-height:20px;font-variant-numeric:tabular-nums}"
    ".qi .p{position:absolute;right:12px;top:5px;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;"
    "font-size:16px;line-height:20px;color:#3B3B3F;font-variant-numeric:tabular-nums}"
    ".qi.zero .r,.qi.zero .v{color:#6B6B70;opacity:.75}.qi.zero .s{opacity:.45}.qi.zero .p{opacity:.6}"
    ".qi:hover{background:rgba(233,224,207,.35)}"
    # resultado do mês (faixa preta 44) e do mês anterior (creme 40), 4 px entre elas
    ".qr{position:fixed;inset:0}"
    ".qr .f{position:absolute;left:0;right:0;display:flex;align-items:center;padding:0 16px;border-radius:4px;"
    "white-space:nowrap}"
    ".qr .f1{top:0;height:44px;background:#0B0B0C;color:#FFFFFF}"
    ".qr .f2{top:48px;height:40px;background:#E9E0CF;color:#0B0B0C}"
    ".qr .f span{flex:1;font-size:15px;line-height:21px}.qr .f1 span{font-weight:600}"
    ".qr .f b{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;width:170px;margin-right:16px;"
    "text-align:right;font-variant-numeric:tabular-nums}"
    ".qr .f1 b{font-size:21px;line-height:26px}.qr .f2 b{font-size:16px;line-height:20px}"
    ".qr .f em{font-style:normal;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:16px;"
    "line-height:20px;width:70px;text-align:right;font-variant-numeric:tabular-nums}"
)
m("T2 · Quadradinho · CSS", QUAD, "CSS do quadradinho v2: entradas, itens (uma entrada por item) e as duas faixas do "
  "resultado.", "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(CSS_QUAD))

m("T2 · Quadradinho · HTML entradas", QUAD,
  "Caixa offwhite do topo do quadradinho: projeto, orçamento, tipo, mês e aba; % previsto e executado no mês e "
  "acumulados (A132:J136 da aba). Só lê contas · foco.",
  linhas(
      "-- 1 · Leituras",
      "VAR _obra = [Nota · obra em foco]",
      "VAR _cod = [Obra · código · foco]",
      "VAR _orc = [Orçamento · foco]",
      "VAR _tipo = [Tipo de orçamento · foco]",
      "VAR _mesC = [Mês de referência · curto]",
      "VAR _aba = [Aba · foco]",
      "VAR _pm = [Físico · previsto no mês · foco]",
      "VAR _em = [Físico · executado no mês · foco]",
      "VAR _pa = [Físico · previsto acumulado · foco]",
      "VAR _ea = [Físico · executado acumulado · foco]",
      "-- 2 · Textos",
      D.rs_cheio("_orc", "_to"),
      D.pct("_pm", "_t1", casas=2), D.pct("_em", "_t2", casas=2), D.pct("_pa", "_t3", casas=2), D.pct("_ea", "_t4", casas=2),
      "VAR _txtTipo = IF ( _tipo = \"\", \"—\", \"Orçamento \" & _tipo )",
      "-- 4 · Marcação",
      "VAR _lin = \"<div class='l'><span>\"",
      "RETURN",
      "    IF (",
      "        NOT ISBLANK ( _orc ),",
      "        \"<div class='u qe'><div>\"",
      "            & _lin & \"Projeto</span><b>\" & " + D.esc("_obra") + " & \" · \" & _cod & \"</b></div>\"",
      "            & _lin & \"Orçamento</span><b>\" & _toTxt & \"</b></div>\"",
      "            & _lin & \"Tipo</span><b>\" & _txtTipo & \"</b></div>\"",
      "            & _lin & \"Mês · aba</span><b>\" & _mesC & \" · \" & _aba & \"</b></div>\"",
      "        & \"</div><div>\"",
      "            & _lin & \"% previsto no mês</span><b>\" & _t1Txt & \"</b></div>\"",
      "            & _lin & \"% executado no mês</span><b>\" & _t2Txt & \"</b></div>\"",
      "            & _lin & \"% previsto acumulado</span><b>\" & _t3Txt & \"</b></div>\"",
      "            & _lin & \"% executado acumulado</span><b>\" & _t4Txt & \"</b></div>\"",
      "        & \"</div></div>\"",
      "    )",
  ))

m("T2 · Quadradinho · HTML item", QUAD,
  "Uma linha por item do quadradinho (granularidade dItem, na ordem do bloco A132:J157): número, sinal da conta (o "
  "\"−\" em vermelho), rótulo, valor como a planilha imprime (centavos) e % do orçamento; item zerado em cinza. O "
  "mouse abre o tooltip do item.",
  linhas(
      "-- 1 · Leituras",
      "VAR _ordem = SELECTEDVALUE ( dItem[Ordem] )",
      "VAR _rot = SELECTEDVALUE ( dItem[Rotulo] )",
      "VAR _sinal = SELECTEDVALUE ( dItem[Sinal] )",
      "VAR _v = [Item · valor · foco]",
      "VAR _p = [Item · % do orçamento · foco]",
      "VAR _temObra = NOT ISBLANK ( [Orçamento · foco] )",
      "-- 2 · Textos",
      D.rs_cheio("_v", "_tv", vazio="R$ 0,00"),
      D.pct("_p", "_tp", casas=2, vazio="0,00%"),
      "VAR _zero = ISBLANK ( _v ) || _v = 0",
      "-- 4 · Marcação",
      "RETURN",
      "    IF (",
      "        _temObra && NOT ISBLANK ( _ordem ),",
      "        \"<div class='u qi\" & IF ( _zero, \" zero\", \"\" ) & \"'>\"",
      "            & \"<span class='n'>\" & FORMAT ( _ordem, \"00\" ) & \"</span>\"",
      "            & IF ( _sinal < 0, \"<span class='s ng'>" + MENOS + "</span>\", \"<span class='s'>+</span>\" )",
      "            & \"<span class='r'>\" & _rot & \"</span>\"",
      "            & \"<span class='v'>\" & _tvTxt & \"</span><span class='p'>\" & _tpTxt & \"</span>\"",
      "        & \"</div>\"",
      "    )",
  ))

m("T2 · Quadradinho · HTML resultado", QUAD,
  "As duas faixas do fim do quadradinho: resultado mensal da obra (preta, D155 e E155; negativo em vermelho sobre "
  "preto) e resultado do mês anterior (creme, D156 e E156), em centavos como a planilha.",
  linhas(
      "-- 1 · Leituras",
      "VAR _res = [Resultado da obra · foco]",
      "VAR _pct = [Resultado % · foco]",
      "VAR _ant = [Resultado · mês anterior · foco]",
      "VAR _pa = [Resultado % · mês anterior · foco]",
      "VAR _mesAnt = [Mês anterior à referência · curto]",
      "-- 2 · Textos",
      D.rs_cheio("_res", "_tr"), D.pct("_pct", "_tp", casas=2, mais=True),
      D.rs_cheio("_ant", "_ta"), D.pct("_pa", "_tpa", casas=2, mais=True),
      "-- 4 · Marcação",
      "RETURN",
      "    IF (",
      "        NOT ISBLANK ( _res ),",
      "        \"<div class='u qr'><div class='f f1 sobre-preto'><span>Resultado mensal da obra</span>\"",
      f"            & \"<b class='tn{ng('_tr')}'>\" & _trTxt & \"</b><em class='tn{ng('_tp')}'>\" & _tpTxt & \"</em></div>\"",
      "        & \"<div class='f f2 sobre-creme'><span>Resultado do mês anterior\" & IF ( _mesAnt = \"\", \"\", \" · \" & _mesAnt )",
      f"            & \"</span><b class='tn{ng('_ta')}'>\" & _taTxt & \"</b><em class='tn{ng('_tpa')}'>\"",
      "            & IF ( ISBLANK ( _ant ), \"\", _tpaTxt ) & \"</em></div></div>\"",
      "    )",
  ))

# ======================================================================================================== desembolso do mês
DES = r"T2 Análise crítica\Desembolso do mês"
CSS_DES = (
    # miolo do painel (372 × 271, a partir do y +68 do painel): 2 × 2 números, barras previsto × desembolsado e a
    # caixa da justificativa. O desvio e a diferença negativos (gastou menos que o previsto) ficam em preto
    ".dm{position:fixed;inset:0}"
    ".dm .c{position:absolute;width:186px}"
    ".dm .c .vs{display:flex;align-items:center;gap:6px}"
    ".dm .c .vs i{display:block;width:10px;height:10px;flex:none}"
    ".dm .c .vs i.pv{background:#E9E0CF;box-shadow:inset 0 0 0 1px #E1E1E1}.dm .c .vs i.dv{background:#0B0B0C}"
    ".dm .c b{display:flex;align-items:center;gap:7px;margin-top:4px;font-family:'Barlow U','Segoe UI',sans-serif;"
    "font-weight:600;font-size:21px;line-height:26px;white-space:nowrap;font-variant-numeric:tabular-nums}"
    ".dm .br{position:absolute;left:0;height:10px}"
    ".dm .br.pv{background:#E9E0CF}.dm .br.dv{background:#0B0B0C}"
    ".dm .js{position:absolute;left:0;right:0;top:156px;bottom:0;background:#F7F4EE;border-radius:6px;padding:16px}"
    ".dm .js .vs{display:block}"
    ".dm .js p{margin-top:8px;font-size:15px;line-height:21px;color:#3B3B3F;display:-webkit-box;-webkit-line-clamp:3;"
    "-webkit-box-orient:vertical;overflow:hidden}"
)
m("T2 · Desembolso · CSS", DES, "CSS do bloco Desembolso do mês v2.", "-- 4 · Marcação\n[Comum · CSS base]\n    & "
  + dax_lit(CSS_DES))
m("T2 · Desembolso · HTML", DES,
  "Desembolso do mês da obra em foco: previsto e desembolsado (com as barras creme × preta na mesma escala), diferença "
  "e × previsto com a marca dos pontos da previsão de caixa na nota (cheio, parcial ou zero, pelas faixas do item) e os "
  "pontos ao lado do rótulo, e a justificativa da planilha (exigida acima de ±10%; em branco vira "
  "aviso). Desvio e diferença negativos ficam em preto (decisão do Alisson).",
  linhas(
      "-- 1 · Leituras",
      "VAR _prev = [Desembolso · previsto no mês · foco]",
      "VAR _real = [Desembolso · realizado no mês · foco]",
      "VAR _dif = [Desembolso · diferença no mês · foco]",
      "VAR _desv = [Desembolso · desvio no mês · foco]",
      "VAR _ptx = [Nota · pontos caixa · foco]",
      "VAR _psx = [Nota · possíveis · caixa · foco]",
      "VAR _exig = [Justificativa · exigida · foco]",
      "VAR _branco = [Justificativa · em branco · foco]",
      "VAR _just = [Justificativa do desembolso · foco]",
      "-- 2 · Textos",
      D.rs("_prev", "_tp") + D.rs("_real", "_tr") + D.rs("_dif", "_td", mais=True) + D.pct("_desv", "_tv", casas=0, mais=True),
      item_txt_m("_ti", "_ptx", "_psx", fonte="ac"),
      D.od_tabela(), D.od_rs("_prev", "_tp"), D.od_rs("_real", "_tr"), D.od_rs("_dif", "_td"), D.od_pct("_desv", "_tv"),
      "VAR _txtRot = IF ( _exig = 1, \"Justificativa · exigida acima de ±10%\", \"Justificativa · não exigida (dentro de ±10%)\" )",
      "VAR _txtJust =",
      "    SWITCH (",
      "        TRUE (),",
      "        _branco = 1, \"Em branco: a planilha não traz a justificativa exigida.\",",
      "        TRIM ( _just ) = \"\", \"Sem justificativa na planilha.\",",
      "        " + D.esc("TRIM ( _just )"),
      "    )",
      "-- 3 · Geometria",
      "VAR _maior = MAX ( ABS ( _prev ), ABS ( _real ) ) -- geometria",
      "VAR _wP = IF ( ISBLANK ( _prev ), 0, MAX ( ROUND ( DIVIDE ( ABS ( _prev ), _maior ) * 372, 0 ), 2 ) ) -- geometria",
      "VAR _wR = IF ( ISBLANK ( _real ), 0, MAX ( ROUND ( DIVIDE ( ABS ( _real ), _maior ) * 372, 0 ), 2 ) ) -- geometria",
      "-- 4 · Marcação",
      "RETURN",
      "    IF (",
      "        NOT ISBLANK ( _prev ) || NOT ISBLANK ( _real ),",
      "        \"<div class='u dm'>\"",
      "            & \"<div class='c' style='left:0;top:0'><span class='vs'><i class='pv a-pop'></i>Previsto</span><b>\" & _tpOd & \"</b></div>\"",
      "            & \"<div class='c' style='left:186px;top:0'><span class='vs'><i class='dv a-pop' style='animation-delay:90ms'></i>Desembolsado</span><b>\" & _trOd"
      " & \"</b></div>\"",
      "            & \"<i class='br pv' style='top:55px;width:\" & _wP & \"px' data-rk='dp' data-rp='width'></i>\"",
      "            & \"<i class='br dv' style='top:69px;width:\" & _wR & \"px' data-rk='dr' data-rp='width' data-rd='90'></i>\"",
      "            & \"<div class='c' style='left:0;top:95px'><span class='vs'>Diferença</span><b>\" & _tdOd & \"</b></div>\"",
      "            & \"<div class='c' style='left:186px;top:95px'><span class='vs'>× previsto\" & IF ( ISBLANK ( _ptx ), \"\", \" · <span>\" & _tiTxt & \"</span>\" ) & \"</span><b>\" & "
      + marca_item("_ptx", "_psx", 700) + " & \"<span>\" & _tvOd & \"</span></b></div>\"",
      "            & \"<div class='js'><span class='vs'>\" & _txtRot & \"</span><p>\" & _txtJust & \"</p></div>\"",
      "        & \"</div>\" & [Comum · JS contador] & [Comum · JS corrida]",
      "    )",
  ))

# ======================================================================================================== cascata
CAS = r"T2 Análise crítica\Como o resultado se forma"
CSS_CAS = (
    # uma coluna por degrau (508 ÷ n), barra de 56 no centro; escala de y 20 (topo do maior nível) a 218 (fundo do
    # menor); rótulo do valor 3 px acima do topo (o resultado negativo, 4 px abaixo); nome do degrau em y 249
    "#htmlContent{display:flex!important;align-items:flex-start;width:100vw;height:100vh;padding:0!important}"
    ".htmlViewerEntry{display:block!important;flex:1 1 0;min-width:0;margin:0!important;padding:0!important}"
    ".cd{position:relative;height:282px}"
    ".cd .b{position:absolute;left:calc(50% - 28px);width:56px}"
    ".cd .b.k2{background:#0B0B0C}"
    ".cd .b.kd{background:#F7E3E3;box-shadow:inset 0 0 0 1px #C43737}"
    ".cd .b.kn{background:#C43737}"
    # a realizar: o que a planilha conta e ainda não aconteceu (hachura)
    ".cd .b.kr{background:repeating-linear-gradient(135deg,#0B0B0C 0 2px,#FFFFFF 2px 6px);box-shadow:inset 0 0 0 1px #0B0B0C}"
    ".cd .lg{position:absolute;left:calc(50% + 28px);width:calc(100% - 56px);height:1px;background:rgba(59,59,63,.5)}"
    ".cd .z{position:absolute;left:0;right:0;height:1px;background:rgba(59,59,63,.6)}"
    ".cd .v{position:absolute;left:-10px;right:-10px;text-align:center;font-family:'Barlow U','Segoe UI',sans-serif;"
    "font-weight:600;font-size:14px;line-height:17px;white-space:nowrap;font-variant-numeric:tabular-nums}"
    ".cd .n{position:absolute;left:0;right:0;top:249px;text-align:center;font-size:13px;line-height:16px;color:#3B3B3F}"
    ".cd:hover .b{filter:brightness(.94)}"
)
m("T2 · Cascata · CSS", CAS, "CSS da cascata v2 (uma entrada por degrau, colunas iguais).",
  "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(CSS_CAS))
m("T2 · Cascata · HTML degrau", CAS,
  "Um degrau da cascata por entrada (granularidade dDegrau): valor agregado em preto (soma), custo aplicado em "
  "vermelho-claro com contorno vermelho (desconta), resultado aplicado, a realizar hachurado (o que a planilha conta e "
  "ainda não aconteceu) e o resultado da planilha (resultados em preto; vermelho quando negativos). A barra vai da base ao topo do degrau na mesma escala (y 20–218); a "
  "ligação leva o nível ao próximo degrau; o zero atravessa as colunas. O mouse abre o tooltip do degrau.",
  linhas(
      "-- 1 · Leituras",
      "VAR _deg = SELECTEDVALUE ( dDegrau[Degrau] )",
      "VAR _ordem = SELECTEDVALUE ( dDegrau[Ordem] )",
      "VAR _rot = SELECTEDVALUE ( dDegrau[Rotulo] )",
      "VAR _sinal = SELECTEDVALUE ( dDegrau[Sinal] )",
      "VAR _aparece = [Cascata · degrau · aparece · foco]",
      "VAR _v = [Cascata · degrau · valor · foco]",
      "VAR _base = [Cascata · degrau · base · foco]",
      "VAR _topo = [Cascata · degrau · topo · foco]",
      "VAR _max = [Cascata · escala · máximo · foco]",
      "VAR _min = [Cascata · escala · mínimo · foco]",
      "-- 2 · Textos",
      D.rs("_v", "_tv"),
      "VAR _sinalTxt = SWITCH ( TRUE (), _sinal > 0, \"+\", _sinal < 0, \"" + MENOS + "\", \"\" )",
      "VAR _txtV = IF ( _sinal = 0 || _tvZero, _tvTxt, _sinalTxt & SUBSTITUTE ( _tvTxt, \"" + MENOS + "\", \"\" ) )",
      "VAR _vermelho = IF ( _sinal = 0, _v < 0, _sinal < 0 && NOT _tvZero )",
      "VAR _txtRot =",
      "    SWITCH (",
      "        _deg,",
      "        \"ValorAgregado\", \"Valor<br>agregado\",",
      "        \"CustoAplicado\", \"Custo<br>aplicado\",",
      "        \"ResultadoAplicado\", \"Resultado<br>aplicado\",",
      "        \"ARealizar\", \"A realizar\",",
      "        \"Resultado\", \"Resultado da<br>planilha\",",
      "        _rot",
      "    )",
      # resultados (sinal 0) em preto, vermelho quando negativos; custo (desconta) em vermelho-claro; a realizar
      # (ainda não aconteceu) hachurado
      "VAR _cls = SWITCH ( TRUE (), _sinal = 0, IF ( _v < 0, \"kn\", \"k2\" ), _sinal < 0, \"kd\", _deg = \"ARealizar\", \"kr\", \"k2\" )",
      "-- 3 · Geometria",
      "VAR _faixa = _max - _min -- geometria",
      "VAR _yTopo = 20 + ROUND ( DIVIDE ( _max - _topo, _faixa ) * 198, 0 ) -- geometria",
      "VAR _yBase = 20 + ROUND ( DIVIDE ( _max - _base, _faixa ) * 198, 0 ) -- geometria",
      "VAR _h = MAX ( _yBase - _yTopo, 2 ) -- geometria",
      "VAR _yZero = 20 + ROUND ( DIVIDE ( _max, _faixa ) * 198, 0 ) -- geometria",
      "VAR _yLig = IF ( _sinal < 0, _yBase, _yTopo ) -- geometria",
      "VAR _yRot = IF ( _sinal = 0 && _v < 0, _yTopo + _h + 4, _yTopo - 20 ) -- geometria",
      "VAR _atraso = ( _ordem - 1 ) * 110 -- geometria",
      "-- 4 · Marcação",
      "RETURN",
      "    IF (",
      "        _aparece = 1 && NOT ISBLANK ( _max ),",
      "        \"<div class='u cd'>\"",
      "            & \"<i class='b \" & _cls & \"' style='top:\" & _yTopo & \"px;height:\" & _h & \"px' data-rk='\" & _deg"
      " & \"' data-rp='top,height' data-r0-top='\" & _yLig & \"px' data-r0-height='0px' data-rd='\" & _atraso & \"'></i>\"",
      # F4: o zero atravessa as colunas crescendo da esquerda na cascata dos degraus; a ligação ao próximo degrau
      # cresce depois da barra; o nome do degrau aparece com ela; o valor conta
      "            & \"<i class='z a-gx' style='top:\" & _yZero & \"px;animation-delay:\" & _atraso & \"ms'></i>\"",
      "            & IF ( _deg <> \"Resultado\", \"<i class='lg a-gx' style='top:\" & IF ( _sinal = 0, IF ( _v < 0, _yBase, _yTopo ), _yLig ) "
      "& \"px;animation-delay:\" & ( _atraso + 600 ) & \"ms'></i>\", \"\" )",
      "            & \"<span class='v\" & IF ( _vermelho, \" ng\", \"\" ) & \"' style='top:\" & _yRot & \"px'>\" & " + C.marca("_txtV") + " & \"</span>\"",
      "            & \"<span class='n a-fd' style='animation-delay:\" & _atraso & \"ms'>\" & _txtRot & \"</span>\"",
      "        & \"</div>\" & [Comum · JS contador] & [Comum · JS corrida]",
      "    )",
  ))

# ======================================================================================================== IDC mês a mês
# F3 (docs/08 §5): o painel "Resultado da obra, mês a mês" virou o IDC da obra em foco, uma série só (os R$ ficam no
# tooltip do mês). Janela de 1 a 12 meses (drawer, dJanela), colunas iguais (flex) num contêiner de 508 com 20 de
# margem à direita. Escala de y 20 a 236 entre o menor valor (o menor IDC ou a trava, menos 0,02) e o maior (o maior
# IDC ou 1,00, mais 0,02). Cada mês é uma barra que sai da linha de 1,00 até o IDC: sálvia acima, ocre entre 1,00 e a
# trava, vermelha abaixo da trava. Linha cheia em 1,00 e tracejada vermelha na trava, atravessando as colunas. Rótulo
# (Barlow 14) no mês de referência, no maior e no menor IDC; eixo em y 265 como no resto do painel.
MES = r"T2 Análise crítica\IDC, mês a mês"
HALO = ("text-shadow:1px 0 0 #FFF,-1px 0 0 #FFF,0 1px 0 #FFF,0 -1px 0 #FFF,1px 1px 0 #FFF,-1px -1px 0 #FFF,"
        "1px -1px 0 #FFF,-1px 1px 0 #FFF,0 0 3px #FFF")
CSS_MES = (
    "#htmlContent{display:flex!important;align-items:flex-start;width:100vw;height:100vh;margin:0!important;"
    "padding:0 20px 0 0!important;box-sizing:border-box!important}"
    ".htmlViewerEntry{display:block!important;flex:1 1 0;min-width:0;margin:0!important;padding:0!important}"
    ".mm{position:relative;height:281px}"
    ".mm .l1{position:absolute;left:0;right:0;height:0;border-top:1px solid #0B0B0C}"
    ".mm .l9{position:absolute;left:0;right:0;height:0;border-top:1px dashed #C43737}"
    ".mm .b{position:absolute;left:calc(50% - 9px);width:18px}"
    ".mm .b.q0{background:#A9CDB9}.mm .b.q1{background:#C9821F}.mm .b.q2{background:#C43737}"
    ".mm .v{position:absolute;left:-30px;right:-30px;text-align:center;font-family:'Barlow U','Segoe UI',sans-serif;"
    f"font-weight:600;font-size:14px;line-height:17px;white-space:nowrap;font-variant-numeric:tabular-nums;color:#0B0B0C;{HALO}}}"
    ".mm .v.ng{color:#C43737}"
    ".mm .ms{position:absolute;left:-12px;right:-12px;top:265px;text-align:center;font-size:13px;line-height:16px;"
    "white-space:nowrap;color:#3B3B3F}"
    ".mm .ms.ref{font-weight:600;color:#0B0B0C}.mm .ms.sem{opacity:.35}"
    ".mm:hover .b{filter:brightness(.92)}"
    ".ms2{position:fixed;inset:0;font-size:15px;line-height:20px;color:#3B3B3F;white-space:nowrap}"
)
m("T2 · Mês a mês · CSS", MES, "CSS do IDC mês a mês (uma entrada por mês da janela; colunas iguais) e do subtítulo.",
  "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(CSS_MES))

m("T2 · Mês a mês · HTML subtítulo", MES,
  "Subtítulo do IDC mês a mês com a régua e a janela em uso: linha cheia em 1,00, tracejada na trava · jan–set/26 (um "
  "mês só: set/26). Os limites vêm das medidas Nota · limite custo · ….",
  linhas(
      "-- 1 · Leituras",
      "VAR _ini = [Série · primeiro mês]",
      "VAR _ref = [Mês de referência]",
      "VAR _n = [Série · meses até a referência]",
      "VAR _cheio = [Nota · limite custo · ponto cheio]",
      "VAR _trv = [Nota · limite custo · trava]",
      "-- 2 · Textos",
      "VAR _txtRef = FORMAT ( _ref, \"mmm/yy\", \"pt-BR\" )",
      "VAR _txtIni = IF ( YEAR ( _ini ) = YEAR ( _ref ), FORMAT ( _ini, \"mmm\", \"pt-BR\" ), FORMAT ( _ini, \"mmm/yy\", \"pt-BR\" ) )",
      "VAR _txtJanela = IF ( _n <= 1, _txtRef, _txtIni & \"–\" & _txtRef )",
      "VAR _txt = \"linha em \" & " + C.marca('FORMAT ( _cheio, "0.00", "pt-BR" )') + " & \" · tracejado na trava, \" "
      "& " + C.marca('FORMAT ( _trv, "0.00", "pt-BR" )') + " & \" · \" & _txtJanela",
      "-- 4 · Marcação",
      "RETURN",
      "    IF ( NOT ISBLANK ( _ref ), \"<p class='u ms2'>\" & _txt & \"</p>\" & [Comum · JS contador] )",
  ))

m("T2 · Mês a mês · HTML coluna", MES,
  "IDC mês a mês da obra em foco: uma entrada por mês da janela (granularidade dMes, colunas iguais), com a barra da "
  "linha de 1,00 até o IDC (sálvia acima, ocre entre 1,00 e a trava, vermelha abaixo dela), as linhas de 1,00 e da "
  "trava atravessando as colunas, o rótulo no mês de referência e no maior e no menor IDC, e o mês no eixo (com mais "
  "de oito meses, só a sigla; o ano no primeiro mês e em janeiro). Mês sem aba: só o rótulo do mês, apagado. O mouse "
  "abre o tooltip do mês (os valores em R$).",
  linhas(
      "-- 1 · Leituras",
      "VAR _noRecorte = [Série · mês até a referência]",
      "VAR _n = [Série · meses até a referência]",
      "VAR _pos = [Série · posição na janela]",
      "VAR _mesAno = [Mês · rótulo curto]",
      "VAR _mesAbrev = [Mês · abreviado]",
      "VAR _ehRef = [Série · é o mês de referência]",
      "VAR _idc = [IDC · foco no mês]",
      "VAR _max = [T2 · IDC · máximo na janela]",
      "VAR _min = [T2 · IDC · mínimo na janela]",
      "VAR _extremo = [T2 · IDC · mês com rótulo]",
      "VAR _cheio = [Nota · limite custo · ponto cheio]",
      "VAR _trv = [Nota · limite custo · trava]",
      "-- 3 · Geometria",
      "VAR _hi = MAX ( _max, _cheio ) + 0.02 -- geometria",
      "VAR _lo = MIN ( _min, _trv ) - 0.02 -- geometria",
      "VAR _k = DIVIDE ( 216, _hi - _lo ) -- geometria",
      "VAR _y1 = 20 + ROUND ( ( _hi - _cheio ) * _k, 0 ) -- geometria",
      "VAR _y9 = 20 + ROUND ( ( _hi - _trv ) * _k, 0 ) -- geometria",
      "VAR _yV = 20 + ROUND ( ( _hi - _idc ) * _k, 0 ) -- geometria",
      "VAR _yTop = MIN ( _y1, _yV ) -- geometria",
      "VAR _h = MAX ( ABS ( _yV - _y1 ), 2 ) -- geometria",
      "VAR _yRot = IF ( _idc >= _cheio, _yTop - 20, _yTop + _h + 3 ) -- geometria",
      "VAR _atraso = ( _pos - 1 ) * ROUND ( DIVIDE ( 420, _n ), 0 ) -- geometria",
      "-- 2 · Textos",
      "VAR _cls = SWITCH ( TRUE (), ISBLANK ( _idc ), \"\", ROUND ( _idc, 2 ) >= _cheio, \"q0\", ROUND ( _idc, 2 ) >= _trv, \"q1\", \"q2\" )",
      "VAR _rotula = NOT ISBLANK ( _idc ) && ( _ehRef = 1 || _extremo = 1 || _n <= 6 )",
      "VAR _txtV = FORMAT ( _idc, \"0.00\", \"pt-BR\" )",
      "VAR _comAno = _n <= 8 || _pos = 1 || _mesAbrev = \"jan\"",
      "VAR _rotMes = IF ( _comAno, _mesAno, _mesAbrev )",
      "-- 4 · Marcação",
      "RETURN",
      "    IF (",
      "        _noRecorte = 1 && NOT ISBLANK ( _max ),",
      "        \"<div class='u mm'>\"",
      # F4: as linhas de 1,00 e da trava atravessam as colunas crescendo da esquerda, na cascata das barras
      "            & \"<i class='l1 a-gx' style='top:\" & _y1 & \"px;animation-delay:\" & _atraso & \"ms'></i>\"",
      "            & \"<i class='l9 a-gx' style='top:\" & _y9 & \"px;animation-delay:\" & _atraso & \"ms'></i>\"",
      "            & IF ( ISBLANK ( _idc ), \"\", \"<i class='b \" & _cls & \"' style='top:\" & _yTop & \"px;height:\" & _h"
      " & \"px' data-rk='m\" & _pos & \"' data-rp='top,height' data-r0-top='\" & _y1 & \"px' data-r0-height='0px' data-rd='\" & _atraso & \"'></i>\" )",
      "            & IF ( _rotula, \"<span class='v\" & IF ( _cls = \"q2\", \" ng\", \"\" ) & \"' style='top:\" & _yRot & \"px'>\" & " + C.marca("_txtV") + " & \"</span>\" )",
      "            & \"<span class='ms a-fd\" & IF ( _ehRef = 1, \" ref\", IF ( ISBLANK ( _idc ), \" sem\", \"\" ) ) & \"' style='animation-delay:\" & _atraso "
      "& \"ms'>\" & _rotMes & \"</span>\"",
      "        & \"</div>\" & [Comum · JS contador] & [Comum · JS corrida]",
      "    )",
  ))


def x_item(cod: str, x: str, fx: str, pts: str, marcar: bool = False) -> list[str]:
    """VAR _txtX: o X de um item da nota na unidade dele, em <b> (vazio sem dado): IDC com 2 casas (vermelho abaixo de
    1); atraso em meses (em palavras: atraso, adiantada, em dia); PPC, caixa, inspeção, NR-18 e entregas em %; a taxa de
    frequência (TF); as checagens da análise crítica (3 de 3). `marcar` (telas, F4): o número vai marcado para o
    odômetro; sem ele (tooltips_t2, que marca o texto inteiro), sem marca, para não aninhar marcas."""
    mk = C.marca if marcar else (lambda e: e)
    return [
        f"VAR _xA1 = ROUND ( ABS ( {x} ) * 100, 1 )",
        # % sempre com uma casa (retorno de 28/10/2026: "3%" ao lado de "3,1%")
        "VAR _xPct = " + mk('FORMAT ( _xA1, "0.0", "pt-BR" )') + " & \"%\"",
        "VAR _xMes = " + mk(f'FORMAT ( ABS ( {x} ), "0.0", "pt-BR" )')
        + f" & IF ( ROUND ( ABS ( {x} ), 1 ) <= 1, \" mês\", \" meses\" )",
        "VAR _txtX =",
        "    SWITCH (",
        "        TRUE (),",
        f"        ISBLANK ( {pts} ), \"\",",
        f"        {cod} = \"custo\", \"<b class='\" & IF ( {x} < 1, \"ng\", \"\" ) & \"'>IDC \" & "
        + mk(f'FORMAT ( {x}, "0.00", "pt-BR" )') + " & \"</b>\",",
        f"        {cod} = \"prazo\",",
        f"            \"<b>\" & IF ( ROUND ( {x}, 1 ) > 0, \"atraso de \" & _xMes, IF ( ROUND ( {x}, 1 ) < 0, \"adiantada \" & _xMes, \"em dia\" ) ) & \"</b>\",",
        f"        {cod} = \"acidentes\", \"<b>TF \" & " + mk(f'FORMAT ( {x}, "0.0", "pt-BR" )') + " & \"</b>\",",
        f"        {cod} = \"analise\", \"<b>\" & " + mk(f'FORMAT ( {x}, "0" )') + " & \" de 3 checagens</b>\",",
        "        \"<b>\" & _xPct & \"</b>\"",
        "    )",
    ]


# ======================================================================================================== itens da nota
# F3 (docs/08 §5): Itens da nota ganha o espaço do quadradinho (548 de largura, painel 352,273 até o pé): nove linhas
# de 76 a partir de y 68 do painel (eixo dItemNota, ordem T2 · Itens · posição: quem mais perde primeiro). Cada linha:
# nome do item (Segoe SB 15) e o chip de pontos de possíveis (DC.chip_item) à direita; embaixo, o X (Barlow SB 14) e a
# faixa atingida (Segoe 13 grafite); à direita, a minissérie dos meses da janela (até 12 barras de ITN_BW px, altura
# pela fração dos pontos, cor cheio/parcial/zero; mês sem dado só o traço) com o mês de referência em preto.
# Item sem dado: "falta na base" (base complementar) ou "sem dado na planilha" (Análise Crítica) e quanto o item vale.
ITN = r"T2 Análise crítica\Itens da nota"
ITN_H, ITN_BW, ITN_GAP, ITN_SH = 76, 9, 3, 26     # linha, barra da minissérie, vão e altura da minissérie
ITN_SW = 12 * ITN_BW + 11 * ITN_GAP               # 141: largura da minissérie com 12 meses
CSS_ITN = (
    "#htmlContent{padding:0!important}"
    ".htmlViewerEntry{display:block!important;margin:0!important;padding:0!important}"
    f".it{{position:relative;height:{ITN_H}px;border-bottom:1px solid #E1E1E1;white-space:nowrap}}"
    ".it .nm{position:absolute;left:0;top:12px;font-size:15px;line-height:19px;font-weight:600}"
    f".it .ln{{position:absolute;left:0;right:{ITN_SW + 24}px;top:40px;display:flex;align-items:baseline;gap:10px;"
    "overflow:hidden}"
    ".it .ln b{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:14px;line-height:17px;"
    "font-variant-numeric:tabular-nums}"
    ".it .ln span{font-size:13px;line-height:17px;color:#3B3B3F;overflow:hidden;text-overflow:ellipsis}"
    ".it .chi{position:absolute;right:0;top:11px}"
    f".it .sr{{position:absolute;right:0;top:40px;width:{ITN_SW}px;height:{ITN_SH}px}}"
    f".it .sr i{{position:absolute;bottom:0;width:{ITN_BW}px}}"
    ".it .sr i.c{background:#A9CDB9}.it .sr i.p{background:#C9821F}.it .sr i.z{background:#C43737}"
    ".it .sr i.v{height:1px!important;background:#CFCCC6}"
    ".it .sr i.r{outline:1px solid #0B0B0C;outline-offset:1px}"
    ".it:hover{background:rgba(233,224,207,.3)}"
    ".ss{position:fixed;inset:0;font-size:15px;line-height:20px;color:#3B3B3F;white-space:nowrap}"
)
m("T2 · Itens · CSS", ITN, f"CSS de Itens da nota (uma entrada por item, linhas de {ITN_H}, minissérie à direita) e do "
  "subtítulo.", "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(CSS_ITN))
m("T2 · Itens · HTML subtítulo", ITN,
  "Subtítulo de Itens da nota: diz a ordem das linhas (quem mais perde pontos primeiro) e o que a minissérie mostra. O "
  "total perdido já está no cartão Nota da obra e não se repete aqui.",
  linhas(
      "-- 1 · Leituras",
      "VAR _po = [Nota · pontos possíveis · ranking · foco]",
      "-- 4 · Marcação",
      "RETURN",
      "    IF ( NOT ISBLANK ( _po ), \"<p class='u ss'>pontos de cada item, quem mais perde primeiro · à direita, "
      "os pontos mês a mês</p>\" )",
  ))
m("T2 · Itens · HTML linha", ITN,
  "Um item da nota por entrada (granularidade dItemNota, na ordem de T2 · Itens · posição): nome, o chip de pontos de "
  "possíveis (cheio, parcial, zero; sem dado tracejado, com 'falta na base' ou 'sem dado na planilha' conforme a "
  "fonte), o X e a faixa atingida e, à direita, a minissérie dos pontos do item nos meses da janela (fração dos "
  "pontos; o mês de referência contornado). O mouse abre o tooltip do item.",
  linhas(
      "-- 1 · Leituras",
      "VAR _cod = SELECTEDVALUE ( dItemNota[Item] )",
      "VAR _nome = [Nota · item · nome médio]",
      "VAR _fonte = [Nota · item · fonte]",
      "VAR _max = [Nota · item · máximo]",
      "VAR _pts = [Nota · item · pontos · foco]",
      "VAR _poss = [Nota · item · possíveis · foco]",
      "VAR _x = [Nota · item · X · foco]",
      "VAR _fx = [Nota · item · faixa atingida · foco]",
      "VAR _fora = [Nota · item · fora da faixa · foco]",
      "VAR _temObra = NOT ISBLANK ( [Nota · pontos possíveis · ranking · foco] )",
      "VAR _ref = [Mês de referência]",
      "VAR _n = [Série · meses até a referência]",
      "VAR _todos =",
      "    ADDCOLUMNS (",
      "        VALUES ( dMes[Mes] ),",
      "        \"@ate\", [Série · mês até a referência],",
      "        \"@pos\", [Série · posição na janela],",
      "        \"@v\", [Nota · item · pontos · foco no mês],",
      "        \"@p\", [Nota · item · possíveis · foco no mês]",
      "    )",
      "VAR _meses = FILTER ( _todos, [@ate] = 1 ) /* lista */",
      "-- 2 · Textos",
      chip_item_m("_ca", "_pts", "_poss", fonte="ac", ms="450"),
      chip_item_m("_cb", "_pts", "_poss", fonte="base", ms="450"),
      DC.pontos("_max", "_tmx"),
      "VAR _chip =",
      "    SWITCH (",
      "        TRUE (),",
      "        NOT ISBLANK ( _pts ) && _poss = 0, \"<span class='a-pop chi chi-n' style='animation-delay:450ms'>não conta</span>\",",
      # valor digitado fora da faixa: sem pontos, mas não por falta (auditoria da Fase 2, P3/N3)
      "        ISBLANK ( _pts ) && _fora = 1, \"<span class='a-pop chi chi-f' style='animation-delay:450ms'>fora da faixa</span>\",",
      "        _fonte = \"Análise Crítica\", _caHtml,",
      "        _cbHtml",
      "    )",
      x_item("_cod", "_x", "_fx", "_pts", marcar=True),
      "VAR _txtFaixa =",
      "    SWITCH (",
      "        TRUE (),",
      "        ISBLANK ( _pts ), \"vale até \" & " + C.marca("_tmxTxt") + " & IF ( _max < 2, \" ponto\", \" pontos\" ),",
      "        " + faixa_html("_fx"),
      "    )",
      "-- 3 · Geometria",
      f"VAR _x0 = {ITN_SW} - _n * {ITN_BW + ITN_GAP} + {ITN_GAP} -- geometria",
      "-- 4 · Marcação",
      "VAR _serie =",
      "    CONCATENATEX (",
      "        _meses,",
      f"        VAR _xb = _x0 + ( [@pos] - 1 ) * {ITN_BW + ITN_GAP} /* geometria */",
      "        VAR _cls = SWITCH ( TRUE (), ISBLANK ( [@v] ) || [@p] = 0, \"v\", [@v] >= [@p], \"c\", [@v] = 0, \"z\", \"p\" )",
      f"        VAR _hb = IF ( _cls = \"z\", 3, MAX ( 3, ROUND ( DIVIDE ( [@v], [@p] ) * {ITN_SH}, 0 ) ) ) /* geometria */",
      "        /* F4: a barra cresce da base (corrida; o traço do mês sem dado tem altura fixa e só aparece) */",
      "        VAR _rd = ( [@pos] - 1 ) * 40 /* geometria */",
      "        VAR _corre = IF ( _cls = \"v\", \";animation-delay:\" & _rd & \"ms'\", \"' data-rk='\" & _cod & \"|\" "
      "& FORMAT ( dMes[Mes], \"yyyymm\" ) & \"' data-rp='height' data-r0-height='0px' data-rd='\" & _rd & \"'\" ) /* geometria */",
      "        RETURN",
      "            \"<i class='\" & _cls & IF ( _cls = \"v\", \" a-fd\", \"\" ) & IF ( dMes[Mes] = _ref, \" r\", \"\" ) & \"' style='left:\" & _xb "
      "& \"px;height:\" & _hb & \"px\" & _corre & \"></i>\",",
      "        \"\",",
      "        dMes[Mes], ASC",
      "    )",
      "RETURN",
      "    IF (",
      "        _temObra && NOT ISBLANK ( _cod ),",
      "        \"<div class='u it' data-rr='\" & _cod & \"'><p class='nm'>\" & _nome & \"</p>\" & _chip",
      "            & \"<p class='ln'>\" & _txtX & IF ( _txtFaixa = \"\", \"\", \"<span>\" & _txtFaixa & \"</span>\" ) & \"</p>\"",
      "            & \"<div class='sr'>\" & _serie & \"</div>\"",
      "        & \"</div>\" & [Comum · JS contador] & [Comum · JS corrida]",
      "    )",
  ))

# ======================================================================================================== nota mês a mês
# F3: o canto direito de cima (era Itens, 1488,273 · 372 × 388) mostra a nota da obra em foco mês a mês: barras na cor
# do status (pendente tracejado com os pontos obtidos), de 0 ao máximo da nota em 200 px, com as linhas de estável e
# de atenção tracejadas; rótulo no mês de referência, na maior e na menor nota; o mês no eixo como no IDC.
NMM = r"T2 Análise crítica\Nota, mês a mês"
NMM_W, NMM_TOP, NMM_H = 372, 30, 220
CSS_NMM = (
    ".nm2{position:fixed;inset:0}"
    f".nm2 .ar{{position:absolute;left:0;top:{NMM_TOP}px;width:{NMM_W}px;height:{NMM_H}px}}"
    ".nm2 .lm{position:absolute;left:0;right:0;height:0;border-top:1px dashed #6B6B70}"
    ".nm2 .lm span{position:absolute;right:0;top:-16px;font-size:12px;line-height:14px;color:#6B6B70}"
    ".nm2 .z{position:absolute;left:0;right:0;height:1px;background:#0B0B0C}"
    ".nm2 .b{position:absolute;bottom:0;box-sizing:border-box}"
    ".nm2 .b.s2{background:#C43737}.nm2 .b.s1{background:#C9821F}.nm2 .b.s0{background:#A9CDB9}"
    ".nm2 .b.sm{background:#FFFFFF;border:1px dashed #3B3B3F}"
    ".nm2 .v{position:absolute;width:50px;margin-left:-25px;text-align:center;font-family:'Barlow U','Segoe UI',"
    "sans-serif;font-weight:600;font-size:14px;line-height:17px;white-space:nowrap;font-variant-numeric:tabular-nums}"
    ".nm2 .ms{position:absolute;width:44px;margin-left:-22px;text-align:center;font-size:13px;line-height:16px;"
    "color:#3B3B3F;white-space:nowrap}"
    ".nm2 .ms.ref{font-weight:600;color:#0B0B0C}.nm2 .ms.sem{opacity:.35}"
    ".nm2 .tx{position:absolute;left:0;right:0;bottom:0;font-size:14px;line-height:19px;color:#3B3B3F}"
)
m("T2 · Nota mês a mês · CSS", NMM, "CSS do painel 'A nota, mês a mês' (um HTML só, sem granularidade).",
  "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(CSS_NMM))
m("T2 · Nota mês a mês · HTML", NMM,
  "A nota da obra em foco mês a mês na janela: barras na cor do status (pendente tracejado até os pontos obtidos) de "
  "0 ao máximo da nota, linhas tracejadas nos limites de estável e de atenção (lidos das medidas), rótulo no mês de "
  "referência, na maior e na menor nota, e embaixo uma linha com o que a nota fez desde o primeiro mês da janela.",
  linhas(
      "-- 1 · Leituras",
      "VAR _ref = [Mês de referência]",
      "VAR _n = [Série · meses até a referência]",
      "VAR _max = [Nota · nota · máximo]",
      "VAR _limA = [Nota · status · nota mínima atenção]",
      "VAR _limE = [Nota · status · nota mínima estável]",
      "VAR _todos =",
      "    ADDCOLUMNS (",
      "        VALUES ( dMes[Mes] ),",
      "        \"@ate\", [Série · mês até a referência],",
      "        \"@pos\", [Série · posição na janela],",
      "        \"@rotAno\", [Mês · rótulo curto],",
      "        \"@rot\", [Mês · abreviado],",
      "        \"@nota\", [Nota · nota final · foco no mês],",
      "        \"@st\", [Nota · status · foco no mês],",
      "        \"@pend\", [Nota · pendente · foco no mês],",
      "        \"@obt\", [Nota · pontos obtidos · foco no mês]",
      "    )",
      "VAR _meses = FILTER ( _todos, [@ate] = 1 ) /* lista */",
      "VAR _com = FILTER ( _meses, NOT ISBLANK ( [@nota] ) ) /* lista */",
      "VAR _vMax = MAXX ( _com, [@nota] ) /* geometria */",
      "VAR _vMin = MINX ( _com, [@nota] ) /* geometria */",
      "VAR _mMax = MAXX ( FILTER ( _com, [@nota] = _vMax ), dMes[Mes] ) /* geometria */",
      "VAR _mMin = MAXX ( FILTER ( _com, [@nota] = _vMin ), dMes[Mes] ) /* geometria */",
      "VAR _ini = MINX ( _com, dMes[Mes] ) /* geometria */",
      "VAR _nIni = MAXX ( FILTER ( _com, dMes[Mes] = _ini ), [@nota] ) /* geometria */",
      "VAR _nRef = MAXX ( FILTER ( _com, dMes[Mes] = _ref ), [@nota] ) /* geometria */",
      "-- 3 · Geometria",
      f"VAR _slot = DIVIDE ( {NMM_W}, _n ) -- geometria",
      "VAR _bw = MIN ( 24, ROUND ( _slot - 8, 0 ) ) -- geometria",
      f"VAR _k = DIVIDE ( {NMM_H - 24}, _max ) -- geometria",
      f"VAR _yA = {NMM_H} - ROUND ( _limA * _k, 0 ) -- geometria",
      f"VAR _yE = {NMM_H} - ROUND ( _limE * _k, 0 ) -- geometria",
      "VAR _passo = ROUND ( DIVIDE ( 420, _n ), 0 ) -- geometria",
      "-- 2 · Textos",
      "VAR _txtVar =",
      "    SWITCH (",
      "        TRUE (),",
      "        ISBLANK ( _nRef ), \"sem nota no mês de referência\",",
      "        _ini = _ref || ISBLANK ( _nIni ), \"primeiro mês com nota na janela\",",
      "        ROUND ( _nRef, 2 ) = ROUND ( _nIni, 2 ), \"mesma nota de \" & FORMAT ( _ini, \"mmm/yy\", \"pt-BR\" ),",
      "        \"de \" & " + C.marca(fmt_pts_dax("_nIni")) + " & \" em \" & FORMAT ( _ini, \"mmm/yy\", \"pt-BR\" ) & \" para \" & "
      + C.marca(fmt_pts_dax("_nRef")) + " & \" agora\"",
      "    )",
      "-- 4 · Marcação",
      "VAR _barras =",
      "    CONCATENATEX (",
      "        _meses,",
      "        VAR _pd = [@pend] = 1",
      "        VAR _v = IF ( _pd, [@obt], [@nota] )",
      "        VAR _tem = NOT ISBLANK ( _v )",
      "        VAR _h = IF ( _tem, MAX ( ROUND ( _v * _k, 0 ), 2 ), 0 ) /* geometria */",
      "        VAR _xc = ROUND ( ( [@pos] - 0.5 ) * _slot, 0 ) /* geometria */",
      "        VAR _cls = IF ( _pd, \"sm\", \"s\" & [@st] )",
      "        VAR _ehRef = dMes[Mes] = _ref",
      "        VAR _rotula = _tem && NOT _pd && ( _ehRef || dMes[Mes] = _mMax || dMes[Mes] = _mMin || _n <= 6 )",
      "        VAR _rotMes = IF ( _n <= 6 || [@pos] = 1 || [@rot] = \"jan\", [@rotAno], [@rot] )",
      "        VAR _mostraMes = _slot >= 40 || MOD ( _n - [@pos], 2 ) = 0",
      "        VAR _rd = ( [@pos] - 1 ) * _passo /* geometria */",
      "        RETURN",
      "            IF ( _tem, \"<i class='b \" & _cls & \"' style='left:\" & ( _xc - ROUND ( _bw / 2, 0 ) ) & \"px;width:\" & _bw"
      " & \"px;height:\" & _h & \"px' data-rk='n\" & FORMAT ( dMes[Mes], \"yyyymm\" ) & \"' data-rp='height' "
      "data-r0-height='0px' data-rd='\" & _rd & \"'></i>\" ) /* geometria */",
      "                & IF ( _rotula, \"<span class='v' style='left:\" & _xc & \"px;top:\" & ( "
      + str(NMM_H) + " - _h - 19 ) & \"px'>\" & "
      + C.marca(fmt_pts_dax("_v")) + " & \"</span>\" )",
      "                & IF ( _mostraMes, \"<span class='ms a-fd\" & IF ( _ehRef, \" ref\", IF ( _tem, \"\", \" sem\" ) ) & \"' style='left:\""
      " & _xc & \"px;top:" + str(NMM_H + 6) + "px;animation-delay:\" & _rd & \"ms'>\" & _rotMes & \"</span>\" ),",
      "        \"\",",
      "        dMes[Mes], ASC",
      "    )",
      "RETURN",
      "    IF (",
      "        NOT ISEMPTY ( _com ),",
      "        \"<div class='u nm2'><div class='ar'>\"",
      # F4: limites tracejados aparecem, a base cresce da esquerda, as barras correm da base em cascata
      "            & \"<i class='lm a-fd' style='top:\" & _yE & \"px'><span>estável</span></i>\"",
      "            & \"<i class='lm a-fd' style='top:\" & _yA & \"px;animation-delay:80ms'><span>atenção</span></i>\"",
      f"            & \"<i class='z a-gx' style='top:{NMM_H}px'></i>\" & _barras & \"</div>\"",
      "            & \"<p class='tx'>\" & _txtVar & \"</p>\"",
      "        & \"</div>\" & [Comum · JS contador] & [Comum · JS corrida]",
      "    )",
  ))


# ======================================================================================================== com e sem estoque
CSE = r"T2 Análise crítica\Com e sem estoque"
GRUPOS = [("Estoque", "material comprado e não aplicado"), ("AdiantServicos", "serviços pagos e ainda não medidos"),
          ("AdiantMateriais", "materiais pagos e ainda não entregues"), ("Equipamentos", "equipamentos"),
          ("SaldoContrato", "saldo de contrato")]
m("T2 · Com e sem estoque · CSS", CSE, "CSS do texto 'com e sem estoque' (sobre a caixa creme do papel de parede).",
  "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(".ce{position:fixed;inset:0;font-size:15px;line-height:21px;"
                                                        "color:#0B0B0C}"))
m("T2 · Com e sem estoque · HTML", CSE,
  "Síntese escrita da obra em foco no mês: o resultado com e sem estoque e adiantamentos e de que pagos e não "
  "aplicados ele depende (negativos em vermelho sobre creme). Variações: sem ativos lançados; positivo mesmo sem eles; "
  "negativo de qualquer jeito. Os textos são fixos ou números formatados (nada vindo de digitação).",
  linhas(
      "-- 1 · Leituras",
      "VAR _mesC = [Mês de referência · curto]",
      "VAR _res = [Resultado da obra · foco]",
      "VAR _sem = [Resultado sem ativos · foco]",
      "VAR _at = [Ativos não consumidos · foco]",
      [f'VAR _g{i} = CALCULATE ( [Item · valor · foco], dItem[Item] = "{c}" )' for i, (c, _t) in enumerate(GRUPOS)],
      "-- 2 · Textos",
      D.rs("_res", "_tr"), D.rs("_sem", "_ts"), D.rs("_at", "_ta"),
      "VAR _hRes = " + span_ng("_tr"),
      "VAR _hSem = " + span_ng("_ts"),
      "VAR _todos = { " + ", ".join(f'( {i}, _g{i}, "{t}" )' for i, (_c, t) in enumerate(GRUPOS)) + " } /* lista */",
      "VAR _comValor = FILTER ( _todos, NOT ISBLANK ( [Value2] ) && [Value2] <> 0 ) /* lista */",
      "VAR _grupos =",
      "    CONCATENATEX (",
      "        _comValor,",
      "        [Value3],",
      "        \" e \",",
      "        [Value1], ASC",
      "    )",
      "VAR _txt =",
      "    SWITCH (",
      "        TRUE (),",
      "        ISBLANK ( _res ), \"\",",
      "        ISBLANK ( _at ) || _at = 0, \"Nada pago e ainda não aplicado entra na conta de \" & _mesC & \": o resultado de \""
      " & _hRes & \" é o consumo real da obra.\",",
      "        _sem >= 0, \"Estoque e adiantamentos entram somando: é dinheiro pago que ainda não virou obra. Mesmo sem eles, o \""
      " & \"resultado de \" & _mesC & \" seria \" & _hSem & \" — o resultado de \" & _hRes & \" não depende dos \" & _taTxt"
      " & \" em \" & _grupos & \".\",",
      "        _res < 0, \"Estoque e adiantamentos entram somando, e mesmo assim o resultado de \" & _mesC & \" é \" & _hRes"
      " & \". Sem eles, seria \" & _hSem & \": os \" & _taTxt & \" em \" & _grupos & \" só adiam o prejuízo.\",",
      "        \"Estoque e adiantamentos entram somando: é dinheiro pago que ainda não virou obra. Sem eles, o resultado de \""
      " & _mesC & \" seria \" & _hSem & \" — o resultado de \" & _hRes & \" depende de \" & _taTxt & \" em \" & _grupos & \".\"",
      "    )",
      "-- 4 · Marcação",
      "RETURN",
      "    IF ( _txt <> \"\", \"<p class='u ce sobre-creme'>\" & _txt & \"</p>\" )",
  ))

# Fase 2 da régua antiga (13/10/2026): medidas de desenho que a tela deixou de ler (renomeadas ou da régua antiga). Ficam fora
# da gravação; o gerador apaga o .dax que tinha escrito antes.
RETIRADAS = {
    # F3 (docs/08 §5): o quadradinho e o texto "com e sem estoque" saem (a cascata mostra a mesma conta; as dez linhas
    # vão para o tooltip do degrau); o cartão "Mês anterior" sai (repetia o mês a mês)
    "T2 · Quadradinho · CSS", "T2 · Quadradinho · HTML entradas", "T2 · Quadradinho · HTML item",
    "T2 · Quadradinho · HTML resultado", "T2 · Com e sem estoque · CSS", "T2 · Com e sem estoque · HTML",
    "T2 · Cartão criticidade · HTML",     # → T2 · Cartão nota da obra · HTML
    "T2 · Sinais · CSS",                  # → T2 · Itens · CSS
    "T2 · Sinais · HTML subtítulo",       # → T2 · Itens · HTML subtítulo
    "T2 · Sinais · HTML linha",           # → T2 · Itens · HTML linha (eixo dItemNota)
}

if __name__ == "__main__":
    sys.exit(gravar([x for x in MEDIDAS if x.nome not in RETIRADAS], RAIZ / "dax" / "T2", GERADO))

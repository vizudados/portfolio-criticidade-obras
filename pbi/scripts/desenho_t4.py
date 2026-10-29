#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""desenho_t4 — medidas de DESENHO da Tela 04 · Resultado no tempo (pbi/dax/T4/**). Só leem contas (base/**,
T4/**/Contas e as genéricas de T1); formatam, escapam e posicionam.

Redesenho v2 (07/10/2026, aprovado pelo Alisson): Figma FjBWDk5odF9HaZ2pwhGosl, página 04 · Redesenho v2 (372:685),
seção 379:791 — componente Tela 04 · v2 387:5688 (prancheta em 300,12); spec em pbi/spec/redesenho/t04.md. Geometria
no canvas (fase 5, 07/10/2026: "o gráfico de colunas de baixo ocupa o mesmo espaço do de cima", a justificativa e a
tendência viram tooltip e a coluna da direita se comprime): cartões em y 109 (302 × 140; x 352 · 654 · 955 · 1257 ·
1558); à esquerda, os dois gráficos de colunas com a mesma largura — Resultado da carteira, mês a mês 352,273 ·
1068 × 380 (gráfico 1068 × 312 a partir de y 341) e Desembolso da carteira 352,693 · 1068 × 347 (gráfico 1068 × 279
a partir de y 761); divisória vertical única em x 1440. F3 (28/10/2026, docs/08 §5): à direita, uma tabela só, Obras
no mês, na coluna inteira (1460,273 · 400 × 767: cabeçalho em y 305, linhas de 92 a partir de y 365), no lugar de
Resultado por obra e Desembolso por obra; o cartão "Mês anterior" virou o IDC da carteira; o mês a mês tem uma série
(resultado aplicado) e o traço do resultado da planilha, com subtítulo e legenda em HTML. O papel de parede (Casca v2 ·
T4 408:1237 → pbi/spec/casca/_fonte_v2/T4.svg) traz títulos, "?", subtítulos e legendas fixos; onde eles ficaram
velhos, o HTML tem fundo branco por cima até a casca nova.

Cores v2: negativo em vermelho (.ng) só em resultado, variação e sem estoque — número, rótulo e barra; o desvio de
desembolso negativo (gastou menos que o previsto) fica em preto e a barra segue a cor da faixa (decisão do Alisson).
Hachura só na série sem estoque (comum: .hach preta, .hach.ng vermelha). Status por cor com as marcas da camada comum.

Geometria em px sempre inteira (o modelo é pt-BR: decimal sairia com vírgula e o CSS ignoraria).

F4 (pedido do Alisson, 28/10/2026: todo número conta e todo elemento de gráfico entra animado): os números que ainda
eram estáticos (contexto dos cartões, IDC, variação e caixa de Obras no mês) vão marcados com C.marca() e viram
odômetro no fim da medida (C.envolver_marcas); traço da planilha, linhas de base, rótulos de mês e marcas entram com
as classes genéricas do CSS base (.a-pop, .a-fd), em cascata depois da barra da mesma coluna ou linha.

    python -X utf8 pbi/scripts/desenho_t4.py
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
import justificativas_rodape as R  # noqa: E402

RAIZ = AQUI.parent
GERADO = "pbi/scripts/desenho_t4.py"
TELA = "T4 Resultado no tempo"
MEDIDAS: list[Medida] = []
MENOS = D.MENOS

# ---------------------------------------------------------------------------------------------------------- geometria
# Resultado da carteira, mês a mês: visual em (352, 341) · 1068 × 312. Uma entrada por mês da janela (dMes), coluna =
# 1068 ÷ n (flex). Topo da maior barra positiva em 27, MES_ALT px para o maior positivo + o maior negativo (Figma, ago/26:
# 53 px por R$ 1 mi; R$ 96 mil → 5 px acima do zero em 32; −R$ 4,16 mi → 221 px), rótulo do mês em 296 (Segoe 13/16,
# termina em 312). Janela de 1 a 12 meses (regras da §9 da spec v1 na geometria v2, t04.md §6): barra = mín(46; 0,36 ×
# coluna), centrada (F3: uma barra, o resultado aplicado, e o traço do resultado da planilha); até 8 meses, rótulo em
# todo mês ("−R$ 340 mil"); de 9 a 12, só na referência e nos meses do maior e do menor aplicado, compacto ("−3,65 mi");
# o rótulo fica do lado de fora da barra, preso na coluna (CSS clamp), e pula o traço quando cai nele; eixo "jan/26" até
# 8 meses, "jan" com o ano só no primeiro mês e em janeiro de 9 a 12.
MES_W, MES_H, MES_TOPO, MES_ALT, MES_ROT = 1068, 312, 27, 226, 296
MES_BARRA = 46              # teto da barra (Figma 417:8059: coluna 133,5 com 8 meses → 0,36 × 133,5 = 48 → 46)
MES_DENSO = 9               # a partir de quantos meses o painel só rotula referência, máximo e mínimo
MES_CAIXA = (80, 56)        # largura da caixa do rótulo: completo ("−R$ 3,65 mi") e compacto ("−3,65 mi")
# Desembolso da carteira: visual em (352, 761) · 1068 × 279; base em 255; maior valor = 231 px (Figma: 39 px por
# R$ 1 mi, jul/26 R$ 5,93 mi); mês em 263. Coluna = 1068 ÷ n, barra = mín(44; 0,36 × coluna), 3 px entre as barras;
# o desvio (preto, também quando negativo) cabe em todo mês até 12 (13 px a partir de 10); eixo "jan", com o ano só no
# primeiro mês e em janeiro quando a janela cruza a virada do ano. O desvio da carteira segue a regra "sem previsto"
# (T4 · Desembolso · desvio no mês · com previsto).
DES_W, DES_H, DES_BASE, DES_ALT = 1068, 279, 255, 231
DES_BARRA = 44              # teto da barra (Figma 417:8117)


def m(nome, pasta, descricao, dax):
    """Medida de desenho; os valores marcados com C.marca() viram odômetro no fim (F4)."""
    MEDIDAS.append(Medida(nome, pasta, "texto", descricao, C.envolver_marcas(dax)))


def css(nome, pasta, descricao, texto, base="[Comum · CSS base]"):
    m(nome, pasta, descricao, "-- 4 · Marcação\n" + base + "\n    & " + dax_lit(texto))


def linhas(*ls) -> str:
    return "\n".join(l for g in ls for l in (g if isinstance(g, list) else [g]))


def ng(sinal: str) -> str:
    """Classe do negativo (resultado, variação, sem estoque) pelo sinal já formatado: " ng" quando sai "−"."""
    return f'IF ( {sinal} = "{MENOS}", " ng", "" )'


# ======================================================================================================== cartões
CARTOES = rf"{TELA}\Cartões"
m("T4 · Cartões · CSS", CARTOES,
  "CSS dos cartões da T4: o do cartão com flip comum (v2: rótulo em caixa normal, número 42, contexto 14 numa linha; "
  "verso creme com 'DE ONDE VEM' em y 82 com régua e 106 sem).",
  "-- 4 · Marcação\n[Comum · CSS cartão]")


def regua(itens: list[tuple[str, str]]) -> str:
    return "".join(f"<i class='mk {c}'></i><span>{t}</span>" for c, t in itens)


def cartao(chave: str, eb: str, leituras: list[tuple[str, str]], textos: list[str], hero: str, lado: str | None,
           ctx: str, regra: str, origem: str, regua_itens: list | None, anima: list[str], escuro: bool = False,
           cls_hero: str = '""', cls_lado: str = '""', desc: str = "") -> None:
    """Cartão com flip (frente e verso no mesmo visual, L057). `eb`, `hero`, `lado`, `ctx` e `regra` são expressões
    DAX de texto já formatado; `cls_hero`/`cls_lado` = expressão da classe extra (" ng" no negativo); `anima` = linhas
    D.od_* que definem os {p}Od usados em hero/lado (contador). Verso v2: "DE ONDE VEM" em y 82 com régua (régua em
    106) e em 106 sem régua."""
    topo_ond = 82 if regua_itens else 106
    verso = ("\"<div class='lado verso sobre-creme'>\"\n"
             "            & \"<p class='ab vs v1'>COMO É CALCULADO</p>\"\n"
             f"            & \"<p class='regra'>\" & {regra} & \"</p>\"\n"
             f"            & \"<div class='ond' style='top:{topo_ond}px'><span class='vs'>DE ONDE VEM</span>"
             f"<span>{origem}</span></div>\"\n")
    if isinstance(regua_itens, str):     # régua montada na medida (expressão DAX que já devolve o HTML das marcas)
        verso += f"            & \"<div class='regua'>\" & {regua_itens} & \"</div>\"\n"
    elif regua_itens:
        verso += f"            & \"<div class='regua'>{regua(regua_itens)}</div>\"\n"
    verso += "        & \"</div>\""
    lado_html = (f" & \"<span class='b5 lado2\" & {cls_lado} & \"'>\" & {lado} & \"</span>\"" if lado else "")
    dax = linhas(
        "-- 1 · Leituras", [f"VAR {v} = [{x}]" for v, x in leituras],
        "-- 2 · Textos", textos,
        [D.od_tabela()] + anima,
        "-- 4 · Marcação",
        "RETURN",
        f"    \"<div class='u kc{' escuro' if escuro else ''}' tabindex='0'>\"",
        "        & \"<div class='lado frente'>\"",
        f"            & \"<p class='ab vs eb'>\" & {eb} & \"</p>\"",
        f"            & \"<div class='linha1'><span class='b6 hero\" & {cls_hero} & \"'>\" & {hero} & \"</span>\""
        f"{lado_html} & \"</div>\"",
        f"            & \"<p class='ctx'>\" & {ctx} & \"</p>\"",
        "        & \"</div>\"",
        "        & " + verso,
        "    & \"</div>\" & [Comum · JS contador]",
    )
    m(f"T4 · Cartão {chave} · HTML", CARTOES, desc or f"Cartão '{chave}' (frente e verso). Só lê contas · ref.", dax)


# F3 (docs/08 §5): o cartão "Mês anterior" saiu (repetia a coluna anterior do gráfico); no lugar, o custo da carteira
# (IDC, com o resultado aplicado ao lado). O escuro segue o resultado da planilha: aplicado + o que falta realizar.
cartao(
    "resultado", '"Resultado da carteira · " & _mesC',
    [("_res", "Resultado da obra · ref"), ("_pct", "Resultado % · ref"), ("_orc", "Orçamento · ref"),
     ("_n", "Obras com análise · ref"), ("_mesC", "Mês de referência · curto")],
    D.rs("_res", "_tr") + D.pct("_pct", "_tp", casas=2, mais=True) + D.rs("_orc", "_to") + [
        'VAR _txtN = IF ( _n = 1, "1 obra", ' + C.marca("_n") + ' & " obras" )',
        'VAR _txtCtx = _txtN & " · " & ' + C.marca("_toTxt") + ' & " de orçamento"',
        'VAR _txtRegra = "Soma " & IF ( _n = 1, "da obra", "das " & ' + C.marca("_n") + ' & " obras" ) '
        '& ", como a planilha apresenta: o resultado aplicado mais o que ainda vai se realizar."'],
    "_trOd", "_tpOd", "_txtCtx", "_txtRegra", "Quadradinho da aba",
    None,
    D.od_rs("_res", "_tr") + D.od_pct("_pct", "_tp"), escuro=True, cls_hero=ng("_trS"), cls_lado=ng("_tpS"),
    desc="Cartão 'Resultado da carteira' (o escuro, a resposta): resultado da planilha no mês e % do orçamento "
         "(vermelho sobre preto quando negativos), obras e orçamento; verso com a regra (aplicado + a realizar). Só lê "
         "contas · ref.")

cartao(
    "IDC", '"Custo · IDC da carteira"',
    [("_idc", "IDC · ref"), ("_var", "T4 · IDC · variação no mês · ref"), ("_ra", "Resultado aplicado · ref"),
     ("_abx", "T1 · Custo · obras com IDC abaixo de 1 · ref")],
    ['VAR _tiN = FORMAT ( _idc, "0.00", "pt-BR" )', 'VAR _tiTxt = IF ( ISBLANK ( _idc ), "—", _tiN )']
    + D.rs("_ra", "_tra", mais=True) + [
        f'VAR _tvTxt = IF ( ISBLANK ( _var ), "", SWITCH ( TRUE (), _var > 0, "+", _var < 0, "{MENOS}", "" ) '
        '& ' + C.marca('FORMAT ( ABS ( _var ), "0.00", "pt-BR" )') + ' & " no mês · " )',
        'VAR _a = _abx + 0',
        "VAR _txtCtx = IF ( ISBLANK ( _idc ), \"sem aba no mês\", \"<span class='\" & IF ( _var < 0, \"ng\", \"\" ) & \"'>\" "
        "& _tvTxt & \"</span>\" & IF ( _a = 0, \"nenhuma obra abaixo de 1\", IF ( _a = 1, \"1 obra abaixo de 1\", " + C.marca("_a") + " & \" obras abaixo de 1\" ) ) )",
        'VAR _txtRegra = "Valor agregado ÷ custo aplicado, com as obras somadas (com a dívida). Ao lado, o resultado '
        'aplicado em R$."'],
    "_tiOd", "_traOd", "_txtCtx", "_txtRegra", "Análise Crítica",
    None, D.od_num("_idc", "_ti") + D.od_rs("_ra", "_tra"), cls_lado=ng("_traS"),
    desc="Cartão 'Custo · IDC da carteira' (F3, no lugar do 'Mês anterior'): o IDC da carteira (valor agregado ÷ custo "
         "aplicado, soma ÷ soma) e o resultado aplicado em R$ ao lado (vermelho quando negativo); na linha de baixo, a "
         "variação do IDC no mês (vermelha quando cai) e quantas obras estão com IDC abaixo de 1. Só lê contas · ref.")

cartao(
    "sem estoque", '"Sem estoque e adiantamentos"',
    [("_sem", "Resultado sem ativos · ref"), ("_ativos", "Ativos não consumidos · ref")],
    D.rs("_sem", "_ts") + D.rs("_ativos", "_ta") + [
        'VAR _txtCtx = ' + C.marca("_taTxt") + ' & " pagos e ainda não aplicados"',
        'VAR _txtRegra = "Resultado menos o que foi pago e ainda não virou obra: estoque e adiantamentos."'],
    "_tsOd", None, "_txtCtx", "_txtRegra", "Resultado menos itens 2 a 6",
    None, D.od_rs("_sem", "_ts"), cls_hero=ng("_tsS"),
    desc="Cartão 'Sem estoque e adiantamentos': o resultado sem o que foi pago e não aplicado (vermelho quando "
         "negativo). Só lê contas · ref.")

cartao(
    "desembolso", '"Desembolso do mês"',
    [("_des", "Desembolso · realizado no mês · ref"), ("_prev", "Desembolso · previsto no mês · ref"),
     ("_desv", "T4 · Desembolso · desvio no mês · com previsto · ref"),
     ("_fx", "T4 · Desembolso · faixas do fluxo de caixa (lista)")],
    D.rs("_des", "_td") + D.rs("_prev", "_tp") + D.pct("_desv", "_tv", casas=0, mais=True) + [
        'VAR _txtCtx = ' + C.marca("_tpTxt") + ' & " previsto para o mês"',
        'VAR _txtRegra = "Desembolsado ÷ previsto − 1. Na nota, por obra, para mais ou para menos:"',
        "VAR _fxN = IF ( ISBLANK ( _fx ), 0, PATHLENGTH ( _fx ) )",
        "/* da faixa crítica (vermelha) à de pontos cheios (sálvia) */",
        "VAR _htmlRegua =",
        "    CONCATENATEX (",
        "        GENERATESERIES ( 1, _fxN ),",
        "        \"<i class='mk mk\" & SWITCH ( TRUE (), [Value] = 1, 2, [Value] = _fxN, 0, 1 ) & \"'></i><span>\"",
        "            & PATHITEM ( _fx, [Value] ) & \"</span>\",",
        "        \"\",",
        "        [Value], ASC",
        "    ) /* lista */"],
    "_tdOd", "_tvOd", "_txtCtx", "_txtRegra", "Previsto e desembolsado",
    "_htmlRegua",
    D.od_rs("_des", "_td") + D.od_pct("_desv", "_tv"),
    desc="Cartão 'Desembolso do mês': desembolsado, desvio sobre o previsto (só as obras com previsto; preto também "
         "quando negativo) e o previsto; verso com a régua da previsão de caixa da nota (o desvio de cada obra, para mais "
         "ou para menos; rótulos lidos das contas). Só lê contas · ref.")

# Linha de contexto numa linha só (regra na nota 366:8262 da v1; Figma v2 t04.md): o herói diz P e o lado "de E
# exigidas"; a linha é o mesmo trecho do rodapé dos tooltips de desembolso (justificativas_rodape.py): "em branco: " e
# os nomes do maior para o menor |desvio|, sem cortar nome — todos; senão os 2 primeiros e "e mais M" (M é conta;
# "e outra(s)" quando M = P, L058); senão "todas em branco", "as outras em branco" ou "N em branco". Largura: a da .ctx
# v2 (262 px a 14 px) menos 2 de folga; a tabela de larguras de justificativas_rodape.py é de Segoe 13, então o espaço
# entra convertido para 13 px (× 13 ÷ 14).
CARTAO_JUS_W, CARTAO_JUS_FOLGA = 262, 2
CARTAO_JUS_PX13 = int((CARTAO_JUS_W - CARTAO_JUS_FOLGA) * 13 / 14)
cartao(
    "justificativas", '"Justificativas do mês"',
    [("_ex", "Carteira · justificativas exigidas · ref"), ("_pre", "Carteira · justificativas preenchidas · ref"),
     ("_br", "Carteira · justificativas em branco · ref"), ("_lista", "Recorte · justificativas em branco (lista) · ref"),
     ("_fora", "Recorte · justificativas em branco fora da lista curta · ref")],
    ["VAR _e = _ex + 0", "VAR _p = _pre + 0", "VAR _b = _br + 0"] + D.inteiro("_p", "_tj") + [
        'VAR _txtLado = IF ( _e = 0, "exigidas", "de " & ' + C.marca("_e") + ' & IF ( _e = 1, " exigida", " exigidas" ) )',
        f"VAR _pxCtx = {CARTAO_JUS_PX13} -- geometria",
    ] + R.nomes("_lista", "_fora", "_p", "_b", "_pxCtx") + [
        'VAR _txtCtx =',
        '    SWITCH (',
        '        TRUE (),',
        '        _e = 0, "nenhuma exigida: tudo dentro de ±10%",',
        '        _b = 0, "todas as exigidas preenchidas",',
        '        ' + C.marca(D.esc("_nbTxt")),
        '    )',
        'VAR _txtRegra = "Obras acima de ±10% no mês (exigida) e quantas preencheram o campo; nomes do maior ao menor '
        'desvio."'],
    "_tjOd", "_txtLado", "_txtCtx", "_txtRegra", "Justificativa, cada aba", None,
    D.od_num("_p", "_tj"),
    desc="Cartão 'Justificativas do mês': preenchidas entre as exigidas (desvio do desembolso acima de ±10%) e, numa "
         "linha só, quais obras deixaram em branco (do maior para o menor |desvio|, sem cortar nome: todas, as 2 "
         "primeiras e 'e mais M', ou nenhuma, com 'todas em branco' / 'N em branco'). Só lê contas · ref.")

# ======================================================================================================== mês a mês
# F3 (docs/08 §5): uma série só, o resultado aplicado da carteira (barra cheia: preta ≥ 0, vermelha < 0), com o resultado
# da planilha como traço sobre a coluna (a distância entre os dois é o que ainda vai se realizar). Duas barras lado a
# lado em 12 meses ficavam finas demais. Subtítulo e legenda em HTML (fundo branco por cima dos fixos da casca antiga):
# legenda na linha do título até x 1382, subtítulo em y 305.
MES = rf"{TELA}\Resultado mês a mês"
css("T4 · Mês a mês · CSS cabeçalho", MES, "CSS do subtítulo e da legenda do Resultado da carteira, mês a mês (F3).",
    ".mlg{position:fixed;inset:0;background:#FFFFFF;display:flex;justify-content:flex-end;align-items:center;"
    "font-size:14px;line-height:19px;color:#3B3B3F;white-space:nowrap}"
    ".mlg i{display:block;flex:none;margin-right:6px}.mlg span{margin-right:18px}.mlg span:last-child{margin-right:0}"
    ".mlg .sp{width:12px;height:12px;background:#0B0B0C}.mlg .sn{width:12px;height:12px;background:#C43737}"
    ".mlg .tq{width:18px;height:3px;background:#0B0B0C}"
    ".msb{position:fixed;inset:0;background:#FFFFFF;font-size:15px;line-height:22px;color:#3B3B3F;white-space:nowrap}")
m("T4 · Mês a mês · HTML legenda", MES,
  "Legenda do Resultado da carteira, mês a mês, na linha do título (F3): resultado aplicado positivo e negativo (barra) "
  "e o traço do resultado da planilha. Fundo branco por cima da legenda antiga da casca.",
  "-- 4 · Marcação\n" + dax_lit("<div class='u mlg'><i class='sp'></i><span>resultado aplicado</span><i class='sn'></i>"
                                "<span>negativo</span><i class='tq'></i><span>resultado da planilha</span></div>"))
m("T4 · Mês a mês · HTML subtítulo", MES,
  "Subtítulo do Resultado da carteira, mês a mês (F3): o que a barra e o traço mostram. Fundo branco por cima do "
  "subtítulo antigo da casca.",
  "-- 4 · Marcação\n" + dax_lit("<p class='u msb'>barra = resultado aplicado (valor agregado − custo aplicado) · traço = "
                                "resultado da planilha · a distância é o que ainda vai se realizar</p>"))
css("T4 · Mês a mês · CSS", MES, "CSS das colunas do painel Resultado da carteira, mês a mês (uma entrada por mês).",
    "#htmlContent{display:flex!important;align-items:flex-start;width:100vw;height:100vh;margin:0!important;"
    "padding:0!important}"
    ".htmlViewerEntry{display:block!important;flex:1 1 0;min-width:0;margin:0!important;padding:0!important}"
    f".mc{{position:relative;height:{MES_H}px;transition:background .15s}}"
    ".mc:hover,.htmlViewerEntry.hover .mc{background:rgba(233,224,207,.3)}"
    ".mc .rz{position:absolute;left:0;right:0;height:1px;background:#6B6B70}"
    # barra do resultado aplicado (preta ≥ 0, vermelha < 0) e o traço do resultado da planilha por cima
    ".mc .br{position:absolute;background:#0B0B0C}.mc .br.ng{background:#C43737}"
    ".mc .tq{position:absolute;z-index:1;height:3px;background:#0B0B0C;box-shadow:0 0 0 1px #FFFFFF}"
    # rótulo Barlow SemiBold 14 centrado na barra e preso na coluna (left = clamp na medida); halo branco
    ".mc .vl{position:absolute;z-index:2;text-align:center;font-size:14px;line-height:17px;white-space:nowrap;"
    "color:#0B0B0C;text-shadow:0 0 2px #FFFFFF,0 0 4px #FFFFFF,0 0 6px #FFFFFF}"
    f".mc .ms{{position:absolute;left:0;right:0;top:{MES_ROT}px;text-align:center;font-size:13px;line-height:16px;"
    "color:#3B3B3F;white-space:nowrap}"
    ".mc .ms.ref{font-weight:600;color:#0B0B0C}.mc .ms.sem{opacity:.35}")
m("T4 · Mês a mês · HTML coluna", MES,
  "Uma coluna por mês da janela (granularidade dMes[Mes]; coluna = 1068 ÷ n): barra = resultado aplicado da carteira "
  "(preta ≥ 0, vermelha < 0) a partir do zero, barra = mín(46; 0,36 × coluna), e o traço do resultado da planilha por "
  "cima (a distância é o que falta realizar). Até 8 meses, valor do aplicado em todo mês ('−R$ 340 mil', vermelho "
  "quando negativo); de 9 a 12, só no mês de referência e nos meses do maior e do menor aplicado, compacto "
  "('−3,65 mi'). O valor fica do lado de fora da barra (em cima no positivo, embaixo no negativo), preso na coluna. Mês "
  "de referência em semibold; mês sem aba só com o rótulo apagado; eixo 'jan/26' até 8 meses e 'jan' (ano só no "
  "primeiro mês e em janeiro) acima disso. A barra corre do zero em cascata e o valor conta.",
  linhas(
      "-- 1 · Leituras",
      "VAR _noRecorte = [Série · mês até a referência]",
      "VAR _ap = [Resultado aplicado]",
      "VAR _pla = [Resultado da obra]",
      "VAR _topo = [T4 · Mês a mês · topo da escala]",
      "VAR _base = [T4 · Mês a mês · base da escala]",
      "VAR _mes = [Mês · rótulo curto]",
      "VAR _mesAbrev = [Mês · abreviado]",
      "VAR _data = [Mês · data]",
      "VAR _ehRef = [Série · é o mês de referência]",
      "VAR _pos = [Série · posição na janela]",
      "VAR _n = [Série · meses até a referência]",
      "VAR _mx = [T4 · Mês a mês · mês do maior aplicado]",
      "VAR _mn = [T4 · Mês a mês · mês do menor aplicado]",
      "-- 2 · Textos",
      D.rs("_ap", "_tr"),
      D.od_tabela(), D.od_rs("_ap", "_tr"),
      f"VAR _denso = _n >= {MES_DENSO}",
      "VAR _rot = NOT _denso || _ehRef = 1 || _data = _mx || _data = _mn",
      "VAR _txtR = IF ( _denso, _trS & _trKOd & _trUn, _trOd )",
      'VAR _txtMes = IF ( _denso, _mesAbrev & IF ( _pos = 1 || MONTH ( _data ) = 1, RIGHT ( _mes, 3 ), "" ), _mes )',
      'VAR _clsMes = IF ( _ehRef = 1, " ref", "" ) & IF ( ISBLANK ( _ap ), " sem", "" )',
      "VAR _ngR = " + ng("_trS"),
      "VAR _clsBr = IF ( _ap < 0, \" ng\", \"\" )",
      "-- 3 · Geometria",
      f"VAR _b = MIN ( {MES_BARRA}, ROUND ( 0.36 * {MES_W} / _n, 0 ) ) -- geometria",
      f"VAR _caixa = IF ( _denso, {MES_CAIXA[1]}, {MES_CAIXA[0]} ) -- geometria",
      f"VAR _meiaCaixa = IF ( _denso, {MES_CAIXA[1] // 2}, {MES_CAIXA[0] // 2} ) -- geometria",
      f"VAR _u = DIVIDE ( {MES_ALT}, _topo - _base ) -- geometria",
      f"VAR _zero = {MES_TOPO} + ROUND ( _topo * _u, 0 ) -- geometria",
      "VAR _hR = IF ( _ap = 0, 0, MAX ( 2, ROUND ( ABS ( _ap ) * _u, 0 ) ) ) -- geometria",
      "VAR _yR = IF ( _ap >= 0, _zero - _hR, _zero + 1 ) -- geometria",
      "VAR _yT = _zero - ROUND ( _pla * _u, 0 ) - 1 -- geometria",
      "/* o rótulo fica do lado de fora da barra; se o traço da planilha cai ali, passa para o outro lado do traço */",
      "VAR _yRot0 = IF ( _ap >= 0, _yR - 21, _yR + _hR + 4 ) -- geometria",
      "VAR _bate = NOT ISBLANK ( _pla ) && _yT >= _yRot0 - 3 && _yT <= _yRot0 + 20 -- geometria",
      "VAR _yRot = IF ( _bate, IF ( _ap >= 0, _yT - 21, _yT + 6 ), _yRot0 ) -- geometria",
      "VAR _offR = _meiaCaixa -- geometria",
      "VAR _caixaCss = \"px),calc(100% - \" & _caixa & \"px));width:\" & _caixa & \"px'>\"",
      "VAR _atraso = ( _pos - 1 ) * 100 -- geometria",
      "VAR _corre = \"' data-rp='top,height' data-r0-top='\" & _zero & \"px' data-r0-height='0px' data-rd='\"",
      "-- 4 · Marcação",
      "VAR _htmlBarras =",
      "    IF (",
      "        NOT ISBLANK ( _ap ),",
      "        IF ( _rot, \"<span class='vl b6 a-fd\" & _ngR & \"' style='animation-delay:\" & ( _atraso + 250 ) & \"ms;top:\" "
      "& _yRot & \"px;left:clamp(0px,calc(50% - \"",
      "            & _offR & _caixaCss & _txtR & \"</span>\" )",
      "            & \"<i class='br\" & _clsBr & \"' style='top:\" & _yR & \"px;height:\" & _hR & \"px;left:calc(50% - \"",
      "            & INT ( _b / 2 ) & \"px);width:\" & _b & \"px' data-rk='\" & _mes & \"|a\" & _corre & _atraso & \"'></i>\"",
      "            & IF ( ISBLANK ( _pla ), \"\", \"<i class='tq a-pop' style='animation-delay:\" & ( _atraso + 600 ) & \"ms;top:\" "
      "& _yT & \"px;left:calc(50% - \" & ( INT ( _b / 2 ) + 6 )",
      "                & \"px);width:\" & ( _b + 12 ) & \"px'></i>\" )",
      "    )",
      "RETURN",
      "    IF (",
      "        _noRecorte = 1,",
      "        \"<div class='u mc'><i class='rz a-fd' style='top:\" & _zero & \"px'></i>\" & _htmlBarras",
      "            & \"<p class='ms a-fd\" & _clsMes & \"' style='animation-delay:\" & _atraso & \"ms'>\" & _txtMes & \"</p>\"",
      "        & \"</div>\" & [Comum · JS contador] & [Comum · JS corrida]",
      "    )",
  ))

# ======================================================================================================== obras no mês
# F3 (docs/08 §5): Resultado por obra e Desembolso por obra (duas tabelas com as mesmas obras) viram uma tabela, na coluna
# da direita inteira (1460,273 · 400 × 767): cabeçalho em y 305 (subtítulo com o mês e os nomes das colunas em y 341) e
# sete linhas de 92 a partir de y 365, na ordem da nota (T1 · Obras · posição). Cada linha: nome (Barlow 18), IDC com a
# marca dos pontos do item custo, a variação do IDC no mês (vermelha quando cai) e, à direita, o desvio de caixa do mês
# com a marca da faixa da previsão de caixa (preto também quando negativo: gastar menos não é vermelho); embaixo, a
# justificativa da planilha em até duas linhas, ou "em branco · exigida acima de ±10%" (vermelho, com a marca de
# pendência), "dentro de ±10%: não exigida" ou "sem previsto no mês". Fundo branco por cima da casca antiga (que ainda
# tem a divisória, o "?" e a legenda do painel de baixo).
OBRAS = rf"{TELA}\Obras no mês"
OB_LINHA = 92
css("T4 · Obras · CSS", OBRAS, "CSS do cabeçalho e das linhas da tabela Obras no mês (F3).",
    ".htmlViewerEntry{display:block!important;margin:0!important;padding:0!important}"
    ".obc{position:fixed;inset:0;background:#FFFFFF;white-space:nowrap}"
    ".obc .sub{position:absolute;left:0;top:0;font-size:15px;line-height:20px;color:#3B3B3F}"
    ".obc .vs{position:absolute;top:36px;font-size:12px;line-height:16px;letter-spacing:1px;text-transform:uppercase;"
    "color:#6B6B70}"
    # fundo branco opaco na linha (o corpo do visual é transparente): cobre a divisória, o "?" e a legenda do painel de
    # baixo da casca antiga; o realce do mouse é o creme a 35% já misturado ao branco
    f".ob{{position:relative;height:{OB_LINHA - 1}px;border-bottom:1px solid #E1E1E1;background:#FFFFFF;"
    "transition:background .15s}"
    ".ob:hover,.htmlViewerEntry.hover .ob{background:#F7F4EE}"
    ".ob .nm{position:absolute;left:14px;top:10px;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;"
    "font-size:18px;line-height:22px;white-space:nowrap}"
    ".ob .ic,.ob .vr,.ob .cx{position:absolute;top:11px;display:flex;align-items:center;white-space:nowrap;"
    "font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:16px;line-height:20px}"
    ".ob .ic{left:150px}.ob .vr{left:230px;font-size:15px}.ob .cx{right:14px}"
    ".ob .ic .mk,.ob .cx .mk{margin-right:6px}"
    ".ob .ng{color:#C43737}"
    ".ob .js{position:absolute;left:14px;right:14px;top:40px;font-size:13px;line-height:18px;color:#3B3B3F;"
    "white-space:normal;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}"
    ".ob .js.nx{color:#6B6B70}.ob .js.pd{color:#C43737}"
    ".ob .js .pend{display:inline-block;width:11px;height:11px;margin:0 6px -1px 0;border:1.25px dashed #C43737;"
    "box-sizing:border-box}")
m("T4 · Obras · HTML cabeçalho", OBRAS,
  "Cabeçalho da tabela Obras no mês (F3): o mês e a ordem (subtítulo) e os nomes das colunas (OBRA, IDC, NO MÊS, CAIXA). "
  "Fundo branco por cima do subtítulo antigo da casca.",
  linhas(
      "-- 1 · Leituras",
      "VAR _mesC = [Mês de referência · curto]",
      "-- 4 · Marcação",
      "RETURN",
      "    \"<div class='u obc'><span class='sub'>\" & _mesC & \" · IDC, variação no mês, caixa e justificativa\"",
      "        & \"</span><span class='vs' style='left:14px'>obra</span><span class='vs' style='left:150px'>IDC</span>\"",
      "        & \"<span class='vs' style='left:230px'>no mês</span><span class='vs' style='right:14px'>caixa</span></div>\"",
  ))
m("T4 · Obras · HTML linha", OBRAS,
  "Uma linha por obra com aba no mês de referência (granularidade dObra[Obra], ordem T1 · Obras · posição): nome, IDC "
  "com a marca dos pontos do item custo (cheio, parte, nenhum), a variação do IDC no mês (vermelha quando cai), o desvio "
  "de caixa do mês com a marca da faixa da previsão de caixa (preto também quando negativo) e, embaixo, a justificativa "
  "da planilha em até duas linhas; sem ela, 'em branco · exigida acima de ±10%' (vermelho, com a marca de pendência), "
  "'dentro de ±10%: não exigida' ou 'sem previsto no mês'. O limite vem de [Nota · limite caixa · ponto inteiro].",
  linhas(
      "-- 1 · Leituras",
      "VAR _obra = [Obra · nome]",
      "VAR _idc = [IDC · ref]",
      "VAR _var = [T4 · IDC · variação no mês · ref]",
      "VAR _ptc = [Nota · pontos custo · ref]",
      "VAR _psc = [Nota · possíveis · custo · ref]",
      "VAR _dv = [Desembolso · desvio no mês · ref]",
      "VAR _fx = [T4 · Desembolso · faixa do fluxo de caixa · ref]",
      "VAR _prev = [Desembolso · previsto no mês · ref]",
      "VAR _jus = [Justificativa do desembolso · ref]",
      "VAR _ex = [Justificativa · exigida · ref]",
      "VAR _lim = [Nota · limite caixa · ponto inteiro]",
      "VAR _pos = [T1 · Obras · posição]",
      "-- 2 · Textos",
      "VAR _chave = " + D.esc("_obra"),
      'VAR _tiTxt = FORMAT ( _idc, "0.00", "pt-BR" )',
      f'VAR _tvTxt = IF ( ISBLANK ( _var ), "", SWITCH ( TRUE (), _var > 0, "+", _var < 0, "{MENOS}", "" ) '
      '& FORMAT ( ABS ( _var ), "0.00", "pt-BR" ) )',
      D.pct("_dv", "_td", casas=0, mais=True),
      'VAR _clsC = IF ( ISBLANK ( _ptc ), "", IF ( _ptc >= _psc, "0", IF ( _ptc = 0, "2", "1" ) ) )',
      'VAR _txtLim = "±" & FORMAT ( _lim, "0%", "pt-BR" )',
      "VAR _d0 = ( MAX ( 1, _pos ) - 1 ) * 80 -- geometria",
      "VAR _temJus = NOT ISBLANK ( _jus ) && TRIM ( _jus ) <> \"\"",
      "VAR _htmlJus =",
      "    SWITCH (",
      "        TRUE (),",
      "        _temJus, \"<p class='js'>“\" & " + D.esc("TRIM ( _jus )") + " & \"”</p>\",",
      "        ISBLANK ( _prev ), \"<p class='js nx'>sem previsto no mês</p>\",",
      "        _ex = 1, \"<p class='js pd'><i class='pend a-pop' style='animation-delay:\" & ( _d0 + 300 ) & \"ms'></i>\" "
      "& \"em branco · exigida acima de \" & _txtLim & \"</p>\",",
      "        \"<p class='js nx'>dentro de \" & _txtLim & \": não exigida</p>\"",
      "    )",
      "-- 4 · Marcação",
      "RETURN",
      "    IF (",
      "        NOT ISBLANK ( _idc ),",
      "        \"<div class='u ob'><b class='nm'>\" & _chave & \"</b>\"",
      "            & \"<span class='ic'>\" & IF ( _clsC = \"\", \"\", \"<i class='mk a-pop mk\" & _clsC & \"' style='animation-delay:\" "
      "& _d0 & \"ms'></i>\" ) & " + C.marca("_tiTxt") + " & \"</span>\"",
      "            & \"<span class='vr\" & IF ( _var < 0, \" ng\", \"\" ) & \"'>\" & IF ( _tvTxt = \"\", \"\", " + C.marca("_tvTxt") + " ) & \"</span>\"",
      "            & \"<span class='cx'>\" & IF ( ISBLANK ( _fx ), \"\", \"<i class='mk a-pop mk\" & _fx & \"' style='animation-delay:\" "
      "& ( _d0 + 150 ) & \"ms'></i>\" )",
      "            & IF ( ISBLANK ( _dv ), \"—\", " + C.marca("_tdTxt") + " ) & \"</span>\"",
      "            & _htmlJus",
      "        & \"</div>\" & [Comum · JS contador]",
      "    )",
  ))

# ======================================================================================================== desembolso da carteira
DESC = rf"{TELA}\Desembolso da carteira"
css("T4 · Desembolso · CSS", DESC, "CSS das colunas do painel Desembolso da carteira (uma entrada por mês da janela).",
    "#htmlContent{display:flex!important;align-items:flex-start;width:100vw;height:100vh;margin:0!important;"
    "padding:0!important}"
    ".htmlViewerEntry{display:block!important;flex:1 1 0;min-width:0;margin:0!important;padding:0!important}"
    f".dc{{position:relative;height:{DES_H}px;transition:background .15s}}"
    ".dc:hover,.htmlViewerEntry.hover .dc{background:rgba(233,224,207,.3)}"
    f".dc .rz{{position:absolute;left:0;right:0;top:{DES_BASE}px;height:1px;background:#6B6B70}}"
    # largura e posição das barras vêm da medida (barra = mín(44; 0,36 × coluna)): previsto creme × desembolsado preto
    ".dc .bp,.dc .bd{position:absolute}"
    ".dc .bp{background:#E9E0CF}"
    ".dc .bd{background:#0B0B0C}"
    # desvio Barlow SemiBold 14 preto, também quando negativo (gastar menos não é alerta; decisão do Alisson)
    ".dc .dv{position:absolute;text-align:center;font-size:14px;line-height:17px;white-space:nowrap;color:#0B0B0C}"
    ".dc .dv.d13{font-size:13px}"
    f".dc .ms{{position:absolute;left:0;right:0;top:{DES_BASE + 8}px;text-align:center;"
    "font-size:13px;line-height:16px;color:#3B3B3F;white-space:nowrap}"
    ".dc .ms.ref{font-weight:600;color:#0B0B0C}.dc .ms.sem{opacity:.35}")
m("T4 · Desembolso · HTML coluna", DESC,
  "Um par de colunas por mês da janela (granularidade dMes[Mes]; coluna = 1068 ÷ n, barra = mín(44; 0,36 × coluna)): "
  "previsto (creme) × desembolsado (preto) na mesma escala, com o desvio sobre o previsto em cima (só as obras com "
  "previsto; preto também quando negativo; cabe em todo mês até 12; 13 px a partir de 10). Mês de referência em "
  "semibold; mês sem aba só com o rótulo apagado; o ano entra no primeiro mês e em janeiro quando a janela cruza a "
  "virada. As colunas correm da base em cascata e o desvio conta.",
  linhas(
      "-- 1 · Leituras",
      "VAR _noRecorte = [Série · mês até a referência]",
      "VAR _prev = [Desembolso · previsto no mês]",
      "VAR _real = [Desembolso · realizado no mês]",
      "VAR _desv = [T4 · Desembolso · desvio no mês · com previsto]",
      "VAR _topo = [T4 · Desembolso · topo da escala]",
      "VAR _mes = [Mês · abreviado]",
      "VAR _mesAno = [Mês · rótulo curto]",
      "VAR _data = [Mês · data]",
      "VAR _ehRef = [Série · é o mês de referência]",
      "VAR _pos = [Série · posição na janela]",
      "VAR _n = [Série · meses até a referência]",
      "VAR _ini = [Série · primeiro mês]",
      "VAR _ref = [Mês de referência]",
      "-- 2 · Textos",
      D.pct("_desv", "_td", casas=0, mais=True),
      D.od_tabela(), D.od_pct("_desv", "_td"),
      "VAR _cruza = YEAR ( _ini ) <> YEAR ( _ref )",
      'VAR _txtMes = _mes & IF ( _cruza && ( _pos = 1 || MONTH ( _data ) = 1 ), RIGHT ( _mesAno, 3 ), "" )',
      'VAR _clsMes = IF ( _ehRef = 1, " ref", "" ) & IF ( ISBLANK ( _real ) && ISBLANK ( _prev ), " sem", "" )',
      "-- 3 · Geometria",
      f"VAR _b = MIN ( {DES_BARRA}, ROUND ( 0.36 * {DES_W} / _n, 0 ) ) -- geometria",
      f"VAR _caixa = MIN ( 70, INT ( {DES_W} / _n ) ) -- geometria",
      "VAR _meiaCaixa = INT ( _caixa / 2 ) -- geometria",
      "VAR _xP = _b + 2 -- geometria",
      f"VAR _u = DIVIDE ( {DES_ALT}, _topo ) -- geometria",
      "VAR _hP = MAX ( 0, ROUND ( _prev * _u, 0 ) ) -- geometria",
      "VAR _hR = MAX ( 0, ROUND ( _real * _u, 0 ) ) -- geometria",
      f"VAR _yP = {DES_BASE} - _hP -- geometria",
      f"VAR _yR = {DES_BASE} - _hR -- geometria",
      "VAR _yRot = MIN ( _yP, _yR ) - 21 -- geometria",
      "VAR _atraso = ( _pos - 1 ) * 100 -- geometria",
      f"VAR _corre = \"' data-rp='top,height' data-r0-top='{DES_BASE}px' data-r0-height='0px' data-rd='\"",
      'VAR _clsDv = IF ( _n >= 10, " d13", "" )',
      "-- 4 · Marcação",
      "VAR _htmlBarras =",
      "    IF (",
      "        NOT ISBLANK ( _real ) || NOT ISBLANK ( _prev ),",
      "        \"<i class='bp' style='top:\" & _yP & \"px;height:\" & _hP & \"px;left:calc(50% - \" & _xP & \"px);width:\" & _b",
      "            & \"px' data-rk='\" & _mes & \"|p\" & _corre & _atraso & \"'></i>\"",
      "            & \"<i class='bd' style='top:\" & _yR & \"px;height:\" & _hR & \"px;left:calc(50% + 1px);width:\" & _b",
      "            & \"px' data-rk='\" & _mes & \"|d\" & _corre & ( _atraso + 50 ) & \"'></i>\"",
      "            & IF (",
      "                NOT ISBLANK ( _desv ),",
      "                \"<span class='dv b6 a-fd\" & _clsDv & \"' style='animation-delay:\" & ( _atraso + 250 ) & \"ms;top:\" "
      "& _yRot & \"px;left:calc(50% - \" & _meiaCaixa",
      "                    & \"px);width:\" & _caixa & \"px'>\" & _tdOd & \"</span>\"",
      "            )",
      "    )",
      "RETURN",
      "    IF (",
      "        _noRecorte = 1,",
      "        \"<div class='u dc'><i class='rz a-fd'></i>\" & _htmlBarras",
      "            & \"<p class='ms a-fd\" & _clsMes & \"' style='animation-delay:\" & _atraso & \"ms'>\" & _txtMes & \"</p>\"",
      "        & \"</div>\" & [Comum · JS contador] & [Comum · JS corrida]",
      "    )",
  ))

if __name__ == "__main__":
    sys.exit(gravar(MEDIDAS, RAIZ / "dax" / "T4", GERADO))

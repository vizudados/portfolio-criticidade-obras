#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tooltips_t4 — desenho dos tooltips de página da Tela 04 (pbi/dax/T4/Tooltips/**). As contas estão em contas_t4.py
(pasta T4 Resultado no tempo\\Tooltips\\Contas) e em base/.

Figma: seção Interações · Tela 04 (304:3105) — Tooltip · T4 · Mês 306:3416 (· primeiro mês 306:3478), Obra 307:3713
(e o estado 307:3757, da régua antiga), Mês do desembolso 308:3713 (· primeiro mês 308:3787), Obra do desembolso 309:3713 (· em
branco 309:3766, · não exigida 309:3823). Linguagem: docs/06-interacoes-spec.md §1.6 e docs/06-interacoes-spec-t4.md §3.
Cartão 480 de largura com cantos retos (CSS comum do tooltip), cabeçalho preto 54 px, corpo em fluxo; a linha de dados
e o rodapé de uma linha ficam presos à base do cartão (a página de tooltip tem uma altura só; o que sobra nos estados
mais curtos vira respiro entre o gráfico e o pé, não um vão no fim). Uma série por mini gráfico, sem eixo nem grade;
rótulo só no mês do ponto e no extremo oposto. Janela de 1 a 12 meses (Figma 350:7993, nota 350:7996): coluna = 447 ÷ n
(flex), barra = mín(40; 0,55 × coluna); o rótulo da referência encosta na borda direita e o do extremo fica centrado na
sua coluna, preso à área, e recua para a esquerda quando encostaria no da referência na mesma altura. Lista de
justificativas: os 6 meses mais recentes, um por linha; os anteriores da janela numa linha de resumo.

Listas de uma obra por linha (mês e mês do desembolso; Figma 362:8044, 362:8161, 362:8288 e nota 362:8377): a página
tem a altura do pior caso, 10 obras na lista (402); o corpo para 9 px acima da régua do pé (.corpo.lim) e nunca o
invade. De 11 obras em diante, as 9 de maior peso no mês (|R$| ou |desvio|), na ordem de sempre, e a linha "e mais N
obras"; N é conta (contas_t4.py, T4 · Tooltip … · obras fora da lista).

Barras divergentes das listas de mês (Figma 366:7993, ago/26 com desvios negativos; nota 366:8262): o zero fica no meio
da coluna da barra e a escala é simétrica (o maior |valor| da lista ocupa a meia coluna, dos dois lados), então positivo
cresce para a direita, negativo para a esquerda e nenhum invade os números. Mês do desembolso: previsto alinhado à
direita até 242, × 246, desembolsado 258, barra 350–430 (zero 390, ±40), % à direita (F4: colunas para a direita, para
caber CAJUEIRO com o selo e "sem previsto"). Rodapé das justificativas: "P de E
preenchidas · em branco: " e os nomes do maior |desvio| para o menor, sem cortar nome (justificativas_rodape.py).

    python -X utf8 pbi/scripts/tooltips_t4.py
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import contador as C  # noqa: E402
import desenho_projeto as D  # noqa: E402
import desenho_comum as DC  # noqa: E402
import tooltip_lib as TL  # noqa: E402
from contas_lib_projeto import Medida, gravar  # noqa: E402
from desenho_comum import dax_lit  # noqa: E402
import justificativas_rodape as R  # noqa: E402

RAIZ = AQUI.parent
GERADO = "pbi/scripts/tooltips_t4.py"
DES = r"T4 Resultado no tempo\Tooltips"
MEDIDAS: list[Medida] = []
MENOS = D.MENOS

# redesenho v2 (07/10/2026; Figma 389:1528, t04.md §2–§6): páginas de 560 de largura (gráfico de colunas pode passar
# disso, nunca ficar abaixo) e corpo de 520 (margens de 20). Alturas: mês e mês do desembolso 480 = pior caso de 10
# obras na lista (cabeçalho 72 + 16 + versalete 24 + 10 × 28 + pé 75 com folga; o cabeçalho de 94, quando a meta desce
# para a 2ª linha, só acontece no primeiro mês, que não tem rodapé); obra 324 (a trajetória do resultado % que saiu do
# painel Resultado por obra, fase 5); obra do desembolso 596 (fase 5: a justificativa do mês de referência em até 2
# linhas, que saiu do painel Desembolso por obra, e o histórico dos 5 meses anteriores + resumo, em linhas de 29).
LARGURA = 560
ALTURA = {"mes": 480, "obra": 324, "mesdes": 480, "obrades": 596}
LISTA_MAX, LISTA_MOSTRA = 10, 9     # até 10 obras na lista, todas; de 11 em diante, 9 e "e mais N obras"
# barras divergentes das listas de mês (coordenadas da linha, corpo de 520): zero no meio da coluna da barra, escala
# simétrica (o maior |valor| da lista ocupa a meia coluna, dos dois lados); positivo para a direita, negativo para a
# esquerda, nunca sobre os números. Contribuição: positivo preto, negativo vermelho. Desvio do desembolso: as duas
# pontas na cor da faixa da previsão de caixa da nota, nunca pelo sinal (régua antiga, 13/10/2026: o desvio conta para mais
# ou para menos, então gastar 20% abaixo também cai na faixa crítica; antes só o negativo ia pela faixa, sempre estável).
# F4 (28/10/2026, varredura com o nome mais longo, CAJUEIRO + selo REAL ≈ 155 a 17 px, e "sem previsto"): as colunas
# andaram para a direita para nada encostar no nome
MES_ZERO, MES_MEIA = 240, 72        # contribuição de cada obra: coluna 168–312; R$ à direita em 420; % em 520
DES_ZERO, DES_MEIA = 390, 40        # desvio do desembolso: coluna 350–430; % à direita em 520
PV_FIM, X_X, DS_X = 242, 246, 258   # previsto (Segoe 14, alinhado à direita até 242), ×, desembolsado (Barlow 16)
# linha de dados do pé no mês do desembolso (corpo 520, Segoe 14): JUSTIFICATIVAS ~105, vãos 10 + 6, "P de E" (Barlow
# 16: ~11 px por algarismo + 24), "preenchidas · " ~90; o resto é o trecho dos nomes. A tabela de larguras de
# justificativas_rodape.py é de Segoe 13: o espaço entra convertido (× 13 ÷ 14).
JUS_W, JUS_VS, JUS_GAP, JUS_PRE, JUS_FOLGA = 520, 105, 16, 90, 2
# trajetória do resultado % no tooltip da obra (Figma 390:2151): área 520 × 124, o maior positivo + o maior negativo da
# obra ocupam SL_ESC px a partir de y SL_TOPO (zero no meio quando tudo é zero); eixo dos meses em SL_EIXO
SL_H, SL_TOPO, SL_ESC, SL_EIXO = 124, 21, 60, 108


def desenho(nome, descricao, dax):
    """Medida de desenho; os valores marcados com C.marca() viram odômetro no fim (F4)."""
    MEDIDAS.append(Medida(nome, DES, "texto", descricao, C.envolver_marcas(dax)))


def linhas(*ls) -> str:
    def plano(x):
        for g in x:
            if isinstance(g, list):
                yield from plano(g)
            else:
                yield g
    return "\n".join(plano(ls))


def extenso(v: str, fem: bool = True) -> str:
    nomes = (["nenhuma", "uma", "duas"] if fem else ["nenhum", "um", "dois"]) + \
        ["três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez", "onze", "doze"]
    casos = ", ".join(f'{i}, "{n}"' for i, n in enumerate(nomes))
    return f'SWITCH ( {v}, {casos}, FORMAT ( {v}, "0" ) )'


def cap(v: str) -> str:
    return f"UPPER ( LEFT ( {v}, 1 ) ) & MID ( {v}, 2, LEN ( {v} ) )"


def nome_mes(v: str) -> str:
    return f'FORMAT ( {v}, "mmmm", "pt-BR" )'


def lista_e(v: str, p: str) -> list[str]:
    """{p}Txt = "A, B e C" a partir de "A|B|C"; {p}N = quantos (só decide o texto)."""
    return [
        f'VAR {p}N = IF ( ISBLANK ( {v} ) || {v} = "", 0, PATHLENGTH ( {v} ) )',
        f'VAR {p}Pos = IF ( {p}N >= 2, FIND ( "§", SUBSTITUTE ( {v}, "|", "§", {p}N - 1 ) ) )',
        f'VAR {p}Txt = SWITCH ( TRUE (), {p}N = 0, "", {p}N = 1, {v}, '
        f'SUBSTITUTE ( LEFT ( {v}, {p}Pos - 1 ), "|", ", " ) & " e " & MID ( {v}, {p}Pos + 1, 999 ) )',
    ]


def selo(var_selo: str) -> str:
    return (f"\"<span class='selo \" & IF ( {var_selo} = \"REAL\", \"selo-r\", \"selo-i\" ) & \"'>\" & {var_selo} "
            f"& \"</span>\"")


def selo_real(var_selo: str) -> str:
    """Nas listas só a CAJUEIRO (REAL) leva selo; as ilustrativas não (spec T4 §1)."""
    return f"IF ( {var_selo} = \"REAL\", \"<span class='selo selo-r'>REAL</span>\", \"\" )"


def rs_linha(v: str, p: str, r: str) -> list[str]:
    """Dentro de uma linha (CONCATENATEX): {p}Txt = "−R$ 354 mil" e {p}Od = o mesmo com o núcleo contando."""
    return [
        f"{r}VAR {p}A = ABS ( {v} )",
        f'{r}VAR {p}Nu = SWITCH ( TRUE (), {p}A >= 999500, FORMAT ( {p}A / 1000000, "0.00", "pt-BR" ), '
        f'{p}A >= 999.5, FORMAT ( {p}A / 1000, "0", "pt-BR" ), FORMAT ( {p}A, "#,0", "pt-BR" ) )',
        f'{r}VAR {p}Un = SWITCH ( TRUE (), {p}A >= 999500, " mi", {p}A >= 999.5, " mil", "" )',
        f'{r}VAR {p}S = IF ( {v} < 0 && {p}Nu <> "0", "{MENOS}", "" )',
        C.bloco_od(p + "K", p + "Nu", recuo=r).rstrip(),
        f'{r}VAR {p}Txt = {p}S & "R$ " & {p}Nu & {p}Un',
        f'{r}VAR {p}Od = {p}S & "R$ " & {p}KOd & {p}Un',
    ]


def pct_linha(v: str, p: str, r: str, casas: int) -> list[str]:
    """Dentro de uma linha: {p}Txt = "+0,40%" (casas decimais) e {p}Od com o núcleo contando."""
    fmt = "0." + "0" * casas if casas else "0"
    return [
        f'{r}VAR {p}R = ROUND ( {v} * 100, {casas} )',
        f'{r}VAR {p}S = SWITCH ( TRUE (), {p}R > 0, "+", {p}R < 0, "{MENOS}", "" )',
        f'{r}VAR {p}Nu = FORMAT ( ABS ( {v} ) * 100, "{fmt}", "pt-BR" )',
        C.bloco_od(p + "K", p + "Nu", recuo=r).rstrip(),
        f'{r}VAR {p}Txt = {p}S & {p}Nu & "%"',
        f'{r}VAR {p}Od = {p}S & {p}KOd & "%"',
    ]


# ===================================================================================================== CSS
# CSS v2 completo dos tooltips da T4 (não depende do 'Comum · CSS tooltip' da T1, que ainda é v1): corpo BRANCO (pedido
# do Alisson, 07/10/2026; só o cabeçalho segue preto),
# contorno 1 px preto, cantos retos; cabeçalho preto em fluxo (72; 94 quando a meta desce para a 2ª linha — flex-wrap
# com 24 de folga); corpo flexível; pé (régua + linha de dados + rodapé de uma linha) preso à base.
CSS_T4 = (
    ".tt{position:fixed;inset:0;display:flex;flex-direction:column;background:#FFFFFF;border:1px solid #0B0B0C;"
    "border-radius:0;overflow:hidden;color:#0B0B0C}"
    ".tt .vs{display:block}"
    ".tt .cab{flex:none;background:#0B0B0C;padding:14px 20px 13px}"
    ".tt .cab>.vs{color:#E9E0CF}"
    ".tt .cab .lin1{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;column-gap:24px;"
    "row-gap:6px;margin-top:4px}"
    ".tt .cab .tit{display:flex;align-items:baseline;gap:8px;white-space:nowrap}"
    ".tt .cab .tit b{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:21px;line-height:26px;"
    "color:#FFFFFF}"
    ".tt .cab .tit em{font-style:normal;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:12px;"
    "line-height:15px;letter-spacing:1.2px;text-transform:uppercase;color:#E9E0CF}"
    ".tt .cab .dir{color:#E9E0CF;white-space:nowrap}"
    ".tt .corpo{flex:1 1 auto;min-height:0;overflow:hidden;position:relative;margin:16px 20px 0}"
    ".tt .bh{display:flex;justify-content:space-between;margin-bottom:9px}"
    ".tt .rg{height:1px;background:#E1E1E1;margin:10px 0 10px}"
    ".tt .pe{flex:none;margin:8px 20px 14px;padding-top:12px;border-top:1px solid #E1E1E1}"
    ".tt .dd{display:flex;align-items:baseline;gap:10px;white-space:nowrap;height:20px}"
    ".tt .dd b{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:16px;line-height:20px}"
    ".tt .dd .dt{margin-left:-4px;font-size:14px;line-height:19px;color:#3B3B3F;overflow:hidden;text-overflow:ellipsis}"
    # F4: o rodapé quebra em duas linhas em vez de cortar com reticências (o corpo encolhe e a lista se ajusta)
    ".tt .rod{margin-top:8px;font-size:14px;line-height:19px}"
    ".tt .pe .rod:first-child{margin-top:0}"
    # listas de uma obra por linha (mês e mês do desembolso), linhas de 28
    ".tt .lc{position:relative;height:28px;white-space:nowrap}"
    ".tt .lc .mk{position:absolute;left:0;top:9px}"
    ".tt .lc .nm{position:absolute;left:19px;top:4px;display:flex;align-items:center;gap:7px;"
    "font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:16px;line-height:20px}"
    ".tt .lc .bz{position:absolute;top:8px;height:12px;background:#0B0B0C}"
    ".tt .lc .bz.ng{background:#C43737}"
    ".tt .lc .bz.s0{background:#A9CDB9;box-shadow:inset 0 0 0 1px #6E9F85}"
    ".tt .lc .bz.s1{background:#C9821F}.tt .lc .bz.s2{background:#C43737}"
    ".tt .lc .v{position:absolute;right:100px;top:4px;text-align:right;font-family:'Barlow U','Segoe UI',sans-serif;"
    "font-weight:600;font-size:16px;line-height:20px}"
    ".tt .lc .p{position:absolute;right:0;top:3px;text-align:right;font-size:15px;line-height:21px;color:#3B3B3F}"
    f".tt .lc .pv{{position:absolute;right:{520 - PV_FIM}px;top:4px;text-align:right;font-size:14px;line-height:19px;"
    "color:#3B3B3F}"
    f".tt .lc .px{{position:absolute;left:{X_X}px;top:4px;font-size:14px;line-height:19px;color:#3B3B3F}}"
    f".tt .lc .ds{{position:absolute;left:{DS_X}px;top:4px;font-family:'Barlow U','Segoe UI',sans-serif;"
    "font-weight:600;font-size:16px;line-height:20px}"
    ".tt .lc .p.dv{top:4px;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:16px;"
    "line-height:20px;color:#0B0B0C}"
    ".tt i.vz{display:block;font-style:normal;color:#3B3B3F;font-size:14px;line-height:19px}"
    ".tt i.vz.mais{line-height:28px;padding-left:19px}"
    # mini série por mês (coluna = 520 ÷ n; largura e posição da barra e dos rótulos vêm da medida); cor da barra =
    # faixa do indicador no mês (estável sálvia, atenção ocre, crítico vermelho)
    ".tt .sr{position:relative;display:flex;margin-top:9px}"
    ".tt .sr .c{position:relative;flex:1 1 0;min-width:0}"
    ".tt .sr .c .bar{position:absolute}"
    ".tt .sr .c .bar.s2{background:#C43737}.tt .sr .c .bar.s1{background:#C9821F}"
    ".tt .sr .c .bar.s0{background:#A9CDB9;box-shadow:inset 0 0 0 1px #6E9F85}"
    ".tt .sr .c .val{position:absolute;z-index:2;text-align:center;font-family:'Barlow U','Segoe UI',"
    "sans-serif;font-weight:600;font-size:14px;line-height:17px;white-space:nowrap;color:#0B0B0C}"
    ".tt .sr .c .val.ext{color:#3B3B3F}"
    ".tt .sr .c .ms{position:absolute;left:0;right:0;text-align:center;font-size:13px;line-height:16px;"
    "color:#3B3B3F;white-space:nowrap}"
    ".tt .sr .c .ms.ref{font-weight:600;color:#0B0B0C}.tt .sr .c .ms.sem{opacity:.45}"
    # histórico das justificativas (obra do desembolso), linhas de 29: mês Segoe SemiBold 15, texto Segoe 15
    ".tt .jl{display:grid;grid-template-columns:72px 1fr;align-items:center;height:29px;white-space:nowrap}"
    ".tt .jl .m{font-size:15px;line-height:21px;font-weight:600}"
    ".tt .jl .t{font-size:15px;line-height:21px;overflow:hidden;text-overflow:ellipsis}"
    ".tt .jl .t.ne{color:#6B6B70}"
    ".tt .jl .chp{justify-self:start}"
    # justificativa do mês de referência (obra do desembolso, fase 5): o texto da aba em até 2 linhas, o chip de
    # pendência (comum) ou "dentro de ±10%: não exigida" / "sem previsto no mês" em terciário
    ".tt .jr{min-height:21px}"
    ".tt .jr .t{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;font-size:15px;"
    "line-height:21px;white-space:normal;overflow-wrap:anywhere}"
    ".tt .jr .t.ne{color:#6B6B70}"
    # trajetória do resultado % da obra (fase 5, veio do painel): área 520 × 124, SVG em décimos de px; zero
    # pontilhado terciário, linha 2 px preta acima do zero e vermelha abaixo, pontos; rótulos e eixo em HTML
    f".tt .sl{{position:relative;height:{SL_H}px;margin-top:9px}}"
    ".tt .sl svg{position:absolute;left:0;top:0;overflow:visible}"
    ".tt .sl .z{stroke:#6B6B70;stroke-width:10;stroke-dasharray:20 30;fill:none}"
    ".tt .sl .t{stroke:#0B0B0C;stroke-width:20;fill:none;stroke-linejoin:round;stroke-linecap:round}"
    ".tt .sl .t.n{stroke:#C43737}"
    ".tt .sl circle{fill:#0B0B0C}.tt .sl circle.n{fill:#C43737}"
    ".tt .sl .val{position:absolute;z-index:2;text-align:center;font-family:'Barlow U','Segoe UI',sans-serif;"
    "font-weight:600;font-size:14px;line-height:17px;white-space:nowrap;color:#0B0B0C}"
    ".tt .sl .val.ext{color:#3B3B3F}"
    f".tt .sl .ms{{position:absolute;top:{SL_EIXO}px;text-align:center;font-size:13px;line-height:16px;color:#3B3B3F;"
    "white-space:nowrap}"
    ".tt .sl .ms.ref{font-weight:600;color:#0B0B0C}.tt .sl .ms.sem{opacity:.45}"
    "@keyframes ttFim{from{opacity:0}}"
    ".tt .fim{animation:ttFim .2s ease-out backwards}"
    # obra: a linha do título do gráfico divide com os pontos do Orçamento na nota (sem somar altura ao tooltip)
    ".tt .bh+.sl{margin-top:0}.tt .bh .mk{margin-right:6px}"
    "@media (prefers-reduced-motion:reduce){.tt .fim{animation:none}}"
)
# F4 (pedido do Alisson, 28/10/2026; tooltip_lib): as listas de uma obra por linha e o histórico das justificativas
# ocupam o corpo inteiro, com linhas e fonte pela contagem; os filhos da linha (em posição fixa) ficam centrados na
# altura dela. Colunas em posição fixa: a lista do mês cresce até 17 px; a do mês do desembolso (previsto alinhado
# até 200, colado ao nome) só diminui. Cascata C5 em tudo: cabeçalho, blocos do corpo, cada linha e o pé.
FONTES_MES = {".tt .ls .lc .nm": 16, ".tt .ls .lc .v": 16, ".tt .ls .lc .p": 15, ".tt .ls>.mais": 14}
FONTES_DES = {".tt .ld .lc .nm": 16, ".tt .ld .lc .pv": 14, ".tt .ld .lc .px": 14, ".tt .ld .lc .ds": 16,
              ".tt .ld .lc .p.dv": 16, ".tt .ld>.mais": 14}
FONTES_JL = {".tt .jls .jl .m": 15, ".tt .jls .jl .t": 15}
CSS_F4_LISTAS = (
    TL.css_escala(FONTES_MES, teto=17)
    + TL.css_fontes(FONTES_DES, teto=0) + TL.css_fontes(FONTES_JL, teto=19)
    + ".tt .ls .lc>*,.tt .ls .lc>.dv{top:50%;translate:0 -50%;line-height:1.25}"
    ".tt .ls>.mais{display:flex;align-items:center;line-height:1.25}"
    ".tt .ls .jl>*{line-height:1.3}"
    # justificativa longa quebra em vez de cortar com reticências; a linha não encolhe abaixo do texto
    # (sem a altura fixa de 29 da .jl: com ela, o mínimo automático parava em 29 e a 2ª linha invadia a de baixo)
    ".tt .ls>.jl{min-height:auto;height:auto}"
    ".tt .ls .jl .t{white-space:normal;overflow:visible;text-overflow:clip;overflow-wrap:anywhere}"
)
CSS_F4 = CSS_F4_LISTAS + TL.entrada(
    ".tt .ls>:nth-child({k})",
    [".tt .corpo>.bh", ".tt .corpo>.vs", ".tt .sr", ".tt .rg", ".tt .jr"], pe=".tt .pe")
desenho("T4 · Tooltip · CSS", "CSS v2 dos tooltips de página da T4 (completo, sobre o CSS base): cabeçalho preto com a "
        "meta que desce para a 2ª linha quando não cabe, pé preso à base, linhas por obra com barra divergente, mini "
        "série por mês pela faixa e histórico das justificativas.",
        "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(CSS_T4 + CSS_F4))


def cabecalho_mes(sob: str) -> list[str]:
    """Cabeçalho dos tooltips de mês: só sobretítulo e título (a meta "N OBRAS COM ABA · X SEM PLANILHA" saiu a
    pedido do Alisson, 07/10/2026: "sem necessidade")."""
    return [
        "        \"<div class='u tt'><div class='cab'><p class='vs'>\" & " + sob + " & \"</p>\"",
        "            & \"<div class='lin1'><div class='tit'><b>\" & _mesL & \"</b></div></div></div>\"",
    ]


LEITURAS_MES = [
    "VAR _mesC = UPPER ( [Mês · rótulo curto] )",
    "VAR _mesL = [Mês · longo]",
    "VAR _mesAnt = [Mês anterior · nome]",
    "VAR _n = [Obras com análise] + 0",
    "VAR _primeiro = [Mês · é o primeiro do histórico] = 1",
]

# ===================================================================================================== 3.1 Mês
desenho(
    "T4 · Tooltip mês · HTML",
    "Tooltip de página do mês (coluna de Resultado da carteira, mês a mês): o resultado aplicado de cada obra no mês, do "
    "maior ao menor (marca do status da obra na nota, tracejada quando pendente; barra divergente de zero comum, R$ e % "
    "do orçamento), o que ainda vai se realizar (a distância até o traço da planilha) contra o mês anterior e, fora do "
    "primeiro mês, quantas obras caíram ou subiram no aplicado (F3). Até "
    f"{LISTA_MAX} obras, todas aparecem; de {LISTA_MAX + 1} em diante, as {LISTA_MOSTRA} de maior peso e 'e mais N obras'.",
    linhas(
        "-- 1 · Leituras",
        LEITURAS_MES,
        "VAR _ativ = [A realizar]",
        "VAR _ativAnt = [T4 · A realizar · mês anterior]",
        "VAR _nC = [T4 · Obras que caíram no mês]",
        "VAR _nS = [T4 · Obras que subiram no mês]",
        "VAR _m = [T4 · Obras comparáveis no mês]",
        "VAR _listaS = [T4 · Obras que subiram no mês (lista)]",
        "VAR _listaC = [T4 · Obras que caíram no mês (lista)]",
        "VAR _mais = [T4 · Tooltip mês · obras fora da lista]",
        "VAR _obras =",
        "    ADDCOLUMNS (",
        "        VALUES ( dObra[Obra] ),",
        "        \"@r\", [Resultado aplicado],",
        "        \"@p\", [Resultado aplicado %],",
        "        \"@st\", [Nota · status · um mês],",
        "        \"@pend\", [Nota · pendente · um mês],",
        "        \"@selo\", [Obra · selo]",
        "    )",
        "VAR _comAba = FILTER ( _obras, NOT ISBLANK ( [@r] ) ) /* geometria */",
        f"/* passou de {LISTA_MAX} obras: as {LISTA_MOSTRA} de maior peso no mês (|R$|), na ordem de sempre, e a linha "
        "'e mais N obras' */",
        f"VAR _mostra = TOPN ( IF ( _mais > 0, {LISTA_MOSTRA}, {LISTA_MAX} ), _comAba, ABS ( [@r] ), DESC, "
        "dObra[Obra], ASC ) /* geometria */",
        "-- 2 · Textos",
        D.od_tabela(),
        D.rs("_ativ", "_ta") + D.rs("_ativAnt", "_taa"), D.od_rs("_ativ", "_ta"),
        lista_e("_listaS", "_ls"), lista_e("_listaC", "_lc"),
        "VAR _txtSob = IF ( _primeiro, \"RESULTADO MÊS A MÊS · \" & _mesC & \" · PRIMEIRO MÊS DO HISTÓRICO\", "
        "\"RESULTADO DA CARTEIRA, MÊS A MÊS · \" & _mesC )",
        "VAR _txtAtivAnt = IF ( ISBLANK ( _ativAnt ), \"sem mês anterior\", _mesAnt & \" \" & " + C.marca("_taaTxt") + " )",
        "VAR _txtRod =",
        "    SWITCH (",
        "        TRUE (),",
        "        _primeiro || _m = 0, \"\",",
        "        _nC = _m, \"Caiu em todas as \" & " + extenso("_m") + " & \" obras desde \" & _mesAnt & \".\",",
        "        _nS = _m, \"Subiu em todas as \" & " + extenso("_m") + " & \" obras desde \" & _mesAnt & \".\",",
        "        _nC >= _nS,",
        "            \"Caiu em \" & " + extenso("_nC") + " & \" das \" & " + extenso("_m") + " & \" obras desde \" & _mesAnt "
        "& IF ( _nS = 0, \"; as outras ficaram iguais.\", \"; só \" & _lsTxt & IF ( _nS = 1, \" subiu.\", \" subiram.\" ) ),",
        "        \"Subiu em \" & " + extenso("_nS") + " & \" das \" & " + extenso("_m") + " & \" obras desde \" & _mesAnt "
        "& IF ( _nC = 0, \"; nenhuma caiu.\", \"; só \" & _lcTxt & IF ( _nC = 1, \" caiu.\", \" caíram.\" ) )",
        "    )",
        "-- 3 · Geometria",
        "VAR _max = MAXX ( _comAba, ABS ( [@r] ) ) /* geometria */",
        "-- 4 · Marcação",
        "VAR _htmlLinhas =",
        "    CONCATENATEX (",
        "        _mostra,",
        "        VAR _r = [@r]",
        rs_linha("_r", "_v", "        "),
        pct_linha("[@p]", "_q", "        ", 2),
        f"        VAR _w = MAX ( 1, ROUND ( DIVIDE ( ABS ( _r ), _max ) * {MES_MEIA}, 0 ) ) -- geometria",
        f"        VAR _x = IF ( _r >= 0, {MES_ZERO}, {MES_ZERO} - _w ) -- geometria",
        f"        VAR _corre = IF ( _r < 0, \" data-rp='left,width' data-r0-left='{MES_ZERO}px'\" )",
        "        VAR _clsBz = IF ( _r < 0, \" ng\", \"\" )",
        f"        VAR _ngV = IF ( _vS = \"{MENOS}\", \" ng\", \"\" )",
        f"        VAR _ngQ = IF ( _qS = \"{MENOS}\", \" ng\", \"\" )",
        "        VAR _cls = " + DC.cls_status("[@st]", "[@pend]"),
        "        RETURN",
        "            \"<div class='lc'>\" & IF ( _cls = \"\", \"\", \"<i class='mk mk\" & _cls & \"'></i>\" ) "
        "& \"<span class='nm'>\" & dObra[Obra] & "
        + selo_real("[@selo]") + " & \"</span>\"",
        "                & \"<i class='bz\" & _clsBz & \"' style='left:\" & _x & \"px;width:\" & _w & \"px'\" & _corre "
        "& \" data-rk='\" & dObra[Obra] & \"' data-rd='\" & ( RANKX ( _mostra, [@r], _r, DESC ) - 1 ) * 60 & \"'></i>\" "
        "/* geometria */",
        "                & \"<span class='v\" & _ngV & \"'>\" & _vOd & \"</span><span class='p\" & _ngQ & \"'>\" & _qOd "
        "& \"</span></div>\",",
        "        \"\",",
        "        [@r], DESC,",
        "        dObra[Obra], ASC",
        "    )",
        "VAR _htmlMais = IF ( _mais > 0, \"<i class='vz mais'>e mais \" & " + C.marca('FORMAT ( _mais, "0" )') + " "
        "& \" obras, com resultado mais perto de zero</i>\" )",
        "VAR _nLs = COUNTROWS ( _mostra ) + IF ( _mais > 0, 1, 0 ) /* lista */",
        "RETURN",
        "    IF (",
        "        _n > 0,",
        cabecalho_mes("_txtSob"),
        "            & \"<div class='corpo lim'><div class='bh'><span class='vs'>RESULTADO APLICADO DE CADA OBRA · R$ NO MÊS</span>\"",
        "            & \"<span class='vs'>% DO ORÇ.</span></div><div class='lsb\" & " + TL.atributos("_nLs") + "'>\" & _htmlLinhas & _htmlMais & \"</div></div>\"",
        "            & \"<div class='pe'><div class='dd'><span class='vs'>A REALIZAR (ATÉ O TRAÇO DA "
        "PLANILHA)</span>\"",
        "            & \"<b>\" & _taOd & \"</b><span class='dt'>· \" & _txtAtivAnt & \"</span></div>\"",
        "            & IF ( _txtRod <> \"\", \"<p class='rod'>\" & " + D.esc("_txtRod") + " & \"</p>\" )",
        "        & \"</div></div>\" & [Comum · JS contador tooltip] & [Comum · JS corrida]",
        "    )",
    ))


# ===================================================================================================== série por mês (3.2 e 3.4)
TT_W = 520                  # largura útil do corpo do tooltip v2 (560 − 20 − 20)
TT_COMPACTO = 7             # a partir de quantos meses o rótulo em R$ perde o "R$" (o versalete já diz "R$")
CHAR_PX = {"rs": 6.5, "pct": 8.5}   # largura média de um caractere do rótulo (Barlow SemiBold 14, medida no Figma)


def serie_mes(valor: str, status: str, fmt: str, neg_vermelho: bool = True) -> list[str]:
    """VARs da mini série da obra por mês da janela: _htmlSerie e _altSerie. `valor`/`status` são as medidas lidas por
    mês; fmt = "rs" ou "pct" (desvio, sem casa). Coluna = 447 ÷ n (flex), barra = mín(40; 0,55 × coluna), par de px;
    rótulo só na referência e no extremo oposto, centrado na sua coluna e preso à área (0 a 447); se o do extremo
    encostaria no da referência na mesma altura, recua para a esquerda até ficar a 6 px dele. Em R$, de 7 meses em
    diante o rótulo perde o "R$" (o versalete do gráfico já diz a unidade)."""
    f = CHAR_PX[fmt]
    if fmt == "rs":
        rotulo = rs_linha("_v", "_t", "        ") + [
            "        VAR _tLab = IF ( _compacto, _tS & _tNu & _tUn, _tTxt )",
            "        VAR _tLabOd = IF ( _compacto, _tS & _tKOd & _tUn, _tOd )",
        ]
        ref_lab = [
            "VAR _rA = ABS ( _vRef )",
            'VAR _rNu = SWITCH ( TRUE (), _rA >= 999500, FORMAT ( _rA / 1000000, "0.00", "pt-BR" ), _rA >= 999.5, '
            'FORMAT ( _rA / 1000, "0", "pt-BR" ), FORMAT ( _rA, "#,0", "pt-BR" ) )',
            'VAR _rUn = SWITCH ( TRUE (), _rA >= 999500, " mi", _rA >= 999.5, " mil", "" )',
            f'VAR _rLab = IF ( _vRef < 0, "{MENOS}", "" ) & IF ( _compacto, "", "R$ " ) & _rNu & _rUn',
        ]
    else:
        rotulo = pct_linha("_v", "_t", "        ", 0) + [
            "        VAR _tLab = _tTxt",
            "        VAR _tLabOd = _tOd",
        ]
        ref_lab = [
            f'VAR _rLab = SWITCH ( TRUE (), ROUND ( _vRef * 100, 0 ) > 0, "+", ROUND ( _vRef * 100, 0 ) < 0, "{MENOS}", '
            '"" ) & FORMAT ( ABS ( _vRef ) * 100, "0", "pt-BR" ) & "%"',
        ]
    return [
        "VAR _n = [Série · meses até a referência]",
        "VAR _meses =",
        "    ADDCOLUMNS (",
        "        VALUES ( dMes[Mes] ),",
        "        \"@ate\", [Série · mês até a referência],",
        "        \"@pos\", [Série · posição na janela],",
        "        \"@rot\", [Mês · abreviado],",
        f"        \"@v\", [{valor}],",
        f"        \"@st\", [{status}]",
        "    )",
        "VAR _serie = FILTER ( _meses, [@ate] = 1 ) /* lista */",
        "VAR _com = FILTER ( _serie, NOT ISBLANK ( [@v] ) ) /* lista */",
        "VAR _vMax = MAXX ( _com, [@v] ) /* lista */",
        "VAR _vMin = MINX ( _com, [@v] ) /* lista */",
        "VAR _vRef = MAXX ( FILTER ( _com, dMes[Mes] = _ref ), [@v] ) /* lista */",
        "VAR _ext = IF ( _vMax - _vRef >= _vRef - _vMin, _vMax, _vMin ) /* lista */",
        "VAR _mesExt = MINX ( FILTER ( _com, [@v] = _ext && dMes[Mes] <> _ref ), dMes[Mes] ) /* lista */",
        f"VAR _compacto = _n >= {TT_COMPACTO}",
        ref_lab,
        "-- 3 · Geometria",
        "VAR _pos = MAX ( 0, _vMax ) -- geometria",
        "VAR _neg = MAX ( 0, - _vMin ) -- geometria",
        "VAR _esc = DIVIDE ( 60, _pos + _neg ) -- geometria",
        "VAR _topo = IF ( _pos > 0, 21, 4 ) -- geometria",
        "VAR _base = _topo + ROUND ( _pos * _esc, 0 ) -- geometria",
        "VAR _yMes = _base + ROUND ( _neg * _esc, 0 ) + IF ( _neg > 0, 25, 6 ) -- geometria",
        "VAR _altSerie = _yMes + 17 -- geometria",
        f"VAR _cw = {TT_W} / _n -- geometria",
        f"VAR _bw = MIN ( 40, 2 * ROUND ( 0.275 * _cw, 0 ) ) -- geometria",
        "VAR _meiaBw = INT ( _bw / 2 ) -- geometria",
        "VAR _hRef = IF ( ISBLANK ( _vRef ), 0, MAX ( 2, ROUND ( ABS ( _vRef ) * _esc, 0 ) ) ) -- geometria",
        "VAR _yRotRef = IF ( _vRef >= 0, _base - _hRef - 21, _base + _hRef + 4 ) -- geometria",
        f"VAR _wRef = INT ( LEN ( _rLab ) * {f} ) + 2 -- geometria",
        f"VAR _xRef = MAX ( 0, MIN ( ( _n - 0.5 ) * _cw - _wRef / 2, {TT_W} - _wRef ) ) -- geometria",
        "VAR _htmlSerie =",
        "    CONCATENATEX (",
        "        _serie,",
        "        VAR _v = [@v]",
        "        VAR _p = [@pos]",
        "        VAR _tem = NOT ISBLANK ( _v )",
        "        VAR _h = IF ( _tem, MAX ( 2, ROUND ( ABS ( _v ) * _esc, 0 ) ), 0 ) -- geometria",
        "        VAR _y = IF ( _v >= 0, _base - _h, _base ) -- geometria",
        "        VAR _yRot = IF ( _v >= 0, _y - 21, _y + _h + 4 ) -- geometria",
        "        VAR _ngL = " + ( "IF ( _v < 0, \" ng\", \"\" )" if neg_vermelho else "\"\"" ),
        "        VAR _atraso = ( _p - 1 ) * 100 -- geometria",
        "        VAR _ehRef = dMes[Mes] = _ref",
        "        VAR _ehExt = dMes[Mes] = _mesExt",
        rotulo,
        "        /* rótulo centrado na coluna e preso à área; o do extremo recua se encostar no da referência */",
        f"        VAR _w = INT ( LEN ( _tLab ) * {f} ) + 2 -- geometria",
        f"        VAR _xNat = MAX ( 0, MIN ( ( _p - 0.5 ) * _cw - _w / 2, {TT_W} - _w ) ) -- geometria",
        "        VAR _colide = _ehExt && ABS ( _yRot - _yRotRef ) < 18 && _xNat + _w > _xRef - 6 -- geometria",
        "        VAR _x = IF ( _colide, MAX ( 0, _xRef - 6 - _w ), _xNat ) -- geometria",
        "        VAR _xRel = ROUND ( _x - ( _p - 1 ) * _cw, 0 ) -- geometria",
        "        VAR _estilo = \"top:\" & _yRot & \"px;left:\" & _xRel & \"px;width:\" & _w & \"px\"",
        "        VAR _rot =",
        "            SWITCH (",
        "                TRUE (),",
        "                _tem && _ehRef, \"<span class='val fim\" & _ngL & \"' style='\" & _estilo & \";animation-delay:\"",
        "                    & ( _atraso + 700 ) & \"ms'>\" & _tLabOd & \"</span>\",",
        "                _tem && _ehExt, \"<span class='val ext\" & _ngL & \"' style='\" & _estilo & \"'>\" & _tLabOd & \"</span>\",",
        "                \"\"",
        "            )",
        "        VAR _corre = \"' data-rp='top,height' data-r0-top='\" & _base & \"px' data-r0-height='0px' data-rd='\"",
        "        RETURN",
        "            \"<div class='c' style='height:\" & _altSerie & \"px'>\" & _rot",
        "                & IF ( _tem, \"<i class='bar s\" & [@st] & \"' style='top:\" & _y & \"px;height:\" & _h "
        "& \"px;left:calc(50% - \" & _meiaBw & \"px);width:\" & _bw & \"px' data-rk='m\" & _p & _corre & _atraso "
        "& \"'></i>\" )",
        "                & \"<span class='ms\" & IF ( _ehRef, \" ref\", IF ( _tem, \"\", \" sem\" ) ) & \"' style='top:\" "
        "& _yMes & \"px'>\" & [@rot] & \"</span></div>\",",
        "        \"\",",
        "        dMes[Mes], ASC",
        "    )",
    ]


CAB_OBRA = [
    "VAR _ref = [Mês de referência]",
    "VAR _mesCM = [Mês de referência · curto maiúsculo]",
    "VAR _iniHist = [Série · primeiro mês]",
    "VAR _aba = [Aba · ref]",
    "VAR _obra = [Obra · nome]",
    "VAR _cod = [Obra · código]",
    "VAR _selo = [Obra · selo]",
    "VAR _ini = [Obra · início]",
    "VAR _fim = [Obra · término previsto]",
    "VAR _adoSt = [Nota · status · ranking · ref]",
    "VAR _adoPend = [Nota · pendente · ranking · ref]",
    "VAR _adoNota = [Nota · nota final · ranking · ref]",
    "VAR _adoObt = [Nota · pontos obtidos · ranking · ref]",
    "VAR _adoPoss = [Nota · pontos possíveis · ranking · ref]",
]
TEXTOS_CAB_OBRA = [
    "VAR _txtPer =",
    "    SWITCH (",
    "        TRUE (),",
    "        _iniHist = _ref || ISBLANK ( _iniHist ), _mesCM,",
    "        YEAR ( _iniHist ) <> YEAR ( _ref ), UPPER ( FORMAT ( _iniHist, \"mmm/yy\", \"pt-BR\" ) ) & \"–\" & _mesCM,",
    "        UPPER ( FORMAT ( _iniHist, \"mmm\", \"pt-BR\" ) ) & \"–\" & _mesCM",
    "    )",
    "VAR _txtDir = IF ( ISBLANK ( _ini ), \"\", \"INÍCIO \" & UPPER ( FORMAT ( _ini, \"mmm/yy\", \"pt-BR\" ) ) ) "
    "& IF ( ISBLANK ( _fim ), \"\", \" · TÉRMINO \" & UPPER ( FORMAT ( _fim, \"mmm/yy\", \"pt-BR\" ) ) )",
    "/* Nota da obra no mês de referência: 'nota 7,75 · atenção' ou 'pendente · 5,0 de 6,0' */",
    DC.nota_txt("_ado", "_adoNota", "_adoObt", "_adoPoss", "_adoPend"),
    "VAR _txtAdo =",
    "    SWITCH (",
    "        TRUE (),",
    "        ISBLANK ( _adoPend ), \"\",",
    "        _adoPend = 1, _adoTxt,",
    "        _adoTxt & \" · \" & " + DC.palavra_status("_adoSt", "_adoPend"),
    "    )",
    "VAR _txtAdoC = IF ( _txtAdo = \"\", \"\", IF ( _txtDir = \"\", \"\", \" · \" ) & UPPER ( _txtAdo ) )",
    "/* a Nota da obra entra depois de início · término; se a linha do título não couber nos 520 px (título Barlow 21 ≈",
    "   12 px por letra, código ≈ 8, selo ≈ 50, vão 24, meta em versalete ≈ 7; medido no JANGADA: 496 de 520), o período fica só 'OUT/25–JUL/28' */",
    "VAR _txtPerCurto = IF ( ISBLANK ( _ini ) || ISBLANK ( _fim ), _txtDir, UPPER ( FORMAT ( _ini, \"mmm/yy\", \"pt-BR\" ) ) "
    "& \"–\" & UPPER ( FORMAT ( _fim, \"mmm/yy\", \"pt-BR\" ) ) )",
    f"VAR _pxCab = 12 * LEN ( _obra ) + 8 + 8 * LEN ( _cod ) + IF ( _selo = \"\" || ISBLANK ( _selo ), 0, 50 ) + 24 "
    "+ 7 * LEN ( _txtDir & _txtAdoC ) -- geometria",
    "VAR _txtDirAdo = IF ( _pxCab <= 520, _txtDir, _txtPerCurto ) & _txtAdoC",
]


def cab_obra(prefixo: str) -> list[str]:
    return [
        "        \"<div class='u tt'><div class='cab'><p class='vs'>\" & " + prefixo + " & \" · \" & _txtPer "
        "& IF ( ISBLANK ( _aba ), \"\", \" · ABA \" & _aba ) & \"</p>\"",
        "            & \"<div class='lin1'><div class='tit'><b>\" & " + D.esc("_obra") + " & \"</b><em>\" & _cod "
        "& \"</em>\" & " + selo("_selo") + " & \"</div>\"",
        "            & \"<p class='vs dir'>\" & _txtDirAdo & \"</p></div></div>\"",
    ]


# ===================================================================================================== 3.3 Mês do desembolso
desenho(
    "T4 · Tooltip mês do desembolso · HTML",
    "Tooltip de página do mês (par de colunas de Desembolso da carteira): previsto × desembolsado de cada obra no mês, "
    "do maior ao menor desvio (marca da faixa da previsão de caixa da nota, que conta o desvio para mais ou para menos; "
    "barra divergente do desvio na cor da faixa, com o zero no meio da sua coluna e escala simétrica pelo maior "
    "|desvio|), as justificativas preenchidas entre as exigidas no mês com as obras "
    "em branco numa linha só (do maior |desvio| para o menor, sem cortar nome: todas, as 2 primeiras e 'e mais M', ou "
    "nenhuma) e, fora do primeiro mês, quem entrou ou saiu da faixa crítica. Até "
    f"{LISTA_MAX} obras, todas aparecem; de {LISTA_MAX + 1} em diante, as {LISTA_MOSTRA} de maior desvio e 'e mais N obras'.",
    linhas(
        "-- 1 · Leituras",
        LEITURAS_MES,
        "VAR _ex = [Carteira · justificativas exigidas] + 0",
        "VAR _pre = [Carteira · justificativas preenchidas] + 0",
        "VAR _br = [Carteira · justificativas em branco] + 0",
        "VAR _listaBr = [T4 · Justificativas em branco no mês (lista)]",
        "VAR _foraRod = [T4 · Tooltip mês do desembolso · em branco fora do rodapé]",
        "VAR _saiu = [T4 · Desembolso · saíram da faixa crítica (lista)]",
        "VAR _entrou = [T4 · Desembolso · entraram na faixa crítica (lista)]",
        "VAR _seguem = [T4 · Desembolso · seguem na faixa crítica] + 0",
        "VAR _mais = [T4 · Tooltip mês do desembolso · obras fora da lista]",
        "VAR _obras =",
        "    ADDCOLUMNS (",
        "        VALUES ( dObra[Obra] ),",
        "        \"@pv\", [Desembolso · previsto no mês],",
        "        \"@ds\", [Desembolso · realizado no mês],",
        "        \"@d\", [Desembolso · desvio no mês],",
        "        \"@st\", [T4 · Desembolso · faixa do fluxo de caixa],",
        "        \"@selo\", [Obra · selo],",
        "        \"@tem\", [Obras com análise]",
        "    )",
        "VAR _comAba = FILTER ( _obras, [@tem] > 0 ) /* geometria */",
        f"/* passou de {LISTA_MAX} obras: as {LISTA_MOSTRA} de maior desvio (|desvio|), na ordem de sempre, e a linha "
        "'e mais N obras' */",
        f"VAR _mostra = TOPN ( IF ( _mais > 0, {LISTA_MOSTRA}, {LISTA_MAX} ), _comAba, ABS ( [@d] ), DESC, "
        "dObra[Obra], ASC ) /* geometria */",
        "VAR _o1 = PATHITEM ( _saiu, 1 )",
        "VAR _e1 = PATHITEM ( _entrou, 1 )",
        "VAR _dAntS = CALCULATE ( [T4 · Desembolso · desvio · mês anterior], dObra[Obra] = _o1 )",
        "VAR _dAntE = CALCULATE ( [T4 · Desembolso · desvio · mês anterior], dObra[Obra] = _e1 )",
        "-- 2 · Textos",
        D.od_tabela(),
        lista_e("_saiu", "_ls"), lista_e("_entrou", "_le"),
        D.pct("_dAntS", "_tds", casas=0, mais=True), D.pct("_dAntE", "_tde", casas=0, mais=True),
        D.inteiro("_pre", "_tpr"), D.od_num("_pre", "_tpr"), D.inteiro("_ex", "_tex"), D.od_num("_ex", "_tex"),
        f"/* linha de dados do pé ({JUS_W} px): JUSTIFICATIVAS ({JUS_VS}) · 'P de E' (~10 px por algarismo + 19) · "
        f"'preenchidas · ' ({JUS_PRE}) e o trecho dos nomes, com {JUS_FOLGA} px de folga */",
        f"VAR _pxJus = ( {JUS_W - JUS_VS - JUS_GAP - JUS_PRE - JUS_FOLGA} - ( 11 * LEN ( _tprTxt & _ex ) + 24 ) ) * 13 / 14 -- geometria",
        R.nomes("_listaBr", "_foraRod", "_pre", "_br", "_pxJus"),
        "VAR _txtSob = \"DESEMBOLSO DA CARTEIRA · \" & _mesC & IF ( _primeiro, \" · PRIMEIRO MÊS DO HISTÓRICO\", \"\" )",
        "VAR _htmlJus =",
        "    SWITCH (",
        "        TRUE (),",
        "        _ex = 0, \"<b>0</b><span class='dt'>· nenhuma exigida: todo desembolso dentro de ±10%</span>\",",
        "        _br = 0,",
        "            \"<b>\" & _texOd & \"</b><span class='dt'>\"",
        "                & IF ( _ex = 1, \"exigida, preenchida\", \"exigidas, todas preenchidas\" ) & \"</span>\",",
        "        \"<b>\" & _tprOd & \" de \" & " + C.marca("_ex") + " & \"</b><span class='dt'>\"",
        "            & IF ( _ex = 1, \"preenchida · \", \"preenchidas · \" ) & " + D.esc("_nbTxt") + " & \"</span>\"",
        "    )",
        "VAR _txtSeguem = SWITCH ( _seguem, 0, \"nenhuma segue nela\", 1, \"uma segue nela\", "
        + extenso("_seguem") + " & \" seguem nela\" )",
        "VAR _txtRod =",
        "    SWITCH (",
        "        TRUE (),",
        "        _primeiro, \"\",",
        "        _lsN + _leN = 0, \"Nenhuma obra entrou ou saiu da faixa crítica desde \" & _mesAnt & \".\",",
        "        _lsN = 1 && _leN = 0, _o1 & \" saiu da faixa crítica (era \" & " + C.marca("_tdsTxt") + " & \" em \" & _mesAnt & \"); \" "
        "& _txtSeguem & \".\",",
        "        _leN = 1 && _lsN = 0, _e1 & \" entrou na faixa crítica (era \" & " + C.marca("_tdeTxt") + " & \" em \" & _mesAnt & \"); \" "
        "& _txtSeguem & \".\",",
        "        _leN = 0, _lsTxt & \" saíram da faixa crítica desde \" & _mesAnt & \"; \" & _txtSeguem & \".\",",
        "        _lsN = 0, _leTxt & \" entraram na faixa crítica desde \" & _mesAnt & \"; \" & _txtSeguem & \".\",",
        "        _lsTxt & IF ( _lsN = 1, \" saiu e \", \" saíram e \" ) & _leTxt & IF ( _leN = 1, \" entrou\", \" entraram\" ) "
        "& \" na faixa crítica desde \" & _mesAnt & \".\"",
        "    )",
        "-- 3 · Geometria",
        "VAR _max = MAXX ( _comAba, ABS ( [@d] ) ) /* geometria */",
        "-- 4 · Marcação",
        "VAR _htmlLinhas =",
        "    CONCATENATEX (",
        "        _mostra,",
        "        VAR _d = [@d]",
        rs_linha("[@pv]", "_p", "        "),
        rs_linha("[@ds]", "_r", "        "),
        pct_linha("_d", "_q", "        ", 0),
        f"        VAR _w = IF ( ISBLANK ( _d ), 0, MAX ( 1, ROUND ( DIVIDE ( ABS ( _d ), _max ) * {DES_MEIA}, 0 ) ) ) "
        "-- geometria",
        f"        VAR _x = IF ( _d >= 0, {DES_ZERO}, {DES_ZERO} - _w ) -- geometria",
        f"        VAR _corre = IF ( _d < 0, \" data-rp='left,width' data-r0-left='{DES_ZERO}px'\" )",
        "        /* as duas pontas na cor da faixa do fluxo de caixa (o desvio conta para mais ou para menos), nunca pelo sinal */",
        "        VAR _clsBz = IF ( ISBLANK ( [@st] ), \"\", \" s\" & [@st] )",
        "        RETURN",
        "            \"<div class='lc'>\" & IF ( ISBLANK ( _d ), \"\", \"<i class='mk mk\" & [@st] & \"'></i>\" ) "
        "& \"<span class='nm'>\" & dObra[Obra] & "
        + selo_real("[@selo]") + " & \"</span>\"",
        "                & \"<span class='pv'>\" & IF ( ISBLANK ( [@pv] ), \"sem previsto\", _pOd ) & \"</span><span class='px'>×</span><span class='ds'>\" & _rOd "
        "& \"</span>\"",
        "                & IF ( _w > 0, \"<i class='bz\" & _clsBz & \"' style='left:\" & _x & \"px;width:\" & _w "
        "& \"px'\" & _corre "
        "& \" data-rk='\" & dObra[Obra] & \"' data-rd='\" & ( RANKX ( _mostra, [@d], _d, DESC ) - 1 ) * 60 & \"'></i>\" ) "
        "/* geometria */",
        "                & \"<span class='p dv'>\" & IF ( ISBLANK ( _d ), \"—\", _qOd ) & \"</span></div>\",",
        "        \"\",",
        "        [@d], DESC,",
        "        dObra[Obra], ASC",
        "    )",
        "VAR _htmlMais = IF ( _mais > 0, \"<i class='vz mais'>e mais \" & " + C.marca('FORMAT ( _mais, "0" )') + " "
        "& \" obras, com desvio mais perto de zero</i>\" )",
        "VAR _nLs = COUNTROWS ( _mostra ) + IF ( _mais > 0, 1, 0 ) /* lista */",
        "RETURN",
        "    IF (",
        "        _n > 0,",
        cabecalho_mes("_txtSob"),
        "            & \"<div class='corpo lim'><div class='bh'><span class='vs'>PREVISTO × DESEMBOLSADO, POR OBRA</span>\"",
        "            & \"<span class='vs'>DESVIO</span></div><div class='lsb ld\" & " + TL.atributos("_nLs") + "'>\" & _htmlLinhas & _htmlMais & \"</div></div>\"",
        "            & \"<div class='pe'><div class='dd'><span class='vs'>JUSTIFICATIVAS</span>\"",
        "            & _htmlJus & \"</div>\"",
        "            & IF ( _txtRod <> \"\", \"<p class='rod'>\" & " + D.esc("_txtRod") + " & \"</p>\" )",
        "        & \"</div></div>\" & [Comum · JS contador tooltip] & [Comum · JS corrida]",
        "    )",
    ))

# ===================================================================================================== 3.4 Obra do desembolso
desenho(
    "T4 · Tooltip obra do desembolso · HTML",
    "Tooltip de página da obra (linha de Obras no mês; era a de Desembolso por obra): o desvio sobre o previsto mês a "
    "mês (cor = faixa do "
    "previsão de caixa da nota, para mais ou para menos; rótulo no mês de referência e no extremo oposto), a justificativa do mês de referência (veio do painel "
    "na fase 5: o texto da aba em até 2 linhas, o chip 'EM BRANCO · EXIGIDA', 'dentro de ±10%: não exigida' ou 'sem "
    "previsto no mês', com o desvio e se era exigida à direita), o histórico das justificativas nos 5 meses anteriores "
    "(os mais antigos numa linha de resumo; some quando nada foi exigido no período) e um rodapé com o que foi exigido "
    "e preenchido.",
    linhas(
        "-- 1 · Leituras",
        CAB_OBRA,
        "VAR _ex = [T4 · Obra · justificativas exigidas no período] + 0",
        "VAR _pre = [T4 · Obra · justificativas preenchidas no período] + 0",
        "VAR _seg = [T4 · Obra · meses seguidos em branco] + 0",
        "VAR _critIni = [T4 · Obra · faixa crítica do desembolso · início]",
        "VAR _abaixoIni = [T4 · Obra · abaixo do previsto · início]",
        "VAR _nAba = [T4 · Meses com aba]",
        "VAR _rIni = [T4 · Obra · resumo das justificativas · primeiro mês]",
        "VAR _rFim = [T4 · Obra · resumo das justificativas · último mês]",
        "VAR _rMeses = [T4 · Obra · resumo das justificativas · meses] + 0",
        "VAR _rEx = [T4 · Obra · resumo das justificativas · exigidas] + 0",
        "VAR _rPre = [T4 · Obra · resumo das justificativas · preenchidas] + 0",
        "VAR _rNao = [T4 · Obra · resumo das justificativas · não exigidas] + 0",
        "VAR _tR = TRIM ( [Justificativa do desembolso · ref] )",
        "VAR _exR = [Justificativa · exigida · ref]",
        "VAR _brR = [Justificativa · em branco · ref]",
        "VAR _dvR = [Desembolso · desvio no mês · ref]",
        "VAR _jus =",
        "    ADDCOLUMNS (",
        "        VALUES ( dMes[Mes] ),",
        "        \"@ate\", [Série · mês até a referência],",
        "        \"@rot\", [Mês · abreviado],",
        "        \"@tem\", [Obras com análise],",
        "        \"@t\", [Justificativa do desembolso],",
        "        \"@e\", [Justificativa · exigida],",
        "        \"@b\", [Justificativa · em branco]",
        "    )",
        "/* histórico: os 5 meses antes da referência, um por linha; os anteriores viram a linha de resumo */",
        "VAR _jusMeses = FILTER ( _jus, [@ate] = 1 && [@tem] > 0 && dMes[Mes] >= EDATE ( _ref, -5 ) && dMes[Mes] < _ref ) "
        "/* lista */",
        "VAR _nHist = [T4 · Tooltip obra do desembolso · meses com aba nos 5 anteriores]",
        "VAR _nJl = COUNTROWS ( _jusMeses ) + IF ( _rMeses > 0, 1, 0 ) /* lista */",
        "-- 2 · Textos",
        D.od_tabela(),
        TEXTOS_CAB_OBRA,
        "VAR _txtFaixa =",
        "    SWITCH (",
        "        TRUE (),",
        "        NOT ISBLANK ( _critIni ), \"; na faixa crítica desde \" & " + nome_mes("_critIni") + ",",
        "        NOT ISBLANK ( _abaixoIni ), \"; abaixo do previsto desde \" & " + nome_mes("_abaixoIni") + ",",
        "        \"\"",
        "    )",
        "VAR _txtBranco = IF ( _seg > 0, \"; em branco há \" & " + extenso("_seg", fem=False)
        + " & IF ( _seg = 1, \" mês\", \" meses\" ), \"\" )",
        "VAR _txtRod =",
        "    SWITCH (",
        "        TRUE (),",
        "        _ex = 0, \"Dentro de ±10% nos \" & " + extenso("_nAba", fem=False)
        + " & \" meses: nenhuma justificativa exigida.\",",
        "        _pre = _ex,",
        "            IF ( _ex = _nAba, \"Exigida e preenchida nos \" & " + extenso("_ex", fem=False) + " & \" meses\", "
        "\"Exigida em \" & " + extenso("_ex", fem=False) + " & IF ( _ex = 1, \" mês, preenchida\", "
        "\" meses, todas preenchidas\" ) ) & _txtFaixa & \".\",",
        "        _pre = 0, " + cap(extenso("_ex", fem=False)) + " & IF ( _ex = 1, \" mês exigido, não preenchido\", "
        "\" meses exigidos, nenhum preenchido\" ) & _txtBranco & \".\",",
        "        \"Exigida em \" & " + extenso("_ex", fem=False) + " & \" meses, \" & " + extenso("_pre")
        + " & IF ( _pre = 1, \" preenchida\", \" preenchidas\" ) & _txtBranco & \".\"",
        "    )",
        "/* justificativa do mês de referência (fase 5, veio do painel): texto da aba, chip, não exigida ou sem previsto */",
        D.pct("_dvR", "_tdr", casas=0, mais=True),
        "VAR _txtDirR =",
        "    IF ( ISBLANK ( _dvR ), \"SEM PREVISTO NO MÊS\", \"DESVIO \" & " + C.marca("_tdrTxt") + " & IF ( _exR = 1, \" · EXIGIDA\", "
        "\" · NÃO EXIGIDA\" ) )",
        "VAR _htmlRef =",
        "    SWITCH (",
        "        TRUE (),",
        "        _brR = 1, \"<span class='chp'><i></i>Em branco · exigida</span>\",",
        "        NOT ISBLANK ( _tR ) && _tR <> \"\", \"<p class='t'>\" & " + D.esc("_tR") + " & \"</p>\",",
        "        ISBLANK ( _exR ), \"<p class='t ne'>sem previsto no mês</p>\",",
        "        \"<p class='t ne'>dentro de ±10%: não exigida</p>\"",
        "    )",
        "VAR _clsJl = IF ( _rMeses > 0, \" lg\", \"\" )",
        "VAR _txtRIni = FORMAT ( _rIni, \"mmm\", \"pt-BR\" )",
        "VAR _txtRPer = IF ( _rIni = _rFim, _txtRIni, _txtRIni & \"–\" & FORMAT ( _rFim, \"mmm\", \"pt-BR\" ) )",
        "VAR _txtRPre =",
        "    SWITCH (",
        "        TRUE (),",
        "        _rPre = 0, \"nenhuma preenchida\",",
        "        _rPre = _rEx, IF ( _rEx = 1, \"preenchida\", \"todas preenchidas\" ),",
        "        " + C.marca("_rPre") + " & IF ( _rPre = 1, \" preenchida\", \" preenchidas\" )",
        "    )",
        "VAR _txtResumo =",
        "    IF (",
        "        _rEx = 0,",
        "        \"nenhuma exigida (dentro de ±10%)\",",
        "        " + C.marca("_rEx") + " & IF ( _rEx = 1, \" exigida, \", \" exigidas, \" ) & _txtRPre",
        "            & IF ( _rNao > 0, \" (\" & " + C.marca("_rNao") + " & \" dentro de ±10%)\", \"\" )",
        "    )",
        "VAR _htmlResumo =",
        "    IF (",
        "        _rMeses > 0,",
        "        \"<div class='jl lg'><span class='m'>\" & _txtRPer & \"</span><span class='t ne'>\" & _txtResumo & \"</span></div>\"",
        "    )",
        "VAR _htmlJus =",
        "    _htmlResumo & CONCATENATEX (",
        "        _jusMeses,",
        "        VAR _t = TRIM ( [@t] )",
        "        VAR _cel =",
        "            SWITCH (",
        "                TRUE (),",
        "                [@b] = 1, \"<span class='chp'><i></i>Em branco · exigida</span>\",",
        "                NOT ISBLANK ( _t ) && _t <> \"\", \"<span class='t'>\" & " + D.esc("_t") + " & \"</span>\",",
        "                ISBLANK ( [@e] ), \"<span class='t ne'>sem previsto no mês</span>\",",
        "                \"<span class='t ne'>não exigida (dentro de ±10%)</span>\"",
        "            )",
        "        RETURN",
        "            \"<div class='jl\" & _clsJl & \"'><span class='m'>\" & [@rot] & \"</span>\" & _cel & \"</div>\",",
        "        \"\",",
        "        dMes[Mes], ASC",
        "    )",
        serie_mes("Desembolso · desvio no mês", "T4 · Desembolso · faixa do fluxo de caixa", "pct", neg_vermelho=False),
        "-- 4 · Marcação",
        "RETURN",
        "    IF (",
        "        NOT ISBLANK ( [Orçamento · ref] ),",
        cab_obra("\"DESEMBOLSO\""),
        "            & \"<div class='corpo'><span class='vs'>DESVIO SOBRE O PREVISTO, MÊS A MÊS</span>\"",
        "            & \"<div class='sr'>\" & _htmlSerie & \"</div>\"",
        "            & \"<div class='rg'></div><div class='bh'><span class='vs'>JUSTIFICATIVA DE \" & _mesCM & \"</span>\"",
        "            & \"<span class='vs'>\" & _txtDirR & \"</span></div><div class='jr'>\" & _htmlRef & \"</div>\"",
        "            & IF (",
        "                _ex > 0 && _nHist + _rMeses > 0,",
        "                \"<div class='rg'></div><div class='bh'><span class='vs'>NOS MESES ANTERIORES</span>\"",
        "                    & \"<span class='vs'>EXIGIDA ACIMA DE ±10%</span></div><div class='jls\" & " + TL.atributos("_nJl") + "'>\" & _htmlJus & \"</div>\"",
        "            )",
        "            & \"</div><div class='pe'><p class='rod'>\" & " + D.esc("_txtRod") + " & \"</p></div>\"",
        "        & \"</div>\" & [Comum · JS contador tooltip] & [Comum · JS corrida]",
        "    )",
    ))

if __name__ == "__main__":
    sys.exit(gravar(MEDIDAS, RAIZ / "dax" / "T4", GERADO))

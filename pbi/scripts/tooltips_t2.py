#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tooltips_t2 — tooltips de página da Tela 02 · Análise crítica (pbi/dax/T2/Tooltips/**). Só leem contas.

Redesenho v2 (07/10/2026): Figma FjBWDk5odF9HaZ2pwhGosl, seção v2 · Tela 02 (379:789) › Fileira · Tooltips (386:790):
Item 389:1908 (· título longo 389:1945, · vazio 389:1992, · fórmula 389:2003), Degrau 390:1918 (· pago e não aplicado
390:1962, · vazio 390:2012), Mês 390:2052 (· justificativa longa 390:2086, · primeiro mês 390:2120), Indicador 390:2509
(· sinais mistos 390:2545, · estável 390:2581); regras em pbi/spec/redesenho/t02.md §2–§5.
Anatomia v2: 560 de largura, fundo branco (pedido do Alisson, 07/10/2026) com contorno 1 px preto e cantos retos; cabeçalho preto (sobretítulo versalete,
título Barlow SemiBold 21 e código) com a meta da direita num flex com quebra: quando não cabe ao lado do título com
24 px de folga, desce para a 2ª linha (cabeçalho 72 → 94). Corpo com margem 18: linhas de 24 (Segoe 15 + Barlow 16),
série de uma só (coluna = 524 ÷ n, barra mín(48, coluna − 16) × até 44, rótulo Barlow SemiBold 14 só no mês do ponto e
no extremo, mês em Segoe 13 e o do ponto em Segoe SemiBold 13). Rodapé numa linha, preso ao pé (L019), com reticências.
Negativo em vermelho em todo número, rótulo e barra (inclusive desvio físico); só o desvio de desembolso negativo fica
em preto.
CSS própria (não depende da CSS de tooltip da T1). Contador nos valores e corrida nas barras (contador.py, corrida.py).

    python -X utf8 pbi/scripts/tooltips_t2.py
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import desenho_projeto as D  # noqa: E402
from contas_lib_projeto import Medida, gravar  # noqa: E402
from desenho_comum import dax_lit  # noqa: E402
import desenho_comum as DC  # noqa: E402
import contador as C  # noqa: E402
import tooltip_lib as TL  # noqa: E402
from desenho_t2 import faixa_html, marca_item, span_ng, x_item  # noqa: E402

RAIZ = AQUI.parent
GERADO = "pbi/scripts/tooltips_t2.py"
DES = r"T2 Análise crítica\Tooltips"
MEDIDAS: list[Medida] = []
MENOS = D.MENOS
LINHAS_MAX = 8          # linhas da tabela anexada no tooltip de item; com mais, 7 + "e mais N linhas"


def desenho(nome, descricao, dax):
    """Medida de desenho; os valores marcados com C.marca() viram odômetro no fim (F4)."""
    MEDIDAS.append(Medida(nome, DES, "texto", descricao, C.envolver_marcas(dax)))


def ng_m(p: str) -> str:
    """span_ng com o texto marcado para o odômetro."""
    return span_ng(p, C.marca(p + "Txt"))


def linhas(*ls) -> str:
    def plano(x):
        for g in x:
            if isinstance(g, list):
                yield from plano(g)
            else:
                yield g
    return "\n".join(plano(ls))


def ext(v: str, fem: bool = False) -> str:
    nomes = (["nenhuma", "uma", "duas"] if fem else ["nenhum", "um", "dois"]) + \
        ["três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez"]
    casos = ", ".join(f'{i}, "{n}"' for i, n in enumerate(nomes))
    return f'SWITCH ( {v}, {casos}, FORMAT ( {v}, "0" ) )'


def sw(cod: str, mapa: dict, outro: str = '""') -> str:
    return "SWITCH ( " + cod + ", " + ", ".join(f'"{k}", {D.texto(v)}' for k, v in mapa.items()) + f", {outro} )"


def cabeca(sob: str, tit: str, cod: str | None, dir_: str) -> str:
    """Marcação do cabeçalho (expressões DAX): sobretítulo, título + código e a meta da direita (quebra para a 2ª
    linha quando não cabe; flex com justify space-between, então na 2ª linha ela fica à esquerda)."""
    cod_html = f" & \"<em class='vs'>\" & {cod} & \"</em>\"" if cod else ""
    return (f"\"<div class='u tt'><div class='cab sobre-preto'><p class='vs sob'>\" & {sob} & \"</p>\"\n"
            f"            & \"<div class='tl'><div class='tit'><b>\" & {tit} & \"</b>\"{cod_html} & \"</div>\"\n"
            f"            & \"<p class='vs dir'>\" & {dir_} & \"</p></div></div>\"")


def rodape(txt: str, rotulo: str | None = None) -> str:
    """Rodapé preso ao pé (L019): regra, rótulo opcional e uma linha com reticências. `txt` pode trazer HTML (span)."""
    rot = f" & \"<span class='vs'>\" & {rotulo} & \"</span>\"" if rotulo else ""
    return f"\"<div class='rp'><div class='rg'></div>\"{rot} & \"<p class='rod'>\" & {txt} & \"</p></div>\""


# ===================================================================================================== CSS
CSS_TT = (
    ".tt{position:fixed;inset:0;background:#FFFFFF;border:1px solid #0B0B0C;border-radius:0;overflow:hidden;"
    "color:#0B0B0C}"
    ".tt .cab{background:#0B0B0C;padding:14px 18px 13px}"
    ".tt .cab .sob{display:block;color:rgba(233,224,207,.75);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
    ".tt .cab .tl{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;column-gap:24px;"
    "row-gap:6px;margin-top:4px}"
    ".tt .cab .tit{display:flex;align-items:baseline;gap:10px;white-space:nowrap;min-width:0}"
    ".tt .cab .tit b{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:21px;line-height:26px;"
    "color:#FFFFFF}"
    ".tt .cab .tit em{font-style:normal;color:rgba(233,224,207,.85)}"
    ".tt .cab .dir{color:rgba(233,224,207,.75);white-space:nowrap}"
    ".tt .corpo{padding:16px 18px 0}"
    ".tt .corpo .vs{display:block}.tt .sl{margin-bottom:6px}"
    ".tt .bh{display:flex;justify-content:space-between;margin-bottom:6px}"
    ".tt .rg{height:1px;background:#E1E1E1;margin:12px 0 11px}"
    ".tt .tx{font-size:15px;line-height:21px}"
    ".tt .vz{font-size:15px;line-height:21px;color:#3B3B3F}"
    ".tt .lin{display:grid;align-items:center;height:24px;white-space:nowrap}"
    ".tt .lin .v{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:16px;line-height:20px;"
    "text-align:right;font-variant-numeric:tabular-nums}"
    ".tt .lin.it{grid-template-columns:1fr 170px}"
    ".tt .lin.it .d2{font-size:15px;line-height:21px;overflow:hidden;text-overflow:ellipsis}"
    ".tt .lin.mais{display:block;font-size:14px;line-height:24px;color:#3B3B3F}"
    ".tt .lin.dg{grid-template-columns:28px 1fr 170px}"
    ".tt .lin.dg .o{font-size:13px;line-height:16px;color:#6B6B70}"
    ".tt .lin.dg .n{font-size:15px;line-height:21px;overflow:hidden;text-overflow:ellipsis}"
    ".tt .lin.dg.z .n,.tt .lin.dg.z .v{color:#6B6B70;opacity:.75}.tt .lin.dg.z .o{opacity:.6}"
    ".tt .lin.cf{grid-template-columns:20px 180px 100px 1fr;height:26px}"
    ".tt .lin.cf.so{grid-template-columns:20px 1fr 150px}"
    # linha do quadradinho em zero dentro do degrau: esmaecida
    ".tt .lin.cf.z .n,.tt .lin.cf.z .v,.tt .lin.cf.z .sg{color:#6B6B70;opacity:.75}"
    ".tt .lin.cf .sg,.tt .lin.cf .n{font-weight:600;font-size:15px;line-height:21px}"
    ".tt .lin.cf .n{overflow:hidden;text-overflow:ellipsis}"
    ".tt .lin.cf .d{padding-left:16px;font-size:14px;line-height:19px;color:#3B3B3F;overflow:hidden;"
    "text-overflow:ellipsis}"
    ".tt .faixa{display:flex;align-items:center;gap:6px;white-space:nowrap;font-size:14px;line-height:19px}"
    ".tt .faixa .mk{margin-left:10px}.tt .faixa .mk:first-child{margin-left:0}"
    ".tt .des{display:flex;align-items:center;gap:6px;font-size:15px;line-height:21px;white-space:nowrap}"
    ".tt .des b{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:16px;margin-left:8px}"
    # rodapé preso ao pé (L019): caixa de altura fixa, uma linha, reticências
    ".tt .rp{position:absolute;left:18px;right:18px;bottom:16px}"
    ".tt .rp .rg{margin:0 0 11px}.tt .rp .vs{display:block;margin-bottom:4px}"
    ".tt .rod{height:21px;font-size:15px;line-height:21px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
    # série de uma só, janela de 1 a 12 meses: coluna = 524 ÷ n, barra mín(48, coluna − 16), até 44 de altura
    ".tt .ser{display:flex;position:relative;width:524px}"
    ".tt .ser .c{flex:1 1 0;min-width:0;text-align:center;position:relative;height:var(--alt,86px)}"
    ".tt .ser .c .val{position:absolute;width:80px;text-align:center;font-family:'Barlow U','Segoe UI',sans-serif;"
    "font-weight:600;font-size:14px;line-height:17px;white-space:nowrap;font-variant-numeric:tabular-nums;"
    "text-shadow:1px 0 0 #FFFFFF,-1px 0 0 #FFFFFF,0 1px 0 #FFFFFF,0 -1px 0 #FFFFFF,0 0 3px #FFFFFF}"
    ".tt .ser .c .bar{position:absolute;left:calc(50% - var(--b,48px) / 2);width:var(--b,48px)}"
    ".tt .ser .c .bar.nt{background:rgba(11,11,12,.18)}.tt .ser .c .bar.nt.ng{background:rgba(196,55,55,.35)}"
    ".tt .ser .c .bar.nr{background:#0B0B0C}.tt .ser .c .bar.nr.ng{background:#C43737}"
    ".tt .ser .c .bar.s2{background:#C43737}.tt .ser .c .bar.s1{background:#C9821F}"
    ".tt .ser .c .bar.s0{background:#A9CDB9;box-shadow:inset 0 0 0 1px #6E9F85}"
    ".tt .ser .c .bar.z0{background:rgba(107,107,112,.6)}"
    ".tt .ser .c .ms{position:absolute;left:-6px;right:-6px;bottom:0;font-size:13px;line-height:16px;"
    "white-space:nowrap;color:#3B3B3F}"
    ".tt .ser .c .ms.ref{font-weight:600;color:#0B0B0C}.tt .ser .c .ms.sem{opacity:.35}"
    "@keyframes ttFim{from{opacity:0}}.tt .fim{animation:ttFim .2s ease-out backwards}"
    "@media (prefers-reduced-motion:reduce){.tt .fim{animation:none}}"
)
# faixas do item da nota (tooltip do item da nota)
CSS_FX = (
    ".tt .fx{display:grid;grid-template-columns:1fr 1fr;column-gap:16px;row-gap:2px;margin-bottom:4px}"
    ".tt .fx .f{display:flex;align-items:center;gap:7px;height:22px;font-size:14px;line-height:19px;white-space:nowrap;"
    "color:#3B3B3F;overflow:hidden;text-overflow:ellipsis}"
    ".tt .fx .f.on{color:#0B0B0C;font-weight:600}"
    ".tt .fx .f .mk.mkv{box-shadow:inset 0 0 0 1px #E1E1E1}"
    ".tt .nt{font-size:14px;line-height:19px;color:#3B3B3F;margin-top:2px}"
)
# F4 (28/10/2026): o corpo é uma coluna flexível que vai até o rodapé (reserva de 72 px com rodapé, classe crp); a lista
# principal (linhas do degrau, a conta do mês, as faixas do item) ocupa o que sobra, com a escala do tooltip_lib, e tudo
# entra em cascata (C5)
CSS_F4 = (".tt{display:flex;flex-direction:column}.tt .cab{flex:none}"
          ".tt .corpo{flex:1 1 auto;min-height:0;display:flex;flex-direction:column;padding-bottom:16px}"
          ".tt .corpo.crp{padding-bottom:72px}.tt .corpo>*{flex:none}"
          ".tt .ls>.lin{height:auto;min-height:0}"
          ".tt .fx.ls{display:grid;grid-auto-rows:minmax(0,1fr);align-content:stretch}.tt .fx.ls .f{height:auto}"
          # conta do mês (página de 620): nome 210 e valor 120 para a escala; o detalhe fica em 14 e cabe inteiro
          ".tt .lin.cf{grid-template-columns:20px 210px 120px 1fr}")
FONTES_T2 = {".tt .ls .lin .v": 16, ".tt .ls .lin .n": 15, ".tt .ls .lin .sg": 15, ".tt .ls .lin .d2": 15,
             ".tt .fx.ls .f": 14}
CASCATA_T2 = TL.entrada(".tt .ls>:nth-child({k})", [".tt .corpo>.bh", ".tt .corpo>.sl", ".tt .corpo>.vs",
                                                     ".tt .corpo>.tx", ".tt .corpo>.des", ".tt .corpo>.nt",
                                                     ".tt .corpo>.vz", ".tt .ser .ms"], pe=".tt .rp")
desenho("T2 · Tooltip · CSS", "CSS dos tooltips v2 da T2 (cartão branco 560, cabeçalho preto com a meta que quebra "
        "de linha, linhas de item, degrau e conta, faixa, série de uma só e rodapé preso ao pé; F4: corpo flexível, lista "
        "com escala e cascata de entrada). Não depende da CSS de tooltip da T1.",
        "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(CSS_TT + CSS_FX + TL.css_escala(FONTES_T2) + CSS_F4
                                                         + CASCATA_T2))


def serie(var_lista: str, ref: str, modo: str = "neutra") -> list[str]:
    """Marcação da série mês a mês a partir de uma lista própria com @v, @rot, @ord, @pos (posição na janela) e, no modo
    "pts", @s (classe dos pontos: 0 cheio · 1 parcial · 2 zero; vazio = neutro). Coluna = 524 ÷ n, barra = mín(48,
    coluna − 16), até 44 px de altura. Rótulo só no mês do ponto e no extremo, numa caixa de 80 px presa a x −14…458; o
    extremo que toca o ponto desliza até encostar e sai se o centro deixar a própria coluna. Modo "neutra": R$ curto e
    vermelho quando negativo; modo "pts": pontos da nota (0,5 · 4,25), barra na cor da classe e zero como traço de 2 px
    na cor da classe. Sinais mistos: positivas para cima e negativas para baixo; série toda negativa em módulo para
    cima. Valor nulo some (mês a 35 %)."""
    pts = modo == "pts"
    fmt = ([f'VAR _fTxt = FORMAT ( _p, "{DC.FMT_PTS}", "pt-BR" )', 'VAR _fS = ""'] if pts else D.rs("_p", "_f"))
    fmt = [("        " + l) for l in fmt]
    ng_rot = '""' if pts else 'IF ( _fS = "' + MENOS + '", " ng", "" )'
    return [
        f"VAR _comV = FILTER ( {var_lista}, NOT ISBLANK ( [@v] ) ) /* lista */",
        "VAR _vRef = MAXX ( FILTER ( _comV, dMes[Mes] = " + ref + " ), [@v] ) /* geometria */",
        "VAR _vMax = MAXX ( _comV, [@v] ) /* geometria */",
        "VAR _vMin = MINX ( _comV, [@v] ) /* geometria */",
        "VAR _ext = IF ( _vRef >= _vMax, _vMin, _vMax ) /* geometria */",
        "VAR _mesExt = MINX ( FILTER ( _comV, [@v] = _ext && dMes[Mes] <> " + ref + " ), dMes[Mes] ) /* geometria */",
        "VAR _posExt = MINX ( FILTER ( _comV, dMes[Mes] = _mesExt ), [@pos] ) /* geometria */",
        "VAR _pos = MAX ( _vMax, 0 ) -- geometria",
        "VAR _neg = MAX ( - _vMin, 0 ) -- geometria",
        "VAR _todaNeg = _pos = 0 -- geometria",
        "VAR _esc = IF ( _todaNeg, _neg, _pos + _neg ) -- geometria",
        "VAR _yZero = IF ( _todaNeg, 64, 20 + ROUND ( DIVIDE ( _pos, _esc ) * 44, 0 ) ) -- geometria",
        "VAR _wSer = DIVIDE ( 524, _nSer ) -- geometria",
        "VAR _bSer = MIN ( 48, ROUND ( _wSer - 16, 0 ) ) -- geometria",
        "VAR _hRef = MAX ( ROUND ( DIVIDE ( ABS ( _vRef ), _esc ) * 44, 0 ), 2 ) -- geometria",
        "VAR _yRef = IF ( _todaNeg || _vRef >= 0, _yZero - _hRef - 20, _yZero + _hRef + 4 ) -- geometria",
        "VAR _lRef = MIN ( MAX ( ROUND ( ( _nSer - 0.5 ) * _wSer, 0 ) - 40, -14 ), 458 ) -- geometria",
        "VAR _hExt = MAX ( ROUND ( DIVIDE ( ABS ( _ext ), _esc ) * 44, 0 ), 2 ) -- geometria",
        "VAR _yExt = IF ( _todaNeg || _ext >= 0, _yZero - _hExt - 20, _yZero + _hExt + 4 ) -- geometria",
        "VAR _lExt0 = MIN ( MAX ( ROUND ( ( _posExt - 0.5 ) * _wSer, 0 ) - 40, -14 ), 458 ) -- geometria",
        "VAR _toca = ABS ( _lExt0 - _lRef ) < 80 && ABS ( _yExt - _yRef ) < 17 -- geometria",
        "VAR _lExt = IF ( _toca, IF ( _lExt0 <= _lRef, _lRef - 80, _lRef + 80 ), _lExt0 ) -- geometria",
        "VAR _extVe = NOT _toca || ( ABS ( _lExt - _lExt0 ) <= _wSer / 2 && _lExt >= -14 && _lExt <= 458 ) -- geometria",
        "VAR _htmlSerie =",
        "    CONCATENATEX (",
        f"        {var_lista},",
        "        VAR _p = [@v]",
        "        VAR _tem = NOT ISBLANK ( _p )",
        "        VAR _h = IF ( _tem, MAX ( ROUND ( DIVIDE ( ABS ( _p ), _esc ) * 44, 0 ), 2 ), 0 ) -- geometria",
        "        VAR _sobe = _todaNeg || _p >= 0",
        "        VAR _top = IF ( _sobe, _yZero - _h, _yZero ) -- geometria",
        "        VAR _atraso = ( [@pos] - 1 ) * 60 -- geometria",
        "        VAR _colL = ROUND ( ( [@pos] - 1 ) * _wSer, 0 ) -- geometria",
        "        VAR _ehRef = dMes[Mes] = " + ref,
        "        VAR _ehExt = dMes[Mes] = _mesExt && _ext <> _vRef && _extVe",
        fmt,
        f"        VAR _ngRot = {ng_rot}",
        "        VAR _yRot = IF ( _sobe, _top - 20, _top + _h + 4 ) -- geometria",
        ("        VAR _cls = IF ( ISBLANK ( [@s] ), \"z0\", \"s\" & [@s] )" if pts
         else "        VAR _cls = IF ( _p = 0, \"z0\", IF ( _ehRef, \"nr\", \"nt\" ) & IF ( _p < 0, \" ng\", \"\" ) )"),
        "        VAR _rot =",
        "            SWITCH (",
        "                TRUE (),",
        "                _tem && _ehRef, \"<span class='val fim\" & _ngRot & \"' style='left:\" & ( _lRef - _colL ) & \"px;top:\""
        " & _yRot & \"px;animation-delay:\" & ( _atraso + 700 ) & \"ms'>\" & " + C.marca("_fTxt") + " & \"</span>\",",
        "                _tem && _ehExt, \"<span class='val\" & _ngRot & \"' style='left:\" & ( _lExt - _colL ) & \"px;top:\""
        " & _yRot & \"px'>\" & " + C.marca("_fTxt") + " & \"</span>\",",
        "                \"\"",
        "            )",
        "        RETURN",
        "            \"<div class='c'>\" & _rot",
        "                & IF ( _tem, \"<i class='bar \" & _cls & \"' style='top:\" & _top & \"px;height:\" & _h & \"px' data-rk='m\""
        " & [@ord] & \"' data-rp='top,height' data-r0-top='\" & _yZero & \"px' data-r0-height='0px' data-rd='\" & _atraso"
        " & \"'></i>\" )",
        "                & \"<span class='ms\" & IF ( _ehRef, \" ref\", IF ( _tem, \"\", \" sem\" ) ) & \"'>\" & [@rot] & \"</span>"
        "</div>\",",
        "        \"\",",
        "        dMes[Mes], ASC",
        "    )",
        "VAR _altSerie =",
        "    IF ( _todaNeg, 86, _yZero + ROUND ( DIVIDE ( _neg, _esc ) * 44, 0 ) + IF ( _neg > 0, 21, 0 ) + 22 ) -- geometria",
    ]


def bloco_serie(titulo: str) -> str:
    return (f"\"<div class='rg'></div><span class='vs sl'>\" & {titulo} & \"</span>\""
            " & \"<div class='ser' style='--alt:\" & _altSerie & \"px;--b:\" & _bSer & \"px'>\" & _htmlSerie & \"</div>\"")


def lista_meses(medida_v: str, medida_s: str | None = None) -> list[str]:
    cols = [f'        "@v", [{medida_v}],']
    if medida_s:
        cols.append(f'        "@s", [{medida_s}],')
    return [
        "VAR _nSer = [Série · meses até a referência]",
        "VAR _meses =",
        "    ADDCOLUMNS (",
        "        VALUES ( dMes[Mes] ),",
        '        "@ate", [Série · mês até a referência],',
        '        "@ord", [Mês · ordem],',
        '        "@pos", [Série · posição na janela],',
    ] + cols + [
        '        "@rot", [Mês · abreviado]',
        "    )",
        "VAR _serie = FILTER ( _meses, [@ate] = 1 ) /* lista */",
    ]


# ===================================================================================================== Item
TABELA_NOME = {"SaldoContrato": "Saldo de contrato", "AdiantServicos": "Adiantamento de serviços não medidos",
               "AdiantMateriais": "Adiantamento de materiais não estocados", "Estoque": "Estoque de materiais",
               "Equipamentos": "Equipamentos comprados", "ReceitaPersonalizacao": "Receitas de personalizações",
               "ContasPagar": "Contas a pagar dos medidos", "Divida": "Dívida da obra a ser paga"}
O_QUE_E = {
    "Credito": "Quanto a obra podia ter gasto: orçamento projetado × executado acumulado. Não tem tabela anexada — é "
               "fórmula.",
    "SaldoContrato": "Desconto obtido num contrato, usado como artifício temporário (elevador e esquadrias); abatido "
                     "conforme o serviço é medido.",
    "AdiantServicos": "Sinal pago a um contrato cujo serviço ainda não foi medido; soma porque o dinheiro já saiu.",
    "AdiantMateriais": "Material pago que ainda não chegou à obra; soma porque o dinheiro já saiu antes da entrega.",
    "Estoque": "Material comprado e ainda não aplicado, informado pelo almoxarifado; soma porque o dinheiro já saiu "
               "antes da medição.",
    "Equipamentos": "Equipamento comprado que pode ser reaproveitado em outra obra, a valor de mercado.",
    "ReceitaPersonalizacao": "Reformas e personalizações pagas pelo cliente (personalizações), que entram como receita da obra.",
    "ContasPagar": "Serviço já medido e ainda sendo pago ao fornecedor; desconta porque o gasto já está comprometido.",
    "Desembolsado": "Desembolso acumulado da obra desde o início, conferido com o relatório; o maior desconto da conta.",
    "Divida": "Material de outra obra usado nesta, a devolver; soma de volta na conta.",
}
CURTO = {"Credito": "Crédito", "SaldoContrato": "Saldo de contrato", "AdiantServicos": "Adiant. de serviços",
         "AdiantMateriais": "Adiant. de materiais", "Estoque": "Estoque", "Equipamentos": "Equipamentos",
         "ReceitaPersonalizacao": "Receita de personalizações", "ContasPagar": "Contas a pagar", "Desembolsado": "Desembolsado",
         "Divida": "Dívida"}
direita_item = ("SWITCH ( _item, \"Credito\", \"8º passo · executado acumulado × orçamento\", \"Desembolsado\", \"RELATÓRIO CONFERIDO · 15º passo\", "
                "IF ( _sinal < 0, \"DESCONTA\", \"SOMA\" ) & \" · TABELA ANEXADA · \" & "
                + sw("_item", TABELA_NOME) + " )")

desenho(
    "T2 · Tooltip item · HTML",
    "Tooltip de página do item do quadradinho (linha de O quadradinho): o que o item é, as linhas da tabela anexada "
    f"que o compõem (até {LINHAS_MAX}; com mais, {LINHAS_MAX - 1} e 'e mais N linhas') e o item mês a mês. Estados: "
    "completo; vazio (item em zero: aviso no lugar das linhas, sem série); fórmula (crédito e desembolsado, sem "
    "tabela; o crédito traz o físico do mês no rodapé).",
    linhas(
        "-- 1 · Leituras",
        "VAR _item = SELECTEDVALUE ( dItem[Item] )",
        "VAR _ordem = [Item · ordem]",
        "VAR _rotItem = SELECTEDVALUE ( dItem[Rotulo] )",
        "VAR _sinal = SELECTEDVALUE ( dItem[Sinal] )",
        "VAR _ref = [Mês de referência]",
        "VAR _obra = [Nota · obra em foco]",
        "VAR _mesCM = [Mês de referência · curto maiúsculo]",
        "VAR _aba = [Aba · foco]",
        "VAR _v = [Item · valor · foco]",
        "VAR _pm = [Físico · previsto no mês · foco]",
        "VAR _em = [Físico · executado no mês · foco]",
        "VAR _linhasTab =",
        "    ADDCOLUMNS (",
        "        VALUES ( fItens[Linha] ),",
        '        "@d", [Item · linha · descrição · foco],',
        '        "@v", [Item · linha · valor · foco]',
        "    )",
        "VAR _comLinha = FILTER ( _linhasTab, NOT ISBLANK ( [@v] ) && [@v] <> 0 ) /* lista */",
        "VAR _nLin = COUNTROWS ( _comLinha ) + 0 /* geometria */",
        f"VAR _nMostra = IF ( _nLin > {LINHAS_MAX}, {LINHAS_MAX - 1}, _nLin ) /* geometria */",
        "VAR _mostra = TOPN ( _nMostra, _comLinha, fItens[Linha], ASC ) /* lista */",
        lista_meses("Item · valor · foco no mês"),
        "-- 2 · Textos",
        D.od_tabela(),
        "VAR _formula = _item IN { \"Credito\", \"Desembolsado\" }",
        "VAR _zero = ISBLANK ( _v ) || _v = 0",
        "VAR _txtSob = \"O QUADRADINHO · \" & UPPER ( _obra ) & \" · \" & _mesCM & IF ( _aba = \"\", \"\", \" · ABA \" & _aba )",
        "VAR _txtDir = " + direita_item,
        "VAR _txtOque = " + sw("_item", O_QUE_E),
        "VAR _txtSerieTit = " + sw("_item", CURTO) + " & \", mês a mês\"",
        "VAR _htmlLinhas =",
        "    CONCATENATEX (",
        "        _mostra,",
        "        VAR _lv = [@v]",
        "        VAR _lTxt = \"R$ \" & FORMAT ( _lv, \"#,0.00\", \"pt-BR\" )",
        "        RETURN",
        "            \"<div class='lin it'><span class='d2'>\" & " + D.esc("[@d]") + " & \"</span><span class='v'>\" & _lTxt"
        " & \"</span></div>\",",
        "        \"\",",
        "        fItens[Linha], ASC",
        "    )",
        "VAR _maisN = _nLin - _nMostra",
        "VAR _htmlMais = IF ( _maisN > 0, \"<div class='lin mais'>e mais \" & _maisN & IF ( _maisN = 1, \" linha\", \" linhas\" )"
        " & \" na tabela anexada</div>\", \"\" )",
        serie("_serie", "_ref"),
        D.pct("_em", "_te", casas=2), D.pct("_pm", "_tp", casas=2),
        "VAR _blocoLinhas =",
        "    SWITCH (",
        "        TRUE (),",
        "        _formula, \"\",",
        "        _zero, \"<div class='rg'></div><p class='vz'>Nenhuma linha este mês: o item está em zero e não entra na conta.</p>\",",
        "        \"<div class='rg'></div><div class='bh'><span class='vs'>Linhas da tabela anexada</span><span class='vs'>Valor</span>"
        "</div>\" & _htmlLinhas & _htmlMais",
        "    )",
        "VAR _blocoSerie = IF ( _vMax = 0 && _vMin = 0, \"\", " + bloco_serie("_txtSerieTit") + " )",
        "VAR _rod = IF ( _item = \"Credito\", " + rodape("\"No mês: \" & _teTxt & \" executado × \" & _tpTxt & \" previsto.\"")
        + ", \"\" )",
        "-- 4 · Marcação",
        "RETURN",
        "    IF (",
        "        NOT ISBLANK ( _item ) && NOT ISBLANK ( [Orçamento · foco] ),",
        "        " + cabeca("_txtSob", "_rotItem", "\"ITEM \" & FORMAT ( _ordem, \"00\" )", "_txtDir"),
        "            & \"<div class='corpo'><span class='vs sl'>O que é</span><p class='tx'>\" & _txtOque & \"</p>\"",
        "            & _blocoLinhas & _blocoSerie & \"</div>\" & _rod",
        "        & \"</div>\" & [Comum · JS contador tooltip] & [Comum · JS corrida]",
        "    )",
    ))

# ===================================================================================================== Degrau
# F3 (docs/08 §5): os degraus da cascata nova. O quadradinho saiu da tela; as linhas dele que formam cada degrau vêm
# aqui, com o sinal da conta (o "−" em vermelho). Resultado aplicado e resultado da planilha mostram a conta dos
# degraus. Embaixo, o degrau mês a mês; no pé, uma linha por degrau.
COMPOE = {  # degrau → [(item do quadradinho, sinal na conta do degrau)]
    "ValorAgregado": [("Credito", 1)],
    "CustoAplicado": [("Desembolsado", 1), ("ContasPagar", 1), ("Divida", 1), ("AdiantServicos", -1),
                      ("AdiantMateriais", -1), ("Estoque", -1), ("ReceitaPersonalizacao", -1)],
    "ARealizar": [("SaldoContrato", 1), ("Equipamentos", 1)],
}
_COMPOE_DAX = "{ " + ", ".join(f'( "{d}", "{it}", {sg}, {k} )' for d, lst in COMPOE.items()
                               for k, (it, sg) in enumerate(lst, 1)) + " }"
desenho(
    "T2 · Tooltip degrau · HTML",
    "Tooltip de página do degrau da cascata (Como o resultado se forma): as linhas do quadradinho que formam o degrau, "
    "com o sinal da conta (zeros esmaecidos), o degrau mês a mês e uma linha de rodapé por degrau, presa ao pé. No "
    "resultado aplicado e no resultado da planilha, os degraus da conta (o \"−\" em vermelho) e o resultado mês a mês "
    "com valores positivos e negativos. Estado vazio: degrau todo em zero.",
    linhas(
        "-- 1 · Leituras",
        "VAR _deg = SELECTEDVALUE ( dDegrau[Degrau] )",
        "VAR _ordemDeg = [Cascata · degrau · ordem]",
        "VAR _rotDeg = SELECTEDVALUE ( dDegrau[Rotulo] )",
        "VAR _sinal = SELECTEDVALUE ( dDegrau[Sinal] )",
        "VAR _ref = [Mês de referência]",
        "VAR _obra = [Nota · obra em foco]",
        "VAR _mesCM = [Mês de referência · curto maiúsculo]",
        "VAR _mesN = [Mês de referência · nome]",
        "VAR _nDeg = [Cascata · degraus · foco]",
        "VAR _v = [Cascata · degrau · valor · foco]",
        "VAR _pctOrc = [Cascata · degrau · % do orçamento · foco]",
        "VAR _exec = [Físico · executado acumulado · foco]",
        "VAR _idc = [IDC · foco]",
        "VAR _pctRes = [Resultado % · foco]",
        "VAR _vVA = CALCULATE ( [Cascata · degrau · valor · foco], dDegrau[Degrau] = \"ValorAgregado\" )",
        "VAR _vCA = CALCULATE ( [Cascata · degrau · valor · foco], dDegrau[Degrau] = \"CustoAplicado\" )",
        "VAR _vRA = CALCULATE ( [Cascata · degrau · valor · foco], dDegrau[Degrau] = \"ResultadoAplicado\" )",
        "VAR _vAR = CALCULATE ( [Cascata · degrau · valor · foco], dDegrau[Degrau] = \"ARealizar\" )",
        "VAR _vR = CALCULATE ( [Cascata · degrau · valor · foco], dDegrau[Degrau] = \"Resultado\" )",
        # as linhas do quadradinho que formam o degrau, com o sinal na conta do degrau
        f"VAR _tabCompoe = {_COMPOE_DAX} /* lista */",
        "VAR _compoe = FILTER ( _tabCompoe, [Value1] = _deg ) /* lista */",
        "VAR _linhas =",
        "    ADDCOLUMNS (",
        "        _compoe,",
        "        \"@rot\", VAR _c = [Value2] RETURN CALCULATE ( [Item · rótulo], dItem[Item] = _c ),",
        "        \"@v\", VAR _c = [Value2] RETURN CALCULATE ( [Item · valor · foco], dItem[Item] = _c )",
        "    ) /* lista */",
        lista_meses("Cascata · degrau · valor · foco no mês"),
        "-- 2 · Textos",
        D.od_tabela(),
        "VAR _ehConta = _deg IN { \"ResultadoAplicado\", \"Resultado\" }",
        "VAR _zero = ( ISBLANK ( _v ) || _v = 0 ) && NOT _ehConta",
        "VAR _txtSob = \"COMO O RESULTADO SE FORMA · \" & UPPER ( _obra ) & \" · \" & _mesCM",
        D.pct("_pctOrc", "_tpo", casas=2, mais=True), D.pct("_pctRes", "_tpr", casas=2, mais=True),
        "VAR _txtDir =",
        "    IF (",
        "        _ehConta,",
        "        \"RESULTADO · \" & " + ng_m("_tpo") + " & \" DO ORÇAMENTO\",",
        "        IF ( _sinal < 0, \"DESCONTA\", \"SOMA\" ) & \" · \" & " + C.marca('SUBSTITUTE ( _tpoTxt, "+", "" )') + " & \" DO ORÇAMENTO\"",
        "    )",
        "VAR _txtCod = \"DEGRAU \" & _ordemDeg & \" DE \" & _nDeg",
        "VAR _nLs = IF ( _ehConta, 3, COUNTROWS ( _linhas ) ) /* lista */",
        "VAR _htmlItens =",
        "    CONCATENATEX (",
        "        _linhas,",
        "        VAR _iv = [@v]",
        "        VAR _z = ISBLANK ( _iv ) || _iv = 0",
        "        VAR _iTxt = \"R$ \" & FORMAT ( ABS ( _iv + 0 ), \"#,0.00\", \"pt-BR\" )",
        "        RETURN",
        "            \"<div class='lin cf so\" & IF ( _z, \" z\", \"\" ) & \"'><span class='sg\" & IF ( [Value3] < 0, \" ng'>"
        + MENOS + "\", \"'>+\" ) & \"</span>\"",
        "                & \"<span class='n'>\" & [@rot] & \"</span><span class='v'>\" & " + C.marca("_iTxt") + " & \"</span></div>\",",
        "        \"\",",
        "        [Value4], ASC",
        "    )",
        D.rs("_vVA", "_t1"), D.rs("_vCA", "_t2"), D.rs("_vRA", "_t3"), D.rs("_vAR", "_t4"), D.rs("_vR", "_t5"),
        "VAR _lin = \"<div class='lin cf so'><span class='sg\"",
        "VAR _htmlContaRA =",
        "    _lin & \"'>+</span><span class='n'>Valor agregado</span><span class='v'>\" & " + C.marca("_t1Txt") + " & \"</span></div>\"",
        "        & _lin & \" ng'>" + MENOS + "</span><span class='n'>Custo aplicado</span><span class='v'>\" & " + C.marca("_t2Txt") + " & \"</span></div>\"",
        "        & _lin & \"'>=</span><span class='n'>Resultado aplicado</span><span class='v'>\" & " + ng_m("_t3") + " & \"</span></div>\"",
        "VAR _htmlContaR =",
        "    _lin & \"'>+</span><span class='n'>Resultado aplicado</span><span class='v'>\" & " + ng_m("_t3") + " & \"</span></div>\"",
        "        & _lin & \"'>+</span><span class='n'>A realizar</span><span class='v'>\" & " + C.marca("_t4Txt") + " & \"</span></div>\"",
        "        & _lin & \"'>=</span><span class='n'>Resultado da planilha</span><span class='v'>\" & " + ng_m("_t5") + " & \"</span></div>\"",
        "VAR _titLista = IF ( _ehConta, \"Degraus da conta\", \"Linhas da planilha que formam o degrau\" )",
        "VAR _txtSerieTit = _rotDeg & \", mês a mês\"",
        serie("_serie", "_ref"),
        D.pct("_exec", "_te"),
        "VAR _txtIdc = FORMAT ( _idc, \"0.00\", \"pt-BR\" )",
        "VAR _txtRod =",
        "    SWITCH (",
        "        TRUE (),",
        "        _zero, \"Nada lançado em \" & _mesN & \": o degrau fica em zero.\",",
        "        _deg = \"ValorAgregado\", \"Único degrau que cresce com o físico: \" & " + C.marca("_teTxt") + " & \" executado × orçamento.\",",
        "        _deg = \"CustoAplicado\", \"O que já virou obra, com a dívida. IDC = agregado ÷ este custo: \" & " + C.marca("_txtIdc") + " & \".\",",
        "        _deg = \"ResultadoAplicado\", \"O que a obra já ganhou ou perdeu no que executou.\",",
        "        _deg = \"ARealizar\", \"A planilha conta como ganho e ainda não aconteceu.\",",
        "        \"É o que a planilha apresenta: \" & " + ng_m("_tpr") + " & \" do orçamento.\"",
        "    )",
        "-- 4 · Marcação",
        "RETURN",
        "    IF (",
        "        NOT ISBLANK ( _deg ) && NOT ISBLANK ( [Orçamento · foco] ),",
        "        " + cabeca("_txtSob", "_rotDeg", "_txtCod", "_txtDir"),
        "            & \"<div class='corpo crp'><div class='bh'><span class='vs'>\" & _titLista & \"</span><span class='vs'>Valor"
        "</span></div>\"",
        "            & \"<div class='lsb\" & " + TL.atributos("_nLs") + "'>\" & SWITCH ( _deg, \"ResultadoAplicado\", _htmlContaRA, \"Resultado\", _htmlContaR, _htmlItens ) & \"</div>\"",
        "            & IF ( _vMax = 0 && _vMin = 0, \"\", " + bloco_serie("_txtSerieTit") + " ) & \"</div>\"",
        "            & " + rodape("_txtRod"),
        "        & \"</div>\" & [Comum · JS contador tooltip] & [Comum · JS corrida]",
        "    )",
    ))

# ===================================================================================================== Mês
GRUPOS = [("SaldoContrato", "saldo de contrato"), ("AdiantServicos", "adiantamento de serviços"),
          ("AdiantMateriais", "adiantamento de materiais"), ("Estoque", "estoque de materiais"),
          ("Equipamentos", "equipamentos"), ("ReceitaPersonalizacao", "receita de personalizações")]
desenho(
    "T2 · Tooltip mês · HTML",
    "Tooltip de página do mês (coluna do IDC, mês a mês): como o resultado se formou no mês (valor agregado, custo "
    "aplicado, resultado aplicado com o IDC, a realizar e o resultado da planilha), o que mudou desde o mês anterior e o "
    "desembolso do mês (desvio negativo em preto); a justificativa vai no rodapé, numa linha, preso ao pé. Primeiro mês "
    "do histórico: sem o bloco 'desde'.",
    linhas(
        "-- 1 · Leituras",
        "VAR _mesL = [Mês · longo]",
        "VAR _mesAntN = [Mês anterior · nome]",
        "VAR _obra = [Nota · obra em foco]",
        "VAR _selo = [Obra em foco · selo]",
        "VAR _aba = [Aba · foco no mês]",
        "VAR _primeiro = [Mês · é o primeiro do histórico] = 1",
        "VAR _exec = [Físico · executado acumulado · foco no mês]",
        "VAR _prev = [Físico · previsto acumulado · foco no mês]",
        "VAR _cred = [Crédito do orçamento · foco no mês]",
        "VAR _ca = [Custo aplicado · foco no mês]",
        "VAR _ra = [Resultado aplicado · foco no mês]",
        "VAR _ar = [A realizar · foco no mês]",
        "VAR _res = [Resultado da obra · foco no mês]",
        "VAR _idc = [IDC · foco no mês]",
        "VAR _pct = [Resultado % · foco no mês]",
        "VAR _pctAnt = [Resultado % · mês anterior · foco no mês]",
        "VAR _var = [Resultado · variação p.p. · foco no mês]",
        "VAR _estAnt = [Estoque de materiais · mês anterior · foco no mês]",
        "VAR _dr = [Desembolso · realizado no mês · foco no mês]",
        "VAR _dp = [Desembolso · previsto no mês · foco no mês]",
        "VAR _desv = [Desembolso · desvio no mês · foco no mês]",
        "VAR _pfx = CALCULATE ( [Nota · item · pontos · foco no mês], dItemNota[Item] = \"caixa\" )",
        "VAR _sfx = CALCULATE ( [Nota · item · possíveis · foco no mês], dItemNota[Item] = \"caixa\" )",
        "VAR _just = [Justificativa do desembolso · foco no mês]",
        "VAR _exig = [Justificativa · exigida · foco no mês]",
        "VAR _branco = [Justificativa · em branco · foco no mês]",
        "-- 2 · Textos",
        D.od_tabela(),
        D.rs("_cred", "_tc"), D.od_rs("_cred", "_tc"), D.rs("_ca", "_tca"), D.od_rs("_ca", "_tca"),
        D.rs("_ra", "_tra"), D.od_rs("_ra", "_tra"), D.rs("_ar", "_tar"), D.od_rs("_ar", "_tar"),
        D.rs("_res", "_tres"), D.od_rs("_res", "_tres"),
        D.pct("_exec", "_te"), D.pct("_prev", "_tpv"), D.pct("_pct", "_tp", casas=2, mais=True),
        D.pct("_pctAnt", "_tpa", casas=2, mais=True), D.pp("_var", "_tv", casas=2), D.rs("_estAnt", "_tea"),
        D.rs("_dr", "_tdr"), D.rs("_dp", "_tdp"), D.pct("_desv", "_tdv", casas=0, mais=True), D.od_pct("_desv", "_tdv"),
        DC.item_txt("_tfx", "_pfx", "_sfx", fonte="ac"),
        "VAR _txtSob = \"IDC, MÊS A MÊS · \" & UPPER ( _obra ) & IF ( _selo = \"\", \"\", \" · \" & _selo )"
        " & IF ( _primeiro, \" · PRIMEIRO MÊS DO HISTÓRICO\", \"\" )",
        "VAR _txtDir = \"IDC \" & " + C.marca('FORMAT ( _idc, "0.00", "pt-BR" )') + " & \" · EXECUTADO \" & " + C.marca("_teTxt") + " & \" × PREVISTO \" & " + C.marca("_tpvTxt"),
        "VAR _lin = \"<div class='lin cf'><span class='sg\"",
        "VAR _htmlConta =",
        "    _lin & \"'>+</span><span class='n'>Valor agregado</span><span class='v'>\" & _tcOd & \"</span>"
        "<span class='d'>orçamento × executado</span></div>\"",
        "        & _lin & \" ng'>−</span><span class='n'>Custo aplicado</span><span class='v'>\" & _tcaOd & \"</span>"
        "<span class='d'>o que já virou obra</span></div>\"",
        "        & _lin & \"'>=</span><span class='n'>Resultado aplicado</span><span class='v\" & IF ( _ra < 0, \" ng\", \"\" ) "
        "& \"'>\" & _traOd & \"</span><span class='d'>IDC \" & " + C.marca('FORMAT ( _idc, "0.00", "pt-BR" )') + " & \"</span></div>\"",
        "        & _lin & \"'>+</span><span class='n'>A realizar</span><span class='v'>\" & _tarOd & \"</span>"
        "<span class='d'>saldo de contrato e equipamentos</span></div>\"",
        "        & _lin & \"'>=</span><span class='n'>Resultado da planilha</span><span class='v\" & IF ( _res < 0, \" ng\", \"\" ) "
        "& \"'>\" & _tresOd & \"</span><span class='d'>\" & " + C.marca("_tpTxt") + " & \" do orçamento</span></div>\"",
        "VAR _txtDesde = \"Resultado de \" & " + ng_m("_tpa") + " & \" para \" & " + ng_m("_tp") + " & \" (\" & "
        + ng_m("_tv") + " & \")\" & IF ( ISBLANK ( _estAnt ), \".\", \"; o estoque era \" & " + C.marca("_teaTxt") + " & \".\" )",
        "VAR _txtJust =",
        "    SWITCH (",
        "        TRUE (),",
        "        _branco = 1, \"Justificativa exigida e não preenchida.\",",
        "        _exig = 1 && TRIM ( _just ) <> \"\", \"Justificativa: \" & " + D.esc("LOWER ( LEFT ( TRIM ( _just ), 1 ) ) & MID ( TRIM ( _just ), 2, 200 )") + ",",
        "        \"\"",
        "    )",
        "-- 4 · Marcação",
        "RETURN",
        "    IF (",
        "        NOT ISBLANK ( _cred ),",
        "        " + cabeca("_txtSob", "_mesL", "IF ( _aba = \"\", BLANK (), \"ABA \" & _aba )", "_txtDir"),
        "            & \"<div class='corpo\" & IF ( _txtJust = \"\", \"\", \" crp\" ) & \"'><span class='vs sl'>Como o resultado se formou</span>\"",
        "            & \"<div class='lsb\" & " + TL.atributos("5") + "'>\" & _htmlConta & \"</div>\"",
        "            & IF ( NOT _primeiro && NOT ISBLANK ( _pctAnt ), \"<div class='rg'></div><span class='vs sl'>Desde \" & _mesAntN"
        " & \"</span><p class='tx'>\" & _txtDesde & \"</p>\" )",
        "            & \"<div class='rg'></div><span class='vs sl'>Desembolso do mês\" & IF ( ISBLANK ( _pfx ), \"\", \" · previsão de \""
        " & \"caixa \" & " + C.marca("_tfxTxt") + " ) & \"</span>\"",
        "            & \"<p class='des'>\" & " + marca_item("_pfx", "_sfx") + " & " + C.marca("_tdrTxt") + " & \" × \" & " + C.marca("_tdpTxt") + " & \" previsto<b>\""
        " & _tdvOd"
        " & \"</b></p></div>\"",
        "            & IF ( _txtJust = \"\", \"\", " + rodape("_txtJust") + " )",
        "        & \"</div>\" & [Comum · JS contador tooltip]",
        "    )",
    ))

# ==================================================================================================== Item da nota
# Tooltip do item da nota da linha de Itens da nota: as faixas do item lidas do modelo (Nota · item · faixas), com a
# faixa atingida marcada na cor dos pontos. Embaixo, os pontos do item mês a mês da obra em foco e, no rodapé preso ao
# pé, o que mudou desde o mês anterior. Nenhum limite fica escrito aqui.
VALOR_FORA = "valor fora da faixa válida"
desenho(
    "T2 · Tooltip item da nota · HTML",
    "Tooltip de página do item da nota (linha de Itens da nota): as faixas do item como estão no modelo, com a faixa "
    "atingida marcada na cor dos pontos, o X do mês, os pontos do item mês a mês na obra em foco e, no rodapé preso ao "
    "pé, o que mudou desde o mês anterior. Estados: com dado, sem dado (falta na base / sem dado na planilha), valor "
    "fora da faixa válida.",
    linhas(
        "-- 1 · Leituras",
        "VAR _cod = SELECTEDVALUE ( dItemNota[Item] )",
        "VAR _nome = [Nota · item · nome]",
        "VAR _fonte = [Nota · item · fonte]",
        "VAR _pts = [Nota · item · pontos · foco]",
        "VAR _poss = [Nota · item · possíveis · foco]",
        "VAR _x = [Nota · item · X · foco]",
        "VAR _fx = [Nota · item · faixa atingida · foco]",
        "VAR _faixas = [Nota · item · faixas]",
        "VAR _ptsAnt = [T2 · Item da nota · pontos no mês anterior · foco]",
        "VAR _possAnt = [T2 · Item da nota · possíveis no mês anterior · foco]",
        "VAR _foraAnt = [T2 · Item da nota · fora da faixa no mês anterior · foco] + 0",
        "VAR _ref = [Mês de referência]",
        "VAR _obra = [Nota · obra em foco]",
        "VAR _mesCM = [Mês de referência · curto maiúsculo]",
        "VAR _mesN = [Mês de referência · nome]",
        "VAR _mesAntN = [Mês anterior à referência · nome]",
        "VAR _nSer = [Série · meses até a referência]",
        "VAR _meses =",
        "    ADDCOLUMNS (",
        "        VALUES ( dMes[Mes] ),",
        '        "@ate", [Série · mês até a referência],',
        '        "@ord", [Mês · ordem],',
        '        "@pos", [Série · posição na janela],',
        '        "@v", [Nota · item · pontos · foco no mês],',
        '        "@p", [Nota · item · possíveis · foco no mês],',
        '        "@rot", [Mês · abreviado]',
        "    )",
        # classe dos pontos de cada mês (desenho: só escolhe a cor): cheio, parcial, zero; sem dado fica neutro
        "VAR _serie =",
        "    ADDCOLUMNS (",
        "        FILTER ( _meses, [@ate] = 1 ), /* lista */",
        '        "@s",',
        "            IF (",
        "                ISBLANK ( [@v] ) || [@p] = 0, BLANK (),",
        "                IF ( [@v] >= [@p], 0, IF ( [@v] = 0, 2, 1 ) )",
        "            )",
        "    ) /* lista */",
        "-- 2 · Textos",
        D.od_tabela(),
        DC.item_txt("_ca", "_pts", "_poss", fonte="ac"), DC.item_txt("_cb", "_pts", "_poss", fonte="base"),
        DC.item_txt("_cn", "_ptsAnt", "_possAnt", fonte="base"),
        "VAR _txtPts = IF ( _fonte = \"Análise Crítica\", _caTxt, _cbTxt )",
        "VAR _fora = [Nota · item · fora da faixa · foco]",
        # valor fora da faixa válida: o item fica sem pontos, mas não por falta
        "VAR _txtDir =",
        "    SWITCH (",
        "        TRUE (),",
        "        ISBLANK ( _pts ) && _fora = 1, \"" + VALOR_FORA + "\",",
        "        NOT ISBLANK ( _pts ) && _poss = 0, \"não conta\",",
        "        " + C.marca("_txtPts"),
        "    )",
        "VAR _txtSob = \"ITENS DA NOTA · \" & UPPER ( _obra ) & \" · \" & _mesCM & \" · \" & UPPER ( _fonte )",
        x_item("_cod", "_x", "_fx", "_pts"),
        "VAR _clsOn = IF ( ISBLANK ( _pts ) || _poss = 0, \"mkv\", IF ( _pts >= _poss, \"mk0\", IF ( _pts = 0, \"mk2\", \"mk1\" ) ) )",
        # faixas do item como estão no modelo: "rótulo → pontos", separadas por " · "
        "VAR _segs = SUBSTITUTE ( _faixas, \" · \", \"|\" )",
        "VAR _nSeg = IF ( _segs = \"\", 0, PATHLENGTH ( _segs ) )",
        "VAR _htmlFx =",
        "    CONCATENATEX (",
        "        GENERATESERIES ( 1, _nSeg ),",
        "        VAR _sg = PATHITEM ( _segs, [Value] )",
        "        VAR _on = NOT ISBLANK ( _fx ) && LEFT ( _sg, LEN ( _fx ) + 2 ) = _fx & \" →\"",
        "        RETURN",
        "            \"<span class='f\" & IF ( _on, \" on\", \"\" ) & \"'><i class='mk \" & IF ( _on, _clsOn, \"mkv\" ) & \"'></i>\"",
        "                & " + faixa_html("_sg") + " & \"</span>\",",
        "        \"\",",
        "        [Value], ASC",
        "    ) /* lista */",
        "VAR _txtNota = [Nota · item · explica]",
        "VAR _nFx = MAX ( 1, ROUNDUP ( _nSeg / 2, 0 ) )",
        "VAR _txtFxTit = \"Faixas\"",
        "VAR _txtNoMes = IF ( _txtX = \"\", \"\", \"No mês: \" & _txtX )",
        serie("_serie", "_ref", modo="pts"),
        "VAR _txtRod =",
        "    SWITCH (",
        "        TRUE (),",
        # valor fora da faixa antes de "sem dado" (auditoria da Fase 3, minor 1: o rodapé dizia "Sem dado em julho nem
        # em agosto" sob "VALOR FORA DA FAIXA")
        "        ISBLANK ( _ptsAnt ) && ISBLANK ( _pts ),",
        "            SWITCH (",
        "                TRUE (),",
        "                _foraAnt = 1 && _fora = 1, \"Valor fora da faixa em \" & _mesAntN & \" e em \" & _mesN & \".\",",
        "                _fora = 1, \"Sem dado em \" & _mesAntN & \"; em \" & _mesN & \", o valor está fora da faixa.\",",
        "                _foraAnt = 1, \"Em \" & _mesAntN & \", o valor estava fora da faixa; agora falta o dado.\",",
        "                \"Sem dado em \" & _mesAntN & \" nem em \" & _mesN & \".\"",
        "            ),",
        "        ISBLANK ( _ptsAnt ), IF ( _foraAnt = 1, \"Em \" & _mesAntN & \", o valor estava fora da faixa.\", "
        "\"Em \" & _mesAntN & \", o item não tinha dado.\" ),",
        "        ISBLANK ( _pts ), \"Era \" & " + C.marca("_cnTxt") + " & \" em \" & _mesAntN & IF ( _fora = 1, \"; agora o valor está fora da faixa.\", "
        "\"; agora falta o dado.\" ),",
        # na precisão que o leitor vê (FMT_PTS, 2 casas): desde o ÷ 10, os termômetros variam na 4ª casa (1,4121 × 1,4128)
        "        ROUND ( _pts, 2 ) = ROUND ( _ptsAnt, 2 ) && _poss = _possAnt, \"Mesmos pontos de \" & _mesAntN & \".\",",
        "        \"Era \" & " + C.marca("_cnTxt") + " & \" em \" & _mesAntN & \".\"",
        "    )",
        "-- 4 · Marcação",
        "RETURN",
        "    IF (",
        "        NOT ISBLANK ( _cod ) && NOT ISBLANK ( [Nota · pontos possíveis · ranking · foco] ),",
        "        " + cabeca("_txtSob", "_nome", None, "_txtDir"),
        "            & \"<div class='corpo crp'><div class='bh'><span class='vs'>\" & _txtFxTit & \"</span><span class='vs'>\" & " + C.marca("_txtNoMes")
        + " & \"</span></div>\"",
        "            & \"<div class='fx\" & " + TL.atributos("_nFx") + "'>\" & _htmlFx & \"</div>\"",
        "            & IF ( _txtNota = \"\", \"\", \"<p class='nt'>\" & " + faixa_html("_txtNota") + " & \"</p>\" )",
        "            & IF ( ISEMPTY ( _comV ), \"<div class='rg'></div><p class='vz'>Nenhum mês da janela tem dado deste item.</p>\", "
        + bloco_serie("\"Pontos, mês a mês\"") + " ) & \"</div>\"",
        "            & " + rodape("_txtRod", "\"Desde \" & _mesAntN"),
        "        & \"</div>\" & [Comum · JS contador tooltip] & [Comum · JS corrida]",
        "    )",
    ))

# Fase 2 da régua antiga (13/10/2026): o tooltip do sinal (régua antiga) virou o do item da nota. Fica fora da gravação; o
# gerador apaga o .dax que tinha escrito antes.
RETIRADAS = {"T2 · Tooltip indicador · HTML",
             "T2 · Tooltip item · HTML"}   # F3: o quadradinho saiu da tela (as linhas vão para o tooltip do degrau)

if __name__ == "__main__":
    sys.exit(gravar([x for x in MEDIDAS if x.nome not in RETIRADAS], RAIZ / "dax" / "T2" / "Tooltips", GERADO))

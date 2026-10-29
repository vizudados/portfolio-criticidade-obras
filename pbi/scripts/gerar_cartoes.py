#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gerar_cartoes — cartões de KPI com flip (frente e verso) do painel.

Escreve as medidas de DESENHO (HTML e ALT) em pbi/dax/T<n>/<Cartão>/. Só lêem contas (base/** e T<n>/**/Contas).
Geometria e tipografia lidas do Figma Ymu8hISEG66DR3lg8YS6QS (frente: telas da página Telas; verso: seção
"Versos dos cartões" 60:3443 da página de interações). Depois de gerar, rode contador.py --aplicar (preenche os blocos
do odômetro) e o lint.

    python -X utf8 pbi/scripts/gerar_cartoes.py
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import desenho_lib as D  # noqa: E402

RAIZ = AQUI.parent
DAX = RAIZ / "dax"

# ------------------------------------------------------------------------------------------------ CSS comum dos cartões
CSS_CARTAO = (
    ".fr{position:absolute;left:20px;white-space:nowrap}"
    ".fr--tit{top:16px;font-size:19px;line-height:26px;font-weight:600;color:#1E2433}"
    ".fr--sub{top:42px;font-size:14px;line-height:20px;color:#6B7280}"
    ".fr--rot{font-size:13px;line-height:18px;font-weight:600;color:#6B7280}"
    ".fr--hero{font-size:44px;line-height:52px;font-weight:600;color:#1E2433;letter-spacing:-.2px}"
    ".fr--var{font-size:14px;line-height:20px;color:#474E5E;display:flex;gap:24px}"
    ".up{color:#1F4094}.dn{color:#FE1A21}.eq{color:#6B7280}"
    ".tb{position:absolute;left:20px;right:20px}"
    ".tb__h{position:absolute;left:0;right:0;height:26px;background:#F0F2F5;border-radius:6px}"
    ".tb__c{position:absolute;font-size:13px;line-height:18px;font-weight:600;color:#6B7280;white-space:nowrap}"
    ".tb__l{position:absolute;left:0;right:0;height:28px}"
    ".tb__l+.tb__l{border-top:1px solid #ECEEF2}"
    ".tb__v{position:absolute;font-size:14px;line-height:20px;white-space:nowrap}"
    ".tb__rot{color:#474E5E}.tb__a{font-weight:600;color:#1E2433}.tb__b{color:#6B7280}.tb__d{color:#474E5E}"
    ".r{text-align:right}"
    # verso: Figma 83:3517 (azul da marca, texto branco; sobretítulo, título, termos e definições, fonte no pé)
    ".kc__verso{padding:0!important;display:block!important;border-radius:16px!important}"
    ".vs__sob{position:absolute;left:22px;top:20px;font-size:11px;line-height:14px;font-weight:600;"
    "letter-spacing:.9px;text-transform:uppercase;color:rgba(255,255,255,.75)}"
    ".vs__tit{position:absolute;left:22px;top:40px;font-size:22px;line-height:28px;font-weight:600;color:#FFFFFF}"
    ".vs__l{position:absolute;left:22px;right:22px;display:flex;align-items:center;"
    "border-bottom:1px solid rgba(255,255,255,.16)}"
    ".vs__l:last-of-type{border-bottom-color:rgba(255,255,255,.35)}"
    ".vs__t{width:140px;flex:none;font-size:13px;line-height:18px;font-weight:600;color:#FFFFFF}"
    ".vs__d{font-size:12px;line-height:16px;color:rgba(255,255,255,.88);white-space:normal}"
    ".vs__f{position:absolute;left:22px;right:22px;bottom:18px;font-size:12px;line-height:16px;"
    "color:rgba(255,255,255,.75);white-space:normal}"
)


def verso(titulo: str, linhas: list[tuple[str, str]], fonte: str, altura: int) -> str:
    """HTML do verso (texto estático vindo do Figma). Linhas entre y 84 e o topo da fonte, divididas igualmente."""
    n = len(linhas)
    fonte_alt = 32 if len(fonte) > 70 else 16
    topo, fim = 84, altura - 18 - fonte_alt - 14
    rh = (fim - topo) / n
    partes = [f"<p class='vs__sob'>Como é calculado</p><p class='vs__tit'>{titulo}</p>"]
    for i, (t, d) in enumerate(linhas):
        partes.append(f"<div class='vs__l' style='top:{round(topo + i * rh)}px;height:{round(rh)}px'>"
                      f"<p class='vs__t'>{t}</p><p class='vs__d'>{d}</p></div>")
    partes.append(f"<p class='vs__f'>{fonte}</p>")
    return "".join(partes)


def dax_texto(s: str) -> str:
    return '"' + s.replace('"', '""') + '"'


# ------------------------------------------------------------------------------------------------ T1 · Resultado do mês
def t1_resultado() -> dict[str, str]:
    pasta = DAX / "T1" / "Resultado"
    linhas_verso = [
        ("Venda", "Valor de venda dos itens no mês, nas 10 lojas."),
        ("Lucratividade", "Venda − ICMS − PIS − COFINS − custo líquido."),
        ("Margem", "Lucratividade ÷ venda."),
        ("Markup", "Venda ÷ custo bruto − 1."),
        ("Quantidade", "Unidades e quilos vendidos no mês."),
        ("SKUs vendidos", "Itens diferentes com venda no mês."),
        ("Variação", "Venda e lucratividade: % sobre o mês comparado. Margem e markup: diferença entre os dois meses."),
    ]
    fonte = ("Fonte: WinThor, rotina 322 (venda por produto). SR&nbsp;-&nbsp;Tibiri usa o dado real; as outras lojas "
             "seguem o mesmo padrão.")
    html_verso = verso("Resultado do mês", linhas_verso, fonte, 372)

    L = []
    L.append("-- 1 · Leituras")
    leituras = [
        ("_venda", "Venda (R$)"), ("_vAA", "Venda · variação sobre o ano anterior (%)"),
        ("_vMA", "Venda · variação sobre o mês anterior (%)"),
        ("_mes", "Período · mês (curto)"), ("_aa", "Período · ano anterior (curto)"), ("_ma", "Período · mês anterior (curto)"),
        ("_lucr", "Lucratividade (R$)"), ("_lucrAA", "Lucratividade · ano anterior (R$)"),
        ("_lucrVar", "Lucratividade · variação sobre o ano anterior (%)"),
        ("_marg", "Margem (%)"), ("_margAA", "Margem · ano anterior (%)"), ("_margDif", "Margem · diferença sobre o ano anterior"),
        ("_mkp", "Markup (%)"), ("_mkpAA", "Markup · ano anterior (%)"), ("_mkpDif", "Markup · diferença sobre o ano anterior"),
        ("_qtd", "Quantidade vendida"), ("_qtdAA", "Quantidade · ano anterior"),
        ("_qtdVar", "Quantidade · variação sobre o ano anterior (%)"),
        ("_sku", "SKUs vendidos"), ("_skuAA", "SKUs · ano anterior"), ("_skuDif", "SKUs · diferença sobre o ano anterior"),
        ("_anim", "Exibição · animação ligada"), ("_alt", "T1 · Resultado · ALT"),
    ]
    for v, m in leituras:
        L.append(f"VAR {v} = [{m}]")
    L.append("-- 2 · Textos")
    L += D.compacto("_venda", "_hv")
    L.append('VAR _hvTxt = IF ( ISBLANK ( _venda ), "—", "⁅" & _hvS & "¦" & _hvN & "¦⁆" )')
    L += D.variacao("_vAA", "_va")
    L += D.variacao("_vMA", "_vm")
    L += D.brl("_lucr", "_l1") + D.brl("_lucrAA", "_l2", marca=False) + D.variacao("_lucrVar", "_l3")
    L += D.pct("_marg", "_m1") + D.pct("_margAA", "_m2", marca=False) + D.variacao("_margDif", "_m3")
    L += D.pct("_mkp", "_k1") + D.pct("_mkpAA", "_k2", marca=False) + D.variacao("_mkpDif", "_k3")
    L += D.num("_qtd", "_q1") + D.num("_qtdAA", "_q2", marca=False) + D.variacao("_qtdVar", "_q3")
    L += D.inteiro("_sku", "_s1") + D.inteiro("_skuAA", "_s2", marca=False) + D.variacao("_skuDif", "_s3", tipo="int")
    L.append('VAR _clsAnim = IF ( _anim = 1, "", " sem-anim" )')
    L.append("VAR _altAttr = " + D.esc("_alt"))
    # frente: um texto com os números marcados (o contador transforma num bloco prosa só)
    def linha_tabela(i, rot, a, b, d):
        top = 31 + 28 * i      # 1ª linha 215 − 184 = 31 do topo da tabela; 28 px por linha (Figma)
        return (f"\"<div class='tb__l' style='top:{top - 5}px'>"
                f"<p class='tb__v tb__rot' style='left:12px;top:5px'>{rot}</p>"
                f"<p class='tb__v tb__a r' style='right:178px;top:5px'>\" & {a} & \"</p>"
                f"<p class='tb__v tb__b r' style='right:92px;top:5px'>\" & {b} & \"</p>"
                f"<p class='tb__v tb__d r' style='right:12px;top:5px'>\" & {d} & \"</p></div>\"")
    L.append("VAR _frente =")
    partes = [
        "\"<p class='fr fr--tit'>Resultado do mês</p>\"",
        "\"<p class='fr fr--sub'>\" & _mes & \" · comparado a \" & _aa & \" e \" & _ma & \"</p>\"",
        "\"<p class='fr fr--rot' style='top:78px'>Venda</p>\"",
        "\"<p class='fr fr--hero' style='top:94px'>R$ \" & _hvTxt & _hvU & \"</p>\"",
        "\"<p class='fr fr--var' style='top:150px'><span>\" & _vaTxt & \" sobre \" & _aa & \"</span><span>\" & _vmTxt"
        " & \" sobre \" & _ma & \"</span></p>\"",
        "\"<div class='tb' style='top:184px;height:170px'><div class='tb__h' style='top:0'></div>"
        "<p class='tb__c' style='left:12px;top:4px'>Indicador</p>"
        "<p class='tb__c r' style='right:178px;top:4px'>\" & _mes & \"</p>"
        "<p class='tb__c r' style='right:92px;top:4px'>\" & _aa & \"</p>"
        "<p class='tb__c r' style='right:12px;top:4px'>Variação</p>\"",
        linha_tabela(0, "Lucratividade", "_l1Txt", "_l2Txt", "_l3Txt"),
        linha_tabela(1, "Margem", "_m1Txt", "_m2Txt", "_m3Txt"),
        linha_tabela(2, "Markup", "_k1Txt", "_k2Txt", "_k3Txt"),
        linha_tabela(3, "Quantidade (un.)", "_q1Txt", "_q2Txt", "_q3Txt"),
        linha_tabela(4, "SKUs vendidos", "_s1Txt", "_s2Txt", "_s3Txt"),
        "\"</div>\"",
    ]
    L.append("    " + "\n        & ".join(partes))
    L.append("/* @contador:tabela */")
    L.append("/* @contador:fim */")
    L.append("/* @contador:prosa nome=_fr texto=_frente */")
    L.append("/* @contador:fim */")
    L.append("-- 4 · Marcação")
    L.append("VAR _html =")
    L.append("    \"<div class='vp kc\" & _clsAnim & \"' tabindex='0' role='group' aria-label='\" & _altAttr & \"'>\"")
    L.append("        & \"<div class='kc__gira'>\"")
    L.append("            & \"<section class='kc__face kc__frente'>\" & _frHtml & \"</section>\"")
    L.append("            & \"<section class='kc__face kc__verso' aria-hidden='true'>" + html_verso.replace('"', '""') + "</section>\"")
    L.append("        & \"</div>\"")
    L.append("    & \"</div>\"")
    L.append("RETURN")
    L.append("    \"<style>\" & [Comum · CSS base] & [Comum · CSS cartão] & [Comum · CSS contador] & "
             + dax_texto(CSS_CARTAO) + " & \"</style>\"")
    L.append("        & _html")
    L.append("        & IF ( _anim = 1, [Comum · JS contador] )")
    html = D.cabecalho("T1 Visão geral\\Resultado", "Cartão Resultado do mês (T1), frente e verso com flip no hover e no "
                       "foco (Figma 12:2725 e verso 83:3517). Só lê contas; não calcula.", gerado="pbi/scripts/gerar_cartoes.py")
    html += "\n".join(L) + "\n"

    A = ["-- 1 · Leituras"]
    for v, m in leituras[:-2]:
        A.append(f"VAR {v} = [{m}]")
    A.append("-- 2 · Textos")
    A += D.brl("_venda", "_a1", marca=False) + D.variacao("_vAA", "_a2", marca=False) + D.pct("_marg", "_a3", marca=False)
    A.append("RETURN")
    A.append('    "Resultado do mês, " & _mes & ": venda de " & _a1Txt & ", " & _a2Num & " sobre " & _aa '
             '& "; margem de " & _a3Txt & "."')
    alt = D.cabecalho("T1 Visão geral\\Resultado", "Texto alternativo do cartão Resultado do mês (leitor de tela).",
                      gerado="pbi/scripts/gerar_cartoes.py") + "\n".join(A) + "\n"
    return {str(pasta / "T1 · Resultado · HTML.dax"): html, str(pasta / "T1 · Resultado · ALT.dax"): alt}


def verso_dax(titulo: str, linhas: list[tuple[str, str]], fonte: str, altura: int, fonte_alt: int = 32) -> str:
    """Verso com textos que leem contas: `linhas` = [(termo, definição em expressão DAX)], `fonte` = expressão DAX.
    Devolve uma expressão DAX (concatenação) do HTML."""
    n = len(linhas)
    topo, fim = 84, altura - 18 - fonte_alt - 14
    rh = (fim - topo) / n
    partes = [dax_texto(f"<p class='vs__sob'>Como é calculado</p><p class='vs__tit'>{titulo}</p>")]
    for i, (t, d) in enumerate(linhas):
        partes.append(dax_texto(f"<div class='vs__l' style='top:{round(topo + i * rh)}px;height:{round(rh)}px'>"
                                f"<p class='vs__t'>{t}</p><p class='vs__d'>") + " & " + d + " & " + dax_texto("</p></div>"))
    partes.append(dax_texto("<p class='vs__f'>") + " & " + fonte + " & " + dax_texto("</p>"))
    return "\n            & ".join(partes)


# ------------------------------------------------------------------------------------ T6 · Concentração da venda
CSS_CONC = (
    ".cc__ch{position:absolute;left:20px;top:188px;font-size:12px;line-height:16px;color:#474E5E}"
    ".cc__k{position:absolute;left:20px;top:207px;height:5px;border:1px solid #6B7280;border-bottom:0}"
    ".cc__br{position:absolute;left:20px;right:20px;top:216px;display:flex;gap:2px}"
    ".cc__s{min-width:0;display:flex;flex-direction:column}"
    ".cc__s i{display:block;height:14px;transform-origin:left;animation:ccC .6s cubic-bezier(.2,.7,.2,1) both}"
    ".cc__s b{margin-top:8px;font-size:13px;line-height:18px;font-weight:600;color:#1E2433;white-space:nowrap}"
    ".cc__s span{font-size:12px;line-height:16px;color:#6B7280;white-space:nowrap}"
    "@keyframes ccC{from{transform:scaleX(0)}}"
)


def t6_concentracao() -> dict[str, str]:
    pasta = DAX / "T6" / "Concentracao"
    leituras = [
        ("_p10", "T6 · Concentração · parcela dos 10 maiores (%)"), ("_p5", "T6 · Concentração · parcela dos 5 maiores (%)"),
        ("_p6", "T6 · Concentração · parcela do 6º ao 10º (%)"), ("_p11", "T6 · Concentração · parcela do 11º ao 20º (%)"),
        ("_pD", "T6 · Concentração · parcela dos demais (%)"), ("_nD", "T6 · Concentração · demais fornecedores"),
        ("_nV", "T6 · Concentração · fornecedores com venda"), ("_nC", "T6 · Concentração · fornecedores cadastrados"),
        ("_mes", "Período · mês (curto)"), ("_lojas", "Recorte · lojas (texto)"),
        ("_anim", "Exibição · animação ligada"), ("_alt", "T6 · Concentração · ALT"),
    ]
    L = ["-- 1 · Leituras"] + [f"VAR {v} = [{m}]" for v, m in leituras] + ["-- 2 · Textos"]
    L += D.pct("_p10", "_h") + D.pct("_p5", "_a", marca=False) + D.pct("_p6", "_b", marca=False)
    L += D.pct("_p11", "_c", marca=False) + D.pct("_pD", "_d", marca=False) + D.inteiro("_nV", "_n")
    L.append('VAR _clsAnim = IF ( _anim = 1, "", " sem-anim" )')
    L.append("VAR _altAttr = " + D.esc("_alt"))
    L.append("-- 3 · Geometria")
    for v in ("_p5", "_p6", "_p11", "_pD"):
        L.append(f'VAR {v}F = SUBSTITUTE ( FORMAT ( MAX ( 0.004, {v} ) * 100, "0.000" ), ",", "." ) -- geometria')
    L.append('VAR _kW = SUBSTITUTE ( FORMAT ( ( _p5 + _p6 ) / MAX ( 0.0001, _p5 + _p6 + _p11 + _pD ) * 454 + 2, "0.0" ), ",", "." )'
             ' -- geometria')

    def seg(flex, cor, val, rot, atraso):
        return (f"\"<div class='cc__s' style='flex:\" & {flex} & \" 1 0'><i style='background:{cor};animation-delay:{atraso}ms'>"
                f"</i><b>\" & {val} & \"</b><span>\" & {rot} & \"</span></div>\"")

    L.append("VAR _frente =")
    partes = [
        "\"<p class='fr fr--tit'>Concentração da venda</p>\"",
        "\"<p class='fr fr--sub'>\" & _mes & \" · % da venda por fornecedor · \" & _lojas & \"</p>\"",
        "\"<p class='fr fr--rot' style='top:78px'>Venda nos 10 maiores fornecedores</p>\"",
        "\"<p class='fr fr--hero' style='top:94px'>\" & _hTxt & \"</p>\"",
        "\"<p class='fr' style='top:150px;font-size:14px;line-height:20px;color:#474E5E'>\" & _nTxt & \" fornecedores com venda em \" & _mes & \"</p>\"",
        "\"<p class='cc__ch'>10 maiores</p><i class='cc__k' style='width:\" & _kW & \"px'></i>\"",
        "\"<div class='cc__br'>\"",
        seg("_p5F", "#1F4094", "_aTxt", "\"1º ao 5º\"", 0),
        seg("_p6F", "#6279B4", "_bTxt", "\"6º ao 10º\"", 80),
        seg("_p11F", "#B0BCD9", "_cTxt", "\"11º ao 20º\"", 160),
        seg("_pDF", "#B4B9C4", "_dTxt", "\"Demais \" & FORMAT ( _nD, \"#,0\", \"pt-BR\" )", 240),
        "\"</div>\"",
    ]
    L.append("    " + "\n        & ".join(partes))
    L += ["/* @contador:tabela */", "/* @contador:fim */", "/* @contador:prosa nome=_fr texto=_frente */",
          "/* @contador:fim */"]
    verso = verso_dax("Concentração da venda", [
        ("Participação", "\"Venda do fornecedor ÷ venda da rede em \" & _mes & \".\""),
        ("10 maiores", "\"Soma da participação dos 10 fornecedores de maior venda.\""),
        ("Faixas", "\"1º ao 5º, 6º ao 10º, 11º ao 20º e demais, na mesma ordem.\""),
        ("Fornecedor", "\"Fornecedor do cadastro do produto no WinThor.\"")],
        "\"Fonte: WinThor, rotina 322 (venda por produto). \" & FORMAT ( _nV, \"#,0\", \"pt-BR\" ) & \" dos \" & "
        "FORMAT ( _nC, \"#,0\", \"pt-BR\" ) & \" fornecedores cadastrados venderam em \" & _mes & \".\"", 300)
    L += ["VAR _verso =", "    " + verso, "-- 4 · Marcação", "VAR _html =",
          "    \"<div class='vp kc\" & _clsAnim & \"' tabindex='0' role='group' aria-label='\" & _altAttr & \"'>\"",
          "        & \"<div class='kc__gira'>\"",
          "            & \"<section class='kc__face kc__frente'>\" & _frHtml & \"</section>\"",
          "            & \"<section class='kc__face kc__verso' aria-hidden='true'>\" & _verso & \"</section>\"",
          "        & \"</div>\"", "    & \"</div>\"", "RETURN",
          "    \"<style>\" & [Comum · CSS base] & [Comum · CSS cartão] & [Comum · CSS contador] & "
          + dax_texto(CSS_CARTAO + CSS_CONC) + " & \"</style>\"",
          "        & _html", "        & IF ( _anim = 1, [Comum · JS contador] )"]
    html = D.cabecalho("T6 Fornecedores e marcas\\Concentração", "Cartão Concentração da venda (T6), frente e verso com "
                       "flip no hover e no foco (Figma 26:3385 e verso da seção 60:3443): parcela dos 10 maiores, barra das "
                       "faixas de fornecedores e a chave dos 10 maiores. Só lê contas; larguras são geometria.",
                       gerado="pbi/scripts/gerar_cartoes.py") + "\n".join(L) + "\n"
    A = ["-- 1 · Leituras", "VAR _p10 = [T6 · Concentração · parcela dos 10 maiores (%)]",
         "VAR _nV = [T6 · Concentração · fornecedores com venda]", "VAR _mes = [Período · mês (curto)]", "-- 2 · Textos"]
    A += D.pct("_p10", "_a1", marca=False)
    A += ["RETURN", '    "Concentração da venda em " & _mes & ": os 10 maiores fornecedores fazem " & _a1Txt & " da venda; " '
          '& FORMAT ( _nV, "#,0", "pt-BR" ) & " fornecedores venderam no mês."']
    alt = D.cabecalho("T6 Fornecedores e marcas\\Concentração", "Texto alternativo do cartão Concentração da venda.",
                      gerado="pbi/scripts/gerar_cartoes.py") + "\n".join(A) + "\n"
    return {str(pasta / "T6 · Concentração · HTML.dax"): html, str(pasta / "T6 · Concentração · ALT.dax"): alt}


# ----------------------------------------------------------------------------------------------- T5 · Estoque a custo
CSS_EST = (
    ".ec__l{position:absolute;left:20px;right:20px;height:31px;border-top:1px solid #ECEEF2}"
    ".ec__l p{position:absolute;top:5.5px;font-size:14px;line-height:20px;white-space:nowrap}"
    ".ec__r{left:0;color:#474E5E}.ec__v{right:0;color:#474E5E}.ec__v b{font-weight:600;color:#1E2433}"
)


def t5_estoque() -> dict[str, str]:
    pasta = DAX / "T5" / "EstoqueCusto"
    leituras = [
        ("_val", "Estoque · valor a custo (R$)"), ("_dias", "Estoque · dias da rede"),
        ("_com", "Estoque · itens com estoque"), ("_tot", "Estoque · itens × loja"),
        ("_sv", "Estoque · sobre a venda do mês (%)"), ("_pIt", "Estoque · pendente · itens × loja"),
        ("_pQt", "Estoque · pendente · quantidade"), ("_pVl", "Estoque · pendente · valor a custo (R$)"),
        ("_corte", "Estoque · data do corte"), ("_lojas", "Recorte · lojas (texto)"),
        ("_janela", "T5 · Estoque a custo · janela do custo médio"), ("_mc", "T5 · Estoque a custo · mês do corte (curto)"),
        ("_anim", "Exibição · animação ligada"), ("_alt", "T5 · Estoque a custo · ALT"),
    ]
    L = ["-- 1 · Leituras"] + [f"VAR {v} = [{m}]" for v, m in leituras] + ["-- 2 · Textos"]
    L += D.compacto("_val", "_hv")
    L.append('VAR _hvTxt = IF ( ISBLANK ( _val ), "—", "⁅" & _hvS & "R$ ¦" & _hvN & "¦" & _hvU & "⁆" )')
    L.append('VAR _diasTxt = IF ( ISBLANK ( _dias ), "—", "⁅¦" & FORMAT ( _dias, "0.0", "pt-BR" ) & "¦ dias⁆" )')
    L += D.inteiro("_com", "_c1") + D.inteiro("_tot", "_c2", marca=False) + D.pct("_sv", "_s1")
    L += D.inteiro("_pIt", "_p1") + D.num("_pQt", "_p2", marca=False) + D.brl("_pVl", "_p3", marca=False)
    L.append('VAR _corteTxt = FORMAT ( _corte, "dd/mm/yyyy", "pt-BR" )')
    L.append('VAR _clsAnim = IF ( _anim = 1, "", " sem-anim" )')
    L.append("VAR _altAttr = " + D.esc("_alt"))

    def linha(i, rot_, val):
        return (f"\"<div class='ec__l' style='top:{156 + 31 * i}px'><p class='ec__r'>{rot_}</p><p class='ec__v'>\" & {val}"
                f" & \"</p></div>\"")

    L.append("VAR _frente =")
    partes = [
        "\"<p class='fr fr--tit'>Estoque a custo</p>\"",
        "\"<p class='fr fr--sub'>posição de \" & _corteTxt & \" · \" & _lojas & \" · itens contados por loja</p>\"",
        "\"<p class='fr fr--rot' style='top:78px'>Valor a custo</p>\"",
        "\"<p class='fr fr--hero' style='top:94px'>\" & _hvTxt & \"</p>\"",
        linha(0, "Dias de estoque da rede", "\"<b>\" & _diasTxt & \"</b>\""),
        linha(1, "Itens com estoque", "\"<b>\" & _c1Txt & \"</b> de \" & _c2Txt"),
        linha(2, "Estoque ÷ venda do mês", "\"<b>\" & _s1Txt & \"</b>\""),
        linha(3, "Pedido de compra pendente", "\"<b>\" & _p1Txt & \" itens</b> · \" & _p2Txt & \" un. · \" & _p3Txt"),
    ]
    L.append("    " + "\n        & ".join(partes))
    L += ["/* @contador:tabela */", "/* @contador:fim */", "/* @contador:prosa nome=_fr texto=_frente */",
          "/* @contador:fim */"]
    verso = verso_dax("Estoque a custo", [
        ("Valor a custo", "\"Estoque físico × último custo líquido, em \" & _corteTxt & \".\""),
        ("Dias de estoque", "\"Estoque a custo ÷ custo líquido médio por dia de \" & _janela & \".\""),
        ("Itens com estoque", "\"Itens × loja com estoque físico acima de zero.\""),
        ("Estoque ÷ venda", "\"Estoque a custo ÷ venda de \" & _mc & \".\""),
        ("Pedido pendente", "\"Pedidos de compra em aberto, valorizados a custo.\"")],
        "\"Fonte: WinThor, rotina 286 (posição de estoque). Cada item é contado uma vez por loja.\"", 300)
    L += ["VAR _verso =", "    " + verso, "-- 4 · Marcação", "VAR _html =",
          "    \"<div class='vp kc\" & _clsAnim & \"' tabindex='0' role='group' aria-label='\" & _altAttr & \"'>\"",
          "        & \"<div class='kc__gira'>\"",
          "            & \"<section class='kc__face kc__frente'>\" & _frHtml & \"</section>\"",
          "            & \"<section class='kc__face kc__verso' aria-hidden='true'>\" & _verso & \"</section>\"",
          "        & \"</div>\"", "    & \"</div>\"", "RETURN",
          "    \"<style>\" & [Comum · CSS base] & [Comum · CSS cartão] & [Comum · CSS contador] & "
          + dax_texto(CSS_CARTAO + CSS_EST) + " & \"</style>\"",
          "        & _html", "        & IF ( _anim = 1, [Comum · JS contador] )"]
    html = D.cabecalho("T5 Estoque\\Estoque a custo", "Cartão Estoque a custo (T5), frente e verso com flip no hover e no "
                       "foco (Figma 26:3926 e verso 83:3565): valor a custo, dias de estoque da rede, itens com estoque, "
                       "estoque sobre a venda e pedido pendente. Só lê contas.",
                       gerado="pbi/scripts/gerar_cartoes.py") + "\n".join(L) + "\n"
    A = ["-- 1 · Leituras", "VAR _val = [Estoque · valor a custo (R$)]", "VAR _dias = [Estoque · dias da rede]",
         "VAR _corte = [Estoque · data do corte]", "-- 2 · Textos"] + D.brl("_val", "_a1", marca=False)
    A += ["RETURN", '    "Estoque a custo em " & FORMAT ( _corte, "dd/mm/yyyy", "pt-BR" ) & ": " & _a1Txt & ", " '
          '& FORMAT ( _dias, "0.0", "pt-BR" ) & " dias de estoque."']
    alt = D.cabecalho("T5 Estoque\\Estoque a custo", "Texto alternativo do cartão Estoque a custo.",
                      gerado="pbi/scripts/gerar_cartoes.py") + "\n".join(A) + "\n"
    return {str(pasta / "T5 · Estoque a custo · HTML.dax"): html, str(pasta / "T5 · Estoque a custo · ALT.dax"): alt}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    arqs = {}
    arqs.update(t1_resultado())
    arqs.update(t6_concentracao())
    arqs.update(t5_estoque())
    for caminho, txt in arqs.items():
        p = Path(caminho)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(txt, encoding="utf-8")
        print("gravado", p.relative_to(RAIZ))
    return 0


if __name__ == "__main__":
    sys.exit(main())

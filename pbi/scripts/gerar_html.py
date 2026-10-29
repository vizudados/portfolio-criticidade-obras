#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gerar_html — medidas de DESENHO (HTML Content) dos painéis que não são
cartão de KPI nem Deneb: listas, composições e tabelas. Só lêem contas.

Geometria do Figma Ymu8hISEG66DR3lg8YS6QS no espaço do visual (coordenada do Figma no cartão menos a origem do visual).
Depois de gerar: contador.py --aplicar e lint_conta_desenho.py.

    python -X utf8 pbi/scripts/gerar_html.py
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import desenho_lib as D  # noqa: E402

RAIZ = AQUI.parent
DAX = RAIZ / "dax"
GERADO = "pbi/scripts/gerar_html.py"


def q(s: str) -> str:
    """Literal DAX de texto."""
    return '"' + s.replace('"', '""') + '"'


def medida(pasta: str, descricao: str, leituras: list[tuple[str, str]], textos: list[str], geometria: list[str],
           frente: list[str], css: str, raiz_cls: str, alt: str, contador: bool = True) -> str:
    """Monta a medida nos quatro blocos. `frente` = partes DAX concatenadas do HTML com números marcados ⁅¦¦⁆."""
    L = ["-- 1 · Leituras"] + [f"VAR {v} = [{m}]" for v, m in leituras]
    L += ["VAR _anim = [Exibição · animação ligada]", f"VAR _alt = [{alt}]", "-- 2 · Textos"] + textos
    L += ['VAR _clsAnim = IF ( _anim = 1, "", " sem-anim" )', "VAR _altAttr = " + D.esc("_alt")]
    if geometria:
        L += ["-- 3 · Geometria"] + geometria
    L += ["VAR _corpo =", "    " + "\n        & ".join(frente)]
    if contador:
        L += ["/* @contador:tabela */", "/* @contador:fim */", "/* @contador:prosa nome=_cp texto=_corpo */",
              "/* @contador:fim */"]
    corpo = "_cpHtml" if contador else "_corpo"
    L += ["-- 4 · Marcação", "VAR _html =",
          f"    \"<div class='vp {raiz_cls}\" & _clsAnim & \"' role='group' aria-label='\" & _altAttr & \"'>\" & {corpo} & \"</div>\"",
          "RETURN",
          "    \"<style>\" & [Comum · CSS base] & [Comum · CSS contador] & " + q(css) + " & \"</style>\"",
          "        & _html"]
    if contador:
        L.append("        & IF ( _anim = 1, [Comum · JS contador] )")
    return D.cabecalho(pasta, descricao, gerado=GERADO) + "\n".join(L) + "\n"


# ============================================================================== T1 · Variação da venda (Figma 24:3070)
CSS_VAR = (
    ".vr{position:fixed;inset:0;font-size:14px;line-height:20px}"
    ".vr p{position:absolute;white-space:nowrap}"
    ".vr .r{right:0;text-align:right}"
    ".vr__rot{font-size:13px;line-height:18px;color:#474E5E}.vr__rot.sb{color:#1E2433}"
    ".vr__tr{position:absolute;left:56px;width:300px;height:14px;border-radius:4px;background:#F0F2F5;overflow:hidden}"
    ".vr__br{position:absolute;left:0;top:0;bottom:0;border-radius:4px;transform-origin:left center;"
    "animation:vrCresce .7s cubic-bezier(.2,.7,.2,1) both}"
    ".vr__vl{color:#474E5E}.vr__vl.sb{color:#1E2433}"
    ".vr__lv{font-size:19.5px;line-height:26px;color:#6B7280}"
    ".vr__vv{font-size:26.4px;line-height:34px;font-weight:600;color:#1E2433}"
    ".vr__vp{font-size:15px;line-height:22px;color:#474E5E}"
    ".vr__dv{position:absolute;left:0;right:0;height:1px;background:#ECEEF2}"
    ".vr__cp{font-size:13px;line-height:18px;font-weight:600;color:#6B7280}"
    ".vr__st{position:absolute;left:0;right:0;height:24px;display:flex;gap:2px}"
    ".vr__sg{height:24px;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600;"
    "color:#FFFFFF;overflow:hidden;transform-origin:left center;animation:vrCresce .6s cubic-bezier(.2,.7,.2,1) both}"
    ".vr__sg:first-child{border-radius:4px 0 0 4px}.vr__sg:last-child{border-radius:0 4px 4px 0}"
    ".vr__sg.cl{color:#1E2433}"
    ".vr__mk{position:absolute;left:0;width:10px;height:10px;border-radius:3px}"
    ".vr__nm{left:18px;font-weight:600;color:#1E2433}"
    ".vr__ds{left:18px;font-size:12px;line-height:16px;color:#6B7280}"
    ".vr__vf{font-weight:600;color:#1E2433}"
    ".vr__nt{left:0;font-size:12px;line-height:16px;color:#6B7280}"
    ".up{color:#1F4094}.dn{color:#FE1A21}.eq{color:#6B7280}"
    "@keyframes vrCresce{from{transform:scaleX(0)}}"
)


def t1_variacao() -> dict[str, str]:
    pasta = "T1 Visão geral\\Variação"
    leituras = [
        ("_v1", "Venda (R$)"), ("_v0", "Venda · ano anterior (R$)"), ("_var", "T1 · Variação · variação (R$)"),
        ("_varPct", "Venda · variação sobre o ano anterior (%)"),
        ("_ePre", "T1 · Variação · efeito preço (R$)"), ("_eVol", "T1 · Variação · efeito volume (R$)"),
        ("_eMix", "T1 · Variação · efeito mix (R$)"),
        ("_pPre", "T1 · Variação · parcela do preço"), ("_pVol", "T1 · Variação · parcela do volume"),
        ("_pMix", "T1 · Variação · parcela do mix"),
        ("_novos", "T1 · Variação · itens novos"), ("_semVenda", "T1 · Variação · itens sem venda no mês"),
        ("_mes", "Período · mês (curto)"), ("_aa", "Período · ano anterior (curto)"),
    ]
    textos = []
    textos += D.brl("_v0", "_t0") + D.brl("_v1", "_t1") + D.brl("_var", "_tv", mais=True)
    textos += D.variacao("_varPct", "_tp")
    textos += D.brl("_ePre", "_tpr", mais=True) + D.brl("_eVol", "_tvo", mais=True) + D.brl("_eMix", "_tmx", mais=True)
    textos += D.inteiro("_novos", "_tn", marca=False) + D.inteiro("_semVenda", "_ts", marca=False)
    for p, v in (("_lp", "_pPre"), ("_lv", "_pVol"), ("_lm", "_pMix")):
        textos.append(f'VAR {p} = FORMAT ( {v} * 100, "0", "pt-BR" ) & "%"')
    textos.append('VAR _nota = _tnTxt & " itens novos e " & _tsTxt & " itens sem venda em " & _mes & " entram no mix."')
    geometria = [
        "VAR _maxV = MAX ( _v0, _v1 ) -- geometria",
        "VAR _p10 = POWER ( 10, INT ( LOG10 ( MAX ( 1, _maxV / 9 ) ) ) ) -- geometria",
        "VAR _mm = DIVIDE ( _maxV / 9, _p10 ) -- geometria",
        "VAR _passo = _p10 * SWITCH ( TRUE (), _mm <= 1, 1, _mm <= 2, 2, _mm <= 2.5, 2.5, _mm <= 5, 5, 10 ) -- geometria",
        "VAR _escala = MAX ( 1, CEILING ( _maxV / _passo, 1 ) * _passo ) -- geometria",
        "VAR _w0 = ROUND ( DIVIDE ( _v0, _escala ) * 300, 1 ) -- geometria",
        "VAR _w1 = ROUND ( DIVIDE ( _v1, _escala ) * 300, 1 ) -- geometria",
        "VAR _sPre = ROUND ( _pPre * 100, 3 ) -- geometria",
        "VAR _sVol = ROUND ( _pVol * 100, 3 ) -- geometria",
        "VAR _sMix = ROUND ( _pMix * 100, 3 ) -- geometria",
    ]

    def seg(cor, flex, rot, cls="", atraso=0):
        return (f"\"<div class='vr__sg{cls}' style='background:{cor};flex:\" & SUBSTITUTE ( FORMAT ( {flex}, \"0.000\" ), \",\", \".\" )"
                f" & \" 1 0;animation-delay:{atraso}ms'>\" & IF ( {flex} >= 9, {rot} ) & \"</div>\"")

    def linha(y, cor, nome, desc, val, div=True):
        partes = [f"\"<i class='vr__mk' style='top:{y + 5}px;background:{cor}'></i>"
                  f"<p class='vr__nm' style='top:{y}px'>{nome}</p>\"",
                  f"\"<p class='vr__ds' style='top:{y + 22}px'>\" & {desc} & \"</p>\"",
                  f"\"<p class='vr__vf r' style='top:{y}px'>\" & {val} & \"</p>\""]
        if div:
            partes.append(f"\"<i class='vr__dv' style='top:{y + 44}px'></i>\"")
        return partes

    frente = [
        "\"<p class='vr__rot' style='left:0;top:14px'>\" & _aa & \"</p>\"",
        "\"<div class='vr__tr' style='top:16px'><i class='vr__br' style='width:\" & SUBSTITUTE ( FORMAT ( _w0, \"0.0\" ), \",\", \".\" ) & \"px;background:#B0BCD9'></i></div>\"",
        "\"<p class='vr__vl r' style='top:13px'>\" & _t0Txt & \"</p>\"",
        "\"<p class='vr__rot sb' style='left:0;top:48px'>\" & _mes & \"</p>\"",
        "\"<div class='vr__tr' style='top:50px'><i class='vr__br' style='width:\" & SUBSTITUTE ( FORMAT ( _w1, \"0.0\" ), \",\", \".\" ) & \"px;background:#1F4094;animation-delay:90ms'></i></div>\"",
        "\"<p class='vr__vl sb r' style='top:47px'>\" & _t1Txt & \"</p>\"",
        "\"<p class='vr__lv' style='left:0;top:90px'>Variação</p>\"",
        "\"<p class='vr__vv' style='left:0;top:123px'>\" & _tvTxt & \"</p>\"",
        "\"<p class='vr__vp r' style='right:5px;top:133px'>\" & _tpTxt & \" sobre \" & _aa & \"</p>\"",
        "\"<i class='vr__dv' style='top:160px'></i>\"",
        "\"<p class='vr__cp' style='left:0;top:176px'>Composição da variação</p>\"",
        "\"<div class='vr__st' style='top:202px'>\"",
        seg("#1F4094", "_sPre", "_lp", atraso=150),
        seg("#6279B4", "_sVol", "_lv", atraso=230),
        seg("#B0BCD9", "_sMix", "_lm", cls=" cl", atraso=310),
        "\"</div>\"",
    ]
    frente += linha(248, "#1F4094", "Preço", q("variação do preço de cada item"), "_tprTxt")
    frente += linha(304, "#6279B4", "Volume", "\"variação da quantidade, ao preço médio de \" & _aa", "_tvoTxt")
    frente += linha(360, "#B0BCD9", "Mix", q("troca de participação entre itens"), "_tmxTxt", div=False)
    frente.append("\"<p class='vr__nt' style='top:420px'>\" & _nota & \"</p>\"")

    html = medida(pasta, "Cartão Variação da venda (T1, Figma 24:3070): barras do mês e do ano anterior, variação, "
                  "composição preço × volume × mix e a nota dos itens novos. Só lê contas; não calcula.",
                  leituras, textos, geometria, frente, CSS_VAR, "vr", "T1 · Variação · ALT")
    alt_l = ["-- 1 · Leituras", "VAR _var = [T1 · Variação · variação (R$)]", "VAR _pPre = [T1 · Variação · parcela do preço]",
             "VAR _mes = [Período · mês (curto)]", "VAR _aa = [Período · ano anterior (curto)]", "-- 2 · Textos"]
    alt_l += D.brl("_var", "_a1", marca=False, mais=True)
    alt_l += ["RETURN", '    "Variação da venda de " & _aa & " para " & _mes & ": " & _a1Txt & "; o preço explica "'
              ' & FORMAT ( _pPre * 100, "0", "pt-BR" ) & "% da composição."']
    alt = D.cabecalho(pasta, "Texto alternativo do cartão Variação da venda.", gerado=GERADO) + "\n".join(alt_l) + "\n"
    base = DAX / "T1" / "Variacao"
    return {str(base / "T1 · Variação · HTML.dax"): html, str(base / "T1 · Variação · ALT.dax"): alt}


# ======================================================================== T4 · Da venda à lucratividade (Figma 8:376)
# Visual sobre o "Conteúdo · Cascata" (320,198 720×332): destaque da margem, variações, legenda e a cascata em tabela
# (Etapa · barra flutuante · Valor · % da venda). Barras: trilho 403 px em x128; venda inteira; ICMS, PIS, COFINS e
# custo líquido descem da ponta direita, um depois do outro; a lucratividade é o que sobra à esquerda.
CSS_CASCATA = (
    ".cs{position:fixed;inset:0;font-size:14px;line-height:20px;color:#474E5E}"
    ".cs p{position:absolute;white-space:nowrap}"
    ".cs .r{text-align:right}"
    ".cs__lb{left:0;top:0;font-size:13px;line-height:18px;font-weight:600;color:#6B7280}"
    ".cs__mg{left:0;top:16px;font-size:44px;line-height:52px;font-weight:600;color:#1E2433;letter-spacing:-.2px}"
    ".cs__vr{left:0;top:72px}"
    ".cs__lg{top:0;font-size:13px;line-height:18px}"
    ".cs__mk{position:absolute;top:4px;width:10px;height:10px;border-radius:2px}"
    ".cs__cb{position:absolute;left:0;top:100px;width:720px;height:26px;border-radius:6px;background:#F0F2F5}"
    ".cs__ch{top:104px;font-size:13px;line-height:18px;font-weight:600;color:#6B7280}"
    ".cs__et{left:12px}.cs__et.sb{color:#1E2433}"
    ".cs__tr{position:absolute;left:128px;width:403px;height:14px;border-radius:4px;background:#F0F2F5}"
    ".cs__br{position:absolute;top:0;height:14px;border-radius:4px;"
    "animation:csCresce .7s cubic-bezier(.2,.7,.2,1) both}"
    ".cs__br.dir{transform-origin:right center}.cs__br.esq{transform-origin:left center}"
    ".cs__vl{right:105px}"
    ".cs__pc{right:12px;font-weight:600;color:#1E2433}"
    ".cs__dv{position:absolute;left:0;width:720px;height:1px;background:#ECEEF2}"
    ".cs__nt{left:0;top:312px;font-size:12px;line-height:16px;color:#6B7280}"
    ".up{color:#1F4094}.dn{color:#FE1A21}.eq{color:#6B7280}"
    "@keyframes csCresce{from{transform:scaleX(0)}}"
)


def t4_cascata() -> dict[str, str]:
    pasta = "T4 Margem e preço\\Cascata"
    etapas = [  # (chave, rótulo, conta R$, conta % da venda, dedução?)
        ("ve", "Venda", "Venda (R$)", "T4 · Cascata · venda (% da venda)", False),
        ("ic", "ICMS", "ICMS (R$)", "T4 · Cascata · ICMS (% da venda)", True),
        ("pi", "PIS", "PIS (R$)", "T4 · Cascata · PIS (% da venda)", True),
        ("co", "COFINS", "COFINS (R$)", "T4 · Cascata · COFINS (% da venda)", True),
        ("cl", "Custo líquido", "Custo líquido (R$)", "T4 · Cascata · custo líquido (% da venda)", True),
        ("lu", "Lucratividade", "Lucratividade (R$)", "Margem (%)", False),
    ]
    leituras = [("_mg", "Margem (%)"), ("_dAA", "Margem · diferença sobre o ano anterior"),
                ("_dMA", "Margem · diferença sobre o mês anterior"), ("_aa", "Período · ano anterior (curto)"),
                ("_ma", "Período · mês anterior (curto)"), ("_cb", "Custo bruto (R$)"),
                ("_cbP", "T4 · Cascata · custo bruto (% da venda)")]
    for k, _r, rs, pc, _d in etapas:
        leituras += [(f"_{k}", rs), (f"_{k}P", pc)]
    textos = D.pct("_mg", "_tmg") + D.variacao("_dAA", "_va") + D.variacao("_dMA", "_vm")
    for k, _r, _rs, _pc, ded in etapas:
        textos += D.brl(f"_{k}", f"_t{k}")
        textos += D.pct(f"_{k}P", f"_p{k}")
        if ded:
            textos.append(f'VAR _p{k}Sn = IF ( _{k}P > 0, "{D.MENOS}", "" ) & _p{k}Txt')
        else:
            textos.append(f"VAR _p{k}Sn = _p{k}Txt")
    textos += D.brl("_cb", "_tcb", marca=False) + D.pct("_cbP", "_pcb", marca=False)
    textos.append('VAR _nota = "Lucratividade = venda − ICMS − PIS − COFINS − custo líquido · custo bruto: " & _pcbTxt'
                  ' & " da venda (" & _tcbTxt & ")"')
    # geometria: cada dedução desce da ponta direita a partir do fim da anterior (posições acumuladas, em px de 403)
    geometria = [
        "VAR _W = 403 -- geometria",
        "VAR _xIc = _W * ( 1 - _icP ) -- geometria",
        "VAR _xPi = _xIc - _W * _piP -- geometria",
        "VAR _xCo = _xPi - _W * _coP -- geometria",
        "VAR _xCl = _xCo - _W * _clP -- geometria",
        "VAR _wLu = MAX ( 0, _W * _luP ) -- geometria",
    ]

    def px(v: str) -> str:
        return f'SUBSTITUTE ( FORMAT ( {v}, "0.0" ), ",", "." )'

    def barra(y, cor, x, w, lado, atraso):
        return (f"\"<i class='cs__br {lado}' style='left:\" & {px(x)} & \"px;width:\" & {px(w)} & \"px;"
                f"background:{cor};animation-delay:{atraso}ms'></i>\"")

    frente = [
        "\"<p class='cs__lb'>Margem</p>\"",
        "\"<p class='cs__mg tn'>\" & _tmgTxt & \"</p>\"",
        "\"<p class='cs__vr'>\" & _vaTxt & \" sobre \" & _aa & \"&#8195;&#8194;\" & _vmTxt & \" sobre \" & _ma & \"</p>\"",
        "\"<i class='cs__mk' style='left:403px;background:#1F4094'></i><p class='cs__lg' style='left:419px'>Venda e lucratividade</p>\"",
        "\"<i class='cs__mk' style='left:562px;background:#FE1A21'></i><p class='cs__lg' style='left:578px'>Impostos e custo líquido</p>\"",
        "\"<i class='cs__cb'></i>\"",
        "\"<p class='cs__ch' style='left:12px'>Etapa</p><p class='cs__ch r' style='right:105px'>Valor</p>"
        "<p class='cs__ch r' style='right:12px'>% da venda</p>\"",
    ]
    # x e largura de cada barra (as deduções ficam 1 px afastadas da vizinha da esquerda)
    geo = {"ve": ("0", "_W", "esq"), "ic": ("_xIc + 1", "MAX ( 2, _W * _icP - 1 )", "dir"),
           "pi": ("_xPi + 1", "MAX ( 2, _W * _piP - 1 )", "dir"), "co": ("_xCo + 1", "MAX ( 2, _W * _coP - 1 )", "dir"),
           "cl": ("_xCl + 1", "MAX ( 2, _W * _clP - 1 )", "dir"), "lu": ("0", "_wLu", "esq")}
    for i, (k, rot_, _rs, _pc, ded) in enumerate(etapas):
        y = 131 + 30 * i
        cor = "#FE1A21" if ded else "#1F4094"
        x, w, lado = geo[k]
        cls = "" if ded else " sb"
        frente += [
            f"\"<p class='cs__et{cls}' style='top:{y}px'>{rot_}</p>\"",
            f"\"<div class='cs__tr' style='top:{y + 3}px'>\"",
            barra(y, cor, x, w, lado, 120 + 90 * i),
            "\"</div>\"",
            f"\"<p class='cs__vl r tn' style='top:{y}px'>\" & _t{k}Txt & \"</p>\"",
            f"\"<p class='cs__pc r tn' style='top:{y}px'>\" & _p{k}Sn & \"</p>\"",
        ]
        if i < len(etapas) - 1:
            frente.append(f"\"<i class='cs__dv' style='top:{y + 25}px'></i>\"")
    frente.append("\"<p class='cs__nt'>\" & _nota & \"</p>\"")
    html = medida(pasta, "Cartão Da venda à lucratividade (T4, Figma 8:376): margem em destaque, diferenças sobre o "
                  "ano anterior e o mês anterior (em %), legenda e a cascata da venda até a lucratividade com barras "
                  "flutuantes, valor e % da venda. Só lê contas; as posições acumuladas das barras são geometria.",
                  leituras, textos, geometria, frente, CSS_CASCATA, "cs", "T4 · Cascata · ALT")
    alt_l = ["-- 1 · Leituras", "VAR _mg = [Margem (%)]", "VAR _imp = [T4 · Cascata · impostos (% da venda)]",
             "VAR _cl = [T4 · Cascata · custo líquido (% da venda)]", "VAR _mes = [Período · mês (curto)]",
             "-- 2 · Textos"]
    alt_l += D.pct("_mg", "_a1", marca=False) + D.pct("_imp", "_a2", marca=False) + D.pct("_cl", "_a3", marca=False)
    alt_l += ["RETURN", '    "Da venda à lucratividade em " & _mes & ": margem de " & _a1Txt & "; os impostos levam "'
              ' & _a2Txt & " da venda e o custo líquido, " & _a3Txt & "."']
    alt = D.cabecalho(pasta, "Texto alternativo do cartão Da venda à lucratividade.", gerado=GERADO) + "\n".join(alt_l) + "\n"
    base = DAX / "T4" / "Cascata"
    return {str(base / "T4 · Cascata · HTML.dax"): html, str(base / "T4 · Cascata · ALT.dax"): alt}


# ================================================================================ T2 · Venda por cidade (Figma 8:136)
# Visual sobre o bloco "Venda por cidade" (320,796 660×236): título, nota, barra 100% das cidades e um cartão por cidade
# (cor pela ordem de venda: #1F4094, #6279B4, #B0BCD9).
CSS_CIDADES = (
    ".cd{position:fixed;inset:0;font-size:12px;line-height:16px;color:#474E5E}"
    ".cd-ti{position:absolute;left:0;top:0;font-size:13px;line-height:18px;font-weight:600}"
    ".cd-nt{position:absolute;right:0;top:1px;color:#6B7280}"
    ".cd-br{position:absolute;left:0;right:0;top:26px;height:22px;display:flex;gap:3px}"
    ".cd-br i{display:flex;align-items:center;justify-content:center;font-style:normal;font-size:13px;font-weight:600;"
    "color:#FFFFFF;overflow:hidden;white-space:nowrap;transform-origin:left;animation:cdC .6s cubic-bezier(.2,.7,.2,1) both}"
    ".cd-br i.cl{color:#1E2433}"
    ".cd-cs{position:absolute;left:0;right:0;top:64px;display:flex;gap:16px}"
    ".cd-c{flex:0 0 209.3px;height:168px;border-radius:12px;background:#F0F2F5;padding:14px 16px 0;position:relative}"
    ".cd-h{display:flex;align-items:center;gap:6px;height:20px}"
    ".cd-h i{flex:none;width:10px;height:10px;border-radius:3px}"
    ".cd-h b{font-size:14px;line-height:20px;font-weight:600;color:#1E2433;flex:1 1 auto;white-space:nowrap;overflow:hidden;"
    "text-overflow:ellipsis}"
    ".cd-h span{flex:none;color:#6B7280}"
    ".cd-v{margin-top:8px;font-size:22px;line-height:28px;font-weight:600;color:#1E2433;white-space:nowrap}"
    ".cd-d{margin-top:2px;white-space:nowrap}"
    ".cd-dv{height:1px;background:#DFE2E8;margin:10px 0 9px}"
    ".cd-b{max-height:32px;overflow:hidden}"
    ".up{color:#1F4094}.dn{color:#FE1A21}.eq{color:#6B7280}"
    "@keyframes cdC{from{transform:scaleX(0)}}"
)


def t2_cidades() -> dict[str, str]:
    pasta = "T2 Lojas e bairros\\Localização"
    leituras = [("_mes", "Período · mês (curto)"), ("_aa", "Período · ano anterior (curto)")]
    cores = "SWITCH ( {r}, 1, \"#1F4094\", 2, \"#6279B4\", \"#B0BCD9\" )"
    textos = [
        "VAR _cids =\n    ADDCOLUMNS (\n        VALUES ( dLoja[Cidade] ),\n"
        "        \"@p\", [T2 · Localização · participação na venda da rede (%)],\n        \"@v\", [Venda (R$)],\n"
        "        \"@x\", [Venda · variação sobre o ano anterior (%)],\n        \"@n\", [T2 · Localização · lojas com venda],\n"
        "        \"@b\", [T2 · Localização · bairros das lojas]\n    )",
        "VAR _ok = FILTER ( _cids, [@v] > 0 ) -- lista",
        "VAR _rk = ADDCOLUMNS ( _ok, \"@r\", RANKX ( _ok, [@v], , DESC, DENSE ) ) -- lista",
        "VAR _barra =\n    CONCATENATEX (\n        _rk,\n"
        "        VAR _w = SUBSTITUTE ( FORMAT ( MAX ( 0.5, [@p] * 100 ), \"0.000\" ), \",\", \".\" ) -- geometria\n"
        "        RETURN\n            \"<i class='\" & IF ( [@r] >= 3, \"cl\" ) & \"' style='flex:\" & _w & \" 1 0;background:\" & "
        + cores.format(r="[@r]") + " & \";animation-delay:\" & [@r] * 80 & \"ms'>\" & IF ( [@p] >= 0.08, "
        "FORMAT ( [@p] * 100, \"0.0\", \"pt-BR\" ) & \"%\" ) & \"</i>\",\n        \"\",\n        [@r], ASC\n    )",
        "VAR _cartoes =\n    CONCATENATEX (\n        _rk,\n"
        "        VAR _a = ABS ( [@v] )\n"
        "        VAR _esc = SWITCH ( TRUE (), _a >= 999950, 1000000, _a >= 9999.5, 1000, 1 )\n"
        "        VAR _vTxt = \"⁅R$ ¦\" & FORMAT ( _a / _esc, SWITCH ( _esc, 1000000, \"0.0\", 1000, \"0\", \"#,0\" ), \"pt-BR\" )"
        " & \"¦\" & SWITCH ( _esc, 1000000, \" mi\", 1000, \" mil\", \"\" ) & \"⁆\"\n"
        "        VAR _xr = ROUND ( [@x] * 100, 1 )\n"
        "        VAR _seta = SWITCH ( TRUE (), _xr > 0, \"<span class='up'>▲</span>\", _xr < 0, \"<span class='dn'>▼</span>\", "
        "\"<span class='eq'>■</span>\" )\n"
        "        VAR _xTxt = SWITCH ( TRUE (), _xr > 0, \"+\", _xr < 0, \"" + D.MENOS + "\", \"\" ) & FORMAT ( ABS ( [@x] ) * 100, "
        "\"0.0\", \"pt-BR\" ) & \"%\"\n"
        "        RETURN\n"
        "            \"<div class='cd-c'><div class='cd-h'><i style='background:\" & " + cores.format(r="[@r]")
        + " & \"'></i><b>\" & " + D.esc("dLoja[Cidade]") + " & \"</b><span>\" & [@n] & IF ( [@n] = 1, \" loja\", \" lojas\" )"
        " & \"</span></div>\"\n"
        "                & \"<p class='cd-v'>\" & _vTxt & \"</p>\"\n"
        "                & \"<p class='cd-d'>\" & IF ( ISBLANK ( [@x] ), \"sem \" & _aa & \" na base\", _seta & \" \" & _xTxt & \" sobre \" & _aa )"
        " & \"</p><div class='cd-dv'></div><p class='cd-b'>\" & " + D.esc("[@b]") + " & \"</p></div>\",\n"
        "        \"\",\n        [@r], ASC\n    )",
    ]
    frente = [
        "\"<p class='cd-ti'>Venda por cidade</p>\"",
        "\"<p class='cd-nt'>\" & _mes & \" · participação na venda da rede</p>\"",
        "\"<div class='cd-br'>\" & _barra & \"</div>\"",
        "\"<div class='cd-cs'>\" & _cartoes & \"</div>\"",
    ]
    html = medida(pasta, "Bloco Venda por cidade (T2, Figma 8:136): barra 100% da participação de cada cidade na venda da "
                  "rede e um cartão por cidade com venda, variação sobre o ano anterior e os bairros das lojas. Só lê "
                  "contas; a ordem e a cor vêm da própria lista (venda).", leituras, textos, [], frente, CSS_CIDADES, "cd",
                  "T2 · Cidades · ALT")
    alt_l = ["-- 1 · Leituras", "VAR _mes = [Período · mês (curto)]", "VAR _n = COUNTROWS ( VALUES ( dLoja[Cidade] ) ) -- lista",
             "RETURN", '    "Venda por cidade em " & _mes & ": participação de cada cidade na venda da rede e venda das lojas."']
    alt = D.cabecalho(pasta, "Texto alternativo do bloco Venda por cidade.", gerado=GERADO) + "\n".join(
        [l for l in alt_l if "_n =" not in l]) + "\n"
    base = DAX / "T2" / "Localizacao"
    return {str(base / "T2 · Cidades · HTML.dax"): html, str(base / "T2 · Cidades · ALT.dax"): alt}


# ============================================================================== T5 · Classe A sem estoque (Figma 8:496)
# Visual 1440,518 424×518: cabeçalho, 10 pares item × loja (maior média de venda por dia primeiro) e nota no pé.
CSS_CLASSEA = (
    ".ca{position:fixed;inset:0;font-size:14px;line-height:20px;color:#474E5E}"
    ".ca p{position:absolute;white-space:nowrap}"
    ".ca-cb{position:absolute;left:0;right:0;top:0;height:26px;border-radius:6px;background:#F0F2F5}"
    ".ca-ch{top:4px;font-size:13px;line-height:18px;font-weight:600;color:#6B7280}"
    ".ca-r{transform:translateX(-100%)}"
    ".ca-ls{position:absolute;left:0;right:0;top:26px}"
    ".ca-l{position:relative;height:47px;animation:caE .35s ease-out both}"
    ".ca-l+.ca-l{border-top:1px solid #ECEEF2}"
    ".ca-it{left:10px;top:4px;color:#1E2433;max-width:270px;overflow:hidden;text-overflow:ellipsis}"
    ".ca-sb{left:10px;top:24px;font-size:12px;line-height:16px;color:#6B7280;max-width:270px;overflow:hidden;"
    "text-overflow:ellipsis}"
    ".ca-md{left:334px;top:4px;font-weight:600;color:#1E2433}.ca-pe{left:414px;top:4px}"
    ".ca-nt{left:0;top:502px;font-size:12px;line-height:16px;color:#6B7280}"
    "@keyframes caE{from{opacity:0;transform:translateY(4px)}}"
)


def t5_classe_a() -> dict[str, str]:
    pasta = "T5 Estoque\\Classe A sem estoque"
    leituras = [("_n", "T5 · Classe A sem estoque · itens × loja")]
    textos = [
        "VAR _itensTodos = ADDCOLUMNS ( VALUES ( dProduto[Codigo] ), \"@n\", [T5 · Classe A sem estoque · itens × loja] )",
        "VAR _itens = FILTER ( _itensTodos, [@n] > 0 ) -- lista",
        "VAR _paresTodos =\n    GENERATE (\n        _itens,\n"
        "        ADDCOLUMNS ( VALUES ( dLoja[Loja] ), \"@n2\", [T5 · Classe A sem estoque · itens × loja] )\n    )",
        "VAR _pares = FILTER ( _paresTodos, [@n2] > 0 ) -- lista",
        "VAR _lista =\n    ADDCOLUMNS (\n        _pares,\n        \"@m\", [T5 · Classe A sem estoque · média de venda por dia],\n"
        "        \"@p\", [T5 · Classe A sem estoque · pendente],\n        \"@i\", [T5 · Classe A sem estoque · item],\n"
        "        \"@d\", [T5 · Classe A sem estoque · departamento do item]\n    )",
        "VAR _top = TOPN ( 10, _lista, [@m], DESC, [@i], ASC, dLoja[Loja], ASC )",
        "VAR _mostra = COUNTROWS ( _top ) -- lista",
        "VAR _linhas =\n    CONCATENATEX (\n        _top,\n"
        "        \"<div class='ca-l'>"
        "<p class='ca-it'>\" & " + D.esc("[@i]") + " & \"</p><p class='ca-sb'>\" & " + D.esc("[@d] & \" · \" & dLoja[Loja]")
        + " & \"</p><p class='ca-md ca-r tn'>\" & FORMAT ( [@m], \"#,0.0\", \"pt-BR\" ) & \"</p><p class='ca-pe ca-r tn'>\" & "
        "IF ( ISBLANK ( [@p] ) || [@p] = 0, \"—\", FORMAT ( [@p], \"#,0\", \"pt-BR\" ) ) & \"</p></div>\",\n"
        "        \"\",\n        [@m], DESC,\n        [@i], ASC\n    )",
        "VAR _nota = IF ( _n > 0, \"Mostrando \" & _mostra & \" de \" & FORMAT ( _n, \"#,0\", \"pt-BR\" ) & \" · ordem: média de "
        "venda/dia · qtd. em un. ou kg\", \"Nenhum item de classe A sem estoque no recorte.\" )",
    ]
    frente = [
        "\"<i class='ca-cb'></i><p class='ca-ch' style='left:10px'>Item</p><p class='ca-ch ca-r' style='left:334px'>"
        "Média/dia</p><p class='ca-ch ca-r' style='left:414px'>Pendente</p>\"",
        "\"<div class='ca-ls'>\" & _linhas & \"</div>\"",
        "\"<p class='ca-nt'>\" & _nota & \"</p>\"",
    ]
    html = medida(pasta, "Lista Classe A sem estoque (T5, Figma 27:3406): os 10 pares item × loja de maior média de venda "
                  "por dia, com departamento, loja e pedido pendente; nota com o total. Só lê contas; a lista e a ordem "
                  "são do desenho.", leituras, textos, [], frente, CSS_CLASSEA, "ca", "T5 · Classe A sem estoque · ALT",
                  contador=False)
    alt_l = ["-- 1 · Leituras", "VAR _n = [T5 · Classe A sem estoque · itens × loja]", "RETURN",
             '    "Itens de classe A sem estoque disponível: " & FORMAT ( _n, "#,0", "pt-BR" ) & " itens × loja."']
    alt = D.cabecalho(pasta, "Texto alternativo da lista Classe A sem estoque.", gerado=GERADO) + "\n".join(alt_l) + "\n"
    sub_l = ["-- 1 · Leituras", "VAR _n = [T5 · Classe A sem estoque · itens]",
             "VAR _lMax = [T5 · Classe A sem estoque · lojas por item (máximo)]",
             "VAR _lMin = [T5 · Classe A sem estoque · lojas por item (mínimo)]", "-- 2 · Textos",
             'VAR _lojas = SWITCH ( TRUE (), _n = 0, "", _lMax = 1, IF ( _n = 1, "em 1 loja", "cada um em 1 loja" ), '
             '_lMin = _lMax, "cada um em " & _lMax & " lojas", "em " & _lMin & " a " & _lMax & " lojas cada" )',
             'VAR _txt = FORMAT ( _n, "#,0", "pt-BR" ) & IF ( _n = 1, " item", " itens" ) & " com disponível zero" & '
             'IF ( _lojas <> "", " · " & _lojas )',
             "-- 4 · Marcação", "RETURN",
             "    \"<style>\" & [Comum · CSS base] & [Comum · CSS subtítulo] & \"</style>\"",
             "        & \"<p class='vp st'>\" & _txt & \"</p>\""]
    sub = D.cabecalho(pasta, "Subtítulo do cartão Classe A sem estoque: itens com disponível zero e em quantas lojas cada um. "
                      "Só lê contas.", gerado=GERADO) + "\n".join(sub_l) + "\n"
    base = DAX / "T5" / "ClasseA"
    return {str(base / "T5 · Classe A sem estoque · HTML.dax"): html,
            str(base / "T5 · Classe A sem estoque · ALT.dax"): alt,
            str(base / "T5 · Classe A sem estoque · HTML subtítulo.dax"): sub}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    arqs = {}
    arqs.update(t1_variacao())
    arqs.update(t4_cascata())
    arqs.update(t2_cidades())
    arqs.update(t5_classe_a())
    for caminho, txt in arqs.items():
        p = Path(caminho)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(txt, encoding="utf-8")
        print("gravado", p.relative_to(RAIZ))
    return 0


if __name__ == "__main__":
    sys.exit(main())

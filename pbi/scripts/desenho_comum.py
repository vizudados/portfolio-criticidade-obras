#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""desenho_comum — medidas de DESENHO compartilhadas pelas telas (pbi/dax/comum/**): CSS base (Barlow embutida em
subconjunto, marcas de status, chips, selos, hachura), CSS do cartão com flip, cabeçalho "em uso", bloco "Mês de
referência" da sidebar e selo de origem do rodapé. Só leem contas (base/**).

Estilos lidos do Figma FjBWDk5odF9HaZ2pwhGosl (Tela 01 281:720; linguagem em docs/06-interacoes-spec.md §1).

    python -X utf8 pbi/scripts/desenho_comum.py
"""
from __future__ import annotations

import base64
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import contador as C  # noqa: E402
import corrida as K  # noqa: E402
import desenho_projeto as D  # noqa: E402
from contas_lib_projeto import Medida, gravar  # noqa: E402

RAIZ = AQUI.parent
GERADO = "pbi/scripts/desenho_comum.py"
PASTA = r"Comum\Desenho"
MEDIDAS: list[Medida] = []

# Retiradas do modelo em 08/10/2026 (auditoria: dependencias-pos-telas.json e dependencias-final.json, chave mortas).
# Nenhum visual alcança estas contas e nenhum script de QA as lê (o conferir_contas.py, que lia as 16 'Criticidade ·
# … · ref' e o rótulo, saiu do projeto nesta data). Fora da gravação: o gerador não escreve o nome e apaga o .dax que
# tinha escrito antes. Para reativar, tire o nome do conjunto.
RETIRADAS = {
    "Drawer · HTML obras",
}


# ---------------------------------------------------------------------------------------------------------- tokens
PRETO, GRAFITE, CREME, OFF, BRANCO = "#0B0B0C", "#3B3B3F", "#E9E0CF", "#F7F4EE", "#FFFFFF"
# redesenho v2 (Figma 372:685, coleção "Construtora · Painel v2"; cores aprovadas pelo Alisson em 07/10/2026): status por
# cor e peso — crítico vermelho sólido > atenção ocre sólido > estável sálvia clara > PENDENTE tracejado — e negativo
# em vermelho (sobre preto e sobre creme, tons próprios). Fase 2 da régua antiga (13/10/2026): o tracejado, que era a
# mobilização, passa a ser a obra PENDENTE na nota (falta item; sem nota nem status). Classes .mkm e .chipm iguais.
VERM, VERM_CLARO = "#C43737", "#F7E3E3"
OCRE = "#C9821F"
SALVIA, SALVIA_CLARO, SALVIA_TXT, SALVIA_BORDA = "#A9CDB9", "#E1EFE7", "#1E5C43", "#6E9F85"
NEG, NEG_PRETO, NEG_CREME = VERM, "#F2877C", "#A82C2C"
REGRA, TRILHA, TERC = "#E1E1E1", "#EFEFEF", "#6B6B70"
# hachura 45° (de baixo-esquerda para cima-direita), traço 1 px a cada 4 px — o mesmo vetor do Figma. Na v2 a hachura
# deixou de ser status: marca só a série "sem estoque e adiantamentos" (preta; vermelha quando negativa)
HACH = ("url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%224%22 height=%224%22%3E"
        "%3Cpath d=%22M-1 1L1 -1M0 4L4 0M3 5L5 3%22 stroke=%22%230B0B0C%22 stroke-width=%221%22/%3E%3C/svg%3E')")
HACH_CREME = HACH.replace("%230B0B0C", "%23E9E0CF")
HACH_NEG = HACH.replace("%230B0B0C", "%23C43737")


def dax_lit(s: str) -> str:
    """Literal DAX quebrado em pedaços de até ~180 caracteres (o lint prefere linhas curtas)."""
    s = s.replace('"', '""')
    partes = [s[i:i + 180] for i in range(0, len(s), 180)] or [""]
    return "\n    & ".join(f'"{p}"' for p in partes)


def css_fontes() -> str:
    regras = []
    for peso in (500, 600):
        b64 = base64.b64encode((RAIZ / "assets" / "fontes" / f"barlow-{peso}.woff").read_bytes()).decode("ascii")
        regras.append("@font-face{font-family:'Barlow U';font-style:normal;font-weight:%d;"
                      "src:url(data:font/woff;base64,%s) format('woff')}" % (peso, b64))
    return "".join(regras)


CSS_BASE = (
    "*{box-sizing:border-box;margin:0;padding:0}"
    "html,body{background:transparent!important;overflow:hidden}"
    "#htmlContent{margin:0!important;padding:0!important}"
    # geometria em px vem do DAX como inteiro (o modelo é pt-BR: decimal sairia com vírgula e o CSS ignoraria)
    ".os-scrollbar-horizontal{display:none!important}"
    # v2: todo painel é de tamanho fixo e desenhado para caber (L037/L065, sem rolagem). Na foto do canvas (07/10/2026)
    # os gráficos de colunas da T2 e da T4 ganhavam barra vertical por poucos px de rótulo; a barra sai como a horizontal
    ".os-scrollbar-vertical{display:none!important}"
    f".u{{font-family:'Segoe UI',system-ui,-apple-system,sans-serif;color:{PRETO};-webkit-font-smoothing:antialiased;"
    "text-rendering:optimizeLegibility}"
    ".u .b5{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:500}"
    ".u .b6{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600}"
    ".u .sb{font-weight:600}.u .tn{font-variant-numeric:tabular-nums}"
    ".u .ab{position:absolute;white-space:nowrap}"
    # versalete v2: Barlow SemiBold 12 (piso geral), 10% de espaçamento, grafite cheio (o claro "doía a vista")
    ".u .vs{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:12px;line-height:15px;"
    f"letter-spacing:1.2px;text-transform:uppercase;color:{GRAFITE}}}"
    # marcas de status 11 px (Figma Marca · v2 373:734): crítico vermelho · atenção ocre · estável sálvia com borda ·
    # pendente (nota) tracejado grafite (.mkm, a antiga mobilização)
    ".u .mk{display:inline-block;width:11px;height:11px;flex:none}"
    f".u .mk2{{background:{VERM}}}"
    f".u .mk1{{background:{OCRE}}}"
    f".u .mk0{{background:{SALVIA};box-shadow:inset 0 0 0 1px {SALVIA_BORDA}}}"
    f".u .mkm{{border:1px dashed {GRAFITE}}}"
    # série "sem estoque e adiantamentos" (Figma Hachura · v2 373:752): preta quando ≥ 0, vermelha quando < 0
    f".u .hach{{background:{HACH};box-shadow:inset 0 0 0 1px {PRETO}}}"
    f".u .hach.ng,.u .hach-ng{{background:{HACH_NEG};box-shadow:inset 0 0 0 1px {VERM}}}"
    # negativo em vermelho: número, sinal e rótulo (sobre preto e sobre creme, tons próprios)
    f".u .ng{{color:{NEG}!important}}"
    f".u .escuro .ng,.u.escuro .ng,.u .sobre-preto .ng{{color:{NEG_PRETO}!important}}"
    f".u .sobre-creme .ng,.u .verso .ng{{color:{NEG_CREME}!important}}"
    # chips de status (Figma Chip · v2 373:747): altura 25, Barlow SemiBold 13, 8% de espaçamento; o peso cai com a
    # gravidade (crítico sólido vermelho > atenção sólido ocre > estável sálvia clara > pendente tracejado, .chipm)
    ".u .chip{display:inline-flex;align-items:center;gap:7px;height:25px;padding:0 10px 0 9px;border-radius:4px;"
    "font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:13px;letter-spacing:1.04px;"
    "text-transform:uppercase;white-space:nowrap}"
    ".u .chip i{display:block;width:9px;height:9px;flex:none}"
    f".u .chip2{{background:{VERM};color:{BRANCO}}}.u .chip2 i{{background:{BRANCO}}}"
    f".u .chip1{{background:{OCRE};color:{PRETO}}}.u .chip1 i{{background:{PRETO}}}"
    f".u .chip0{{background:{SALVIA_CLARO};color:{SALVIA_TXT}}}"
    f".u .chip0 i{{background:{SALVIA};box-shadow:inset 0 0 0 1px {SALVIA_BORDA}}}"
    f".u .chipm{{background:{BRANCO};color:{PRETO};border:1px dashed {GRAFITE}}}"
    f".u .chipm i{{border:1px dashed {GRAFITE}}}"
    # chip de pendência (Figma Chip · v2 Status=Pendência 398:8718): campo exigido e não preenchido ("Em branco ·
    # exigida"); contorno tracejado vermelho, texto vermelho, marca vazada — não é status de obra
    ".u .chp{display:inline-flex;align-items:center;gap:7px;height:25px;padding:0 10px 0 9px;border-radius:4px;"
    f"background:{BRANCO};border:1px dashed {VERM};color:{VERM};font-family:'Barlow U','Segoe UI',sans-serif;"
    "font-weight:600;font-size:13px;letter-spacing:1.04px;text-transform:uppercase;white-space:nowrap}"
    f".u .chp i{{display:block;width:9px;height:9px;flex:none;box-shadow:inset 0 0 0 1.25px {VERM}}}"
    # chip de item da nota ("4,25 de 4,5", "falta na base"): cheio (sálvia), parcial (ocre claro), zero (vermelho claro),
    # falta (tracejado grafite) e neutro (item que não conta). Altura 22, Barlow SemiBold 13, números tabulares
    ".u .chi{display:inline-flex;align-items:center;height:22px;padding:0 8px;border-radius:4px;"
    "font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:13px;line-height:16px;"
    "font-variant-numeric:tabular-nums;white-space:nowrap}"
    f".u .chi-c{{background:{SALVIA_CLARO};color:{SALVIA_TXT}}}"
    f".u .chi-p{{background:#F6E8D2;color:{PRETO};box-shadow:inset 0 0 0 1px {OCRE}}}"
    f".u .chi-z{{background:{VERM_CLARO};color:{NEG_CREME}}}"
    f".u .chi-f{{background:{BRANCO};color:{GRAFITE};border:1px dashed {GRAFITE}}}"
    f".u .chi-n{{background:{BRANCO};color:{TERC};box-shadow:inset 0 0 0 1px {REGRA}}}"
    # selos de origem do dado
    ".u .selo{display:inline-block;padding:1px 5px;border-radius:3px;font-family:'Barlow U','Segoe UI',sans-serif;"
    "font-weight:600;font-size:12px;line-height:14px;letter-spacing:1.2px;white-space:nowrap}"
    ".u .selo-i{border:1px dashed rgba(59,59,63,.5);color:rgba(59,59,63,.8)}"
    f".u .selo-r{{background:{GRAFITE};color:{BRANCO}}}"
    # obra real não leva selo (dObra[Selo] vazio): o span vazio some, sem caixa tracejada
    ".selo:empty{display:none!important}"
    # F4 (pedido do Alisson, 28/10/2026: "todo elemento de gráfico animado"): entradas genéricas para o que a corrida
    # (barras, colunas, path[data-rl]) não cobre. O estado final é o estilo base e o keyframe só tem 'from' (sem
    # animação, com movimento reduzido ou num navegador sem a propriedade 'scale', aparece o valor certo); a cascata vem
    # do style inline (animation-delay). .a-pop: pontos, marcas e pílulas entram crescendo do centro; .a-fd: grade, eixo
    # e rótulos de apoio aparecem; .a-gx: faixas e réguas crescem da esquerda; .a-gy: crescem de baixo.
    "@keyframes cbPop{from{opacity:0;scale:.4}}@keyframes cbFd{from{opacity:0}}"
    "@keyframes cbGx{from{scale:0 1}}@keyframes cbGy{from{scale:1 0}}"
    ".u .a-pop{transform-box:fill-box;transform-origin:center;animation:cbPop .4s cubic-bezier(.2,.7,.2,1) backwards}"
    ".u .a-fd{animation:cbFd .45s ease-out backwards}"
    ".u .a-gx{transform-box:fill-box;transform-origin:left center;animation:cbGx .7s cubic-bezier(.2,.7,.2,1) backwards}"
    ".u .a-gy{transform-box:fill-box;transform-origin:center bottom;animation:cbGy .7s cubic-bezier(.2,.7,.2,1) backwards}"
    "@media (prefers-reduced-motion:reduce){.u *{transition:none!important;animation:none!important}}"
)

# cartão com flip: frente e verso no mesmo visual (coluna inteira do cartão, L057); hover ou foco
CSS_CARTAO = (
    ".kc{position:fixed;inset:0;overflow:hidden;outline:none;cursor:default}"
    ".kc .lado{position:absolute;inset:0;transition:transform .22s cubic-bezier(.3,.7,.3,1)}"
    f".kc .verso{{background:{CREME};transform:translateY(100%)}}"
    ".kc:hover .frente,.kc:focus .frente,.kc:focus-within .frente{transform:translateY(-100%)}"
    ".kc:hover .verso,.kc:focus .verso,.kc:focus-within .verso{transform:translateY(0)}"
    # frente v2 (Figma Cartão · v2 377:726, 302 × 140): rótulo Barlow SemiBold 15 em caixa normal (sai o versalete),
    # número 42/50, lado 17/21 pela linha de base, contexto Segoe 14/19 numa linha; margem 20, área útil 262
    f".kc .eb{{left:20px;top:18px;font-size:15px;line-height:18px;letter-spacing:.03px;text-transform:none;"
    f"color:{GRAFITE}}}"
    ".kc .linha1{position:absolute;left:20px;top:40px;display:flex;align-items:baseline;gap:6px;white-space:nowrap}"
    # marca de status no início da linha de contexto (T2, T3: "■ −0,90% · crítico · faixa < 0")
    ".kc .ctx .mk{margin-right:6px}"
    ".kc .hero{font-size:42px;line-height:50px}"
    f".kc .lado2{{font-size:17px;line-height:21px;color:{GRAFITE}}}"
    f".kc .ctx{{position:absolute;left:20px;top:102px;width:262px;font-size:14px;line-height:19px;color:{GRAFITE};"
    "white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
    # só a frente é escura; o verso é creme e mantém as cores de texto padrão
    f".kc.escuro .frente .vs{{color:{CREME}}}.kc.escuro .frente .hero{{color:#FFFFFF}}"
    f".kc.escuro .frente .lado2{{color:{CREME}}}.kc.escuro .frente .ctx{{color:rgba(233,224,207,.85)}}"
    # verso v2 (geometria comum às quatro telas, Figma 07/10/2026): "COMO É CALCULADO" em y 16; regra Segoe 14/19 de
    # y 36; com régua, "DE ONDE VEM" em y 82 e régua em y 106; sem régua, "DE ONDE VEM" em y 106 (o y da linha de
    # origem vem do gerador da tela, top inline). Limites da régua são neutros (grafite), nunca .ng
    ".kc .verso .v1{left:20px;top:16px}"
    ".kc .verso .regra{position:absolute;left:20px;top:36px;width:262px;font-size:14px;line-height:19px;"
    "color:#0B0B0C;white-space:normal}"
    ".kc .verso .ond{position:absolute;left:20px;display:flex;align-items:baseline;gap:0;white-space:nowrap}"
    ".kc .verso .ond .vs{width:93px;flex:none}"
    ".kc .verso .ond span+span{font-size:14px;line-height:19px;color:#0B0B0C}"
    ".kc .verso .regua{position:absolute;left:20px;top:106px;display:flex;align-items:center;gap:6px;"
    f"font-size:14px;line-height:19px;white-space:nowrap;color:{GRAFITE}}}"
    ".kc .verso .regua .mk{margin-left:8px}.kc .verso .regua .mk:first-child{margin-left:0}"
)


# ---------------------------------------------------------------------------------------------------------- helpers da nota
# Trechos DAX de DESENHO para o status e os pontos da nota (Fase 2). As telas usam estes no lugar dos seus helpers de
# criticidade/mobilização; recebem EXPRESSÕES que já leem contas (ex.: "[Nota · status · ranking · ref]" ou uma VAR "_st") e só
# escolhem classe, palavra e formato. Contrato: artefato plano-nota-painel/fase-2-telas/contrato-camada-comum.
FALTA_NA_BASE = "falta na base"          # item da base complementar sem dado
SEM_DADO_AC = "sem dado na planilha"     # item da Análise Crítica sem dado (ex.: físico-financeiro sem previsto)
FMT_PTS = "0.0#"                         # 7,25 · 5,4 · 6,0 · 10,5


def cls_status(st: str, pend: str) -> str:
    """Sufixo da classe de status: "2" crítico · "1" atenção · "0" estável · "m" pendente · "" sem obra no contexto.
    Use em 'mk mk' & … e 'chip chip' & …. BLANK nunca vira estável (BLANK = 0 é verdadeiro em DAX)."""
    return f'IF ( {pend} = 1, "m", IF ( ISBLANK ( {st} ), "", {st} & "" ) )'


def marca_status(st: str, pend: str) -> str:
    """<i class='mk mk2'></i> … <i class='mk mkm'></i> (pendente, tracejado); vazio sem obra."""
    c = cls_status(st, pend)
    return f'IF ( {c} = "", "", "<i class=\'mk mk" & {c} & "\'></i>" )'


def falta_curto(base: str, plan: str, fora: str | None = None) -> str:
    """DAX do que falta, curto, para linha e cartão: 'faltam 5 itens na base', 'falta 1 item na planilha' ou 'faltam 6 ·
    1 da planilha' (auditoria da Fase 2, minor 4: o que falta na planilha não é falta na base; cabe nos 262 px
    da linha do cartão). Com `fora` ([Nota · itens fora da faixa], já contados em `base`), o valor fora da faixa sai da
    falta (auditoria da Fase 3, minor 1): só fora, '1 item fora da faixa'; falta e fora juntos, curto para caber,
    'faltam 3 · 1 fora' (rodada 2: 'falta 1 item na base · 1 fora da faixa' cortava)."""
    b = base if fora is None else f"( {base} - {fora} )"
    falta = (f'SWITCH ( TRUE (), {b} > 0 && {plan} > 0, "faltam " & ( {b} + {plan} ) & " · " & {plan} & '
             f'" da planilha", {b} > 0, IF ( {b} = 1, "falta 1 item na base", "faltam " & {b} & '
             f'" itens na base" ), {plan} > 0, IF ( {plan} = 1, "falta 1 item na planilha", "faltam " & {plan} & '
             f'" itens na planilha" ), "" )')
    if fora is None:
        return falta
    return (f'SWITCH ( TRUE (), {fora} > 0 && {b} + {plan} > 0, IF ( {b} + {plan} = 1, "falta 1", "faltam " & ( {b} + '
            f'{plan} ) ) & " · " & {fora} & " fora", {fora} > 0, IF ( {fora} = 1, "1 item fora da faixa", {fora} & '
            f'" itens fora da faixa" ), {falta} )')


def onde_falta(v: str = "_onde") -> list[str]:
    """VARs de onde falta item na carteira (T1, síntese e leitura de obras), pelas obras de cada fonte (auditoria da Fase
    3, minor 8): 'na base complementar', 'na planilha', 'na base complementar e na planilha' (as mesmas obras) ou 'na
    base complementar (na JANGADA, também na planilha)'. Também dá `{v}Fora` ('; na DUNAS, há valor fora da faixa',
    ou '; em 2 obras, …') e `{v}SoFora` (nada falta, só há valor fora da faixa), para a frase não chamar de falta o
    valor fora da faixa (auditoria da Fase 3, rodada 2, m3).

    Casos de borda: sem nenhuma falta, {v} = "na base complementar" (a frase usa {v}SoFora ou nem chega a citar);
    duas ou mais obras na planilha e a base também faltando, '(na planilha, em N obras)', sem dizer se é 'também' ou
    'só' (cada obra pode ser uma coisa)."""
    return [
        'VAR _ofB = [T1 · Obras · com item faltando na base (lista) · ref] & ""',
        'VAR _ofP = [T1 · Obras · com item faltando na planilha (lista) · ref] & ""',
        'VAR _ofF = [T1 · Obras · com item fora da faixa (lista) · ref] & ""',
        'VAR _ofNB = IF ( _ofB = "", 0, PATHLENGTH ( _ofB ) )',
        'VAR _ofNP = IF ( _ofP = "", 0, PATHLENGTH ( _ofP ) )',
        'VAR _ofNF = IF ( _ofF = "", 0, PATHLENGTH ( _ofF ) )',
        'VAR _ofP1 = PATHITEM ( _ofP, 1 ) & ""',
        'VAR _ofF1 = PATHITEM ( _ofF, 1 ) & ""',
        f'VAR {v} =',
        '    SWITCH (',
        '        TRUE (),',
        '        _ofNB > 0 && _ofNP > 0 && _ofB = _ofP, "na base complementar e na planilha",',
        '        _ofNB > 0 && _ofNP = 1, "na base complementar (na " & _ofP1',
        '            & IF ( PATHCONTAINS ( _ofB, _ofP1 ), ", também na planilha)", ", só na planilha)" ),',
        '        _ofNB > 0 && _ofNP > 1, "na base complementar (na planilha, em " & _ofNP & " obras)",',
        '        _ofNP > 0, "na planilha",',
        '        "na base complementar"',
        '    )',
        f'VAR {v}Fora = SWITCH ( TRUE (), _ofNF = 0, "", _ofNF = 1, "; na " & _ofF1 & ", há valor fora da faixa", '
        '"; em " & _ofNF & " obras, há valor fora da faixa" )',
        f'VAR {v}SoFora = _ofNB + _ofNP = 0 && _ofNF > 0',
    ]


def palavra_status(st: str, pend: str) -> str:
    """"crítico" · "atenção" · "estável" · "pendente" (minúsculas); vazio sem obra."""
    return (f'SWITCH ( TRUE (), {pend} = 1, "pendente", ISBLANK ( {st} ), "", {st} = 2, "crítico", '
            f'{st} = 1, "atenção", "estável" )')


def chip_status(st: str, pend: str) -> str:
    """Chip v2 do status (o CSS põe em caixa alta): <span class='chip chip2'><i></i>crítico</span>; vazio sem obra."""
    c = cls_status(st, pend)
    return (f'IF ( {c} = "", "", "<span class=\'chip chip" & {c} & "\'><i></i>" & {palavra_status(st, pend)} '
            f'& "</span>" )')


def pontos(v: str, p: str, vazio: str = "—") -> list[str]:
    """{p}Txt = "7,25" · "5,4" · "6,0" (pontos da nota, vírgula, até 2 casas)."""
    return [f'VAR {p}Txt = IF ( ISBLANK ( {v} ), "{vazio}", FORMAT ( {v}, "{FMT_PTS}", "pt-BR" ) )']


def nota_txt(p: str, nota: str, obtidos: str, possiveis: str, pend: str, prefixo: str = "nota ") -> list[str]:
    """{p}Txt = "nota 7,25" (completa) · "pendente · 4,5 de 6,0" (falta item) · "—" (sem obra). Também {p}N (só a
    nota), {p}Ob e {p}Po. Para "crítico · 5,4": palavra_status(...) & " · " & {p}N."""
    return [
        f'VAR {p}N = FORMAT ( {nota}, "{FMT_PTS}", "pt-BR" )',
        f'VAR {p}Ob = FORMAT ( {obtidos}, "{FMT_PTS}", "pt-BR" )',
        f'VAR {p}Po = FORMAT ( {possiveis}, "{FMT_PTS}", "pt-BR" )',
        f'VAR {p}Txt = SWITCH ( TRUE (), {pend} = 1, "pendente · " & {p}Ob & " de " & {p}Po, '
        f'ISBLANK ( {nota} ), "—", "{prefixo}" & {p}N )',
    ]


def item_txt(p: str, pts: str, poss: str, fonte: str = "base") -> list[str]:
    """{p}Txt = "4,25 de 4,5" · "falta na base" (fonte="base") · "sem dado na planilha" (fonte="ac")."""
    falta = FALTA_NA_BASE if fonte == "base" else SEM_DADO_AC
    return [f'VAR {p}Txt = IF ( ISBLANK ( {pts} ), "{falta}", FORMAT ( {pts}, "{FMT_PTS}", "pt-BR" ) & " de " '
            f'& FORMAT ( {poss}, "{FMT_PTS}", "pt-BR" ) )']


def chip_item(p: str, pts: str, poss: str, fonte: str = "base", bonus: bool = False) -> list[str]:
    """Linhas DAX até {p}Html = <span class='chi chi-c'>4,5 de 4,5</span> (cheio) · chi-p (parcial) · chi-z (zero) ·
    chi-f (falta, com o texto de item_txt) · chi-n (item que não conta: nunca vermelho)."""
    zero = '"n"' if bonus else '"z"'
    return item_txt(p, pts, poss, fonte) + [
        f'VAR {p}Cls = SWITCH ( TRUE (), ISBLANK ( {pts} ), "f", {pts} >= {poss}, "c", {pts} = 0, {zero}, "p" )',
        f'VAR {p}Html = "<span class=\'chi chi-" & {p}Cls & "\'>" & {p}Txt & "</span>"',
    ]


def m(nome, descricao, dax, pasta=PASTA, formato="texto"):
    MEDIDAS.append(Medida(nome, pasta, formato, descricao, dax))


m("Comum · CSS fontes",
  "Barlow Medium e SemiBold (subconjunto latino, WOFF em base64) para números e títulos nos HTML Content; a Segoe UI "
  "segue no texto corrido. Licença OFL (mockup/fonts/OFL-Barlow.txt).",
  "-- 4 · Marcação\n" + dax_lit(css_fontes()))
m("Comum · CSS base",
  "CSS base de todo HTML Content: fontes, cores da Construtora, marcas de status v2 (crítico vermelho · atenção ocre · "
  "estável sálvia · pendente tracejado), negativo em vermelho (.ng), hachura da série sem estoque, chips de status e "
  "de item da nota (.chi) e selos. "
  "Altura por position:fixed, nunca height:100% (L037).",
  "-- 4 · Marcação\n[Comum · CSS fontes]\n    & " + dax_lit(CSS_BASE + C.css_texto()))
m("Comum · JS contador",
  "Contador dos números (odômetro de contador.py): memória do texto final por número; o que não mudou desde a "
  "atualização anterior não reconta. Só compara textos que o DAX já formatou; nunca calcula número.",
  "-- 4 · Marcação\n" + dax_lit(C.js_texto()))
m("Comum · JS contador tooltip",
  "Contador dos números nos tooltips de página: cada aparição nova do balão conta de novo; passando de um ponto a outro "
  "em menos de 1,5 s, não.",
  "-- 4 · Marcação\n" + dax_lit(C.js_texto(tooltip=True)))
m("Comum · JS corrida",
  "Corrida das barras, colunas e linhas (corrida.py): na primeira aparição crescem do zero em cascata; quando o filtro "
  "muda, saem do valor anterior e as linhas que trocam de lugar deslizam. Só anima a geometria que o DAX escreveu.",
  "-- 4 · Marcação\n" + dax_lit(K.js_texto()))
m("Comum · CSS cartão",
  "CSS dos cartões de KPI com flip (frente e verso no mesmo visual; hover ou foco desliza a frente para cima e o verso "
  "creme entra por baixo, docs/06-interacoes-spec.md §1.5).",
  "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(CSS_CARTAO))

# ---------------------------------------------------------------------------------------------------------- cabeçalho
CSS_CAB = (".cab{position:fixed;inset:0;display:flex;justify-content:flex-end;align-items:center;gap:28px;"
           "white-space:nowrap}"
           ".cab div{display:flex;align-items:center;gap:8px}"
           # v2: rótulo versalete 12 grafite, valor Barlow SemiBold 19/24 (Figma Casca v2 · modelo 377:10485)
           ".cab .r{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:12px;letter-spacing:1.2px;"
           "color:#3B3B3F}"
           ".cab .v{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:19px;line-height:24px;"
           "color:#0B0B0C}"
           # nome de obra longo: reticências, nunca corte seco na borda da caixa de 500 px (auditoria da Fase 3, nit;
           # 180 px ≈ 20 caracteres, e OBRA + selo + MÊS "setembro de 2026" ainda cabem)
           ".cab .v.nm{display:inline-block;max-width:180px;overflow:hidden;text-overflow:ellipsis;vertical-align:bottom}")
m("Cabeçalho · CSS", "CSS do recorte em uso no cabeçalho.", "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(CSS_CAB))
m("Cabeçalho · HTML recorte carteira",
  "Recorte em uso nas telas da carteira (Visão geral, Resultado no tempo): MÊS + OBRAS. Só informa; os seletores "
  "ficam no drawer.",
  """-- 1 · Leituras
VAR _mes = [Mês de referência · longo]
VAR _n = [Recorte · obras no recorte]
VAR _total = [Recorte · obras no total]
VAR _lista = [Recorte · obras (lista)]
-- 2 · Textos
VAR _txtObras =
    SWITCH (
        TRUE (),
        ISBLANK ( _n ), "nenhuma",
        _n = _total, "Todas (" & _total & ")",
        _n <= 2, _lista,
        _n & " de " & _total
    )
-- 4 · Marcação
RETURN
    "<div class='u cab'>"
        & "<div><span class='r'>MÊS</span><span class='v'>" & _mes & "</span></div>"
        & "<div><span class='r'>OBRAS</span><span class='v nm'>" & """ + D.esc("_txtObras") + """ & "</span></div>"
    & "</div>\"""".replace('\\"', '"'))
m("Cabeçalho · HTML recorte obra",
  "Recorte em uso nas telas de uma obra (Análise crítica, Avanço físico): OBRA (com selo) + MÊS.",
  """-- 1 · Leituras
VAR _obra = [Nota · obra em foco]
VAR _selo = [Obra em foco · selo]
VAR _mes = [Mês de referência · longo]
-- 2 · Textos
VAR _clsSelo = IF ( _selo = "REAL", "selo selo-r", "selo selo-i" )
-- 4 · Marcação
RETURN
    "<div class='u cab'>"
        & "<div><span class='r'>OBRA</span><span class='v nm'>" & """ + D.esc("_obra") + """ & "</span>"
        & "<span class='" & _clsSelo & "'>" & _selo & "</span></div>"
        & "<div><span class='r'>MÊS</span><span class='v'>" & _mes & "</span></div>"
    & "</div>\"""".replace('\\"', '"'))

# ---------------------------------------------------------------------------------------------------------- sidebar
# v2 (Figma Sidebar · v2 376:15025): versalete 12 a 60%, mês Barlow SemiBold 23/28, nota Segoe 14/19 a 70%
CSS_SIDE = (".sd{position:fixed;inset:0}"
            ".sd .r{left:0;top:0;color:rgba(233,224,207,.6)}"
            ".sd .m{left:0;top:18px;font-size:23px;line-height:28px;color:#F7F4EE}"
            ".sd .n{position:absolute;left:0;top:54px;width:232px;font-size:14px;line-height:19px;"
            "color:rgba(233,224,207,.7);white-space:normal}")
m("Sidebar · CSS", "CSS do bloco Mês de referência da sidebar.",
  "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(CSS_SIDE))
m("Sidebar · HTML mês",
  "Bloco 'Mês de referência' da sidebar: o mês do seletor e quantas obras têm planilha no mês (contando, F4).",
  C.envolver_marcas("""-- 1 · Leituras
VAR _mes = [Mês de referência · longo]
VAR _n = [Recorte · obras no total]
-- 2 · Textos
VAR _txtN = IF ( _n = 1, "1 obra em andamento", """ + C.marca("_n") + """ & " obras em andamento" )
-- 4 · Marcação
RETURN
    "<div class='u sd'>"
        & "<p class='ab vs r'>MÊS DE REFERÊNCIA</p>"
        & "<p class='ab b6 m'>" & _mes & "</p>"
        & "<p class='n'>" & _txtN & " · planilhas Análise Crítica · Power Query</p>"
    & "</div>" & [Comum · JS contador]"""))

# ---------------------------------------------------------------------------------------------------------- drawer
# v2 (Figma Tela 01 · v2 · Filtros abertos 387:5503): texto 14/19 a 75%, caixa de obras Barlow SB 15; a contagem por
# status é uma linha informativa com as marcas v2 (não filtra, então não tem cara de botão)
CSS_DRAWER = (".dw{position:fixed;inset:0;font-size:14px;line-height:19px;color:rgba(233,224,207,.75)}"
              ".dw.cx{display:flex;align-items:center;padding-left:14px;font-family:'Barlow U','Segoe UI',sans-serif;"
              "font-weight:600;font-size:15px;color:#F7F4EE}"
              # 4 contagens (Fase 2 da régua antiga): grade 2 × 2 na coluna de 310
              ".dw .st{display:grid;grid-template-columns:1fr 1fr;column-gap:22px;row-gap:6px;margin-top:8px}"
              ".dw .st span{display:inline-flex;align-items:center;gap:8px;font-size:15px;line-height:19px;"
              "color:#F7F4EE;white-space:nowrap}"
              ".dw .st b{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600}"
              ".dw .st .mkm{border-color:#B8B8B8}"
              ".dw .vs{color:rgba(233,224,207,.6)}")
m("Drawer · CSS", "CSS dos textos do drawer de filtros (sobre a sidebar estendida, preta).",
  "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(CSS_DRAWER))
m("Drawer · HTML recorte",
  "Frase do recorte em uso no topo do drawer: mês, quantas obras e, nas telas de uma obra, a obra em foco.",
  """-- 1 · Leituras
VAR _mes = [Mês de referência · longo]
VAR _n = [Recorte · obras no recorte]
VAR _foco = [Nota · obra em foco]
VAR _escolhida = [Recorte · obra em foco escolhida]
-- 2 · Textos
VAR _txtObras = IF ( _n = 1, "1 obra em andamento", _n & " obras em andamento" )
-- 4 · Marcação
RETURN
    "<div class='u dw'>Recorte exibido: " & _mes & ", " & _txtObras & ". Vale para todas as telas.</div>"
""")
m("Drawer · HTML recorte obra",
  "Frase do recorte nas telas de uma obra: mês e obra em foco (escolhida ou a mais crítica).",
  """-- 1 · Leituras
VAR _mes = [Mês de referência · longo]
VAR _foco = [Nota · obra em foco]
VAR _escolhida = [Recorte · obra em foco escolhida]
-- 2 · Textos
VAR _txtFoco = IF ( _escolhida = 1, "obra " & _foco, _foco & ", a obra mais crítica do mês" )  -- critério da nota
-- 4 · Marcação
RETURN
    "<div class='u dw'>Recorte exibido: " & _mes & ", " & """ + D.esc("_txtFoco") + """ & ". O mês vale para todas as telas.</div>"
""")
m("Drawer · HTML janela",
  "Nota sob o seletor de janela (Figma: nota da janela na Tela 01 · Filtros abertos 281:724): de que mês a que mês as "
  "séries vão e quantos meses mostram; quando a janela pede mais meses do que o histórico tem, diz que a série começa "
  "no início do histórico.",
  """-- 1 · Leituras
VAR _ini = [Série · primeiro mês]
VAR _ref = [Mês de referência]
VAR _n = [Série · meses até a referência]
VAR _janela = [Série · janela (meses)]
-- 2 · Textos
VAR _txtIni = FORMAT ( _ini, "mmm/yy", "pt-BR" )
VAR _txtRef = FORMAT ( _ref, "mmm/yy", "pt-BR" )
VAR _txtMeses = IF ( _n = 1, "1 mês", _n & " meses" )
VAR _txtFaixa = IF ( _n = 1, "só " & _txtRef, _txtIni & " a " & _txtRef & " · " & _txtMeses )
VAR _txtCorte = IF ( _n < _janela, ", desde o início do histórico", "" )
-- 4 · Marcação
RETURN
    IF (
        NOT ISBLANK ( _ref ),
        "<div class='u dw'>Mostrando " & _txtFaixa & _txtCorte & ".</div>"
    )
""")
m("Drawer · HTML obras",
  "Texto da caixa do seletor de obras: todas, quantas ou quais.",
  """-- 1 · Leituras
VAR _n = [Recorte · obras no recorte]
VAR _total = [Recorte · obras no total]
VAR _lista = [Recorte · obras (lista)]
-- 2 · Textos
VAR _txt =
    SWITCH (
        TRUE (),
        ISBLANK ( _n ), "Nenhuma obra",
        _n = _total, "Todas as obras (" & _total & ")",
        _n <= 2, _lista,
        _n & " de " & _total & " obras"
    )
-- 4 · Marcação
RETURN
    "<div class='u dw cx'>" & """ + D.esc("_txt") + """ & "</div>"
""")
m("Drawer · HTML foco",
  "Nota sob o seletor de obra em foco: sem escolha, vale a mais crítica do mês.",
  """-- 1 · Leituras
VAR _escolhida = [Recorte · obra em foco escolhida]
VAR _foco = [Nota · obra em foco]
-- 2 · Textos
VAR _txt =
    IF (
        _escolhida = 1,
        "Obra escolhida: " & _foco & ".",
        "Sem escolha, vale a obra mais crítica do mês (a que mais perde pontos na nota): " & _foco & "."
    )
-- 4 · Marcação
RETURN
    "<div class='u dw'>" & """ + D.esc("_txt") + """ & "</div>"
""")
m("Drawer · HTML status",
  "Contagem das obras do recorte por status da nota no mês de referência, com as marcas v2 (informativo: não filtra): "
  "críticas, em atenção, estáveis e pendentes (falta item; tracejado).",
  """-- 1 · Leituras
VAR _mes = [Mês de referência · curto maiúsculo]
VAR _c = [Nota · carteira · obras críticas · ref] + 0
VAR _a = [Nota · carteira · obras em atenção · ref] + 0
VAR _e = [Nota · carteira · obras estáveis · ref] + 0
VAR _p = [Nota · carteira · obras pendentes · ref] + 0
-- 4 · Marcação
RETURN
    "<div class='u dw'><p class='vs'>STATUS NA NOTA EM " & _mes & "</p><div class='st'>"
        & "<span><i class='mk mk2'></i>Crítico <b>" & _c & "</b></span>"
        & "<span><i class='mk mk1'></i>Atenção <b>" & _a & "</b></span>"
        & "<span><i class='mk mk0'></i>Estável <b>" & _e & "</b></span>"
        & "<span><i class='mk mkm'></i>Pendente <b>" & _p & "</b></span>"
    & "</div></div>"
""")
# ---- lista de obras do drawer no VizuFilter 2.10 (papéis itemMarker e itemLabel): a marca e o rótulo do status da obra
# no mês de referência. Devolvem texto, nunca BLANK (linha com todas as medidas em BLANK sai do dataView e a obra some
# da lista — TransLog 2.10.0.0). Gramática da marca: "#RRGGBB" sólido · "#preenchimento|#contorno" · "tracejado|#cor".
m("Drawer · obra · marca",
  "Marca do status da nota da obra no mês de referência, na gramática do VizuFilter 2.10 (crítico vermelho sólido, "
  "atenção ocre sólido, estável sálvia com contorno, pendente tracejado claro); sem obra no mês, sem marca.",
  f"""-- 1 · Leituras
VAR _st = [Nota · status · ranking · ref]
VAR _pend = [Nota · pendente · ranking · ref]
-- 4 · Marcação
RETURN
    SWITCH ( TRUE (),
        _pend = 1, "tracejado|#B8B8B8",
        ISBLANK ( _st ), "",
        _st = 2, "{VERM}",
        _st = 1, "{OCRE}",
        "{SALVIA}|{SALVIA_BORDA}"
    )""")
m("Drawer · obra · rótulo",
  "Rótulo à direita do nome da obra no drawer, pela nota no mês de referência: 'crítico · 5,4' (status e nota) ou "
  "'pendente · 4,0 de 6,0' (pontos obtidos dos possíveis, quando falta item); sem obra no mês, 'sem aba no mês'.",
  "-- 1 · Leituras\n"
  "VAR _st = [Nota · status · ranking · ref]\n"
  "VAR _pend = [Nota · pendente · ranking · ref]\n"
  "VAR _nota = [Nota · nota final · ranking · ref]\n"
  "VAR _obt = [Nota · pontos obtidos · ranking · ref]\n"
  "VAR _poss = [Nota · pontos possíveis · ranking · ref]\n"
  "-- 2 · Textos\n"
  + "\n".join(nota_txt("_n", "_nota", "_obt", "_poss", "_pend", prefixo="")) + "\n"
  f"VAR _txt = IF ( _pend = 1, _nTxt, {palavra_status('_st', '_pend')} & \" · \" & _nN )\n"
  "-- 4 · Marcação\n"
  "RETURN\n"
  "    IF ( ISBLANK ( _pend ), \"sem aba no mês\", _txt )")
m("Drawer · HTML estado",
  "Ao lado do 'Limpar filtros': nenhum filtro ou quantos estão aplicados (mês, obras, obra em foco e a janela, esta só "
  "quando não é a de 12 meses).",
  """-- 1 · Leituras
VAR _mes = [Recorte · mês escolhido]
VAR _obras = [Recorte · obras escolhidas]
VAR _foco = [Recorte · obra em foco escolhida]
VAR _janela = [Recorte · janela escolhida]
-- 2 · Textos
VAR _n = _mes + _obras + _foco + _janela
VAR _txt = IF ( _n = 0, "Nenhum filtro aplicado", IF ( _n = 1, "1 filtro aplicado", _n & " filtros aplicados" ) )
-- 4 · Marcação
RETURN
    "<div class='u dw' style='display:flex;align-items:center'>" & _txt & "</div>"
""")

if __name__ == "__main__":
    sys.exit(gravar([x for x in MEDIDAS if x.nome not in RETIRADAS], RAIZ / "dax" / "comum", GERADO))

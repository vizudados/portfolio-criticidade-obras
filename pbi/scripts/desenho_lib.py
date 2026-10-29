# -*- coding: utf-8 -*-
"""desenho_lib — trechos DAX de DESENHO (formatação, escape, marcação) para os geradores do painel.

Regra do cliente para número (Alisson, 02/10):
  · 1 milhão ou mais ........ "R$ 43,3 mi"  (uma casa)
  · de 10 mil a 1 milhão .... "R$ 321 mil"  (inteiro)
  · abaixo de 10 mil ........ "R$ 1.500"    (inteiro com ponto de milhar; preço unitário mantém os centavos)
  · variação de percentual .. "▼ −0,4%"     (diferença entre os dois percentuais, escrita em %; nunca "p.p.")
Sinal negativo é o "−" (U+2212). Os trechos só formatam valores já lidos de medidas de conta (o desenho não calcula).

Cada função devolve linhas DAX (lista de str, sem recuo) que definem VARs com o prefixo dado. Números que entram no
contador vão marcados ⁅pré¦núcleo¦pós⁆ (formato do contador.py, bloco prosa).
"""
from __future__ import annotations

MENOS = "−"


def esc(expr: str) -> str:
    """Escape de HTML de um texto vindo do modelo (& primeiro)."""
    return ('SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( ' + expr
            + ', "&", "&amp;" ), "<", "&lt;" ), ">", "&gt;" ), "\'", "&#39;" )')


def compacto(v: str, p: str) -> list[str]:
    """VARs {p}Esc, {p}N (núcleo sem sinal), {p}U (unidade com espaço) e {p}S (sinal) para o valor em v.
    Fronteiras: 999.950 já vira "1,0 mi" (e não "1.000 mil"); 9.999,5 já vira "10 mil"."""
    return [
        f"VAR {p}A = ABS ( {v} )",
        f"VAR {p}Esc = SWITCH ( TRUE (), {p}A >= 999950, 1000000, {p}A >= 9999.5, 1000, 1 )",
        f'VAR {p}N = FORMAT ( {p}A / {p}Esc, SWITCH ( {p}Esc, 1000000, "0.0", 1000, "0", "#,0" ), "pt-BR" )',
        f'VAR {p}U = SWITCH ( {p}Esc, 1000000, " mi", 1000, " mil", "" )',
        f'VAR {p}S = IF ( {v} < 0, "{MENOS}", "" )',
    ]


def brl(v: str, p: str, marca: bool = True, mais: bool = False) -> list[str]:
    """{p}Txt = "R$ 43,3 mi" (ou "—" vazio); com marca, o núcleo vai marcado para o contador; mais=True escreve "+"
    nos positivos ("+R$ 2,8 mi")."""
    linhas = compacto(v, p)
    if mais:
        linhas[-1] = f'VAR {p}S = SWITCH ( TRUE (), {v} < 0, "{MENOS}", {v} > 0, "+", "" )'
    if marca:
        corpo = f'"⁅" & {p}S & "R$ ¦" & {p}N & "¦" & {p}U & "⁆"'
    else:
        corpo = f'{p}S & "R$ " & {p}N & {p}U'
    linhas.append(f'VAR {p}Txt = IF ( ISBLANK ( {v} ), "—", {corpo} )')
    return linhas


def num(v: str, p: str, marca: bool = True) -> list[str]:
    """{p}Txt = "6,3 mi" / "321 mil" / "1.500" (sem R$)."""
    linhas = compacto(v, p)
    corpo = (f'"⁅" & {p}S & "¦" & {p}N & "¦" & {p}U & "⁆"' if marca else f'{p}S & {p}N & {p}U')
    linhas.append(f'VAR {p}Txt = IF ( ISBLANK ( {v} ), "—", {corpo} )')
    return linhas


def inteiro(v: str, p: str, marca: bool = True) -> list[str]:
    """{p}Txt = "7.226"."""
    n = f'FORMAT ( ABS ( {v} ), "#,0", "pt-BR" )'
    s = f'IF ( {v} < 0, "{MENOS}", "" )'
    corpo = f'"⁅" & {s} & "¦" & {n} & "¦⁆"' if marca else f'{s} & {n}'
    return [f'VAR {p}Txt = IF ( ISBLANK ( {v} ), "—", {corpo} )']


def pct(v: str, p: str, casas: int = 1, marca: bool = True) -> list[str]:
    """{p}Txt = "17,9%" (v em 0–1)."""
    fmt = "0." + "0" * casas if casas else "0"
    n = f'FORMAT ( ABS ( {v} ) * 100, "{fmt}", "pt-BR" )'
    s = f'IF ( {v} < 0, "{MENOS}", "" )'
    corpo = f'"⁅" & {s} & "¦" & {n} & "¦%⁆"' if marca else f'{s} & {n} & "%"'
    return [f'VAR {p}Txt = IF ( ISBLANK ( {v} ), "—", {corpo} )']


def variacao(v: str, p: str, tipo: str = "pct", casas: int = 1, marca: bool = True) -> list[str]:
    """{p}Seta (HTML do ▲/▼ colorido), {p}Num ("+6,8%" / "−0,4%" / "+213") e {p}Txt = seta + espaço + número.
    tipo: pct (variação ou diferença de percentuais, v em 0–1) | int (diferença inteira). Zero exibido = sem seta."""
    if tipo == "pct":
        fmt = "0." + "0" * casas if casas else "0"
        r = f"ROUND ( {v} * 100, {casas} )"
        n = f'FORMAT ( ABS ( {v} ) * 100, "{fmt}", "pt-BR" )'
        suf = "%"
    else:
        r = f"ROUND ( {v}, 0 )"
        n = f'FORMAT ( ABS ( {v} ), "#,0", "pt-BR" )'
        suf = ""
    nucleo = f'"⁅" & {p}Sn & "¦" & {n} & "¦{suf}⁆"' if marca else f'{p}Sn & {n} & "{suf}"'
    return [
        f"VAR {p}R = {r}",
        f'VAR {p}Sn = SWITCH ( TRUE (), {p}R > 0, "+", {p}R < 0, "{MENOS}", "" )',
        f"VAR {p}Seta = SWITCH ( TRUE (), {p}R > 0, \"<span class='up'>▲</span>\", {p}R < 0, "
        f"\"<span class='dn'>▼</span>\", \"<span class='eq'>■</span>\" )",
        f"VAR {p}Num = {nucleo}",
        f'VAR {p}Txt = IF ( ISBLANK ( {v} ), "—", {p}Seta & " " & {p}Num )',
    ]


def cabecalho(pasta: str, descricao: str, formato: str = "texto", gerado: str = "manual") -> str:
    return "\n".join(["/*", f"@pasta: {pasta}", f"@formato: {formato}", f"@descricao: {descricao}",
                      f"@gerado: {gerado}", "*/"]) + "\n"


def bloco(linhas: list[str], recuo: int = 0) -> str:
    return "\n".join((" " * recuo) + l for l in linhas)


# ---------------------------------------------------------------------------------------------- rótulos para o Deneb
# Cada função devolve as VARs de um rótulo com os 25 quadros do contador separados por '|' ({p}Txt; vazio sem valor).
# A medida que as usa precisa do bloco /* @contador:tabela */ … /* @contador:fim */ uma vez, antes delas.
def quadros_brl(v: str, p: str, mais: bool = False) -> list[str]:
    linhas = compacto(v, p)
    if mais:
        linhas[-1] = f'VAR {p}S = SWITCH ( TRUE (), {v} < 0, "{MENOS}", {v} > 0, "+", "" )'
    linhas += [f"VAR {p}T = {p}N", f"/* @contador:deneb final={p}T nome={p}q */", "/* @contador:fim */",
               f'VAR {p}Txt = IF ( ISBLANK ( {v} ), "", {p}S & "R$ " & SUBSTITUTE ( COALESCE ( {p}q, {p}T ), "|", '
               f'{p}U & "|" & {p}S & "R$ " ) & {p}U )']
    return linhas


def quadros_num(v: str, p: str) -> list[str]:
    linhas = compacto(v, p)
    linhas += [f"VAR {p}T = {p}N", f"/* @contador:deneb final={p}T nome={p}q */", "/* @contador:fim */",
               f'VAR {p}Txt = IF ( ISBLANK ( {v} ), "", {p}S & SUBSTITUTE ( COALESCE ( {p}q, {p}T ), "|", '
               f'{p}U & "|" & {p}S ) & {p}U )']
    return linhas


def quadros_pct(v: str, p: str, casas: int = 1, mais: bool = False) -> list[str]:
    fmt = "0." + "0" * casas if casas else "0"
    s = (f'SWITCH ( TRUE (), ROUND ( {v} * 100, {casas} ) > 0, "+", ROUND ( {v} * 100, {casas} ) < 0, "{MENOS}", "" )'
         if mais else f'IF ( {v} < 0, "{MENOS}", "" )')
    return [f"VAR {p}S = {s}", f'VAR {p}T = FORMAT ( ABS ( {v} ) * 100, "{fmt}", "pt-BR" )',
            f"/* @contador:deneb final={p}T nome={p}q */", "/* @contador:fim */",
            f'VAR {p}Txt = IF ( ISBLANK ( {v} ), "", {p}S & SUBSTITUTE ( COALESCE ( {p}q, {p}T ), "|", "%|" & {p}S ) & "%" )']


def quadros_dec(v: str, p: str, casas: int = 1) -> list[str]:
    """Número com casas decimais e sem unidade ("28,7")."""
    fmt = "0." + "0" * casas if casas else "0"
    return [f'VAR {p}S = IF ( {v} < 0, "{MENOS}", "" )', f'VAR {p}T = FORMAT ( ABS ( {v} ), "{fmt}", "pt-BR" )',
            f"/* @contador:deneb final={p}T nome={p}q */", "/* @contador:fim */",
            f'VAR {p}Txt = IF ( ISBLANK ( {v} ), "", {p}S & SUBSTITUTE ( COALESCE ( {p}q, {p}T ), "|", "|" & {p}S ) )']


def quadros_int(v: str, p: str, mais: bool = False) -> list[str]:
    s = (f'SWITCH ( TRUE (), {v} > 0, "+", {v} < 0, "{MENOS}", "" )' if mais else f'IF ( {v} < 0, "{MENOS}", "" )')
    return [f"VAR {p}S = {s}", f'VAR {p}T = FORMAT ( ABS ( {v} ), "#,0", "pt-BR" )',
            f"/* @contador:deneb final={p}T nome={p}q */", "/* @contador:fim */",
            f'VAR {p}Txt = IF ( ISBLANK ( {v} ), "", {p}S & SUBSTITUTE ( COALESCE ( {p}q, {p}T ), "|", "|" & {p}S ) )']


def medida_rotulos(pasta: str, descricao: str, leituras: list[tuple[str, str]], rotulos: list[list[str]],
                   finais: list[str], gerado: str, guarda: str | None = None) -> str:
    """Medida de desenho que devolve vários rótulos de uma linha do Deneb separados por '§' (cada um com os quadros
    do contador separados por '|')."""
    L = ["-- 1 · Leituras"] + [f"VAR {v} = [{m}]" for v, m in leituras] + ["-- 2 · Textos",
         "/* @contador:tabela */", "/* @contador:fim */"]
    for r in rotulos:
        L += r
    corpo = ' & "§" & '.join(finais)
    if guarda:
        # linha fora da lista mostrada: vazio (o Deneb descarta a linha e o contador não roda à toa)
        corpo = f"IF ( {guarda} <> 1, BLANK (), {corpo} )"
    L += ["-- 4 · Marcação", "RETURN", "    " + corpo]
    return cabecalho(pasta, descricao, gerado=gerado) + "\n".join(L) + "\n"

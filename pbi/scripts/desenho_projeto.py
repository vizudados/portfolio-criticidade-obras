# -*- coding: utf-8 -*-
"""desenho_projeto — trechos DAX de DESENHO (formatação pt-BR, escape, cabeçalho) do painel Criticidade de Obras.

Regras de número, lidas das telas do Figma (FjBWDk5odF9HaZ2pwhGosl, página 03 · Mockup):
  · 100 mi ou mais ........ "R$ 163,8 mi"   (uma casa)
  · 1 mi a 100 mi ......... "R$ 6,21 mi"    (duas casas)
  · mil a 1 mi ............ "R$ 731 mil"    (inteiro)
  · abaixo de mil ......... "R$ 850"
  · quadradinho ........... "R$ 5.435.297,10" (centavos, como a planilha imprime)
  · % do orçamento ........ "+0,45%" (duas casas, com sinal) · físico "45,2%" · desembolso × previsto "+36%"
  · pontos percentuais .... "−3,9 p.p." · variação do resultado "−0,49 p.p."
Sinal negativo é o "−" (U+2212) e vem antes do "R$" ("−R$ 2,19 mi"). Cada função devolve linhas DAX (sem recuo) que
definem VARs com o prefixo dado e terminam em {p}Txt; valor vazio vira "—". O desenho só formata o que a conta leu.
"""
from __future__ import annotations

MENOS = "−"


def esc(expr: str) -> str:
    """Escape de HTML de um texto vindo do modelo (& primeiro)."""
    return ('SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( ' + expr
            + ', "&", "&amp;" ), "<", "&lt;" ), ">", "&gt;" ), "\'", "&#39;" )')


def texto(s: str) -> str:
    """Literal DAX de um texto fixo."""
    return '"' + s.replace('"', '""') + '"'


def _sinal(v: str, mais: bool, arred: str | None = None) -> str:
    r = arred or v
    if mais:
        return f'SWITCH ( TRUE (), {r} < 0, "{MENOS}", {r} > 0, "+", "" )'
    return f'IF ( {r} < 0, "{MENOS}", "" )'


def rs(v: str, p: str, mais: bool = False, vazio: str = "—") -> list[str]:
    """{p}Txt = "R$ 731 mil" · "R$ 6,21 mi" · "R$ 163,8 mi" · "−R$ 2,19 mi" (mais=True: "+R$ 811 mil")."""
    return [
        f"VAR {p}A = ABS ( {v} )",
        f'VAR {p}Nu = SWITCH ( TRUE (), {p}A >= 99950000, FORMAT ( {p}A / 1000000, "0.0", "pt-BR" ), '
        f'{p}A >= 999500, FORMAT ( {p}A / 1000000, "0.00", "pt-BR" ), '
        f'{p}A >= 999.5, FORMAT ( {p}A / 1000, "0", "pt-BR" ), FORMAT ( {p}A, "#,0", "pt-BR" ) )',
        f'VAR {p}Un = SWITCH ( TRUE (), {p}A >= 999500, " mi", {p}A >= 999.5, " mil", "" )',
        f"VAR {p}N = {p}Nu & {p}Un",
        f"VAR {p}Zero = {p}N = \"0\"",
        f"VAR {p}S = IF ( {p}Zero, \"\", {_sinal(v, mais)} )",
        f'VAR {p}Txt = IF ( ISBLANK ( {v} ), "{vazio}", {p}S & "R$ " & {p}N )',
    ]


def rs_cheio(v: str, p: str, vazio: str = "—") -> list[str]:
    """{p}Txt = "R$ 5.435.297,10" (centavos)."""
    return [
        f'VAR {p}N = FORMAT ( ABS ( {v} ), "#,0.00", "pt-BR" )',
        f"VAR {p}S = {_sinal(v, False, f'ROUND ( {v}, 2 )')}",
        f'VAR {p}Txt = IF ( ISBLANK ( {v} ), "{vazio}", {p}S & "R$ " & {p}N )',
    ]


def pct(v: str, p: str, casas: int = 1, mais: bool = False, vazio: str = "—") -> list[str]:
    """{p}Txt = "45,2%" (v em 0–1); mais=True escreve "+" nos positivos ("+0,45%")."""
    fmt = "0." + "0" * casas if casas else "0"
    arred = f"ROUND ( {v} * 100, {casas} )"
    return [
        f'VAR {p}N = FORMAT ( ABS ( {v} ) * 100, "{fmt}", "pt-BR" )',
        f"VAR {p}S = {_sinal(v, mais, arred)}",
        f'VAR {p}Txt = IF ( ISBLANK ( {v} ), "{vazio}", {p}S & {p}N & "%" )',
    ]


def pp(v: str, p: str, casas: int = 1, vazio: str = "—") -> list[str]:
    """{p}Txt = "−3,9 p.p." / "+4,3 p.p." (v já em pontos percentuais)."""
    fmt = "0." + "0" * casas if casas else "0"
    arred = f"ROUND ( {v}, {casas} )"
    return [
        f'VAR {p}N = FORMAT ( ABS ( {v} ), "{fmt}", "pt-BR" )',
        f"VAR {p}S = {_sinal(v, True, arred)}",
        f'VAR {p}Txt = IF ( ISBLANK ( {v} ), "{vazio}", {p}S & {p}N & " p.p." )',
    ]


def numero(v: str, p: str, casas: int = 1, vazio: str = "—") -> list[str]:
    """{p}Txt = "72,5" · "0" (pontos: sem casa quando inteiro)."""
    fmt = "0." + "0" * casas if casas else "0"
    return [
        f'VAR {p}N = IF ( {v} = INT ( {v} ), FORMAT ( {v}, "0", "pt-BR" ), FORMAT ( {v}, "{fmt}", "pt-BR" ) )',
        f'VAR {p}Txt = IF ( ISBLANK ( {v} ), "{vazio}", {p}N )',
    ]


def inteiro(v: str, p: str, vazio: str = "0") -> list[str]:
    return [f'VAR {p}N = FORMAT ( {v}, "#,0", "pt-BR" )',
            f'VAR {p}Txt = IF ( ISBLANK ( {v} ), "{vazio}", {p}N )']


# ---------------------------------------------------------------------------------------------------------------------
# Contador (odômetro de contador.py): {p}Od = o mesmo texto de {p}Txt com o núcleo numérico contando. Chame depois da
# função de formatação do mesmo prefixo; a medida precisa de od_tabela() uma vez (a VAR _odQ).
# ---------------------------------------------------------------------------------------------------------------------
def od_tabela() -> str:
    import contador as C
    return C.bloco_tabela().rstrip()


def _od(p: str, nucleo: str, pre: str, suf: str, vazio: str) -> list[str]:
    import contador as C
    return [C.bloco_od(p + "K", nucleo).rstrip(),
            f"VAR {p}Od = IF ( {vazio}, {p}Txt, {pre}{p}KOd{suf} )"]


def od_rs(v: str, p: str) -> list[str]:
    """Depois de rs(v, p): "−R$ " + odômetro do núcleo ("2,19") + unidade (" mi")."""
    return _od(p, f"{p}Nu", f'{p}S & "R$ " & ', f" & {p}Un", f"ISBLANK ( {v} )")


def od_pct(v: str, p: str) -> list[str]:
    """Depois de pct(v, p): sinal + odômetro + "%"."""
    return _od(p, f"{p}N", f"{p}S & ", ' & "%"', f"ISBLANK ( {v} )")


def od_pp(v: str, p: str) -> list[str]:
    """Depois de pp(v, p): sinal + odômetro + " p.p."."""
    return _od(p, f"{p}N", f"{p}S & ", ' & " p.p."', f"ISBLANK ( {v} )")


def od_num(v: str, p: str) -> list[str]:
    """Depois de numero(v, p) ou inteiro(v, p): o próprio número no odômetro."""
    return _od(p, f"{p}N", "", "", f"ISBLANK ( {v} )")


def cabecalho(pasta: str, descricao: str, gerado: str, formato: str = "texto", nome: str | None = None) -> str:
    linhas = ["/*", f"@pasta: {pasta}", f"@formato: {formato}", f"@descricao: {descricao}"]
    if nome:
        linhas.append(f"@nome: {nome}")
    linhas += [f"@gerado: {gerado}", "*/"]
    return "\n".join(linhas) + "\n"

# -*- coding: utf-8 -*-
"""justificativas_rodape — nomes das obras com justificativa em branco no rodapé de uma linha dos tooltips de desembolso
(T1 · Tooltip indicador, no indicador desembolso; T4 · Tooltip mês do desembolso). Figma: nota 366:8262 na Fileira ·
Tooltips da Tela 04 (estados 366:7993 e 366:8126, ago/26 com dados reais).

Regra (o rodapé tem uma linha e nunca corta um nome no meio):
  "P de E preenchidas · em branco: " e os nomes da lista, que é conta e já vem do maior para o menor |desvio|.
  1. todos os nomes cabem → todos ("JANGADA, POTENGI, REDINHA e CAJUEIRO");
  2. senão, os RODAPE_NOMES primeiros e "e mais M" (M é conta: '… em branco fora do rodapé'); quando M = P, "e
     outra(s)", sem número, para nenhum número se repetir na linha (L058);
  3. nem esses cabem → sem nomes: "todas em branco" (P = 0), "as outras em branco" (N = P) ou "N em branco".
O desenho só estima a largura para escolher a forma (geometria; Segoe UI 13, medido no Edge): cada caractere do nome
pela sua largura (LARGURA, arredondada para cima; o SWITCH do DAX não distingue maiúsculas, então minúscula conta como
maiúscula, para mais), JANGADA 48,6 × 48,3 medido · POTENGI 33,4 × 32,9 · REDINHA 41,5 × 41,2 · CAJUEIRO 41,6 × 41,7; ", " 7,
" e " 14, " e mais 9" 51 (+7 por algarismo a mais), " e outra" 41, " e outras" 50, "em branco: " 68.
"""
from __future__ import annotations

RODAPE_NOMES = 2            # nomes antes de "e mais M" (as contas '… em branco fora do rodapé' usam o mesmo número)
# largura (px) de cada caractere de nome em Segoe UI 13 (medida no Edge, 06/10/2026); o resto conta PX_OUTRO
LARGURA = {" ": 3.6, "A": 8.4, "B": 7.5, "C": 7.8, "D": 9.2, "E": 6.6, "F": 6.4, "G": 9.0, "H": 9.3, "I": 3.5, "J": 4.2,
           "K": 7.6, "L": 6.2, "M": 11.7, "N": 9.8, "O": 9.8, "P": 7.3, "Q": 9.8, "R": 7.8, "S": 7.0, "T": 7.1,
           "U": 9.0, "V": 8.1, "W": 12.2, "X": 7.7, "Y": 7.2, "Z": 7.5, "Á": 8.4, "Ã": 8.4, "Â": 8.4, "À": 8.4,
           "É": 6.6, "Ê": 6.6, "Í": 3.5, "Ó": 9.8, "Õ": 9.8, "Ô": 9.8, "Ú": 9.0, "Ç": 7.8}
PX_OUTRO = 8
PX_VIRG, PX_E = 7, 14
PX_MAIS, PX_DIGITO, PX_OUTRA, PX_OUTRAS, PX_EM_BRANCO = 51, 7, 41, 50, 68


def _px_nomes(var: str, sem: str) -> list[str]:
    """Linhas DAX: VAR {var} = largura estimada (px, sem arredondar) dos caracteres do texto {sem} (sem '|'), somando a
    largura de cada caractere (LARGURA) sobre a série de posições que a própria medida monta."""
    pares = [f'"{c}", {w}' for c, w in LARGURA.items()]
    casos = [", ".join(pares[i:i + 10]) for i in range(0, len(pares), 10)]
    return [
        f"VAR {var}Car = GENERATESERIES ( 1, LEN ( {sem} ) + 0 )",
        f"VAR {var} =",
        f"    SUMX ( {var}Car, /* lista */ -- geometria",
        f"        SWITCH (",
        f"            MID ( {sem}, [Value], 1 ),",
        *[f"            {c}," for c in casos],
        f"            {PX_OUTRO}",
        f"        )",
        f"    )",
    ]


def nomes(lista: str, fora: str, pre: str, branco: str, cabe: str, p: str = "_nb") -> list[str]:
    """Linhas DAX (bloco '-- 2 · Textos') que montam {p}Txt, o trecho depois de "P de E preenchidas · ".

    lista: VAR com 'A|B|C' (conta, na ordem do maior |desvio|); fora: VAR com M (conta, vazio até RODAPE_NOMES nomes);
    pre: VAR com P; branco: VAR com N; cabe: expressão com os px disponíveis para o trecho (geometria do chamador).
    {p}N (quantos nomes) só decide o texto; nenhum número escrito sai daqui: P, N e M são contas."""
    k = RODAPE_NOMES
    return [
        "/* nomes em branco numa linha só, sem cortar nome: todos; senão os "
        f"{k} primeiros e 'e mais M'; senão nenhum (justificativas_rodape.py) */",
        f'VAR {p}N = IF ( ISBLANK ( {lista} ) || {lista} = "", 0, PATHLENGTH ( {lista} ) )',
        f'VAR {p}Pos = IF ( {p}N >= 2, FIND ( "§", SUBSTITUTE ( {lista}, "|", "§", {p}N - 1 ) ) )',
        f'VAR {p}Todos =',
        f'    IF (',
        f'        {p}N <= 1,',
        f'        {lista},',
        f'        SUBSTITUTE ( LEFT ( {lista}, {p}Pos - 1 ), "|", ", " ) & " e " & MID ( {lista}, {p}Pos + 1, 999 )',
        f'    )',
        f'VAR {p}Corte = FIND ( "§", SUBSTITUTE ( {lista} & "|", "|", "§", {k} ), 1, LEN ( {lista} ) + 1 )',
        f'VAR {p}Primeiros = LEFT ( {lista}, {p}Corte - 1 )',
        f'VAR {p}Resto = IF ( {fora} = {pre}, IF ( {fora} = 1, " e outra", " e outras" ), " e mais " & {fora} )',
        f'VAR {p}SemTodos = SUBSTITUTE ( {lista}, "|", "" )',
        f'VAR {p}SemPrimeiros = SUBSTITUTE ( {p}Primeiros, "|", "" )',
        *_px_nomes(f"{p}PxNomesTodos", f"{p}SemTodos"),
        *_px_nomes(f"{p}PxNomesPrimeiros", f"{p}SemPrimeiros"),
        f'VAR {p}PxTodos = ROUND ( {p}PxNomesTodos + {PX_VIRG} * MAX ( {p}N - 2, 0 ) + IF ( {p}N >= 2, {PX_E}, 0 ), 0 )'
        ' -- geometria',
        f'VAR {p}PxResto =',
        f'    SWITCH (',
        f'        TRUE (),',
        f'        {fora} <> {pre}, {PX_MAIS} + {PX_DIGITO} * ( LEN ( {fora} & "" ) - 1 ), -- geometria',
        f'        {fora} = 1, {PX_OUTRA},',
        f'        {PX_OUTRAS}',
        f'    )',
        f'VAR {p}PxPrimeiros = ROUND ( {p}PxNomesPrimeiros + {PX_VIRG} * {k - 1} + {p}PxResto, 0 ) -- geometria',
        f'VAR {p}PxCabe = ROUND ( {cabe}, 0 ) - {PX_EM_BRANCO} -- geometria',
        f'VAR {p}Txt =',
        f'    SWITCH (',
        f'        TRUE (),',
        f'        {branco} = 0, "nenhuma em branco",',
        f'        {p}PxTodos <= {p}PxCabe, "em branco: " & {p}Todos,',
        f'        {p}N > {k} && {p}PxPrimeiros <= {p}PxCabe,',
        f'            "em branco: " & SUBSTITUTE ( {p}Primeiros, "|", ", " ) & {p}Resto,',
        f'        {pre} = 0, "todas em branco",',
        f'        {branco} = {pre}, "as outras em branco",',
        f'        {branco} & " em branco"',
        f'    )',
    ]

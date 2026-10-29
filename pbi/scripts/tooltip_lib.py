# -*- coding: utf-8 -*-
"""tooltip_lib — o que os tooltips de página das cinco telas têm em comum desde a F4 (pedido do Alisson, 28/10/2026:
"aproveitar todo espaço, redistribuir quando há menos elementos, e diminuir quando há mais" e "todos elementos de
tooltip animados").

Escala pela contagem de linhas. A lista principal do tooltip ganha a classe `ls`, a faixa `e1`…`e5` (escala()) e
`--n` = quantas linhas ela tem (com a "e mais N obras"). A lista cresce até ocupar o corpo (o corpo é uma coluna
flexível e a lista tem flex 1), limitada a n × a altura máxima da linha da faixa; cada linha fica com 1fr dessa altura.
Com poucas linhas, linhas mais altas e fonte maior; com muitas, linhas e fonte menores, até o piso de 13 px:

    faixa  linhas   altura máx. da linha   fator da fonte
    e1     ≤ 3      96                     1,35
    e2     4–6      64                     1,20
    e3     7–9      52                     1,08
    e4     10–12    40                     0,95
    e5     ≥ 13     32                     0,87

O teto é folgado de propósito: a lista quase sempre ocupa o corpo inteiro; ele só impede uma ou duas linhas gigantes.

O fator vale para os corpos de fonte que cada tooltip passa a css_escala (seletor → px de antes), com piso de 13 px.

Cascata C5 (contador.py: 200 ms de .35 → 1 e 40 ms por posição, sem animation-delay, '.tqv' = já visto): cabeçalho
na posição 0, os blocos do corpo fora da lista na 1, a linha k da lista na k + 1 (até LINHAS_MAX) e o pé na última.
Marcas, pílulas e pontos de cada linha entram junto com ela, crescendo de 50% (tqP). Sem animação, com movimento
reduzido ou já visto: o estado final, que é o estilo base.
"""
from __future__ import annotations

import contador as C

LINHAS_MAX = 14
FAIXAS = [(3, 1, 96, "1.35"), (6, 2, 64, "1.2"), (9, 3, 52, "1.08"), (12, 4, 40, ".95"), (None, 5, 32, ".87")]
PISO_PX = 13


def escala(n: str) -> str:
    """DAX: a classe da faixa ("e1"…"e5") pela contagem de linhas `n`."""
    ramos = ", ".join(f"{n} <= {lim}, \"e{k}\"" for lim, k, _h, _f in FAIXAS if lim is not None)
    return f"SWITCH ( TRUE (), {ramos}, \"e5\" )"


def atributos(n: str) -> str:
    """DAX (trecho de concatenação para dentro de class='…'): " ls eK' style='--n:N" — feche a aspa simples depois."""
    return f'" ls " & {escala(n)} & "\' style=\'--n:" & {n} & "'


def css_escala(fontes: dict[str, int], grade: bool = False, linha: str = ".tt .ls>*", teto: int | None = None) -> str:
    """CSS da escala. `fontes` = seletor → corpo de antes (px); `grade` = a lista é uma grade CSS (linhas com
    display:contents): as linhas viram grid-auto-rows de 1fr; senão é uma coluna flexível com linhas de flex 1."""
    faixas = "".join(f".tt .e{k}{{--k:{f};--hm:{h}px}}" for _l, k, h, f in FAIXAS)
    base = (".tt .corpo{display:flex;flex-direction:column}"
            ".tt .ls{flex:1 1 auto;min-height:0;max-height:calc(var(--n,9) * var(--hm,36px))}")
    if grade:
        base += ".tt .ls{grid-auto-rows:minmax(0,1fr);align-content:stretch}"
    else:
        base += f".tt .ls{{display:flex;flex-direction:column}}{linha}{{flex:1 1 0;min-height:0}}"
    tam = css_fontes(fontes, teto)
    # pílula de item (altura fixa de 22) e marca de status (11) acompanham a faixa
    marcas = (".tt .ls .chi{height:auto;min-height:22px;padding:calc(2px * var(--k,1)) 8px;"
              "font-size:max(13px,calc(13px * var(--k,1)))}"
              ".tt .ls .mk{width:calc(11px * var(--k,1));height:calc(11px * var(--k,1))}")
    return faixas + base + tam + marcas


def css_fontes(fontes: dict[str, int], teto: int | None = None) -> str:
    """Só as regras de fonte da escala: corpo de antes × o fator da faixa, com piso de 13 px. `teto` (px): linhas com
    colunas em posição fixa (barra divergente no meio) não crescem além dele; teto 0 = não crescem além do corpo de
    antes (só diminuem)."""
    def corpo(px: int) -> str:
        v = f"max({PISO_PX}px,calc({px}px * var(--k,1)))"
        if teto is None:
            return v
        return f"min({max(teto, px)}px,{v})"
    return "".join(f"{sel}{{font-size:{corpo(px)}}}" for sel, px in fontes.items())


def entrada(linha_k: str, blocos: list[str] | None = None, pe: str = ".tt .pe", cab: str = ".tt .cab",
            pop: str = ".mk,.chi,.chip,.chp,circle,.pend") -> str:
    """CSS da cascata C5 do tooltip. `linha_k` = seletor da linha k com '{k}' no lugar do índice (ex.:
    '.tt .ls>:nth-child({k})'); `blocos` = seletores do corpo fora da lista (posição 1); `pop` = elementos que entram
    crescendo junto com a linha (marcas, pílulas, pontos)."""
    pos: list[tuple[int, list[str]]] = [(0, [cab])]
    if blocos:
        pos.append((1, blocos))
    for k in range(1, LINHAS_MAX + 1):
        pos.append((k + 1, [linha_k.format(k=k)]))
    pos.append((LINHAS_MAX + 2, [pe]))
    regras, keyframes, todos = [], [], []
    for i, sels in pos:
        atraso = C.ENTRADA_PASSO_MS * i
        dur = C.ENTRADA_MS + atraso
        p = C._pct(100 * atraso / dur) if atraso else None
        keyframes.append(f"@keyframes tqE{i}{{{'from' if not atraso else '0%,' + p + '%'}{{opacity:.35}}}}")
        keyframes.append(f"@keyframes tqP{i}{{{'from' if not atraso else '0%,' + p + '%'}{{opacity:0;transform:scale(.5)}}}}")
        alvo = ",".join(sels)
        regras.append(f"{alvo}{{animation:tqE{i} {dur / 1000:g}s ease-out}}")
        filhos = ",".join(f"{s} :is({pop})" for s in sels)
        regras.append(f"{filhos}{{animation:tqP{i} {dur / 1000 + .1:g}s ease-out}}")
        todos += sels + [f"{s} :is({pop})" for s in sels]
    lista = ",".join(todos)
    lista_v = ",".join(f".tqv {s}" for s in todos)
    return (C.CSS_ABRE + "".join(keyframes)
            + f":is({pop}){{transform-box:fill-box;transform-origin:center}}"
            + "".join(regras) + f"{lista_v}{{animation:none}}"
            + f"@media (prefers-reduced-motion:reduce){{{lista}{{animation:none!important}}}}" + C.CSS_FECHA)

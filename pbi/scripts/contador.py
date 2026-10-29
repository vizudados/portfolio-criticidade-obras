#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contador dos números (odômetro à prova de falha) — copiado de outro projeto em 06/10/2026 (a origem não muda; lá veio do painel de referência). No painel deste projeto, os geradores Python usam as funções (css_texto, js_texto, bloco_tabela, bloco_od, colapsar, conferir); os blocos @contador em .dax não são usados, porque os .dax daqui são todos gerados. Texto original: ajudante ÚNICO das páginas VG, ON,
PD, RT, FT e dos 9 tooltips de página do painel de referência. Contrato: spec/contadores-animacoes.md (C1–C10).

A técnica é a da capa (capa/SPEC-CAPA-V4.md §4; scripts/capa/gerar_capa_v3.py), sem outra:
  - 25 quadros formatados pelo DAX em aritmética inteira: quadro k (0..23) = ROUND ( T × f_k / 1000, 0 ) na unidade do
    último dígito exibido, f_k = milésimos inteiros de 1 − (1 − k/24)³ (a MESMA tabela da capa); o quadro 24 é o texto
    final canônico que a medida já emitia;
  - o transform final no estilo base e o keyframe só com 'from': sem animação aparece o valor certo, nunca zero;
  - T sai do próprio texto final (o núcleo numérico sem '.' e ','), então o quadro 23 é sempre igual ao final e o
    espelho Python bate caractere a caractere; prefixo e sufixo ('R$ ', ' mi', '%', ' dias') ficam fora da tira;
  - tira compacta (um nó de texto, uma linha por quadro, white-space:pre), texto final no fluxo e invisível (<o-v>,
    fica para o leitor de tela e para a cópia) e a tira por cima (<o-t aria-hidden>), caixa <o-d> inline-block com
    height:1lh e overflow:clip — medidas no Edge em 28/09 (spec C2).

O que este módulo faz:
  1. gera os BLOCOS entre marcadores dentro dos .dax (a medida continua escrita à mão; só o bloco é gerado):
       /* @contador:tabela */ … /* @contador:fim */                  VAR _odQ (os 25 pares k, f)
       /* @contador:od nome=_x final=_xTxt [prefixo='R$ '] [sufixo=' mi'] */ … /* @contador:fim */
                                                                     VARs _xN … _xOd (o HTML do número)
       /* @contador:css */ … /* @contador:fim */                     & "…" do CSS do odômetro (dentro de folha DAX)
       /* @contador:entrada sel0=… sel1=… … */ … /* @contador:fim */  & "…" da cascata dos tooltips (C5)
       /* @contador:js */ … /* @contador:fim */                      VAR _odJs = "<script>…</script>" (C4)
       /* @contador:deneb final=_t [prefixo=…] [sufixo=…] */ … /* @contador:fim */
                                                                     VAR _odQuadros = quadros separados por '|'
       /* @contador:od nome=_x final=_xTxt prefixo='R$ ' sufixos=' mil| mi|' */ … /* @contador:fim */
                                                                     R$ agregado: a unidade é lida do próprio texto
       /* @contador:prosa nome=_p texto=_textoEscapado */ … /* @contador:fim */
                                                                     VAR _pHtml: texto corrido com números marcados
                                                                     ⁅pré¦número¦pós⁆ (dax_marca) → odômetro dentro de
                                                                     <o-n>; o ALT usa dax_limpar_marcas
  2. dá o CSS/JS em texto cru para os geradores que montam folha a partir de fonte (qa/tela-PD/gerar_dax.py,
     qa/tela-FT/gerar_dax_ft.py): css_texto(), entrada_texto(...), js_texto();
  3. dá o espelho e as provas: quadros(nucleo), extrair(html), colapsar(html), conferir(html).

    python -X utf8 scripts/contador.py --listar            # blocos encontrados em dax/**
    python -X utf8 scripts/contador.py --conferir          # disco × gerado (sai 1 se algum bloco estiver velho)
    python -X utf8 scripts/contador.py --aplicar [arq …]   # regrava os blocos (backup em _backups/ antes)
    python -X utf8 scripts/contador.py --lint              # autoteste: frações = capa, portões de texto, node --check
"""
from __future__ import annotations

import argparse
import datetime
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True
AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
DAX = RAIZ / "dax"
BACKUPS = RAIZ / "_backups"

# ---------------------------------------------------------------------------------------------------------------------
# Contrato (spec/contadores-animacoes.md)
# ---------------------------------------------------------------------------------------------------------------------
PASSOS = 24
FRACOES = [round(1000 * (1 - (1 - k / PASSOS) ** 3)) for k in range(PASSOS + 1)]
PASSOS_DENSO = 12                    # C8 "tabelas densas": a mesma fórmula com 12 passos (13 quadros), só nas células
FRACOES_DENSO = [round(1000 * (1 - (1 - k / PASSOS_DENSO) ** 3)) for k in range(PASSOS_DENSO + 1)]


def fracoes(passos: int = PASSOS) -> list[int]:
    return FRACOES if passos == PASSOS else FRACOES_DENSO if passos == PASSOS_DENSO else \
        [round(1000 * (1 - (1 - k / passos) ** 3)) for k in range(passos + 1)]
DURACAO = ".6s"                      # C3: 600 ms (R13 da VG; a revisita da capa)
T_MINIMO = 2                         # C1: T < 2 na unidade do último dígito fica estático (zero, "1 pedido", "0,1%")
SEP_QUADRO = "\n"                    # tira compacta: um quadro por linha
SEP_DENEB = "|"                      # quadros de rótulo do Deneb (split no Vega)
MARCA_JS = "/*contador*/"            # identifica o <script> do contador (colapsar() tira)
CSS_ABRE, CSS_FECHA = "/*contador*/", "/*fim-contador*/ "  # delimitam o CSS do contador (colapsar() tira o embutido);
# o espaço no fim evita "*//*" quando dois blocos ficam lado a lado (o portão da FT recusa qualquer "//")
ENTRADA_MS, ENTRADA_PASSO_MS = 200, 40   # C5: .35 → 1 em 200 ms, 40 ms por posição
JANELA_VISTO_MS = 1500               # C5: atualização a menos de 1,5 s da anterior = "já visto" (sem cascata)

MARCA_ABRE, MARCA_SEP, MARCA_FECHA = "\u2045", "\u00a6", "\u2046"   # ⁅pré¦número¦pós⁆ no texto corrido
ABRE_OD = "<o-d><o-v>"
MEIO_OD = "</o-v><o-t aria-hidden='true'>"
FECHA_OD = "</o-t></o-d>"


# ---------------------------------------------------------------------------------------------------------------------
# Espelho Python (prova): os quadros a partir do núcleo numérico do texto final
# ---------------------------------------------------------------------------------------------------------------------
def _meio_para_cima(num: int, den: int) -> int:
    """ROUND ( num / den, 0 ) do DAX (meio para longe do zero), num ≥ 0, em aritmética inteira."""
    q, r = divmod(num, den)
    return q + (1 if 2 * r >= den else 0)


def analisar_nucleo(nucleo: str) -> tuple[int, int, bool] | None:
    """(T, casas, milhar) do núcleo pt-BR ('5.205' → (5205, 0, True); '72,5' → (725, 1, False)); None se não for número
    puro (a mesma regra do DAX: sem '.' e ',' só dígitos, e T ≥ T_MINIMO)."""
    if not nucleo:
        return None
    s = nucleo.replace(".", "").replace(",", "")
    if not s.isdigit() or not s.isascii():
        return None
    t = int(s)
    if t < T_MINIMO:
        return None
    casas = len(nucleo) - nucleo.index(",") - 1 if "," in nucleo else 0
    return t, casas, "." in nucleo


def _fmt(x: int, casas: int, milhar: bool) -> str:
    base = 10 ** casas
    inteiro, frac = divmod(x, base)
    txt = f"{inteiro:,}".replace(",", ".") if milhar else str(inteiro)
    return txt + ("," + str(frac).zfill(casas) if casas else "")


def quadros(nucleo: str, passos: int = PASSOS) -> list[str] | None:
    """Os passos + 1 quadros do núcleo (último = o próprio núcleo), ou None se o número fica estático."""
    a = analisar_nucleo(nucleo)
    if a is None:
        return None
    t, casas, milhar = a
    return [nucleo if k == passos else _fmt(_meio_para_cima(t * f, 1000), casas, milhar)
            for k, f in enumerate(fracoes(passos))]


def _sufixo_de(final: str, sufixos: list[str]) -> str:
    """O primeiro sufixo alternativo (do mais longo ao mais curto; '' por último) com que o texto final termina."""
    for x in sorted(sufixos, key=len, reverse=True):
        if not x or final.endswith(x):
            return x
    return ""


def html_od(final: str, prefixo: str = "", sufixo: str = "", sufixos: list[str] | None = None,
            passos: int = PASSOS) -> str:
    """Espelho do bloco DAX @contador:od — o HTML que a medida emite para um número. `sufixos` = alternativas lidas do
    próprio texto (R$ agregado: [' mil', ' mi', ''])."""
    if sufixos is not None:
        sufixo = _sufixo_de(final, sufixos)
    if (prefixo and not final.startswith(prefixo)) or (sufixo and not final.endswith(sufixo)) \
            or len(final) <= len(prefixo) + len(sufixo):
        return final
    nucleo = final[len(prefixo):len(final) - len(sufixo)] if sufixo else final[len(prefixo):]
    q = quadros(nucleo, passos)
    if q is None:
        return final
    return prefixo + ABRE_OD + nucleo + MEIO_OD + SEP_QUADRO.join(q) + FECHA_OD + sufixo


def quadros_deneb(final: str, prefixo: str = "", sufixo: str = "") -> str | None:
    """Espelho do bloco @contador:deneb — 25 textos completos separados por '|' (None = rótulo estático)."""
    if (prefixo and not final.startswith(prefixo)) or (sufixo and not final.endswith(sufixo)) \
            or len(final) <= len(prefixo) + len(sufixo):
        return None
    nucleo = final[len(prefixo):len(final) - len(sufixo)] if sufixo else final[len(prefixo):]
    q = quadros(nucleo)
    if q is None:
        return None
    return SEP_DENEB.join(final if k == PASSOS else prefixo + x + sufixo for k, x in enumerate(q))


def html_prosa(texto: str) -> str:
    """Espelho do bloco @contador:prosa: cada ⁅pré¦número¦pós⁆ do texto (já escapado) vira <o-n>pré<o-d>…</o-d>pós</o-n>
    quando o número conta; senão pré+número+pós. Texto com '|' fica sem contador (o PATHITEM usa '|')."""
    limpo = limpar_marcas(texto)
    if "|" in limpo:
        return limpo
    partes = texto.replace(MARCA_ABRE, "|").replace(MARCA_FECHA, "|").split("|")
    out = []
    for i, seg in enumerate(partes, 1):
        if i % 2:
            out.append(seg)
            continue
        i1 = seg.find(MARCA_SEP)
        i2 = seg.find(MARCA_SEP, i1 + 1) if i1 >= 0 else -1
        if i2 >= 0:
            pre, num, suf = seg[:i1], seg[i1 + 1:i2], seg[i2 + 1:]
        else:
            pre, num, suf = "", seg.replace(MARCA_SEP, ""), ""
        q = quadros(num)
        out.append(pre + num + suf if q is None else
                   "<o-n>" + pre + ABRE_OD + num + MEIO_OD + SEP_QUADRO.join(q) + FECHA_OD + suf + "</o-n>")
    return "".join(out)


def limpar_marcas(texto: str) -> str:
    """O texto sem as marcas ⁅ ¦ ⁆ — é o que o ALT e o texto de antes mostravam."""
    return texto.replace(MARCA_ABRE, "").replace(MARCA_FECHA, "").replace(MARCA_SEP, "")


_RE_OD = re.compile(re.escape(ABRE_OD) + r"(.*?)" + re.escape(MEIO_OD) + r"(.*?)" + re.escape(FECHA_OD), re.S)
_RE_JS = re.compile(r"<script>" + re.escape(MARCA_JS) + r".*?</script>", re.S)
_RE_CSS = re.compile(re.escape(CSS_ABRE) + r".*?" + re.escape(CSS_FECHA.rstrip()) + r" ?", re.S)  # tolera o fechamento antigo sem espaço (TTR-HCJ-05)
# a classe do contêiner denso (C8) sai no colapsar: "X od12" → "X"; "od12 X" → "X"; class só com od12 → sem o atributo
_RE_OD12_SO = re.compile(r"""\s+class=(['"])od12\1""")
_RE_OD12 = re.compile(r"""(class=(['"])[^'"]*?)\s+od12(?=\2|\s)""")
_RE_OD12_INI = re.compile(r"""(class=(['"]))od12\s+""")
_RE_STYLE_VAZIO = re.compile(r"<style>\s*</style>")


def extrair(html: str) -> list[tuple[str, list[str]]]:
    """[(texto final do <o-v>, [25 quadros da tira])] na ordem do HTML."""
    return [(m.group(1), m.group(2).split(SEP_QUADRO)) for m in _RE_OD.finditer(html)]


def colapsar(html: str) -> str:
    """O HTML sem contador: cada <o-d> vira o seu texto final; o <script> e o CSS embutido do contador (entre
    /*contador*/ e /*fim-contador*/) saem. Tem de ser igual ao HTML de antes, caractere a caractere (prova C9.3)."""
    semjs = _RE_JS.sub("", _RE_OD.sub(lambda m: m.group(1), html)).replace("<o-n>", "").replace("</o-n>", "")
    semjs = _RE_OD12_INI.sub(r"\1", _RE_OD12.sub(r"\1", _RE_OD12_SO.sub("", semjs)))
    return _RE_STYLE_VAZIO.sub("", _RE_CSS.sub("", semjs))


def referencia_tnum(html: str) -> str:
    """O estado final ESPERADO do HTML novo como texto estático (prova C9.5): cada <o-d> vira um <o-d> em linha só com o
    texto final com os algarismos da fonte (o que o contador mostra no fim; desde 28/10/2026 o <o-v> não é tabular), <o-n>
    fica só com o nowrap, e saem o <script> e o CSS do contador. O render do novo tem de ser igual ao desta referência, e
    a referência igual ao de antes: sem quebra de linha nova, sem texto passando da caixa e sem rolagem nova. Os elementos
    continuam <o-d>/<o-n>, que a medição pula como no novo."""
    ref = _RE_OD.sub(lambda m: "<o-d style='display:inline-block;height:1lh;overflow-x:visible;overflow-y:clip'>" + m.group(1) + "</o-d>", html)
    ref = _RE_JS.sub("", ref).replace("<o-n>", "<o-n style='white-space:nowrap'>")
    return _RE_STYLE_VAZIO.sub("", _RE_CSS.sub("", ref))


def _atributos_com_contador(html: str) -> list[tuple[str, str]]:
    """Atributos cujo VALOR contém '<o-' (contador em title, aria-label ou data-*): a prova de texto colapsaria de volta
    e passaria, mas o leitor de tela leria a tira."""
    from html.parser import HTMLParser

    achados: list[tuple[str, str]] = []

    class _P(HTMLParser):
        def handle_starttag(self, tag, attrs):
            for k, v in attrs:
                if v and "<o-" in v:
                    achados.append((k, v))

    try:
        _P(convert_charrefs=True).feed(html)
    except Exception:  # pragma: no cover
        pass
    return achados


def conferir(html: str) -> list[str]:
    """Prova C9.4: cada tira = espelho do seu <o-v>; quadro 0 = zero; quadros monótonos; quadro 24 = final."""
    erros = []
    for nome, valor in _atributos_com_contador(html):
        erros.append(f"contador dentro do atributo {nome}={valor[:60]!r} (o leitor de tela e o title leriam a tira)")
    for i, (final, q) in enumerate(extrair(html)):
        esperado = quadros(final, len(q) - 1 if len(q) - 1 in (PASSOS, PASSOS_DENSO) else PASSOS)
        if esperado is None:
            erros.append(f"contador {i}: '{final}' não devia ter tira (estático pelo contrato C1)")
            continue
        if q != esperado:
            prim = next((k for k in range(max(len(q), len(esperado))) if k >= len(q) or k >= len(esperado)
                         or q[k] != esperado[k]), None)
            erros.append(f"contador {i}: '{final}' quadro {prim}: motor {q[prim] if prim is not None and prim < len(q) else '∅'!r}"
                         f" × espelho {esperado[prim] if prim is not None and prim < len(esperado) else '∅'!r}")
            continue
        t, casas, milhar = analisar_nucleo(final)
        vals = [int(x.replace(".", "").replace(",", "")) for x in q]
        if vals[0] != 0 or any(b < a for a, b in zip(vals, vals[1:])) or vals[-1] != t:
            erros.append(f"contador {i}: '{final}' não é monótono de 0 ao final")
    return erros


# ---------------------------------------------------------------------------------------------------------------------
# CSS, JS e cascata (texto cru) — o mesmo texto vai para as folhas DAX (blocos) e para os geradores de PD/FT
# ---------------------------------------------------------------------------------------------------------------------
def css_denso_texto() -> str:
    """Regra extra das tabelas densas (C8): dentro de um contêiner .od12, a tira tem 13 quadros e anda em 12 passos (a
    segunda função de tempo é a do odT, que mostra a tira só durante a contagem e precisa continuar steps(1,end))."""
    n = PASSOS_DENSO
    return (f".od12 o-t{{transform:translateY(-{1.33 * n:g}em);transform:translateY(-{n}lh);"
            f"animation-timing-function:steps({n},end),steps(1,end)}}")


# Emenda de 28/09 (HCJ-03/04): o REPOUSO é o <o-v> no fluxo (o texto de hoje, sem transform) e a tira só existe durante
# a contagem. Por isso <o-t> e <o-v> andam SEMPRE em par: toda regra que liga, desliga ou muda a duração de um muda a
# do outro (senão o número some ou aparece dobrado). As páginas não escrevem essas regras à mão: usam css_parado,
# css_conta e css_duracao (bloco /* @contador:camada … */ nas folhas DAX; linhas @parado/@conta no gerador da PD).
ANIM_T = f"odConta {DURACAO} steps({PASSOS},end),odT {DURACAO} steps(1,end)"
ANIM_V = f"odV {DURACAO} steps(1,end)"


def css_parado(sel: str) -> str:
    """Contadores dentro de `sel` não contam (repouso = o texto final): ex. o verso de um card antes do hover."""
    return f"{sel} o-t,{sel} o-v{{animation:none}}"


def css_conta(sels: list[str]) -> str:
    """Contadores dentro de cada seletor de `sels` contam de novo (ex.: '.kc:hover .vs', '.kc:focus-within .vs'): o
    valor muda de 'none' para a animação e ela recomeça a cada aparição (C3)."""
    t = ",".join(f"{s} o-t" for s in sels)
    v = ",".join(f"{s} o-v" for s in sels)
    return f"{t}{{animation:{ANIM_T}}}{v}{{animation:{ANIM_V}}}"


def css_duracao(sel: str, dur: str) -> str:
    """Duração da contagem dentro de `sel` (ex.: o cartão de hover volta aos 600 ms mesmo com o '.tqv' do html)."""
    return f"{sel} o-t,{sel} o-v{{animation-duration:{dur}}}"


def css_herda(sel: str) -> str:
    """Os contadores dentro de `sel` começam junto com a entrada do próprio `sel`: herdam o animation-delay dele (posto
    inline pelo DAX, ex. a cascata das linhas da lista da Onde) e mostram o quadro 0 enquanto esperam (fill backwards:
    tira visível no quadro 0, valor oculto). Exceção ao C3 decidida pelo dono em 28/09 ('Sincronizar', F6-DES-01): sem
    animação, com movimento reduzido ou com '.oq' continua valendo o repouso = <o-v>."""
    return f"{sel} *{{animation-delay:inherit}}{sel} o-t,{sel} o-v{{animation-fill-mode:backwards}}"


def css_camada(parado: str = "", conta: list[str] | None = None, duracao: str = "", dur: str = DURACAO,
               herda: str = "") -> str:
    """As regras de página acima, entre /*contador*/ e /*fim-contador*/ (colapsar() as tira como o resto do contador)."""
    corpo = (css_parado(parado) if parado else "") + (css_conta(conta) if conta else "") \
        + (css_duracao(duracao, dur) if duracao else "") + (css_herda(herda) if herda else "")
    return CSS_ABRE + corpo + CSS_FECHA


def css_texto(denso: bool = False) -> str:
    """CSS do odômetro (C2, C6, C7), entre /*contador*/ e /*fim-contador*/. Sem aspas duplas, sem '//', sem '--'
    (portões dos geradores de PD/FT). `denso` acrescenta a regra das tabelas densas (C8).

    Repouso = o <o-v> no fluxo (Emenda HCJ-03/04): a tira <o-t> tem opacity:0 na base e fica visível só durante a
    contagem (odT, steps(1,end), 'from' opaco), e o <o-v> fica invisível só durante a contagem (odV, 'from' 0). Sem
    fill-mode: sem animação, com '.oq', com movimento reduzido ou sem suporte a 'lh' o que aparece é o <o-v>, o texto de
    hoje, sem transform e sem depender da altura de linha. O transform final (-24lh) continua no estilo base e o
    keyframe da tira só tem 'from', como na capa. Sem 'lh' (motores antigos) o contador desliga e a caixa vira texto
    comum (TTR-HCJ-08)."""
    n = PASSOS
    return (CSS_ABRE + "o-d{position:relative;display:inline-block;height:1.33em;height:1lh;overflow:hidden;vertical-align:top;"
            "font-variant-numeric:tabular-nums}"
            "@supports (overflow:clip){o-d{overflow-x:visible;overflow-y:clip;vertical-align:baseline}}"
            # o número parado tem os algarismos da fonte (F4, retorno de 28/10/2026): na Segoe UI Semibold o '1' tabular
            # é 0,153 em mais largo e "3,1%" parecia "3,1 %"; só a tira que conta fica tabular (não treme)
            f"o-v{{font-variant-numeric:normal;animation:{ANIM_V}}}"
            "o-t{position:absolute;right:0;top:0;white-space:pre;text-align:right;user-select:none;opacity:0;"
            f"transform:translateY(-{1.33 * n:g}em);transform:translateY(-{n}lh);"
            f"animation:{ANIM_T}}}"
            "@supports not (height:1lh){o-d{height:auto;overflow:visible;vertical-align:baseline}o-t{display:none}"
            "o-v{animation:none}}"
            "@keyframes odConta{from{transform:translateY(0)}}"
            "@keyframes odT{from{opacity:1}}"
            "@keyframes odV{from{opacity:0}}"
            ".tqv o-t,.tqv o-v{animation-duration:.3s}"
            "o-d.oq>o-t,o-d.oq>o-v{animation:none}"
            "o-n{white-space:nowrap}"
            "@media (prefers-reduced-motion:reduce){o-t,o-v{animation:none!important}}"
            + (css_denso_texto() if denso else "") + CSS_FECHA)


def _pct(x: float) -> str:
    s = f"{x:.3f}".rstrip("0").rstrip(".")
    return s


def entrada_texto(posicoes: list[str]) -> str:
    """Cascata dos tooltips (C5): posicoes[i] = seletor CSS da linha na posição i (ordem de leitura); cada posição tem
    o seu keyframe com trecho parado em .35 (sem animation-delay, sem fill-mode). '.tqv' no <html> = já visto."""
    regras, keyframes, todos = [], [], []
    for i, sel in enumerate(posicoes):
        if not sel:
            continue
        atraso = ENTRADA_PASSO_MS * i
        dur = ENTRADA_MS + atraso
        nome = f"tqE{i}"
        if atraso == 0:
            keyframes.append(f"@keyframes {nome}{{from{{opacity:.35}}}}")
        else:
            keyframes.append(f"@keyframes {nome}{{0%,{_pct(100 * atraso / dur)}%{{opacity:.35}}}}")
        regras.append(f"{sel}{{animation:{nome} {dur / 1000:g}s ease-out}}")
        todos.append(sel)
    lista = ",".join(todos)
    lista_v = ",".join(f".tqv {s}" for s in todos)
    return (CSS_ABRE + "".join(keyframes) + "".join(regras) + f"{lista_v}{{animation:none}}"
            f"@media (prefers-reduced-motion:reduce){{{lista}{{animation:none!important}}}}" + CSS_FECHA)


CONTINUA_MS = 600                    # C4 emendado (HCJ-02): DOM refeito a menos de 600 ms do início da contagem = a mesma
                                     # contagem, que continua de onde estava (não é "número igual", não é "já visto")


def js_texto(tooltip: bool = False) -> str:
    """C4 + C5: memória do texto final por contador (chave = entrada + posição) e .oq no que não mudou desde a
    atualização ANTERIOR do mesmo iframe; a memória é refeita a cada atualização (posição que não veio sai — achado da
    fase 3: um número que sumia e voltava não recontava). Com várias entradas (Granularity) cada <script> processa só os
    contadores ainda sem data-od, todos comparam com a mesma base e gravam na memória nova (__odn), e a troca acontece
    uma vez, depois de todos (setTimeout 0). 'tqv' no <html> quando a atualização anterior foi há menos de 1,5 s
    (tooltip passando de um ponto a outro: sem cascata).

    Emenda HCJ-02 (o visual 1.6.2 refaz o DOM a cada update): a decisão é tomada UMA vez por atualização (o primeiro
    script dela) e guardada em window. Se o DOM é refeito a menos de 600 ms do início da contagem (__odA), é a MESMA
    contagem: a base de comparação (__odB) e o 'já visto' (__odJ) são os do início, e os contadores cujo texto é o mesmo
    da atualização anterior continuam do ponto em que estavam (currentTime = decorrido), assim como a cascata tqE*; um
    número que mudou no meio recomeça do zero. `tooltip`: uma aparição nova do balão (sem 'já visto' nem continuação)
    zera a base, e todos os números contam junto com a cascata (nas páginas, a base é a memória anterior: número igual
    não reconta, C4). Sem '//', sem '--', todo comando com ';', try/catch; nunca calcula número (só compara textos do
    DAX e ajusta TEMPO de animação)."""
    base = "!W.__odJ?{}:(W.__odm||{})" if tooltip else "W.__odm||{}"
    from corrida import FIM_OCULTO_JS, REDE_JS
    return (f"<script>{MARCA_JS}(function(){{try{{var d=document,W=window,R=d.documentElement,t=Date.now();"
            f"{FIM_OCULTO_JS}if(d.visibilityState==='hidden'){{setTimeout(Fz,0);}}{REDE_JS}"
            "if(!W.__odP){W.__odP=1;"
            f"W.__odC=!!(W.__odA&&t-W.__odA<{CONTINUA_MS});"
            f"if(!W.__odC){{W.__odJ=!!(W.__odT&&t-W.__odT<{JANELA_VISTO_MS});W.__odB={base};W.__odA=t;}}"
            "setTimeout(function(){W.__odP=0;W.__odT=Date.now();W.__odm=W.__odn||{};W.__odn=null;},0);}"
            "var m=W.__odB||{},p=W.__odm||{},n=W.__odn||(W.__odn={}),dt=t-W.__odA;"
            "if(W.__odJ){R.classList.add('tqv');}else{R.classList.remove('tqv');}"
            "var E=d.querySelectorAll('.htmlViewerEntry');"
            "var grupos=E.length?Array.prototype.slice.call(E):[d];"
            "grupos.forEach(function(g,ie){var L=g.querySelectorAll('o-d');"
            "Array.prototype.forEach.call(L,function(o,io){if(o.getAttribute('data-od')){return;}"
            "o.setAttribute('data-od','1');var v=o.firstChild?o.firstChild.textContent:'',ch=ie+'.'+io;"
            "if(m[ch]===v){o.classList.add('oq');}"
            "else if(W.__odC&&p[ch]===v&&o.getAnimations){o.getAnimations({subtree:true}).forEach(function(a){"
            "a.currentTime=dt;});}"
            "n[ch]=v;});});"
            "if(W.__odC&&d.getAnimations){d.getAnimations().forEach(function(a){"
            "if(!/^od(Conta|T|V)$/.test(a.animationName||'')){a.currentTime=dt;}});}"
            "}catch(x){}})();</script>")


# ---------------------------------------------------------------------------------------------------------------------
# Blocos DAX
# ---------------------------------------------------------------------------------------------------------------------
def dax_literal(texto: str) -> str:
    """Texto cru → concatenação de literais DAX (sem aspa dupla, sem quebra de linha)."""
    if '"' in texto or "\n" in texto or "\r" in texto:
        raise ValueError(f"literal com aspa dupla ou quebra de linha: {texto[:60]!r}")
    pedacos, atual = [], ""
    for parte in re.split(r"(?<=[};])", texto):
        if len(atual) + len(parte) > 110 and atual:
            pedacos.append(atual)
            atual = ""
        atual += parte
    if atual:
        pedacos.append(atual)
    return pedacos


def _tabela_nome(passos: int) -> str:
    return "_odQ" if passos == PASSOS else f"_odQ{passos}"


def bloco_tabela(recuo: str = "", passos: int = PASSOS) -> str:
    pares = ", ".join(f"( {k}, {f} )" for k, f in enumerate(fracoes(passos)))
    if passos == PASSOS:
        nota = "a mesma tabela da capa"
    else:
        nota = f"tabela densa de {passos} passos (C8)"
    return (f"{recuo}/* odômetro (spec/contadores-animacoes.md C2): quadro k de 0 a {passos}, fração f do easing "
            f"1−(1−t)³ em milésimos inteiros, {nota} */\n"
            f"{recuo}VAR {_tabela_nome(passos)} =\n{recuo}    SELECTCOLUMNS ( {{ {pares} }}, \"@odk\", [Value1], \"@odf\", [Value2] )\n")


def _q(s: str) -> str:
    return '"' + s.replace('"', '""') + '"'


def _od_vars(n: str, nucleo: str, r: str) -> str:
    """As VARs comuns (a partir da VAR/expressão com o núcleo numérico): {n}S, {n}T, {n}Ok, {n}D, {n}M."""
    return (
        f"{r}VAR {n}S = SUBSTITUTE ( SUBSTITUTE ( {nucleo}, \".\", \"\" ), \",\", \"\" )\n"
        f"{r}VAR {n}T = IFERROR ( VALUE ( {n}S ), -1 )\n"
        f"{r}VAR {n}Ok = {{ok}}{n}T >= {T_MINIMO} && FORMAT ( {n}T, REPT ( \"0\", LEN ( {n}S ) ) ) = {n}S\n"
        f"{r}VAR {n}D = IF ( CONTAINSSTRING ( {nucleo}, \",\" ), LEN ( {nucleo} ) - SEARCH ( \",\", {nucleo}, 1, 0 ), 0 )\n"
        f"{r}VAR {n}M = IF ( CONTAINSSTRING ( {nucleo}, \".\" ), \"#,##0\", \"0\" ) & IF ( {n}D > 0, \".\" & REPT ( \"0\", {n}D ) )\n"
    )


def _od_tira(n: str, nucleo: str, r: str, passos: int = PASSOS, troca: str | None = None) -> str:
    """O trecho DAX da tira: "<o-d><o-v>" & núcleo & … & "</o-t></o-d>" (sem prefixo/sufixo). `troca` = VAR booleana:
    verdadeira, os quadros trocam ponto e vírgula (motor que ignora a cultura do FORMAT)."""
    q = f"FORMAT ( ROUND ( {n}T * [@odf] / 1000, 0 ) / POWER ( 10, {n}D ), {n}M, \"pt-BR\" )"
    if troca:
        u = "UNICHAR ( 57344 )"
        q = f"IF ( {troca}, SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( {q}, \",\", {u} ), \".\", \",\" ), {u}, \".\" ), {q} )"
    return (
        f"\"{ABRE_OD}\" & {nucleo} & \"{MEIO_OD}\"\n"
        f"{r}    & CONCATENATEX (\n"
        f"{r}        {_tabela_nome(passos)},\n"
        f"{r}        IF ( [@odk] = {passos}, {nucleo}, {q} ),\n"
        f"{r}        UNICHAR ( 10 ),\n"
        f"{r}        [@odk], ASC\n"
        f"{r}    )\n"
        f"{r}    & \"{FECHA_OD}\""
    )


def bloco_od_sufixos(nome: str, final: str, prefixo: str, sufixos: list[str], recuo: str = "",
                     passos: int = PASSOS) -> str:
    """Variante de bloco_od para unidade que depende do valor (R$ agregado: ' mil', ' mi' ou nada): o sufixo é lido do
    próprio texto final, e a tira fica na unidade do final (nunca troca no meio)."""
    n, r = nome, recuo
    lp = len(prefixo)
    alts = sorted(sufixos, key=len, reverse=True)
    ramos = ", ".join(f"RIGHT ( {final}, {len(x)} ) = {_q(x)}, {_q(x)}" for x in alts if x)
    padrao = _q(next((x for x in alts if not x), ""))
    cond = [f"LEN ( {final} ) > {lp} + LEN ( {n}X )"]
    if prefixo:
        cond.append(f"LEFT ( {final}, {lp} ) = {_q(prefixo)}")
    return (
        f"{r}VAR {n}X = SWITCH ( TRUE (), {ramos}, {padrao} )\n"
        f"{r}VAR {n}P = {' && '.join(cond)}\n"
        f"{r}VAR {n}N = IF ( {n}P, MID ( {final}, {lp + 1}, LEN ( {final} ) - {lp} - LEN ( {n}X ) ) )\n"
        + _od_vars(n, f"{n}N", r).replace("{ok}", f"{n}P && ")
        + f"{r}VAR {n}Od =\n"
        f"{r}    IF (\n"
        f"{r}        {n}Ok,\n"
        f"{r}        {_q(prefixo) + ' & ' if prefixo else ''}" + _od_tira(n, f"{n}N", r + "        ", passos) + f" & {n}X,\n"
        f"{r}        {final}\n"
        f"{r}    )\n"
    )


def bloco_prosa(nome: str, texto: str, recuo: str = "", passos: int = PASSOS) -> str:
    """VAR {nome}Html: o texto corrido (já escapado para HTML) com cada número marcado ⁅pré¦número¦pós⁆ trocado por
    <o-n>pré<o-d>…</o-d>pós</o-n> (o <o-n> segura a quebra de linha de hoje). Guarda: texto com '|' sai só limpo."""
    n, r = nome, recuo
    a, sp, f = _q(MARCA_ABRE), _q(MARCA_SEP), _q(MARCA_FECHA)
    limpo = f"SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( {texto}, {a}, \"\" ), {f}, \"\" ), {sp}, \"\" )"
    r3 = r + "            "
    return (
        f"{r}VAR {n}Q = SUBSTITUTE ( SUBSTITUTE ( {texto}, {a}, \"|\" ), {f}, \"|\" )\n"
        f"{r}VAR {n}Html =\n"
        f"{r}    IF (\n"
        f"{r}        CONTAINSSTRING ( {limpo}, \"|\" ),\n"
        f"{r}        {limpo},\n"
        f"{r}        CONCATENATEX (\n"
        f"{r}            GENERATESERIES ( 1, PATHLENGTH ( {n}Q ) ),\n"
        f"{r3}VAR {n}sg = PATHITEM ( {n}Q, [Value] )\n"
        f"{r3}VAR {n}i1 = SEARCH ( {sp}, {n}sg, 1, 0 )\n"
        f"{r3}VAR {n}i2 = IF ( {n}i1 > 0, SEARCH ( {sp}, {n}sg, {n}i1 + 1, 0 ), 0 )\n"
        f"{r3}VAR {n}pre = IF ( {n}i2 > 0, LEFT ( {n}sg, {n}i1 - 1 ), \"\" )\n"
        f"{r3}VAR {n}num = IF ( {n}i2 > 0, MID ( {n}sg, {n}i1 + 1, {n}i2 - {n}i1 - 1 ), SUBSTITUTE ( {n}sg, {sp}, \"\" ) )\n"
        f"{r3}VAR {n}suf = IF ( {n}i2 > 0, MID ( {n}sg, {n}i2 + 1, LEN ( {n}sg ) ), \"\" )\n"
        + _od_vars(n, f"{n}num", r3).replace("{ok}", "")
        + f"{r3}RETURN\n"
        f"{r3}    IF (\n"
        f"{r3}        ISODD ( [Value] ),\n"
        f"{r3}        {n}sg,\n"
        f"{r3}        IF (\n"
        f"{r3}            {n}Ok,\n"
        f"{r3}            \"<o-n>\" & {n}pre & " + _od_tira(n, f"{n}num", r3 + "            ", passos)
        + f" & {n}suf & \"</o-n>\",\n"
        f"{r3}            {n}pre & {n}num & {n}suf\n"
        f"{r3}        )\n"
        f"{r3}    ),\n"
        f"{r}            \"\",\n"
        f"{r}            [Value], ASC\n"
        f"{r}        )\n"
        f"{r}    )\n"
    )


def dax_limpar_marcas(expr: str) -> str:
    """Expressão DAX do texto sem as marcas (para o ALT e para qualquer outro consumidor do texto marcado)."""
    return (f"SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( {expr}, {_q(MARCA_ABRE)}, \"\" ), {_q(MARCA_FECHA)}, \"\" ), "
            f"{_q(MARCA_SEP)}, \"\" )")


def dax_marca(pre: str, expr_numero: str, pos: str = "") -> str:
    """Trecho DAX que marca um número no texto corrido: "⁅pré¦" & <número> & "¦pós⁆" (pré e pós = a pontuação colada,
    sem espaço, que precisa ficar na mesma linha do número)."""
    return f"{_q(MARCA_ABRE + pre + MARCA_SEP)} & {expr_numero} & {_q(MARCA_SEP + pos + MARCA_FECHA)}"


# ---------------------------------------------------------------------------------------------------------------------
# F4 (28/10/2026): valor marcado na marcação e uma conversão por medida. Em vez de um bloco @contador:od por número (25
# quadros escritos à mão em cada helper), o desenho envolve o TEXTO do valor, no ponto em que ele entra no HTML, com
# marca(): ⁅texto⁆ (ou ⁅pré¦número¦pós⁆, como na prosa). No fim da medida, envolver_marcas() passa o HTML inteiro por
# bloco_marcas(): cada marca vira <o-n>pré<o-d>…</o-d>pós</o-n> com os mesmos quadros do bloco od (tabela _odQ,
# aritmética inteira; o texto final no fluxo). O núcleo é o primeiro número do texto (dígitos, '.' e ','; o '.' ou ','
# do fim de frase fica fora), então "IDC 0,97", "−R$ 1,89 mi", "atraso 1,4 mês" e "89,6%" contam só o número. Sem
# funções PATH: a k-ésima marca sai de SUBSTITUTE ( …, k ) + FIND, então o '|' do HTML (data-rk, JS) não atrapalha.
# Nunca marque texto que vá para atributo (title, aria-label, data-*).
# ---------------------------------------------------------------------------------------------------------------------
MARCA_POS = ""                  # caractere de uso privado: a k-ésima marca é achada trocando só ela por ele


def marca(expr: str) -> str:
    """DAX: o texto `expr` (já formatado e escapado) marcado para a conversão da medida: "⁅" & expr & "⁆"."""
    return f"{_q(MARCA_ABRE)} & {expr} & {_q(MARCA_FECHA)}"


def bloco_marcas(nome: str, texto: str, recuo: str = "", passos: int = PASSOS) -> str:
    """VAR {nome}Html: o HTML `texto` com cada ⁅…⁆ trocado pelo odômetro do primeiro número dentro da marca (ou do
    número entre ¦, na forma da prosa); marca sem número, ou com T < 2, sai só sem as marcas. Precisa da tabela
    {_tabela_nome(passos)} (bloco_tabela) antes. Todo MID/LEFT tem os argumentos presos (MAX): o DAX não para no
    primeiro lado falso de '&&' nem sempre adia o ramo do IF, e marca sem algarismo ("—", vazio: tooltip sem obra no
    contexto, 29/10/2026) chegava a MID na posição 0."""
    n, r = nome, recuo
    a, f, sp, u = _q(MARCA_ABRE), _q(MARCA_FECHA), _q(MARCA_SEP), "UNICHAR ( 57344 )"
    r3 = r + "            "
    dig = '"0123456789"'
    return (
        f"{r}VAR {n}K = LEN ( {texto} ) - LEN ( SUBSTITUTE ( {texto}, {a}, \"\" ) )\n"
        f"{r}/* o motor que ignora a cultura do FORMAT devolve 1.5: aí o núcleo troca ponto e vírgula (decimal sempre vírgula) */\n"
        f"{r}VAR {n}En = FORMAT ( 1.5, \"0.0\", \"pt-BR\" ) <> \"1,5\"\n"
        f"{r}VAR {n}Html =\n"
        f"{r}    IF (\n"
        f"{r}        {n}K = 0,\n"
        f"{r}        {texto},\n"
        f"{r}        CONCATENATEX (\n"
        f"{r}            GENERATESERIES ( 1, {n}K ),\n"
        # {n}j, não {n}k: o DAX não diferencia caixa, e {n}k seria a mesma variável que {n}K (o total de marcas); com
        # ela, toda marca virava "a última" e repetia o resto do HTML
        f"{r3}VAR {n}j = [Value]\n"
        f"{r3}VAR {n}a = FIND ( {u}, SUBSTITUTE ( {texto}, {a}, {u}, {n}j ) )\n"
        f"{r3}VAR {n}f = FIND ( {u}, SUBSTITUTE ( {texto}, {f}, {u}, {n}j ) )\n"
        f"{r3}VAR {n}f0 = IF ( {n}j = 1, 0, FIND ( {u}, SUBSTITUTE ( {texto}, {f}, {u}, {n}j - 1 ) ) )\n"
        f"{r3}VAR {n}antes = MID ( {texto}, {n}f0 + 1, MAX ( 0, {n}a - {n}f0 - 1 ) )\n"
        f"{r3}VAR {n}depois = IF ( {n}j = {n}K, MID ( {texto}, {n}f + 1, LEN ( {texto} ) ), \"\" )\n"
        f"{r3}VAR {n}sg = MID ( {texto}, {n}a + 1, MAX ( 0, {n}f - {n}a - 1 ) )\n"
        f"{r3}VAR {n}i1 = SEARCH ( {sp}, {n}sg, 1, 0 )\n"
        f"{r3}VAR {n}i2 = IF ( {n}i1 > 0, SEARCH ( {sp}, {n}sg, {n}i1 + 1, 0 ), 0 )\n"
        f"{r3}VAR {n}c = LEN ( {n}sg )\n"
        f"{r3}VAR {n}p0 = MINX ( FILTER ( GENERATESERIES ( 1, MAX ( 1, {n}c ) ), CONTAINSSTRING ( {dig}, MID ( {n}sg, [Value], 1 ) ) && {n}c > 0 ), [Value] ) /* lista */\n"
        f"{r3}VAR {n}p1 = MINX ( FILTER ( GENERATESERIES ( MAX ( 1, {n}p0 ), {n}c + 1 ), [Value] > {n}c || NOT CONTAINSSTRING ( \"0123456789.,\", MID ( {n}sg, [Value], 1 ) ) ), [Value] ) /* lista */\n"
        f"{r3}VAR {n}p2 = IF ( {n}p1 - 1 > {n}p0 && CONTAINSSTRING ( \".,\", MID ( {n}sg, MAX ( 1, {n}p1 - 1 ), 1 ) ), {n}p1 - 1, {n}p1 )\n"
        f"{r3}VAR {n}pre = IF ( {n}i2 > 0, LEFT ( {n}sg, MAX ( 0, {n}i1 - 1 ) ), IF ( ISBLANK ( {n}p0 ), {n}sg, LEFT ( {n}sg, MAX ( 0, {n}p0 - 1 ) ) ) )\n"
        f"{r3}VAR {n}num0 = IF ( {n}i2 > 0, MID ( {n}sg, {n}i1 + 1, MAX ( 0, {n}i2 - {n}i1 - 1 ) ), IF ( ISBLANK ( {n}p0 ), \"\", MID ( {n}sg, MAX ( 1, {n}p0 ), MAX ( 0, {n}p2 - {n}p0 ) ) ) )\n"
        f"{r3}VAR {n}num = IF ( {n}En, SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( {n}num0, \",\", {u} ), \".\", \",\" ), {u}, \".\" ), {n}num0 )\n"
        f"{r3}VAR {n}suf = IF ( {n}i2 > 0, MID ( {n}sg, {n}i2 + 1, {n}c ), IF ( ISBLANK ( {n}p0 ), \"\", MID ( {n}sg, MAX ( 1, {n}p2 ), {n}c ) ) )\n"
        + _od_vars(n, f"{n}num", r3).replace("{ok}", f"{n}num <> \"\" && ")
        + f"{r3}RETURN\n"
        f"{r3}    {n}antes\n"
        f"{r3}        & IF (\n"
        f"{r3}            {n}Ok,\n"
        f"{r3}            \"<o-n>\" & {n}pre & " + _od_tira(n, f"{n}num", r3 + "            ", passos, f"{n}En")
        + f" & {n}suf & \"</o-n>\",\n"
        f"{r3}            {n}pre & {n}num & {n}suf\n"
        f"{r3}        )\n"
        f"{r3}        & {n}depois,\n"
        f"{r}            \"\",\n"
        f"{r}            [Value], ASC\n"
        f"{r}        )\n"
        f"{r}    )\n"
    )


def envolver_marcas(dax: str, passos: int = PASSOS) -> str:
    """A medida de desenho com as marcas ⁅…⁆ convertidas: o RETURN do nível de cima vira VAR _saidaHtml e a medida
    devolve o HTML convertido (bloco_marcas). Sem marca na medida, devolve o DAX como veio."""
    if MARCA_ABRE not in dax:
        return dax
    linhas = dax.split("\n")
    i = max(k for k, l in enumerate(linhas) if l == "RETURN")
    corpo = linhas[i + 1:]
    tab = "" if f"VAR {_tabela_nome(passos)} =" in dax else bloco_tabela("", passos)
    return "\n".join(linhas[:i] + ["VAR _saidaHtml ="] + corpo) + "\n" + tab + bloco_marcas("_mc", "_saidaHtml", "", passos) \
        + "RETURN\n    _mcHtml"


def html_marcas(texto: str, passos: int = PASSOS) -> str:
    """Espelho Python de bloco_marcas (prova)."""
    out, i = [], 0
    while True:
        a = texto.find(MARCA_ABRE, i)
        if a < 0:
            out.append(texto[i:])
            break
        f = texto.find(MARCA_FECHA, a)
        out.append(texto[i:a])
        sg = texto[a + 1:f]
        if MARCA_SEP in sg and sg.count(MARCA_SEP) >= 2:
            i1 = sg.find(MARCA_SEP)
            i2 = sg.find(MARCA_SEP, i1 + 1)
            pre, num, suf = sg[:i1], sg[i1 + 1:i2], sg[i2 + 1:]
        else:
            m = re.search(r"\d[\d.,]*", sg)
            if not m:
                pre, num, suf = sg, "", ""
            else:
                num = m.group(0)
                if len(num) > 1 and num[-1] in ".,":
                    num = num[:-1]
                pre, suf = sg[:m.start()], sg[m.start() + len(num):]
        q = quadros(num, passos) if num else None
        out.append(pre + num + suf if q is None else
                   "<o-n>" + pre + ABRE_OD + num + MEIO_OD + SEP_QUADRO.join(q) + FECHA_OD + suf + "</o-n>")
        i = f + 1
    return "".join(out)


def bloco_od(nome: str, final: str, prefixo: str = "", sufixo: str = "", recuo: str = "", passos: int = PASSOS) -> str:
    """VARs de um número: {nome}Od = prefixo & <o-d>…</o-d> & sufixo quando o núcleo é número puro com T ≥ 2; senão o
    próprio texto final (estático). `final` é a VAR (já escapada para HTML) com o texto canônico de hoje."""
    n = nome
    lp, ls = len(prefixo), len(sufixo)
    cond = [f"LEN ( {final} ) > {lp + ls}"]
    if prefixo:
        cond.append(f"LEFT ( {final}, {lp} ) = {_q(prefixo)}")
    if sufixo:
        cond.append(f"RIGHT ( {final}, {ls} ) = {_q(sufixo)}")
    ok_pre = " && ".join(cond)
    nucleo = (f"MID ( {final}, {lp + 1}, LEN ( {final} ) - {lp + ls} )" if (prefixo or sufixo) else final)
    r = recuo
    return (
        f"{r}VAR {n}P = {ok_pre}\n"
        f"{r}VAR {n}N = IF ( {n}P, {nucleo} )\n"
        f"{r}VAR {n}S = SUBSTITUTE ( SUBSTITUTE ( {n}N, \".\", \"\" ), \",\", \"\" )\n"
        f"{r}VAR {n}T = IFERROR ( VALUE ( {n}S ), -1 )\n"
        f"{r}VAR {n}Ok = {n}P && {n}T >= {T_MINIMO} && FORMAT ( {n}T, REPT ( \"0\", LEN ( {n}S ) ) ) = {n}S\n"
        f"{r}VAR {n}D = IF ( CONTAINSSTRING ( {n}N, \",\" ), LEN ( {n}N ) - SEARCH ( \",\", {n}N ), 0 )\n"
        f"{r}VAR {n}M = IF ( CONTAINSSTRING ( {n}N, \".\" ), \"#,##0\", \"0\" ) & IF ( {n}D > 0, \".\" & REPT ( \"0\", {n}D ) )\n"
        f"{r}VAR {n}Od =\n"
        f"{r}    IF (\n"
        f"{r}        {n}Ok,\n"
        f"{r}        {_q(prefixo) + ' & ' if prefixo else ''}\"{ABRE_OD}\" & {n}N & \"{MEIO_OD}\"\n"
        f"{r}            & CONCATENATEX (\n"
        f"{r}                {_tabela_nome(passos)},\n"
        f"{r}                IF ( [@odk] = {passos}, {n}N, FORMAT ( ROUND ( {n}T * [@odf] / 1000, 0 ) / POWER ( 10, {n}D ), {n}M, \"pt-BR\" ) ),\n"
        f"{r}                UNICHAR ( 10 ),\n"
        f"{r}                [@odk], ASC\n"
        f"{r}            )\n"
        f"{r}            & \"{FECHA_OD}\"{' & ' + _q(sufixo) if sufixo else ''},\n"
        f"{r}        {final}\n"
        f"{r}    )\n"
    )


def bloco_deneb(final: str, prefixo: str = "", sufixo: str = "", nome: str = "_odQuadros", recuo: str = "") -> str:
    """VAR {nome} = os 25 textos completos separados por '|' (quadro 24 = o final), ou BLANK (rótulo estático)."""
    lp, ls = len(prefixo), len(sufixo)
    cond = [f"LEN ( {final} ) > {lp + ls}"]
    if prefixo:
        cond.append(f"LEFT ( {final}, {lp} ) = {_q(prefixo)}")
    if sufixo:
        cond.append(f"RIGHT ( {final}, {ls} ) = {_q(sufixo)}")
    nucleo = (f"MID ( {final}, {lp + 1}, LEN ( {final} ) - {lp + ls} )" if (prefixo or sufixo) else final)
    n, r = nome, recuo
    pre = _q(prefixo) + " & " if prefixo else ""
    suf = " & " + _q(sufixo) if sufixo else ""
    return (
        f"{r}VAR {n}P = {' && '.join(cond)}\n"
        f"{r}VAR {n}N = IF ( {n}P, {nucleo} )\n"
        f"{r}VAR {n}S = SUBSTITUTE ( SUBSTITUTE ( {n}N, \".\", \"\" ), \",\", \"\" )\n"
        f"{r}VAR {n}T = IFERROR ( VALUE ( {n}S ), -1 )\n"
        f"{r}VAR {n}Ok = {n}P && {n}T >= {T_MINIMO} && FORMAT ( {n}T, REPT ( \"0\", LEN ( {n}S ) ) ) = {n}S\n"
        f"{r}VAR {n}D = IF ( CONTAINSSTRING ( {n}N, \",\" ), LEN ( {n}N ) - SEARCH ( \",\", {n}N ), 0 )\n"
        f"{r}VAR {n}M = IF ( CONTAINSSTRING ( {n}N, \".\" ), \"#,##0\", \"0\" ) & IF ( {n}D > 0, \".\" & REPT ( \"0\", {n}D ) )\n"
        f"{r}VAR {n} =\n"
        f"{r}    IF (\n"
        f"{r}        {n}Ok,\n"
        f"{r}        CONCATENATEX (\n"
        f"{r}            _odQ,\n"
        f"{r}            IF ( [@odk] = {PASSOS}, {final}, {pre}FORMAT ( ROUND ( {n}T * [@odf] / 1000, 0 ) / POWER ( 10, {n}D ), {n}M, \"pt-BR\" ){suf} ),\n"
        f"{r}            \"{SEP_DENEB}\",\n"
        f"{r}            [@odk], ASC\n"
        f"{r}        )\n"
        f"{r}    )\n"
    )


def bloco_css(recuo: str = "    ", denso: bool = False) -> str:
    return "".join(f"{recuo}& \"{p}\"\n" for p in dax_literal(css_texto(denso)))


def bloco_entrada(posicoes: list[str], recuo: str = "    ") -> str:
    return "".join(f"{recuo}& \"{p}\"\n" for p in dax_literal(entrada_texto(posicoes)))


def bloco_camada(p: dict[str, str], recuo: str = "    ") -> str:
    """Regras de página que ligam/desligam/mudam a duração do contador (<o-t> e <o-v> sempre em par): parâmetros
    parado='<sel>', conta='<sel1>|<sel2>', duracao='<sel>' [dur='.6s']."""
    texto = css_camada(p.get("parado", ""), [x for x in p.get("conta", "").split("|") if x] or None,
                       p.get("duracao", ""), p.get("dur", DURACAO), p.get("herda", ""))
    return "".join(f"{recuo}& \"{x}\"\n" for x in dax_literal(texto))


def bloco_js(recuo: str = "", tooltip: bool = False) -> str:
    pedacos = dax_literal(js_texto(tooltip))
    corpo = f"\n{recuo}        & ".join(f"\"{p}\"" for p in pedacos)
    return f"{recuo}VAR _odJs =\n{recuo}    {corpo}\n"


# ---------------------------------------------------------------------------------------------------------------------
# Marcadores nos .dax
# ---------------------------------------------------------------------------------------------------------------------
_RE_ABRE = re.compile(r"^(?P<recuo>[ \t]*)/\* @contador:(?P<tipo>tabela|od|css|entrada|js|deneb|prosa|camada)(?P<params>[^*]*)\*/[ \t]*\n",
                      re.M)
_RE_FECHA = re.compile(r"^[ \t]*/\* @contador:fim \*/[ \t]*\n?", re.M)
_RE_PARAM = re.compile(r"(\w+)=('(?:[^']*)'|\"(?:[^\"]*)\"|\S+)")


def _params(txt: str) -> dict[str, str]:
    out = {}
    for k, v in _RE_PARAM.findall(txt):
        if v[:1] in "'\"" and v[-1:] == v[:1]:
            v = v[1:-1]
        out[k] = v
    return out


def gerar_bloco(tipo: str, p: dict[str, str], recuo: str) -> str:
    passos = int(p.get("passos", PASSOS))
    if tipo == "tabela":
        return bloco_tabela(recuo, passos)
    if tipo == "od":
        if "sufixos" in p:
            return bloco_od_sufixos(p["nome"], p["final"], p.get("prefixo", ""), p["sufixos"].split("|"), recuo,
                                    passos)
        return bloco_od(p["nome"], p["final"], p.get("prefixo", ""), p.get("sufixo", ""), recuo, passos)
    if tipo == "prosa":
        return bloco_prosa(p["nome"], p["texto"], recuo, passos)
    if tipo == "css":
        return bloco_css(recuo or "    ", bool(p.get("denso")))
    if tipo == "entrada":
        pos = [p.get(f"sel{i}", "") for i in range(12)]
        while pos and not pos[-1]:
            pos.pop()
        return bloco_entrada(pos, recuo or "    ")
    if tipo == "js":
        return bloco_js(recuo, bool(p.get("tooltip")))
    if tipo == "camada":
        return bloco_camada(p, recuo or "    ")
    if tipo == "deneb":
        return bloco_deneb(p["final"], p.get("prefixo", ""), p.get("sufixo", ""), p.get("nome", "_odQuadros"), recuo)
    raise ValueError(tipo)


def regenerar(texto: str) -> tuple[str, list[tuple[str, dict]]]:
    """Refaz o conteúdo de todos os blocos; devolve (texto novo, [(tipo, params)])."""
    saida, pos, blocos = [], 0, []
    for m in _RE_ABRE.finditer(texto):
        if m.start() < pos:
            continue
        fim = _RE_FECHA.search(texto, m.end())
        if not fim:
            raise ValueError(f"bloco @contador:{m.group('tipo')} sem /* @contador:fim */")
        p = _params(m.group("params"))
        blocos.append((m.group("tipo"), p))
        saida.append(texto[pos:m.end()])
        saida.append(gerar_bloco(m.group("tipo"), p, m.group("recuo")))
        saida.append(texto[fim.start():fim.end()])
        pos = fim.end()
    saida.append(texto[pos:])
    return "".join(saida), blocos


def arquivos_com_blocos(pastas: list[Path] | None = None) -> list[Path]:
    alvo = pastas or [DAX]
    out = []
    for pasta in alvo:
        for arq in sorted(pasta.rglob("*.dax")) if pasta.is_dir() else [pasta]:
            if "/* @contador:" in arq.read_text(encoding="utf-8"):
                out.append(arq)
    return out


_RE_REGRA = re.compile(r"([^{}]+)\{([^{}]*)\}")
_RE_SEM_LH = re.compile(r"@supports not \(height:1lh\)\{(?:[^{}]*\{[^{}]*\})*\}")


def _tipo_anim(decl: str) -> str | None:
    d = decl.replace(" ", "")
    if re.search(r"(^|;)animation:none", d):
        return "none"
    m = re.search(r"(^|;)animation-duration:([^;!]+)", d)
    if m:
        return "dur=" + m.group(2)
    if re.search(r"(^|;)animation:", d):
        return "anim"
    return None


def checar_pares(css: str) -> list[str]:
    """Emenda HCJ-03/04: toda regra que liga, desliga ou muda a duração da animação de <o-t> tem a gêmea em <o-v> com o
    mesmo prefixo de seletor, e vice-versa (senão o número some ou aparece dobrado durante a contagem). O bloco
    '@supports not (height:1lh)' (contador desligado: tira display:none) fica de fora."""
    css = _RE_SEM_LH.sub("", re.sub(r"/\*.*?\*/", "", css, flags=re.S))
    lados: dict[str, set] = {"o-t": set(), "o-v": set()}
    for m in _RE_REGRA.finditer(css):
        tipo = _tipo_anim(m.group(2))
        if not tipo:
            continue
        for sel in m.group(1).split(","):
            sel = sel.strip()
            for alvo in ("o-t", "o-v"):
                if re.search(r"(^|[\s>])" + alvo + r"$", sel):
                    lados[alvo].add((sel[: -len(alvo)].strip(), "anim" if tipo == "anim" else tipo))
    erros = []
    for a, b in (("o-t", "o-v"), ("o-v", "o-t")):
        for pref, tipo in sorted(lados[a] - lados[b]):
            erros.append(f"regra de {a} sem a gêmea em {b}: '{pref} {a}' ({tipo})")
    return erros


def _literais_dax(texto: str) -> str:
    """O conteúdo dos literais de texto de um .dax, concatenados (a folha/HTML como o motor emitiria, sem as partes
    calculadas)."""
    semcom = re.sub(r"/\*.*?\*/", " ", texto, flags=re.S)
    return "".join(x.replace('""', '"') for x in re.findall(r'"((?:[^"]|"")*)"', semcom))


# ---------------------------------------------------------------------------------------------------------------------
# Autoteste (--lint)
# ---------------------------------------------------------------------------------------------------------------------
def lint() -> list[str]:
    erros = []
    # tabela da capa do painel de referência (fonte da técnica): milésimos de 1 − (1 − k/24)³, k = 0..24
    if FRACOES != [round(1000 * (1 - (1 - k / 24) ** 3)) for k in range(25)] or PASSOS != 24:
        erros.append("frações/passos diferentes da fórmula da capa")
    for rotulo, txt in (("css", css_texto()), ("js", js_texto()), ("js tooltip", js_texto(True)),
                        ("entrada", entrada_texto([".a", ".b", ".c"])),
                        ("css+entrada", css_texto(True) + entrada_texto([".a", ".b"]) + css_texto())):
        if '"' in txt:
            erros.append(f"{rotulo}: aspas duplas")
        if "//" in txt:
            erros.append(f"{rotulo}: '//'")
        if "--" in txt:
            erros.append(f"{rotulo}: '--'")
        if re.search(r"height\s*:\s*100%", txt):
            erros.append(f"{rotulo}: height:100%")
    if shutil.which("node"):
        for tt in (False, True):
            js = js_texto(tt)[len("<script>"):-len("</script>")]
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
                fh.write(js)
                caminho = fh.name
            r = subprocess.run(["node", "--check", caminho], capture_output=True, text=True)
            Path(caminho).unlink(missing_ok=True)
            if r.returncode:
                erros.append(f"js{' tooltip' if tt else ''}: node --check: {r.stderr.strip()[:200]}")
    # espelho: casos de fronteira (o DAX faz o mesmo; a prova no motor compara)
    casos = {"72,5": 25, "5.205": 25, "0,45": 25, "1.094,8": 25, "0": None, "1": None, "0,1": None, "0,2": 25,
             "&lt; 0,1": None, "—": None, "": None, "12a": None}
    for nucleo, n in casos.items():
        q = quadros(nucleo)
        if (q is None) != (n is None) or (q is not None and (len(q) != n or q[-1] != nucleo or q[-2] != nucleo)):
            erros.append(f"espelho: caso {nucleo!r} → {q}")
    q12 = quadros("72,5", PASSOS_DENSO)
    if not q12 or len(q12) != 13 or q12[-1] != "72,5" or FRACOES_DENSO[-1] != 1000:
        erros.append(f"espelho denso: {q12} {FRACOES_DENSO}")
    for rotulo, txt in (("css", css_texto()), ("css denso", css_texto(True)),
                        ("camada", css_camada(".a", [".b:hover .a", ".b:focus-within .a"], ".c", ".6s"))):
        erros += [f"{rotulo}: {e}" for e in checar_pares(txt)]
    if not checar_pares("o-t{animation:none}"):
        erros.append("checar_pares não acusou uma regra de o-t sem a gêmea")
    for arq in arquivos_com_blocos() + sorted(DAX.rglob("CSS *.dax")):
        texto = arq.read_text(encoding="utf-8")
        if "o-t" in texto:
            erros += [f"{arq.relative_to(RAIZ)}: {e}" for e in checar_pares(_literais_dax(texto))]
    if colapsar("<p class='x od12'>1</p><p class='od12'>2</p><p class='od12 y'>3</p>") != \
            "<p class='x'>1</p><p>2</p><p class='y'>3</p>":
        erros.append("colapsar: classe od12")
    if colapsar("<style>/*contador*/o-d{}/*fim-contador*/a</style>") != "<style>a</style>":
        erros.append("colapsar: fechamento antigo sem espaço")
    if not conferir("<b title='<o-d>'>x</b>"):
        erros.append("conferir: contador em atributo não acusado")
    h = html_od("R$ 2,78 mi", "R$ ", " mi")
    if colapsar(h) != "R$ 2,78 mi" or conferir(h):
        erros.append("espelho: colapsar/conferir de 'R$ 2,78 mi'")
    if html_od("—", "R$ ", " mi") != "—" or html_od("&lt; 0,1%", "", "%") != "&lt; 0,1%":
        erros.append("espelho: estáticos")
    return erros


# ---------------------------------------------------------------------------------------------------------------------
def _backup(arquivos: list[Path]) -> Path:
    BACKUPS.mkdir(exist_ok=True)
    destino = BACKUPS / f"contador-{datetime.datetime.now():%Y%m%d-%H%M%S}.zip"
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        for a in arquivos:
            z.write(a, a.relative_to(RAIZ).as_posix())
    return destino


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("arquivos", nargs="*", type=Path)
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--conferir", action="store_true")
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--lint", action="store_true")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    if a.lint:
        erros = lint()
        print("\n".join("ERRO " + e for e in erros) or "lint ok: frações = capa; css/js/entrada sem aspas, '//', '--'; "
              "node --check; espelho nas fronteiras; pares o-t/o-v em todas as folhas; colapsar/conferir")
        return 1 if erros else 0
    arqs = [p if p.is_absolute() else (RAIZ / p) for p in a.arquivos] or arquivos_com_blocos()
    velhos = []
    for arq in arqs:
        atual = arq.read_text(encoding="utf-8")
        novo, blocos = regenerar(atual)
        if a.listar:
            print(f"{arq.relative_to(RAIZ)}: " + ", ".join(t + (f"({p.get('nome', '')})" if t == 'od' else '')
                                                          for t, p in blocos))
        if novo != atual:
            velhos.append((arq, novo))
    if a.conferir or not a.aplicar:
        for arq, _ in velhos:
            print(f"DIFERENTE {arq.relative_to(RAIZ)}")
        print(f"{len(arqs)} arquivo(s) com blocos; {len(velhos)} a regravar")
        return 1 if (a.conferir and velhos) else 0
    if velhos:
        z = _backup([arq for arq, _ in velhos])
        for arq, novo in velhos:
            arq.write_text(novo, encoding="utf-8", newline="\n")
            print(f"regravado {arq.relative_to(RAIZ)}")
        print(f"backup: {z.relative_to(RAIZ)}")
    else:
        print("nada a regravar")
    return 0


if __name__ == "__main__":
    sys.exit(main())

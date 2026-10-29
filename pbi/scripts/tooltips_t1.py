#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tooltips_t1 — contas e desenho dos tooltips de página da Tela 01 (pbi/dax/T1/Tooltips/**).

Figma: seção Interações · Tela 01 (290:720) e redesenho v2 (379:788): Tooltip · T1 · v2 · Obra 389:1618, Indicador
390:1528, Mês 390:1741. Linguagem: docs/06-interacoes-spec.md §1.6 e §3. Páginas de 560 de largura (paginas/tt_t1.py);
um HTML Content do tamanho da página desenha o cartão (cabeçalho preto de 72, corpo branco em fluxo, pé preso à base).

F3 (28/10/2026, docs/08 §5):
- Obra: os 9 itens da nota com o valor, a faixa atingida e os pontos de possíveis (chip de item do desenho_comum); a
  nota mês a mês (pendente tracejado com os pontos obtidos); no pé, o que mudou desde o mês anterior (status e nota,
  só entre notas completas) ou, se pendente, quantos itens faltam.
- Dimensão da nota (eixo dItemNota[Dimensao], era o indicador): as faixas dos itens da dimensão (Nota · item ·
  faixas), obra por obra com o X de cada item e os pontos da dimensão, e no pé "como ler" (no caixa, as justificativas
  da planilha, regra da Análise Crítica).
- Mês: as obras em cada um dos quatro estados (crítico, atenção, estável, pendente) e quem entrou, saiu ou abriu em
  crítico pela regra nova (só conta quando os dois meses têm nota completa; ir de pendente a crítico é "abrir").

Listas de uma obra por linha: até LISTA_MAX obras todas aparecem; de LISTA_MAX + 1 em diante, as LISTA_MOSTRA primeiras
e a linha "e mais N obras" (N é conta). O pé fica preso à base do cartão (.pe).

    python -X utf8 pbi/scripts/tooltips_t1.py
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import contador as C  # noqa: E402
import tooltip_lib as TL  # noqa: E402
import desenho_comum as DC  # noqa: E402
import desenho_projeto as D  # noqa: E402
from contas_lib_projeto import Medida, gravar  # noqa: E402
from desenho_comum import dax_lit  # noqa: E402
import justificativas_rodape as R  # noqa: E402

RAIZ = AQUI.parent
GERADO = "pbi/scripts/tooltips_t1.py"
F = "fAnaliseCritica"
MEDIDAS: list[Medida] = []
PTS = DC.FMT_PTS

# Retiradas do modelo em 08/10/2026 (auditoria: dependencias-pos-telas.json e dependencias-final.json, chave mortas) e
# na Fase 2 da régua antiga (13/10/2026: régua antiga — status por indicador, mobilização, sinais — fora da tela). Fora da
# gravação: o gerador não escreve o nome e apaga o .dax que tinha escrito antes. Para reativar, tire o nome do conjunto.
RETIRADAS = {
    "Comum · CSS tooltip",
    "Obras com análise · no histórico",
    # Fase 2 da régua antiga
    "Criticidade · status · mês anterior",
    # integração da Fase 2 (agente base): régua antiga por indicador; nenhuma tela lê mais (a T2 também saiu delas)
    "Indicador · status · mês anterior",
    "Indicador · status · mês anterior · ref",
    "Indicador · valor · mês anterior",
    "Indicador · valor · mês anterior · ref",
    "Variação · sequência · início · ref",           # integração da Fase 2: nenhum visual lê mais
    "Criticidade · indicador que mudou de faixa",
    "T1 · Tooltip obra · sinais que mudaram de faixa",
    "T1 · Tooltip obra · sinais que mudaram de faixa (lista)",
    "T1 · Tooltip obra · todos os sinais estáveis",
}
# (as Indicador · status/valor · mês anterior, e · ref, saíram na integração da Fase 2; as definições, na auditoria)

CONTAS = r"T1 Visão geral\Tooltips\Contas"
DES = r"T1 Visão geral\Tooltips"


def conta(nome, formato, descricao, dax, oraculo=""):
    MEDIDAS.append(Medida(nome, CONTAS, formato, descricao, dax, oraculo))


def desenho(nome, descricao, dax):
    """Medida de desenho dos tooltips; os valores marcados com C.marca() viram odômetro no fim (F4)."""
    MEDIDAS.append(Medida(nome, DES, "texto", descricao, C.envolver_marcas(dax)))


def linhas(*ls) -> str:
    return "\n".join(l for g in ls for l in (g if isinstance(g, list) else [g]))


def fmt_pts(v: str) -> str:
    return f'FORMAT ( {v}, "{PTS}", "pt-BR" )'


def palavra(st: str) -> str:
    """'crítico' · 'atenção' · 'estável' de um status completo (o chamador garante que não está vazio)."""
    return f'SWITCH ( {st}, 2, "crítico", 1, "atenção", "estável" )'


def lista_e(v: str, p: str) -> list[str]:
    """{p}Txt = "A, B e C" a partir de "A|B|C"."""
    return [
        f'VAR {p}N = IF ( ISBLANK ( {v} ) || {v} = "", 0, PATHLENGTH ( {v} ) )',
        f'VAR {p}Pos = IF ( {p}N >= 2, FIND ( "§", SUBSTITUTE ( {v}, "|", "§", {p}N - 1 ) ) )',
        f'VAR {p}Txt = SWITCH ( TRUE (), {p}N = 0, "", {p}N = 1, {v}, '
        f'SUBSTITUTE ( LEFT ( {v}, {p}Pos - 1 ), "|", ", " ) & " e " & MID ( {v}, {p}Pos + 1, 999 ) )',
    ]


# listas de uma obra por linha: até LISTA_MAX obras todas aparecem; de LISTA_MAX + 1 em diante, as LISTA_MOSTRA
# primeiras e a linha "e mais N obras". A mesma regra vale nos tooltips de mês da T4 (contas_t4.py, tooltips_t4.py).
# auditoria da Fase 2 (M3): o pé do tooltip do mês tem 2 linhas; o corpo (≈ 273 px) cabe chip + 9 linhas de 25
LISTA_MAX = 9
LISTA_MOSTRA = 8
# item da nota: as faixas do item ocupam o alto do corpo, então a lista vai até 8 obras (7 + "e mais N")
ITEM_MAX = 8
ITEM_MOSTRA = 7
RJ_W, RJ_PRE, RJ_FOLGA = 520, 120, 2   # v2: corpo 520, Segoe 15 ("0 de 4 preenchidas · " ≈ 120 + 9 por algarismo)
COM_ABA = f"FILTER ( VALUES ( dObra[Obra] ), NOT ISEMPTY ( RELATEDTABLE ( {F} ) ) )"


def fora_da_lista(contagem: str, maximo: int = LISTA_MAX, mostra: int = LISTA_MOSTRA) -> str:
    """DAX da conta 'obras fora da lista': vazio até `maximo` obras; acima, o que passa das `mostra` mostradas."""
    return f"""VAR _n =
    {contagem}
RETURN
    IF ( _n > {maximo}, _n - {mostra} )"""


# ===================================================================================================== contas
conta("Recorte · justificativas em branco (lista) · ref", "texto",
      "Obras do recorte com justificativa exigida e em branco no mês de referência, do maior para o menor |desvio| do "
      "desembolso (empate: ordem alfabética), separadas por '|'. O rodapé do tooltip do item fluxo de caixa escreve "
      "quantas couberem numa linha (justificativas_rodape.py); a leitura do desembolso por obra (T4) lista todas.",
      f"""VAR _mes = [Mês de referência]
VAR _obras =
    CALCULATETABLE (
        ADDCOLUMNS (
            VALUES ( {F}[Obra] ),
            "@b", [Justificativa · em branco],
            "@d", ABS ( [Desembolso · desvio no mês] )
        ),
        REMOVEFILTERS ( dMes ),
        dMes[Mes] = _mes
    )
RETURN
    CONCATENATEX ( FILTER ( _obras, [@b] = 1 ), {F}[Obra], "|", [@d], DESC, {F}[Obra], ASC )""",
      "obras[].ultimo.justificativa_ausente · ago/26 real: JANGADA|POTENGI|REDINHA|CAJUEIRO (−31%, −21%, +17%, +15%)")
conta("Recorte · justificativas em branco fora da lista curta · ref", "0",
      f"Justificativas exigidas e em branco no mês de referência além das {R.RODAPE_NOMES} primeiras obras da lista "
      "(Recorte · justificativas em branco (lista) · ref): o M de 'em branco: A, B e mais M' no rodapé do tooltip do "
      f"item fluxo de caixa (T1) e no cartão Justificativas do mês (T4); vazio com até {R.RODAPE_NOMES} em branco.",
      f"""VAR _n = [Carteira · justificativas em branco · ref] + 0
RETURN
    IF ( _n > {R.RODAPE_NOMES}, _n - {R.RODAPE_NOMES} )""",
      "ago/26 real: 2 (4 em branco) · jun/26: vazio (1 em branco)")
conta("Desembolso · obra de maior desvio · ref", "texto",
      "Obra do recorte com o maior desvio do desembolso (absoluto) no mês de referência.",
      f"""VAR _mes = [Mês de referência]
VAR _obras =
    CALCULATETABLE (
        ADDCOLUMNS ( VALUES ( {F}[Obra] ), "@d", ABS ( [Desembolso · desvio no mês] ) ),
        REMOVEFILTERS ( dMes ),
        dMes[Mes] = _mes
    )
RETURN
    MAXX ( TOPN ( 1, FILTER ( _obras, NOT ISBLANK ( [@d] ) ), [@d], DESC ), {F}[Obra] )""",
      "maior obras[].ultimo.indicadores.desvio_desembolso")

# a obra no mês anterior ao do contexto, pela nota (uma obra no contexto): base das comparações "desde julho" do tooltip
# da obra e das contas de entrou / saiu / abriu em crítico (leituras_t1.py)
# (lê a leitura de um mês, [Nota · X · um mês]: a linha de dRankingNota, o mesmo valor da medida, sem recalcular os itens)
for nome_, med_, fmt_ in (("status", "Nota · status", "0"), ("nota", "Nota · nota final", "0.00"),
                          ("pendente", "Nota · pendente", "0")):
    conta(f"T1 · Obra · {nome_} no mês anterior", fmt_,
          f"[{med_}] da obra no mês anterior ao do contexto (vazio sem aba nem base no mês anterior"
          + ("; vazio também quando o mês anterior está pendente" if nome_ != "pendente" else "") + "). Uma obra no "
          f"contexto. Lê [{med_} · um mês].",
          f"""VAR _mes = EDATE ( MAX ( dMes[Mes] ), -1 )
RETURN
    CALCULATE ( [{med_} · um mês], REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )""", "oráculo da régua antiga (mês anterior)")
    conta(f"T1 · Obra · {nome_} no mês anterior · ref", fmt_,
          f"[T1 · Obra · {nome_} no mês anterior] com o mês do contexto = mês de referência.",
          f"""VAR _mes = [Mês de referência]
RETURN
    CALCULATE ( [T1 · Obra · {nome_} no mês anterior], REMOVEFILTERS ( dMes ), dMes[Mes] = _mes )""",
          "oráculo da régua antiga (mês anterior)")

for chave_, cond_ in (("crítico", "[Nota · status · um mês] == 2"), ("atenção", "[Nota · status · um mês] == 1"),
                      ("estável", "[Nota · status · um mês] == 0"), ("pendente", "[Nota · pendente · um mês] == 1")):
    conta(f"T1 · Tooltip mês · obras fora da lista · {chave_}", "0",
          f"Obras com aba no mês do contexto no estado {chave_} da nota (as da coluna do tooltip do mês; o mesmo que "
          f"Nota · carteira · …) que não cabem na coluna: vazio com até {LISTA_MAX} obras (todas aparecem); com mais, "
          f"as que passam das {LISTA_MOSTRA} mostradas (o N da linha 'e mais N obras').",
          fora_da_lista(f"COUNTROWS ( FILTER ( {COM_ABA}, {cond_} ) )"),
          f"vazio com até {LISTA_MAX} obras no estado")
conta("T1 · Tooltip indicador · obras fora da lista", "0",
      f"Obras com aba no mês de referência que não cabem na lista do tooltip do item da nota: vazio com até {ITEM_MAX} "
      f"obras (todas aparecem); com mais, as que passam das {ITEM_MOSTRA} mostradas (o N da linha 'e mais N obras').",
      fora_da_lista("[Obras com análise · ref] + 0", ITEM_MAX, ITEM_MOSTRA),
      f"vazio com até {ITEM_MAX} obras")

# nota de termômetro digitada fora da faixa (auditoria da Fase 2, minor 6). No chip, a mesma largura de "falta na
# base" (um chip mais largo estreita a coluna da faixa e quebra "−3% ≤ X < −2%"); o tooltip do item da T2 diz a faixa
TERMO_FORA = "fora da faixa"

# ===================================================================================================== CSS comum
CSS_TT2 = (
    # v2 (Figma 04 · Redesenho v2, seção 379:788; pbi/spec/redesenho/t01.md): cartão offwhite, contorno 1 px preto,
    # cantos retos. Em fluxo, de cima para baixo: cabeçalho preto (72; a meta desce para a 2ª linha, 94, quando não
    # cabe ao lado do título com 24 px de folga — flex-wrap), corpo (margem 16 · 20, encolhe e esconde o que passar) e
    # pé preso à base (.pe, margem 20 · 16: regra + versalete + uma linha). Mesmo HTML da v1: sobretítulo, .tit e .dir
    # são irmãos dentro de .cab.
    # corpo branco (pedido do Alisson, 07/10/2026); só o cabeçalho é preto
    ".tt{position:fixed;inset:0;display:flex;flex-direction:column;background:#FFFFFF;border:1px solid #0B0B0C;"
    "border-radius:0;overflow:hidden}"
    ".tt .cab{flex:none;display:flex;flex-wrap:wrap;align-items:baseline;column-gap:24px;row-gap:6px;"
    "padding:14px 20px 13px;background:#0B0B0C}"
    ".tt .cab>.vs:first-child{flex:0 0 100%;margin-bottom:-2px;color:rgba(233,224,207,.7)}"
    ".tt .cab .tit{display:flex;align-items:baseline;gap:8px;white-space:nowrap;min-width:0}"
    ".tt .cab .tit b{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:21px;line-height:26px;"
    "color:#F7F4EE}"
    ".tt .cab .tit em{font-style:normal;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:12px;"
    "line-height:15px;letter-spacing:1.2px;color:rgba(233,224,207,.6)}"
    ".tt .cab .tit .selo-i{border-color:rgba(233,224,207,.6);color:rgba(233,224,207,.85)}"
    ".tt .cab .tit .selo-r{background:#E9E0CF;color:#0B0B0C}"
    ".tt .cab .vs.dir{margin-left:auto;line-height:16px;white-space:nowrap;color:rgba(233,224,207,.85)}"
    ".tt .corpo{flex:1;min-height:0;position:relative;margin:16px 20px 0;overflow:hidden}"
    ".tt .pe{flex:none;margin:0 20px 16px}"
    ".tt .pe .rg{margin:0 0 11px}"
    ".tt .bh{display:flex;justify-content:space-between;margin-bottom:8px}"
    ".tt .pe .bh{margin-bottom:0}"
    ".tt .rg{height:1px;background:#E1E1E1;margin:12px 0}"
    ".tt .tx{font-size:15px;line-height:21px;color:#0B0B0C}"
    ".tt .vs{display:block}"
    # tabela de linhas (uma grade só, colunas pela maior célula: marca + rótulo · valor · detalhe · pontos)
    ".tt .tab{display:grid;grid-template-columns:max-content max-content 1fr max-content;column-gap:16px;"
    "align-items:center;white-space:nowrap}"
    ".tt .lin{display:grid;align-items:center;height:28px;white-space:nowrap}"
    ".tt .tab .lin{display:contents}"
    # célula em bloco (flex comeria o espaço de " p.p." e de " · julho"); só o rótulo, com a marca, é flex
    ".tt .tab .lin>span{display:block;height:28px;line-height:28px;min-width:0}"
    ".tt .tab .lin>.n{display:flex;align-items:center;gap:6px}"
    ".tt .lin .n{font-size:15px;font-weight:600}"
    ".tt .lin .n .mk{flex:none}"
    ".tt .lin .v{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:16px}"
    ".tt .lin .d{font-size:14px;color:#3B3B3F;overflow:hidden;text-overflow:ellipsis}"
    # o detalhe quebra em até duas linhas de 14 dentro da linha de 28 (auditoria da Fase 2, M4: "zerada pelo Médio Prazo")
    ".tt .tab .lin>.d{display:flex;align-items:center;white-space:normal;line-height:14px}"
    ".tt .lin .p{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:16px;text-align:right}"
    ".tt .lin .p em{font-style:normal;color:#6B6B70;margin-left:4px}"
    ".tt .lin .p.z{color:#6B6B70}"
    ".tt .lin.est .v{color:#3B3B3F}"
    ".tt i.vz{display:block;font-style:normal;color:#6B6B70;font-size:14px;line-height:25px}"
    ".tt .tab i.vz{grid-column:1/-1;padding-left:17px;line-height:27px}"
    # rodapé de uma linha (no máximo ~70 caracteres; o que passar vira reticências)
    ".tt .rod{margin-top:4px;font-size:15px;line-height:21px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
    # pé de duas linhas, com a altura reservada (tooltip do mês: quem entrou, saiu ou abriu nunca some; auditoria, M3)
    ".tt .rod.r2{white-space:normal;min-height:42px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}"
    # o rótulo que só aparece no fim da corrida (mês do ponto)
    "@keyframes ttFim{from{opacity:0}}"
    ".tt .fim{animation:ttFim .2s ease-out backwards}"
    "@media (prefers-reduced-motion:reduce){.tt .fim{animation:none}}"
)
desenho("T1 · CSS tooltip",
        "CSS dos tooltips de página v2 da Tela 01 (cartão offwhite de cantos retos, cabeçalho preto de 72 com a meta em "
        "flex-wrap, corpo em fluxo e pé preso à base). Candidato a substituir o [Comum · CSS tooltip] (v1, usado pelas "
        "outras telas) quando a camada comum passar para a v2.",
        "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(CSS_TT2))


def ng_span(txt: str, cond: str) -> str:
    """DAX: o texto {txt} dentro de <span class='ng'> quando {cond}."""
    return f"IF ( {cond}, \"<span class='ng'>\" & {txt} & \"</span>\", {txt} )"


def selo(var_selo: str) -> str:
    return (f"\"<span class='selo \" & IF ( {var_selo} = \"REAL\", \"selo-r\", \"selo-i\" ) & \"'>\" & {var_selo} "
            f"& \"</span>\"")


def valor_item(cod: str, x: str, faixa: str, p: str) -> list[str]:
    """{p}Txt = o X do item `cod` na unidade dele, e {p}Ng = ' ng' quando é um valor que se lê como perda: custo
    'IDC 0,97' (vermelho abaixo de 1) · prazo 'atraso 1,4 mês' ou 'adiantada 0,3 mês' · PPC, caixa, inspeção, NR-18 e
    entregas em % · acidentes 'TF 6,2' · análise crítica '3 de 3'. Vazio: '—'."""
    return [
        f"VAR {p}A = ABS ( {x} )",
        f"VAR {p}Txt =",
        f"    SWITCH (",
        f"        TRUE (),",
        f'        ISBLANK ( {x} ), "—",',
        f'        {cod} = "custo", "IDC " & FORMAT ( {x}, "0.00", "pt-BR" ),',
        f'        {cod} = "prazo", IF ( ROUND ( {x}, 1 ) > 0, "atraso ", IF ( ROUND ( {x}, 1 ) < 0, "adiantada ", "em dia" ) )',
        f'            & IF ( ROUND ( {x}, 1 ) = 0, "", FORMAT ( {p}A, "0.0", "pt-BR" ) & IF ( ROUND ( {p}A, 1 ) <= 1, " mês", " meses" ) ),',
        f'        {cod} = "acidentes", "TF " & FORMAT ( {x}, "0.0", "pt-BR" ),',
        f'        {cod} = "analise", FORMAT ( {x}, "0" ) & " de 3",',
        # truncado em uma casa: 89,9999% não pode aparecer como 90% ao lado da faixa "X < 90%"; sempre com uma casa
        # (retorno de 28/10/2026: "3%" ao lado de "3,1%" na mesma coluna)
        f'        FORMAT ( TRUNC ( {p}A * 100, 1 ), "0.0", "pt-BR" ) & "%"',
        f"    )",
        f'VAR {p}Ng = IF ( ( {cod} = "custo" && {x} < 1 ) || ( {cod} = "prazo" && ROUND ( {x}, 1 ) > 0 ), " ng", "" )',
    ]


# ===================================================================================================== Obra
# 9 itens × 28 + série da nota (82) + pé: 568 de altura (paginas/tt_t1.py). Série "nota, mês a mês": área 520, vaga =
# mín(65, 518 ÷ n), barra = mín(32, vaga − 12), 40 px = a nota máxima,
# x pela posição na janela; mês pendente em barra tracejada até os pontos obtidos; rótulo no mês de referência, no maior
# e no menor das notas completas; eixo em três letras (Segoe 13; o do ponto em Semibold preto)
# 518 = a largura útil do .corpo (560 − 2 × 20 de margem − 2 × 1 de borda do .u); com 520 o último rótulo, preso à
# direita, perdia 1 a 2 px (auditoria da Fase 2, M4, rodada 2)
AREA_TT = 518
CSS_OBRA = (".tt .ser{position:relative;height:82px}"
            ".tt .ser .c{position:absolute;top:0;text-align:center;height:82px}"
            ".tt .ser .c .val{position:absolute;left:-14px;right:-14px;font-family:'Barlow U','Segoe UI',sans-serif;"
            "font-weight:600;font-size:14px;line-height:17px;white-space:nowrap}"
            ".tt .ser .c .bar{position:absolute;bottom:21px;box-sizing:border-box}"
            ".tt .ser .c .bar.s2{background:#C43737}"
            ".tt .ser .c .bar.s1{background:#C9821F}"
            ".tt .ser .c .bar.s0{background:#A9CDB9}"
            # pendente: branco com contorno tracejado grafite, até os pontos obtidos
            ".tt .ser .c .bar.sm{background:#FFFFFF;border:1px dashed #3B3B3F}"
            ".tt .ser .c .ms{position:absolute;left:-10px;right:-10px;bottom:0;font-size:13px;line-height:16px;"
            "color:#6B6B70;white-space:nowrap}"
            ".tt .ser .c .ms.ref{font-weight:600;color:#0B0B0C}.tt .ser .c .ms.sem{opacity:.4}"
            ".tt .ser .c .val.ext{color:#6B6B70}"
            # nas pontas da série o rótulo não passa da borda do corpo (auditoria da Fase 2, M4)
            ".tt .ser .c.ini .val{left:0;right:auto;text-align:left}"
            ".tt .ser .c.fim .val{left:auto;right:0;text-align:right}"
            ".tt .ser .c.ini .ms,.tt .ser .c.fim .ms{left:0;right:0}"
            ".tt .rg.s{margin:6px 0 11px}"
            ".tt .vs+.ser{margin-top:4px}"
            ".tt .tab .lin>.p{display:flex;justify-content:flex-end;align-items:center}")
# F4: a grade dos itens é a lista com escala (sempre os 9 itens: faixa e3, a altura de antes) e tudo entra em cascata
CSS_GRADE_LS = (".tt .tab.ls .lin>span{height:auto;line-height:1.3}"
                ".tt .tab.ls .lin>.d{line-height:1.15}")
FONTES_TAB = {".tt .ls .lin .n": 15, ".tt .ls .lin .v": 16, ".tt .ls .lin .p": 16}   # o detalhe (2 linhas de 14) fica
CASCATA_TAB = TL.entrada(".tt .ls>:nth-child({k})>*", [".tt .corpo>.bh", ".tt .corpo>.vs", ".tt .corpo>.rg",
                                                         ".tt .ser .ms", ".tt .fx"])
desenho("T1 · Tooltip obra · CSS", "CSS do tooltip de obra (F4: lista dos itens com escala e cascata de entrada).",
        "-- 4 · Marcação\n[T1 · CSS tooltip]\n    & " + dax_lit(CSS_OBRA + TL.css_escala(FONTES_TAB, grade=True)
                                                       + CSS_GRADE_LS + CASCATA_TAB))

desenho(
    "T1 · Tooltip obra · HTML",
    "Tooltip de página da obra (linha da lista de obras): no cabeçalho a nota e o status da nota (ou 'pendente · X de Y') "
    "e o gestor, se houver; os 9 itens da nota com o valor, a faixa atingida e os pontos de possíveis ('falta na base' "
    "quando não há dado); a nota mês a mês na janela (pendente tracejado até os pontos obtidos; rótulo no mês de "
    "referência, na maior e na menor nota); no pé, o que mudou desde o mês anterior, só entre notas completas, ou "
    "quantos itens faltam para a nota sair.",
    linhas(
        "-- 1 · Leituras",
        "VAR _ref = [Mês de referência]",
        "VAR _mesCM = [Mês de referência · curto maiúsculo]",
        "VAR _mesAnt = [Mês anterior à referência · nome]",
        "VAR _obra = [Obra · nome]",
        "VAR _cod = [Obra · código]",
        "VAR _selo = [Obra · selo]",
        "VAR _gestor = [Nota · gestor · ref]",
        "VAR _st = [Nota · status · ranking · ref]",
        "VAR _pend = [Nota · pendente · ranking · ref]",
        "VAR _nota = [Nota · nota final · ranking · ref]",
        "VAR _obt = [Nota · pontos obtidos · ranking · ref]",
        "VAR _poss = [Nota · pontos possíveis · ranking · ref]",
        "VAR _falta = [Nota · itens faltando · ref] + 0",
        # valor fora da faixa: já contado em "itens faltando", mas não é falta (auditoria da Fase 3, minor 1)
        "VAR _fora = [Nota · itens fora da faixa · ref] + 0",
        "VAR _fal = _falta - _fora",
        "VAR _max = [Nota · nota · máximo]",
        "VAR _stAnt = [T1 · Obra · status no mês anterior · ref]",
        "VAR _notaAnt = [T1 · Obra · nota no mês anterior · ref]",
        "VAR _pendAnt = [T1 · Obra · pendente no mês anterior · ref]",
        "VAR _itens =",
        "    ADDCOLUMNS (",
        "        VALUES ( dItemNota[Item] ),",
        "        \"@ord\", [Nota · item · ordem],",
        "        \"@rot\", [Nota · item · nome médio],",
        "        \"@fonte\", [Nota · item · fonte],",
        "        \"@fora\", [Nota · item · fora da faixa · ref],",
        "        \"@x\", [Nota · item · X · ref],",
        "        \"@fx\", [Nota · item · faixa atingida · ref],",
        "        \"@pts\", [Nota · item · pontos · ref],",
        "        \"@poss\", [Nota · item · possíveis · ref]",
        "    )",
        "VAR _nIt = COUNTROWS ( _itens ) /* lista */",
        "VAR _n = [Série · meses até a referência]",
        "VAR _meses =",
        "    ADDCOLUMNS (",
        "        VALUES ( dMes[Mes] ),",
        "        \"@ate\", [Série · mês até a referência],",
        "        \"@ord\", [Mês · ordem],",
        "        \"@pos\", [Série · posição na janela],",
        "        \"@rotAno\", [Mês · rótulo curto],",
        "        \"@nota\", [Nota · nota final · um mês],",
        "        \"@st\", [Nota · status · um mês],",
        "        \"@pend\", [Nota · pendente · um mês],",
        "        \"@obt\", [Nota · pontos obtidos · um mês],",
        "        \"@poss\", [Nota · pontos possíveis · um mês],",
        "        \"@rot\", [Mês · abreviado]",
        "    )",
        "-- 2 · Textos",
        D.od_tabela(),
        "VAR _txtSob = \"NOTA DA OBRA · \" & _mesCM & IF ( _gestor = \"\" || ISBLANK ( _gestor ), \"\", \" · GESTOR: \" "
        "& UPPER ( _gestor ) )",
        "VAR _txtDir =",
        "    IF (",
        "        _pend = 1,",
        "        \"PENDENTE · \" & " + C.marca(fmt_pts("_obt")) + " & \" DE \" & " + fmt_pts("_poss") + ",",
        "        \"NOTA \" & " + C.marca(fmt_pts("_nota")) + " & \" · \" & UPPER ( " + DC.palavra_status("_st", "_pend") + " )",
        "    )",
        "VAR _htmlLinhas =",
        "    CONCATENATEX (",
        "        _itens,",
        "        VAR _c = dItemNota[Item]",
        "        VAR _x = [@x]",
        "        VAR _fx = [@fx]",
        "        VAR _pts = [@pts]",
        "        VAR _possI = [@poss]",
        "\n".join("        " + l for l in valor_item("_c", "_x", "_fx", "_v")),
        "\n".join("        " + l for l in DC.chip_item("_k", "_pts", "_possI", "base")),
        f'        VAR _txtFalta = IF ( [@fora] = 1, "{TERMO_FORA}", IF ( [@fonte] = "Análise Crítica", '
        f'"{DC.SEM_DADO_AC}", "{DC.FALTA_NA_BASE}" ) )',
        "        VAR _clsK = SWITCH ( TRUE (), ISBLANK ( _pts ), \"f\", _pts >= _possI, \"c\", "
        "_pts = 0, \"z\", \"p\" )",
        "        VAR _chip = \"<span class='chi chi-\" & _clsK & \"'>\" & IF ( ISBLANK ( _pts ), _txtFalta, " + C.marca("_kTxt") + " ) & \"</span>\"",
        "        VAR _det = IF ( ISBLANK ( _pts ), \"\", _fx )",
        "        RETURN",
        "            \"<div class='lin'><span class='n'>\" & [@rot] & \"</span><span class='v\" & _vNg & \"'>\" & " + C.marca("_vTxt"),
        "                & \"</span><span class='d'>\" & _det & \"</span><span class='p'>\" & _chip & \"</span></div>\",",
        "        \"\",",
        "        [@ord], ASC",
        "    )",
        "VAR _serie = FILTER ( _meses, [@ate] = 1 ) /* lista */",
        "VAR _comNota = FILTER ( _serie, NOT ISBLANK ( [@nota] ) ) /* lista */",
        "VAR _vMax = MAXX ( _comNota, [@nota] ) /* geometria */",
        "VAR _vMin = MINX ( _comNota, [@nota] ) /* geometria */",
        "VAR _mesMax = MINX ( FILTER ( _comNota, [@nota] = _vMax ), dMes[Mes] ) /* geometria */",
        "VAR _mesMin = MINX ( FILTER ( _comNota, [@nota] = _vMin ), dMes[Mes] ) /* geometria */",
        "VAR _rotMax = _vMax <> _nota",
        "VAR _rotMin = _vMin <> _nota && _vMin <> _vMax",
        f"VAR _slot = MIN ( 65, DIVIDE ( {AREA_TT}, _n ) ) -- geometria",
        "VAR _larg = MIN ( 32, ROUND ( _slot - 12, 0 ) ) -- geometria",
        "VAR _w = ROUND ( _slot, 0 ) -- geometria",
        "VAR _xb = ROUND ( ( _slot - _larg ) / 2, 0 ) -- geometria",
        "VAR _passo = ROUND ( DIVIDE ( 420, _n ), 0 ) -- geometria",
        "VAR _escala = DIVIDE ( 40, _max ) -- geometria",
        "VAR _htmlSerie =",
        "    CONCATENATEX (",
        "        _serie,",
        "        VAR _pd = [@pend] = 1",
        "        VAR _v = IF ( _pd, [@obt], [@nota] )",
        "        VAR _tem = NOT ISBLANK ( [@pend] ) && NOT ISBLANK ( _v )",
        "        VAR _h = IF ( _tem, MAX ( ROUND ( _v * _escala, 0 ), 2 ), 0 ) /* geometria */",
        "        VAR _x = ROUND ( ( [@pos] - 1 ) * _slot, 0 ) /* geometria */",
        "        VAR _atraso = ( [@pos] - 1 ) * _passo /* geometria */",
        "        VAR _cls = IF ( _pd, \"sm\", \"s\" & [@st] )",
        "        VAR _txtV = IF ( _pd, " + fmt_pts("[@obt]") + " & \" de \" & " + fmt_pts("[@poss]") + ", "
        + fmt_pts("[@nota]") + " )",
        "        VAR _ehRef = dMes[Mes] = _ref",
        "        VAR _ehExt = NOT _pd && ( ( _rotMax && dMes[Mes] = _mesMax ) || ( _rotMin && dMes[Mes] = _mesMin ) )",
        "        VAR _rotMes = IF ( [@rot] = \"jan\" && [@pos] > 1, [@rotAno], [@rot] )",
        "        VAR _rot =",
        "            SWITCH (",
        "                TRUE (),",
        "                _tem && _ehRef, \"<span class='val fim' style='bottom:\" & ( 24 + _h ) & \"px;animation-delay:\"",
        "                    & ( _atraso + 700 ) & \"ms'>\" & " + C.marca("_txtV") + " & \"</span>\",",
        "                _tem && _ehExt, \"<span class='val ext' style='bottom:\" & ( 24 + _h ) & \"px'>\" & " + C.marca("_txtV") + " & \"</span>\",",
        "                \"\"",
        "            )",
        "        RETURN",
        "            \"<div class='c\" & IF ( [@pos] = 1, \" ini\", IF ( [@pos] = _n, \" fim\" ) ) & \"' style='left:\" & _x "
        "& \"px;width:\" & _w & \"px'>\" & _rot",
        "                & IF ( _tem, \"<i class='bar \" & _cls & \"' style='left:\" & _xb & \"px;width:\" & _larg",
        "                    & \"px;height:\" & _h & \"px' data-rk='m\" & [@ord] & \"' data-rp='height' data-rd='\" & _atraso",
        "                    & \"'></i>\" )",
        "                & \"<span class='ms\" & IF ( _ehRef, \" ref\", IF ( _tem, \"\", \" sem\" ) ) & \"'>\" & _rotMes "
        "& \"</span></div>\",",
        "        \"\",",
        "        dMes[Mes], ASC",
        "    )",
        # pé: pendente → por que não há nota; completa → o que mudou desde o mês anterior, só entre notas completas
        "VAR _txtNota = " + C.marca(fmt_pts("_nota")),
        "VAR _txtNotaAnt = " + C.marca(fmt_pts("_notaAnt")),
        "VAR _txtFalta =",
        "    SWITCH (",
        "        TRUE (),",
        "        _fal > 0 && _fora > 0, \"falta dado em \" & _fal & IF ( _fal = 1, \" item\", \" itens\" ) & \" e \" & _fora & \" está\"",
        "            & IF ( _fora > 1, \"ão\", \"\" ) & \" fora da faixa\",",
        "        _fal > 0, IF ( _fal = 1, \"falta dado em 1 item\", \"falta dado em \" & _fal & \" itens\" ),",
        "        IF ( _fora = 1, \"1 item está fora da faixa\", _fora & \" itens estão fora da faixa\" )",
        "    )",
        "VAR _txtSai =",
        "    SWITCH (",
        "        TRUE (),",
        # o pé é uma linha de 518 px (~70 caracteres): o fecho fica curto
        "        _fal = 0, IF ( _fora = 1, \"; a nota sai quando ele for corrigido\", \"; a nota sai quando forem corrigidos\" ),",
        "        _fora > 0, \"; sem nota por enquanto\",",
        "        _falta = 1, \"; a nota sai quando ele tiver dado\",",
        "        \"; a nota sai quando todos tiverem dado\"",
        "    )",
        "VAR _txtMud =",
        "    SWITCH (",
        "        TRUE (),",
        "        _pend = 1, _txtFalta & _txtSai,",
        "        _pendAnt = 1, \"em \" & _mesAnt & \" a obra estava pendente: sem nota para comparar\",",
        "        ISBLANK ( _notaAnt ), \"\",",
        "        _stAnt = _st, \"seguiu em \" & " + palavra("_st") + " & IF ( _txtNotaAnt = _txtNota, "
        "\", com a mesma nota\", \": nota de \" & _txtNotaAnt & \" para \" & _txtNota ),",
        "        _st = 2, \"entrou em crítico: nota de \" & _txtNotaAnt & \" para \" & _txtNota,",
        "        _stAnt = 2, \"saiu de crítico para \" & " + palavra("_st") + " & \": nota de \" & _txtNotaAnt & \" para \" "
        "& _txtNota,",
        "        \"passou de \" & " + palavra("_stAnt") + " & \" para \" & " + palavra("_st") + " & \": nota de \" "
        "& _txtNotaAnt & \" para \" & _txtNota",
        "    )",
        "VAR _tituloMud = IF ( _pend = 1, \"POR QUE ESTÁ PENDENTE\", \"DESDE \" & UPPER ( _mesAnt ) )",
        "-- 4 · Marcação",
        "RETURN",
        "    IF (",
        "        NOT ISBLANK ( _pend ),",
        "        \"<div class='u tt'><div class='cab'><p class='vs'>\" & _txtSob & \"</p>\"",
        "            & \"<div class='tit'><b>\" & " + D.esc("_obra") + " & \"</b><em>\" & _cod & \"</em>\" & "
        + selo("_selo") + " & \"</div>\"",
        "            & \"<p class='vs dir'>\" & _txtDir & \"</p></div>\"",
        "            & \"<div class='corpo'><div class='bh'><span class='vs'>ITENS DA NOTA</span>\"",
        "            & \"<span class='vs'>PONTOS</span></div><div class='tab\" & " + TL.atributos("_nIt") + "'>\" & _htmlLinhas & \"</div>\"",
        "            & \"<div class='rg s'></div><span class='vs'>NOTA, MÊS A MÊS</span>\"",
        "            & \"<div class='ser'>\" & _htmlSerie & \"</div></div>\"",
        "            & IF ( _txtMud <> \"\", \"<div class='pe'><div class='rg'></div><span class='vs'>\" & _tituloMud & \"</span>\"",
        "                & \"<p class='rod'>\" & _txtMud & \"</p></div>\" )",
        "        & \"</div>\" & [Comum · JS contador tooltip] & [Comum · JS corrida]",
        "    )",
    ))

# ===================================================================================================== Dimensão da nota
# (era o tooltip do indicador; nomes das medidas mantidos) — F3: eixo dItemNota[Dimensao]. Corpo: as faixas de cada
# item da dimensão (texto do dicionário NOTA), obra por obra (até ITEM_MAX) e o pé preso à base
CSS_IND = (".tt .fx{font-size:13px;line-height:18px;color:#3B3B3F;margin:0 0 10px;white-space:normal}"
           ".tt .fx .f{white-space:nowrap}"
           ".tt .fx b{font-weight:600;color:#0B0B0C}"
           ".tt .fx+.bh{margin-top:2px}"
           ".tt .tab.i .lin>span{height:27px;line-height:27px}"
           ".tt .tab.i .lin>.p{display:flex;justify-content:flex-end;align-items:center}"
           ".tt .lin .n .selo{margin-left:2px}")
desenho("T1 · Tooltip indicador · CSS", "CSS do tooltip da dimensão da nota (F4: a lista de obras ocupa o corpo, com "
        "escala pela contagem de linhas, e tudo entra em cascata).",
        "-- 4 · Marcação\n[T1 · CSS tooltip]\n    & " + dax_lit(CSS_IND + TL.css_escala(FONTES_TAB, grade=True)
                                                       + CSS_GRADE_LS + ".tt .tab.i.ls .lin>span{height:auto}"
                                                       + CASCATA_TAB))
COMO_LER = {   # uma linha, no máximo ~70 caracteres; sem limite escrito (as faixas vêm de Nota · item · faixas)
    "Custo": "IDC = valor agregado ÷ custo do que já virou obra",
    "Prazo": "atraso pelo cronograma; PPC = tarefas da semana cumpridas",
    "Qualidade": "serviços aprovados na primeira inspeção ÷ verificados",
    "Segurança": "acidentes por milhão de horas em 12 meses; checklist NR-18",
    "Suprimentos": "pedidos no prazo e completos ÷ previstos no mês",
    "Gestão": "conta fecha, justificativa quando exigida, previsto não caiu",
}
desenho(
    "T1 · Tooltip indicador · HTML",
    "Tooltip de página da dimensão da nota (linha de 'Onde a carteira perde pontos', eixo dItemNota[Dimensao]): quanto "
    "a dimensão vale, as faixas de cada item dela (Nota · item · faixas), obra por obra da que mais perde à que menos "
    "perde, com o status da obra, o X de cada item e os pontos da dimensão de possíveis ('falta na base' sem dado), e no "
    "pé 'como ler' (no caixa, as justificativas exigidas e preenchidas na planilha). Até "
    f"{ITEM_MAX} obras, todas aparecem; de {ITEM_MAX + 1} em diante, as {ITEM_MOSTRA} primeiras e 'e mais N obras'. O pé "
    "fica preso à base do cartão.",
    linhas(
        "-- 1 · Leituras",
        "VAR _dim = SELECTEDVALUE ( dItemNota[Dimensao] )",
        "VAR _maxD = [Nota · item · máximo]",
        "VAR _fonte = [Nota · item · fonte]",
        "VAR _mesCM = [Mês de referência · curto maiúsculo]",
        "VAR _exig = [Carteira · justificativas exigidas · ref] + 0",
        "VAR _branco = [Carteira · justificativas em branco · ref] + 0",
        "VAR _pre = [Carteira · justificativas preenchidas · ref] + 0",
        "VAR _listaBranco = [Recorte · justificativas em branco (lista) · ref]",
        "VAR _foraRod = [Recorte · justificativas em branco fora da lista curta · ref]",
        "VAR _mais = [T1 · Tooltip indicador · obras fora da lista]",
        "VAR _itens =",
        "    ADDCOLUMNS (",
        "        VALUES ( dItemNota[Item] ),",
        "        \"@ord\", [Nota · item · ordem],",
        "        \"@rot\", [Nota · item · nome],",
        "        \"@fx\", [Nota · item · faixas]",
        "    )",
        "VAR _nItens = COUNTROWS ( _itens ) /* lista */",
        "VAR _obras =",
        "    ADDCOLUMNS (",
        "        VALUES ( dObra[Obra] ),",
        "        \"@aba\", [Obras com análise · ref],",
        "        \"@pos\", [T1 · Obras · posição],",
        "        \"@st\", [Nota · status · ranking · ref],",
        "        \"@pend\", [Nota · pendente · ranking · ref],",
        "        \"@pts\", [Nota · item · pontos · ref],",
        "        \"@poss\", [Nota · item · possíveis · ref],",
        "        \"@perd\", [Nota · item · perdidos · ref],",
        "        \"@selo\", [Obra · selo]",
        "    )",
        "VAR _comAba = FILTER ( _obras, [@aba] = 1 ) /* lista */",
        f"/* passou de {ITEM_MAX} obras: as {ITEM_MOSTRA} primeiras (a ordem da lista) e a linha 'e mais N obras' */",
        "VAR _mostra =",
        "    TOPN (",
        f"        IF ( _mais > 0, {ITEM_MOSTRA}, {ITEM_MAX} ),",
        "        _comAba,",
        "        INT ( ISBLANK ( [@pts] ) ), ASC,",
        "        [@perd], DESC,",
        "        [@pos], ASC",
        "    ) /* lista */",
        "-- 2 · Textos",
        f'VAR _txtFalta = IF ( _fonte = "Análise Crítica", "{DC.SEM_DADO_AC}", "{DC.FALTA_NA_BASE}" )',
        "VAR _txtDir = \"VALE ATÉ \" & " + C.marca(fmt_pts("_maxD")) + " & IF ( _maxD < 2, \" PONTO\", \" PONTOS\" )",
        # faixas → pontos de cada item da dimensão (com o nome do item quando a dimensão tem mais de um); cada faixa
        # inteira numa linha (.f sem quebra), a quebra só cai entre as faixas
        "VAR _htmlFx =",
        "    CONCATENATEX (",
        "        _itens,",
        "        VAR _fxEsc = SUBSTITUTE ( SUBSTITUTE ( [@fx], \"<\", \"&lt;\" ), \">\", \"&gt;\" )",
        "        RETURN",
        "            \"<p class='fx'>\" & IF ( _nItens > 1, \"<b>\" & [@rot] & \":</b> \", \"\" ) & \"<span class='f'>\"",
        "                & SUBSTITUTE ( _fxEsc, \" · \", \"</span> · <span class='f'>\" ) & \"</span></p>\",",
        "        \"\",",
        "        [@ord], ASC",
        "    )",
        "VAR _htmlLinhas =",
        "    CONCATENATEX (",
        "        _mostra,",
        "        VAR _pts = [@pts]",
        "        VAR _possI = [@poss]",
        "        VAR _vals =",
        "            CONCATENATEX (",
        "                VALUES ( dItemNota[Item] ),",
        "                VAR _c = dItemNota[Item]",
        "                VAR _x = [Nota · item · X · ref]",
        "\n".join("                " + l for l in valor_item("_c", "_x", "", "_v")),
        "                RETURN",
        "                    \"<span class='\" & TRIM ( _vNg ) & \"'>\" & " + C.marca("_vTxt") + " & \"</span>\",",
        "                \" · \",",
        "                [Nota · item · ordem], ASC",
        "            )",
        "\n".join("        " + l for l in DC.chip_item("_k", "_pts", "_possI", "base")),
        "        VAR _clsK = SWITCH ( TRUE (), ISBLANK ( _pts ), \"f\", _pts >= _possI, \"c\", "
        "_pts = 0, \"z\", \"p\" )",
        "        VAR _chip = \"<span class='chi chi-\" & _clsK & \"'>\" & IF ( ISBLANK ( _pts ), _txtFalta, " + C.marca("_kTxt") + " ) & \"</span>\"",
        "        VAR _mk = " + DC.marca_status("[@st]", "[@pend]"),
        "        VAR _seloH = \"<span class='selo \" & IF ( [@selo] = \"REAL\", \"selo-r\", \"selo-i\" ) & \"'>\" "
        "& [@selo] & \"</span>\"",
        "        RETURN",
        "            \"<div class='lin'><span class='n'>\" & _mk & dObra[Obra] & _seloH & \"</span>\"",
        "                & \"<span class='v'>\" & _vals & \"</span><span class='d'></span>\"",
        "                & \"<span class='p'>\" & _chip & \"</span></div>\",",
        "        \"\",",
        "        INT ( ISBLANK ( [@pts] ) ), ASC,",
        "        [@perd], DESC,",
        "        [@pos], ASC",
        "    )",
        "VAR _htmlMais = IF ( _mais > 0, \"<i class='vz'>e mais \" & " + C.marca('FORMAT ( _mais, "0" )') + " & \" obras</i>\" )",
        "VAR _nLin = COUNTROWS ( _mostra ) + IF ( _mais > 0, 1, 0 ) /* lista */",
        f"/* rodapé do caixa ({RJ_W} px): 'P de E preenchidas · ' (~9 px por algarismo + {RJ_PRE}) e o trecho dos nomes, "
        f"com {RJ_FOLGA} px de folga; o ±10% (regra da Análise Crítica) fica no versalete da direita */",
        f"VAR _pxRod = ROUND ( ( {RJ_W - RJ_PRE - RJ_FOLGA} - 9 * LEN ( _pre & _exig ) ) * 13 / 15, 0 ) -- geometria",
        R.nomes("_listaBranco", "_foraRod", "_pre", "_branco", "_pxRod"),
        "VAR _txtRod =",
        "    SWITCH (",
        "        TRUE (),",
        "        _dim <> \"Caixa\", SWITCH ( _dim, " + ", ".join(f'"{k}", {D.texto(v)}' for k, v in COMO_LER.items())
        + " ),",
        "        _exig = 0, \"nenhuma exigida: todo desembolso ficou dentro da tolerância\",",
        "        _branco = 0, IF ( _exig = 1, \"a única exigida está preenchida\", \"todas as \" & _exig & \" preenchidas\" ),",
        "        " + C.marca("_pre") + " & \" de \" & _exig & IF ( _exig = 1, \" preenchida · \", \" preenchidas · \" ) & _nbTxt",
        "    )",
        "VAR _htmlRotRod =",
        "    IF (",
        "        _dim = \"Caixa\",",
        "        \"<div class='bh'><span class='vs'>JUSTIFICATIVA NA PLANILHA</span><span class='vs'>EXIGIDA ACIMA DE ±10%</span>\"",
        "            & \"</div>\",",
        "        \"<span class='vs'>COMO LER</span>\"",
        "    )",
        "-- 4 · Marcação",
        "RETURN",
        "    IF (",
        "        NOT ISBLANK ( _dim ),",
        "        \"<div class='u tt'><div class='cab'><p class='vs'>ONDE A CARTEIRA PERDE PONTOS · \" & _mesCM & \"</p>\"",
        "            & \"<div class='tit'><b>\" & _dim & \"</b></div>\"",
        "            & \"<p class='vs dir'>\" & _txtDir & \"</p></div>\"",
        "            & \"<div class='corpo'>\" & _htmlFx",
        "            & \"<div class='bh'><span class='vs'>OBRA POR OBRA</span><span class='vs'>PONTOS</span></div>\"",
        "            & \"<div class='tab i\" & " + TL.atributos("_nLin") + "'>\" & _htmlLinhas & _htmlMais & \"</div></div>\"",
        "            & \"<div class='pe'><div class='rg'></div>\" & _htmlRotRod",
        "            & \"<p class='rod'>\" & " + D.esc("_txtRod") + " & \"</p>\"",
        "        & \"</div></div>\" & [Comum · JS contador tooltip]",
        "    )",
    ))

# ===================================================================================================== Mês
# v2 (Figma 390:1741), quatro estados da nota: quatro colunas com vão de 14; chip, 12 px, e uma obra por linha de 25
# (Segoe Semibold 15 + nota Barlow SemiBold 16 à direita; na pendente, "obtidos/possíveis" em grafite 14)
CSS_MES = (".tt .col4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));column-gap:14px}"
           ".tt .col4 .chip{margin-bottom:12px;width:max-content}"
           ".tt .col4 .ob{display:flex;justify-content:space-between;align-items:center;gap:6px;height:25px;"
           "white-space:nowrap}"
           ".tt .col4 .ob span:first-child{font-size:15px;font-weight:600;overflow:hidden;text-overflow:ellipsis}"
           ".tt .col4 .ob b{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:16px}"
           ".tt .col4 .ob b.pd{font-size:14px;color:#3B3B3F}")
# F4: a página passa a 760 (corpo de 720, colunas de ~170): "PONTA NEGRA" com a nota ou com "4,5/6,0" cabe sem
# reticências; as linhas de cada coluna ocupam a altura do corpo (a coluna mais longa dá o --n) e o nome cresce no
# máximo até 16 px (a coluna não alarga)
CSS_MES_LS = (".tt .col4.ls{display:grid;max-height:calc(var(--n,9) * var(--hm,36px) + 34px)}"
              ".tt .col4.ls>div{display:grid;grid-template-rows:auto repeat(var(--n,9),minmax(0,1fr));min-height:0}"
              ".tt .col4.ls .ob{height:auto;min-height:0}"
              ".tt .col4.ls .ob span:first-child{font-size:min(16px,max(13px,calc(15px * var(--k,1))))}"
              ".tt .col4.ls .ob b{font-size:max(13px,calc(16px * var(--k,1)))}"
              ".tt .col4.ls .ob b.pd{font-size:max(13px,calc(14px * var(--k,1)))}")
desenho("T1 · Tooltip mês · CSS", "CSS do tooltip do mês (F4: 760 de largura, linhas com escala, cascata de entrada).",
        "-- 4 · Marcação\n[T1 · CSS tooltip]\n    & " + dax_lit(CSS_MES + TL.css_escala({}, grade=True) + CSS_MES_LS
                                                       + TL.entrada(".tt .col4>div>:nth-child({k})")))
desenho(
    "T1 · Tooltip mês · HTML",
    "Tooltip de página do mês (coluna de Como os meses evoluíram): as obras em cada estado da nota (crítico, atenção, "
    "estável com a nota; pendente com os pontos obtidos dos possíveis) e quem entrou, saiu ou abriu em crítico desde o "
    "mês anterior, pela regra nova (só entre notas completas; ir de pendente a crítico é abrir). Primeiro mês do "
    f"histórico: a carteira no mês. Até {LISTA_MAX} obras num estado, todas aparecem; de {LISTA_MAX + 1} em diante, as "
    f"{LISTA_MOSTRA} primeiras e 'e mais N obras'. O pé fica preso à base do cartão.",
    linhas(
        "-- 1 · Leituras",
        "VAR _mesC = UPPER ( [Mês · rótulo curto] )",
        "VAR _mesL = [Mês · longo]",
        "VAR _mesAnt = [Mês anterior · nome]",
        "VAR _n = [Obras com análise] + 0",
        "VAR _primeiro = [Mês · é o primeiro do histórico] = 1",
        "VAR _res = [Resultado da obra]",
        "VAR _pct = [Resultado %]",
        "VAR _desv = [Desembolso · desvio no mês]",
        "VAR _maisC = [T1 · Tooltip mês · obras fora da lista · crítico]",
        "VAR _maisA = [T1 · Tooltip mês · obras fora da lista · atenção]",
        "VAR _maisE = [T1 · Tooltip mês · obras fora da lista · estável]",
        "VAR _maisP = [T1 · Tooltip mês · obras fora da lista · pendente]",
        # quem entrou, saiu ou abriu em crítico: contagens e listas das contas (mesma regra da leitura)
        "VAR _nE = [T1 · Leitura · obras que entraram em crítico] + 0",
        "VAR _nS = [T1 · Leitura · obras que saíram de crítico] + 0",
        "VAR _nAb = [T1 · Leitura · obras que abriram em crítico] + 0",
        "VAR _listaE = [T1 · Leitura · obras que entraram em crítico (lista)]",
        "VAR _listaS = [T1 · Leitura · obras que saíram de crítico (lista)]",
        "VAR _listaAb = [T1 · Leitura · obras que abriram em crítico (lista)]",
        "VAR _obras =",
        "    ADDCOLUMNS (",
        "        VALUES ( dObra[Obra] ),",
        "        \"@aba\", [Obras com análise],",
        "        \"@st\", [Nota · status · um mês],",
        "        \"@pend\", [Nota · pendente · um mês],",
        "        \"@nota\", [Nota · nota final · um mês],",
        "        \"@obt\", [Nota · pontos obtidos · um mês],",
        "        \"@poss\", [Nota · pontos possíveis · um mês],",
        "        \"@perd\", [Nota · pontos perdidos · um mês],",
        "        \"@notaAnt\", [T1 · Obra · nota no mês anterior]",
        "    )",
        "-- 2 · Textos",
        D.od_tabela(),
        D.rs("_res", "_tr") + D.pct("_pct", "_tp", casas=2, mais=True) + D.pct("_desv", "_tdv", casas=0, mais=True),
        "VAR _htmlCol =",
        "    CONCATENATEX (",
        "        { 2, 1, 0, -1 },",
        "        VAR _s = [Value]",
        "        VAR _lista = FILTER ( _obras, [@aba] = 1 && IF ( _s = -1, [@pend] = 1, NOT ISBLANK ( [@st] ) && [@st] = _s ) )"
        " /* lista */",
        "        VAR _mais = SWITCH ( _s, 2, _maisC, 1, _maisA, 0, _maisE, _maisP )",
        f"        /* passou de {LISTA_MAX} obras no estado: as {LISTA_MOSTRA} primeiras e a linha 'e mais N obras' */",
        f"        VAR _mostra = TOPN ( IF ( _mais > 0, {LISTA_MOSTRA}, {LISTA_MAX} ), _lista, [@perd], DESC, "
        "dObra[Obra], ASC ) /* lista */",
        "        VAR _cls = IF ( _s = -1, \"m\", _s & \"\" )",
        "        VAR _rot = SWITCH ( _s, 2, \"crítico\", 1, \"atenção\", 0, \"estável\", \"pendente\" )",
        "        VAR _itens =",
        "            CONCATENATEX (",
        "                _mostra,",
        "                VAR _txtV = IF ( _s = -1, " + fmt_pts("[@obt]") + " & \"/\" & " + fmt_pts("[@poss]") + ", "
        + fmt_pts("[@nota]") + " )",
        "                RETURN",
        "                    \"<div class='ob'><span>\" & dObra[Obra] & \"</span><b\" & IF ( _s = -1, \" class='pd'\", \"\" ) "
        "& \">\" & " + C.marca("_txtV") + " & \"</b></div>\",",
        "                \"\",",
        "                [@perd], DESC,",
        "                dObra[Obra], ASC",
        "            )",
        "        VAR _htmlMais = IF ( _mais > 0, \"<i class='vz mais'>e mais \" & " + C.marca('FORMAT ( _mais, "0" )') + " & \" obras</i>\" )",
        "        RETURN",
        "            \"<div><span class='chip chip\" & _cls & \"'><i></i>\" & _rot & \"</span>\"",
        "                & IF ( _itens = \"\", \"<i class='vz'>nenhuma</i>\", _itens & _htmlMais ) & \"</div>\",",
        "        \"\",",
        "        [Value], DESC",
        "    )",
        "VAR _nCol =",
        "    MAXX (",
        "        { 2, 1, 0, -1 },",
        "        VAR _s = [Value]",
        "        VAR _q = COUNTROWS ( FILTER ( _obras, [@aba] = 1 && IF ( _s = -1, [@pend] = 1, NOT ISBLANK ( [@st] ) && [@st] = _s ) ) ) + 0 /* lista */",
        f"        RETURN IF ( _q > {LISTA_MAX}, {LISTA_MOSTRA} + 1, MAX ( 1, _q ) )",
        "    ) /* geometria */",
        "VAR _mudaram = FILTER ( _obras, PATHCONTAINS ( _listaE, dObra[Obra] ) || PATHCONTAINS ( _listaS, dObra[Obra] ) ) /* lista */",
        "VAR _frases =",
        "    CONCATENATEX (",
        "        _mudaram,",
        "        dObra[Obra] & IF ( [@st] == 2, \" entrou em crítico\", \" saiu de crítico\" ) & \" (nota \" & "
        + C.marca(fmt_pts("[@notaAnt]")) + " & \" → \" & " + C.marca(fmt_pts("[@nota]")) + " & \")\",",
        "        \" · \",",
        "        [@st], DESC,",
        "        dObra[Obra], ASC",
        "    )",
        # quem teve a primeira nota completa já crítica: à parte, não conta como entrada
        lista_e("_listaAb", "_ab"),
        "VAR _txtAb = IF ( _nAb = 0, \"\", _abTxt & IF ( _nAb = 1, \" abriu em crítico\", \" abriram em crítico\" ) )",
        # pé de 2 linhas (auditoria, M3): até 2 eventos, a frase com a nota; de 3 em diante, os nomes por tipo — quem
        # entrou, saiu ou abriu nunca some
        "VAR _nTot = _nE + _nS + _nAb",
        "VAR _pE = IF ( _nE > 0, IF ( _nE = 1, \"entrou em crítico: \", \"entraram em crítico: \" ) & SUBSTITUTE ( _listaE, \"|\", \", \" ) )",
        "VAR _pS = IF ( _nS > 0, IF ( _nS = 1, \"saiu de crítico: \", \"saíram de crítico: \" ) & SUBSTITUTE ( _listaS, \"|\", \", \" ) )",
        "VAR _pA = IF ( _nAb > 0, IF ( _nAb = 1, \"abriu em crítico: \", \"abriram em crítico: \" ) & SUBSTITUTE ( _listaAb, \"|\", \", \" ) )",
        "VAR _txtCompacto = _pE & IF ( _pE <> \"\" && _pS & _pA <> \"\", \" · \" ) & _pS & IF ( _pS <> \"\" && _pA <> \"\", \" · \" ) & _pA",
        "VAR _txtDesde =",
        "    SWITCH (",
        "        TRUE (),",
        "        _nTot = 0, \"nenhuma obra entrou ou saiu de crítico\",",
        "        _nTot > 2, _txtCompacto,",
        "        _nE + _nS = 0, _txtAb,",
        "        _nAb > 0, _frases & \" · \" & _txtAb,",
        "        _nE = 0, _frases & \" · nenhuma obra entrou\",",
        "        _nS = 0, _frases & \" · nenhuma saiu\",",
        "        _frases",
        "    )",
        "VAR _txtSob = \"OBRAS POR STATUS DA NOTA · \" & _mesC & IF ( _primeiro, \" · PRIMEIRO MÊS DO HISTÓRICO\", \"\" )",
        "VAR _txtCart = \"resultado \" & " + ng_span(C.marca("_trTxt"), "_res < 0") + " & \" (\" & "
        + ng_span(C.marca("_tpTxt"), "ROUND ( _pct * 100, 2 ) < 0") + " & \") · desembolso \" & " + C.marca("_tdvTxt")
        + " & \" sobre o previsto\"",
        "-- 4 · Marcação",
        "RETURN",
        "    IF (",
        "        _n > 0,",
        "        \"<div class='u tt'><div class='cab'><p class='vs'>\" & _txtSob & \"</p>\"",
        # sem a meta "N OBRAS COM ABA · X SEM PLANILHA" (pedido do Alisson, 07/10/2026): só sobretítulo e título
        "            & \"<div class='tit'><b>\" & _mesL & \"</b></div></div>\"",
        "            & \"<div class='corpo'><div class='col4\" & " + TL.atributos("_nCol") + "'>\" & _htmlCol & \"</div></div>\"",
        "            & \"<div class='pe'><div class='rg'></div>\"",
        "            & IF (",
        "                _primeiro,",
        "                \"<span class='vs'>CARTEIRA NO MÊS</span><p class='rod r2'>\" & _txtCart & \"</p>\",",
        "                \"<span class='vs'>DESDE \" & UPPER ( _mesAnt ) & \"</span><p class='rod r2'>\" & _txtDesde & \"</p>\"",
        "            )",
        "        & \"</div></div>\" & [Comum · JS contador tooltip]",
        "    )",
    ))

if __name__ == "__main__":
    sys.exit(gravar([x for x in MEDIDAS if x.nome not in RETIRADAS], RAIZ / "dax" / "T1" / "Tooltips", GERADO))

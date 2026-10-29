#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""leituras_t3 — desenho das leituras do "?" e do guia da Tela 03 · Avanço físico (pbi/dax/T3/Leituras/**). As contas
que elas leem estão em contas_t3.py (T3 Avanço físico\\…\\Contas) e em base/.

Redesenho v2 (Figma FjBWDk5odF9HaZ2pwhGosl, página 04 · Redesenho v2, seção 379:790, Fileira · Leituras e guia
388:4067; pbi/spec/redesenho/t03.md): Leitura · T3 · v2 · Curva S 391:10160 (900 × 370, duas colunas 500 + 320),
Ritmo do mês 391:10201 (568 × 290, condensada), Avanço das obras 392:6436 (568 × 437, sem a explicação), Linha do
tempo das obras 392:6473 (900 × 357, duas colunas), sem previsto (JANGADA) 394:8908 e 394:8944, Guia · T3 · v2
395:6438 (1120, duas colunas, centrado, véu 55 %). L065: a leitura cobre o painel que explica (o HTML Content tem o
retângulo exato do painel, sem margem nem sombra; × = leituras_lib.X_SVG). L058: cada número aparece uma vez por leitura.
Escala v2: sobretítulo versalete 12, achado Barlow 23/28 (grande) ou 21/26 (pequena), explicação Segoe 17/26,
destaques Barlow 34/40 com rótulo 14/19 em caixa creme, "o que explica" Segoe 15/21, "como ler" 14/19. O que saiu com
a fonte maior (não volta): Curva S, o "Mouse num mês…" do como ler; Ritmo, a explicação longa (fica uma frase);
Avanço, a explicação; Linha do tempo, a 2.ª frase do "o que explica" e o código e o m² da tabela das a iniciar.

F4 (pedido do Alisson, 28/10/2026): os números que ainda eram texto fixo (limite e pontos da nota no "como ler", meta
e pontos do PPC, atraso, previsto da carteira, crédito, orçamento das a iniciar) entram marcados com C.marca() e o
desenho() converte a medida com C.envolver_marcas(); meses do detalhe, eixo, marcas da trajetória e linhas das a
iniciar entram com as classes genéricas do CSS base (.a-fd, .a-gx, .a-pop) em cascata. Datas e anos não contam.

Troca da régua pela nota (13/10/2026): o físico é lido pelo item prazo da nota ([T3 · Status desvio físico]:
dentro ou fora do limite); o limite, o peso do item e a nota máxima vêm de [Nota · limite prazo · ponto cheio],
[T3 · Prazo · máximo na nota] e [Nota · nota · máximo] (nenhum número da nota escrito aqui). A mobilização sai.

    python -X utf8 pbi/scripts/leituras_t3.py
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import contador as C  # noqa: E402
import desenho_projeto as D  # noqa: E402
import desenho_comum as DC  # noqa: E402
from contas_lib_projeto import Medida, gravar  # noqa: E402
from desenho_comum import CREME, GRAFITE, PRETO, REGRA, SALVIA, VERM, dax_lit  # noqa: E402
from leituras_lib import CSS_X, X_SVG  # noqa: E402

RAIZ = AQUI.parent
GERADO = "pbi/scripts/leituras_t3.py"
MEDIDAS: list[Medida] = []
DES = r"T3 Avanço físico\Leituras"
X = X_SVG


def desenho(nome, descricao, dax):
    """Medida de desenho; os valores marcados com C.marca() viram odômetro no fim (F4)."""
    MEDIDAS.append(Medida(nome, DES, "texto", descricao, C.envolver_marcas(dax)))


def linhas(*ls) -> str:
    return "\n".join(l for g in ls for l in (g if isinstance(g, list) else [g]))


def ext(v: str, fem: bool = True) -> str:
    nomes = (["nenhuma", "uma", "duas"] if fem else ["nenhum", "um", "dois"]) + \
        ["três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez", "onze", "doze"]
    casos = ", ".join(f'{i}, "{n}"' for i, n in enumerate(nomes))
    return f'SWITCH ( {v}, {casos}, FORMAT ( {v}, "0" ) )'


def cap(v: str) -> str:
    return f"UPPER ( LEFT ( {v}, 1 ) ) & MID ( {v}, 2, 1000 )"


def nome_mes(v: str) -> str:
    return f'FORMAT ( {v}, "mmmm", "pt-BR" )'


def abrev(v: str) -> str:
    return f'FORMAT ( {v}, "mmm", "pt-BR" )'


def mes_ano(v: str) -> str:
    return f'FORMAT ( {v}, "mmm/yy", "pt-BR" )'


def em_meses(n: str) -> str:
    """'em oito meses' (n = meses da obra na janela): no lugar do 'do semestre' fixo (a janela vai de 1 a 12 meses)."""
    return f'"em " & {ext(n, fem=False)} & " meses"'


def nos_meses(n: str) -> str:
    return f'"nos " & {ext(n, fem=False)} & " meses"'


def em_todos(n: str) -> str:
    return f'"em todos os " & {ext(n, fem=False)} & " meses"'


def desde(d: str) -> str:
    """Mês de um 'desde': por extenso; mês/ano quando bate no começo da janela (_jan) ou cai em outro ano que a
    referência (_ref) — 'desde jan/26'. A medida precisa das VAR _jan e _ref."""
    return (f'IF ( {d} = _jan || YEAR ( {d} ) <> YEAR ( _ref ), FORMAT ( {d}, "mmm/yy", "pt-BR" ), '
            f'FORMAT ( {d}, "mmmm", "pt-BR" ) )')


def lista_e(v: str, p: str, n: str | None = None) -> list[str]:
    """{p}Txt = "A, B e C" a partir de "A|B|C"; {p}N = quantos nomes (só decide o texto). Com `n` (conta de quantidade
    da mesma lista), o número vem da conta; sem ele, conta os nomes da lista."""
    contagem = (f"VAR {p}N = {n}" if n else
                f'VAR {p}N = IF ( ISBLANK ( {v} ) || {v} = "", 0, PATHLENGTH ( {v} ) )')
    return [
        contagem,
        f'VAR {p}Pos = IF ( {p}N >= 2, FIND ( "§", SUBSTITUTE ( {v}, "|", "§", {p}N - 1 ) ) )',
        f'VAR {p}Txt = SWITCH ( TRUE (), {p}N = 0, "", {p}N = 1, {v}, '
        f'SUBSTITUTE ( LEFT ( {v}, {p}Pos - 1 ), "|", ", " ) & " e " & MID ( {v}, {p}Pos + 1, 999 ) )',
    ]


def painel(classe: str, aria: str, corpo: str, script: str) -> str:
    return (f'"<div class=\'u lv\' role=\'dialog\' aria-label=\'" & {aria} & "\'><div class=\'pn {classe}\'>" '
            f'& {corpo} & "</div>{X}</div>" & {script}')


def destaques(*itens: tuple[str, str]) -> str:
    return ("\"<div class='dst sobre-creme'>\" & " + " & ".join(
        f"\"<div><b>\" & {n} & \"</b><span>\" & {r} & \"</span></div>\"" for n, r in itens) + " & \"</div>\"")


def bloco(rotulo_dax: str, conteudo: str) -> str:
    return f"\"<div class='sec'><span class='vs'>\" & {rotulo_dax} & \"</span>\" & {conteudo} & \"</div>\""


JS = "[Comum · JS contador tooltip] & [Comum · JS corrida]"

# ===================================================================================================== 4.1 Curva S
FAIXA_EM = 'IF ( {v} = 2, "fora do limite", "dentro do limite" )'
MUDANCA = """IF ( _para = 2, "passou do limite da nota em " & _nm, "em " & _nm & " voltou para dentro do limite" )"""
# o limite, o peso do item e a nota máxima são lidos das medidas da nota (VAR _tl, _tMax e _tNota da leitura)
# (Fase 3 da régua antiga: mais curto, para a coluna caber no 898 × 368 com as justificativas)
COMO_LER_CURVA = ('"<p class=\'cl\'>Tracejado = previsto; sólido = executado; a área entre eles é o atraso. Na nota '
                  'vale o atraso em meses: até " & ' + C.marca("_tl") + ' & ", " & ' + C.marca("_tMax") + ' & " pontos; '
                  'os pontos caem até zero com mais de " & ' + C.marca("_ttv") + ' & ", e a obra fica crítica.</p>"')
COMO_LER_SEM_P = ("<p class='cl'>Sólido = executado acumulado, em % do orçamento. Sem previsto na planilha não há "
                  "tracejado nem área de atraso; o desvio e o ponto do físico na nota ficam vazios.</p>")

desenho(
    "T3 · Leitura curva · HTML",
    "Leitura do \"?\" da Curva S, sobre o próprio painel (L065, Figma 317:5115, 1028 × 402, duas colunas): achado com o "
    "desvio e a tendência da distância, explicação (ritmo executado × previsto, o que o cronograma pede, a trajetória "
    "do físico na nota na janela: dentro ou fora do limite), três destaques que contam, como ler; à direita o que explica (justificativas da "
    "planilha) e o detalhe do desvio mês a mês na janela, com o limite da nota (as barras correm; x pela posição "
    "na janela). Obra sem previsto na planilha (Figma 352:7993): achado com o executado e a falta do previsto, sem "
    "desvio nem faixa, e o detalhe vira o executado do mês, mês a mês. Só lê contas.",
    linhas(
        "-- 1 · Leituras",
        "VAR _obra = [Nota · obra em foco]",
        "VAR _mesL = [Mês de referência · longo]",
        "VAR _mesN = [Mês de referência · nome]",
        "VAR _ref = [Mês de referência]",
        "VAR _jan = [Série · primeiro mês]",
        "VAR _nJan = [Série · meses até a referência]",
        "VAR _d = [Físico · desvio acumulado p.p. · foco]",
        "VAR _e = [Físico · executado acumulado · foco]",
        "VAR _s = [T3 · Status desvio físico · foco]",
        "VAR _lim = [Nota · limite prazo · ponto cheio]",
        "VAR _maxFF = [T3 · Prazo · máximo na nota]",
        "VAR _trv = [Nota · limite prazo · trava]",
        "VAR _notaMax = [Nota · nota · máximo]",
        "VAR _td = [T3 · Físico · tendência da distância · foco]",
        "VAR _tdd0 = [T3 · Físico · tendência da distância desde · foco]",
        # o atraso não "cresce desde maio" quando só começou em junho: o "desde" é o mais tarde entre o início da
        # tendência e o 1º mês da sequência atrás do cronograma (auditoria da Fase 3, rodada 2, m5)
        "VAR _iniLado = [T3 · Físico · sinal · início da sequência · foco]",
        "VAR _tdd = IF ( NOT ISBLANK ( _iniLado ) && _iniLado > _tdd0, _iniLado, _tdd0 )",
        "VAR _abx = [T3 · Ritmo · executa abaixo desde · foco]",
        "VAR _acm = [T3 · Ritmo · executa acima desde · foco]",
        "VAR _pm1 = [T3 · Série · primeiro mês da obra · foco]",
        "VAR _n = [T3 · Série · meses da obra · foco]",
        "VAR _tp = [T3 · Ritmo · tendência do previsto · foco]",
        "VAR _te = [T3 · Ritmo · tendência do executado · foco]",
        "VAR _alc = [T3 · Ritmo · meses que alcançaram o previsto · foco]",
        "VAR _mMax = [T3 · Série · mês de maior executado · foco]",
        "VAR _eMax = [T3 · Série · executado no mês de maior executado · foco]",
        "VAR _mud = [T3 · Físico · mudanças de faixa (lista) · foco]",
        "VAR _ms = [T3 · Físico · maior status na série · foco]",
        "VAR _d1 = [T3 · Curva S · desvio no primeiro mês · foco]",
        "VAR _s1 = [T3 · Curva S · status no primeiro mês · foco]",
        "VAR _eMin = [T3 · Série · executado no mês de menor executado · foco]",
        "VAR _mMin = [T3 · Série · mês de menor executado · foco]",
        "VAR _des = [Desembolsado acumulado · foco]",
        "VAR _cred = [Crédito do orçamento · foco]",
        "VAR _jus = [T3 · Justificativas · grupos (lista) · foco]",
        "VAR _nAcima = [T3 · Justificativas · meses acima do previsto · foco]",
        "VAR _ddRef = [Desembolso · desvio no mês · foco]",
        "VAR _meses =",
        "    ADDCOLUMNS (",
        "        VALUES ( dMes[Mes] ),",
        "        \"@ate\", [Série · mês até a referência],",
        "        \"@pj\", [Série · posição na janela],",
        "        \"@d\", [T3 · Desvio físico p.p. · foco no mês],",
        "        \"@s\", [T3 · Status desvio físico · foco no mês],",
        "        \"@em\", [Físico · executado no mês · foco no mês],",
        "        \"@rot\", [Mês · abreviado]",
        "    )",
        "-- 2 · Textos",
        "VAR _semP = ISBLANK ( _d )",
        "VAR _dA = ABS ( _d )",
        D.pp("_d", "_td") + D.pp("_d1", "_td1") + D.pct("_eMin", "_tem", casas=2) + D.pct("_eMax", "_tex", casas=2)
        + D.pct("_e", "_tea") + D.rs("_des", "_tds") + D.rs("_cred", "_tcr"),
        D.od_tabela(),
        "VAR _txtSob = \"LEITURA · CURVA S · \" & " + D.esc("UPPER ( _obra )") + " & \" · \" & UPPER ( _mesL )",
        "VAR _tl = FORMAT ( _lim, IF ( _lim = INT ( _lim ), \"0\", \"0.0\" ), \"pt-BR\" ) & IF ( _lim <= 1, \" mês\", \" meses\" )",
        "VAR _tMax = FORMAT ( _maxFF, \"0.0#\", \"pt-BR\" )",
        "VAR _ttv = FORMAT ( _trv, \"0\", \"pt-BR\" ) & IF ( _trv <= 1, \" mês\", \" meses\" )",
        "VAR _tNota = FORMAT ( _notaMax, \"0\", \"pt-BR\" )",
        "VAR _txtTend =",
        "    SWITCH (",
        "        TRUE (),",
        "        _d >= 0, \".\",",
        "        _td = \"cresce\", \", e o atraso cresce desde \" & " + desde("_tdd") + " & \".\",",
        "        _td = \"cai\", \", e o atraso vem caindo desde \" & " + desde("_tdd") + " & \".\",",
        "        _td = \"oscila\", \", e o atraso oscila desde \" & " + desde("_tdd") + " & \".\",",
        "        \".\"",
        "    )",
        "VAR _lado = IF ( _d < 0, \" p.p. atrás do cronograma\", \" p.p. à frente do cronograma\" )",
        "-- o número-chave do achado conta (contador): o núcleo é o |desvio| com uma casa, sem sinal",
        "VAR _tkN = FORMAT ( _dA, \"0.0\", \"pt-BR\" )",
        "VAR _tkTxt = IF ( ISBLANK ( _dA ), \"—\", _tkN )",
        D.od_num("_dA", "_tk") + D.od_pp("_d", "_td") + D.od_pct("_e", "_tea"),
        "VAR _achado =",
        "    SWITCH (",
        "        TRUE (),",
        "        _semP, \"A \" & " + D.esc("_obra") + " & \" fecha \" & _mesN & \" com \" & _teaOd",
        "            & \" executado, mas a planilha não traz o previsto: não há cronograma para medir atraso.\",",
        "        ROUND ( _d, 1 ) = 0, \"A \" & " + D.esc("_obra") + " & \" fecha \" & _mesN & \" no ritmo do cronograma (\" & _tdOd & \").\",",
        "        \"A \" & " + D.esc("_obra") + " & \" fecha \" & _mesN & \" \" & _tkOd & _lado & _txtTend",
        "    )",
        "VAR _txtE1 =",
        "    SWITCH (",
        "        TRUE (),",
        "        NOT ISBLANK ( _abx ),",
        "            \"A obra executa menos do que o previsto desde \"",
        "                & IF ( _abx = _pm1 && _pm1 > _jan, \"a primeira aba, em \" & " + nome_mes("_pm1") + ", "
        + desde("_abx") + " ) & \".\",",
        "        NOT ISBLANK ( _acm ),",
        "            \"A obra executa o previsto ou mais desde \"",
        "                & IF ( _acm = _pm1 && _pm1 > _jan, \"a primeira aba, em \" & " + nome_mes("_pm1") + ", "
        + desde("_acm") + " ) & \".\",",
        "        \"\"",
        "    )",
        "VAR _txtRitmo = SWITCH ( _tp, \"acelera\", \"acelera a cada mês\", \"desacelera\", \"desacelera a cada mês\", "
        "\"constante\", \"é constante\", \"varia de mês a mês\" )",
        "VAR _txtE2 =",
        "    \" O cronograma pede um ritmo que \" & _txtRitmo",
        "        & IF (",
        "            _alc = 0,",
        "            \" e a execução não acompanhou: nem no melhor mês, \" & " + nome_mes("_mMax") + " & \", ela alcançou o "
        "previsto.\",",
        "            \"; a execução alcançou o previsto em \" & " + ext("_alc", fem=False) + " & \" dos \" & "
        + ext("_n", fem=False) + " & \" meses.\"",
        "        )",
        "VAR _nMud = IF ( ISBLANK ( _mud ) || _mud = \"\", 0, PATHLENGTH ( _mud ) )",
        "VAR _frases =",
        "    CONCATENATEX (",
        "        GENERATESERIES ( 1, MAX ( _nMud, 1 ) ),",
        "        VAR _it = SUBSTITUTE ( PATHITEM ( _mud, [Value] ), \"§\", \"|\" )",
        "        VAR _nm = PATHITEM ( _it, 1 )",
        "        VAR _de = PATHITEM ( _it, 3, INTEGER )",
        "        VAR _para = PATHITEM ( _it, 4, INTEGER )",
        "        VAR _nf = PATHITEM ( _it, 5, INTEGER )",
        "        VAR _sep = IF ( [Value] = 1, \"\", IF ( [Value] = _nMud, \" e \", \", \" ) )",
        "        RETURN",
        "            _sep & " + MUDANCA,
        "                & IF ( [Value] < _nMud && _nf >= 2, \", ficou \" & " + ext("_nf", fem=False) + " & \" meses \" & "
        + FAIXA_EM.format(v="_para") + ", \"\" ),",
        "        \"\",",
        "        [Value], ASC",
        "    )",
        "VAR _txtE3 =",
        "    IF (",
        "        _nMud = 0,",
        "        IF ( _ms = 2, \" O atraso ficou acima do limite da nota \" & IF ( _n = 1, \"no único mês\", " + em_todos("_n") + " ), "
        "\" O atraso nunca passou do limite da nota \" & IF ( _n = 1, \"no único mês\", " + nos_meses("_n") + " ) ) & \".\",",
        "        \" O físico \" & _frases & \".\"",
        "    )",
        "VAR _txtExecMes = SWITCH ( _te, \"cresce\", \"cresce\", \"cai\", \"cai\", \"constante\", \"se repete\", \"oscila\" )",
        "VAR _explica =",
        "    IF (",
        "        _semP,",
        "        \"As abas trazem o previsto em branco: a curva mostra só o executado, sem área de atraso, e o desvio e o \"",
        "            & \"ponto do físico ficam vazios — não valem zero.\",",
        "        _txtE1 & _txtE2 & _txtE3",
        "    )",
        "VAR _rotD1 = \"desvio em \" & " + nome_mes("_pm1") + " & \", \"",
        "    & IF ( _s1 = 2, \"já fora do limite\", IF ( _s = 2, \"ainda dentro do limite\", \"dentro do limite\" ) )",
        "VAR _rotMin = \"executado no mês mais fraco, \" & " + nome_mes("_mMin"),
        "VAR _rotMax = \"executado no melhor mês, \" & " + nome_mes("_mMax"),
        "VAR _rotD3 = \"pagos até \" & _mesN & \"; \" & " + C.marca("_tcrTxt") + " & \" de obra executada\"",
        D.od_pp("_d1", "_td1") + D.od_pct("_eMin", "_tem") + D.od_pct("_eMax", "_tex") + D.od_rs("_des", "_tds"),
        "VAR _g1 = SUBSTITUTE ( PATHITEM ( _jus, 1 ), \"§\", \"|\" )",
        "VAR _g2 = SUBSTITUTE ( PATHITEM ( _jus, 2 ), \"§\", \"|\" )",
        "VAR _t1 = PATHITEM ( _g1, 1 )",
        "VAR _t2 = PATHITEM ( _g2, 1 )",
        "VAR _n1 = PATHITEM ( _g1, 2, INTEGER )",
        "VAR _n2 = PATHITEM ( _g2, 2, INTEGER )",
        # a justificativa entra inteira até 72 caracteres (F4, 28/10/2026: nada com reticências; as da planilha fictícia têm
        # até ~70). Só a primeira é citada; a segunda vira "por outro motivo" (com as duas inteiras e o fecho, a frase
        # passaria das 5 linhas do "O QUE EXPLICA", coluna de 320). Acima de 72 caracteres (planilha real), o corte num
        # espaço com "…" fica como proteção. Texto todo em maiúsculas fica como foi digitado.
        *[l for i in (1,) for l in (
            f"VAR _t{i}s = IF ( RIGHT ( _t{i}, 1 ) = \".\", LEFT ( _t{i}, LEN ( _t{i} ) - 1 ), _t{i} )",
            f"VAR _t{i}m = IF ( EXACT ( UPPER ( _t{i}s ), _t{i}s ), _t{i}s, LOWER ( LEFT ( _t{i}s, 1 ) ) & MID ( _t{i}s, 2, LEN ( _t{i}s ) ) )",
            f"VAR _t{i}e = SEARCH ( \" \", _t{i}m, 56, 0 )",
            f"VAR _t{i}L = IF ( LEN ( _t{i}m ) <= 72, _t{i}m, LEFT ( _t{i}m, IF ( _t{i}e > 0 && _t{i}e <= 71, _t{i}e - 1, 70 ) ) & \"…\" )")],
        "VAR _txtOqe =",
        "    SWITCH (",
        "        TRUE (),",
        "        _nAcima = 0, \"O desembolso acompanhou o previsto em todos os meses; o atraso não veio de falta de dinheiro.\",",
        "        ISBLANK ( _jus ) || _jus = \"\", \"A planilha não traz justificativa para o desembolso acima do previsto em "
        "nenhum mês.\",",
        # obra atrasada e gastando acima do previsto: só a 1ª justificativa e um fecho curto (auditoria da Fase 3, MJ1: com
        # as duas e o fecho longo, a frase passava de 360 caracteres e o "como ler" saía do painel de 368 px)
        "        _d < 0 && _ddRef > 0,",
        "            \"Pela planilha, o gasto acima do previsto foi justificado em \" & IF ( _n1 = 1, \"um mês\", "
        + ext("_n1", fem=False) + " & \" meses\" ) & \" como \" & _t1L",
        "            & IF ( RIGHT ( _t1L, 1 ) = \"…\", \" \", \". \" ) & \"A obra paga para recuperar o prazo.\",",
        "        ISBLANK ( _t2 ) || _t2 = \"\",",
        "            \"Pela planilha, o gasto acima do previsto foi justificado em \" & IF ( _n1 = 1, \"um mês\", "
        + ext("_n1", fem=False) + " & \" meses\" ) & \" como \" & _t1L & IF ( RIGHT ( _t1L, 1 ) = \"…\", \"\", \".\" ),",
        "        \"Pela planilha, o gasto acima do previsto foi justificado em \" & IF ( _n1 = 1, \"um mês\", "
        + ext("_n1", fem=False) + " & \" meses\" ) & \" como \" & _t1L",
        "            & IF ( RIGHT ( _t1L, 1 ) = \"…\", \" \", \"; \" ) & \"em \" & IF ( _n2 = 1, \"outro mês\", "
        + ext("_n2", fem=False) + " & \" meses\" ) & \", por outro motivo.\"",
        "    )",
        "-- 3 · Geometria",
        "VAR _serie = FILTER ( _meses, [@ate] = 1 ) /* lista */",
        "VAR _com = FILTER ( _serie, NOT ISBLANK ( [@d] ) ) /* lista */",
        "VAR _colW = INT ( DIVIDE ( 220, _nJan ) ) /* geometria */",
        "VAR _bw = MIN ( 18, _colW - 8 ) -- geometria",
        "VAR _maxPos = MAXX ( _com, MAX ( [@d], 0 ) ) /* geometria */",
        # altura FIXA (auditoria da Fase 3, MJ1): 8 px de folga no topo e 40 px de barras, que positivas e negativas
        # dividem numa escala só (até 10 px por p.p.); o lado negativo vai pelo menos até o limite da nota, para a
        # linha tracejada caber sempre. Antes a altura crescia com o maior desvio e empurrava o "COMO LER" para fora.
        "VAR _maxNeg = MAXX ( _com, MAX ( - [@d], 0 ) ) /* geometria */",
        "VAR _negSpan = MAX ( _maxNeg, 1 ) /* geometria */",
        "VAR _k = MIN ( 10, DIVIDE ( 40, _maxPos + _negSpan ) ) /* geometria */",
        "VAR _base = 8 + ROUND ( _maxPos * _k, 0 ) /* geometria */",
        "VAR _yMes = 8 + 40 + 6 /* geometria */",
        "VAR _alt = _yMes + 16 /* geometria */",
        "VAR _colE = INT ( DIVIDE ( 320, _nJan ) ) /* geometria */",
        "VAR _bwE = MIN ( 20, _colE - 10 ) -- geometria",
        "VAR _maxEm = MAXX ( _serie, [@em] ) /* geometria */",
        "VAR _barras =",
        "    CONCATENATEX (",
        "        _serie,",
        "        VAR _v = [@d]",
        "        VAR _x = ( [@pj] - 1 ) * _colW /* geometria */",
        "        VAR _zero = NOT ISBLANK ( _v ) && ROUND ( _v, 1 ) = 0 -- geometria",
        "        VAR _h = IF ( ISBLANK ( _v ), 0, IF ( _zero, 2, MAX ( 1, ROUND ( ABS ( _v ) * _k, 0 ) ) ) ) /* geometria */",
        "        VAR _atraso = 300 + ( [@pj] - 1 ) * 120 /* geometria */",
        "        RETURN",
        "            \"<span class='ms a-fd' style='left:\" & _x & \"px;width:\" & _colW & \"px;top:\" & _yMes & \"px;animation-delay:\" & _atraso "
        "& \"ms'>\" & [@rot] & \"</span>\"",
        "                & IF (",
        "                    NOT ISBLANK ( _v ),",
        "                    \"<i class='b \" & IF ( _zero, \"z\", \"s\" & [@s] ) & \"' style='left:\" & ( _x + INT ( ( _colW - _bw ) / 2 ) )",
        "                        & \"px;width:\" & _bw & \"px;\" & IF ( _v >= 0, \"top:auto;bottom:\" & ( _alt - _base ), \"top:\" & _base )",
        "                        & \"px;height:\" & _h & \"px' data-rk='c\" & [@pj] & \"' data-rp='height' data-rd='\" & _atraso & \"'></i>\"",
        "                ),",
        "        \"\",",
        "        [@pj], ASC",
        "    )",
        "VAR _barrasE =",
        "    CONCATENATEX (",
        "        _serie,",
        "        VAR _x = ( [@pj] - 1 ) * _colE /* geometria */",
        "        VAR _h = IF ( ISBLANK ( [@em] ), 0, MAX ( 1, ROUND ( DIVIDE ( [@em], _maxEm ) * 30, 0 ) ) ) /* geometria */",
        "        VAR _atraso = 300 + ( [@pj] - 1 ) * 120 /* geometria */",
        "        RETURN",
        "            \"<span class='ms a-fd' style='left:\" & _x & \"px;width:\" & _colE & \"px;top:40px;animation-delay:\" & _atraso & \"ms'>\" "
        "& [@rot] & \"</span>\"",
        "                & IF (",
        "                    NOT ISBLANK ( [@em] ) && _h > 0,",
        "                    \"<i class='b e' style='left:\" & ( _x + INT ( ( _colE - _bwE ) / 2 ) ) & \"px;width:\" & _bwE",
        "                        & \"px;top:auto;bottom:22px;height:\" & _h & \"px' data-rk='c\" & [@pj] & \"' data-rp='height' data-rd='\"",
        "                        & _atraso & \"'></i>\"",
        "                ),",
        "        \"\",",
        "        [@pj], ASC",
        "    )",
        "-- 4 · Marcação",
        "VAR _htmlDet =",
        "    IF (",
        "        _semP,",
        "        \"<div class='bp' style='height:56px'>\" & _barrasE & \"<i class='ax a-gx' style='top:34px;width:320px'></i></div>\",",
        "        \"<div class='bp' style='height:\" & _alt & \"px'>\" & _barras",
        "            & \"</div>\"",
        "    )",
        "VAR _rotDet = IF ( _semP, \"DETALHE · EXECUTADO NO MÊS · %\", \"DETALHE · DESVIO MÊS A MÊS · P.P.\" )",
        "VAR _htmlDst =",
        "    IF (",
        "        _semP,",
        "        " + destaques(("_temOd", "_rotMin"), ("_texOd", "_rotMax"), ("_tdsOd", "_rotD3")) + ",",
        "        " + destaques(("IF ( ROUND ( _d1, 1 ) < 0, \"<span class='ng'>\" & _td1Od & \"</span>\", _td1Od )", "_rotD1"), ("_temOd", "_rotMin"), ("_tdsOd", "_rotD3")),
        "    )",
        "VAR _esq =",
        "    \"<div class='esq'><span class='vs sob'>\" & _txtSob & \"</span><h2 class='ach'>\" & _achado & \"</h2>\"",
        "        & \"<p class='exp'>\" & _explica & \"</p>\" & _htmlDst",
        "    & \"</div>\"",
        "VAR _dir =",
        "    \"<div class='dir'>\" & " + bloco('"O QUE EXPLICA"', "\"<p class='oqe oq5'>\" & _txtOqe & \"</p>\""),
        "        & " + bloco("_rotDet", "_htmlDet"),
        "        & " + bloco('"COMO LER"', "IF ( _semP, " + D.texto(COMO_LER_SEM_P) + ", " + COMO_LER_CURVA + " )"),
        "    & \"</div>\"",
        "VAR _corpo = \"<div class='cols'>\" & _esq & _dir & \"</div>\"",
        "RETURN",
        "    IF ( NOT ISBLANK ( _e ), " + painel("pn-g", '"Leitura da Curva S"', "_corpo", JS) + " )",
    ))

# ===================================================================================================== 4.2 PPC mês a mês
# F3 (docs/08 §5): a leitura do Ritmo do mês saiu com o painel; a do PPC mês a mês diz onde o PPC da obra em foco está
# diante da meta (o ponto cheio do item PPC da nota), quantos meses da janela chegaram a ela e desde quando está abaixo,
# e liga o PPC ao atraso em meses (o sinal que chega antes).
desenho(
    "T3 · Leitura PPC · HTML",
    "Leitura do \"?\" do PPC mês a mês, sobre o próprio painel (L065, mesma geometria da antiga leitura do Ritmo): "
    "achado com o PPC do mês de referência diante da meta e os pontos do item, explicação (quantos meses da janela "
    "chegaram à meta, desde quando está abaixo, o atraso em meses de hoje) e três destaques: o melhor e o mais fraco "
    "mês da janela e a média das obras no mês. Sem PPC na base: achado que diz a falta. Só lê contas.",
    linhas(
        "-- 1 · Leituras",
        "VAR _obra = [Nota · obra em foco]",
        "VAR _mesL = [Mês de referência · longo]",
        "VAR _mesN = [Mês de referência · nome]",
        "VAR _ref = [Mês de referência]",
        "VAR _jan = [Série · primeiro mês]",
        "VAR _ppc = [Canteiro · PPC · foco]",
        "VAR _pt = [Nota · pontos PPC · foco]",
        "VAR _ps = [Nota · possíveis · PPC · foco]",
        "VAR _meta = [Nota · limite PPC · ponto cheio]",
        "VAR _nCom = [T3 · PPC · meses com PPC · foco]",
        "VAR _nMeta = [T3 · PPC · meses na meta · foco]",
        "VAR _desde = [T3 · PPC · abaixo da meta desde · foco]",
        "VAR _vMax = [T3 · PPC · maior na janela · foco]",
        "VAR _mMax = [T3 · PPC · mês do maior · foco]",
        "VAR _vMin = [T3 · PPC · menor na janela · foco]",
        "VAR _mMin = [T3 · PPC · mês do menor · foco]",
        "VAR _media = [T3 · PPC · média das obras · ref]",
        "VAR _atr = [Prazo · atraso (meses) · foco]",
        "-- 2 · Textos",
        D.pct("_ppc", "_tc", casas=0) + D.pct("_meta", "_tm", casas=0) + D.pct("_vMax", "_tmx", casas=0)
        + D.pct("_vMin", "_tmi", casas=0) + D.pct("_media", "_tmd", casas=0),
        "VAR _tkTxt = " + C.marca("FORMAT ( _pt, \"" + DC.FMT_PTS + "\", \"pt-BR\" )") + " & \" de \" & "
        + C.marca("FORMAT ( _ps, \"" + DC.FMT_PTS + "\", \"pt-BR\" )"),
        "VAR _atA = ROUND ( ABS ( _atr ), 1 )",
        "VAR _txtAtr = " + C.marca("FORMAT ( _atA, \"0.0\", \"pt-BR\" )") + " & IF ( _atA <= 1, \" mês\", \" meses\" )",
        D.od_tabela(),
        D.od_pct("_ppc", "_tc") + D.od_pct("_vMax", "_tmx") + D.od_pct("_vMin", "_tmi") + D.od_pct("_media", "_tmd"),
        "VAR _txtSob = \"LEITURA · PPC MÊS A MÊS · \" & " + D.esc("UPPER ( _obra )") + " & \" · \" & UPPER ( _mesL )",
        "VAR _naMeta = ROUND ( _ppc, 2 ) >= _meta",
        "VAR _achado =",
        "    \"Em \" & _mesN & \" a \" & " + D.esc("_obra") + " & \" cumpriu \" & _tcOd & \" do plano semanal\"",
        "        & IF ( _naMeta, \", na meta de \" & " + C.marca("_tmTxt") + " & \": o ponto cheio do PPC na nota.\",",
        "            \", abaixo da meta de \" & " + C.marca("_tmTxt") + " & \"; na nota, o PPC vale \" & _tkTxt & \".\" )",
        "VAR _txtMeses =",
        "    SWITCH (",
        "        TRUE (),",
        "        _nCom <= 1, \"\",",
        "        _nMeta = _nCom, \"Todos os \" & " + ext("_nCom", fem=False) + " & \" meses da janela chegaram à meta\",",
        "        _nMeta = 0, \"Nenhum dos \" & " + ext("_nCom", fem=False) + " & \" meses da janela chegou à meta\",",
        "        " + cap(ext("_nMeta", fem=False)) + " & \" dos \" & " + ext("_nCom", fem=False)
        + " & IF ( _nMeta = 1, \" meses da janela chegou à meta\", \" meses da janela chegaram à meta\" )",
        "    )",
        "VAR _txtDesde = IF ( ISBLANK ( _desde ) || _desde = _ref, \"\", \"; está abaixo dela desde \" & " + desde("_desde") + " )",
        "VAR _txtAtraso =",
        "    IF (",
        "        ISBLANK ( _atr ),",
        "        \"\",",
        "        \" O PPC mede a semana; quando cai por vários meses, o atraso em meses vem depois. Hoje a obra está \"",
        "            & IF ( ROUND ( _atr, 1 ) < 0, _txtAtr & \" à frente do cronograma.\", \"com \" & _txtAtr & \" de atraso.\" )",
        "    )",
        "VAR _explica = IF ( _txtMeses = \"\", \"\", _txtMeses & _txtDesde & \".\" ) & _txtAtraso",
        "VAR _rotD1 = \"o melhor mês, \" & " + nome_mes("_mMax"),
        "VAR _rotD2 = \"o mês mais fraco, \" & " + nome_mes("_mMin"),
        "VAR _rotD3 = \"a média das obras em \" & _mesN",
        "-- 4 · Marcação",
        "VAR _corpo =",
        "    \"<span class='vs sob'>\" & _txtSob & \"</span><h2 class='ach'>\" & _achado & \"</h2>\"",
        "        & IF ( TRIM ( _explica ) = \"\", \"\", \"<p class='exp'>\" & TRIM ( _explica ) & \"</p>\" )",
        "        & " + destaques(("_tmxOd", "_rotD1"), ("_tmiOd", "_rotD2"), ("_tmdOd", "_rotD3")),
        "VAR _semBase =",
        "    \"<span class='vs sob'>\" & _txtSob & \"</span><h2 class='ach'>A base complementar de \" & _mesN",
        "        & \" não traz o PPC da \" & " + D.esc("_obra") + " & \": o item fica pendente na nota.</h2>\"",
        "RETURN",
        "    " + painel("pn-p", '"Leitura do PPC mês a mês"', "IF ( ISBLANK ( _ppc ), _semBase, _corpo )",
                       "[Comum · JS contador tooltip]"),
    ))

# ===================================================================================================== 4.3 Avanço das obras
FAIXA_TRAJ = 'IF ( {v} = 2, "fora do limite", "dentro do limite" )'
LADO_TXT = 'SWITCH ( {v}, -1, "atrás", 0, "no previsto", 1, "à frente" )'
desenho(
    "T3 · Leitura avanço · HTML",
    "Leitura do \"?\" do Avanço das obras, sobre o próprio painel (L065, Figma 317:5214, 461 × 468, condensada): "
    "quantas obras estão atrás do cronograma (atraso em meses acima de zero) e quais perdem pontos no item prazo da "
    "nota, o atraso médio da carteira (ponderado pelo orçamento), três destaques que contam (o executado compara o mesmo "
    "grupo do previsto; a obra de menor atraso) e a trajetória do físico de cada obra "
    "na janela, na ordem da nota — atrás, no previsto ou à frente, e quando cruzou o limite (as linhas entram de cima "
    "para baixo; Figma 352:8054). Lê a carteira (não muda com a obra em foco). Só lê contas.",
    linhas(
        "-- 1 · Leituras",
        "VAR _ref = [Mês de referência]",
        "VAR _jan = [Série · primeiro mês]",
        "VAR _mesL = [Mês de referência · longo]",
        "VAR _mesN = [Mês de referência · nome]",
        "VAR _nObras = [Obras com análise · ref] + 0",
        "VAR _nComP = [T3 · Avanço · obras com atraso calculado] + 0",
        "VAR _atras = [T3 · Avanço · obras atrás do cronograma] + 0",
        "VAR _fora = [T3 · Avanço · obras fora do limite do físico] + 0",
        "VAR _lFora = [T3 · Avanço · obras fora do limite do físico (lista)]",
        "VAR _aCart = [Prazo · atraso médio (meses) · ref]",
        "VAR _eCart = [T3 · Avanço · executado acumulado das obras com previsto]",
        "VAR _pCart = [Físico · previsto acumulado · ref]",
        "VAR _lSem = [T3 · Avanço · obras sem previsto (lista)]",
        "VAR _adiant = [T3 · Avanço · obra de menor atraso]",
        "VAR _minA = [T3 · Avanço · menor atraso]",
        "VAR _comeco = [T3 · Avanço · obra mais no começo]",
        "VAR _comecoE = [T3 · Avanço · executado da obra mais no começo]",
        "VAR _obras =",
        "    ADDCOLUMNS (",
        "        VALUES ( dObra[Obra] ),",
        "        \"@pos\", [T3 · Avanço · posição],",
        "        \"@d\", [Físico · desvio acumulado p.p. · ref],",
        "        \"@s\", [T3 · Status desvio físico · ref],",
        "        \"@ld\", [T3 · Físico · lado do cronograma · ref],",
        "        \"@sg\", [T3 · Físico · sinal · início da sequência],",
        "        \"@sga\", [T3 · Físico · sinal · início da sequência anterior],",
        "        \"@lda\", [T3 · Físico · lado da sequência anterior],",
        "        \"@mud\", [T3 · Físico · mudanças de faixa (lista)],",
        "        \"@ms\", [T3 · Físico · maior status na série],",
        "        \"@pm1\", [T3 · Série · primeiro mês da obra],",
        "        \"@n\", [T3 · Série · meses da obra],",
        "        \"@fim\", [Obra · término previsto]",
        "    )",
        "-- 2 · Textos",
        "VAR _aCartA = ROUND ( ABS ( _aCart ), 1 )",
        "VAR _minAA = ROUND ( ABS ( _minA ), 1 )",
        D.pct("_eCart", "_tec") + D.pct("_pCart", "_tpc") + D.pct("_comecoE", "_tco"),
        D.od_tabela(),
        ["VAR _tacN = FORMAT ( _aCartA, \"0.0\", \"pt-BR\" )", "VAR _tacTxt = IF ( ISBLANK ( _aCart ), \"—\", _tacN )",
         "VAR _tmaN = FORMAT ( _minAA, \"0.0\", \"pt-BR\" )", "VAR _tmaTxt = IF ( ISBLANK ( _minA ), \"—\", _tmaN )"]
        + D.od_num("_aCart", "_tac") + D.od_num("_minA", "_tma") + D.od_pct("_eCart", "_tec") + D.od_pct("_comecoE", "_tco"),
        "VAR _txtSob = \"LEITURA · AVANÇO DAS OBRAS · \" & UPPER ( _mesL )",
        "VAR _parcial = _nComP < _nObras",
        "VAR _txtGrupo = " + ext("_nComP") + " & IF ( _parcial, \" obras com curva prevista\", \" obras\" )",
        "VAR _txtAtras =",
        "    SWITCH (",
        "        TRUE (),",
        "        _atras = 0, \"Nenhuma das \" & _txtGrupo & \" está atrás do cronograma\",",
        "        _atras = 1 && _nComP = 1, \"A única obra está atrás do cronograma\",",
        "        _atras = 1, \"Uma das \" & _txtGrupo & \" está atrás do cronograma\",",
        "        _atras = _nComP, \"As \" & _txtGrupo & \" estão atrás do cronograma\",",
        "        " + cap(ext("_atras")) + " & \" das \" & _txtGrupo & \" estão atrás do cronograma\"",
        "    )",
        lista_e("_lFora", "_lfo", "_fora"),
        "VAR _txtFora =",
        "    SWITCH (",
        "        TRUE (),",
        "        _fora = 0, \", nenhuma perdendo pontos no prazo da nota\",",
        "        _fora = 1, \", a \" & _lfoTxt & \" perdendo pontos no prazo da nota\",",
        "        _fora = 2, \", \" & _lfoTxt & \" perdendo pontos no prazo da nota\",",
        "        \", \" & " + ext("_fora") + " & \" perdendo pontos no prazo da nota\"",
        "    )",
        "VAR _achado =",
        "    _txtAtras & _txtFora & \"; o atraso médio da carteira é de \" & _tacOd",
        "        & IF ( _aCartA <= 1, \" mês\", \" meses\" ) & IF ( ROUND ( _aCart, 1 ) < 0, \" à frente.\", \".\" )",
        lista_e("_lSem", "_ls"),
        "VAR _rotD1 = \"executado × \" & " + C.marca("_tpcTxt") + " & \" previsto\" & IF ( _lsN = 1, \", sem a \" & _lSem, IF ( _lsN > 1, \", só obras com previsto\", \"\" ) )",
        "VAR _rotD2 = IF ( ROUND ( _minA, 1 ) < 0, \"meses à frente: \" & _adiant & \", a mais adiantada\", "
        "IF ( _minAA <= 1, \"mês de atraso: \", \"meses de atraso: \" ) & _adiant & \", a menos atrasada\" )",
        "VAR _rotD3 = _comeco & \", a obra mais no começo\"",
        "VAR _txtJanela = UPPER ( " + mes_ano("_jan") + " & \" A \" & " + mes_ano("_ref") + " )",
        "VAR _lista = FILTER ( _obras, NOT ISBLANK ( [@pos] ) ) /* lista */",
        "VAR _htmlTraj =",
        "    CONCATENATEX (",
        "        _lista,",
        "        VAR _d = [@d]",
        "        VAR _ld = [@ld]",
        "        VAR _sg = [@sg]",
        "        VAR _sga = [@sga]",
        "        VAR _mud = [@mud]",
        "        VAR _semP = ISBLANK ( _d )",
        "        VAR _nMud = IF ( ISBLANK ( _mud ) || _mud = \"\", 0, PATHLENGTH ( _mud ) )",
        "        VAR _sempreEst = _ld = -1 && [@ms] = 0",
        "        VAR _txtSinal =",
        "            SWITCH (",
        "                TRUE (),",
        "                _semP, \"sem previsto na planilha\",",
        "                _sempreEst, \"atrás, sempre dentro do limite\",",
        "                NOT ISBLANK ( _sga ),",
        "                    " + LADO_TXT.format(v="[@lda]") + " & \" \" & IF ( EDATE ( _sg, -1 ) = _sga, \"em \" & " + abrev("_sga")
        + ", \"de \" & " + abrev("_sga") + " & \" a \" & " + abrev("EDATE ( _sg, -1 )") + " ) & \"; \" & "
        + LADO_TXT.format(v="_ld") + " & \" desde \" & " + abrev("_sg") + ",",
        "                _ld = -1, \"atrás desde \" & IF ( _sg = [@pm1] && [@pm1] > _jan, \"a 1.ª aba, \" & " + abrev("_sg")
        + ", " + abrev("_sg") + " ),",
        "                _sg = [@pm1] && [@n] > 1, " + LADO_TXT.format(v="_ld") + " & \" nos \" & " + ext("[@n]", fem=False)
        + " & \" meses\",",
        "                " + LADO_TXT.format(v="_ld") + " & \" desde \" & " + abrev("_sg"),
        "            )",
        "        VAR _txtFaixa =",
        "            IF (",
        "                _semP || _sempreEst || _nMud = 0,",
        "                \"\",",
        "                \"; \" & CONCATENATEX (",
        "                    GENERATESERIES ( 1, _nMud ),",
        "                    VAR _it = SUBSTITUTE ( PATHITEM ( _mud, [Value] ), \"§\", \"|\" )",
        "                    VAR _para = PATHITEM ( _it, 4, INTEGER )",
        "                    VAR _nf = PATHITEM ( _it, 5, INTEGER )",
        "                    RETURN",
        "                        " + FAIXA_TRAJ.format(v="_para") + " & IF ( [Value] = _nMud && _nf > 1, \" desde \", \" em \" ) "
        "& PATHITEM ( _it, 2 ),",
        "                    \", \",",
        "                    [Value], ASC",
        "                )",
        "            )",
        "        VAR _txtFim = IF ( [@fim] = _ref, \"; termina em \" & " + abrev("_ref") + ", \"\" )",
        "        VAR _mk = IF ( _semP, \"sm\", \"mk mk\" & [@s] )",
        "        RETURN",
        "            \"<div class='tj\" & IF ( _semP, \" sp\", \"\" ) & \"' style='animation-delay:\" & ( 400 + ( [@pos] - 1 ) * 80 )",
        "                & \"ms'><i class='a-pop \" & _mk & \"' style='animation-delay:\" & ( 500 + ( [@pos] - 1 ) * 80 ) & \"ms'></i>\"",
        "                & \"<b>\" & dObra[Obra] & \"</b><span>\" & _txtSinal & _txtFaixa & _txtFim",
        "                & \"</span></div>\",",
        "        \"\",",
        "        [@pos], ASC",
        "    )",
        "-- 4 · Marcação",
        "VAR _corpo =",
        "    \"<span class='vs sob'>\" & _txtSob & \"</span><h2 class='ach'>\" & _achado & \"</h2>\"",
        "        & " + destaques(("_tecOd", "_rotD1"), ("_tmaOd", "_rotD2"), ("_tcoOd", "_rotD3")),
        "        & " + bloco('"DETALHE · TRAJETÓRIA · " & _txtJanela', "_htmlTraj"),
        "RETURN",
        "    IF ( _nObras > 0, " + painel("pn-p av", '"Leitura do Avanço das obras"', "_corpo",
                                         "[Comum · JS contador tooltip]") + " )",
    ))

# ===================================================================================================== 4.4 Linha do tempo das obras
TIPOS = ["executivo", "preliminar", "legal", "alvo", "final"]
desenho(
    "T3 · Leitura linha · HTML",
    "Leitura do \"?\" da Linha do tempo das obras, sobre o próprio painel (L065, Figma 317:5261, 1028 × 340, duas "
    "colunas): quantas obras em andamento e a entrar e quem termina, a fase do canteiro (as mais novas, as perto do "
    "fim com atraso, as que atrasam cedo), onde cai o término projetado (F3: quem passa da entrega contratual e quem "
    "passa dos 180 dias de tolerância), três destaques (o orçamento conta; datas não), o que explica (orçamento das "
    "a iniciar e o tipo de orçamento pela fase) e a tabela das obras a iniciar. Lê a carteira. Só lê contas.",
    linhas(
        "-- 1 · Leituras",
        "VAR _ref = [Mês de referência]",
        "VAR _mesL = [Mês de referência · longo]",
        "VAR _mesN = [Mês de referência · nome]",
        "VAR _nAnd = [Obras com análise · ref] + 0",
        "VAR _nAI = [T3 · Linha do tempo · obras a iniciar] + 0",
        "VAR _tipoAI = [T3 · Linha do tempo · tipo das obras a iniciar]",
        "VAR _uiAI = [T3 · Linha do tempo · último início a iniciar]",
        "VAR _antiga = [T3 · Linha do tempo · obra mais antiga]",
        "VAR _iniAntiga = [T3 · Linha do tempo · primeiro início em andamento]",
        "VAR _dist = [T3 · Linha do tempo · obra de término mais distante]",
        "VAR _fimDist = [T3 · Linha do tempo · término mais distante em andamento]",
        "VAR _mOrc = [T3 · Linha do tempo · obra de maior orçamento]",
        "VAR _vOrc = [T3 · Linha do tempo · maior orçamento]",
        "VAR _termina = [T3 · Linha do tempo · obra que termina no mês]",
        "VAR _prox = [T3 · Linha do tempo · próxima a terminar]",
        "VAR _fimProx = [T3 · Linha do tempo · término da próxima a terminar]",
        "VAR _lCom = [T3 · Linha do tempo · obras no começo (lista)]",
        "VAR _lPerto = [T3 · Linha do tempo · obras perto do fim com atraso (lista)]",
        "VAR _fimPerto = [T3 · Linha do tempo · término da primeira perto do fim]",
        "VAR _lCedo = [T3 · Linha do tempo · obras com atraso cedo (lista)]",
        "VAR _anosCedo = [T3 · Linha do tempo · anos de término com atraso cedo (lista)]",
        [f"VAR _t{t.capitalize()} = [T3 · Linha do tempo · obras com orçamento {t} (lista)]" for t in TIPOS],
        "VAR _aiLista = [T3 · Linha do tempo · obras a iniciar (lista)]",
        "VAR _lDepois = [T3 · Linha do tempo · obras depois da entrega (lista)]",
        "VAR _lAlem = [T3 · Linha do tempo · obras além da tolerância (lista)]",
        "-- 2 · Textos",
        "VAR _nAL = IF ( _aiLista = \"\", 0, PATHLENGTH ( _aiLista ) )",
        "VAR _aIniciar = ADDCOLUMNS ( GENERATESERIES ( 1, _nAL ), \"@obra\", PATHITEM ( _aiLista, [Value] ) )",
        "VAR _lista =",
        "    GENERATE (",
        "        _aIniciar,",
        "        VAR _ob = [@obra]",
        "        RETURN",
        "            ROW (",
        "                \"@ini\", CALCULATE ( [Obra · início], dObra[Obra] = _ob ),",
        "                \"@fim\", CALCULATE ( [Obra · término previsto], dObra[Obra] = _ob ),",
        "                \"@orc\", CALCULATE ( [T3 · Obra · orçamento cronograma], dObra[Obra] = _ob )",
        "            )",
        "    )",
        D.rs("_vOrc", "_tvo"),
        D.od_tabela(), D.od_rs("_vOrc", "_tvo"),
        "VAR _txtSob = \"LEITURA · LINHA DO TEMPO DAS OBRAS · \" & UPPER ( _mesL )",
        "VAR _txtEntrar =",
        "    IF (",
        "        _nAI = 0,",
        "        \" e nenhuma a entrar\",",
        "        \" e \" & " + ext("_nAI") + " & \" a entrar \" & IF ( YEAR ( _uiAI ) = YEAR ( _ref ), \"ainda em \" & YEAR ( _ref ), "
        "\"até \" & " + mes_ano("_uiAI") + " )",
        "    )",
        "VAR _txtTermina =",
        "    IF (",
        "        _termina <> \"\" && NOT ISBLANK ( _termina ),",
        "        \"; a \" & _termina & IF ( _termina = _antiga, \", a mais antiga,\", \"\" ) & \" termina agora em \" & _mesN & \".\",",
        "        IF ( ISBLANK ( _prox ), \".\", \"; a próxima a terminar é a \" & _prox & \", em \" & " + mes_ano("_fimProx") + " & \".\" )",
        "    )",
        "VAR _achado = " + cap(ext("_nAnd")) + " & IF ( _nAnd = 1, \" obra em andamento\", \" obras em andamento\" ) & _txtEntrar & _txtTermina",
        lista_e("_lCom", "_lc"), lista_e("_lPerto", "_lp"), lista_e("_lCedo", "_lcd"), lista_e("_anosCedo", "_la"),
        "VAR _txtNovas =",
        "    IF (",
        "        _lcN = 0,",
        "        \"\",",
        "        \" e as mais novas mal começaram — \" & IF ( _nAI > 0, SUBSTITUTE ( _lCom, \"|\", \", \" ) & \" e, em seguida, as \" & "
        + ext("_nAI") + " & \" da cronograma\", _lcTxt )",
        "    )",
        "VAR _txtE1 =",
        "    IF (",
        "        _termina <> \"\" && NOT ISBLANK ( _termina ),",
        "        \"O canteiro está em transição: \" & IF ( _termina = _antiga, \"a obra mais antiga\", \"a \" & _termina )",
        "            & \" chega ao fim no mês de referência\" & _txtNovas & \".\",",
        "        \"O canteiro segue em obra\" & _txtNovas & \".\"",
        "    )",
        "VAR _mFim = MONTH ( _fimPerto )",
        "VAR _txtQuando = IF ( _mFim <= 4, \"no começo de \", IF ( _mFim <= 8, \"no meio de \", \"no fim de \" ) ) & YEAR ( _fimPerto )",
        "VAR _txtPerto =",
        "    SWITCH (",
        "        _lpN,",
        "        0, \"\",",
        "        1, \" A \" & _lpTxt & \" se aproxima do término, \" & _txtQuando & \", com atraso\",",
        "        \" \" & _lpTxt & \" se aproximam do término com atraso\"",
        "    )",
        "VAR _txtCedo =",
        "    SWITCH (",
        "        _lcdN,",
        "        0, \"\",",
        "        1, \"a \" & _lcdTxt & \" só termina em \" & _laTxt & \" e já acumula atraso cedo\",",
        "        _lcdTxt & \" só terminam em \" & _laTxt & \" e já acumulam atraso cedo\"",
        "    )",
        "VAR _txtE2 =",
        "    SWITCH (",
        "        TRUE (),",
        "        _txtPerto <> \"\" && _txtCedo <> \"\", _txtPerto & \"; \" & _txtCedo & \".\",",
        "        _txtPerto <> \"\", _txtPerto & \".\",",
        "        _txtCedo <> \"\", \" \" & " + cap("_txtCedo") + " & \".\",",
        "        \"\"",
        "    )",
        lista_e("_lDepois", "_ld"), lista_e("_lAlem", "_lal"),
        "VAR _txtProj =",
        "    SWITCH (",
        "        TRUE (),",
        "        _ldN = 0 && _lalN = 0, \" Pelo ritmo de hoje, todas terminam até a entrega contratual.\",",
        "        _lalN = 0, \" Pelo ritmo de hoje, \" & IF ( _ldN = 1, \"a \" & _ldTxt & \" termina\", _ldTxt & \" terminam\" )",
        "            & \" depois da entrega contratual, ainda nos 180 dias de tolerância.\",",
        "        \" Pelo ritmo de hoje, \" & IF ( _lalN = 1, \"a \" & _lalTxt & \" passa\", _lalTxt & \" passam\" )",
        "            & \" dos 180 dias de tolerância depois da entrega\" & SWITCH ( _ldN, 0, \".\", 1, \"; a \" & _ldTxt & \" fica nos 180 dias.\", \"; \" & _ldTxt & \" ficam nos 180 dias.\" )",
        "    )",
        "VAR _rotD1 = \"início da \" & _antiga & \", a mais antiga\"",
        "VAR _rotD2 = _dist & \", o término mais distante\"",
        "VAR _rotD3 = _mOrc & \", o maior orçamento das \" & " + ext("_nAnd"),
        "VAR _txtAI = IF ( _nAI = 0, \"\", \"As obras a iniciar entram com o orçamento \" & IF ( ISBLANK ( _tipoAI ), \"\", _tipoAI & \" \" )"
        " & \"da cronograma e só ganham previsto, executado e desembolso na primeira aba da Análise Crítica — por isso aparecem "
        "tracejadas, sem avanço. \" )",
        lista_e("_tExecutivo", "_lx", "[T3 · Linha do tempo · obras com orçamento executivo (quantidade)]"),
        lista_e("_tPreliminar", "_lpr", "[T3 · Linha do tempo · obras com orçamento preliminar (quantidade)]"),
        lista_e("_tLegal", "_lg", "[T3 · Linha do tempo · obras com orçamento legal (quantidade)]"),
        lista_e("_tAlvo", "_la2", "[T3 · Linha do tempo · obras com orçamento alvo (quantidade)]"),
        lista_e("_tFinal", "_lfi", "[T3 · Linha do tempo · obras com orçamento final (quantidade)]"),
        "VAR _legalNova = IF ( _lgN = 1 && CONTAINSSTRING ( \"|\" & _lCom & \"|\", \"|\" & _tLegal & \"|\" ), 1, 0 )",
        "VAR _tabGrupos =",
        "    {",
        "        ( 1, \"executivo\", _lxN, IF ( _lxN = 1, \"na mais madura (\", \"nas mais maduras (\" ) & _lxTxt & \")\",",
        "            [T3 · Linha do tempo · orçamento executivo · na maioria] ),",
        "        ( 2, \"preliminar\", _lprN, \"em \" & _lprTxt, [T3 · Linha do tempo · orçamento preliminar · na maioria] ),",
        "        ( 3, \"legal\", _lgN, IF ( _lgN = 1, \"na \" & _lgTxt & IF ( _legalNova = 1, \", que acabou de começar\", \"\" ), "
        "\"em \" & _lgTxt ), [T3 · Linha do tempo · orçamento legal · na maioria] ),",
        "        ( 4, \"alvo\", _la2N, \"em \" & _la2Txt, [T3 · Linha do tempo · orçamento alvo · na maioria] ),",
        "        ( 5, \"final\", _lfiN, \"em \" & _lfiTxt, [T3 · Linha do tempo · orçamento final · na maioria] )",
        "    }",
        "VAR _grupos =",
        "    CONCATENATEX (",
        "        FILTER ( _tabGrupos, [Value3] > 0 ), /* geometria */",
        "        [Value2] & \" \" & IF ( [Value5] = 1, \"na maioria\", [Value4] ),",
        "        \", \",",
        "        [Value1], ASC",
        "    )",
        "VAR _txtTipos = \"Entre as \" & " + ext("_nAnd") + " & \" em andamento, o tipo de orçamento acompanha a fase: \" & _grupos & \".\"",
        "VAR _htmlAI =",
        "    CONCATENATEX (",
        "        _lista,",
        "        VAR _o = [@orc]",
        "        VAR _oA = ABS ( _o )",
        "        VAR _oNu = IF ( _oA >= 99950000, FORMAT ( _oA / 1000000, \"0.0\", \"pt-BR\" ), FORMAT ( _oA / 1000000, \"0.00\", \"pt-BR\" ) )",
        "        VAR _oTxt = IF ( ISBLANK ( _o ), \"—\", " + C.marca("\"R$ \" & _oNu & \" mi\"") + " )",
        "        VAR _atraso = 400 + ( [Value] - 1 ) * 80 -- geometria (a lista já vem pelo início previsto)",
        "        RETURN",
        "            \"<div class='ai a-fd' style='animation-delay:\" & _atraso & \"ms'><i class='aim a-pop' style='animation-delay:\" "
        "& ( _atraso + 100 ) & \"ms'></i><b>\" & [@obra] & \"</b>\"",
        "                & \"<span class='pr'>\" & " + mes_ano("[@ini]") + " & \" → \" & " + mes_ano("[@fim]")
        + " & \"</span><span class='or'>\" & _oTxt & \"</span></div>\",",
        "        \"\",",
        "        [@ini], ASC,",
        "        [@obra], ASC",
        "    )",
        "VAR _htmlDet =",
        "    IF (",
        "        _nAI = 0,",
        "        \"<p class='oqe'>Nenhuma obra a iniciar na cronograma de \" & [T3 · cronograma · versão] & \".</p>\",",
        "        _htmlAI",
        "    )",
        "VAR _rotDet = \"DETALHE · AS \" & UPPER ( " + ext("_nAI") + " ) & \" A INICIAR · cronograma \" & UPPER ( [T3 · cronograma · versão] )",
        "-- 4 · Marcação",
        "VAR _esq =",
        "    \"<div class='esq'><span class='vs sob'>\" & _txtSob & \"</span><h2 class='ach'>\" & _achado & \"</h2>\"",
        "        & \"<p class='exp'>\" & _txtE1 & _txtE2 & _txtProj & \"</p>\"",
        "        & " + destaques(("IF ( ISBLANK ( _iniAntiga ), \"—\", " + mes_ano("_iniAntiga") + " )", "_rotD1"),
                                ("IF ( ISBLANK ( _fimDist ), \"—\", " + mes_ano("_fimDist") + " )", "_rotD2"),
                                ("_tvoOd", "_rotD3")),
        "    & \"</div>\"",
        "VAR _dir =",
        "    \"<div class='dir'>\" & " + bloco('"O QUE EXPLICA"', "\"<p class='oqe'>\" & TRIM ( _txtAI ) & \"</p>\""),
        "        & " + bloco("_rotDet", "_htmlDet"),
        "    & \"</div>\"",
        "VAR _corpo = \"<div class='cols'>\" & _esq & _dir & \"</div>\"",
        "RETURN",
        "    IF ( _nAnd > 0, " + painel("pn-g ln", '"Leitura da Linha do tempo das obras"', "_corpo",
                                     "[Comum · JS contador tooltip]") + " )",
    ))

# ===================================================================================================== CSS
CSS_LEITURA = (
    ".lv{position:fixed;inset:0}"
    # o visual é o retângulo do painel (sem margem nem sombra); × = X_SVG de leituras_lib (CSS_X, no fim)
    f".lv .pn{{position:absolute;inset:0;background:#FFFFFF;border:1px solid {PRETO};border-radius:16px;"
    f"overflow:hidden;color:{PRETO}}}"
    ".lv .sob{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
    f".lv .ach{{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;color:{PRETO}}}"
    f".lv .exp{{font-size:17px;line-height:26px;color:{GRAFITE}}}"
    # destaques: caixa creme, número Barlow 34/40 e rótulo Segoe 14/19; a coluna se ajusta ao número (o rótulo não
    # alarga a coluna: width 0 + min-width 100%)
    f".lv .dst{{background:{CREME};border-radius:4px;display:grid;grid-template-columns:repeat(3,minmax(110px,auto));"
    "column-gap:16px;padding:12px 16px}"
    ".lv .dst b{display:block;font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:34px;"
    "line-height:40px;white-space:nowrap;font-variant-numeric:tabular-nums}"
    f".lv .dst span{{display:block;width:0;min-width:100%;margin-top:2px;font-size:14px;line-height:19px;color:{GRAFITE}}}"
    ".lv .sec>.vs{margin-bottom:6px}"
    f".lv .oqe{{font-size:15px;line-height:21px;color:{PRETO}}}"
    f".lv .cl{{font-size:14px;line-height:19px;color:{PRETO}}}"
    # completa em duas colunas (Curva S 900 × 370, Linha do tempo 900 × 357)
    ".pn-g{padding:20px 24px 0}"
    ".pn-g .cols{display:grid;grid-template-columns:500px 320px;column-gap:32px}"
    ".pn-g .ach{margin-top:8px;font-size:23px;line-height:28px}"
    ".pn-g .exp{margin-top:10px}"
    ".pn-g .dst{margin-top:14px}"
    ".pn-g .dir .sec+.sec{margin-top:14px}"
    ".pn-g .dir .sec:first-child .oqe{padding-right:48px}"
    # rede de segurança da curva S (auditoria da Fase 3, MJ1): o "O QUE EXPLICA" para em 5 linhas (21 px cada) e nunca
    # empurra o "COMO LER" para fora do painel de 368 px; os textos cabem em 5 linhas nos piores casos provados
    ".lv .oq5{display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:5;overflow:hidden}"
    # detalhe da curva S: desvio mês a mês com o limite da nota (ou, sem previsto, o executado no mês)
    ".lv .bp{position:relative}"
    f".lv .bp .ms{{position:absolute;text-align:center;font-size:13px;line-height:16px;color:{GRAFITE}}}"
    ".lv .bp .b{position:absolute}"
    f".lv .bp .b.s0{{background:{SALVIA}}}.lv .bp .b.s2{{background:{VERM}}}"
    f".lv .bp .b.z{{background:{REGRA}}}.lv .bp .b.e{{background:{PRETO}}}"
    f".lv .bp .ax{{position:absolute;left:0;height:1px;background:{REGRA}}}"
    f".lv .bp .lm{{position:absolute;left:0;height:0;border-top:1px dashed {GRAFITE};transform-origin:left;"
    "animation:lvLim .4s ease-out .1s backwards}"
    "@keyframes lvLim{from{transform:scaleX(0)}}"
    f".lv .bp .lr{{position:absolute;font-size:13px;line-height:16px;color:{GRAFITE};white-space:nowrap}}"
    # tabela das obras a iniciar (Linha do tempo): nome, prazo e orçamento legal
    ".ln .ai{display:grid;grid-template-columns:22px 60px 1fr auto;align-items:center;height:22px;white-space:nowrap}"
    f".ln .ai .aim{{display:block;width:14px;height:9px;border:1px dashed {GRAFITE}}}"
    ".ln .ai b{font-size:15px;line-height:21px;font-weight:600}"
    f".ln .ai .pr{{font-size:14px;line-height:19px;color:{GRAFITE}}}"
    ".ln .ai .or{font-family:'Barlow U','Segoe UI',sans-serif;font-weight:600;font-size:16px;text-align:right}"
    # condensada (Ritmo 568 × 290, Avanço 568 × 437)
    ".pn-p{padding:20px 24px 0}"
    ".pn-p .sob{padding-right:52px}"
    ".pn-p .ach{margin-top:8px;font-size:21px;line-height:26px;padding-right:40px}"
    ".pn-p .exp{margin-top:10px}"
    ".pn-p .dst{margin-top:14px}"
    ".pn-p .sec{margin-top:14px}"
    ".av .tj{display:grid;grid-template-columns:18px 86px 1fr;align-items:center;height:22px;white-space:nowrap;"
    "animation:lvTj .3s ease-out backwards}"
    ".av .tj b{font-size:15px;line-height:21px;font-weight:600}"
    # F4: a trajetória longa quebra em duas linhas (entrelinha 17) em vez de cortar com reticências; a linha cresce junto
    f".av .tj span{{font-size:14px;line-height:17px;padding:2px 0;color:{GRAFITE};white-space:normal}}"
    ".av .tj{height:auto;min-height:22px}"
    ".av .tj.sp span{color:#6B6B70}"
    "@keyframes lvTj{from{opacity:0}}"
    "@media (prefers-reduced-motion:reduce){.lv .bp .lm,.av .tj{animation:none}}"
) + CSS_X
desenho("T3 · Leitura · CSS", "CSS das leituras do \"?\" da Tela 03 (v2: sobre o painel, superfície offwhite reta com "
        "contorno e sombra; completa em duas colunas, condensada, detalhe do desvio, tabela das obras a iniciar, "
        "trajetória) e do guia da página (1120, duas colunas, centrado).",
        "-- 4 · Marcação\n[Comum · CSS base]\n    & " + dax_lit(CSS_LEITURA))

if __name__ == "__main__":
    sys.exit(gravar(MEDIDAS, RAIZ / "dax" / "T3", GERADO))

"""Extrai as abas mensais das planilhas "Análise Crítica" (uma por obra) para tabelas longas.

Uso:
    python pipeline/extrair_analise_critica.py dados/analise-critica --cadastro dados/cadastro/obras_cadastro.csv \
        --saida <pasta> --desde 2025-10

--desde limita as saídas ao histórico do painel (out/25 em diante, pInicioHistorico). As abas anteriores continuam
sendo lidas para as regras que comparam com o mês anterior (ex.: a variação de out/25 usa set/25).

Cada planilha tem uma aba por mês (SET25, OUT25, ..., SET26). Nada é lido por endereço fixo: cada campo é achado pelo
rótulo (o layout já mudou uma linha entre versões). O resultado é recalculado a partir das entradas e conferido com o
valor salvo na planilha. Versão 01 da planilha: a dívida da obra (item 10) desconta do resultado.

Saídas (CSV UTF-8 com BOM, separador ";", decimal "."):
    fato_analise_critica.csv  uma linha por obra x mês, com entradas, resultado recalculado e conferência
    fato_itens.csv            linhas das tabelas anexadas (estoque, adiantamentos, contas a pagar...)
    qualidade_dado.csv        avisos de padronização encontrados em cada aba
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

import openpyxl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ler_crono as lc  # noqa: E402

MESES = {
    "JAN": 1, "JANEIRO": 1, "FEV": 2, "FEVEREIRO": 2, "MAR": 3, "MARCO": 3, "ABR": 4, "ABRIL": 4, "MAI": 5,
    "MAIO": 5, "JUN": 6, "JUNHO": 6, "JUL": 7, "JULHO": 7, "AGO": 8, "AGOSTO": 8, "SET": 9, "SETEMBRO": 9,
    "OUT": 10, "OUTUBRO": 10, "NOV": 11, "NOVEMBRO": 11, "DEZ": 12, "DEZEMBRO": 12,
}
# Aba com mês por extenso ou abreviado, colado ou não ao ano de 2 ou 4 dígitos, com complemento depois do ano ou entre
# parênteses (JUN26, "NOV25 ", MARÇO 2026, NOVEMBRO2025, "ABRIL 2026 (RETA FINAL)", JUNHO 2025 EXECUTIVO)
RE_ABA = re.compile(r"^([A-Z]+) ?(\d{4}|\d{2})(?: [A-Z0-9 ]+)?$")
MARCAS_DESCARTE = {"OBSOLETO", "OBSOLETA", "TESTE", "REV", "COPIA"}

# Tabelas anexadas: título da tabela -> (chave, coluna do valor relativa ao título)
TABELAS = {
    "saldo de contrato": "saldo_contrato",
    "adiantamento de materiais nao estocados": "adiant_materiais",
    "adiantamento de servicos nao medidos": "adiant_servicos",
    "estoque de materiais": "estoque",
    "equipamentos comprados": "equipamentos",
    "receitas de personalizacoes": "receita_personalizacao",
    "contas a pagar dos medidos": "contas_pagar",
    "itens apontados irregularmente no relatorio": "itens_irregulares",
    "divida da obra a ser paga": "divida",
}
# Rótulo legível (com acento) de cada tabela, para os textos dos avisos
TITULO_TABELA = {
    "saldo_contrato": "Saldo de contrato", "adiant_materiais": "Adiantamento de materiais não estocados",
    "adiant_servicos": "Adiantamento de serviços não medidos", "estoque": "Estoque de materiais",
    "equipamentos": "Equipamentos comprados", "receita_personalizacao": "Receitas de personalizações",
    "contas_pagar": "Contas a pagar dos medidos", "itens_irregulares": "Itens apontados irregularmente",
    "divida": "Dívida da obra a ser paga",
}
PLACEHOLDER = re.compile(r"^(servico|material|equipamento|reforma|divida|item)\s*\d+$")


def norm(txt) -> str:
    """Minúsculas, sem acento, sem espaços duplicados — para comparar rótulos."""
    if txt is None:
        return ""
    s = unicodedata.normalize("NFKD", str(txt)).encode("ascii", "ignore").decode()
    s = s.replace("°", "").replace("º", "")
    return re.sub(r"\s+", " ", s).strip().lower()


def mes_da_aba(nome: str) -> date | None:
    """Mês pelo nome da aba (espelha pbi/m/fxMesDaAba.m). Sem ano, sem mês no começo ou marcada OBSOLETO/TESTE/REV/
    CÓPIA → None."""
    n = norm(nome).upper()
    parenteses = " ".join(re.findall(r"\(([^)]*)\)", n))
    fora = re.sub(r"\([^)]*\)", " ", n)
    base = re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9 ]", " ", fora)).strip()
    marcas = set(re.sub(r"[^A-Z0-9 ]", " ", fora + " " + parenteses).split())
    if marcas & MARCAS_DESCARTE:
        return None
    m = RE_ABA.match(base)
    if not m or m.group(1) not in MESES:
        return None
    ano = int(m.group(2))
    return date(ano if ano > 1000 else 2000 + ano, MESES[m.group(1)], 1)


def aba_preliminar(nome: str) -> bool:
    """Aba marcada como preliminar perde para a outra do mesmo mês (ABRIL 2026 (RETA FINAL) × (PRELIMINAR))."""
    return "preliminar" in norm(nome)


def num(v) -> float:
    if v is None or v == "" or v == "-":
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).replace(".", "").replace(",", "."))
    except ValueError:
        return 0.0

def br_num(v: float, casas: int = 2) -> str:
    """1234567.8 -> '1.234.567,80' (formato pt-BR, para os textos dos avisos)."""
    s = f"{abs(v):,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("−" if v < 0 else "") + s


def br_rs(v: float, casas: int = 2) -> str:
    return ("−" if v < 0 else "") + "R$ " + br_num(abs(v), casas)


def br_pct(v: float) -> str:
    return br_num(v * 100, 2) + "%"


@dataclass
class Aba:
    obra: str
    arquivo: str
    aba: str
    mes: date
    campos: dict = field(default_factory=dict)
    itens: list = field(default_factory=list)
    avisos: list = field(default_factory=list)

    def aviso(self, regra: str, severidade: str, detalhe: str):
        self.avisos.append({"obra": self.obra, "mes": self.mes.isoformat(), "aba": self.aba,
                            "regra": regra, "severidade": severidade, "detalhe": detalhe})


def ultimo_valor(ws, row: int, col_ini: int = 3, col_fim: int = 12, tipo=(int, float)):
    for c in range(col_fim, col_ini - 1, -1):
        v = ws.cell(row, c).value
        if isinstance(v, tipo) and not isinstance(v, bool):
            return v
    return None


def ler_aba(ws, ws_f, obra_arquivo: str, arquivo: str) -> Aba | None:
    """ws = valores salvos; ws_f = mesma aba com as fórmulas (para checar os totais do modelo)."""
    mes = mes_da_aba(ws.title)
    if mes is None:
        return None
    a = Aba(obra=obra_arquivo, arquivo=arquivo, aba=ws.title, mes=mes)
    f = a.campos
    linha_resultado = None
    rotulos = {}
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row):
        for c in row:
            if isinstance(c.value, str):
                rotulos.setdefault((c.row, c.column), norm(c.value))
    for (r, col), t in rotulos.items():
        if t.startswith("resultado para utilizar na apresentacao"):
            linha_resultado = r
    if linha_resultado is None:
        a.aviso("layout", "alta", "bloco 'RESULTADO PARA UTILIZAR NA APRESENTAÇÃO' não encontrado")
        return a

    # 1) Passos de entrada (acima das tabelas anexadas)
    for (r, col), t in sorted(rotulos.items()):
        if r >= linha_resultado or col != 2:
            continue
        if "projeto (definir" in t:
            f["projeto"] = next((ws.cell(r, c).value for c in range(3, 11) if ws.cell(r, c).value), None)
        elif "mes de analise (definir" in t:
            # PrimeiraData do fxLerAba: a primeira data da linha; sem data, o primeiro número de série plausível (a data
            # com formato personalizado chega como número no Power Query; ler_crono.valor_pq)
            vals = [lc.valor_pq(ws.cell(r, c)) for c in range(3, 11)]
            v = next((x for x in vals if isinstance(x, datetime)), None) or next((x for x in vals if lc.eh_data(x)), None)
            f["mes_celula"] = lc.mes_de(v) if v is not None else None
        elif "orcamento da obra projetado" in t:
            f["orcamento"] = num(ultimo_valor(ws, r))
            f["tipo_orcamento"] = ultimo_valor(ws, r + 1, tipo=(str,))
        elif t.startswith(("4 passo", "4o passo")) or "previsto do mes (incluir" in t:
            # previsto em branco fica None (obra que não preenche o cronograma): zero viraria desvio falso
            v = ultimo_valor(ws, r)
            f["prev_mes"] = None if v is None else num(v)
        elif "executado do mes (incluir" in t:
            f["exec_mes"] = num(ultimo_valor(ws, r))
        elif "previsto acumulado do mes" in t:
            v = ultimo_valor(ws, r)
            f["prev_acum"] = None if v is None else num(v)
        elif "executado acumulado do mes" in t:
            f["exec_acum"] = num(ultimo_valor(ws, r))
        elif "valor desembolsado pela obra" in t:
            f["desembolsado_bruto"] = num(ws.cell(r, 6).value)

    # 2) Tabelas anexadas: soma das linhas (o total da planilha é fórmula e pode não estar salvo)
    for (r, col), t in sorted(rotulos.items()):
        if r >= linha_resultado or t not in TABELAS:
            continue
        chave = TABELAS[t]
        col_valor = col + 3  # B->E, G->J
        total = 0.0
        rr = r + 1
        while rr < r + 16:
            desc = ws.cell(rr, col).value
            if norm(desc) == "total":
                break
            val = ws.cell(rr, col_valor).value
            if isinstance(val, (int, float)) and val != 0:
                d = str(desc).strip() if desc else "(sem descrição)"
                if PLACEHOLDER.match(norm(d)):
                    a.aviso("item_sem_descricao", "baixa", f"{TITULO_TABELA[chave]}: {br_rs(val)} na linha '{d}' (rótulo padrão, sem descrição)")
                a.itens.append({"obra": obra_arquivo, "mes": mes.isoformat(), "grupo": chave,
                                "descricao": d, "valor": round(float(val), 2)})
                total += float(val)
            rr += 1
        f[chave] = round(total, 2)
        tot = ws_f.cell(rr, col_valor).value if norm(ws.cell(rr, col).value) == "total" else None
        if not (isinstance(tot, str) and tot.upper().startswith("=SUM")):
            f.setdefault("_totais_sem_formula", []).append(chave)
            if total:
                a.aviso("item_fora_da_conta", "alta",
                        f"{br_rs(total)} digitados em '{TITULO_TABELA[chave]}', mas o total dessa tabela não tem fórmula: "
                        "o valor não entrou no resultado apresentado")

    # 3) Bloco de resultado: valores salvos pelo Excel (para conferência) e tabela informativa
    for (r, col), t in rotulos.items():
        if r < linha_resultado:
            continue
        if t.startswith("resultado mensal da obra"):
            f["resultado_excel"] = ws.cell(r, 4).value
        elif t.startswith("resultado do mes anterior"):
            f["resultado_anterior_excel"] = ws.cell(r, 4).value
        elif t.startswith("valor previsto para"):
            f["previsto_mes_rs"] = num(ws.cell(r, 10).value) or None
        elif t.startswith("valor desembolsado") and col == 7:
            f["desembolsado_mes_rs"] = num(ws.cell(r, 10).value) or None
        elif t.startswith("diferenca entre o previsto") and col == 7:
            f["_linha_diferenca"] = r
        elif t.startswith("justificativa para diferenca"):
            f.setdefault("_linha_justificativa", r)
    # justificativa nos dois leiautes (com rótulo: CAJUEIRO, DUNAS; sem rótulo, texto direto em G uma ou duas linhas abaixo
    # da "Diferença…": REDINHA G144, TIROL G143 em 2026) — espelho de fxLerAba.m (defeito achado em 07/10/2026)
    base = f.pop("_linha_diferenca", None) or f.pop("_linha_justificativa", None)
    f.pop("_linha_justificativa", None)
    f["justificativa"] = None
    if base:
        for rr in range(base + 1, base + 5):
            v = ws.cell(rr, 7).value
            txt = str(v).strip() if v is not None else ""
            if norm(txt).startswith("tabela informativa"):
                break
            if txt and txt != "-" and not norm(txt).startswith("justificativa para diferenca"):
                f["justificativa"] = txt
                break
    return a


def calcular(a: Aba):
    f = a.campos
    for k in ("orcamento", "prev_mes", "exec_mes", "prev_acum", "exec_acum", "desembolsado_bruto", *TABELAS.values()):
        f.setdefault(k, 0.0)
    f["credito"] = round(f["exec_acum"] * f["orcamento"], 2)
    f["desembolsado_corrigido"] = round(f["desembolsado_bruto"] - f["itens_irregulares"], 2)
    # Mesma conta da célula D155 da planilha, versão 01: (1..7) - 8 - 9 - 10 (a dívida desconta)
    f["resultado_recalculado"] = round(
        f["credito"] + f["saldo_contrato"] + f["adiant_servicos"] + f["adiant_materiais"] + f["estoque"]
        + f["equipamentos"] + f["receita_personalizacao"] - f["contas_pagar"] - f["desembolsado_corrigido"]
        - f["divida"], 2)
    rx = f.get("resultado_excel")
    # Oficial = o número apresentado pela planilha; sem valor salvo (planilha gerada por script), vale a regra
    f["resultado"] = round(float(rx), 2) if isinstance(rx, (int, float)) else f["resultado_recalculado"]
    f["resultado_pct"] = f["resultado"] / f["orcamento"] if f["orcamento"] else None
    ativos = (f["saldo_contrato"] + f["adiant_servicos"] + f["adiant_materiais"] + f["estoque"] + f["equipamentos"])
    f["ativos_nao_consumidos"] = round(ativos, 2)
    f["resultado_sem_ativos"] = round(f["resultado"] - ativos, 2)
    if isinstance(rx, (int, float)):
        f["conferido"] = abs(rx - f["resultado_recalculado"]) < 1.0
        if not f["conferido"]:
            a.aviso("conta_diverge", "alta",
                    f"pela regra da planilha daria {br_rs(f['resultado_recalculado'])}; a aba apresentou {br_rs(rx)}")
    else:
        f["conferido"] = None  # planilha salva sem cálculo (ex.: gerada por script) — vale o recalculado


def checar_sequencia(abas: list[Aba]):
    """Regras que comparam a aba com a do mês anterior da mesma obra."""
    abas.sort(key=lambda x: x.mes)
    for i, a in enumerate(abas):
        f = a.campos
        if a.aba != a.aba.strip() or not re.match(r"^[A-Z]{3}\d{2}$", a.aba.strip()):
            a.aviso("nome_da_aba", "baixa", f"'{a.aba}' fora do padrão MMMAA (3 letras + ano)")
        mc = f.get("mes_celula")
        if mc and mc != a.mes:
            a.aviso("mes_divergente", "media", f"célula 'Mês de análise' = {mc:%m/%Y}, aba = {a.mes:%m/%Y}")
        if f["prev_acum"] is None:
            a.aviso("previsto_vazio", "alta", "previsto acumulado em branco na aba: sem ele não há desvio físico")
        if i == 0:
            continue
        p = abas[i - 1].campos
        tem_prev = None not in (f["prev_acum"], p["prev_acum"], f["prev_mes"])
        if tem_prev and f["prev_acum"] + 1e-6 < p["prev_acum"]:
            a.aviso("previsto_regrediu", "alta",
                    f"previsto acumulado caiu de {br_pct(p['prev_acum'])} para {br_pct(f['prev_acum'])}")
        if f["exec_acum"] + 1e-6 < p["exec_acum"]:
            a.aviso("executado_regrediu", "alta",
                    f"executado acumulado caiu de {br_pct(p['exec_acum'])} para {br_pct(f['exec_acum'])}")
        gap = f["exec_acum"] - (p["exec_acum"] + f["exec_mes"])
        if abs(gap) > 0.0015:
            a.aviso("executado_nao_fecha", "media",
                    f"acum. anterior {br_pct(p['exec_acum'])} + mês {br_pct(f['exec_mes'])} ≠ acum. {br_pct(f['exec_acum'])}")
        gap = f["prev_acum"] - (p["prev_acum"] + f["prev_mes"]) if tem_prev else 0.0
        if tem_prev and abs(gap) > 0.0015 and f["prev_acum"] >= p["prev_acum"]:
            a.aviso("previsto_reprogramado", "baixa",
                    f"acum. anterior {br_pct(p['prev_acum'])} + mês {br_pct(f['prev_mes'])} ≠ acum. {br_pct(f['prev_acum'])} "
                    "(cronograma reprogramado ou digitação)")
        ra = f.get("resultado_anterior_excel")
        if isinstance(ra, (int, float)) and abs(ra - p["resultado"]) > 1.0:
            a.aviso("mes_anterior_errado", "alta",
                    f"'Resultado do mês anterior' = {br_rs(ra, 0)}, mas a aba {abas[i-1].aba.strip()} fechou {br_rs(p['resultado'], 0)}")
        if f.get("previsto_mes_rs") and f.get("previsto_mes_rs") == p.get("previsto_mes_rs"):
            a.aviso("previsto_rs_repetido", "baixa", f"valor previsto do mês igual ao do mês anterior ({br_rs(f['previsto_mes_rs'])})")
        if f.get("tipo_orcamento") != p.get("tipo_orcamento"):
            a.aviso("tipo_orcamento_mudou", "info", f"{p.get('tipo_orcamento')} → {f.get('tipo_orcamento')}")
        if f.get("projeto") and norm(f["projeto"]) != norm(a.obra):
            a.aviso("projeto_divergente", "media", f"célula Projeto = '{f['projeto']}'")


def obra_do_arquivo(path: Path, wb) -> str:
    m = re.search(r"analise critica\s+(.+?)(?:\s*[_(]|\s+-|$)", norm(path.stem))  # nome pode ter espaço (PONTA NEGRA)
    if m:
        return m.group(1).strip().upper()
    return path.stem.upper()


def processar(arquivos: list[Path], obras: dict[Path, str] | None = None):
    """obras: obra de cada arquivo (pela pasta do cadastro); sem ela, a obra sai do nome do arquivo (mockup)."""
    linhas, itens, avisos = [], [], []
    for p in arquivos:
        wb = openpyxl.load_workbook(p, data_only=True)
        wbf = openpyxl.load_workbook(p, data_only=False)
        obra = (obras or {}).get(p) or obra_do_arquivo(p, wb)
        por_mes = {}
        ocultas = [ws.title for ws in wb.worksheets if ws.sheet_state != "visible" and mes_da_aba(ws.title)]
        for i, ws in enumerate(wb.worksheets):
            if ws.sheet_state != "visible":
                continue
            a = ler_aba(ws, wbf[ws.title], obra, p.name)
            if a is None:
                continue
            calcular(a)
            # uma aba por mês: a preliminar perde; entre iguais, vale a mais à direita (espelha fAnaliseCritica.m)
            chave = (not aba_preliminar(ws.title), i)
            if a.mes not in por_mes or chave > por_mes[a.mes][0]:
                por_mes[a.mes] = (chave, a)
        abas = [a for _, a in por_mes.values()]
        checar_sequencia(abas)
        if abas and abas[-1].campos.get("_totais_sem_formula"):
            avisos.append({"obra": obra, "mes": abas[-1].mes.isoformat(), "aba": abas[-1].aba.strip(),
                           "regra": "modelo_sem_formula", "severidade": "alta",
                           "detalhe": "total sem fórmula no modelo da planilha: " + ", ".join(TITULO_TABELA.get(t, t) for t in abas[-1].campos["_totais_sem_formula"]) + " (o que for digitado ali não entra no resultado)"})
        if ocultas:
            avisos.append({"obra": obra, "mes": "", "aba": ", ".join(ocultas[:3]) + ("…" if len(ocultas) > 3 else ""),
                           "regra": "abas_ocultas", "severidade": "media",
                           "detalhe": f"{len(ocultas)} abas mensais ocultas com layout antigo (fora da extração)"})
        prev = None
        for a in abas:
            f = a.campos
            linhas.append({
                "obra": obra, "mes": a.mes.isoformat(), "aba": a.aba.strip(), "arquivo": a.arquivo,
                "tipo_orcamento": f.get("tipo_orcamento"), "orcamento": f["orcamento"],
                "prev_mes": f["prev_mes"], "exec_mes": f["exec_mes"], "prev_acum": f["prev_acum"], "exec_acum": f["exec_acum"],
                "credito": f["credito"], "saldo_contrato": f["saldo_contrato"], "adiant_servicos": f["adiant_servicos"],
                "adiant_materiais": f["adiant_materiais"], "estoque": f["estoque"], "equipamentos": f["equipamentos"],
                "receita_personalizacao": f["receita_personalizacao"], "contas_pagar": f["contas_pagar"],
                "desembolsado_bruto": f["desembolsado_bruto"], "itens_irregulares": f["itens_irregulares"],
                "desembolsado_corrigido": f["desembolsado_corrigido"], "divida": f["divida"],
                "resultado": f["resultado"], "resultado_recalculado": f["resultado_recalculado"], "resultado_pct": round(f["resultado_pct"], 6) if f["resultado_pct"] is not None else None,
                "resultado_mes_anterior": prev["resultado"] if prev else None,
                "ativos_nao_consumidos": f["ativos_nao_consumidos"], "resultado_sem_ativos": f["resultado_sem_ativos"],
                "previsto_mes_rs": f.get("previsto_mes_rs"), "desembolsado_mes_rs": f.get("desembolsado_mes_rs"),
                "justificativa": f.get("justificativa"),
                "resultado_excel": f.get("resultado_excel") if isinstance(f.get("resultado_excel"), (int, float)) else None,
                "conferido": f.get("conferido"), "avisos": len(a.avisos),
            })
            prev = f
            itens.extend(a.itens)
            avisos.extend(a.avisos)
    return linhas, itens, avisos


def gravar(path: Path, rows: list[dict]):
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), delimiter=";")
        w.writeheader()
        w.writerows(rows)


def escolher_por_cadastro(raiz: Path, cadastro: Path) -> tuple[list[Path], dict[Path, str]]:
    """Uma planilha por obra do cadastro (espelha pbi/m/stgAbas.m): na subpasta pasta_analise_critica, com as
    subpastas, os .xlsx cujo nome começa com "Análise Crítica", fora o que tiver OBSOLETO no caminho ou no nome; vale a
    que tem a aba mensal visível mais recente (empate: a modificada por último)."""
    with cadastro.open(encoding="utf-8-sig") as fh:
        linhas = list(csv.DictReader(fh, delimiter=";"))
    arquivos, obras = [], {}
    for c in linhas:
        pasta = (c.get("pasta_analise_critica") or "").strip()
        if not pasta:
            continue
        cands = []
        for f in (raiz / pasta).rglob("*.xlsx"):
            rel = norm(str(f.relative_to(raiz / pasta)))
            if f.name.startswith("~$") or "obsolet" in rel or not norm(f.name).startswith("analise critica"):
                continue
            wb = openpyxl.load_workbook(f, read_only=True)
            meses = [m for ws in wb.worksheets if ws.sheet_state == "visible" and (m := mes_da_aba(ws.title))]
            wb.close()
            if meses:
                cands.append((max(meses), f.stat().st_mtime, f))
        if cands:
            f = max(cands, key=lambda c: (c[0], c[1]))[2]
            arquivos.append(f)
            obras[f] = c["obra"].strip().upper()
    return arquivos, obras


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("pastas", nargs="+", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("dados/saida"))
    ap.add_argument("--desde", default=None, help="AAAA-MM: grava só os meses a partir deste")
    ap.add_argument("--cadastro", type=Path, default=None,
                    help="cadastro com pasta_analise_critica (ex.: dados/cadastro/obras_cadastro.csv): a pasta dada é a "
                         "raiz ANÁLISE CRÍTICA-GESTÃO e cada obra é lida da sua subpasta")
    args = ap.parse_args(argv)
    obras = None
    if args.cadastro:
        arquivos, obras = escolher_por_cadastro(args.pastas[0], args.cadastro)
    else:
        arquivos = sorted(p for d in args.pastas for p in d.glob("*.xlsx") if not p.name.startswith("~$"))
    if not arquivos:
        sys.exit("nenhuma planilha .xlsx encontrada")
    linhas, itens, avisos = processar(arquivos, obras)
    if args.desde:
        corte = f"{args.desde}-01"[:10]
        linhas = [l for l in linhas if l["mes"] >= corte]
        itens = [i for i in itens if i["mes"] >= corte]
        avisos = [a for a in avisos if not a["mes"] or a["mes"] >= corte]  # sem mês = aviso do arquivo
    args.saida.mkdir(parents=True, exist_ok=True)
    gravar(args.saida / "fato_analise_critica.csv", linhas)
    gravar(args.saida / "fato_itens.csv", itens)
    gravar(args.saida / "qualidade_dado.csv", avisos)
    conf = [l for l in linhas if l["conferido"] is not None]
    ok = sum(1 for l in conf if l["conferido"])
    print(f"{len(arquivos)} planilhas · {len(linhas)} abas · {len(itens)} itens · {len(avisos)} avisos")
    print(f"conferência com o Excel: {ok}/{len(conf)} abas batem (as demais não têm valor salvo)")
    return linhas, itens, avisos


if __name__ == "__main__":
    main()

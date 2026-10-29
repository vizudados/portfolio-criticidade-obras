"""Confere o resultado do Power Query (bancada do Excel, rodar_m_excel.ps1) contra as PLANILHAS REAIS
(pbi/qa/conferencia-real/fato_analise_critica.csv e fato_itens.csv, gravados por conferir_real.py).

    python -I -X utf8 pbi/scripts/conferir_m.py [pbi/qa/m/saida.xlsx]

Confronta só o histórico (a partir de pInicioHistorico, 2025-10-01): as linhas de set/25 do oráculo ficam fora.
Texto compara sem espaço no fim do nome (aba "MAIO 2026 " × "MAIO 2026").

Diferenças conhecidas e aceitas. O Power Query usa o quadradinho como a planilha apresenta; o extrator soma as tabelas
anexadas. Onde a planilha deixa valor fora da conta, os dois divergem nesse item, e só nele:
- CAJUEIRO fev/26, Equipamentos: R$ 78 mil de elevador digitado fora da conta (total sem fórmula).
- JANGADA, linhas com conferido = False: Saldo de contrato (a tabela virou "PAGAMENTO") e Desembolsado (jul/26:
  quadradinho R$ 4.032.147,35 × soma das tabelas R$ 4.054.712,35).
O resultado apresentado é o mesmo.
"""
from __future__ import annotations

import csv
import sys
from datetime import date, datetime
from pathlib import Path

import openpyxl

RAIZ = Path(__file__).resolve().parents[2]
ORACULO = RAIZ / "pbi" / "qa" / "conferencia-real"   # planilhas reais, gravadas por conferir_real.py
INICIO_HISTORICO = "2025-10-01"                      # pInicioHistorico do modelo: set/25 fica fora do confronto
CONHECIDAS: set = set()   # dados fictícios da F2: nenhuma diferença aceita
# JANGADA com conferido = False no extrator: saldo de contrato virou "PAGAMENTO"; desembolsado = quadradinho (planilha)
# diferente da soma das tabelas (regra). Só essas colunas, só nessas linhas.
JANGADA_NAO_FECHA = {"SaldoContrato", "Desembolsado"}

MAPA = {  # coluna do Power Query -> coluna do oráculo
    "Aba": "aba", "TipoOrcamento": "tipo_orcamento", "Orcamento": "orcamento", "PrevMes": "prev_mes",
    "ExecMes": "exec_mes", "PrevAcum": "prev_acum", "ExecAcum": "exec_acum", "Credito": "credito",
    "SaldoContrato": "saldo_contrato", "AdiantServicos": "adiant_servicos", "AdiantMateriais": "adiant_materiais",
    "Estoque": "estoque", "Equipamentos": "equipamentos", "ReceitaPersonalizacao": "receita_personalizacao",
    "ContasPagar": "contas_pagar", "Desembolsado": "desembolsado_corrigido", "Divida": "divida",
    "Resultado": "resultado", "ResultadoRegra": "resultado_recalculado", "ResultadoAnterior": "resultado_mes_anterior",
    "PrevistoMesRS": "previsto_mes_rs", "DesembolsadoMesRS": "desembolsado_mes_rs", "Justificativa": "justificativa",
    "DesembolsadoBruto": "desembolsado_bruto", "ItensIrregulares": "itens_irregulares",
}


def ler_planilha(caminho: Path, aba: str) -> list[dict]:
    wb = openpyxl.load_workbook(caminho, data_only=True, read_only=True)
    if aba not in wb.sheetnames:
        return []
    linhas = list(wb[aba].iter_rows(values_only=True))
    cab = linhas[0]
    return [dict(zip(cab, l)) for l in linhas[1:] if any(v is not None for v in l)]


def ler_csv(nome: str) -> list[dict]:
    with (ORACULO / nome).open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh, delimiter=";"))


def iso(v) -> str:
    if isinstance(v, datetime):
        return v.date().isoformat()
    if isinstance(v, date):
        return v.isoformat()
    return str(v)


def num(v):
    if v in (None, "", "None"):
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return v


def texto(v):
    return None if v in (None, "") else str(v).strip()


def conhecida(chave, col_pq, linha_oraculo) -> bool:
    if (chave[0], chave[1], col_pq) in CONHECIDAS:
        return True
    return chave[0] == "JANGADA" and linha_oraculo.get("conferido") == "False" and col_pq in JANGADA_NAO_FECHA


def main(argv: list[str]) -> int:
    xlsx = Path(argv[0]) if argv else RAIZ / "pbi" / "qa" / "m" / "saida.xlsx"
    erros, conhecidas, ok = [], [], 0
    pq = {(r["Obra"], iso(r["Mes"])): r for r in ler_planilha(xlsx, "fAnaliseCritica")}
    oraculo = {(r["obra"], r["mes"]): r for r in ler_csv("fato_analise_critica.csv") if r["mes"] >= INICIO_HISTORICO}
    if not pq:
        print(f"sem fAnaliseCritica em {xlsx}")
        return 2
    for chave in sorted(set(pq) | set(oraculo)):
        if chave not in pq or chave not in oraculo:
            erros.append(f"{chave}: só no {'Power Query' if chave in pq else 'oráculo'}")
            continue
        a, b = pq[chave], oraculo[chave]
        for col_pq, col_or in MAPA.items():
            va, vb = num(a.get(col_pq)), num(b.get(col_or))
            if isinstance(va, float) or isinstance(vb, float):
                igual = (va or 0.0) == (vb or 0.0) or abs((va or 0.0) - (vb or 0.0)) < 0.011
            else:
                igual = texto(va) == texto(vb)
            if igual:
                ok += 1
            elif conhecida(chave, col_pq, b):
                conhecidas.append(f"{chave[0]} {chave[1]} {col_pq}: PQ {va} × oráculo {vb}")
            else:
                erros.append(f"{chave[0]} {chave[1]} {col_pq}: PQ {va!r} × oráculo {vb!r}")
    print(f"fAnaliseCritica: {len(pq)} linhas no Power Query · {len(oraculo)} no oráculo · {ok} campos iguais")
    for c in conhecidas:
        print("  [conhecida]", c)
    for e in erros[:60]:
        print("  [DIFERENTE]", e)
    print(f"diferenças: {len(erros)} (conhecidas: {len(conhecidas)})")

    itens_pq = ler_planilha(xlsx, "fItens")
    if itens_pq:
        orc = [r for r in ler_csv("fato_itens.csv") if r["mes"] >= INICIO_HISTORICO]
        # grupo do oráculo -> Item do Power Query (ItemDaTabela em pbi/m/fItens.m; ItensIrregulares corrige o desembolsado)
        ITEM_DO_GRUPO = {"saldo_contrato": "SaldoContrato", "adiant_materiais": "AdiantMateriais",
                         "adiant_servicos": "AdiantServicos", "estoque": "Estoque", "equipamentos": "Equipamentos",
                         "receita_personalizacao": "ReceitaPersonalizacao", "contas_pagar": "ContasPagar",
                         "itens_irregulares": "Desembolsado", "divida": "Divida"}
        cj_pq = sorted((r["Obra"], iso(r["Mes"]), r["Item"], r["Descricao"], round(float(r["Valor"]), 2)) for r in itens_pq)
        cj_or = sorted((r["obra"], r["mes"], ITEM_DO_GRUPO[r["grupo"]], r["descricao"], round(float(r["valor"]), 2)) for r in orc)
        so_pq = sorted(set(cj_pq) - set(cj_or))
        so_or = sorted(set(cj_or) - set(cj_pq))
        print(f"fItens: {len(cj_pq)} linhas no Power Query · {len(cj_or)} no oráculo · só PQ {len(so_pq)} · só oráculo {len(so_or)}")
        for x in (so_pq + so_or)[:20]:
            print("  [DIFERENTE]", x)
        erros += so_pq + so_or
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

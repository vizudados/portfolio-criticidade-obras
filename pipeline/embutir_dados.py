#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""embutir_dados — grava pbi/m/fxDadosEmbutidos.m: os arquivos de dados/ (analise-critica, bases-complementares,
cronograma e cadastro; o _gabarito fica fora) dentro de uma consulta M, em base64, para pOrigem = "Embutido".

Com os dados no próprio modelo, o serviço do Power BI atualiza sem fonte externa (nem credencial, nem gateway) e o
PBIP abre em qualquer máquina. A consulta devolve a mesma listagem que o Folder.Files daria (Content, Name, Extension,
Date modified, Folder Path), com a raiz "embutido\\": o fxArquivosOrigem recorta por pasta do mesmo jeito nas três
origens.

  - Cada arquivo leva o caminho relativo a dados/ e o conteúdo em pedaços de até PEDACO caracteres (literais de texto
    curtos, uma linha cada no TMDL).
  - "Date modified" é a mesma data fixa para todos (DATA): o git não guarda a data do arquivo, e uma data que mudasse
    a cada clone mudaria o modelo sem motivo. Os dados fictícios não têm mês repetido entre arquivos, então a regra
    "vale o arquivo modificado por último" não é usada aqui.
  - Só grava quando o texto muda. O gerar_modelo.py chama este script antes de montar o modelo.

    python -X utf8 pipeline/embutir_dados.py
"""
from __future__ import annotations

import base64
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "dados"
DESTINO = RAIZ / "pbi" / "m" / "fxDadosEmbutidos.m"
PASTAS = ["analise-critica", "bases-complementares", "cronograma", "cadastro"]
PEDACO = 16000
DATA = "#datetime(2026, 10, 1, 0, 0, 0)"


def _m_texto(t: str) -> str:
    return '"' + t.replace('"', '""') + '"'


def _milhar(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def arquivos() -> list[Path]:
    out = []
    for pasta in PASTAS:
        base = DADOS / pasta
        if not base.is_dir():
            raise SystemExit(f"embutir_dados: falta a pasta {base.relative_to(RAIZ)}")
        out += sorted(p for p in base.rglob("*") if p.is_file() and not p.name.startswith("~$"))
    return out


def gerar() -> str:
    regs = []
    total = 0
    for arq in arquivos():
        rel = arq.relative_to(DADOS)
        b64 = base64.b64encode(arq.read_bytes()).decode("ascii")
        total += len(b64)
        partes = [b64[i:i + PEDACO] for i in range(0, len(b64), PEDACO)] or [""]
        pasta = "\\".join(("embutido",) + rel.parts[:-1]) + "\\"
        corpo = (",\n                ".join(f'"{p}"' for p in partes))
        regs.append(
            "        [\n"
            f"            Name = {_m_texto(rel.name)},\n"
            f"            Folder = {_m_texto(pasta)},\n"
            "            Partes = {\n"
            f"                {corpo}\n"
            "            }\n"
            "        ]")
    lista = ",\n".join(regs)
    return f"""/*
@tipo: consulta
@descricao: Os arquivos de dados/ (análise crítica, bases complementares, cronograma e cadastro) embutidos em base64, para pOrigem = "Embutido": a mesma listagem de pasta (Content, Name, Extension, Date modified, Folder Path), com a raiz "embutido\\". {len(regs)} arquivos, {_milhar(total)} caracteres de base64. GERADA por pipeline/embutir_dados.py a partir de dados/: não edite à mão (rode o script quando dados/ mudar; o gerar_modelo.py já roda).
*/
let
    Arquivos = {{
{lista}
    }},
    Linhas = List.Transform(Arquivos, each [
        Content = Binary.FromText(Text.Combine([Partes]), BinaryEncoding.Base64),
        Name = [Name],
        Extension = Text.Lower(if Text.Contains([Name], ".") then "." & List.Last(Text.Split([Name], ".")) else ""),
        #"Date modified" = {DATA},
        #"Folder Path" = [Folder]
    ]),
    Tabela = Table.FromRecords(Linhas, type table [
        Content = binary, Name = text, Extension = text, #"Date modified" = datetime, #"Folder Path" = text
    ])
in
    Tabela
"""


def main() -> int:
    texto = gerar()
    antigo = DESTINO.read_text(encoding="utf-8") if DESTINO.is_file() else None
    if antigo != texto:
        DESTINO.write_text(texto, encoding="utf-8", newline="\n")
        print(f"embutir_dados: {DESTINO.relative_to(RAIZ)} gravado ({len(texto.encode('utf-8')) / 1024:.0f} KB)")
    else:
        print(f"embutir_dados: {DESTINO.relative_to(RAIZ)} sem mudança ({len(texto.encode('utf-8')) / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

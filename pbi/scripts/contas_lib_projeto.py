# -*- coding: utf-8 -*-
"""contas_lib_projeto — gravação dos .dax gerados por contas_t<n>.py e desenho_t<n>.py (um arquivo por medida, no
formato do dax_para_tmdl). Cada gerador é dono só dos arquivos que tem @gerado com o nome dele: os outros .dax da
pasta (escritos à mão ou por outro gerador) ficam intactos."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PROIBIDOS = set('/\\:*?"<>|')


@dataclass
class Medida:
    nome: str
    pasta: str
    formato: str
    descricao: str
    dax: str
    oraculo: str = ""
    oculta: bool = False


def nome_arquivo(nome: str) -> str:
    return "".join("_" if c in PROIBIDOS else c for c in nome) + ".dax"


def gravar(medidas: list[Medida], destino: Path, gerado: str) -> int:
    nomes = [x.nome for x in medidas]
    rep = {n for n in nomes if nomes.count(n) > 1}
    if rep:
        print("[ERRO] nomes repetidos:", sorted(rep))
        return 2
    escritos = set()
    for x in medidas:
        sub = x.pasta.split("\\")
        pasta_arq = destino.joinpath(*[s for s in sub[1:] if s != "Contas"]) if len(sub) > 1 else destino
        arq = pasta_arq / nome_arquivo(x.nome)
        arq.parent.mkdir(parents=True, exist_ok=True)
        cab = ["/*", f"@pasta: {x.pasta}", f"@formato: {x.formato}", f"@descricao: {x.descricao}"]
        if x.oraculo:
            cab.append(f"@oraculo: {x.oraculo}")
        if x.oculta:
            cab.append("@oculta: sim")
        if nome_arquivo(x.nome)[:-4] != x.nome:
            cab.append(f"@nome: {x.nome}")
        cab += [f"@gerado: {gerado}", "*/"]
        texto = "\n".join(cab) + "\n" + x.dax.strip("\n") + "\n"
        if not arq.is_file() or arq.read_text(encoding="utf-8") != texto:
            arq.write_text(texto, encoding="utf-8", newline="\n")
        escritos.add(arq.resolve())
    sobras = []
    if destino.is_dir():
        for p in destino.rglob("*.dax"):
            if p.resolve() in escritos:
                continue
            if f"@gerado: {gerado}" in p.read_text(encoding="utf-8"):
                sobras.append(p)
    for p in sobras:
        p.unlink()
    print(f"{len(medidas)} medidas em {destino} · {len(sobras)} removidas")
    return 0

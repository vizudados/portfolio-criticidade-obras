# -*- coding: utf-8 -*-
"""deneb_lib — ajudantes para escrever specs Vega (puro, L026) dos gráficos do painel.

Convenções (vindas dos specs provados em outro projeto e no painel de referência):
  - o desenho é feito num espaço de design W0 × H0 (o tamanho do visual no Figma) e escalado por S =
    min(largura/W0, altura/H0) do denebContainer; toda coordenada passa por S;
  - animação finita por timer{40}: t0 é zerado a cada mudança de dados (assinatura) e `ms` = tempo desde t0; o primeiro
    quadro e qualquer quadro sem animação (SemAnim = 1, prefers-reduced-motion) mostram o ESTADO FINAL (L019);
  - cascata de racing: item i começa em i × passo ms e cresce em `dur` ms com 1 − (1 − p)³ (handoff §12.4);
  - contador em rótulo: o DAX manda os 25 quadros separados por '|' (contador.py, bloco deneb); o quadro mostrado é
    floor(p × 24) com p linear (as frações do DAX já trazem a curva);
  - alvo de hover transparente separado do que anima (L012), com tooltip = datum (a linha leva __row__ para a página
    de tooltip).
Somente biblioteca padrão.
"""
from __future__ import annotations

import json
from pathlib import Path

FONTE = "Segoe UI"
ASC = 1.0791            # ascendente do Segoe UI em em (2210/2048): base = topo + tamanho × ASC
COR = {
    "texto": "#172333", "apoio": "#575756", "eixo": "#767C83", "borda": "#DCE4EC", "grade": "#EDF1F5",
    "base": "#C9D3DD", "faixa": "#F6F9FB", "trilho": "#E8EEF4", "receb": "#1169B1", "exped": "#1BA48A",
    "transf": "#8E63CE", "laranja": "#E3923A", "laranja_num": "#B85F0E", "laranja_txt": "#A8560C",
    "azul_claro": "#4B91CC", "ruim": "#C23B32", "selo": "#8A5300", "selo_fundo": "#FBEFD9",
}


def s(expr) -> dict:
    """Valor escalado pelo S: s(23) → {'signal': 'S*(23)'}; texto vira expressão Vega."""
    return {"signal": f"S*({expr})"}


def base(topo: float, tam: float) -> float:
    """Linha de base (alphabetic) de um texto do Figma a partir do topo da caixa e do tamanho da fonte."""
    return round(topo + tam * ASC, 2)


def sinais_escala(w0: float, h0: float) -> list:
    return [
        {"name": "W0", "value": w0},
        {"name": "H0", "value": h0},
        {"name": "S", "update": "isObject(denebContainer) && denebContainer.width > 0 && denebContainer.height > 0 ? "
                                "min(denebContainer.width / W0, denebContainer.height / H0) : 1"},
    ]


def sinais_animacao(assinatura: str, total_ms: int) -> list:
    """`assinatura`: expressão que muda quando os dados mudam (reinicia a entrada). `ms`: tempo desde o início."""
    return [
        {"name": "assinatura", "update": assinatura},
        {"name": "animacao", "update": "indexof(pluck(data('dataset'), 'SemAnim'), 1) < 0 && "
                                       "indexof(pluck(data('dataset'), 'SemAnim'), '1') < 0"},
        {"name": "reduceMotion", "value": False},
        {"name": "totalMs", "value": total_ms},
        {"name": "iniciado", "value": False, "on": [{"events": "timer{40}", "update": "true"}]},
        {"name": "t0", "value": 0, "on": [
            {"events": "timer{40}", "update": "t0 > 0 ? t0 : now()"},
            {"events": {"signal": "assinatura"}, "update": "now()"}]},
        {"name": "ms", "value": 1e9, "on": [
            {"events": "timer{40}",
             "update": "!animacao || reduceMotion || !iniciado || !(t0 > 0) ? 1e9 : "
                       "(ms >= totalMs && now() - t0 >= totalMs ? 1e9 : now() - t0)"}]},
    ]


def p_item(idx_expr: str, passo: int, dur: int, atraso: int = 0) -> str:
    """Progresso linear 0..1 do item (cascata)."""
    return f"clamp((ms - {atraso} - ({idx_expr}) * {passo}) / {dur}, 0, 1)"


def e_item(idx_expr: str, passo: int, dur: int, atraso: int = 0) -> str:
    """Progresso com 1 − (1 − p)³."""
    return f"(1 - pow(1 - {p_item(idx_expr, passo, dur, atraso)}, 3))"


def quadro(campo: str, p_expr: str) -> str:
    """Texto do contador: quadro floor(p × 24) da lista '|' do DAX; sem lista, o próprio campo."""
    c = f"({campo})"
    return (f"isString({c}) && indexof({c}, '|') >= 0 ? split({c}, '|')[min(24, floor(({p_expr}) * 24))]"
            f" : ({c} || '')")


def final(campo: str) -> str:
    """Texto final de um campo com quadros (o último da lista)."""
    c = f"({campo})"
    return f"isString({c}) && indexof({c}, '|') >= 0 ? peek(split({c}, '|')) : ({c} || '')"


def largura_texto(expr_texto: str, tam: float, semibold: bool = False) -> str:
    """Estimativa da largura (px, antes do S) de um texto Segoe UI: dígitos 0,537 em, espaço 0,274, maiúsculas 0,62,
    pontuação estreita 0,26, demais 0,47; Semibold +4%. Serve para pílulas e para colar dois pedaços de texto."""
    t = f"({expr_texto})"
    nd = f"length(replace({t}, regexp('[^0-9]', 'g'), ''))"
    ns = f"length(replace({t}, regexp('[^ ]', 'g'), ''))"
    nu = f"length(replace({t}, regexp('[^A-ZÀ-ÝÇ]', 'g'), ''))"
    npont = f"length(replace({t}, regexp('[^.,:;·|]', 'g'), ''))"
    resto = f"(length({t}) - {nd} - {ns} - {nu} - {npont})"
    k = 1.04 if semibold else 1.0
    return f"({tam} * {k} * (0.537 * {nd} + 0.274 * {ns} + 0.62 * {nu} + 0.26 * {npont} + 0.47 * {resto}))"


def texto(nome: str, x, y, txt: str, tam: float, cor: str, *, peso: int = 400, alinhar: str = "left",
          de: str | None = None, opac: str | None = None, interativo: bool = False) -> dict:
    """Marca de texto. x, y e txt são expressões Vega (y = linha de base)."""
    enc = {"x": s(x), "y": s(y), "text": {"signal": txt}, "font": {"value": FONTE}, "fontSize": s(tam),
           "fontWeight": {"value": peso}, "fill": {"value": cor} if cor.startswith("#") else {"signal": cor},
           "align": {"value": alinhar}, "baseline": {"value": "alphabetic"}}
    if opac:
        enc["opacity"] = {"signal": opac}
    m = {"name": nome, "type": "text", "interactive": interativo, "encode": {"update": enc}}
    if de:
        m["from"] = {"data": de}
    return m


def retangulo(nome: str, x, y, w, h, cor: str, *, raio=None, de: str | None = None, borda: str | None = None,
              borda_w: float = 1, opac: str | None = None, raio_topo=None, extra: dict | None = None,
              interativo: bool = False, y2=None) -> dict:
    enc = {"x": s(x), "y": s(y), "width": s(w)}
    if y2 is not None:
        enc["y2"] = s(y2)
    else:
        enc["height"] = s(h)
    enc["fill"] = {"value": cor} if (cor.startswith("#") or cor == "transparent") else {"signal": cor}
    if raio is not None:
        enc["cornerRadius"] = s(raio)
    if raio_topo is not None:
        enc["cornerRadiusTopLeft"] = s(raio_topo)
        enc["cornerRadiusTopRight"] = s(raio_topo)
    if borda:
        enc["stroke"] = {"value": borda} if borda.startswith("#") else {"signal": borda}
        enc["strokeWidth"] = {"signal": f"max(1, S*{borda_w})"}
    if opac:
        enc["opacity"] = {"signal": opac}
    if extra:
        enc.update(extra)
    m = {"name": nome, "type": "rect", "interactive": interativo, "encode": {"update": enc}}
    if de:
        m["from"] = {"data": de}
    return m


def regra(nome: str, x, y, x2, y2, cor: str, *, larg: float = 1, tracejado: list | None = None,
          de: str | None = None, opac: str | None = None) -> dict:
    enc = {"x": s(x), "y": s(y), "x2": s(x2), "y2": s(y2),
           "stroke": {"value": cor} if cor.startswith("#") else {"signal": cor},
           "strokeWidth": {"signal": f"max(1, S*{larg})"}}
    if tracejado:
        enc["strokeDash"] = {"signal": f"[S*{tracejado[0]}, S*{tracejado[1]}]"}
    if opac:
        enc["opacity"] = {"signal": opac}
    m = {"name": nome, "type": "rule", "interactive": False, "encode": {"update": enc}}
    if de:
        m["from"] = {"data": de}
    return m


def pilula_reativa(nome: str, de: str, partes: list, *, ancora: str, alinhar: str, y_topo, h: float, pad: float,
                   raio: float, fundo: str, borda: str, borda_w: float = 1, opac: str | None = None,
                   xmin: float = 0, xmax: float = 1e6, folga: float = 4, topo_txt: float | None = None,
                   frac: str | None = None, sombra_on: bool = True) -> list:
    """Pílula com texto em partes (ex.: número Semibold + texto Regular) medida pela geometria reativa do Vega, sem
    estimar largura: marcas ocultas escrevem o texto FINAL em x=0, uma após a outra (bounds.x2 da anterior + folga), a
    pílula usa a largura medida e as partes visíveis se posicionam pela pílula. `partes` = [(texto_final, texto_vivo,
    tamanho, peso, cor)]; as expressões usam ROW para a linha de dados original e são de design (multiplicadas por S).
    `ancora`: x de design (centro da pílula, ou borda direita com alinhar='direita'); `y_topo`: topo de design."""
    n = len(partes)
    marcas = []
    for k, (tfinal, _tvivo, tam, peso, _cor) in enumerate(partes):
        linha = "datum" + ".datum" * k
        m = {"name": f"{nome}_med{k}", "type": "text", "interactive": False,
             "from": {"data": de if k == 0 else f"{nome}_med{k - 1}"},
             "encode": {"update": {
                 "x": {"signal": "0" if k == 0 else f"datum.bounds.x2 + S*{folga}"},
                 "y": s(0), "text": {"signal": tfinal.replace("ROW", linha)},
                 "font": {"value": FONTE}, "fontSize": s(tam), "fontWeight": {"value": peso},
                 "baseline": {"value": "alphabetic"}, "opacity": {"value": 0}}}}
        marcas.append(m)
    linha_pil = "datum" + ".datum" * n
    w = f"(datum.bounds.x2 + S*{2 * pad})"
    anc = ancora.replace("ROW", linha_pil)
    if alinhar == "frac":
        # fração da largura à esquerda da âncora, por linha (0 = começa na âncora, 0,5 = centrada, 1 = termina nela)
        fr = (frac or "0").replace("ROW", linha_pil)
        x = f"clamp(S*({anc}) - {w} * ({fr}), S*{xmin}, S*{xmax} - {w})"
    elif alinhar == "direita":
        x = f"clamp(S*({anc}) - {w}, S*{xmin}, S*{xmax} - {w})"
    elif alinhar == "esquerda":
        x = f"clamp(S*({anc}), S*{xmin}, S*{xmax} - {w})"
    else:
        x = f"clamp(S*({anc}) - {w} / 2, S*{xmin}, S*{xmax} - {w})"
    enc = {"x": {"signal": x}, "y": s(str(y_topo).replace("ROW", linha_pil)), "width": {"signal": w},
           "height": s(h), "cornerRadius": s(raio), "fill": {"value": fundo},
           "stroke": {"value": borda}, "strokeWidth": {"signal": f"max(1, S*{borda_w})"}}
    if sombra_on:
        enc.update(sombra())
    if opac:
        enc["opacity"] = {"signal": opac.replace("ROW", linha_pil)}
    marcas.append({"name": f"{nome}_pil", "type": "rect", "interactive": False,
                   "from": {"data": f"{nome}_med{n - 1}"}, "encode": {"update": enc}})
    linha_vis = "datum" + ".datum" * (n + 1)
    for j, (_tfinal, tvivo, tam, peso, cor) in enumerate(partes):
        med_j = "datum.datum" + ".datum" * (n - 1 - j)       # a marca oculta da parte j, vista da pílula
        desloc = "0" if j == 0 else f"{med_j}.bounds.x1"
        enc = {"x": {"signal": f"datum.x + S*{pad} + {desloc}"},
               "y": {"signal": f"datum.y + S*{round(((h - tam * 1.33) / 2 if topo_txt is None else topo_txt) + tam * ASC, 2)}"},
               "text": {"signal": tvivo.replace("ROW", linha_vis)}, "font": {"value": FONTE}, "fontSize": s(tam),
               "fontWeight": {"value": peso}, "fill": {"value": cor}, "align": {"value": "left"},
               "baseline": {"value": "alphabetic"}}
        if opac:
            enc["opacity"] = {"signal": opac.replace("ROW", linha_vis)}
        marcas.append({"name": f"{nome}_t{j}", "type": "text", "interactive": False,
                       "from": {"data": f"{nome}_pil"}, "encode": {"update": enc}})
    return marcas


def texto_partes(nome: str, de: str, partes: list, *, x, y, opac: str | None = None, folga: float = 4) -> list:
    """Texto corrido em partes com pesos/cores diferentes, emendadas pela geometria reativa (sem estimar largura):
    marcas ocultas escrevem o texto FINAL em x=0 em cadeia; cada parte visível nasce da sua oculta (x = início medido).
    `partes` = [(texto_final, texto_vivo, tamanho, peso, cor)]; ROW = linha de dados original; x e y de design."""
    marcas = []
    for k, (tfinal, _tv, tam, peso, _c) in enumerate(partes):
        marcas.append({"name": f"{nome}_med{k}", "type": "text", "interactive": False,
                       "from": {"data": de if k == 0 else f"{nome}_med{k - 1}"},
                       "encode": {"update": {
                           "x": {"signal": "0" if k == 0 else f"datum.bounds.x2 + S*{folga}"}, "y": s(0),
                           "text": {"signal": tfinal.replace("ROW", "datum" + ".datum" * k)},
                           "font": {"value": FONTE}, "fontSize": s(tam), "fontWeight": {"value": peso},
                           "baseline": {"value": "alphabetic"}, "opacity": {"value": 0}}}})
    for j, (_tf, tvivo, tam, peso, cor) in enumerate(partes):
        enc = {"x": {"signal": f"S*({x}) + datum.bounds.x1"}, "y": s(y),
               "text": {"signal": tvivo.replace("ROW", "datum.datum" + ".datum" * j)},
               "font": {"value": FONTE}, "fontSize": s(tam), "fontWeight": {"value": peso},
               "fill": {"value": cor}, "align": {"value": "left"}, "baseline": {"value": "alphabetic"}}
        if opac:
            enc["opacity"] = {"signal": opac}
        marcas.append({"name": f"{nome}_t{j}", "type": "text", "interactive": False,
                       "from": {"data": f"{nome}_med{j}"}, "encode": {"update": enc}})
    return marcas


def sombra() -> dict:
    """Sombra leve das pílulas do Figma (0 2 5 rgba(13,31,51,.06))."""
    return {"shadowColor": {"value": "rgba(13,31,51,0.10)"}, "shadowBlur": {"signal": "S*5"},
            "shadowOffsetY": {"signal": "S*2"}}


def spec(descricao: str, w0: float, h0: float, sinais: list, dados: list, marcas: list) -> dict:
    return {
        "$schema": "https://vega.github.io/schema/vega/v6.json",
        "description": descricao,
        "width": {"signal": f"isObject(denebContainer) && denebContainer.width > 0 ? denebContainer.width : {w0}"},
        "height": {"signal": f"isObject(denebContainer) && denebContainer.height > 0 ? denebContainer.height : {h0}"},
        "autosize": "none",
        "padding": 0,
        "config": {"font": FONTE, "background": "transparent", "text": {"font": FONTE}},
        "signals": sinais_escala(w0, h0) + sinais,
        "data": [{"name": "dataset"}] + dados,
        "marks": marcas,
    }


def gravar(caminho: Path, doc: dict) -> bool:
    texto_json = json.dumps(doc, ensure_ascii=False, indent=1) + "\n"
    caminho.parent.mkdir(parents=True, exist_ok=True)
    if caminho.exists() and caminho.read_text(encoding="utf-8") == texto_json:
        return False
    caminho.write_text(texto_json, encoding="utf-8", newline="\n")
    return True

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""capa_provar — provas da capa v2 no PBIP (saídas em pbi/qa/capa/pbip/).

    python -I -X utf8 pbi/scripts/capa_provar.py --motor     # no motor do Desktop aberto (qa/porta.txt):
        # (1) para ago/26 e mais 4 contextos, o texto de cada número da capa = o texto que o cartão da T1 mostra
        #     (as 12 contas de texto e o próprio HTML da capa, lidos do motor, contra o HTML dos 5 cartões da T1);
        # (2) CO Capa · HTML e CO Capa · ALT do motor = espelho Python do gerador (capa_medidas.html_capa), caractere
        #     a caractere; CO Capa · CSS = gerador; LEN de cada medida da capa
    python -I -X utf8 pbi/scripts/capa_provar.py --fundo-motor   # refaz o fundo da página com os números do motor
    python -I -X utf8 pbi/scripts/capa_provar.py --previa [--html motor.html]
        # no Edge headless, com o filme tocando do GitHub Pages: capturas nos takes 1, 2, 4 e na cena final, sincronia
        # (defasagem e entrada dos números), o botão de pausar (clique e teclado; números congelados junto; continua
        # parado quando o visual refaz o HTML), src inválido, movimento reduzido e autoplay recusado. Compara cada
        # captura com a do protótipo aprovado (pbi/qa/capa/prototipo-video) no mesmo instante.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(AQUI))
import capa_medidas as CM  # noqa: E402

QA = RAIZ / "qa" / "capa" / "pbip"
P = CM.P
MENOS = CM.MENOS

# ============================================================================================== motor: T1 × capa
CONTEXTOS = [
    ("ago26-padrao", "agosto de 2026 (padrão: último mês, todas as obras)", ""),
    ("jul26", "julho de 2026", "FILTER ( ALL ( dMesRef ), dMesRef[OrdemRef] = 3 )"),
    ("jan26", "janeiro de 2026", "FILTER ( ALL ( dMesRef ), dMesRef[OrdemRef] = 9 )"),
    ("ago26-cajueiro-potengi", "agosto de 2026, só CAJUEIRO e POTENGI", 'TREATAS ( { "CAJUEIRO", "POTENGI" }, dObra[Obra] )'),
    ("ago26-jangada", "agosto de 2026, só JANGADA (sem previsto)", 'TREATAS ( { "JANGADA" }, dObra[Obra] )'),
]
CARTOES_T1 = {"obras": "T1 · Cartão obras · HTML", "resultado": "T1 · Cartão resultado · HTML",
              "fisico": "T1 · Cartão físico · HTML", "desembolso": "T1 · Cartão desembolso · HTML",
              "sem_estoque": "T1 · Cartão sem estoque · HTML"}
DESENHO = ["CO Capa · HTML", "CO Capa · ALT", "CO Capa · CSS", "CO Capa · CSS fontes"]


def _texto(html: str) -> str:
    """O que o leitor vê: sem a tira do odômetro (<o-t>/<o-w>), sem script, sem tags."""
    html = re.sub(r"<o-w[^>]*>.*?</o-w>", "", html, flags=re.S)
    html = re.sub(r"<o-t[^>]*>.*?</o-t>", "", html, flags=re.S)
    html = re.sub(r"<script.*?</script>", "", html, flags=re.S)
    t = re.sub(r"<[^>]+>", "", html)
    return t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'").strip()


def _span(html: str, cls: str) -> tuple[str, bool] | None:
    """(texto, negativo) do <span class='… cls …'> de primeiro nível do cartão."""
    m = re.search(r"<span class='([^']*\b" + cls + r"\b[^']*)'>(.*?)</span>(?=<span class='b5|</div>)", html, re.S)
    if not m:
        return None
    return _texto(m.group(2)), " ng" in f" {m.group(1)}"


def pecas_t1(cartoes: dict) -> dict:
    """As peças de texto que os 5 cartões da T1 mostram (frente)."""
    out = {}
    for k, html in cartoes.items():
        hero = _span(html, "hero")
        lado = _span(html, "lado2")
        ctx_m = re.search(r"<p class='ctx'>(.*?)</p>", html, re.S)
        ctx_html = ctx_m.group(1) if ctx_m else ""
        out[k] = {"valor": hero[0] if hero else None, "valor_ng": hero[1] if hero else None,
                  "lado": lado[0] if lado else None, "lado_ng": lado[1] if lado else None,
                  "ctx": _texto(ctx_html), "ctx_ng": [_texto(x) for x in re.findall(r"<span class='ng'>(.*?)</span>",
                                                                                  ctx_html, re.S)]}
    return out


def pecas_capa(html: str) -> dict:
    """As peças de texto que a capa mostra em cada bloco de número."""
    out = {}
    for ident, *_r in CM.NUMEROS:
        m = re.search(rf"<div class='nm n\d b' data-ind='{ident}'>(.*?)</p></div>(?=<div class='nm|</div>)", html, re.S)
        bloco = m.group(1) if m else ""
        v = re.search(r"<p class='v( ng)?'>(.*?)</p>", bloco, re.S)
        ap = re.search(r"<p class='ap'>(.*)$", bloco, re.S)
        chips = [_texto(x) for x in re.findall(r"<span class='ch c[\dm]'>(.*?)</span>", bloco, re.S)]
        ap_html = ap.group(1) if ap else ""
        out[ident] = {"valor": _texto(v.group(2)) if v else None, "valor_ng": bool(v and v.group(1)),
                      "apoio": _texto(ap_html), "apoio_ng": [_texto(x) for x in re.findall(
                          r"<span class='ng'>(.*?)</span>", ap_html, re.S)], "chips": chips}
    return out


def comparar(t1: dict, capa: dict, contas: dict, mes_ant: str) -> list[dict]:
    """Cada número da capa contra a peça do cartão da T1 que diz o mesmo número."""
    linhas = []

    def par(ind, peca, capa_txt, t1_txt, conta=None):
        ok = capa_txt == t1_txt and (conta is None or contas[conta] == t1_txt)
        linhas.append({"indicador": ind, "peca": peca, "capa": capa_txt, "t1": t1_txt,
                       "conta": contas.get(conta) if conta else None, "igual": ok})

    def sep(txt, a, b=None):
        if txt is None or a not in txt:
            return None
        x = txt.split(a, 1)[1] if b is None else txt.split(a, 1)[0]
        return x
    o, r, f, d, s = (capa[k] for k in ("obras", "resultado", "fisico", "desembolso", "sem_estoque"))
    # obras
    par("obras", "valor", o["valor"], t1["obras"]["valor"], "Capa · obras · valor (texto)")
    par("obras", "orçamento", o["apoio"].removesuffix(" em orçamento"), t1["obras"]["lado"],
        "Capa · obras · orçamento (texto)")
    chips_t1 = [x.strip() for x in t1["obras"]["ctx"].split("·")]
    par("obras", "status (chips > 0)", " · ".join(o["chips"]),
        " · ".join(x for x in chips_t1 if not x.startswith("0 ")))
    # resultado
    par("resultado", "valor", r["valor"], t1["resultado"]["valor"], "Capa · resultado · valor (texto)")
    par("resultado", "valor negativo (vermelho)", str(r["valor_ng"]), str(t1["resultado"]["valor_ng"]))
    par("resultado", "% do orçamento", sep(r["apoio"], " do orçamento · ", True), t1["resultado"]["lado"],
        "Capa · resultado · % do orçamento (texto)")
    ctx = t1["resultado"]["ctx"]
    if ctx.startswith("sem mês anterior"):
        par("resultado", "variação", sep(r["apoio"], " do orçamento · "), ctx)
    else:
        par("resultado", "variação", sep(sep(r["apoio"], " do orçamento · "), " sobre ", True), sep(ctx, " sobre ", True),
            "Capa · resultado · variação (texto)")
        par("resultado", "mês anterior", sep(r["apoio"], " sobre "), sep(sep(ctx, " sobre "), " (", True))
    # vermelho na linha de apoio da capa = o que o cartão da T1 pinta das mesmas peças (o % e a variação; o resultado do
    # mês anterior, que a T1 também pinta, não aparece na capa)
    var_t1 = None if ctx.startswith("sem mês") else sep(ctx, " sobre ", True)
    esperado = ([t1["resultado"]["lado"]] if t1["resultado"]["lado_ng"] else []) + (
        [var_t1] if var_t1 and var_t1 in t1["resultado"]["ctx_ng"] else [])
    par("resultado", "vermelhos da linha de apoio", " | ".join(r["apoio_ng"]), " | ".join(esperado))
    dev_t1_ng = [x for x in t1["fisico"]["ctx_ng"]]
    par("fisico", "vermelhos da linha de apoio", " | ".join(f["apoio_ng"]), " | ".join(dev_t1_ng))
    # físico
    par("fisico", "valor", f["valor"], t1["fisico"]["valor"], "Capa · físico · valor (texto)")
    par("fisico", "previsto", sep(f["apoio"], " previsto · ", True), sep(t1["fisico"]["ctx"], " previsto · ", True),
        "Capa · físico · previsto (texto)")
    dev_t1 = sep(t1["fisico"]["ctx"], " previsto · ")
    par("fisico", "desvio", sep(f["apoio"], " previsto · "), dev_t1.split(" · ")[0] if dev_t1 else None,
        "Capa · físico · desvio (texto)")
    # desembolso
    par("desembolso", "valor", d["valor"], t1["desembolso"]["valor"], "Capa · desembolso · valor (texto)")
    par("desembolso", "previsto", d["apoio"].removesuffix(" previsto"), t1["desembolso"]["ctx"].removesuffix(" previsto"),
        "Capa · desembolso · previsto (texto)")
    # sem estoque
    par("sem_estoque", "valor", s["valor"], t1["sem_estoque"]["valor"], "Capa · sem estoque · valor (texto)")
    par("sem_estoque", "valor negativo (vermelho)", str(s["valor_ng"]), str(t1["sem_estoque"]["valor_ng"]))
    par("sem_estoque", "pagos e não aplicados", s["apoio"].removesuffix(" pagos e ainda não aplicados"),
        t1["sem_estoque"]["ctx"].removesuffix(" pagos e ainda não aplicados"),
        "Capa · sem estoque · pagos não aplicados (texto)")
    return linhas


DEFINIR = ""        # --definir: as medidas da capa entram como DEFINE MEASURE (prova antes de aplicar no modelo)


def definir_medidas() -> str:
    defs = []
    for p in sorted(CM.DESTINO.glob("*.dax")):
        t = p.read_text(encoding="utf-8")
        m = re.search(r"@nome:\s*(.*)", t)
        nome = m.group(1).strip() if m else p.stem
        defs.append(f"MEASURE '_Medidas'[{nome}] =" + chr(10) + t[t.index("*/") + 2:].strip())
    return "DEFINE" + chr(10) + chr(10).join(defs) + chr(10)


def consulta(filtro: str) -> str:
    colunas = [f'"{v}", [{m}]' for v, m in CM.LEITURAS]
    colunas += [f'"t1_{k}", [{m}]' for k, m in CARTOES_T1.items()]
    colunas += [f'"d{i}", [{m}]' for i, m in enumerate(DESENHO)]
    colunas += [f'"len{i}", LEN ( [{m}] )' for i, m in enumerate(DESENHO)]
    linha = "ROW ( " + ", ".join(colunas) + " )"
    return DEFINIR + f"EVALUATE {f'CALCULATETABLE ( {linha}, {filtro} )' if filtro else linha}"


def motor() -> int:
    from dax import consultar
    saida, falhas = [], 0
    css_gerador = CM.css_capa()
    for chave, rotulo, filtro in CONTEXTOS:
        r = consultar(consulta(filtro))[0]
        v = {k.strip("[]"): x for k, x in r.items()}
        leituras = {var: v[var] for var, _m in CM.LEITURAS}
        contas = {m: v[var] for var, m in CM.LEITURAS if m.startswith("Capa ·")}
        html_motor, alt_motor, css_motor, fontes_motor = (v[f"d{i}"] for i in range(4))
        html_esp, alt_esp = CM.html_capa(leituras), CM.alt_capa(leituras)
        t1 = pecas_t1({k: v[f"t1_{k}"] for k in CARTOES_T1})
        capa = pecas_capa(html_motor)
        pares = comparar(t1, capa, contas, leituras["_mesAnt"])
        iguais = sum(p["igual"] for p in pares)
        espelho = {"html": html_motor == html_esp, "alt": alt_motor == alt_esp,
                   "css": css_motor == CM.css_fontes() + css_gerador, "fontes": fontes_motor == CM.css_fontes()}
        ctx_falhas = (len(pares) - iguais) + sum(not x for x in espelho.values())
        falhas += ctx_falhas
        if not espelho["html"]:
            (QA / "motor").mkdir(parents=True, exist_ok=True)
            (QA / "motor" / f"html-motor-{chave}.html").write_text(html_motor, encoding="utf-8")
            (QA / "motor" / f"html-espelho-{chave}.html").write_text(html_esp, encoding="utf-8")
        saida.append({"contexto": chave, "rotulo": rotulo, "filtro": filtro or "(nenhum)",
                      "mes": leituras["_mes"], "pares": pares, "iguais": iguais, "total": len(pares),
                      "espelho_igual": espelho,
                      "len": {m: v[f"len{i}"] for i, m in enumerate(DESENHO)}, "alt": alt_motor})
        print(f"{chave:<18} {leituras['_mes']:<17} T1 × capa: {iguais}/{len(pares)} iguais · espelho "
              + " ".join(f"{k} {'=' if x else '≠'}" for k, x in espelho.items())
              + f" · LEN HTML {v['len0']:,} · ALT {v['len1']} · CSS {v['len2']:,}".replace(",", "."))
        for p in pares:
            if not p["igual"]:
                print(f"   ≠ {p['indicador']} · {p['peca']}: capa {p['capa']!r} · T1 {p['t1']!r} · conta {p['conta']!r}")
    QA.mkdir(parents=True, exist_ok=True)
    (QA / "prova-motor.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    md = ["# Capa × T1 no motor", "", f"{len(CONTEXTOS)} contextos; cada número da capa contra a peça do cartão da T1 "
          "que diz o mesmo número (texto visível, sem a tira do odômetro). `conta` = a medida de texto da capa.", ""]
    for c in saida:
        md += [f"## {c['rotulo']}", "", f"Filtro: `{c['filtro']}` · mês de referência: {c['mes']} · "
               f"{c['iguais']}/{c['total']} iguais · espelho do gerador: "
               + ", ".join(f"{k} {'igual' if x else 'DIFERENTE'}" for k, x in c["espelho_igual"].items()), "",
               "| indicador | peça | capa | cartão da T1 | igual |", "|---|---|---|---|---|"]
        md += [f"| {p['indicador']} | {p['peca']} | {str(p['capa']).replace('|', '·')} | "
               f"{str(p['t1']).replace('|', '·')} | {'sim' if p['igual'] else 'NÃO'} |"
               for p in c["pares"]]
        md += ["", f"LEN: " + " · ".join(f"{k} {x:,}".replace(",", ".") for k, x in c["len"].items()), "",
               f"ALT: {c['alt']}", ""]
    (QA / "prova-motor.md").write_text("\n".join(md), encoding="utf-8")
    print(f"prova em {QA / 'prova-motor.md'} · {falhas} falha(s)")
    return 1 if falhas else 0


# ============================================================================================ prévia no Edge
ESTADO_JS = r"""(() => { const v = document.querySelector('video.filme'), R = document.documentElement,
  b = document.querySelector('.uc .pz'), an = document.getAnimations().filter(a => a.animationName);
  return {classes: R.className, src: v && v.getAttribute('src'), paused: v ? v.paused : null,
          currentTime: v ? v.currentTime : null, botao: b ? b.getAttribute('aria-label') : null,
          botao_visivel: b ? getComputedStyle(b).display !== 'none' : false,
          animacoes: an.length, pausadas: an.filter(a => a.playState === 'paused').length}; })()"""
# congelado = cada número (opacidade, posição), cada janela do odômetro, a tira e a régua, num instante
FOTO_JS = r"""(() => Array.from(document.querySelectorAll('.uc .nm, .uc o-w, .uc o-t, .uc .rl span, .uc .ps i, .uc .rid'))
  .map(e => { const s = getComputedStyle(e); return [s.opacity, s.transform, s.width]; }))()"""


def _captura_svg(nome_video: str) -> Path:
    return RAIZ / "qa" / "capa" / "prototipo-video" / nome_video


def previa(html_motor: Path | None) -> int:
    import numpy as np
    from PIL import Image
    from playwright.sync_api import sync_playwright
    pasta = QA / "previa"
    pasta.mkdir(parents=True, exist_ok=True)
    if html_motor:
        arq = pasta / "previa-capa-motor.html"
        arq.write_text(CM.previa(html_motor.read_text(encoding="utf-8"), CM.css_fontes() + CM.css_capa(),
                                 "Capa · HTML do motor"), encoding="utf-8", newline="\n")
    else:
        arq = CM.gravar_previa()
    texto = arq.read_text(encoding="utf-8")
    falha = pasta / "previa-capa-falha.html"
    invalido = CM.VIDEO.rsplit("/", 1)[0] + "/nao-existe.mp4"
    falha.write_text(texto.replace(f'src="{CM.VIDEO}"', f'src="{invalido}"', 1), encoding="utf-8", newline="\n")
    out: dict = {"pagina": str(arq), "video": CM.VIDEO}
    erros: list[str] = []
    tela = {"width": 1920, "height": 1080}

    def compara(a: Path, b: Path) -> dict:
        x = np.asarray(Image.open(a).convert("RGB"), dtype=np.int16)
        y = np.asarray(Image.open(b).convert("RGB"), dtype=np.int16)
        dd = np.abs(x - y).max(axis=2)
        # fora do botão de pausar (x 66–110, y 80–120), que o protótipo não tem
        mascara = np.ones(dd.shape, bool)
        mascara[80:120, 66:110] = False
        return {"ref": b.name, "media": round(float(dd[mascara].mean()), 3),
                "px_acima_32_pct": round(100 * float((dd[mascara] > 32).mean()), 3), "max": int(dd[mascara].max())}

    with sync_playwright() as pw:
        nav = pw.chromium.launch(channel="msedge", headless=True)
        out["navegador"] = f"Edge {nav.version} headless"
        pag = nav.new_page(viewport=tela, device_scale_factor=1)
        pag.goto(arq.resolve().as_uri())
        pag.evaluate(P.QA_JS)
        pag.wait_for_function("!document.documentElement.classList.contains('uo-espera')", timeout=30000)
        pag.evaluate("document.fonts.ready")
        out["tocando"] = pag.evaluate(ESTADO_JS)
        print("tocando:", out["tocando"])
        # sincronia num laço inteiro (o mesmo instrumento do protótipo)
        pag.evaluate("__qa.vai(0, 2)")
        reg = pag.evaluate("ms => __qa.log(ms, false)", 34500)
        out["sinc"] = P._sinc(reg)
        print("defasagem (linha − vídeo):", out["sinc"]["laco_1"])
        for tk in out["sinc"]["takes"]:
            print(f"  take {tk['take']}: entra {tk['entra_no_quadro_s']} s, conta {tk['conta_de_s']}–{tk['conta_ate_s']} s,"
                  f" sai {tk['sai_no_quadro_s']} s")
        # capturas nos instantes do protótipo
        caps = []
        for nome, t, _ref in P.CAPTURAS_VIDEO:
            mt = pag.evaluate("t => __qa.vai(t, 2)", t)
            destino = pasta / nome.replace("capa-v2-video", "capa-pbip").replace("apoio-video", "apoio-pbip")
            pag.screenshot(path=str(destino))
            c = compara(destino, _captura_svg(nome))
            c.update({"arquivo": destino.name, "t": t, "quadro": round(mt, 4)})
            caps.append(c)
            print(f"captura {destino.name}: quadro {mt:.3f} s · × protótipo: média {c['media']} · >32 {c['px_acima_32_pct']}%")
        out["capturas"] = caps
        # botão de pausar: clique no take 1 com o número na tela
        pag.evaluate("__qa.vai(4.2, 2)")
        bx = pag.locator(".uc .pz").bounding_box()
        out["botao_caixa"] = bx
        pag.mouse.click(bx["x"] + bx["width"] / 2, bx["y"] + bx["height"] / 2)
        pag.wait_for_timeout(300)
        e1, f1 = pag.evaluate(ESTADO_JS), pag.evaluate(FOTO_JS)
        pag.screenshot(path=str(pasta / "pausa-1-clicado.png"))
        pag.wait_for_timeout(2000)
        e2, f2 = pag.evaluate(ESTADO_JS), pag.evaluate(FOTO_JS)
        pag.screenshot(path=str(pasta / "pausa-2-dois-segundos-depois.png"))
        congelado = f1 == f2 and e1["currentTime"] == e2["currentTime"] and e2["paused"]
        defas = pag.evaluate("""() => { const v = document.querySelector('video.filme');
          const a = document.getAnimations().find(x => x.animationName === 'n0');
          return a ? (a.currentTime / 1000 - v.currentTime) * 1000 : null; }""")
        out["pausa"] = {"estado": e2, "congelado": congelado, "linha_menos_video_ms": defas,
                        "pixels_iguais": compara(pasta / "pausa-1-clicado.png", pasta / "pausa-2-dois-segundos-depois.png")}
        print("pausado:", e2, "· congelado:", congelado, f"· linha − vídeo {defas} ms")
        if not (congelado and e2["botao"] == "Tocar o filme" and e2["pausadas"] == e2["animacoes"] and "uo-pausa" in e2["classes"]):
            erros.append("pausa: vídeo, números ou botão não congelaram juntos")
        # o visual refaz o HTML com o filme pausado (filtro, redimensionar): continua parado no mesmo quadro
        corpo = re.search(r'(<div class="uc".*?)<script>', texto, re.S).group(1)
        script = re.search(r"<script>(.*?)</script>", texto, re.S).group(1)
        pag.evaluate("""([uc, scr]) => { document.querySelector('.uc').remove();
          const host = document.querySelector('.htmlViewerEntry > div'); host.innerHTML = uc;
          const s = document.createElement('script'); s.textContent = scr; host.appendChild(s); }""",
                     [corpo, script])
        pag.wait_for_function("!document.documentElement.classList.contains('uo-espera')", timeout=15000)
        pag.wait_for_timeout(600)
        e3 = pag.evaluate(ESTADO_JS)
        pag.screenshot(path=str(pasta / "pausa-3-visual-refeito.png"))
        out["pausa_refeito"] = {"estado": e3, "mesmo_quadro": abs((e3["currentTime"] or 0) - e2["currentTime"]) < 0.02,
                                "pixels_iguais": compara(pasta / "pausa-2-dois-segundos-depois.png",
                                                         pasta / "pausa-3-visual-refeito.png")}
        print("refeito pausado:", out["pausa_refeito"])
        if not (e3["paused"] and out["pausa_refeito"]["mesmo_quadro"] and e3["botao"] == "Tocar o filme"):
            erros.append("pausa: o visual refeito não continuou parado no mesmo quadro")
        # tocar de novo pelo teclado (foco no botão + Enter)
        pag.mouse.move(5, 1075)
        pag.evaluate("document.activeElement && document.activeElement.blur && document.activeElement.blur()")
        pag.keyboard.press("Tab")
        out["foco_teclado"] = pag.evaluate("document.activeElement && document.activeElement.className")
        pag.wait_for_timeout(200)
        pag.screenshot(path=str(pasta / "pausa-4-foco-teclado.png"), clip={"x": 40, "y": 10, "width": 520, "height": 130})
        if out["foco_teclado"] != "pz":
            erros.append(f"teclado: o Tab não levou o foco ao botão (foi para {out['foco_teclado']!r})")
        pag.keyboard.press("Enter")
        pag.wait_for_function("!document.querySelector('video.filme').paused", timeout=5000)
        pag.wait_for_timeout(1500)
        e4 = pag.evaluate(ESTADO_JS)
        reg2 = pag.evaluate("ms => __qa.log(ms, false)", 2500)
        d2 = P._sinc(reg2)["laco_1"]
        out["tocar_de_novo"] = {"estado": e4, "defasagem": d2}
        print("tocando de novo:", e4, "· defasagem", d2)
        if not (not e4["paused"] and e4["pausadas"] == 0 and e4["botao"] == "Pausar o filme"
                and d2 and d2["max_abs_ms"] <= 1000 / 60):
            erros.append("tocar de novo: vídeo e números não voltaram juntos")
        nav.close()
        # sem vídeo: src inválido, movimento reduzido e autoplay recusado → pôster com os 5 números
        for nome, opcoes, url, args in (
                ("estado-sem-video-src-invalido", {}, falha.resolve().as_uri(), []),
                ("estado-movimento-reduzido", {"reduced_motion": "reduce"}, arq.resolve().as_uri(), []),
                ("estado-autoplay-recusado", {}, arq.resolve().as_uri(), ["--autoplay-policy=user-gesture-required"])):
            nv = pw.chromium.launch(channel="msedge", headless=True, args=args)
            ctx = nv.new_context(viewport=tela, device_scale_factor=1, **opcoes)
            pg = ctx.new_page()
            pg.goto(url)
            pg.wait_for_function("document.documentElement.classList.contains('uo-parado')", timeout=15000)
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(2500)
            est = pg.evaluate(ESTADO_JS)
            pg.screenshot(path=str(pasta / f"{nome}.png"))
            c = compara(pasta / f"{nome}.png", _captura_svg("estado-falha-src-invalido.png"))
            out[nome] = {"estado": est, "x_prototipo_falha": c}
            print(f"{nome}: {est} · × protótipo (falha): média {c['media']}")
            if est["botao_visivel"]:
                erros.append(f"{nome}: botão de pausar visível sem filme")
            nv.close()
    out["erros"] = erros
    (pasta / "medicoes.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"medições em {pasta / 'medicoes.json'} · {len(erros)} erro(s)")
    for e in erros:
        print("  [ERRO]", e)
    return 1 if erros else 0


def fundo_motor() -> int:
    """Refaz o fundo da página (wp-capa.jpg) com os números que o motor dá hoje no contexto da capa (sem filtro)."""
    from dax import consultar
    r = consultar(consulta(""))[0]
    v = {k.strip("[]"): x for k, x in r.items()}
    leituras = {var: v[var] for var, _m in CM.LEITURAS}
    print("fundo com", leituras["_mes"], "·", CM.render_fundo(leituras))
    return 0


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--motor", action="store_true")
    ap.add_argument("--previa", action="store_true")
    ap.add_argument("--html", type=Path, help="HTML da medida lido do motor (para a prévia)")
    ap.add_argument("--definir", action="store_true", help="--motor com as medidas da capa em DEFINE (antes de aplicar)")
    ap.add_argument("--fundo-motor", action="store_true",
                    help="refaz pbi/assets/wallpapers/wp-capa.jpg com os números do motor (depois: montar_pbip --aplicar)")
    a = ap.parse_args(argv)
    if a.definir:
        global DEFINIR
        DEFINIR = definir_medidas()
    rc = 0
    if a.motor:
        rc |= motor()
    if a.previa:
        rc |= previa(a.html)
    if a.fundo_motor:
        rc |= fundo_motor()
    if not (a.motor or a.previa or a.fundo_motor):
        ap.error("diga --motor, --previa e/ou --fundo-motor")
    return rc


if __name__ == "__main__":
    sys.exit(main())

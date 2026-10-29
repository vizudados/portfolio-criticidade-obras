// Leitura do SVG de traço (gerado por pbi/spec/capa/animacao/vetorizar_traco.py) e o estado de cada classe de tempo
// num instante. É a mesma técnica do protótipo (montar_capa_v2.agrupar_por_classe + css_filme): um <g> por classe kN,
// com o stroke-dashoffset no grupo, herdado pelos traços; o tracejado só existe enquanto o traço cresce.

import { Easing } from "remotion";

export type Classe = {
  readonly atraso: number; // s, início do crescimento na cena
  readonly duracao: number; // s
  readonly html: string; // <g stroke-width="…"><path …/>…</g>… desta classe
};

export type Traco = {
  readonly viewBox: string;
  readonly classes: readonly Classe[];
  readonly tracos: number;
};

const OCULTO = 1.001; // dashoffset de traço ainda não desenhado (o tracejado "1 2" fica todo em vão)
const EASE = Easing.bezier(0.4, 0.05, 0.55, 1); // cubic-bezier(.4,.05,.55,1), o do protótipo

export const lerTraco = (svg: string): Traco => {
  const cab = svg.match(/<svg[^>]*>/);
  if (!cab) throw new Error("SVG sem cabeçalho");
  const viewBox = cab[0].match(/viewBox="([^"]+)"/)?.[1];
  const tempos = cab[0].match(/data-tempos="([^"]+)"/)?.[1];
  if (!viewBox || !tempos) throw new Error("SVG sem viewBox ou data-tempos (gere com vetorizar_traco.py)");
  const pares = tempos.split(";").map((p) => p.split(",").map(Number) as [number, number]);
  const por: Map<number, Map<string, string[]>> = new Map();
  let tracos = 0;
  const grupos = svg.matchAll(/<g stroke-width="([^"]+)">([\s\S]*?)<\/g>/g);
  for (const [, largura, corpo] of grupos) {
    for (const [p] of corpo.matchAll(/<path [^>]*\/>/g)) {
      const c = p.match(/\sclass="k(\d+)"/);
      if (!c) throw new Error("traço sem classe de tempo");
      const k = Number(c[1]);
      const porLargura = por.get(k) ?? new Map<string, string[]>();
      const lista = porLargura.get(largura) ?? [];
      lista.push(p.replace(c[0], ""));
      porLargura.set(largura, lista);
      por.set(k, porLargura);
      tracos++;
    }
  }
  if (tracos !== (svg.match(/<path/g) ?? []).length) throw new Error("traços perdidos ao agrupar");
  const classes = [...por.keys()]
    .sort((a, b) => a - b)
    .map((k) => {
      const [atraso, duracao] = pares[k];
      let html = "";
      for (const [w, ps] of por.get(k)!) html += `<g stroke-width="${w}">${ps.join("")}</g>`;
      return { atraso, duracao, html };
    });
  return { viewBox, classes, tracos };
};

// Estado de uma classe no instante t (s, relógio da cena): o mesmo dos keyframes do protótipo
// (ESPERA → CRESCE 1,001 → CRESCE 0 → PRONTO).
export const estadoClasse = (t: number, c: Classe): React.CSSProperties => {
  if (t < c.atraso) {
    return { visibility: "hidden", strokeDasharray: "1 2", strokeDashoffset: OCULTO };
  }
  if (t < c.atraso + c.duracao) {
    const p = EASE((t - c.atraso) / c.duracao);
    return { visibility: "visible", strokeDasharray: "1 2", strokeDashoffset: OCULTO * (1 - p) };
  }
  return { visibility: "visible", strokeDasharray: "none", strokeDashoffset: 0 };
};

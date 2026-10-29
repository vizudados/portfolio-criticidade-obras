#!/usr/bin/env node
// render_vega.mjs - renderiza uma spec Deneb (Vega) fora do Power BI, na caixa exata do visual.
// Portado de outro projeto (22/09/2026). Mudança: VEGA_MODULES (ou TORRE_VEGA_MODULES) para
// apontar o node_modules com Vega 6.4.0; o padrão é o node_modules da raiz do repositório, usado SÓ PARA LEITURA (nada é instalado).
//
// Emula o que o Deneb faz antes de entregar a spec ao Vega (codigo-fonte do Deneb, tags 2.0.0.0 e
// 1.9.1.0, lido em 22/09/2026):
//   - Deneb 2.0 (padrao, --deneb 2): troca no TEXTO da spec pbiContainerWidth -> denebContainer.width,
//     pbiContainerHeight -> denebContainer.height, pbiContainer -> denebContainer; acrescenta o sinal
//     denebContainer {width,height,scrollWidth,scrollHeight,scrollTop,scrollLeft} (se a spec nao o
//     define) e, sem width/height na spec, usa {signal:"denebContainer.width|height"}.
//   - Deneb 1.9 (--deneb 1): sinais pbiContainerWidth/pbiContainerHeight (aqui com valor fixo; no
//     Deneb sao containerSize()) e pbiContainer; width/height padrao nesses sinais.
//   - config: {background:"transparent", customFormatTypes:true} + a config do Deneb (--config),
//     sem width/height "container" e com autosize.resize=false.
//   - dados: o dataset vira data[name=dataset].values; cada linha ganha __row__ (indice), __selected__
//     (--selected) e, com --formato, Campo__format/Campo__formatted. Nomes de campo codificados como
//     no Deneb (\ " . [ ] viram _). Datas viram Date (no Deneb: new Date(valor)).
//   - funcoes de expressao do Deneb (registradas antes do parse): pbiColor, pbiFormat,
//     pbiFormatAutoUnit, pbiPatternSVG, pbiCrossFilterApply, pbiCrossFilterClear; esquemas
//     pbiColorNominal/Ordinal/Linear/Divergent. Aqui sao simulacoes (ver RESULTADO).
//   - nada externo: o loader recusa URL e arquivo (so o dataset interno vale).
// Runtime daqui: Vega 6.4.0 do node_modules do Construtora (= Deneb 2.0). Deneb 1.9.1 roda Vega 6.2.0.
//
// Uso:
//   node render_vega.mjs --spec deneb/VG/otif.json --dados qa/VG/otif.tsv --caixa 900x320 --saida qa/VG/otif
//   opcoes: --config cfg.json  --tema tema.json  --campos "Semana=dCalendario[Bloco],OTIF=[OTIF %]"
//           --selected neutral|on|off|ausente|Campo=valor|linhas=0,2   --formato "OTIF=0.0%"
//           --sinal nome=valorJSON  --quadro-inicial  --esperar 1500  --escala 2  --fundo #FFFFFF|transparente
//           --svg  --deneb 1|2  --cultura pt-BR  --visual <visual.json> (em vez de --caixa)
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';

const RAIZ = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const MODULOS = process.env.VIZU_VEGA_MODULES || process.env.VEGA_MODULES || process.env.TORRE_VEGA_MODULES
  || path.join(RAIZ, 'node_modules');   // só leitura
const req = createRequire(path.join(path.dirname(MODULOS), '_ancora_.js'));

function falhar(msg, codigo = 1) {
  console.error('ERRO ' + msg);
  process.exit(codigo);
}

const { values: op } = parseArgs({
  options: {
    spec: { type: 'string' }, dados: { type: 'string' }, caixa: { type: 'string' }, visual: { type: 'string' },
    saida: { type: 'string' }, config: { type: 'string' }, tema: { type: 'string' }, campos: { type: 'string' },
    selected: { type: 'string', default: 'neutral' }, formato: { type: 'string', multiple: true, default: [] },
    sinal: { type: 'string', multiple: true, default: [] }, 'quadro-inicial': { type: 'boolean', default: false },
    esperar: { type: 'string', default: '1500' }, escala: { type: 'string', default: '2' },
    fundo: { type: 'string', default: '#FFFFFF' }, svg: { type: 'boolean', default: false },
    deneb: { type: 'string', default: '2' }, cultura: { type: 'string', default: 'pt-BR' },
    caixas: { type: 'boolean', default: false },
  },
  allowPositionals: false,
});
if (!op.spec || !op.saida || (!op.caixa && !op.visual)) {
  falhar('uso: node render_vega.mjs --spec <spec.json> [--dados <.tsv|.json>] (--caixa LxA | --visual visual.json) --saida <prefixo> [opcoes]');
}

// ---------------------------------------------------------------- fontes: registradas ANTES de carregar o Vega
// (o node-canvas so enxerga fonte registrada antes de criar o canvas; o Vega cria o de medir texto ao carregar)
const canvasMod = req('canvas');
const FONTES = [['segoeui.ttf', 'normal', 'normal'], ['segoeuib.ttf', 'bold', 'normal'], ['seguisb.ttf', '600', 'normal'],
  ['segoeuil.ttf', '300', 'normal'], ['segoeuisl.ttf', '350', 'normal'], ['segoeuii.ttf', 'normal', 'italic'],
  ['segoeuiz.ttf', 'bold', 'italic']];
for (const [arq, weight, style] of FONTES) {
  const p = path.join(process.env.WINDIR || 'C:/Windows', 'Fonts', arq);
  if (fs.existsSync(p)) {
    try { canvasMod.registerFont(p, { family: 'Segoe UI', weight, style }); } catch { /* segue sem */ }
  }
}
const vega = await import(pathToFileURL(req.resolve('vega')).href);
const { interpolateRgbBasis } = await import(pathToFileURL(req.resolve('d3-interpolate')).href);

// ---------------------------------------------------------------- caixa
let W, H;
if (op.caixa) {
  const m = /^\s*(\d+)\s*[xX]\s*(\d+)\s*$/.exec(op.caixa);
  if (!m) falhar('--caixa no formato LxA, ex. 900x320');
  W = Number(m[1]); H = Number(m[2]);
} else {
  const pos = JSON.parse(fs.readFileSync(op.visual, 'utf8').replace(/^\uFEFF/, '')).position;
  W = Math.round(pos.width); H = Math.round(pos.height);
}
const ESCALA = Math.max(1, Number(op.escala) || 2);
const avisos = [];
const chamadas = { pbiColor: new Set(), pbiFormat: new Set(), pbiFormatAutoUnit: new Set(), pbiPatternSVG: 0, pbiCrossFilterApply: 0, pbiCrossFilterClear: 0 };

// ---------------------------------------------------------------- tema (pbiColor e esquemas)
const PALETA_PADRAO = ['#118DFF', '#12239E', '#E66C37', '#6B007B', '#E044A7', '#744EC2', '#D9B300', '#D64550', '#197278', '#1AAB40',
  '#15C6F4', '#4092FF', '#FFA058', '#BE5DC9', '#F472D0', '#B5A1FF', '#C4A200', '#FF8080', '#00DBBC', '#5BD667', '#0091D5', '#4668C5',
  '#FF6300', '#99008A', '#EC008C', '#533285', '#99700A', '#FF4141', '#1F9A85', '#25891C', '#0057A2', '#002050', '#C94F0F', '#450F54',
  '#B60064', '#34124F', '#6A5A29', '#1AAB40', '#BA141A', '#0C3D37'];
const tema = { cores: PALETA_PADRAO, negative: '#D64554', positive: '#1AAB40', neutral: '#D9B300', minimum: '#DEEFFF', center: '#D9B300', maximum: '#118DFF', fonte: 'padrao do Power BI (shim do Deneb)' };
if (op.tema) {
  const t = JSON.parse(fs.readFileSync(op.tema, 'utf8').replace(/^\uFEFF/, ''));
  if (Array.isArray(t.dataColors) && t.dataColors.length) tema.cores = t.dataColors;
  if (t.bad) tema.negative = t.bad;
  if (t.good) tema.positive = t.good;
  if (t.neutral) tema.neutral = t.neutral;
  if (t.minimum) tema.minimum = t.minimum;
  if (t.center) tema.center = t.center;
  if (t.maximum) tema.maximum = t.maximum;
  tema.fonte = op.tema;
}
function shadeColor(color, percent) {           // igual a @deneb-viz/utils/color
  const f = parseInt(color.slice(1), 16), t = percent < 0 ? 0 : 255, p = percent < 0 ? percent * -1 : percent;
  const R = f >> 16, G = (f >> 8) & 0x00ff, B = f & 0x0000ff;
  return `#${(0x1000000 + (Math.round((t - R) * p) + R) * 0x10000 + (Math.round((t - G) * p) + G) * 0x100 + (Math.round((t - B) * p) + B)).toString(16).slice(1)}`;
}
const NOMEADAS = () => ({ max: tema.maximum, min: tema.minimum, middle: tema.center, negative: tema.negative, bad: tema.negative, positive: tema.positive, good: tema.positive, neutral: tema.neutral });

// ---------------------------------------------------------------- pbiFormat (subconjunto do formato .NET/Power BI)
const CULTURAS = {
  'pt-BR': { milhar: '.', decimal: ',', meses: ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'], dias: ['domingo', 'segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado'] },
  'en-US': { milhar: ',', decimal: '.', meses: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'], dias: ['Sunday', 'formulário', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'] },
};
const NOMES_FORMATO = { 'percent': '0.00%', 'fixed': '0.00', 'standard': '#,0.00', 'general number': '', 'general': '' };

function secoes(fmt) {
  const out = []; let atual = '', aspas = null;
  for (let i = 0; i < fmt.length; i++) {
    const c = fmt[i];
    if (aspas) { atual += c; if (c === aspas) aspas = null; continue; }
    if (c === '"' || c === "'") { aspas = c; atual += c; continue; }
    if (c === '\\' && i + 1 < fmt.length) { atual += c + fmt[i + 1]; i++; continue; }
    if (c === ';') { out.push(atual); atual = ''; continue; }
    atual += c;
  }
  out.push(atual);
  return out;
}

function formatarNumeroSecao(v, sec, cult) {
  // separa prefixo literal, bloco numerico e sufixo literal
  const tokens = []; let i = 0;
  while (i < sec.length) {
    const c = sec[i];
    if (c === '"' || c === "'") { const j = sec.indexOf(c, i + 1); tokens.push({ lit: sec.slice(i + 1, j < 0 ? sec.length : j) }); i = j < 0 ? sec.length : j + 1; continue; }
    if (c === '\\') { tokens.push({ lit: sec[i + 1] || '' }); i += 2; continue; }
    if ('0#.,'.includes(c)) { tokens.push({ num: c }); i++; continue; }
    if (c === '%' || c === '\u2030') { tokens.push({ pct: c }); i++; continue; }
    tokens.push({ lit: c }); i++;
  }
  const idxNum = tokens.map((t, k) => (t.num ? k : -1)).filter(k => k >= 0);
  if (!idxNum.length) return tokens.map(t => t.lit ?? t.pct ?? '').join('');
  const ini = idxNum[0], fim = idxNum[idxNum.length - 1];
  const bloco = tokens.slice(ini, fim + 1).map(t => t.num ?? '').join('');
  let escala = 1;
  for (const t of tokens) { if (t.pct === '%') escala *= 100; if (t.pct === '\u2030') escala *= 1000; }
  const ponto = bloco.indexOf('.');
  let inteira = ponto < 0 ? bloco : bloco.slice(0, ponto);
  const frac = ponto < 0 ? '' : bloco.slice(ponto + 1).replace(/,/g, '');
  const mVirg = /,+$/.exec(inteira);
  if (mVirg) { escala /= Math.pow(1000, mVirg[0].length); inteira = inteira.slice(0, -mVirg[0].length); }
  const agrupa = inteira.includes(',');
  const minInt = (inteira.match(/0/g) || []).length;
  const minDec = (frac.match(/0/g) || []).length, maxDec = frac.length;
  let n = Math.abs(v) * escala;
  let txt = n.toFixed(maxDec);
  let [pInt, pDec = ''] = txt.split('.');
  while (pDec.length > minDec && pDec.endsWith('0')) pDec = pDec.slice(0, -1);
  if (pInt === '0' && minInt === 0 && pDec) pInt = '';
  pInt = pInt.padStart(minInt, '0');
  if (agrupa) pInt = pInt.replace(/\B(?=(\d{3})+(?!\d))/g, cult.milhar);
  const numero = pInt + (pDec ? cult.decimal + pDec : '');
  const antes = tokens.slice(0, ini).map(t => t.lit ?? t.pct ?? '').join('');
  const depois = tokens.slice(fim + 1).map(t => t.lit ?? t.pct ?? '').join('');
  return antes + numero + depois;
}

function formatarData(d, fmt, cult) {
  const p2 = x => String(x).padStart(2, '0');
  return fmt.replace(/"[^"]*"|'[^']*'|\\.|yyyy|yy|MMMM|MMM|MM|M|dddd|ddd|dd|d|HH|H|hh|h|mm|m|ss|s|tt/g, (t) => {
    if (t[0] === '"' || t[0] === "'") return t.slice(1, -1);
    if (t[0] === '\\') return t.slice(1);
    switch (t) {
      case 'yyyy': return String(d.getFullYear()); case 'yy': return p2(d.getFullYear() % 100);
      case 'MMMM': return cult.meses[d.getMonth()]; case 'MMM': return cult.meses[d.getMonth()].slice(0, 3);
      case 'MM': return p2(d.getMonth() + 1); case 'M': return String(d.getMonth() + 1);
      case 'dddd': return cult.dias[d.getDay()]; case 'ddd': return cult.dias[d.getDay()].slice(0, 3);
      case 'dd': return p2(d.getDate()); case 'd': return String(d.getDate());
      case 'HH': return p2(d.getHours()); case 'H': return String(d.getHours());
      case 'hh': return p2(d.getHours() % 12 || 12); case 'h': return String(d.getHours() % 12 || 12);
      case 'mm': return p2(d.getMinutes()); case 'm': return String(d.getMinutes());
      case 'ss': return p2(d.getSeconds()); case 's': return String(d.getSeconds());
      case 'tt': return d.getHours() < 12 ? 'AM' : 'PM';
      default: return t;
    }
  });
}

const UNIDADES = [[1e12, 'T'], [1e9, 'bn'], [1e6, 'M'], [1e3, 'K']];
function pbiFormatCore(valor, fmt, opcoes) {
  const o = opcoes || {};
  const cult = CULTURAS[o.cultureSelector || op.cultura] || CULTURAS['en-US'];
  if (valor === null || valor === undefined) return '';
  let formato = o.format ?? fmt;
  if (formato && NOMES_FORMATO[String(formato).toLowerCase()] !== undefined) formato = NOMES_FORMATO[String(formato).toLowerCase()];
  if (valor instanceof Date) return formatarData(valor, formato || 'dd/MM/yyyy HH:mm:ss', cult);
  if (typeof valor !== 'number') return String(valor);
  let v = valor, sufixo = '';
  if (typeof o.value === 'number' && o.value !== 0) {
    const ref = Math.abs(o.value);
    const u = UNIDADES.find(([lim]) => ref >= lim);
    if (u) { v = v / u[0]; sufixo = u[1]; }
    if (o.precision === undefined && !formato) formato = '#,0.##';
  }
  if (typeof o.precision === 'number') formato = '#,0' + (o.precision > 0 ? '.' + '0'.repeat(o.precision) : '');
  if (!formato) {
    const t = Number.isInteger(v) ? String(v) : String(Number(v.toPrecision(15)));
    return t.replace('.', cult.decimal) + sufixo;
  }
  const s = secoes(String(formato));
  let sec = s[0], abs = false;
  if (v < 0 && s.length > 1 && s[1] !== '') { sec = s[1]; abs = true; }
  if (v === 0 && s.length > 2 && s[2] !== '') sec = s[2];
  const corpo = formatarNumeroSecao(v, sec, cult);
  const negativo = v < 0 && !abs && /[1-9]/.test(corpo);
  return (negativo ? '-' : '') + corpo + sufixo;
}

// ---------------------------------------------------------------- registro das funcoes do Deneb
vega.expressionFunction('pbiColor', (valor, shadePercent = 0) => {
  chamadas.pbiColor.add(String(valor));
  const nomeada = NOMEADAS()[`${valor}`];
  const base = nomeada || tema.cores[parseInt(`${valor}`) || 0] || '#000000';
  return shadeColor(base, shadePercent);
});
vega.expressionFunction('pbiFormat', (datum, params, options = {}) => {
  const ehObj = params !== null && typeof params === 'object';
  chamadas.pbiFormat.add(ehObj ? JSON.stringify(params) : String(params));
  return ehObj ? pbiFormatCore(datum, null, params) : pbiFormatCore(datum, params === null ? null : `${params}`, options);
});
vega.expressionFunction('pbiFormatAutoUnit', (datum, params, options = {}) => {
  const ehObj = params !== null && typeof params === 'object';
  chamadas.pbiFormatAutoUnit.add(ehObj ? JSON.stringify(params) : String(params));
  return ehObj ? pbiFormatCore(datum, null, { ...params, value: datum }) : pbiFormatCore(datum, params, { ...options, value: datum });
});
vega.expressionFunction('pbiPatternSVG', (id, fgColor, bgColor) => { chamadas.pbiPatternSVG++; return fgColor; });
vega.expressionFunction('pbiCrossFilterApply', () => { chamadas.pbiCrossFilterApply++; return {}; });
vega.expressionFunction('pbiCrossFilterClear', () => { chamadas.pbiCrossFilterClear++; });
vega.scheme('pbiColorNominal', tema.cores);
vega.scheme('pbiColorOrdinal', interpolateRgbBasis([tema.minimum, tema.maximum]));
vega.scheme('pbiColorLinear', interpolateRgbBasis([tema.minimum, tema.maximum]));
vega.scheme('pbiColorDivergent', interpolateRgbBasis([tema.minimum, tema.center, tema.maximum]));

// ---------------------------------------------------------------- dataset
const codificar = (nome) => String(nome).replace(/([\\".[\]])/g, '_');
function nomePadrao(c) {
  const m = /^(?:'(?:[^']|'')*'|[^[\]]*)\[(.*)\]$/.exec(c);
  return m ? m[1] : c;
}
function lerDados(arq) {
  if (!arq) return { colunas: [], tipos: [], linhas: [] };
  const texto = fs.readFileSync(arq, 'utf8').replace(/^\uFEFF/, '');
  if (arq.toLowerCase().endsWith('.json')) {
    const doc = JSON.parse(texto);
    if (Array.isArray(doc)) return { colunas: doc.length ? Object.keys(doc[0]) : [], tipos: [], linhas: doc };
    if (doc.resultados) {
      const c = doc.resultados[0] || { colunas: [], tipos: [], linhas: [] };
      return { colunas: c.colunas, tipos: c.tipos || [], linhas: c.linhas.map(l => Object.fromEntries(c.colunas.map((k, i) => [k, l[i]]))) };
    }
    return { colunas: doc.colunas || (doc.linhas?.length ? Object.keys(doc.linhas[0]) : []), tipos: doc.tipos || [], linhas: doc.linhas || [] };
  }
  const des = s => s.replace(/\\(.)/g, (m, x) => ({ '\\': '\\', t: '\t', r: '\r', n: '\n' }[x] ?? m));
  const todas = texto.split('\n');
  const fimRes = todas.findIndex(l => l.startsWith('#resultado'));
  const ls = (fimRes < 0 ? todas : todas.slice(0, fimRes)).map(l => l.replace(/\r$/, '')).filter(l => l.length);  // so o 1o resultado
  if (!ls.length) falhar('TSV vazio: ' + arq);
  const cols = ls[0].split('\t').map(des);
  const linhas = ls.slice(1).map(l => {
    const cel = l.split('\t');
    return Object.fromEntries(cols.map((c, i) => {
      let v = cel[i] === undefined ? '' : des(cel[i]);
      if (v === '') v = null;
      else if (/^-?\d+(\.\d+)?([eE][+-]?\d+)?$/.test(v)) v = Number(v);
      else if (v === 'true' || v === 'false') v = v === 'true';
      return [c, v];
    }));
  });
  return { colunas: cols, tipos: [], linhas };
}
const ISO = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?$/;
const bruto = lerDados(op.dados);
const renomear = {};
for (const par of (op.campos || '').split(',').map(s => s.trim()).filter(Boolean)) {
  const k = par.indexOf('=');
  if (k < 1) falhar('--campos no formato Alias=Coluna,Alias2=Coluna2');
  renomear[par.slice(k + 1).trim()] = par.slice(0, k).trim();
}
const ehData = {};
bruto.colunas.forEach((c, i) => { if (bruto.tipos[i] === 'DateTime') ehData[c] = true; });
const nomes = {};
for (const c of bruto.colunas) {
  const alias = renomear[c] ?? renomear[nomePadrao(c)] ?? nomePadrao(c);
  const cod = codificar(alias);
  if (cod !== alias) avisos.push(`campo "${alias}" codificado como "${cod}" (o Deneb troca \\ " . [ ] por _)`);
  nomes[c] = cod;
}
const formatos = {};
for (const f of op.formato) {
  const k = f.indexOf('=');
  if (k < 1) falhar('--formato no formato Campo=formato');
  formatos[f.slice(0, k).trim()] = f.slice(k + 1);
}
function estadoSelecionado(linha, i) {
  const s = op.selected;
  if (['neutral', 'on', 'off'].includes(s)) return s;
  if (s.startsWith('linhas=')) return s.slice(7).split(',').map(Number).includes(i) ? 'on' : 'off';
  const k = s.indexOf('=');
  if (k > 0) return String(linha[s.slice(0, k)]) === s.slice(k + 1) ? 'on' : 'off';
  falhar('--selected: neutral|on|off|ausente|Campo=valor|linhas=0,2');
}
const linhasDataset = bruto.linhas.map((l, i) => {
  const r = { __row__: i };
  const campos = {};
  for (const c of bruto.colunas) {
    let v = l[c];
    if (typeof v === 'string' && (ehData[c] || (!bruto.tipos.length && ISO.test(v)))) v = new Date(v);
    campos[nomes[c]] = v;
  }
  if (op.selected !== 'ausente') r.__selected__ = estadoSelecionado(campos, i);
  Object.assign(r, campos);
  for (const [campo, fmt] of Object.entries(formatos)) {
    r[campo + '__format'] = fmt;
    r[campo + '__formatted'] = pbiFormatCore(campos[campo], fmt, {});
  }
  return r;
});

// ---------------------------------------------------------------- spec + patch do Deneb
let textoSpec = fs.readFileSync(op.spec, 'utf8').replace(/^\uFEFF/, '');
const migracoes = [];
if (op.deneb === '2') {
  for (const [de, para] of [['pbiContainerWidth', 'denebContainer.width'], ['pbiContainerHeight', 'denebContainer.height'], ['pbiContainer', 'denebContainer']]) {
    const re = new RegExp(`\\b${de}\\b`, 'g');
    const n = (textoSpec.match(re) || []).length;
    if (n) { textoSpec = textoSpec.replace(re, para); migracoes.push(`${de} -> ${para} (${n}x)`); }
  }
}
let spec;
try { spec = JSON.parse(textoSpec); } catch (e) { falhar('spec nao e JSON valido: ' + e.message); }
if (String(spec.$schema || '').includes('vega-lite')) falhar('spec Vega-Lite: este harness renderiza Vega (L026: Deneb em Vega puro)');
spec.signals = Array.isArray(spec.signals) ? spec.signals : [];
const temSinal = n => spec.signals.some(s => s.name === n);
const recipiente = { width: W, height: H, scrollHeight: H, scrollWidth: W, scrollTop: 0, scrollLeft: 0 };
if (op.deneb === '2') {
  if (!temSinal('denebContainer')) spec.signals.push({ name: 'denebContainer', value: recipiente });
  if (spec.width == null && !temSinal('width')) spec.width = { signal: 'denebContainer.width' };
  if (spec.height == null && !temSinal('height')) spec.height = { signal: 'denebContainer.height' };
} else {
  spec.signals.push({ name: 'pbiContainerHeight', value: H }, { name: 'pbiContainerWidth', value: W }, { name: 'pbiContainer', value: recipiente });
  if (spec.width == null) spec.width = { signal: 'pbiContainerWidth' };
  if (spec.height == null) spec.height = { signal: 'pbiContainerHeight' };
}
spec.data = Array.isArray(spec.data) ? spec.data : [];
const iDs = spec.data.findIndex(d => d.name === 'dataset');
if (iDs >= 0) spec.data[iDs] = { ...spec.data[iDs], values: linhasDataset };
else spec.data.push({ name: 'dataset', values: linhasDataset });

let configUsuario = {};
if (op.config) configUsuario = JSON.parse(fs.readFileSync(op.config, 'utf8').replace(/^\uFEFF/, ''));
const config = { background: 'transparent', customFormatTypes: true, ...configUsuario };
if (config.width === 'container') delete config.width;
if (config.height === 'container') delete config.height;
if (config.autosize && config.autosize.resize === true) config.autosize = { ...config.autosize, resize: false };

const temTimer = /timer\s*\{|"type"\s*:\s*"timer"|"events"\s*:\s*"timer"/.test(textoSpec);
const temReduce = temSinal('reduceMotion');

// ---------------------------------------------------------------- vista
const loaderBloqueado = vega.loader();
loaderBloqueado.sanitize = async (uri) => { throw new Error('recurso externo bloqueado (so o dataset interno vale): ' + uri); };
loaderBloqueado.load = async (uri) => { throw new Error('recurso externo bloqueado: ' + uri); };
const logs = [];
function registrador(ignorar) {
  const base = vega.logger(vega.Warn);
  const guarda = (nivel) => (...a) => {
    const msg = a.map(String).join(' ');
    if (!(ignorar && ignorar.test(msg))) logs.push(`${nivel}: ${msg}`);
    return base;
  };
  return { level: (l) => (l === undefined ? vega.Warn : base), error: guarda('erro'), warn: guarda('aviso'), info: () => base, debug: () => base };
}
async function criarVista(configExtra, sinaisExtra, ignorarLog) {
  // o Vega marca cada objeto de dados ao ingerir: cada vista recebe a sua copia (o Deneb faz structuredClone)
  const specVista = { ...spec, data: spec.data.map(d => (d.name === 'dataset' ? { ...d, values: structuredClone(linhasDataset) } : d)) };
  let runtime;
  try { runtime = vega.parse(specVista, { ...config, ...configExtra }); } catch (e) { falhar('parse do Vega: ' + e.message, 2); }
  const vista = new vega.View(runtime, { renderer: 'none', loader: loaderBloqueado, logger: registrador(ignorarLog) });
  for (const [n, v] of Object.entries(sinaisExtra)) {
    try { vista.signal(n, v); } catch (e) { avisos.push(`sinal ${n} nao existe na spec (${e.message})`); }
  }
  if (op.fundo !== 'transparente') vista.background(op.fundo);
  await vista.runAsync();
  return vista;
}
const sinaisUsuario = {};
for (const s of op.sinal) {
  const k = s.indexOf('=');
  if (k < 1) falhar('--sinal nome=valorJSON');
  const bruto2 = s.slice(k + 1);
  try { sinaisUsuario[s.slice(0, k)] = JSON.parse(bruto2); } catch { sinaisUsuario[s.slice(0, k)] = bruto2; }
}
function estadoSinais(v) {
  // so valores serializaveis: sinais com evento/objeto circular ficam de fora da comparacao
  const s = v.getState({ signals: vega.truthy, data: vega.falsy, recurse: true }).signals || {};
  const out = {};
  for (const [k, val] of Object.entries(s)) {
    try { out[k] = JSON.parse(JSON.stringify(val)); } catch { /* ignora */ }
  }
  return JSON.stringify(out);
}
const saida = path.resolve(op.saida.replace(/\.(png|svg)$/i, ''));
fs.mkdirSync(path.dirname(saida), { recursive: true });

// ---------------------------------------------------------------- caixas da cena (--caixas: prova de espaçamento)
// Texto: TINTA medida no canvas (actualBoundingBox*) com a mesma fonte, na linha de base que o Vega usa (offset de
// vega-scenegraph: top 0,79·h, middle 0,30·h, bottom −0,21·h, alfabética 0) e com o alinhamento horizontal. Outras marcas:
// item.bounds do Vega (inclui traço). Fica de fora o invisível (opacidade 0, sem preenchimento nem traço visível), que é
// o caso dos alvos de hover e das marcas de medir da geometria reativa. Coordenadas = px do visual (origem + grupos).
function caixasDaCena(vista) {
  const cv = canvasMod.createCanvas(10, 10).getContext('2d');
  const [ox, oy] = vista.origin ? vista.origin() : [0, 0];
  const out = [];
  const visivelCor = (c) => c != null && c !== 'transparent' && c !== 'none' && !/rgba\([^)]*,\s*0(\.0*)?\s*\)$/.test(String(c));
  const base = (it, h) => {
    const b = it.baseline, lh = it.lineHeight != null ? it.lineHeight : h;
    return b === 'top' ? 0.79 * h : b === 'middle' ? 0.30 * h : b === 'bottom' ? -0.21 * h
      : b === 'line-top' ? 0.29 * h + 0.5 * lh : b === 'line-bottom' ? 0.29 * h - 0.5 * lh : 0;
  };
  function visitar(cena, dx, dy, opac, caminho) {
    if (!cena || !cena.items) return;
    for (const it of cena.items) {
      const op = opac * (it.opacity == null ? 1 : it.opacity);
      if (cena.marktype === 'group') {
        const gx = dx + (it.x || 0), gy = dy + (it.y || 0);
        const temFundo = (visivelCor(it.fill) && (it.fillOpacity == null || it.fillOpacity > 0))
          || (visivelCor(it.stroke) && (it.strokeOpacity == null || it.strokeOpacity > 0));
        if (temFundo && op > 0.02 && it.width && it.height) {
          out.push({ tipo: 'grupo', marca: cena.name || '', papel: cena.role || '', x1: gx, y1: gy, x2: gx + it.width, y2: gy + it.height });
        }
        for (const filho of it.items || []) visitar(filho, gx, gy, op, caminho + '/' + (cena.name || cena.role || 'g'));
        continue;
      }
      if (op <= 0.02) continue;
      const fillOk = visivelCor(it.fill) && (it.fillOpacity == null || it.fillOpacity > 0.02);
      const strokeOk = visivelCor(it.stroke) && (it.strokeOpacity == null || it.strokeOpacity > 0.02) && (it.strokeWidth == null || it.strokeWidth > 0);
      if (cena.marktype === 'text') {
        if (!fillOk || it.text == null || String(it.text).trim() === '') continue;
        const linhas = Array.isArray(it.text) ? it.text.map(String) : [String(it.text)];
        const h = it.fontSize == null ? 11 : it.fontSize;
        cv.font = `${it.fontStyle || 'normal'} ${it.fontWeight || 'normal'} ${h}px ${it.font || 'sans-serif'}`;
        cv.textAlign = 'left';
        cv.textBaseline = 'alphabetic';
        if (it.angle) {
          const b = it.bounds;
          out.push({ tipo: 'texto', marca: cena.name || '', papel: cena.role || '', texto: linhas.join(' ').slice(0, 60), girado: true,
            x1: dx + b.x1, y1: dy + b.y1, x2: dx + b.x2, y2: dy + b.y2 });
          continue;
        }
        const lh = it.lineHeight != null ? it.lineHeight : h;
        linhas.forEach((ln, i) => {
          const m = cv.measureText(ln);
          const largura = m.width;
          const x = dx + (it.x || 0) + (it.dx || 0);
          const ini = it.align === 'center' ? x - largura / 2 : it.align === 'right' ? x - largura : x;
          const yb = dy + (it.y || 0) + (it.dy || 0) + base(it, h) + i * lh - (linhas.length - 1) * (it.baseline === 'bottom' || it.baseline === 'line-bottom' ? lh : it.baseline === 'middle' ? lh / 2 : 0);
          out.push({ tipo: 'texto', marca: cena.name || '', papel: cena.role || '', texto: ln.slice(0, 60),
            fonte: `${it.fontWeight || 'normal'} ${h}px`, x1: ini - m.actualBoundingBoxLeft, x2: ini + m.actualBoundingBoxRight,
            y1: yb - m.actualBoundingBoxAscent, y2: yb + m.actualBoundingBoxDescent, base: yb });
        });
        continue;
      }
      if (!fillOk && !strokeOk) continue;
      const b = it.bounds;
      if (!b || !isFinite(b.x1) || b.x2 - b.x1 <= 0 && b.y2 - b.y1 <= 0) continue;
      // opaco: preenchimento cheio, sem transparência: esconde o que foi desenhado antes dele (grade atrás do rótulo)
      const opaco = fillOk && (it.fillOpacity == null || it.fillOpacity >= 0.98) && op >= 0.98;
      out.push({ tipo: cena.marktype, marca: cena.name || '', papel: cena.role || '', x1: dx + b.x1, y1: dy + b.y1, x2: dx + b.x2, y2: dy + b.y2, opaco });
    }
  }
  visitar(vista.scenegraph().root, ox, oy, 1, '');
  out.forEach((c, i) => { c.z = i; });   // ordem de desenho do scenegraph
  const r1 = (v) => Math.round(v * 10) / 10;
  return out.map((c) => ({ ...c, x1: r1(c.x1), y1: r1(c.y1), x2: r1(c.x2), y2: r1(c.y2), ...(c.base != null ? { base: r1(c.base) } : {}) }));
}

async function gravarPng(vista, arq) {
  const cv = await vista.toCanvas(ESCALA);
  fs.writeFileSync(arq, cv.toBuffer('image/png'));
  return { w: cv.width, h: cv.height };
}

const t0 = Date.now();
const relatorio = { spec: op.spec, dados: op.dados || null, caixa: { w: W, h: H }, escala: ESCALA, deneb: op.deneb, runtime_vega: vega.version, linhas: linhasDataset.length, tema: tema.fonte, cultura: op.cultura, migracoes, avisos, logs };

// quadro inicial: timers bloqueados por config.events.timer=false (API publica do Vega)
if (op['quadro-inicial']) {
  const vi = await criarVista({ events: { ...(config.events || {}), timer: false } }, { ...(temReduce ? { reduceMotion: false } : {}), ...sinaisUsuario }, /Blocked timer/);
  relatorio.inicial = { png: saida + '.inicial.png', ...(await gravarPng(vi, saida + '.inicial.png')) };
  vi.finalize();
}

// estado final: reduceMotion=true quando a spec segue o contrato da skill; com timer, os timers correm
// --esperar ms de relogio real antes da checagem de repouso (animacao finita <= 800 ms pelo brief)
const vf = await criarVista({}, { ...(temReduce ? { reduceMotion: true } : {}), ...sinaisUsuario });
if (temTimer) {
  await new Promise(r => setTimeout(r, Number(op.esperar) || 1500));
  await vf.runAsync();
  if (!temReduce) avisos.push(`spec com timer e sem sinal reduceMotion: o estado final depende de ${op.esperar} ms de relogio real`);
}
const antes = estadoSinais(vf);
await new Promise(r => setTimeout(r, 250));
await vf.runAsync();
const depois = estadoSinais(vf);
if (antes !== depois) {
  const a = JSON.parse(antes), b = JSON.parse(depois);
  const mudaram = Object.keys(b).filter(k => JSON.stringify(a[k]) !== JSON.stringify(b[k]));
  avisos.push('sinais ainda mudando no estado final (animacao sem fim?): ' + mudaram.slice(0, 10).join(', '));
}
const tam = await gravarPng(vf, saida + '.png');
relatorio.final = { png: saida + '.png', ...tam };
if (tam.w !== W * ESCALA || tam.h !== H * ESCALA) {
  avisos.push(`o render tem ${tam.w / ESCALA}x${tam.h / ESCALA} e a caixa ${W}x${H}: confira autosize ("fit", contains "padding") e padding`);
}
if (op.svg) { fs.writeFileSync(saida + '.svg', await vf.toSVG()); relatorio.svg = saida + '.svg'; }
if (op.caixas) { relatorio.caixas = saida + '.caixas.json'; fs.writeFileSync(relatorio.caixas, JSON.stringify(caixasDaCena(vf), null, 0)); }
const sinaisFinais = JSON.parse(depois);
relatorio.sinais = Object.fromEntries(Object.entries(sinaisFinais).filter(([, v]) => v === null || ['number', 'string', 'boolean'].includes(typeof v)));
relatorio.funcoes_deneb = {
  pbiColor: [...chamadas.pbiColor], pbiFormat: [...chamadas.pbiFormat], pbiFormatAutoUnit: [...chamadas.pbiFormatAutoUnit],
  pbiPatternSVG: chamadas.pbiPatternSVG, pbiCrossFilterApply: chamadas.pbiCrossFilterApply, pbiCrossFilterClear: chamadas.pbiCrossFilterClear,
};
if (chamadas.pbiFormatAutoUnit.size || [...chamadas.pbiFormat].some(s => s.includes('"value"'))) avisos.push('pbiFormat com unidade de exibicao: rotulo (K/M/bn/T) e aproximacao; confira no Desktop');
if (chamadas.pbiPatternSVG) avisos.push('pbiPatternSVG simulado como cor solida (fgColor)');
relatorio.ms = Date.now() - t0;
fs.writeFileSync(saida + '.relatorio.json', JSON.stringify(relatorio, null, 1));
vf.finalize();

console.log(`render ok: ${path.basename(saida)}.png ${tam.w}x${tam.h} (caixa ${W}x${H} x${ESCALA}) linhas=${linhasDataset.length} vega=${vega.version} deneb=${op.deneb}`);
if (relatorio.inicial) console.log(`quadro inicial: ${path.basename(saida)}.inicial.png`);
for (const m of migracoes) console.log('migracao: ' + m);
for (const a of avisos) console.log('aviso: ' + a);
for (const l of logs.slice(0, 20)) console.log('vega ' + l);
const f = relatorio.funcoes_deneb;
console.log(`funcoes Deneb chamadas: pbiColor=${f.pbiColor.length} pbiFormat=${f.pbiFormat.length} pbiFormatAutoUnit=${f.pbiFormatAutoUnit.length} crossFilter=${f.pbiCrossFilterApply}/${f.pbiCrossFilterClear}`);
console.log(`relatorio: ${saida}.relatorio.json`);
process.exit(0);

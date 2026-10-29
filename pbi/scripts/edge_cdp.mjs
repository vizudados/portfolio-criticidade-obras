// edge_cdp.mjs — abre uma página no Edge headless pelo protocolo de depuração (CDP), espera a medição da página encher
// <pre id="__medidas__">, opcionalmente captura a tela e devolve no stdout o texto de __medidas__.
//
// Base: producao/scripts/edge_cdp.mjs do painel de referência (28/09/2026; a origem não muda). Mesma razão de existir: o
// msedge.exe se relança ao iniciar e o stdout do --dump-dom se perde; pelo CDP a leitura é confiável. Diferenças: grava
// PNG (Page.captureScreenshot, com recorte opcional) e devolve só a medição, não o documento.
//
// Uso (chamado por scripts/medir_espacos.py): node edge_cdp.mjs '<json>'
//   json = {edge, url, perfil, janela_w, janela_h, escala, virtual_ms, reduzir, timeout_ms, png?, recorte?: {x,y,w,h}}
// Sem rede (proxy morto), perfil próprio. Em toda saída fecha o navegador pelo CDP (Browser.close).
import { spawn } from 'node:child_process';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const a = JSON.parse(process.argv[2]);
const flags = ['--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run', '--no-default-browser-check',
  '--disable-extensions', '--disable-sync', '--disable-default-apps', '--disable-background-networking',
  '--disable-component-update', '--mute-audio', '--proxy-server=http://127.0.0.1:9', '--proxy-bypass-list=<-loopback>',
  '--allow-file-access-from-files', `--user-data-dir=${a.perfil}`, `--force-device-scale-factor=${a.escala}`,
  `--window-size=${a.janela_w},${a.janela_h}`, '--remote-debugging-port=0'];
if (a.reduzir) { flags.push('--force-prefers-reduced-motion'); }
flags.push(a.url);
const proc = spawn(a.edge, flags, { stdio: 'ignore' });
const t0 = Date.now();
const limite = t0 + (a.timeout_ms || 120000);
const dorme = (ms) => new Promise((r) => setTimeout(r, ms));

let conexao = null;
async function sair(codigo, msg) {
  if (msg) { process.stderr.write(msg + '\n'); }
  if (conexao && conexao.readyState === 1) {
    try {
      conexao.send(JSON.stringify({ id: 999999, method: 'Browser.close', params: {} }));
      await dorme(800);
    } catch (e) { /* segue */ }
    try { conexao.close(); } catch (e) { /* segue */ }
  }
  try { proc.kill(); } catch (e) { /* já saiu */ }
  process.exit(codigo);
}

let porta = null;
while (!porta && Date.now() < limite) {
  const f = join(a.perfil, 'DevToolsActivePort');
  try {
    if (existsSync(f)) {
      const l = readFileSync(f, 'utf8').split('\n');
      if (l[0] && l[0].trim()) { porta = l[0].trim(); break; }
    }
  } catch (e) { /* EBUSY/EPERM: arquivo em uso */ }
  await dorme(50);
}
if (!porta) { await sair(2, 'edge_cdp: o Edge não abriu a porta de depuração'); }

let alvo = null;
while (!alvo && Date.now() < limite) {
  try {
    const lista = await (await fetch(`http://127.0.0.1:${porta}/json/list`)).json();
    alvo = lista.find((x) => x.type === 'page' && x.url && x.url.indexOf('about:') !== 0);
  } catch (e) { /* ainda subindo */ }
  if (!alvo) { await dorme(50); }
}
if (!alvo) { await sair(2, 'edge_cdp: a aba da página não apareceu'); }

try {
  const versao = await (await fetch(`http://127.0.0.1:${porta}/json/version`)).json();
  conexao = new WebSocket(versao.webSocketDebuggerUrl);
  await new Promise((r, j) => { conexao.addEventListener('open', r); conexao.addEventListener('error', j); });
} catch (e) { conexao = null; }
const ws = new WebSocket(alvo.webSocketDebuggerUrl);
await new Promise((r, j) => { ws.addEventListener('open', r); ws.addEventListener('error', j); });
let seq = 0;
const pend = new Map();
ws.addEventListener('message', (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); }
});
const cmd = (method, params = {}) => Promise.race([
  new Promise((r) => { seq += 1; pend.set(seq, r); ws.send(JSON.stringify({ id: seq, method, params })); }),
  dorme(30000).then(() => ({ error: { message: `sem resposta a ${method} em 30 s` } })),
]);
const avaliar = async (expr) => {
  const res = await cmd('Runtime.evaluate', { expression: expr, returnByValue: true });
  return res.result && res.result.result ? res.result.result.value : undefined;
};

// 1) o orçamento inteiro, com o documento carregado
const fim = t0 + (a.virtual_ms || 3000);
while (Date.now() < limite && (Date.now() < fim || (await avaliar('document.readyState')) !== 'complete')) {
  await dorme(100);
}
// 2) espera a medição encher
const vazia = "(function(){var p=document.getElementById('__medidas__');return !!p&&!(p.textContent||'').trim();})()";
while (Date.now() < limite && (await avaliar(vazia)) === true) { await dorme(100); }
// 3) captura (opcional)
if (a.png) {
  const p = { format: 'png', captureBeyondViewport: true };
  if (a.recorte) { p.clip = { x: a.recorte.x, y: a.recorte.y, width: a.recorte.w, height: a.recorte.h, scale: 1 }; }
  const r = await cmd('Page.captureScreenshot', p);
  if (r.result && r.result.data) { writeFileSync(a.png, Buffer.from(r.result.data, 'base64')); }
  else { process.stderr.write('edge_cdp: captura falhou ' + JSON.stringify(r.error || {}) + '\n'); }
}
const medidas = await avaliar("(document.getElementById('__medidas__')||{}).textContent||''");
await new Promise((ok) => process.stdout.write(String(medidas || ''), ok));
try { ws.close(); } catch (e) { /* segue */ }
await sair(0);

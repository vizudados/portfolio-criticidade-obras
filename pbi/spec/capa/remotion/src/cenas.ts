// Linha do tempo do filme da capa: a mesma da prévia aprovada (pbi/spec/capa/prototipo/montar_capa_v2.py, CENAS).
// Cinco takes de 5 s e a cena final de 8 s, laço de 33 s. Cada cena se desenha de baixo para cima em ~3 s (os tempos
// de cada traço estão no data-tempos do SVG) e fica parada até o fim da janela; na virada, papel em branco.
// x, y e escala são as do palco de 1920×640 (a faixa da capa); o vídeo é a mesma faixa ×4/3 (2560×854).

export type Cena = {
  readonly arquivo: string; // SVG de traço em pbi/spec/capa/animacao (pasta public deste projeto)
  readonly inicio: number; // s no laço
  readonly janela: number; // s
  readonly x: number; // px no palco de 1920×640
  readonly y: number;
  readonly escala: number;
};

export const CENAS: readonly Cena[] = [
  { arquivo: "take1-obras.svg", inicio: 0, janela: 5, x: 0, y: 0, escala: 1 },
  { arquivo: "take2-resultado.svg", inicio: 5, janela: 5, x: 0, y: 0, escala: 1 },
  { arquivo: "take3-fisico.svg", inicio: 10, janela: 5, x: 50, y: 13, escala: 0.97 },
  { arquivo: "take4-desembolso.svg", inicio: 15, janela: 5, x: 0, y: 0, escala: 1 },
  { arquivo: "take5-sem-estoque.svg", inicio: 20, janela: 5, x: 0, y: 0, escala: 1 },
  { arquivo: "final-natal.svg", inicio: 25, janela: 8, x: 0, y: 0, escala: 1 },
];

export const LACO_S = 33;
export const FPS = 60;
export const PALCO_W = 1920;
export const PALCO_H = 640;
export const K = 4 / 3; // 1920×640 → 2560×853,33 (a linha 854 fica branca, como no filme anterior)
export const VIDEO_W = 2560;
export const VIDEO_H = 854;

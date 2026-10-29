# Filme da capa · Remotion

O filme da faixa de cima da capa (1920×640 no painel, gravado em 2560×854): cinco takes de 5 s e a cena final de 8 s,
laço de 33 s, cada cena de Natal em traço de caneta se desenhando de baixo para cima. Só o desenho: os números, a
identidade, a régua e a base são HTML por cima, no HTML Content (`pbi/scripts/capa_medidas.py`), sincronizados pelo
JS da capa com o `<video>`.

- Cenas: os SVGs de traço de `../animacao/` (pasta `public` deste projeto, em `remotion.config.ts`), os mesmos do
  protótipo `../prototipo/montar_capa_v2.py`. A linha do tempo e as posições estão em `src/cenas.ts` (espelho de
  `CENAS` do protótipo); o estado de cada classe de traço em cada quadro, em `src/traco.ts`.
- Formato: 2560×854, 60 q/s, 1.980 quadros, H.264 yuv420p, faststart, mudo; pôster WebP = último quadro.

## Gravar

```console
npm ci
npx remotion render CapaFilme renders/quadros --sequence --image-format=png --gl=angle --image-sequence-pattern="quadro_[frame].[ext]"
python -I codificar_mp4.py --medir
```

O primeiro comando gera os 1.980 quadros sem perda com o Chrome na GPU (ANGLE). O segundo codifica pela placa de
vídeo (`h264_nvenc`, preset p7, CQ 30, quadros-chave só nas viradas de cena) e grava
`renders/capa-filme-2560x854-60fps.mp4` e `renders/capa-filme-poster.webp`. A aceleração de hardware do próprio
Remotion só existe no macOS; por isso a codificação é pelo ffmpeg. Depois, `pbi/scripts/capa_publicar.py --montar`
leva as mídias para a pasta de publicação.

Para ver no navegador: `npm run dev` (Remotion Studio).

Licença do Remotion: gratuita para equipes de até 3 pessoas (ver os termos do Remotion).

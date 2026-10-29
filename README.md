# Criticidade de Obras · mídias da capa

Ativos públicos da capa de um painel Power BI de acompanhamento de obras (visual HTML Content). O repositório guarda
**apenas as mídias da capa**: não há dado, texto, marca nem pessoas identificáveis nos arquivos. Os números do painel
são desenhados pelo próprio relatório, por cima do filme; nada aqui contém número de obra ou de empresa.

- `assets/capa-filme-2560x854-60fps-*.mp4`: filme em laço de 33 s, com cenas de obra em traço de caneta que se
  desenham de baixo para cima; 2560×854, 60 fps, H.264, mudo.
- `assets/capa-filme-poster-*.webp`: pôster do filme (a cena final desenhada).
- `assets/panoramica-base-*.svg`: ilustração vetorial de traço (horizonte de Natal com prédios em obra), usada em
  baixa opacidade na base da capa.
- `assets/manifest.json`: tamanho, SHA-256 e origem de cada arquivo.

Os cenários foram gerados por IA a partir de roteiro próprio, vetorizados em traço e animados localmente (Remotion).
O nome de cada arquivo leva os 12 primeiros dígitos do SHA-256 do conteúdo: um arquivo publicado nunca muda; uma
versão nova entra com outro nome. Servidos pelo GitHub Pages para que o `<video>` receba `Accept-Ranges` e respostas
`206`.

© Vizu Dados. Uso restrito ao painel a que pertencem.

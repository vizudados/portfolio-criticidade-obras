/**
 * Filme da capa do Criticidade de Obras. Vale para o CLI (npx remotion render / still / studio).
 * Todas as opções: https://remotion.dev/docs/config
 */

import { Config } from "@remotion/cli/config";

Config.setRspack(true);
// os SVGs de traço das cenas ficam em pbi/spec/capa/animacao (a mesma fonte do protótipo e da prévia): sem cópia
Config.setPublicDir("../animacao");
// quadros sem perda; o MP4 é codificado depois pela NVENC (codificar_mp4.py)
Config.setVideoImageFormat("png");
// Chrome com a GPU (ANGLE sobre Direct3D no Windows) para rasterizar os ~6 mil traços de cada quadro
Config.setChromiumOpenGlRenderer("angle");
Config.setOverwriteOutput(true);
Config.setDefaultPremountInSeconds(1);

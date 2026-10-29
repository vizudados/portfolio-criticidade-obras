import { AbsoluteFill, Sequence, useVideoConfig } from "remotion";
import { Cena } from "./Cena";
import { CENAS } from "./cenas";

// O filme da faixa de cima da capa: só o desenho, fundo branco e traço preto. Números, identidade, régua e base
// NÃO entram no vídeo: são HTML por cima, no HTML Content do Power BI, com os números vivos da DAX, sincronizados
// pelo JS da capa com o evento 'playing' do <video> (pbi/scripts/capa_medidas.py).
export const CapaFilme: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ backgroundColor: "#FFFFFF" }}>
      {CENAS.map((c) => (
        <Sequence
          key={c.arquivo}
          name={c.arquivo.replace(".svg", "")}
          from={Math.round(c.inicio * fps)}
          durationInFrames={Math.round(c.janela * fps)}
          premountFor={fps}
        >
          <Cena cena={c} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

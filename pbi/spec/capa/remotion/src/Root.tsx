import { Composition } from "remotion";
import { CapaFilme } from "./Composition";

// 2560×854, 60 q/s, 1.980 quadros (laço de 33 s): o formato do filme anterior da capa (LACO_S × FPS em cenas.ts).
export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="CapaFilme"
      component={CapaFilme}
      durationInFrames={1980}
      fps={60}
      width={2560}
      height={854}
    />
  );
};

import { useEffect, useState } from "react";
import { cancelRender, continueRender, delayRender, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { K, PALCO_H, PALCO_W, type Cena as CenaT } from "./cenas";
import { estadoClasse, lerTraco, type Traco } from "./traco";

// Uma cena de traço se desenhando de baixo para cima. O relógio é o da <Sequence> da cena (0 = papel em branco).
export const Cena: React.FC<{ readonly cena: CenaT }> = ({ cena }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const [handle] = useState(() => delayRender(`traço ${cena.arquivo}`));
  const [traco, setTraco] = useState<Traco | null>(null);

  useEffect(() => {
    fetch(staticFile(cena.arquivo))
      .then((r) => {
        if (!r.ok) throw new Error(`${cena.arquivo}: HTTP ${r.status}`);
        return r.text();
      })
      .then((svg) => {
        setTraco(lerTraco(svg));
        continueRender(handle);
      })
      .catch((e) => cancelRender(e));
  }, [cena.arquivo, handle]);

  if (!traco) return null;
  const t = frame / fps;
  // posição do protótipo: translate(x, y) scale(escala) com origem 0 0, no palco de 1920×640, tudo ×4/3
  return (
    <svg
      viewBox={traco.viewBox}
      preserveAspectRatio="xMidYMid meet"
      fill="none"
      stroke="#0B0B0C"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      style={{
        position: "absolute",
        left: cena.x * K,
        top: cena.y * K,
        width: PALCO_W * cena.escala * K,
        height: PALCO_H * cena.escala * K,
        overflow: "visible",
      }}
    >
      {traco.classes.map((c, k) => (
        <g key={k} style={estadoClasse(t, c)} dangerouslySetInnerHTML={{ __html: c.html }} />
      ))}
    </svg>
  );
};

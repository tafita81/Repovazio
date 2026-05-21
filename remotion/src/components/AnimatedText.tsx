import React from "react";
import { useCurrentFrame, spring, interpolate, useVideoConfig } from "remotion";

interface TextGroup {
  text: string;
  type: "GANCHO" | "IMPACTO" | "REVELACAO" | "CHORO" | "PAUSA" | "CTA" | "NORMAL";
  startFrame: number;
}

const TYPE_STYLES = {
  GANCHO:    { color: "#e2e8f0", size: "28px", weight: "400", tracking: "0.02em" },
  IMPACTO:   { color: "#ffffff", size: "42px", weight: "800", tracking: "-0.02em" },
  REVELACAO: { color: "#F59E0B", size: "34px", weight: "700", tracking: "0.01em" },
  CHORO:     { color: "#c4b5fd", size: "30px", weight: "400", tracking: "0.02em" },
  PAUSA:     { color: "#94a3b8", size: "26px", weight: "300", tracking: "0.05em" },
  CTA:       { color: "#F59E0B", size: "32px", weight: "700", tracking: "0.01em" },
  NORMAL:    { color: "#e2e8f0", size: "28px", weight: "400", tracking: "0.01em" },
};

const AnimatedWord: React.FC<{
  word: string;
  wordIndex: number;
  groupStart: number;
  type: TextGroup["type"];
  fps: number;
}> = ({ word, wordIndex, groupStart, type, fps }) => {
  const frame = useCurrentFrame();
  const wordStart = groupStart + wordIndex * 4; // 4 frames entre palavras
  
  const progress = spring({
    fps,
    frame: frame - wordStart,
    config: { damping: type === "IMPACTO" ? 8 : 12, stiffness: type === "IMPACTO" ? 250 : 180 },
  });
  
  const y = interpolate(progress, [0, 1], [30, 0]);
  const opacity = interpolate(progress, [0, 1], [0, 1]);
  // Escala extra para IMPACTO (bounce dramático)
  const scale = type === "IMPACTO"
    ? interpolate(progress, [0, 0.6, 1], [0.5, 1.15, 1])
    : interpolate(progress, [0, 1], [0.8, 1]);
  
  const s = TYPE_STYLES[type];
  
  return (
    <span style={{
      display: "inline-block",
      transform: `translateY(${y}px) scale(${scale})`,
      opacity,
      marginRight: "0.25em",
      color: type === "IMPACTO" && word.toUpperCase() === word && word.length > 2
        ? "#7C3AED" : s.color,
    }}>
      {word}
    </span>
  );
};

// Efeito câmera shake para IMPACTO
const useShake = (groupStart: number, duration: number = 20, type: string) => {
  const frame = useCurrentFrame();
  if (type !== "IMPACTO") return { x: 0, y: 0 };
  const t = frame - groupStart;
  if (t < 0 || t > duration) return { x: 0, y: 0 };
  const intensity = Math.max(0, 1 - t / duration) * 4;
  const x = Math.sin(t * 2.3) * intensity;
  const y = Math.cos(t * 1.7) * intensity;
  return { x, y };
};

export const AnimatedTextGroup: React.FC<{ group: TextGroup }> = ({ group }) => {
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();
  const s = TYPE_STYLES[group.type];
  const words = group.text.split(" ");
  const shake = useShake(group.startFrame, 20, group.type);
  
  const containerOpacity = frame >= group.startFrame ? 1 : 0;
  const lastWordEnd = group.startFrame + words.length * 4 + 15;
  const fadeOut = interpolate(frame, [lastWordEnd + 30, lastWordEnd + 60], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  
  return (
    <div style={{
      display: "flex",
      flexWrap: "wrap",
      justifyContent: "center",
      alignItems: "center",
      opacity: containerOpacity * fadeOut,
      transform: `translate(${shake.x}px, ${shake.y}px)`,
      fontSize: s.size,
      fontWeight: s.weight,
      letterSpacing: s.tracking,
      lineHeight: 1.3,
      fontFamily: group.type === "GANCHO" || group.type === "NORMAL"
        ? "'DM Sans', sans-serif"
        : "Georgia, serif",
      textAlign: "center",
      padding: "0 32px",
      maxWidth: "100%",
    }}>
      {words.map((word, i) => (
        <AnimatedWord
          key={i}
          word={word}
          wordIndex={i}
          groupStart={group.startFrame}
          type={group.type}
          fps={fps}
        />
      ))}
    </div>
  );
};

export default AnimatedTextGroup;

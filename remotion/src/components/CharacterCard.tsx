import React from "react";
import { useCurrentFrame, spring, interpolate, useVideoConfig, Img } from "remotion";

interface CharacterCardProps {
  imageUrl: string;
  character: "daniela" | "sara" | "marcos" | "ana" | "julia";
  startFrame?: number;
  emotion?: "neutral" | "sad" | "happy" | "concerned" | "authoritative";
}

const CHARACTER_COLORS = {
  daniela: "#7C3AED",
  sara:    "#8B5CF6",
  marcos:  "#E11D48",
  ana:     "#2563EB",
  julia:   "#F59E0B",
};

const CHARACTER_NAMES = {
  daniela: "Daniela Coelho",
  sara:    "Sara",
  marcos:  "Marcos",
  ana:     "Dra. Ana",
  julia:   "Julia",
};

// Flutuação suave do personagem
const useFloat = (amplitude = 8, period = 180) => {
  const frame = useCurrentFrame();
  return Math.sin((frame / period) * Math.PI * 2) * amplitude;
};

export const CharacterCard: React.FC<CharacterCardProps> = ({
  imageUrl,
  character,
  startFrame = 0,
  emotion = "neutral",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const color = CHARACTER_COLORS[character];
  const float = useFloat(6, 150);

  const enterProgress = spring({
    fps,
    frame: frame - startFrame,
    config: { damping: 14, stiffness: 120, mass: 1.2 },
  });

  const x = interpolate(enterProgress, [0, 1], [60, 0]);
  const opacity = interpolate(enterProgress, [0, 1], [0, 1]);
  const scale = interpolate(enterProgress, [0, 0.5, 1], [0.85, 1.05, 1.0]);

  // Halo pulsante ao redor do personagem
  const haloOpacity = interpolate(Math.sin(frame / 45), [-1, 1], [0.08, 0.22]);

  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      transform: `translateX(${x}px) scale(${scale}) translateY(${float}px)`,
      opacity,
    }}>
      {/* Container do personagem com halo */}
      <div style={{ position: "relative", width: 260, height: 260 }}>
        {/* Halo exterior pulsante */}
        <div style={{
          position: "absolute",
          top: -16, left: -16, right: -16, bottom: -16,
          borderRadius: "50%",
          border: `3px solid ${color}`,
          opacity: haloOpacity,
        }} />
        {/* Círculo de fundo */}
        <div style={{
          position: "absolute", inset: 0, borderRadius: "50%",
          background: `radial-gradient(circle, ${color}22 0%, transparent 70%)`,
        }} />
        {/* Imagem do personagem */}
        <div style={{
          width: 260, height: 260, borderRadius: "50%",
          overflow: "hidden",
          border: `4px solid ${color}`,
          boxShadow: `0 0 40px ${color}44, 0 20px 60px rgba(0,0,0,0.5)`,
          position: "relative", zIndex: 1,
          background: "#0d0d1a",
        }}>
          {imageUrl ? (
            <Img
              src={imageUrl}
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
          ) : (
            /* Fallback: avatar geométrico */
            <div style={{
              width: "100%", height: "100%",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: "80px",
              background: `linear-gradient(135deg, ${color}33, #06060F)`,
            }}>
              {character === "daniela" ? "ψ" :
               character === "sara" ? "👁" :
               character === "marcos" ? "⚡" :
               character === "ana" ? "🔬" : "✨"}
            </div>
          )}
        </div>
      </div>

      {/* Badge com nome — slide in com delay */}
      <div style={{
        marginTop: 12,
        background: `linear-gradient(135deg, ${color}CC, ${color}88)`,
        padding: "6px 20px",
        borderRadius: 24,
        backdropFilter: "blur(10px)",
        opacity: enterProgress,
        transform: `translateY(${interpolate(enterProgress, [0,1],[10,0])}px)`,
      }}>
        <span style={{
          color: "#ffffff", fontSize: "16px", fontWeight: 700,
          fontFamily: "'DM Sans', sans-serif", letterSpacing: "0.05em",
        }}>
          {CHARACTER_NAMES[character]}
        </span>
      </div>
    </div>
  );
};

export default CharacterCard;

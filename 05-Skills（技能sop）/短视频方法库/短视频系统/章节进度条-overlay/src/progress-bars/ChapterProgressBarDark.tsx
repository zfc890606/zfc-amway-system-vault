import { loadFont } from "@remotion/google-fonts/NotoSansSC";
import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import type { ScriptProgressData } from "../data/all-scripts";

const { fontFamily } = loadFont("normal", { weights: ["700"] });

const COLORS = {
  filled:   "#666666",
  unfilled: "#2A2A2A",
  divider:  "#444444",
  text:     "#FFFFFF",
  shadow:   "rgba(0, 0, 0, 0.4)",
};

const BAR_HEIGHT = 52;
const BAR_OPACITY = 0.9;

export const ChapterProgressBarDark: React.FC<ScriptProgressData> = ({
  totalDurationS,
  chapters,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTimeS = frame / fps;

  return (
    <AbsoluteFill style={{ background: "transparent" }}>
      {/* 底部阴影 */}
      <div style={{
        position: "absolute", top: BAR_HEIGHT, left: 0, right: 0, height: 8,
        background: `linear-gradient(to bottom, ${COLORS.shadow}, transparent)`,
      }} />

      {/* 进度条主体 */}
      <div style={{
        position: "absolute", top: 0, left: 0, right: 0,
        height: BAR_HEIGHT, display: "flex", opacity: BAR_OPACITY,
      }}>
        {chapters.map((chapter, i) => {
          const segDuration = chapter.endS - chapter.startS;
          const widthPct = (segDuration / totalDurationS) * 100;
          const isCompleted = currentTimeS >= chapter.endS;
          const isActive = currentTimeS >= chapter.startS && currentTimeS < chapter.endS;
          const fill = isCompleted ? 1 : isActive
            ? (currentTimeS - chapter.startS) / segDuration : 0;

          return (
            <div key={chapter.label} style={{
              width: `${widthPct}%`, height: "100%", position: "relative",
              backgroundColor: COLORS.unfilled,
              overflow: "hidden",
            }}>
              {/* 填充进度 */}
              <div style={{
                position: "absolute", top: 0, left: 0,
                width: `${fill * 100}%`, height: "100%",
                backgroundColor: COLORS.filled,
              }} />
              {/* 短分隔线 — 上下留空 */}
              {i < chapters.length - 1 && (
                <div style={{
                  position: "absolute", right: 0, top: "50%",
                  transform: "translateY(-50%)",
                  width: 2, height: 30,
                  backgroundColor: COLORS.divider,
                  borderRadius: 1,
                  zIndex: 3,
                }} />
              )}
              {/* 章节名：一行 */}
              <div style={{
                position: "absolute", inset: 0,
                display: "flex", flexDirection: "column",
                alignItems: "center", justifyContent: "center",
                gap: 1, overflow: "hidden", userSelect: "none",
              }}>
                <div style={{
                  fontFamily, fontSize: 16, fontWeight: "700",
                  color: COLORS.text, letterSpacing: "0.04em",
                  whiteSpace: "nowrap",
                }}>
                  {chapter.label}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

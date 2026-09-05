import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { loadFont } from "@remotion/google-fonts/NotoSansSC";
import type { ScriptProgressData } from "../data/all-scripts";

const { fontFamily } = loadFont("normal", { weights: ["700"] });

const COLORS = {
  playedText: "#666666",
  upcomingText: "#FFFFFF",
  divider: "#444444",
  progressLine: "#666666",
  barBg: "#2A2A2A",
};

const BAR_HEIGHT = 86;

export const TextHighlightProgressBarDark: React.FC<ScriptProgressData> = ({ totalDurationS, chapters }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTimeS = frame / fps;

  return (
    <AbsoluteFill style={{ background: "transparent", justifyContent: "flex-start" }}>
      {/* 黑底背景条 */}
      <div style={{
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        height: BAR_HEIGHT,
        backgroundColor: COLORS.barBg,
        opacity: 0.85,
      }} />

      {/* 进度线 — 一步一步往前推 */}
      <div style={{
        position: "absolute",
        bottom: 6,
        left: 40,
        right: 40,
        height: 3,
        display: "flex",
        gap: 2,
      }}>
        {chapters.map((chapter, i) => {
          const segPct = ((chapter.endS - chapter.startS) / totalDurationS) * 100;
          const isCompleted = currentTimeS >= chapter.endS;
          const isActive = currentTimeS >= chapter.startS && currentTimeS < chapter.endS;
          const fillPct = isCompleted ? 100 : isActive
            ? ((currentTimeS - chapter.startS) / (chapter.endS - chapter.startS)) * 100 : 0;

          return (
            <div key={i} style={{
              width: `${segPct}%`,
              height: "100%",
              backgroundColor: COLORS.divider,
              borderRadius: 2,
              position: "relative",
              overflow: "hidden",
            }}>
              <div style={{
                position: "absolute",
                left: 0,
                top: 0,
                height: "100%",
                width: `${fillPct}%`,
                backgroundColor: COLORS.progressLine,
                borderRadius: 2,
              }} />
            </div>
          );
        })}
      </div>

      {/* 文字内容 */}
      <div style={{
        width: "100%",
        height: BAR_HEIGHT,
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 40px 10px 40px",
        position: "relative",
        zIndex: 1,
      }}>
        {chapters.map((chapter, i) => {
          const isPlayed = currentTimeS >= chapter.startS;
          const textColor = isPlayed ? COLORS.playedText : COLORS.upcomingText;

          return (
            <React.Fragment key={chapter.label}>
              <div style={{
                flex: 1,
                display: "flex",
                justifyContent: "center",
              }}>
                <div style={{
                  fontFamily,
                  fontSize: 22,
                  fontWeight: "700",
                  letterSpacing: "0.04em",
                  color: textColor,
                  whiteSpace: "nowrap",
                }}>
                  {chapter.label}
                </div>
              </div>

              {/* 竖线分隔符 — 比之前大一点但上下留空 */}
              {i < chapters.length - 1 && (
                <div style={{
                  width: 2,
                  height: 22,
                  backgroundColor: currentTimeS >= chapters[i + 1].startS ? COLORS.playedText : COLORS.divider,
                  borderRadius: 1,
                  flexShrink: 0,
                  opacity: 0.4,
                }} />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

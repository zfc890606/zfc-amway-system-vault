import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import type { ScriptProgressData } from "../data/all-scripts";

const COLORS = {
  filled: "#666666",
  unfilled: "#2A2A2A",
};

const BAR_HEIGHT = 120;

export const MinimalProgressBarDark: React.FC<ScriptProgressData> = ({ totalDurationS, chapters }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTimeS = frame / fps;

  return (
    <AbsoluteFill style={{ background: "transparent", justifyContent: "flex-start" }}>
      <div style={{
        width: "100%",
        height: BAR_HEIGHT,
        position: "relative",
        display: "flex",
        alignItems: "center",
        marginTop: -40,
      }}>
        {/* 整体进度条容器 */}
        <div style={{
          width: "100%",
          height: 6,
          backgroundColor: COLORS.unfilled,
          position: "relative",
          display: "flex",
          alignItems: "center",
        }}>
          {/* 填充层 */}
          <div style={{
            position: "absolute",
            top: 0,
            left: 0,
            height: "100%",
            width: `${Math.max(0, Math.min(100, (currentTimeS / totalDurationS) * 100))}%`,
            backgroundColor: COLORS.filled,
            zIndex: 1,
          }} />

          {/* 节点 (圆点) */}
          {chapters.map((chapter, i) => {
            const positionPct = (chapter.startS / totalDurationS) * 100;
            const isCompleted = currentTimeS >= chapter.startS;

            return (
              <div key={i} style={{
                position: "absolute",
                left: `${positionPct}%`,
                transform: "translateX(-50%)",
                width: 16,
                height: 16,
                borderRadius: "50%",
                backgroundColor: isCompleted ? COLORS.filled : COLORS.unfilled,
                zIndex: 2,
              }} />
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

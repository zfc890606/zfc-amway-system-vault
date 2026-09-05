import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { loadFont } from "@remotion/google-fonts/NotoSansSC";
import type { ScriptProgressData } from "../data/all-scripts";

const { fontFamily } = loadFont("normal", { weights: ["700"] });

const COLORS = {
  activeText: "#C09070",
  inactiveText: "#EDE4D4",
  divider: "#CBBFA8",
};

const BAR_HEIGHT = 80;

export const TextHighlightProgressBar: React.FC<ScriptProgressData> = ({ totalDurationS, chapters }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTimeS = frame / fps;

  return (
    <AbsoluteFill style={{ background: "transparent", justifyContent: "flex-start" }}>
      <div style={{
        width: "100%",
        height: BAR_HEIGHT,
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between", // 均匀分布在全宽
        padding: "0 40px", // 两边留点边距
        paddingTop: 0,
        marginTop: -20, // 往上提，让文字更贴近顶部
      }}>
        {chapters.map((chapter, i) => {
          // 当前章节是否正在进行，或者已经完成
          const isPastOrActive = currentTimeS >= chapter.startS;
          
          // 只要是走过的地方（包括当前），就保持高亮颜色
          const textColor = isPastOrActive ? COLORS.activeText : COLORS.inactiveText;

          return (
            <React.Fragment key={chapter.label}>
              <div style={{
                flex: 1, // 让每个文字块占据相同的空间
                display: "flex",
                justifyContent: "center", // 文字在自己的块里居中
              }}>
                <div style={{
                  fontFamily,
                  fontSize: 24, // 缩小一点以适应 10 个章节
                  fontWeight: "700", // 统一使用 700 粗细
                  letterSpacing: "0.04em", // 和 ChapterProgressBar 保持一致
                  color: textColor,
                  transition: "color 0.3s ease",
                  whiteSpace: "nowrap",
                }}>
                  {chapter.label}
                </div>
              </div>
              
              {/* 分隔符 | */}
              {i < chapters.length - 1 && (
                <div style={{
                  fontFamily,
                  fontSize: 24,
                  fontWeight: "400",
                  color: currentTimeS >= chapters[i + 1].startS ? COLORS.activeText : COLORS.divider,
                  transition: "color 0.3s ease",
                }}>
                  |
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

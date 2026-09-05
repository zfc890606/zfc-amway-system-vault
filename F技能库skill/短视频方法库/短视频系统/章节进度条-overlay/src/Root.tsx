import "./index.css";
import { Composition, CalculateMetadataFunction } from "remotion";
import { ChapterProgressBar } from "./progress-bars/ChapterProgressBar";
import { ChapterProgressBarDark } from "./progress-bars/ChapterProgressBarDark";
import { ChapterProgressBarBottom } from "./progress-bars/ChapterProgressBarBottom";
import { ChapterProgressBarPortrait } from "./progress-bars/ChapterProgressBarPortrait";
import { CrabProgressBar } from "./progress-bars/CrabProgressBar";
import { TextHighlightProgressBar } from "./progress-bars/TextHighlightProgressBar";
import { DashProgressBar } from "./progress-bars/DashProgressBar";
import { MinimalProgressBar } from "./progress-bars/MinimalProgressBar";
import { MinimalProgressBarDark } from "./progress-bars/MinimalProgressBarDark";
import { TextHighlightProgressBarDark } from "./progress-bars/TextHighlightProgressBarDark";
import { KyomiProgressBar } from "./progress-bars/KyomiProgressBar";
import { allScripts } from "./data/all-scripts";
import type { ScriptProgressData } from "./data/all-scripts";

const alphaMeta: CalculateMetadataFunction<
  Record<string, unknown>
> = async () => ({
  defaultVideoImageFormat: "png",
  defaultPixelFormat: "yuva444p10le",
});

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* 所有安利脚本的进度条 - 下拉切换选择 */}
      {allScripts.map((script) => (
        <Composition
          key={script.id}
          id={script.id}
          component={ChapterProgressBarDark}
          durationInFrames={script.totalDurationS * 30}
          fps={30}
          width={1920}
          height={1080}
          calculateMetadata={alphaMeta}
          defaultProps={script satisfies ScriptProgressData}
        />
      ))}
      {/* 其他风格保留 */}
      {/* script-001 × 四种风格对比 */}
    </>
  );
};

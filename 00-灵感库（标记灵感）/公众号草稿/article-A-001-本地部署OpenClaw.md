# 本地部署 OpenClaw（小龙虾）完整教程：从下载到运行

下载了一个AI工具，打开教程发现第一行代码就报错，然后默默关掉。有过吗？

我上次就是这样。下载了OpenClaw，想着本地跑一跑看看效果。结果光配置环境就搞了两个小时。不是我不会装，是我电脑里Python是3.9，OpenClaw要3.10以上，死活跑不起来。

后来看报错才发现的。这篇文章帮你省掉我踩过的那些坑。

## 第一步：检查Python版本

终端输 `python3 --version`，如果是3.9或更低，去Python官网下个3.11。别下3.13，有些包还不兼容。

## 第二步：装依赖

就一句 `pip install openclaw`。但我劝你别直接pip，最好建个虚拟环境。我第一次直接pip，结果跟另一个项目冲突了，跑完OpenClaw，之前好好的一个工具废了。

cd到项目文件夹，敲这几行：

```
python3 -m venv venv
source venv/bin/activate
pip install openclaw
```

看着进度条跑完，最难那关就过去了。

然后输 `openclaw --version`，能看到版本号就是装好了。

## 第三步：开始用

想用图形界面就 `openclaw gui`，命令行就 `openclaw run`。填上API key就能开始用。

如果报什么"No module named"，别慌。大概率缺某个包，`pip install`那个名字就行。我第一次报了个pydantic的错——上网一搜，pip install pydantic就搞定了。

## 为什么值得做

装完之后你会发现，本地跑AI有一个好处网页版给不了——你随便折腾，不用担心额度超了，也不用怕对话记录被别人看。

本地部署不是技术活。你能一路走到命令行跑出结果，已经赢了大部分人了。

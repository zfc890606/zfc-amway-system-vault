# 飞书妙记自动同步到Obsidian：launchd+Python全自动

每次开会或听课，录音完了，你是不是还要手动导出来、手动整理、再手动存到Obsidian里面？

我以前就是。飞书妙记录了一堆，攒了好几个G，一个都没整理。不是不想整，是每次想到要打开飞书复制粘贴到笔记里，得先喝口水缓一缓。

后来我写了个Python脚本，搭了一套自动同步链，从此再也没手动复制过任何一条录音。

## 怎么做？其实不复杂

**第一步：飞书JSON转Markdown。** 飞书妙记有导出功能，但它是JSON格式的，不能直接用。我写了个脚本，把JSON转成Markdown——读出每段文字，加上时间戳，写成.md文件。几十行代码的事。

**第二步：让脚本自动跑。** Mac上有launchd，相当于Windows的计划任务。写个plist文件，告诉它每天几点跑一次，或者每次文件有变化就跑。我设的是每天凌晨两点。新建一个 `~/Library/LaunchAgents/com.feishu.sync.plist`，里面写：

```xml
<key>ProgramArguments</key>
<array>
  <string>/usr/local/bin/python3</string>
  <string>/Users/你的路径/sync_feishu.py</string>
</array>
<key>StartInterval</key>
<integer>3600</integer>
```

3600秒就是一小时检查一次。加载命令是 `launchctl load` 那个plist文件。

我第一次加载完，等了一个小时，发现没跑起来。后来查了半天，发现plist里路径写错了——把python3写成了python，mac没有python这个命令。改过来就好了。

**第三步：输出到Obsidian。** 脚本把生成的Markdown文件丢到Obsidian的vault目录里，设个固定的文件夹，比如"飞书录音/待整理"。第二天打开Obsidian，文件就在那儿了。

## 一次配置，终身受益

用了三个月，这个流程从来没出过问题。每天早上打开电脑，Obsidian里自动躺着昨晚的会议记录。不用动手。

你的大脑终于不用再记这些破事了。

# idea 激活

## 步骤

1. 下载下载并解压激活文件，`idea2020.2-激活/jetbrains-agent/lib/jetbrains-agent.jar`拖进idea界面
1. 拖拽完成选择restart,会出现一个弹窗
1. 将 `idea2020.2-激活/安装参数.txt` 中的内容复制到安装参数中
1. restart后成功，使用到期限2089年

注意：

更新在`idea iu 2020.1.2 => 2020.2.1`测试可用

[idea2020.2-激活](../assets/files/idea2020.2-激活.zip)

参考：[【全平台】IntelliJ IDEA 2020.2 激活至2089新方式](https://www.52pojie.cn/thread-1264151-1-1.html)

## 无限试用

### Reset evaluation period of IntelliJ IDEA(Linux)

参考：[Reset IntelliJ IDE evaluation period in linux](https://gist.github.com/dev-rijan/bb880cfd9279ce817faee42c69a45bab#file-gistfile1-md)

```bash
rm -rf ~/.config/JetBrains/IntelliJIdea*/eval
rm -rf ~/.config/JetBrains/PyCharm*/options/other.xml (if exists)
sed -i -E 's/<property name=\"evl.*\".*\/>//' ~/.config/JetBrains/IntelliJIdea*/options/other.xml
rm -rf ~/.java/.userPrefs/jetbrains/idea
```

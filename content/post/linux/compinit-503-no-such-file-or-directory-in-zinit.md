---
title: "Compinit 503 No Such File or Directory in Zinit"
date: 2021-10-20T14:59:00+08:00
draft: true
tags: [zsh, zinit]
---

在使用zinit安装插件时反复调试时可能出现`compinit:503: no such file or directory: ~/.zinit/completions/_xxx`问题，但是并不影响正常使用，只是在首次进入后提示两次

## 解决

运行`zinit cclear`

<!--more-->
参考：

* [Enhancd load error! #376](https://github.com/zdharma/zinit/issues/376#issuecomment-653731705)
* [Issue with removing z-a-man #333](https://github.com/zdharma/zinit/issues/333#issuecomment-626313212)

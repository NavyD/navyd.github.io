---
title: "Python Installed From Mstore Not Found in Terminal"
date: 2022-07-01T14:24:24+08:00
draft: false
---

在升级win 11后，正常使用之前的python，但是在一次修改了环境变量path后，之前正常使用python无法使用了，无论是正常安装还是商店的都无法使用

<!--more-->

## 分析

可能是由于更新的问题，在动了path后出现问题，更新path就好，windows 商店的问题可能也是未加入path的问题

## 解决方式

```powershell
$env:PATH += '%USERPROFILE%\AppData\Local\Microsoft\WindowsApps'
```

参考：

* [CMD opens Windows Store when I type 'python'](https://stackoverflow.com/a/58773979/8566831)

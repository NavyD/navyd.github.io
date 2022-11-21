---
title: "How to Extract a Single File From Tar to a Different Directory"
date: 2022-11-21T17:57:04+08:00
draft: true
---

在使用tar时如何解压其中某个文件到指定的目录

<!--more-->

## 分析

通常使用`-C`选项放在后面`-f`也没问题，但是当结合指定的解压文件时`-C`将失效并解压到当前目录，并不会出现提示

```bash
curl -L "https://github.com/xxx.tar.gz" | tar -xzf - --strip-components 1 --wildcards '*/rest-server' -C ./testdir
# 解压到当前目录
```

正确的方式应该将`-C`放在`-f`之前

## 方案

```bash
tar --strip-components 1 --wildcards -C ./testdir -xzf - '*/rest-server'
```

参考：

* [How to extract a single file from tar to a different directory? [closed]](https://stackoverflow.com/a/9249779/8566831)

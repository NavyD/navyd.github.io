---
title: "How to Monitor Proc Filesystem in Linux"
date: 2021-11-14T21:07:09+08:00
draft: true
---

在linux中的/proc文件系统中包括了各种系统信息，有没有一种方式在信息更新时得到通知？

实际上/proc不是文件系统，类似于api调用，不能像普通文件一样监听事件改变

参考：

* [How frequently is the proc file system updated on Linux?](https://unix.stackexchange.com/a/74724)
* [Notify of changes on a file under /proc](https://unix.stackexchange.com/a/90628)
* [How is having processes kept as files in `/proc` not a performance issue?](https://unix.stackexchange.com/a/647555)

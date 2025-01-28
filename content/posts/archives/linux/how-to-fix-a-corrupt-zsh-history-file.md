---
title: "How to Fix a Corrupt Zsh History File"
date: 2022-05-19T23:46:40+08:00
draft: true
---

在一次系统崩溃重启后提示：`zsh: corrupt history file /home/xxx/.zsh_history`。并且在多次登录zsh后也出现同样的问题

<!--more-->

```sh
mv .zsh_history .zsh_history_bad
strings .zsh_history_bad > .zsh_history
fc -R .zsh_history
```

参考：

* [How to fix a corrupt zsh history file](https://shapeshed.com/zsh-corrupt-history-file/)
* [How to fix and recover a "corrupt history file" in zsh?](https://superuser.com/a/957924)

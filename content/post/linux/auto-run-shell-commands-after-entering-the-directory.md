---
title: "进入目录后自动运行shell命令"
date: 2021-10-01T02:22:59+08:00
draft: false
tags: [zsh, hugo, bash]
---

在使用hugo时需要启动服务实时查看本地渲染情况，每次启动都要键入命令`hugo server -D`比较麻烦，有没有一种方式在hugo博客目录时自动运行命令

## 分析

在编写博客时通常要进入命令行（vscode terminal），只要在cd后自动运行就行了。zsh提供了一个hook函数`chpwd()`

```bash
function chpwd() {
    emulate -L zsh
    ls -a
}
```

另外[ohmyzsh/plugins/dotenv](https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/dotenv)提供了类似的方式自动加载.env文件，可以使用.env文件实现

```bash
# project/.env
# auto start hugo server in entering dir of this project
if command -v hugo >/dev/null && ! pidof hugo >/dev/null; then
    echo 'hugo serving'
    # in the shell session background
    hugo server -D >/dev/null &
fi
```

参考：

* [ZSH: automatically run ls after every cd](https://stackoverflow.com/a/3964198/8566831)
* [Execute bash scripts on entering a directory](https://unix.stackexchange.com/a/21364)

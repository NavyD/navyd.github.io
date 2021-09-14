---
title: "在sudo时如何保持当前环境变量"
date: 2021-09-13T20:53:59+08:00
draft: false
---

在使用sudo时经常出现环境问题，如命令无法找到

```bash
$ sudo poetry;sudo sh -c 'echo $VISUAL'
sudo: poetry: command not found

$ which poetry; echo $VISUAL
/home/navyd/.local/bin/poetry
vim
```
<!--more-->
## 分析

sudo存在一个`security policy`不会使用当前用户的环境，提供了`-E`启用当前存在的环境变量，`--preserve-env=[key,key1,..]`从当前用户环境中保存的环境变量，允许覆盖

上面的是在`~/.bashrc`中定义的变量`PATH, VISUAL`本质是没有被sudo设置，可以保存当前环境变量在 sudo 之后以 `ENV=VALUE` 的形式传递被后续命令接受。

而`env` run a program in a modified environment 是一个接受变量执行命令的命令如`env a=b sh -c 'echo $a'`

```bash
$ sudo --preserve-env=PATH env poetry --version
Poetry version 1.1.7
# or
$ sudo PATH=$PATH env poetry --version

$ sudo --preserve-env=PATH,VISUAL env sh -c 'echo $VISUAL'
vim
# or
$ sudo -E --preserve-env=PATH env sh -c 'echo $VISUAL'
vim
```

注意：不能使用`sudo PATH=$PATH cmd`这种方式，前导参数本身视为环境变量赋值使cmd使用PATH变量，但不会影响sudo的可执行文件的搜索路径，sudo无法找到在当前PATH中找到cmd

```bash
# 变量传递给了sh
$ sudo -E PATH=$PATH sh -c 'which poetry; echo $VISUAL'
/home/navyd/.local/bin/poetry
vim
# 变量给了poetry，但sudo是无法在root的PATH中找到poetry的
$ sudo -E PATH=$PATH poetry --version
sudo: poetry: command not found
```

## 解决

最小特权原则，在`~/.bashrc`中添加alias，命名最好不要与`sudo`一样，可能导致程序行为不一致出bug

```bash
alias sudoe='sudo -E --preserve-env=PATH env'
```

参考：

- [How to keep environment variables when using sudo](https://stackoverflow.com/a/8633575/8566831)
- [How to make `sudo` preserve $PATH?](https://unix.stackexchange.com/a/83194)

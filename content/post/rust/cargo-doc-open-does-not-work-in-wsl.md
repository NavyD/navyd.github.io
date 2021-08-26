---
title: "Cargo Doc Open Does Not Work in Wsl"
date: 2021-08-26T16:26:40+08:00
draft: false
---

## 问题

在wsl命令行中使用`cargo doc --open`无法在windows端打开

## 分析

在wsl命令行中是可以直接执行windows exe文件的，ubuntu中预置了[wslu](https://github.com/wslutilities/wslu)工具，其中的`wslview`可以满足要求

>A fake WSL browser that can help you open link in default Windows browser or open files on Windows.

在wsl命令行中使用wslview可以用windows的默认程序打开文件

```sh
# 使用默认文本处理程序打开
wslview test.txt
```

尝试更新wslview为默认浏览器

```sh
$ wslview --help
wslview - Part of wslu, a collection of utilities for Windows 10 Windows Subsystem for Linux
Usage: wslview (--register|--unregister|--help|--version) [LINK]

For more help for wslview, visit the following site: https://github.com/wslutilities/wslu/wiki/wslview
$ wslview --version
wslu v2.3.6; wslview v06
$ wslview --register
[sudo] password for navyd:

$ update-alternatives --list x-www-browser
/usr/bin/wslview

# empty
$ echo $BROWSER

$ file $(which x-www-browser)
/usr/bin/x-www-browser: symbolic link to /etc/alternatives/x-www-browser
$ file /etc/alternatives/x-www-browser
/etc/alternatives/x-www-browser: symbolic link to /usr/bin/wslview
$ file /usr/bin/wslview
/usr/bin/wslview: Bourne-Again shell script, ASCII text executable
$ head -n 2 /usr/bin/wslview
#!/bin/bash
# wslu - Windows 10 linux Subsystem Utility
```

可以看到wslview脚本确实成为了wsl中的浏览器，但是cargo依然无法打开，应该是cargo依赖的是环境变量而不是xserver环境。

**注意：当前版本`wslu v2.3.6; wslview v06`存在无法打开绝对路径bug：[wslview open file by absolute path failed #118](https://github.com/wslutilities/wslu/issues/118)**

```sh
$ wslview /home/panjie/temp/aaa.docx

Start : 由于出现以下错误，无法运行此命令: 系统找不到指定的文件。。
所在位置 行:1 字符: 1
+ Start "/home/panjie/temp/aaa.docx"
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : InvalidOperation: (:) [Start-Process]，InvalidOperationException
    + FullyQualifiedErrorId : InvalidOperationException,Microsoft.PowerShell.Commands.StartProcessCommand
```

## 解决方案

### file protocol

以ubuntu为例，创建文件`~/open_browser.sh`并添加执行权限，在`.bashrc`或`.zshrc`中添加下面代码，注意`file://///wsl$`不能改为`file:///wsl$`。

```sh
# ~/open_browser.sh
# chrome
browser='/mnt/c/Program Files/Google/Chrome/Application/chrome.exe'
# 如果不是ubuntu则需要修改对应目录 如果输入$1为相对路径则转为绝对路径
file_path="file://///wsl$//Ubuntu$([[ "$1" = /*  ]] && echo "$1" || echo "$(pwd)/$1")"
$browser "$file_path"

# 执行权限
chmod +x ~/open_browser.sh

# .zshrc
export BROWSER="$HOME/open_browser.sh"
```

cargo还允许配置[`doc.browser`](https://doc.rust-lang.org/stable/cargo/reference/config.html#docbrowser)覆盖环境变量BROWSER，如在`/.cargo/config.toml`或当前项目的config.toml中指定

```toml
# ...
[doc]
browser = "$HOME/open_browser.sh"
```

### wslu-wslview

从[wslview sh源码](https://github.com/wslutilities/wslu/blob/master/src/wslview.sh)上看还是使用了`file`协议，功能更强大，但是需要更新默认版本`wslu v2.3.6`

```sh
wslview --version
# wslu v2.3.6; wslview v06

# 更新wslu
sudo add-apt-repository ppa:wslutilities/wslu
sudo apt-get update && sudo apt-get upgrade

wslview --version
# wslu v3.2.2-1; wslview v10

# 在`~/.zshrc`中添加
export BROWSER="wslview"
```

### http server

python3自带一个http server，在workspace中运行

```sh
# --directory DIRECTORY port
python3 -m http.server --directory target/doc/$crate_name 8000
```

注意：

- `--directory`在python3.7可用
- `$crate_name`通常是当前目录名 `-` to `_`如：a-b -> `target/doc/a_b`

参考：

- [cargo doc --open doesn't work in WSL #7557](https://github.com/rust-lang/cargo/issues/7557#issuecomment-791320960)
- [cargo doc --open should start a web server to enable keyboard accessibility #4966](https://github.com/rust-lang/cargo/issues/4966#issuecomment-406584885)
- [The Cargo Book cargo-doc(1)](https://doc.rust-lang.org/stable/cargo/commands/cargo-doc.html#documentation-options)
- [http.server — HTTP servers](https://docs.python.org/3/library/http.server.html)
- [Check If Shell Script $1 Is Absolute Or Relative Path [duplicate]](https://stackoverflow.com/a/20204890/8566831)
- [file URI scheme How many slashes?](https://en.wikipedia.org/wiki/File_URI_scheme#How_many_slashes?)
- [How can I “open” a file from WSL with the default application?](https://superuser.com/a/1600972)
- [What's the difference between x-www-browser and gnome-www-browser?](https://askubuntu.com/a/232430)
- [wslu](https://github.com/wslutilities/wslu)

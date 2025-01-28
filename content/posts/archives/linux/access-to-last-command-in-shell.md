---
title: "在shell中访问上次运行的命令"
date: 2021-09-15T21:40:47+08:00
draft: false
tags: [linux, shell, zsh]
---

如何在shell中使用快捷键运行上次命令

## 快捷键运行sh脚本命令

在绑定key的时候需要找到对应键位的ascii码，对于特殊的键位可能很难找到，linux中提供了`showkey -a`可以查询ascii码。下面是键入`F10, ctrl+d`两个快捷键的输出：

```bash
$ showkey -a

Press any keys - Ctrl-D will terminate this program

^[[21~   27 0033 0x1b
         91 0133 0x5b
         50 0062 0x32
         49 0061 0x31
        126 0176 0x7e
^D        4 0004 0x04
```

zsh中内置了bindkey使用快捷键，在`man zshzle`中可以找到。

> bindkey [ options ] -s in-string out-string
> Bind each in-string to each out-string.  When in-string is typed, out-string will  be  pushed  back
> and treated as input to the line editor.  When -R is also used, interpret the in-strings as ranges.
>
> Note  that  both  in-string  and  out-string are subject to the same form of interpretation, as de‐
> scribed below.

下面是演示绑定命令与脚本文件：

```bash
# 绑定F10
$ bindkey -s '^[[21~' 'echo test\n'
# 键入F10 自动输入
$ echo test
test

# test.sh: echo test
$ bindkey -s '^[[21~' "$(pwd)/test.sh\n"
$ /home/navyd/Workspaces/projects/navyd.github.io/test.sh
test
```

参考：

- [Show keys pressed in Linux [closed]](https://superuser.com/a/248568)
- [Binding Keys in Zsh](https://jdhao.github.io/2019/06/13/zsh_bind_keys/)
- [How can I use bindkey to run a script?](https://unix.stackexchange.com/a/226062)

## 获取上次命令的参数

在shell使用时可能需要上次命令中的某些参数，避免重复输入如：

```bash
$ ls -al ~/.local
# 想要的效果：du -sh ~/.local
$ du -sh !$
# 输入!$后回车不会执行而是替换成
$ du -sh ~/.local
```

在shell中`!`用法可以直接在`man bash`中搜索`\!!`如下：

>Word Designators
>       Word designators are used to select desired words from the event.  A : separates the event specification from the
>       word designator.  It may be omitted if the word designator begins with a ^, $, *, -, or %.   Words  are  numbered
>       from  the beginning of the line, with the first word being denoted by 0 (zero).  Words are inserted into the cur‐
>       rent line separated by single spaces.
>
>       0 (zero)
>              The zeroth word.  For the shell, this is the command word.
>       n      The nth word.
>       ^      The first argument.  That is, word 1.
>       $      The last word.  This is usually the last argument, but will expand to the zeroth word if there is only one
>              word in the line.
>       %      The word matched by the most recent `?string?' search.
>       x-y    A range of words; `-y' abbreviates `0-y'.
>       *      All  of  the  words but the zeroth.  This is a synonym for `1-$'.  It is not an error to use * if there is
>              just one word in the event; the empty string is returned in that case.
>       x*     Abbreviates x-$.
>       x-     Abbreviates x-$ like x*, but omits the last word

具体的用法后面慢慢探索

<!-- TODO -->

参考：

- [Access to last command in Zsh (not previous command line)](https://stackoverflow.com/a/25305091/8566831)
- [bash Word Designators](https://www.gnu.org/software/bash/manual/html_node/Word-Designators.html#Word-Designators)
- [Is there a shortcut for repeat the second proximate command in bash?](https://unix.stackexchange.com/a/151110)
- [Re run previous command with different arguments](https://stackoverflow.com/a/38176552/8566831)

## 快捷键运行上次执行的命令

读取上次命令可以使用zsh内置`fc -ln -1`，结合上面的`bindkey -s`使用，发现无法工作

```bash
bindkey -s '^[[21~' 'fc -ln -1\n\n'

$ echo test
test
# 键入F10
$ fc -ln -1 #\n
echo test
$ #\n
$
```

在网上找到答案，可以参考[zsh zle Chapter 4: The Z-Shell Line Editor](https://zsh.sourceforge.io/Guide/zshguide04.html)

```bash
# define function that retrieves and runs last command
function run-again {
    # get previous history item
    zle up-history
    # confirm command
    zle accept-line
}
# define run-again widget from function of the same name
zle -N run-again
# bind widget to Ctrl+X in viins mode
# bindkey -M viins '^E' run-again
# bind widget to Ctrl+X in vicmd mode
bindkey '^[[21~' run-again
```

参考：

- [In zsh how do I bind a keyboard shortcut to run the last command?](https://stackoverflow.com/a/28938270/8566831)
- [Rerun previous command under sudo](https://askubuntu.com/a/530687)

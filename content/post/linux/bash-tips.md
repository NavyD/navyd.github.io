---
title: "Bash Tips"
date: 2022-09-05T11:27:47+08:00
draft: true
---

bash tips

<!--more-->

## heredoc: less-than sign

`<<,<<<`保存文字里面的换行或是缩进等空白字元。允许在字符串里执行变量替换和命令替换。

```bash
# shell变量替换
python3 <<EOF
distinct_paths = list(dict.fromkeys('$PATH'.split(':')))
print(':'.join(distinct_paths))
EOF
# stdout: /usr/local/sbin:/usr/local/bin:...

# 禁用shell变量替换
cat << 'EOF'
Working dir $PWD
EOF
# stdout: Working dir $PWD


# tab缩进格式手动\t替换为tab，空格将失败，在现代基本不用
python3 <<-EOF
\t  distinct_paths = list(dict.fromkeys('$PATH'.split(':')))
\t  print(':'.join(distinct_paths))
EOF
# stdout: /usr/local/sbin:/usr/local/bin:...
```

## subshell with pipe

在子shell中使用pipe的时候通常希望获取命令的exit code或设置环境变量如

```bash
# get command exit code in pipe
unset retcode
retcode=0
{ eval "sh -c 'echo test; exit 121'" 2>&1; retcode=$?; }
test "$retcode" -eq "121" # true

unset retcode
{ eval "sh -c 'echo test; exit 121'" 2>&1; retcode=$?; } | while IFS= read -r line; do echo "$line"; done
test "$retcode" -eq "121" # false


###### test fun######
retcode=0
run() { eval "sh -c 'echo test; exit 121'" 2>&1; retcode=$?; }
run | while IFS= read -r line; do echo "$line"; done
test "$retcode" -eq "121" # false
```

在正常的subshell中是可以正常修改变量的，但是，在子shell pipe中设置的变量在子shell 之外不可用，所以retcode为空。同样，bash函数中修改变量在pipe中也不会生效

要在pipe中获取命令的退出code可以参考[Get exit status of process that's piped to another](https://unix.stackexchange.com/a/73180)，有3种方式

```bash
# Pipefail
$ set -o pipefail
$ false | true; echo $?

# $PIPESTATUS
$ false | true; echo "${PIPESTATUS[@]}"

# Separate executions
$ OUTPUT="$(echo foo)"
$ STATUS_ECHO="$?"
```

## double square brackets VS single square brackets VS test

> [What is the difference between test, \[ and \[\[ ?](http://mywiki.wooledge.org/BashFAQ/031)

test实现了命令的旧的可移植语法。在几乎所有shell中（最古老的Bourne shell除外），`[`是test的同义词（但需要最后一个参数]）。尽管所有现代shell都有内置的`[`实现，但通常仍有一个该名称的外部可执行文件，例如`/bin/[`。POSIX为`[`定义了一个必需的功能集，但几乎每个shell都提供了对它的扩展。因此，如果您想要可移植代码，您应该小心不要使用任何这些扩展。

`[[`是它的一个新的改进版本，它是一个关键字，而不是一个程序。这使得它更易于使用，如下所示。

<!-- 使用简悦转换复制表格 或 直接debug复制element -->
<!-- markdownlint-disable MD033 -->
<table><tbody><tr><td><p><strong>Feature</strong></p></td><td><p><strong>new test</strong> <tt>[[</tt></p></td><td><p><strong>old test</strong> <tt>[</tt></p></td><td><p><strong>Example</strong></p></td></tr><tr><td colspan="1" rowspan="4"><p>string comparison</p></td><td><p><tt>&gt;</tt></p></td><td><p><tt>\&gt;</tt> <a href="http://mywiki.wooledge.org/BashFAQ/031#np">(*)</a></p></td><td><p><tt>[[a&gt;&nbsp;b&nbsp;]]&nbsp;||&nbsp;echo&nbsp;"a&nbsp;does&nbsp;not&nbsp;come&nbsp;after&nbsp;b"</tt></p></td></tr><tr><td><p><tt>&lt;</tt></p></td><td><p><tt>\&lt;</tt> <a href="http://mywiki.wooledge.org/BashFAQ/031#np">(*)</a></p></td><td><p><tt>[[az&nbsp;&lt;&nbsp;za]]&nbsp;&amp;&amp;&nbsp;echo&nbsp;"az&nbsp;comes&nbsp;before&nbsp;za"</tt></p></td></tr><tr><td><p><tt>=</tt> (or <tt>==</tt>)</p></td><td><p><tt>=</tt></p></td><td><p><tt>[[a&nbsp;=&nbsp;a]]&nbsp;&amp;&amp;&nbsp;echo&nbsp;"a&nbsp;equals&nbsp;a"</tt></p></td></tr><tr><td><p><tt>!=</tt></p></td><td><p><tt>!=</tt></p></td><td><p><tt>[[a&nbsp;!=&nbsp;b]]&nbsp;&amp;&amp;&nbsp;echo&nbsp;"a&nbsp;is&nbsp;not&nbsp;equal&nbsp;to&nbsp;b"</tt></p></td></tr><tr><td colspan="1" rowspan="6"><p>integer comparison</p></td><td><p><tt>-gt</tt></p></td><td><p><tt>-gt</tt></p></td><td><p><tt>[[5&nbsp;-gt&nbsp;10]]&nbsp;||&nbsp;echo&nbsp;"5&nbsp;is&nbsp;not&nbsp;bigger&nbsp;than&nbsp;10"</tt></p></td></tr><tr><td><p><tt>-lt</tt></p></td><td><p><tt>-lt</tt></p></td><td><p><tt>[[8&nbsp;-lt&nbsp;9]]&nbsp;&amp;&amp;&nbsp;echo&nbsp;"8&nbsp;is&nbsp;less&nbsp;than&nbsp;9"</tt></p></td></tr><tr><td><p><tt>-ge</tt></p></td><td><p><tt>-ge</tt></p></td><td><p><tt>[[3&nbsp;-ge&nbsp;3]]&nbsp;&amp;&amp;&nbsp;echo&nbsp;"3&nbsp;is&nbsp;greater&nbsp;than&nbsp;or&nbsp;equal&nbsp;to&nbsp;3"</tt></p></td></tr><tr><td><p><tt>-le</tt></p></td><td><p><tt>-le</tt></p></td><td><p><tt>[[3&nbsp;-le&nbsp;8]]&nbsp;&amp;&amp;&nbsp;echo&nbsp;"3&nbsp;is&nbsp;less&nbsp;than&nbsp;or&nbsp;equal&nbsp;to&nbsp;8"</tt></p></td></tr><tr><td><p><tt>-eq</tt></p></td><td><p><tt>-eq</tt></p></td><td><p><tt>[[5&nbsp;-eq&nbsp;05]]&nbsp;&amp;&amp;&nbsp;echo&nbsp;"5&nbsp;equals&nbsp;05"</tt></p></td></tr><tr><td><p><tt>-ne</tt></p></td><td><p><tt>-ne</tt></p></td><td><p><tt>[[6&nbsp;-ne&nbsp;20]]&nbsp;&amp;&amp;&nbsp;echo&nbsp;"6&nbsp;is&nbsp;not&nbsp;equal&nbsp;to&nbsp;20"</tt></p></td></tr><tr><td colspan="1" rowspan="2"><p>conditional evaluation</p></td><td><p><tt>&amp;&amp;</tt></p></td><td><p><tt>-a</tt> <a href="http://mywiki.wooledge.org/BashFAQ/031#np2">(**)</a></p></td><td><p><tt>[[-n&nbsp;$var&nbsp;&amp;&amp;&nbsp;-f&nbsp;$var]]&nbsp;&amp;&amp;&nbsp;echo&nbsp;"$var&nbsp;is&nbsp;a&nbsp;file"</tt></p></td></tr><tr><td><p><tt>||</tt></p></td><td><p><tt>-o</tt> <a href="http://mywiki.wooledge.org/BashFAQ/031#np2">(**)</a></p></td><td><p><tt>[[-b&nbsp;$var&nbsp;||&nbsp;-c&nbsp;$var]]&nbsp;&amp;&amp;&nbsp;echo&nbsp;"$var&nbsp;is&nbsp;a&nbsp;device"</tt></p></td></tr><tr><td><p>expression grouping</p></td><td><p><tt>(...)</tt></p></td><td><p><tt>\(...&nbsp;\)</tt> <a href="http://mywiki.wooledge.org/BashFAQ/031#np2">(**)</a></p></td><td><p><tt>[[$var&nbsp;=&nbsp;img*&nbsp;&amp;&amp;&nbsp;($var&nbsp;=&nbsp;*.png&nbsp;||&nbsp;$var&nbsp;=&nbsp;*.jpg)&nbsp;]]&nbsp;&amp;&amp;</tt><br><tt>echo&nbsp;"$var&nbsp;starts&nbsp;with&nbsp;img&nbsp;and&nbsp;ends&nbsp;with&nbsp;.jpg&nbsp;or&nbsp;.png"</tt></p></td></tr><tr><td><p>Pattern matching</p></td><td><p><tt>=</tt> (or <tt>==</tt>)</p></td><td><p>(not available)</p></td><td><p><tt>[[$name&nbsp;=&nbsp;a*]]&nbsp;||&nbsp;echo&nbsp;"name&nbsp;does&nbsp;not&nbsp;start&nbsp;with&nbsp;an'a':&nbsp;$name"</tt></p></td></tr><tr><td><p><a href="http://mywiki.wooledge.org/RegularExpression">RegularExpression</a> matching</p></td><td><p><tt>=~</tt></p></td><td><p>(not available)</p></td><td><p><tt>[[$(date)&nbsp;=~&nbsp;^Fri\&nbsp;...\&nbsp;13&nbsp;]]&nbsp;&amp;&amp;&nbsp;echo&nbsp;"It's&nbsp;Friday&nbsp;the&nbsp;13th!"</tt></p></td></tr></tbody></table>

## make background jobs quiet

在使用bash或zsh后台任务时会出现提示

```bash
$ { sleep 1; echo finished; } &
[1] 19510
$ finished

[1]+  Done                    { sleep 1; echo finished; }
```

有时这样的输出可能干扰，有什么方式可以禁止后台任务输出？

bash提供了一个选项`+m`禁止任务控制，但是启用后无法使用jobs查看当前运行的任务了，可以参考这里[Is there a way to make bash job control quiet?](https://stackoverflow.com/a/38278291/8566831)

<!-- markdownlint-disable MD014 -->
```bash
# $ [[ -o monitor ]] && set +m && monitor_enabled=true # unset option monitor if was set
$ { { sleep 2 && echo finished; } & } 2>/dev/null # turn job-control option off and launch quietly
$ finished

# $ [ -n "$monitor_enabled" ] && set -m # set monitor if was set
```

另外zsh后台任务提示可以看这里[auto-run-shell-commands-in-zsh-after-entering-the-directory](auto-run-shell-commands-in-zsh-after-entering-the-directory.md)

## 引用
<!-- heredoc -->
* [How can I write a heredoc to a file in Bash script?](https://stackoverflow.com/a/2954835/8566831)
* [Advanced Bash-Scripting Guide: Chapter 19. Here Documents](https://tldp.org/LDP/abs/html/here-docs.html)
* [wiki: Here 文档](https://zh.wikipedia.org/wiki/Here%E6%96%87%E6%A1%A3)
  <!-- subshell -->
* [var was modified in a subshell. That change might be lost.](https://www.shellcheck.net/wiki/SC2031)
* [How do you catch error codes in a shell pipe?](https://stackoverflow.com/a/4959616/8566831)
* [Get exit status of process that's piped to another](https://unix.stackexchange.com/a/73180)
  <!-- test and brackets -->
* [Are double square brackets `[[ ]]` preferable over single square brackets `[ ]` in Bash?](https://stackoverflow.com/a/669486/8566831)
* [What is the difference between test, `[` and `[[` ?](http://mywiki.wooledge.org/BashFAQ/031)
  <!-- background jobs quiet -->
* [Is there a way to make bash job control quiet?](https://stackoverflow.com/a/38278291/8566831)
* [man bash: Job Control](https://www.gnu.org/software/bash/manual/bash.html#Job-Control)
* [man bash shopt: 4.3.2 The Shopt Builtin](https://www.gnu.org/software/bash/manual/html_node/The-Shopt-Builtin.html)
* [man bash set: 4.3.1 The Set Builtin](https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html#index-set)
* [man bash: 6.4 Bash Conditional Expressions -o](https://www.gnu.org/software/bash/manual/html_node/Bash-Conditional-Expressions.html)
* [How do I wait for background jobs in the background?](https://unix.stackexchange.com/a/323878)

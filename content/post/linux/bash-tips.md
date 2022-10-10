---
title: "Bash Tips"
date: 2022-09-05T11:27:47+08:00
draft: true
---

bash tips

<!--more-->

## heredoc `<<,<<<`

保存文字里面的换行或是缩进等空白字元。允许在字符串里执行变量替换和命令替换。

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

参考：

* [How can I write a heredoc to a file in Bash script?](https://stackoverflow.com/a/2954835/8566831)
* [Advanced Bash-Scripting Guide: Chapter 19. Here Documents](https://tldp.org/LDP/abs/html/here-docs.html)
* [wiki: Here 文档](https://zh.wikipedia.org/wiki/Here%E6%96%87%E6%A1%A3)

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

参考：

* [var was modified in a subshell. That change might be lost.](https://www.shellcheck.net/wiki/SC2031)
* [How do you catch error codes in a shell pipe?](https://stackoverflow.com/a/4959616/8566831)
* [Get exit status of process that's piped to another](https://unix.stackexchange.com/a/73180)

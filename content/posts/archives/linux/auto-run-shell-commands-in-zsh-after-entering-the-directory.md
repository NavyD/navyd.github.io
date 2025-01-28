---
title: "进入目录后自动运行shell命令"
date: 2021-10-01T02:22:59+08:00
draft: false
tags: [zsh, hugo, cd]
---

在使用hugo时需要启动服务实时查看本地渲染情况，每次启动都要键入命令`hugo server -D`比较麻烦，有没有一种方式在hugo博客目录时自动运行命令。

另外，通常会检查当前目录是否是一个git项目，并自动运行相关命令

## 分析

在编写博客时通常要进入命令行（vscode terminal），只要在cd后自动运行就行了。zsh提供了一个hook函数`chpwd()`

```bash
function chpwd() {
    emulate -L zsh
    ls -a
}
```

实际在zsh中使用chpwd_functions定义当改变目录时运行多个function，对于耗时的任务需要后台运行

注意

在使用子shell时环境变量修改应该谨慎，在后台任务subshell无法修改其环境变量，可能需要其它方式与当前shell通信，如使用缓存文件替换环境变量

```bash
declare -A _onefetch_repos=()
# 注意：不要使用后台任务更新vars，无效
{
    ONEFETCH_TIMEOUT="${ONEFETCH_TIMEOUT:=10}"
    timeout "${ONEFETCH_TIMEOUT}" onefetch && _onefetch_repos["$cur_repo"]=1
} &
# _onefetch_repos 无法被更新
```

不要使用wait后台任务等待另一个后台任务。由于前一个任务修改了setopt nomonitor，禁止了任务输出，如果在后台任务中最后setopt monitor会出现任务输出，所以想要使用下一个后台任务去`setopt monitor`，但是这样的后台任务的方式一定是会出现任务输出。且不能在subshell中使用wait

```bash
# 禁止zsh 任务控制
if [[ -o monitor ]]; then
    local -r monitor_enabled=true
    setopt nomonitor
fi
{
    sleep 3 && echo test
    # [ -n "$monitor_enabled" ] && setopt monitor # 将会出现任务输出：
    # [7]  + exit 1     { ... }
} &
# wait %% # 等待
# 尝试重启用任务控制，任务输出还是会出现的
# { sleep 4; [ -n "$monitor_enabled" ] && setopt monitor } &

# 无法在subshell中使用wait另一个job
$ sleep 21 &
[1] 27095
$ { wait 27095; echo aa; } &
[2] 27378
wait: pid 27095 is not a child of this shell
```

另外，[zsh-defer: Deferred execution of zsh commands](https://github.com/romkatv/zsh-defer)使用zsh-defer异步运行job，同时可以修改shell变量，但只能运行完成后才能响应键入命令

> zsh-defer defers execution of a zsh command until zsh has nothing else to do and is waiting for user input. Its intended purpose is staged zsh startup. It works similarly to Turbo mode in zinit.

## 方案

对于使用chpwd，可以参考这里使用了相关的zsh hook：[direnv/direnv: internal/cmd/shell_zsh.go](https://github.com/direnv/direnv/blob/c74bab86d2c547364c0f5c282ff41d76f1ebadde/internal/cmd/shell_zsh.go#L10-L22)，[ajeetdsouza/zoxide: templates/zsh.txt](https://github.com/ajeetdsouza/zoxide/blob/main/templates/zsh.txt)

### zsh-defer

```bash
declare -A _onefetch_repos=()
_onefetch_hook_chpwd() {
    emulate -L zsh
    if git rev-parse 2>/dev/null; then
        _onefetch_cur_repo="$(git rev-parse --show-toplevel | xargs basename)"
        if [ ! "${_onefetch_repos["$_onefetch_cur_repo"]}" ]; then
            if timeout 0.8 onefetch; then
                _onefetch_repos["$_onefetch_cur_repo"]=1
            else
                # for key val in "${(@kv)_onefetch_repos}"; do echo "$key -> $val"; done
                echo "defering onefetch timeout ${ONEFETCH_TIMEOUT:=10} for $_onefetch_cur_repo"
                # -12: enable redir to stdin/stderr https://github.com/romkatv/zsh-defer#usage
                # +p: Call zle reset-prompt，即在最后模拟键入enter刷新prompt
                zsh-defer -12 -c 'timeout "${ONEFETCH_TIMEOUT:=2}" onefetch && _onefetch_repos["$_onefetch_cur_repo"]=1' # eval
            fi
        fi
    fi
}
if [[ -z "${chpwd_functions[(r)_onefetch_hook_chpwd]+1}" ]]; then
    chpwd_functions=( _onefetch_hook_chpwd "${chpwd_functions[@]}" )
fi
```

### ohmyzsh dotenv

[ohmyzsh/plugins/dotenv](https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/dotenv)提供了类似的方式自动加载.env文件，可以使用.env文件实现

```bash
# project/.env
# auto start hugo server in entering dir of this project
if command -v hugo >/dev/null && ! pidof hugo >/dev/null; then
    echo 'hugo serving'
    # in the shell session background
    hugo server -D >/dev/null &
fi
```

### background jobs

TODO：使用缓存文件替换环境变量

### 参考

* [ZSH: automatically run ls after every cd](https://stackoverflow.com/a/3964198/8566831)
* [Execute bash scripts on entering a directory](https://unix.stackexchange.com/a/21364)
* [zsh wait for jobs to complete](https://unix.stackexchange.com/a/227411)
* [zsh: How to check if an option is enabled](https://unix.stackexchange.com/a/122743)
* [9 Functions - zsh 9.3.1 Hook Functions chpwd](https://zsh.sourceforge.io/Doc/Release/Functions.html)
* [direnv/direnv: internal/cmd/shell_zsh.go](https://github.com/direnv/direnv/blob/c74bab86d2c547364c0f5c282ff41d76f1ebadde/internal/cmd/shell_zsh.go#L10-L22)
* [ajeetdsouza/zoxide: templates/zsh.txt](https://github.com/ajeetdsouza/zoxide/blob/main/templates/zsh.txt)
* [SC2031 – ShellCheck Wiki var was modified in a subshell. That change might be lost.](https://www.shellcheck.net/wiki/SC2031)
* [zsh-defer: Deferred execution of zsh commands](https://github.com/romkatv/zsh-defer)
* [Iterating over keys (or k/v pairs) in zsh associative array?](https://superuser.com/a/1237504)

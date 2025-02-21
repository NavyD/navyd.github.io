---
title: 在 Systemd Unit 中转义字符
date: 2025-02-21T16:12:29+08:00
draft: false
tags: [systemd, shell, linux]
---

在 [systemd.unit](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html) 中的 [ExecStart](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html#ExecStart=) 有时会使用 shell 执行命令，就会出现字符串转义的问题。

## 分析

```sh
watchexec -vv \
    --emit-events-to none \
    --fs-events create,modify,remove,rename \
    --filter '**/common/*' \
    # 禁用首次启动时运行命令 \
    --postpone \
    # 等待时发现有新的事件时重启 \
    --on-busy-update restart \
    # 事件等待间隔 \
    --debounce 10s \
    --shell none \
    -- sh -euxc '\
        sleep 120; \
        is_running="$(docker ps -q -f name=photoprism -f status=running)"; \
        [ -z "$is_running" ] && docker start photoprism; \
        docker exec -u "$(id -u):$(id -g)" photoprism photoprism index -c; \
        [ -z "$is_running" ] && docker stop photoprism;'
```

参考 [String Escaping for Inclusion in Unit Names](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html#String%20Escaping%20for%20Inclusion%20in%20Unit%20Names)

> The escaping algorithm operates as follows: given a string, any "/" character is replaced by "-", and all other characters which are not ASCII alphanumerics, ":", "_" or "." are replaced by C-style "\x2d" escapes. In addition, "." is replaced with such a C-style escape when it would appear as the first character in the escaped string.

使用 [systemd-escape](https://www.freedesktop.org/software/systemd/man/latest/systemd-escape.html) 命令可以将 `''` 单引号中内容转义：

```console
$ cat <<'EOF'
"hello world'
EOF

$ cat <<'EOF' | xargs -0 --no-run-if-empty systemd-escape
"hello world'
EOF
\x22hello\x20world\x27\x0a

$ systemd-escape 'echo \"hello world\"'
echo\x20\x5c\x22hello\x20world\x5c\x22
```

## 解决

将部分引用内 `'` 转义 `\x27` 避免可读性下降

```systemd
[Service]
ExecStart=/usr/bin/zsh -c 'watchexec -vv \
    --emit-events-to none \
    --fs-events create,modify,remove,rename \
    --filter "**/common/*" \
    # 禁用首次启动时运行命令 \
    --postpone \
    # 等待时发现有新的事件时重启 \
    --on-busy-update restart \
    # 事件等待间隔 \
    --debounce 10s \
    --shell none \
    -- sh -euxc \x27\
        sleep 120; \
        is_running="$(docker ps -q -f name=photoprism -f status=running)"; \
        [ -z "$is_running" ] && docker start photoprism; \
        docker exec -u "$(id -u):$(id -g)" photoprism photoprism index -c; \
        [ -z "$is_running" ] && docker stop photoprism;\x27'
```

参考：

- [How do I cat multi-line content to a file in a systemd unit file?](https://stackoverflow.com/a/32447633/8566831)
- [Systemd string escaping](https://stackoverflow.com/a/38367553/8566831)
- [How to escape single quotes within single quoted strings](https://stackoverflow.com/a/1250279/8566831)
- [xargs: unmatched single quote; by default quotes are special to xargs unless you use the -0 option](https://askubuntu.com/a/1106806)

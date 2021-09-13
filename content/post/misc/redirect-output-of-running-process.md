---
title: "重定向已启动程序的输出"
date: 2021-09-06T12:22:01+08:00
draft: false
---

## 问题

在使用[clash](https://github.com/Dreamacro/clash)时要在clash启动后创建对应tun设备iptables与ip route相关操作，这需要保证clash正常启动。

如果使用延时方式操作，可能clash不一定能启动完成，如在clash首次启动时会进行较长时间的初始化下载，延时不可取。如果可以读取clash的输出，可以保证clash可以正常启动
<!--more-->
## 分析

下面是典型的clash的启动输出：

```sh
$ clash
time="2021-09-13T02:35:40Z" level=info msg="Start initial provider HK"
time="2021-09-13T02:35:40Z" level=info msg="Start initial provider IEPL"
time="2021-09-13T02:35:40Z" level=info msg="Start initial provider SGP"
time="2021-09-13T02:35:40Z" level=info msg="Start initial provider US"
time="2021-09-13T02:35:40Z" level=info msg="Start initial provider NeteaseMusic"
time="2021-09-13T02:35:40Z" level=info msg="Start initial provider TW"
time="2021-09-13T02:35:40Z" level=info msg="Start initial compatible provider GoogleCN"
time="2021-09-13T02:35:40Z" level=info msg="Start initial compatible provider Proxy"
time="2021-09-13T02:35:40Z" level=info msg="Start initial compatible provider Epic"
time="2021-09-13T02:35:40Z" level=info msg="Start initial compatible provider Apple"
time="2021-09-13T02:35:40Z" level=info msg="Start initial compatible provider SSH22"
time="2021-09-13T02:35:40Z" level=info msg="Start initial compatible provider Icloud"
time="2021-09-13T02:35:40Z" level=info msg="Start initial compatible provider Final-Match"
time="2021-09-13T02:35:40Z" level=info msg="Start initial compatible provider Telegram"
time="2021-09-13T02:35:40Z" level=info msg="Start initial rule provider direct"
time="2021-09-13T02:35:40Z" level=info msg="Start initial rule provider telegramcidr"
time="2021-09-13T02:35:40Z" level=info msg="Start initial rule provider reject"
time="2021-09-13T02:35:41Z" level=info msg="Start initial rule provider gfw"
time="2021-09-13T02:35:41Z" level=info msg="Start initial rule provider tld-not-cn"
time="2021-09-13T02:35:41Z" level=info msg="Start initial rule provider cncidr"
time="2021-09-13T02:35:41Z" level=info msg="Start initial rule provider proxy"
time="2021-09-13T02:35:41Z" level=info msg="Start initial rule provider lancidr"
time="2021-09-13T02:35:41Z" level=info msg="Start initial rule provider icloud"
time="2021-09-13T02:35:41Z" level=info msg="Start initial rule provider netease-music"
time="2021-09-13T02:35:41Z" level=info msg="Start initial rule provider greatfire"
time="2021-09-13T02:35:41Z" level=info msg="Start initial rule provider apple"
time="2021-09-13T02:35:41Z" level=info msg="Start initial rule provider private"
time="2021-09-13T02:35:41Z" level=info msg="Start initial rule provider google"
time="2021-09-13T02:35:41Z" level=info msg="RESTful API listening at: 0.0.0.0:9090"
time="2021-09-13T02:35:41Z" level=info msg="DNS server listening at: 0.0.0.0:5353"
```

通常可以在启动程序时重定向如`clash &> temp.log`，有没有一种可能，复制或重定向已启动程序的输出，这样可以不用局限于启动clash，只要clash进程存在就行

### strace

过滤strace的输出

- 过滤write指定的文件描述符fd

使用`-e write=1,2`表示仅列出fd 1与2即stdout,stderr。但是在docker的进程中与宿主机存在区别，无法生效。

```bash
$ strace -p $(pgrep clash) -e write=1 -e signal=none -e trace=write
strace: Process 220553 attached
write(14, "E\0\0\220\304\206@\0?\21\352\250\306\22\0\10\306\22\0\1'\34\36a\0|\204\334\0\1\0`"..., 144) = 144
write(14, "E\0\4\351\17\36@\0@\21&\\\337J\2\335\300\250]\272\\@\312J\4\325\302m\27\376\375\0"..., 1257) = 1257
#...
```

strace使用`-y`显示对应的fd

```bash
$ sudo strace -p $(pgrep clash) -e trace=write -y
strace: Process 220553 attached
write(14</dev/net/tun>, "E\0\0004\237D@\0?\6\20S\306\22\0\7\306\22\0\1\221 \36a>[\376\316\234k\271\274"..., 52) = 52
write(35<socket:[1897396]>, "\202\301!\16F\234\256\3733\270\307H\203\265!\223H\344_#\337)d\223\310~]%m\362\250\202"..., 71) = 71
write(1<pipe:[1652130]>, "...", 40) = 40
```

查看对应进程的fd

- 在docker中

    ```bash
    $ docker exec -it clash bash -c 'ls -al /proc/$(pgrep clash)/fd'
    total 0
    dr-x------    2 root     root             0 Sep 13 06:10 .
    dr-xr-xr-x    9 nobody   nobody           0 Sep 13 06:10 ..
    lrwx------    1 root     root            64 Sep 13 06:10 0 -> /dev/null
    l-wx------    1 root     root            64 Sep 13 06:10 1 -> pipe:[1652130]
    lrwx------    1 root     root            64 Sep 13 06:10 10 -> socket:[1645489]
    # ...

    # docker clash进程在主机上的fd
    $ sudo ls -al /proc/$(pgrep clash)/fd
    total 0
    dr-x------ 2 root   root     0 Sep 13 14:24 .
    dr-xr-xr-x 9 nobody nogroup  0 Sep 13 14:09 ..
    lrwx------ 1 root   root    64 Sep 13 14:29 0 -> /dev/null
    l-wx------ 1 root   root    64 Sep 13 14:29 1 -> 'pipe:[1652130]'
    lrwx------ 1 root   root    64 Sep 13 14:29 10 -> 'socket:[1645489]'
    # ...
    ```

- 在host中

    ```bash
    # no redirection
    $ bash -c 'while true; do echo '1'; sleep 1; done & ls -al /proc/$!/fd && kill -9 $!'
    1
    total 0
    dr-x------ 2 navyd navyd  0 Sep 13 14:18 .
    dr-xr-xr-x 9 navyd navyd  0 Sep 13 14:18 ..
    lr-x------ 1 navyd navyd 64 Sep 13 14:18 0 -> /dev/null
    lrwx------ 1 navyd navyd 64 Sep 13 14:18 1 -> /dev/pts/0
    lrwx------ 1 navyd navyd 64 Sep 13 14:18 2 -> /dev/pts/0
    # ...

    # redirect to /dev/null
    $ while true; do echo '1'; sleep 1; done >/dev/null & ls -al /proc/$!/fd && kill -9 $!
    total 0
    dr-x------ 2 navyd navyd  0 Sep 13 12:42 .
    dr-xr-xr-x 9 navyd navyd  0 Sep 13 12:42 ..
    lrwx------ 1 navyd navyd 64 Sep 13 12:42 0 -> /dev/pts/0
    l-wx------ 1 navyd navyd 64 Sep 13 12:42 1 -> /dev/null
    lrwx------ 1 navyd navyd 64 Sep 13 12:42 10 -> /dev/pts/0
    lr-x------ 1 navyd navyd 64 Sep 13 12:42 11 -> /home/navy
    # ...
    ```

可以明显的看到docker中的stdout被链接到了`pipe:[1652130]`，而host中是一个本地路径链接，strace可能无法正确访问docker的stdout，可以使用readlink读取链接给strace过滤：`-P "$(readlink /proc/"$CLASH_PID"/fd/1)"`

```bash
start_clash() {
    sudo -u "$RUN_USER" clash -d "$CLASH_DIR"
    strace -P "$(readlink /proc/"$CLASH_PID"/fd/1)" -e trace=write -e signal=none -s 1000 -X raw -p "$CLASH_PID" 2>&1 | while read -r line; do
        # 修改
        line=$(sed -n -r 's/^write\([0-9]+,\s*"(.+)",\s*[0-9]+\)\s*=\s*[[:digit:]]+$/\1/p' <<< "$line")
        # echo "dumping line: $line"
        if [[ $line == *"listening at"* ]]; then
            echo "clash has started at line: $line"
            break
        fi
    done
}
```

注意：

- strace默认输出到stderr重定向到标准输出`2>&1`
- `-X raw`使用原始的输出防止乱码
- `-s 1000`指定最大的打印字符串避免默认32过小截断输出
- `-e trace=write -e signal=none`过滤非write输出

***但是上面存在一个问题，strace是对sys call作用，clash输出log时没有`Start initial rule provider`与后面的`listening at`，同时使用sync命令没用，可能是缓存没有刷新。这里不清楚 TODO***

<!-- TODO -->

另外还有gdb,screen两种方式可以重定向，但是无法简单编程使用

## 解决

### 重定向

最简单的方法就是在后台重定向clash的输出到文件，再读取文件确认启动

```bash
# start clash and confirm and return pid
start_clash() {
    sudo -u "$RUN_USER" clash -d "$CLASH_DIR" &> temp.log
    local pid=$!
    tail -f temp.log | while read -r line
    do
        if [[ $line == *"listening at"* ]]; then
            echo "clash has started at line: $line"
            return pid
        fi
    done
}
```

注意不能使用`sudo -u "$RUN_USER" clash -d "$CLASH_DIR" | while read -r line; do ... done`，在while退出break后将会使clash直接退出。下面使用bash一行命令测试：无限循环while退出后整个管道命令终止

```bash
#!/bin/bash
local count=0; while true; do echo "sleeping $((count+=1))"; sleep 1; done | while read line; do echo "read $line"; if [[ $line == *"9"* ]]; then echo "end $line"; break; fi; done
```

另外，可以使用python等方式完全重写更好维护，算上iptables相关的配置都200多行了

参考：

- [Redirect STDERR / STDOUT of a process AFTER it's been started, using command line?](https://stackoverflow.com/questions/593724/redirect-stderr-stdout-of-a-process-after-its-been-started-using-command-lin)
- [Redirecting the Output of an Already Running Process](https://www.baeldung.com/linux/redirect-output-of-running-process)
- [How do I save terminal output to a file?](https://askubuntu.com/a/731237)
- [Why strace doesn't work in Docker](https://jvns.ca/blog/2020/04/29/why-strace-doesnt-work-in-docker/)
- [How to check if a string contains a substring in Bash](https://stackoverflow.com/a/229606/8566831)
- [How to get the pid of the last executed command in shell script?](https://unix.stackexchange.com/questions/30370/how-to-get-the-pid-of-the-last-executed-command-in-shell-script)
- [grep on a variable](https://unix.stackexchange.com/a/163814)

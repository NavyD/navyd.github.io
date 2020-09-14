# 后台运行任务

## 如何让一个普通的shell命令在shell terminal退出后还在后台运行

### 描述

在wsl2中启动xfce4桌面用命令`startxfce4`，只要退出shell就终止进程

```bash
$ startxfce4 2>/dev/null &
```

即使用了这个`&`也在shell退出后就终止，退出时提示：

```bash
zsh: you have running jobs
```

`jobs`可查看到当前shell运行的进程

### 方法

nohup和builds-in disown命令

```bash
#!/bin/bash
if ! command -v xfce4-session > /dev/null; then
    return
fi
echo 'checking the xfce4 environment';
if ! pidof xfce4-session > /dev/null; then
    DISPLAY=$(awk '/nameserver / {print $2; exit}' /etc/resolv.conf 2>/dev/null):0 # in WSL 2
    export DISPLAY
    export LIBGL_ALWAYS_INDIRECT=1
    echo 'starting up xfce4 desktop'
    nohup startxfce4 & disown
fi
```

当shell退出后还可以运行，可以通过ps,pidof查看

```bash
$ ps -aux | grep xfce4-session
navyd       90  0.0  0.0 271844 24700 pts/0    SNl  17:44   0:00 xfce4-session
navyd      689  0.0  0.0   7252  2392 pts/0    SN   17:44   0:00 /usr/bin/dbus-launch --sh-syntax --exit-with-session xfce4-session

$ pidof xfce4-session
90
```

参考：

- [Exiting terminal running “nohup ./my_script &” => “You have running jobs”. OK to exit?](https://unix.stackexchange.com/questions/231316/exiting-terminal-running-nohup-my-script-you-have-running-jobs-ok-to)
- [Exit zsh, but leave running jobs open?](https://stackoverflow.com/questions/19302913/exit-zsh-but-leave-running-jobs-open)
- [linux后台运行和关闭、查看后台任务](https://www.cnblogs.com/qize/p/11392533.html)
- [Linux 后台运行程序的几种方法](https://www.jianshu.com/p/48a65d33760d)

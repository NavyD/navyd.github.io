# installation

## import

## ubuntu init

### source list

```bash
sudo sed --in-place=.bak "s/archive.ubuntu.com/mirrors.aliyun.com/g" /etc/apt/sources.list
```

### softwares

```bash
sudo apt-get install openjdk-14-jdk
```

## desktop environment

- [wsl2-tutorial](https://github.com/QMonkey/wsl-tutorial/blob/master/README.wsl2.md)
- [WSL](https://wiki.ubuntu.com/WSL#Running_Graphical_Applications)
- [WSL使用笔记](https://blog.faymek.com/2018/11/2018-11-03-wsl%E4%BD%BF%E7%94%A8%E7%AC%94%E8%AE%B0/)

### Install xfce desktop

```bash
$ sudo apt-get install xfce4 xfce4-terminal
```

如果出现`Unable to fetch some archives`可修复后再install

```bash
# 可能出现的问题：
# Get:598 http://mirrors.aliyun.com/ubuntu focal/main amd64 usb-modeswitch-data all 20191128-3 [32.3 kB]
# Get:599 http://mirrors.aliyun.com/ubuntu focal/main amd64 usb-modeswitch amd64 2.5.2+repack0-2ubuntu3 [53.1 kB]
# Fetched 189 MB in 1min 26s (2180 kB/s)
# E: Failed to fetch http://mirrors.aliyun.com/ubuntu/pool/main/i/isl/libisl22_0.22.1-1_amd64.deb  Undetermined Error [IP: 112.67.242.118 80]
# E: Failed to fetch http://mirrors.aliyun.com/ubuntu/pool/main/g/gnome-keyring/gnome-keyring_3.36.0-1ubuntu1_amd64.deb  Undetermined Error [IP: 112.67.242.118 80]
# E: Failed to fetch http://mirrors.aliyun.com/ubuntu/pool/main/g/gst-plugins-base1.0/gstreamer1.0-gl_1.16.2-4_amd64.deb  Undetermined Error [IP: 112.67.242.118 80]
# E: Unable to fetch some archives, maybe run apt-get update or try with --fix-missing?
$ sudo apt-get update --fix-missing
$ sudo apt-get install xfce4 xfce4-terminal
```

Configuring lightdm选择`lightdm`

```bash
Package configuration




 ┌──────────────────────────────────────────────┤ Configuring lightdm ├──────────────────────────────────────────────┐
 │ A display manager is a program that provides graphical login capabilities for the X Window System.                │
 │                                                                                                                   │
 │ Only one display manager can manage a given X server, but multiple display manager packages are installed.        │
 │ Please select which display manager should run by default.                                                        │
 │                                                                                                                   │
 │ Multiple display managers can run simultaneously if they are configured to manage different servers; to achieve   │
 │ this, configure the display managers accordingly, edit each of their init scripts in /etc/init.d, and disable     │
 │ the check for a default display manager.                                                                          │
 │                                                                                                                   │
 │ Default display manager:                                                                                          │
 │                                                                                                                   │
 │                                                     gdm3                                                          │
 │                                                     lightdm                                                       │
 │                                                                                                                   │
 │                                                                                                                   │
 │                                                      <Ok>                                                         │
 │                                                                                                                   │
 └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### configuration

```bash
# wsl2
export DISPLAY=$(awk '/nameserver / {print $2; exit}' /etc/resolv.conf 2>/dev/null):0 # in WSL 2
export LIBGL_ALWAYS_INDIRECT=1

if ! pidof xfce4-session > /dev/null; then 
    echo 'starting up xfce4 desktop'
    startxfce4 2>/dev/null &
fi

# fcitx
export XMODIFIERS=@im=fcitx
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
if pidof fcitx > /dev/null; then
    echo 'starting up fcitx'
    fcitx -d
fi
```

```bash

sudo apt-get install fcitx fcitx-pinyin
# Install drop-down terminal
sudo apt-get install guake
```


### idea desktop

```bash
[Desktop Entry]
Name=IntelliJ IDEA
Comment=IntelliJ IDEA
Exec=/usr/local/bin/idea/idea-IU-201.7846.76/bin/idea.sh
Icon=/usr/local/bin/idea/idea-IU-201.7846.76/bin/idea.png
Terminal=false
Type=Application
Categories=Developer
```

### 问题/usr/bin/dpkg error

在安装xfce4 desktop相关的软件时，出现了`/usr/bin/dpkg error`，可能是`/etc/apt/sources.list.d/vscode.list`没有目录

```bash
$ sudo apt-get install guake
# ...
/var/lib/dpkg/info/code.postinst: line 71: /etc/apt/sources.list.d/vscode.list: No such file or directory
dpkg: error processing package code (--configure):
 installed code package post-installation script subprocess returned error exit status 1
# ...
Errors were encountered while processing:
 code
E: Sub-process /usr/bin/dpkg returned an error code (1)
```

确实是没有目录`/etc/apt/sources.list.d`，可能什么时候改成了`/etc/apt/sources.list.d.bak`，改回`/etc/apt/sources.list.d`即可

```bash
$ ll /etc/apt/sources.list.d
ls: cannot access '/etc/apt/sources.list.d': No such file or directory

$ ll /etc/apt/sources.list.d.bak
total 32K
drwxr-xr-x 2 root root 4.0K Aug  5 12:54 .
drwxr-xr-x 7 root root 4.0K Sep  8 20:09 ..
-rw-r--r-- 1 root root  201 Aug  5 12:55 deadsnakes-ubuntu-ppa-bionic.list

$ sudo mv /etc/apt/sources.list.d.bak /etc/apt/sources.list.d
```

`sudo apt-get install guake`完整的输出：

```bash
$ sudo apt-get install guake
[sudo] password for navyd:
Reading package lists... Done
Building dependency tree
Reading state information... Done
The following additional packages will be installed:
  gir1.2-keybinder-3.0 gir1.2-wnck-3.0 python3-pbr
Suggested packages:
  numix-gtk-theme
The following NEW packages will be installed:
  gir1.2-keybinder-3.0 gir1.2-wnck-3.0 guake python3-pbr
0 upgraded, 4 newly installed, 0 to remove and 5 not upgraded.
1 not fully installed or removed.
Need to get 860 kB of archives.
After this operation, 2552 kB of additional disk space will be used.
Do you want to continue? [Y/n] y
Get:1 http://mirrors.aliyun.com/ubuntu focal/universe amd64 gir1.2-keybinder-3.0 amd64 0.3.2-1ubuntu1 [3164 B]
Get:2 http://mirrors.aliyun.com/ubuntu focal/main amd64 gir1.2-wnck-3.0 amd64 3.36.0-1 [9104 B]
Get:3 http://mirrors.aliyun.com/ubuntu focal/main amd64 python3-pbr all 5.4.5-0ubuntu1 [64.0 kB]
Get:4 http://mirrors.aliyun.com/ubuntu focal/universe amd64 guake all 3.6.3-2 [784 kB]
Fetched 860 kB in 1s (1451 kB/s)
Selecting previously unselected package gir1.2-keybinder-3.0.
(Reading database ... 108951 files and directories currently installed.)
Preparing to unpack .../gir1.2-keybinder-3.0_0.3.2-1ubuntu1_amd64.deb ...
Unpacking gir1.2-keybinder-3.0 (0.3.2-1ubuntu1) ...
Selecting previously unselected package gir1.2-wnck-3.0:amd64.
Preparing to unpack .../gir1.2-wnck-3.0_3.36.0-1_amd64.deb ...
Unpacking gir1.2-wnck-3.0:amd64 (3.36.0-1) ...
Selecting previously unselected package python3-pbr.
Preparing to unpack .../python3-pbr_5.4.5-0ubuntu1_all.deb ...
Unpacking python3-pbr (5.4.5-0ubuntu1) ...
Selecting previously unselected package guake.
Preparing to unpack .../archives/guake_3.6.3-2_all.deb ...
Unpacking guake (3.6.3-2) ...
Setting up code (1.48.2-1598353430) ...
/var/lib/dpkg/info/code.postinst: line 71: /etc/apt/sources.list.d/vscode.list: No such file or directory
dpkg: error processing package code (--configure):
 installed code package post-installation script subprocess returned error exit status 1
Setting up python3-pbr (5.4.5-0ubuntu1) ...
update-alternatives: using /usr/bin/python3-pbr to provide /usr/bin/pbr (pbr) in auto mode
Setting up gir1.2-keybinder-3.0 (0.3.2-1ubuntu1) ...
Setting up gir1.2-wnck-3.0:amd64 (3.36.0-1) ...
Setting up guake (3.6.3-2) ...
Processing triggers for mime-support (3.64ubuntu1) ...
Processing triggers for gnome-menus (3.36.0-1ubuntu1) ...
Processing triggers for libglib2.0-0:amd64 (2.64.3-1~ubuntu20.04.1) ...
Processing triggers for man-db (2.9.1-1) ...
Processing triggers for desktop-file-utils (0.24-1ubuntu3) ...
Errors were encountered while processing:
 code
E: Sub-process /usr/bin/dpkg returned an error code (1)
```

还有另一种方法：重建`/var/lib/dpkg/info`

[E: Sub-process /usr/bin/dpkg returned an error code (1)解决办法](https://blog.csdn.net/stickmangod/article/details/85316142)

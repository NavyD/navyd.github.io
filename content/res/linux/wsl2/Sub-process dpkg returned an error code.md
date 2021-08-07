# Sub-process /usr/bin/dpkg returned an error code

## 描述

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

## 原因

确实是没有目录`/etc/apt/sources.list.d`，可能什么时候改成了`/etc/apt/sources.list.d.bak`

```bash
$ ll /etc/apt/sources.list.d
ls: cannot access '/etc/apt/sources.list.d': No such file or directory
$ ll /etc/apt/sources.list.d.bak
total 32K
drwxr-xr-x 2 root root 4.0K Aug  5 12:54 .
drwxr-xr-x 7 root root 4.0K Sep  8 20:09 ..
-rw-r--r-- 1 root root  201 Aug  5 12:55 deadsnakes-ubuntu-ppa-bionic.list
```

## 方法

### 创建`/etc/apt/sources.list.d`

```bash
$ sudo mv /etc/apt/sources.list.d.bak /etc/apt/sources.list.d
```

### 重建`/var/lib/dpkg/info`

参考：[E: Sub-process /usr/bin/dpkg returned an error code (1)解决办法](https://blog.csdn.net/stickmangod/article/details/85316142)

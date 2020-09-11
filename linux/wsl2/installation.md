# installation

## import

## ubuntu init

### source list

```bash
sudo sed --in-place=.bak "s/archive.ubuntu.com/mirrors.aliyun.com/g" /etc/apt/sources.list
```

### softwares

#### 通用

```bash
sudo apt-get install openjdk-14-jdk shellcheck tldr
```

- tldr: Displays simple help pages for command-line tools

#### fcitx中文输入法

```bash
sudo apt-get install fcitx fcitx-pinyin
```

注意：

- 如果输入法没有响应，可检查配置是否在shell环境中

```bash
export XMODIFIERS=@im=fcitx
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
```

- 如果切换快捷键没有反应，可以看下是不是设置与windows一样了，最好是不一样就好打开fcitx配置
`input method configuration -> global config`:

```
trigger input method: CTRL+SHIFT+SPACE,
extra key for trigger input method: L_SHIFT,
enable hotkey to scroll between input method: checked
```

#### VS code

#### Idea

安装idea桌面快捷方式到`/usr/share/applications/intellij-idea.desktop`：

```toml
[Desktop Entry]
Version=1.0
Type=Application
Terminal=false
Icon=/usr/local/bin/idea/idea-IU-201.7846.76//bin/idea.png
Exec="/usr/local/bin/idea/idea-IU-201.7846.76//bin/idea.sh %f"
Name=IntelliJ Idea
Categories=Development;IDE;
```

#### Chrome

```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
```

#### zsh配置

```bash
sudo apt-get install zsh
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
git clone https://github.com/zsh-users/zsh-autosuggestions "${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions"
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git "${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting"
```

配置

```bash
plugins=(git z extract zsh-autosuggestions zsh-syntax-highlighting mvn)
ZSH_THEME="ys"
```

##### home/end 响应修复

写入shell环境：

```bash
bindkey  "^[[H"   beginning-of-line
bindkey  "^[[F"   end-of-line
```

参考：[Fix key settings (Home/End/Insert/Delete) in .zshrc when running Zsh in Terminator Terminal Emulator](https://stackoverflow.com/questions/8638012/fix-key-settings-home-end-insert-delete-in-zshrc-when-running-zsh-in-terminat)

##### 注意

当从bash先启动startxfce4，退出后加载的是zsh，则可能导致先前的变量`DISPLAY`无效：

```bash
$ startxfce4
/usr/lib/xorg/Xorg.wrap: Only console users are allowed to run the X server
```

修改文件`/etc/X11/Xwrapper.config`：

```bash
allowed_users = anybody
```

启动后依然出现error，这是由于`DISPLAY`无效导致，在`.zshrc`中重设即可

[Error when trying to use Xorg: Only console users are allowed to run the X server?
](https://unix.stackexchange.com/a/529945)

#### Docker安装

- [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- [Install Docker Compose](https://docs.docker.com/compose/install/)

ohmyzsh自带plugin支持命令行补全

```bash
plugins=(git z extract zsh-autosuggestions zsh-syntax-highlighting mvn docker)
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

### 修改快捷键

#### xml

用xml的方式修改`~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml`

```bash
$ cat ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml | grep -i insert
      <property name="&lt;Alt&gt;Insert" type="string" value=""/>
```

将对应的`property.value`置为空即可

```bash
$ cat ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml | grep -i f12
      <property name="&lt;Alt&gt;F12" type="empty"/>
```

参考：

- [pycharm在ubuntu xfce下面Alt+insert快捷键冲突解决](https://yuchi.blog.csdn.net/article/details/77433901)

#### editor

在settings editor中找`xfce4-keyboard-shortcuts`中对应的快捷键，删除`property.value`置为空

注意：在`xfce4-settings-manager -> keyboard`中快捷键不全

参考：[Change global keyboard shortcuts](https://unix.stackexchange.com/questions/44643/change-global-keyboard-shortcuts#:~:text=Go%20to%20Menu%20%E2%86%92%20Settings,Xfce4%2C%20though%20not%20user%20friendly.)

### 黑屏

在一段时间没有操作后就会黑屏，但是`xfce4-session`并没有进程退出

在/etc/X11/xorg.conf.d/文件夹下创建文件20-intel.conf。

```bash
sudo mkdir /etc/X11/xorg.conf.d
sudo vim /etc/X11/xorg.conf.d/20-intel.conf
```

然后在文件中输入以下内容，保存退出即可解决问题。

```bash
Section "Device"
  Identifier "Intel Graphics"
  Driver "intel"
EndSection
```

***测试不可用***

参考： [[Debian10]intel核显使用xfce锁屏会黑屏无法唤醒解决方案](https://www.cnblogs.com/DouglasLuo/p/12715993.html)

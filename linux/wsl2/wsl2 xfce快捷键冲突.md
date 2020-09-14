# wsl2 xfce快捷键冲突

## 修改快捷键

wsl2 xfce中修改快捷键

### xml

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

### editor

在settings editor中找`xfce4-keyboard-shortcuts`中对应的快捷键，删除`property.value`置为空

注意：在`xfce4-settings-manager -> keyboard`中快捷键不全

![](../../assets/images/a249bcd7-371d-44e9-b23d-4b1af5e5757f.png)

参考：[Change global keyboard shortcuts](https://unix.stackexchange.com/questions/44643/change-global-keyboard-shortcuts#:~:text=Go%20to%20Menu%20%E2%86%92%20Settings,Xfce4%2C%20though%20not%20user%20friendly.)

## `ctrl+alt+b`快捷键冲突

### 描述

在idea中使用`ctrl+alt+b`时出现这个虚拟键盘

![](../../assets/images/e318a901-dda3-45f4-bd17-3efda62a0823.png)

### 原因

Fcitx “虚拟键盘”的快捷键

### 方法

#### gui关闭

1. 打开fcitx设置，选择Addon选项卡，取消选择虚拟键盘
2. 重启fcitx或logout

![](../../assets/images/09dbe5c7-951c-4fb0-b9c4-a92a5056eb7f.png)

参考：[Ubuntu ctrl+alt+b快捷键冲突](https://www.cnblogs.com/drizzlewithwind/p/5997369.html)

#### cli

1. 编辑`/usr/share/fcitx/addon/fcitx-vk.conf`属性`Enabled=false`
2. 重启fcitx或logout

```zsh
# 查看是否启用
$ ccat /usr/share/fcitx/addon/fcitx-vk.conf | grep -i enable
Enabled=True
# 编辑Enabled=false
sudo vim /usr/share/fcitx/addon/fcitx-vk.conf
```

参考：[Weird on screen keyboard appearing when pressing ctrl+alt+b](https://askubuntu.com/a/884288)

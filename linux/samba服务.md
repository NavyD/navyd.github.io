# samba服务

## 安装

```bash
sudo usermod -aG sambashare navyd
sudo chown navyd:sambashare /mnt/share
sudo smbpasswd -a navyd
```

参考：

* [How to Install and Configure Samba on Ubuntu 18.04](https://linuxize.com/post/how-to-install-and-configure-samba-on-ubuntu-18-04/)

## 启用win10自动发现 wsdd

安装wsdd

```bash
sudo sh -c 'echo deb https://pkg.ltec.ch/public/ focal main > /etc/apt/sources.list.d/wsdd.list'
sudo apt-key adv --fetch-keys https://pkg.ltec.ch/public/conf/ltec-ag.gpg.key
sudo apt-get install wsdd
```

参考：

* [解决 Linux samba 主机不能被windows 10 发现的问题](https://zhuanlan.zhihu.com/p/339975385)
* [wsdd](https://github.com/christgau/wsdd)

## win10 samba共享密码无法登陆

在修改win10 登陆当前帐户密码后，不能用新密码登入samba共享，经过重启和注销多次测试，samba还工作在原密码上，可用原密码可正常登入samba中

测试用一个新帐户share，用它做samba分享，测试其它设备可用samba，说明只是帐户密码问题

### 原因

在多次重启和注销中，都使用的是windows hello或PIN登录，没有将新密码同步到系统，可使用新密码登入win10系统

### 解决方案

`选择PIN登录 --> 忘记PIN --> 输入帐户密码 --> 是否确定PIN忘记 --> 否 --> 成功登录`

现在新密码在samba中可用

## win10 samba挂载无法执行exe文件

点击exe文件时无法直接执行，提示没有权限访问文件

![](../assets/images/4a6a52ee-e75b-479c-90af-8d77784f651b.png)

### 解决方法

在`/etc/samba/smb.conf`中`[global]`或自定义组下添加`acl allow execute always = True`：

```ini
# ...
[your-share]
    path = /mnt/share
    browseable = yes
    read only = no
    writeable = yes
    force create mode = 0660
    force directory mode = 2770
    valid users = user, @sambashare
    # fix Execute a .exe on a samba share error
    acl allow execute always = True
```

参考：

* [Execute a .exe on a samba share](https://unix.stackexchange.com/questions/188721/execute-a-exe-on-a-samba-share)

## docker启动

可以考虑使用docker同时启动samba与wsdd，但是没有直接使用的方法，可以参考下面的方法。默认的两个独立容器配置wsdd不能正常工作在samba容器间，没有测试过修改配置或放到同一个容器中

<!-- todo -->

参考：

* [JonasPed/wsdd-docker](https://github.com/JonasPed/wsdd-docker)
* [dperson/docker-samba](https://github.com/dperson/samba)

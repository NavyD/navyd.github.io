# pi

## 安装

ubuntu

修改密码：

```bash
sudo passwd ubuntu
sudo adduser navyd
sudo usermod -a -G sudo,adm,dialout,cdrom,floppy,sudo,audio,dip,video,plugdev,netdev,lxd navyd
```

修改source.list

```
# 默认注释了源码镜像以提高 apt update 速度，如有需要可自行取消注释
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ focal main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ focal main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ focal-updates main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ focal-updates main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ focal-backports main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ focal-backports main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ focal-security main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ focal-security main restricted universe multiverse

# 预发布软件源，不建议启用
# deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ focal-proposed main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ focal-proposed main restricted universe multiverse
```

* [Ubuntu 镜像使用帮助](https://mirror.tuna.tsinghua.edu.cn/help/ubuntu/)

### docker

```
curl -fsSL https://get.docker.com -o get-docker.sh | sh
```

docker: Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Post http://%2Fvar%2Frun%2Fdocker.sock/v1.24/containers/create: dial unix /var/run/docker.sock: connect: permission denied.
See 'docker run --help'.

```
sudo usermod -aG docker navyd
```

### zsh

```bash
sudo apt-get install zsh zsh-antigen
chsh -s /bin/zsh navyd
```

修改hostname

```
sudo hostnamectl set-hostname 'rpi4-ubuntu'
```

### docker openwrt

```bash
sudo ip link set eth0 promisc on
```

混杂模式（英语：promiscuous mode）是电脑网络中的术语。是指一台机器的网卡能够接收所有经过它的数据流，而不论其目的地址是否是它。

一般计算机网卡都工作在非混杂模式下，此时网卡只接受来自网络端口的目的地址指向自己的数据。当网卡工作在混杂模式下时，网卡将来自接口的所有数据都捕获并交给相应的驱动程序。网卡的混杂模式一般在网络管理员分析网络数据作为网络故障诊断手段时用到，同时这个模式也被网络黑客利用来作为网络数据窃听的入口。在Linux操作系统中设置网卡混杂模式时需要管理员权限。在Windows操作系统和Linux操作系统中都有使用混杂模式的抓包工具，比如著名的开源软件Wireshark。

```bash

```

#### 旁路由模式

采用`主路由关DHCP，openwrt开唯一DHCP`，一旦openwrt连接到主路由会自动获取ip

* [[N1盒子] N1网关模式(旁路由)详细设置指南-搭配主路由华为AX3Pro](https://www.right.com.cn/forum/thread-4035785-1-1.html)
* [在Docker 中运行 OpenWrt 旁路网关](https://mlapp.cn/376.html)
* [OpenWrt-Rpi-Docker 镜像](https://github.com/SuLingGG/OpenWrt-Rpi-Docker)

如果连接主路由wifi时无法获取ip，可以使用固定ip的方式连接；

##### 安装openwrt后win10无法通过ssh访问rpi4主机

在路由器上无法找到rpi4的ip地址

可以在路由器上开户dhcp服务，但是不选中唯一的server，在openwrt中选中dhcp作为唯一server。这样当openwrt没有启动时，网络依然可用，而且在路由上存在了到rpi4的ip地址

##### 启动v2ray无法访问国内网络

在使用ShadowSocksR Plus+启动后, 只能访问外网，切换iptables防火墙全局模式才可以访问国内网络

[Xray以后版本为什么国内网站无法访问](https://github.com/SuLingGG/OpenWrt-Rpi-Docker/issues/15)

解决方法：接口 - LAN网络里面，物理设置，取消桥接接口，应用即可

这个问题可能只出现在当前日期`20210209`的openwrt: `registry.cn-shanghai.aliyuncs.com/suling/openwrt:latest`

#### rpi4主机通过ip访问openwrt

在主机上无法直接通过ip访问openwrt.

基本方式是使用创建虚拟网上通过`macvlan`docker接口互通

```bash
ifname="openwrt"
openwrt_ip="192.168.93.2"
ifip="192.168.93.3/24"
sudo ip link add link eth0 $ifname type macvlan mode bridge # 在 eth0 接口下添加一个 macvlan 虚拟接口
sudo ip addr add $ifip brd + dev $ifname # 为 $ifname 分配 ip 地址
sudo ip link set $ifname up
sudo ip route del default # 删除默认路由
sudo ip route add default via $openwrt_ip dev $ifname # 设置静态路由
# echo "nameserver 10.1.1.1" > /etc/resolv.conf # 设置静态 dns 服务

# delete vif
# sudo ip link delete $ifname
```

使用netplan设置dns使ip生效

```yaml
network:
    ethernets:
        eth0:
            dhcp4: true
            optional: true
            nameservers:
                    addresses: [192.168.93.2]
```

```bash
sudo netplan apply
```

可能无法Ping通，但是可以用`curl google.com`测试

* [docker 中运行 openwrt](https://github.com/lisaac/openwrt-in-docker)
* [Openwrt 下 Docker 网络食用方法](https://zhuanlan.zhihu.com/p/113664215)

#### 多开openwrt

修改mac地址

* [树莓派 | Docker上运行 OpenWrt 做旁路由，超简单！](https://blog.sillyson.com/archives/7.html)

#### 开启wifi

```yaml
network:
    ethernets:
        eth0:
            dhcp4: true
            optional: true
    version: 2

    wifis:
        wlan0:
            dhcp4: true
            access-points:
                "wifi的ssid":
                    password: "wifi密码"
```

```bash
$ sudo netplan try
Job for netplan-wpa-wlan0.service canceled.

An error occurred: Command '['systemctl', 'stop', 'systemd-networkd.service', 'netplan-wpa-*.service']' returned non-zero exit status 1.

Reverting.
Warning: Stopping systemd-networkd.service, but it can still be activated by:
  systemd-networkd.socket
```

#### 开启wifi ap热点

* [从零开始：树莓派共享 WiFi 秒变无线热点（树莓派路由器](https://zhuanlan.zhihu.com/p/102598741)
* [Setting up a Raspberry Pi as a routed wireless access point](https://www.raspberrypi.org/documentation/configuration/wireless/access-point-routed.md)

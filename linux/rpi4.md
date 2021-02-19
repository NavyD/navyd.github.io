# pi

## 安装

## 初始化ubuntu server 20.04

修改密码：

```bash
sudo passwd ubuntu
# 添加用户
sudo adduser navyd
# 复制ubuntu 的默认权限
sudo usermod -a -G sudo,adm,dialout,cdrom,floppy,sudo,audio,dip,video,plugdev,netdev,lxd navyd

# 安装zsh
sudo apt-get install zsh zsh-antigen
# 修改用户默认shell
chsh -s /bin/zsh navyd

# 修改hostname
sudo hostnamectl set-hostname 'rpi4-ubuntu'
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

### 修改时间

在系统的时间比实际时间慢了8小时

```sh
# 查看当前的时间信息
$ timedatectl
               Local time: Thu 2021-02-18 17:43:31 UTC
           Universal time: Thu 2021-02-18 17:43:31 UTC
                 RTC time: n/a
                Time zone: Etc/UTC (UTC, +0000)
System clock synchronized: yes
              NTP service: active
          RTC in local TZ: no

# 查看可用的时区
$ timedatectl list-timezones
# ...
Asia/Shanghai
Asia/Singapore
# ...

# 修改时区
$ sudo timedatectl set-timezone Asia/Shanghai
```

### docker openwrt

安装docker

```
curl -fsSL https://get.docker.com -o get-docker.sh | sh -c
# 解决权限问题
sudo usermod -aG docker navyd
```

混杂模式（英语：promiscuous mode）是电脑网络中的术语。是指一台机器的网卡能够接收所有经过它的数据流，而不论其目的地址是否是它。

一般计算机网卡都工作在非混杂模式下，此时网卡只接受来自网络端口的目的地址指向自己的数据。当网卡工作在混杂模式下时，网卡将来自接口的所有数据都捕获并交给相应的驱动程序。网卡的混杂模式一般在网络管理员分析网络数据作为网络故障诊断手段时用到，同时这个模式也被网络黑客利用来作为网络数据窃听的入口。在Linux操作系统中设置网卡混杂模式时需要管理员权限。在Windows操作系统和Linux操作系统中都有使用混杂模式的抓包工具，比如著名的开源软件Wireshark。

```bash
sudo ip link set eth0 promisc on

# 下载启动openwrt
docker run --restart always --name openwrt -d --network openwrtnet --privileged registry.cn-shanghai.aliyuncs.com/suling/openwrt:rpi4 /sbin/init
```

#### 旁路由模式

采用`主路由关DHCP，openwrt开唯一DHCP`，一旦openwrt连接到主路由会自动获取ip

如果连接主路由wifi时无法获取ip，可以使用固定ip的方式连接；

```yaml
network:
  ethernets:
    eth0:
      dhcp4: false
      addresses:
        - 192.168.93.243/24
      gateway4: 192.168.93.1
        # 防止网上无法连接 开机时等待
      optional: true
      nameservers:
        addresses:
          - 192.168.93.2
  version: 2
```

使用netplan设置dns使ip生效

```bash
sudo netplan generate
sudo netplan apply
```

可能会出现下面的问题`systemd-networkd.socket`直接重启快点

```bash
$ sudo netplan try
Job for netplan-wpa-wlan0.service canceled.

An error occurred: Command '['systemctl', 'stop', 'systemd-networkd.service', 'netplan-wpa-*.service']' returned non-zero exit status 1.

Reverting.
Warning: Stopping systemd-networkd.service, but it can still be activated by:
  systemd-networkd.socket
```

参考：

* [[N1盒子] N1网关模式(旁路由)详细设置指南-搭配主路由华为AX3Pro](https://www.right.com.cn/forum/thread-4035785-1-1.html)
* [在Docker 中运行 OpenWrt 旁路网关](https://mlapp.cn/376.html)
* [OpenWrt-Rpi-Docker 镜像](https://github.com/SuLingGG/OpenWrt-Rpi-Docker)
* [Netplan configuration examples](https://netplan.io/examples/#configuration)

##### rpi4主机通过ip访问openwrt

在主机上无法直接通过ip访问openwrt.

基本方式是使用创建虚拟网上通过`macvlan`docker接口互通

```bash
#!/bin/sh
ifname="openwrt"
openwrt_ip="192.168.93.2"
ifip="192.168.93.202/24"

ip link delete $ifname
ip link add $ifname link eth0 type macvlan mode bridge # 在 eth0 接口下添加一个 macvlan 虚拟接口
ip addr add $ifip dev $ifname # 为 $ifname 分配 ip 地址
ip link set $ifname up # 启动ifname
ip route add $openwrt_ip dev $ifname # 可以ping通
ip route del default
ip route add default via $openwrt_ip dev $ifname #  设置静态路由
```

参考：

* [【Docker】macvlan网络模式下容器与宿主机互通](https://rehtt.com/index.php/archives/236/)
* [docker 中运行 openwrt](https://github.com/lisaac/openwrt-in-docker)
* [Openwrt 下 Docker 网络食用方法](https://zhuanlan.zhihu.com/p/113664215)

可以将上面的sh脚本写成systemd service，在将下面的内容写入`/etc/systemd/system/myinit.service`文件中

```
[Unit]
Description=My init services

[Service]
ExecStart=/home/navyd/config-openwrt-net.sh
Type=oneshot
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

使用`systemctl`工具：

```bash
sudo systemctl daemon-reload
sudo systemctl enable myinit.service
sudo systemctl status myinit.service
sudo systemctl restart myinit.service
```

参考：[How to run scripts on start up?](https://askubuntu.com/a/719157)

##### 安装openwrt后win10无法通过ssh访问rpi4主机名

在路由器上无法找到rpi4的ip地址。必须在openwrt上主动解析出主机名。可以通过openwrt中dns设置固定主机新增的网卡ip

#### docker无法停止openwrt

```bash
docker update --restart=no openwrt
```

#### 启动v2ray无法访问国内网络

在使用ShadowSocksR Plus+启动后, 只能访问外网，切换iptables防火墙全局模式才可以访问国内网络

解决方法：接口 - LAN网络里面，物理设置，取消桥接接口，应用即可

这个问题可能只出现在当前日期`20210209`的openwrt: `registry.cn-shanghai.aliyuncs.com/suling/openwrt:latest`

参考：[Xray以后版本为什么国内网站无法访问](https://github.com/SuLingGG/OpenWrt-Rpi-Docker/issues/15)

#### 多开openwrt

修改mac地址

* [树莓派 | Docker上运行 OpenWrt 做旁路由，超简单！](https://blog.sillyson.com/archives/7.html)

#### 使用wifi连接网络

```yaml
network:
  ethernets:
    eth0:
      dhcp4: false
      addresses:
        - 192.168.93.243/24
      gateway4: 192.168.93.1
      optional: true
      nameservers:
        addresses:
          - 192.168.93.2
  version: 2
  wifis:
   wlan0:
     access-points:
        # wifi ssid
        "hack_fast":
          password: "147258369.0"
          # 连接隐藏ssid的wifi
          hidden: true
          # 连接5g wifi
          band: 5GHz
     dhcp4: false
     optional: true
     addresses:
       - 192.168.93.245/24
     gateway4: 192.168.93.1
     nameservers:
       addresses:
         - 192.168.93.2
         - 192.168.93.1
```

wifi配置参考：[netplan](https://netplan.io/reference/)

注意：如果使用前面配置了docker network `macvlan` 对eth0配置，wlan0可能无法正确从docker openwrt中获取ip地址，wlan0是没法与docker内的网络通信的，暂时没有研究。rpi4的wifi网卡速度比较慢`135 Mbit/s, 40MHz`。如果做AP使用更慢，大概是7Mbit/s的样子，基本不可用

#### 开启wifi ap热点

* [从零开始：树莓派共享 WiFi 秒变无线热点（树莓派路由器](https://zhuanlan.zhihu.com/p/102598741)
* [Setting up a Raspberry Pi as a routed wireless access point](https://www.raspberrypi.org/documentation/configuration/wireless/access-point-routed.md)

## 安装docker compose

在docker官方文档中没有提到如何在arm上安装docker compose，而且在[docker compose仓库](https://github.com/docker/compose/releases)中也没有发布arm的release文件。但可使用pip安装

```sh
$ sudo apt-get install python3-pip

# 检查pip安装
$ pip3 --version
pip 20.0.2 from /usr/lib/python3/dist-packages/pip (python 3.8)

$ pip3 install docker-compose
#...
Installing collected packages: cached-property, python-dotenv, texttable, distro, docopt, websocket-client, dockerpty, pycparser, cffi, bcrypt, paramiko, docker, docker-compose
  WARNING: The script dotenv is installed in '/home/navyd/.local/bin' which is not on PATH.
  Consider adding this directory to PATH or, if you prefer to suppress this warning, use --no-warn-script-location.
  WARNING: The script distro is installed in '/home/navyd/.local/bin' which is not on PATH.
# ...

$ docker-compose --version
docker-compose version 1.28.4, build unknown
```

如果shell提示没有找到docker-compose，可能是docker-compose没有在环境变量中，可以检查`$HOME/.local/bin`

参考：

* [Alternative install options](https://docs.docker.com/compose/install/#alternative-install-options)

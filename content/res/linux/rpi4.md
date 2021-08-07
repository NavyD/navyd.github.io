# pi

## 安装

## 初始化ubuntu server 20.04

### 修改用户名

```bash
# permit root ssh login
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
# sudo echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config
# -bash: /etc/ssh/sshd_config: Permission denied
sudo sh -c 'echo PermitRootLogin yes >> /etc/ssh/sshd_config'

# as root
# killall 所有之前用户的进程
ps -u navyd | awk 'NR>1{print $1}' | xargs kill -9
# 修改用户名与组
usermod -l navyd ubuntu
usermod -d /home/navyd -m navyd
groupmod -n navyd ubuntu
```

参考：

* [How do I change my username?](https://askubuntu.com/questions/34074/how-do-i-change-my-username/34075#34075)
* [sudo echo “something” >> /etc/privilegedFile doesn't work](https://stackoverflow.com/questions/84882/sudo-echo-something-etc-privilegedfile-doesnt-work)

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
curl -fsSL https://get.docker.com | sudo sh
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

## 使用wifi网络

1. 配置[netplan wifi](https://netplan.io/reference/) `/etc/netplan/50-cloud-init.yaml`

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
            "your-ssid":
              password: "your-password"
              # 连接隐藏ssid的wifi
              hidden: true
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

2. 修改country code将`/etc/default/crda`中替换为`REGDOMAIN=CN`

    ```sh
    # 查询REGDOMAIN对应代码
    $ cat /usr/share/zoneinfo/zone.tab | grep Asia/Shanghai
    CN      +3114+12128     Asia/Shanghai   Beijing Time
    ```

3. 应用配置

    ```sh
    sudo netplan try
    # 如果出现这种错误可以忽略
    # An error occurred: Command '['systemctl', 'stop', 'systemd-networkd.service', # 'netplan-wpa-*.service']' returned non-zero exit status 1.
    # 
    # Reverting.
    # Warning: Stopping systemd-networkd.service, but it can still be activated by:
    #   systemd-networkd.socket
    sudo netplan generate
    sudo netplan apply
    # 可选 重启
    sudo reboot
    ```

参考：

* [Help: Unable to connect to 5G Wifi on raspberry pi 4 using ubuntu server 18.04](https://askubuntu.com/a/1264616)

### wifi验证

wifi扫描可用网络：

```sh
$ sudo iw dev wlan0 scan | grep SSID
        SSID: ChinaNet-WkML
        SSID: MERCURY_1232
        SSID: 62-504
        SSID: hack
        SSID: CMCC-Q9RP
        SSID: CMCC-JdD5
        SSID: 0658
```

查看当前网络wifi连接：

```sh
$ iw wlan0 link
Connected to fe:7c:02:43:c5:5a (on wlan0)
        SSID: hack_fast
        freq: 5745
        RX: 1128953 bytes (6350 packets)
        TX: 1048 bytes (10 packets)
        signal: -39 dBm
        rx bitrate: 150.0 MBit/s
        tx bitrate: 24.0 MBit/s

        bss flags:      short-preamble
        dtim period:    1
        beacon int:     100
```

参考：

* [How can I display the list of available WiFi networks?](https://askubuntu.com/a/567021)
* [Is there a tool to display WiFi information in console?](https://unix.stackexchange.com/a/489619)

### 开启wifi ap热点

注意：如果使用前面配置了docker network `macvlan` 对eth0配置，wlan0可能无法正确从docker openwrt中获取ip地址，wlan0是没法与docker内的网络通信的，暂时没有研究。rpi4的wifi网卡速度比较慢`150 Mbit/s, 40MHz`。如果做AP使用更慢，大概是7Mbit/s的样子，基本不可用

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

## docker 路由器nginx反向代理

<!-- todo -->

## 在ubuntu2004安装摄像头

### 通过raspi-config启用摄像头

启动摄像头需要用到官方的raspi-config配置程序[进入官网下载最新的deb程序](http://archive.raspberrypi.org/debian/pool/main/r/raspi-config/)

```sh
curl -sSLO http://archive.raspberrypi.org/debian/pool/main/r/raspi-config/raspi-config_20210604_all.deb
sudo dpkg -i raspi-config_20210604_all.deb
# 修复依赖报错
sudo apt-get install -f

# 启动raspi-config 在交互界面中选择 Interface Options -> Camera -> ok
sudo raspi-config
```

如果出现固件过时的错误时`Your firmwave appears to be out of date (no start_x.elf). Please update`的解决方法：

```sh
# 查看boot分区所在的设备号，设备号可能是：/dev/mmcblk0p1
df -h
# 将该设备号挂载在/boot上
mount /dev/mmcblk0p1 /boot

# 重新配置
sudo raspi-config
# 树莓派重启
sudo reboot

# 重启后检查是否有摄像头设备
$ ls -al /dev/ | grep video
crw-rw----  1 root video   508,   0 May 27 23:16 media0
crw-rw----  1 root video   508,   1 May 27 23:16 media1
crw-rw----  1 root video   236,   0 May 27 23:16 vchiq
crw-rw----  1 root video   240,   0 May 27 23:16 vcio
crw-rw----  1 root video    81,   5 May 27 23:16 video0
crw-rw----  1 root video    81,   0 May 27 23:16 video10
crw-rw----  1 root video    81,   6 May 27 23:16 video11
crw-rw----  1 root video    81,   7 May 27 23:16 video12
crw-rw----  1 root video    81,   1 May 27 23:16 video13
crw-rw----  1 root video    81,   2 May 27 23:16 video14
crw-rw----  1 root video    81,   3 May 27 23:16 video15
crw-rw----  1 root video    81,   4 May 27 23:16 video16
```

使用raspi lib命令判断摄像头是否激活

```sh
# 如果vcgencmd未找到时 安装
sudo apt install libraspberrypi-bin
# 如果安装后运行vcgencmd提示raspi init failed重启生效
sudo reboot
# 判断摄像头是否激活
vcgencmd get_camera
# supported=1 detected=1
```

### 测试拍照

树莓派自带raspistill可以用来进行摄像头拍照功能，如下命令：

```sh
raspistill -v -o test.jpg
```

参考：

* [树莓派raspberry4B指南part-7 摄像头使用及tensorflow lite实现目标检测](https://zhuanlan.zhihu.com/p/98523007)
* [Ubuntu Server下给树莓派安装摄像头](https://blog.csdn.net/sinat_25259461/article/details/108353324)
* [How to use the Raspberry Pi High Quality camera on Ubuntu Core](https://ubuntu.com/blog/how-to-stream-video-with-raspberry-pi-hq-camera-on-ubuntu-core)

## 启用swap

安装dphys-swapfile

```sh
sudo apt install dphys-swapfile
```

编辑/etc/dphys-swapfile修改默认swap文件位置，sd卡速度太慢，使用usb硬盘：

```properties
# where we want the swapfile to be, this is the default /var/swap
CONF_SWAPFILE=/mnt/share/swap
```

重启

```sh
sudo service dphys-swapfile restart
```

参考：

* [How to set up swap space?](https://raspberrypi.stackexchange.com/questions/70/how-to-set-up-swap-space)
* [Permanently disable swap on Raspbian Buster](https://www.raspberrypi.org/forums/viewtopic.php?t=244130)

## Raspberry Pi OS

适用于raspbian 32bit系统

### 启动配置

在boot分区配置，不是在root分区的`/boot`

* 开启ssh：添加`ssh`空文件

* wifi连接

  ```sh
  ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
  update_config=1
  country=<Insert 2 letter ISO 3166-1 country code here>

  network={
          scan_ssid=1
          ssid="<Name of your wireless LAN>"
          psk="<Password for your wireless LAN>"
          proto=RSN
          key_mgmt=WPA-PSK
          pairwise=CCMP
          auth_alg=OPEN
  }
  ```

* static ip
  * 如果使用的是网线，可以直接在`cmdline.txt`中添加ip：`ip=192.168.x.x`
  * 如果使用的是wifi，需要手动挂载root分区编辑`/etc/dhcpcd.conf`：

    ```sh
    interface wlan0
    static ip_address= 192.168.1.10/24
    static routers=192.168.1.1
    static domain_name_servers=1.1.1.1
    ```

参考：

* [Setting up a Raspberry Pi headless](https://www.raspberrypi.org/documentation/configuration/wireless/headless.md)
* [Setting a static IP address from SD card before boot](https://www.raspberrypi.org/forums/viewtopic.php?t=217629)
* [Setting a Static IP from Boot Drive (headless static IP)](https://raspberrypi.stackexchange.com/questions/85747/setting-a-static-ip-from-boot-drive-headless-static-ip)

## 备份

todo

### 系统迁移

参考：

* [把树莓派的系统迁移到U盘上](https://lyq.blogd.club/2017/02/11/pi-usb-boot/)
* [树莓派学习笔记 篇四：树莓派4B 的系统备份方法大全（全卡+压缩备份）](https://post.smzdm.com/p/apzkgne7/)
* [rpi-clone](https://github.com/billw2/rpi-clone)
* [Move your existing Raspberry Pi 4 Ubuntu install from SD card to USB/SSD](https://medium.com/xster-tech/move-your-existing-raspberry-pi-4-ubuntu-install-from-sd-card-to-usb-ssd-52e99723f07b)

## face_recognition

```sh
pi@raspberrypi:~/.local/bin $ face_recognition --help
Traceback (most recent call last):
  File "/home/pi/.local/bin/face_recognition", line 6, in <module>
    from face_recognition.face_recognition_cli import main
  File "/home/pi/.local/lib/python3.7/site-packages/face_recognition/__init__.py", line 7, in <module>
    from .api import load_image_file, face_locations, batch_face_locations, face_landmarks, face_encodings, compare_faces, face_distance
  File "/home/pi/.local/lib/python3.7/site-packages/face_recognition/api.py", line 3, in <module>
    import PIL.Image
  File "/home/pi/.local/lib/python3.7/site-packages/PIL/Image.py", line 114, in <module>
    from . import _imaging as core
ImportError: libopenjp2.so.7: cannot open shared object file: No such file or directory
```

libf77blas.so

```sh
sudo apt-get install libatlas-base-dev
```

参考：

* [Numpy import error Python3 on Raspberry Pi?](https://stackoverflow.com/a/67043061)

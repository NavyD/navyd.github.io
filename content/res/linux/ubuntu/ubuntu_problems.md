## 在ubuntu中使用su无法root登录(未创建root账户) ##

在终端下用su命令切换到root用户提示认证失败：
```
navyd@navyd-virtual-machine:/usr$ su
Password: 
su: Authentication failure
```

原因是root用户没有被创建。

解决方法:

创建root账户

```
navyd@navyd-virtual-machine:/usr$ sudo passwd 
Enter new UNIX password: 
Retype new UNIX password: 
passwd: password updated successfully
navyd@navyd-virtual-machine:/usr$ su
Password: 
root@navyd-virtual-machine:/usr# 
```

## 软件安装error后出现错误信息提示 ##

右上角提示错误信息：

An error occurred,please run Package Manager from the right-click menu or apt-get in a terminal to see what is wrong.The error message was: 'Error:BrokenCount>0'This usually means that your installed packages have umnet dependencies

![](images/Package_Manager_1.png)

出现这样的提示就是在安装软件的过程中，出现了错误，缺少相应的依赖包。

可以使用一下的方法进行解决。

    sudo apt-get install upgrade
    sudo apt-get install -f

通过以上的命令，缺失的安依赖包也就安装完成了，相应的提示也就消失了。


## vm tools安装后无法拖拽文件 ##

- 点击当前虚拟机设置->选项
- 客户机隔离两个都打勾  拖放和复制黏贴
- 可以尝试点击vmware tools 同步客户机时间


## Ubuntu每次启动报错 ##

[http://www.linuxidc.com/Linux/2014-12/110069.htm](http://www.linuxidc.com/Linux/2014-12/110069.htm "手把手 教你解决Ubuntu的错误提示")

## ubuntu 在vmware中无法使用ss翻墙问题 ##

保持NAT模式；

在虚拟机里面，打开SS Qt版，填入服务器地址和密码、加密方式，方式选择HTTPS的不要选SOCKS。然后系统设置-网络-代理设置里面手动设置代理，地址都是127.0.0.1，端口是1080。这样就可以正常使用SS了。

下面是代理设置：

![](images/2017-12-24_17-22-26.png)

注意：如果关闭ss，将无法上网，需要更换为自动或none，或者不关闭ss。这样的设置为全局模式

## 搜狗输入法使用过程中出错 ##

问题描述：

开机后能够正常使用一段时间，在输入时会突然系统报告发生一个错误，然后就无法正常输入中文。
![](images/ubuntu_problems-sougou_1.png)

点击通知栏搜狗图标，搜狗界面已经不见了

![](images/ubuntu_problems-sougou_2.png)

解决方法：
[http://blog.csdn.net/moewifj/article/details/68484900](http://blog.csdn.net/moewifj/article/details/68484900 "解决Ubuntu 16.04下搜狗输入法显示白框的问题")

## win10 和 Ubuntu 16.04时间不同步

在ubuntu中使用本地时间而不是UTC

```bash
timedatectl set-local-rtc 1 --adjust-system-clock
```

检查是否成功。如果出现下面的warning即表示成功

```bash
navyd@navyd-notebook:~$ timedatectl 
      Local time: 五 2018-02-23 12:08:43 CST
  Universal time: 五 2018-02-23 04:08:43 UTC
        RTC time: 五 2018-02-23 04:08:43
       Time zone: Asia/Shanghai (CST, +0800)
 Network time on: yes
NTP synchronized: no
 RTC in local TZ: yes

Warning: The system is configured to read the RTC time in the local time zone.
         This mode can not be fully supported. It will create various problems
         with time zone changes and daylight saving time adjustments. The RTC
         time is never updated, it relies on external facilities to maintain it.
         If at all possible, use RTC in UTC by calling
         'timedatectl set-local-rtc 0'.
```

如下图：

![](images/win-ubuntu_time_fixed_1.png)

详细信息参考：[How to Fix Time Differences in Ubuntu 16.04 & Windows 10 Dual Boot](http://ubuntuhandbook.org/index.php/2016/05/time-differences-ubuntu-1604-windows-10/)

## 环境变量（全局变量）

将一个变量设置为全局变量，这样程序就能使用到该变量，而不是用户的terminal中shell变量

在用户级别上的变量设置都不是全局变量（系统变量），已经尝试过各种`~/.profile`等文件的设置。

只有在全局范围设置系统变量，如`/etc/profile`;`/etc/environment`

注意：`/etc/environment`文件不支持变量扩展如`PATH=$MY_VAR/bin:$PATH`不支持（未验证）

官方建议不应该在`/etc/profile`中直接设置变量，而是应该在`/etc/profile.d/*.sh`中配置

下面是`/etc/profile.d/myenvvars.sh`的配置文件

```sh
#!/bin/bash

#oracle jdk config
export JAVA_HOME=/opt/java/jdk/jdk1.8.0_151/
export JRE_HOME=${JAVA_HOME}/jre
export CLASSPATH=.
PATH=$JAVA_HOME/bin:$PATH

#maven config
export M2_HOME=/opt/apache-maven-3.5.2
PATH=$M2_HOME/bin:$PATH
```

载入设置

在terminal中使用`source或.`无法生效，可以注销或重启生效

验证是否生效

注意：如果在用户级上如`.profile,.bashrc`中配置变量，在`echo $...`时仍然能够访问，但是不是全局变量，只能在terminal中生效

在全新的终端或cli中验证才行：

- press Alt-F2
- run the command `xterm -e bash --noprofile --norc`
- run the command `env `

在env中查看该变量是否存在

参考：

ubuntu帮助文档 完整的环境变量的描述，比如系统变量，Desktop environment specifics： [EnvironmentVariables](https://help.ubuntu.com/community/EnvironmentVariables?action=fullsearch&value=linkto%3A%22EnvironmentVariables%22&context=180)

验证系统变量生效：[How to list all variables names and their current values?](http://askubuntu.com/questions/275965/how-to-list-all-variables-names-and-their-current-values/356973#356973)

## 软件升级have been kept back

```bash
sudo apt-get install <list of packages kept back>
```

参考：

[“The following packages have been kept back:” Why and how do I solve it?](https://askubuntu.com/questions/601/the-following-packages-have-been-kept-back-why-and-how-do-i-solve-it)

 

## sudo 出现unable to resolve host

由于在system setting --> details --> device name 更改了device name可能会在terminal中sudo时出现提示：

```bash
navyd@navyd-laptop:~$ sudo service privoxy start 
sudo: unable to resolve host navyd-laptop
[sudo] password for navyd:
```

通过命令修改你当前系统的hostname：

```bash
sudo hostname -b localhost
```

过程如下：

```bash
navyd@navyd-laptop:~$ sudo hostname -b localhost
sudo: unable to resolve host navyd-laptop
[sudo] password for navyd: 
navyd@navyd-laptop:~$ sudo hostname -b localhost
```

参考：

[sudo 出现unable to resolve host 解决方法](http://blog.csdn.net/End0o0/article/details/8241847)

## 分区

### ESP分区

[UEFI](https://help.ubuntu.com/community/UEFI?highlight=%28%28UEFI%29%29)

### 卸载挂载点

使用命令umount

```
sudo umount /home
```

注意：

如果由于存在进程访问分区导致无法卸载该挂载点。提示使用的lsof和fuser查看进程占用，然后可以结束一些进程，但是有些目录进程太多，不好操作。

```bash
$ sudo umount /var 
[sudo] password for navyd: 
umount: /var: target is busy
        (In some cases useful info about processes that
         use the device is found by lsof(8) or fuser(1).)
```

可以在先将该分区备份到新的分区，然后将新分区开机挂载到该目录，就可以完成更换挂载点，卸载busy的挂载点

```bash
#挂载新分区用于备份数据
sudo mount /dev/sda10 test/var/
#备份到新分区。注意var的文件夹是否与/var下一致，否则将出现未知错误
sudo cp -ap /var/* /test/var
#更改/etc/fstab开机挂载到/var
sudo vi /etc/fstab
```

重启后将/dev/sda10 挂载到/var目录。然后就可以操作原/var目录下的分区了



### 设置分区label

可以使用`e2label`或`tune2fs -L`更改label

#### 使用`e2label`

```bash
sudo e2label /dev/sda8 home-hdd
```

验证成功输出信息：

```bash
$ lsblk -f
NAME    FSTYPE LABEL    UUID                                 MOUNTPOINT
sdb                                                          
├─sdb4  ntfs            FC70E2F770E2B792                     
├─sdb2  vfat            5AD9-E738                            /boot/efi
├─sdb10 ext4            589a4447-21ea-4068-9da3-0770dd1d8ca4 /usr
├─sdb7  ext4   opt-ssd  e97c4814-61a1-4cf6-b5cf-9ae27c3183af /opt
├─sdb5  ntfs            5E9C82D59C82A6DD                     
├─sdb3                                                       
├─sdb11 ext4            faacec27-9912-45f2-bdff-7dd6d174d0df /
├─sdb1  ntfs   恢复     1E0AD7C70AD799DB                     
├─sdb8  vfat            F0BA-6F0E                            
└─sdb6  ntfs   软件     4E0A75220A75086B                     
sda                                                          
├─sda9  swap   swap-hdd 3d97f103-a824-4a71-8909-fd11754d9b4b [SWAP]
├─sda7  ext4   var-hdd  52700a76-40ac-46c2-91bc-20d9d69558f8 /var
├─sda10 ext4   tmp-hdd  0100f84e-c4a3-49aa-aa15-713fc3e26b2e /tmp
├─sda5  ntfs   文档     0001871A0008FC42                     /media/navyd/文档
├─sda8  ext4   home-hdd 3639ac15-460f-4d5a-bbbd-7f5003573248 /home
└─sda6  ntfs   娱乐     000D5F5000077921                     
```

## 如何处理apt upgrade The following packages have been kept back

原因：

```bash
$ sudo apt-get upgrade
Reading package lists... Done
Building dependency tree
Reading state information... Done
Calculating upgrade... Done
The following packages have been kept back:
  libgl1-mesa-dri libglapi-mesa libglx-mesa0 mesa-vulkan-drivers
0 upgraded, 0 newly installed, 0 to remove and 4 not upgraded.
```

方法：

```bash
sudo apt-get --with-new-pkgs upgrade
```

参考：

- [“The following packages have been kept back:” Why and how do I solve it?](https://askubuntu.com/q/601)

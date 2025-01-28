---
title: "Mounting Practice on Linux"
date: 2022-05-09T22:49:19+08:00
draft: false
tags: [linux, dev, mount]
---

有一个需求，由于raspi4 home目录所在的dev空间容量不足达到90%，需要更换更大容量的dev。当前在系统中已挂载了一个4T的USB dev在/mnt/share/中，想在USB dev中直接划分一个目录挂载到/home中即可，mount的bind最合适

但是，在挂载后出现问题无法执行bin：`mount zsh: permission denied: bin`

```sh
$ mount --bind /mnt/share/home/navyd /home/navyd

$ bin
mount zsh: permission denied: bin
```

<!--more-->

## 分析

出现问题后首先想到的是回滚，卸掉/home/navyd

```sh
# avoid busy device
cd /
sudo umount -f /home/navyd
```

然后在`/mnt/share/`挂载点测试是否可以执行bin文件，结果也无法执行bin，可能是挂载配置的问题。在[这里](https://stackoverflow.com/a/51234415/8566831)了解到可能是mount选项为noexec，查询下当前的mount配置

```sh
$ mount -t ext4
/dev/sda1 on /mnt/share type ext4 (rw,nosuid,nodev,noexec,relatime)
```

下面是/etc/fstab配置

```
# ...
UUID=5d0-x-x /mnt/share ext4 defaults,auto,rw,nofail,users,x-systemd.device-timeout=5 0 0
```

果然是mount的问题，修改fstab增加选项`exec,dev,suid`并重新挂载查询，可以正常执行bin文件。然后试试重新bind /home/navyd看看，也可以正常使用了

```sh
# UUID=5d0-x-x /mnt/share ext4 defaults,auto,rw,nofail,users,exec,dev,suid,x-systemd.device-timeout=5 0 0
$ sudo mount -o remount /mnt/share
$ mount -t ext4
/dev/sda1 on /mnt/share type ext4 (rw,relatime)
$ cd /mnt/share
$ bin
# ...
```

另外提一点，tar确实是最合适linux的备份工具，symlink可以完整的保留，而cp在默认是不会保留link的

### 访问挂载点的原始内容

在挂载后旧目录的内容被覆盖，无法通过原来的目录访问。但linux通过bind挂载仍然可以访问原有目录，如这里我想访问所有占用达到90%磁盘，并删除其中的内容。

```sh
mkdir -p /mnt/home
mount --bind /home /mnt/home
# 原始目录
rm -rf /mnt/home/navyd
```

## 解决

在/etc/fstab中配置

```
UUID=5d0-x-x /mnt/share ext4 defaults,auto,rw,nofail,users,exec,dev,suid,x-systemd.device-timeout=5 0 0
/mnt/share/home/navyd /home/navyd ext4 defaults,bind 0 0
```

参考：

* [How to unmount a busy device [closed]](https://stackoverflow.com/a/19969471/8566831)
* [Can't execute a .sh script from mounted disk (Ubuntu 18.04): zsh: permission denied](https://stackoverflow.com/a/51234415/8566831)
* [Can't execute a script on a mounted external drive](https://superuser.com/a/99637)
* [How do I remount a filesystem as read/write?](https://askubuntu.com/a/175742)
* [How do I do 'mount --bind' in /etc/fstab?](https://serverfault.com/a/613184)
* [Access to original contents of mount point](https://unix.stackexchange.com/a/4428)
* [fstab fileds: defaults](https://man7.org/linux/man-pages/man5/fstab.5.html)
* [Access to original contents of mount point](https://unix.stackexchange.com/a/4428)

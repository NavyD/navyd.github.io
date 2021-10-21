---
title: "docker installation"
date: 2021-08-06T17:30:53+08:00
draft: false
tags: [docker, wsl2]
---

在[Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)提供了安装教程，同时提供一个直接运行的脚本[Install using the convenience script](https://docs.docker.com/engine/install/ubuntu/#install-using-the-convenience-script)

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

## Manage Docker as a non-root user

在安装完成后不能使用非root用户运行，可能遇到下面的问题：

```bash
$ docker stats
Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get "http://%2Fvar%2Frun%2Fdocker.sock/v1.24/version": dial unix /var/run/docker.sock: connect: permission denied
```

可以为当前用户添加到docker组中解决

```bash
sudo groupadd docker
sudo usermod -aG docker "$USER"
#  Change user's primary group membership or logout and login again or reboot
newgrp docker
```

### Rootless mode

在[Run the Docker daemon as a non-root user (Rootless mode)](https://docs.docker.com/engine/security/rootless/#install)中可以不作为root用户运行，在Docker Engine v20.10发布

在ubuntu上可以直接运行`dockerd-rootless-setuptool.sh install`或下载运行`curl -fsSL https://get.docker.com/rootless | sh`

但是在wsl2中存在问题，要使用`dockerd-rootless-setuptool.sh install --skip-iptables`禁用iptables检查，运行后提示成功：

```bash

$ dockerd-rootless-setuptool.sh install --skip-iptables
[INFO] systemd not detected, dockerd-rootless.sh needs to be started manually:

PATH=/usr/bin:/sbin:/usr/sbin:$PATH dockerd-rootless.sh  --iptables=false

[INFO] Creating CLI context "rootless"
Successfully created context "rootless"

[INFO] Make sure the following environment variables are set (or add them to ~/.bashrc):

export PATH=/usr/bin:$PATH
export DOCKER_HOST=unix:///mnt/wslg/runtime-dir/docker.sock
```

但是DOCKER_HOST不合理，docker没有被安装在wslg中，运行`docker stats`失败`Rootless mode`在wsl中不可用

参考：

- [How to fix docker: Got permission denied issue](https://stackoverflow.com/a/48957722/8566831)
- [Manage Docker as a non-root user](https://docs.docker.com/engine/install/linux-postinstall/)

## 配置wsl2 docker自启动

wsl2没有systemd，不能使用官方教程[Configure Docker to start on boot](https://docs.docker.com/engine/install/linux-postinstall/#configure-docker-to-start-on-boot)，只能使用service启动。

配置sudo在运行service命令时不会请求密码

```bassh
echo "$USER ALL=(ALL:ALL) NOPASSWD: /usr/sbin/service" | sudo tee -a "/etc/sudoers.d/$USER"
```

然后在`~/.zshrc`中启动docker

```bash
service docker status > /dev/null || sudo service docker start
```

参考：

- [sudo visudo 退出保存](https://blog.csdn.net/weiyi556/article/details/78980139)
- [Execute sudo without Password?](https://askubuntu.com/a/878705)

## docker更换国内镜像

配置文件启动Docker,修改`/etc/docker/daemon.json`

```json
{
    "registry-mirrors": [
        "http://hub-mirror.c.163.com/",
        "https://docker.mirrors.ustc.edu.cn/"
    ]
}
```

修改保存后，重启 Docker 以使配置生效。`docker info`查看

```bash
$ sudo service docker restart

$ docker info | grep -i mirror
 Registry Mirrors:
  http://hub-mirror.c.163.com/
  https://docker.mirrors.ustc.edu.cn/
```

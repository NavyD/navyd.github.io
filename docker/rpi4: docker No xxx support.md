# no xxx support

环境：

ubuntu 20.04 server
rpi4b

在`docker info`时显示：

```sh
$ docker info
# ...
  http://hub-mirror.c.163.com/
  https://docker.mirrors.ustc.edu.cn/
 Live Restore Enabled: false

WARNING: No memory limit support
WARNING: No swap limit support
WARNING: No kernel memory TCP limit support
WARNING: No oom kill disable support
WARNING: No blkio weight support
WARNING: No blkio weight_device support
```

影响在不能限制和正常显示容器的内存

```sh
$ docker update --memory=400M 17f588668ce6
17f588668ce6
Your kernel does not support swap limit capabilities or the cgroup is not mounted. Memory limited without swap.

$ docker stats
CONTAINER ID   NAME                   CPU %     MEM USAGE / LIMIT   MEM %     NET I/O           BLOCK I/O         PIDS
17f588668ce6   openwrt                218.24%   0B / 0B             0.00%     1.16MB / 330kB    20.3MB / 176kB    63
```

## 解决方式

在`/boot/firmware/cmdline.txt`文件中添加首先最前面：`cgroup_enable=memory cgroup_memory=1 swapaccount=1`，然后重启生效。完整的文件：

```sh
$ cat /boot/firmware/cmdline.txt
cgroup_enable=memory cgroup_memory=1 swapaccount=1 net.ifnames=0 dwc_otg.lpm_enable=0 console=serial0,115200 console=tty1 root=LABEL=writable rootfstype=ext4 elevator=deadline rootwait fixrtc

$ docker stats
CONTAINER ID   NAME       CPU %     MEM USAGE / LIMIT     MEM %     NET I/O           BLOCK I/O         PIDS
17f588668ce6   openwrt    0.57%     283.6MiB / 320MiB     88.62%    1.32GB / 1.32GB   34.2MB / 168kB    80
```

生效后即可对容器内存限制，注意要保证swap>=内存容量

```sh
docker update --memory=320M --memory-swap=320M openwrt
```

参考：

* [How to build a Raspberry Pi Kubernetes cluster using MicroK8s](https://ubuntu.com/tutorials/how-to-kubernetes-cluster-on-raspberry-pi#4-installing-microk8s)
* [enabling cgroup memory doesn't take effect](https://www.raspberrypi.org/forums/viewtopic.php?t=203128)
* [docker stats doesn't report memory usage on arm64 #1112](https://github.com/docker/for-linux/issues/1112)
* [Pi Image docker info warnings - No kernel memory limit support #303](https://github.com/me-box/databox/issues/303)

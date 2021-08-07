# docker installation

[Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)

## Manage Docker as a non-root user

[Manage Docker as a non-root user](https://docs.docker.com/engine/install/linux-postinstall/)

## Got permission denied issue

```bash
$ docker search mysql
Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get http://%2Fvar%2Frun%2Fdocker.sock/v1.40/images/search?limit=25&term=mysql: dial unix /var/run/docker.sock: connect: permission denied
```

参考：

- [How to fix docker: Got permission denied issue](https://stackoverflow.com/questions/48957195/how-to-fix-docker-got-permission-denied-issue)

## 配置wsl2 docker自启动

first edited sudoers:

```bash
sudo visudo
```

And added the following (replace "username" with your user):

```bash
username ALL=(ALL:ALL) NOPASSWD: /usr/sbin/service
```

then in bash.rc added this line:

```bash
service docker status > /dev/null || sudo service docker start
```

参考：

- [sudo visudo 退出保存](https://blog.csdn.net/weiyi556/article/details/78980139)
- [how wsl config service auto start, like docker #30](https://github.com/microsoft/WSL2-Linux-Kernel/issues/30#issuecomment-577667701)

## docker更换国内镜像

[[docker更换国内镜像.md]]
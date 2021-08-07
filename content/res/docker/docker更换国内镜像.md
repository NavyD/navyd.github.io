# docker更换国内镜像

配置文件启动Docker,修改`/etc/docker/daemon.json`

```bash
sudo vim /etc/docker/daemon.json
```

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

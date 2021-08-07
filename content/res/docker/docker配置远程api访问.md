# docker配置远程api访问

在`/etc/docker/daemon.json`中配置：

```json
{
  "registry-mirrors": [
    "https://registry.cn-hongkong.aliyuncs.com",
    "https://lwwzdyx2.mirror.aliyuncs.com"
  ],
  "hosts": [
    "unix:///var/run/docker.sock",
    "tcp://0.0.0.0:2375"
  ]
}
```

参考：

* [Configure where the Docker daemon listens for connections](https://docs.docker.com/engine/install/linux-postinstall/#configure-where-the-docker-daemon-listens-for-connections)
* [Protect the Docker daemon socket](https://docs.docker.com/engine/security/protect-access/)
* [Docker开启远程安全访问](https://www.cnblogs.com/niceyoo/p/13270224.html)

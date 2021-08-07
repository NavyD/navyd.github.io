# MySQL常见问题

## mysql时区差8

### 描述

docker mysql默认配置

启动命令：`docker run --detach --tty --name=mysql0 --restart=always --network mysql-net --mount type=bind,source=$HOME/Workspaces
/docker/mysql/master/conf.d,target=/etc/mysql/conf.d -e MYSQL_ROOT_PASSWORD=1234 mysql:latest`

在java中查询到`LocalDateTime gmtCreate`与win10时间差8小时

### 原因

mysql默认使用System时间，可用查询变量`time_zone`

```bash
mysql root@localhost:(none)> show variables like '%zone%';
+------------------+---------+
| Variable_name    | Value   |
|------------------+---------|
| system_time_zone | UTC     |
| time_zone        | SYSTEM  |
+------------------+---------+
```

### 方法

- my.cnf配置

mysql重启生效

```toml
[mysqld]
default-time-zone=+8:00
```

参考：[Configure time zone to mysql docker container](https://stackoverflow.com/questions/49959601/configure-time-zone-to-mysql-docker-container)

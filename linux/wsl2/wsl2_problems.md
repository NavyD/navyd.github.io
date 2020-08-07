# wsl

## 不能访问wsl2 docker mysql, redis

***描述***

mysql

在java中可用`jdbc:mysql://localhost:33060/seckill?useSSL=false`访问，但是在win10 vscode插件sql tools中用localhost无法连接，用wsl2的ip可连接。而在vscode wsl2 可用localhost连接

redis

在vscode wsl2可用localhost，vscode win10不可用localhost，wsl2 ip可用连接。在java中jedis不可用`localhost`，jedis可以用wsl2 ip

***方法***

用ipv6 `::1`代替`localhost`

- mysql: `jdbc:mysql://[::1]:33060/seckill?useSSL=false`
- redis: `redis://[::1]:6379`

参考

[Can't connect to docker container running inside WSL2 #4983](https://github.com/microsoft/WSL/issues/4983#issuecomment-602487077)

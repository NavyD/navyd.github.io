# zsh加载登录信息

```sh
Welcome to Ubuntu 20.04.2 LTS (GNU/Linux 5.4.72-microsoft-standard-WSL2 x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Fri Jul  9 22:10:44 CST 2021

  System load:                      0.07
  Usage of /:                       18.0% of 250.98GB
  Memory usage:                     8%
  Swap usage:                       0%
  Processes:                        43
  Users logged in:                  0
  IPv4 address for br-33c954977917: 172.18.0.1
  IPv4 address for docker0:         172.17.0.1
  IPv4 address for eth0:            192.168.185.236
```

在`/etc/zsh/zprofile`中添加，不会在每次进入`zsh`时加载

```sh
run-parts /etc/update-motd.d/
```

![](../assets/images/373dd381-3599-4daa-81ae-6b7a271e6f9b.png)

参考：

* [SSHing into system with ZSH as default shell doesn't run /etc/profile](https://unix.stackexchange.com/questions/537637/sshing-into-system-with-zsh-as-default-shell-doesnt-run-etc-profile)

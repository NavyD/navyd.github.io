
# samba

```bash
sudo usermod -aG sambashare navyd
sudo chown navyd:sambashare /mnt/share
sudo smbpasswd -a navyd
```

## wsdd

```bash
sudo sh -c 'echo deb https://pkg.ltec.ch/public/ focal main > /etc/apt/sources.list.d/wsdd.list'
sudo apt-key adv --fetch-keys https://pkg.ltec.ch/public/conf/ltec-ag.gpg.key
sudo apt-get install wsdd
```

参考：

* [How to Install and Configure Samba on Ubuntu 18.04](https://linuxize.com/post/how-to-install-and-configure-samba-on-ubuntu-18-04/)
* [wsdd](https://github.com/christgau/wsdd)
* [解决 Linux samba 主机不能被windows 10 发现的问题](https://zhuanlan.zhihu.com/p/339975385)
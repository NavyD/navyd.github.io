# SAMBA

[Samba : Restricted share directory](https://www.server-world.info/en/note?os=Ubuntu_18.04&p=samba&f=2)

注意：

1. `usermod -G share`会改变group sudo=>share，导致无法使用root。应该使用`usermod -a -G share user`

2. 连接server时，密码是`smbpasswd -a user`时配置的，而不是linux user的密码
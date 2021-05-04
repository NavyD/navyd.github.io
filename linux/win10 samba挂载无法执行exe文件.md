# win10 samba挂载无法执行exe文件

点击exe文件时无法直接执行，提示没有权限访问文件

![](../assets/images/4a6a52ee-e75b-479c-90af-8d77784f651b.png)

## 解决方法

在`/etc/samba/smb.conf`中`[global]`或自定义组下添加`acl allow execute always = True`：

```ini
# ...
[your-share]
    path = /mnt/share
    browseable = yes
    read only = no
    writeable = yes
    force create mode = 0660
    force directory mode = 2770
    valid users = user, @sambashare
    # fix Execute a .exe on a samba share error
    acl allow execute always = True
```

参考：

* [Execute a .exe on a samba share](https://unix.stackexchange.com/questions/188721/execute-a-exe-on-a-samba-share)

# Linux下检测进程是否存在

这个问题看起来好像很简单，`ps -ef | grep xx`一下就行啦！这样做当然可以，但是如果我们考究起性能来，这恐怕不是个好办法。

假设我们现在要监测某进程是否存活，每分钟检查一次，用上面的办法就要每分钟运行一次ps命令并且做一次grep正则查找。这点开销在服务器上似乎不算什么，然而如果我们要在同一节点上同时监测数十个、数百个这样的进程又如何呢？所以，我们有必要从性能的角度出发，发掘一些更好的办法。
 
对于daemon进程，通常都会有自己的pid或者lock文件，我们可以检查这些文件是否存在来判断进程是否存在。然而有些异常情况下，pid文件存在进程却并不存在。因此并不能依赖进程的pid文件来检测进程是否存活。
 
一种可靠的方法是使用`kill -0 pid`，kill -0不会向进程发送任何信号，但是会进行错误检查。如果进程存在，命令返回0，如果不存在返回1。

```sh
$ ps
  PID TTY          TIME CMD
15091 pts/0    00:00:00 bash
15943 pts/0    00:00:00 ps
$ kill -0 15091
$ echo $?
0
$ kill -0 15092
-bash: kill: (15092) - No such process
$ echo $?
1
```

但是，这种方法对于普通用户来说只能用于检查自己的进程，因为向其它用户的进程发送信号会因为没有权限而出错，返回值也是1。

```sh
$ kill 2993
-bash: kill: (2993) - Operation not permitted
$ echo $?
1
```

当然，如果你用特权用户执行kill命令的话，就没有权限问题啦。
 
另一方面，我们知道内核会通过/proc虚拟文件系统导出系统中正在运行的进程信息，每个进程都有一个`/proc/<pid>`目录。因此我们可以将检测进程是否存在转换为检测`/proc/<pid>`目录是否存在，这样就简单多了。
 
## 方法

通常对于daemon进程我们可以从它的pid文件或者lock文件中读取。如果没有pid文件的话，在监控脚本中先用`ps | grep`、pgrep、pidof等命令得到要监控的进程pid，再用上述方法检测就行了。

要注意是在pid文件夹中

```sh
$ l /proc | grep 30747
dr-xr-xr-x   9 navyd navyd     0 Mar  2 17:14 30747
```

rust判断

```rust
Path::new(&format!("/proc/{}", pid)).exists()
```

参考：

* [Linux下检测进程是否存在](https://www.cnblogs.com/hellogc/p/3232017.html)
* [How to check if process is running in linux.](http://stackoverflow.com/questions/13260974/how-to-check-if-process-is-running-in-linux)

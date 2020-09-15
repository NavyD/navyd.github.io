# Shell后台运行任务

## 相关命令

- `&`: 让进程在后台运行
- jobs: 查看后台运行的进程
- fg: 让后台运行的进程到前台来
- bg: 让进程到后台去
- `ctrl+z`: 将一个正在前台执行的命令放到后台，并且暂停

如果当前shell终止，这些后台进程都会终止，下面使用这几个命令在`zsh`命令行启动`idea`测试

```bash
$ ./bin/idea.sh            
OpenJDK 64-Bit Server VM warning: Option UseConcMarkSweepGC was deprecated in version 9.0 and will likely be removed in a future release.
2020-09-15 16:00:21,464 [  12412]   WARN - llij.ide.plugins.PluginManager - Problems found 
# ctrl+z idea进程挂起暂停
^Z
[1]  + 14295 suspended  ./bin/idea.sh

$ jobs  
[1]  + suspended  ./bin/idea.sh
# 切换到前台
$ fg %1
[1]  + 14295 continued  ./bin/idea.sh
loading plugins:
  The Gradle-Java (id=org.jetbrains.plugins.gradle, path=~/Desktop/idea/idea-IU-201.7846.76/
# 出现idea加载gui, ctrl+z 挂起 如果此时退出terminal则idea进程终止
^Z
[1]  + 14295 suspended  ./bin/idea.sh
# idea 后台运行 如果有输出就会到当前shell中出现
$ bg %1             
  The Gradle-Maven (id=org.jetbrains.plugins.gradle.maven, path=~/Desktop/idea/idea-IU-201.7846.76/plugins/gradle-java-maven) plugin Non-optional dependency plugin org.intellij.groovy is disabled 
  #....
$ jobs
[1]  + running    ./bin/idea.sh
# idea进程一起终止
$ exit
```

那如何让一个普通的shell命令在shell terminal退出后还在后台运行？

### disown

Allow sub-processes to live beyond the shell that they are attached to.See also the jobs command

这个命令可以在启动的shell退出后运行，以启动idea为例

```bash
$ ./bin/idea.sh 
OpenJDK 64-Bit Server VM warning: Option UseConcMarkSweepGC was deprecated in version 9.0 and will likely be removed in a future release.
# ctrl+z
^Z
[1]  + 17025 suspended  ./bin/idea.sh

$ bg %1
[1]  + 17025 continued  ./bin/idea.sh
2020-09-15 16:27:41,730 [  31367]   WARN - llij.ide.plugins.PluginManager - Problems found loading plugins:
  The Gradle-Java (id=org.jetbrains.plugins.gradle, path=~/Desktop/idea/idea-IU-201.7846.76/plugins/gradle-java) plugin Non-optional dependency plugin com.intellij.gradle is disabled
  The Gradle-Maven (id=org.jetbrains.plugins.gradle.maven, path=~/Desktop/idea/idea-IU-201.7846.76/plugins/gradle-java-maven) plugin Non-optional dependency plugin org.intellij.groovy is disabled 

$ jobs
[1]  + running    ./bin/idea.sh
$ disown %1    
$ jobs 
# 没有输出        

# idea 不会退出
$ exit
```

### nohub

Allows for a process to live when the terminal gets killed

目前看来还是要用disown配合

在wsl2中启动xfce4桌面用命令`startxfce4`，只要退出shell就终止进程

```bash
$ startxfce4 2>/dev/null &
```

即使用了这个`&`也在shell退出后就终止，退出时提示：

```bash
zsh: you have running jobs
```

`jobs`可查看到当前shell运行的进程

### 方法

`nohup`和`builds-in disown`命令

```bash
#!/bin/bash
if ! pidof xfce4-session > /dev/null; then
    echo 'starting xfce4 desktop'
    # 统一输入到一个文件中，不指定则会到启动时目录中"$(PWD)/nohup.out"
    nohup startxfce4 >> "$HOME/nohup.out" & disown
fi
```

当shell退出后还可以运行，可以通过ps,pidof查看

```bash
$ ps -aux | grep xfce4-session
navyd       90  0.0  0.0 271844 24700 pts/0    SNl  17:44   0:00 xfce4-session
navyd      689  0.0  0.0   7252  2392 pts/0    SN   17:44   0:00 /usr/bin/dbus-launch --sh-syntax --exit-with-session xfce4-session

$ pidof xfce4-session
90
```

参考：

- [Exiting terminal running “nohup ./my_script &” => “You have running jobs”. OK to exit?](https://unix.stackexchange.com/questions/231316/exiting-terminal-running-nohup-my-script-you-have-running-jobs-ok-to)
- [Exit zsh, but leave running jobs open?](https://stackoverflow.com/questions/19302913/exit-zsh-but-leave-running-jobs-open)
- [linux后台运行和关闭、查看后台任务](https://www.cnblogs.com/qize/p/11392533.html)
- [Linux 后台运行程序的几种方法](https://www.jianshu.com/p/48a65d33760d)
- [tldr](https://tldr.sh)

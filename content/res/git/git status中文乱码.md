# git status 中文乱码

`git status`查看有改动但未提交的文件时总只显示数字串，显示不出中文文件名：

```sh
$ git status
On branch master
Your branch is up to date with 'origin/master'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   "linux/vim\351\205\215\347\275\256.md"

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        "docker/docker\346\236\204\345\273\272\345\256\271\345\231\250.md"
        wordpress.md

no changes added to commit (use "git add" and/or "git commit -a")
```

## 解决办法

将git 配置文件 core.quotepath项设置为false。

```sh
$ git config --global core.quotepath false

$ git status
On branch master
Your branch is up to date with 'origin/master'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   linux/vim配置.md

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        docker/docker构建容器.md
        wordpress.md

no changes added to commit (use "git add" and/or "git commit -a")
```

参考：

- [git status 显示中文和解决中文乱码](https://blog.csdn.net/u012145252/article/details/81775362)

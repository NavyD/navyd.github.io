# git

### 在Ubuntu上安装Git

	sudo apt-get install git

## 创建仓库

### 初始化仓库

	git init

注意：这是在当前目录下创建仓库.git的目录，所以需要先创建好项目文件夹才初始化git仓库
```
navyd-virtual-machine:~/workspace/git$ cd project/
navyd@navyd-virtual-machine:~/workspace/git/project$ git init
Initialized empty Git repository in /home/navyd/workspace/git/project/.git/
```
添加到仓库

	git add file_name, file_name2...

如：没有输出就是添加成功
```
navyd@navyd-virtual-machine:~/workspace/git/project$ git add file1 
```


提交修改

    git commit -m "comments"

如：
```
navyd@navyd-virtual-machine:~/workspace/git/project$ git commit -m "back test"
[master 6d60c59] back test
 1 file changed, 2 insertions(+)
```

### 查看仓库当前状态

	git status

如：修改了文件未add
```
navyd@navyd-virtual-machine:~/workspace/git/project$ git status
On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git checkout -- <file>..." to discard changes in working directory)

	modified:   file1

no changes added to commit (use "git add" and/or "git commit -a")
```
add 文件后未commit
```
navyd@navyd-virtual-machine:~/workspace/git/project$ git add file1 
navyd@navyd-virtual-machine:~/workspace/git/project$ git status
On branch master
Changes to be committed:
  (use "git reset HEAD <file>..." to unstage)

	modified:   file1

```

## 概念

### 工作区（Working Directory）

当前使用的目录就是工作区

### 版本库（Repository）

工作区有一个隐藏目录.git，这个不算工作区，而是Git的版本库。

用git add把文件添加进去，实际上就是把文件修改添加到暂存区；
用git commit提交更改，实际上就是把暂存区的所有内容提交到当前分支。

因为我们创建Git版本库时，Git自动为我们创建了唯一一个master分支，所以，现在，git commit就是往master分支上提交更改。


## 版本回退

查看提交commit历史记录

    git log

如：
```
navyd@navyd-virtual-machine:~/workspace/git/project$ git log
commit 6d60c59db71e15f571c3df3bb200502dde578e53
Author: Navy D <dhjnavyd@gmail.com>
Date:   Wed Dec 6 23:03:59 2017 +0800

    back test

commit e533beac0e3681400e0146fc438dfdcc7a58e356
Author: Navy D <dhjnavyd@gmail.com>
Date:   Wed Dec 6 22:56:54 2017 +0800

    add line

commit 7041bccd4373f3dde4dc51db432c79d1ddd60ef5
Author: Navy D <dhjnavyd@gmail.com>
Date:   Wed Dec 6 22:41:14 2017 +0800

    ad 3 files
```

### 回退版本

在Git中，用HEAD表示当前版本，上一个版本就是HEAD^，上上一个版本就是HEAD^^，往上100个版本可写成HEAD~100

回退到上一个版本

	git reset --hard HEAD^

回退到指定版本(需要存在)

	git reset --hard sha1_id

其中sha1_id可以只写部分前缀

### 查看命令历史信息

	git reflog

如：查看历史操作文件的sha1_id信息，恢复到指定版本
```
navyd@navyd-virtual-machine:~/workspace/git/project$ git reflog
6d60c59 HEAD@{0}: reset: moving to 6d60
e533bea HEAD@{1}: reset: moving to HEAD^
6d60c59 HEAD@{2}: commit: back test
e533bea HEAD@{3}: commit: add line
7041bcc HEAD@{4}: commit (initial): ad 3 files

navyd@navyd-virtual-machine:~/workspace/git/project$ git reset --hard 6d60
HEAD is now at 6d60c59 back test
```


### 对比

工作区(work dict)和暂存区(stage)的比较

	git diff file_name

注意：在add和commit后diff都不能显示不同

暂存区(stage)和分支(master)的比较

	git diff --cached file_name



修改文件未add

```
navyd@navyd-virtual-machine:~/workspace/git/project$ git diff file1
diff --git a/file1 b/file1
index a07acb2..3f61a7c 100644
--- a/file1
+++ b/file1
@@ -1,4 +1,4 @@
 git test version back
-
+tttt
 test
 add line
```




设置用户信息

git config --global user.name "Navy D"
git config --global user.email "dhjnavyd@gmail.com"

在家目录创建了.gitconfig文件
```
navyd@navyd-virtual-machine:~$ ll .gitconfig 
-rw-rw-r-- 1 navyd navyd 50 12月  6 22:17 .gitconfig

navyd@navyd-virtual-machine:~$ cat .gitconfig 
[user]
	name = Navy D
	email = dhjnavyd@gmail.com
```

### 删除暂存区的文件

适用于add但未commit到仓库的文件删除

	git rm -r --cached file_name

old

-----------

new

## 常见问题

- 如何将本地仓库同步到github新的仓库中

```bash
# Create a bare clone of the repository.
git clone --bare https://github.com/exampleuser/old-repository.git

# Mirror-push to the new repository.
cd old-repository.git
git push --mirror https://github.com/exampleuser/new-repository.git

# Remove the temporary local repository you created earlier.
cd ..
rm -rf old-repository.git
```

[github: Duplicating a repository](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/duplicating-a-repository)
[Git push existing repo to a new and different remote repo server?](https://stackoverflow.com/q/5181845/8566831)

- 如何查看当前remote

```bash
git remote -v
```

- 如何避免在git push时输入密码

  原因：

  在push时使用的是https而不是ssh

  ```bash
  $ git remote -v
  > origin  https://github.com/USERNAME/REPOSITORY.git (fetch)
  > origin  https://github.com/USERNAME/REPOSITORY.git (push)
  ```

  方法：使用ssh push

  ```bash
  $ git remote set-url origin git@github.com:USERNAME/REPOSITORY.git
  # Verify new remote URL
  $ git remote -v
  > origin  git@github.com:USERNAME/REPOSITORY.git (fetch)
  > origin  git@github.com:USERNAME/REPOSITORY.git (push)
  ```

  参考：

  - [Git push requires username and password](https://stackoverflow.com/q/6565357/8566831)
  - [github Switching remote URLs from HTTPS to SSH](https://help.github.com/en/github/using-git/changing-a-remotes-url#switching-remote-urls-from-https-to-ssh)


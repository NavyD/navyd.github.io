# git

这是一个git日常使用问题记录

## 常见问题

### 如何将本地仓库同步到github新的仓库中

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

参考

- [github: Duplicating a repository](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/duplicating-a-repository)
- [Git push existing repo to a new and different remote repo server?](https://stackoverflow.com/q/5181845/8566831)

### 如何查看当前remote

```bash
git remote -v
```

### 如何避免在git push时输入密码

原因：

在push时使用的是https而不是ssh

```bash
$ git remote -v
> origin  https://github.com/USERNAME/REPOSITORY.git (fetch)
> origin  https://github.com/USERNAME/REPOSITORY.git (push)
```

方法：

使用ssh push

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

### git push Warning added hosts

描述：

当用`git push`时提示：

```bash
$ git push
Warning: Permanently added the RSA host key for IP address '140.82.113.4' to the list of known hosts
```

原因：

github有多个服务器，可能在使用ssh时对改变的ip时自动加入`~/.ssh/known_hosts`

解决：

warnings后ip已添加到ssh hosts文件中，下次push时不会再warning

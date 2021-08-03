# vscode发布

## 定制

### 外部资源

引入css

参考：

- [How to link external css in wordpress? [closed]](https://stackoverflow.com/questions/27045670/how-to-link-external-css-in-wordpress)

### markdown sidebar

参考：

- [博客标题导航栏及标题导航栏联动的实现](https://segmentfault.com/a/1190000038767920)

### vscode git

```sh
❯ git rev-parse --short HEAD
e99d7c3

❯ git diff-tree --no-commit-id --name-only -r e99d7c3a9e
docker/docker构建容器.md
git/git status中文乱码.md
linux/vim配置.md
wordpress/wordpress.md
```

- [How do I list all of the files in a commit?](https://stackoverflow.com/questions/424071/how-do-i-list-all-of-the-files-in-a-commit)
- [Get the short Git version hash](https://stackoverflow.com/questions/5694389/get-the-short-git-version-hash)

## docker部署

### nginx 反向代理

参考：

- [Nginx反向代理wordpress站点](https://blog.csdn.net/czx0132/article/details/109734490)
- [Document how to run behind nginx #331](https://github.com/docker-library/wordpress/issues/331)
- [nginx WordPress](https://www.nginx.com/resources/wiki/start/topics/recipes/wordpress/)

### markdown发布

- [在WordPress中使用Markdown进行写作的正确姿势](https://cloud.tencent.com/developer/article/1150073)
- [WordPress+PublishMarkdown快速构建个人博客](https://www.paincker.com/publish-markdown)
- [命令行创建和发布 MarkDown 到 WordPress](https://zhuanlan.zhihu.com/p/65593971)

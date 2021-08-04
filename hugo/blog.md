# hugo blog

开始使用hugo在github搭建静态博客。

## 选型

可选类型

### 动态

比较知名的动态博客工具有下面几种：

- [wordpress](https://wordpress.com/)
- [typecho](http://typecho.org/)

都是开源项目，wordpress(简称WP)是使用最广泛的，而typecho开发都不是告别活跃

对于博客项目，稳定是前提

开源项目参考：

- [WordPress/WordPress](https://github.com/WordPress/WordPress)
- [typecho/typecho](https://github.com/typecho/typecho)

#### 部署

在试用WP中，虽然现在可以使用docker方便的部署，我使用raspi4 2GB运行有点不够，运行WP与mysql后仅剩下200M左右，如果再vscode remote连接直接死机，需要开启swap才能正常。

#### markdown

由于之前都是使用markdown写作，存在100多篇md博文，不可能一一复制到WP中，所以想使用工具批量发布到WP中。在初步使用中没有发现在WP中有方法直接渲染markdown，基本都是md在线编辑器，不符合需求。

换个方式，使用已经渲染好的html文件发布到WP更好，避免了md的渲染不一致的问题，同时可以使用wp rest api批量更新。

尝试直接复制使用渲染markdown转换的html不可用，WP的html代码文本编辑器会转义部分代码

1. 原始markdown内容

    ```markdown
    # vim配置

    <!-- 去除空格`` ` -->
    `` `yaml
    vim: true
    `` `

    参考：

    * [Vim 配置入门](http://www.ruanyifeng.com/blog/2018/09/vimrc.html)
    ```

1. 使用markdown-preview-enhanced导出cdn hosted文件[vim_markdown_preview_enhanced.html](blog/vim_markdown_preview_enhanced.html)，下面是部分代码：

    ```html
    <!DOCTYPE html><html><head>
    <title>vim&#x914D;&#x7F6E;</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.13.11/dist/katex.min.css">

    <style>
    /**
    * prism.js Github theme based on GitHub's theme.
    * @author Sam Clarke
    */
    code[class*="language-"],
    pre[class*="language-"] {
    color: #333;
    background: none;
    font-family: Consolas, "Liberation Mono", Menlo, Courier, monospace;
    text-align: left;
    white-space: pre;
    word-spacing: normal;
    word-break: normal;
    word-wrap: normal;
    line-height: 1.4;

    -moz-tab-size: 8;
    -o-tab-size: 8;
    tab-size: 8;

    -webkit-hyphens: none;
    -moz-hyphens: none;
    -ms-hyphens: none;
    hyphens: none;
    }
    ```

1. 经过WP转义后[vim_wordpress_esc](blog/vim_wordpress_esc)

    ![](blog/2021-08-04-23-17-08.png) 下面是部分代码：

    ```html
    &nbsp;

    &nbsp;

    <style>
    /**<br />
    * prism.js Github theme based on GitHub's theme.<br />
    * @author Sam Clarke<br />
    */<br />
    code[class*="language-"],<br />
    pre[class*="language-"] {<br />
    color: #333;<br />
    background: none;<br />
    font-family: Consolas, "Liberation Mono", Menlo, Courier, monospace;<br />
    text-align: left;<br />
    white-space: pre;<br />
    word-spacing: normal;<br />
    word-break: normal;<br />
    word-wrap: normal;<br />
    line-height: 1.4;</p>
    <p>-moz-tab-size: 8;<br />
    -o-tab-size: 8;<br />
    tab-size: 8;</p>
    <p>-webkit-hyphens: none;<br />
    -moz-hyphens: none;<br />
    -ms-hyphens: none;<br />
    hyphens: none;<br />
    }</p>
    ```

可以看到`title, link`等tag被移除转义为`&nbsp;`，其中`<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.13.11/dist/katex.min.css">`被移除导致无法正确显示代码高亮；`\n`被转义为`<br />`。下面有可以解决这两个问题：

- minifiy html移除所有`\n`避免转义：有各种插件可以生成一行的html文件
- 在WP中引用全局外部css。有两种方式

  1. 在额外css中插入`@import url("//cdn.jsdelivr.net/npm/katex@0.13.11/dist/katex.min.css");`
    ![](blog/2021-08-05-00-41-10.png)

  1. 在主题style.css中插入`@import url("//cdn.jsdelivr.net/npm/katex@0.13.11/dist/katex.min.css");`
    ![](blog/2021-08-05-00-43-59.png)

参考：

- [在WordPress中使用Markdown进行写作的正确姿势](https://cloud.tencent.com/developer/article/1150073)
- [WordPress+PublishMarkdown快速构建个人博客](https://www.paincker.com/publish-markdown)
- [命令行创建和发布 MarkDown 到 WordPress](https://zhuanlan.zhihu.com/p/65593971)
- [REST API Handbook](https://developer.wordpress.org/rest-api/reference/)
- [rest api: Posts](https://developer.wordpress.org/rest-api/reference/posts/)
- [How to link external css in wordpress? [closed]](https://stackoverflow.com/questions/27045670/how-to-link-external-css-in-wordpress)

#### 问题

到此，markdown渲染的问题解决了，新的问题出现了，如何批量渲染md文件。vscode markdown-preview-enhanced插件只提供了手动的方式渲染出html，front-matter配置自动导出需要打开预览界面才行，不利于自动化

```yaml
---
html:
  embed_local_images: false
  embed_svg: true
  offline: false
  toc: undefined

print_background: false
---
```

另外，对于不常用的图片，可以base64编码嵌入html文件中，缺点是文件过大，不利于缓存加载，链接形式的图片可以懒加载体验更好

于是转而寻找自动化工具，在[typora issues](https://github.com/typora/typora-issues/issues/824#issuecomment-418176112)中找到答案：Static Site Generator

参考：

- [Markdown Preview Enhanced docs](https://shd101wyy.github.io/markdown-preview-enhanced/#/zh-cn/)
- [Support export Multiple Documents #824](https://github.com/typora/typora-issues/issues/824)
- [[Summary] Advanced command line interface support #1999](https://github.com/typora/typora-issues/issues/1999)
- [typora issues](https://github.com/typora/typora-issues)

### 静态

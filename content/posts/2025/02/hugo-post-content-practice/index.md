---
date: 2025-02-04T15:40:12+08:00
tags:
  - hugo
  - actions
  - github
---
# hugo博客实践

![](20250204223346.png)

## hugo new content

在使用`hugo new content posts/your-post.md`创建一个md文件`content/posts/your-post.md`，但更好的博客目录结构可以使用`posts/2025/01/your-post/index.md`这种

根据[leaf-bundles](https://gohugo.io/content-management/archetypes/#leaf-bundles)自动创建叶子结点目录结构，根据常用的shell使用下面的命令运行即可

```bash
hugo new posts/$(date +'%Y/%m')/'your post'
```

```powershell
hugo new "posts/$(Get-Date -Format 'yyyy/MM')/my posts"
```

参考：

* [content-management archetypes](https://gohugo.io/content-management/archetypes/)
* [“Hugo way” to create new content in year/month/subfolders?](https://discourse.gohugo.io/t/hugo-way-to-create-new-content-in-year-month-subfolders/36557)
* [Dates in post filenames](https://discourse.gohugo.io/t/dates-in-post-filenames/26219)
* [搭建好博客之后，纠结怎么组织文章的目录结构](https://linux.do/t/topic/206540)
* [Page resources not working (as expected) with extract date and slug from filename funtionality #4558](https://github.com/gohugoio/hugo/issues/4558)
* [Add a date to default filename](https://discourse.gohugo.io/t/add-a-date-to-default-filename/31059)


## 如何兼容多种主题

由于多种主题间的params是不兼容的，一旦在md的[front matter](https://gohugo.io/content-management/front-matter/)中指定了主题的配置，会导致切换主题后无效。如果允许动态的修改front matter中的主题的配置，能轻易的兼容多种主题

### 模板

从模板中通过[Override the base template](https://gohugo.io/templates/base/#define-the-base-template)和[Template lookup order](https://gohugo.io/templates/lookup-order/)重置`.Site.Params`变量是不可行的，这是由于所有全局模板变量基本是只读的，无法更新，如果使用[hugo.Store](https://gohugo.io/functions/hugo/store/)允许更新但无法覆盖params api

在[Theme components](https://gohugo.io/hugo-modules/theme-components/)中提到允许指定`theme = ['my-shortcodes', 'base-theme']`覆盖主题，尽管也允许使用[Merge configuration from themes](https://gohugo.io/getting-started/configuration/)参考示例[Allow smarter merging of config (esp. params) from themes #8633](https://github.com/gohugoio/hugo/issues/8633)合并主题配置，但有这样一种需求是无法满足的：**当前post中如果存在1个图片链接则作为文章cover**

大多数主题都有cover图片配置参数，但这样的逻辑处理却需要动态处理，只能修改主题的处理逻辑。但如果可以在build page时修改front matter动态的设置cover就可以避免修改主题也能达成类似的效果

参考：

* [Porting posts between themes?](https://discourse.gohugo.io/t/porting-posts-between-themes/35455)
* [CONTENT MANAGEMENT Content adapters](https://gohugo.io/content-management/content-adapters/)
* [Build pages from data source #5074](https://github.com/gohugoio/hugo/issues/5074)
* [Create pages from _content.gotmpl #12427](https://github.com/gohugoio/hugo/issues/12427)
* [Allow Hugo to parse "plain" Markdown #6098](https://github.com/gohugoio/hugo/issues/6098)
* [Could I add Front Matter auto based on markdown file information #8638](https://github.com/gohugoio/hugo/issues/8638)
* [Setting page params/variables from a template](https://discourse.gohugo.io/t/setting-page-params-variables-from-a-template/9505)

### Content adapters

根据[Content adapters](https://gohugo.io/content-management/content-adapters/)通过go模板`content/$section/_content.gotmpl`在构建时动态添加page生成静态页面

#### 问题

`_content.gotmpl`模板只能在构建时使用，其相对于主题中能使用的众多模板Methods相当有限[content-adapters/#methods](https://gohugo.io/content-management/content-adapters/#methods)，只要是与[Page](https://gohugo.io/methods/page/)相关都不可用，如[Site.Config](https://gohugo.io/methods/page/)。

想要动态生成元数据就需要解析md文件，但hugo目前不提供在构建阶段解析markdown,html的方法，如[transform.Markdownify](https://gohugo.io/functions/transform/markdownify/)在这个阶段使用将会出现`this method cannot be called before the site is fully initialized`错误。

另外，如果只用go模板，一旦代码规模稍大其可维护性必然很糟糕。

在github上发现大部分都是使用解析一个data.json文件添加到page，而不是复杂的解析md文件，问题就变成了解析md文件到json再使用`_content.gotmpl`解析添加到page

由于hugo不支持调用外部命令运行[Configuration option to invoke a command upon build #9460](https://github.com/gohugoio/hugo/issues/9460)，在`hugo server|build`等命令运行前需要处理好data.json避免部分数据更新无效的问题

## 部署gh-pages


### gh-pages分支

在gh-pages分支中保留当前构建的static页面，默认情况下会保留deploy的提交，可能导致仓库大小激增。

![](20250204224213.png)

在[actions-gh-pages #Force orphan `force_orphan`](https://github.com/peaceiris/actions-gh-pages#%EF%B8%8F-force-orphan-force_orphan)中提到可以使用`force_orphan: true`仅保留最新提交

```yaml
- name: Deploy
  uses: peaceiris/actions-gh-pages@v4
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./public
    force_orphan: true
```

### baseUrl

如果域名根目录指向主页，无需设置baseUrl

参考：

* [How put the URL base?](https://discourse.gohugo.io/t/how-put-the-url-base/45920)
* [hugo: Host on GitHub Pages](https://gohugo.io/hosting-and-deployment/hosting-on-github/)

## Obsidian

### hugo兼容ob链接

目前未找到兼容`![[img]]`,`[[post.md]]`转换为标准md链接的方式，只能修改obsidian从默认wiki方式转为标准的md链接避免这个问题

![](20250204233158.png)

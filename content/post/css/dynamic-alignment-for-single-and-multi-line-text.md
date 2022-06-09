---
title: "Dynamic Alignment for Single and Multi Line Text"
date: 2022-06-10T07:42:44+08:00
draft: true
---

> 本文由 [简悦 SimpRead](http://ksria.com/simpread/) 转码， 原文地址 [segmentfault.com](https://segmentfault.com/a/1190000021385669)

> 原文链接 [链接] 很久以前 刚入前端那会，产品经理提出了这样一个需求 这段文字能不能这样判断一下，当文字不足一行时，让它居中显示，当文字超过一行就让它居...

> 原文链接
> [https://github.com/XboxYan/notes/issues/13](https://link.segmentfault.com/?enc=W7f2t33ZEBZFA2oExh3MQw%3D%3D.lU%2BQ6scSa3Go1sH71VzNkMDJJWZDeWriX%2FZZXC8KVcs74RVwOFB%2FJrjSkgw1L06%2F)

很久以前
----

刚入前端那会，产品经理提出了这样一个需求

> 这段文字能不能这样判断一下，当文字不足一行时，让它居中显示，当文字超过一行就让它居左，不然居中显示很奇怪，因为最后一行是吊着的

![](https://segmentfault.com/img/remote/1460000021385672)

琢磨了一下，当时我还真按照产品经理的逻辑，通过 `js` 判断一下文字的高度，如果超过一行，就添加一个类名，而且这样的文字很多地方都有，所以还做了遍历，还有最重要的一点是关于方法执行的时机，有可能刚加载的时候高度还获取不到（当时好像还用了定时器，还造成了先居中随后居左跳动的现象）...

```
//伪代码
$('.text').each(function(){
    if($(this).height()>30){
        $(this).addClass('mul');
    }
})
```

然后这些文本有可能还是动态生成的，所以还得在生成文本的地方再调用一次这个方法，功能是做出来了，可别说有多啰嗦了，体验也不咋地（虽然外面的人看不到）

当时也在想，如果是 `CSS` 实现，那么就完全不用考虑这些问题了！

关于 CSS 实现思路
-----------

其实只要你逻辑清晰，`js` 都能实现出来，按照正常的思路一步一步走下来就行了。`CSS` 可不是这样，她需要你有更多的想象力。

比如上面这种需求，表面上来看是需要判断文本行数，这完全不是 `CSS` 能干的事呀，不过我们可以换个方向思考，文本默认是居左的（默认文本流），只有首行是居中的，首行可以联想到`::first-line` 伪元素，所以可以试着这样实现一下

```
<p>这段文字能不能这样判断一下，当文字不足一行时，让它居中显示，当文字超过一行就让它居左</p>
```

```
p::first-line{
    text-align:center;
}
```

很好理解是吧，只针对首行进行居中操作，当多行时，首行已经铺满了，居中或者居左效果已经不明显了，只是稍微有点瑕疵，首行的居中效果和后面的文字看着有些不太整齐的感觉（因为当一行剩余空间不足一个字符的时候会掉下去）

![](https://segmentfault.com/img/remote/1460000021385673)

解决这个问题也很简单，上面的问题是由于首行一直处于居中状态，那有没有什么办法可以只要一行的时候才居中呢？这里可以借助一下 `text-align-last`，意思就是规定多行文本的最后一行的居中方式，如果和`::first-line` 一起使用，**既要满足首行又要满足是最后一行**，是不是就判断出了当前只有一行呢？

```
p::first-line{/*匹配首行*/
    text-align-last:center;/*最后一行居中*/
}
```

![](https://segmentfault.com/img/remote/1460000021385675)

这下就正常了，有点首尾夹击的味道～

[See the Pen](https://codepen.io/xboxyan/pen/WNbjBEX) 点击预览

遗憾的是，由于`::first-line` 支持样式非常有限（[MDN](https://link.segmentfault.com/?enc=xaJeywhCKy%2BkKhmMCrczGA%3D%3D.vFXXJzl9X9GoaMcZnoeb%2FeI97QPn9Kt9Ywgq4%2F55sAQFQlezhAiYkuNgqL%2FF8eUdGcauVQZ4Fu5PmLCokUJZ4w%3D%3D)），上述实现方法仅在 `chrome` 下有效，不过这种逻辑还是和 `js` 差别很大的

![](https://segmentfault.com/img/remote/1460000021385674)

> 虽然上述并没有 `text-align` 相关属性，不过 `chrome` 却已经支持了～

更好的实现方式
-------

### 1. 父级 text-align:center，子级 inline-block+text-align:left

首先来看看兼容性最好的实现方式

结构如下

```
<div class="content">
    <span class="text">这段文字能不能这样判断一下，当文字不足一行时，让它居中显示，当文字超过一行就让它居左</span>
</div>
```

样式如下

```
.content{
    text-align: center;
}
.text{
    display: inline-block;
    text-align: left;
}
```

这个方式最早是在[《CSS 世界》](https://link.segmentfault.com/?enc=WA75huuBvmKDkdIFXWb1Xw%3D%3D.gX4O0%2FUNiFKkzmarnHBZKPaogL1Vo75d7mD2fZBuZWE%3D)中学到的，

![](https://segmentfault.com/img/remote/1460000021385677)

大概原理如下：

> 对于一个元素，如果其 `display` 属性值是 `inline-block`，那么其宽度由内部元素决定，但永远小于 “包含块” 容器的尺寸，也就是 “包裹性（shrink-to-fit）”

可能这样描述的不够直观，来上述的案例简单来讲

*   当文本比较少时，`.text` 的宽度跟随文本，然后我们可以使用父级 `text-align:center` 来使一个 `inline-block` 元素居中，所以可以满足单行文本居中的效果，
*   当文本比较多时，`.text` 的宽度跟随父级容器，由于 `text-align:center` 会继承下去，所以在`.text` 上修复一下即可

[See the Pen](https://codepen.io/xboxyan/pen/QWwvRBm)

兼容性一级棒～

### 2.width:fit-content+margin:auto

上述方式是通过父级 `text-align:center` 来实现 `inline-block` 居中的，很巧妙，但是额外增加了标签，因为 `inline-block` 元素无法本身居中的。

块级 `block` 元素可以在设置宽度后直接通过 `margin:0 auto` 来实现居中，但是必须指明宽度，不然就水平填充了，这两者的关系很微妙，有没有什么办法能够让块级 `block` 元素的宽度像 `inline-block` 元素跟随内部元素呢？

答案就是 `width:fit-content`，详细可参考[这篇文章](https://link.segmentfault.com/?enc=WmXUI2JIORAvpea2ZuHA%2BQ%3D%3D.z46PYRZgY6NSmCxgu5bp%2FiP31gvJM%2BwrqkBL9ta2k0nstmtypZ223%2FEZ6q0xh274ZXU5KKsope%2FX5TVnFh9WZDhtJR57pnCxud6WoRLqc%2F4rcWnP%2BLzVCJBZwRjGAWZc)

> `width:fit-content` 可以实现元素收缩效果的同时，保持原本的 `block` 水平状态，于是，就可以直接使用 `margin:auto` 实现元素向内自适应同时的居中效果了。

下面的实现方式均只需要单层标签

```
<p class="text">这段文字能不能这样判断一下，当文字不足一行时，让它居中显示，当文字超过一行就让它居左</p>
```

```
.text{
    width: fit-content;
    width: -moz-fit-content;//火狐需要-moz-前缀
    margin: 0 auto;
}
```

[See the Pen](https://codepen.io/xboxyan/pen/QWwvRRB) 点击预览

当然，这种特性 `IE` 肯定是不支持的～

![](https://segmentfault.com/img/remote/1460000021385676)

### 3.position:relative+transform

仍需设置 `display:inline-block` 来实现自适应，然后配合 `transform` 来实现水平方向居中效果，实现也很简洁～

```
.text{
    display: inline-block;
    position: relative;
    left: 50%;
    transform: translateX(-50%);
}
```

[See the Pen](https://codepen.io/xboxyan/pen/QWwgWWV) 点击预览

### 4.display:table+margin:auto

前一种方式 `width:fit-content` 很有效，`IE` 不支持怎么办呢？其实默认 `display` 已经有这种特性了，当 `display` 属性值是 `table`，元素会表现出和 `width:fit-content` 的效果，既支持宽度跟随内部元素，又支持水平方向上 `margin` 居中

```
.text{
    display: table;
    margin: 0 auto;
}
```

[See the Pen](https://codepen.io/xboxyan/pen/PowmrYO) 点击预览

`IE8` 也完美支持～

![](https://segmentfault.com/img/remote/1460000021385678)

### 5.flex 和 grid 实现

对于 `flex` 和 `grid` 来说，实现这样一个效果还是挺容易的。

在 `flex` 容器中，所有子项成为弹性项，包括纯文本节点（匿名盒子），就好像包裹了一层，所以很容易通过 `justify-content: center` 实现居中，同时（匿名盒子）也跟随文本自适应宽度，当超过一行时，就按照默认的文本对齐方式。

`grid` 同理，只不过对齐方式需要通过 `justify-items: center`。

*   `flex` 实现

```
.text{
    display: flex;
    justify-content: center;
}
```

[See the Pen](https://codepen.io/xboxyan/pen/oNgWKzy) 点击预览

*   `grid` 实现

```
.text{
    display: grid;
    justify-items: center;
}
```

[See the Pen](https://codepen.io/xboxyan/pen/XWJRvNg) 点击预览

相对于 `flex`，`grid` 的兼容性要差一些，所以尽量选取 `flex` 方式，至少移动端和 `IE10`（需要 `-ms-`）是没问题的

### 6.float 实现

本以为 `float` 实现不了的，感谢[林小志](https://segmentfault.com/u/linxz)提供了 `float` 居中的实现方法，大致原理如下：本身 `float` 元素是具备包裹特性的，主要难点在于如何居中，毕竟没有 `float:center` 这种写法，这里主要用到两层标签，利用 `position:relative;left:50%` 正负抵消来实现

```
.content{
    position: relative;
    float: left;
    left: 50%;/**父级设置50%**/
}
.text{
    position: relative;
    float: left;
    left: -50%;/**子级设置-50%**/
}
```

[See the Pen](https://codepen.io/xboxyan/pen/KKwqKMJ) 点击预览

略微繁琐一点，不过也不失为一种方法，兼容性也极好

小结
--

上述一共列举了 8 种实现方式，当然第一种属于实验性质的，兼容性少的可怜，但也不失为一种思路。怎么想到这些方法呢？

第一就是联想。比如上述提到了自适应（简单来讲就是尺寸由内容决定），我就想哪些可以实现自适应呢？除了 `inline-block`，还有 `float`、`position:absolute`、`display:table` 等... ~首先 `float` 就排除了，元素设置了 `float` 后，整体居中其实是件麻烦的事，几乎不可能~（经过试验，可以实现）。`position:absolute` 还是挺有希望的，借助 `left:50%;transform:translateX(-50%)` 可以实现居中效果， 尝试了一番，发现宽度无法自适应父级宽度，同样失败（说不定可以，只是没有想到）~~ 最后选择了 `diaplay:table`，也算是循序渐进。`flex` 和 `grid` 就更不用说了，天然就是为弹性布局而生了，实现这类效果不奇怪。

第二还是基础。`CSS` 属性可就那么多，那只是停留在表面，很多看起来不相关的属性在整个体系中又会有些微妙的关系，比如上面的 `width:fill-content`，单独看这个肯定很鸡肋，完全可以用 `inline-block` 来代替，但是他却可以让一个普通的 `div` 元素具备 `inline-block` 的特性，不得不佩服 `CSS` 的设计～（肯定有设计人员参与）

前一段时间在思考做一个可视化编辑工具，希望可以通过一些属性，就像 `photoshop` 那样，直接作出一个页面来，想想看，发现只能作出最最基本的样式，也就颜色，大小什么的，如果要做成本文这样一个效果，八成是做不了的，除了本身是做开发，别人怎么可能知道这样设置呢？可视化编辑工具的道路还很长很长，所以做前端的也无需担心被其他什么 “一键生成工具” 给取代了～

![](https://segmentfault.com/img/remote/1460000021385679)

各位小伙伴如果还有其他实现方式可在下方留言评论，如果文章有错误请及时指出，谢谢～
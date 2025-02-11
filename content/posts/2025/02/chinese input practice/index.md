---
title: 中文输入实践
date: 2025-02-09T12:31:52+08:00
draft: false
tags: [neovim, chinese, spellcheck, editor, copywriting, linter, IME]
---

参考：

- [neo451/nvim-zh: neovim 中文输入改进计划](https://github.com/neo451/nvim-zh)
- [常用 Obsidian 处理中文长文？试试这些大幅提升体验的插件和代码片段](https://sspai.com/post/69628)

## 输入法

### vim 自动切换中英模式

Vim/Neovim 下输入中文最大的痛，就是在 Normal 模式下，需要频繁从中文模式切换到英文模式，来输入 Vim 的各种命令。

参考：

- [如何让 Neovim 中文输入时自动切换输入法](https://jdhao.github.io/2021/02/25/nvim_ime_mode_auto_switch/)
- [解决 Windows 下 (Neo)Vim 中文输入法的切换问题](https://www.cnblogs.com/tuilk/p/16421831.html)

#### Rime 输入法

使用 Rime 输入法提供 vim_mode 配置在 vim insert 模式使用`Esc`,`<C-[>`切换到 Normal 模式时变为 ascii 输入，参考[Weasel-定制化 应用设置](https://github.com/rime/weasel/wiki/Weasel-%E5%AE%9A%E5%88%B6%E5%8C%96#%E5%BA%94%E7%94%A8%E8%AE%BE%E7%BD%AE)和[feat: vim_mode in app_options #1047](https://github.com/rime/weasel/pull/1047)自动切换。

```yaml
# weasel.yaml
app_options:
  cmd.exe:
    ascii_mode: true
  conhost.exe:
    ascii_mode: true
  firefox.exe:
    inline_preedit: true
  gvim.exe:
    ascii_mode: true
    vim_mode: true
```

注意：在 vim 模式中如果在候选面板中键入`<C-[>`会导致清屏且切换为英文输入法，可能会造成麻烦，参考[gvim 进入退出插入模式时，无法禁用小狼毫自动切换 ascii_mode #1450](https://github.com/rime/weasel/issues/1450)

## 中文分词

在 nvim 中使用 w/b 等移动光标时对于中文来说，无法像英文一样以单词为单位移动，而是所有连续的中文为一个单位，移动非常不方便

[kkew3/jieba.vim](https://github.com/kkew3/jieba.vim) 相比于[neo451/jieba.nvim](https://github.com/neo451/jieba.nvim)更快且更稳定，但目前对于 nvim 的支持不够，需要通过[neovim/pynvim](https://github.com/neovim/pynvim)才能工作

参考：

- [neovim provider-python](https://neovim.io/doc/user/provider.html#provider-python)
- [Setting up Python for Neovim](https://github.com/deoplete-plugins/deoplete-jedi/wiki/Setting-up-Python-for-Neovim)
- [Automating pynvim Installation in Neovim](https://kevinmorio.com/posts/2023/10/29/automating-pynvim-installation-in-neovim.html)
- [vim/nvim 中文分词插件 jieba.vim](https://kkew3.github.io/2024/11/10/jieba-vim.html)
- [# Neovim as a markdown editor](https://mambusskruj.github.io/posts/pub-neovim-for-markdown/)

## 中英文排版

安装[hotoo/pangu.vim](https://github.com/hotoo/pangu.vim)

参考：

- [中文文案排版指北](https://github.com/sparanoid/chinese-copywriting-guidelines)
- [vim 里自动更新 markdown 格式](https://aisensiy.me/auto-update-content-in-markdown/)

### autocorrect

最近发现[huacnlee/autocorrect](https://github.com/huacnlee/autocorrect)更好用，同时提供 LSP 功能，但未提供 nvim 插件

#### 不支持 markdown 链接语法

对于 md 链接为中文时不会添加空格导致观感不佳，参考 [[Feature Request] 链接语法 config/flag #178](https://github.com/huacnlee/autocorrect/issues/178) 目前不支持对这种情况添加配置，需要主动添加空格。

### zhlint

[zhlint-project/zhlint: A linting tool for Chinese language](https://github.com/zhlint-project/zhlint) 也支持检查修复中文排版，但初步体验下来没发现比 autocorrect 更好，链接语法也不能添加空格

## 拼写检查

- [crate-ci/typos: Source code spell checker](https://github.com/crate-ci/typos)
- [codespell-project/codespell: check code for common misspellings](https://github.com/codespell-project/codespell)

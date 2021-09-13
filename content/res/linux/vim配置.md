# vim配置

## sudo无法使用配置

在使用`sudo vim`时配置无效

## yaml文件编辑问题

在yaml编辑时使用tab时默认缩进为8，不符合yaml文件格式，且在`ctrl+v`多行插入`#`时可能出现自动缩进。在使用下面的命令解决：

```sh
# raspi4 `#`自动缩进 无法无效
# autocmd FileType yaml setlocal sw=2 ts=2 et ai

# 在raspi4 ubuntu20.04上/etc/vim/vimrc生效
autocmd FileType yaml setlocal ts=2 sts=2 sw=2 expandtab
```

在直接粘贴时也会导致格式混乱多缩进和空格，可以在vim中使用粘贴模式命令解决`:set paste`

## 完整配置

```vim
"--外观--"

"显示行号"
set number
"set relativenumber
"光标所在的当前行高亮
set cursorline
"设置行宽，即一行显示多少个字符"
set textwidth=80
"显示括号匹配"
set showmatch
"自动折行，即太长的行分成几行显示。"
set wrap
"只有遇到指定的符号（比如空格、连词号和其他标点符号），才发生折行。也就是说，不会在单词内部折行。"
set linebreak
"使用 utf-8 编码。"
set encoding=utf-8

"语法高亮"
syntax on
"在底部显示，当前处于命令模式还是插入模式"
set showmode
"命令模式下，在底部显示，当前键入的指令"
set showcmd
"开启文件类型检查，并且载入与该类型对应的缩进规则"
filetype indent on

"--缩进--"

"自动缩进"
set autoindent
"按下 Tab 键时，Vim 显示的空格数。"
set tabstop=4
"将tab转成空格"
set expandtab
"Tab 转为多少个空格"
set softtabstop=4
autocmd FileType yaml setlocal sw=2 ts=2 et ai
```

参考：

- [Vim 配置入门](http://www.ruanyifeng.com/blog/2018/09/vimrc.html)
- [Vim入门级基础配置](https://segmentfault.com/a/1190000016330314)
- [Wrong indentation when editing Yaml in Vim](https://stackoverflow.com/a/37488992)
- [Vim 从入门到精通](https://github.com/wsdjeg/vim-galore-zh_cn)

## 常用操作

### [How to duplicate a whole line in Vim?](https://stackoverflow.com/a/73357/8566831)

```vim
:yy | Y
:p | P
```

### 使用系统clipboard

- 复制到系统剪切板`"+y`
- 从系统剪切板中粘贴`"+p`
- 剪切单行`dd`，复制单行`yy`，粘贴`p`
参考：

- [How to copy to clipboard in Vim?](https://stackoverflow.com/a/3961954/8566831)
- [How can I copy text to the system clipboard from Vim?](https://vi.stackexchange.com/a/96)
- [How to cut an entire line in vim and paste it?](https://stackoverflow.com/a/8773315/8566831)

### 替换字符

% => run this command on all lines. g => match multiple occurences in the same line.

`:%s/foo/bar/g`

Change each 'foo' to 'bar' for all lines from line 6 to line 10 inclusive.

`:6,10s/foo/bar/g`

Replace all occurrences of str1 with str2 in certain line:

`:s/str1/str2/g`

参考：

- [Find and replace strings in vim on multiple lines](https://stackoverflow.com/a/19995072/8566831)
- [How to search and replace in current line only?](https://stackoverflow.com/a/46181589/8566831)

### 移动光标word

In Vim's normal mode:

- `e` goes to the end of the next word
- `w` goes to the beginning of the next word
- `b` goes to the beginning of the previous word

参考：

- [In Vim/Vi, how do you move the cursor to the end of the previous word?](https://stackoverflow.com/questions/5125270/in-vim-vi-how-do-you-move-the-cursor-to-the-end-of-the-previous-word)

### 文本对象

- 删除括号：`c"^R"`。仅对`"`有用

  That is, c to move the selected text to the @” register and start insert mode, " to insert one double quote, Control-R+” to insert the contents of the @” register, and " again to insert the end quote.
- 删除括号：`di"hP2x`

参考：

- [What Vim command(s) can be used to quote/unquote words?](https://stackoverflow.com/a/2148055/8566831)
- [surround.vim](https://github.com/tpope/vim-surround)
- [How do I put quotes around a selection in Vim?](https://www.quora.com/How-do-I-put-quotes-around-a-selection-in-Vim)

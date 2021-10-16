# zsh配置

使用zsh包管理器 [antigen](https://github.com/zsh-users/antigen) 比ohmyzsh更方便

## 安装

```bash
curl -L git.io/antigen > antigen.zsh
```

或者[Installation](https://github.com/zsh-users/antigen/wiki/Installation)

简单配置在`$HOME/.zshrc`中

```zsh
source /path-to-antigen/antigen.zsh

# Load the oh-my-zsh's library.
antigen use oh-my-zsh

# Bundles from the default repo (robbyrussell's oh-my-zsh).
antigen bundle git
antigen bundle heroku
antigen bundle pip
antigen bundle lein
antigen bundle command-not-found

# Syntax highlighting bundle.
antigen bundle zsh-users/zsh-syntax-highlighting

# Load the theme.
antigen theme robbyrussell

# Tell Antigen that you're done.
antigen apply
```

如果使用ubuntu apt安装`sudo apt install zsh-antigen`可能会出现问题[antigen.zsh:748: command not found: -antigen-env-setup in Ubuntu 18.04 LTS Bionic Beaver #659](https://github.com/zsh-users/antigen/issues/659)，解决方式是不使用ubuntu的包，手动写入

```
/usr/share/zsh-antigen/antigen.zsh:748: command not found: -antigen-env-setup
Antigen: Unknown command: use
Antigen: Unknown command: bundle
Antigen: Unknown command: bundle
Antigen: Unknown command: bundle
Antigen: Unknown command: bundle
Antigen: Unknown command: bundle
Antigen: Unknown command: bundle
Antigen: Unknown command: theme
Antigen: Unknown command: apply
```

## alias

查看当前alias

```bash
$ alias
-='cd -'
...=../..
....=../../..
.....=../../../..
......=../../../../..
1='cd -'
2='cd -2'
# ...

$ alias | grep -E "'ls"
l='ls -lah'
la='ls -lAh'
ll='ls -lh'
ls='ls --color=tty'
lsa='ls -lah'
```

参考：[Cheatsheet](https://github.com/ohmyzsh/ohmyzsh/wiki/Cheatsheet)

## plugins

```bash
antigen bundles <<EOBUNDLES
    # Bundles from the default repo (robbyrussell's oh-my-zsh).
    # antigen bundle git
    git
    heroku
    pip
    lein
    command-not-found
    zsh-users/zsh-syntax-highlighting
    # custom
    zsh-users/zsh-autosuggestions
    z
    extract
    mvn
    docker
    colorize
    safe-paste
    gitignore
    rustup
    cargo
    colored-man-pages
    cp
    ubuntu
    alias-finder
EOBUNDLES
```

- [git](https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/git)

The git plugin provides many aliases and a few useful functions.

- [cp](https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/cp)

提供一个 cpv 命令，这个命令使用 rsync 实现带进度条的复制功能。

```zsh
$ cpv nohup.out Desktop/
sending incremental file list
nohup.out
         18.99K 100%    0.00kB/s    0:00:00 (xfr#1, to-chk=0/1)
```

## bindkey

terminal快捷键控制

列出当前关联所有的key

```bash
$ bindkey
"^@" set-mark-command
"^A" beginning-of-line
"^B" backward-char
# ...
```

### home/end响应修复

写入shell环境：

```zsh
bindkey  "^[[H"   beginning-of-line
bindkey  "^[[F"   end-of-line
```

参考：[Fix key settings (Home/End/Insert/Delete) in .zshrc when running Zsh in Terminator Terminal Emulator](https://stackoverflow.com/questions/8638012/fix-key-settings-home-end-insert-delete-in-zshrc-when-running-zsh-in-terminat)

### up/down上下前缀历史搜索

```zsh
bindkey "^[[A" history-beginning-search-backward
bindkey "^[[B" history-beginning-search-forward
```

```zsh
bindkey '^[[A' up-line-or-search
bindkey '^[[B' down-line-or-search
```

[ZSH: search history on up and down keys?](https://unix.stackexchange.com/a/100860)

### ctrl+U删除光标前字符

```zsh
bindkey "^U" backward-kill-line
```

[Which shortcut in Zsh does the same as Ctrl-U in Bash?](https://stackoverflow.com/questions/3483604/which-shortcut-in-zsh-does-the-same-as-ctrl-u-in-bash)

### ctrl+backspace删除前一个单词

```sh
bindkey '^H' backward-kill-word
```

参考：[In zsh how do you bind Ctrl+backspace to delete the previous word?](https://stackoverflow.com/a/21252464)

## cowsay欢迎消息

在shell启动时打印消息：

```zsh
 ____________________________
< Just to have it is enough. >
 ----------------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||

# navyd @ desktop-navyd in ~/Workspaces/projects/blog-resources on git:master x [17:44:33] 
$ 
```

### fortune

安装`fortune`和`cowsay`后在`$HOME/.zshrc`最后加入：

```zsh
# 显示随机名言
fortune | cowsay -f "$(find /usr/share/cowsay/cows/ | shuf -n 1)"
```

参考：[cowsay command line with random cowfile](https://askubuntu.com/a/514134)

### rand-quote plugin

zsh 内置插件`rand-quote`：Displays a random quote taken from quotationspage.com。在`$HOME/.zshrc`中加入

```zsh
antigen bundle rand-quote
```


由于quote要从网络中加载，速度有点慢，影响shell加载速度，可放到后台运行，在`$HOME/.zshrc`最后加入：

```zsh
quote | cowsay &
```

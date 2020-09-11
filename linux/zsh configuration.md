# zsh配置

## 安装

```bash
sudo apt-get install zsh
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
git clone https://github.com/zsh-users/zsh-autosuggestions "${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions"
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git "${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting"
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
plugins=(
    git
    z
    extract
    zsh-autosuggestions
    zsh-syntax-highlighting
    mvn docker
    colorize
    safe-paste
    gitignore
    rustup
    cargo
    colored-man-pages
    rand-quote
    cp
)
```

### [git](https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/git)

The git plugin provides many aliases and a few useful functions.

### [cp](https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/cp)

提供一个 cpv 命令，这个命令使用 rsync 实现带进度条的复制功能。

```zsh
$ cpv nohup.out Desktop/
sending incremental file list
nohup.out
         18.99K 100%    0.00kB/s    0:00:00 (xfr#1, to-chk=0/1)
```

## bindkey

列出当前关联所有的key

```bash
$ bindkey
"^@" set-mark-command
"^A" beginning-of-line
"^B" backward-char
# ...
```

### home/end

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

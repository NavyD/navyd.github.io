# gui

## GWSL

### gui显示中文字体与输入法

```sh
sudo apt-get install fonts-noto fcitx-pinyin fcitx-table-wbpy
```

```sh
export XMODIFIERS=@im=fcitx
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
```

参考：

* [wsl-tutorial](https://github.com/QMonkey/wsl-tutorial/blob/master/README.wsl2.md)

---
title: "使用cargo安装rust二进制文件"
date: 2021-10-01T01:21:51+08:00
draft: false
tags: [rust, cargo]
---

`cargo install`管理cargo本地的binary类型文件：bin, example targets

## 方法

### install

```bash
cargo install evcxr
```

### 检查更新

cargo当前未提供直接的命令对已安装的bin检查版本更新，但是提供了一个`cargo search`命令，可以列出bin的最新版本，与install命令组合可以查看是否可以更新了

```bash
$ cargo search --limit 1 evcxr
evcxr = "0.11.0"    # An Evaluation Context for Rust
... and 11 crates more (use --limit N to see more)

$ cargo install --list | grep evcxr
evcxr v0.10.0:
```

另外，cargo可以通过安装扩展命令[cargo-update](https://github.com/nabijaczleweli/cargo-update)更新

```bash
$ cargo install cargo-update
#...

$ cargo install-update -l evcxr
    Updating registry 'https://rsproxy.cn/crates.io-index'

Package  Installed  Latest   Needs update
evcxr    v0.10.0    v0.11.0  Yes
```

参考：

* [Does cargo install have an equivalent update command?](https://stackoverflow.com/questions/34484361/does-cargo-install-have-an-equivalent-update-command)
* [cargo-install](https://doc.rust-lang.org/cargo/commands/cargo-install.html)
* [cargo-search](https://doc.rust-lang.org/cargo/commands/cargo-search.html)

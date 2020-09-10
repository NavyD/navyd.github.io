# rust installation

## wsl

```bash
$ curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 环境变量
# rust
export CARGO_HOME=$HOME/.cargo
export RUSTUP_HOME=$HOME/.rustup
export RUST_SRC_PATH=$HOME/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/src/rust/src/
# rustup mirrors
export RUSTUP_DIST_SERVER=https://mirrors.ustc.edu.cn/rust-static
export RUSTUP_UPDATE_ROOT=https://mirrors.ustc.edu.cn/rust-static/rustup
```

参考：[Getting started](https://www.rust-lang.org/learn/get-started)

### cargo mirror

编辑 `~/.cargo/config` 文件，添加以下内容：

```toml
[source.crates-io]
registry = "https://github.com/rust-lang/crates.io-index"
# 指定镜像
replace-with = 'sjtu'

# 清华大学
[source.tuna]
registry = "https://mirrors.tuna.tsinghua.edu.cn/git/crates.io-index.git"

# 中国科学技术大学
[source.ustc]
registry = "git://mirrors.ustc.edu.cn/crates.io-index"

# 上海交通大学
[source.sjtu]
registry = "https://mirrors.sjtug.sjtu.edu.cn/git/crates.io-index"
```

### linker 'cc' not found

```bash
sudo apt install build-essential
```

参考：[How do I fix the Rust error “linker 'cc' not found” for Debian on Windows 10?](https://stackoverflow.com/questions/52445961/how-do-i-fix-the-rust-error-linker-cc-not-found-for-debian-on-windows-10)

### cargo: Blocking waiting for file lock on the registry index

```bash
rm -rf ~/.cargo/registry/index/*
```

如果还不行则更换cargo mirrors

参考：[Cargo build hangs with “ Blocking waiting for file lock on the registry index” after building parity from source](https://stackoverflow.com/questions/47565203/cargo-build-hangs-with-blocking-waiting-for-file-lock-on-the-registry-index-a)

## vscode analyzer

安装rust std源码

```bash
rustup component add rust-src
```

参考：

- [User Manual](https://rust-analyzer.github.io/manual.html)

## zsh completions

安装rustup, cargo zsh命令补全

```bash
# ~/.oh-my-zsh/custom
$ mkdir -p $ZSH_CUSTOM/zsh-rustup-completions
$ echo 'fpath+="${0:h}' > $ZSH_CUSTOM/zsh-rustup-completions/rustup.plugin.zsh
$ rustup completions zsh > $ZSH_CUSTOM/zsh-rustup-completions/_rustup
$ rustup completions zsh cargo > $ZSH_CUSTOM/zsh-rustup-completions/_cargo
```

在`.zshrc`文件plugins中加入

```bash
plugins=(... rustup cargo)
```

参考：

- [RFC: add rustup completion to plugins #8072](https://github.com/ohmyzsh/ohmyzsh/issues/8072)
- [zsh-rustup-completion](https://github.com/pkulev/zsh-rustup-completion)

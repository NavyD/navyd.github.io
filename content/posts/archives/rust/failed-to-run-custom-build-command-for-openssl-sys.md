---
title: "Failed to Run Custom Build Command for openssl-sys"
date: 2021-10-17T16:19:48+08:00
draft: false
tags: [rust, cargo, ssl]
---

在编译reqwest一段简单的代码时出现`error: failed to run custom build command for openssl-sys v0.9.58`

```bash
$ cargo check
   Compiling libc v0.2.77
# ...
    Checking url v2.1.1
error: failed to run custom build command for `openssl-sys v0.9.58`

Caused by:
  process didn't exit successfully: `/home/navyd/Workspaces/projects/youdao-dict-export/target/debug/build/openssl-sys-bc6e4f996293b8bd/build-script-main` (exit code: 101)
  --- stdout
  cargo:rustc-cfg=const_fn
  cargo:rerun-if-env-changed=X86_64_UNKNOWN_LINUX_GNU_OPENSSL_LIB_DIR
  X86_64_UNKNOWN_LINUX_GNU_OPENSSL_LIB_DIR unset
  cargo:rerun-if-env-changed=OPENSSL_LIB_DIR
  OPENSSL_LIB_DIR unset
  cargo:rerun-if-env-changed=X86_64_UNKNOWN_LINUX_GNU_OPENSSL_INCLUDE_DIR
  X86_64_UNKNOWN_LINUX_GNU_OPENSSL_INCLUDE_DIR unset
  cargo:rerun-if-env-changed=OPENSSL_INCLUDE_DIR
  OPENSSL_INCLUDE_DIR unset
  cargo:rerun-if-env-changed=X86_64_UNKNOWN_LINUX_GNU_OPENSSL_DIR
  X86_64_UNKNOWN_LINUX_GNU_OPENSSL_DIR unset
  cargo:rerun-if-env-changed=OPENSSL_DIR
  OPENSSL_DIR unset
  cargo:rerun-if-env-changed=OPENSSL_NO_PKG_CONFIG
  cargo:rerun-if-env-changed=PKG_CONFIG
  cargo:rerun-if-env-changed=OPENSSL_STATIC
  cargo:rerun-if-env-changed=OPENSSL_DYNAMIC
  cargo:rerun-if-env-changed=PKG_CONFIG_ALL_STATIC
  cargo:rerun-if-env-changed=PKG_CONFIG_ALL_DYNAMIC
  cargo:rerun-if-env-changed=PKG_CONFIG_PATH_x86_64-unknown-linux-gnu
  cargo:rerun-if-env-changed=PKG_CONFIG_PATH_x86_64_unknown_linux_gnu
  cargo:rerun-if-env-changed=HOST_PKG_CONFIG_PATH
  cargo:rerun-if-env-changed=PKG_CONFIG_PATH
  cargo:rerun-if-env-changed=PKG_CONFIG_LIBDIR_x86_64-unknown-linux-gnu
  cargo:rerun-if-env-changed=PKG_CONFIG_LIBDIR_x86_64_unknown_linux_gnu
  cargo:rerun-if-env-changed=HOST_PKG_CONFIG_LIBDIR
  cargo:rerun-if-env-changed=PKG_CONFIG_LIBDIR
  cargo:rerun-if-env-changed=PKG_CONFIG_SYSROOT_DIR_x86_64-unknown-linux-gnu
  cargo:rerun-if-env-changed=PKG_CONFIG_SYSROOT_DIR_x86_64_unknown_linux_gnu
  cargo:rerun-if-env-changed=HOST_PKG_CONFIG_SYSROOT_DIR
  cargo:rerun-if-env-changed=PKG_CONFIG_SYSROOT_DIR
  run pkg_config fail: "Failed to run `\"pkg-config\" \"--libs\" \"--cflags\" \"openssl\"`: No such file or directory (os error 2)"

  --- stderr
  thread 'main' panicked at '

  Could not find directory of OpenSSL installation, and this `-sys` crate cannot
  proceed without this knowledge. If OpenSSL is installed and this crate had
  trouble finding it,  you can set the `OPENSSL_DIR` environment variable for the
  compilation process.

  Make sure you also have the development packages of openssl installed.
  For example, `libssl-dev` on Ubuntu or `openssl-devel` on Fedora.

  If you're in a situation where you think the directory *should* be found
  automatically, please open a bug at https://github.com/sfackler/rust-openssl
  and include information about your system as well as this message.

  $HOST = x86_64-unknown-linux-gnu
  $TARGET = x86_64-unknown-linux-gnu
  openssl-sys = 0.9.58


  It looks like you're compiling on Linux and also targeting Linux. Currently this
  requires the `pkg-config` utility to find OpenSSL but unfortunately `pkg-config`
  could not be found. If you have OpenSSL installed you can likely fix this by
  installing `pkg-config`.

  ', /home/navyd/.cargo/registry/src/mirrors.sjtug.sjtu.edu.cn-7a04d2510079875b/openssl-sys-0.9.58/build/find_normal.rs:157:5
  note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
warning: build failed, waiting for other jobs to finish...
error: build failed
```

代码

```rust
use std::collections::HashMap;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let resp = reqwest::get("https://httpbin.org/ip")
        .await?
        .json::<HashMap<String, String>>()
        .await?;
    println!("{:#?}", resp);
    Ok(())
}
```

cargo.toml依赖

```toml
[dependencies]
reqwest = { version = "0.10", features = ["json"] }
tokio = { version = "0.2", features = ["full"] }
```

## 解决方案

在[Crate openssl automatic](https://docs.rs/openssl/0.10.36/openssl/#automatic)中提到，在ubuntu中可以`sudo apt-get install pkg-config libssl-dev`安装依赖

参考：

- [Ubuntu 18: failed to run custom build command for `openssl-sys v0.9.39`](https://github.com/sfackler/rust-openssl/issues/1021#issuecomment-441387063)

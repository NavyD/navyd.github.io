# failed to run custom build command for openssl-sys

在编译reqwest一段简单的代码时出现`error: failed to run custom build command for openssl-sys v0.9.58`

```bash
$ cargo check
   Compiling libc v0.2.77
    Checking cfg-if v0.1.10
   Compiling autocfg v1.0.1
   Compiling proc-macro2 v1.0.21
   Compiling unicode-xid v0.2.1
   Compiling log v0.4.11
   Compiling syn v1.0.41
    Checking lazy_static v1.4.0
   Compiling pkg-config v0.3.18
   Compiling cc v1.0.60
    Checking fnv v1.0.7
   Compiling memchr v2.3.3
    Checking bytes v0.5.6
    Checking futures-core v0.3.5
    Checking slab v0.4.2
    Checking itoa v0.4.6
   Compiling pin-project-internal v0.4.23
    Checking arc-swap v0.4.7
   Compiling version_check v0.9.2
   Compiling bitflags v1.2.1
    Checking pin-project-lite v0.1.7
    Checking foreign-types-shared v0.1.1
   Compiling openssl v0.10.30
    Checking tinyvec v0.3.4
    Checking matches v0.1.8
   Compiling httparse v1.3.4
    Checking hashbrown v0.9.0
   Compiling serde v1.0.116
    Checking futures-task v0.3.5
   Compiling native-tls v0.2.4
    Checking futures-sink v0.3.5
    Checking pin-utils v0.1.0
    Checking try-lock v0.2.3
   Compiling ryu v1.0.5
    Checking openssl-probe v0.1.2
   Compiling encoding_rs v0.8.24
   Compiling serde_json v1.0.57
    Checking httpdate v0.3.2
    Checking tower-service v0.3.0
    Checking percent-encoding v2.1.0
    Checking dtoa v0.4.6
    Checking mime v0.3.16
    Checking ipnet v2.3.0
    Checking base64 v0.12.3
    Checking tracing-core v0.1.16
    Checking futures-channel v0.3.5
    Checking foreign-types v0.3.2
    Checking http v0.2.1
    Checking unicode-bidi v0.3.4
   Compiling indexmap v1.6.0
    Checking unicode-normalization v0.1.13
   Compiling unicase v2.6.0
    Checking tracing v0.1.19
    Checking want v0.3.0
   Compiling quote v1.0.7
   Compiling openssl-sys v0.9.58
   Compiling mime_guess v2.0.3
    Checking iovec v0.1.4
    Checking net2 v0.2.35
    Checking signal-hook-registry v1.2.1
    Checking num_cpus v1.13.0
    Checking socket2 v0.3.15
    Checking idna v0.2.0
    Checking mio v0.6.22
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

## 解法

```bash
sudo apt install pkg-config
```

参考：

- [Ubuntu 18: failed to run custom build command for `openssl-sys v0.9.39`](https://github.com/sfackler/rust-openssl/issues/1021#issuecomment-441387063)

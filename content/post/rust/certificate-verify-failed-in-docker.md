---
title: "Certificate Verify Failed in Docker"
date: 2022-05-01T12:26:57+08:00
tags: [rust, docker]
draft: false
---

在docker中运行编译好的bin时出现ssl certificate verify failed问题：

```sh
$ binaries
# ...
[2022-05-01T04:25:01Z ERROR binaries] failed to install: error sending request for url (https://api.github.com/repos/ClementTsang/bottom/releases/latest): error trying to connect: error:1416F086:SSL routines:tls_process_server_certificate:certificate verify failed:../ssl/statem/statem_clnt.c:1913: (unable to get local issuer certificate)
failed to run: install has 1 failed tasks
```

<!--more-->

下面是源码

```rust
#[tokio::main]
async fn main() {
    let body = reqwest::ClientBuilder::new()
        .build()
        .unwrap()
        // .get("https://api.github.com/repos/Dreamacro/clash/releases/latest")
        .get("https://www.baidu.com")
        .send()
        .await
        .unwrap()
        .text()
        .await
        .unwrap();
    println!("{}", body);
}
```

Cargo.toml配置

```toml
[package]
name = "atest"
version = "0.1.0"
edition = "2021"
# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html
[dependencies]
reqwest = "0.11.10"
tokio = { version = "1.18.1", features = ["macros", "rt-multi-thread"] }
```

调试时返回的Err：

```sh
thread 'main' panicked at 'called `Result::unwrap()` on an `Err` value: reqwest::Error { kind: Request, url: Url { scheme: "https", cannot_be_a_base: false, username: "", password: None, host: Some(Domain("www.baidu.com")), port: None, path: "/", query: None, fragment: None }, source: hyper::Error(Connect, Ssl(Error { code: ErrorCode(1), cause: Some(Ssl(ErrorStack([Error { code: 337047686, library: "SSL routines", function: "tls_process_server_certificate", reason: "certificate verify failed", file: "../ssl/statem/statem_clnt.c", line: 1913 }]))) }, X509VerifyResult { code: 20, error: "unable to get local issuer certificate" })) }', src/main.rs:55:6
```

## 分析

开始google时以为是docker内部时区的问题，尝试设置docker容器时区。获取当前时区`cat /etc/timezone`，但仍然没有任何作用。

```yaml
version: "3"

services:
  serviceA:
    # environment:
    #   TZ: "Asia/Shanghai"
    volumes:
      - "/etc/localtime:/etc/localtime:ro"
```

未配置时区尝试直接在rust docker镜像[rust:1.60](https://hub.docker.com/_/rust/)中运行是正常的

### openssl

想到reqwest依赖openssl，可能是在docker容器中未安装openssl报错：`atest: error while loading shared libraries: libssl.so.1.1: cannot open shared object file: No such file or directory`

```dockerfile
FROM rust:1.60 as builder
WORKDIR /usr/src/atest
COPY . .
RUN cargo install --path .

FROM ubuntu:20.04
RUN apt-get update && apt-get install -y openssl && rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/local/cargo/bin/atest /usr/local/bin/atest
ENTRYPOINT [ "atest" ]
```

尝试运行后出现问题X509VerifyResult。另外在[openssl Automatic](https://docs.rs/openssl/0.10.40/openssl/index.html#automatic)中安装`pkg-config libssl-dev`也出现一样的问题：

```sh
$ docker run --rm navyd/atest
thread 'main' panicked at 'called `Result::unwrap()` on an `Err` value: reqwest::Error { kind: Request, url: Url { scheme: "https", cannot_be_a_base: false, username: "", password: None, host: Some(Domain("www.baidu.com")), port: None, path: "/", query: None, fragment: None }, source: hyper::Error(Connect, Ssl(Error { code: ErrorCode(1), cause: Some(Ssl(ErrorStack([Error { code: 337047686, library: "SSL routines", function: "tls_process_server_certificate", reason: "certificate verify failed", file: "../ssl/statem/statem_clnt.c", line: 1913 }]))) }, X509VerifyResult { code: 20, error: "unable to get local issuer certificate" })) }', src/main.rs:10:10
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
```

在这里[Docker container always shows ssl connection error](https://stackoverflow.com/questions/48946036/docker-container-always-shows-ssl-connection-error)发现可能是ssl ca证书的问题，尝试安装`ca-certificates`后正常运行了

```dockerfile
FROM ubuntu:20.04
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y openssl ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/local/cargo/bin/atest /usr/local/bin/atest
ENTRYPOINT [ "atest" ]
```

另外，使用docker-compose时有一个坑点，docker build的镜像构建后不会被docker-compose使用，而是使用之前的缓存，如果`docker-compose run atest`未运行build，可能不会更新新的镜像

### rustls

在reqwest中提供了features可以不使用openssl，默认的feature为`default-tls=["hyper-tls", "native-tls-crate", "__tls", "tokio-native-tls"]`。如果要使用rustls，需要禁用默认feature，否则将会导致在依赖中还存在openssl依赖：

```sh
$ cargo tree
├── reqwest v0.11.10
│   ├── hyper v0.14.18
│   ├── hyper-rustls v0.23.0
│   ├── hyper-tls v0.5.0
│   │   ├── hyper v0.14.18 (*)
│   │   ├── native-tls v0.2.10
│   │   │   ├── log v0.4.17 (*)
│   │   │   ├── openssl v0.10.40
│   │   │   │   ├── openssl-macros v0.1.0 (proc-macro)
│   │   │   │   └── openssl-sys v0.9.73
│   │   │   │       └── libc v0.2.125
│   │   │   ├── openssl-probe v0.1.5
│   │   │   └── openssl-sys v0.9.73 (*)
```

禁用默认feature，此时才没有了openssl依赖，[When rustls-tls feature is enabled, native-tls dependencies are still built.](https://github.com/seanmonstar/reqwest/issues/1099#issuecomment-739417517)

```toml
reqwest = { version = "0.11.10", features = ["rustls-tls"], default-features = false }
```

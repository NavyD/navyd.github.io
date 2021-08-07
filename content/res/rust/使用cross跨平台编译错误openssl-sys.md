# 使用cross跨平台编译错误openssl-sys

在[Remove OpenSSL #229](https://github.com/rust-embedded/cross/issues/229)中提到cross已移除对openssl的支持，但是部分依赖opensys无法编译`failed to run custom build command for openssl-sys v0.9.60`

使用cross跨平台编译有两种方式

* cargo install --version 0.1.16 cross
* 定制docker image使用openssl

## 定制docker image使用openssl

在项目根目录上创建`Cross.toml`并写入：

```yaml
[target.aarch64-unknown-linux-musl]
# docker image name
image = "navyd/aarch64:sec"
```

新建docker空文件夹中写入`Dockerfile`：

```dockerfile
FROM rustembedded/cross:aarch64-unknown-linux-musl-0.2.1

COPY openssl.sh /
RUN bash /openssl.sh linux-aarch64 aarch64-linux-musl-

ENV OPENSSL_DIR=/openssl \
    OPENSSL_INCLUDE_DIR=/openssl/include \
    OPENSSL_LIB_DIR=/openssl/lib \
```

下载[`openssh.sh`](https://github.com/rust-embedded/cross/blob/c183ee37a9dc6b0e6b6a6ac9c918173137bad4ef/docker/openssl.sh)到docker文件夹

进入docker文件夹中运行docker命令：`docker build -t navyd/aarch64:sec  .`

参考：

* [how to support openssl](https://github.com/rust-embedded/cross/issues/229#issuecomment-748500115)
* [cross Configuration](https://github.com/rust-embedded/cross#Configuration)

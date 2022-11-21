---
title: "Docker Multi Platform Build"
date: 2021-08-08T20:07:10+08:00
draft: true
tags: [docker]
---

## github actions

<!-- TODO -->

## docker-compose build for multi-stage

在使用docker-compose up 首次启动需要multi-stage build的容器时可能会出现问题

```yml
version: "3.8"
services:
  nginx:
    build:
      context: .
      dockerfile: ./rest-server.Dockerfile
    container_name: nginx
    restart: unless-stopped
    network_mode: host
    volumes:
      - nginx-data:/etc/nginx
```

```dockerfile
FROM debian:11-slim as base
ENV APT_MIRROR="http://mirrors.163.com" \
    DEBIAN_FRONTEND="noninteractive"
RUN set -eu; \
    sed -ri "s@^([^#]*)http[s]?://[^/\.]+(\.[^/\.]+)+@\1${APT_MIRROR}@g" /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y unzip curl xz-utils && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p "/public"

FROM base as base-ariang
ENV ARIANG_VERSION='1.2.5'
RUN set -eu; \
    curl -o ariang.zip -L "https://github.com/mayswind/AriaNg/releases/download/${ARIANG_VERSION}/AriaNg-${ARIANG_VERSION}.zip" && \
    unzip ariang.zip -d "/public" && \
    rm ariang.zip

FROM base as base-yacd
ENV YACD_VERSION='0.3.6'
RUN set -eu; \
    curl -L "https://github.com/haishanh/yacd/releases/download/v${YACD_VERSION}/yacd.tar.xz" | \
    tar -xJf - --strip-components 1 -C "/public"

FROM nginx:1.23-alpine
COPY --from=base-ariang "/public" "/var/www/a/public"
COPY --from=base-yacd "/public" "/var/www/c/public"
```

```bash
$ docker-compose up nginx
[+] Building 0.3s (4/4) FINISHED                                                                         
 => [internal] load build definition from nginx.Dockerfile                                          0.0s
 => => transferring dockerfile: 1.15kB                                                              0.0s
 => [internal] load .dockerignore                                                                   0.0s
 => => transferring context: 2B                                                                     0.0s
 => CANCELED [internal] load metadata for docker.io/library/debian:11-slim                          0.1s
 => ERROR [internal] load metadata for docker.io/library/nginx:1.23-alpine                          0.1s
------
 > [internal] load metadata for docker.io/library/nginx:1.23-alpine:
------
failed to solve: rpc error: code = Unknown desc = failed to solve with frontend dockerfile.v0: failed to create LLB definition: unexpected status code [manifests 1.23-alpine]: 403 Forbidden
```

在这里[DOCKER_BUILDKIT=0 is not applied by docker-compose build #8649](https://github.com/docker/compose/issues/8649#issuecomment-923816281)提到docker-compose v2 build总是使用buildkit构建

> Compose V2 always uses BuildKit by design.
> If Buildkit can't build some Dockerfile, either there's good reasons, otherwise it has to be fixed.

默认的docker build是没有使用buildkit的，可以通过这里[Build images with BuildKit](https://docs.docker.com/develop/develop-images/build_enhancements/)配置启用buildkit构建

## 方案

不建议使用docker-compose build镜像，而是build到docker registry即docker hub上再在compose文件中拉取

### 使用buildkit

TODO

### 禁用buildkit

使用环境变量禁止docker-compose build使用buildkit构建

```bash
$ DOCKER_BUILDKIT=0 COMPOSE_DOCKER_CLI_BUILD=0 docker compose up nginx
Sending build context to Docker daemon  7.788MB
Step 1/16 : FROM debian:11-slim as base
...
Removing intermediate container 6ac3d0901c6a
 ---> 351b817b0a40
Successfully built 351b817b0a40
Successfully tagged rpi4-nginx:latest
```

## 注意

有些地方可能会出现各种问题

### debian镜像源

在国内debian下载安装软件包时通常会使用国内的代理源替换debian.org，但是在使用docker多平台构建时要注意使用的镜像源是否支持对应的平台，否则就会出现无法找到对应包的问题。

如[网易Debian 镜像使用帮助 mirrors.163.com](https://mirrors.163.com/.help/debian.html)中是不支持armv7的，导致构建出错

```bash
$ docker buildx build --platform linux/arm/v7 -t navyd/nginx --push -f nginx.Dockerfile .
# ...
 => [stage-3 1/3] FROM docker.io/library/nginx:1.23-alpine@sha256:b87c350e6c69e0dc7069093dcda226c4430f3836682af4f649f2af9e9b5f1c74                                                                                              0.2s
 => => resolve docker.io/library/nginx:1.23-alpine@sha256:b87c350e6c69e0dc7069093dcda226c4430f3836682af4f649f2af9e9b5f1c74                                                                                                      0.1s
 => ERROR [base 2/2] RUN set -eu;     sed -ri "s@^([^#]*)http[s]?://[^/\.]+(\.[^/\.]+)+@\1http://mirrors.163.com@g" /etc/apt/sources.list &&     apt-get update &&     apt-get install -y unzip curl xz-utils &&     rm -rf /v  5.0s
------                                                                                                                                                                                                                               
 > [base 2/2] RUN set -eu;     sed -ri "s@^([^#]*)http[s]?://[^/\.]+(\.[^/\.]+)+@\1http://mirrors.163.com@g" /etc/apt/sources.list &&     apt-get update &&     apt-get install -y unzip curl xz-utils &&     rm -rf /var/lib/apt/lists/* &&     mkdir -p "/public":                                                                                                                                                                                                      
#0 0.764 Get:1 http://mirrors.163.com/debian bullseye InRelease [116 kB]                                                                  
#...
#0 4.670 Err:6 http://mirrors.163.com/debian bullseye-updates/main armhf Packages
#0 4.786 Err:5 http://mirrors.163.com/debian-security bullseye-security/main armhf Packages
#0 4.786   404  Not Found [IP: 117.147.202.12 80]
#0 4.799 Fetched 208 kB in 4s (49.1 kB/s)
#0 4.799 Reading package lists...
#0 4.833 E: Failed to fetch http://mirrors.163.com/debian/dists/bullseye/main/binary-armhf/Packages  404  Not Found [IP: 117.147.202.12 80]
#0 4.833 E: Failed to fetch http://mirrors.163.com/debian-security/dists/bullseye-security/main/binary-armhf/Packages  404  Not Found [IP: 117.147.202.12 80]
#0 4.834 E: Failed to fetch http://mirrors.163.com/debian/dists/bullseye-updates/main/binary-armhf/Packages  404  Not Found [IP: 117.147.202.12 80]
#0 4.834 E: Some index files failed to download. They have been ignored, or old ones used instead.
------
nginx.Dockerfile:7
--------------------
   6 |         DEBIAN_FRONTEND="noninteractive"
   7 | >>> RUN set -eu; \
   8 | >>>     sed -ri "s@^([^#]*)http[s]?://[^/\.]+(\.[^/\.]+)+@\1${APT_MIRROR}@g" /etc/apt/sources.list && \
   9 | >>>     apt-get update && \
  10 | >>>     apt-get install -y unzip curl xz-utils && \
  11 | >>>     rm -rf /var/lib/apt/lists/* && \
  12 | >>>     mkdir -p "/public"
  13 |     
--------------------
ERROR: failed to solve: process "/bin/sh -c set -eu;     sed -ri \"s@^([^#]*)http[s]?://[^/\\.]+(\\.[^/\\.]+)+@\\1${APT_MIRROR}@g\" /etc/apt/sources.list &&     apt-get update &&     apt-get install -y unzip curl xz-utils &&     rm -rf /var/lib/apt/lists/* &&     mkdir -p \"/public\"" did not complete successfully: exit code: 100
```

下面是常用的debian/ubuntu常用的镜像源，中科大，清华是支持debian全平台的，但有可能速度不及商用平台

```
# 中国科学技术大学
http://mirrors.ustc.edu.cn
# 清华大学开源软件镜像站
https://mirrors.tuna.tsinghua.edu.cn
http://mirrors.163.com
http://mirrors.aliyun.com
```

### buildkit 多平台构建

同样是由于国内的网络问题，在构建时可能需要使用国内的buildkit镜像，在[使用 buildx 构建多种系统架构支持的 Docker 镜像](https://yeasy.gitbook.io/docker_practice/buildx/multi-arch-images)推荐使用[dockerpracticesig/buildkit:master](https://hub.docker.com/r/dockerpracticesig/buildkit/tags)，但是，如果没有注意看，这个buildkit镜像在arm平台是无法成功运行的，直接在arm64平台运行会出现

```bash
# 正常创建 builder
$ docker buildx create --use --name=mybuilder-cn --driver docker-container --bootstrap --use --driver-opt image=dock
erpracticesig/buildkit:master
[+] Building 9.6s (1/1) FINISHED
# ...                                              6.6s
mybuilder-cn

# 无法解析buildkit语法
$ docker buildx build --platform linux/amd64,linux/arm64 -t navyd/curl:latest --push - <<EOF
# syntax=docker/dockerfile:1
FROM alpine:3.16
RUN apk add curl
EOF

[+] Building 15.6s (4/4) FINISHED
# ...
 => => extracting sha256:1328b32c40fca9bcf9d70d8eccb72eb873d1124d72dadce04db8badbe7b08546                      2.3s
Dockerfile:1
--------------------
   1 | >>> # syntax=docker/dockerfile:1
   2 |     FROM alpine:3.16
   3 |     RUN apk add curl
--------------------
ERROR: failed to solve: frontend grpc server closed unexpectedly

# 移除buildkit语法 出现broken pipe错误
> docker buildx build --platform linux/amd64,linux/arm64 -t navyd/curl:latest --push - <<EOF
FROM alpine:3.16
RUN apk add curl
EOF
[+] Building 5.0s (9/9) FINISHED
# ...
 => ERROR [linux/arm64 2/2] RUN apk add curl                                                                   1.5s
 => [auth] library/alpine:pull token for registry-1.docker.io                                                  0.0s
 => ERROR [linux/amd64 2/2] RUN apk add curl                                                                   0.0s
------
 > [linux/arm64 2/2] RUN apk add curl:
#0 1.130 Error while loading init: No such file or directory
#0 1.275 container_linux.go:380: starting container process caused: process_linux.go:393: copying bootstrap data to pipe caused: write init-p: broken pipe
------
------
 > [linux/amd64 2/2] RUN apk add curl:
------
Dockerfile:2
--------------------
   1 |     FROM alpine:3.16
   2 | >>> RUN apk add curl
   3 |
--------------------
ERROR: failed to solve: process "/bin/sh -c apk add curl" did not complete successfully: exit code: 1
```

这个问题很难直接找到根源，可能是在arm平台使用了国内的buildkit镜像源，可以不具备通用性，网上基本没有什么有用的，在这里[Docker buildx 报错了，求大神看看](https://www.v2ex.com/t/839204)了解到可能是平台问题后，并在amd64平台测试后发现确实是这个erpracticesig/buildkit镜像的问题，在amd64正常使用，在arm64上无法使用，直接使用官方的镜像[moby/buildkit](https://hub.docker.com/r/moby/buildkit)就可以了。

另外，[dockerpracticesig/buildkit](https://hub.docker.com/r/dockerpracticesig/buildkit/tags)这个镜像已经很久没有更新，不建议使用了

```bash
> docker buildx create --use --name mybuilder --driver docker-container --bootstrap --use
[+] Building 8.2s (1/1) FINISHED
 => [internal] booting buildkit                                                                                8.0s
 => => pulling image moby/buildkit:buildx-stable-1                                                             2.6s
 => => creating container buildx_buildkit_mybuilder0                                                           5.4s
mybuilder

$ docker buildx build --platform linux/amd64,linux/arm64 -t navyd/curl:latest --push - <<EOF
FROM alpine:3.16
RUN apk add curl
EOF
# ...
```

### Error while loading /usr/sbin/dpkg-split: No such file or directory

重装了系统后，不知道什么原因，在安装了mybuilder后无法正常构建，出现问题：dpkg-split: No such file or directory

```bash
$ docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t navyd/nginx --push -f nginx.Dockerfile .
[+] Building 96.1s (30/34)                                                                               
 => [internal] load build definition from nginx.Dockerfile                                          0.1s
# ...
 => => resolve docker.io/library/nginx:1.23-alpine@sha256:bd1ef87802f41785f48862616c1b89fdce091cd3  0.4s
 => [linux/arm64 stage-3 1/3] FROM docker.io/library/nginx:1.23-alpine@sha256:bd1ef87802f41785f488  0.5s
 => => resolve docker.io/library/nginx:1.23-alpine@sha256:bd1ef87802f41785f48862616c1b89fdce091cd3  0.4s
 => CACHED [linux/arm64 base 2/2] RUN set -eu;     sed -ri "s@^([^#]*)http[s]?://[^/\.]+(\.[^/\.]+  0.0s
 => CACHED [linux/arm64 base-ariang 1/1] RUN set -eu;     curl -m 10 -o ariang.zip -L "https://git  0.0s
 => CACHED [linux/arm64 stage-3 2/3] COPY --from=base-ariang /public /var/www/a.navyd.xyz/public    0.0s
 => CACHED [linux/arm64 base-yacd 1/1] RUN set -eu;     curl -m 10 -L "https://github.com/haishanh  0.0s
 => CACHED [linux/arm64 stage-3 3/3] COPY --from=base-yacd /public /var/www/c.navyd.xyz/public      0.0s
 => CACHED [linux/arm/v7 base 2/2] RUN set -eu;     sed -ri "s@^([^#]*)http[s]?://[^/\.]+(\.[^/\.]  0.0s
 => CACHED [linux/arm/v7 base-ariang 1/1] RUN set -eu;     curl -m 10 -o ariang.zip -L "https://gi  0.0s
 => CACHED [linux/arm/v7 stage-3 2/3] COPY --from=base-ariang /public /var/www/a.navyd.xyz/public   0.0s
 => CACHED [linux/arm/v7 base-yacd 1/1] RUN set -eu;     curl -m 10 -L "https://github.com/haishan  0.0s
 => CACHED [linux/arm/v7 stage-3 3/3] COPY --from=base-yacd /public /var/www/c.navyd.xyz/public     0.0s
 => ERROR [linux/amd64 base 2/2] RUN set -eu;     sed -ri "s@^([^#]*)http[s]?://[^/\.]+(\.[^/\.]+  77.7s
------
 > [linux/amd64 base 2/2] RUN set -eu;     sed -ri "s@^([^#]*)http[s]?://[^/\.]+(\.[^/\.]+)+@\1http://mirrors.ustc.edu.cn@g" /etc/apt/sources.list &&     apt-get update &&     apt-get install -y unzip curl xz-utils &&     rm -rf /var/lib/apt/lists/* &&     mkdir -p "/public":
#0 2.244 Get:1 http://mirrors.ustc.edu.cn/debian bullseye InRelease [116 kB]
# ...
#0 71.61 Get:17 http://mirrors.ustc.edu.cn/debian bullseye/main amd64 unzip amd64 6.0-26+deb11u1 [172 kB]
#0 75.53 debconf: delaying package configuration, since apt-utils is not installed
#0 76.21 Fetched 3382 kB in 2s (2119 kB/s)
#0 76.43 Error while loading /usr/sbin/dpkg-split: No such file or directory
#0 76.44 Error while loading /usr/sbin/dpkg-deb: No such file or directory
#0 76.45 dpkg: error processing archive /tmp/apt-dpkg-install-Az6LcO/00-openssl_1.1.1n-0+deb11u3_amd64.deb (--unpack):
#0 76.45  dpkg-deb --control subprocess returned error exit status 1
#0 76.46 Error while loading /usr/sbin/dpkg-split: No such file or directory
#0 76.47 Error while loading /usr/sbin/dpkg-deb: No such file or directory
#0 76.47 dpkg: error processing archive /tmp/apt-dpkg-install-Az6LcO/01-ca-certificates_20210119_all.deb (--unpack):
#0 76.47  dpkg-deb --control subprocess returned error exit status 1
#0 76.48 Error while loading /usr/sbin/dpkg-split: No such file or directory
#0 76.49 Error while loading /usr/sbin/dpkg-deb: No such file or directory
#0 76.49 dpkg: error processing archive /tmp/apt-dpkg-install-Az6LcO/02-xz-utils_5.2.5-2.1~deb11u1_amd64.deb (--unpack):
#0 76.49  dpkg-deb --control subprocess returned error exit status 1
#0 76.51 Error while loading /usr/sbin/dpkg-split: No such file or directory
#0 76.52 Error while loading /usr/sbin/dpkg-deb: No such file or directory
#0 76.52 dpkg: error processing archive /tmp/apt-dpkg-install-Az6LcO/03-libbrotli1_1.0.9-2+b2_amd64.deb (--unpack):
#0 76.52  dpkg-deb --control subprocess returned error exit status 1
#0 76.53 Error while loading /usr/sbin/dpkg-split: No such file or directory
#0 76.54 Error while loading /usr/sbin/dpkg-deb: No such file or directory
#0 76.55 dpkg: error processing archive /tmp/apt-dpkg-install-Az6LcO/04-libsasl2-modules-db_2.1.27+dfsg-2.1+deb11u1_amd64.deb (--unpack):
#0 76.55  dpkg-deb --control subprocess returned error exit status 1
#0 76.56 Error while loading /usr/sbin/dpkg-split: No such file or directory
#0 76.57 Error while loading /usr/sbin/dpkg-deb: No such file or directory
#0 76.57 dpkg: error processing archive /tmp/apt-dpkg-install-Az6LcO/05-libsasl2-2_2.1.27+dfsg-2.1+deb11u1_amd64.deb (--unpack):
#0 76.57  dpkg-deb --control subprocess returned error exit status 1
#0 76.58 Error while loading /usr/sbin/dpkg-split: No such file or directory
#0 76.59 Error while loading /usr/sbin/dpkg-deb: No such file or directory
#0 76.59 dpkg: error processing archive /tmp/apt-dpkg-install-Az6LcO/06-libldap-2.4-2_2.4.57+dfsg-3+deb11u1_amd64.deb (--unpack):
#0 76.59  dpkg-deb --control subprocess returned error exit status 1
#0 76.60 Error while loading /usr/sbin/dpkg-split: No such file or directory
#0 76.61 Error while loading /usr/sbin/dpkg-deb: No such file or directory
#0 76.61 dpkg: error processing archive /tmp/apt-dpkg-install-Az6LcO/07-libnghttp2-14_1.43.0-1_amd64.deb (--unpack):
#0 76.61  dpkg-deb --control subprocess returned error exit status 1
#0 76.63 Error while loading /usr/sbin/dpkg-split: No such file or directory
#0 76.64 Error while loading /usr/sbin/dpkg-deb: No such file or directory
#0 76.64 dpkg: error processing archive /tmp/apt-dpkg-install-Az6LcO/08-libpsl5_0.21.0-1.2_amd64.deb (--unpack):
#0 76.64  dpkg-deb --control subprocess returned error exit status 1
#0 76.64 Error while loading /usr/sbin/dpkg-split: No such file or directory
#0 76.66 Error while loading /usr/sbin/dpkg-deb: No such file or directory
#0 76.66 dpkg: error processing archive /tmp/apt-dpkg-install-Az6LcO/09-librtmp1_2.4+20151223.gitfa8646d.1-2+b2_amd64.deb (--unpack):
#0 76.66  dpkg-deb --control subprocess returned error exit status 1
#0 76.67 Error while loading /usr/sbin/dpkg-split: No such file or directory
#0 76.68 Error while loading /usr/sbin/dpkg-deb: No such file or directory
#0 76.68 dpkg: error processing archive /tmp/apt-dpkg-install-Az6LcO/10-libssh2-1_1.9.0-2_amd64.deb (--unpack):
#0 76.68  dpkg-deb --control subprocess returned error exit status 1
#0 76.69 Error while loading /usr/sbin/dpkg-split: No such file or directory
#0 76.70 Error while loading /usr/sbin/dpkg-deb: No such file or directory
#0 76.70 dpkg: error processing archive /tmp/apt-dpkg-install-Az6LcO/11-libcurl4_7.74.0-1.3+deb11u3_amd64.deb (--unpack):
#0 76.70  dpkg-deb --control subprocess returned error exit status 1
#0 76.71 Error while loading /usr/sbin/dpkg-split: No such file or directory
#0 76.72 Error while loading /usr/sbin/dpkg-deb: No such file or directory
#0 76.72 dpkg: error processing archive /tmp/apt-dpkg-install-Az6LcO/12-curl_7.74.0-1.3+deb11u3_amd64.deb (--unpack):
#0 76.72  dpkg-deb --control subprocess returned error exit status 1
#0 76.73 Error while loading /usr/sbin/dpkg-split: No such file or directory
#0 76.74 Error while loading /usr/sbin/dpkg-deb: No such file or directory
#0 76.74 dpkg: error processing archive /tmp/apt-dpkg-install-Az6LcO/13-libldap-common_2.4.57+dfsg-3+deb11u1_all.deb (--unpack):
#0 76.74  dpkg-deb --control subprocess returned error exit status 1
#0 76.75 Error while loading /usr/sbin/dpkg-split: No such file or directory
#0 76.76 Error while loading /usr/sbin/dpkg-deb: No such file or directory
#0 76.76 dpkg: error processing archive /tmp/apt-dpkg-install-Az6LcO/14-libsasl2-modules_2.1.27+dfsg-2.1+deb11u1_amd64.deb (--unpack):
#0 76.76  dpkg-deb --control subprocess returned error exit status 1
#0 76.77 Error while loading /usr/sbin/dpkg-split: No such file or directory
#0 76.78 Error while loading /usr/sbin/dpkg-deb: No such file or directory
#0 76.78 dpkg: error processing archive /tmp/apt-dpkg-install-Az6LcO/15-publicsuffix_20220811.1734-0+deb11u1_all.deb (--unpack):
#0 76.78  dpkg-deb --control subprocess returned error exit status 1
#0 76.79 Error while loading /usr/sbin/dpkg-split: No such file or directory
#0 76.80 Error while loading /usr/sbin/dpkg-deb: No such file or directory
#0 76.80 dpkg: error processing archive /tmp/apt-dpkg-install-Az6LcO/16-unzip_6.0-26+deb11u1_amd64.deb (--unpack):
#0 76.80  dpkg-deb --control subprocess returned error exit status 1
#0 76.86 Errors were encountered while processing:
#0 76.86  /tmp/apt-dpkg-install-Az6LcO/00-openssl_1.1.1n-0+deb11u3_amd64.deb
#0 76.86  /tmp/apt-dpkg-install-Az6LcO/01-ca-certificates_20210119_all.deb
#0 76.86  /tmp/apt-dpkg-install-Az6LcO/02-xz-utils_5.2.5-2.1~deb11u1_amd64.deb
#0 76.86  /tmp/apt-dpkg-install-Az6LcO/03-libbrotli1_1.0.9-2+b2_amd64.deb
#0 76.86  /tmp/apt-dpkg-install-Az6LcO/04-libsasl2-modules-db_2.1.27+dfsg-2.1+deb11u1_amd64.deb
#0 76.86  /tmp/apt-dpkg-install-Az6LcO/05-libsasl2-2_2.1.27+dfsg-2.1+deb11u1_amd64.deb
#0 76.86  /tmp/apt-dpkg-install-Az6LcO/06-libldap-2.4-2_2.4.57+dfsg-3+deb11u1_amd64.deb
#0 76.86  /tmp/apt-dpkg-install-Az6LcO/07-libnghttp2-14_1.43.0-1_amd64.deb
#0 76.86  /tmp/apt-dpkg-install-Az6LcO/08-libpsl5_0.21.0-1.2_amd64.deb
#0 76.86  /tmp/apt-dpkg-install-Az6LcO/09-librtmp1_2.4+20151223.gitfa8646d.1-2+b2_amd64.deb
#0 76.87  /tmp/apt-dpkg-install-Az6LcO/10-libssh2-1_1.9.0-2_amd64.deb
#0 76.87  /tmp/apt-dpkg-install-Az6LcO/11-libcurl4_7.74.0-1.3+deb11u3_amd64.deb
#0 76.87  /tmp/apt-dpkg-install-Az6LcO/12-curl_7.74.0-1.3+deb11u3_amd64.deb
#0 76.87  /tmp/apt-dpkg-install-Az6LcO/13-libldap-common_2.4.57+dfsg-3+deb11u1_all.deb
#0 76.87  /tmp/apt-dpkg-install-Az6LcO/14-libsasl2-modules_2.1.27+dfsg-2.1+deb11u1_amd64.deb
#0 76.87  /tmp/apt-dpkg-install-Az6LcO/15-publicsuffix_20220811.1734-0+deb11u1_all.deb
#0 76.87  /tmp/apt-dpkg-install-Az6LcO/16-unzip_6.0-26+deb11u1_amd64.deb
#0 77.17 E: Sub-process /usr/bin/dpkg returned an error code (1)
------
nginx.Dockerfile:7
--------------------
   6 |         DEBIAN_FRONTEND="noninteractive"
   7 | >>> RUN set -eu; \
   8 | >>>     sed -ri "s@^([^#]*)http[s]?://[^/\.]+(\.[^/\.]+)+@\1${APT_MIRROR}@g" /etc/apt/sources.list && \
   9 | >>>     apt-get update && \
  10 | >>>     apt-get install -y unzip curl xz-utils && \
  11 | >>>     rm -rf /var/lib/apt/lists/* && \
  12 | >>>     mkdir -p "/public"
  13 |     
--------------------
ERROR: failed to solve: process "/dev/.buildkit_qemu_emulator /bin/sh -c set -eu;     sed -ri \"s@^([^#]*)http[s]?://[^/\\.]+(\\.[^/\\.]+)+@\\1${APT_MIRROR}@g\" /etc/apt/sources.list &&     apt-get update &&     apt-get install -y unzip curl xz-utils &&     rm -rf /var/lib/apt/lists/* &&     mkdir -p \"/public\"" did not complete successfully: exit code: 100
```

在这里[Error building python 3.6 slim #495](https://github.com/docker/buildx/issues/495#issuecomment-991603416)了解到再次更新binfmt安装即可

```bash
docker run --rm --privileged tonistiigi/binfmt:latest --install all
```

### Persisting ENV and ARG settings to all later stages in multi-stage builds

在dockerfile多阶段构建中通常需要使用同一个变量在所有stage中，但是，对于无关的两个stage是无法直接使用之前stage的变量的

在这里[Persisting ENV and ARG settings to all later stages in multi-stage builds #37345](https://github.com/moby/moby/issues/37345#issuecomment-400245466)使用ARG声明可以达到这种效果

```dockerfile
ARG version_default=v1

FROM alpine:latest as base1
ARG version_default
ENV version=$version_default
RUN echo ${version}
RUN echo ${version_default}

FROM alpine:latest as base2
ARG version_default
RUN echo ${version_default}
```

参考：

* [Multi-platform image](https://github.com/docker/build-push-action/blob/master/docs/advanced/multi-platform.md)
* [multi-stage build in docker compose?](https://stackoverflow.com/a/53101932/8566831)
* [使用 buildx 构建多种系统架构支持的 Docker 镜像](https://yeasy.gitbook.io/docker_practice/buildx/multi-arch-images)
* [An error, "failed to solve with frontend dockerfile.v0"](https://stackoverflow.com/a/66695181/8566831)
* [failed to solve with frontend dockerfile.v0: failed to build LLB: executor failed running - runc did not terminate sucessfully #426](https://github.com/docker/buildx/issues/426#issuecomment-732964418)
* [DOCKER_BUILDKIT=0 is not applied by docker-compose build #8649](https://github.com/docker/compose/issues/8649#issuecomment-923816281)
* [How do you enable BuildKit with docker-compose?](https://stackoverflow.com/a/58923844/8566831)
* [Build images with BuildKit](https://docs.docker.com/develop/develop-images/build_enhancements/)
* [基于 BuildKit 优化 Dockerfile 的构建](https://www.kubernetes.org.cn/9059.html)
* [Dockerfile reference syntax](https://docs.docker.com/engine/reference/builder/#syntax)
* [Docker buildx 报错了，求大神看看](https://www.v2ex.com/t/839204)
* [Error building python 3.6 slim #495](https://github.com/docker/buildx/issues/495#issuecomment-991603416)
* [Persisting ENV and ARG settings to all later stages in multi-stage builds #37345](https://github.com/moby/moby/issues/37345#issuecomment-400245466)

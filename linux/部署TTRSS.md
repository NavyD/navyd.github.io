# 部署TTRSS

## 通过 docker-compose 部署

基本可以参考：[通过 docker-compose 部署](http://ttrss.henry.wang/zh/#%E9%80%9A%E8%BF%87-docker-compose-%E9%83%A8%E7%BD%B2)

部分问题可以在[github issues](https://github.com/HenryQW/Awesome-TTRSS/issues)找到

如：[关于 SELF_URL_PATH 错误的解决方案大合集](https://github.com/HenryQW/Awesome-TTRSS/issues/62)

### bilibili视频

参考：[移除 iframe 上的 sandbox 属性](http://ttrss.henry.wang/zh/#remove-iframe-sandbox)

### docker nginx反向代理https

### 申请域名

在aliyun和tencent中选择一个域名注册

### 子域名申请ssl证书

在ali和tencent有免费的ssl DV证书，还有[`let's encrypt`免费证书](letsencrypt证书申请.md)

需要注意的是当前`20210221`ali的免费证书申请改变到[证书资源包领取](https://common-buy.aliyun.com/?spm=5176.14113079.commonbuy2container.4.5d4656a7XqSDJp&commodityCode=cas_dv_public_cn&request=%7B%22ord_time%22:%221:Year%22,%22order_num%22:1,%22product%22:%22free_product%22,%22certCount%22:%2220%22%7D)

在[域名解析页面](https://dns.console.aliyun.com/?spm=5176.12818093.Operation--ali--widget-home-product-recent.dre2.75e316d0gVoDxB#/dns/setting/navyd.xyz)可以添加记录

### nginx反向代理

将上面的ssl证书下载后，配置nginx-default.conf

```conf
upstream ttrssdev {
    server ttrss:80;
}

server {
    listen 80;
    server_name  rss.navyd.xyz;
    return 301 https://rss.navyd.xyz$request_uri;
}

server {
    listen 443 ssl;
    gzip on;
    server_name  rss.navyd.xyz;

    ssl_certificate /etc/nginx/certs/rss.navyd.xyz.pem;
    ssl_certificate_key /etc/nginx/certs/rss.navyd.xyz.key;

    access_log /var/log/nginx/ttrssdev_access.log combined;
    error_log  /var/log/nginx/ttrssdev_error.log;

    location / {
        proxy_redirect off;
        proxy_pass http://ttrssdev;

        proxy_set_header  Host                $http_host;
        proxy_set_header  X-Real-IP           $remote_addr;
        proxy_set_header  X-Forwarded-Ssl     on;
        proxy_set_header  X-Forwarded-For     $proxy_add_x_forwarded_for;
        proxy_set_header  X-Forwarded-Proto   $scheme;
        proxy_set_header  X-Frame-Options     SAMEORIGIN;

        client_max_body_size        100m;
        client_body_buffer_size     128k;

        proxy_buffer_size           4k;
        proxy_buffers               4 32k;
        proxy_busy_buffers_size     64k;
        proxy_temp_file_write_size  64k;
    }
}
```

配置docker compose，更多的内容参考[通过 docker-compose 部署](http://ttrss.henry.wang/zh/#%E9%80%9A%E8%BF%87-docker-compose-%E9%83%A8%E7%BD%B2)

```yaml
version: "3"
services:
  service.nginx:
    image: nginx:alpine
    container_name: rssnginx
    ports:
      # - 9090:80
      - 9090:443
      - 443:443
    volumes:
      - type: bind
        source: $PWD/certs
        target: /etc/nginx/certs
      - type: bind
        source: $PWD/nginx-default.conf
        target: /etc/nginx/conf.d/default.conf
    restart: always
    networks:
      - public_access
# ...
```

## https穿透

[Linux 系统使用 frpc](https://doc.natfrp.com/#/frpc/usage/linux)

参考：[SakuraFrp 帮助文档](https://doc.natfrp.com/#/)

注意在使用systemd启动frpc时配置`/lib/systemd/system/frpc.service`

```
[Unit]
Description=Sakura Frp Client Service
After=network.target syslog.target
Wants=network.target

[Service]
Type=simple
Restart=on-failure
RestartSec=5s
ExecStart=/usr/local/frp/frpc_linux_arm64 -f auhgl7erobqywz96:990364

[Install]
WantedBy=multi-user.target
```

### 内外网切换

当在内网时使用路由器dns劫持避免访问外网，在使用子域名时会出现url不一致的情况。如外网url`rss.navyd.xyz`在内网的服务：`192.168.93.202:9090`，就算劫持了dns，`rss.navyd.xyz` -> `192.168.93.202`，也不能避免写端口号`rss.navyd.xyz:9090`

```yaml
    container_name: rssnginx
    ports:
      # - 9090:80
      - 9090:443
      # 代理rss.navyd.xyz到容器
      - 443:443
```

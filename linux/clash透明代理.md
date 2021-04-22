# clash

## 订阅转换subconverter

clash提供[Proxy Provider](https://lancellc.gitbook.io/clash/clash-config-file/proxy-provider)功能，可以方便的分离代理节点为单个url资源，自动更新订阅节点等如：

```yaml
#port: 8888
#socks-port: 8889
# ...
# proxy provider start here
proxy-providers:
	hk:
		type: http
		path: ./hk.yaml
		url: http://remote.lancelinked.icu/files/hk.yaml
		interval: 3600
		health-check:
			enable: true
			url: http://www.gstatic.com/generate_204
			interval: 300
	us:
		type: file
		path: /home/lance/.clash/provider/us.yaml
		health-check:
			enable: true
			url: http://www.gstatic.com/generate_204
			interval: 300
# proxy provider end

#Proxy:
#  - type: socks5
#    name: spck
#    port: 34335
#    server: 127.0.0.1
#    udp: true
```

在使用机场提供的clash文件时通常只会使用到其中的proxies，还有过滤节点等需求，clash不支持过滤节点。而[subconverter](https://github.com/tindy2013/subconverter/blob/master/README-cn.md#%E8%AF%B4%E6%98%8E%E7%9B%AE%E5%BD%95)提供了订阅转换与过滤等必要的功能

### 部署

使用docker安装

```sh
docker run -d --restart=always -p 25500:25500 tindy2013/subconverter:latest
```

subconverter参数：

```
target=clash	# 转换结果为 clash 配置
url=xxx	# 机场订阅链接
include=(TW|台湾|台灣)	# 只匹配台湾节点
list=true	# 生成 provider 链接

# 将urlencoded 参数拼接起来得到新的订阅链接——只包含台湾节点的 provider 链接
https://localhost:25500/sub?target=clash&url=https%3a%2f%2fnfnf.xyz%2flink%2fabcdefg%3fmu%3d4&include=(TW%7c%e5%8f%b0%e6%b9%be%7c%e5%8f%b0%e7%81%a3)&list=true
```

参考：

* [[WIP]Tun](https://comzyh.gitbook.io/clash/)
* [clash premium(2020.10.09) tun模式,无法代理本机,不知道哪出问题了 #1060](https://github.com/Dreamacro/clash/issues/1060)
* [Clash TUN mode](https://lancellc.gitbook.io/clash/start-clash/clash-tun-mode)
* [Kr328 的 Clash 配置脚本们](https://github.com/Kr328/kr328-clash-setup-scripts)
* [Clash proxy-provider 搭配 subconverter 使用小记](https://10101.io/2020/02/12/use-clash-proxy-provider-with-subconverter)

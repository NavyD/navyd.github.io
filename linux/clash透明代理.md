# clash

## Linux透明代理原理

参考：

* [Linux transparent proxy support](https://powerdns.org/tproxydoc/tproxy.md.html)
* [Linux transparent proxy support github](https://github.com/ahupowerdns/tproxydoc/blob/master/tproxy.md)
* [透明代理 UDP 为什么要用 TProxy？](https://www.codenong.com/js5393fb5e2c87/)
* [透明代理的基本原理](https://github.com/lazytiger/trojan-rs/blob/master/PRINCIPLE.md)
* [从 ss-redir 的实现到 Linux NAT](https://vvl.me/2018/06/from-ss-redir-to-linux-nat/)

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

## docker部署

在docker内启动时使用iptables操作，stop时清理iptables。

* [自用docker镜像](https://hub.docker.com/r/navyd/clash)
* [NavyD/docker-clash](https://github.com/NavyD/docker-clash)

## 代理方式

### TCP redir + UDP TPROXY

redir模式。对转发流量使用tcp redir, udp tproxy方式代理。本机仅代理tcp，支持docker内部代理。支持fakeip但存在icmp无法回应的问题（tcp udp没有问题），tun-fakeip可以提供更好的服务。

```bash
# local 
# 接管clash宿主机内部流量
iptables -t nat -N CLASH
iptables -t nat -F CLASH
# private
setup_private nat CLASH
# 过滤本机clash流量 避免循环 user无法使用代理
iptables -t nat -A CLASH -m owner --uid-owner "$RUNNING_UID" -j RETURN
iptables -t nat -A CLASH -p tcp -j REDIRECT --to-port "$REDIR_PORT"

iptables -t nat -A OUTPUT -j CLASH

# 转发流量 tcp redir
iptables -t nat -N CLASH_EXTERNAL
iptables -t nat -F CLASH_EXTERNAL
# google dns first
iptables -t nat -A CLASH_EXTERNAL -p tcp -d 8.8.8.8 -j REDIRECT --to-port "$REDIR_PORT"
iptables -t nat -A CLASH_EXTERNAL -p tcp -d 8.8.4.4 -j REDIRECT --to-port "$REDIR_PORT"
# private
setup_private nat CLASH_EXTERNAL
# tcp redir
iptables -t nat -A CLASH_EXTERNAL -p tcp -j REDIRECT --to-port "$REDIR_PORT"

iptables -t nat -A PREROUTING -j CLASH_EXTERNAL

# 转发流量 udp tproxy
iptables -t mangle -N CLASH_EXTERNAL
iptables -t mangle -F CLASH_EXTERNAL
# private
setup_private mangle CLASH_EXTERNAL
# udp tproxy redir
iptables -t mangle -A CLASH_EXTERNAL -p udp -j TPROXY --on-port "$REDIR_PORT" --tproxy-mark $MARK_ID

iptables -t mangle -A PREROUTING -j CLASH_EXTERNAL

# route udp
ip rule add fwmark $MARK_ID table $TABLE_ID
ip route add local default dev lo table $TABLE_ID
```

参考：

* [Clash TProxy Mode](https://lancellc.gitbook.io/clash/start-clash/clash-udp-tproxy-support)
* [clash本机做透明代理iptables规则请教](https://github.com/Dreamacro/clash/issues/555#issuecomment-595064646)
* [Fake IP 模式如何直接转发icmp包（无法Ping任何网站）](https://github.com/Dreamacro/clash/issues/1047)
* [iptables处理icmp转发](https://lev.shield.asia/index.php/Ops/31.html)
* [使用 iptables 透明代理 TCP 与 UDP](https://blog.lilydjwg.me/2018/7/16/transparent-proxy-for-tcp-and-udp-with-iptables.213139.html)

### TCP&UDP TPROXY

clash支持tcp tproxy，可以使用tcp tproxy避免在nat中重定向定义多个chain

在配置文件config.yaml中增加：

```yaml
# Transparent proxy server port for Linux (TProxy TCP and TProxy UDP)
tproxy-port: 7893
```

本机代理与TCP redir相似，下面是透明代理

```bash
# ROUTE RULES
ip rule add fwmark $MARK_ID table $TABLE_ID
ip route add local default dev lo table $TABLE_ID

# CREATE TABLE
iptables -t mangle -N clash

# RETURN LOCAL AND LANS
setup_private mangle clash

# FORWARD ALL
iptables -t mangle -A clash -p udp -j TPROXY --on-port $REDIR_PORT --tproxy-mark $MARK_ID
iptables -t mangle -A clash -p tcp -j TPROXY --on-port $REDIR_PORT --tproxy-mark $MARK_ID

# REDIRECT
iptables -t mangle -A PREROUTING -j clash
```

参考：

* [Add TCP TPROXY support](https://github.com/Dreamacro/clash/pull/1049)
* [Clash 作为网关的透明代理](https://www.wogong.net/blog/2020/11/clash-transparent-proxy)
* [v2ray 透明代理(TPROXY)](https://guide.v2fly.org/app/tproxy.html)

### TUN

适用于tun-redir,tun-fakeip，代理本机与外部流量。在iptables mangle中设置mark并过滤内部私有地址、过滤指定运行clash uid的流量防止循环。

~~本机docker内部网络无法直接被代理，如果不`-s 172.16.0.0/12 -j RETURN`则docker内部无法ping到外部网络，可能是在mangle表后路由到tun设备后无法被iptables nat中的DOCKER链处理。~~

使用`-i "$TUN_NAME" -j RETURN`防止docker内部流量被mark循环到tun接口。具体可行原因未知`todo` <!-- todo -->

```bash
# 代理本机与外部流量。在iptables mangle中设置mark并过滤内部私有地址、
# 过滤指定运行clash uid的流量防止循环。允许本机与docker通过代理

## 接管clash宿主机内部流量
iptables -t mangle -N CLASH
iptables -t mangle -F CLASH
# filter clash traffic running under uid 注意顺序 owner过滤 要在 set mark之前
iptables -t mangle -A CLASH -m owner --uid-owner "$RUNNING_UID" -j RETURN
# private
local_iptables mangle CLASH
# mark
iptables -t mangle -A CLASH -j MARK --set-xmark $MARK_ID

iptables -t mangle -A OUTPUT -j CLASH

## 接管转发流量
iptables -t mangle -N CLASH_EXTERNAL
iptables -t mangle -F CLASH_EXTERNAL
# private
local_iptables mangle CLASH_EXTERNAL
# avoid rerouting for local docker
iptables -t mangle -A CLASH_EXTERNAL -i "$TUN_NAME" -j RETURN
# mark
iptables -t mangle -A CLASH_EXTERNAL -j MARK --set-xmark $MARK_ID

iptables -t mangle -A PREROUTING -j CLASH_EXTERNAL

# utun route table
ip route replace default dev "$TUN_NAME" table "$TABLE_ID"
ip rule add fwmark "$MARK_ID" lookup "$TABLE_ID"

# 排除 rp_filter 的故障 反向路由
sysctl -w net.ipv4.conf."$TUN_NAME".rp_filter=0 2> /dev/null
sysctl -w net.ipv4.conf.all.rp_filter=0 2> /dev/null
```

参考：

* [Real-IP Tun Example](https://comzyh.gitbook.io/clash/real-ip-tun-example)
* [Clash TUN mode](https://lancellc.gitbook.io/clash/start-clash/clash-tun-mode)

### 已知问题

1. TPROXY 不能用于 OUTPUT 链，无法用于本机代理。在[v2ray 配置透明代理规则](https://guide.v2fly.org/app/tproxy.html#%E9%85%8D%E7%BD%AE%E9%80%8F%E6%98%8E%E4%BB%A3%E7%90%86%E8%A7%84%E5%88%99)中可以通过标记重路由的方式代理本机，但是在clash要对clash源码在socket上标记`SO_MARK`。查看了openclash源码也没有对`UDP TPROXY`的解决方法，在使用TPROXY时只能代理本机tcp流量。尝试使用`--owner-uid`的方式过滤clash发出的流量，但是没有用，可能是与OUTPUT重路由到PREROUTING链不同，原理不清
2. ~~TUN方式在docker使用时bridge网络无法解析dns到外部网络，[容器(docker)桥接(bridge)模式时的代理问题](https://github.com/springzfx/cgproxy/issues/10)有相关讨论。fakeip直接启动时不设置只是作为dns网关使用时，docker bridge网络可以正常使用。`TCP TPROXY`的方式可以bridge网络可正常使用~~

shell实现参考：

* [shellclash start.sh](https://github.com/juewuy/ShellClash/blob/master/scripts/start.sh)
* [OpenClash openclash](https://github.com/vernesong/OpenClash/blob/master/luci-app-openclash/root/etc/init.d/openclash)
* [clash-premium-installer setup-tun.sh](https://github.com/Kr328/clash-premium-installer/blob/master/scripts/setup-tun.sh)

参考：

* [How to check if a variable is set in Bash?](https://stackoverflow.com/a/17538964)
* [Clash Premiun Installer](https://github.com/Kr328/clash-premium-installer)
* [你的 docker stop，它优雅吗？](https://segmentfault.com/a/1190000022971054)
* [Unable to trap signals in docker entrypoint script](https://stackoverflow.com/a/60699262)
* [Linux 网络工具详解之 ip tuntap 和 tunctl 创建 tap/tun 设备](https://www.cnblogs.com/bakari/p/10449664.html)
* [ShellClash](https://github.com/juewuy/ShellClash)
* [浅谈在代理环境中的 DNS 解析行为](https://blog.skk.moe/post/what-happend-to-dns-in-proxy/)
* [容器(docker)桥接(bridge)模式时的代理问题](https://github.com/springzfx/cgproxy/issues/10)
* [Transparent Proxy powered by cgroup v2](https://github.com/springzfx/cgproxy/blob/aaa628a76b2911018fc93b2e3276c177e85e0861/readme.md#known-issues)

相关项目：

* [go Dreamacro/clash](https://github.com/Dreamacro/clash)
* [go tun comzyh/clash](https://github.com/comzyh/clash)
* [rust Trojan-rs](https://github.com/lazytiger/trojan-rs)

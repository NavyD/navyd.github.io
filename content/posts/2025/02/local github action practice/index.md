---
title: Local Github Action Practice
date: 2025-02-16T23:37:39+08:00
draft: false
tags: [DevOps, github, actions, docker, proxy, CI]
---

[nektos/act: Run your GitHub Actions locally](https://github.com/nektos/act) 允许在本地使用 docker 运行 github actions。

## 问题

### 网络

在国内使用 github 最大的问题是网络非常不稳定，而在 act 中基本都是需要直连 github，而其中绝大部分都不支持自建 github host，即使部分支持如果在 act 中单独配置会与 github action 不兼容

#### 代理

参考 [Unable to use Proxy in act - Containers](https://github.com/nektos/act/issues/1578#issuecomment-1744424213) 使用 `act --env https_proxy=http://host.docker.internal:3128 --env http_proxy=http://host.docker.internal:3128`

现在通常使用有 tun 代理模式的 mihomo 等全局代理，不需要主动指定 http 环境代理。

但对于代理的稳定性来说，下载文件极可能失败导致 step 失败，重复运行可能出现大量的 github 请求，所以尽量减少重复的运行，缓存是必要的！

### 缓存

参考 [Action Offline Mode](https://nektosact.com/usage/index.html#action-offline-mode) 使用 `act --action-offline-mode` 与 [actions/cache](https://github.com/actions/cache) 尽最大可能利用缓存！

这是有一个问题，如果在 step 中一次进行大量请求极大可能出现网络错误，在成功前是无法缓存的，如果可能，可以减少请求数，多次运行 act 慢慢增加缓存避免错误！

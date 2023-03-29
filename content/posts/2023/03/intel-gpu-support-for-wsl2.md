---
title: Intel Gpu Support for Wsl2
date: 2023-03-29T11:50:19+08:00
draft: false
tags: [wsl2, gpu, docker, intel, linux]
author: [navyd]
cover:
    useFirstImageIfNone: true
---

![](https://tomthegreat.com/content/images/size/w960/2022/09/plex_ubuntu_docker.png)

在使用docker时应用需要使用gpu加速解码，尝试在wsl2中挂载intel集显设备/dev/dri时无法正常启动，找不到设备文件。

<!--more-->

## 分析

在win10 21H2以上开始支持wsl2 gpu，win11肯定是支持的，网上大部分都是NVIDIA的资料，intel集显比较少。

在这里[WDDM GPU Paravirtualization support for WSL2](https://github.com/intel/compute-runtime/blob/master/WSL.md)提到可能是显卡驱动的问题

> Required driver package (30.0.100.9955) is available here.

## 解决

在这里下载新驱动[Intel® Graphics – Windows* DCH Drivers](https://www.intel.com/content/www/us/en/download/19344/intel-graphics-windows-dch-drivers.html)，重新安装新的驱动后即可正常挂载设备/dev/dri

参考：

* [WDDM GPU Paravirtualization support for WSL2](https://github.com/intel/compute-runtime/blob/master/WSL.md)
* [GPU accelerated ML training](https://learn.microsoft.com/en-us/windows/ai/directml/gpu-accelerated-training)
* [Enabling GPU acceleration on Ubuntu on WSL2 with the NVIDIA CUDA Platform](https://ubuntu.com/tutorials/enabling-gpu-acceleration-on-ubuntu-on-wsl2-with-the-nvidia-cuda-platform#1-overview)
